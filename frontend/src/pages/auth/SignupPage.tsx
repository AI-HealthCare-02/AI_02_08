import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { sendVerificationCode, verifyEmailCode, signup } from '../../api/authApi';
import Button from '../../components/common/Button';
import Input from '../../components/common/Input';
import './SignupPage.css';
import bgLandingImage from '../../assets/images/bg-landing.png';

interface FormData {
  email: string;
  password: string;
  passwordConfirm: string;
  verificationCode: string;
  name: string;
  gender: 'MALE' | 'FEMALE' | '';
  birthDate: string;
  phoneNumber: string;
  agreeTerms: boolean;
  agreePrivacy: boolean;
}

interface FormErrors {
  email?: string;
  password?: string;
  passwordConfirm?: string;
  verificationCode?: string;
  name?: string;
  gender?: string;
  birthDate?: string;
  phoneNumber?: string;
  agreeTerms?: string;
  agreePrivacy?: string;
}

const SignupPage: React.FC = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState<FormData>({
    email: '',
    password: '',
    passwordConfirm: '',
    verificationCode: '',
    name: '',
    gender: '',
    birthDate: '',
    phoneNumber: '',
    agreeTerms: false,
    agreePrivacy: false,
  });
  const [errors, setErrors] = useState<FormErrors>({});
  const [isLoading, setIsLoading] = useState(false);
  const [emailVerified, setEmailVerified] = useState(false);
  const [codeSent, setCodeSent] = useState(false);
  const [signupCompleted, setSignupCompleted] = useState(false);
  const [timer, setTimer] = useState(0);

  const startTimer = () => {
    setTimer(300);
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
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const value = e.target.type === 'checkbox'
      ? (e.target as HTMLInputElement).checked
      : e.target.value;
    setFormData(prev => ({ ...prev, [field]: value }));
    if (errors[field as keyof FormErrors]) {
      setErrors(prev => ({ ...prev, [field]: undefined }));
    }
  };

  // 회원가입 버튼 활성화 조건
  const isFormValid = () => {
    return (
      formData.email &&
      formData.password &&
      formData.passwordConfirm &&
      formData.name &&
      formData.gender &&
      formData.birthDate &&
      formData.phoneNumber &&
      formData.agreeTerms &&
      formData.agreePrivacy &&
      formData.password === formData.passwordConfirm
    );
  };

  // 회원가입 제출
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const newErrors: FormErrors = {};
    if (formData.password.length < 8) newErrors.password = '비밀번호는 8자 이상이어야 합니다.';
    if (formData.password !== formData.passwordConfirm) newErrors.passwordConfirm = '비밀번호가 일치하지 않습니다.';
    if (!formData.name) newErrors.name = '이름을 입력해주세요.';
    if (!formData.gender) newErrors.gender = '성별을 선택해주세요.';
    if (!formData.birthDate) newErrors.birthDate = '생년월일을 입력해주세요.';
    if (!formData.phoneNumber) newErrors.phoneNumber = '전화번호를 입력해주세요.';
    if (!formData.agreeTerms) newErrors.agreeTerms = '이용약관에 동의해주세요.';
    if (!formData.agreePrivacy) newErrors.agreePrivacy = '개인정보 처리방침에 동의해주세요.';

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setIsLoading(true);
    try {
      await signup({
        email: formData.email,
        password: formData.password,
        passwordConfirm: formData.passwordConfirm,
        name: formData.name,
        gender: formData.gender as 'MALE' | 'FEMALE',
        birthDate: formData.birthDate,
        phoneNumber: formData.phoneNumber,
        agreeTerms: formData.agreeTerms,
        agreePrivacy: formData.agreePrivacy,
      });
      setSignupCompleted(true);
    } catch (error: any) {
      const message = error.response?.data?.detail || '회원가입에 실패했습니다.';
      alert(message);
    } finally {
      setIsLoading(false);
    }
  };

  // 인증코드 발송
  const handleSendCode = async () => {
    setIsLoading(true);
    try {
      await sendVerificationCode(formData.email);
      setCodeSent(true);
      startTimer();
      alert('인증코드가 발송되었습니다. 이메일을 확인해주세요.');
    } catch (error) {
      alert('인증코드 발송에 실패했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  // 인증코드 확인
  const handleVerifyCode = async () => {
    if (!formData.verificationCode) {
      setErrors(prev => ({ ...prev, verificationCode: '인증코드를 입력해주세요.' }));
      return;
    }

    setIsLoading(true);
    try {
      const verified = await verifyEmailCode(formData.email, formData.verificationCode);
      if (verified) {
        setEmailVerified(true);
        alert('이메일 인증이 완료되었습니다!');
        navigate('/login');
      } else {
        setErrors(prev => ({ ...prev, verificationCode: '잘못된 인증코드입니다.' }));
      }
    } catch (error) {
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
    <div className="signup-page">
      <div
        className="signup-page__background"
        style={{ backgroundImage: `url(${bgLandingImage})` }}
      >
        <div className="signup-page__background-overlay" />
      </div>

      <div className="signup-page__container">
        <div className="signup-page__card-line" />

        <div className="signup-page__header">
          <h1 className="signup-page__title">이루도담</h1>
          <p className="signup-page__subtitle">처음 만나서 반가워요 🌿</p>
        </div>

        <form onSubmit={handleSubmit} className="signup-page__form">
          {/* 이메일 */}
          <Input
            label="이메일"
            type="email"
            value={formData.email}
            onChange={handleInputChange('email')}
            placeholder="이메일을 입력하세요"
            disabled={signupCompleted}
            error={errors.email}
          />

          {/* 비밀번호 */}
          <Input
            label="비밀번호"
            type="password"
            value={formData.password}
            onChange={handleInputChange('password')}
            placeholder="영문 대소문자, 숫자, 특수문자 포함 8자 이상"
            disabled={signupCompleted}
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
            disabled={signupCompleted}
            error={errors.passwordConfirm}
            showPasswordToggle
          />

          {/* 이름 */}
          <Input
            label="이름"
            type="text"
            value={formData.name}
            onChange={handleInputChange('name')}
            placeholder="이름을 입력하세요"
            disabled={signupCompleted}
            error={errors.name}
          />

          {/* 성별 */}
          <div className="signup-page__field">
            <label className="signup-page__label">성별</label>
            <select
              value={formData.gender}
              onChange={handleInputChange('gender')}
              disabled={signupCompleted}
              className="signup-page__select"
            >
              <option value="">성별을 선택하세요</option>
              <option value="MALE">남성</option>
              <option value="FEMALE">여성</option>
            </select>
            {errors.gender && <p className="signup-page__error">{errors.gender}</p>}
          </div>

          {/* 생년월일 */}
          <Input
            label="생년월일"
            type="date"
            value={formData.birthDate}
            onChange={handleInputChange('birthDate')}
            disabled={signupCompleted}
            error={errors.birthDate}
          />

          {/* 전화번호 */}
          <Input
            label="전화번호"
            type="tel"
            value={formData.phoneNumber}
            onChange={handleInputChange('phoneNumber')}
            placeholder="01012345678"
            disabled={signupCompleted}
            error={errors.phoneNumber}
          />

          {/* 약관 동의 */}
          <div className="signup-page__field">
            <label className="signup-page__checkbox">
              <input
                type="checkbox"
                checked={formData.agreeTerms}
                onChange={handleInputChange('agreeTerms')}
                disabled={signupCompleted}
              />
              이용약관에 동의합니다 (필수)
            </label>
            {errors.agreeTerms && <p className="signup-page__error">{errors.agreeTerms}</p>}
          </div>

          <div className="signup-page__field">
            <label className="signup-page__checkbox">
              <input
                type="checkbox"
                checked={formData.agreePrivacy}
                onChange={handleInputChange('agreePrivacy')}
                disabled={signupCompleted}
              />
              개인정보 처리방침에 동의합니다 (필수)
            </label>
            {errors.agreePrivacy && <p className="signup-page__error">{errors.agreePrivacy}</p>}
          </div>

          {/* 회원가입 버튼 */}
          <Button
            type="submit"
            disabled={isLoading || !isFormValid() || signupCompleted}
            isLoading={isLoading}
            fullWidth
            className="signup-page__submit"
          >
            회원가입
          </Button>

          {/* 인증번호 - 회원가입 완료 후 활성화 */}
          <div className="signup-page__field">
            <div className="signup-page__code-group">
              <Input
                label={`인증번호${timer > 0 ? ` (${formatTime(timer)})` : ''}`}
                type="text"
                value={formData.verificationCode}
                onChange={handleInputChange('verificationCode')}
                placeholder="인증번호를 입력하세요"
                maxLength={6}
                disabled={!signupCompleted || emailVerified}
                error={errors.verificationCode}
              />
              <Button
                type="button"
                onClick={codeSent ? handleVerifyCode : handleSendCode}
                disabled={
                  isLoading ||
                  !signupCompleted ||
                  emailVerified ||
                  (codeSent && !formData.verificationCode)
                }
                variant="secondary"
                size="sm"
              >
                {codeSent ? '인증하기' : '인증코드 발송'}
              </Button>
            </div>
          </div>
        </form>

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