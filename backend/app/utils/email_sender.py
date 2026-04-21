"""
AWS SES Boto3 SDK를 사용한 이메일 발송 유틸리티
SMTP 대신 AWS SDK를 사용하여 보안 강화
"""

import logging

import boto3
from botocore.exceptions import ClientError

from app.core.config import settings

logger = logging.getLogger(__name__)


class SESEmailSender:
    """AWS SES를 사용한 이메일 발송 클래스"""

    def __init__(self):
        self.client = boto3.client(
            "ses",
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        self.from_email = settings.SES_FROM_EMAIL

    def send_email(
        self,
        to_emails: list[str],
        subject: str,
        html_body: str,
        text_body: str | None = None,
        reply_to: list[str] | None = None,
    ) -> bool:
        """
        SES를 통해 이메일 발송

        Args:
            to_emails: 수신자 이메일 리스트
            subject: 이메일 제목
            html_body: HTML 본문
            text_body: 텍스트 본문 (옵션)
            reply_to: 회신 이메일 (옵션)

        Returns:
            bool: 발송 성공 여부
        """
        try:
            message_body = {"Html": {"Charset": "UTF-8", "Data": html_body}}

            if text_body:
                message_body["Text"] = {"Charset": "UTF-8", "Data": text_body}

            send_kwargs = {
                "Source": self.from_email,
                "Destination": {"ToAddresses": to_emails},
                "Message": {
                    "Subject": {"Charset": "UTF-8", "Data": subject},
                    "Body": message_body,
                },
            }

            if reply_to:
                send_kwargs["ReplyToAddresses"] = reply_to

            response = self.client.send_email(**send_kwargs)

            logger.info(f"이메일 발송 성공: MessageId={response['MessageId']}, To={to_emails}")
            return True

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]
            logger.error(f"SES 이메일 발송 실패: {error_code} - {error_message}, To={to_emails}")
            return False

        except Exception as e:
            logger.exception(f"이메일 발송 중 예외 발생: {str(e)}, To={to_emails}")
            return False

    def send_templated_email(
        self,
        to_emails: list[str],
        template_name: str,
        template_data: dict,
        reply_to: list[str] | None = None,
    ) -> bool:
        """
        SES 템플릿을 사용한 이메일 발송

        Args:
            to_emails: 수신자 이메일 리스트
            template_name: SES 템플릿 이름
            template_data: 템플릿 변수 데이터
            reply_to: 회신 이메일 (옵션)

        Returns:
            bool: 발송 성공 여부
        """
        try:
            import json

            send_kwargs = {
                "Source": self.from_email,
                "Destination": {"ToAddresses": to_emails},
                "Template": template_name,
                "TemplateData": json.dumps(template_data),
            }

            if reply_to:
                send_kwargs["ReplyToAddresses"] = reply_to

            response = self.client.send_templated_email(**send_kwargs)

            logger.info(f"템플릿 이메일 발송 성공: MessageId={response['MessageId']}, Template={template_name}")
            return True

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]
            logger.error(f"SES 템플릿 이메일 발송 실패: {error_code} - {error_message}")
            return False

        except Exception as e:
            logger.exception(f"템플릿 이메일 발송 중 예외 발생: {str(e)}")
            return False


# 싱글톤 인스턴스
ses_sender = SESEmailSender()
