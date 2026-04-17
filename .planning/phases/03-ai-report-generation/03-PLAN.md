---
phase: "03"
plan: "ai-report-generation"
objective: "OpenAI 리포트 생성 API의 비동기 백그라운드 태스크 구현 및 챗봇 연동 DTO 매핑"
requirements: []
user_setup: []
---

# Phase 03 Plan: AI Report Generation Integration

## 🎯 Goal
사용자의 요청에 따라 OpenAI를 호출해 맞춤형 건강 관리 리포트를 생성하는 백엔드 파이프라인(`report_routers.py`) 기능 완성. 기존에 하드코딩 되어있던 로직들을 Tortoise ORM 기반 실제 쿼리로 교체하고 API 응답 체계를 정립한다.

---

### Wave 1: Report Generation Background Task (API 고도화)
<read_first>
- `backend/app/apis/v1/report_routers.py`
- `backend/app/services/openai_service.py`
</read_first>

1. **BackgroundTasks 로직 추가 (`report_routers.py`)**
   - FastAPI 라우터 `generate_report` 에 `BackgroundTasks` 매개변수 도입.
   - 데이터 집계, AI 호출, 모델 저장을 담당할 비동기 헬퍼 코루틴 `_process_report_task(report_id, period, user_id)` 구현.

2. **통계 데이터 집계 처리기**
   - `MedicationIntakeLog`의 "taken" vs "pending/skipped" 수를 기준으로 순응도(%)를 계산하는 쿼리 및 변환 로직 구성. 
   - `user_conditions` (opinion 항목) 내용들을 List[str]로 모아 프롬프트에 주입.

3. **OpenAI 서비스 실제 매핑**
   - `generate_medication_report()` 호출 결과 얻은 코멘트를 `AiReport` 레코드의 `ai_comment`, `condition_summary`, `adherence_rate` 등에 매핑 후, 상태(status)를 `COMPLETED` 또는 예외 시 `FAILED` 로 DB 업데이트.

---

### Wave 2: Chatbot Context Bridge (데이터 소스 연동)
<read_first>
- `backend/app/services/openai_service.py`
</read_first>

1. **`get_medication_context_for_chatbot` 리팩토링**
   - 현재 더미 텍스트를 반환하는 부분을 제거.
   - `MedicationLog.filter(user_id=user_id)` 를 통해 실제 복용 중인 약품명, 용법(`dosage`, `frequency`), 주의사항(`caution` 또는 연관된 `DrugInfo.warning`) 정보를 조회 후 `\n` 구분된 텍스트 컨텍스트로 렌더링하여 반환.

---

### Wave 3: Verification

1. **동작 검증 (개발자 테스트)**
   - **Type**: command
   - **Command**: `uv run pytest tests/test_openai.py` 
   - **Expected**: 기존 테스트가 손상 없이 정상 작동하는지 확인. 라우터 관련 추가 테스트가 필요하다면 추후 고도화 단계에서 진행.

---

## 🛠 <verification>
- Python 린트 검증: `uv run ruff check . --fix` 및 `uv run ruff format .` 통과.
- 코드 상 하드코딩된 더미 항목들(예: mock_context)이 올바른 비즈니스 워크플로우로 바뀐 것을 확인가능해야 함.

## 🏁 <success_criteria>
- `POST /api/v1/ai/reports/generate` API가 블로킹 없이 202 Accepted 를 잘 내어주면서도, 백그라운드에서 AI 리포트를 성공적으로 DB에 Insert 함.
- 챗봇 팀원이 사용할 Context 조회 메서드가 안정적인 String 포맷을 제공함.
