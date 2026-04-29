import asyncio
import os

import httpx
from tortoise import Tortoise

from app.db.databases import TORTOISE_ORM
from app.models.users import User
from app.services.jwt import JwtService

BASE_URL = "http://localhost:8001"
TEST_IMAGE_PATH = "/Users/admin/PycharmProjects/8_project/backend/ocr_test_image/rx_01_design_A.png"


async def test_ocr_01_backend():
    print("🚀 [OCR-01] 처방전 이미지 업로드 (Backend) QA 테스트 시작")
    await Tortoise.init(config=TORTOISE_ORM)

    # 1. 토큰 생성
    user = await User.filter(email="new_qa_test@example.com").first()
    if not user:
        print("❌ 테스트용 사용자가 없습니다. 먼저 회원가입 QA를 완료해주세요.")
        await Tortoise.close_connections()
        return

    token_obj = JwtService().create_access_token(user)
    headers = {"Authorization": f"Bearer {token_obj}"}

    async with httpx.AsyncClient(headers=headers, timeout=60.0) as client:
        # 2. PNG 파일 업로드 (AUTH-01-1)
        print(f"\n[OCR-01-1] PNG 파일 업로드 테스트 ({os.path.basename(TEST_IMAGE_PATH)})")
        if not os.path.exists(TEST_IMAGE_PATH):
            print("❌ 테스트 이미지가 존재하지 않습니다.")
        else:
            with open(TEST_IMAGE_PATH, "rb") as f:
                files = {"image": (os.path.basename(TEST_IMAGE_PATH), f, "image/png")}
                resp = await client.post(f"{BASE_URL}/api/v1/ai/ocr/prescription", files=files)

                if resp.status_code == 200:
                    data = resp.json()
                    print(f"✅ 결과: 업로드 성공 (Status: {data.get('status')})")
                    print(f"✅ 결과: OCR ID 발급됨 ({data.get('ocrId')})")
                    if data.get("medications"):
                        print(f"✅ [OCR-01-7] 약 목록 카드 데이터 출력됨 (건수: {len(data['medications'])})")
                        for med in data["medications"]:
                            print(f"   - {med['name']} / {med['dosage']}")
                    else:
                        print("⚠️ 알림: 약물이 추출되지 않았습니다 (이미지 품질 또는 API 제한 가능성)")
                else:
                    print(f"❌ 결과: 실패 ({resp.status_code}, {resp.text})")

        # 3. 5MB 초과 파일 테스트 (OCR-01-3)
        print("\n[OCR-01-3] 5MB 초과 파일 업로드 테스트")
        # 가상의 6MB 파일 생성
        large_file = b"0" * (6 * 1024 * 1024)
        files = {"image": ("large.png", large_file, "image/png")}
        resp = await client.post(f"{BASE_URL}/api/v1/ai/ocr/prescription", files=files)
        if resp.status_code == 400 and "5MB" in resp.text:
            print("✅ 결과: '5MB 이하만 가능합니다' 에러 정상 발생")
        else:
            print(f"❌ 결과: 차단 실패 또는 엉뚱한 응답 ({resp.status_code})")

        # 4. 지원하지 않는 형식 테스트 (OCR-01-4)
        print("\n[OCR-01-4] 지원하지 않는 형식(image/gif) 업로드 테스트")
        files = {"image": ("test.gif", b"GIF89a...", "image/gif")}
        resp = await client.post(f"{BASE_URL}/api/v1/ai/ocr/prescription", files=files)
        if resp.status_code == 400 and "지원하지 않는" in resp.text:
            print("✅ 결과: 지원 불가 형식 에러 정상 발생")
        else:
            print(f"❌ 결과: 차단 실패 또는 엉뚱한 응답 ({resp.status_code})")

    await Tortoise.close_connections()
    print("\n✨ 모든 [OCR-01] Backend QA 테스트 완료")


if __name__ == "__main__":
    asyncio.run(test_ocr_01_backend())
