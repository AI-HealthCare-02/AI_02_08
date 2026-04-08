from unittest.mock import AsyncMock, patch
import pytest

from app.services.openai_service import parse_ocr_text_to_medications, OcrMedicationList, ParsedMedication

@pytest.mark.asyncio
async def test_parse_ocr_text_to_medications_success():
    # Mocking data
    sample_texts = [
        "타이레놀500mg", "1정", "1일 3회", "식후 30분",
        "소화제", "2알", "1일 2회", "취침전"
    ]

    mock_medications = OcrMedicationList(
        medications=[
            ParsedMedication(name="타이레놀500mg", dosage="1정", frequency="1일 3회", timing="식후 30분"),
            ParsedMedication(name="소화제", dosage="2알", frequency="1일 2회", timing="취침전")
        ]
    )

    class MockMessage:
        parsed = mock_medications

    class MockChoice:
        message = MockMessage()

    class MockResponse:
        choices = [MockChoice()]

    # Patch AsyncOpenAI client directly in the service module
    with patch("app.services.openai_service.client") as mock_client:
        mock_client.beta.chat.completions.parse = AsyncMock(return_value=MockResponse())

        # Calling the function
        result = await parse_ocr_text_to_medications(sample_texts)

        # Asserts
        assert len(result) == 2
        assert result[0]["name"] == "타이레놀500mg"
        assert result[0]["dosage"] == "1정"
        assert result[1]["name"] == "소화제"
        assert result[1]["frequency"] == "1일 2회"

@pytest.mark.asyncio
async def test_parse_ocr_text_to_medications_empty():
    result = await parse_ocr_text_to_medications([])
    assert result == []

@pytest.mark.asyncio
async def test_parse_ocr_text_to_medications_exception():
    with patch("app.services.openai_service.client") as mock_client:
        mock_client.beta.chat.completions.parse.side_effect = Exception("API Error")
        
        result = await parse_ocr_text_to_medications(["어떤약", "1알"])
        assert result == []
