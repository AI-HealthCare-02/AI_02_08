import asyncio
import os
import sys
import httpx
from tortoise import Tortoise
from app.models.users import User
from app.services.jwt import JwtService
from app.db.databases import TORTOISE_ORM
from app.models.medications import OcrPrescription, MedicationLog, OcrStatus

BASE_URL = "http://localhost:8001"

async def test_ocr_03_backend():
    print("🚀 [OCR-03] OCR → 복약관리 확정 (Backend) QA 테스트 시작")
    await Tortoise.init(config=TORTOISE_ORM)
    
    # 1. 토큰 생성 및 데이터 준비
    user = await User.filter(email="new_qa_test@example.com").first()
    if not user:
        print("❌ 테스트용 사용자가 없습니다.")
        await Tortoise.close_connections()
        return
        
    token_obj = JwtService().create_access_token(user)
    headers = {"Authorization": f"Bearer {token_obj}"}
    
    # 가상의 OCR 레코드 생성
    ocr_id = "test_ocr_confirm_123"
    await OcrPrescription.filter(ocr_id=ocr_id).delete()
    await OcrPrescription.create(
        ocr_id=ocr_id,
        user_id=user.id,
        image_url="http://example.com/test.jpg",
        status=OcrStatus.PENDING,
        extracted_data={"parsed": [{"name": "타이레놀", "dosage": "500mg"}]}
    )
    
    async with httpx.AsyncClient(headers=headers, timeout=10.0) as client:
        # 1. OCR 결과 확정 테스트 (OCR-03-1)
        print("\n[OCR-03-1] OCR 결과 확정 API 테스트")
        confirm_payload = {
            "medications": [
                {"name": "타이레놀", "dosage": "500mg", "frequency": "1일 3회", "timing": "식후 30분"}
            ]
        }
        resp = await client.post(f"{BASE_URL}/api/v1/ai/ocr/prescription/{ocr_id}/confirm", json=confirm_payload)
        
        if resp.status_code == 201:
            data = resp.json()
            print(f"✅ 결과: 확정 성공 (등록 건수: {data.get('registeredCount')})")
            
            # DB 확인
            med_logs = await MedicationLog.filter(ocr_prescription_id=ocr_id)
            if len(med_logs) == 1:
                print(f"✅ 결과: MedicationLog DB 저장 확인 ({med_logs[0].name})")
            else:
                print("❌ 결과: DB 저장 실패")
        else:
            print(f"❌ 결과: 확정 실패 ({resp.status_code}, {resp.text})")

        # 2. 존재하지 않는 OCR ID 테스트 (OCR-03-4 예외케이스)
        print("\n[OCR-03-4 예외] 존재하지 않는 OCR ID 확정 테스트")
        resp = await client.post(f"{BASE_URL}/api/v1/ai/ocr/prescription/invalid_id/confirm", json=confirm_payload)
        if resp.status_code == 404:
            print("✅ 결과: 404 Not Found 정상 발생")
        else:
            print(f"❌ 결과: 예외 처리 실패 ({resp.status_code})")

    await Tortoise.close_connections()
    print("\n✨ 모든 [OCR-03] Backend QA 테스트 완료")

if __name__ == "__main__":
    asyncio.run(test_ocr_03_backend())
