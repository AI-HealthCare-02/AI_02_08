import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './LandingPage.css';
import bgLandingImage from '../../assets/images/bg-landing.png';

const LandingPage: React.FC = () => {
  const [currentSlide, setCurrentSlide] = useState(0);
  const navigate = useNavigate();
  
  const slides = [
    {
      id: 'slide1',
      subtitle: 'MEDICATION GUIDE',
      title: '당신을 위한 건강 가이드',
      description: '처방전 인식부터 복약 관리까지, 이루도담이 함께합니다'
    },
    {
      id: 'slide2', 
      subtitle: 'OCR SCAN',
      title: '처방전을 찍으면 끝',
      description: '카메라로 처방전을 촬영하면 약 정보를 자동으로 분석합니다'
    },
    {
      id: 'slide3',
      subtitle: 'AI CHATBOT', 
      title: '약솔이가 답해드려요',
      description: '복약 관련 궁금한 점을 AI 챗봇 약솔이에게 물어보세요'
    }
  ];

  // 자동 슬라이드 (3초마다)
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentSlide(prev => (prev + 1) % (slides.length + 1)); // +1 for CTA slide
    }, 3000);
    
    return () => clearInterval(timer);
  }, [slides.length]);

  const handleDotClick = (index: number) => {
    setCurrentSlide(index);
  };

  const handleLoginClick = () => {
    navigate('/login');
  };

  const handleSkipClick = () => {
    navigate('/login');
  };

  return (
    <div className="landing-page">
      {/* 배경 이미지 */}
      <div 
        className="landing-page__background"
        style={{ backgroundImage: `url(${bgLandingImage})` }}
      >
        <div className="landing-page__background-overlay" />
      </div>
      
      {/* 슬라이드 컨텐츠 */}
      <div className="landing-page__content">
        {currentSlide < slides.length ? (
          // 슬라이드 1-3
          <div className="landing-page__slide">
            <div className="landing-page__slide-content">
              <p className="landing-page__subtitle">
                {slides[currentSlide].subtitle}
              </p>
              <h1 className="landing-page__title">
                {slides[currentSlide].title}
              </h1>
              <p className="landing-page__description">
                {slides[currentSlide].description}
              </p>
              
              {/* 스킵 버튼 - 원 안에 위치 */}
              <button 
                onClick={handleSkipClick}
                className="landing-page__skip-button"
                aria-label="슬라이드 건너뛰고 로그인"
              >
                <div className="landing-page__skip-circle">
                  <div className="landing-page__skip-icon">↓</div>
                </div>
                <span className="landing-page__skip-text">로그인하기</span>
              </button>
            </div>
            
            {/* 슬라이드 도트 */}
            <div className="landing-page__dots">
              {slides.map((_, index) => (
                <button
                  key={index}
                  className={`landing-page__dot ${
                    index === currentSlide ? 'landing-page__dot--active' : ''
                  }`}
                  onClick={() => handleDotClick(index)}
                  aria-label={`슬라이드 ${index + 1}로 이동`}
                />
              ))}
            </div>
          </div>
        ) : (
          // CTA 슬라이드
          <div className="landing-page__cta">
            <div className="landing-page__cta-content">
              <img 
                src="/logo.png" 
                alt="이루도담" 
                className="landing-page__cta-logo"
              />
              <h1 className="landing-page__cta-title">이루도담</h1>
              <p className="landing-page__cta-subtitle">
                당신을 위한 건강 가이드
              </p>
              <button 
                onClick={handleLoginClick}
                className="landing-page__cta-button"
              >
                로그인
              </button>
            </div>
          </div>
        )}
        {/* 스킵 버튼 - 우측 하단 고정 */}
        <button 
          onClick={handleSkipClick}
          className="landing-page__skip-button"
          aria-label="슬라이드 건너뛰고 로그인"
        >
          <div className="landing-page__skip-icon">↓</div>
          <span className="landing-page__skip-text">스킵</span>
        </button>
      </div>
    </div>
  );
};

export default LandingPage;