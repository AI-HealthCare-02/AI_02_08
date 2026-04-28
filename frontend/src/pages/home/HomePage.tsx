import React, { useState, useEffect, useRef, memo } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { analyzePrescription, confirmPrescription, OcrMedicationItem } from '../../api/ocrApi';
import {
  createChatSession,
  getChatMessages,
  sendMessageAndGetAIResponse,
  updateChatSession,
  ChatMessage
} from '../../api/chatApi';
import {
  saveOcrResults, loadOcrResults,
  saveOcrStatus, loadOcrStatus,
  saveOcrPreview, loadOcrPreview,
  saveOcrId, loadOcrId,
  loadMedications, saveMedications,
  ocrToMedication
} from '../../utils/ocrStorage';
import yakssoriImg from '../../assets/images/yakssori.png';
import './HomePage.css';

// 접기/펼치기 파싱 함수
const parseCollapsibleContent = (content: string) => {
  const lines = content.split('\n');
  const result: Array<{ type: 'text' | 'collapsible'; content: string; title?: string }> = [];
  let currentText: string[] = [];
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];

    if (line.startsWith('▼ ')) {
      if (currentText.length > 0) {
        result.push({ type: 'text', content: currentText.join('\n') });
        currentText = [];
      }

      const title = line.substring(2).trim();
      const details: string[] = [];
      i++;
      while (i < lines.length && (lines[i].startsWith('  ') || lines[i] === '')) {
        if (lines[i].trim()) {
          details.push(lines[i].trim());
        }
        i++;
      }

      result.push({
        type: 'collapsible',
        title,
        content: details.join('\n')
      });
      continue;
    }

    currentText.push(line);
    i++;
  }

  if (currentText.length > 0) {
    result.push({ type: 'text', content: currentText.join('\n') });
  }

  return result;
};

// 접기/펼치기 아이템 컴포넌트
const CollapsibleItem: React.FC<{ title: string; content: string }> = ({ title, content }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div style={{ marginBottom: '8px' }}>
      <div
        onClick={() => setIsOpen(!isOpen)}
        style={{
          cursor: 'pointer',
          fontWeight: 'bold',
          padding: '8px',
          backgroundColor: '#f5f5f5',
          borderRadius: '4px',
          userSelect: 'none'
        }}
      >
        {isOpen ? '▼' : '▶'} {title}
      </div>
      {isOpen && (
        <div style={{ padding: '8px 16px', whiteSpace: 'pre-wrap' }}>
          {content}
        </div>
      )}
    </div>
  );
};

const ChatMessageItem = memo(({ msg }: { msg: ChatMessage }) => (
  <div className={`home-page__chat-message home-page__chat-message--${msg.sender === 'user' ? 'user' : 'bot'}`}>
    {msg.sender === 'user' ? (
      <div style={{ userSelect: 'text', WebkitUserSelect: 'text' }}>{msg.content}</div>
    ) : (
      parseCollapsibleContent(msg.content).map((item, idx) => (
        <React.Fragment key={idx}>
          {item.type === 'text' ? (
            <div style={{ whiteSpace: 'pre-wrap', userSelect: 'text', WebkitUserSelect: 'text' }}>{item.content}</div>
          ) : (
            <CollapsibleItem title={item.title!} content={item.content} />
          )}
        </React.Fragment>
      ))
    )}
  </div>
));

const HomePage: React.FC = () => {
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(loadOcrPreview());
  const [ocrStatus, setOcrStatus] = useState<'idle' | 'uploading' | 'processing' | 'completed' | 'partial_failure' | 'error'>(loadOcrStatus() as any || 'idle');
  const [ocrResults, setOcrResults] = useState<OcrMedicationItem[] | null>(loadOcrResults());
  const [ocrErrorMessage, setOcrErrorMessage] = useState<string>('');
  const [ocrId, setOcrId] = useState<string | null>(loadOcrId());
  const [addedToMedication, setAddedToMedication] = useState(false);
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

  // 챗봇 관련 state
  const [chatMessage, setChatMessage] = useState('');
  const [chatSessionId, setChatSessionId] = useState<number | null>(null);
  const chatSessionIdRef = useRef<number | null>(null);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [isChatLoading, setIsChatLoading] = useState(false);
  const chatMessagesRef = useRef<HTMLDivElement>(null);
  const [showScrollTop, setShowScrollTop] = useState(false);
  const [showFaq, setShowFaq] = useState(false);

  // 채팅 메시지 변경 시 자동 스크롤
  useEffect(() => {
    if (chatMessagesRef.current) {
      chatMessagesRef.current.scrollTop = chatMessagesRef.current.scrollHeight;
    }
  }, [chatMessages, isChatLoading]);

  const handleChatScroll = () => {
    if (chatMessagesRef.current) {
      const shouldShow = chatMessagesRef.current.scrollTop > 200;
      setShowScrollTop(prev => prev === shouldShow ? prev : shouldShow);
    }
  };

  const scrollToTop = () => {
    if (chatMessagesRef.current) {
      chatMessagesRef.current.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const { user } = useAuth();
  const displayName = user?.name || '사용자';

  // 컴포넌트 마운트 시 채팅 세션 생성
  useEffect(() => {
    const initChatSession = async () => {
      try {
        const savedOcrId = loadOcrId();
        const session = await createChatSession(savedOcrId || undefined);
        setChatSessionId(session.session_id);
        chatSessionIdRef.current = session.session_id;

        // 초기 메시지 로드
        const messages = await getChatMessages(session.session_id);
        setChatMessages(messages);
      } catch (error) {
        console.error('채팅 세션 생성 실패:', error);
      }
    };

    initChatSession();
  }, []);

  const MAX_FILE_SIZE = 5 * 1024 * 1024;
  const MAX_IMAGE_DIMENSION = 4096;
  const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'application/pdf'];

  const validateFile = (file: File): string | null => {
    if (!ALLOWED_TYPES.includes(file.type)) {
      return 'JPG, PNG, PDF 형식만 업로드 가능합니다.';
    }
    if (file.size > MAX_FILE_SIZE) {
      return '파일 크기는 5MB 이하만 가능합니다.';
    }
    return null;
  };

  const resizeImage = (file: File): Promise<File> => {
    return new Promise((resolve) => {
      if (file.type === 'application/pdf') {
        resolve(file);
        return;
      }
      const img = new Image();
      img.onload = () => {
        const { width, height } = img;
        if (width <= MAX_IMAGE_DIMENSION && height <= MAX_IMAGE_DIMENSION) {
          resolve(file);
          return;
        }
        const ratio = Math.min(MAX_IMAGE_DIMENSION / width, MAX_IMAGE_DIMENSION / height);
        const canvas = document.createElement('canvas');
        canvas.width = Math.round(width * ratio);
        canvas.height = Math.round(height * ratio);
        const ctx = canvas.getContext('2d')!;
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        canvas.toBlob((blob) => {
          if (blob) {
            resolve(new File([blob], file.name, { type: file.type }));
          } else {
            resolve(file);
          }
        }, file.type, 0.9);
      };
      img.src = URL.createObjectURL(file);
    });
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

    setOcrStatus('uploading');
    const resized = await resizeImage(file);
    setSelectedImage(resized);

    const reader = new FileReader();
    reader.onload = (e) => {
      const url = e.target?.result as string;
      setPreviewUrl(url);
      saveOcrPreview(url);
    };
    reader.readAsDataURL(resized);

    try {
      setOcrStatus('processing');
      setOcrErrorMessage('');
      const result = await analyzePrescription(resized);

      if (result.status === 'partial_failure' || !result.medications?.length) {
        setOcrResults([]);
        setOcrStatus('partial_failure');
      } else {
        setOcrResults(result.medications);
        setOcrId(result.ocrId);
        saveOcrResults(result.medications);
        saveOcrId(result.ocrId);
        // 챗봇 연결 완료 후에 completed 표시
        if (chatSessionIdRef.current) {
          try {
            await updateChatSession(chatSessionIdRef.current, result.ocrId);
          } catch (e) {
            console.error('OCR-챗봇 연결 실패:', e);
          }
        }
        setOcrStatus('completed');
        saveOcrStatus('completed');
      }
    } catch (err) {
      console.error('OCR 분석 실패:', err);
      setOcrErrorMessage(err instanceof Error ? err.message : '처방전 분석 중 오류가 발생했습니다.');
      setOcrStatus('error');
    }
  };

  const handleCapturedImage = async (file: File) => {
    const error = validateFile(file);
    if (error) {
      alert(error);
      return;
    }

    setOcrStatus('uploading');
    const resized = await resizeImage(file);
    setSelectedImage(resized);

    const reader = new FileReader();
    reader.onload = (e) => {
      const url = e.target?.result as string;
      setPreviewUrl(url);
      saveOcrPreview(url);
    };
    reader.readAsDataURL(resized);

    try {
      setOcrStatus('processing');
      setOcrErrorMessage('');
      const result = await analyzePrescription(resized);

      if (result.status === 'partial_failure' || !result.medications?.length) {
        setOcrResults([]);
        setOcrStatus('partial_failure');
      } else {
        setOcrResults(result.medications);
        setOcrId(result.ocrId);
        saveOcrResults(result.medications);
        saveOcrId(result.ocrId);
        if (chatSessionIdRef.current) {
          try {
            await updateChatSession(chatSessionIdRef.current, result.ocrId);
          } catch (e) {
            console.error('OCR-챗봇 연결 실패:', e);
          }
        }
        setOcrStatus('completed');
        saveOcrStatus('completed');
      }
    } catch (err) {
      console.error('OCR 분석 실패:', err);
      setOcrErrorMessage(err instanceof Error ? err.message : '처방전 분석 중 오류가 발생했습니다.');
      setOcrStatus('error');
    }
  };

  const getStatusText = () => {
    switch (ocrStatus) {
      case 'idle': return '대기중';
      case 'uploading': return '업로드 중...';
      case 'processing': return 'OCR 처리 중...';
      case 'completed': return '분석완료 ✓';
      case 'partial_failure': return '부분 인식 ⚠';
      case 'error': return '오류 발생';
      default: return '대기중';
    }
  };

  const getStatusColor = () => {
    switch (ocrStatus) {
      case 'idle': return '#8B7355';
      case 'uploading': return '#6B5E4E';
      case 'processing': return '#B8860B';
      case 'completed': return '#8B7355';
      case 'partial_failure': return '#B8860B';
      case 'error': return '#A0522D';
      default: return '#8B7355';
    }
  };

  const handleManualInputSubmit = () => {
    if (manualInputData.name && manualInputData.dosage) {
      const results: OcrMedicationItem[] = [{
        name: manualInputData.name,
        dosage: manualInputData.dosage,
        frequency: manualInputData.usage || '',
        timing: manualInputData.timing || '',
      }];
      setOcrResults(results);
      setOcrStatus('completed');
      saveOcrResults(results);
      saveOcrStatus('completed');
      setShowManualInput(false);
      setManualInputData({ name: '', dosage: '', usage: '', timing: '' });
    }
  };

  const handleClearPrescription = () => {
    setPreviewUrl(null);
    setSelectedImage(null);
    setOcrStatus('idle');
    setOcrResults(null);
    setOcrErrorMessage('');
    setAddedToMedication(false);
    saveOcrStatus('idle');
    sessionStorage.removeItem('ocr_results');
    sessionStorage.removeItem('ocr_preview');
  };

  const handleRetakePhoto = () => {
    handleClearPrescription();
    openCameraModal();
  };

  const handleAddToMedication = async () => {
    if (!ocrResults?.length) return;
    try {
      if (ocrId) {
        await confirmPrescription(ocrId, ocrResults);
      }
      const existing = loadMedications();
      const newMeds = ocrResults.map(ocrToMedication);
      saveMedications([...existing, ...newMeds]);
      setAddedToMedication(true);
    } catch (error) {
      console.error('복약관리 추가 실패:', error);
      alert('복약관리 추가 중 오류가 발생했습니다.');
    }
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

  // 챗봇 메시지 전송 함수
  const handleChatSubmit = async () => {
    if (!chatMessage.trim() || !chatSessionId || isChatLoading) return;

    const userMessageText = chatMessage.trim();
    setChatMessage('');
    setIsChatLoading(true);

    // 사용자 메시지 UI에 즉시 표시
    const tempUserMessage: ChatMessage = {
      message_id: Date.now(), // 임시 ID
      session_id: chatSessionId,
      sender: 'user',
      content: userMessageText,
      is_faq: false,
      created_at: new Date().toISOString(),
    };
    setChatMessages(prev => [...prev, tempUserMessage]);

    try {
      // AI 응답 받기
      const aiMessage = await sendMessageAndGetAIResponse(chatSessionId, userMessageText);

      // AI 응답 추가
      setChatMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('챗봇 응답 실패:', error);

      // 에러 메시지 표시
      const errorMessage: ChatMessage = {
        message_id: Date.now(),
        session_id: chatSessionId,
        sender: 'assistant',
        content: '죄송합니다. 일시적인 오류가 발생했습니다. 다시 시도해주세요.',
        is_faq: false,
        created_at: new Date().toISOString(),
      };
      setChatMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsChatLoading(false);
    }
  };

  // 추천 질문 클릭 핸들러
  // handleSuggestionClick 함수 수정
  const handleSuggestionClick = async (suggestion: string) => {
    setChatMessage('');
    setShowFaq(false);
    if (!chatSessionId || isChatLoading) return;

    setIsChatLoading(true);
    const tempUserMessage: ChatMessage = {
      message_id: Date.now(),
      session_id: chatSessionId,
      sender: 'user',
      content: suggestion,
      is_faq: true,
      created_at: new Date().toISOString(),
    };
    setChatMessages(prev => [...prev, tempUserMessage]);

    try {
      const aiMessage = await sendMessageAndGetAIResponse(
        chatSessionId,
        suggestion,
        true
      );

      // 🔍 디버깅: 실제 응답 출력
      console.log('=== AI 응답 원본 ===');
      console.log('content:', aiMessage.content);
      console.log('content type:', typeof aiMessage.content);
      console.log('includes ▼:', aiMessage.content.includes('▼'));
      console.log('split by \\n:', aiMessage.content.split('\n').length);
      console.log('첫 100자:', aiMessage.content.substring(0, 100));

      setChatMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      // ... 에러 처리
    } finally {
      setIsChatLoading(false);
    }
  };

  return (
    <div className="home-page">
      <div className="home-page__greeting">
        <h1 className="home-page__title">안녕하세요, {displayName}님 !</h1>
        <p className="home-page__subtitle">이루도담과 함께 건강을 관리하세요🌿</p>
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
                      onClick={handleClearPrescription}
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
                    <p className="home-page__upload-formats">JPG, PNG, PDF 최대 5MB (4096x4096px 자동 리사이즈)</p>
                    <p className="home-page__upload-notice">💡 텍스트 인식은 밝기가 중요해요. 밝은 곳에서 촬영해주세요!</p>
                  </label>
                  <div className="home-page__camera-section">
                    <div className="home-page__divider"><span>또는</span></div>
                    <div className="home-page__camera-buttons">
                      <button onClick={openCameraModal} className="home-page__camera-btn" type="button">
                        📸 카메라로 촬영하기
                      </button>
                      <label htmlFor="prescription-upload" className="home-page__camera-btn home-page__camera-btn--select">
                        사진 선택하기
                      </label>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* OCR 결과 섹션 */}
          <div className="home-page__ocr-results">
            <div className="home-page__ocr-results-header">
              <h2 className="home-page__section-title">
                처방전 인식 결과 {ocrResults ? '✓' : ''}
              </h2>
              {ocrResults && ocrResults.length > 0 && (
                <button
                  onClick={handleAddToMedication}
                  className={`home-page__add-medication-btn-sm ${addedToMedication ? 'home-page__add-medication-btn-sm--done' : ''}`}
                  disabled={addedToMedication}
                >
                  {addedToMedication ? '✓ 추가됨' : '복약관리에 추가'}
                </button>
              )}
            </div>

            <div className="home-page__medicine-categories">
              {/* 약 목록 */}
              <div className="home-page__medicine-category">
                <h3 className="home-page__category-title home-page__category-title--blue">약 목록</h3>
                <div className="home-page__medicine-tags">
                  {ocrResults && ocrResults.length > 0 ? (
                    <>
                      {ocrResults.map((med, index) => (
                        <span key={index} className="home-page__medicine-tag home-page__medicine-tag--blue">
                          {med.name}{med.dosage ? ` ${med.dosage}` : ''}
                        </span>
                      ))}
                    </>
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


            </div>
          </div>
        </div>

        {/* 챗봇 섹션 */}
        <div className="home-page__right" id="chatbot-section">
          <div className="home-page__chatbot-section">
            <div className="home-page__chatbot-header">
              <div className="home-page__chatbot-title-row">
                <img src={yakssoriImg} alt="약속이" className="home-page__chatbot-icon" />
                <div>
                  <h2 className="home-page__section-title">약속이 상담소</h2>
                  <p className="home-page__chatbot-ai-label">AI 기반 건강 상담 서비스</p>
                </div>
              </div>
              {isChatLoading && <span className="home-page__chatbot-status">답변 준비 중...</span>}
            </div>

            <div className="home-page__chatbot-disclaimer">
              ⚠️ AI가 제공하는 정보는 참고용이며, 의료적 진단이나 치료를 대체하지 않습니다. 정확한 복약 상담은 전문 의료진과 상담해주세요.
            </div>

            <div className="home-page__chat-messages" ref={chatMessagesRef} onScroll={handleChatScroll}>

              {/* 실제 채팅 메시지 렌더링 */}
              {chatMessages.length === 0 ? (
                <div className="home-page__chat-message home-page__chat-message--bot">
                  안녕하세요! 복약 관련 궁금한 점을 물어보세요
                </div>
              ) : (
                chatMessages.map((msg) => (
                  <ChatMessageItem key={msg.message_id} msg={msg} />
                ))
              )}

              {/* 로딩 표시 */}
              {isChatLoading && (
                <div className="home-page__chat-message home-page__chat-message--bot">
                  <div className="home-page__typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              )}

              {showScrollTop && (
                <span />
              )}
            </div>

            <div className="home-page__faq-wrapper">
              {showScrollTop && (
                <button onClick={scrollToTop} className="home-page__scroll-top-btn">
                  <img src="/arrow.png" alt="맨 위로" className="home-page__scroll-top-icon" />
                  <span className="home-page__scroll-top-tooltip">맨 위로</span>
                </button>
              )}
              <button
                className={`home-page__faq-bubble ${showFaq ? 'home-page__faq-bubble--active' : ''}`}
                onClick={() => setShowFaq(!showFaq)}
              >
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
                  <ellipse cx="12" cy="11" rx="9" ry="8"/>
                  <path d="M17 17.5C17 17.5 19.5 19.5 21 20c-1-0.5-2.5-1-3.5-3"/>
                </svg>
                <span className="home-page__faq-tooltip">자주 묻는 질문</span>
              </button>
              {showFaq && (
                <div className="home-page__faq-popup">
                  <button className="home-page__faq-item" onClick={() => handleSuggestionClick('부작용이 있나요?')}>부작용이 있나요?</button>
                  <button className="home-page__faq-item" onClick={() => handleSuggestionClick('주의사항 알려주세요')}>주의사항 알려주세요</button>
                  <button className="home-page__faq-item" onClick={() => handleSuggestionClick('다른 약과 같이 먹어도 되나요?')}>다른 약과 같이 먹어도 되나요?</button>
                </div>
              )}
            </div>

            <div className="home-page__chat-input-area">
              <div className="home-page__chat-input-wrapper">
                <input
                  type="text"
                  value={chatMessage}
                  onChange={(e) => setChatMessage(e.target.value)}
                  placeholder={ocrResults ? '궁금한 내용을 물어보세요' : '처방전을 먼저 인식해주세요'}
                  className="home-page__chat-input"
                  onKeyPress={(e) => e.key === 'Enter' && !isChatLoading && ocrResults && handleChatSubmit()}
                  disabled={isChatLoading || !ocrResults}
                />
                <button
                  onClick={handleChatSubmit}
                  className={`home-page__send-btn ${ocrResults && !isChatLoading ? 'home-page__send-btn--ready' : ''}`}
                  disabled={!chatMessage.trim() || isChatLoading || !ocrResults}
                >
                  {isChatLoading ? '...' : '전송'}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>



      {/* OCR 처리 모달 */}
      {(ocrStatus === 'uploading' || ocrStatus === 'processing') && (
        <div className="home-page__modal-overlay">
          <div className="home-page__modal">
            <div className="home-page__loading-spinner"></div>
            <h3 className="home-page__modal-title">
              {ocrStatus === 'uploading' ? '이미지 업로드 중...' : '처방전 분석 중...'}
            </h3>
            <p className="home-page__modal-subtitle">
              {ocrStatus === 'uploading'
                ? '잠시만 기다려주세요.'
                : '약물 정보를 추출하고 있습니다. 잠시만 기다려주세요 😊'}
            </p>
          </div>
        </div>
      )}

      {/* OCR 부분 실패 모달 (partial_failure) */}
      {ocrStatus === 'partial_failure' && (
        <div className="home-page__modal-overlay">
          <div className="home-page__modal">
            <button onClick={() => setOcrStatus('idle')} className="home-page__modal-close">✕</button>
            <div className="home-page__error-icon"></div>
            <h3 className="home-page__modal-title home-page__modal-title--warning">
              처방전에서 약물 정보를 찾지 못했습니다.
            </h3>
            <p className="home-page__modal-subtitle">
              이미지가 흐리거나 처방전 형식이 아닐 수 있습니다.<br />
              더 선명한 이미지로 다시 시도하거나, 직접 입력해주세요.
            </p>
            <div className="home-page__modal-buttons">
              <button onClick={handleRetakePhoto} className="home-page__modal-btn home-page__modal-btn--primary">다시 찍기</button>
              <button onClick={() => { setOcrStatus('idle'); setShowManualInput(true); }} className="home-page__modal-btn home-page__modal-btn--secondary">직접 입력하기</button>
            </div>
          </div>
        </div>
      )}

      {/* OCR 실패 모달 (서버 에러) */}
      {ocrStatus === 'error' && (
        <div className="home-page__modal-overlay">
          <div className="home-page__modal">
            <button onClick={() => { setOcrStatus('idle'); setOcrErrorMessage(''); }} className="home-page__modal-close">✕</button>
            <div className="home-page__error-icon"></div>
            <h3 className="home-page__modal-title home-page__modal-title--error">
              처방전 인식에 실패했습니다.
            </h3>
            <p className="home-page__modal-subtitle">
              {ocrErrorMessage || '알 수 없는 오류가 발생했습니다.'}
            </p>
            <div className="home-page__modal-buttons">
              <button onClick={handleRetakePhoto} className="home-page__modal-btn home-page__modal-btn--primary">다시 찍기</button>
              <button onClick={() => { setOcrStatus('idle'); setOcrErrorMessage(''); setShowManualInput(true); }} className="home-page__modal-btn home-page__modal-btn--secondary">직접 입력하기</button>
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

      {/* 모바일 챗봇 플로팅 버튼 */}
      <button
        className="home-page__chatbot-fab"
        onClick={() => document.getElementById('chatbot-section')?.scrollIntoView({ behavior: 'smooth' })}
      >
        <img src={yakssoriImg} alt="약속이" className="home-page__chatbot-fab-img" />
      </button>
    </div>
  );
};

export default HomePage;