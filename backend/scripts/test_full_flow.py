import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tortoise import Tortoise
from httpx import ASGITransport, AsyncClient

from app.db.databases import TORTOISE_ORM
from app.main import app
from app.dependencies.security import get_request_user
from app.models.users import User

TEST_IMAGE_PATH = "/Users/admin/PycharmProjects/8_project/backend/ocr_test_image/rx_01_design_A.png"

async def mock_get_user():
    user = await User.get_or_none(email="test_full_flow@example.com")
    if not user:
        user = await User.create(
            email="test_full_flow@example.com",
            name="TestUser",
            password_hash="fake",
        )
    return user

async def run_test():
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()

    app.dependency_overrides[get_request_user] = mock_get_user

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        print("1. Uploading OCR Image...")
        if not os.path.exists(TEST_IMAGE_PATH):
            print(f"Error: {TEST_IMAGE_PATH} not found.")
            return

        with open(TEST_IMAGE_PATH, "rb") as f:
            file_bytes = f.read()

        files = {"image": ("prescription.png", file_bytes, "image/png")}
        response = await ac.post("/api/v1/ai/ocr/prescription", files=files, timeout=60.0)
        
        if response.status_code != 200:
            print("❌ OCR Failed:", response.status_code, response.text)
            return

        data = response.json()
        ocr_id = data.get("ocrId")
        print(f"✅ OCR Success! ocr_id: {ocr_id}")
        print("   Extracted Medications:", [m.get("name") for m in data.get("medications", [])])

        print("\n2. Creating Chat Session...")
        session_resp = await ac.post("/api/v1/chat/sessions", json={"ocr_id": ocr_id})
        
        if session_resp.status_code != 201:
            print("❌ Session Create Failed:", session_resp.status_code, session_resp.text)
            return
        
        session_data = session_resp.json()
        session_id = session_data.get("session_id")
        print(f"✅ Chat Session Created! session_id: {session_id}")

        print("\n3. Asking Chatbot about the medicine...")
        question = "방금 스캔한 처방전의 모든 약품에 대해서 용도와 주의사항을 알려줘"
        print(f"🙍‍♂️ User: {question}")

        chat_resp = await ac.post(
            f"/api/v1/chat/sessions/{session_id}/ai-response",
            json={"user_message": question},
            timeout=60.0
        )
        
        if chat_resp.status_code != 201:
            print("❌ Chatbot Failed:", chat_resp.status_code, chat_resp.text)
            return

        chat_data = chat_resp.json()
        print(f"🤖 AI Answer:\n{chat_data.get('content')}")

    await Tortoise.close_connections()

if __name__ == "__main__":
    asyncio.run(run_test())
