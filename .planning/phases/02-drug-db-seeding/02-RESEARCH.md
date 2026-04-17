# Phase 2: DB Seeding - Research

## Current State Analysis

1. **DB 모델 구조 확인**
   - 파일: `backend/app/models/drugs.py`
   - 모델명: `DrugInfo`
   - 필드: `name`, `manufacturer`, `efficacy`, `usage`, `warning`, `precautions`, `interactions`, `side_effects`, `storage`, `updated_at`.
   - 특징: `name`은 `CharField(200)` 나머지 텍스트 설명은 `TextField(null=True)`로 정의되어 있어 대용량 문자열을 수용하기 적합함.

2. **CSV 파일 구조 확인**
   - 파일: `data/drugs.csv` (크기: 약 2.1MB, 약 8200개 row)
   - 헤더: `약품명`, `제조사`, `효능`, `복용법`, `경고`, `주의사항`, `상호작용`, `부작용`, `보관법`
   - 특징: 각 칼럼이 `DrugInfo` 모델과 일대일로 매칭 가능, 일부 텍스트 내에 개행문자(`\n`)와 구분자(`,`)가 포함되어 있어 `pandas` 또는 `csv.reader`가 반드시 필요함.

3. **스크립트 실행 환경**
   - Tortoise ORM은 비동기이므로 비동기로 런타임을 띄워주는 `Tortoise.init()` 및 `Tortoise.generate_schemas()`가 필요. (단, 마이그레이션이 이미 되어 있으므로 `aerich upgrade` 상태라 가정하고 연결만 수행하면 됨)
   - 공통 실행 패턴: `cd backend && uv run python -m scripts.seed_drugs`

## Options Evaluated

### Option 1: ORM을 우회한 순수 SQL Insert (`aiomysql`)
- **Pro**: 극도의 성능 제공
- **Con**: 유지보수성이 떨어지고 프로젝트 통일성(Tortoise ORM 사용 원칙) 훼손.

### Option 2: Tortoise ORM `bulk_create` (선택)
- **Pro**: 코드 가독성과 유지보수성이 우수. `bulk_create`는 일반적인 `save()` 반복보다 압도적으로 빠르기 때문에 8000개 로우에 적합.
- **Con**: Python 내장 `csv` 모듈 다이얼렉트를 잘 고려하지 않으면 이스케이프 문자 등 파싱 에러 발생 소지가 있음. -> `csv.DictReader` 사용으로 해결.
