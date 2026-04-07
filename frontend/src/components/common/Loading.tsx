// ==============================================
// Loading.tsx — 공통 로딩 컴포넌트
// 이루도담 | Branch: feature/common-components
// ==============================================


// ── 타입 정의 ──────────────────────────────
type LoadingSize = 'sm' | 'md' | 'lg';

interface LoadingProps {
  size?: LoadingSize;       // 스피너 크기
  text?: string;            // 로딩 텍스트
  subText?: string;         // 서브 텍스트
  showProgress?: boolean;   // 진행바 표시 여부
  progress?: number;        // 진행 퍼센트 (0~100)
  fullScreen?: boolean;     // 전체 화면 로딩 여부
}

// ── 사이즈 스타일 맵 ───────────────────────
const sizeStyles: Record<LoadingSize, string> = {
  sm: 'loading-sm',   // 32px
  md: 'loading-md',   // 56px
  lg: 'loading-lg',   // 80px
};

// ── 컴포넌트 ───────────────────────────────
const Loading = ({
  size = 'md',
  text,
  subText,
  showProgress = false,
  progress = 0,
  fullScreen = false,
}: LoadingProps) => {
  return (
    <div className={`loading-wrapper ${fullScreen ? 'loading-fullscreen' : ''}`}>

      {/* 원형 스피너 */}
      <div className={`loading-spinner ${sizeStyles[size]}`}>
        {/* 뒤 회색 원 */}
        <div className="loading-track" />
        {/* 앞 초록 원 (돌아가는 것) */}
        <div className="loading-circle" />
      </div>

      {/* 로딩 텍스트 */}
      {text && (
        <p className="loading-text">{text}</p>
      )}

      {/* 서브 텍스트 */}
      {subText && (
        <p className="loading-subtext">{subText}</p>
      )}

      {/* 진행바 */}
      {showProgress && (
        <div className="loading-progress-track">
          <div
            className="loading-progress-bar"
            style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
            role="progressbar"
            aria-valuenow={progress}
            aria-valuemin={0}
            aria-valuemax={100}
          />
        </div>
      )}
    </div>
  );
};

export default Loading;