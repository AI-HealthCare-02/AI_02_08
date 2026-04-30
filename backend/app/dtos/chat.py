from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from app.models.chat_message import SenderType


class ChatSessionCreateRequest(BaseModel):
    ocr_id: Annotated[str | None, Field(None, description="OCR 처방전 ID")]


class ChatSessionUpdateRequest(BaseModel):
    ocr_id: Annotated[str, Field(..., description="연동할 OCR 처방전 ID")]


class ChatSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    session_id: int
    user_id: int
    ocr_id: str | None
    message_count: int
    created_at: datetime


class ChatMessageCreateRequest(BaseModel):
    content: Annotated[str, Field(..., description="메시지 내용")]
    is_faq: Annotated[bool, Field(False, description="FAQ 클릭 여부")]


class ChatMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    message_id: int
    session_id: int
    sender: SenderType
    content: str
    is_faq: bool
    faq_buttons: list[dict] = []  # 추가!
    created_at: datetime


class AiResponseRequest(BaseModel):
    user_message: Annotated[str, Field(..., description="사용자 메시지")]


class FaqItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    question: str
    answer: str
    display_order: int
