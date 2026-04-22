import asyncio
import os
import sys
import tempfile
import uuid
from datetime import datetime

from fastapi import UploadFile

# 프로젝트 루트 디렉토리를 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.db.databases import TORTOISE_ORM
from app.dtos.chat import AiResponseRequest
from app.models.chat_message import ChatMessage
from app.models.medications import MedicationLog, OcrPrescription, OcrStatus
from app.models.users import User
from app.services.chat import ChatService
from app.services.ocr_service import analyze_prescription_via_clova, upload_image_to_s3
from tortoise import Tortoise

# 백그라운드 태스크 모킹
class MockBackgroundTasks:
    def add_task(self, func, *args, **kwargs):
        # 튜플이나 코루틴 함수를 백그라운드에서 실행하는 척
        asyncio.create_task(func(*args, **kwargs))


async def init_db():
    print("▶ DB 초기화 중...")
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()
    print("▶ DB 초기화 완료.")


async def get_or_create_test_user() -> User:
    user, created = await User.get_or_create(
        email="test_ocr_chat@example.com",
        defaults={"name": "테스트유저", "hashed_password": "dummy"}
    )
    return user


async def run_interactive_test(image_path: str):
    await init_db()
    user = await get_or_create_test_user()
    chat_service = ChatService()
    
    if not os.path.exists(image_path):
        print(f"❌ 파일을 찾을 수 없습니다: {image_path}")
        return

    print(f"\n[1/5] 이미지 S3 업로드 중... ({image_path})")
    
    # UploadFile 객체 모킹
    file_name = os.path.basename(image_path)
    file_bytes = open(image_path, "rb").read()
    
    # 임시 파일로 UploadFile 모방
    with tempfile.SpooledTemporaryFile() as tmp:
        tmp.write(file_bytes)
        tmp.seek(0)
        upload_file = UploadFile(filename=file_name, file=tmp)
        
        try:
            s3_url = await upload_image_to_s3(upload_file)
        except Exception as e:
            print(f"S3 업로드 실패: {e}")
            return
            
    print(f"✅ S3 URL 발급 완료: {s3_url[:50]}...")

    print("\n[2/5] Naver Clova OCR 및 GPT 파싱 분석 중... (토큰 소비)")
    ocr_id = f"ocr_test_{uuid.uuid4().hex[:6]}"
    try:
        raw_json, parsed_medications = await analyze_prescription_via_clova(s3_url)
    except Exception as e:
        print(f"❌ OCR 에러: {e}")
        return

    print("\n✅ 분석 완료! [추출된 약품 목록]:")
    for idx, med in enumerate(parsed_medications, start=1):
        print(f"  {idx}. {med.name} | {med.dosage} | {med.frequency} | {med.timing}")
        print(f"     설명: {med.description}")

    print("\n[3/5] OCR 데이터 보관(최초 저장) 및 확정 처리 중...")
    await OcrPrescription.create(
        ocr_id=ocr_id,
        user_id=user.id,
        image_url=s3_url,
        status=OcrStatus.PENDING,
        extracted_data=raw_json,
    )
    
    # 사용자 '확정(Confirm)' 시뮬레이션
    ocr_record = await OcrPrescription.get(ocr_id=ocr_id)
    ocr_record.status = OcrStatus.CONFIRMED
    await ocr_record.save()
    
    created_meds = []
    for med in parsed_medications:
        m = await MedicationLog.create(
            user_id=user.id,
            ocr_prescription_id=ocr_id,
            name=med.name,
            dosage=med.dosage,
            frequency=med.frequency,
            timing=med.timing,
        )
        created_meds.append(m)
    print(f"✅ DB 확정 완료. (총 {len(created_meds)}개 MedicationLog 등록됨)")

    print("\n[4/5] 챗봇 세션(채팅방) 생성 중...")
    session = await chat_service.create_session(user_id=user.id, ocr_id=ocr_id)
    print(f"✅ 채팅방 생성 완료. Session ID: {session.id}")

    print("\n[5/5] 대화 시작! 챗봇과 대화해보세요. (종료하려면 'exit'나 'quit' 입력)")
    print("---------------------------------------------------------")
    
    bg_tasks = MockBackgroundTasks()

    while True:
        user_input = input("😀 나: ")
        if user_input.strip().lower() in ["exit", "quit", "종료"]:
            print("챗봇 테스트를 종료합니다.")
            break
            
        if not user_input.strip():
            continue

        # 유저 메시지 선저장
        await chat_service.save_message(
            session_id=session.id,
            user_id=user.id,
            content=user_input,
            is_faq=False
        )

        print("🤖 AI 약사 (생성 중...):", end=" ")
        
        try:
            # 챗봇 답변 획득 시 1번 과정에서 붙인 get_medication_context_for_chatbot이 발동됨
            ai_msg = await chat_service.get_ai_response(
                session_id=session.id,
                user_id=user.id,
                user_message=user_input,
                background_tasks=bg_tasks
            )
            print(f"\n>> {ai_msg.content}\n")
        except Exception as e:
            print(f"\n❌ 챗봇 답변 실패: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: uv run backend/scripts/test_ocr_interactive.py <처방전_이미지_경로>")
        sys.exit(1)
        
    image_to_test = sys.argv[1]
    asyncio.run(run_interactive_test(image_to_test))
