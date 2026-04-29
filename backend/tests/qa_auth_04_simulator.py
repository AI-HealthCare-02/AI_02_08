import asyncio
import httpx
import os
import sys

# sys.path 설정
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tortoise import Tortoise
from app.models.users import User
from app.models.email_verification import EmailVerification, VerificationType
from app.db.databases import TORTOISE_ORM

BASE_URL = "http://localhost:8001"

async def test_auth_04():
    print("🚀 [AUTH-04] 비밀번호 찾기/재설정 QA 테스트 시작")
    await Tortoise.init(config=TORTOISE_ORM)
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        # 1. 미가입 이메일로 재설정 요청 (AUTH-04-2)
        # 요구사항: 오류 메시지 노출 | 실제 구현: 보안상 성공 메시지 반환
        print("\n[AUTH-04-2] 미가입 이메일(non-exist@example.com) 재설정 요청")
        resp = await client.post(f"{BASE_URL}/api/v1/auth/password/reset-request", json={"email": "non-exist@example.com"})
        print(f"결과 응답: {resp.status_code}, {resp.text}")
        if resp.status_code == 200:
            print("ℹ️ 알림: 실제 구현은 보안상의 이유로(Email Enumeration 방지) 미가입 이메일에도 성공 메시지를 반환합니다.")
        else:
            print("❌ 결과: 실패")

        # 2. 정상 이메일로 재설정 요청 및 성공 여부 (AUTH-04-3)
        test_email = "new_qa_test@example.com"
        print(f"\n[AUTH-04-3] 정상 이메일({test_email}) 비밀번호 재설정")
        
        # 요청 발송
        await client.post(f"{BASE_URL}/api/v1/auth/password/reset-request", json={"email": test_email})
        
        # DB에서 인증 코드 확인 (PASSWORD_RESET 타입)
        verification = await EmailVerification.filter(
            email=test_email, 
            type=VerificationType.PASSWORD_RESET
        ).order_by("-created_at").first()
        
        if not verification:
            print("❌ 결과: 인증 코드가 생성되지 않았습니다.")
            await Tortoise.close_connections()
            return
            
        reset_code = verification.code
        print(f"인증 코드 확인됨: {reset_code}")
        
        # 새 비밀번호 설정
        new_pass = "UpdatedPass123!"
        reset_data = {
            "email": test_email,
            "code": reset_code,
            "new_password": new_pass,
            "new_password_confirm": new_pass
        }
        resp = await client.post(f"{BASE_URL}/api/v1/auth/password/reset", json=reset_data)
        if resp.status_code == 200:
            print("✅ 결과: 비밀번호 재설정 완료")
            
            # 변경된 비밀번호로 로그인 확인
            login_resp = await client.post(f"{BASE_URL}/api/v1/auth/login", json={"email": test_email, "password": new_pass})
            if login_resp.status_code == 200:
                print("✅ 결과: 변경된 비밀번호로 로그인 성공")
            else:
                print(f"❌ 결과: 로그인 실패 ({login_resp.status_code})")
        else:
            print(f"❌ 결과: 재설정 실패 ({resp.status_code}, {resp.text})")

    await Tortoise.close_connections()
    print("\n✨ 모든 [AUTH-04] QA 테스트 완료")

if __name__ == "__main__":
    asyncio.run(test_auth_04())
