from tortoise import fields, models


class DrugInfo(models.Model):
    id = fields.BigIntField(primary_key=True)
    name = fields.CharField(max_length=200, description="약품명")
    manufacturer = fields.CharField(max_length=200, null=True, description="제조사")
    efficacy = fields.TextField(null=True, description="효능")
    usage = fields.TextField(null=True, description="복용법")
    warning = fields.TextField(null=True, description="경고")
    precautions = fields.TextField(null=True, description="주의사항")
    interactions = fields.TextField(null=True, description="상호작용")
    side_effects = fields.TextField(null=True, description="부작용")
    storage = fields.TextField(null=True, description="보관법")
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "drugs"

    def __str__(self) -> str:
        return self.name
