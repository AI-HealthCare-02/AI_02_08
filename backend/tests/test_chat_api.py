import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from unittest.mock import AsyncMock, MagicMock

@pytest.mark.asyncio
async def test_chat_ai_response_background_trigger():
    # 시나리오 1: 챗봇에 메시지 생성 및 BackgroundTask 트리거 검증
    # FastAPI TestClient(AsyncClient)는 내부적으로 앱 라우터를 직접 호출합니다.
    # ChatService와 get_request_user를 오버라이드하거나 관련된 모델 쿼리를 모킹
    
    # 1. 의존성 격리 (보안 미들웨어 등 통과를 위함)
    app.dependency_overrides = {}
    
    # 임시 우회용 Mock Service 설정 (전체 시스템을 로드하긴 무거우므로 서비스 로직을 Mock)
    from app.services.chat import ChatService
    from app.dependencies.security import get_request_user
    from app.models.users import User
    
    # User Mocking
    async def mock_get_user():
        u = User()
        u.id = 1
        return u
        
    app.dependency_overrides[get_request_user] = mock_get_user
    
    # ChatService Mocking
    mock_chat_service = MagicMock(spec=ChatService)
    
    # 응답 모의 객체
    class MockMessage:
        def __init__(self):
            self.id = 1
            self.session_id = 1
            self.sender = "assistant"
            self.content = "Mocked AI Response"
            self.is_faq = False
            self.created_at = "2026-01-01T00:00:00"
            
    mock_chat_service.get_ai_response = AsyncMock(return_value=MockMessage())
    
    app.dependency_overrides[ChatService] = lambda: mock_chat_service

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/chat/sessions/1/ai-response",
            json={"user_message": "약 언제 먹어요?"}
        )
        
    # 결과가 201 Created인지 검증
    assert response.status_code == 201
    assert response.json()["content"] == "Mocked AI Response"
    
    # background_tasks가 인자로 전달되는지 검증
    # 인자가 어떻게 넘어갔는지 내부 Mock 콜 검사
    mock_chat_service.get_ai_response.assert_called_once()
    kwargs = mock_chat_service.get_ai_response.call_args.kwargs
    assert "background_tasks" in kwargs
    assert kwargs["user_message"] == "약 언제 먹어요?"

    app.dependency_overrides.clear()
