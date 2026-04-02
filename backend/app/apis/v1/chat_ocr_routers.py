from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel

from app.services.chat_ocr_service import chat_ocr_service

chat_ocr_router = APIRouter(tags=["Chat & OCR"])


@chat_ocr_router.post("/ocr/analyze")
async def analyze_prescription(file: UploadFile = Depends()):
    """1 단계: 사진 분석 (e 약은요 연동 실패시 fallback 로직 포함)"""
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="이미지 파일만 가능합니다.")

    image_data = await file.read()
    return await chat_ocr_service.process_ocr(image_data)


class MedicationInput(BaseModel):
    name: str
    dosage: str = "미정"
    frequency: str = "미정"


@chat_ocr_router.post("/ocr/confirm", status_code=status.HTTP_201_CREATED)
async def confirm_prescription(medication_list: list[MedicationInput]):
    """2 단계: 분석 결과 확정 (실제 약 목록에 등록)"""
    return await chat_ocr_service.confirm_prescription(medication_list)


@chat_ocr_router.get("/chat/history")
async def get_chat_history():
    """채팅 이력 조회"""
    from dataclasses import asdict

    return {
        "messages": [asdict(m) for m in chat_ocr_service.messages],
        "quick_replies": chat_ocr_service.quick_replies,
    }


@chat_ocr_router.post("/chat/reset")
async def reset_chat():
    """챗봇 대화 초기화"""
    return chat_ocr_service.reset_chat()


class ChatPayload(BaseModel):
    text: str


@chat_ocr_router.post("/chat/send")
async def send_chat(payload: ChatPayload):
    """메시지 전송 및 AI 응답 (OpenAI 연동 실패시 fallback 포함)"""
    return await chat_ocr_service.send_chat(payload.text)
