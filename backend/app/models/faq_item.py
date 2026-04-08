from tortoise import fields, models


class FaqItem(models.Model):
    id = fields.BigIntField(primary_key=True)
    question = fields.CharField(max_length=255)
    answer = fields.TextField()
    display_order = fields.IntField(default=0)
    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "faq_items"
        ordering = ["display_order"]