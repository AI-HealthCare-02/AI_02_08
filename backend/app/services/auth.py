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
            # 인증 코드 생성 및 이메일 발송
            await self._send_verification_code(
                user_id=user.id,
                email=data.email,
                verification_type=VerificationType.SIGNUP,
            )
            return user

    async def verify_email(self, email: str, code: str) -> None:
        # 인증 코드 조회
        verification = await self.email_verification_repo.get_latest_by_email_and_type(
            email=email,
            verification_type=VerificationType.SIGNUP,
        )
        # 코드 유효성 검증
        self._validate_verification(verification, code)

        async with in_transaction():
            # 인증 완료 처리
            await self.email_verification_repo.mark_as_verified(verification)
            # users 테이블 is_verified 업데이트
            user = await self.user_repo.get_user_by_email(email)
            if user:
                user.is_verified = True
                await user.save(update_fields=["is_verified"])

    async def resend_verification_email(self, email: str) -> None:
        # 이미 인증된 유저인지 확인
        user = await self.user_repo.get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="존재하지 않는 이메일입니다.")
        if user.is_verified:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="이미 인증된 이메일입니다.")

        # 기존 코드 삭제 후 재발송
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
        return self.jwt_service.issue_jwt_pair(user)

    async def check_email_exists(self, email: str | EmailStr) -> None:
        if await self.user_repo.exists_by_email(email):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="이미 사용중인 이메일입니다.")

    async def check_phone_number_exists(self, phone_number: str) -> None:
        if await self.user_repo.exists_by_phone_number(phone_number):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="이미 사용중인 휴대폰 번호입니다.")

    async def _send_verification_code(
        self,
        user_id: int,
        email: str,
        verification_type: VerificationType,
        expire_hours: int = 24,
    ) -> None:
        # 6자리 랜덤 숫자 코드 생성
        code = str(secrets.randbelow(1000000)).zfill(6)
        expires_at = datetime.now(tz=config.TIMEZONE) + timedelta(hours=expire_hours)

        await self.email_verification_repo.create(
            user_id=user_id,
            email=email,
            code=code,
            verification_type=verification_type,
            expires_at=expires_at,
        )
        await self.email_service.send_verification_email(email=email, code=code)

    async def is_email_duplicate(self, email: str) -> bool:
        return await self.user_repo.exists_by_email(email)

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
