from app.models.faq_item import FaqItem


class FaqRepository:
    def __init__(self):
        self._model = FaqItem

    async def get_active_faqs(self) -> list[FaqItem]:
        return await self._model.filter(is_active=True).order_by("display_order")

    async def find_answer_by_question(self, question: str) -> str | None:
        """
        질문과 유사한 FAQ 답변 찾기 (부분 일치 허용)

        Args:
            question: 사용자 질문 (예: "부작용이 있나요?")

        Returns:
            str | None: FAQ 답변 또는 None
        """
        # 1차: 정확히 일치
        faq = await self._model.filter(
            question=question,
            is_active=True,
        ).first()

        if faq:
            return faq.answer

        # 2차: 핵심 키워드로 매칭
        keywords = ['부작용', '주의사항', '상호작용', '같이']
        for keyword in keywords:
            if keyword in question:
                faq = await self._model.filter(
                    question__icontains=keyword,
                    is_active=True,
                ).first()
                if faq:
                    return faq.answer

        return None