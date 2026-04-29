from datetime import date

from fastapi import APIRouter, Depends, status

from app.dependencies.security import get_request_user
from app.dtos.medications import MedicationHistoryItem
from app.models.users import User
from app.services.medication_service import MedicationService

router = APIRouter(prefix="/medications", tags=["복약 정보 관리"])


# ──────────────────────────────────────────────
# 1. 복약 히스토리 조회 API
# ──────────────────────────────────────────────
@router.get(
    "/history",
    response_model=list[MedicationHistoryItem],
    status_code=status.HTTP_200_OK,
    summary="특정 날짜의 복약 히스토리 조회",
    description="사용자가 선택한 특정 날짜에 등록된 모든 복약 기록(약품명, 용량, 횟수 등)을 리스트 형태로 조회합니다.",
    responses={
        200: {"description": "조회 성공"},
        401: {"description": "인증 실패 (토큰 누락 또는 만료)"},
        422: {"description": "날짜 형식 오류 (YYYY-MM-DD)"},
    },
)
async def get_medication_history(
    date: date,
    current_user: User = Depends(get_request_user),  # noqa: B008
):
    """
    특정 날짜의 복약 히스토리 조회 API
    - date: YYYY-MM-DD 형식 (예: 2026-04-27)
    """
    service = MedicationService()
    history_data = await service.get_medication_history_by_date(current_user.id, date)
    return history_data
