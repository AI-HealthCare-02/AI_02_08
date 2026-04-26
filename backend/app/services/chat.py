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

            # 4. AI 답변 준비 (Trimming & Windowing 반영된 서비스 호출)
            ocr_context = await get_medication_context_for_chatbot(user_id, session.ocr_id)
            recent_chat_messages = await self.message_repo.get_by_session_id(session_id=session_id)
            recent_chat_messages = recent_chat_messages[-7:]  # 최신 질문 포함 7건

            recent_dicts = [
                {"role": "user" if m.sender == SenderType.USER else "assistant", "content": m.content}
                for m in recent_chat_messages
            ]

            # 5. AI 호출 (Retry 로직 내장됨)
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
