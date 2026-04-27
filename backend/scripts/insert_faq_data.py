import asyncio
import os
import sys

# 프로젝트 루트를 sys.path에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tortoise import Tortoise
from app.db.databases import TORTOISE_ORM
from app.models.faq_item import FaqItem


async def insert_faq_data():
    """FAQ 데이터 삽입 스크립트"""
    # Tortoise ORM 초기화
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas(safe=True)

    faqs = [
        {
            "question": "부작용이 있나요?",
            "answer": "일반적인 부작용은 다음과 같습니다.",
            "display_order": 1,
            "is_active": True
        },
        {
            "question": "주의사항 알려주세요",
            "answer": "주의사항은 다음과 같습니다.",
            "display_order": 2,
            "is_active": True
        }
    ]

    # 기존 FAQ 삭제 (재실행 대비)
    existing_count = await FaqItem.all().count()
    if existing_count > 0:
        print(f"기존 FAQ {existing_count}건 삭제 중...")
        await FaqItem.all().delete()

    # FAQ 삽입
    for faq_data in faqs:
        await FaqItem.create(**faq_data)

    print(f"FAQ 데이터 {len(faqs)}건 삽입 완료!")

    # 연결 종료
    await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(insert_faq_data())