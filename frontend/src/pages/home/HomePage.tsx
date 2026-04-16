import React, { useState } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { analyzePrescription, OcrMedicationItem } from '../../api/ocrApi';
import './HomePage.css';

const HomePage: React.FC = () => {
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [ocrStatus, setOcrStatus] = useState<'idle' | 'uploading' | 'processing' | 'completed' | 'error'>('idle');
  const [ocrResults, setOcrResults] = useState<OcrMedicationItem[] | null>(null);
  const [showManualInput, setShowManualInput] = useState(false);
  const [showCameraModal, setShowCameraModal] = useState(false);
  const [cameraStream, setCameraStream] = useState<MediaStream | null>(null);
  const [cameraError, setCameraError] = useState<string | null>(null);
  const [manualInputData, setManualInputData] = useState({
    name: '',
    dosage: '',
    usage: '',
    timing: ''
  });
  const [chatMessage, setChatMessage] = useState('');
  const { user } = useAuth();

  const displayName = user?.name || '사용자';

  // 실제 OCR API 호출
  const MAX_FILE_SIZE = 15 * 1024 * 1024;
  const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'application/pdf'];

  const validateFile = (file: File): string | null => {
    if (!ALLOWED_TYPES.includes(file.type)) {
      return 'JPG, PNG, PDF 형식만 업로드 가능합니다.';
    }
    if (file.size > MAX_FILE_SIZE) {
      return '파일 크기는 15MB 이하만 가능합니다.';
    }
    return null;
  };

  const handleImageUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const error = validateFile(file);
    if (error) {
      alert(error);
      event.target.value = '';
      return;
    }

    setSelectedImage(file);
    setOcrStatus('uploading');

    const reader = new FileReader();
    reader.onload = (e) => {
      setPreviewUrl(e.target?.result as string);
    };
    reader.readAsDataURL(file);

    try {
      setOcrStatus('processing');
      const result = await analyzePrescription(file);
      setOcrResults(result.medications);
      setOcrStatus('completed');
    } catch (error) {
      console.error('OCR 분석 실패:', error);
      setOcrStatus('error');
    }
  };

  // 카메라 촬영 후 OCR 호출
  const handleCapturedImage = async (file: File) => {
    const error = validateFile(file);
    if (error) {
      alert(error);
      return;
    }

    setSelectedImage(file);
    setOcrStatus('uploading');

    const reader = new FileReader();
    reader.onload = (e) => {
      setPreviewUrl(e.target?.result as string);
    };
    reader.readAsDataURL(file);

    try {
      setOcrStatus('processing');
      const result = await analyzePrescription(file);
      setOcrResults(result.medications);
      setOcrStatus('completed');
    } catch (error) {
      console.error('OCR 분석 실패:', error);
      setOcrStatus('error');
    }
  };

  const getStatusText = () => {
    switch (ocrStatus) {
      case 'idle': return '대기중';
      case 'uploading': return '업로드 중...';
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
      setOcrResults([{
        name: manualInputData.name,
        dosage: manualInputData.dosage,
        frequency: manualInputData.usage || '',
        timing: manualInputData.timing || '',
      }]);
      setOcrStatus('completed');
      setShowManualInput(false);
      setManualInputData({ name: '', dosage: '', usage: '', timing: '' });
    }
  };

  const handleRetakePhoto = () => {
    setPreviewUrl(null);
    setSelectedImage(null);
    setOcrStatus('idle');
    setOcrResults(null);
    openCameraModal();
  };

  const openCameraModal = () => {
    setShowCameraModal(true);
    startCamera();
  };

  const startCamera = async () => {
    try {
      setCameraError(null);
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: 'environment',
          width: { ideal: 1920 },
          height: { ideal: 1080 }
        }
      });
      setCameraStream(stream);
    } catch (error) {
      console.error('카메라 접근 오류:', error);
      setCameraError('카메라에 접근할 수 없습니다. 권한을 확인해주세요.');
    }
  };

  const stopCamera = () => {
    if (cameraStream) {
      cameraStream.getTracks().forEach(track => track.stop());
      setCameraStream(null);
    }
  };

  const closeCameraModal = () => {
    stopCamera();
    setShowCameraModal(false);
    setCameraError(null);
  };

  const capturePhoto = () => {
    const video = document.getElementById('camera-video') as HTMLVideoElement;
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');

    if (video && context) {
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      context.drawImage(video, 0, 0);

      canvas.toBlob((blob) => {
        if (blob) {
          const file = new File([blob], 'camera-photo.jpg', { type: 'image/jpeg' });
          closeCameraModal();
          handleCapturedImage(file);
        }
      }, 'image/jpeg', 0.9);
    }
  };

  const handleChatSubmit = () => {
    if (chatMessage.trim()) {
      console.log('챗봇 메시지:', chatMessage);
      setChatMessage('');
    }
  };

  return (
    <div className="home-page">
      <div className="home-page__greeting">
        <h1 className="home-page__title">안녕하세요, {displayName}님 !</h1>
        <p className="home-page__subtitle">오늘도 건강한 하루 되세요 😊</p>
      </div>

      <div className="home-page__content">
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
                  <img src={previewUrl} alt="업로드된 처방전" className="home-page__preview-image" />
                  <div className="home-page__preview-overlay">
                    <button
                      onClick={handleRetakePhoto}
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
                <div>
                  <label htmlFor="prescription-upload" className="home-page__upload-label">
                    <div className="home-page__upload-icon">📷</div>
                    <p className="home-page__upload-text">
                      처방전 이미지를 업로드 하거나<br />
                      드래그 & 드롭하세요
                    </p>
                    <p className="home-page__upload-formats">JPG, PNG, PDF 최대 15MB</p>
                    <p className="home-page__upload-notice">💡 텍스트 인식은 밝기가 중요해요. 밝은 곳에서 촬영해주세요!</p>
                  </label>
                  <div className="home-page__camera-section">
                    <div className="home-page__divider"><span>또는</span></div>
                    <button onClick={openCameraModal} className="home-page__camera-btn" type="button">
                      📸 카메라로 촬영하기
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* OCR 결과 섹션 */}
          <div className="home-page__ocr-results">
            <h2 className="home-page__section-title">
              처방전 인식 결과 {ocrResults ? '✓' : ''}
            </h2>

            <div className="home-page__medicine-categories">
              {/* 약 목록 */}
              <div className="home-page__medicine-category">
                <h3 className="home-page__category-title home-page__category-title--blue">약 목록</h3>
                <div className="home-page__medicine-tags">
                  {ocrResults && ocrResults.length > 0 ? (
                    ocrResults.map((med, index) => (
                      <span key={index} className="home-page__medicine-tag home-page__medicine-tag--blue">
                        {med.name}{med.dosage ? ` ${med.dosage}` : ''}
                      </span>
                    ))
                  ) : (
                    <div className="home-page__empty-state">처방전을 업로드하면 약 목록이 표시됩니다</div>
                  )}
                </div>
              </div>

              {/* 복용법 */}
              <div className="home-page__medicine-category">
                <h3 className="home-page__category-title home-page__category-title--orange">복용법</h3>
                <div className="home-page__medicine-tags">
                  {ocrResults && ocrResults.length > 0 ? (
                    ocrResults.map((med, index) => (
                      <span key={index} className="home-page__medicine-tag home-page__medicine-tag--orange">
                        {med.name}: {med.frequency}{med.timing ? ` (${med.timing})` : ''}
                      </span>
                    ))
                  ) : (
                    <div className="home-page__empty-state">복용법이 표시됩니다</div>
                  )}
                </div>
              </div>

              {/* 상호작용 - 추후 연동 예정 */}
              <div className="home-page__medicine-category">
                <h3 className="home-page__category-title home-page__category-title--teal">상호작용</h3>
                <div className="home-page__medicine-tags">
                  <div className="home-page__empty-state">상호작용 정보가 표시됩니다</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* 챗봇 섹션 */}
        <div className="home-page__right">
          <div className="home-page__chatbot-section">
            <div className="home-page__chatbot-header">
              <div>
                <h2 className="home-page__section-title">🤖 약속이 상담소</h2>
                <p className="home-page__chatbot-ai-label">AI 기반 건강 상담 서비스</p>
              </div>
              {chatMessage.trim() && <span className="home-page__chatbot-status">답변 준비 중</span>}
            </div>
            <div className="home-page__chat-messages">
              <div className="home-page__chatbot-disclaimer">
                ⚠️ AI가 제공하는 정보는 참고용이며, 의료적 진단이나 치료를 대체하지 않습니다. 정확한 복약 상담은 전문 의료진과 상담해주세요.
              </div>
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
                <button onClick={handleChatSubmit} className="home-page__send-btn">전송</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 생활습관 가이드 섹션 */}
      <div className="home-page__lifestyle-guide">
        <h2 className="home-page__section-title">생활습관 가이드 💡</h2>
        <div className="home-page__guide-cards">
          <div className="home-page__guide-card home-page__guide-card--diet home-page__guide-card--coming-soon">
            <h3>식단 🍎</h3>
          </div>
          <div className="home-page__guide-card home-page__guide-card--exercise home-page__guide-card--coming-soon">
            <h3>운동🏃</h3>
          </div>
          <div className="home-page__guide-card home-page__guide-card--sleep home-page__guide-card--coming-soon">
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
              {ocrStatus === 'uploading' ? '이미지 업로드 중...' : 'OCR 처리 중...'}
            </h3>
            <p className="home-page__modal-subtitle">
              {ocrStatus === 'uploading' ? '잠시만 기다려주세요.' : '약물 정보를 추출하고 있습니다.'}
            </p>
          </div>
        </div>
      )}

      {/* OCR 실패 모달 */}
      {ocrStatus === 'error' && (
        <div className="home-page__modal-overlay">
          <div className="home-page__modal">
            <button onClick={() => setOcrStatus('idle')} className="home-page__modal-close">✕</button>
            <div className="home-page__error-icon"></div>
            <h3 className="home-page__modal-title home-page__modal-title--error">
              처방전 인식에 실패했습니다.
            </h3>
            <p className="home-page__modal-subtitle">
              이미지가 명확하지 않아 인식에 실패했습니다.<br />
              다시 촬영하거나 직접 입력해주세요.
            </p>
            <div className="home-page__modal-buttons">
              <button onClick={handleRetakePhoto} className="home-page__modal-btn home-page__modal-btn--primary">재촬영하기</button>
              <button onClick={() => setShowManualInput(true)} className="home-page__modal-btn home-page__modal-btn--secondary">수동입력</button>
            </div>
          </div>
        </div>
      )}

      {/* 수동 입력 모달 */}
      {showManualInput && (
        <div className="home-page__modal-overlay home-page__modal-overlay--light">
          <div className="home-page__modal home-page__modal--large">
            <div className="home-page__modal-header">
              <h3 className="home-page__modal-title">복용 정보 입력</h3>
              <button onClick={() => setShowManualInput(false)} className="home-page__modal-close">✕</button>
            </div>
            <div className="home-page__modal-form">
              <div className="home-page__form-group">
                <label>약 이름</label>
                <input type="text" placeholder="약 이름을 입력해주세요" value={manualInputData.name} onChange={(e) => setManualInputData({...manualInputData, name: e.target.value})} className="home-page__form-input" />
              </div>
              <div className="home-page__form-group">
                <label>용량</label>
                <input type="text" placeholder="ex) 500mg" value={manualInputData.dosage} onChange={(e) => setManualInputData({...manualInputData, dosage: e.target.value})} className="home-page__form-input" />
              </div>
              <div className="home-page__form-group">
                <label>복용법</label>
                <input type="text" placeholder="ex) 1일 3회" value={manualInputData.usage} onChange={(e) => setManualInputData({...manualInputData, usage: e.target.value})} className="home-page__form-input" />
              </div>
              <div className="home-page__form-group">
                <label>식후 ❓</label>
                <select value={manualInputData.timing} onChange={(e) => setManualInputData({...manualInputData, timing: e.target.value})} className="home-page__form-select">
                  <option value="">선택해주세요</option>
                  <option value="식전">식전</option>
                  <option value="식후">식후</option>
                  <option value="취침전">취침전</option>
                </select>
              </div>
            </div>
            <div className="home-page__modal-buttons">
              <button onClick={() => setShowManualInput(false)} className="home-page__modal-btn home-page__modal-btn--secondary">취소</button>
              <button onClick={handleManualInputSubmit} className="home-page__modal-btn home-page__modal-btn--primary" disabled={!manualInputData.name || !manualInputData.dosage}>확인</button>
            </div>
          </div>
        </div>
      )}

      {/* 카메라 촬영 모달 */}
      {showCameraModal && (
        <div className="home-page__modal-overlay">
          <div className="home-page__modal home-page__modal--camera">
            <div className="home-page__modal-header">
              <h3 className="home-page__modal-title">처방전 촬영</h3>
              <button onClick={closeCameraModal} className="home-page__modal-close">✕</button>
            </div>
            <div className="home-page__camera-container">
              {cameraError ? (
                <div className="home-page__camera-error">
                  <div className="home-page__error-icon-small">⚠️</div>
                  <p>{cameraError}</p>
                  <button onClick={startCamera} className="home-page__retry-btn">다시 시도</button>
                </div>
              ) : cameraStream ? (
                <div className="home-page__camera-preview">
                  <video
                    id="camera-video"
                    autoPlay
                    playsInline
                    muted
                    className="home-page__camera-video"
                    ref={(video) => {
                      if (video && cameraStream) {
                        video.srcObject = cameraStream;
                      }
                    }}
                  />
                  <div className="home-page__camera-overlay">
                    <div className="home-page__camera-frame"></div>
                    <p className="home-page__camera-guide">처방전을 프레임 안에 맞춰주세요</p>
                  </div>
                </div>
              ) : (
                <div className="home-page__camera-loading">
                  <div className="home-page__loading-spinner"></div>
                  <p>카메라를 준비하고 있습니다...</p>
                </div>
              )}
            </div>
            {cameraStream && !cameraError && (
              <div className="home-page__camera-controls">
                <button onClick={closeCameraModal} className="home-page__modal-btn home-page__modal-btn--secondary">취소</button>
                <button onClick={capturePhoto} className="home-page__camera-capture-btn">📸</button>
                <input
                  type="file"
                  id="camera-file-select"
                  accept="image/*,.pdf"
                  onChange={(e) => {
                    closeCameraModal();
                    handleImageUpload(e);
                  }}
                  style={{ display: 'none' }}
                />
                <label htmlFor="camera-file-select" className="home-page__modal-btn home-page__modal-btn--secondary">
                  사진 선택
                </label>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default HomePage;