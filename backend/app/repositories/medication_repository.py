from datetime import date, datetime, timedelta

from app.models.medications import MedicationLog, OcrPrescription


class MedicationRepository:
    def __init__(self):
        self._model = MedicationLog

    async def get_by_date(self, user_id: int, target_date: date) -> list[dict]:
        """
        특정 날짜에 OCR로 분석된 처방전 목록 조회
        """
        # 해당 날짜의 시작과 끝 시간
        start_datetime = datetime.combine(target_date, datetime.min.time())
        end_datetime = datetime.combine(target_date, datetime.max.time())

        # OCR 처방전 조회 (해당 날짜에 생성된 것)
        ocr_prescriptions = await OcrPrescription.filter(
            user_id=user_id, created_at__gte=start_datetime, created_at__lte=end_datetime
        ).order_by("-created_at")

        result = []
        for ocr in ocr_prescriptions:
            # 해당 OCR과 연결된 약물 목록 조회
            medications = await MedicationLog.filter(ocr_prescription_id=ocr.ocr_id).values(
                "name", "dosage", "frequency", "timing", "start_date", "end_date"
            )

            result.append(
                {"ocr_id": ocr.ocr_id, "created_at": ocr.created_at.isoformat(), "medications": medications}
            )

        return result