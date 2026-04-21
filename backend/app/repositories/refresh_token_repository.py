from datetime import datetime

from app.models.refresh_token import RefreshToken


class RefreshTokenRepository:
    def __init__(self):
        self._model = RefreshToken

    async def create(
        self,
        user_id: int,
        token: str,
        expires_at: datetime,
    ) -> RefreshToken:
        return await self._model.create(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
        )

    async def get_by_token(self, token: str) -> RefreshToken | None:
        return await self._model.get_or_none(token=token)

    async def delete_by_token(self, token: str) -> None:
        await self._model.filter(token=token).delete()

    async def delete_by_user_id(self, user_id: int) -> None:
        await self._model.filter(user_id=user_id).delete()

    async def exists_by_token(self, token: str) -> bool:
        return await self._model.filter(token=token).exists()
