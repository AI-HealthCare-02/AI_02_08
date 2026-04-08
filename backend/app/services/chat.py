from fastapi import HTTPException
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
        ocr_id: int | None = None,
    ) -> ChatSession:
        return await self.session_repo.create(
            user_id=user_id,
            ocr_id=ocr_id,
        )

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
        await self.session_repo.delete(session)

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

        # message_count 10회 초과 시 AI 호출 차단
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
    ) -> ChatMessage:
        from openai import AsyncOpenAI

        session = await self.get_session(session_id=session_id, user_id=user_id)

        # OCR 컨텍스트 조회
        context = ""
        if session.ocr_id:
            await session.fetch_related("ocr")
            if session.ocr and session.ocr.extracted_data:
                context = f"처방전 분석 결과: {session.ocr.extracted_data}"

        client = AsyncOpenAI()
        system_prompt = f"""당신은 복약 정보 전문 AI 어시스턴트입니다.
약학 및 복약 관련 질문에만 답변하고, 그 외 질문은 정중히 거절하세요.
답변 끝에 반드시 '[출처: 식품의약품안전처 e약은요]' 문구를 추가하세요.
{f'참고 정보: {context}' if context else ''}"""

        response = await client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        )

        ai_content = response.choices[0].message.content

        # AI 답변 저장
        async with in_transaction():
            message = await self.message_repo.create(
                session_id=session_id,
                sender=SenderType.ASSISTANT,
                content=ai_content,
                is_faq=False,
            )
            await self.session_repo.increment_message_count(session)

        return message

    async def get_faqs(self) -> list[FaqItem]:
        return await self.faq_repo.get_active_faqs()