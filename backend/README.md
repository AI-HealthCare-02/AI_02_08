# Backend - Python + FastAPI + Tortoise ORM

이 프로젝트는 Python, FastAPI, Tortoise ORM, uv를 사용한 AI 헬스케어 기반의 백엔드 애플리케이션입니다.

## 기술 스택

- **FastAPI (Python 3.13+)** - 비동기 웹 프레임워크
- **Database** - MySQL, Tortoise ORM
- **Migration** - Aerich
- **AI & Task** - OpenAI API, Redis
- **Cloud** - AWS S3 (aioboto3)
- **Auth** - JWT, Bcrypt, Kakao OAuth
- **Package Manager** - uv
- **Infra** - Docker, Docker Compose

## 프로젝트 구조

```text
backend/
├── app/                     # 메인 애플리케이션 코드
│   ├── apis/                # 도메인별 API 라우터 핸들러
│   │   └── v1/              # API 버전 관리 (auth, chat, ocr, report, user)
│   ├── core/                # 환경 변수, 설정 및 글로벌 예외 처리
│   ├── db/                  # 데이터베이스 연결 및 설정
│   ├── dtos/                # 요청/응답 Pydantic 스키마
│   ├── models/              # DB 모델 테이블 정의 (Tortoise ORM)
│   ├── repositories/        # 데이터베이스 접근 및 쿼리 계층
│   ├── services/            # 핵심 비즈니스 로직 연동 (AI, 메일, 인증 등)
│   ├── utils/               # 공통 유틸리티 함수
│   ├── validators/          # 추가 커스텀 유효성 검증
│   └── main.py              # 앱 진입점 (Lifespan, Middleware, Router)
├── db/
│   └── migrations/          # Aerich를 통한 DB 마이그레이션 히스토리
├── docs/                    # S3 등 인프라 아키텍처 및 설정 가이드
├── scripts/                 # 스크립트 모음 (데이터 시딩 등)
├── tests/                   # 단위 및 통합 테스트 코드 (Pytest)
├── .env.example             # 환경 변수 참조 템플릿
├── pyproject.toml           # 의존성 및 프로젝트 환경 관리
└── uv.lock                  # 패키지 의존성 잠금 파일
```

## 주요 기능 및 설명

### 인증 및 보안 (Auth System)
- 카카오 소셜 로그인 연동을 통한 빠른 가입
- JWT (`Access Token`, `Refresh Token`) 기반 세션 관리 및 엔드포인트 접근 권한 제어
- `FastAPI-Mail` 로직을 활용한 이메일 인증 코드로 강력한 2FA 가입 절차 도입

### 복약 관리 챗봇 (AI Chatbot)
- OpenAI API와의 통신을 통해 부작용 우려, 복약 방법 등 의료 질의 응답 챗봇 수행
- 사용자 과거 대화 내역 및 DB에 저장된 실제 투약 데이터를 프롬프트로 제공하여 개인화 응답 제공

### 처방전 OCR 분석 (OCR & AI Structuring)
- **AWS S3** 인프라를 활용하여 분석할 처방전 및 약 봉투 이미지를 비동기 업로드로 안전하게 관리
- 추출된 문자 텍스트를 파싱하여, 약품명, 1일 투약량, 제조사 정보 등을 정형화된 JSON 트리로 변환 및 DB 적재

### 사용자 맞춤형 레포트 (Personalized Report)
- 실 투약 기록, 복약 순응도를 취합하여 사용자의 의료 상태 패턴 분석 로직 마련
- 사용자의 주간/월간 등 주기적인 건강 및 약물 분석 정보를 OpenAI를 활용한 최신 리포트로 자동 생성

## 스크립트 안내

- `uv sync` - 패키지 및 가상 환경 생성/동기화
- `uv run uvicorn app.main:app --reload` - 로컬 개발 서버 실행
- `uv run pytest` - 전체 모듈 테스트 코드 실행
- `uv run ruff check . --fix` - 코드 스타일 린트 검사 및 자동 수정
- `uv run ruff format .` - 코드 포맷터 실행

## API 문서

해당 서버가 환경 안에서 실행 중일 때, 다음 경로에 접속하면 대화형 API 검증 및 문서를 확인할 수 있습니다:

- **Swagger UI**: `/api/docs`
- **ReDoc**: `/api/redoc`
