import React, { useState } from 'react';
import { useAuth } from '../../hooks/useAuth';
import './HomePage.css';

const HomePage: React.FC = () => {
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [ocrStatus, setOcrStatus] = useState<'idle' | 'uploading' | 'processing' | 'completed' | 'error'>('idle');
  const [uploadProgress, setUploadProgress] = useState(0);
  const [ocrResults, setOcrResults] = useState<{
    medicines: string[];
    warnings: string[];
    interactions: string[];
  } | null>(null);
  const [showManualInput, setShowManualInput] = useState(false);
  const [manualInputData, setManualInputData] = useState({
    name: '',
    dosage: '',
    usage: '',
    timing: ''
  });
  const [chatMessage, setChatMessage] = useState('');
  const { user } = useAuth();

  const displayName = user?.name || '사용자';

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedImage(file);
      setOcrStatus('uploading');
      
      // 이미지 미리보기 URL 생성
      const reader = new FileReader();
      reader.onload = (e) => {
        setPreviewUrl(e.target?.result as string);
        
        // 업로드 진행률 시뮬레이션
        simulateUploadProgress();
      };
      reader.readAsDataURL(file);
    }
  };

  const simulateUploadProgress = () => {
    setUploadProgress(0);
    const interval = setInterval(() => {
      setUploadProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          setOcrStatus('processing');
          
          setTimeout(() => {
            // 이미지 유형 검증 시뮬레이션
            const imageValidation = validateImageType();
            
            if (!imageValidation.isValid) {
              // 처방전이 아닌 경우
              setOcrStatus('error');
              return;
            }
            
            // 처방전이지만 OCR 실패 가능성
            const isOcrSuccess = Math.random() > 0.2; // 80% OCR 성공률
            
            if (isOcrSuccess) {
              setOcrStatus('completed');
              setOcrResults({
                medicines: ['타이레놀정 500mg', '루코페트정', '세레브렉스캅슐 200mg', '낙시용정 20mg'],
                warnings: ['아세트아미노펜', '알코올 주의'],
                interactions: ['아스피린 병용 주의', '위장약 병용 주의']
              });
            } else {
              setOcrStatus('error');
            }
          }, 3000);
          return 100;
        }
        return prev + 10;
      });
    }, 200);
  };

  // 이미지 유형 검증 시뮬레이션
  const validateImageType = () => {
    if (!selectedImage) return { isValid: false, reason: '이미지가 없습니다' };
    
    // 파일명에 기반한 간단한 검증 (실제로는 AI 모델로 검증)
    const fileName = selectedImage.name.toLowerCase();
    
    // 처방전 관련 키워드가 있으면 처방전으로 간주
    const prescriptionKeywords = ['처방', 'prescription', '약', 'medicine', '병원', 'hospital'];
    const hasKeyword = prescriptionKeywords.some(keyword => fileName.includes(keyword));
    
    if (hasKeyword) {
      return { isValid: true };
    }
    
    // 70% 확률로 처방전이 아닌 것으로 판단 (랜덤 시뮬레이션)
    const isValidPrescription = Math.random() > 0.7;
    
    return {
      isValid: isValidPrescription,
      reason: isValidPrescription ? '' : '처방전이 아닌 이미지입니다'
    };
  };

  const getStatusText = () => {
    switch (ocrStatus) {
      case 'idle': return '대기중';
      case 'uploading': return `업로드 중... ${uploadProgress}%`;
      case 'processing': return 'OCR 처리 중...';
      case 'completed': return '분석완료 ✓';
      case 'error': return '오류 발생';
      default: return '대기중';
    }
  };

  const getStatusColor = () => {
    switch (ocrStatus) {
      case 'idle': return '#9A8058';
      case 'uploading': return '#3498db';
      case 'processing': return '#f39c12';
      case 'completed': return '#27ae60';
      case 'error': return '#e74c3c';
      default: return '#9A8058';
    }
  };

  const handleManualInputSubmit = () => {
    if (manualInputData.name && manualInputData.dosage) {
      // 수동 입력 데이터를 OCR 결과로 변환
      setOcrResults({
        medicines: [`${manualInputData.name} ${manualInputData.dosage}`],
        warnings: ['수동 입력된 약물'],
        interactions: [manualInputData.usage || '복용법 미입력']
      });
      setOcrStatus('completed');
      setShowManualInput(false);
      // 입력 데이터 초기화
      setManualInputData({ name: '', dosage: '', usage: '', timing: '' });
    }
  };

  const handleRetakePhoto = () => {
    setPreviewUrl(null);
    setSelectedImage(null);
    setOcrStatus('idle');
    setUploadProgress(0);
    setOcrResults(null);
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
              <p className="home-page__upload-status" style={{ color: getStatusColor() }}>
                {getStatusText()}
              </p>
            </div>
            
            <div className="home-page__upload-area">
              <input 
                type="file" 
                id="prescription-upload"
                accept="image/*,.pdf"
                onChange={handleImageUpload}
                className="home-page__file-input"
                disabled={ocrStatus === 'uploading' || ocrStatus === 'processing'}
              />
              
              {previewUrl ? (
                <div className="home-page__image-preview">
                  <img 
                    src={previewUrl} 
                    alt="업로드된 처방전" 
                    className="home-page__preview-image"
                  />
                  
                  <div className="home-page__preview-overlay">
                    <button 
                      onClick={() => {
                        setPreviewUrl(null);
                        setSelectedImage(null);
                        setOcrStatus('idle');
                        setUploadProgress(0);
                        setOcrResults(null);
                      }}
                      className="home-page__remove-btn"
                      disabled={ocrStatus === 'uploading' || ocrStatus === 'processing'}
                    >
                      ✕
                    </button>
                    <label htmlFor="prescription-upload" className="home-page__change-btn">
                      변경
                    </label>
                  </div>
                </div>
              ) : (
                <label htmlFor="prescription-upload" className="home-page__upload-label">
                  <div className="home-page__upload-icon">📷</div>
                  <p className="home-page__upload-text">
                    처방전 이미지를 업로드 하거나<br />
                    드래그 & 드롭하세요
                  </p>
                  <p className="home-page__upload-formats">JPG, PNG, PDF 최대 10MB</p>
                </label>
              )}
            </div>
          </div>

          {/* OCR 결과 섹션 */}
          <div className="home-page__ocr-results">
            <h2 className="home-page__section-title">
              처방전 인식 결과 {ocrResults ? '✓' : ''}
            </h2>
            
            <div className="home-page__medicine-categories">
              <div className="home-page__medicine-category">
                <h3 className="home-page__category-title home-page__category-title--blue">약 목록</h3>
                <div className="home-page__medicine-tags">
                  {ocrResults && ocrResults.medicines.length > 0 ? (
                    ocrResults.medicines.map((medicine, index) => (
                      <span key={index} className="home-page__medicine-tag home-page__medicine-tag--blue">
                        {medicine}
                      </span>
                    ))
                  ) : (
                    <div className="home-page__empty-state">처방전을 업로드하면 약 목록이 표시됩니다</div>
                  )}
                </div>
              </div>
              
              <div className="home-page__medicine-category">
                <h3 className="home-page__category-title home-page__category-title--orange">주의 성분</h3>
                <div className="home-page__medicine-tags">
                  {ocrResults && ocrResults.warnings.length > 0 ? (
                    ocrResults.warnings.map((warning, index) => (
                      <span key={index} className="home-page__medicine-tag home-page__medicine-tag--orange">
                        {warning}
                      </span>
                    ))
                  ) : (
                    <div className="home-page__empty-state">주의해야 할 성분이 표시됩니다</div>
                  )}
                </div>
              </div>
              
              <div className="home-page__medicine-category">
                <h3 className="home-page__category-title home-page__category-title--teal">상호작용</h3>
                <div className="home-page__medicine-tags">
                  {ocrResults && ocrResults.interactions.length > 0 ? (
                    ocrResults.interactions.map((interaction, index) => (
                      <span key={index} className="home-page__medicine-tag home-page__medicine-tag--teal">
                        {interaction}
                      </span>
                    ))
                  ) : (
                    <div className="home-page__empty-state">상호작용 정보가 표시됩니다</div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* 오른쪽: 챗봇 섹션 */}
        <div className="home-page__right">
          <div className="home-page__chatbot-section">
            <div className="home-page__chatbot-header">
              <h2 className="home-page__section-title">🤖 약속이 상담소</h2>
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

      {/* OCR 처리 모달 */}
      {(ocrStatus === 'uploading' || ocrStatus === 'processing') && (
        <div className="home-page__modal-overlay">
          <div className="home-page__modal">
            <div className="home-page__loading-spinner"></div>
            <h3 className="home-page__modal-title">
              {ocrStatus === 'uploading' ? '처방전을 분석하고 있습니다 ...' : 'OCR 처리 중...'}
            </h3>
            <p className="home-page__modal-subtitle">
              {ocrStatus === 'uploading' ? '잠시만 기다려주세요.' : '약물 정보를 추출하고 있습니다.'}
            </p>
            
            {/* 진행률 바 */}
            <div className="home-page__modal-progress">
              <div className="home-page__modal-progress-bar">
                <div 
                  className="home-page__modal-progress-fill"
                  style={{ 
                    width: ocrStatus === 'uploading' ? `${uploadProgress}%` : '100%'
                  }}
                />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* OCR 실패 모달 */}
      {ocrStatus === 'error' && (
        <div className="home-page__modal-overlay">
          <div className="home-page__modal">
            <div className="home-page__error-icon"></div>
            <h3 className="home-page__modal-title home-page__modal-title--error">
              처방전 인식에 실패 했습니다.
            </h3>
            <p className="home-page__modal-subtitle">
              처방전이 아닌 이미지이거나<br />
              이미지가 명확하지 않아 인식에 실패했습니다.<br />
              다시 촬영하거나 직접 입력해주세요.
            </p>
            
            <div className="home-page__modal-buttons">
              <button 
                onClick={handleRetakePhoto}
                className="home-page__modal-btn home-page__modal-btn--primary"
              >
                재촬영하기
              </button>
              <button 
                onClick={() => setShowManualInput(true)}
                className="home-page__modal-btn home-page__modal-btn--secondary"
              >
                수동입력
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 수동 입력 모달 */}
      {showManualInput && (
        <div className="home-page__modal-overlay">
          <div className="home-page__modal home-page__modal--large">
            <div className="home-page__modal-header">
              <h3 className="home-page__modal-title">복용 정보 입력</h3>
              <button 
                onClick={() => setShowManualInput(false)}
                className="home-page__modal-close"
              >
                ✕
              </button>
            </div>
            
            <div className="home-page__modal-form">
              <div className="home-page__form-group">
                <label>약 이름</label>
                <input 
                  type="text"
                  placeholder="약 이름을 입력해주세요"
                  value={manualInputData.name}
                  onChange={(e) => setManualInputData({...manualInputData, name: e.target.value})}
                  className="home-page__form-input"
                />
              </div>
              
              <div className="home-page__form-group">
                <label>용량</label>
                <input 
                  type="text"
                  placeholder="ex) 500mg"
                  value={manualInputData.dosage}
                  onChange={(e) => setManualInputData({...manualInputData, dosage: e.target.value})}
                  className="home-page__form-input"
                />
              </div>
              
              <div className="home-page__form-group">
                <label>복용법</label>
                <input 
                  type="text"
                  placeholder="ex) 1일 3회"
                  value={manualInputData.usage}
                  onChange={(e) => setManualInputData({...manualInputData, usage: e.target.value})}
                  className="home-page__form-input"
                />
              </div>
              
              <div className="home-page__form-group">
                <label>식후 ❓</label>
                <input 
                  type="text"
                  placeholder="식후 30분"
                  value={manualInputData.timing}
                  onChange={(e) => setManualInputData({...manualInputData, timing: e.target.value})}
                  className="home-page__form-input"
                />
              </div>
            </div>
            
            <div className="home-page__modal-buttons">
              <button 
                onClick={() => setShowManualInput(false)}
                className="home-page__modal-btn home-page__modal-btn--secondary"
              >
                취소
              </button>
              <button 
                onClick={handleManualInputSubmit}
                className="home-page__modal-btn home-page__modal-btn--primary"
                disabled={!manualInputData.name || !manualInputData.dosage}
              >
                확인
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default HomePage;