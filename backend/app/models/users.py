from enum import StrEnum

from tortoise import fields, models


class Gender(StrEnum):
    MALE = "MALE"
    FEMALE = "FEMALE"


class User(models.Model):
    # 수정된 부분: pk=True와 generated=True를 확실히 명시합니다.
    id = fields.BigIntField(primary_key=True, generated=True)
    email = fields.CharField(max_length=255, unique=True, db_index=True)
    hashed_password = fields.CharField(max_length=128)
    name = fields.CharField(max_length=20)
    gender = fields.CharEnumField(enum_type=Gender)
    birthday = fields.DateField()
    phone_number = fields.CharField(max_length=13)

    is_active = fields.BooleanField(default=True)
    is_admin = fields.BooleanField(default=False)
    is_verified = fields.BooleanField(default=False)

    agree_terms = fields.BooleanField(default=False, description="이용약관 동의 여부")
    agree_privacy = fields.BooleanField(default=False, description="개인정보 처리방침 동의 여부")

    last_login = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    # 소프트 딜리트를 위한 필드 (null=True여야 탈퇴 안 한 상태를 표현 가능)
    deleted_at = fields.DatetimeField(null=True, description="탈퇴 일시")

    class Meta:
        table = "users"
