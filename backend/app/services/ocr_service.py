import json
import time
import uuid

import aioboto3
import httpx
from fastapi import UploadFile
from openai import AsyncOpenAI

from app.core.config import Config
from app.dtos.medications import OcrMedicationItem

settings = Config()
openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


async def upload_image_to_s3(file: UploadFile) -> str:
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

        url = await s3.generate_presigned_url(
            "get_object", Params={"Bucket": settings.AWS_S3_BUCKET, "Key": unique_filename}, ExpiresIn=3600
        )

    return url


async def parse_medications_with_gpt(extracted_texts: list[str]) -> list[OcrMedicationItem]:
    text_joined = "\n".join(extracted_texts)

    prompt = f"""
다음은 한국 처방전에서 OCR로 추출한 텍스트입니다.
이 텍스트에서 약물 정보를 추출하여 JSON 배열로 반환해주세요.

추출 규칙:
1. 약물명은 정제, 캡슐, 액, 정 등이 포함된 실제 약품명을 추출하세요.
2. dosage는 1회 복용량 (예: "1정", "1포", "5ml")
3. frequency는 1일 복용 횟수 (예: "1일 3회", "1일 2회")
4. timing은 복용 시점 (예: "식후 30분", "식전", "취침 전")
5. description은 처방전에 나와있는 약품 설명을 바탕으로 한 줄로 요약 (예: "해열진통제로 열을 내리고 통증을 줄여줍니다")
6. 처방전 왼쪽의 약품 목록에 있는 약품명만 추출하세요.
7. 괄호 안에 성분명이 포함된 약품명 형식 (예: 파독심정(세프포독심))으로 된 것만 추출하세요.
8. 제조사명, 병원명, 환자정보 등은 제외하세요.

반드시 아래 JSON 형식으로만 응답하세요. 마크다운 코드블록 없이 순수 JSON만 반환하세요:
[
  {{
    "name": "약물명",
    "dosage": "1회 복용량",
    "frequency": "1일 복용 횟수",
    "timing": "복용 시점",
    "description": "약품 한 줄 설명"
  }}
]

처방전 텍스트:
{text_joined}
"""

    response = await openai_client.chat.completions.create(
        model=settings.openai_chat_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=1500,
    )

    content = response.choices[0].message.content or "[]"

    # 코드블록 제거
    clean_content = content.strip()
    if clean_content.startswith("```"):
        clean_content = clean_content.split("```")[1]
        if clean_content.startswith("json"):
            clean_content = clean_content[4:]
    clean_content = clean_content.strip()

    medications_data = json.loads(clean_content)
    return [
        OcrMedicationItem(
            name=med.get("name", ""),
            dosage=med.get("dosage", ""),
            frequency=med.get("frequency", ""),
            timing=med.get("timing", ""),
            description=med.get("description", ""),
        )
        for med in medications_data
        if med.get("name")
    ]


async def analyze_prescription_via_clova(image_url: str) -> tuple[dict, list[OcrMedicationItem]]:
    headers = {"X-OCR-SECRET": settings.CLOVA_OCR_SECRET, "Content-Type": "application/json"}

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
    parsed_medications: list[OcrMedicationItem] = []

    if "images" in data and data["images"] and "fields" in data["images"][0]:
        fields = data["images"][0].get("fields", [])
        extracted_texts = [f.get("inferText", "") for f in fields]

        if extracted_texts:
            try:
                parsed_medications = await parse_medications_with_gpt(extracted_texts)
            except Exception as e:
                print(f"GPT 파싱 실패: {e}")
                import traceback

                traceback.print_exc()
                parsed_medications = []

    return data, parsed_medications
