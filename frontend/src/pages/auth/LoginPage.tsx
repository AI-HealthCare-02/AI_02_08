import React, { useState, useRef, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import './LoginPage.css';
import bgLandingImage from '../../assets/images/bg-landing.png';

const LoginPage: React.FC = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const handleShowPassword = useCallback(() => {
    if (timerRef.current) clearTimeout(timerRef.current);
    setShowPassword(true);
    timerRef.current = setTimeout(() => setShowPassword(false), 1000);
  }, []);

  const [errors, setErrors] = useState<{[key: string]: string}>({});
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  const validateForm = () => {
    const newErrors: {[key: string]: string} = {};
    if (!formData.email) {
      newErrors.email = '이메일을 입력해주세요.';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = '올바른 이메일 형식이 아닙니다.';
    }
    if (!formData.password) {
      newErrors.password = '비밀번호를 입력해주세요.';
    }
    return newErrors;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const newErrors = validateForm();
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }
    setIsLoading(true);
    try {
      const success = await login(formData.email, formData.password);
      if (success) {
        window.location.href = '/home';
      } else {
        setErrors({ general: '이메일 또는 비밀번호를 확인해주세요.' });
      }
    } catch (error) {
      console.error('로그인 오류:', error);
      setErrors({ general: '로그인에 실패했습니다. 다시 시도해주세요.' });
    } finally {
      setIsLoading(false);
    }
  };

  // 카카오 로그인
   const handleKakaoLogin = () => {
    const KAKAO_CLIENT_ID = import.meta.env.VITE_KAKAO_CLIENT_ID;
    const REDIRECT_URI = import.meta.env.VITE_KAKAO_REDIRECT_URI || 'http://localhost:3000/auth/kakao/callback';
    const kakaoAuthUrl = `https://kauth.kakao.com/oauth/authorize?client_id=${KAKAO_CLIENT_ID}&redirect_uri=${encodeURIComponent(REDIRECT_URI)}&response_type=code&prompt=login`;
    window.location.href = kakaoAuthUrl;
  };

  return (
    <div className="login-page">
      <div
        className="login-page__background"
        style={{ backgroundImage: `url(${bgLandingImage})` }}
      >
        <div className="login-page__background-overlay" />
      </div>

      <div className="login-page__card">
        <div className="login-page__card-line" />

        <div className="login-page__header">
          <img src="/logo.png" alt="이루도담" className="login-page__logo" />
          <h1 className="login-page__title">다시 만나서 반가워요 🌿</h1>
        </div>

        <form onSubmit={handleSubmit} className="login-page__form">
          {errors.general && (
            <div className="login-page__error-general">{errors.general}</div>
          )}

          <div className="login-page__field">
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              placeholder="이메일을 입력하세요"
              className={`login-page__input ${errors.email ? 'login-page__input--error' : ''}`}
              disabled={isLoading}
            />
            {errors.email && <span className="login-page__error">{errors.email}</span>}
          </div>

          <div className="login-page__field">
            <div className="login-page__password-wrapper">
              <input
                type={showPassword ? 'text' : 'password'}
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                placeholder="비밀번호를 입력하세요"
                className={`login-page__input ${errors.password ? 'login-page__input--error' : ''}`}
                disabled={isLoading}
              />
              <button
                type="button"
                onClick={handleShowPassword}
                className="login-page__password-toggle"
                disabled={isLoading}
              >
                {showPassword ? '숨기기' : '보기'}
              </button>
            </div>
            {errors.password && <span className="login-page__error">{errors.password}</span>}
          </div>

          <button type="submit" className="login-page__submit" disabled={isLoading}>
            {isLoading ? '로그인 중...' : '로그인'}
          </button>
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

        {/* 카카오 로그인 버튼 */}
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '6px' }}>
          <button
            type="button"
            onClick={handleKakaoLogin}
            style={{
              width: '52px',
              height: '52px',
              backgroundColor: '#FEE500',
              border: 'none',
              borderRadius: '50%',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <img
              src="https://developers.kakao.com/assets/img/about/logos/kakaolink/kakaolink_btn_medium.png"
              alt="카카오"
              style={{ width: '24px', height: '24px' }}
            />
          </button>
          <span style={{ color: '#fff', fontSize: '12px' }}>카카오톡</span>
        </div>

        <div className="login-page__footer">
          <Link to="/forgot-password" className="login-page__link">
            비밀번호를 잊으셨나요?
          </Link>
          <p className="login-page__signup-prompt">
            아직 회원이 아니신가요?
            <Link to="/signup" className="login-page__link login-page__link--primary">
              회원가입
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;