from datetime import date, datetime, timedelta

from app.models.medications import MedicationLog


class MedicationRepository:
    def __init__(self):
        self._model = MedicationLog

    async def get_by_date(self, user_id: int, target_date: date) -> list[dict]:
        """
        특정 날짜에 추가된 약물 목록 조회 (약물명 기준 중복 제거)
        """
        start_datetime = datetime.combine(target_date, datetime.min.time())
        end_datetime = datetime.combine(target_date, datetime.max.time())

        medications = await MedicationLog.filter(
            user_id=user_id, created_at__gte=start_datetime, created_at__lte=end_datetime
        ).values("name", "dosage", "frequency", "timing")

        # 약물명 기준 중복 제거
        seen = set()
        unique_meds = []
        for med in medications:
            key = med["name"]
            if key not in seen:
                seen.add(key)
                # None 값을 빈 문자열로 변환
                unique_meds.append({
                    "name": med["name"] or "",
                    "dosage": med["dosage"] or "",
                    "frequency": med["frequency"] or "",
                    "timing": med["timing"] or ""
                })

        return unique_meds