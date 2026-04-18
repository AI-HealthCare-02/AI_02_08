import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import apiClient from '../../api/apiClient';
import Modal from '../../components/common/Modal';
import TermsContent from '../auth/TermsContent';
import PrivacyContent from '../auth/PrivacyContent';
import './KakaoAdditionalInfoPage.css';
import bgLandingImage from '../../assets/images/bg-landing.png';

const KakaoAdditionalInfoPage: React.FC = () => {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [termsModalOpen, setTermsModalOpen] = useState(false);
  const [privacyModalOpen, setPrivacyModalOpen] = useState(false);
  const [formData, setFormData] = useState({
    gender: '',
    birthDate: '',
    phoneNumber: '',
    agreeTerms: false,
    agreePrivacy: false,
  });
  const [errors, setErrors] = useState<{ [key: string]: string }>({});
  const isSubmitted = useRef(false);

  useEffect(() => {
    const handleBeforeUnload = () => {
      if (!isSubmitted.current) {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('user');
      }
    };
    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, []);

  const validate = () => {
    const newErrors: { [key: string]: string } = {};
    if (!formData.gender) newErrors.gender = '성별을 선택해주세요.';
    if (!formData.birthDate) newErrors.birthDate = '생년월일을 입력해주세요.';
    if (!formData.phoneNumber) newErrors.phoneNumber = '전화번호를 입력해주세요.';
    const phoneRegex = /^010[0-9]{8}$|^010-[0-9]{4}-[0-9]{4}$/;
    if (formData.phoneNumber && !phoneRegex.test(formData.phoneNumber)) {
      newErrors.phoneNumber = '올바른 전화번호 형식이 아닙니다. (010XXXXXXXX 또는 010-XXXX-XXXX)';
    }
    if (!formData.agreeTerms) newErrors.agreeTerms = '이용약관에 동의해주세요.';
    if (!formData.agreePrivacy) newErrors.agreePrivacy = '개인정보 처리방침에 동의해주세요.';
    return newErrors;
  };

  const handleSubmit = async () => {
    const newErrors = validate();
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setIsLoading(true);
    try {
      await apiClient.patch('/auth/kakao/additional-info', {
        gender: formData.gender,
        birth_date: formData.birthDate,
        phone_number: formData.phoneNumber,
        agree_terms: formData.agreeTerms,
        agree_privacy: formData.agreePrivacy,
      });

      isSubmitted.current = true;
      localStorage.removeItem('user');
      alert('카카오 간편가입이 완료되었습니다! 환영합니다 🌿');
      window.location.href = '/home';
    } catch (error: any) {
      // 422 유효성 검증 에러 처리
      if (error.response?.status === 422) {
        const details = error.response?.data?.detail;
        if (Array.isArray(details)) {
          const newErrors: { [key: string]: string } = {};
          details.forEach((err: any) => {
            const field = err.loc?.[err.loc.length - 1];
            const message = err.msg;
            if (field === 'birth_date') {
              newErrors.birthDate = '만 14세 이상만 가입할 수 있습니다.';
            } else if (field === 'phone_number') {
              newErrors.phoneNumber = '올바른 전화번호 형식이 아닙니다.';
            } else if (field === 'gender') {
              newErrors.gender = '성별을 선택해주세요.';
            }
          });
          setErrors(newErrors);
        }
      } else {
        const message = error.response?.data?.detail || '추가 정보 저장에 실패했습니다.';
        alert(message);
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="kakao-additional__page">
      <div
        className="kakao-additional__background"
        style={{ backgroundImage: `url(${bgLandingImage})` }}
      >
        <div className="kakao-additional__background-overlay" />
      </div>

      <div className="kakao-additional__container">
        <div className="kakao-additional__card-line" />

        <div className="kakao-additional__header">
          <img src="/logo.png" alt="이루도담 로고" className="kakao-additional__logo" />
          <h1 className="kakao-additional__title">추가 정보 입력</h1>
          <p className="kakao-additional__subtitle">서비스 이용을 위해 추가 정보를 입력해주세요 🌿</p>
        </div>

        <div className="kakao-additional__form">
          <div className="kakao-additional__field">
            <label className="kakao-additional__label">성별</label>
            <select
              value={formData.gender}
              onChange={(e) => setFormData({ ...formData, gender: e.target.value })}
              className="kakao-additional__select"
            >
              <option value="">성별을 선택하세요</option>
              <option value="MALE">남성</option>
              <option value="FEMALE">여성</option>
            </select>
            {errors.gender && <p className="kakao-additional__error">{errors.gender}</p>}
          </div>

          <div className="kakao-additional__field">
            <label className="kakao-additional__label">생년월일 (만 14세 이상)</label>
            <input
              type="date"
              value={formData.birthDate}
              onChange={(e) => setFormData({ ...formData, birthDate: e.target.value })}
              className="kakao-additional__input"
              max={new Date().toISOString().split('T')[0]}
            />
            {errors.birthDate && <p className="kakao-additional__error">{errors.birthDate}</p>}
          </div>

          <div className="kakao-additional__field">
            <label className="kakao-additional__label">전화번호</label>
            <input
              type="tel"
              value={formData.phoneNumber}
              onChange={(e) => setFormData({ ...formData, phoneNumber: e.target.value })}
              placeholder="010XXXXXXXX 또는 010-XXXX-XXXX"
              className="kakao-additional__input"
            />
            {errors.phoneNumber && <p className="kakao-additional__error">{errors.phoneNumber}</p>}
          </div>

          <div className="kakao-additional__terms-section">
            <div className="kakao-additional__field">
              <div className="kakao-additional__terms-row">
                <label className="kakao-additional__checkbox">
                  <input
                    type="checkbox"
                    checked={formData.agreeTerms}
                    onChange={(e) => setFormData({ ...formData, agreeTerms: e.target.checked })}
                  />
                  이용약관에 동의합니다 (필수)
                </label>
                <button type="button" className="kakao-additional__terms-view" onClick={() => setTermsModalOpen(true)}>보기</button>
              </div>
              {errors.agreeTerms && <p className="kakao-additional__error">{errors.agreeTerms}</p>}
            </div>

            <div className="kakao-additional__field">
              <div className="kakao-additional__terms-row">
                <label className="kakao-additional__checkbox">
                  <input
                    type="checkbox"
                    checked={formData.agreePrivacy}
                    onChange={(e) => setFormData({ ...formData, agreePrivacy: e.target.checked })}
                  />
                  개인정보 처리방침에 동의합니다 (필수)
                </label>
                <button type="button" className="kakao-additional__terms-view" onClick={() => setPrivacyModalOpen(true)}>보기</button>
              </div>
              {errors.agreePrivacy && <p className="kakao-additional__error">{errors.agreePrivacy}</p>}
            </div>
          </div>

          <Modal isOpen={termsModalOpen} onClose={() => setTermsModalOpen(false)} title="이용약관" size="lg">
            <TermsContent />
          </Modal>

          <Modal isOpen={privacyModalOpen} onClose={() => setPrivacyModalOpen(false)} title="개인정보 처리방침" size="lg">
            <PrivacyContent />
          </Modal>

          <button
            onClick={handleSubmit}
            disabled={isLoading}
            className="kakao-additional__submit"
          >
            {isLoading ? '저장 중...' : '시작하기'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default KakaoAdditionalInfoPage;