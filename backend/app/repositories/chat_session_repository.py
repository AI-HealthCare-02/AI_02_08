from app.models.chat_session import ChatSession


class ChatSessionRepository:
    def __init__(self):
        self._model = ChatSession

    async def create(
        self,
        user_id: int,
        ocr_id: int | None = None,
    ) -> ChatSession:
        return await self._model.create(
            user_id=user_id,
            ocr_id=ocr_id,
        )

    async def get_by_id(self, session_id: int) -> ChatSession | None:
        return await self._model.get_or_none(id=session_id)

    async def get_by_user_id(self, user_id: int) -> list[ChatSession]:
        return await self._model.filter(user_id=user_id).order_by("-created_at")

    async def increment_message_count(self, session: ChatSession) -> None:
        session.message_count += 1
        await session.save(update_fields=["message_count"])

    async def delete(self, session: ChatSession) -> None:
        await session.delete()