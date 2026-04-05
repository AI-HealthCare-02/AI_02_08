from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse as Response

from app.core.config import Config, Env
from app.dtos.auth import (
    LoginRequest,
    LoginResponse,
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
) -> Response:
    await auth_service.signup(request)
    return Response(
        content={"detail": "회원가입이 성공적으로 완료되었습니다. 이메일을 확인해주세요."},
        status_code=status.HTTP_201_CREATED,
    )


@auth_router.get("/verify-email", status_code=status.HTTP_200_OK)
async def verify_email(
    email: Annotated[str, Query(description="인증할 이메일")],
    code: Annotated[str, Query(description="인증 코드")],
    auth_service: Annotated[AuthService, Depends(AuthService)],
) -> Response:
    await auth_service.verify_email(email=email, code=code)
    return Response(
        content={"detail": "이메일 인증이 완료되었습니다."},
        status_code=status.HTTP_200_OK,
    )


@auth_router.post("/resend-verification", status_code=status.HTTP_200_OK)
async def resend_verification(
    request: ResendVerificationRequest,
    auth_service: Annotated[AuthService, Depends(AuthService)],
) -> Response:
    await auth_service.resend_verification_email(email=request.email)
    return Response(
        content={"detail": "인증 이메일을 재발송했습니다."},
        status_code=status.HTTP_200_OK,
    )


@auth_router.get("/check-email", status_code=status.HTTP_200_OK)
async def check_email(
    email: Annotated[str, Query(description="중복 확인할 이메일")],
    auth_service: Annotated[AuthService, Depends(AuthService)],
) -> Response:
    is_duplicate = await auth_service.is_email_duplicate(email=email)
    return Response(
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
        content=LoginResponse(access_token=str(tokens["access_token"])).model_dump(),
        status_code=status.HTTP_200_OK,
    )
    resp.set_cookie(
        key="refresh_token",
        value=str(tokens["refresh_token"]),
        httponly=True,
        secure=True if config.ENV == Env.PROD else False,
        domain=config.COOKIE_DOMAIN or None,
        expires=tokens["access_token"].payload["exp"],
    )
    return resp


@auth_router.get("/token/refresh", response_model=TokenRefreshResponse, status_code=status.HTTP_200_OK)
async def token_refresh(
    jwt_service: Annotated[JwtService, Depends(JwtService)],
    refresh_token: Annotated[str | None, Cookie()] = None,
) -> Response:
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token is missing.")
    access_token = jwt_service.refresh_jwt(refresh_token)
    return Response(
        content=TokenRefreshResponse(access_token=str(access_token)).model_dump(),
        status_code=status.HTTP_200_OK,
    )
