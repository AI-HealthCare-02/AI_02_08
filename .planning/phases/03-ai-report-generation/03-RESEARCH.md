# Phase 3: AI Report Generation - Research

## Current State Analysis

1. **라우터 (API 엔드포인트)**
   - 파일: `backend/app/apis/v1/report_routers.py`
   - `generate_report(body: ReportGenerateRequest)` 부분에 TODO로 주석 처리된 핵심 로직이 남아있음.
   - 현재 더미/임시 코드로 "generating" 상태 응답만 반환하고, 실제 데이터 연산이나 저장이 진행되지 않음.
   - `FastAPI`의 `BackgroundTasks` 활용을 위해 임포트 추가 필요.

2. **OpenAI 서비스 연결부**
   - 파일: `backend/app/services/openai_service.py`
   - `generate_medication_report()`: 파라미터로 `adherence_rate`, `medication_records`, `user_conditions`, `period`를 받아 실제 리포트를 작성할 수 있도록 잘 구현되어 있음. (`tests/test_openai.py` 통과)
   - `get_medication_context_for_chatbot()`: 하드코딩된 더미 문자열 반환 중 → `MedicationLog` 모델과 조인하여 실제 데이터를 문자열로 조합하는 쿼리 로직 교체 필요.

3. **데이터베이스 모델**
   - 파일: `backend/app/models/medications.py`
   - `MedicationIntakeLog`: 해당 테이블에서 `taken` 및 `pending/skipped` 수를 기반으로 순응도(adherence_rate)와 컨디션 메모(`opinion`) 요소를 추출해야 함.
   - 테이블 릴레이션: `AiReport` 생성을 위해선 `User`, `MedicationLog`, `MedicationIntakeLog` 와 관계형 조회가 필수적임.

## Evaluated Approaches

### Approach 1: 동기식 API (Synchronous Calling)
- **Pro**: 구조 도출 코드가 단순하며 관리하기 쉬움.
- **Con**: OpenAI API 호출 시간(약 1~5초) 동안 HTTP 연결이 유지되어 클라이언트 응답 체감 속도가 떨어짐.

### Approach 2: FastAPI `BackgroundTasks` (선택된 접근식)
- **Pro**: FastAPI 내장 기능으로 별도 의존성(Celery/Redis 큐) 추가 없이 OpenAI API의 장시간 워크로드를 비동기로 처리할 수 있으며 클라이언트에는 202 Accepted 응답을 즉시 줄 수 있음.
- **Con**: 워커 예외 처리 및 `AiReport` 모델의 상태(`COMPLETED`, `FAILED`)를 비동기로 업데이트해야 하는 로직 구현 필요. 기존 코드에서도 이미 `status` 컬럼 관리를 염두에 두고 있었으므로, 이 방법이 적합함.

## Key Changes Needed
1. `report_routers.py`에 `BackgroundTasks` 파라미터 추가.
2. 백그라운드용 핸들러 워커(Worker) 콜백 함수 개발.
3. 데이터 쿼리 로직 (순응도 추출 및 리스트업) 구현 코드 작성.
4. `openai_service.py` 내부의 챗봇 함수용 ORM 쿼리 작성.
