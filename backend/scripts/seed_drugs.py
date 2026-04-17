"""
공공데이터 (다중 CSV) → DrugInfo 테이블 일괄 적재(Seeding) 스크립트.

실행 방법 (backend 디렉토리에서):
  uv run python scripts/seed_drugs.py

특징:
  - data 폴더 안의 모든 .csv 파일을 찾아 읽어옴
  - CSV 파일의 다양한 헤더 명(한글, 영문 등)을 유연하게 맵핑
  - 기존 데이터 삭제 후 일괄 적재
  - 이름과 제조사를 기준으로 중복 데이터 삽입 방지 로직 포함
  - 1,000건 단위 Chunk Bulk Insert 로 메모리·속도 최적화
"""

import asyncio
import csv
import glob
import os
import sys

# 프로젝트 루트를 sys.path 에 추가하여 app 모듈을 import 할 수 있게 설정
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tortoise import Tortoise

from app.db.databases import TORTOISE_ORM
from app.models.drugs import DrugInfo

# ── 설정 ──────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
CHUNK_SIZE = 1000  # Bulk Insert 1회당 처리 건수

# 모델 필드 → 처리 가능한 CSV 헤더 목록 매핑
COLUMN_MAP = {
    "name": ["약품명", "itemName"],
    "manufacturer": ["제조사", "entpName"],
    "efficacy": ["효능", "efcyQesitm"],
    "usage": ["복용법", "useMethodQesitm"],
    "warning": ["경고", "atpnWarnQesitm"],
    "precautions": ["주의사항", "atpnQesitm"],
    "interactions": ["상호작용", "intrcQesitm"],
    "side_effects": ["부작용", "seQesitm"],
    "storage": ["보관법", "depositMethodQesitm"],
}


def clean_value(value: str | None) -> str | None:
    """빈 문자열·공백만 있는 셀을 None 으로 정규화합니다."""
    if value is None:
        return None
    stripped = value.strip()
    return stripped if stripped else None


async def _process_csv_file(csv_path: str, seen_drugs: set) -> tuple[int, int]:
    file_count = 0
    duplicate_count = 0
    try:
        with open(csv_path, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            buffer: list[DrugInfo] = []

            for raw_row in reader:
                row = {k.strip(): v for k, v in raw_row.items() if k is not None}

                model_data: dict = {}
                for model_field, possible_csv_cols in COLUMN_MAP.items():
                    val = None
                    for col in possible_csv_cols:
                        if col in row:
                            val = row[col]
                            break
                    model_data[model_field] = clean_value(val)

                name = model_data.get("name")
                manufacturer = model_data.get("manufacturer")

                if not name:
                    continue

                unique_key = (
                    name.replace(" ", "").lower(),
                    manufacturer.replace(" ", "").lower() if manufacturer else "",
                )

                if unique_key in seen_drugs:
                    duplicate_count += 1
                    continue

                seen_drugs.add(unique_key)
                buffer.append(DrugInfo(**model_data))

                if len(buffer) >= CHUNK_SIZE:
                    await DrugInfo.bulk_create(buffer)
                    file_count += len(buffer)
                    print(f"  ✅ {file_count}건 삽입 완료...")
                    buffer.clear()

            if buffer:
                await DrugInfo.bulk_create(buffer)
                file_count += len(buffer)

            print(f"  👉 {os.path.basename(csv_path)} 에서 총 {file_count}건 적재 완료.\n")

    except Exception as e:
        print(f"❌ 파일 처리 중 에러 발생 ({csv_path}): {e}")

    return file_count, duplicate_count


async def seed() -> None:
    """메인 시딩 로직."""
    # 1) Tortoise ORM 초기화
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas(safe=True)

    # 2) CSV 파일 목록 찾기
    csv_pattern = os.path.join(os.path.abspath(DATA_DIR), "*.csv")
    csv_files = glob.glob(csv_pattern)

    if not csv_files:
        print(f"❌ CSV 파일을 찾을 수 없습니다: {csv_pattern}")
        await Tortoise.close_connections()
        return

    # 3) 기존 데이터 초기화 (명확한 재적재를 위해 삭제)
    existing_count = await DrugInfo.all().count()
    if existing_count > 0:
        print(
            f"⚠️  DrugInfo 테이블에 이미 {existing_count}건의 데이터가 존재합니다. 기존 데이터를 삭제하고 다시 시딩합니다..."
        )
        await DrugInfo.all().delete()

    # 4) 각 CSV 순회하며 읽기
    total_count = 0
    duplicate_count = 0
    seen_drugs = set()

    for csv_path in csv_files:
        print(f"📂 CSV 처리 중: {csv_path}")
        f_count, d_count = await _process_csv_file(csv_path, seen_drugs)
        total_count += f_count
        duplicate_count += d_count

    print(
        f"🎉 시딩 완료! 총 {total_count}건의 약품 데이터가 적재되었으며, 중복된 {duplicate_count}건은 무시되었습니다."
    )
    await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(seed())
