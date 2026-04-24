import json
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, status
from fastapi.responses import JSONResponse

from app.dependencies.security import get_request_user
from app.dtos.chat import (
    AiResponseRequest,
    ChatMessageCreateRequest,
    ChatMessageResponse,
    ChatSessionCreateRequest,
    ChatSessionResponse,
    ChatSessionUpdateRequest,
    # FaqItemResponse, # FAQ 우선 비활성화
)
from app.models.users import User
from app.services.chat import ChatService

chat_router = APIRouter(prefix="/chat", tags=["AI 맞춤형 챗봇"])


@chat_router.post(
    "/sessions",
    status_code=status.HTTP_201_CREATED,
    summary="챗봇 세션(채팅방) 생성",
    description="선택한 처방전(OCR) 데이터와 연동되거나, 새롭게 질문할 수 있는 맞춤형 채팅방(세션)을 개설합니다.",
)
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


@chat_router.patch(
    "/sessions/{session_id}",
    status_code=status.HTTP_200_OK,
    summary="챗봇 세션(채팅방) 연동 정보 업데이트",
    description="기존 채팅방에 처방전(OCR) ID를 연동합니다.",
)
async def update_session(
    session_id: int,
    request: ChatSessionUpdateRequest,
    user: Annotated[User, Depends(get_request_user)],
    chat_service: Annotated[ChatService, Depends(ChatService)],
) -> JSONResponse:
    session = await chat_service.update_session_ocr_id(
        session_id=session_id,
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
        status_code=status.HTTP_200_OK,
    )


@chat_router.get(
    "/sessions",
    status_code=status.HTTP_200_OK,
    summary="전체 챗봇 세션 목록 조회",
    description="현재 로그인한 사용자가 이전에 생성해 둔 모든 채팅방(세션)의 목록과 요약 정보를 불러옵니다.",
)
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


@chat_router.get(
    "/sessions/{session_id}",
    status_code=status.HTTP_200_OK,
    summary="특정 챗봇 세션 상세 내역 조회",
    description="선택한 특정 채팅방의 고유 식별값, 연결된 처방전, 총 대화 개수 등의 기본 정보를 확인합니다.",
)
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


@chat_router.delete(
    "/sessions/{session_id}",
    status_code=status.HTTP_200_OK,
    summary="챗봇 세션(채팅방) 삭제",
    description="목적을 달성한 특정 채팅방을 목록에서 제거합니다. (실제 데이터베이스 완전삭제가 아닌 Soft Delete 기법으로 안전하게 감춤 처리됩니다)",
)
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


@chat_router.get(
    "/sessions/{session_id}/messages",
    status_code=status.HTTP_200_OK,
    summary="해당 세션의 전체 채팅 대화 내역 조회",
    description="해당 방 안에서 사용자와 AI 어시스턴트가 핑퐁으로 주고받은 모든 대화(메시지) 기록을 시간순으로 불러옵니다.",
)
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


@chat_router.post(
    "/sessions/{session_id}/messages",
    status_code=status.HTTP_201_CREATED,
    summary="사용자 발화 메시지(질문) 저장",
    description="사용자가 직접 타이핑했거나 추천 FAQ(자주 묻는 질문) 메뉴를 통해 발생시킨 질문 텍스트를 데이터베이스에 적재합니다.",
)
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


@chat_router.post(
    "/sessions/{session_id}/ai-response",
    status_code=status.HTTP_201_CREATED,
    summary="AI 챗봇 의료 상담 답변 생성",
    description="""
사용자의 질문을 기반으로 AI 어시스턴트(GPT)가 검토하여 맞춤형 의료 답변 텍스트를 즉시 반환합니다.

- **개인화 답변**: 환자의 과거 투약 이력과 이전 대화 맥락을 모두 고려하여 응답합니다.
- **성능 최적화**: 사용자의 전체 대화 턴(Turn)이 5회 이상 누적될 시, 서버 뒤쪽 단(BackgroundTasks)에서 최근 대화의 주민번호 등 민감정보(PII)를 제거하고 의학적 관점으로만 한 줄 요약하여 프롬프트 토큰 낭비를 획기적으로 줄여줍니다.
    """,
)
async def get_ai_response(
    session_id: int,
    request: AiResponseRequest,
    user: Annotated[User, Depends(get_request_user)],
    chat_service: Annotated[ChatService, Depends(ChatService)],
    background_tasks: BackgroundTasks,
) -> JSONResponse:
    message = await chat_service.get_ai_response(
        session_id=session_id,
        user_id=user.id,
        user_message=request.user_message,
        background_tasks=background_tasks,
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


# @chat_router.get("/faq", status_code=status.HTTP_200_OK)
# async def get_faqs(
#     chat_service: Annotated[ChatService, Depends(ChatService)],
# ) -> JSONResponse:
#     faqs = await chat_service.get_faqs()
#     return JSONResponse(
#         content=[
#             FaqItemResponse(
#                 id=f.id,
#                 question=f.question,
#                 answer=f.answer,
#                 display_order=f.display_order,
#             ).model_dump()
#             for f in faqs
#         ],
#         status_code=status.HTTP_200_OK,
#     )
