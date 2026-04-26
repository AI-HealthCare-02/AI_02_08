from tortoise import fields, models


class ChatIdempotency(models.Model):
    idempotency_key = fields.CharField(max_length=64, primary_key=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "chat_idempotencies"
