"""
공공데이터 drugs.csv → DrugInfo 테이블 일괄 적재(Seeding) 스크립트.

실행 방법 (backend 디렉토리에서):
  uv run python scripts/seed_drugs.py

특징:
  - 이미 데이터가 존재하면 중복 삽입하지 않음 (안전 장치)
  - 1,000건 단위 Chunk Bulk Insert 로 메모리·속도 최적화
  - CSV의 멀티라인 셀(줄바꿈 포함)도 정상 처리
"""

import asyncio
import csv
import os
import sys

# 프로젝트 루트를 sys.path 에 추가하여 app 모듈을 import 할 수 있게 설정
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tortoise import Tortoise

from app.db.databases import TORTOISE_ORM
from app.models.drugs import DrugInfo

# ── 설정 ──────────────────────────────────────
CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "drugs.csv")
CHUNK_SIZE = 1000  # Bulk Insert 1회당 처리 건수

# CSV 헤더 → DrugInfo 모델 필드 매핑
COLUMN_MAP = {
    "약품명": "name",
    "제조사": "manufacturer",
    "효능": "efficacy",
    "복용법": "usage",
    "경고": "warning",
    "주의사항": "precautions",
    "상호작용": "interactions",
    "부작용": "side_effects",
    "보관법": "storage",
}


def clean_value(value: str | None) -> str | None:
    """빈 문자열·공백만 있는 셀을 None 으로 정규화합니다."""
    if value is None:
        return None
    stripped = value.strip()
    return stripped if stripped else None


async def seed() -> None:
    """메인 시딩 로직."""
    # 1) Tortoise ORM 초기화
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas(safe=True)

    # 2) 중복 방어: 이미 데이터가 있으면 스킵
    existing_count = await DrugInfo.all().count()
    if existing_count > 0:
        print(f"⚠️  DrugInfo 테이블에 이미 {existing_count}건의 데이터가 존재합니다. 시딩을 건너뜁니다.")
        await Tortoise.close_connections()
        return

    # 3) CSV 파일 읽기
    csv_path = os.path.abspath(CSV_PATH)
    if not os.path.exists(csv_path):
        print(f"❌ CSV 파일을 찾을 수 없습니다: {csv_path}")
        await Tortoise.close_connections()
        return

    print(f"📂 CSV 파일 경로: {csv_path}")

    with open(csv_path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        buffer: list[DrugInfo] = []
        total_count = 0

        for row in reader:
            # CSV 헤더 → 모델 필드 변환
            model_data: dict = {}
            for csv_col, model_field in COLUMN_MAP.items():
                model_data[model_field] = clean_value(row.get(csv_col))

            # 약품명이 없으면 무효 데이터이므로 스킵
            if not model_data.get("name"):
                continue

            buffer.append(DrugInfo(**model_data))

            # Chunk 단위로 Bulk Insert 실행
            if len(buffer) >= CHUNK_SIZE:
                await DrugInfo.bulk_create(buffer)
                total_count += len(buffer)
                print(f"  ✅ {total_count}건 삽입 완료...")
                buffer.clear()

        # 나머지 데이터 삽입
        if buffer:
            await DrugInfo.bulk_create(buffer)
            total_count += len(buffer)

    print(f"🎉 시딩 완료! 총 {total_count}건의 약품 데이터가 DrugInfo 테이블에 적재되었습니다.")
    await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(seed())
