// ==============================================
// Input.tsx — 공통 인풋 컴포넌트
// 이루도담 | Branch: feature/common-components
// ==============================================

import React, { useState } from 'react';

// ── 타입 정의 ──────────────────────────────
interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;         // 인풋 위 레이블
  error?: string;         // 에러 메시지
  hint?: string;          // 힌트 텍스트
  showPasswordToggle?: boolean; // 비밀번호 보이기/숨기기 버튼
}

// ── 컴포넌트 ───────────────────────────────
const Input = ({
  label,
  error,
  hint,
  showPasswordToggle = false,
  type = 'text',
  className = '',
  id,
  ...props
}: InputProps) => {
  const [showPassword, setShowPassword] = useState(false);

  const inputId = id || label?.replace(/\s+/g, '-').toLowerCase();
  const inputType = showPasswordToggle
    ? showPassword ? 'text' : 'password'
    : type;

  return (
    <div className="input-wrapper">
      {/* 레이블 */}
      {label && (
        <label htmlFor={inputId} className="input-label">
          {label}
        </label>
      )}

      {/* 인풋 영역 */}
      <div className={`input-container ${error ? 'input-error' : ''}`}>
        <input
          id={inputId}
          type={inputType}
          className={`input-field ${className}`}
          aria-invalid={!!error}
          aria-describedby={error ? `${inputId}-error` : undefined}
          {...props}
        />

        {/* 비밀번호 토글 버튼 */}
        {showPasswordToggle && (
          <button
            type="button"
            className="input-toggle"
            onClick={() => setShowPassword(!showPassword)}
            aria-label={showPassword ? '비밀번호 숨기기' : '비밀번호 보이기'}
          >
            {showPassword ? '숨기기' : '보이기'}
          </button>
        )}
      </div>

      {/* 에러 메시지 */}
      {error && (
        <span id={`${inputId}-error`} className="input-error-msg" role="alert">
          {error}
        </span>
      )}

      {/* 힌트 텍스트 */}
      {!error && hint && (
        <span className="input-hint">{hint}</span>
      )}
    </div>
  );
};

export default Input;