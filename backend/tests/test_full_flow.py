import asyncio
import os
import sys
import uuid
from datetime import datetime

# sys.path 설정
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.ocr_service import analyze_prescription_via_clova, upload_image_to_s3
from app.models.medications import OcrPrescription, OcrStatus
from app.services.chat import ChatService
from app.models.users import User
from tortoise import Tortoise
from fastapi import BackgroundTasks

async def run_real_test():
    # 1. DB 초기화
    from app.db.databases import TORTOISE_ORM
    await Tortoise.init(config=TORTOISE_ORM)
    
    # 2. 테스트 사용자 확보
    user = await User.filter(email="test@example.com").get_or_none()
    if not user:
        user = await User.create(email="test@example.com", name="테스트", hashed_password="dummy")
    
    # 3. 실제 이미지 처리 (OCR 서비스 함수 직접 호출)
    img_path = "/Users/admin/PycharmProjects/8_project/backend/ocr_test_image/image 복사본.png"
    if not os.path.exists(img_path):
        print(f"❌ 이미지를 찾을 수 없습니다: {img_path}")
        await Tortoise.close_connections()
        return

    print(f"--- 🚀 1단계: 실제 이미지 OCR 처리 시작 ---")
    
    with open(img_path, "rb") as f:
        content = f.read()
        
        # UploadFile 객체 시뮬레이션
        class MockUploadFile:
            def __init__(self, file_content, filename):
                self.file_content = file_content
                self.filename = filename
                self.content_type = "image/png"
            async def read(self): return self.file_content
            async def seek(self, pos): pass

        mock_file = MockUploadFile(content, os.path.basename(img_path))
        
        try:
            # 1) S3 업로드
            print("   (1/3) S3 업로드 중...")
            s3_url = await upload_image_to_s3(mock_file)
            print(f"   ✅ S3 업로드 성공: {s3_url[:60]}...")
            
            # 2) Clova OCR 분석
            print("   (2/3) 네이버 Clova OCR 및 GPT 분석 중...")
            raw_json, parsed_meds = await analyze_prescription_via_clova(s3_url)
            print(f"   ✅ 분석 성공! 추출된 약물: {[m.name for m in parsed_meds]}")
            
            # 3) DB 저장
            ocr_id = f"ocr_{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:6]}"
            await OcrPrescription.create(
                ocr_id=ocr_id,
                user_id=user.id,
                image_url=s3_url,
                status=OcrStatus.PENDING,
                extracted_data={
                    "raw": raw_json,
                    "parsed": [m.model_dump() for m in parsed_meds]
                }
            )
            print(f"   ✅ (3/3) DB 저장 완료: {ocr_id}")
            
        except Exception as e:
            print(f"❌ 분석 과정 중 오류 발생: {e}")
            await Tortoise.close_connections()
            return

    # 4. 챗봇 연동 및 답변 생성
    print("\n--- 🚀 2단계: 챗봇 세션 연동 및 테스트 ---")
    chat_service = ChatService()
    
    # 1) 세션 생성
    session = await chat_service.create_session(user_id=user.id)
    print(f"   채팅 세션 생성됨 (ID: {session.id})")
    
    # 2) PATCH 연동 (오늘 신규 구현한 로직)
    print(f"   세션에 ocr_id({ocr_id}) 연동 중...")
    await chat_service.update_session_ocr_id(session_id=session.id, user_id=user.id, ocr_id=ocr_id)
    print(f"   ✅ 모델 연동 완료")
    
    # 3) AI 답변 요청
    print(f"\n--- 🚀 3단계: AI 답변 생성 질의 ---")
    bg_tasks = BackgroundTasks()
    ai_msg = await chat_service.get_ai_response(
        session_id=session.id,
        user_id=user.id,
        user_message="방금 올린 처방전에 어떤 약들이 있는지 설명해줄래?",
        background_tasks=bg_tasks
    )
    print(f"\n🤖 AI 최종 답변:\n{ai_msg.content}")

    await Tortoise.close_connections()
    print("\n--- ✨ 모든 실전 테스트 완료 ---")

if __name__ == "__main__":
    asyncio.run(run_real_test())
