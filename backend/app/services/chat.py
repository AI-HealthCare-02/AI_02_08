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

    async def get_ai_response(
        self,
        session_id: int,
        user_id: int,
        user_message: str,
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

        # 1. AI 응답 생성
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
        # 여기서 message_count는 user+assistant 합쳐서 카운트 됨.
        # (save_message에서 1 증가, get_ai_response에서 1 증가 = 1턴당 2 증가)
        # 따라서 10 (5턴 * 2) 시점 단위로 요약 실행
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
