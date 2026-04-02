from datetime import date, datetime
from typing import Annotated

from pydantic import BaseModel, EmailStr, Field

from app.dtos.base import BaseSerializerModel
from app.models.users import Gender
from app.validators.common import optional_after_validator
from app.validators.user_validators import validate_birthday, validate_phone_number


# 1. 회원가입 요청 DTO (사용자가 보내는 데이터 검증)
class UserCreateRequest(BaseModel):
    email: Annotated[EmailStr, Field(..., max_length=40, description="사용자 이메일")]
    password: Annotated[str, Field(..., min_length=8, description="비밀번호 (최소 8자)")]
    name: Annotated[str, Field(..., min_length=2, max_length=20)]
    phone_number: Annotated[
        str,
        Field(..., description="Available Format: 01011112222, 010-1111-2222"),
        validate_phone_number  # 필수값 검증
    ]
    birthday: Annotated[
        date,
        Field(..., description="Date Format: YYYY-MM-DD"),
        validate_birthday  # 필수값 검증
    ]
    gender: Annotated[Gender, Field(..., description="'MALE' or 'FEMALE'")]

    # --- 새로 추가된 동의 필드 (가입 시 필수) ---
    agree_terms: Annotated[bool, Field(..., description="이용약관 동의 여부")]
    agree_privacy: Annotated[bool, Field(..., description="개인정보 처리방침 동의 여부")]


# 2. 유저 정보 수정 DTO (기본 템플릿 유지)
class UserUpdateRequest(BaseModel):
    name: Annotated[str | None, Field(None, min_length=2, max_length=20)]
    email: Annotated[EmailStr | None, Field(None, max_length=40)]
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
    gender: Annotated[Gender, Field(None, description="'MALE' or 'FEMALE'")]


# 3. 유저 정보 응답 DTO (DB 데이터를 사용자에게 보여줄 때)
class UserInfoResponse(BaseSerializerModel):
    id: int
    name: str
    email: str
    phone_number: str
    birthday: date
    gender: Gender
    # 응답에도 동의 여부를 포함하고 싶다면 아래를 추가하세요.
    agree_terms: bool
    agree_privacy: bool
    created_at: datetime