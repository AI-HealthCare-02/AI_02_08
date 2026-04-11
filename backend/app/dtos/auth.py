from datetime import date
from typing import Annotated

from pydantic import AfterValidator, BaseModel, EmailStr, Field, field_validator

from app.models.users import Gender
from app.validators.user_validators import validate_birth_date, validate_password, validate_phone_number


class SignUpRequest(BaseModel):
    email: Annotated[
        EmailStr,
        Field(..., max_length=255),
    ]
    password: Annotated[str, Field(min_length=8), AfterValidator(validate_password)]
    name: Annotated[str, Field(max_length=20)]
    gender: Gender
    birth_date: Annotated[date, AfterValidator(validate_birth_date)]
    phone_number: Annotated[str, AfterValidator(validate_phone_number)]
    agree_terms: Annotated[bool, Field(..., description="이용약관 동의 여부")]
    agree_privacy: Annotated[bool, Field(..., description="개인정보 처리방침 동의 여부")]

    @field_validator("agree_terms", "agree_privacy")
    @classmethod
    def must_be_agreed(cls, v: bool) -> bool:
        if not v:
            raise ValueError("필수 약관에 동의해야 합니다.")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: Annotated[str, Field(min_length=8)]


class LoginResponse(BaseModel):
    access_token: str


class TokenRefreshResponse(LoginResponse): ...


class VerifyEmailRequest(BaseModel):
    email: Annotated[EmailStr, Field(..., description="인증할 이메일")]
    code: Annotated[str, Field(..., min_length=6, max_length=6, description="6자리 인증 코드")]


class ResendVerificationRequest(BaseModel):
    email: Annotated[EmailStr, Field(..., description="인증 이메일 재발송할 이메일")]


class LogoutRequest(BaseModel):
    refresh_token: Annotated[str, Field(..., description="로그아웃할 리프레시 토큰")]


class PasswordResetEmailRequest(BaseModel):
    email: Annotated[EmailStr, Field(..., description="비밀번호 재설정 이메일 발송할 이메일")]


class PasswordResetRequest(BaseModel):
    email: Annotated[EmailStr, Field(..., description="비밀번호 재설정할 이메일")]
    code: Annotated[str, Field(..., min_length=6, max_length=6, description="6자리 인증 코드")]
    new_password: Annotated[str, Field(..., min_length=8), AfterValidator(validate_password)]
    new_password_confirm: Annotated[str, Field(..., min_length=8)]

    @field_validator("new_password_confirm")
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        if "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("비밀번호가 일치하지 않습니다.")
        return v


class ChangePasswordRequest(BaseModel):
    current_password: Annotated[str, Field(..., min_length=8, description="현재 비밀번호")]
    new_password: Annotated[str, Field(..., min_length=8), AfterValidator(validate_password)]
    new_password_confirm: Annotated[str, Field(..., min_length=8)]

    @field_validator("new_password_confirm")
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        if "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("비밀번호가 일치하지 않습니다.")
        return v
