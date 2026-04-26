"""
OCR 관련 API 라우터
- POST /api/v1/ai/ocr/prescription          : 처방전 이미지 OCR 분석
- POST /api/v1/ai/ocr/prescription/{ocrId}/confirm : OCR 결과 확정 → 복약 일정 등록
- GET  /api/v1/ai/ocr/prescription/{ocrId}/analysis : 약물 상호작용 분석
"""

import traceback
import uuid
from datetime import datetime
from io import BytesIO
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.dependencies.security import get_request_user
from app.dtos.medications import (
    OcrAnalyzeResponse,
    OcrConfirmRequest,
    OcrConfirmResponse,
    PrescriptionAnalysisResponse,
)
from app.models.medications import MedicationLog, OcrPrescription, OcrStatus
from app.models.users import User
from app.services.ocr_service import analyze_prescription_via_clova, upload_image_to_s3
from app.validators.file_validator import FileSecurityValidator

ocr_router = APIRouter(prefix="/ai/ocr", tags=["OCR 처방전 분석"])


# ──────────────────────────────────────────────
# 1. 처방전 OCR 분석 API
# ──────────────────────────────────────────────
@ocr_router.post(
    "/prescription",
    response_model=OcrAnalyzeResponse,
    status_code=status.HTTP_200_OK,
    summary="처방전 OCR 분석",
    description="처방전 또는 약봉지 사진 업로드 시 네이버 클로바 OCR로 약 이름·용량·복용법 자동 추출",
    responses={
        400: {"description": "지원하지 않는 파일 형식 또는 10MB 초과"},
        401: {"description": "인증 실패 (토큰 누락 또는 만료)"},
        500: {"description": "OCR 서비스 연동 오류"},
    },
)
async def analyze_prescription(
    image: UploadFile = File(..., description="JPG·PNG·PDF, 최대 10MB"),  # noqa: B008
    user: Annotated[User, Depends(get_request_user)] = None,
):
    # ---  파일 유효성 검사 (MIME 타입) ---
    allowed_types = ["image/jpeg", "image/png", "application/pdf", "image/jpg"]
    if image.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="지원하지 않는 파일 형식입니다. JPG, PNG, PDF 파일만 업로드 가능합니다.",
        )

    # ---  보안 검증 (Magic Number, 파일 크기 10MB, EXIF 제거, 재인코딩) ---
    try:
        validated_bytes = await FileSecurityValidator.validate_file(image)
    except HTTPException:
        raise  # 검증 실패 시 그대로 전파
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"파일 검증 실패: {str(e)}") from e

    # ---  검증된 파일로 UploadFile 재구성 ---
    # 원본 UploadFile의 파일 포인터를 검증된 바이트로 교체
    image.file = BytesIO(validated_bytes)
    await image.seek(0)

    # ---  S3에 이미지 업로드 및 URL 확보 ---
    try:
        s3_url = await upload_image_to_s3(image)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"이미지 스토리지 업로드 실패: {str(e)}") from e

    ocr_id = f"ocr_{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:6]}"

    # ---  Clova OCR API 호출 및 파싱 진행 ---
    try:
        raw_json, parsed_medications = await analyze_prescription_via_clova(s3_url)
    except Exception as e:
        traceback.print_exc()
        error_msg = str(e)
        if "OCR API 연동 실패" in error_msg:
            raise HTTPException(
                status_code=502, detail=f"네이버 클로바 OCR 서버 연동 중 오류가 발생했습니다: {error_msg}"
            ) from e
        elif "GPT" in error_msg or "rate limit" in error_msg.lower():
            raise HTTPException(status_code=502, detail="AI 분석 서버 지연으로 약품을 파싱하지 못했습니다.") from e
        else:
            raise HTTPException(status_code=500, detail=f"처방전 분석 실패: {error_msg}") from e

    # ---  추출 결과 DB 저장 ---
    try:
        await OcrPrescription.create(
            ocr_id=ocr_id,
            user_id=user.id,
            image_url=s3_url,
            status=OcrStatus.PENDING,
            extracted_data={
                "raw": raw_json,
                "parsed": [m.model_dump() for m in parsed_medications] if parsed_medications else [],
            },
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"DB 저장 실패: {str(e)}") from e

    # 부분 실패 처리
    status_msg = "success"
    if not parsed_medications:
        status_msg = "partial_failure"

    return OcrAnalyzeResponse(
        ocrId=ocr_id,
        status=status_msg,
        medications=parsed_medications,
    )


# ──────────────────────────────────────────────
# 2. OCR 결과 확정 API
# ──────────────────────────────────────────────
@ocr_router.post(
    "/prescription/{ocr_id}/confirm",
    response_model=OcrConfirmResponse,
    status_code=status.HTTP_201_CREATED,
    summary="OCR 결과 확정",
    description="OCR 추출 결과를 사용자가 검토·수정 후 확정. 복약 일정으로 자동 등록",
    responses={
        401: {"description": "인증 실패 (토큰 누락 또는 만료)"},
        404: {"description": "해당 OCR 기록을 찾을 수 없음"},
        422: {"description": "요청 바디 유효성 검증 실패"},
    },
)
async def confirm_prescription(
    ocr_id: str,
    body: OcrConfirmRequest,
    user: Annotated[User, Depends(get_request_user)] = None,
):
    ocr_record = await OcrPrescription.get_or_none(ocr_id=ocr_id)
    if not ocr_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="해당 OCR 기록을 찾을 수 없습니다.")

    ocr_record.status = OcrStatus.CONFIRMED
    await ocr_record.save()

    created_ids: list[int] = []
    for med in body.medications:
        medication = await MedicationLog.create(
            user_id=user.id,
            ocr_prescription_id=ocr_id,
            name=med.name,
            dosage=med.dosage,
            frequency=med.frequency,
            timing=med.timing,
        )
        created_ids.append(medication.id)

    return OcrConfirmResponse(
        registeredCount=len(created_ids),
        medicationIds=created_ids,
    )


# ──────────────────────────────────────────────
# 3. 처방전 성분 분석 API
# ──────────────────────────────────────────────
@ocr_router.get(
    "/prescription/{ocr_id}/analysis",
    response_model=PrescriptionAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="처방전 성분 분석",
    description="OCR로 추출된 약의 주의 성분 및 약물 간 상호작용 분석 결과 조회",
    responses={
        401: {"description": "인증 실패 (토큰 누락 또는 만료)"},
        404: {"description": "해당 OCR 기록을 찾을 수 없음"},
    },
)
async def analyze_interactions(
    ocr_id: str,
    user: Annotated[User, Depends(get_request_user)] = None,
):
    ocr_record = await OcrPrescription.get_or_none(ocr_id=ocr_id)
    if not ocr_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="해당 OCR 기록을 찾을 수 없습니다.")

    return PrescriptionAnalysisResponse(
        interactions=[],
        cautionIngredients=[],
        allergyWarnings=[],
    )
