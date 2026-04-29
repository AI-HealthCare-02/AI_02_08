import React, { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './LandingPage.css';
import bgLandingImage from '../../assets/images/bg-landing.png';
import landing1Image from '../../assets/images/landing1.png';
import yakssoriImage from '../../assets/images/yakssori.png';

const LandingPage: React.FC = () => {
  const navigate = useNavigate();
  const heroImgRef = useRef<HTMLDivElement>(null);
  const circularTextRef = useRef<SVGSVGElement>(null);
  const heroContentRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('animate-in');
          } else {
            entry.target.classList.remove('animate-in');
          }
        });
      },
      { threshold: 0.15 }
    );

    document.querySelectorAll('.scroll-animate').forEach((el) => {
      observer.observe(el);
    });

    const handleScroll = () => {
      const scrollY = window.scrollY;
      const vh = window.innerHeight;
      if (heroImgRef.current) {
        heroImgRef.current.style.transform = `scale(${1 + scrollY * 0.0003})`;
      }
      if (circularTextRef.current) {
        circularTextRef.current.style.transform = `rotate(${scrollY * 0.3}deg)`;
      }
      if (heroContentRef.current) {
        const fade = Math.max(0, 1 - scrollY / (vh * 0.5));
        heroContentRef.current.style.opacity = `${fade}`;
        heroContentRef.current.style.transform = `translateY(${scrollY * 0.3}px)`;
      }
    };

    window.addEventListener('scroll', handleScroll, { passive: true });

    return () => {
      observer.disconnect();
      window.removeEventListener('scroll', handleScroll);
    };
  }, []);

  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <div className="lp">

      {/* Section 1: Hero */}
      <section className="lp-hero">
        <div className="lp-hero__bg" ref={heroImgRef} style={{ backgroundImage: `url(${bgLandingImage})` }} />
        <div className="lp-hero__overlay" />
        <div className="lp-hero__content" ref={heroContentRef}>
          <div className="lp-hero__circle-wrap">
            <svg className="lp-hero__circular" ref={circularTextRef} viewBox="0 0 300 300">
              <defs>
                <path id="circlePath" d="M150,150 m-120,0 a120,120 0 1,1 240,0 a120,120 0 1,1 -240,0" />
              </defs>
              <text>
                <textPath href="#circlePath" startOffset="0%">
                  이루도담 · 복약관리 · AI상담 · OCR인식 · 이루도담 · 복약관리 · AI상담 · OCR인식 ·
                </textPath>
              </text>
            </svg>
            <h1 className="lp-hero__title">이루도담</h1>
          </div>
          <p className="lp-hero__sub">
            사용자가 복용 중인 약을 등록·관리하고<br />올바른 복약 습관을 돕는 웹 서비스
          </p>
        </div>
        <div className="lp-hero__scroll">
          <span className="lp-hero__scroll-arrow">↓</span>
        </div>
      </section>

      {/* Section 2: 민트 반 + 흰 반 배경 */}
      <section className="lp-split">
        {/* 배경: 위 민트, 아래 흰색 */}
        <div className="lp-split__bg-mint scroll-animate" />
        <div className="lp-split__bg-white" />

        {/* 콘텐츠 */}
        <div className="lp-split__content">
          {/* 이미지 */}
          <div className="lp-split__image-wrap scroll-animate">
            <img src={landing1Image} alt="이루도담 서비스" className="lp-split__image" />
          </div>

          {/* 소개글 */}
          <div className="lp-split__about scroll-animate">
            <h2 className="lp-split__about-title">이루도담</h2>
            <div className="lp-split__meaning">
              <div className="lp-split__word">
                <span className="lp-split__word-kr">이루</span>
                <span className="lp-split__word-desc">이루다 / 성취</span>
              </div>
              <span className="lp-split__plus">+</span>
              <div className="lp-split__word">
                <span className="lp-split__word-kr">도담</span>
                <span className="lp-split__word-desc">탈 없이 건강하게 자람</span>
              </div>
            </div>
            <p className="lp-split__summary">
              복약 이력을 쌓아 건강한 삶을 이뤄나가는<br />
              AI 기반 처방전 분석 및 복약 관리 서비스입니다.
            </p>
          </div>

          {/* 주요 기능 */}
          <div className="lp-split__features scroll-animate">
            <h2 className="lp-split__features-title">주요 기능</h2>
            <div className="lp-split__features-grid">
              <div className="lp-split__feature">
                <div className="lp-split__feature-num">01</div>
                <h3>처방전 OCR 인식</h3>
                <p>처방전 사진을 업로드하면<br />AI가 자동으로 약물 정보를 추출합니다.</p>
              </div>
              <div className="lp-split__feature">
                <div className="lp-split__feature-num">02</div>
                <h3>AI 약속이 상담</h3>
                <p>복약 관련 궁금한 점을<br />약속이에게 물어보세요.</p>
              </div>
              <div className="lp-split__feature">
                <div className="lp-split__feature-num">03</div>
                <h3>복약 관리</h3>
                <p>복약 히스토리를 기록하고<br />건강한 습관을 만들어갑니다.</p>
              </div>
            </div>
          </div>

          {/* 약속이 소개 */}
          <div className="lp-split__mascot scroll-animate">
            <img src={yakssoriImage} alt="약속이" className="lp-split__mascot-img" />
            <div className="lp-split__mascot-text">
              <h2>약속이를 소개합니다</h2>
              <p>
                약속이는 이루도담의 AI 건강 상담 챗봇입니다.<br />
                처방전 분석 결과를 바탕으로 맞춤형 복약 상담을 제공합니다.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Floating Menu Toggle */}
      <div className="lp-float">
        {menuOpen && (
          <div className="lp-float__menu">
            <span className="lp-float__item lp-float__item--active" onClick={() => navigate('/')}>홈</span>
            <span className="lp-float__item" onClick={() => navigate('/login')}>복약관리</span>
            <span className="lp-float__item" onClick={() => navigate('/login')}>마이페이지</span>
            <span className="lp-float__item lp-float__item--login" onClick={() => navigate('/login')}>로그인</span>
          </div>
        )}
        <button className={`lp-float__toggle ${menuOpen ? 'lp-float__toggle--open' : ''}`} onClick={() => setMenuOpen(!menuOpen)} aria-label="메뉴">
          <span /><span /><span />
        </button>
      </div>
    </div>
  );
};

export default LandingPage;
