import pytest
import json
from unittest.mock import AsyncMock, patch
from app.services.openai_service import batch_analyze_unmatched_drugs, summarize_and_deidentify_chat

@pytest.mark.asyncio
@patch("app.services.openai_service.client.chat.completions.create", new_callable=AsyncMock)
async def test_batch_analyze_unmatched_drugs(mock_client):
    # 시나리오 1: 알 수 없는 약품/일반 약품 JSON 반환 검증
    mock_response = AsyncMock()
    # GPT가 JSON을 반환하는 상황 모사
    mock_response.choices[0].message.content = '```json\n{"타이레놀": "해열진통제", "이상한약123": "일치하는 약품 정보를 찾을 수 없습니다."}\n```'
    mock_client.return_value = mock_response

    unmatched_meds = [{"name": "타이레놀"}, {"name": "이상한약123"}]
    result = await batch_analyze_unmatched_drugs(unmatched_meds)

    assert result["타이레놀"] == "해열진통제"
    assert "일치하는 약품 정보" in result["이상한약123"]

@pytest.mark.asyncio
@patch("app.services.openai_service.client.chat.completions.create", new_callable=AsyncMock)
async def test_summarize_and_deidentify_chat(mock_client):
    # 시나리오 2: PII 제외 기능 검증
    mock_response = AsyncMock()
    mock_response.choices[0].message.content = "환자는 빈속에 타이레놀 복용 후 속쓰림을 겪었으며, 대체 방안을 문의함."
    mock_client.return_value = mock_response

    messages = [
        {"role": "user", "content": "선생님, 저 김철수인데요. 오늘 타이레놀 먹고 속이 쓰려요."},
        {"role": "assistant", "content": "빈속에 드셨나요?"}
    ]
    
    result = await summarize_and_deidentify_chat(messages)
    
    assert "김철수" not in result
    assert "타이레놀" in result
