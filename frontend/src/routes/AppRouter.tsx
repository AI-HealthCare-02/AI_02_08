import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import MainLayout from '../components/layout/MainLayout';
import ProtectedRoute from '../components/common/ProtectedRoute';

// 페이지 컴포넌트 import
import HomePage from '../pages/home/HomePage';
import LandingPage from '../pages/home/LandingPage';
import LoginPage from '../pages/auth/LoginPage';
import SignupPage from '../pages/auth/SignupPage';

const AppRoutes: React.FC = () => {
  return (
    <Routes>
      {/* 홈 페이지 (메인 화면) - 임시로 로그인 없이 접근 가능 */}
      <Route 
        path="/" 
        element={
          <MainLayout>
            <HomePage />
          </MainLayout>
        } 
      />
      
      {/* 랜딩 페이지 (로고 클릭 시) */}
      <Route 
        path="/landing" 
        element={
          <MainLayout>
            <LandingPage />
          </MainLayout>
        } 
      />
      
      {/* 복약관리 페이지 - 로그인 필요 */}
      <Route 
        path="/medication" 
        element={
          <ProtectedRoute>
            <MainLayout>
              <div style={{ padding: '2rem' }}>
                <h1>복약관리</h1>
                <p>복약관리 페이지입니다. (3주차에 구현 예정)</p>
              </div>
            </MainLayout>
          </ProtectedRoute>
        } 
      />
      
      {/* 마이페이지 - 로그인 필요 */}
      <Route 
        path="/mypage" 
        element={
          <ProtectedRoute>
            <MainLayout>
              <div style={{ padding: '2rem' }}>
                <h1>마이페이지</h1>
                <p>마이페이지입니다. (3주차에 구현 예정)</p>
              </div>
            </MainLayout>
          </ProtectedRoute>
        } 
      />
      
      {/* 인증 관련 페이지 (네비게이션 포함) */}
      <Route 
        path="/login" 
        element={
          <MainLayout>
            <LoginPage />
          </MainLayout>
        } 
      />
      <Route 
        path="/signup" 
        element={
          <MainLayout>
            <SignupPage />
          </MainLayout>
        } 
      />
      
      {/* 404 페이지 */}
      <Route 
        path="*" 
        element={
          <MainLayout>
            <div style={{ textAlign: 'center', padding: '2rem' }}>
              <h2>404 - 페이지를 찾을 수 없습니다</h2>
              <p>요청하신 페이지가 존재하지 않습니다.</p>
            </div>
          </MainLayout>
        } 
      />
    </Routes>
  );
};

const AppRouter: React.FC = () => {
  return (
    <BrowserRouter>
      <AppRoutes />
    </BrowserRouter>
  );
};

export default AppRouter;