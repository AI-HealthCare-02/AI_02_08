from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from app.apis.v1 import v1_routers
from app.db.databases import initialize_tortoise
from app.middlewares.rate_limit import rate_limit_middleware

tags_metadata = [
    {
        "name": "auth",
        "description": "이메일 기반 가입, 카카오 소셜 연동 로그인, 패스워드 재설정 등 전반적인 사용자 인증 및 인가를 담당합니다.",
    },
    {
        "name": "users",
        "description": "사용자 프로필 관리, 약관 동의 등 내 정보 설정을 처리합니다.",
    },
    {
        "name": "OCR 처방전 분석",
        "description": "처방전 사진을 비동기로 AWS S3에 안전하게 업로드하고, 네이버 클로바와 OpenAI를 파이프라인으로 연결하여 약품명/복용법 등 구조적인 데이터를 추출합니다.",
    },
    {
        "name": "AI 복약 리포트",
        "description": "주기(주간/월간) 단위로 투약 기록과 컨디션을 요약하여, 주기적인 건강 피드백용 GPT 레포트를 Background 작업으로 생성하고 조회합니다.",
    },
    {
        "name": "AI 맞춤형 챗봇",
        "description": "과거 대화 내역(Context)과 실제 복약 이력을 GPT 프롬프트에 주입하여 개인화된 의료 상담을 진행하는 챗봇 세션을 관리합니다.",
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
