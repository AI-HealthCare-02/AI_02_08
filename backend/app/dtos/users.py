from datetime import date, datetime
from typing import Annotated

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.dtos.base import BaseSerializerModel
from app.models.users import Gender
from app.validators.common import optional_after_validator
from app.validators.user_validators import validate_birthday, validate_phone_number


# 1. 회원가입 요청 DTO (사용자가 보내는 데이터 검증)
class UserCreateRequest(BaseModel):
    email: Annotated[EmailStr, Field(..., max_length=255, description="사용자 이메일")]
    password: Annotated[str, Field(..., min_length=8, description="비밀번호 (최소 8자)")]
    name: Annotated[str, Field(..., min_length=2, max_length=20)]
    phone_number: Annotated[
        str,
        Field(..., description="Available Format: 01011112222, 010-1111-2222"),
        validate_phone_number,
    ]
    birthday: Annotated[date, Field(..., description="Date Format: YYYY-MM-DD"), validate_birthday]
    gender: Annotated[Gender, Field(..., description="'MALE' or 'FEMALE'")]

    agree_terms: Annotated[bool, Field(..., description="이용약관 동의 여부")]
    agree_privacy: Annotated[bool, Field(..., description="개인정보 처리방침 동의 여부")]

    @field_validator("agree_terms", "agree_privacy")
    @classmethod
    def must_be_agreed(cls, v: bool) -> bool:
        if not v:
            raise ValueError("필수 약관에 동의해야 합니다.")
        return v


# 2. 유저 정보 수정 DTO
class UserUpdateRequest(BaseModel):
    name: Annotated[str | None, Field(None, min_length=2, max_length=20)]
    email: Annotated[EmailStr | None, Field(None, max_length=255)]
    phone_number: Annotated[
        str | None,
        Field(None, description="Available Format: +8201011112222, 01011112222, 010-1111-2222"),
        optional_after_validator(validate_phone_number),
    ]
    birthday: Annotated[
        date | None,
        Field(None, description="Date Format: YYYY-MM-DD"),
        optional_after_validator(validate_birthday),
    ]
    gender: Annotated[Gender | None, Field(None, description="'MALE' or 'FEMALE'")]


# 3. 유저 정보 응답 DTO
class UserInfoResponse(BaseSerializerModel):
    id: int
    name: str
    email: str
    phone_number: str
    birthday: date
    gender: Gender
    agree_terms: bool
    agree_privacy: bool
    created_at: datetime
