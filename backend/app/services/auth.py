import secrets
from datetime import datetime, timedelta

from fastapi.exceptions import HTTPException
from pydantic import EmailStr
from starlette import status
from tortoise.transactions import in_transaction

from app.core.config import Config
from app.dtos.auth import LoginRequest, SignUpRequest
from app.models.email_verification import EmailVerification, VerificationType
from app.models.users import User
from app.repositories.email_verification_repository import EmailVerificationRepository
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.user_repository import UserRepository
from app.services.email import EmailService
from app.services.jwt import JwtService
from app.utils.common import normalize_phone_number
from app.utils.jwt.tokens import AccessToken, RefreshToken
from app.utils.security import hash_password, verify_password

config = Config()


class AuthService:
    def __init__(self):
        self.user_repo = UserRepository()
        self.jwt_service = JwtService()
        self.email_verification_repo = EmailVerificationRepository()
        self.refresh_token_repo = RefreshTokenRepository()
        self.email_service = EmailService()

    async def signup(self, data: SignUpRequest) -> User:
        await self.check_email_exists(data.email)

        normalized_phone_number = normalize_phone_number(data.phone_number)
        await self.check_phone_number_exists(normalized_phone_number)

        async with in_transaction():
            user = await self.user_repo.create_user(
                email=data.email,
                hashed_password=hash_password(data.password),
                name=data.name,
                phone_number=normalized_phone_number,
                gender=data.gender,
                birthday=data.birth_date,
                agree_terms=data.agree_terms,
                agree_privacy=data.agree_privacy,
            )
            await self._send_verification_code(
                user_id=user.id,
                email=data.email,
                verification_type=VerificationType.SIGNUP,
            )
            return user

    async def verify_email(self, email: str, code: str) -> None:
        verification = await self.email_verification_repo.get_latest_by_email_and_type(
            email=email,
            verification_type=VerificationType.SIGNUP,
        )
        self._validate_verification(verification, code)

        async with in_transaction():
            await self.email_verification_repo.mark_as_verified(verification)
            user = await self.user_repo.get_user_by_email(email)
            if user:
                user.is_verified = True
                await user.save(update_fields=["is_verified"])

    async def resend_verification_email(self, email: str) -> None:
        user = await self.user_repo.get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="존재하지 않는 이메일입니다.")
        if user.is_verified:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="이미 인증된 이메일입니다.")

        await self.email_verification_repo.delete_previous(
            email=email,
            verification_type=VerificationType.SIGNUP,
        )
        await self._send_verification_code(
            user_id=user.id,
            email=email,
            verification_type=VerificationType.SIGNUP,
        )

    async def authenticate(self, data: LoginRequest) -> User:
        email = str(data.email)
        user = await self.user_repo.get_user_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="이메일 또는 비밀번호가 올바르지 않습니다."
            )
        if not verify_password(data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="이메일 또는 비밀번호가 올바르지 않습니다."
            )
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_423_LOCKED, detail="비활성화된 계정입니다.")
        if not user.is_verified:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="이메일 인증이 필요합니다.")

        return user

    async def login(self, user: User) -> dict[str, AccessToken | RefreshToken]:
        await self.user_repo.update_last_login(user.id)
        tokens = self.jwt_service.issue_jwt_pair(user)

        # 리프레시 토큰 DB 저장
        refresh_token = tokens["refresh_token"]
        expires_at = datetime.fromtimestamp(refresh_token.payload["exp"], tz=config.TIMEZONE)
        await self.refresh_token_repo.create(
            user_id=user.id,
            token=str(refresh_token),
            expires_at=expires_at,
        )
        return tokens

    async def logout(self, refresh_token: str) -> None:
        # 리프레시 토큰 DB에서 삭제 (무효화)
        token_exists = await self.refresh_token_repo.exists_by_token(refresh_token)
        if not token_exists:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 토큰입니다.",
            )
        await self.refresh_token_repo.delete_by_token(refresh_token)

    async def send_password_reset_email(self, email: str) -> None:
        # 유저 존재 여부 확인 (보안상 존재 여부 노출 안 함)
        user = await self.user_repo.get_user_by_email(email)
        if not user:
            return

        # 기존 코드 삭제 후 재발송 (유효시간 30분)
        await self.email_verification_repo.delete_previous(
            email=email,
            verification_type=VerificationType.PASSWORD_RESET,
        )
        await self._send_verification_code(
            user_id=user.id,
            email=email,
            verification_type=VerificationType.PASSWORD_RESET,
            expire_hours=0,
            expire_minutes=30,
        )

    async def reset_password(self, email: str, code: str, new_password: str) -> None:
        verification = await self.email_verification_repo.get_latest_by_email_and_type(
            email=email,
            verification_type=VerificationType.PASSWORD_RESET,
        )
        self._validate_verification(verification, code)

        async with in_transaction():
            await self.email_verification_repo.mark_as_verified(verification)
            user = await self.user_repo.get_user_by_email(email)
            if user:
                user.hashed_password = hash_password(new_password)
                await user.save(update_fields=["hashed_password"])
                # 모든 리프레시 토큰 무효화
                await self.refresh_token_repo.delete_by_user_id(user.id)

    async def check_email_exists(self, email: str | EmailStr) -> None:
        if await self.user_repo.exists_by_email(email):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="이미 사용중인 이메일입니다.")

    async def check_phone_number_exists(self, phone_number: str) -> None:
        if await self.user_repo.exists_by_phone_number(phone_number):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="이미 사용중인 휴대폰 번호입니다.")

    async def is_email_duplicate(self, email: str) -> bool:
        return await self.user_repo.exists_by_email(email)

    async def _send_verification_code(
        self,
        user_id: int,
        email: str,
        verification_type: VerificationType,
        expire_hours: int = 24,
        expire_minutes: int = 0,
    ) -> None:
        code = str(secrets.randbelow(1000000)).zfill(6)
        expires_at = datetime.now(tz=config.TIMEZONE) + timedelta(hours=expire_hours, minutes=expire_minutes)

        await self.email_verification_repo.create(
            user_id=user_id,
            email=email,
            code=code,
            verification_type=verification_type,
            expires_at=expires_at,
        )

        if verification_type == VerificationType.PASSWORD_RESET:
            await self.email_service.send_password_reset_email(email=email, code=code)
        else:
            await self.email_service.send_verification_email(email=email, code=code)

    def _validate_verification(
        self,
        verification: EmailVerification | None,
        code: str,
    ) -> None:
        if not verification:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="인증 코드를 찾을 수 없습니다.")
        if verification.expires_at < datetime.now(tz=config.TIMEZONE):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="인증 코드가 만료되었습니다.")
        if verification.code != code:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="인증 코드가 올바르지 않습니다.")

    async def change_password(
        self,
        user: User,
        current_password: str,
        new_password: str,
    ) -> None:
        # 현재 비밀번호 확인
        if not verify_password(current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="현재 비밀번호가 올바르지 않습니다.",
            )
        # 현재 비밀번호와 동일한지 확인
        if current_password == new_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="새 비밀번호는 현재 비밀번호와 달라야 합니다.",
            )
        user.hashed_password = hash_password(new_password)
        await user.save(update_fields=["hashed_password"])
        # 모든 리프레시 토큰 무효화
        await self.refresh_token_repo.delete_by_user_id(user.id)

    async def withdraw(self, user: User) -> None:
        async with in_transaction():
            # 소프트 딜리트 처리
            user.deleted_at = datetime.now(tz=config.TIMEZONE)
            user.is_active = False
            await user.save(update_fields=["deleted_at", "is_active"])
            # 모든 리프레시 토큰 무효화
            await self.refresh_token_repo.delete_by_user_id(user.id)
