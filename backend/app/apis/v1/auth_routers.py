import json
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from starlette.responses import Response

from app.core.config import Config, Env
from app.dependencies.security import get_request_user
from app.dtos.auth import (
    ChangePasswordRequest,
    LoginRequest,
    LoginResponse,
    PasswordResetEmailRequest,
    PasswordResetRequest,
    ResendVerificationRequest,
    SignUpRequest,
    TokenRefreshResponse,
)
from app.models.users import User
from app.services.auth import AuthService
from app.services.jwt import JwtService
from app.services.kakao_auth import get_kakao_token, get_kakao_user_info

config = Config()
auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post(
    "/signup",
    status_code=status.HTTP_201_CREATED,
    summary="회원가입",
    description="""
이메일과 비밀번호로 회원가입합니다.

- 회원가입 완료 후 입력한 이메일로 **6자리 인증 코드**가 발송됩니다.
- 이메일 인증 완료 후 로그인이 가능합니다.
- 비밀번호는 **대소문자, 숫자, 특수문자를 각 1개 이상 포함한 8자 이상**이어야 합니다.
    """,
    responses={
        201: {"description": "회원가입 성공 및 인증 이메일 발송 완료"},
        409: {"description": "이미 사용중인 이메일 또는 전화번호"},
        422: {"description": "입력값 유효성 검증 실패"},
    },
)
async def signup(
    request: SignUpRequest,
    auth_service: Annotated[AuthService, Depends(AuthService)],
) -> JSONResponse:
    await auth_service.signup(request)
    return JSONResponse(
        content={"detail": "회원가입이 성공적으로 완료되었습니다. 이메일을 확인해주세요."},
        status_code=status.HTTP_201_CREATED,
    )


@auth_router.get(
    "/verify-email",
    status_code=status.HTTP_200_OK,
    summary="이메일 인증",
    description="""
회원가입 시 발송된 인증 코드로 이메일을 인증합니다.

- 인증 코드는 **24시간** 동안 유효합니다.
- 인증 코드 입력은 발송 후 **5분 이내**에 완료해야 합니다.
- 인증 완료 후 로그인이 가능합니다.
    """,
    responses={
        200: {"description": "이메일 인증 완료"},
        400: {"description": "인증 코드 불일치 또는 만료"},
        404: {"description": "인증 코드를 찾을 수 없음"},
    },
)
async def verify_email(
    email: Annotated[str, Query(description="인증할 이메일")],
    code: Annotated[str, Query(description="6자리 인증 코드")],
    auth_service: Annotated[AuthService, Depends(AuthService)],
) -> JSONResponse:
    await auth_service.verify_email(email=email, code=code)
    return JSONResponse(
        content={"detail": "이메일 인증이 완료되었습니다."},
        status_code=status.HTTP_200_OK,
    )


@auth_router.post(
    "/resend-verification",
    status_code=status.HTTP_200_OK,
    summary="인증 이메일 재발송",
    description="""
이메일 인증 코드를 재발송합니다.

- 이미 인증된 이메일은 재발송이 불가합니다.
- 기존 인증 코드는 무효화되고 새 코드가 발송됩니다.
    """,
    responses={
        200: {"description": "인증 이메일 재발송 완료"},
        400: {"description": "이미 인증된 이메일"},
        404: {"description": "존재하지 않는 이메일"},
    },
)
async def resend_verification(
    request: ResendVerificationRequest,
    auth_service: Annotated[AuthService, Depends(AuthService)],
) -> JSONResponse:
    await auth_service.resend_verification_email(email=request.email)
    return JSONResponse(
        content={"detail": "인증 이메일을 재발송했습니다."},
        status_code=status.HTTP_200_OK,
    )


@auth_router.get(
    "/check-email",
    status_code=status.HTTP_200_OK,
    summary="이메일 중복 확인",
    description="""
회원가입 전 이메일 중복 여부를 확인합니다.

- 탈퇴한 계정의 이메일은 사용 가능한 것으로 표시됩니다.
    """,
    responses={
        200: {"description": "중복 여부 반환 (is_duplicate: true/false)"},
    },
)
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


@auth_router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="로그인",
    description="""
이메일과 비밀번호로 로그인합니다.

- 로그인 성공 시 **Access Token**이 응답 바디로 반환됩니다.
- **Refresh Token**은 HttpOnly 쿠키로 자동 저장됩니다.
- 이메일 인증이 완료된 계정만 로그인이 가능합니다.
    """,
    responses={
        200: {"description": "로그인 성공, Access Token 반환 및 Refresh Token 쿠키 설정"},
        400: {"description": "이메일 또는 비밀번호 불일치"},
        403: {"description": "이메일 인증 미완료"},
        423: {"description": "비활성화된 계정 (탈퇴 처리된 계정)"},
    },
)
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


@auth_router.get(
    "/token/refresh",
    response_model=TokenRefreshResponse,
    status_code=status.HTTP_200_OK,
    summary="Access Token 갱신",
    description="""
Refresh Token으로 새로운 Access Token을 발급합니다.

- Refresh Token은 쿠키에서 자동으로 읽어옵니다.
- Refresh Token의 유효기간은 **14일**입니다.
    """,
    responses={
        200: {"description": "새로운 Access Token 반환"},
        401: {"description": "Refresh Token 누락 또는 만료"},
    },
)
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


@auth_router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="로그아웃",
    description="""
로그아웃합니다.

- 쿠키에 저장된 Refresh Token이 DB에서 삭제됩니다.
- Refresh Token 쿠키가 제거됩니다.
    """,
    responses={
        200: {"description": "로그아웃 성공"},
    },
)
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


@auth_router.post(
    "/password/reset-request",
    status_code=status.HTTP_200_OK,
    summary="비밀번호 재설정 이메일 발송",
    description="""
비밀번호 재설정을 위한 인증 코드를 이메일로 발송합니다.

- 인증 코드는 **5분** 동안 유효합니다.
- 존재하지 않는 이메일로 요청해도 보안상 동일하게 성공 응답을 반환합니다.
    """,
    responses={
        200: {"description": "비밀번호 재설정 이메일 발송 완료"},
    },
)
async def password_reset_request(
    request: PasswordResetEmailRequest,
    auth_service: Annotated[AuthService, Depends(AuthService)],
) -> JSONResponse:
    await auth_service.send_password_reset_email(email=request.email)
    return JSONResponse(
        content={"detail": "비밀번호 재설정 링크를 이메일로 발송했습니다."},
        status_code=status.HTTP_200_OK,
    )


@auth_router.post(
    "/password/reset",
    status_code=status.HTTP_200_OK,
    summary="비밀번호 재설정",
    description="""
인증 코드로 비밀번호를 재설정합니다.

- 인증 코드는 5분 이내에 발급된 코드여야 합니다.
- 재설정 완료 후 기존 모든 Refresh Token이 무효화됩니다.
    """,
    responses={
        200: {"description": "비밀번호 재설정 완료"},
        400: {"description": "인증 코드 불일치 또는 만료"},
        404: {"description": "인증 코드를 찾을 수 없음"},
    },
)
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


@auth_router.patch(
    "/password/change",
    status_code=status.HTTP_200_OK,
    summary="비밀번호 변경",
    description="""
로그인 상태에서 현재 비밀번호를 확인 후 새 비밀번호로 변경합니다.

- 현재 비밀번호와 동일한 비밀번호로는 변경이 불가합니다.
- 변경 완료 후 기존 모든 Refresh Token이 무효화됩니다.
- **Authorization 헤더에 Access Token이 필요합니다.**
    """,
    responses={
        200: {"description": "비밀번호 변경 완료"},
        400: {"description": "현재 비밀번호 불일치 또는 동일한 비밀번호로 변경 시도"},
        401: {"description": "인증 실패 (토큰 누락 또는 만료)"},
    },
)
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


@auth_router.get(
    "/kakao/callback",
    status_code=status.HTTP_200_OK,
    summary="카카오 로그인 콜백",
    description="""
카카오 OAuth 로그인 콜백을 처리합니다.

1. 카카오 인증 코드로 카카오 액세스 토큰 발급
2. 카카오 액세스 토큰으로 유저 정보 조회
3. DB에 없으면 **자동 회원가입**, 있으면 **바로 로그인**
4. JWT 발급 (Access Token 응답, Refresh Token 쿠키 설정)
    """,
    responses={
        200: {"description": "카카오 로그인 성공"},
        400: {"description": "카카오 인증 실패"},
    },
)
async def kakao_callback(
    code: Annotated[str, Query(description="카카오 인증 코드")],
    auth_service: Annotated[AuthService, Depends(AuthService)],
) -> Response:
    try:
        kakao_access_token = await get_kakao_token(code)
        kakao_user_info = await get_kakao_user_info(kakao_access_token)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"카카오 로그인 실패: {str(e)}") from e

    user = await auth_service.kakao_login(kakao_user_info)
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
