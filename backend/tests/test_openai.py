import asyncio
import os
import sys

# 프로젝트 백엔드 루트를 시스템 패스에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.openai_service import generate_medication_report, get_medication_context_for_chatbot


async def test_openai_integration():
    print("=" * 60)
    print("🚀 [TEST] OpenAI GPT-4o mini 복약 리포트 생성 테스트")
    print("=" * 60)

    # 더미 데이터 구성 (실제로는 DB에서 환자의 1주일치 데이터를 가져옵니다)
    adherence_rate = 75
    medication_records = [
        {"약품명": "타이레놀500mg", "복용률": "100%", "특이사항": "잘 챙겨드심"},
        {"약품명": "위장약", "복용률": "50%", "특이사항": "아침 약을 자주 거름"},
    ]
    user_conditions = ["화요일에 약한 두통이 있었음", "아침에 속이 조금 쓰림"]

    print("\n[입력 데이터]")
    print(f"- 순응도: {adherence_rate}%")
    print(f"- 복약 기록: {medication_records}")
    print(f"- 환자 메모(컨디션): {user_conditions}")
    print("-" * 60)

    print("⏳ AI 분석 중... (OpenAI API 호출)")

    # 실제 OpenAPI 함수 호출
    report_result = await generate_medication_report(
        adherence_rate=adherence_rate,
        medication_records=medication_records,
        user_conditions=user_conditions,
        period="weekly",
    )

    print("\n[✨ AI 약사 리포트 코멘트 결과]")
    print(report_result)
    print("=" * 60)

    # 타 팀원(챗봇)용 브릿지 함수 테스트
    print("\n[봇 팀원용 데이터 인터페이스 테스트]")

    # DB 쿼리(MedicationLog.filter)를 더미 객체로 모킹 (Mocking)
    from app.services.openai_service import MedicationLog

    original_filter = MedicationLog.filter

    class DummyLog:
        name = "임시 테스트용 약"
        dosage = "1정"
        frequency = "1일 3회"
        timing = "식후 30분"
        caution = "충분한 물과 함께 복용"

    async def dummy_filter(*args, **kwargs):
        return [DummyLog()]

    MedicationLog.filter = dummy_filter
    try:
        chatbot_context = await get_medication_context_for_chatbot(user_id=1)
        print(chatbot_context)
    finally:
        MedicationLog.filter = original_filter

    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_openai_integration())
