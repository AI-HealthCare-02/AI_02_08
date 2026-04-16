import json
from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.dependencies.security import get_request_user
from app.dtos.users import UserInfoResponse, UserUpdateRequest
from app.models.users import User
from app.services.auth import AuthService
from app.services.users import UserManageService

user_router = APIRouter(prefix="/users", tags=["users"])


@user_router.get(
    "/me",
    response_model=UserInfoResponse,
    status_code=status.HTTP_200_OK,
    summary="내 정보 조회",
    description="""
현재 로그인한 사용자의 정보를 조회합니다.

- **Authorization 헤더에 Access Token이 필요합니다.**
- 카카오 로그인 유저의 경우 이메일, 전화번호, 생년월일, 성별이 없을 수 있습니다.
    """,
    responses={
        200: {"description": "내 정보 반환"},
        401: {"description": "인증 실패 (토큰 누락 또는 만료)"},
    },
)
async def user_me_info(
    user: Annotated[User, Depends(get_request_user)],
) -> JSONResponse:
    return JSONResponse(
        content=json.loads(UserInfoResponse.model_validate(user).model_dump_json()),
        status_code=status.HTTP_200_OK,
    )


@user_router.patch(
    "/me",
    response_model=UserInfoResponse,
    status_code=status.HTTP_200_OK,
    summary="내 정보 수정",
    description="""
현재 로그인한 사용자의 정보를 수정합니다.

- **Authorization 헤더에 Access Token이 필요합니다.**
- 수정 가능한 항목: 이름, 이메일, 전화번호, 생년월일, 성별
- 수정하지 않을 항목은 요청 바디에서 제외하거나 `null`로 전달하세요.
    """,
    responses={
        200: {"description": "수정된 내 정보 반환"},
        401: {"description": "인증 실패 (토큰 누락 또는 만료)"},
        422: {"description": "입력값 유효성 검증 실패"},
    },
)
async def update_user_me_info(
    update_data: UserUpdateRequest,
    user: Annotated[User, Depends(get_request_user)],
    user_manage_service: Annotated[UserManageService, Depends(UserManageService)],
) -> JSONResponse:
    updated_user = await user_manage_service.update_user(user=user, data=update_data)
    return JSONResponse(
        content=json.loads(UserInfoResponse.model_validate(updated_user).model_dump_json()),
        status_code=status.HTTP_200_OK,
    )


@user_router.delete(
    "/me",
    status_code=status.HTTP_200_OK,
    summary="회원 탈퇴",
    description="""
현재 로그인한 사용자의 계정을 탈퇴 처리합니다.

- **Authorization 헤더에 Access Token이 필요합니다.**
- 탈퇴는 **소프트 딜리트** 방식으로 처리됩니다. (DB에서 즉시 삭제되지 않음)
- 탈퇴 후 동일 이메일/카카오 계정으로 재가입이 가능합니다.
- 탈퇴 시 모든 Refresh Token이 무효화됩니다.
    """,
    responses={
        200: {"description": "회원 탈퇴 완료"},
        401: {"description": "인증 실패 (토큰 누락 또는 만료)"},
    },
)
async def delete_user_me(
    user: Annotated[User, Depends(get_request_user)],
    auth_service: Annotated[AuthService, Depends(AuthService)],
) -> JSONResponse:
    await auth_service.withdraw(user=user)
    return JSONResponse(
        content={"detail": "탈퇴 처리되었습니다."},
        status_code=status.HTTP_200_OK,
    )
