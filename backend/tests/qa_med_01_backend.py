import asyncio
from datetime import date

import httpx
from tortoise import Tortoise

from app.db.databases import TORTOISE_ORM
from app.models.medications import MedicationLog
from app.models.users import User
from app.services.jwt import JwtService

BASE_URL = "http://localhost:8001"


async def test_med_01_backend():
    print("🚀 [MED-01] 복약 관리 기능 (Backend) QA 테스트 시작")
    await Tortoise.init(config=TORTOISE_ORM)

    # 1. 토큰 생성 및 데이터 준비
    user = await User.filter(email="new_qa_test@example.com").first()
    if not user:
        print("❌ 테스트용 사용자가 없습니다.")
        await Tortoise.close_connections()
        return

    token_obj = JwtService().create_access_token(user)
    headers = {"Authorization": f"Bearer {token_obj}"}

    # 오늘 날짜로 기록 생성 (MED-01-3용)
    today_str = date.today().isoformat()
    await MedicationLog.filter(user_id=user.id, name="QA용 테스트 약").delete()
    await MedicationLog.create(
        user_id=user.id,
        name="QA용 테스트 약",
        dosage="1정",
        frequency="1일 1회",
        timing="식후 30분",
        start_date=date.today(),
    )

    async with httpx.AsyncClient(headers=headers, timeout=10.0) as client:
        # 1. 기록이 있는 날 조회 (MED-01-2, 3)
        print(f"\n[MED-01-2, 3] 기록이 있는 날({today_str}) 조회 테스트")
        resp = await client.get(f"{BASE_URL}/api/v1/medications/history", params={"date": today_str})

        if resp.status_code == 200:
            data = resp.json()
            print(f"✅ 결과: 조회 성공 (건수: {len(data)})")
            if len(data) > 0:
                print(f"✅ 결과: 첫 번째 약물명 확인 ({data[0].get('name')})")
        else:
            print(f"❌ 결과: 조회 실패 ({resp.status_code}, {resp.text})")

        # 2. 기록이 없는 날 조회 (MED-01-4)
        past_date = "2020-01-01"
        print(f"\n[MED-01-4] 기록이 없는 날({past_date}) 조회 테스트")
        resp = await client.get(f"{BASE_URL}/api/v1/medications/history", params={"date": past_date})

        if resp.status_code == 200:
            data = resp.json()
            print(f"✅ 결과: 조회 성공 (건수: {len(data)})")
            if len(data) == 0:
                print("✅ 결과: 빈 목록 확인 (정상)")
        else:
            print(f"❌ 결과: 조회 실패 ({resp.status_code})")

    await Tortoise.close_connections()
    print("\n✨ 모든 [MED-01] Backend QA 테스트 완료")


if __name__ == "__main__":
    asyncio.run(test_med_01_backend())
