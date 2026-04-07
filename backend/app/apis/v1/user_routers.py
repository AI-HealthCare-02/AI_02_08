import json
from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.dependencies.security import get_request_user
from app.dtos.users import ChangePasswordRequest, UserInfoResponse, UserUpdateRequest
from app.models.users import User
from app.services.auth import AuthService
from app.services.users import UserManageService

user_router = APIRouter(prefix="/users", tags=["users"])


@user_router.get("/me", response_model=UserInfoResponse, status_code=status.HTTP_200_OK)
async def user_me_info(
    user: Annotated[User, Depends(get_request_user)],
) -> JSONResponse:
    return JSONResponse(
        content=json.loads(UserInfoResponse.model_validate(user).model_dump_json()),
        status_code=status.HTTP_200_OK,
    )


@user_router.patch("/me", response_model=UserInfoResponse, status_code=status.HTTP_200_OK)
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


@user_router.patch("/me/password", status_code=status.HTTP_200_OK)
async def change_password(
    request: ChangePasswordRequest,
    user: Annotated[User, Depends(get_request_user)],
    auth_service: Annotated[AuthService, Depends(AuthService)],
) -> JSONResponse:
    await auth_service.change_password(
        user=user,
        current_password=request.current_password,
        new_password=request.new_password,
    )
    return JSONResponse(
        content={"detail": "비밀번호가 변경되었습니다."},
        status_code=status.HTTP_200_OK,
    )


@user_router.delete("/me", status_code=status.HTTP_200_OK)
async def delete_user_me(
    user: Annotated[User, Depends(get_request_user)],
    auth_service: Annotated[AuthService, Depends(AuthService)],
) -> JSONResponse:
    await auth_service.withdraw(user=user)
    return JSONResponse(
        content={"detail": "탈퇴 처리되었습니다."},
        status_code=status.HTTP_200_OK,
    )
