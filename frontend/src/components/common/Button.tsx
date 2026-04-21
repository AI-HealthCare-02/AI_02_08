// ==============================================
// Button.tsx — 공통 버튼 컴포넌트
// 이루도담 | Branch: feature/common-components
// ==============================================

import React from 'react';

// ── 타입 정의 ──────────────────────────────
type ButtonVariant = 'primary' | 'secondary' | 'warning';
type ButtonSize = 'sm' | 'md' | 'lg';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;   // 버튼 스타일 종류
  size?: ButtonSize;         // 버튼 크기
  isLoading?: boolean;       // 로딩 상태
  fullWidth?: boolean;       // 전체 너비 여부
  children: React.ReactNode;
}

// ── 스타일 맵 ──────────────────────────────
const variantStyles: Record<ButtonVariant, string> = {
  primary:   'btn-primary',
  secondary: 'btn-secondary',
  warning:   'btn-warning',
};

const sizeStyles: Record<ButtonSize, string> = {
  sm: 'btn-sm',
  md: 'btn-md',
  lg: 'btn-lg',
};

// ── 컴포넌트 ───────────────────────────────
const Button = ({
  variant = 'primary',
  size = 'md',
  isLoading = false,
  fullWidth = false,
  children,
  disabled,
  className = '',
  ...props
}: ButtonProps) => {
  return (
    <button
      className={[
        'btn',
        variantStyles[variant],
        sizeStyles[size],
        fullWidth ? 'btn-full' : '',
        isLoading ? 'btn-loading' : '',
        className,
      ]
        .filter(Boolean)
        .join(' ')}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading ? (
        <span className="btn-spinner" aria-hidden="true" />
      ) : null}
      <span className={isLoading ? 'btn-text-loading' : ''}>
        {children}
      </span>
    </button>
  );
};

export default Button;