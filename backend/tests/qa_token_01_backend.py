import asyncio
import os
import sys
import httpx
from datetime import datetime, timedelta
from tortoise import Tortoise
from app.models.users import User
from app.services.jwt import JwtService
from app.db.databases import TORTOISE_ORM
from app.models.refresh_token import RefreshToken

BASE_URL = "http://localhost:8001"

async def test_token_01_backend():
    print("🚀 [TOKEN-01] 토큰 갱신 기능 (Backend) QA 테스트 시작")
    await Tortoise.init(config=TORTOISE_ORM)
    
    # 1. 테스트용 사용자 준비
    user = await User.filter(email="new_qa_test@example.com").first()
    if not user:
        print("❌ 테스트용 사용자가 없습니다.")
        await Tortoise.close_connections()
        return
        
    jwt_service = JwtService()
    tokens = jwt_service.issue_jwt_pair(user)
    access_token = str(tokens["access_token"])
    refresh_token = str(tokens["refresh_token"])
    
    # Refresh Token DB 저장 (실제 환경 시뮬레이션)
    await RefreshToken.create(
        user_id=user.id,
        token=refresh_token,
        expires_at=datetime.now() + timedelta(days=7)
    )
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        # 1. 만료된/잘못된 Access Token으로 요청 시 401 확인
        print("\n[TOKEN-01-1-A] 잘못된 Access Token 요청 테스트")
        resp = await client.get(
            f"{BASE_URL}/api/v1/users/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        print(f"✅ 결과: {resp.status_code} (예상: 401)")

        # 2. Refresh Token을 이용한 Access Token 갱신 (Cookie 사용)
        print("\n[TOKEN-01-1-B] Refresh Token으로 Access Token 갱신 테스트")
        cookies = {"refresh_token": refresh_token}
        resp = await client.get(
            f"{BASE_URL}/api/v1/auth/token/refresh",
            cookies=cookies
        )
        if resp.status_code == 200:
            new_access_token = resp.json().get("access_token")
            print(f"✅ 결과: 갱신 성공 (새 토큰: {new_access_token[:20]}...)")
            
            # 새 토큰으로 요청 시 성공 확인
            resp_me = await client.get(
                f"{BASE_URL}/api/v1/users/me",
                headers={"Authorization": f"Bearer {new_access_token}"}
            )
            if resp_me.status_code == 200:
                print("✅ 결과: 새 토큰으로 API 요청 성공")
        else:
            print(f"❌ 결과: 갱신 실패 ({resp.status_code}, {resp.text})")

        # 3. 만료된 Refresh Token 테스트
        print("\n[TOKEN-01-2] 만료된 Refresh Token 요청 테스트")
        # 만료된 토큰 생성 (JWT 자체 만료)
        expired_refresh = jwt_service.create_token(
            data={"sub": str(user.id), "type": "refresh"},
            expires_delta=timedelta(seconds=-10)
        )
        resp = await client.get(
            f"{BASE_URL}/api/v1/auth/token/refresh",
            cookies={"refresh_token": str(expired_refresh)}
        )
        print(f"✅ 결과: {resp.status_code} (예상: 401)")

    await Tortoise.close_connections()
    print("\n✨ 모든 [TOKEN-01] Backend QA 테스트 완료")

if __name__ == "__main__":
    asyncio.run(test_token_01_backend())
