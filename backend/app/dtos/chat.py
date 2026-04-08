from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field

from app.models.chat_message import SenderType


class ChatSessionCreateRequest(BaseModel):
    ocr_id: Annotated[int | None, Field(None, description="OCR 처방전 ID")]


class ChatSessionResponse(BaseModel):
    session_id: int
    user_id: int
    ocr_id: int | None
    message_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class ChatMessageCreateRequest(BaseModel):
    content: Annotated[str, Field(..., description="메시지 내용")]
    is_faq: Annotated[bool, Field(False, description="FAQ 클릭 여부")]


class ChatMessageResponse(BaseModel):
    message_id: int
    session_id: int
    sender: SenderType
    content: str
    is_faq: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AiResponseRequest(BaseModel):
    user_message: Annotated[str, Field(..., description="사용자 메시지")]


class FaqItemResponse(BaseModel):
    id: int
    question: str
    answer: str
    display_order: int

    class Config:
        from_attributes = True