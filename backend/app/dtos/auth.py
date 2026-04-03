from datetime import date
from typing import Annotated

from pydantic import AfterValidator, BaseModel, EmailStr, Field

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


class LoginRequest(BaseModel):
    email: EmailStr
    password: Annotated[str, Field(min_length=8)]


class LoginResponse(BaseModel):
    access_token: str


class TokenRefreshResponse(LoginResponse): ...
