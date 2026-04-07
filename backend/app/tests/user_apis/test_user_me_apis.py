from unittest.mock import AsyncMock, patch

from httpx import ASGITransport, AsyncClient
from starlette import status
from tortoise.contrib.test import TestCase

from app.main import app
from app.models.users import User


class TestUserMeApis(TestCase):
    async def test_get_user_me_success(self):
        email = "me@example.com"
        signup_data = {
            "email": email,
            "password": "Password123!",
            "name": "내정보테스터",
            "gender": "FEMALE",
            "birth_date": "1992-02-02",
            "phone_number": "01055556666",
            "agree_terms": True,
            "agree_privacy": True,
        }
        with patch("app.services.email.EmailService.send_verification_email", new_callable=AsyncMock):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                await client.post("/api/v1/auth/signup", json=signup_data)

                user = await User.get(email=email)
                user.is_verified = True
                await user.save(update_fields=["is_verified"])

                login_response = await client.post(
                    "/api/v1/auth/login",
                    json={"email": email, "password": "Password123!"},
                )
                access_token = login_response.json()["access_token"]

                headers = {"Authorization": f"Bearer {access_token}"}
                response = await client.get("/api/v1/users/me", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["email"] == email
        assert response.json()["name"] == "내정보테스터"

    async def test_update_user_me_success(self):
        email = "update_me@example.com"
        signup_data = {
            "email": email,
            "password": "Password123!",
            "name": "수정전",
            "gender": "MALE",
            "birth_date": "1990-10-10",
            "phone_number": "01077778888",
            "agree_terms": True,
            "agree_privacy": True,
        }
        with patch("app.services.email.EmailService.send_verification_email", new_callable=AsyncMock):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                await client.post("/api/v1/auth/signup", json=signup_data)

                user = await User.get(email=email)
                user.is_verified = True
                await user.save(update_fields=["is_verified"])

                login_response = await client.post(
                    "/api/v1/auth/login",
                    json={"email": email, "password": "Password123!"},
                )
                access_token = login_response.json()["access_token"]

                headers = {"Authorization": f"Bearer {access_token}"}
                response = await client.patch(
                    "/api/v1/users/me",
                    json={"name": "수정후"},
                    headers=headers,
                )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["name"] == "수정후"

    async def test_get_user_me_unauthorized(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/users/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_change_password_success(self):
        email = "change_pw@example.com"
        signup_data = {
            "email": email,
            "password": "Password123!",
            "name": "비번변경테스터",
            "gender": "MALE",
            "birth_date": "1990-01-01",
            "phone_number": "01011112222",
            "agree_terms": True,
            "agree_privacy": True,
        }
        with patch("app.services.email.EmailService.send_verification_email", new_callable=AsyncMock):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                await client.post("/api/v1/auth/signup", json=signup_data)

                user = await User.get(email=email)
                user.is_verified = True
                await user.save(update_fields=["is_verified"])

                login_response = await client.post(
                    "/api/v1/auth/login",
                    json={"email": email, "password": "Password123!"},
                )
                access_token = login_response.json()["access_token"]

                headers = {"Authorization": f"Bearer {access_token}"}
                response = await client.patch(
                    "/api/v1/users/me/password",
                    json={
                        "current_password": "Password123!",
                        "new_password": "NewPassword123!",
                        "new_password_confirm": "NewPassword123!",
                    },
                    headers=headers,
                )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"detail": "비밀번호가 변경되었습니다."}

    async def test_change_password_wrong_current(self):
        email = "change_pw_fail@example.com"
        signup_data = {
            "email": email,
            "password": "Password123!",
            "name": "비번변경실패테스터",
            "gender": "FEMALE",
            "birth_date": "1995-05-05",
            "phone_number": "01033334444",
            "agree_terms": True,
            "agree_privacy": True,
        }
        with patch("app.services.email.EmailService.send_verification_email", new_callable=AsyncMock):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                await client.post("/api/v1/auth/signup", json=signup_data)

                user = await User.get(email=email)
                user.is_verified = True
                await user.save(update_fields=["is_verified"])

                login_response = await client.post(
                    "/api/v1/auth/login",
                    json={"email": email, "password": "Password123!"},
                )
                access_token = login_response.json()["access_token"]

                headers = {"Authorization": f"Bearer {access_token}"}
                response = await client.patch(
                    "/api/v1/users/me/password",
                    json={
                        "current_password": "WrongPassword123!",
                        "new_password": "NewPassword123!",
                        "new_password_confirm": "NewPassword123!",
                    },
                    headers=headers,
                )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_withdraw_success(self):
        email = "withdraw@example.com"
        signup_data = {
            "email": email,
            "password": "Password123!",
            "name": "탈퇴테스터",
            "gender": "MALE",
            "birth_date": "1990-01-01",
            "phone_number": "01099990000",
            "agree_terms": True,
            "agree_privacy": True,
        }
        with patch("app.services.email.EmailService.send_verification_email", new_callable=AsyncMock):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                await client.post("/api/v1/auth/signup", json=signup_data)

                user = await User.get(email=email)
                user.is_verified = True
                await user.save(update_fields=["is_verified"])

                login_response = await client.post(
                    "/api/v1/auth/login",
                    json={"email": email, "password": "Password123!"},
                )
                access_token = login_response.json()["access_token"]

                headers = {"Authorization": f"Bearer {access_token}"}
                response = await client.delete("/api/v1/users/me", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"detail": "탈퇴 처리되었습니다."}

        # 탈퇴 후 is_active False 확인
        withdrawn_user = await User.get(email=email)
        assert withdrawn_user.is_active is False
        assert withdrawn_user.deleted_at is not None
