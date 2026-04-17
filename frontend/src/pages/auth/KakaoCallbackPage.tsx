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
        const { access_token, is_new } = response.data;
        localStorage.setItem('accessToken', access_token);

        if (is_new) {
          // 신규 가입 또는 탈퇴 후 재가입 → 추가 정보 입력 페이지로 이동
          window.location.href = '/auth/kakao/additional-info';
        } else {
          // 기존 유저 → 바로 홈으로 이동
          window.location.href = '/home';
        }
      } catch (error) {
        console.error('카카오 로그인 실패:', error);
        alert('카카오 로그인에 실패했습니다.');
        navigate('/login');
      }
    };

    handleKakaoCallback();
  }, []);

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