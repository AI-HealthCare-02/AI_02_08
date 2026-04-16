from datetime import date, datetime
from typing import Annotated

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.dtos.base import BaseSerializerModel
from app.models.users import Gender
from app.validators.common import optional_after_validator
from app.validators.user_validators import validate_birth_date, validate_phone_number


# 1. 회원가입 요청 DTO
class UserCreateRequest(BaseModel):
    email: Annotated[EmailStr, Field(..., max_length=255, description="사용자 이메일")]
    password: Annotated[str, Field(..., min_length=8, description="비밀번호 (최소 8자)")]
    name: Annotated[str, Field(..., min_length=2, max_length=20, description="사용자 이름 (2~20자)")]
    phone_number: Annotated[
        str,
        Field(..., description="전화번호 (01011112222 또는 010-1111-2222 형식)"),
        validate_phone_number,
    ]
    birth_date: Annotated[
        date,
        Field(..., description="생년월일 (YYYY-MM-DD 형식)"),
        validate_birth_date,
    ]
    gender: Annotated[Gender, Field(..., description="성별 (MALE 또는 FEMALE)")]
    agree_terms: Annotated[bool, Field(..., description="이용약관 동의 여부 (필수)")]
    agree_privacy: Annotated[bool, Field(..., description="개인정보 처리방침 동의 여부 (필수)")]

    @field_validator("agree_terms", "agree_privacy")
    @classmethod
    def must_be_agreed(cls, v: bool) -> bool:
        if not v:
            raise ValueError("필수 약관에 동의해야 합니다.")
        return v


# 2. 유저 정보 수정 DTO
class UserUpdateRequest(BaseModel):
    name: Annotated[str | None, Field(None, min_length=2, max_length=20, description="변경할 이름 (2~20자)")]
    email: Annotated[EmailStr | None, Field(None, max_length=255, description="변경할 이메일")]
    phone_number: Annotated[
        str | None,
        Field(None, description="변경할 전화번호 (01011112222 또는 010-1111-2222 형식)"),
        optional_after_validator(validate_phone_number),
    ]
    birth_date: Annotated[
        date | None,
        Field(None, description="변경할 생년월일 (YYYY-MM-DD 형식)"),
        optional_after_validator(validate_birth_date),
    ]
    gender: Annotated[Gender | None, Field(None, description="변경할 성별 (MALE 또는 FEMALE)")]


# 3. 유저 정보 응답 DTO
class UserInfoResponse(BaseSerializerModel):
    id: Annotated[int, Field(..., description="유저 고유 ID")]
    name: Annotated[str, Field(..., description="사용자 이름")]
    email: Annotated[str | None, Field(None, description="이메일 (카카오 로그인 유저는 없을 수 있음)")]
    phone_number: Annotated[str | None, Field(None, description="전화번호 (카카오 로그인 유저는 없을 수 있음)")]
    birthday: Annotated[date | None, Field(None, description="생년월일 (카카오 로그인 유저는 없을 수 있음)")]
    gender: Annotated[Gender | None, Field(None, description="성별 (카카오 로그인 유저는 없을 수 있음)")]
    agree_terms: Annotated[bool, Field(..., description="이용약관 동의 여부")]
    agree_privacy: Annotated[bool, Field(..., description="개인정보 처리방침 동의 여부")]
    created_at: Annotated[datetime, Field(..., description="계정 생성일시")]
