from enum import StrEnum

from tortoise import fields, models


class SenderType(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"


class ChatMessage(models.Model):
    id = fields.BigIntField(primary_key=True)
    session = fields.ForeignKeyField(
        "models.ChatSession",
        related_name="messages",
        on_delete=fields.CASCADE,
    )
    sender = fields.CharEnumField(enum_type=SenderType)
    content = fields.TextField()
    is_faq = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "chat_messages"
