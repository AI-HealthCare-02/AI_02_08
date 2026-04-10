from unittest.mock import AsyncMock, patch

from httpx import ASGITransport, AsyncClient
from starlette import status
from tortoise.contrib.test import TestCase

from app.main import app
from app.models.users import User


class TestLogoutAPI(TestCase):
    async def test_logout_success(self):
        signup_data = {
            "email": "logout_test@example.com",
            "password": "Password123!",
            "name": "로그아웃테스터",
            "gender": "MALE",
            "birth_date": "1990-01-01",
            "phone_number": "01055556666",
            "agree_terms": True,
            "agree_privacy": True,
        }

        with patch("app.services.email.EmailService.send_verification_email", new_callable=AsyncMock):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                await client.post("/api/v1/auth/signup", json=signup_data)

                user = await User.get(email="logout_test@example.com")
                user.is_verified = True
                await user.save(update_fields=["is_verified"])

                login_response = await client.post(
                    "/api/v1/auth/login",
                    json={"email": "logout_test@example.com", "password": "Password123!"},
                )

                set_cookie = login_response.headers.get("set-cookie")
                refresh_token = ""
                if set_cookie:
                    import re

                    match = re.search(r"refresh_token=([^;]+)", set_cookie)
                    if match:
                        refresh_token = match.group(1)

                response = await client.post(
                    "/api/v1/auth/logout",
                    json={"refresh_token": refresh_token},
                )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"detail": "로그아웃되었습니다."}

    async def test_logout_invalid_token(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            client.cookies["refresh_token"] = "invalid_token"
            response = await client.post("/api/v1/auth/logout")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
