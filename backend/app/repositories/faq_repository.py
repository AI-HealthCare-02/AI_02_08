from app.models.faq_item import FaqItem


class FaqRepository:
    def __init__(self):
        self._model = FaqItem

    async def get_active_faqs(self) -> list[FaqItem]:
        return await self._model.filter(is_active=True).order_by("display_order")

    async def find_answer_by_question(self, question: str) -> str | None:
        """
        질문과 정확히 일치하는 FAQ 답변 찾기

        Args:
            question: 사용자 질문 (예: "부작용이 있나요?")

        Returns:
            str | None: FAQ 답변 또는 None
        """
        faq = await self._model.filter(
            question=question,  # 정확히 일치
            is_active=True,
        ).first()

        return faq.answer if faq else None
