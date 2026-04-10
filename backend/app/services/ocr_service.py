import time
import uuid

import aioboto3
import httpx
from fastapi import UploadFile

from app.core.config import settings
from app.dtos.medications import OcrMedicationItem


async def upload_image_to_s3(file: UploadFile) -> str:
    """
    업로드된 처방전 이미지를 AWS S3에 비동기로 저장하고,
    OCR 분석을 위한 이미지 접근 URL을 반환합니다.
    """
    file_bytes = await file.read()
    file_extension = file.filename.split(".")[-1] if file.filename else "jpg"
    unique_filename = f"prescriptions/{uuid.uuid4().hex}.{file_extension}"

    session = aioboto3.Session(
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION,
    )

    async with session.client("s3") as s3:
        await s3.put_object(
            Bucket=settings.AWS_S3_BUCKET,
            Key=unique_filename,
            Body=file_bytes,
            ContentType=file.content_type or "image/jpeg",
        )

        # 외부 클라우드(CLOVA)가 이미지에 접근할 수 있도록 Presigned URL 생성 (1시간 유효)
        url = await s3.generate_presigned_url(
            "get_object", Params={"Bucket": settings.AWS_S3_BUCKET, "Key": unique_filename}, ExpiresIn=3600
        )

    return url


async def analyze_prescription_via_clova(image_url: str) -> tuple[dict, list[OcrMedicationItem]]:
    """
    이미지 URL을 네이버 클로바 OCR API에 전송하여 텍스트를 추출하고,
    정규식/휴리스틱을 통해 약품명, 용량, 횟수 등을 파싱합니다.

    Returns:
        원본 Json 응답 데이터, 파싱된 약물 리스트
    """
    headers = {"X-OCR-SECRET": settings.CLOVA_OCR_SECRET, "Content-Type": "application/json"}

    # 쿼리 파라미터로 요청할 경우 timestamp가 밀리초로 필요
    timestamp = int(round(time.time() * 1000))

    payload = {
        "version": "V2",
        "requestId": str(uuid.uuid4()),
        "timestamp": timestamp,
        "images": [{"format": "jpg", "name": "prescription", "url": image_url}],
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(settings.CLOVA_OCR_URL, headers=headers, json=payload, timeout=30.0)

    if response.status_code != 200:
        raise Exception(f"OCR API 연동 실패: {response.status_code} - {response.text}")

    data = response.json()

    # ─────────────────────────────────────────────────────────────
    # [파싱 로직] 원본 데이터에서 inferText를 돌면서 약물 정보화
    # ─────────────────────────────────────────────────────────────
    parsed_medications: list[OcrMedicationItem] = []

    if "images" in data and data["images"] and "fields" in data["images"][0]:
        fields = data["images"][0].get("fields", [])
        extracted_texts = [f.get("inferText", "") for f in fields]

        # **향후 고도화 필요 항목**: 클로바 문자열 목록(extracted_texts)을 바탕으로
        # OpenAI 구조화(Structured JSON) 요청을 한 번 더 거치거나 정밀한 정규식을 사용해
        # 실제 약품명, 용량, 빈도를 추출해야 합니다.
        # 현재는 팀 협업의 뼈대 동작성을 위해 간단한 더미-매핑 로직 제공.

        # Example Fallback Mock Data:
        if len(extracted_texts) > 0:
            parsed_medications = [
                OcrMedicationItem(name="타이레놀500mg(예시)", dosage="1정", frequency="1일 3회", timing="식후 30분"),
                OcrMedicationItem(name="소화제(예시)", dosage="1정", frequency="1일 3회", timing="식후 30분"),
            ]

    return data, parsed_medications
