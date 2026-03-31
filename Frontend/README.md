# Frontend

React + TypeScript + Vite 기반 프론트엔드 프로젝트

## 시작하기

```bash
cd Frontend
npm install
npm run dev
```

## 프로젝트 구조

```
Frontend/
├── public/                  # 정적 파일
├── src/
│   ├── api/                 # 백엔드 API 호출 함수
│   │   ├── apiClient.ts     # axios 인스턴스 + 토큰 인터셉터
│   │   └── authApi.ts       # 인증 관련 API (로그인, 회원가입, 토큰 갱신)
│   ├── assets/
│   │   ├── images/          # 이미지 리소스
│   │   └── styles/          # CSS 파일
│   │       └── global.css   # 글로벌 스타일 리셋
│   ├── components/
│   │   ├── common/          # 재사용 공통 컴포넌트 (버튼, 인풋 등)
│   │   └── layout/          # 레이아웃 컴포넌트 (헤더, 푸터, 사이드바)
│   │       └── MainLayout.tsx
│   ├── hooks/               # 커스텀 훅 (useAuth, useFetch 등)
│   ├── pages/               # 페이지 단위 컴포넌트
│   │   ├── auth/
│   │   │   ├── LoginPage.tsx
│   │   │   └── SignupPage.tsx
│   │   └── home/
│   │       └── HomePage.tsx
│   ├── routes/              # 라우팅 설정
│   │   └── AppRouter.tsx
│   ├── stores/              # 전역 상태 관리
│   ├── types/               # TypeScript 타입 정의
│   │   └── index.ts
│   ├── utils/               # 유틸리티 함수
│   ├── App.tsx              # 루트 컴포넌트
│   ├── main.tsx             # 앱 진입점
│   └── vite-env.d.ts
├── .env                     # 환경변수 (VITE_API_BASE_URL)
├── index.html
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## 작업 가이드

### 1. 페이지 추가

`src/pages/` 하위에 폴더/파일 생성 후 `src/routes/AppRouter.tsx`에 Route 등록

### 2. 공통 컴포넌트 추가

`src/components/common/`에 생성하여 여러 페이지에서 재사용

### 3. API 연동

`src/api/`에 도메인별 API 파일 추가 (예: `userApi.ts`), `apiClient.ts`의 axios 인스턴스 사용

### 4. 전역 상태 관리

`src/stores/`에 상태 관리 로직 추가

## 환경변수

| 변수 | 설명 | 기본값 |
|---|---|---|
| `VITE_API_BASE_URL` | 백엔드 API 주소 | `http://localhost:8000/api` |

## 스크립트

| 명령어 | 설명 |
|---|---|
| `npm run dev` | 개발 서버 실행 |
| `npm run build` | 프로덕션 빌드 |
| `npm run preview` | 빌드 결과 미리보기 |
