import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { isLoggedIn, user } = useAuth();

  if (!isLoggedIn) {
    return <Navigate to="/" replace />;
  }

  // 카카오 로그인 후 추가 정보 미입력 유저 → 추가 정보 입력 페이지로 강제 이동
  if (user && !user.agreeTerms) {
    return <Navigate to="/auth/kakao/additional-info" replace />;
  }

  return <>{children}</>;
};

export default ProtectedRoute;