from httpx import ASGITransport, AsyncClient
from starlette import status
from tortoise.contrib.test import TestCase

from app.main import app


class TestLoginAPI(TestCase):
    async def test_login_success(self):
        # 먼저 사용자 등록
        signup_data = {
            "email": "login_test@example.com",
            "password": "Password123!",
            "name": "testuser",
            "gender": "FEMALE",
            "birth_date": "1995-05-05",
            "phone_number": "01011112222",
        }
        login_data = {"email": "login_test@example.com", "password": "Password123!"}

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # 1. 회원가입 시도 및 결과 확인
            signup_response = await client.post("/api/v1/auth/signup", json=signup_data)
            if signup_response.status_code != 201:
                # 회원가입이 실패했다면 그 이유(Validation Error 등)를 출력합니다.
                print(f"\n[DEBUG] Signup Failed: {signup_response.json()}")

            # 2. 로그인 시도
            response = await client.post("/api/v1/auth/login", json=login_data)
            if response.status_code != 200:
                print(f"\n[DEBUG] Login Failed: {response.json()}")
    async def test_login_invalid_credentials(self):
        login_data = {"email": "nonexistent@example.com", "password": "WrongPassword123!"}
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/v1/auth/login", json=login_data)

        # AuthService.authenticate 에서 실패 시 HTTP_400_BAD_REQUEST 발생
        assert response.status_code == status.HTTP_400_BAD_REQUEST
