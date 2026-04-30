import json
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException, Query, Response, status

from app.core.config import Config, Env
from app.dependencies.security import get_request_user
from app.dtos.auth import (
    ChangePasswordRequest,
    KakaoAdditionalInfoRequest,
    LoginRequest,
    LoginResponse,
    PasswordResetEmailRequest,
    PasswordResetRequest,
    ResendVerificationRequest,
    SignUpRequest,
    TokenRefreshResponse,
)
from app.dtos.users import TermsAgreementRequest, UserUpdateRequest
from app.models.users import User
from app.services.auth import AuthService
from app.services.jwt import JwtService
from app.services.kakao_auth import get_kakao_token, get_kakao_user_info
from app.services.users import UserManageService

config = Config()
auth_router = APIRouter(prefix="/auth", tags=["회원 인증 및 계정 관리"])


def set_refresh_cookie(response: Response, refresh_token) -> None:
    """Refresh Token을 HttpOnly 쿠키로 설정하는 공통 함수"""
    response.set_cookie(
        key="refresh_token",
        value=str(refresh_token),
        httponly=True,
        secure=config.ENV == Env.PROD,
        domain=config.COOKIE_DOMAIN or None,
        expires=datetime.fromtimestamp(refresh_token.payload["exp"], tz=UTC),
        samesite="lax",
    )


# ──────────────────────────────────────────────
# 1. 일반 회원가입 및 이메일 인증
# ──────────────────────────────────────────────
@auth_router.post(
    "/signup",
    status_code=status.HTTP_201_CREATED,
    summary="회원가입",
    description="""
이메일과 비밀번호로 회원가입합니다.
- 회원가입 완료 후 입력한 이메일로 **6자리 인증 코드**가 발송됩니다.
- 이메일 인증 완료 후 로그인이 가능합니다.
    """,
    responses={
        201: {"description": "회원가입 성공 및 인증 이메일 발송 완료"},
        409: {"description": "이미 사용중인 이메일 또는 전화번호"},
    },
)
async def signup(
    request: SignUpRequest,
    auth_service: Annotated[AuthService, Depends(AuthService)],
):
    await auth_service.signup(request)
    return {"detail": "회원가입이 성공적으로 완료되었습니다. 이메일을 확인해주세요."}


@auth_router.get(
    "/verify-email",
    status_code=status.HTTP_200_OK,
    summary="이메일 인증",
    description="회원가입 시 발송된 인증 코드로 이메일을 인증합니다.",
    responses={
        200: {"description": "이메일 인증 완료"},
        400: {"description": "인증 코드 불일치 또는 만료"},
    },
)
async def verify_email(
    email: Annotated[str, Query(description="인증할 이메일")],
    code: Annotated[str, Query(description="6자리 인증 코드")],
    auth_service: Annotated[AuthService, Depends(AuthService)],
):
    await auth_service.verify_email(email=email, code=code)
    return {"detail": "이메일 인증이 완료되었습니다."}


@auth_router.post(
    "/resend-verification",
    status_code=status.HTTP_200_OK,
    summary="인증 이메일 재발송",
    description="이메일 인증 코드를 재발송합니다.",
)
async def resend_verification(
    request: ResendVerificationRequest,
    auth_service: Annotated[AuthService, Depends(AuthService)],
):
    await auth_service.resend_verification_email(email=request.email)
    return {"detail": "인증 이메일을 재발송했습니다."}


@auth_router.get(
    "/check-email",
    status_code=status.HTTP_200_OK,
    summary="이메일 중복 확인",
    description="회원가입 전 이메일 중복 여부를 확인합니다.",
)
async def check_email(
    email: Annotated[str, Query(description="중복 확인할 이메일")],
    auth_service: Annotated[AuthService, Depends(AuthService)],
):
    is_duplicate = await auth_service.is_email_duplicate(email=email)
    return {
        "is_duplicate": is_duplicate,
        "message": "이미 사용중인 이메일입니다." if is_duplicate else "사용 가능한 이메일입니다.",
    }


# ──────────────────────────────────────────────
# 2. 로그인 및 토큰 관리
# ──────────────────────────────────────────────
@auth_router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="로그인",
    description="""
이메일과 비밀번호로 로그인하여 Access Token을 발급받습니다.
- **Refresh Token**은 보안을 위해 HttpOnly 쿠키로 자동 설정됩니다.
    """,
    responses={
        200: {"description": "로그인 성공"},
        400: {"description": "이메일 또는 비밀번호 불일치"},
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
    set_refresh_cookie(resp, tokens["refresh_token"])
    return resp


@auth_router.get(
    "/token/refresh",
    response_model=TokenRefreshResponse,
    status_code=status.HTTP_200_OK,
    summary="Access Token 갱신",
    description="쿠키에 저장된 Refresh Token을 사용하여 새로운 Access Token을 발급합니다.",
)
async def token_refresh(
    jwt_service: Annotated[JwtService, Depends(JwtService)],
    refresh_token: Annotated[str | None, Cookie()] = None,
):
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token is missing.")
    access_token = jwt_service.refresh_jwt(refresh_token)
    return TokenRefreshResponse(access_token=str(access_token))


@auth_router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="로그아웃",
    description="세션을 종료하고 보관된 Refresh Token을 무효화합니다.",
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


# ──────────────────────────────────────────────
# 3. 비밀번호 재설정 및 변경
# ──────────────────────────────────────────────
@auth_router.post(
    "/password/reset-request",
    status_code=status.HTTP_200_OK,
    summary="비밀번호 재설정 이메일 발송",
    description="비밀번호 재설정을 위한 인증 코드를 이메일로 전송합니다.",
)
async def password_reset_request(
    request: PasswordResetEmailRequest,
    auth_service: Annotated[AuthService, Depends(AuthService)],
):
    await auth_service.send_password_reset_email(email=request.email)
    return {"detail": "비밀번호 재설정 링크를 이메일로 발송했습니다."}


@auth_router.post(
    "/password/reset",
    status_code=status.HTTP_200_OK,
    summary="비밀번호 재설정 완료",
    description="이메일로 받은 인증 코드를 확인하여 새 비밀번호를 설정합니다.",
)
async def password_reset(
    request: PasswordResetRequest,
    auth_service: Annotated[AuthService, Depends(AuthService)],
):
    await auth_service.reset_password(
        email=request.email,
        code=request.code,
        new_password=request.new_password,
    )
    return {"detail": "비밀번호가 재설정되었습니다."}


@auth_router.patch(
    "/password/change",
    status_code=status.HTTP_200_OK,
    summary="비밀번호 변경 (로그인 상태)",
    description="현재 비밀번호를 확인한 후 새 비밀번호로 교체합니다.",
    responses={
        200: {"description": "비밀번호 변경 완료"},
        400: {"description": "현재 비밀번호 불일치"},
    },
)
async def change_password(
    request: ChangePasswordRequest,
    user: Annotated[User, Depends(get_request_user)],
    auth_service: Annotated[AuthService, Depends(AuthService)],
):
    await auth_service.change_password(
        user=user,
        current_password=request.current_password,
        new_password=request.new_password,
    )
    return {"detail": "비밀번호가 변경되었습니다."}


# ──────────────────────────────────────────────
# 4. 카카오 소셜 로그인 연동
# ──────────────────────────────────────────────
@auth_router.get(
    "/kakao/callback",
    status_code=status.HTTP_200_OK,
    summary="카카오 로그인 콜백",
    description="카카오 인증 후 자동으로 회원가입 또는 로그인을 처리합니다.",
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

    user, is_new = await auth_service.kakao_login(kakao_user_info)
    tokens = await auth_service.login(user)

    requires_terms = not (user.agree_terms and user.agree_privacy)
    requires_additional_info = not all([user.gender, user.birthday, user.phone_number])

    resp = Response(
        content=json.dumps(
            {
                **LoginResponse(access_token=str(tokens["access_token"])).model_dump(),
                "is_new": is_new,
                "requires_terms_agreement": requires_terms,
                "requires_additional_info": requires_additional_info,
                "user_id": user.id,
            }
        ),
        media_type="application/json",
        status_code=status.HTTP_200_OK,
    )
    set_refresh_cookie(resp, tokens["refresh_token"])
    return resp


# ──────────────────────────────────────────────
# 5. 약관 동의 및 추가 정보 입력 (소셜 전용)
# ──────────────────────────────────────────────
@auth_router.post(
    "/terms/agree",
    status_code=status.HTTP_200_OK,
    summary="약관 동의 처리",
    description="소셜 로그인 후 필수 약관에 대한 동의를 저장합니다.",
)
async def agree_terms(
    request: TermsAgreementRequest,
    user: Annotated[User, Depends(get_request_user)],
    user_manage_service: Annotated[UserManageService, Depends(UserManageService)],
):
    await user_manage_service.agree_terms(user=user, agreement=request)
    return {"detail": "약관 동의가 완료되었습니다."}


@auth_router.patch(
    "/kakao/additional-info",
    status_code=status.HTTP_200_OK,
    summary="카카오 로그인 추가 정보 입력",
    description="성별, 생년월일 등 필수 추가 정보를 저장하여 가입을 완료합니다.",
)
async def kakao_additional_info(
    request: KakaoAdditionalInfoRequest,
    user: Annotated[User, Depends(get_request_user)],
    user_manage_service: Annotated[UserManageService, Depends(UserManageService)],
):
    await user_manage_service.update_user(
        user=user,
        data=UserUpdateRequest(
            gender=request.gender,
            birth_date=request.birth_date,
            phone_number=request.phone_number,
        ),
    )
    return {"detail": "추가 정보가 저장되었습니다."}
