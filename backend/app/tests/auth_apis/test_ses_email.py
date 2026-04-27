"""
AWS SES 이메일 발송 테스트
"""

import pytest

from app.services.email import email_service


@pytest.mark.asyncio
async def test_send_verification_email():
    """이메일 인증 코드 발송 테스트"""
    # Sandbox 모드에서는 인증된 이메일만 사용 가능
    result = await email_service.send_verification_email(
        email="irudodam@gmail.com",  # 인증된 이메일로 변경
        code="123456",
    )
    assert result is True, "인증 이메일 발송 실패"


@pytest.mark.asyncio
async def test_send_password_reset_email():
    """비밀번호 재설정 이메일 발송 테스트"""
    result = await email_service.send_password_reset_email(
        email="irudodam@gmail.com",  # 인증된 이메일로 변경
        code="789012",
    )
    assert result is True, "비밀번호 재설정 이메일 발송 실패"


@pytest.mark.asyncio
async def test_send_signup_welcome_email():
    """회원가입 환영 이메일 발송 테스트"""
    result = await email_service.send_signup_welcome_email(
        email="irudodam@gmail.com",  # 인증된 이메일로 변경
        name="테스트유저",
    )
    assert result is True, "환영 이메일 발송 실패"


@pytest.mark.skip(reason="SES Production 모드로 전환되어 테스트 불필요")
@pytest.mark.asyncio
async def test_send_email_to_unverified_address():
    """
    인증되지 않은 이메일로 발송 시 실패 테스트 (Sandbox 모드)
    Production 모드에서는 이 테스트 스킵
    """
    result = await email_service.send_verification_email(email="unverified@example.com", code="000000")
    # Sandbox 모드에서는 실패해야 정상
    assert result is False, "인증되지 않은 이메일로 발송 성공 (예상: 실패)"
