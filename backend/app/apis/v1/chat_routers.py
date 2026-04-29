from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, Header, status

from app.dependencies.security import get_request_user
from app.dtos.chat import (
    ChatMessageCreateRequest,
    ChatMessageResponse,
    ChatSessionCreateRequest,
    ChatSessionResponse,
    ChatSessionUpdateRequest,
)
from app.models.users import User
from app.services.chat import ChatService

chat_router = APIRouter(prefix="/chat", tags=["AI 맞춤형 챗봇"])


# ──────────────────────────────────────────────
# 1. 채팅 세션(채팅방) 생성 및 목록 관리
# ──────────────────────────────────────────────
@chat_router.post(
    "/sessions",
    response_model=ChatSessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="챗봇 세션(채팅방) 생성",
    description="선택한 처방전(OCR) 데이터와 연동되거나, 새롭게 질문할 수 있는 맞춤형 채팅방(세션)을 개설합니다.",
    responses={
        201: {"description": "채팅방 생성 성공"},
        401: {"description": "인증 실패 (토큰 누락 또는 만료)"},
        404: {"description": "연동하려는 OCR 정보를 찾을 수 없음"},
    },
)
async def create_session(
    request: ChatSessionCreateRequest,
    user: Annotated[User, Depends(get_request_user)],
    chat_service: Annotated[ChatService, Depends(ChatService)],
):
    session = await chat_service.create_session(user_id=user.id, ocr_id=request.ocr_id)
    return ChatSessionResponse(
        session_id=session.id,
        user_id=session.user_id,
        ocr_id=session.ocr_id,
        message_count=session.message_count,
        created_at=session.created_at,
    )


# ──────────────────────────────────────────────
# 2. 채팅 세션 및 정보 업데이트
# ──────────────────────────────────────────────
@chat_router.patch(
    "/sessions/{session_id}",
    response_model=ChatSessionResponse,
    status_code=status.HTTP_200_OK,
    summary="챗봇 세션(채팅방) 연동 정보 업데이트",
    description="기존 채팅방에 처방전(OCR) ID를 연동하거나 관련 정보를 수정합니다.",
    responses={
        200: {"description": "업데이트 성공"},
        401: {"description": "인증 실패 (토큰 누락 또는 만료)"},
        403: {"description": "권한 없음 (자신의 채팅방이 아님)"},
    },
)
async def update_session(
    session_id: int,
    request: ChatSessionUpdateRequest,
    user: Annotated[User, Depends(get_request_user)],
    chat_service: Annotated[ChatService, Depends(ChatService)],
):
    session = await chat_service.update_session_ocr_id(session_id=session_id, user_id=user.id, ocr_id=request.ocr_id)
    return ChatSessionResponse(
        session_id=session.id,
        user_id=session.user_id,
        ocr_id=session.ocr_id,
        message_count=session.message_count,
        created_at=session.created_at,
    )


# ──────────────────────────────────────────────
# 3. 채팅 세션 목록 및 상세 조회
# ──────────────────────────────────────────────
@chat_router.get(
    "/sessions",
    response_model=list[ChatSessionResponse],
    status_code=status.HTTP_200_OK,
    summary="전체 챗봇 세션 목록 조회",
    description="현재 로그인한 사용자가 이전에 생성해 둔 모든 채팅방(세션)의 목록과 요약 정보를 불러옵니다.",
    responses={
        200: {"description": "목록 조회 성공"},
        401: {"description": "인증 실패 (토큰 누락 또는 만료)"},
    },
)
async def get_sessions(
    user: Annotated[User, Depends(get_request_user)],
    chat_service: Annotated[ChatService, Depends(ChatService)],
):
    sessions = await chat_service.get_sessions(user_id=user.id)
    return [
        ChatSessionResponse(
            session_id=s.id,
            user_id=s.user_id,
            ocr_id=s.ocr_id,
            message_count=s.message_count,
            created_at=s.created_at,
        )
        for s in sessions
    ]


@chat_router.get(
    "/sessions/{session_id}",
    response_model=ChatSessionResponse,
    status_code=status.HTTP_200_OK,
    summary="특정 챗봇 세션 상세 내역 조회",
    description="선택한 특정 채팅방의 고유 식별값, 연결된 처방전, 총 대화 개수 등의 기본 정보를 확인합니다.",
    responses={
        200: {"description": "세션 정보 조회 성공"},
        401: {"description": "인증 실패 (토큰 누락 또는 만료)"},
        404: {"description": "해당 세션을 찾을 수 없음"},
    },
)
async def get_session(
    session_id: int,
    user: Annotated[User, Depends(get_request_user)],
    chat_service: Annotated[ChatService, Depends(ChatService)],
):
    session = await chat_service.get_session(session_id=session_id, user_id=user.id)
    return ChatSessionResponse(
        session_id=session.id,
        user_id=session.user_id,
        ocr_id=session.ocr_id,
        message_count=session.message_count,
        created_at=session.created_at,
    )


# ──────────────────────────────────────────────
# 4. 채팅 세션 삭제
# ──────────────────────────────────────────────
@chat_router.delete(
    "/sessions/{session_id}",
    status_code=status.HTTP_200_OK,
    summary="챗봇 세션(채팅방) 삭제",
    description="목적을 달성한 특정 채팅방을 목록에서 제거합니다. (실제 데이터베이스 완전삭제가 아닌 Soft Delete 기법으로 안전하게 감춤 처리됩니다)",
    responses={
        200: {"description": "세션 삭제(숨김) 성공"},
        401: {"description": "인증 실패 (토큰 누락 또는 만료)"},
        403: {"description": "권한 없음 (자신의 채팅방이 아님)"},
    },
)
async def delete_session(
    session_id: int,
    user: Annotated[User, Depends(get_request_user)],
    chat_service: Annotated[ChatService, Depends(ChatService)],
):
    await chat_service.delete_session(session_id=session_id, user_id=user.id)
    return {"message": "세션이 삭제되었습니다.", "session_id": session_id}


# ──────────────────────────────────────────────
# 5. 채팅 메시지 조회 및 대화 진행
# ──────────────────────────────────────────────
@chat_router.get(
    "/sessions/{session_id}/messages",
    response_model=list[ChatMessageResponse],
    status_code=status.HTTP_200_OK,
    summary="해당 세션의 전체 채팅 대화 내역 조회",
    description="해당 방 안에서 사용자와 AI 어시스턴트가 핑퐁으로 주고받은 모든 대화(메시지) 기록을 시간순으로 불러옵니다.",
    responses={
        200: {"description": "대화 내역 조회 성공"},
        401: {"description": "인증 실패 (토큰 누락 또는 만료)"},
    },
)
async def get_messages(
    session_id: int,
    user: Annotated[User, Depends(get_request_user)],
    chat_service: Annotated[ChatService, Depends(ChatService)],
):
    messages = await chat_service.get_messages(session_id=session_id, user_id=user.id)
    return [
        ChatMessageResponse(
            message_id=m.id,
            session_id=m.session_id,
            sender=m.sender,
            content=m.content,
            is_faq=m.is_faq,
            created_at=m.created_at,
        )
        for m in messages
    ]


@chat_router.post(
    "/sessions/{session_id}/messages",
    response_model=ChatMessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="사용자 발화 저장 및 AI 응답 생성",
    description="사용자 질문을 저장하고, 멱등성 검사를 통해 중복 호출을 방지하며 AI 상담 결과를 생성하여 반환합니다.",
    responses={
        201: {"description": "대화 성공 및 AI 응답 반환"},
        401: {"description": "인증 실패 (토큰 누락 또는 만료)"},
        409: {"description": "멱등성 키 충돌 (이미 처리 중이거나 완료된 요청)"},
        429: {"description": "AI 호출량 초과 또는 동시 처리 락 발생"},
    },
)
async def process_chat_message(
    session_id: int,
    request: ChatMessageCreateRequest,
    user: Annotated[User, Depends(get_request_user)],
    chat_service: Annotated[ChatService, Depends(ChatService)],
    background_tasks: BackgroundTasks,
    x_idempotency_key: str = Header(..., alias="X-Idempotency-Key"),  # noqa: B008
):
    message = await chat_service.process_chat(
        session_id=session_id,
        user_id=user.id,
        content=request.content,
        is_faq=request.is_faq,
        idempotency_key=x_idempotency_key,
        background_tasks=background_tasks,
    )
    return ChatMessageResponse(
        message_id=message.id,
        session_id=message.session_id,
        sender=message.sender,
        content=message.content,
        is_faq=message.is_faq,
        created_at=message.created_at,
    )
