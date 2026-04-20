import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.openai_service import summarize_and_deidentify_chat


async def test_summarization():
    print("=== [1] 더미 대화 데이터 (5턴) 생성 ===")
    dummy_messages = [
        {"role": "user", "content": "선생님, 저 김철수인데요. 오늘 타이레놀을 먹었는데 속이 좀 쓰려요."},
        {
            "role": "assistant",
            "content": "타이레놀 복용 후 속쓰림이 있으시군요. 식사 후 복용하셨나요? [출처: 식품의약품안전처 e약은요]",
        },
        {"role": "user", "content": "아니요, 아침에 바빠서 빈속에 먹었어요."},
        {
            "role": "assistant",
            "content": "타이레놀 자체는 위장장애가 적은 편이지만, 빈속에 드시면 속쓰림을 유발할 수 있습니다. 다음부터는 식후에 복용하시길 권장합니다. [출처: 식품의약품안전처 e약은요]",
        },
        {"role": "user", "content": "그렇군요. 그럼 지금이라도 우유 같은 걸 좀 마시는 게 나을까요?"},
        {
            "role": "assistant",
            "content": "네, 현재 속쓰림이 심하시다면 따뜻한 물이나 우유를 드시는 것이 일시적으로 도움이 될 수 있습니다.",
        },
        {"role": "user", "content": "알겠습니다. 그리고 내일 서울 출장가는데 약을 몇 알 챙겨가야 할까요?"},
        {
            "role": "assistant",
            "content": "통증이 지속될 경우를 대비해 하루 최대 복용량을 넘지 않는 선에서 여유분을 챙기시는 것이 좋습니다.",
        },
        {"role": "user", "content": "감사합니다. 조심해서 다녀올게요."},
        {
            "role": "assistant",
            "content": "네, 무사히 다녀오시길 바랍니다. 추가로 궁금한 점이 생기면 언제든 질문해 주세요.",
        },
    ]

    for msg in dummy_messages:
        print(f"[{msg['role'].upper()}] {msg['content']}")

    print("\n=== [2] 백그라운드 요약(Summarization) 테스트 실행 ===")
    summary_result = await summarize_and_deidentify_chat(dummy_messages)

    print("\n=== [3] 요약 결과 확인 ===")
    print(f"결과: {summary_result}")

    # 여기서 PII(김철수, 서울 출장 등)가 사라지고 약(타이레놀, 빈속, 속쓰림)에 대한 맥락만 남아야 성공
    if "김철수" in summary_result or "서울" in summary_result:
        print("❌ 실패: 개인식별정보(PII) 혹은 사담이 요약본에 포함되었습니다.")
    else:
        print("✅ 성공: PII가 배제되고 의료 데이터 위주의 깔끔한 요약이 완성되었습니다.")


if __name__ == "__main__":
    asyncio.run(test_summarization())
