import asyncio
import httpx
from datetime import date
from tortoise import Tortoise
from app.models.users import User
from app.models.medications import MedicationLog
from app.services.jwt import JwtService
from app.db.databases import TORTOISE_ORM

BASE_URL = "http://localhost:8001"

async def test_delete_medication():
    print("🚀 [MED-DELETE] 복약 기록 삭제 API 테스트 시작")
    await Tortoise.init(config=TORTOISE_ORM)
    
    user = await User.filter(email="new_qa_test@example.com").first()
    if not user:
        print("❌ 테스트용 사용자가 없습니다.")
        await Tortoise.close_connections()
        return
    
    token = str(JwtService().create_access_token(user))
    headers = {"Authorization": f"Bearer {token}"}
    
    # 테스트용 약물 레코드 생성
    test_med = await MedicationLog.create(
        user_id=user.id,
        name="삭제테스트약",
        dosage="100mg",
        frequency="1일 1회",
        timing="식후",
        start_date=date.today()
    )
    print(f"💡 테스트용 약물 생성됨 (ID: {test_med.id})")
    
    async with httpx.AsyncClient(headers=headers, timeout=10.0) as client:
        # 1. 히스토리 조회 시 id가 포함되는지 확인
        today = date.today().isoformat()
        print(f"\n[TEST-1] 히스토리 조회 시 id 필드 포함 확인")
        resp = await client.get(f"{BASE_URL}/api/v1/medications/history", params={"date": today})
        if resp.status_code == 200:
            data = resp.json()
            has_id = all("id" in item for item in data)
            print(f"✅ 결과: id 필드 포함 여부 = {has_id} (건수: {len(data)})")
        else:
            print(f"❌ 결과: 조회 실패 ({resp.status_code})")
        
        # 2. 정상 삭제
        print(f"\n[TEST-2] 정상 삭제 (ID: {test_med.id})")
        resp = await client.delete(f"{BASE_URL}/api/v1/medications/{test_med.id}")
        print(f"✅ 결과: {resp.status_code} (예상: 204)")
        
        # 3. 이미 삭제된 약물 다시 삭제 시도
        print(f"\n[TEST-3] 존재하지 않는 ID로 삭제 시도 (ID: {test_med.id})")
        resp = await client.delete(f"{BASE_URL}/api/v1/medications/{test_med.id}")
        print(f"✅ 결과: {resp.status_code} (예상: 404)")
        
        # 4. 타인 소유 약물 삭제 시도
        other_user = await User.filter(email="temp_sec_test@example.com").first()
        if other_user:
            other_med = await MedicationLog.create(
                user_id=other_user.id,
                name="타인의약",
                dosage="50mg",
                start_date=date.today()
            )
            print(f"\n[TEST-4] 타인 소유 약물 삭제 시도 (ID: {other_med.id})")
            resp = await client.delete(f"{BASE_URL}/api/v1/medications/{other_med.id}")
            print(f"✅ 결과: {resp.status_code} (예상: 403)")
            # 정리
            await other_med.delete()

    await Tortoise.close_connections()
    print("\n✨ [MED-DELETE] 테스트 완료")

if __name__ == "__main__":
    asyncio.run(test_delete_medication())
