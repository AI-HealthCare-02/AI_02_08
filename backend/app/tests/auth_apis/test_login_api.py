from unittest.mock import AsyncMock, patch

from httpx import ASGITransport, AsyncClient
from starlette import status
from tortoise.contrib.test import TestCase

from app.main import app
from app.models.users import User


class TestLoginAPI(TestCase):
    async def test_login_success(self):
        signup_data = {
            "email": "login_test@example.com",
            "password": "Password123!",
            "name": "로그인테스터",
            "gender": "FEMALE",
            "birth_date": "1995-05-05",
            "phone_number": "01011112222",
            "agree_terms": True,
            "agree_privacy": True,
        }
        login_data = {"email": "login_test@example.com", "password": "Password123!"}

        with patch("app.services.email.EmailService.send_verification_email", new_callable=AsyncMock):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                await client.post("/api/v1/auth/signup", json=signup_data)

                # 이메일 인증 완료 처리
                user = await User.get(email="login_test@example.com")
                user.is_verified = True
                await user.save(update_fields=["is_verified"])

                response = await client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == status.HTTP_200_OK
        assert "access_token" in response.json()
        assert any("refresh_token" in header for header in response.headers.get_list("set-cookie"))

    async def test_login_invalid_credentials(self):
        login_data = {"email": "nonexistent@example.com", "password": "WrongPassword123!"}
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
