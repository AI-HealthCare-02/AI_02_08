from datetime import date

from app.repositories.medication_repository import MedicationRepository


class MedicationService:
    def __init__(self):
        self.medication_repo = MedicationRepository()

    async def get_medication_history_by_date(self, user_id: int, target_date: date) -> list[dict]:
        """
        특정 날짜의 복약 히스토리 조회
        """
        return await self.medication_repo.get_by_date(user_id, target_date)