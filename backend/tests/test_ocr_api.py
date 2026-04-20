import pytest
from httpx import ASGITransport, AsyncClient

from app.dependencies.security import get_request_user
from app.main import app
from app.models.users import User


async def mock_get_user():
    u = User()
    u.id = 1
    return u


@pytest.fixture(autouse=True)
def override_dependency():
    app.dependency_overrides[get_request_user] = mock_get_user
    yield
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_ocr_api_invalid_file_extension():
    # 시나리오 1: 잘못된 확장자 제출
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/ai/ocr/prescription", files={"image": ("test.txt", b"dummy content", "text/plain")}
        )
    assert response.status_code == 400
    assert "지원하지 않는 파일 형식" in response.json()["detail"]


@pytest.mark.asyncio
async def test_ocr_api_large_file_size():
    # 시나리오 1: 15MB 초과 파일 제출 (가상 파일 사이즈 우회/검증)
    dummy_large_content = b"a" * (16 * 1024 * 1024)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/ai/ocr/prescription", files={"image": ("large.jpg", dummy_large_content, "image/jpeg")}
        )
    assert response.status_code == 400
    assert "15MB" in response.json()["detail"] or "최대 파일 크기는 15MB" in response.json()["detail"]
