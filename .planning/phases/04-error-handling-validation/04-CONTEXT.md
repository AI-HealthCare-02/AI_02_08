# Phase 4: Error Handling & System Validation - Context

**Gathered:** 2026-04-09
**Status:** Ready for planning

<domain>
## Phase Boundary
본 페이즈(Phase 4)는 프로젝트 로드맵의 마지막 단계인 "검증 및 고도화" 단계입니다. 
주요 목표는 그동안 구축한 시스템의 불안명성을 해결하고 예외 처리를 강화하는 것입니다.
특히, 로컬 네트워크 및 Docker 컨테이너 간의 통신에서 발생하는 문제(예: `DBConnectionError`)를 완벽히 해결하고, 프로덕션이나 타 팀이 연동할 때 안정성을 보장하도록 에러 응답 체계를 다듬습니다.

- **성공 기준**:
  - `fastapi` Docker 컨테이너가 `mysql` 컨테이너와 오류 없이 통신할 수 있도록 환경 및 빌드 설정 최적화.
  - `/api/v1/ai/reports/generate`를 포함한 핵심 API 호출 시 500 서버 에러 발생 방지 및 실패 시 명확한 에러 코드/메시지 반환.
</domain>

<decisions>
## Implementation Decisions

### [D-01] Docker Compose 환경 변수 동기화 및 핫 리로딩 보장 
- **결정**: 현재 `.env` 정보 업데이트 후 컨테이너가 내려가지 않아 발생한 `Internal Server Error(500)` 이슈를 최우선으로 해결합니다. `fastapi`의 DB 호스트 설정을 `mysql`로 영구 적용하고 Docker 컴포즈를 강제 재시작하여 환경을 동기화합니다.

### [D-02] FastAPI Custom Exception Handler 부착
- **결정**: 통합 서버 에러(500) 상황 발생 시, 단순히 스택 트레이스만 반환되는 것을 막고, 로깅 시스템을 부착하여 디버깅을 편하게 만들며 사용자에게 통일된 JSON 형식(`{"detail": "Internal System Error..."}`)을 응답하도록 예외 핸들링을 적용합니다.

### [D-03] 데이터 부재로 인한 조회 500 에러 차단
- **결정**: 유저가 아직 생성되지 않은 상태(예: `user_id = 1` 가 DB에 없는 상태)에서 API를 요청했을 때 발생할 수 있는 ForeignKey Constraint 에러를 방지합니다. 서비스 로직 이전에 유저의 존재 여부를 1차 검증(Validate)하는 로직을 추가합니다.
</decisions>

<canonical_refs>
## Canonical References
- `backend/docker-compose.yml`
- `backend/.env`
- `backend/app/apis/v1/report_routers.py`
- `backend/app/main.py`
</canonical_refs>
