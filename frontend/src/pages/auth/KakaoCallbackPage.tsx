import React, { useEffect, useRef } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import apiClient from '../../api/apiClient';

const KakaoCallbackPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const hasRun = useRef(false);

  useEffect(() => {
    if (hasRun.current) return;
    hasRun.current = true;

    const code = searchParams.get('code');

    if (!code) {
      alert('카카오 로그인에 실패했습니다.');
      navigate('/login');
      return;
    }

    const handleKakaoCallback = async () => {
      try {
        const response = await apiClient.get(`/auth/kakao/callback?code=${code}`);
        const {
          access_token,
          requires_terms_agreement,
          requires_additional_info
        } = response.data;

        localStorage.setItem('accessToken', access_token);

        // 1단계: 약관 동의 필요?
        if (requires_terms_agreement) {
          navigate('/terms-agreement');
        }
        // 2단계: 추가 정보 입력 필요?
        else if (requires_additional_info) {
          navigate('/auth/kakao/additional-info');
        }
        // 완료: 홈으로
        else {
          window.location.href = '/home';
        }
      } catch (error) {
        console.error('카카오 로그인 실패:', error);
        alert('카카오 로그인에 실패했습니다.');
        navigate('/login');
      }
    };

    handleKakaoCallback();
  }, [navigate, searchParams]);

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      height: '100vh',
      gap: '16px',
    }}>
      <p style={{ fontSize: '16px', color: '#666' }}>카카오 로그인 처리 중...</p>
    </div>
  );
};

export default KakaoCallbackPage;