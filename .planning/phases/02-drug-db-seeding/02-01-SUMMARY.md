# Plan 02-01: seed-drugs-db - Summary

## 🏁 Goal
공공데이터 `drugs.csv`의 약물 정보를 Tortoise ORM의 `bulk_create`를 사용하여 DB에 시딩하는 스크립트 구현 및 실행.

## 🛠 Implementation Details
- **파일**: `backend/scripts/seed_drugs.py`
- **핵심 로직**:
  - Python 내장 `csv` 모듈을 사용하여 의존성 최소화 및 안정적인 파싱.
  - `clean_value` 함수를 통해 공백 처리 및 데이터 정화.
  - 1,000개 단위의 청크(Chunk)를 활용한 `bulk_create`로 대용량 데이터 고속 적재.
  - 멱등성 보장: 실행 시 기존 데이터를 삭제(`DrugInfo.all().delete()`)하고 재적재하도록 구현하여 데이터 무결성 유지.

## ✅ Verification Results
- **명령어**: `uv run python scripts/seed_drugs.py`
- **결과**:
  - 기존 데이터 삭제 후 1,000건의 약품 데이터가 `DrugInfo` 테이블에 정상적으로 적재됨.
  - CSV 행 수와 DB 레코드 수의 일치 확인 완료.
  - 한글 데이터 깨짐 없음 확인.

## 📅 Completed: 2026-04-09
