import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime

import uvicorn
from fastapi import FastAPI, File, HTTPException, UploadFile, status
from pydantic import BaseModel


# Medicine.py의 데이터 구조와 일치시키기 위한 모델 (연동용)
class Medicine(BaseModel):  # 예시 클래스명
    name: str
    category: str
    english_name: str  # 수정
    description: str
    dosage: str | None = ""
    frequency: str | None = ""
    side_effects: str | None = ""  # 수정


# 실제 환경에서는 Medicine.py의 db를 import하여 사용합니다.
# 여기서는 연동 테스트를 위해 임시 db를 정의합니다.
medicine_db = []

app = FastAPI(title="Prescription AI & OCR Integration API")


# --- 1. 데이터 모델 정의 ---
@dataclass
class Message:
    id: str
    content: str
    is_user: bool
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%H:%M"))


# --- 2. 비즈니스 로직 클래스 ---
class PrescriptionService:
    def __init__(self):
        self.messages: list[Message] = [
            Message("1", "안녕하세요! 복약 관련 궁금한 점을 물어보세요.", False),
        ]
        self.quick_replies = ["복약 방법이 있나요?", "주의사항 알려줘", "같이 먹으면 안 되는 약 있어?"]

    async def process_ocr(self, image_bytes: bytes) -> dict:
        """이미지 분석 후 결과 반환 (e약은요 연동 전 임시 구조)"""
        return {
            "analysis_id": str(uuid.uuid4())[:8],
            "medications": [],
            "warnings": "",
            "interactions": "",
            "status": "success",
        }


service = PrescriptionService()


# --- 3. API 엔드포인트 구현 ---
# 1단계: 사진 분석 (이미지 업로드)
@app.post("/api/ocr/analyze")
async def analyze_prescription(file: UploadFile):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="이미지 파일만 가능합니다.")
    image_data = await file.read()
    return await service.process_ocr(image_data)


class MedicationInput(BaseModel):
    name: str
    dosage: str = "미정"
    frequency: str = "미정"


@app.post("/api/ocr/confirm", status_code=status.HTTP_201_CREATED)
async def confirm_prescription(medication_list: list[MedicationInput]):
    """
    와이어프레임의 '확인' 버튼 클릭 시 호출.
    분석된 약물 정보를 받아 Medicine DB에 신규 등록함.
    """
    added_count = 0
    for med in medication_list:
        new_entry = {
            "id": str(uuid.uuid4())[:8],
            "name": med.name,
            "category": "처방약(분석됨)",
            "englishName": "N/A",
            "description": f"{datetime.now().strftime('%Y-%m-%d')} OCR 분석 등록",
            "dosage": med.dosage,
            "frequency": med.frequency,
        }
        medicine_db.append(new_entry)
        added_count += 1
    return {
        "status": "success",
        "message": f"{added_count}개의 약물이 복약 목록에 추가되었습니다.",
        "current_db_size": len(medicine_db),
    }


# [CHAT] 채팅 이력 조회
@app.get("/api/chat/history")
async def get_chat_history():
    return {
        "messages": [asdict(m) for m in service.messages],
        "quick_replies": service.quick_replies,
    }


# [CHAT] 메시지 전송 및 AI 응답
@app.post("/api/chat/send")
async def send_chat(payload: dict[str, str]):
    user_text = payload.get("text", "")
    if not user_text:
        raise HTTPException(status_code=400, detail="내용이 없습니다.")
    user_msg = Message(id=str(uuid.uuid4())[:4], content=user_text, is_user=True)
    ai_msg = Message(id=str(uuid.uuid4())[:4], content=f"'{user_text}'에 대한 답변입니다.", is_user=False)
    service.messages.extend([user_msg, ai_msg])
    return {"user": asdict(user_msg), "ai": asdict(ai_msg)}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)