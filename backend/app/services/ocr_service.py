import time
import uuid

import aioboto3
import httpx
from fastapi import UploadFile

from app.core.config import settings
from app.dtos.medications import OcrMedicationItem
from app.services.openai_service import parse_ocr_text_to_medications


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

    try:
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
    except Exception as e:
        print(f"AWS S3 업로드 중 에러 발생: {e}")
        raise Exception(f"S3 업로드 실패: {e}")


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

        # OpenAI 구조화(Structured JSON) 요청을 통해 약풍명, 용량, 빈도를 추출
        if len(extracted_texts) > 0:
            parsed_dicts = await parse_ocr_text_to_medications(extracted_texts)
            
            parsed_medications = [
                OcrMedicationItem(
                    name=med.get("name", ""),
                    dosage=med.get("dosage", ""),
                    frequency=med.get("frequency", ""),
                    timing=med.get("timing", "")
                )
                for med in parsed_dicts
            ]

    return data, parsed_medications
