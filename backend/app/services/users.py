from tortoise.transactions import in_transaction

from app.dtos.users import UserUpdateRequest
from app.models.users import User
from app.repositories.user_repository import UserRepository
from app.services.auth import AuthService
from app.utils.common import normalize_phone_number


class UserManageService:
    def __init__(self):
        self.repo = UserRepository()
        self.auth_service = AuthService()

    async def update_user(self, user: User, data: UserUpdateRequest) -> User:
        dump = data.model_dump(exclude_none=True)

        if "email" in dump:
            await self.auth_service.check_email_exists(dump["email"])
        if "phone_number" in dump:
            dump["phone_number"] = normalize_phone_number(dump["phone_number"])
            await self.auth_service.check_phone_number_exists(dump["phone_number"])

        async with in_transaction():
            await self.repo.update_instance(user=user, data=dump)
            await user.refresh_from_db()
        return user