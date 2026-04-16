"""
OCR 관련 API 라우터
- POST /api/v1/ai/ocr/prescription          : 처방전 이미지 OCR 분석
- POST /api/v1/ai/ocr/prescription/{ocrId}/confirm : OCR 결과 확정 → 복약 일정 등록
- GET  /api/v1/ai/ocr/prescription/{ocrId}/analysis : 약물 상호작용 분석
"""

import traceback
import uuid
from datetime import datetime
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
        400: {"description": "지원하지 않는 파일 형식 또는 15MB 초과"},
        401: {"description": "인증 실패 (토큰 누락 또는 만료)"},
        500: {"description": "OCR 서비스 연동 오류"},
    },
)
async def analyze_prescription(
    image: UploadFile = File(..., description="JPG·PNG·PDF, 최대 15MB"),  # noqa: B008
    user: Annotated[User, Depends(get_request_user)] = None,
):
    # --- 파일 유효성 검사 (400 에러 분기) ---
    allowed_types = ["image/jpeg", "image/png", "application/pdf", "image/jpg"]
    if image.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="지원하지 않는 파일 형식입니다. JPG, PNG, PDF 파일만 업로드 가능합니다."
        )

    # 사이즈 체크 (15MB 제한)
    # image.size 속성은 FastAPI 최신 버전에 존재하나 없는 경우를 대비해 위치를 0으로 되돌립니다.
    file_bytes = await image.read()
    if len(file_bytes) > 15 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="파일 용량이 15MB를 초과했습니다."
        )
    # 이미 다 읽어버렸으므로 S3 업로드 시 이슈가 없게 포인터를 원복
    await image.seek(0)

    # 1) S3에 이미지 업로드 및 URL 확보
    try:
        s3_url = await upload_image_to_s3(image)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"이미지 스토리지 업로드 실패: {str(e)}") from e

    ocr_id = f"ocr_{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:6]}"

    # 2) Clova OCR API 호출 및 파싱 진행
    try:
        raw_json, parsed_medications = await analyze_prescription_via_clova(s3_url)
    except Exception as e:
        traceback.print_exc()
        error_msg = str(e)
        if "OCR API 연동 실패" in error_msg:
            raise HTTPException(status_code=502, detail=f"네이버 클로바 OCR 서버 연동 중 오류가 발생했습니다: {error_msg}") from e
        elif "GPT" in error_msg or "rate limit" in error_msg.lower():
            raise HTTPException(status_code=502, detail="AI 분석 서버 지연으로 약품을 파싱하지 못했습니다.") from e
        else:
            raise HTTPException(status_code=500, detail=f"처방전 분석 실패: {error_msg}") from e

    # 3) 추출 결과 DB 저장
    try:
        await OcrPrescription.create(
            ocr_id=ocr_id,
            user_id=user.id,
            image_url=s3_url,
            status=OcrStatus.PENDING,
            extracted_data=raw_json,
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
