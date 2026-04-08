import json
from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.dependencies.security import get_request_user
from app.dtos.chat import (
    AiResponseRequest,
    ChatMessageCreateRequest,
    ChatMessageResponse,
    ChatSessionCreateRequest,
    ChatSessionResponse,
    FaqItemResponse,
)
from app.models.users import User
from app.services.chat import ChatService

chat_router = APIRouter(prefix="/chat", tags=["chat"])


@chat_router.post("/sessions", status_code=status.HTTP_201_CREATED)
async def create_session(
    request: ChatSessionCreateRequest,
    user: Annotated[User, Depends(get_request_user)],
    chat_service: Annotated[ChatService, Depends(ChatService)],
) -> JSONResponse:
    session = await chat_service.create_session(
        user_id=user.id,
        ocr_id=request.ocr_id,
    )
    return JSONResponse(
        content=json.loads(
            ChatSessionResponse(
                session_id=session.id,
                user_id=session.user_id,
                ocr_id=session.ocr_id,
                message_count=session.message_count,
                created_at=session.created_at,
            ).model_dump_json()
        ),
        status_code=status.HTTP_201_CREATED,
    )


@chat_router.get("/sessions", status_code=status.HTTP_200_OK)
async def get_sessions(
    user: Annotated[User, Depends(get_request_user)],
    chat_service: Annotated[ChatService, Depends(ChatService)],
) -> JSONResponse:
    sessions = await chat_service.get_sessions(user_id=user.id)
    return JSONResponse(
        content=[
            json.loads(
                ChatSessionResponse(
                    session_id=s.id,
                    user_id=s.user_id,
                    ocr_id=s.ocr_id,
                    message_count=s.message_count,
                    created_at=s.created_at,
                ).model_dump_json()
            )
            for s in sessions
        ],
        status_code=status.HTTP_200_OK,
    )


@chat_router.get("/sessions/{session_id}", status_code=status.HTTP_200_OK)
async def get_session(
    session_id: int,
    user: Annotated[User, Depends(get_request_user)],
    chat_service: Annotated[ChatService, Depends(ChatService)],
) -> JSONResponse:
    session = await chat_service.get_session(
        session_id=session_id,
        user_id=user.id,
    )
    return JSONResponse(
        content=json.loads(
            ChatSessionResponse(
                session_id=session.id,
                user_id=session.user_id,
                ocr_id=session.ocr_id,
                message_count=session.message_count,
                created_at=session.created_at,
            ).model_dump_json()
        ),
        status_code=status.HTTP_200_OK,
    )


@chat_router.delete("/sessions/{session_id}", status_code=status.HTTP_200_OK)
async def delete_session(
    session_id: int,
    user: Annotated[User, Depends(get_request_user)],
    chat_service: Annotated[ChatService, Depends(ChatService)],
) -> JSONResponse:
    await chat_service.delete_session(
        session_id=session_id,
        user_id=user.id,
    )
    return JSONResponse(
        content={"message": "세션이 삭제되었습니다.", "session_id": session_id},
        status_code=status.HTTP_200_OK,
    )


@chat_router.get("/sessions/{session_id}/messages", status_code=status.HTTP_200_OK)
async def get_messages(
    session_id: int,
    user: Annotated[User, Depends(get_request_user)],
    chat_service: Annotated[ChatService, Depends(ChatService)],
) -> JSONResponse:
    messages = await chat_service.get_messages(
        session_id=session_id,
        user_id=user.id,
    )
    return JSONResponse(
        content=[
            json.loads(
                ChatMessageResponse(
                    message_id=m.id,
                    session_id=m.session_id,
                    sender=m.sender,
                    content=m.content,
                    is_faq=m.is_faq,
                    created_at=m.created_at,
                ).model_dump_json()
            )
            for m in messages
        ],
        status_code=status.HTTP_200_OK,
    )


@chat_router.post("/sessions/{session_id}/messages", status_code=status.HTTP_201_CREATED)
async def save_message(
    session_id: int,
    request: ChatMessageCreateRequest,
    user: Annotated[User, Depends(get_request_user)],
    chat_service: Annotated[ChatService, Depends(ChatService)],
) -> JSONResponse:
    message = await chat_service.save_message(
        session_id=session_id,
        user_id=user.id,
        content=request.content,
        is_faq=request.is_faq,
    )
    return JSONResponse(
        content=json.loads(
            ChatMessageResponse(
                message_id=message.id,
                session_id=message.session_id,
                sender=message.sender,
                content=message.content,
                is_faq=message.is_faq,
                created_at=message.created_at,
            ).model_dump_json()
        ),
        status_code=status.HTTP_201_CREATED,
    )


@chat_router.post("/sessions/{session_id}/ai-response", status_code=status.HTTP_201_CREATED)
async def get_ai_response(
    session_id: int,
    request: AiResponseRequest,
    user: Annotated[User, Depends(get_request_user)],
    chat_service: Annotated[ChatService, Depends(ChatService)],
) -> JSONResponse:
    message = await chat_service.get_ai_response(
        session_id=session_id,
        user_id=user.id,
        user_message=request.user_message,
    )
    return JSONResponse(
        content=json.loads(
            ChatMessageResponse(
                message_id=message.id,
                session_id=message.session_id,
                sender=message.sender,
                content=message.content,
                is_faq=message.is_faq,
                created_at=message.created_at,
            ).model_dump_json()
        ),
        status_code=status.HTTP_201_CREATED,
    )


@chat_router.get("/faq", status_code=status.HTTP_200_OK)
async def get_faqs(
    chat_service: Annotated[ChatService, Depends(ChatService)],
) -> JSONResponse:
    faqs = await chat_service.get_faqs()
    return JSONResponse(
        content=[
            FaqItemResponse(
                id=f.id,
                question=f.question,
                answer=f.answer,
                display_order=f.display_order,
            ).model_dump()
            for f in faqs
        ],
        status_code=status.HTTP_200_OK,
    )
