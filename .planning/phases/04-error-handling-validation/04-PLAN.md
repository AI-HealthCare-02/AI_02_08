---
phase: "04"
plan: "error-handling-validation"
objective: "Docker/로컬 DB 통신 장애(500 Error) 격리 해결 및 API 예외 처리, 통합 에러 응답 구조 구축"
requirements: []
user_setup: []
---

# Phase 04 Plan: Error Handling & System Validation

## 🎯 Goal
로컬/도커 환경의 네트워킹을 강제 동기화하고, API 통신에서 발생할 수 있는 Database Connection, FK(Foreign Key) 에러 등 다양한 500 상태를 차단하거나 프론트엔드가 인지할 수 있는 예쁜 JSON 포맷으로 핸들링합니다.

---

### Wave 1: Docker Environment Sync & Restart
<read_first>
- `backend/.env`
- `docker-compose.yml`
</read_first>

1. **Docker 컨테이너 하드 리셋**
   - **Type**: command
   - **Command**: `docker stop fastapi && docker restart fastapi` (또는 docker compose up -d)
   - **Expected**: 이전에 수정된 `.env` 안의 `DB_HOST=mysql` 변경사항이 FastAPI 서버 안으로 최종 투입되어 `Can't connect to MySQL server` 내부 에러가 사라집니다.

---

### Wave 2: Dummy User Bootstrap & Error Mitigation
<read_first>
- `backend/app/apis/v1/report_routers.py`
- `backend/app/models/users.py`
</read_first>

1. **의존성 검증 로직 적용 (`report_routers.py`)**
   - 현재 임시로 `user_id = 1` 을 주입하고 있습니다. 하지만 DB에 1번 유저가 아예 없다면 `IntegrityError`를 내뿜고 서버가 터집니다.
   - `User.get_or_none(id=1)` 을 체크한 뒤, 존재하지 않는다면 테스트 편의를 위해 백그라운드 환경에서 즉시 생성해주는 부트스트랩 코드를 삽입하거나, 적절한 404/400 (사용자 없음) 예외 처리 로직으로 감싸 시스템의 무결성을 도모합니다.

2. **통합 에러 핸들링 도입 (선택사항)**
   - API 라우터 내에서 `try-except Exception as e:` 블록을 활용하여 불의의 사고가 발생할 경우 곧장 HTTPException(status_code=500, detail="서버 에러가 발생했습니다.") 로 감싸 응답을 파싱할 수 있게 개선합니다.

---

### Wave 3: Integration Verification
1. **API cURL 재검수 (`run_command`)**
   - `curl -X POST http://localhost:8000/api/v1/ai/reports/generate ...` 명령을 재실행합니다.
   - **결과**: `Internal Server Error` 가 아닌, `generating` JSON을 받을 수 있어야 합니다.

## 🛠 <verification>
- `docker ps`를 통해 컨테이너가 최신화되었는지 증명합니다.
- Python 린트 검증: `uv run ruff check . --fix` 와 `test` 가 완료되어야 합니다.

## 🏁 <success_criteria>
- 더 이상 프론트엔드 연동 도중 알 수 없는 500 에러(서버 연결, DB FK 무결성) 로직에서 멈추지 않고, 예측 가능한 범위 내의 에러 JSON 이나 성공 JSON만을 내뿜습니다.
