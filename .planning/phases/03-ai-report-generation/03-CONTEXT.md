# Phase 3: AI Report Generation - Context

**Gathered:** 2026-04-09
**Status:** Ready for planning

<domain>
## Phase Boundary
본 페이즈는 프로젝트 로드맵의 3순위 목표인 "AI 기반 복약 리포트 생성 및 OpenAI 연동"을 완수하는 단계입니다.
사전에 구현된 `openai_service.py` 모듈과 연동하여, 프론트엔드가 요청하는 리포트 생성 API(`POST /api/v1/ai/reports/generate`)의 실제 비즈니스 로직을 구현합니다. 또한 챗봇 팀원이 사용할 백엔드 브릿지 파사드(`get_medication_context_for_chatbot`) 내의 기존 더미(Mock) 데이터를 실제 DB 쿼리 데이터로 교체합니다.

- **성공 기준**:
  - `generate_report` 라우터 에러 없이 비동기(백그라운드)로 리포트 생성 또는 동기로 생성 후 `AiReport` 레코드 저장.
  - 리포트 생성을 위한 복약 준수율(Adherence rate) 계산 로직 구현 및 DB 조회 연결.
  - 완성된 AI 리포트 반환 및 상세 내역(Medication Taken Rate 등)이 `AiReport` 모델에 저장됨.
  - 챗봇 연동용 컨텍스트 반환이 하드코딩에서 `MedicationLog` 쿼리 기반으로 변경됨.
</domain>

<decisions>
## Implementation Decisions

### [D-01] 리포트 생성 비동기 처리
- **결정**: `report_routers.py`의 `/generate` 엔드포인트는 클라이언트의 대기 시간을 줄이기 위해 FastAPI의 `BackgroundTasks`를 사용하여 구현합니다. 엔드포인트는 `generating` 상태를 즉시 반환하고, 백그라운드 워커가 `openai_service`를 호출한 후 `AiReport` 객체를 업데이트합니다.

### [D-02] 더미 데이터 제거 및 DB 조회 통합
- **결정**: 챗봇용 브릿지 함수(`get_medication_context_for_chatbot`)의 기능 중 Mock String을 제거하고, `MedicationLog` 및 연관된 `DrugInfo` 데이터를 직접 조회하여 프롬프트 컨텍스트(문자열 기반 메타데이터)로 조합하도록 구현합니다.

### [D-03] 순응도(Adherence Rate) 집계 간소화 로직
- **결정**: 프로젝트 예시 환경임을 고려하여, 실제 `MedicationIntakeLog`의 데이터를 집계하는 로직을 구현하되 데이터가 충분치 않은 경우 임베디드 더미 데이터를 활용해 데모/테스트가 가능하도록 방어적 로직(Fallback)을 적용합니다.
</decisions>

<canonical_refs>
## Canonical References
- `backend/app/apis/v1/report_routers.py`
- `backend/app/services/openai_service.py`
- `backend/tests/test_openai.py`
- `backend/app/models/medications.py`
</canonical_refs>
