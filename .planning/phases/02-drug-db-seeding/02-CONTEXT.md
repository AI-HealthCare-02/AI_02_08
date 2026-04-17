# Phase 2: DB Seeding - Context

**Gathered:** 2026-04-09
**Status:** Ready for planning

<domain>
## Phase Boundary
본 페이즈는 프로젝트의 2순위 목표인 "공공데이터 `drugs.csv` 데이터베이스 시딩"을 담당합니다. 
`data/drugs.csv` (약 8000행 이상)의 원시 데이터를 정제하여 MySQL DB의 `drugs` 테이블(Tortoise ORM `DrugInfo` 모델)에 고속으로 일괄 삽입(Bulk Insert)하는 자동화 스크립트를 구현합니다.

- **성공 기준**:
  - `backend/scripts/seed_drugs.py` 단일 스크립트로 동작해야 함.
  - 외부 의존성(pandas 등) 없이 내장 `csv` 모듈을 사용해 메모리 효율적으로 파싱.
  - Tortoise ORM의 `bulk_create`를 사용하여 빠른 속도로 데이터베이스 적재.
</domain>

<decisions>
## Implementation Decisions

### [D-01] CSV 파싱 방식
- **결정**: `pyproject.toml`에 영향을 주지 않도록 `pandas` 대신 Python 내장 `csv` 모듈 다이얼렉트를 활용하여 따옴표로 감싸진 필드(개행 포함 문자열)를 안전하게 디코딩.

### [D-02] 데이터 매핑 기준
- **결정**: `data/drugs.csv`의 헤더(약품명, 제조사, 효능, 복용법, 경고, 주의사항, 상호작용, 부작용, 보관법)를 `app.models.drugs.DrugInfo` 필드와 1:1 매핑.

### [D-03] 중복 처리 및 멱등성 보장
- **결정**: 스크립트는 여러 번 실행되더라도 기존의 데이터를 비우고 새로 채우거나(Truncate/Delete all), 데이터 존재 유무를 확인한 뒤에만 삽입하도록 구성하여 멱등성(Idempotency)을 갖춥니다.
</decisions>

<canonical_refs>
## Canonical References
- `backend/app/models/drugs.py`
- `data/drugs.csv`
</canonical_refs>
