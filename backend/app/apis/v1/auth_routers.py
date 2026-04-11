import json
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from starlette.responses import Response

from app.core.config import Config, Env
from app.dtos.auth import (
    LoginRequest,
    LoginResponse,
    PasswordResetEmailRequest,
    PasswordResetRequest,
    ResendVerificationRequest,
    SignUpRequest,
    TokenRefreshResponse,
)
from app.services.auth import AuthService
from app.services.jwt import JwtService

config = Config()
auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(
    request: SignUpRequest,
    auth_service: Annotated[AuthService, Depends(AuthService)],
) -> JSONResponse:
    await auth_service.signup(request)
    return JSONResponse(
        content={"detail": "회원가입이 성공적으로 완료되었습니다. 이메일을 확인해주세요."},
        status_code=status.HTTP_201_CREATED,
    )


@auth_router.get("/verify-email", status_code=status.HTTP_200_OK)
async def verify_email(
    email: Annotated[str, Query(description="인증할 이메일")],
    code: Annotated[str, Query(description="인증 코드")],
    auth_service: Annotated[AuthService, Depends(AuthService)],
) -> JSONResponse:
    await auth_service.verify_email(email=email, code=code)
    return JSONResponse(
        content={"detail": "이메일 인증이 완료되었습니다."},
        status_code=status.HTTP_200_OK,
    )


@auth_router.post("/resend-verification", status_code=status.HTTP_200_OK)
async def resend_verification(
    request: ResendVerificationRequest,
    auth_service: Annotated[AuthService, Depends(AuthService)],
) -> JSONResponse:
    await auth_service.resend_verification_email(email=request.email)
    return JSONResponse(
        content={"detail": "인증 이메일을 재발송했습니다."},
        status_code=status.HTTP_200_OK,
    )


@auth_router.get("/check-email", status_code=status.HTTP_200_OK)
async def check_email(
    email: Annotated[str, Query(description="중복 확인할 이메일")],
    auth_service: Annotated[AuthService, Depends(AuthService)],
) -> JSONResponse:
    is_duplicate = await auth_service.is_email_duplicate(email=email)
    return JSONResponse(
        content={
            "is_duplicate": is_duplicate,
            "message": "이미 사용중인 이메일입니다." if is_duplicate else "사용 가능한 이메일입니다.",
        },
        status_code=status.HTTP_200_OK,
    )


@auth_router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login(
    request: LoginRequest,
    auth_service: Annotated[AuthService, Depends(AuthService)],
) -> Response:
    user = await auth_service.authenticate(request)
    tokens = await auth_service.login(user)
    resp = Response(
        content=json.dumps(LoginResponse(access_token=str(tokens["access_token"])).model_dump()),
        media_type="application/json",
        status_code=status.HTTP_200_OK,
    )
    resp.set_cookie(
        key="refresh_token",
        value=str(tokens["refresh_token"]),
        httponly=True,
        secure=True if config.ENV == Env.PROD else False,
        domain=config.COOKIE_DOMAIN or None,
        expires=datetime.fromtimestamp(tokens["refresh_token"].payload["exp"], tz=UTC),
    )
    return resp


@auth_router.get("/token/refresh", response_model=TokenRefreshResponse, status_code=status.HTTP_200_OK)
async def token_refresh(
    jwt_service: Annotated[JwtService, Depends(JwtService)],
    refresh_token: Annotated[str | None, Cookie()] = None,
) -> JSONResponse:
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token is missing.")
    access_token = jwt_service.refresh_jwt(refresh_token)
    return JSONResponse(
        content=TokenRefreshResponse(access_token=str(access_token)).model_dump(),
        status_code=status.HTTP_200_OK,
    )


@auth_router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    auth_service: Annotated[AuthService, Depends(AuthService)],
    refresh_token: Annotated[str | None, Cookie()] = None,
) -> Response:
    if refresh_token:
        await auth_service.logout(refresh_token=refresh_token)
    resp = Response(
        content=json.dumps({"detail": "로그아웃되었습니다."}),
        media_type="application/json",
        status_code=status.HTTP_200_OK,
    )
    resp.delete_cookie(key="refresh_token")
    return resp


@auth_router.post("/password/reset-request", status_code=status.HTTP_200_OK)
async def password_reset_request(
    request: PasswordResetEmailRequest,
    auth_service: Annotated[AuthService, Depends(AuthService)],
) -> JSONResponse:
    await auth_service.send_password_reset_email(email=request.email)
    return JSONResponse(
        content={"detail": "비밀번호 재설정 링크를 이메일로 발송했습니다."},
        status_code=status.HTTP_200_OK,
    )


@auth_router.post("/password/reset", status_code=status.HTTP_200_OK)
async def password_reset(
    request: PasswordResetRequest,
    auth_service: Annotated[AuthService, Depends(AuthService)],
) -> JSONResponse:
    await auth_service.reset_password(
        email=request.email,
        code=request.code,
        new_password=request.new_password,
    )
    return JSONResponse(
        content={"detail": "비밀번호가 재설정되었습니다."},
        status_code=status.HTTP_200_OK,
    )
