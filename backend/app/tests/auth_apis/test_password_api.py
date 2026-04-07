from unittest.mock import AsyncMock, patch

from httpx import ASGITransport, AsyncClient
from starlette import status
from tortoise.contrib.test import TestCase

from app.main import app


class TestPasswordAPI(TestCase):
    async def test_password_reset_request_success(self):
        signup_data = {
            "email": "reset_test@example.com",
            "password": "Password123!",
            "name": "비번재설정테스터",
            "gender": "MALE",
            "birth_date": "1990-01-01",
            "phone_number": "01077778888",
            "agree_terms": True,
            "agree_privacy": True,
        }

        with patch("app.services.email.EmailService.send_verification_email", new_callable=AsyncMock):
            with patch("app.services.email.EmailService.send_password_reset_email", new_callable=AsyncMock):
                async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                    await client.post("/api/v1/auth/signup", json=signup_data)
                    response = await client.post(
                        "/api/v1/auth/password/reset-request",
                        json={"email": "reset_test@example.com"},
                    )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"detail": "비밀번호 재설정 링크를 이메일로 발송했습니다."}

    async def test_password_reset_request_nonexistent_email(self):
        with patch("app.services.email.EmailService.send_password_reset_email", new_callable=AsyncMock):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/auth/password/reset-request",
                    json={"email": "nonexistent@example.com"},
                )
        # 보안상 존재하지 않는 이메일도 200 반환
        assert response.status_code == status.HTTP_200_OK

    async def test_password_reset_success(self):
        signup_data = {
            "email": "reset_confirm@example.com",
            "password": "Password123!",
            "name": "비번확인테스터",
            "gender": "FEMALE",
            "birth_date": "1995-05-05",
            "phone_number": "01033334444",
            "agree_terms": True,
            "agree_privacy": True,
        }

        with patch("app.services.email.EmailService.send_verification_email", new_callable=AsyncMock):
            with patch("app.services.email.EmailService.send_password_reset_email", new_callable=AsyncMock):
                async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                    await client.post("/api/v1/auth/signup", json=signup_data)

                    await client.post(
                        "/api/v1/auth/password/reset-request",
                        json={"email": "reset_confirm@example.com"},
                    )

                    # DB에서 직접 코드 조회
                    from app.models.email_verification import EmailVerification, VerificationType

                    verification = await EmailVerification.filter(
                        email="reset_confirm@example.com",
                        type=VerificationType.PASSWORD_RESET,
                    ).first()

                    response = await client.post(
                        "/api/v1/auth/password/reset",
                        json={
                            "email": "reset_confirm@example.com",
                            "code": verification.code,
                            "new_password": "NewPassword123!",
                            "new_password_confirm": "NewPassword123!",
                        },
                    )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"detail": "비밀번호가 재설정되었습니다."}
