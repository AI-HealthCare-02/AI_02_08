"""
AI 복약 리포트 관련 API 라우터
- POST /api/v1/ai/reports/generate  : 주간/월간 리포트 생성 요청
- GET  /api/v1/ai/reports/{reportId} : 특정 리포트 상세 조회
- GET  /api/v1/ai/reports            : 리포트 목록 조회
"""

from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, status

from app.dtos.medications import (
    MedicationTakenRate,
    ReportDetailResponse,
    ReportGenerateRequest,
    ReportGenerateResponse,
    ReportListItem,
    ReportListResponse,
)
from app.models.medications import AiReport

report_router = APIRouter(prefix="/ai/reports", tags=["AI 복약 리포트"])


# ──────────────────────────────────────────────
# 1. 복약 리포트 생성 API
# ──────────────────────────────────────────────
@report_router.post(
    "/generate",
    response_model=ReportGenerateResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="복약 리포트 생성 요청",
    description="주간/월간 복약 데이터 및 컨디션 기록 기반 GPT-4o mini 분석 리포트 생성",
    responses={
        401: {"description": "인증 실패 (토큰 누락 또는 만료)"},
        422: {"description": "요청 바디 유효성 검증 실패 (period 값 오류 등)"},
        500: {"description": "GPT-4o mini 서비스 연동 오류"},
    },
)
async def generate_report(body: ReportGenerateRequest):
    report_id = f"rpt_{datetime.now().strftime('%Y%m%d')}_{body.period[0]}"

    # TODO: 백그라운드 태스크로 GPT-4o mini 호출
    # 1) MedicationLog에서 해당 기간의 복약 기록 조회
    # 2) adherence_rate 계산
    # 3) OpenAI API 호출 (프롬프트 + 복약 데이터 컨텍스트)
    # 4) 결과를 AiReport 테이블에 저장 (status → COMPLETED)

    # 임시: generating 상태로 레코드 생성
    # await AiReport.create(
    #     report_id=report_id,
    #     user_id=<current_user.id>,
    #     period=body.period,
    #     status=ReportStatus.GENERATING,
    # )

    return ReportGenerateResponse(
        reportId=report_id,
        status="generating",
        estimatedSeconds=10,
    )


# ──────────────────────────────────────────────
# 2. 복약 리포트 상세 조회 API
# ──────────────────────────────────────────────
@report_router.get(
    "/{report_id}",
    response_model=ReportDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="복약 리포트 조회",
    description="생성된 복약 리포트 내용 조회 (복약률, 컨디션 분석, 주의사항 요약 포함)",
    responses={
        401: {"description": "인증 실패 (토큰 누락 또는 만료)"},
        404: {"description": "해당 리포트를 찾을 수 없음"},
    },
)
async def get_report(report_id: str):
    report = await AiReport.get_or_none(report_id=report_id)
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="해당 리포트를 찾을 수 없습니다.")

    medication_summary = []
    if report.medication_summary:
        medication_summary = [
            MedicationTakenRate(name=item["name"], takenRate=item.get("takenRate", 0))
            for item in report.medication_summary
        ]

    return ReportDetailResponse(
        reportId=report.report_id,
        period=report.period,
        adherenceRate=report.adherence_rate,
        conditionSummary=report.condition_summary,
        medicationSummary=medication_summary,
        aiComment=report.ai_comment,
        createdAt=report.created_at.isoformat() if report.created_at else None,
    )


# ──────────────────────────────────────────────
# 3. 복약 리포트 목록 조회 API
# ──────────────────────────────────────────────
@report_router.get(
    "",
    response_model=ReportListResponse,
    status_code=status.HTTP_200_OK,
    summary="복약 리포트 목록 조회",
    description="사용자의 전체 리포트 목록 조회 (주간/월간 구분)",
    responses={
        401: {"description": "인증 실패 (토큰 누락 또는 만료)"},
    },
)
async def list_reports(
    report_type: str | None = Query(None, alias="type", description="weekly | monthly"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    # TODO: current_user = Depends(get_current_user)
):
    # TODO: user_id 필터 추가 (인증 완성 후)
    queryset = AiReport.all()

    if report_type:
        queryset = queryset.filter(period=report_type)

    total_count = await queryset.count()
    reports = await queryset.order_by("-created_at").offset((page - 1) * size).limit(size)

    items = [
        ReportListItem(
            reportId=r.report_id,
            period=r.period,
            adherenceRate=r.adherence_rate,
            createdAt=r.created_at.isoformat() if r.created_at else None,
        )
        for r in reports
    ]

    return ReportListResponse(reports=items, totalCount=total_count)
