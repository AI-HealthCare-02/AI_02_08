# Phase 1: 처방전 분석 파이프라인 고도화 (OCR) - Context

**Gathered:** 2026-04-16
**Status:** Ready for planning
**Source:** User's initial requirements and explicit instruction list

<domain>
## Phase Boundary
OCR 인식부터 DB 조회, GPT 폴백까지 전체 파이프라인을 검증하고 최적화. 에러 케이스 분류.
</domain>

<decisions>
## Implementation Decisions

### 검색 기술 (Search Flexibility)
- 단순 일치 검색(Exact Match) 대신 %LIKE% 쿼리 활용하여 약품명(처방명) 오타 대응.

### 오류/할루시네이션 방지 (Fallback Strategy)
- 매칭 대상이 없을 때나 파싱에 실패했을 때 에러를 발생시키지 않고 빈 응답, 부분 응답 등으로 치환할 것 (서비스 이탈 방지 위함).
- 생명과 직결되는 만큼 GPT 환각을 System Prompt로 철저히 통제할 것.

### 다중 질의 일괄 처리 (Performance & Cost)
- 다건의 약품 정보를 GPT에 요청 시 단일 응답으로 한 번에 몰아서 질의(Batch)를 보낼 것.
</decisions>

<canonical_refs>
## Canonical References
No external specs — requirements fully captured in decisions above
</canonical_refs>

<specifics>
## Specific Ideas
에러 케이스 분리 시, HTTP 상태 코드는 적절히 다르게 하고 Enum 포맷을 채택하여 명확히 나눈다.
</specifics>

<deferred>
## Deferred Ideas
약품 간 상호작용 판단, 챗봇 세션, Soft delete 등은 Phase 2 진행이므로 반영 안 함.
</deferred>
