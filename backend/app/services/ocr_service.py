import json
import time
import uuid

import aioboto3
import httpx
from fastapi import UploadFile
from openai import AsyncOpenAI

from app.core.config import Config
from app.dtos.medications import OcrMedicationItem
from app.models.drugs import DrugInfo
from app.services.openai_service import batch_analyze_unmatched_drugs
from app.validators.file_validator import FileSecurityValidator

settings = Config()
openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


async def upload_image_to_s3(file: UploadFile) -> str:
    """
    S3에 이미지 업로드 및 Presigned URL 반환

    보안 강화:
    1. 파일명 검증 (Path Traversal 방지)
    2. UUID 기반 고유 파일명 생성 (예측 불가)

    Args:
        file: FastAPI UploadFile 객체

    Returns:
        str: S3 Presigned URL (1시간 유효)
    """
    file_bytes = await file.read()

    # 안전한 파일명 생성
    safe_filename = FileSecurityValidator.sanitize_filename(file.filename)
    file_extension = safe_filename.split(".")[-1] if "." in safe_filename else "jpg"

    # UUID 기반 고유 파일명 (예측 불가)
    unique_filename = f"prescriptions/{uuid.uuid4().hex}.{file_extension}"

    session = aioboto3.Session(
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
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


async def extract_medication_structure(extracted_texts: list[str]) -> list[dict]:
    text_joined = "\n".join(extracted_texts)

    prompt = f"""
다음은 한국 처방전에서 OCR로 추출한 텍스트 덩어리입니다.
이 텍스트에서 '약품 목록' 부분만 판별하여 각 약물 정보를 추출하고 JSON 배열로 반환해주세요.

[추출 규칙 및 고도화 가이드]
1. 약물명(name): 정제, 캡슐, 액, 연고 등이 포함된 실제 '처방 약품명'을 추출하세요. OCR 오타가 의심되더라도 최대한 처방전에 적힌 고유명사를 보존하세요. (예: 타이레놀8시간이알서방정)
2. 복용량(dosage): 1회 투약량 또는 복용량 (예: "1정", "1포", "5ml", "0.5정")
3. 복용 횟수(frequency): 1일 투약 횟수 (예: "1일 3회", "1일 2회", "필요시")
4. 복용 시점(timing): 복용하는 시간대나 조건 (예: "식후 30분", "식전", "취침 전", "아침/저녁")
5. 처방전에 기재된 여러 약품이 누락되지 않도록 모두 찾아내어 배열(Array)에 담아주세요.
6. 주의: 제조사명, 환자명, 병원명, 보험코드 등 약품 복용과 관계없는 텍스트는 완전히 제외하세요.

반드시 아래 JSON 형식으로만 응답해야 하며, 마크다운 코드블록(```json 등)이나 부가 설명 없이 순수 JSON만 반환하세요:
[
  {{
    "name": "string (약물명)",
    "dosage": "string (1회 복용량)",
    "frequency": "string (1일 복용 횟수)",
    "timing": "string (복용 시점)"
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

    clean_content = content.strip()
    if clean_content.startswith("```"):
        clean_content = clean_content.split("```")[1]
        if clean_content.startswith("json"):
            clean_content = clean_content[4:]
    clean_content = clean_content.strip()

    medications_data = json.loads(clean_content)
    return [med for med in medications_data if med.get("name")]


async def _match_or_fallback_medications(raw_meds: list[dict]) -> list[dict]:
    matched_meds = []
    unmatched_meds = []

    for med in raw_meds:
        name = med.get("name", "").strip()
        if not name:
            continue

        drug = await DrugInfo.get_or_none(name=name)
        if not drug:
            drug = await DrugInfo.filter(name__icontains=name).first()

        if drug:
            med["description"] = drug.efficacy or "약품 설명이 존재하지 않습니다."
            matched_meds.append(med)
        else:
            unmatched_meds.append(med)

    if unmatched_meds:
        try:
            fallback_desc_map = await batch_analyze_unmatched_drugs(unmatched_meds)
            for med in unmatched_meds:
                med_name = med.get("name")
                med["description"] = fallback_desc_map.get(med_name, "일치하는 약품 정보를 찾을 수 없습니다.")
        except Exception as e:
            print(f"Fallback 처리 중 오류: {e}")
            for med in unmatched_meds:
                med["description"] = "약품 정보 매칭 중 서비스 지연이 발생했습니다."

    return matched_meds + unmatched_meds


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
            # 1. 1차 추출 (약품명 등 구조 추출)
            raw_meds = await extract_medication_structure(extracted_texts)

            if not raw_meds:
                return data, []

            final_meds_data = await _match_or_fallback_medications(raw_meds)

            parsed_medications = [
                OcrMedicationItem(
                    name=m.get("name", ""),
                    dosage=m.get("dosage", ""),
                    frequency=m.get("frequency", ""),
                    timing=m.get("timing", ""),
                    description=m.get("description", ""),
                )
                for m in final_meds_data
            ]

    return data, parsed_medications
