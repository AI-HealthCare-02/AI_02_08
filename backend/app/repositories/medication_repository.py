from datetime import date, datetime

from fastapi import HTTPException, status

from app.models.medications import MedicationLog


class MedicationRepository:
    def __init__(self):
        self._model = MedicationLog

    async def get_by_date(self, user_id: int, target_date: date) -> list[dict]:
        print("\n📅 복약 히스토리 조회")
        print(f"   - user_id: {user_id}")
        print(f"   - target_date: {target_date}")
        """
        특정 날짜에 추가된 약물 목록 조회 (약물명 기준 중복 제거)
        """

        start_datetime = datetime.combine(target_date, datetime.min.time())
        end_datetime = datetime.combine(target_date, datetime.max.time())

        medications = await MedicationLog.filter(
            user_id=user_id, created_at__gte=start_datetime, created_at__lte=end_datetime
        ).values("id", "name", "dosage", "frequency", "timing")
        print(f"   - 조회 결과: {len(medications)}건")
        # 약물명 기준 중복 제거
        seen = set()
        unique_meds = []
        for med in medications:
            key = med["name"]
            if key not in seen:
                seen.add(key)
                unique_meds.append(
                    {
                        "id": med["id"],
                        "name": med["name"] or "",
                        "dosage": med["dosage"] or "",
                        "frequency": med["frequency"] or "",
                        "timing": med["timing"] or "",
                    }
                )
        print(f"   - 중복 제거 후: {len(unique_meds)}건\n")
        return unique_meds

    async def get_by_id(self, medication_id: int) -> MedicationLog | None:
        """개별 복약 기록 조회"""
        return await MedicationLog.get_or_none(id=medication_id)

    async def delete(self, medication_id: int, user_id: int) -> None:
        """
        복약 기록 삭제 (Hard Delete)
        - 본인 소유의 기록만 삭제 가능
        """
        medication = await MedicationLog.get_or_none(id=medication_id)
        if not medication:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 복약 기록을 찾을 수 없습니다.",
            )
        if medication.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="삭제 권한이 없습니다.",
            )
        await medication.delete()
