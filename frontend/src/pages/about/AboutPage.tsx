import React from 'react';
import bgLandingImage from '../../assets/images/bg-landing.png';
import yakssoriImg from '../../assets/images/yakssori.png';
import './AboutPage.css';

const AboutPage: React.FC = () => {
  return (
    <div className="about">
      {/* 상단 이미지 */}
      <div className="about__img-section">
        <img src={bgLandingImage} alt="" className="about__img about__img--top" />
      </div>

      {/* 타이틀 + 의미 */}
      <div className="about__body">
        <div className="about__title-row">
          <h1 className="about__title">이루도담</h1>
          <span className="about__title-badge">소개글</span>
        </div>

        <div className="about__meaning">
          <div className="about__word">
            <span className="about__word-kr">이루</span>
            <span className="about__word-desc">이루다 / 성취</span>
          </div>
          <span className="about__plus">+</span>
          <div className="about__word">
            <span className="about__word-kr">도담</span>
            <span className="about__word-desc">탈 없이 건강하게 자람</span>
          </div>
        </div>

        <p className="about__summary">
          복약 이력을 쌓아 건강한 삶을 이뤄나가는<br />
          AI 기반 처방전 분석 및 복약 관리 서비스입니다.
        </p>
      </div>

      {/* 주요 기능 */}
      <div className="about__features">
        <h2 className="about__section-title">주요 기능</h2>
        <div className="about__feature-grid">
          <div className="about__feature">
            <div className="about__feature-num">01</div>
            <h3 className="about__feature-name">처방전 OCR 인식</h3>
            <p className="about__feature-desc">
              처방전 사진을 업로드하면<br />AI가 자동으로 약물 정보를 추출합니다.
            </p>
          </div>
          <div className="about__feature">
            <div className="about__feature-num">02</div>
            <h3 className="about__feature-name">AI 약속이 상담</h3>
            <p className="about__feature-desc">
              복약 관련 궁금한 점을<br />약속이에게 물어보세요.
            </p>
          </div>
          <div className="about__feature">
            <div className="about__feature-num">03</div>
            <h3 className="about__feature-name">복약 관리</h3>
            <p className="about__feature-desc">
              복약 히스토리를 기록하고<br />건강한 습관을 만들어갑니다.
            </p>
          </div>
        </div>
      </div>

      {/* 약속이 소개 */}
      <div className="about__mascot">
        <img src={yakssoriImg} alt="약속이" className="about__mascot-img" />
        <div className="about__mascot-text">
          <h2 className="about__section-title">약속이를 소개합니다</h2>
          <p className="about__mascot-desc">
            약속이는 이루도담의 AI 건강 상담 챗봇입니다.<br />
            처방전 분석 결과를 바탕으로 맞춤형 복약 상담을 제공합니다.
          </p>
        </div>
      </div>

      {/* 하단 이미지 - 사진 아래쪽 부분 */}
      <div className="about__img-section">
        <img src={bgLandingImage} alt="" className="about__img about__img--bottom" />
      </div>
    </div>
  );
};

export default AboutPage;
