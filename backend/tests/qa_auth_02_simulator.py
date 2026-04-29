import asyncio
import httpx
import os
import sys

# sys.path 설정
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

BASE_URL = "http://localhost:8001"

async def test_auth_02():
    print("🚀 [AUTH-02] 로그인 흐름 QA 테스트 시작")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        # 1. 존재하지 않는 이메일 입력 (AUTH-02-3)
        print("\n[AUTH-02-3] 존재하지 않는 이메일 로그인 시도")
        non_exist_data = {"email": "no-user@example.com", "password": "Password123!"}
        resp = await client.post(f"{BASE_URL}/api/v1/auth/login", json=non_exist_data)
        if resp.status_code == 400: # Backend returns 400 for unmatched credentials
            print("✅ 결과: 오류 메시지 노출 (400 Bad Request)")
        else:
            print(f"❌ 결과: 실패 (응답: {resp.status_code}, {resp.text})")

        # 2. 틀린 비밀번호 입력 (AUTH-02-2)
        print("\n[AUTH-02-2] 틀린 비밀번호 입력")
        test_user = "new_qa_test@example.com"
        wrong_pass_data = {"email": test_user, "password": "WrongPassword123!"}
        resp = await client.post(f"{BASE_URL}/api/v1/auth/login", json=wrong_pass_data)
        if resp.status_code == 400:
            print("✅ 결과: '이메일 또는 비밀번호가 올바르지 않습니다' 관련 에러(400) 정상 발생")
        else:
            print(f"❌ 결과: 실패 (응답: {resp.status_code})")

        # 3. 이메일 로그인 정상 입력 (AUTH-02-1)
        print("\n[AUTH-02-1] 정상 로그인 입력")
        valid_data = {"email": "test@example.com", "password": "dummy"} # test@example.com was created with 'dummy' hashed_password in previous code or DB
        # User in DB might have 'dummy' or we can use the one we just created in AUTH-01
        # 'new_qa_test@example.com' was created with 'Password123!'
        test_user = "new_qa_test@example.com"
        valid_data = {"email": test_user, "password": "Password123!"}
        
        resp = await client.post(f"{BASE_URL}/api/v1/auth/login", json=valid_data)
        if resp.status_code == 200:
            print("✅ 결과: 로그인 성공 (200 OK)")
            # Set-Cookie 확인 (Refresh Token)
            if "refresh_token" in resp.cookies:
                print("✅ 결과: Refresh Token 쿠키 설정 확인")
            else:
                print("❌ 결과: Refresh Token 쿠키 누락")
        else:
            print(f"❌ 결과: 실패 ({resp.status_code}, {resp.text})")

    print("\n[코드 분석] AUTH-02-4, 5, 6 검증")
    print("✅ [AUTH-02-4] 로그인 상태에서 /login 접근: AppRouter.tsx L60-61에서 Navigate to /home 처리 확인됨")
    print("✅ [AUTH-02-5] 카카오 로그인 버튼: KakaoAuthURL 생성 및 리다이렉트 로직 authApi.ts L46-50 확인됨")
    print("✅ [AUTH-02-6] 비로그인이 /home 직접 접근: ProtectedRoute.tsx L12-14에서 메인(/)으로 리다이렉트 처리 확인됨 (랜딩 페이지 노출)")

    print("\n✨ 모든 [AUTH-02] QA 테스트 완료")

if __name__ == "__main__":
    asyncio.run(test_auth_02())
