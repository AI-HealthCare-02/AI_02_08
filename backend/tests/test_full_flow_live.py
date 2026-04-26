import asyncio
import os
import sys
from datetime import datetime

import httpx

# sys.path 설정
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tortoise import Tortoise

from app.models.users import User
from app.services.jwt import JwtService

BASE_URL = "http://localhost:8000"


async def run_test():
    # 1. DB 초기화 (토큰 생성용)
    from app.db.databases import TORTOISE_ORM

    await Tortoise.init(config=TORTOISE_ORM)

    # 2. 테스트 사용자 및 토큰 생성
    user = await User.filter(email="test@example.com").get_or_none()
    if not user:
        user = await User.create(email="test@example.com", name="테스트", hashed_password="dummy")

    token_obj = JwtService().create_access_token(user)
    token = str(token_obj)
    headers = {"Authorization": f"Bearer {token}"}

    print(f"🔑 테스트 토큰 생성 완료 (User: {user.email})")

    async with httpx.AsyncClient(headers=headers, timeout=60.0) as client:
        # 3. OCR 데이터 직접 DB에 생성 (Bypass API failure)
        from app.models.medications import OcrPrescription, OcrStatus

        ocr_id = f"test_ocr_{datetime.now().strftime('%H%M%S')}"
        s3_url = "https://dummy-s3-url.com/image.png"

        print(f"--- 🚀 1단계: DB에 더미 OCR 데이터 생성 (ID: {ocr_id}) ---")
        await OcrPrescription.create(
            ocr_id=ocr_id,
            user_id=user.id,
            image_url=s3_url,
            status=OcrStatus.PENDING,
            extracted_data={
                "parsed": [
                    {"name": "타이레놀정500mg", "dosage": "1정", "frequency": "1일 3회", "timing": "식후 30분"},
                    {"name": "아모디핀정", "dosage": "1정", "frequency": "1일 1회", "timing": "아침 식후"},
                ]
            },
        )
        print("✅ 더미 OCR 데이터 생성 완료!")

        # 4. 챗봇 세션 생성
        print("\n--- 🚀 2단계: 신규 챗봇 세션 생성 ---")
        session_resp = await client.post(f"{BASE_URL}/api/v1/chat/sessions", json={})
        if session_resp.status_code != 201:
            print(f"❌ 세션 생성 실패: {session_resp.text}")
            await Tortoise.close_connections()
            return

        session_id = session_resp.json()["session_id"]
        print(f"✅ 세션 생성 완료! session_id: {session_id}")

        # 5. 세션에 OCR ID 연동 (PATCH)
        print("\n--- 🚀 3단계: 세션에 OCR 정보 연동 (PATCH) ---")
        patch_resp = await client.patch(f"{BASE_URL}/api/v1/chat/sessions/{session_id}", json={"ocr_id": ocr_id})
        if patch_resp.status_code == 200:
            print("✅ PATCH 연동 성공!")
        else:
            print(f"❌ PATCH 연동 실패: {patch_resp.status_code} - {patch_resp.text}")
            await Tortoise.close_connections()
            return

        # 6. AI 답변 테스트
        print("\n--- 🚀 4단계: AI 챗봇에게 약물 정보 질의 ---")
        ai_resp = await client.post(
            f"{BASE_URL}/api/v1/chat/sessions/{session_id}/ai-response",
            json={"user_message": "방금 내가 올린 처방전에 어떤 약들이 있어?"},
        )

        if ai_resp.status_code == 201:
            print(f"🤖 AI 답변:\n{ai_resp.json().get('content')}")
        else:
            print(f"❌ AI 답변 생성 실패: {ai_resp.status_code} - {ai_resp.text}")

    await Tortoise.close_connections()
    print("\n--- ✨ 모든 테스트 완료 ---")


if __name__ == "__main__":
    asyncio.run(run_test())
