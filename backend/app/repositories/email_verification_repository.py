from datetime import datetime

from app.models.email_verification import EmailVerification, VerificationType


class EmailVerificationRepository:
    def __init__(self):
        self._model = EmailVerification

    async def create(
        self,
        user_id: int,
        email: str,
        code: str,
        verification_type: VerificationType,
        expires_at: datetime,
    ) -> EmailVerification:
        return await self._model.create(
            user_id=user_id,
            email=email,
            code=code,
            type=verification_type,
            expires_at=expires_at,
        )

    async def get_latest_by_email_and_type(
        self,
        email: str,
        verification_type: VerificationType,
    ) -> EmailVerification | None:
        return (
            await self._model.filter(
                email=email,
                type=verification_type,
                is_verified=False,
            )
            .order_by("-created_at")
            .first()
        )

    async def mark_as_verified(self, verification: EmailVerification) -> None:
        verification.is_verified = True
        await verification.save(update_fields=["is_verified"])

    async def delete_previous(
        self,
        email: str,
        verification_type: VerificationType,
    ) -> None:
        await self._model.filter(
            email=email,
            type=verification_type,
        ).delete()
