from datetime import date
from typing import Annotated

from pydantic import AfterValidator, BaseModel, EmailStr, Field, field_validator

from app.models.users import Gender
from app.validators.user_validators import validate_birth_date, validate_password, validate_phone_number


class SignUpRequest(BaseModel):
    email: Annotated[
        EmailStr,
        Field(..., max_length=255, description="사용자 이메일 (로그인 ID로 사용)"),
    ]
    password: Annotated[
        str,
        Field(..., min_length=8, description="비밀번호 (대소문자, 숫자, 특수문자 각 1개 이상 포함 8자 이상)"),
        AfterValidator(validate_password),
    ]
    name: Annotated[str, Field(..., max_length=20, description="사용자 이름 (최대 20자)")]
    gender: Annotated[Gender, Field(..., description="성별 (MALE 또는 FEMALE)")]
    birth_date: Annotated[
        date,
        Field(..., description="생년월일 (YYYY-MM-DD 형식, 만 14세 이상)"),
        AfterValidator(validate_birth_date),
    ]
    phone_number: Annotated[
        str,
        Field(..., description="전화번호 (01011112222 또는 010-1111-2222 형식)"),
        AfterValidator(validate_phone_number),
    ]
    agree_terms: Annotated[bool, Field(..., description="이용약관 동의 여부 (필수 동의)")]
    agree_privacy: Annotated[bool, Field(..., description="개인정보 처리방침 동의 여부 (필수 동의)")]

    @field_validator("agree_terms", "agree_privacy")
    @classmethod
    def must_be_agreed(cls, v: bool) -> bool:
        if not v:
            raise ValueError("필수 약관에 동의해야 합니다.")
        return v


class LoginRequest(BaseModel):
    email: Annotated[EmailStr, Field(..., description="가입한 이메일")]
    password: Annotated[str, Field(..., min_length=8, description="비밀번호 (8자 이상)")]


class LoginResponse(BaseModel):
    access_token: Annotated[str, Field(..., description="JWT Access Token (유효기간 1시간)")]


class TokenRefreshResponse(LoginResponse): ...


class VerifyEmailRequest(BaseModel):
    email: Annotated[EmailStr, Field(..., description="인증할 이메일")]
    code: Annotated[str, Field(..., min_length=6, max_length=6, description="이메일로 발송된 6자리 인증 코드")]


class ResendVerificationRequest(BaseModel):
    email: Annotated[EmailStr, Field(..., description="인증 코드를 재발송할 이메일")]


class LogoutRequest(BaseModel):
    refresh_token: Annotated[str, Field(..., description="로그아웃할 Refresh Token")]


class PasswordResetEmailRequest(BaseModel):
    email: Annotated[EmailStr, Field(..., description="비밀번호 재설정 인증 코드를 받을 이메일")]


class PasswordResetRequest(BaseModel):
    email: Annotated[EmailStr, Field(..., description="비밀번호를 재설정할 이메일")]
    code: Annotated[
        str, Field(..., min_length=6, max_length=6, description="이메일로 발송된 6자리 인증 코드 (유효시간 5분)")
    ]
    new_password: Annotated[
        str,
        Field(..., min_length=8, description="새 비밀번호 (대소문자, 숫자, 특수문자 각 1개 이상 포함 8자 이상)"),
        AfterValidator(validate_password),
    ]
    new_password_confirm: Annotated[
        str, Field(..., min_length=8, description="새 비밀번호 확인 (new_password와 동일해야 함)")
    ]

    @field_validator("new_password_confirm")
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        if "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("비밀번호가 일치하지 않습니다.")
        return v


class ChangePasswordRequest(BaseModel):
    current_password: Annotated[str, Field(..., min_length=8, description="현재 비밀번호")]
    new_password: Annotated[
        str,
        Field(..., min_length=8, description="새 비밀번호 (대소문자, 숫자, 특수문자 각 1개 이상 포함 8자 이상)"),
        AfterValidator(validate_password),
    ]
    new_password_confirm: Annotated[
        str, Field(..., min_length=8, description="새 비밀번호 확인 (new_password와 동일해야 함)")
    ]

    @field_validator("new_password_confirm")
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        if "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("비밀번호가 일치하지 않습니다.")
        return v
