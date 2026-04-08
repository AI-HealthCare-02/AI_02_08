from tortoise import fields, models


class ChatSession(models.Model):
    id = fields.BigIntField(primary_key=True)
    user = fields.ForeignKeyField(
        "models.User",
        related_name="chat_sessions",
        on_delete=fields.CASCADE,
    )
    ocr = fields.ForeignKeyField(
        "models.OcrPrescription",
        related_name="chat_sessions",
        on_delete=fields.SET_NULL,
        null=True,
    )
    message_count = fields.IntField(default=0)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "chat_sessions"