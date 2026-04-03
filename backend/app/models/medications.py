from enum import StrEnum

from tortoise import fields, models


# ──────────────────────────────────────────────
# Enum 정의
# ──────────────────────────────────────────────
class OcrStatus(StrEnum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"


class ReportPeriod(StrEnum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class ReportStatus(StrEnum):
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


# ──────────────────────────────────────────────
# 1. OCR 처방전 분석 결과 (원본 보관용)
# ──────────────────────────────────────────────
class OcrPrescription(models.Model):
    """
    POST /api/v1/ai/ocr/prescription 호출 시 생성.
    처방전 이미지의 OCR 원시 결과를 JSON 형태로 저장합니다.
    """

    ocr_id = fields.CharField(max_length=50, primary_key=True, description="UUID 형식 OCR ID (예: ocr_20260327_001)")
    user: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.User", related_name="ocr_prescriptions", on_delete=fields.CASCADE
    )
    image_url = fields.CharField(max_length=500, null=True, description="S3 원본 이미지 URL")
    status = fields.CharEnumField(enum_type=OcrStatus, default=OcrStatus.PENDING, description="분석 상태")
    extracted_data = fields.JSONField(null=True, description="클로바 OCR 추출 원시 JSON 데이터")
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "ocr_prescriptions"


# ──────────────────────────────────────────────
# 2. 복약 상세 및 스케줄 (확정 후 등록) - 기존 MEDICATIONS
# ──────────────────────────────────────────────
class MedicationLog(models.Model):
    """
    POST /api/v1/ai/ocr/prescription/{ocrId}/confirm 호출 시 생성.
    사용자가 검토·수정 후 확정한 개별 약물의 복약 스케줄 정보입니다.
    """

    id = fields.BigIntField(primary_key=True)
    user: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.User", related_name="medication_logs", on_delete=fields.CASCADE
    )
    ocr_prescription: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.OcrPrescription", related_name="medication_logs", on_delete=fields.SET_NULL, null=True
    )
    drug: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.DrugInfo",
        related_name="medication_logs",
        on_delete=fields.SET_NULL,
        null=True,
        description="공공데이터(drugs)와 매칭된 경우 FK",
    )
    name = fields.CharField(max_length=200, description="약품명 (OCR 추출값 또는 사용자 입력)")
    ingredient = fields.CharField(max_length=200, null=True, description="성분명")
    dosage = fields.CharField(max_length=100, null=True, description="용량 (예: 500mg)")
    frequency = fields.CharField(max_length=100, null=True, description="복용 횟수 (예: 1일 3회)")
    timing = fields.CharField(max_length=100, null=True, description="복용 시점 (예: 식후)")
    times = fields.IntField(null=True, description="총 투약 일수")
    stock = fields.IntField(null=True, description="잔여 수량")
    start_date = fields.DateField(null=True, description="복용 시작일")
    end_date = fields.DateField(null=True, description="복용 종료일")
    caution = fields.TextField(null=True, description="주의사항 메모")
    side_effects = fields.TextField(null=True, description="부작용 메모")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "medication_logs"


# ──────────────────────────────────────────────
# 3. 실제 복용 기록 (Intake Record)
# ──────────────────────────────────────────────
class MedicationIntakeLog(models.Model):
    """
    사용자가 실제로 약을 복용했는지 기록하는 테이블.
    """

    id = fields.BigIntField(primary_key=True)
    medication: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.MedicationLog", related_name="intake_logs", on_delete=fields.CASCADE
    )
    user: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.User", related_name="medication_intake_logs", on_delete=fields.CASCADE
    )
    scheduled_time = fields.DatetimeField(description="예정 복용 시각")
    taken_time = fields.DatetimeField(null=True, description="실제 복용 시각")
    status = fields.CharField(max_length=20, default="pending", description="taken / skipped / pending")
    opinion = fields.TextField(null=True, description="컨디션 또는 메모")

    class Meta:
        table = "medication_intake_logs"


# ──────────────────────────────────────────────
# 4. AI 리포트 (GPT-4o mini 분석 결과)
# ──────────────────────────────────────────────
class AiReport(models.Model):
    """
    POST /api/v1/ai/reports/generate 호출 시 생성.
    주간/월간 복약 데이터 및 컨디션 기록 기반 GPT-4o mini 분석 리포트.
    """

    report_id = fields.CharField(max_length=50, primary_key=True, description="UUID 형식 리포트 ID")
    user: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.User", related_name="ai_reports", on_delete=fields.CASCADE
    )
    period = fields.CharEnumField(enum_type=ReportPeriod, description="weekly / monthly")
    adherence_rate = fields.IntField(null=True, description="복약 준수율 (%)")
    condition_summary = fields.TextField(null=True, description="컨디션 요약 텍스트")
    medication_summary = fields.JSONField(null=True, description="약품별 복용률 JSON")
    ai_comment = fields.TextField(null=True, description="GPT가 생성한 종합 코멘트")
    status = fields.CharEnumField(enum_type=ReportStatus, default=ReportStatus.GENERATING, description="생성 상태")
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "ai_reports"
