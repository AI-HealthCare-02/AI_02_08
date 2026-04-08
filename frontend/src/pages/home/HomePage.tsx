import React, { useState } from 'react';
import { useAuth } from '../../hooks/useAuth';
import './HomePage.css';

const HomePage: React.FC = () => {
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [chatMessage, setChatMessage] = useState('');
  const { user } = useAuth();

  const displayName = user?.name || '사용자';

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedImage(file);
    }
  };

  const handleChatSubmit = () => {
    if (chatMessage.trim()) {
      // TODO: 챗봇 API 연결
      console.log('챗봇 메시지:', chatMessage);
      setChatMessage('');
    }
  };

  return (
    <div className="home-page">
      {/* 인사말 섹션 */}
      <div className="home-page__greeting">
        <h1 className="home-page__title">안녕하세요, {displayName}님 !</h1>
        <p className="home-page__subtitle">오늘도 건강한 하루 되세요 😊</p>
      </div>

      <div className="home-page__content">
        {/* 왼쪽: OCR 섹션 */}
        <div className="home-page__left">
          <div className="home-page__ocr-section">
            <div className="home-page__ocr-header">
              <h2 className="home-page__section-title">처방전 인식 ( OCR )</h2>
              <p className="home-page__upload-status">대기중</p>
            </div>
            
            <div className="home-page__upload-area">
              <input 
                type="file" 
                id="prescription-upload"
                accept="image/*,.pdf"
                onChange={handleImageUpload}
                className="home-page__file-input"
              />
              <label htmlFor="prescription-upload" className="home-page__upload-label">
                <div className="home-page__upload-icon">📷</div>
                <p className="home-page__upload-text">
                  처방전 이미지를 업로드 하거나<br />
                  드래그 & 드롭하세요
                </p>
                <p className="home-page__upload-formats">JPG, PNG, PDF 최대 10MB</p>
              </label>
            </div>
          </div>

          {/* OCR 결과 섹션 */}
          <div className="home-page__ocr-results">
            <h2 className="home-page__section-title">처방전 인식 결과 ✓</h2>
            
            <div className="home-page__medicine-categories">
              <div className="home-page__medicine-category">
                <h3>약 종류</h3>
                <div className="home-page__medicine-tags">
                  <div className="home-page__empty-state">처방전을 업로드하면 약 종류가 표시됩니다</div>
                </div>
              </div>
              
              <div className="home-page__medicine-category">
                <h3>주의 성분</h3>
                <div className="home-page__medicine-tags">
                  <div className="home-page__empty-state">주의해야 할 성분이 표시됩니다</div>
                </div>
              </div>
              
              <div className="home-page__medicine-category">
                <h3>성분 작용</h3>
                <div className="home-page__medicine-tags">
                  <div className="home-page__empty-state">성분 간 상호작용 정보가 표시됩니다</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* 오른쪽: 챗봇 섹션 */}
        <div className="home-page__right">
          <div className="home-page__chatbot-section">
            <div className="home-page__chatbot-header">
              <h2 className="home-page__section-title">🤖 약솔이 상담소</h2>
              <span className="home-page__chatbot-status">답변 중</span>
            </div>
            
            <div className="home-page__chat-messages">
              <div className="home-page__chat-message home-page__chat-message--bot">
                안녕하세요! 복약 관련 궁금한 점을 물어보세요
              </div>
              
              <div className="home-page__chat-suggestions">
                <button className="home-page__suggestion-btn">부작용이 있나요?</button>
                <button className="home-page__suggestion-btn">주의사항 알려주세요</button>
                <button className="home-page__suggestion-btn">몇 번 먹어야 하나요?</button>
              </div>
            </div>
            
            <div className="home-page__chat-input-area">
              <div className="home-page__chat-input-wrapper">
                <input 
                  type="text"
                  value={chatMessage}
                  onChange={(e) => setChatMessage(e.target.value)}
                  placeholder="궁금한 내용을 물어보세요"
                  className="home-page__chat-input"
                  onKeyPress={(e) => e.key === 'Enter' && handleChatSubmit()}
                />
                <button 
                  onClick={handleChatSubmit}
                  className="home-page__send-btn"
                >
                  전송
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 생활습관 가이드 섹션 */}
      <div className="home-page__lifestyle-guide">
        <h2 className="home-page__section-title">생활습관 가이드 💡</h2>
        <div className="home-page__guide-cards">
          <div className="home-page__guide-card">
            <h3>식단 🍎</h3>
          </div>
          <div className="home-page__guide-card">
            <h3>운동🏃</h3>
          </div>
          <div className="home-page__guide-card">
            <h3>수면😴</h3>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;