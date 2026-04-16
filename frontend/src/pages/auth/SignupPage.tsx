import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { sendVerificationCode, verifyEmailCode, signup } from '../../api/authApi';
import Button from '../../components/common/Button';
import Input from '../../components/common/Input';
import Modal from '../../components/common/Modal';
import TermsContent from './TermsContent';
import PrivacyContent from './PrivacyContent';
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
  const [signupCompleted, setSignupCompleted] = useState(false);
  const [termsModalOpen, setTermsModalOpen] = useState(false);
  const [privacyModalOpen, setPrivacyModalOpen] = useState(false);


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

  const validatePassword = (password: string): string | null => {
    if (password.length < 8) return '비밀번호는 최소 8자 이상이어야 합니다.';
    if (!/[A-Z]/.test(password)) return '비밀번호에 대문자가 포함되어야 합니다.';
    if (!/[a-z]/.test(password)) return '비밀번호에 소문자가 포함되어야 합니다.';
    if (!/\d/.test(password)) return '비밀번호에 숫자가 포함되어야 합니다.';
    if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) return '비밀번호에 특수문자가 포함되어야 합니다.';
    return null;
  };

  const validateBirthDate = (birthDate: string): string | null => {
    if (!birthDate) return '생년월일을 입력해주세요.';
    const today = new Date();
    const birth = new Date(birthDate);
    const age = today.getFullYear() - birth.getFullYear();
    const monthDiff = today.getMonth() - birth.getMonth();
    const actualAge = (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) ? age - 1 : age;
    if (actualAge < 14) return '만 14세 이상만 가입할 수 있습니다.';
    return null;
  };

  const validatePhoneNumber = (phoneNumber: string): string | null => {
    if (!phoneNumber) return '전화번호를 입력해주세요.';
    const phoneRegex = /^010[0-9]{8}$|^010-[0-9]{4}-[0-9]{4}$/;
    if (!phoneRegex.test(phoneNumber)) return '올바른 전화번호 형식이 아닙니다. (010XXXXXXXX 또는 010-XXXX-XXXX)';
    return null;
  };

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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const newErrors: FormErrors = {};
    const passwordError = validatePassword(formData.password);
    if (passwordError) newErrors.password = passwordError;
    if (formData.password !== formData.passwordConfirm) newErrors.passwordConfirm = '비밀번호가 일치하지 않습니다.';
    if (!formData.name.trim()) newErrors.name = '이름을 입력해주세요.';
    if (!formData.gender) newErrors.gender = '성별을 선택해주세요.';
    const birthDateError = validateBirthDate(formData.birthDate);
    if (birthDateError) newErrors.birthDate = birthDateError;
    const phoneError = validatePhoneNumber(formData.phoneNumber);
    if (phoneError) newErrors.phoneNumber = phoneError;
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

  const handleResendCode = async () => {
    setIsLoading(true);
    try {
      await sendVerificationCode(formData.email);
      alert('인증코드가 재발송되었습니다. 이메일을 확인해주세요.');
    } catch (error) {
      alert('인증코드 재발송에 실패했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

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
        alert('이메일 인증이 완료되었습니다! 로그인해주세요.');
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

  const handleKakaoSignup = () => {
    const KAKAO_CLIENT_ID = import.meta.env.VITE_KAKAO_CLIENT_ID;
    const REDIRECT_URI = 'http://localhost:3000/auth/kakao/callback';
    const kakaoAuthUrl = `https://kauth.kakao.com/oauth/authorize?client_id=${KAKAO_CLIENT_ID}&redirect_uri=${encodeURIComponent(REDIRECT_URI)}&response_type=code`;
    window.location.href = kakaoAuthUrl;
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
          <img src="/logo.png" alt="이루도담 로고" className="signup-page__logo" />
          <h1 className="signup-page__title">이루도담</h1>
          <p className="signup-page__subtitle">처음 만나서 반가워요 🌿</p>
        </div>

        <form onSubmit={handleSubmit} className="signup-page__form">
          <Input label="이메일" type="email" value={formData.email} onChange={handleInputChange('email')} placeholder="이메일을 입력하세요" disabled={signupCompleted} error={errors.email} />
          <Input label="비밀번호" type="password" value={formData.password} onChange={handleInputChange('password')} placeholder="대소문자, 숫자, 특수문자 각 1개 이상 포함 8자 이상" disabled={signupCompleted} error={errors.password} showPasswordToggle />
          <Input label="비밀번호 확인" type="password" value={formData.passwordConfirm} onChange={handleInputChange('passwordConfirm')} placeholder="비밀번호를 다시 입력하세요" disabled={signupCompleted} error={errors.passwordConfirm} showPasswordToggle />
          <Input label="이름" type="text" value={formData.name} onChange={handleInputChange('name')} placeholder="이름을 입력하세요" disabled={signupCompleted} error={errors.name} />

          <div className="signup-page__field">
            <label className="signup-page__label">성별</label>
            <select value={formData.gender} onChange={handleInputChange('gender')} disabled={signupCompleted} className="signup-page__select">
              <option value="">성별을 선택하세요</option>
              <option value="MALE">남성</option>
              <option value="FEMALE">여성</option>
            </select>
            {errors.gender && <p className="signup-page__error">{errors.gender}</p>}
          </div>

          <Input label="생년월일 (만 14세 이상)" type="date" value={formData.birthDate} onChange={handleInputChange('birthDate')} disabled={signupCompleted} error={errors.birthDate} />
          <Input label="전화번호" type="tel" value={formData.phoneNumber} onChange={handleInputChange('phoneNumber')} placeholder="010XXXXXXXX 또는 010-XXXX-XXXX" disabled={signupCompleted} error={errors.phoneNumber} />

          <div className="signup-page__terms-section">
            <div className="signup-page__field">
              <div className="signup-page__terms-row">
                <label className="signup-page__checkbox">
                  <input type="checkbox" checked={formData.agreeTerms} onChange={handleInputChange('agreeTerms')} disabled={signupCompleted} />
                  이용약관에 동의합니다 (필수)
                </label>
                <button type="button" className="signup-page__terms-view" onClick={() => setTermsModalOpen(true)}>보기</button>
              </div>
              {errors.agreeTerms && <p className="signup-page__error">{errors.agreeTerms}</p>}
            </div>

            <div className="signup-page__field">
              <div className="signup-page__terms-row">
                <label className="signup-page__checkbox">
                  <input type="checkbox" checked={formData.agreePrivacy} onChange={handleInputChange('agreePrivacy')} disabled={signupCompleted} />
                  개인정보 처리방침에 동의합니다 (필수)
                </label>
                <button type="button" className="signup-page__terms-view" onClick={() => setPrivacyModalOpen(true)}>보기</button>
              </div>
              {errors.agreePrivacy && <p className="signup-page__error">{errors.agreePrivacy}</p>}
            </div>
          </div>

          <Modal isOpen={termsModalOpen} onClose={() => setTermsModalOpen(false)} title="이용약관" size="lg">
            <TermsContent />
          </Modal>

          <Modal isOpen={privacyModalOpen} onClose={() => setPrivacyModalOpen(false)} title="개인정보 처리방침" size="lg">
            <PrivacyContent />
          </Modal>

          {!signupCompleted ? (
            <Button type="submit" disabled={isLoading || !isFormValid()} isLoading={isLoading} fullWidth className="signup-page__submit">
              회원가입
            </Button>
          ) : (
            <Button type="button" onClick={handleResendCode} disabled={isLoading || emailVerified} variant="secondary" fullWidth className="signup-page__submit">
              인증코드 재발송
            </Button>
          )}

          {signupCompleted && (
            <div className="signup-page__verification-notice">
              <p>이메일을 확인해주세요 📧</p>
              <p>입력하신 이메일로 인증 코드를 발송했습니다.<br />인증 코드는 24시간 내에 입력해주세요.</p>
            </div>
          )}

          {signupCompleted && (
            <div className="signup-page__field">
              <div className="signup-page__code-group">
                <Input
                  label="인증번호"
                  type="text"
                  value={formData.verificationCode}
                  onChange={handleInputChange('verificationCode')}
                  placeholder="인증번호를 입력하세요"
                  maxLength={6}
                  disabled={emailVerified}
                  error={errors.verificationCode}
                />
                <Button
                  type="button"
                  onClick={handleVerifyCode}
                  disabled={isLoading || emailVerified || !formData.verificationCode}
                  variant="secondary"
                  size="sm"
                >
                  인증하기
                </Button>
              </div>
            </div>
          )}
        </form>

        {/* 구분선 */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          margin: '16px 0',
          gap: '8px',
        }}>
          <div style={{ flex: 1, height: '1px', backgroundColor: '#ddd' }} />
          <span style={{ color: '#999', fontSize: '13px' }}>또는</span>
          <div style={{ flex: 1, height: '1px', backgroundColor: '#ddd' }} />
        </div>

        {/* 카카오 간편가입 버튼 */}
        <button
          type="button"
          onClick={handleKakaoSignup}
          style={{
            width: '100%',
            padding: '12px',
            backgroundColor: '#FEE500',
            color: '#000',
            border: 'none',
            borderRadius: '8px',
            fontSize: '15px',
            fontWeight: '600',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px',
            marginBottom: '12px',
          }}
        >
          <img
            src="https://developers.kakao.com/assets/img/about/logos/kakaolink/kakaolink_btn_medium.png"
            alt="카카오"
            style={{ width: '20px', height: '20px' }}
          />
          카카오 1초 회원가입
        </button>

        <div className="signup-page__footer">
          <p>
            이미 회원이신가요?{' '}
            <button type="button" onClick={() => navigate('/login')} className="signup-page__link">
              로그인
            </button>
          </p>
        </div>
      </div>
    </div>
  );
};

export default SignupPage;