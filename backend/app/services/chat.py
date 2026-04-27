from fastapi import BackgroundTasks, HTTPException
from starlette import status
from tortoise.transactions import in_transaction

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

    async def process_chat_message(
        self,
        session_id: int,
        user_id: int,
        content: str,
        idempotency_key: str | None,
        background_tasks: BackgroundTasks,
        is_faq: bool = False,
    ) -> ChatMessage:
        import datetime

        from app.models.chat_idempotency import ChatIdempotency
        from app.services.openai_service import (
            generate_chat_answer,
            get_medication_context_for_chatbot,
        )

        # 1. Idempotency Check
        if idempotency_key:
            existing_key = await ChatIdempotency.get_or_none(idempotency_key=idempotency_key)
            if existing_key:
                diff = (datetime.datetime.now(datetime.UTC) - existing_key.created_at).total_seconds()
                if diff < 60:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT, detail="현재 처리 중이거나 방금 완료된 중복 요청입니다."
                    )
            else:
                await ChatIdempotency.create(idempotency_key=idempotency_key)

        # 2. Session & Processing Lock Check
        session = await self.get_session(session_id=session_id, user_id=user_id)

        if session.is_processing:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="AI가 아직 이전 질문에 답변 중입니다. 잠시 후 다시 시도해주세요.",
            )

        # 락 세팅
        session.is_processing = True
        await session.save(update_fields=["is_processing"])

        try:
            # 3. 사용자 메시지 저장
            async with in_transaction():
                await self.message_repo.create(
                    session_id=session_id,
                    sender=SenderType.USER,
                    content=content,
                    is_faq=is_faq,
                )
                await self.session_repo.increment_message_count(session)

            # 4. FAQ 또는 AI 답변 준비
            if is_faq:
                # FAQ 템플릿 조회
                faq_template = await self.faq_repo.find_answer_by_question(content)

                if faq_template:
                    # OCR 약물 정보 가져오기
                    medications = await self._get_ocr_medications(session.ocr_id)

                    # 약물별 상세 답변 생성
                    ai_content = await self._build_faq_answer(faq_template, medications, content, user_id)
                else:
                    # FAQ에 없으면 GPT로 폴백
                    ocr_context = await get_medication_context_for_chatbot(user_id, session.ocr_id)
                    recent_chat_messages = await self.message_repo.get_by_session_id(session_id=session_id)
                    recent_chat_messages = recent_chat_messages[-7:]
                    recent_dicts = [
                        {"role": "user" if m.sender == SenderType.USER else "assistant", "content": m.content}
                        for m in recent_chat_messages
                    ]

                    try:
                        ai_content = await generate_chat_answer(
                            user_message=content,
                            ocr_context=ocr_context,
                            summary=session.summary or "",
                            recent_messages=recent_dicts[:-1],
                        )
                    except Exception as e:
                        raise HTTPException(
                            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="현재 AI 상담소 응답이 지연되고 있습니다. 잠시 후 재시도해주세요.",
                        ) from e
            else:
                # 일반 질문은 바로 GPT
                ocr_context = await get_medication_context_for_chatbot(user_id, session.ocr_id)
                recent_chat_messages = await self.message_repo.get_by_session_id(session_id=session_id)
                recent_chat_messages = recent_chat_messages[-7:]
                recent_dicts = [
                    {"role": "user" if m.sender == SenderType.USER else "assistant", "content": m.content}
                    for m in recent_chat_messages
                ]

                try:
                    ai_content = await generate_chat_answer(
                        user_message=content,
                        ocr_context=ocr_context,
                        summary=session.summary or "",
                        recent_messages=recent_dicts[:-1],
                    )
                except Exception as e:
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="현재 AI 상담소 응답이 지연되고 있습니다. 잠시 후 재시도해주세요.",
                    ) from e

            # 6. AI 응답 저장
            async with in_transaction():
                message = await self.message_repo.create(
                    session_id=session_id,
                    sender=SenderType.ASSISTANT,
                    content=ai_content,
                    is_faq=False,
                )
                await self.session_repo.increment_message_count(session)

            # 7. 후속 작업 (Summary & Cleanup)
            await session.refresh_from_db(fields=["message_count"])
            if session.message_count > 0 and session.message_count % 10 == 0:
                background_tasks.add_task(self.trigger_summarization, session_id)

            background_tasks.add_task(self.cleanup_old_idempotency_keys)

            return message

        finally:
            # Lock 해제
            session.is_processing = False
            await session.save(update_fields=["is_processing"])

    async def trigger_summarization(self, sess_id: int):
        from app.services.openai_service import summarize_and_deidentify_chat

        sess = await self.session_repo.get_by_id(sess_id)
        if not sess:
            return
        msgs = await self.message_repo.get_by_session_id(sess_id)
        msgs_dicts = [
            {"role": "user" if m.sender == SenderType.USER else "assistant", "content": m.content} for m in msgs[-10:]
        ]
        new_summary = await summarize_and_deidentify_chat(msgs_dicts)

        if sess.summary:
            sess.summary = sess.summary + " | " + new_summary
        else:
            sess.summary = new_summary
        await sess.save(update_fields=["summary"])

    async def cleanup_old_idempotency_keys(self):
        import datetime

        from app.models.chat_idempotency import ChatIdempotency

        threshold = datetime.datetime.now(datetime.UTC) - datetime.timedelta(minutes=10)
        await ChatIdempotency.filter(created_at__lt=threshold).delete()

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

    # ruff: noqa: C901
    async def _build_faq_answer(self, template: str, medications: list[dict], question: str, user_id: int) -> str:
        """FAQ 템플릿 + 약물 데이터로 답변 생성"""
        if not medications:
            return f"{template}\n\n현재 인식된 약물 정보가 없습니다. 처방전을 먼저 업로드해주세요."

        from app.models.drugs import DrugInfo
        from app.services.openai_service import get_drug_info_from_gpt

        answer_parts = [template, ""]

        for idx, med in enumerate(medications, 1):
            med_name = med.get("name", "")
            if not med_name:
                continue

            # e약은요 DB에서 약물 정보 조회 (3단계 매칭)
            drug = await DrugInfo.get_or_none(name=med_name)

            if not drug:
                # 2단계: 부분 매칭 (LIKE '%삼아탄툼액%')
                drug = await DrugInfo.filter(name__icontains=med_name).first()

            if not drug:
                # 3단계: 시작 문자열 매칭 (LIKE '삼아탄툼액%')
                drug = await DrugInfo.filter(name__istartswith=med_name).first()

            if "부작용" in question:
                # 부작용 답변
                if drug and drug.side_effects and drug.side_effects.strip():
                    answer_parts.append(f"{idx}. {med_name}: {drug.side_effects}")
                else:
                    # GPT로 부작용 정보 조회
                    try:
                        gpt_info = await get_drug_info_from_gpt(med_name, "부작용")
                        answer_parts.append(f"{idx}. {med_name}: {gpt_info}")
                    except Exception:
                        answer_parts.append(
                            f"{idx}. {med_name}: 부작용 정보를 찾을 수 없습니다. 의사 또는 약사와 상담하세요."
                        )

            elif "주의사항" in question:
                # 주의사항 답변
                if drug and drug.precautions and drug.precautions.strip():
                    answer_parts.append(f"{idx}. {med_name}: {drug.precautions}")
                else:
                    # GPT로 주의사항 정보 조회
                    try:
                        gpt_info = await get_drug_info_from_gpt(med_name, "주의사항")
                        answer_parts.append(f"{idx}. {med_name}: {gpt_info}")
                    except Exception:
                        answer_parts.append(
                            f"{idx}. {med_name}: 주의사항 정보를 찾을 수 없습니다. 복용 전 의사 또는 약사와 상담하세요."
                        )

            elif "상호작용" in question or "같이 먹" in question:
                # 상호작용 답변
                if drug and drug.interactions and drug.interactions.strip():
                    answer_parts.append(f"{idx}. {med_name}: {drug.interactions}")
                else:
                    # GPT로 상호작용 정보 조회
                    try:
                        gpt_info = await get_drug_info_from_gpt(med_name, "다른 약과의 상호작용")
                        answer_parts.append(f"{idx}. {med_name}: {gpt_info}")
                    except Exception:
                        answer_parts.append(
                            f"{idx}. {med_name}: 상호작용 정보를 찾을 수 없습니다. 복용 전 의사 또는 약사와 상담하세요."
                        )

        # 마지막 안내 문구
        answer_parts.append("")
        answer_parts.append("정확한 복용 상담은 전문 의료진과 상담해주세요.")

        return "\n".join(answer_parts)
