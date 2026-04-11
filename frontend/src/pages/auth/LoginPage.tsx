import React, { useState } from 'react';
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
  const [errors, setErrors] = useState<{[key: string]: string}>({});
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    // 에러 제거
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
        navigate('/home'); // 로그인 성공 시 실제 홈페이지로 이동
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

  return (
    <div className="login-page">
      {/* 배경 이미지 */}
      <div 
        className="login-page__background"
        style={{ backgroundImage: `url(${bgLandingImage})` }}
      >
        <div className="login-page__background-overlay" />
      </div>
      
      {/* 로그인 카드 */}
      <div className="login-page__card">
        {/* 카드 상단 라인 */}
        <div className="login-page__card-line" />
        
        {/* 로고 영역 */}
        <div className="login-page__header">
          <img 
            src="/logo.png" 
            alt="이루도담" 
            className="login-page__logo"
          />
          <h1 className="login-page__title">
            다시 만나서 반가워요 🌿
          </h1>
        </div>
        
        {/* 로그인 폼 */}
        <form onSubmit={handleSubmit} className="login-page__form">
          {errors.general && (
            <div className="login-page__error-general">
              {errors.general}
            </div>
          )}
          
          {/* 이메일 필드 */}
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
            {errors.email && (
              <span className="login-page__error">{errors.email}</span>
            )}
          </div>
          
          {/* 비밀번호 필드 */}
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
                onClick={() => setShowPassword(!showPassword)}
                className="login-page__password-toggle"
                disabled={isLoading}
              >
                {showPassword ? '숨기기' : '보기'}
              </button>
            </div>
            {errors.password && (
              <span className="login-page__error">{errors.password}</span>
            )}
          </div>
          
          {/* 로그인 버튼 */}
          <button 
            type="submit" 
            className="login-page__submit"
            disabled={isLoading}
          >
            {isLoading ? '로그인 중...' : '로그인'}
          </button>
        </form>
        
        {/* 하단 링크 */}
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