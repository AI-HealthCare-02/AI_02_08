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
- **폰트**: 이서윤체 (LeeSeoyun) + Pretendard
- **커스텀 커서**: 약속이 캐릭터 (yakssori_cursor_32.png)
- **카드 UI**: border-radius 16px~32px, hover 시 떠오르는 효과
- **스크롤 애니메이션**: IntersectionObserver 기반 섹션별 페이드인 등장 효과
- **모바일 최적화**: 반응형 레이아웃, 챗봇 플로팅 버튼, 가로 스크롤 차단

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

### 디자인 토큰 시스템

CSS 변수 기반으로 체계적인 디자인 시스템을 구축하여 일관된 디자인 유지 및 유지보수 용이성을 확보했습니다.

- `colors.css` — 색상 변수 (Primary, Neutral, Warning, Accent, Semantic)
- `typography.css` — 폰트 크기/굵기/행간/자간 변수
- `spacing.css` — 간격 변수
- `components.css` — 공통 컴포넌트 스타일 (Button, Input, Modal, Loading)

## 프로젝트 구조

```
frontend/
├── public/                  # 정적 파일
│   ├── favicon.png          # 파비콘
│   ├── logo.png             # 로고 이미지
│   ├── user-icon.svg        # 기본 프로필 아이콘
│   ├── pill.png             # OCR 프로그레스 알약 이미지
│   ├── pill-bottle.png      # OCR 프로그레스 알약통 이미지
│   ├── arrow.png            # 맨 위로 스크롤 아이콘
│   ├── home-icon.png        # 홈 아이콘
│   ├── mypage-icon.png      # 마이페이지 아이콘
│   ├── yakssori_cursor_32.png  # 커스텀 커서 (32px)
│   └── yakssori_cursor_64.png  # 커스텀 커서 원본 (64px)
├── src/
│   ├── api/                 # 백엔드 API 호출 함수
│   │   ├── apiClient.ts     # axios 인스턴스 + 토큰 인터셉터
│   │   ├── authApi.ts       # 인증 API (로그인, 회원가입, 토큰 갱신, 프로필 수정)
│   │   ├── chatApi.ts       # AI 챗봇 API (세션 생성, 메시지 전송)
│   │   ├── medicationApi.ts # 복약 관리 API (등록, 조회)
│   │   └── ocrApi.ts        # OCR API (처방전 이미지 분석)
│   ├── assets/
│   │   ├── images/          # 이미지 리소스
│   │   │   ├── bg-landing.png  # 랜딩/소개 페이지 배경
│   │   │   ├── landing1.png    # 랜딩 페이지 서비스 이미지
│   │   │   ├── landing2.png    # 랜딩 페이지 서비스 이미지
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
│   │   ├── about/           # 소개 페이지
│   │   │   ├── AboutPage.tsx   # 서비스 소개 (스크롤 애니메이션)
│   │   │   └── AboutPage.css
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
│   │   │   ├── LandingPage.tsx # 랜딩 (패럴랙스 스크롤 애니메이션)
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

### 🏠 랜딩 페이지
- **패럴랙스 스크롤**: 배경 이미지 확대, 원형 텍스트 회전, 콘텐츠 페이드아웃
- **스크롤 애니메이션**: IntersectionObserver 기반 섹션별 등장 효과
- **서비스 소개**: 이름 의미 + 주요 기능 3가지 + 약속이 마스코트 소개
- **플로팅 메뉴**: 토글 버튼으로 네비게이션

### 🏥 홈 페이지
- **처방전 OCR 인식**: 카메라 촬영 또는 이미지 업로드 → 약 정보 자동 추출
- **OCR 분석 애니메이션**: 알약 → 알약통 프로그레스 바 + 완료 효과음 + 반짝이 효과
- **AI 챗봇 (약속이 상담소)**: 복약 관련 질문에 AI가 답변, 접기/펼치기 응답 파싱
- **FAQ 말풍선**: 자주 묻는 질문 빠른 선택
- **복약 등록 완료 모달**: 등록 후 마이페이지 히스토리로 이동

### 💊 복약 관리
- OCR 인식 결과를 복약 목록에 자동 추가
- 약물별 활성/비활성 토글
- 필터링 (전체/복용 중/중단됨)
- 통계 카드 (복용 중/오늘 복용/중단된 약물 수)

### 👤 마이페이지
- 프로필 정보 조회/수정 (이름, 연락처, 생년월일, 성별, 프로필 사진)
- 복약 히스토리 (서버 동기화)
- 생활습관 가이드 (운동/식단/수면/스트레스 관리)
- 비밀번호 변경 / 회원탈퇴

### 📖 소개 페이지
- 서비스 소개 + 이름 의미 + 주요 기능 + 약속이 소개
- 스크롤 애니메이션 (페이드인 등장 + 기능 카드 순차 등장)

### 🔐 인증
- 이메일 회원가입 (이메일 인증 코드 + 타이머)
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
