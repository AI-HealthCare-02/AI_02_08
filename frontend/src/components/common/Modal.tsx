// ==============================================
// Modal.tsx — 공통 모달 컴포넌트
// 이루도담 | Branch: feature/common-components
// ==============================================

import React, { useEffect } from 'react';

// ── 타입 정의 ──────────────────────────────
type ModalSize = 'sm' | 'md' | 'lg';
type ModalVariant = 'default' | 'warning';

interface ModalProps {
  isOpen: boolean;              // 모달 열림/닫힘 상태
  onClose: () => void;          // 닫기 함수
  title?: string;               // 모달 제목
  children: React.ReactNode;    // 모달 내용
  size?: ModalSize;             // 모달 크기
  variant?: ModalVariant;       // 모달 종류 (기본/경고)
  showCloseButton?: boolean;    // X 버튼 표시 여부
  closeOnOverlay?: boolean;     // 딤 클릭시 닫기 여부
}

// ── 사이즈 스타일 맵 ───────────────────────
const sizeStyles: Record<ModalSize, string> = {
  sm: 'modal-sm',   // W: 400
  md: 'modal-md',   // W: 480
  lg: 'modal-lg',   // W: 600
};

// ── 컴포넌트 ───────────────────────────────
const Modal = ({
  isOpen,
  onClose,
  title,
  children,
  size = 'md',
  variant = 'default',
  showCloseButton = true,
  closeOnOverlay = true,
}: ModalProps) => {

  // 모달 열릴 때 스크롤 막기
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  // ESC 키로 닫기
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) onClose();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    // 딤 배경 (#000000 40%)
    <div
      className="modal-overlay"
      onClick={closeOnOverlay ? onClose : undefined}
      role="dialog"
      aria-modal="true"
      aria-label={title}
    >
      {/* 모달 카드 */}
      <div
        className={[
          'modal-card',
          sizeStyles[size],
          variant === 'warning' ? 'modal-warning' : '',
        ]
          .filter(Boolean)
          .join(' ')}
        onClick={(e) => e.stopPropagation()}
      >
        {/* 모달 헤더 */}
        {(title || showCloseButton) && (
          <div className="modal-header">
            {title && (
              <h3 className={`modal-title ${variant === 'warning' ? 'modal-title-warning' : ''}`}>
                {title}
              </h3>
            )}
            {showCloseButton && (
              <button
                className="modal-close"
                onClick={onClose}
                aria-label="모달 닫기"
              >
                ✕
              </button>
            )}
          </div>
        )}

        {/* 모달 내용 */}
        <div className="modal-body">
          {children}
        </div>
      </div>
    </div>
  );
};

export default Modal;