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
    
    # 중복 방지를 위한 in-memory Set (표준화 기준으로 약품명 + 제조사를 결합)
    seen_drugs = set()

    for csv_path in csv_files:
        print(f"📂 CSV 처리 중: {csv_path}")

        try:
            with open(csv_path, encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                
                # BOM(Byte Order Mark) 등이 섞여있을 때를 대비해 키들의 앞뒤 공백을 제거한 딕셔너리로 만듦
                buffer: list[DrugInfo] = []
                file_count = 0

                for raw_row in reader:
                    row = {k.strip(): v for k, v in raw_row.items() if k is not None}
                    
                    # CSV 헤더 → 모델 필드 변환
                    model_data: dict = {}
                    for model_field, possible_csv_cols in COLUMN_MAP.items():
                        # 매핑 목록에 있는 키 중 CSV에 존재하는 값을 찾음
                        val = None
                        for col in possible_csv_cols:
                            if col in row:
                                val = row[col]
                                break
                        model_data[model_field] = clean_value(val)

                    # 약품명이 없으면 무효 데이터이므로 스킵
                    name = model_data.get("name")
                    manufacturer = model_data.get("manufacturer")
                    
                    if not name:
                        continue

                    # 중복 체크: (약품명, 제조사) 쌍이 이미 등록되었는지 확인
                    # 데이터 일관성을 위해 대소문자나 공백으로 인한 엇갈림을 최소화
                    unique_key = (name.replace(" ", "").lower(), manufacturer.replace(" ", "").lower() if manufacturer else "")
                    
                    if unique_key in seen_drugs:
                        duplicate_count += 1
                        continue
                        
                    seen_drugs.add(unique_key)
                    buffer.append(DrugInfo(**model_data))

                    # Chunk 단위로 Bulk Insert 실행
                    if len(buffer) >= CHUNK_SIZE:
                        await DrugInfo.bulk_create(buffer)
                        file_count += len(buffer)
                        print(f"  ✅ {file_count}건 삽입 완료...")
                        buffer.clear()

                # 나머지 데이터 삽입
                if buffer:
                    await DrugInfo.bulk_create(buffer)
                    file_count += len(buffer)
                
                total_count += file_count
                print(f"  👉 {os.path.basename(csv_path)} 에서 총 {file_count}건 적재 완료.\n")

        except Exception as e:
            print(f"❌ 파일 처리 중 에러 발생 ({csv_path}): {e}")

    print(f"🎉 시딩 완료! 총 {total_count}건의 약품 데이터가 적재되었으며, 중복된 {duplicate_count}건은 무시되었습니다.")
    await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(seed())
