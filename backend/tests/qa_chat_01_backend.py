import asyncio

import httpx
from tortoise import Tortoise

from app.db.databases import TORTOISE_ORM
from app.models.users import User
from app.services.jwt import JwtService

BASE_URL = "http://localhost:8001"


async def test_chat_01_backend():
    print("🚀 [CHAT-01] AI 챗봇 기본 기능 (Backend) QA 테스트 시작")
    await Tortoise.init(config=TORTOISE_ORM)

    # 1. 토큰 생성
    user = await User.filter(email="new_qa_test@example.com").first()
    if not user:
        print("❌ 테스트용 사용자가 없습니다.")
        await Tortoise.close_connections()
        return

    token_obj = JwtService().create_access_token(user)
    headers = {"Authorization": f"Bearer {token_obj}"}

    async with httpx.AsyncClient(headers=headers, timeout=60.0) as client:
        # 1. 채팅 세션 생성 (CHAT-01-1)
        print("\n[CHAT-01-1] 채팅 세션 생성 테스트")
        # FastAPI Pydantic 모델은 빈 바디라도 {}를 요구할 수 있음
        resp = await client.post(f"{BASE_URL}/api/v1/chat/sessions", json={})
        if resp.status_code == 201:
            session_data = resp.json()
            session_id = session_data.get("session_id")
            print(f"✅ 결과: 세션 생성 성공 (ID: {session_id})")

            # 초기 인사 메시지 확인 (get messages)
            msg_resp = await client.get(f"{BASE_URL}/api/v1/chat/sessions/{session_id}/messages")
            if msg_resp.status_code == 200:
                msgs = msg_resp.json()
                print(f"✅ 결과: 초기 메시지 로드 성공 (건수: {len(msgs)})")
            else:
                print("❌ 결과: 초기 메시지 로드 실패")
        else:
            print(f"❌ 결과: 세션 생성 실패 ({resp.status_code}, {resp.text})")
            await Tortoise.close_connections()
            return

        # 2. 메시지 전송 및 AI 응답 (CHAT-01-2, 3)
        print("\n[CHAT-01-2, 3] 메시지 전송 및 AI 응답 테스트")
        import uuid

        chat_payload = {"content": "감기약 복용법 알려줘", "is_faq": False}
        headers["X-Idempotency-Key"] = f"qa-test-{uuid.uuid4().hex[:8]}"
        resp = await client.post(
            f"{BASE_URL}/api/v1/chat/sessions/{session_id}/messages", json=chat_payload, headers=headers
        )

        if resp.status_code == 201:
            ai_msg = resp.json()
            print("✅ 결과: AI 응답 수신 성공")
            print(f"🤖 AI 응답: {ai_msg.get('content')[:50]}...")
            if ai_msg.get("sender") == "assistant":
                print("✅ 결과: 발신자 'assistant' 확인")
        else:
            print(f"❌ 결과: 메시지 전송 실패 ({resp.status_code}, {resp.text})")

    await Tortoise.close_connections()
    print("\n✨ 모든 [CHAT-01] Backend QA 테스트 완료")


if __name__ == "__main__":
    asyncio.run(test_chat_01_backend())
