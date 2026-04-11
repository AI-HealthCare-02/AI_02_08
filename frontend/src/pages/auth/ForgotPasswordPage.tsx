import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { useToast } from '../../contexts/ToastContext';
import Button from '../../components/common/Button';
import Input from '../../components/common/Input';
import './ForgotPasswordPage.css';
import bgLandingImage from '../../assets/images/bg-landing.png';

interface FormData {
  email: string;
  verificationCode: string;
}

interface FormErrors {
  email?: string;
  verificationCode?: string;
}

const ForgotPasswordPage: React.FC = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const { showToast } = useToast();
  const [formData, setFormData] = useState<FormData>({
    email: '',
    verificationCode: ''
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

  // 이메일 유효성 검사
  const validateEmail = (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  // 인증코드 발송
  const handleSendCode = async () => {
    if (!validateEmail(formData.email)) {
      setErrors(prev => ({ ...prev, email: '올바른 이메일 형식을 입력해주세요.' }));
      return;
    }

    setIsLoading(true);
    try {
      // Mock: 실제로는 API 호출
      console.log('Mock: 비밀번호 찾기 인증코드 발송:', formData.email);
      
      // 임시 로딩 시뮬레이션
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setCodeSent(true);
      startTimer();
      showToast({
        type: 'success',
        title: '인증코드 발송 완료',
        message: '이메일로 인증코드를 발송했습니다. (Mock: 123456)'
      });
    } catch (error) {
      console.error('에러 발생:', error);
      showToast({
        type: 'error',
        title: '인증코드 발송 실패',
        message: '인증코드 발송에 실패했습니다. 다시 시도해주세요.'
      });
    } finally {
      setIsLoading(false);
    }
  };

  // 인증코드 확인 및 자동 로그인
  const handleVerifyCode = async () => {
    if (!formData.verificationCode) {
      setErrors(prev => ({ ...prev, verificationCode: '인증코드를 입력해주세요.' }));
      return;
    }

    setIsLoading(true);
    try {
      console.log('Mock: 인증코드 확인:', formData.verificationCode);
      
      // Mock: 123456이면 성공
      if (formData.verificationCode === '123456') {
        // 임시 비밀번호로 자동 로그인 (실제로는 서버에서 임시 토큰 발급)
        const success = await login(formData.email, 'temp_password_from_server');
        
        if (success) {
          showToast({
            type: 'success',
            title: '인증 완료',
            message: '마이페이지에서 비밀번호를 변경해주세요.'
          });
          // 마이페이지의 보안/계정 탭으로 이동
          navigate('/mypage?tab=account');
        } else {
          // 자동 로그인 실패 시에도 마이페이지로 이동 (Mock)
          navigate('/mypage?tab=account');
        }
      } else {
        setErrors(prev => ({ ...prev, verificationCode: '잘못된 인증코드입니다. (Mock: 123456 입력하세요)' }));
      }
    } catch (error) {
      console.error('인증 에러:', error);
      alert('인증코드 확인에 실패했습니다.');
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
      {/* 배경 이미지 */}
      <div 
        className="forgot-password-page__background"
        style={{ backgroundImage: `url(${bgLandingImage})` }}
      >
        <div className="forgot-password-page__background-overlay" />
      </div>
      
      {/* 비밀번호 찾기 카드 */}
      <div className="forgot-password-page__card">
        {/* 카드 상단 라인 */}
        <div className="forgot-password-page__card-line" />
        
        {/* 로고 영역 */}
        <div className="forgot-password-page__header">
          <img 
            src="/logo.png" 
            alt="이루도담" 
            className="forgot-password-page__logo"
          />
          <h1 className="forgot-password-page__title">
            비밀번호 찾기
          </h1>
          <p className="forgot-password-page__subtitle">
            가입하신 이메일로 인증코드를 발송해드립니다 📧
          </p>
        </div>
        
        {/* 폼 */}
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

          {/* 인증번호 입력 */}
          {codeSent && (
            <div className="forgot-password-page__field">
              <div className="forgot-password-page__code-group">
                <Input
                  label={`인증번호${timer > 0 ? ` (${formatTime(timer)})` : ''}`}
                  type="text"
                  value={formData.verificationCode}
                  onChange={handleInputChange('verificationCode')}
                  placeholder="인증번호를 입력하세요"
                  maxLength={6}
                  disabled={timer === 0}
                  error={errors.verificationCode}
                />
                <Button
                  type="button"
                  onClick={handleVerifyCode}
                  disabled={isLoading || !formData.verificationCode || timer === 0}
                  variant="primary"
                  size="sm"
                >
                  인증하기
                </Button>
              </div>
            </div>
          )}
        </div>
        
        {/* 하단 링크 */}
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