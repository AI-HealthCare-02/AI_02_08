from datetime import date
from typing import Annotated

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
    description="""
사용자가 선택한 특정 날짜에 등록된 복약 기록 목록을 반환합니다.

- 날짜 기준으로 당일 자정~23:59:59 범위 내에 생성된 기록을 조회합니다.
- 동일 약품명의 중복 기록은 자동으로 제거되어 반환됩니다.
- 각 항목에는 삭제 API 호출에 사용할 **`id`** 필드가 포함됩니다.
    """,
    responses={
        200: {"description": "조회 성공 (결과 없으면 빈 배열 반환)"},
        401: {"description": "인증 실패 (Access Token 누락 또는 만료)"},
        422: {"description": "날짜 형식 오류 — YYYY-MM-DD 형식으로 전달해야 합니다."},
    },
)
async def get_medication_history(
    date: date,
    current_user: Annotated[User, Depends(get_request_user)],
):
    """
    특정 날짜의 복약 히스토리 조회 API
    - date: YYYY-MM-DD 형식 (예: 2026-04-27)
    """
    service = MedicationService()
    history_data = await service.get_medication_history_by_date(current_user.id, date)
    return history_data


# ──────────────────────────────────────────────
# 2. 복약 기록 삭제 API
# ──────────────────────────────────────────────
@router.delete(
    "/{medication_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="복약 기록 삭제",
    description="""
복약 리스트에서 특정 약물 기록을 **영구 삭제(Hard Delete)** 합니다.

- 히스토리 조회(`GET /medications/history`) 응답의 `id` 값을 사용합니다.
- 본인 소유의 기록만 삭제할 수 있으며, 타인의 기록 접근 시 `403`을 반환합니다.
- 삭제 성공 시 응답 바디 없이 `204 No Content`를 반환합니다.
    """,
    responses={
        204: {"description": "삭제 성공 (응답 바디 없음)"},
        401: {"description": "인증 실패 (Access Token 누락 또는 만료)"},
        403: {"description": "권한 없음 — 본인 소유의 기록이 아닙니다."},
        404: {"description": "해당 복약 기록을 찾을 수 없음"},
    },
)
async def delete_medication(
    medication_id: int,
    current_user: Annotated[User, Depends(get_request_user)],
):
    """
    복약 기록 삭제 API
    - medication_id: 삭제할 복약 기록의 고유 ID (히스토리 조회 응답의 id 값)
    """
    service = MedicationService()
    await service.delete_medication(medication_id, current_user.id)
