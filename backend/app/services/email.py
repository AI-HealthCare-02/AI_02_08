import logging

from app.utils.email_sender import ses_sender

logger = logging.getLogger(__name__)


class EmailService:
    """이메일 발송 서비스 클래스"""

    async def send_verification_email(self, email: str, code: str) -> bool:
        """
        이메일 인증 코드 발송

        Args:
            email: 수신자 이메일
            code: 인증 코드

        Returns:
            bool: 발송 성공 여부
        """
        subject = "이메일 인증을 완료해주세요"

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #9A8058;">이메일 인증</h2>
                <p>아래 인증 코드를 입력해주세요:</p>
                <div style="margin: 30px 0; padding: 20px; background-color: #f9f9f9; text-align: center;">
                    <h1 style="letter-spacing: 8px; color: #9A8058; font-size: 36px; margin: 0;">{code}</h1>
                </div>
                <p style="color: #666;">인증 코드는 <strong>24시간</strong> 동안 유효합니다.</p>
                <p style="margin-top: 30px; color: #999; font-size: 14px;">
                    본인이 요청하지 않은 경우 이 이메일을 무시하셔도 됩니다.
                </p>
            </div>
        </body>
        </html>
        """

        text_body = f"""
        이메일 인증

        아래 인증 코드를 입력해주세요:

        {code}

        인증 코드는 24시간 동안 유효합니다.

        본인이 요청하지 않은 경우 이 이메일을 무시하셔도 됩니다.
        """

        try:
            success = ses_sender.send_email(
                to_emails=[email],
                subject=subject,
                html_body=html_body,
                text_body=text_body,
            )

            if success:
                logger.info(f"인증 이메일 발송 성공: {email}")
            else:
                logger.error(f"인증 이메일 발송 실패: {email}")

            return success

        except Exception as e:
            logger.exception(f"인증 이메일 발송 중 예외 발생: {email}, {str(e)}")
            return False

    async def send_password_reset_email(self, email: str, code: str) -> bool:
        """
        비밀번호 재설정 코드 발송

        Args:
            email: 수신자 이메일
            code: 인증 코드

        Returns:
            bool: 발송 성공 여부
        """
        subject = "비밀번호 재설정 안내"

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #9A8058;">비밀번호 재설정</h2>
                <p>아래 인증 코드를 입력해주세요:</p>
                <div style="margin: 30px 0; padding: 20px; background-color: #f9f9f9; text-align: center;">
                    <h1 style="letter-spacing: 8px; color: #9A8058; font-size: 36px; margin: 0;">{code}</h1>
                </div>
                <p style="color: #666;">인증 코드는 <strong>30분</strong> 동안 유효합니다.</p>
                <div style="margin: 20px 0; padding: 15px; background-color: #fff3cd; border-left: 4px solid #ffc107;">
                    <p style="margin: 0; color: #856404;">
                        ⚠️ 본인이 요청하지 않은 경우, 즉시 비밀번호를 변경해주세요.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

        text_body = f"""
        비밀번호 재설정

        아래 인증 코드를 입력해주세요:

        {code}

        인증 코드는 30분 동안 유효합니다.

        ⚠️ 본인이 요청하지 않은 경우, 즉시 비밀번호를 변경해주세요.
        """

        try:
            success = ses_sender.send_email(
                to_emails=[email],
                subject=subject,
                html_body=html_body,
                text_body=text_body,
            )

            if success:
                logger.info(f"비밀번호 재설정 이메일 발송 성공: {email}")
            else:
                logger.error(f"비밀번호 재설정 이메일 발송 실패: {email}")

            return success

        except Exception as e:
            logger.exception(f"비밀번호 재설정 이메일 발송 중 예외 발생: {email}, {str(e)}")
            return False

    async def send_signup_welcome_email(self, email: str, name: str) -> bool:
        """
        회원가입 환영 이메일 발송

        Args:
            email: 수신자 이메일
            name: 사용자 이름

        Returns:
            bool: 발송 성공 여부
        """
        subject = "이루도담 회원가입을 환영합니다!"

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #9A8058;">안녕하세요, {name}님!</h2>
                <p>이루도담 회원가입을 진심으로 환영합니다.</p>
                <p>건강한 복약 생활을 위한 첫 걸음을 함께하게 되어 기쁩니다.</p>
                <div style="margin: 30px 0; padding: 20px; background-color: #f9f9f9; border-left: 4px solid #9A8058;">
                    <h3 style="margin-top: 0; color: #9A8058;">주요 기능</h3>
                    <ul style="padding-left: 20px;">
                        <li style="margin-bottom: 8px;">📷 처방전 OCR 인식</li>
                        <li style="margin-bottom: 8px;">💊 복약 일정 관리</li>
                        <li style="margin-bottom: 8px;">🤖 AI 건강 상담</li>
                    </ul>
                </div>
                <p>궁금하신 사항이 있으시면 언제든지 문의해 주세요.</p>
                <p style="margin-top: 30px; color: #666; font-size: 14px;">
                    감사합니다.<br>
                    이루도담 팀 드림
                </p>
            </div>
        </body>
        </html>
        """

        text_body = f"""
        안녕하세요, {name}님!

        이루도담 회원가입을 진심으로 환영합니다.
        건강한 복약 생활을 위한 첫 걸음을 함께하게 되어 기쁩니다.

        주요 기능:
        - 📷 처방전 OCR 인식
        - 💊 복약 일정 관리
        - 🤖 AI 건강 상담

        궁금하신 사항이 있으시면 언제든지 문의해 주세요.

        감사합니다.
        이루도담 팀 드림
        """

        try:
            success = ses_sender.send_email(
                to_emails=[email],
                subject=subject,
                html_body=html_body,
                text_body=text_body,
            )

            if success:
                logger.info(f"환영 이메일 발송 성공: {email}")
            else:
                logger.error(f"환영 이메일 발송 실패: {email}")

            return success

        except Exception as e:
            logger.exception(f"환영 이메일 발송 중 예외 발생: {email}, {str(e)}")
            return False


# 싱글톤 인스턴스
email_service = EmailService()
