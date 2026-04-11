import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { sendPasswordResetEmail, resetPassword } from '../../api/authApi';
import { useToast } from '../../contexts/ToastContext';
import Button from '../../components/common/Button';
import Input from '../../components/common/Input';
import './ForgotPasswordPage.css';
import bgLandingImage from '../../assets/images/bg-landing.png';

interface FormData {
  email: string;
  verificationCode: string;
  newPassword: string;
  newPasswordConfirm: string;
}

interface FormErrors {
  email?: string;
  verificationCode?: string;
  newPassword?: string;
  newPasswordConfirm?: string;
}

const ForgotPasswordPage: React.FC = () => {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [formData, setFormData] = useState<FormData>({
    email: '',
    verificationCode: '',
    newPassword: '',
    newPasswordConfirm: '',
  });
  const [errors, setErrors] = useState<FormErrors>({});
  const [isLoading, setIsLoading] = useState(false);
  const [codeSent, setCodeSent] = useState(false);
  const [timer, setTimer] = useState(0);

  const startTimer = () => {
    setTimer(300); // 5분
    const interval = setInterval(() => {
      setTimer(prev => {
        if (prev <= 1) {
          clearInterval(interval);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  };

  const handleInputChange = (field: keyof FormData) => (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    setFormData(prev => ({ ...prev, [field]: e.target.value }));
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: undefined }));
    }
  };

  const validateEmail = (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  // 비밀번호 재설정 이메일 발송
  const handleSendCode = async () => {
    if (!validateEmail(formData.email)) {
      setErrors(prev => ({ ...prev, email: '올바른 이메일 형식을 입력해주세요.' }));
      return;
    }

    setIsLoading(true);
    try {
      await sendPasswordResetEmail(formData.email);
      setCodeSent(true);
      startTimer();
      showToast({
        type: 'success',
        title: '인증코드 발송 완료',
        message: '이메일로 인증코드를 발송했습니다.',
      });
    } catch (error) {
      showToast({
        type: 'error',
        title: '인증코드 발송 실패',
        message: '인증코드 발송에 실패했습니다. 다시 시도해주세요.',
      });
    } finally {
      setIsLoading(false);
    }
  };

  // 비밀번호 재설정
  const handleResetPassword = async () => {
    const newErrors: FormErrors = {};

    if (!formData.verificationCode) {
      newErrors.verificationCode = '인증코드를 입력해주세요.';
    }
    if (!formData.newPassword || formData.newPassword.length < 8) {
      newErrors.newPassword = '비밀번호는 8자 이상이어야 합니다.';
    }
    if (formData.newPassword !== formData.newPasswordConfirm) {
      newErrors.newPasswordConfirm = '비밀번호가 일치하지 않습니다.';
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setIsLoading(true);
    try {
      await resetPassword(
        formData.email,
        formData.verificationCode,
        formData.newPassword,
        formData.newPasswordConfirm,
      );
      showToast({
        type: 'success',
        title: '비밀번호 재설정 완료',
        message: '새 비밀번호로 로그인해주세요.',
      });
      navigate('/login');
    } catch (error: any) {
      const message = error.response?.data?.detail || '비밀번호 재설정에 실패했습니다.';
      showToast({
        type: 'error',
        title: '비밀번호 재설정 실패',
        message,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="forgot-password-page">
      <div
        className="forgot-password-page__background"
        style={{ backgroundImage: `url(${bgLandingImage})` }}
      >
        <div className="forgot-password-page__background-overlay" />
      </div>

      <div className="forgot-password-page__card">
        <div className="forgot-password-page__card-line" />

        <div className="forgot-password-page__header">
          <img
            src="/logo.png"
            alt="이루도담"
            className="forgot-password-page__logo"
          />
          <h1 className="forgot-password-page__title">비밀번호 찾기</h1>
          <p className="forgot-password-page__subtitle">
            가입하신 이메일로 인증코드를 발송해드립니다 📧
          </p>
        </div>

        <div className="forgot-password-page__form">
          {/* 이메일 입력 */}
          <div className="forgot-password-page__field">
            <div className="forgot-password-page__email-group">
              <Input
                label="이메일"
                type="email"
                value={formData.email}
                onChange={handleInputChange('email')}
                placeholder="가입하신 이메일을 입력하세요"
                disabled={codeSent}
                error={errors.email}
              />
              <Button
                type="button"
                onClick={handleSendCode}
                disabled={isLoading || codeSent || !formData.email}
                variant="secondary"
                size="sm"
              >
                인증코드 발송
              </Button>
            </div>
          </div>

          {/* 인증코드 + 새 비밀번호 - 코드 발송 후 표시 */}
          {codeSent && (
            <>
              <div className="forgot-password-page__field">
                <Input
                  label={`인증코드${timer > 0 ? ` (${formatTime(timer)})` : ''}`}
                  type="text"
                  value={formData.verificationCode}
                  onChange={handleInputChange('verificationCode')}
                  placeholder="인증코드를 입력하세요"
                  maxLength={6}
                  disabled={timer === 0}
                  error={errors.verificationCode}
                />
              </div>

              <Input
                label="새 비밀번호"
                type="password"
                value={formData.newPassword}
                onChange={handleInputChange('newPassword')}
                placeholder="영문 대소문자, 숫자, 특수문자 포함 8자 이상"
                error={errors.newPassword}
                showPasswordToggle
              />

              <Input
                label="새 비밀번호 확인"
                type="password"
                value={formData.newPasswordConfirm}
                onChange={handleInputChange('newPasswordConfirm')}
                placeholder="새 비밀번호를 다시 입력하세요"
                error={errors.newPasswordConfirm}
                showPasswordToggle
              />

              <Button
                type="button"
                onClick={handleResetPassword}
                disabled={isLoading || timer === 0}
                isLoading={isLoading}
                fullWidth
                className="forgot-password-page__submit"
              >
                비밀번호 재설정
              </Button>
            </>
          )}
        </div>

        <div className="forgot-password-page__footer">
          <p>
            비밀번호가 기억나셨나요?{' '}
            <button
              type="button"
              onClick={() => navigate('/login')}
              className="forgot-password-page__link"
            >
              로그인
            </button>
          </p>
        </div>
      </div>
    </div>
  );
};

export default ForgotPasswordPage;