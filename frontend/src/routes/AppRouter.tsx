import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import MainLayout from '../components/layout/MainLayout';
import ProtectedRoute from '../components/common/ProtectedRoute';
import { useAuth } from '../hooks/useAuth';

import HomePage from '../pages/home/HomePage';
import LandingPage from '../pages/home/LandingPage';
import LoginPage from '../pages/auth/LoginPage';
import SignupPage from '../pages/auth/SignupPage';
import ForgotPasswordPage from '../pages/auth/ForgotPasswordPage';
import KakaoCallbackPage from '../pages/auth/KakaoCallbackPage';
import KakaoAdditionalInfoPage from '../pages/auth/KakaoAdditionalInfoPage';
import MyPage from '../pages/mypage/MyPage';
import TermsAgreementPage from '../pages/auth/TermsAgreementPage';

const AppRoutes: React.FC = () => {
  const { isLoggedIn } = useAuth();

  return (
    <Routes>
      <Route
        path="/"
        element={
          isLoggedIn ? (
            <Navigate to="/home" replace />
          ) : (
            <MainLayout>
              <LandingPage />
            </MainLayout>
          )
        }
      />

      <Route
        path="/home"
        element={
          <ProtectedRoute>
            <MainLayout>
              <HomePage />
            </MainLayout>
          </ProtectedRoute>
        }
      />

      <Route
        path="/mypage"
        element={
          <ProtectedRoute>
            <MainLayout>
              <MyPage />
            </MainLayout>
          </ProtectedRoute>
        }
      />

      <Route
        path="/login"
        element={
          isLoggedIn ? (
            <Navigate to="/home" replace />
          ) : (
            <MainLayout>
              <LoginPage />
            </MainLayout>
          )
        }
      />

      <Route
        path="/signup"
        element={
          isLoggedIn ? (
            <Navigate to="/home" replace />
          ) : (
            <MainLayout>
              <SignupPage />
            </MainLayout>
          )
        }
      />

      <Route
        path="/forgot-password"
        element={
          <MainLayout>
            <ForgotPasswordPage />
          </MainLayout>
        }
      />

      <Route
        path="/auth/kakao/callback"
        element={<KakaoCallbackPage />}
      />


      <Route path="/terms-agreement" element={<TermsAgreementPage />} />

      <Route
        path="/auth/kakao/additional-info"
        element={<KakaoAdditionalInfoPage />}
      />

      <Route
        path="*"
        element={
          <MainLayout>
            <div style={{ textAlign: 'center', padding: '2rem' }}>
              <h2>404 - Page Not Found</h2>
              <p>The page you requested does not exist.</p>
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