from app.models.faq_item import FaqItem


class FaqRepository:
    def __init__(self):
        self._model = FaqItem

    async def get_active_faqs(self) -> list[FaqItem]:
        return await self._model.filter(is_active=True).order_by("display_order")
