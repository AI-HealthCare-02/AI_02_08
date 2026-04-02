"""
OCR 관련 API 라우터
- POST /api/v1/ai/ocr/prescription          : 처방전 이미지 OCR 분석
- POST /api/v1/ai/ocr/prescription/{ocrId}/confirm : OCR 결과 확정 → 복약 일정 등록
- GET  /api/v1/ai/ocr/prescription/{ocrId}/analysis : 약물 상호작용 분석
"""

import uuid
from datetime import datetime

from fastapi import APIRouter, HTTPException, UploadFile, File, status

from app.dtos.medications import (
    OcrAnalyzeResponse,
    OcrMedicationItem,
    OcrConfirmRequest,
    OcrConfirmResponse,
    PrescriptionAnalysisResponse,
)
from app.models.medications import OcrPrescription, OcrStatus, Medication

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
    image: UploadFile = File(..., description="JPG·PNG·PDF, 최대 10MB"),
    # TODO: JWT 인증 의존성 주입 (예: current_user = Depends(get_current_user))
):
    """
    실제 Clova OCR 연동 로직은 서비스 레이어(service)에서 구현 예정.
    현재는 DB 레코드 생성 및 응답 스켈레톤만 제공합니다.
    """
    ocr_id = f"ocr_{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:6]}"

    # TODO: 1) S3에 이미지 업로드
    # TODO: 2) Clova OCR API 호출 → 파싱 로직
    # TODO: 3) 파싱 결과를 extracted_data 필드에 저장

    # 임시: DB 레코드 생성 (user_id는 인증 완성 후 교체)
    # await OcrPrescription.create(
    #     ocr_id=ocr_id,
    #     user_id=<current_user.id>,
    #     image_url=<s3_url>,
    #     status=OcrStatus.PENDING,
    #     extracted_data=<parsed_json>,
    # )

    return OcrAnalyzeResponse(
        ocrId=ocr_id,
        status="success",
        medications=[
            # 실제로는 파싱 결과가 채워집니다
        ],
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
async def confirm_prescription(ocr_id: str, body: OcrConfirmRequest):
    # OCR 레코드 존재 확인
    ocr_record = await OcrPrescription.get_or_none(ocr_id=ocr_id)
    if not ocr_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="해당 OCR 기록을 찾을 수 없습니다.")

    # 상태 업데이트
    ocr_record.status = OcrStatus.CONFIRMED
    await ocr_record.save()

    # 약물 스케줄 등록
    created_ids: list[int] = []
    for med in body.medications:
        # TODO: DrugInfo 테이블과 이름매칭하여 drug_id FK 연결
        medication = await Medication.create(
            user_id=ocr_record.user_id,
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
async def analyze_interactions(ocr_id: str):
    ocr_record = await OcrPrescription.get_or_none(ocr_id=ocr_id)
    if not ocr_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="해당 OCR 기록을 찾을 수 없습니다.")

    # TODO: extracted_data에서 약물 목록 추출 → DrugInfo.interactions 컬럼 기반 상호작용 분석 로직 구현
    # TODO: 사용자 알레르기 정보와 교차 검증 로직 구현

    return PrescriptionAnalysisResponse(
        interactions=[],
        cautionIngredients=[],
        allergyWarnings=[],
    )
