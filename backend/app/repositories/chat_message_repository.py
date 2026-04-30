from app.models.chat_message import ChatMessage, SenderType


class ChatMessageRepository:
    def __init__(self):
        self._model = ChatMessage

    async def create(
        self,
        session_id: int,
        sender: SenderType,
        content: str,
        is_faq: bool = False,
    ) -> ChatMessage:
        return await self._model.create(
            session_id=session_id,
            sender=sender,
            content=content,
            is_faq=is_faq,
        )

    async def get_by_session_id(self, session_id: int) -> list[ChatMessage]:
        return await self._model.filter(session_id=session_id, is_deleted=False).order_by("created_at")
