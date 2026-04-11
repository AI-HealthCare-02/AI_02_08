import React from 'react';
import { Toast, ToastType, useToast } from '../../contexts/ToastContext';
import './ToastContainer.css';

interface ToastItemProps {
  toast: Toast;
}

const ToastItem: React.FC<ToastItemProps> = ({ toast }) => {
  const { removeToast } = useToast();

  const getIcon = (type: ToastType) => {
    switch (type) {
      case 'success':
        return '✅';
      case 'error':
        return '❌';
      case 'warning':
        return '⚠️';
      case 'info':
        return 'ℹ️';
      default:
        return 'ℹ️';
    }
  };

  return (
    <div className={`toast toast--${toast.type}`}>
      <div className="toast__content">
        <div className="toast__icon">
          {getIcon(toast.type)}
        </div>
        <div className="toast__text">
          <div className="toast__title">{toast.title}</div>
          {toast.message && (
            <div className="toast__message">{toast.message}</div>
          )}
        </div>
      </div>
      <button 
        className="toast__close"
        onClick={() => removeToast(toast.id)}
        aria-label="닫기"
      >
        ✕
      </button>
    </div>
  );
};

const ToastContainer: React.FC = () => {
  const { toasts } = useToast();

  return (
    <div className="toast-container">
      {toasts.map(toast => (
        <ToastItem key={toast.id} toast={toast} />
      ))}
    </div>
  );
};

export default ToastContainer;