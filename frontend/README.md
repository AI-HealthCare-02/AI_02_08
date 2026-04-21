# Frontend - React + TypeScript + Vite

이 프로젝트는 React, TypeScript, Vite, pnpm을 사용한 프론트엔드 애플리케이션입니다.

## 기술 스택

- **React 18** - UI 라이브러리
- **TypeScript** - 타입 안전성
- **Vite** - 빌드 도구 및 개발 서버
- **pnpm** - 패키지 매니저
- **ESLint** - 코드 품질 관리

## 프로젝트 구조

```
frontend/
├── public/                  # 정적 파일
├── src/
│   ├── api/                 # 백엔드 API 호출 함수
│   │   ├── apiClient.ts     # axios 인스턴스 + 토큰 인터셉터
│   │   ├── authApi.ts       # 인증 관련 API (로그인, 회원가입, 토큰 갱신)
│   │   ├── chatApi.ts       # AI 챗봇 API (메시지 전송, 응답)
│   │   └── ocrApi.ts        # OCR API (처방전 이미지 업로드, 약 정보 파싱)
│   ├── assets/
│   │   ├── images/          # 이미지 리소스 (마스코트, 배경 등)
│   │   └── styles/          # CSS 파일 및 디자인 토큰
│   │       ├── global.css   # 글로벌 스타일 리셋
│   │       ├── colors.css   # 색상 변수
│   │       ├── typography.css # 폰트 변수
│   │       ├── spacing.css  # 스페이싱 변수
│   │       └── components.css # 컴포넌트 스타일
│   ├── components/
│   │   ├── common/          # 재사용 공통 컴포넌트
│   │   │   ├── Button.tsx   # 버튼 컴포넌트
│   │   │   ├── Input.tsx    # 인풋 컴포넌트
│   │   │   ├── Modal.tsx    # 모달 컴포넌트
│   │   │   ├── Loading.tsx  # 로딩 컴포넌트
│   │   │   ├── ProtectedRoute.tsx # 인증 보호 라우트
│   │   │   ├── ToastContainer.tsx # 토스트 알림
│   │   │   └── index.ts     # 컴포넌트 export
│   │   └── layout/          # 레이아웃 컴포넌트
│   │       ├── MainLayout.tsx # 메인 레이아웃
│   │       └── Navbar.tsx   # 네비게이션 바
│   ├── contexts/            # React Context
│   │   └── ToastContext.tsx # 토스트 알림 컨텍스트
│   ├── hooks/               # 커스텀 훅
│   │   └── useAuth.ts       # 인증 상태 관리 훅
│   ├── pages/               # 페이지 단위 컴포넌트
│   │   ├── auth/
│   │   │   ├── LoginPage.tsx          # 로그인
│   │   │   ├── SignupPage.tsx         # 회원가입
│   │   │   ├── ForgotPasswordPage.tsx # 비밀번호 찾기
│   │   │   ├── KakaoCallbackPage.tsx  # 카카오 로그인 콜백
│   │   │   ├── KakaoAdditionalInfoPage.tsx # 카카오 추가정보 입력
│   │   │   ├── TermsAgreementPage.tsx # 약관 동의
│   │   │   ├── TermsContent.tsx       # 이용약관 내용
│   │   │   └── PrivacyContent.tsx     # 개인정보처리방침 내용
│   │   ├── home/
│   │   │   ├── HomePage.tsx   # 메인 홈 (OCR + 챗봇)
│   │   │   └── LandingPage.tsx # 랜딩 페이지
│   │   ├── medication/
│   │   │   └── MedicationPage.tsx # 복약 관리
│   │   └── mypage/
│   │       └── MyPage.tsx     # 마이페이지
│   ├── routes/              # 라우팅 설정
│   │   └── AppRouter.tsx
│   ├── types/               # TypeScript 타입 정의
│   │   ├── auth.ts          # 인증 관련 타입
│   │   └── index.ts
│   ├── App.tsx              # 루트 컴포넌트
│   ├── main.tsx             # 앱 진입점
│   └── vite-env.d.ts        # Vite 환경 타입
├── .gitignore               # Git 무시 파일
├── eslint.config.js         # ESLint 설정
├── index.html               # HTML 템플릿
├── package.json             # 패키지 정보
├── pnpm-lock.yaml           # pnpm 락 파일
├── tsconfig.json            # TypeScript 설정
├── tsconfig.node.json       # Node.js용 TypeScript 설정
└── vite.config.ts           # Vite 설정
```

## 시작하기

### 필수 요구사항

- Node.js 18+
- pnpm

### 설치 및 실행

```bash
# 의존성 설치
pnpm install

# 개발 서버 실행
pnpm dev

# 빌드
pnpm build

# 빌드 결과 미리보기
pnpm preview
```

## 개발 가이드

### 컴포넌트 작성

#### 공통 컴포넌트
`src/components/common/`에는 재사용 가능한 컴포넌트들이 있습니다:

- **Button.tsx** - 다양한 변형과 크기를 지원하는 버튼
- **Input.tsx** - 레이블, 에러 메시지를 지원하는 인풋
- **Modal.tsx** - 다양한 크기를 지원하는 모달
- **Loading.tsx** - 로딩 스피너 컴포넌트
- **ProtectedRoute.tsx** - 인증된 사용자만 접근 가능한 보호 라우트
- **ToastContainer.tsx** - 토스트 알림 컴포넌트

사용 예시:
```tsx
import { Button, Input, Modal } from './components/common';

// 버튼 사용
<Button variant="primary" size="md" onClick={handleClick}>
  클릭
</Button>

// 인풋 사용
<Input 
  label="이메일" 
  type="email" 
  placeholder="이메일을 입력하세요"
  error={emailError}
/>
```

#### 레이아웃 컴포넌트
- **MainLayout.tsx** - 공통 레이아웃 (Navbar 포함)
- **Navbar.tsx** - 네비게이션 바 (로그인 상태에 따른 UI 분기)

#### 페이지 컴포넌트
- `pages/auth/` - 인증 관련 (로그인, 회원가입, 카카오 로그인, 비밀번호 찾기, 약관)
- `pages/home/` - 메인 홈 (OCR 처방전 업로드 + AI 챗봇), 랜딩 페이지
- `pages/medication/` - 복약 관리
- `pages/mypage/` - 마이페이지

### 디자인 시스템

`src/assets/styles/`에는 디자인 토큰들이 정의되어 있습니다:

#### 색상 시스템 (colors.css)
- Primary, Gray, Semantic 색상
- Background, Text, Border 색상
- CSS 변수로 정의: `var(--color-primary-600)`

#### 타이포그래피 (typography.css)
- 폰트 패밀리, 크기, 가중치
- 줄 간격, 자간 설정
- 사용 예시: `var(--font-size-lg)`, `var(--font-weight-semibold)`

#### 스페이싱 (spacing.css)
- 마진, 패딩 값들
- 보더 라디우스, 그림자
- Z-index 값들
- 사용 예시: `var(--spacing-4)`, `var(--radius-md)`

### API 호출

- `apiClient.ts` - axios 인스턴스 및 인터셉터 설정 (토큰 자동 갱신)
- `authApi.ts` - 인증 API (로그인, 회원가입, 토큰 갱신, 카카오 로그인)
- `chatApi.ts` - AI 챗봇 API (메시지 전송, AI 응답)
- `ocrApi.ts` - OCR API (처방전 이미지 업로드, 약 정보 파싱, 에러 핸들링)

### 커스텀 훅

- `useAuth.ts` - 로그인 상태 확인 훅

### 타입 정의

- `src/types/auth.ts` - 인증 관련 타입
- `src/types/index.ts` - 공통 타입

## 스크립트

- `pnpm dev` - 개발 서버 실행
- `pnpm build` - 프로덕션 빌드
- `pnpm preview` - 빌드 결과 미리보기
- `pnpm lint` - ESLint 실행
- `pnpm lint:fix` - ESLint 자동 수정

## 추가 예정 기능

- `src/stores/` - 전역 상태 관리
- `src/utils/` - 유틸리티 함수

## 아이콘 및 이미지 가이드

### 브라우저 탭 아이콘 (Favicon)
- **위치**: `public/favicon.ico` 또는 `public/favicon.svg`
- **설명**: 브라우저 탭에 표시되는 아이콘
- **권장 크기**: 16x16, 32x32, 48x48px

### 앱 아이콘 (PWA/모바일)
- **위치**: `public/` 폴더
- **파일명**: 
  - `icon-192x192.png` - Android 홈스크린
  - `icon-512x512.png` - Android 스플래시
  - `apple-touch-icon.png` - iOS 홈스크린

### 앱 내부 이미지
- **위치**: `src/assets/images/`
- **용도**: 로고, 배경 이미지, UI 요소 등
- **사용법**: 
```tsx
import logo from '../assets/images/logo.png';

<img src={logo} alt="로고" />
```
