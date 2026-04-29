from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.dependencies.security import get_request_user
from app.dtos.users import UserInfoResponse, UserUpdateRequest
from app.models.users import User
from app.services.auth import AuthService
from app.services.users import UserManageService

user_router = APIRouter(prefix="/users", tags=["사용자 정보 관리"])


# ──────────────────────────────────────────────
# 1. 내 정보 조회
# ──────────────────────────────────────────────
@user_router.get(
    "/me",
    response_model=UserInfoResponse,
    status_code=status.HTTP_200_OK,
    summary="내 정보 조회",
    description="현재 로그인한 사용자의 프로필 정보(이메일, 닉네임, 생년월일 등)를 조회합니다.",
    responses={
        200: {"description": "조회 성공"},
        401: {"description": "인증 실패 (토큰 누락 또는 만료)"},
    },
)
async def get_user_me(
    user: Annotated[User, Depends(get_request_user)],
):
    return UserInfoResponse.model_validate(user)


# ──────────────────────────────────────────────
# 2. 내 정보 수정 (PATCH)
# ──────────────────────────────────────────────
@user_router.patch(
    "/me",
    response_model=UserInfoResponse,
    status_code=status.HTTP_200_OK,
    summary="내 정보 수정",
    description="로그인한 사용자의 닉네임, 전화번호 등 프로필 정보를 업데이트합니다.",
    responses={
        200: {"description": "수정 성공"},
        401: {"description": "인증 실패 (토큰 누락 또는 만료)"},
        422: {"description": "입력값 유효성 검증 실패"},
    },
)
async def update_user_me(
    request: UserUpdateRequest,
    user: Annotated[User, Depends(get_request_user)],
    user_manage_service: Annotated[UserManageService, Depends(UserManageService)],
):
    updated_user = await user_manage_service.update_user(user=user, data=request)
    return UserInfoResponse.model_validate(updated_user)


# ──────────────────────────────────────────────
# 3. 회원 탈퇴 (Soft Delete)
# ──────────────────────────────────────────────
@user_router.delete(
    "/me",
    status_code=status.HTTP_200_OK,
    summary="회원 탈퇴",
    description="""
현재 로그인한 사용자의 계정을 탈퇴 처리합니다. (소프트 딜리트 방식으로 데이터가 감춤 처리됩니다)
탈퇴 후에도 일정 기간 내 재가입이 가능하며, 기존 모든 Refresh Token은 무효화됩니다.
    """,
    responses={
        200: {"description": "회원 탈퇴 완료"},
        401: {"description": "인증 실패 (토큰 누락 또는 만료)"},
    },
)
async def delete_user_me(
    user: Annotated[User, Depends(get_request_user)],
    auth_service: Annotated[AuthService, Depends(AuthService)],
):
    await auth_service.withdraw(user=user)
    return {"detail": "탈퇴 처리되었습니다."}
