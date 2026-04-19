import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.repositories.chat_session_repository import ChatSessionRepository
from app.repositories.chat_message_repository import ChatMessageRepository
from app.models.chat_session import ChatSession
from app.models.chat_message import ChatMessage

async def dummy_queryset_result():
    return []

@pytest.mark.asyncio
@patch("app.models.chat_session.ChatSession.filter")
async def test_session_repository_soft_delete_filter(mock_filter_method):
    repo = ChatSessionRepository()
    mock_query_set = MagicMock()
    mock_query_set.order_by = MagicMock(side_effect=lambda *a, **k: dummy_queryset_result())
    mock_filter_method.return_value = mock_query_set
    
    await repo.get_by_user_id(user_id=1)
    
    mock_filter_method.assert_called_with(user_id=1, is_deleted=False)
    mock_query_set.order_by.assert_called_with("-created_at")

@pytest.mark.asyncio
@patch("app.models.chat_message.ChatMessage.filter")
async def test_message_repository_soft_delete_filter(mock_filter_method):
    repo = ChatMessageRepository()
    mock_query_set = MagicMock()
    mock_query_set.order_by = MagicMock(side_effect=lambda *a, **k: dummy_queryset_result())
    mock_filter_method.return_value = mock_query_set
    
    await repo.get_by_session_id(session_id=1)
    
    mock_filter_method.assert_called_with(session_id=1, is_deleted=False)
    mock_query_set.order_by.assert_called_with("created_at")

@pytest.mark.asyncio
async def test_session_repository_soft_delete_action():
    repo = ChatSessionRepository()
    mock_session = AsyncMock(spec=ChatSession)
    mock_session.is_deleted = False
    
    await repo.delete(mock_session)
    
    assert mock_session.is_deleted is True
    mock_session.save.assert_called_once_with(update_fields=["is_deleted"])
