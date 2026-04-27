from datetime import date

from app.dependencies.security import get_request_user
from fastapi import APIRouter, Depends

from app.models.users import User
from app.services.medication_service import MedicationService

router = APIRouter(prefix="/medications", tags=["Medications"])


# ruff: noqa: B008
@router.get("/history")
async def get_medication_history(
    date: date,
    current_user: User = Depends(get_request_user),  # 변수명은 그대로
):
    """
    특정 날짜의 복약 히스토리 조회

    - date: YYYY-MM-DD 형식 (예: 2026-04-27)
    """
    service = MedicationService()
    history = await service.get_medication_history_by_date(current_user.id, date)
    return history
