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

    async def delete_medication(self, medication_id: int, user_id: int) -> None:
        """
        복약 기록 삭제
        - 소유권 검증 후 삭제 수행
        """
        await self.medication_repo.delete(medication_id, user_id)
