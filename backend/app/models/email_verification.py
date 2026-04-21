from enum import StrEnum

from tortoise import fields, models


class VerificationType(StrEnum):
    SIGNUP = "SIGNUP"
    PASSWORD_RESET = "PASSWORD_RESET"


class EmailVerification(models.Model):
    id = fields.BigIntField(primary_key=True)
    user = fields.ForeignKeyField(
        "models.User",
        related_name="email_verifications",
        on_delete=fields.CASCADE,
    )
    email = fields.CharField(max_length=255)
    code = fields.CharField(max_length=64)
    type = fields.CharEnumField(enum_type=VerificationType)
    is_verified = fields.BooleanField(default=False)
    expires_at = fields.DatetimeField()
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "email_verifications"
