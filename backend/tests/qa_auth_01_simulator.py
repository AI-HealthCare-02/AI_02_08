import asyncio
import os
import sys

import httpx

# sys.path 설정
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tortoise import Tortoise

from app.db.databases import TORTOISE_ORM
from app.models.email_verification import EmailVerification
from app.models.users import User

BASE_URL = "http://localhost:8001"


async def test_auth_01():
    print("🚀 [AUTH-01] 회원가입 흐름 QA 테스트 시작")
    await Tortoise.init(config=TORTOISE_ORM)

    async with httpx.AsyncClient(timeout=10.0) as client:
        # 1. 중복 이메일 체크 (AUTH-01-2)
        print("\n[AUTH-01-2] 이미 가입된 이메일 중복 확인")
        resp = await client.get(f"{BASE_URL}/api/v1/auth/check-email?email=test@example.com")
        if resp.json().get("is_duplicate") is True:
            print("✅ 결과: '이미 사용 중인 이메일' 로직 정상 작동 (is_duplicate: True)")
        else:
            print("❌ 결과: 실패")

        # 2. 회원가입 시도 (AUTH-01-3, 6, 7, 9 포함)
        test_email = "new_qa_test@example.com"
        print(f"\n--- 신규 사용자 가입 테스트 ({test_email}) ---")

        # 기존 데이터 삭제 (재테스트용)
        await User.filter(email=test_email).delete()
        await EmailVerification.filter(email=test_email).delete()

        # [AUTH-01-6] 비밀번호 8자 미만
        print("\n[AUTH-01-6] 비밀번호 8자 미만 입력 테스트")
        signup_data = {
            "email": test_email,
            "password": "short",
            "name": "QA테스터",
            "gender": "MALE",
            "birth_date": "1990-01-01",
            "phone_number": "01012345678",
            "agree_terms": True,
            "agree_privacy": True,
        }
        resp = await client.post(f"{BASE_URL}/api/v1/auth/signup", json=signup_data)
        if resp.status_code == 422:
            print("✅ 결과: 유효성 오류(422) 정상 발생")
        else:
            print(f"❌ 결과: 실패 (응답: {resp.status_code})")

        # [AUTH-01-9] 모든 필드 정상 입력 후 가입 완료
        print("\n[AUTH-01-9] 모든 필드 정상 입력 후 가입 완료")
        signup_data["password"] = "Password123!"
        resp = await client.post(f"{BASE_URL}/api/v1/auth/signup", json=signup_data)
        if resp.status_code == 201:
            print("✅ 결과: 회원가입 성공 (201 Created)")
        else:
            print(f"❌ 결과: 실패 ({resp.status_code}, {resp.text})")

        # 3. 이메일 인증 (AUTH-01-4, 5)
        # [AUTH-01-4] 잘못된 인증 코드
        print("\n[AUTH-01-4] 잘못된 인증 코드 입력 (999999)")
        resp = await client.get(f"{BASE_URL}/api/v1/auth/verify-email?email={test_email}&code=999999")
        if resp.status_code == 400:
            print("✅ 결과: 잘못된 인증코드 에러(400) 정상 발생")
        else:
            print(f"❌ 결과: 실패 (응답: {resp.status_code})")

        # [AUTH-01-5] 올바른 인증 코드
        verification = await EmailVerification.get(email=test_email)
        real_code = verification.code
        print(f"\n[AUTH-01-5] 올바른 인증 코드 입력 ({real_code})")
        resp = await client.get(f"{BASE_URL}/api/v1/auth/verify-email?email={test_email}&code={real_code}")
        if resp.status_code == 200:
            print("✅ 결과: 이메일 인증 완료 (200 OK)")
        else:
            print(f"❌ 결과: 실패 (응답: {resp.status_code})")

    await Tortoise.close_connections()
    print("\n✨ 모든 [AUTH-01] QA 테스트 완료")

    await Tortoise.close_connections()
    print("\n✨ 모든 [AUTH-01] QA 테스트 완료")


if __name__ == "__main__":
    asyncio.run(test_auth_01())
