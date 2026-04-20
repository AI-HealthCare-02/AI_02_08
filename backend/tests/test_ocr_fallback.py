import asyncio
import json
import os
import sys

# 백엔드 루트를 시스템 패스에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tortoise import Tortoise

from app.core.config import settings
from app.models.drugs import DrugInfo
from app.services.openai_service import batch_analyze_unmatched_drugs


async def test_fallback_flow():
    # 1. ORM 초기화
    await Tortoise.init(
        db_url=f"mysql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:3306/{settings.DB_NAME}",
        modules={"models": ["app.models.drugs"]},
    )

    # 2. 더미 파싱결과 (OCR & 1차 정규화 통과했다고 치고)
    # 타이레놀8시간이알서방정 -> DB에 존재할 확률 높음 (Exact Match 기대)
    # 파득심 -> '파독심'의 오타, LIKE 매칭 안될수도 있음
    # 존재하지않는우주약물 -> 백프로 DB 미매칭, GPT 폴백 대상
    print("=== [1] 파싱된 더미 약품 입력 ===")
    raw_meds = [
        {"name": "타이레놀8시간이알서방정", "dosage": "1정", "frequency": "3회", "timing": "식후 30분"},
        {"name": "푸라콩", "dosage": "1정", "frequency": "2회", "timing": "식전"},  # 푸라콩정 등 (LIKE Match 기대)
        {"name": "존재하지않는우주약물", "dosage": "2캡슐", "frequency": "1번", "timing": "취침전"},
    ]
    for rw in raw_meds:
        print(rw)

    print("\n=== [2] DB 검색 (Exact/LIKE) ===")
    matched_meds = []
    unmatched_meds = []
    for med in raw_meds:
        name = med.get("name", "").strip()

        # Exact Match
        drug = await DrugInfo.get_or_none(name=name)
        if not drug:
            # LIKE Match
            drug = await DrugInfo.filter(name__icontains=name).first()

        if drug:
            med["description"] = drug.efficacy or "설명 없음"
            matched_meds.append(med)
            print(f"✅ DB 매칭 성공: {name} -> 효능: {med['description'][:40]}...")
        else:
            unmatched_meds.append(med)
            print(f"❌ DB 매칭 실패: {name}")

    if unmatched_meds:
        print(f"\n=== [3] GPT Batch Fallback 호출 ({len(unmatched_meds)}건) ===")
        fallback_desc_map = await batch_analyze_unmatched_drugs(unmatched_meds)
        for med in unmatched_meds:
            med_name = med.get("name")
            med["description"] = fallback_desc_map.get(med_name, "일치하는 약품 정보를 찾을 수 없습니다.")
            print(f"🤖 GPT 병합 결과: {med_name} -> {med['description']}")

    print("\n=== [4] 최종 200 부분 응답용 병합 결과 (Fallback 적용 완료) ===")
    final_meds_data = matched_meds + unmatched_meds
    print(json.dumps(final_meds_data, ensure_ascii=False, indent=2))

    await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(test_fallback_flow())
