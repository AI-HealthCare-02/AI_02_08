from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from app.apis.v1 import v1_routers
from app.db.databases import initialize_tortoise
from app.middlewares.rate_limit import rate_limit_middleware

tags_metadata = [
    {
        "name": "회원 인증 및 계정 관리",
        "description": "이메일 기반 가입·로그인, 카카오 소셜 연동, 이메일 인증, 비밀번호 재설정·변경 등 사용자 인증 전반을 처리합니다.",
    },
    {
        "name": "사용자 정보 관리",
        "description": "현재 로그인한 사용자의 프로필 조회·수정 및 회원 탈퇴(Soft Delete)를 처리합니다.",
    },
    {
        "name": "OCR 처방전 분석",
        "description": "처방전 이미지를 S3에 업로드하고, 네이버 클로바 OCR과 OpenAI를 파이프라인으로 연결하여 약품명·복용법 등 구조적 데이터를 추출합니다. 분석 결과 확정 시 복약 일정으로 자동 등록됩니다.",
    },
    {
        "name": "복약 정보 관리",
        "description": "날짜별 복약 히스토리 조회 및 특정 복약 기록 삭제를 처리합니다. 히스토리 조회 시 반환되는 `id`를 사용하여 삭제 API를 호출합니다.",
    },
    {
        "name": "AI 복약 리포트",
        "description": "주간·월간 단위로 투약 기록과 컨디션을 요약하여, 건강 피드백용 GPT 리포트를 백그라운드 작업으로 생성하고 조회합니다.",
    },
    {
        "name": "AI 맞춤형 챗봇",
        "description": "과거 대화 내역(Context)과 실제 복약 이력을 GPT 프롬프트에 주입하여 개인화된 의료 상담을 제공합니다. 멱등성 키(X-Idempotency-Key)를 통해 중복 요청을 방지합니다.",
    },
]

app = FastAPI(
    title="AI HealthCare Backend API",
    description="AI 헬스케어 기반 맞춤형 처방 분석, 복약 리포트 생성 및 의료 챗봇 서비스 백엔드입니다.",
    version="1.0.0",
    openapi_tags=tags_metadata,
    default_response_class=ORJSONResponse,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate Limiting 미들웨어 (DoS 공격 방지)
app.middleware("http")(rate_limit_middleware)

initialize_tortoise(app)
app.include_router(v1_routers)
