import asyncio

import httpx
from tortoise import Tortoise

from app.db.databases import TORTOISE_ORM
from app.models.chat_session import ChatSession
from app.models.users import User
from app.services.jwt import JwtService

BASE_URL = "http://localhost:8001"


async def test_sec_01_backend():
    print("🚀 [SEC-01] 보안 기본 점검 (Backend) QA 테스트 시작")
    await Tortoise.init(config=TORTOISE_ORM)

    # 1. 두 명의 사용자 준비
    user1 = await User.filter(email="new_qa_test@example.com").first()
    user2 = await User.filter(email="temp_sec_test@example.com").first()
    if not user2:
        user2 = await User.create(
            email="temp_sec_test@example.com", name="임시보안유저", is_active=True, is_verified=True
        )

    if not user1:
        print("❌ 테스트용 사용자(2명)가 부족합니다.")
        await Tortoise.close_connections()
        return

    jwt_service = JwtService()
    token1 = str(jwt_service.create_access_token(user1))
    # 2. User2의 채팅 세션 생성
    session2 = await ChatSession.create(user_id=user2.id)
    print(f"💡 User2의 세션 생성됨 (ID: {session2.id})")

    async with httpx.AsyncClient(timeout=10.0) as client:
        # User1의 토큰으로 User2의 세션 조회를 시도 (SEC-01-3)
        print(f"\n[SEC-01-3] 타 사용자의 세션 ID({session2.id})로 API 직접 호출 테스트")
        headers = {"Authorization": f"Bearer {token1}"}
        resp = await client.get(f"{BASE_URL}/api/v1/chat/sessions/{session2.id}", headers=headers)

        if resp.status_code in [403, 404]:
            print(f"✅ 결과: 접근 차단 성공 ({resp.status_code}, {resp.text})")
        else:
            print(f"❌ 결과: 보안 취약점 발견! ({resp.status_code})")

    await Tortoise.close_connections()
    print("\n✨ 모든 [SEC-01] Backend QA 테스트 완료")


if __name__ == "__main__":
    asyncio.run(test_sec_01_backend())
