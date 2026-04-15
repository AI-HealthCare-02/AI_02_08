import React, { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import apiClient from '../../api/apiClient';

const KakaoCallbackPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  useEffect(() => {
    const code = searchParams.get('code');

    if (!code) {
      alert('카카오 로그인에 실패했습니다.');
      navigate('/login');
      return;
    }

    const handleKakaoCallback = async () => {
      try {
        const response = await apiClient.get(`/auth/kakao/callback?code=${code}`);
        const { access_token } = response.data;

        localStorage.setItem('accessToken', access_token);
        window.location.href = '/home';
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