from fastapi import BackgroundTasks, HTTPException
from starlette import status
from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from app.models.chat_idempotency import ChatIdempotency
from app.models.chat_message import ChatMessage, SenderType
from app.models.chat_session import ChatSession
from app.models.faq_item import FaqItem
from app.repositories.chat_message_repository import ChatMessageRepository
from app.repositories.chat_session_repository import ChatSessionRepository
from app.repositories.faq_repository import FaqRepository

MAX_MESSAGE_COUNT = 10


class ChatService:
    def __init__(self):
        self.session_repo = ChatSessionRepository()
        self.message_repo = ChatMessageRepository()
        self.faq_repo = FaqRepository()

    async def create_session(
        self,
        user_id: int,
        ocr_id: str | None = None,
    ) -> ChatSession:
        return await self.session_repo.create(
            user_id=user_id,
            ocr_id=ocr_id,
        )

    async def update_session_ocr_id(
        self,
        session_id: int,
        user_id: int,
        ocr_id: str,
    ) -> ChatSession:
        session = await self.get_session(session_id=session_id, user_id=user_id)
        session.ocr_id = ocr_id
        await session.save(update_fields=["ocr_id"])
        return session

    async def get_sessions(self, user_id: int) -> list[ChatSession]:
        return await self.session_repo.get_by_user_id(user_id=user_id)

    async def get_session(self, session_id: int, user_id: int) -> ChatSession:
        session = await self.session_repo.get_by_id(session_id=session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="세션을 찾을 수 없습니다.",
            )
        if session.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="접근 권한이 없습니다.",
            )
        return session

    async def delete_session(self, session_id: int, user_id: int) -> None:
        session = await self.get_session(session_id=session_id, user_id=user_id)
        async with in_transaction():
            await self.session_repo.delete(session)
            await ChatMessage.filter(session_id=session_id).update(is_deleted=True)

    async def get_messages(self, session_id: int, user_id: int) -> list[ChatMessage]:
        await self.get_session(session_id=session_id, user_id=user_id)
        return await self.message_repo.get_by_session_id(session_id=session_id)

    async def save_message(
        self,
        session_id: int,
        user_id: int,
        content: str,
        is_faq: bool = False,
    ) -> ChatMessage:
        session = await self.get_session(session_id=session_id, user_id=user_id)

        if not is_faq and session.message_count >= MAX_MESSAGE_COUNT:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="메시지 횟수 제한(10회)을 초과했습니다.",
            )

        async with in_transaction():
            message = await self.message_repo.create(
                session_id=session_id,
                sender=SenderType.USER,
                content=content,
                is_faq=is_faq,
            )
            await self.session_repo.increment_message_count(session)

        return message

    async def process_chat(
        self,
        session_id: int,
        user_id: int,
        content: str,
        is_faq: bool,
        idempotency_key: str,
        background_tasks: BackgroundTasks,
    ) -> ChatMessage:
        """
        사용자 메시지 저장 + AI 응답 생성 (Idempotency 보장)
        """
        # 1. 멱등성 체크 (DB Unique Constraint 활용)
        try:
            await ChatIdempotency.create(idempotency_key=idempotency_key)
        except IntegrityError:
            # 중복 요청 발생 시 기존 메시지 중 가장 최근 assistant 응답 반환 (단순화)
            # 실제 운영에서는 Redis 등을 사용하여 처리 상태를 정교하게 관리해야 함
            recent_msgs = await self.get_messages(session_id=session_id, user_id=user_id)
            for m in reversed(recent_msgs):
                if m.sender == SenderType.ASSISTANT:
                    return m
            raise HTTPException(status_code=409, detail="이미 처리 중인 요청이거나 중복된 요청입니다.") from None

        # 2. 사용자 메시지 저장
        await self.save_message(
            session_id=session_id,
            user_id=user_id,
            content=content,
            is_faq=is_faq,
        )

        # 3. AI 응답 생성 및 저장
        ai_message = await self.get_ai_response(
            session_id=session_id,
            user_id=user_id,
            user_message=content,
            is_faq=is_faq,  # 추가!
            background_tasks=background_tasks,
        )

        return ai_message

    async def get_ai_response(
        self,
        session_id: int,
        user_id: int,
        user_message: str,
        is_faq: bool,  # 추가!
        background_tasks: BackgroundTasks,
    ) -> ChatMessage:
        from app.services.openai_service import (
            generate_chat_answer,
            get_medication_context_for_chatbot,
            summarize_and_deidentify_chat,
        )

        session = await self.get_session(session_id=session_id, user_id=user_id)

        # 현재 복용 중인 약물 컨텍스트 조회 (OCR 원본 JSON 대신 정제된 데이터 활용 + 현재 OCR 세션 데이터 포함)
        ocr_context = await get_medication_context_for_chatbot(user_id, session.ocr_id)

        # 현재 저장된 최근 메시지 조회 (Assistant 생성을 위한 컨텍스트, 최대 6건)
        recent_chat_messages = await self.message_repo.get_by_session_id(session_id=session_id)
        recent_chat_messages = recent_chat_messages[-6:]  # 최근 6개만

        recent_dicts = [
            {"role": "user" if m.sender == SenderType.USER else "assistant", "content": m.content}
            for m in recent_chat_messages
        ]

        # FAQ 질문인 경우 템플릿 기반 답변 생성
        if is_faq:
            # FAQ 아이템 조회
            faq_item = await FaqItem.get_or_none(question=user_message)
            if faq_item:
                # OCR 약물 목록 가져오기
                medications = await self._get_ocr_medications(session.ocr_id)
                # 템플릿 + 약물 정보로 답변 생성
                ai_content = await self._build_faq_answer(
                    template=faq_item.answer,  # 수정!
                    medications=medications,
                    question=user_message,
                    user_id=user_id,
                )
            else:
                ai_content = "질문을 찾을 수 없습니다."
        else:
            # 일반 질문인 경우 GPT 호출
            ai_content = await generate_chat_answer(
                user_message=user_message,
                ocr_context=ocr_context,
                summary=session.summary or "",
                recent_messages=recent_dicts,
            )

        # 2. 메시지 저장 및 횟수 증가
        async with in_transaction():
            message = await self.message_repo.create(
                session_id=session_id,
                sender=SenderType.ASSISTANT,
                content=ai_content,
                is_faq=False,
            )
            await self.session_repo.increment_message_count(session)

        # 3. 5턴(메시지 누적 5쌍) 초과 시 Background Task로 요약 트리거
        if session.message_count > 0 and session.message_count % 10 == 0:

            async def trigger_summarization(sess_id: int):
                sess = await self.session_repo.get_by_id(sess_id)
                if not sess:
                    return
                msgs = await self.message_repo.get_by_session_id(sess_id)
                msgs_dicts = [
                    {"role": "user" if m.sender == SenderType.USER else "assistant", "content": m.content}
                    for m in msgs[-10:]  # 방금 생성된 5턴치
                ]
                new_summary = await summarize_and_deidentify_chat(msgs_dicts)

                # 기존 요약이 있다면 합치거나 대체
                if sess.summary:
                    sess.summary = sess.summary + " | " + new_summary
                else:
                    sess.summary = new_summary
                await sess.save(update_fields=["summary"])

            background_tasks.add_task(trigger_summarization, session_id)

        return message

    async def get_faqs(self) -> list[FaqItem]:
        return await self.faq_repo.get_active_faqs()

    async def _get_ocr_medications(self, ocr_id: str | None) -> list[dict]:
        """OCR로 인식된 약물 목록 가져오기"""
        if not ocr_id:
            return []

        from app.models.medications import OcrPrescription

        ocr = await OcrPrescription.get_or_none(ocr_id=ocr_id)
        if not ocr or not ocr.extracted_data:
            return []

        return ocr.extracted_data.get("parsed", [])

    async def _get_drug_from_db(self, med_name: str):
        """e약은요 DB에서 약물 정보 조회 (3단계 매칭)"""
        from app.models.drugs import DrugInfo

        # 1단계: 정확 일치
        drug = await DrugInfo.get_or_none(name=med_name)
        if drug:
            return drug

        # 2단계: 부분 일치
        drug = await DrugInfo.filter(name__icontains=med_name).first()
        if drug:
            return drug

        # 3단계: 시작 일치
        return await DrugInfo.filter(name__istartswith=med_name).first()

    async def _get_drug_info_for_question(self, drug, med_name: str, question: str) -> str:
        """질문 유형에 따라 약물 정보 반환"""
        from app.services.openai_service import get_drug_info_from_gpt

        if "부작용" in question:
            if drug and drug.side_effects and drug.side_effects.strip():
                return f"  {drug.side_effects}"
            try:
                gpt_info = await get_drug_info_from_gpt(med_name, "부작용")
                return f"  {gpt_info}"
            except Exception:
                return "  부작용 정보를 찾을 수 없습니다. 의사 또는 약사와 상담하세요."

        elif "주의사항" in question:
            if drug and drug.precautions and drug.precautions.strip():
                return f"  {drug.precautions}"
            try:
                gpt_info = await get_drug_info_from_gpt(med_name, "주의사항")
                return f"  {gpt_info}"
            except Exception:
                return "  주의사항 정보를 찾을 수 없습니다. 복용 전 의사 또는 약사와 상담하세요."

        elif "상호작용" in question or "같이 먹" in question:
            if drug and drug.interactions and drug.interactions.strip():
                return f"  {drug.interactions}"
            try:
                gpt_info = await get_drug_info_from_gpt(med_name, "다른 약과의 상호작용")
                return f"  {gpt_info}"
            except Exception:
                return "  상호작용 정보를 찾을 수 없습니다. 복용 전 의사 또는 약사와 상담하세요."

        return "  정보를 찾을 수 없습니다."

    async def _build_faq_answer(self, template: str, medications: list[dict], question: str, user_id: int) -> str:
        """FAQ 템플릿 + 약물 데이터로 답변 생성"""

        # 생활습관 가이드는 템플릿 그대로 반환
        lifestyle_questions = ["운동 가이드", "식단 가이드", "수면 가이드", "스트레스 관리"]
        if question in lifestyle_questions:
            return template

        # 기존 약물 FAQ 로직
        if not medications:
            return f"{template}\n\n현재 인식된 약물 정보가 없습니다. 처방전을 먼저 업로드해주세요."

        answer_parts = [template, ""]

        print("🔍 FAQ 답변 생성 중:")
        print(f"   - 질문: {question}")

        for med in medications:
            med_name = med.get("name", "")
            if not med_name:
                continue

            print(f"   - 약물명: {med_name}")

            # DB에서 약물 정보 조회
            drug = await self._get_drug_from_db(med_name)
            print(f"     → DB 매칭: {'성공' if drug else '실패'}")

            # 접기/펼치기 형식
            answer_parts.append(f"▼ {med_name}")

            # 질문에 따른 정보 추가
            info = await self._get_drug_info_for_question(drug, med_name, question)
            answer_parts.append(info)
            answer_parts.append("")  # 약물 사이 빈 줄

        # 마지막 안내 문구
        answer_parts.append("정확한 복용 상담은 전문 의료진과 상담해주세요.")

        return "\n".join(answer_parts)
