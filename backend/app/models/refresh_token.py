from tortoise import fields, models


class RefreshToken(models.Model):
    id = fields.BigIntField(primary_key=True)
    user = fields.ForeignKeyField(
        "models.User",
        related_name="refresh_tokens",
        on_delete=fields.CASCADE,
    )
    token = fields.CharField(max_length=512, unique=True)
    expires_at = fields.DatetimeField()
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "refresh_tokens"
