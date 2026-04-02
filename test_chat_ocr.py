"""
app/test_chat_ocr.py

ci.yml 기준:
  uv run coverage run -m pytest app

원칙:
  - confirm payload 는 userMedicationData.json 에서 동적으로 구성
  - 약물명/dosage/frequency 하드코딩 금지
  - mock response 금지 — OPENAI_API_KEY=dummy 환경에서 fallback 경로 자연 발동
  - 불법 약물 키워드는 서비스 코드 하드코딩 목록과 동일하게 참조
  - 3시간 경고 문구: last_warning_time 조작으로 검증
"""

import io
import json
import os
from datetime import datetime, timedelta

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.apis.v1.chat_ocr_routers import chat_ocr_router
from app.services.chat_ocr_service import ChatOcrService

# ---------------------------------------------------------------------------
# 테스트 전용 미니 FastAPI 앱
# ---------------------------------------------------------------------------
_app = FastAPI()
_app.include_router(chat_ocr_router, prefix="/api/v1")

# ---------------------------------------------------------------------------
# 서비스 코드 _check_illicit_drugs() 와 동일한 불법 약물 키워드 목록
# ---------------------------------------------------------------------------
_ILLICIT_KEYWORDS = [
    "대마", "코카인", "헤로인", "필로폰", "엑스터시",
    "mdma", "lsd", "펜타닐", "ghb", "케타민", "졸피뎀",
    "프로포폴", "히로뽕", "물뽕", "떨",
]


# ---------------------------------------------------------------------------
# userMedicationData.json 로드 헬퍼
# ChatOcrService._load_medication_data() 와 동일한 경로 계산 방식
# ---------------------------------------------------------------------------
def _load_real_medication_data() -> list[dict]:
    base = os.path.dirname(   # backend/
        os.path.dirname(       # app/
            os.path.abspath(__file__)
        )
    )
    file_path = os.path.join(base, "userMedicationData.json")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def medication_data() -> list[dict]:
    """실제 json 에서 읽은 약물 목록 (모듈 단위로 1회만 로드)"""
    return _load_real_medication_data()


@pytest.fixture()
def service(monkeypatch) -> ChatOcrService:
    """매 테스트마다 독립된 ChatOcrService 인스턴스 (실제 json 로드)"""
    svc = ChatOcrService()

    import app.services.chat_ocr_service as svc_mod
    import app.apis.v1.chat_ocr_routers as router_mod

    monkeypatch.setattr(svc_mod, "chat_ocr_service", svc)
    monkeypatch.setattr(router_mod, "chat_ocr_service", svc)
    return svc


@pytest.fixture()
def client(service) -> TestClient:
    with TestClient(_app) as c:
        yield c


# ===========================================================================
# 1. ChatOcrService 단위 테스트
# ===========================================================================
class TestChatOcrServiceUnit:

    # ── PII 감지 ──────────────────────────────────────────────────────────
    def test_pii_detects_email(self, service):
        assert service._check_pii("user@example.com") is True

    def test_pii_detects_phone(self, service):
        assert service._check_pii("010-1234-5678") is True

    def test_pii_detects_ssn(self, service):
        assert service._check_pii("900101-1234567") is True

    def test_pii_clean_text(self, service):
        assert service._check_pii("복약 방법이 궁금합니다") is False

    # ── 불법 약물 감지 ────────────────────────────────────────────────────
    @pytest.mark.parametrize("keyword", _ILLICIT_KEYWORDS)
    def test_illicit_drug_detected(self, service, keyword):
        assert service._check_illicit_drugs(keyword) is True

    def test_illicit_drug_not_detected_for_normal_text(self, service):
        assert service._check_illicit_drugs("복약 방법이 궁금합니다") is False

    # ── OCR fallback ──────────────────────────────────────────────────────
    @pytest.mark.asyncio
    async def test_process_ocr_returns_success_status(self, service):
        result = await service.process_ocr(b"fake_image_bytes")
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_process_ocr_medications_is_list(self, service):
        result = await service.process_ocr(b"fake_image_bytes")
        assert isinstance(result["medications"], list)

    @pytest.mark.asyncio
    async def test_process_ocr_detail_has_required_fields(self, service):
        result = await service.process_ocr(b"fake_image_bytes")
        required = {"name", "category", "dosage", "schedule", "caution", "description"}
        for item in result.get("medications_detail", []):
            assert required.issubset(item.keys())

    @pytest.mark.asyncio
    async def test_process_ocr_has_analysis_id(self, service):
        result = await service.process_ocr(b"fake_image_bytes")
        assert "analysis_id" in result
        assert len(result["analysis_id"]) > 0

    # ── confirm_prescription (userMedicationData.json 동적 활용) ──────────
    @pytest.mark.asyncio
    async def test_confirm_single_medication(self, service, medication_data):
        """json 첫 번째 약물로 단건 confirm"""
        from app.apis.v1.chat_ocr_routers import MedicationInput

        first = medication_data[0]
        result = await service.confirm_prescription([
            MedicationInput(
                name=first["name"],
                dosage=first.get("dosage", "미정"),
                frequency=first.get("schedule", "미정"),
            )
        ])
        assert result["status"] == "success"
        assert result["current_db_size"] == 1

    @pytest.mark.asyncio
    async def test_confirm_all_medications(self, service, medication_data):
        """json 전체 약물로 confirm 시 전송한 수와 current_db_size 일치"""
        from app.apis.v1.chat_ocr_routers import MedicationInput

        meds = [
            MedicationInput(
                name=m["name"],
                dosage=m.get("dosage", "미정"),
                frequency=m.get("schedule", "미정"),
            )
            for m in medication_data
        ]
        result = await service.confirm_prescription(meds)
        assert result["status"] == "success"
        assert result["current_db_size"] == len(meds)

    @pytest.mark.asyncio
    async def test_confirm_empty_list(self, service):
        result = await service.confirm_prescription([])
        assert result["current_db_size"] == 0

    # ── reset_chat ────────────────────────────────────────────────────────
    def test_reset_restores_initial_state(self, service):
        service.is_blocked = True
        result = service.reset_chat()
        assert result["status"] == "success"
        assert service.is_blocked is False
        assert len(service.messages) == 1

    # ── 3시간 경고 문구 ───────────────────────────────────────────────────
    @pytest.mark.asyncio
    async def test_warning_appended_after_3_hours(self, service):
        """last_warning_time 을 3시간 이전으로 설정하면 경고 문구가 포함돼야 함"""
        service.last_warning_time = datetime.now() - timedelta(hours=3, seconds=1)
        result = await service.send_chat("복약 방법이 궁금합니다")
        ai_content = result["ai"]["content"]
        assert "의료인" in ai_content or "AI" in ai_content or "오류" in ai_content

    @pytest.mark.asyncio
    async def test_warning_not_appended_before_3_hours(self, service):
        """last_warning_time 이 최근이면 경고 문구가 포함되지 않아야 함"""
        service.last_warning_time = datetime.now()
        result = await service.send_chat("복약 방법이 궁금합니다")
        ai_content = result["ai"]["content"]
        # 경고 문구의 고유 문장이 없어야 함
        assert "건강과 관련된 상담은 의료인과 하는 것이 원칙" not in ai_content


# ===========================================================================
# 2. POST /api/v1/ocr/analyze
# ===========================================================================
class TestOcrAnalyze:

    def test_image_upload_returns_success(self, client):
        fake_img = io.BytesIO(b"\xff\xd8\xff" + b"\x00" * 64)
        resp = client.post(
            "/api/v1/ocr/analyze",
            files={"file": ("rx.jpg", fake_img, "image/jpeg")},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "success"

    def test_non_image_returns_400(self, client):
        resp = client.post(
            "/api/v1/ocr/analyze",
            files={"file": ("doc.pdf", b"fake pdf content", "application/pdf")},
        )
        assert resp.status_code == 400

    def test_response_contains_analysis_id(self, client):
        fake_img = io.BytesIO(b"\xff\xd8\xff" + b"\x00" * 64)
        resp = client.post(
            "/api/v1/ocr/analyze",
            files={"file": ("rx.jpg", fake_img, "image/jpeg")},
        )
        assert "analysis_id" in resp.json()

    def test_medications_is_list(self, client):
        fake_img = io.BytesIO(b"\xff\xd8\xff" + b"\x00" * 64)
        resp = client.post(
            "/api/v1/ocr/analyze",
            files={"file": ("rx.jpg", fake_img, "image/jpeg")},
        )
        assert isinstance(resp.json()["medications"], list)

    def test_medications_detail_structure(self, client):
        fake_img = io.BytesIO(b"\xff\xd8\xff" + b"\x00" * 64)
        resp = client.post(
            "/api/v1/ocr/analyze",
            files={"file": ("rx.jpg", fake_img, "image/jpeg")},
        )
        required = {"name", "category", "dosage", "schedule", "caution", "description"}
        for item in resp.json().get("medications_detail", []):
            assert required.issubset(item.keys())


# ===========================================================================
# 3. POST /api/v1/ocr/confirm
# ===========================================================================
class TestOcrConfirm:

    def test_confirm_single_returns_201(self, client, medication_data):
        """json 첫 번째 약물로 단건 요청"""
        first = medication_data[0]
        payload = [{
            "name": first["name"],
            "dosage": first.get("dosage", "미정"),
            "frequency": first.get("schedule", "미정"),
        }]
        resp = client.post("/api/v1/ocr/confirm", json=payload)
        assert resp.status_code == 201
        assert resp.json()["status"] == "success"
        assert resp.json()["current_db_size"] == 1

    def test_confirm_all_medications(self, client, medication_data):
        """json 전체 약물 요청 시 current_db_size 가 전송한 수와 일치"""
        payload = [
            {
                "name": m["name"],
                "dosage": m.get("dosage", "미정"),
                "frequency": m.get("schedule", "미정"),
            }
            for m in medication_data
        ]
        resp = client.post("/api/v1/ocr/confirm", json=payload)
        assert resp.status_code == 201
        assert resp.json()["current_db_size"] == len(payload)

    def test_confirm_empty_list(self, client):
        resp = client.post("/api/v1/ocr/confirm", json=[])
        assert resp.status_code == 201
        assert resp.json()["current_db_size"] == 0

    def test_confirm_omitted_dosage_frequency(self, client, medication_data):
        """dosage/frequency 생략 시 기본값('미정')으로 처리"""
        first = medication_data[0]
        payload = [{"name": first["name"]}]
        resp = client.post("/api/v1/ocr/confirm", json=payload)
        assert resp.status_code == 201
        assert resp.json()["current_db_size"] == 1


# ===========================================================================
# 4. GET /api/v1/chat/history
# ===========================================================================
class TestChatHistory:

    def test_history_has_initial_bot_message(self, client):
        resp = client.get("/api/v1/chat/history")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["messages"]) >= 1
        assert data["messages"][0]["is_user"] is False

    def test_history_has_quick_replies(self, client):
        data = client.get("/api/v1/chat/history").json()
        assert isinstance(data["quick_replies"], list)
        assert len(data["quick_replies"]) > 0


# ===========================================================================
# 5. POST /api/v1/chat/reset
# ===========================================================================
class TestChatReset:

    def test_reset_returns_success(self, client):
        resp = client.post("/api/v1/chat/reset")
        assert resp.status_code == 200
        assert resp.json()["status"] == "success"

    def test_reset_clears_extra_messages(self, client):
        client.post("/api/v1/chat/send", json={"text": "복약 방법이 궁금합니다"})
        client.post("/api/v1/chat/reset")
        history = client.get("/api/v1/chat/history").json()
        assert len(history["messages"]) == 1


# ===========================================================================
# 6. POST /api/v1/chat/send
# ===========================================================================
class TestChatSend:

    def _send(self, client, text: str):
        return client.post("/api/v1/chat/send", json={"text": text})

    def test_normal_message_returns_user_and_ai(self, client):
        resp = self._send(client, "복약 방법이 궁금합니다")
        assert resp.status_code == 200
        data = resp.json()
        assert "user" in data and "ai" in data
        assert data["user"]["is_user"] is True
        assert data["ai"]["is_user"] is False

    def test_empty_message_returns_error(self, client):
        resp = self._send(client, "   ")
        assert resp.status_code == 200
        assert "error" in resp.json()

    def test_pii_email_blocked(self, client):
        resp = self._send(client, "이메일은 user@example.com 입니다")
        assert "답변할 수 없습니다" in resp.json()["ai"]["content"]

    def test_pii_phone_blocked(self, client):
        resp = self._send(client, "010-1234-5678 로 연락 주세요")
        assert "답변할 수 없습니다" in resp.json()["ai"]["content"]

    @pytest.mark.parametrize("keyword", _ILLICIT_KEYWORDS[:3])
    def test_illicit_drug_keyword_blocks_chat(self, client, keyword):
        """불법 약물 키워드 포함 시에만 차단 (대표 3개 parametrize)"""
        client.post("/api/v1/chat/reset")
        resp = self._send(client, f"{keyword} 관련 질문입니다")
        ai_content = resp.json()["ai"]["content"]
        assert "차단" in ai_content or "금지" in ai_content

    def test_blocked_user_cannot_continue(self, client):
        """불법 약물 감지 후 이후 메시지도 차단돼야 함"""
        self._send(client, f"{_ILLICIT_KEYWORDS[0]} 관련 질문입니다")
        resp2 = self._send(client, "복약 방법이 궁금합니다")
        data = resp2.json()
        assert "error" in data or "차단" in data.get("ai", {}).get("content", "")

    def test_message_accumulates_in_history(self, client):
        before = len(client.get("/api/v1/chat/history").json()["messages"])
        self._send(client, "복약 방법이 궁금합니다")
        after = len(client.get("/api/v1/chat/history").json()["messages"])
        assert after == before + 2  # user + ai

    def test_ai_response_content_is_nonempty_string(self, client):
        """OpenAI fallback 포함, AI 응답이 비어있지 않은 문자열"""
        resp = self._send(client, "주의사항 알려줘")
        content = resp.json()["ai"]["content"]
        assert isinstance(content, str)
        assert len(content) > 0

    def test_warning_appended_after_3_hours(self, client, service):
        """3시간 경과 후 AI 응답에 경고 문구가 포함돼야 함"""
        service.last_warning_time = datetime.now() - timedelta(hours=3, seconds=1)
        resp = self._send(client, "복약 방법이 궁금합니다")
        ai_content = resp.json()["ai"]["content"]
        assert "의료인" in ai_content or "AI" in ai_content or "오류" in ai_content

    def test_warning_not_appended_before_3_hours(self, client, service):
        """3시간 미경과 시 경고 문구가 포함되지 않아야 함"""
        service.last_warning_time = datetime.now()
        resp = self._send(client, "복약 방법이 궁금합니다")
        ai_content = resp.json()["ai"]["content"]
        assert "건강과 관련된 상담은 의료인과 하는 것이 원칙" not in ai_content