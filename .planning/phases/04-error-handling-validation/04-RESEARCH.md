# Phase 4: Error Handling & System Validation - Research

## Current State Analysis

1. **Docker 컨테이너 동기화 문제 (블로커)**
   - 현상: `.env`에 `DB_HOST=mysql` 로 수정되었으나, `fastapi` 컨테이너가 내려가지 않아 변경사항이 런타임에 주입되지 않음.
   - 결과: `curl` 테스트 과정에서 127.0.0.1 (자기 자신)로 DB를 찾으려고 하여 `DBConnectionError` 500 에러 발생. 
   - 대응: 다음 Execute 실행 시 최우선으로 `docker restart fastapi` 또는 `docker compose down && docker compose up -d` 를 진행하여야 함.

2. **User Constraint 검증 부재 (Internal Server Error 후보)**
   - 현상: `report_routers.py` 내 임시 하드코딩된 `user_id = 1`의 유저 데이터가 현재 로컬 MySQL 의 `users` 테이블에 생성되어 있지 않은 경우, `AiReport.create()` 시도시 `IntegrityError` (외래 키 매핑 실패)가 발생하며 500 서버 장애 유발.
   - 필요 로직: `generate_report` API 상단에 `current_user = await User.get_or_none(id=user_id)` 를 통해 유저 존재 여부를 검증하고 없으면 404/401 핸들링 또는 임시 테스트 유저 생성을 지원해야 함.

3. **FastAPI 글로벌 에러 처리**
   - 현재 500이 날 경우, Starlette 에러 핸들러만 동작해 클라이언트에게 포맷이 예쁘지 않은 `Internal Server Error` 문자열만 내려가고 있음.
   - 추후 팀단위 협업을 위해 글로벌 예외 핸들러나 미들웨어를 도입하여 로그(Logger) 기록 및 통합 JOSN 에러 뱉기 기능이 필요함.

## Evaluated Approaches

### Approach 1: 인프라 (Docker) 1차 재시작 및 API 안정성 보장
- **Pro**: `DBConnectionError` 블로커가 바로 해결되고 다음 테스트가 자연스럽게 통과할 가능성이 높아짐.
- **Con**: 만약 User 1이 DB에 없다면 통신 에러 해결 즉시 ForeignKey 에러에 또다시 직면함. (해결: 사전 유저 확인 로직 함께 도입 필요)

### Approach 2: 더미 유저 생성기 도입 (선택됨)
- 향후 어떤 개발자가 자신의 로컬 도커 환경을 올리더라도, 임시 테스트 `user_id = 1`을 사용할 수 있게끔, 앱 시작 시 또는 테스트용 API 진입 시 `id=1`의 유저가 없다면 자동으로 만들어주는 부트스트랩(Bootstrap) 로직을 적용.
