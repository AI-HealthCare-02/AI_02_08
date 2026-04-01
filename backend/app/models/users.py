from enum import StrEnum
from tortoise import fields, models


class Gender(StrEnum):
    MALE = "MALE"
    FEMALE = "FEMALE"


class User(models.Model):
    # 수정된 부분: pk=True와 generated=True를 확실히 명시합니다.
    id = fields.BigIntField(pk=True, generated=True, description="고유 ID")

    email = fields.CharField(max_length=40, unique=True, index=True)
    hashed_password = fields.CharField(max_length=128)
    name = fields.CharField(max_length=20)
    gender = fields.CharEnumField(enum_type=Gender)
    birthday = fields.DateField()
    phone_number = fields.CharField(max_length=20)

    is_active = fields.BooleanField(default=True)
    is_admin = fields.BooleanField(default=False)
    is_verified = fields.BooleanField(default=False)

    last_login = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "users"