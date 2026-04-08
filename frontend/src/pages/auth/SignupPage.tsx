import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { checkEmailDuplicate, sendVerificationCode, verifyEmailCode } from '../../api/authApi';
import Button from '../../components/common/Button';
import Input from '../../components/common/Input';
import './SignupPage.css';
import bgLandingImage from '../../assets/images/bg-landing.png';

interface FormData {
  email: string;
  password: string;
  passwordConfirm: string;
  verificationCode: string;
}

interface FormErrors {
  email?: string;
  password?: string;
  passwordConfirm?: string;
  verificationCode?: string;
}

const SignupPage: React.FC = () => {
  const navigate = useNavigate();
  const { signup } = useAuth();
  const [formData, setFormData] = useState<FormData>({
    email: '',
    password: '',
    passwordConfirm: '',
    verificationCode: ''
  });
  const [errors, setErrors] = useState<FormErrors>({});
  const [isLoading, setIsLoading] = useState(false);
  const [emailVerified, setEmailVerified] = useState(false);
  const [codeSent, setCodeSent] = useState(false);
  const [timer, setTimer] = useState(0);

  // 타이머 시작
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

  // 입력 값 변경
  const handleInputChange = (field: keyof FormData) => (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setFormData(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: undefined }));
    }
  };

  // 이메일 유효성 검사
  const validateEmail = (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  // 비밀번호 유효성 검사
  const validatePassword = (password: string): boolean => {
    return password.length >= 8;
  };

  // 이메일 중복 확인 및 인증코드 발송 (Mock)
  const handleSendCode = async () => {
    if (!validateEmail(formData.email)) {
      setErrors(prev => ({ ...prev, email: '올바른 이메일 형식을 입력해주세요.' }));
      return;
    }

    setIsLoading(true);
    try {
      // Mock: 항상 성공으로 처리
      console.log('Mock: 이메일 중복 확인 및 인증코드 발송:', formData.email);
      
      // 임시 로딩 시뮬레이션
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setCodeSent(true);
      startTimer();
      alert('인증코드가 발송되었습니다. (Mock: 123456 입력하세요)');
    } catch (error) {
      console.error('에러 발생:', error);
      alert('인증코드 발송에 실패했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  // 인증코드 확인 (Mock)
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
        setEmailVerified(true);
        alert('이메일 인증이 완료되었습니다.');
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

  // 회원가입 제출
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // 유효성 검사
    const newErrors: FormErrors = {};
    
    if (!emailVerified) {
      newErrors.email = '이메일 인증을 완료해주세요.';
    }
    
    if (!validatePassword(formData.password)) {
      newErrors.password = '비밀번호는 8자 이상이어야 합니다.';
    }
    
    if (formData.password !== formData.passwordConfirm) {
      newErrors.passwordConfirm = '비밀번호가 일치하지 않습니다.';
    }
    
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setIsLoading(true);
    try {
      const success = await signup(formData.email.split('@')[0], formData.email, formData.password);
      if (success) {
        alert('회원가입이 완료되었습니다!');
        navigate('/'); // 회원가입 성공 시 홈으로 이동
      } else {
        alert('회원가입에 실패했습니다.');
      }
    } catch (error) {
      alert('회원가입에 실패했습니다.');
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
    <div className="signup-page">
      {/* 배경 이미지 */}
      <div 
        className="signup-page__background"
        style={{ backgroundImage: `url(${bgLandingImage})` }}
      >
        <div className="signup-page__background-overlay" />
      </div>
      
      <div className="signup-page__container">
        {/* 카드 상단 라인 */}
        <div className="signup-page__card-line" />
        
        <div className="signup-page__header">
          <h1 className="signup-page__title">이루도담</h1>
          <p className="signup-page__subtitle">처음 만나서 반가워요 🌿</p>
        </div>

        <form onSubmit={handleSubmit} className="signup-page__form">
          {/* 이메일 */}
          <div className="signup-page__field">
            <div className="signup-page__email-group">
              <Input
                label="이메일"
                type="email"
                value={formData.email}
                onChange={handleInputChange('email')}
                placeholder="이메일을 입력하세요"
                disabled={emailVerified}
                error={errors.email}
              />
              <Button
                type="button"
                onClick={handleSendCode}
                disabled={isLoading || emailVerified || !formData.email}
                variant="secondary"
                size="sm"
              >
                중복확인
              </Button>
            </div>
            {emailVerified && (
              <p className="signup-page__success">✓ 이메일 인증 완료</p>
            )}
          </div>

          {/* 인증번호 - 항상 표시 */}
          <div className="signup-page__field">
            <div className="signup-page__code-group">
              <Input
                label={`인증번호${timer > 0 ? ` (${formatTime(timer)})` : ''}`}
                type="text"
                value={formData.verificationCode}
                onChange={handleInputChange('verificationCode')}
                placeholder="인증번호를 입력하세요"
                maxLength={6}
                disabled={!codeSent || emailVerified}
                error={errors.verificationCode}
              />
              <Button
                type="button"
                onClick={handleVerifyCode}
                disabled={isLoading || !codeSent || !formData.verificationCode || timer === 0 || emailVerified}
                variant="secondary"
                size="sm"
              >
                인증하기
              </Button>
            </div>
          </div>

          {/* 비밀번호 */}
          <Input
            label="비밀번호"
            type="password"
            value={formData.password}
            onChange={handleInputChange('password')}
            placeholder="비밀번호를 입력하세요"
            error={errors.password}
            showPasswordToggle
          />

          {/* 비밀번호 확인 */}
          <Input
            label="비밀번호 확인"
            type="password"
            value={formData.passwordConfirm}
            onChange={handleInputChange('passwordConfirm')}
            placeholder="비밀번호를 다시 입력하세요"
            error={errors.passwordConfirm}
            showPasswordToggle
          />

          {/* 제출 버튼 */}
          <Button
            type="submit"
            disabled={isLoading || !emailVerified}
            isLoading={isLoading}
            fullWidth
            className="signup-page__submit"
          >
            회원가입
          </Button>
        </form>

        {/* 로그인 링크 */}
        <div className="signup-page__footer">
          <p>
            이미 회원이신가요?{' '}
            <button
              type="button"
              onClick={() => navigate('/login')}
              className="signup-page__link"
            >
              로그인
            </button>
          </p>
        </div>
      </div>
    </div>
  );
};

export default SignupPage;