# 🏥 이루도담 (Irudodam)

> **처방전 촬영 한 번으로 약물 정보를 자동 분석하고, AI 챗봇 상담부터 복약 기록 관리까지 제공하는 개인 맞춤형 스마트 복약 관리 서비스**

복잡한 약 정보로 어려움을 겪는 사용자에게 쉽고 안전한 복약 경험을 제공합니다.

📖 [Frontend 상세 정보](./frontend/README.md) | [Backend 상세 정보](./backend/README.md)

<br>

## 📌 주요 기능

### 1. 📸 처방전 OCR 인식
- 카메라 촬영 또는 이미지 업로드로 처방전/약봉투 자동 인식
- Naver Clova OCR + GPT-4o mini로 약품명, 용량, 복용 방법 정형화
- 인식 결과 확인 후 복약 관리에 즉시 추가

### 2. 💬 AI 챗봇 '약속이 상담소'
- 복약 관련 질문에 실시간 AI 답변
- FAQ 스마트칩: 부작용, 주의사항, 상호작용 빠른 확인
- 약물 DB (e약은요 공공데이터 4,695건) 우선 조회 → GPT fallback
- 멱등성 보장 (`X-Idempotency-Key`) 및 동시성 제어

### 3. 📅 복약 히스토리 캘린더
- 날짜별 복용 약물 목록 확인
- 마이페이지에서 과거 복약 기록 조회

### 4. 🌿 생활습관 가이드
- 운동, 식단, 수면, 스트레스 관리 4개 카테고리
- 의학 근거 기반 정적 콘텐츠 (대한의학회, WHO, 보건복지부 등)
- 카테고리 버튼 토글로 간편하게 확인

### 5. 👤 마이페이지
- 프로필 정보 관리 (이름, 연락처, 생년월일, 성별, 프로필 사진)
- 복약 히스토리
- 생활습관 가이드
- 비밀번호 변경 / 회원탈퇴

### 6. 🔐 인증 시스템
- 이메일 회원가입 (이메일 인증 코드)
- 카카오 소셜 로그인
- JWT 토큰 자동 갱신
- 비밀번호 찾기/재설정

<br>

## 🛠 기술 스택

### Frontend
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react)
![TypeScript](https://img.shields.io/badge/TypeScript-5.6-3178C6?logo=typescript)
![Vite](https://img.shields.io/badge/Vite-6.0-646CFF?logo=vite)

- **React 19** - UI 라이브러리
- **TypeScript** - 타입 안전성
- **Vite** - 빌드 도구
- **React Router v7** - 클라이언트 라우팅
- **Axios** - HTTP 클라이언트

### Backend
![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)
![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?logo=mysql)

- **FastAPI** - 비동기 웹 프레임워크
- **Tortoise ORM** - 비동기 ORM
- **MySQL** - 데이터베이스
- **Redis** - 캐시 및 세션
- **OpenAI API** - GPT-4o mini
- **Naver Clova OCR** - 이미지 텍스트 인식
- **AWS S3** - 이미지 저장

### Infra
![Docker](https://img.shields.io/badge/Docker-27.4-2496ED?logo=docker)
![AWS](https://img.shields.io/badge/AWS-EC2/S3-FF9900?logo=amazon-aws)

- **Docker & Docker Compose** - 컨테이너화
- **AWS EC2** - 배포 서버
- **Nginx** - 리버스 프록시

<br>

## 📂 프로젝트 구조
```text
irudodam/
├── frontend/          # React + TypeScript
│   ├── src/
│   │   ├── api/       # 백엔드 API 호출
│   │   ├── pages/     # 페이지 컴포넌트
│   │   ├── components/# 재사용 컴포넌트
│   │   └── hooks/     # 커스텀 훅
│   └── README.md
│
├── backend/           # FastAPI + Tortoise ORM
│   ├── app/
│   │   ├── apis/      # API 라우터
│   │   ├── models/    # DB 모델
│   │   ├── services/  # 비즈니스 로직
│   │   └── repositories/ # DB 접근 계층
│   ├── scripts/       # 데이터 시딩
│   └── README.md
│
└── README.md          # 이 파일
```
<br>

## 🚀 시작하기

### 필수 요구사항

- **Node.js** 18+
- **Python** 3.13+
- **pnpm**
- **Docker & Docker Compose**
- **MySQL** 8.0+

---

### 1️⃣ 저장소 클론

```bash
git clone https://github.com/your-org/irudodam.git
cd irudodam
```

---

### 2️⃣ Frontend 설정

```bash
cd frontend

# 의존성 설치
pnpm install

# 환경 변수 설정
cp .env.example .env
# .env 파일 편집 (VITE_API_URL, VITE_KAKAO_CLIENT_ID 등)

# 개발 서버 실행
pnpm dev
```

👉 [Frontend 상세 가이드](./frontend/README.md)

---

### 3️⃣ Backend 설정

```bash
cd backend

# Python 가상환경 및 의존성 설치 (uv 사용)
uv sync

# 환경 변수 설정
cp .env.example .env
# .env 파일 편집 (DATABASE_URL, OPENAI_API_KEY 등)

# Docker Compose로 MySQL, Redis 실행
docker compose up -d mysql redis

# DB 마이그레이션
uv run aerich upgrade

# 개발 서버 실행
uv run uvicorn app.main:app --reload
```

👉 [Backend 상세 가이드](./backend/README.md)

---

### 4️⃣ 접속

- **Frontend**: http://localhost:3000
- **Backend API Docs**: http://localhost:8000/api/docs

<br>

## 🧪 테스트

### Frontend
```bash
cd frontend
pnpm test
```

### Backend
```bash
cd backend
uv run pytest
```

<br>

## 📊 데이터베이스

### e약은요 공공데이터
- **약물 DB**: 4,695건
- **출처**: 식품의약품안전처 의약품개요정보
- **시딩 스크립트**: `backend/scripts/seed_drugs.py`

### FAQ 데이터
- **약물 FAQ**: 부작용, 주의사항, 상호작용 (3건)
- **생활습관 가이드**: 운동, 식단, 수면, 스트레스 (4건)
- **시딩 스크립트**: `backend/scripts/insert_faq_data.py`

<br>

## 🎨 디자인

- **베이스 톤**: 베이지/브라운 계열 (한방/약방 감성)
- **포인트 색상**: 민트/세이지 그린 (#5B8C7A)
- **폰트**: 이서윤체 + Pretendard
- **커스텀 커서**: 약속이 캐릭터

<br>

## 🔑 주요 API 엔드포인트

| 기능 | Method | Endpoint |
|------|--------|----------|
| 회원가입 | POST | `/api/v1/auth/signup` |
| 로그인 | POST | `/api/v1/auth/login` |
| OCR 분석 | POST | `/api/v1/ai/ocr/prescription` |
| OCR 확정 | POST | `/api/v1/ai/ocr/prescription/{ocrId}/confirm` |
| 챗봇 세션 생성 | POST | `/api/v1/chat/sessions` |
| 챗봇 메시지 전송 | POST | `/api/v1/chat/sessions/{sessionId}/messages` |
| 복약 히스토리 조회 | GET | `/api/v1/medications/history?date=YYYY-MM-DD` |

<br>

## 📦 배포

### Production 빌드

**Frontend:**
```bash
cd frontend
pnpm build
```

**Backend:**
```bash
cd backend
docker compose up -d --build nginx fastapi
```

### 배포 서버 스크립트 실행

```bash
# FAQ 데이터 삽입
docker exec -it fastapi bash
uv run python scripts/insert_faq_data.py
exit
```

<br>

## 👥 팀

| 역할 | 이름 | GitHub |
|------|------|--------|
| Frontend | OOO | [@username](https://github.com/username) |
| Backend | OOO | [@username](https://github.com/username) |
| Backend | OOO | [@username](https://github.com/username) |

<br>

## 📝 라이선스

This project is licensed under the MIT License.

<br>

## 🙏 Acknowledgments

- **e약은요**: 식품의약품안전처 의약품개요정보
- **Naver Clova OCR**: 이미지 텍스트 인식
- **OpenAI**: GPT-4o mini API

---

<p align="center">
  Made with ❤️ by 이루도담 Team
</p>