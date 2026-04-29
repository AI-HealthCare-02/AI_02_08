from pydantic import Field

from app.dtos.base import BaseSerializerModel


# ──────────────────────────────────────────────
# OCR 관련 DTO
# ──────────────────────────────────────────────
class OcrMedicationItem(BaseSerializerModel):
    """OCR로 추출된 개별 약품 정보"""

    name: str = Field(..., description="약품명")
    dosage: str | None = Field(None, description="용량 (예: 500mg)")
    frequency: str | None = Field(None, description="복용 횟수 (예: 1일 3회)")
    timing: str | None = Field(None, description="복용 시점 (예: 식후)")
    description: str | None = Field(
        None, description="약품 한 줄 설명 (예: 해열진통제로 열을 내리고 통증을 줄여줍니다)"
    )


class OcrAnalyzeResponse(BaseSerializerModel):
    """POST /api/v1/ai/ocr/prescription 응답"""

    ocr_id: str = Field(..., alias="ocrId", description="생성된 OCR 레코드 ID")
    status: str = Field(..., description="success / failed")
    medications: list[OcrMedicationItem] = Field(default_factory=list)


# ──────────────────────────────────────────────
# OCR 확정 관련 DTO
# ──────────────────────────────────────────────
class OcrConfirmRequest(BaseSerializerModel):
    """POST /api/v1/ai/ocr/prescription/{ocrId}/confirm 요청 바디"""

    medications: list[OcrMedicationItem]


class OcrConfirmResponse(BaseSerializerModel):
    """POST /api/v1/ai/ocr/prescription/{ocrId}/confirm 응답"""

    message: str = "복약 일정이 등록되었습니다."
    registered_count: int = Field(..., alias="registeredCount")
    medication_ids: list[int] = Field(default_factory=list, alias="medicationIds")


# ──────────────────────────────────────────────
# 처방전 성분 분석 관련 DTO
# ──────────────────────────────────────────────
class DrugInteraction(BaseSerializerModel):
    drug1: str
    drug2: str
    risk: str = Field(..., description="위험도: 높음 / 보통 / 낮음")
    description: str


class PrescriptionAnalysisResponse(BaseSerializerModel):
    """GET /api/v1/ai/ocr/prescription/{ocrId}/analysis 응답"""

    interactions: list[DrugInteraction] = Field(default_factory=list)
    caution_ingredients: list[str] = Field(default_factory=list, alias="cautionIngredients")
    allergy_warnings: list[str] = Field(default_factory=list, alias="allergyWarnings")


# ──────────────────────────────────────────────
# AI 리포트 관련 DTO
# ──────────────────────────────────────────────
class ReportGenerateRequest(BaseSerializerModel):
    """POST /api/v1/ai/reports/generate 요청 바디"""

    period: str = Field(..., description="weekly | monthly")
    target_date: str = Field(..., alias="targetDate", description="기준 날짜 (YYYY-MM-DD)")


class ReportGenerateResponse(BaseSerializerModel):
    """POST /api/v1/ai/reports/generate 응답"""

    report_id: str = Field(..., alias="reportId")
    status: str = "generating"
    estimated_seconds: int = Field(10, alias="estimatedSeconds")


class MedicationTakenRate(BaseSerializerModel):
    name: str
    taken_rate: int = Field(..., alias="takenRate")


class ReportDetailResponse(BaseSerializerModel):
    """GET /api/v1/ai/reports/{reportId} 응답"""

    report_id: str = Field(..., alias="reportId")
    period: str
    adherence_rate: int | None = Field(None, alias="adherenceRate")
    condition_summary: str | None = Field(None, alias="conditionSummary")
    medication_summary: list[MedicationTakenRate] = Field(default_factory=list, alias="medicationSummary")
    ai_comment: str | None = Field(None, alias="aiComment")
    created_at: str | None = Field(None, alias="createdAt")


class ReportListItem(BaseSerializerModel):
    report_id: str = Field(..., alias="reportId")
    period: str
    adherence_rate: int | None = Field(None, alias="adherenceRate")
    created_at: str | None = Field(None, alias="createdAt")


class ReportListResponse(BaseSerializerModel):
    """GET /api/v1/ai/reports 응답"""

    reports: list[ReportListItem] = Field(default_factory=list)
    total_count: int = Field(0, alias="totalCount")


# ──────────────────────────────────────────────
# 복약 히스토리 관련 DTO
# ──────────────────────────────────────────────
class MedicationHistoryItem(BaseSerializerModel):
    """특정 날짜의 복약 기록 정보"""

    id: int = Field(..., description="복약 기록 고유 ID (삭제 API 호출 시 사용)")
    name: str = Field(..., description="약품명")
    dosage: str = Field(..., description="용량")
    frequency: str = Field(..., description="복용 횟수")
    timing: str = Field(..., description="복용 시점")


class MedicationHistoryResponse(BaseSerializerModel):
    """GET /api/v1/medications/history 응답"""

    history: list[MedicationHistoryItem] = Field(default_factory=list)
