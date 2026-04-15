from enum import StrEnum

from tortoise import fields, models


class Gender(StrEnum):
    MALE = "MALE"
    FEMALE = "FEMALE"


class User(models.Model):
    id = fields.BigIntField(primary_key=True, generated=True)
    email = fields.CharField(max_length=255, unique=True, db_index=True, null=True)  # 카카오는 이메일 없을 수 있음
    hashed_password = fields.CharField(max_length=128, null=True)  # 카카오는 비밀번호 없음
    name = fields.CharField(max_length=20)
    gender = fields.CharEnumField(enum_type=Gender, null=True)  # 카카오는 성별 정보 없음
    birthday = fields.DateField(null=True)  # 카카오는 생년월일 없음
    phone_number = fields.CharField(max_length=13, null=True)  # 카카오는 전화번호 없음

    # 카카오 OAuth
    kakao_id = fields.CharField(max_length=50, null=True, unique=True, db_index=True)

    is_active = fields.BooleanField(default=True)
    is_admin = fields.BooleanField(default=False)
    is_verified = fields.BooleanField(default=False)

    agree_terms = fields.BooleanField(default=False, description="이용약관 동의 여부")
    agree_privacy = fields.BooleanField(default=False, description="개인정보 처리방침 동의 여부")

    last_login = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    deleted_at = fields.DatetimeField(null=True, description="탈퇴 일시")

    class Meta:
        table = "users"