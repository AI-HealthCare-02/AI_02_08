---
wave: 1
depends_on: []
files_modified:
  - app/services/ocr_service.py
  - app/services/openai_service.py
  - app/apis/v1/ocr_routers.py
autonomous: true
---

# Phase 1: 처방전 분석 파이프라인 고도화 (OCR)

## Goal
스크립트가 세팅된 시딩 데이터를 기반으로 OCR 추출 및 GPT 보완, 에러 처리 로직을 안정적으로 구성한다.

## Requirements
- OCR-01
- OCR-02
- OCR-03
- OCR-04

## Tasks

<task>
<description>
`DrugInfo` 등 약품 모델 검색을 위해 `%LIKE%` 쿼리와 Exact Match 지원 로직 구현.
</description>
<read_first>
- app/models/drugs.py
- app/services/ocr_service.py
</read_first>
<action>
`app/services/ocr_service.py` 내부의 약품 파싱 및 조회 로직을 보완한다:
1. 추출된 텍스트 배열을 순회하며 Tortoise ORM을 이용해 약품 정보를 검색하는 로직을 고도화한다.
2. 약품명이 완벽히 일치하는(Exact Match) 데이터를 일차적으로 찾는다 (`name=...`).
3. 완전 일치하는 약이 없을 경우 `%약품명%` 패턴을 사용하는 LIKE 검색(예: `.filter(name__icontains=...)`)을 수행하여 오타나 축약어를 보정하여 조회한다.
</action>
<acceptance_criteria>
`app/services/ocr_service.py` 내의 쿼리 로직에 `icontains` 등의 LIKE 검색 메서드가 포함되어야 한다.
</acceptance_criteria>
</task>

<task>
<description>
GPT 빈값 보완(Fallback)용 비동기 Batch 파이프라인 및 환각 방지 프롬프트 튜닝
</description>
<read_first>
- app/services/openai_service.py
</read_first>
<action>
`app/services/openai_service.py` 로직을 수정하여 보완 로직을 구축한다:
1. 여러 개의 미매칭 약품을 리스트나 딕셔너리로 묶어 단 번에(Batch) GPT에 질의를 보내는 구조로 최적화한다.
2. 전달하는 System Prompt를 크게 수정한다: "너는 의료 전문가다. 모르는 약품명에 대해서는 절대로 효능이나 부작용을 지어내지 말 것. 파악 불가한 약품은 빈 정보로 두되 복용 시간 등 스케줄을 반환하는 임시 템플릿(Fallback 형태)을 사용하여 반환해야 한다"는 맥락의 지시어를 하드코딩한다.
</action>
<acceptance_criteria>
`openai_service.py` 파일 내에 해당 "의료 전문가", "지어내지 말 것" 혹은 유사한 내용의 문자열 프롬프트 지시사항이 포함되어야 한다.
</acceptance_criteria>
</task>

<task>
<description>
ocr_routers.py 실패 처리, 병합 응답 및 에러 상태 코드 세분화
</description>
<read_first>
- app/apis/v1/ocr_routers.py
</read_first>
<action>
`app/apis/v1/ocr_routers.py` 서비스의 OCR 분석 엔드포인트를 고도화한다:
1. 클로바 OCR 연동 실패, GPT 응답 실패 등의 케이스를 구별하기 위한 에러 메시지(Enum이나 문자열 분기)를 도입한다.
2. OCR과 조회 중에 일부 약품은 데이터베이스에서 찾고 일부는 못 찾는 상황(부분 실패)이 발생해도 500 인터널 에러로 죽지 않고, 유효한 데이터만이라도 병합하여 Client가 스케줄러를 세팅할 수 있는 200번대 JSON 응답을 내보내도록 수정한다.
</action>
<acceptance_criteria>
`ocr_routers.py` 또는 관련 모듈에 에러 케이스 분류(`OCR 실패`, `GPT 실패` 등)와 `try-except` 블록이 확충되었고, 강제로 에러를 Throw하는 대신 부분 응답을 생성하는 반환 구조가 정의되어야 함.
</acceptance_criteria>
</task>

## Verification
- Pytest나 직접 로컬 컨테이너 기동을 통해 어플리케이션이 정상적으로 로드되는지 확인.
- 더미 혹은 존재하지 않는 약품명을 인풋으로 넣어보며 500 에러를 뱉지 않고 200번 부분응답 및 Fallback이 일어나는지 응답 로그를 통해 확인.
