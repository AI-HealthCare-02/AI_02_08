from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

from app.core.config import Config

config = Config()

mail_config = ConnectionConfig(
    MAIL_USERNAME=config.MAIL_USERNAME,
    MAIL_PASSWORD=config.MAIL_PASSWORD,
    MAIL_FROM=config.MAIL_FROM,
    MAIL_SERVER=config.MAIL_SERVER,
    MAIL_PORT=config.MAIL_PORT,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
)

fast_mail = FastMail(mail_config)


class EmailService:
    async def send_verification_email(self, email: str, code: str) -> None:
        message = MessageSchema(
            subject="이메일 인증을 완료해주세요",
            recipients=[email],
            body=f"""
            <h2>이메일 인증</h2>
            <p>아래 인증 코드를 입력해주세요:</p>
            <h1 style="letter-spacing: 4px;">{code}</h1>
            <p>인증 코드는 <strong>24시간</strong> 동안 유효합니다.</p>
            """,
            subtype=MessageType.html,
        )
        await fast_mail.send_message(message)

    async def send_password_reset_email(self, email: str, code: str) -> None:
        message = MessageSchema(
            subject="비밀번호 재설정 안내",
            recipients=[email],
            body=f"""
            <h2>비밀번호 재설정</h2>
            <p>아래 인증 코드를 입력해주세요:</p>
            <h1 style="letter-spacing: 4px;">{code}</h1>
            <p>인증 코드는 <strong>30분</strong> 동안 유효합니다.</p>
            """,
            subtype=MessageType.html,
        )
        await fast_mail.send_message(message)
