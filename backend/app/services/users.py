from datetime import datetime

from tortoise.transactions import in_transaction

from app.dtos.users import TermsAgreementRequest, UserUpdateRequest  # 🆕 추가
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

    # 약관 동의 처리 메서드 추가
    async def agree_terms(self, user: User, agreement: TermsAgreementRequest) -> User:
        """약관 동의 처리"""
        user.agree_terms = agreement.agree_terms
        user.agree_privacy = agreement.agree_privacy
        user.agreed_at = datetime.now()
        await user.save(update_fields=["agree_terms", "agree_privacy", "agreed_at"])
        await user.refresh_from_db()
        return user
