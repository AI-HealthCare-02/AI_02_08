---
phase: "02"
plan: "seed-drugs-db"
objective: "공공데이터 drugs.csv의 약물 정보를 DB에 시딩하는 스크립트 작성"
requirements: []
user_setup: []
---

# Phase 02 Plan: Drug DB Seeding

## 🎯 Goal
Tortoise ORM의 `bulk_create` 기능을 활용해 `data/drugs.csv` 데이터를 `DrugInfo` 테이블에 적재하는 멱등성(Idempotency) 보장 시딩 스크립트 작성. 파이썬 내장 `csv` 모듈을 이용하여 빠르게 진행.

---

### Wave 1: 시딩 스크립트 작성
<read_first>
- `backend/app/models/drugs.py`
- `data/drugs.csv`
</read_first>

1. **시딩 스크립트 뼈대 생성** (`backend/scripts/seed_drugs.py`)
   - `asyncio` 및 `Tortoise.init` 환경 세팅.
   - Python 내장 `csv.DictReader`를 사용하여 `../../data/drugs.csv`를 순회.

2. **데이터 처리 및 멱등성 구현**
   - 각 빈 문자열("")를 `None`으로 변환.
   - 멱등성 보장: 스크립트 시작 시 `await DrugInfo.all().delete()` 호출.
   - `DrugInfo` 리스트를 1000개 단위 등 청크(Chunk)로 나누어 `bulk_create`로 삽입.

---

### Wave 2: 동작 검증

1. **동작 검증**
   - **Type**: command
   - **Command**: `cd backend && uv run python scripts/seed_drugs.py`
   - **Expected**: "🎉 시딩 완료!" 메시지 출력.

---

## 🛠 <verification>
- `backend/scripts/seed_drugs.py` 스크립트 실행 후 예외 발생 여부 확인.

## 🏁 <success_criteria>
- 스크립트가 에러 없이 완료되며 `drugs` 테이블에 정상적으로 데이터가 적재됨.
