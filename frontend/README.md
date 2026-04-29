# 이루도담 Frontend

처방전 인식부터 복약 관리까지, AI 기반 건강 가이드 서비스 **이루도담**의 프론트엔드입니다.

## 기술 스택

- **React 19** - UI 라이브러리
- **TypeScript** - 타입 안전성
- **Vite** - 빌드 도구 및 개발 서버
- **pnpm** - 패키지 매니저
- **React Router v7** - 클라이언트 라우팅
- **Axios** - HTTP 클라이언트 (멱등성 키 헤더 지원)
- **ESLint** - 코드 품질 관리

## 디자인 컨셉

- **베이스 톤**: 베이지/브라운 계열 (한방/약방 감성)
- **포인트 색상**: 민트/세이지 그린 (#5B8C7A, #7BA99A) — 절제된 포인트
- **폰트**: 이서윤체 (IsYun) + Pretendard
- **커스텀 커서**: 약속이 캐릭터 (yakssori_cursor_32.png)
- **카드 UI**: border-radius 16px~32px, hover 시 떠오르는 효과
- **다크모드 대응**: `color-scheme: light` + `prefers-color-scheme: dark` 미디어쿼리로 갤럭시 등 Android 다크모드에서도 라이트 테마 색상 유지
- **모바일 최적화**: 챗봇 영역 높이 확대 (650px), 카메라/사진 버튼 컴팩트화, 전송 버튼 간격 조정

### 색상 팔레트

| 용도 | 색상 | 코드 |
|------|------|------|
| 배경 | 베이지 | `#F5F0E8` |
| 카드 배경 | 연한 베이지 | `#EDE5D8` |
| 테두리 | 모래색 | `#C4B49A` |
| 브라운 (Primary 버튼) | 다크 브라운 | `#8B7355` |
| 민트 포인트 (타이틀, 활성 탭) | 세이지 그린 | `#5B8C7A` |
| 민트 서브 (hover, 보조) | 연한 민트 | `#7BA99A` |
| 민트 배경 (뱃지, 상태) | 매우 연한 민트 | `#EAF2EF` |
| 골드 (면책 문구) | 골드 | `#996515` |

## 프로젝트 구조

```
frontend/
├── public/                  # 정적 파일
│   ├── favicon.png          # 파비콘
│   ├── logo.png             # 로고 이미지
│   ├── user-icon.svg        # 기본 프로필 아이콘
│   ├── yakssori_cursor_32.png  # 커스텀 커서 (32px)
│   └── yakssori_cursor_64.png  # 커스텀 커서 원본 (64px)
├── src/
│   ├── api/                 # 백엔드 API 호출 함수
│   │   ├── apiClient.ts     # axios 인스턴스 + 토큰 인터셉터
│   │   ├── authApi.ts       # 인증 API (로그인, 회원가입, 토큰 갱신, 프로필 수정)
│   │   ├── chatApi.ts       # AI 챗봇 API (세션 생성, 메시지 전송)
│   │   └── ocrApi.ts        # OCR API (처방전 이미지 분석)
│   ├── assets/
│   │   ├── images/          # 이미지 리소스
│   │   │   ├── bg-landing.png  # 랜딩 페이지 배경
│   │   │   └── yakssori.png    # 약속이 마스코트
│   │   └── styles/          # 디자인 토큰 CSS
│   │       ├── global.css   # 글로벌 스타일 (커스텀 커서 포함)
│   │       ├── colors.css   # 색상 변수
│   │       ├── typography.css # 폰트 변수 (이서윤체)
│   │       ├── spacing.css  # 스페이싱 변수
│   │       └── components.css # 컴포넌트 스타일
│   ├── components/
│   │   ├── common/          # 재사용 공통 컴포넌트
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Modal.tsx
│   │   │   ├── Loading.tsx
│   │   │   ├── ProtectedRoute.tsx
│   │   │   └── ToastContainer.tsx
│   │   └── layout/
│   │       ├── MainLayout.tsx  # 메인 레이아웃
│   │       ├── Navbar.tsx      # 네비게이션 바
│   │       └── Navbar.css
│   ├── contexts/
│   │   └── ToastContext.tsx
│   ├── hooks/
│   │   └── useAuth.ts       # 인증 상태 관리 (프로필 이미지 포함)
│   ├── pages/
│   │   ├── auth/            # 인증 페이지
│   │   │   ├── LoginPage.tsx
│   │   │   ├── SignupPage.tsx
│   │   │   ├── ForgotPasswordPage.tsx
│   │   │   ├── KakaoCallbackPage.tsx
│   │   │   ├── KakaoAdditionalInfoPage.tsx
│   │   │   └── TermsAgreementPage.tsx
│   │   ├── home/            # 홈 페이지
│   │   │   ├── HomePage.tsx    # 메인 (OCR + 챗봇)
│   │   │   ├── HomePage.css
│   │   │   ├── LandingPage.tsx # 랜딩 (슬라이드)
│   │   │   └── LandingPage.css
│   │   ├── medication/      # 복약 관리
│   │   │   ├── MedicationPage.tsx
│   │   │   └── MedicationPage.css
│   │   └── mypage/          # 마이페이지
│   │       ├── MyPage.tsx
│   │       └── MyPage.css
│   ├── routes/
│   │   └── AppRouter.tsx
│   ├── types/
│   │   └── auth.ts
│   ├── utils/
│   │   └── ocrStorage.ts    # OCR 결과 로컬 저장
│   ├── App.tsx
│   └── main.tsx
├── .env.example
├── package.json
├── pnpm-lock.yaml
├── tsconfig.json
└── vite.config.ts
```

## 시작하기

### 필수 요구사항

- Node.js 18+
- pnpm

### 설치 및 실행

```bash
# 의존성 설치
pnpm install

# 환경변수 설정
cp .env.example .env
# .env 파일에 VITE_KAKAO_CLIENT_ID 등 설정

# 개발 서버 실행
pnpm dev

# 빌드
pnpm build
```

## 주요 기능

### 🏠 홈 페이지
- **처방전 OCR 인식**: 카메라 촬영 또는 이미지 업로드 → 약 정보 자동 추출
- **AI 챗봇 (약속이 상담소)**: 복약 관련 질문에 AI가 답변, `X-Idempotency-Key` 헤더로 중복 전송 방지

### 💊 복약 관리
- OCR 인식 결과를 복약 목록에 추가
- 약물별 활성/비활성 토글
- 필터링 (전체/활성/비활성)

### 👤 마이페이지
- 프로필 정보 조회/수정 (이름, 연락처, 생년월일, 성별, 프로필 사진)
- 내 리포트 (복용률, 연속 복용일)
- 복약 히스토리
- 비밀번호 변경 / 회원탈퇴

### 🔐 인증
- 이메일 회원가입 (이메일 인증 코드)
- 로그인 / 로그아웃
- 카카오 소셜 로그인
- 비밀번호 찾기/재설정
- JWT 토큰 자동 갱신

## 스크립트

| 명령어 | 설명 |
|--------|------|
| `pnpm dev` | 개발 서버 실행 (localhost:3000) |
| `pnpm build` | 프로덕션 빌드 |
| `pnpm preview` | 빌드 결과 미리보기 |
| `pnpm lint` | ESLint 실행 |
| `pnpm lint:fix` | ESLint 자동 수정 |
