from app.models.chat_session import ChatSession


from tortoise.expressions import F

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
        return await self._model.get_or_none(id=session_id, is_deleted=False)

    async def get_by_user_id(self, user_id: int) -> list[ChatSession]:
        return await self._model.filter(user_id=user_id, is_deleted=False).order_by("-created_at")

    async def increment_message_count(self, session: ChatSession) -> None:
        await self._model.filter(id=session.id).update(message_count=F("message_count") + 1)
        session.message_count += 1

    async def delete(self, session: ChatSession) -> None:
        session.is_deleted = True
        await session.save(update_fields=["is_deleted"])
