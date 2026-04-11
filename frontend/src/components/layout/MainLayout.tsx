import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import Navbar from './Navbar';
import './MainLayout.css';

interface MainLayoutProps {
  children: React.ReactNode;
  showNavbar?: boolean;
}

const MainLayout: React.FC<MainLayoutProps> = ({
  children,
  showNavbar = true
}) => {
  const navigate = useNavigate();
  const { isLoggedIn, user, logout } = useAuth();
  const [showLogoutModal, setShowLogoutModal] = useState(false);

  const userProfile = user ? {
    name: user.name,
    avatar: user.avatar
  } : undefined;

  const handleLogin = () => navigate('/login');
  const handleSignup = () => navigate('/signup');

  const handleLogout = () => {
    setShowLogoutModal(true);
  };

  const confirmLogout = () => {
    setShowLogoutModal(false);
    logout();
    window.location.href = '/';
  };

  return (
    <div className="main-layout">
      {showNavbar && (
        <Navbar
          isLoggedIn={isLoggedIn}
          userProfile={userProfile}
          onLogin={handleLogin}
          onSignup={handleSignup}
          onLogout={handleLogout}
        />
      )}

      <main className="main-layout__content">
        {children}
      </main>

      {/* 로그아웃 확인 모달 */}
      {showLogoutModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
        }}>
          <div style={{
            backgroundColor: 'white',
            borderRadius: '16px',
            padding: '32px',
            width: '320px',
            textAlign: 'center',
            boxShadow: '0 4px 20px rgba(0,0,0,0.15)',
          }}>
            <h3 style={{ marginBottom: '8px', fontSize: '18px', fontWeight: '600' }}>
              로그아웃
            </h3>
            <p style={{ marginBottom: '24px', color: '#666', fontSize: '14px' }}>
              정말 로그아웃 하시겠습니까?
            </p>
            <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
              <button
                onClick={() => setShowLogoutModal(false)}
                style={{
                  flex: 1,
                  padding: '12px',
                  borderRadius: '8px',
                  border: '1px solid #ddd',
                  backgroundColor: 'white',
                  cursor: 'pointer',
                  fontSize: '14px',
                }}
              >
                취소
              </button>
              <button
                onClick={confirmLogout}
                style={{
                  flex: 1,
                  padding: '12px',
                  borderRadius: '8px',
                  border: 'none',
                  backgroundColor: '#78a085',
                  color: 'white',
                  cursor: 'pointer',
                  fontSize: '14px',
                }}
              >
                로그아웃
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MainLayout;