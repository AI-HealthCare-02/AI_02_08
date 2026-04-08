import React from 'react';
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

  // 디버깅용 로그
  console.log('MainLayout - isLoggedIn:', isLoggedIn);
  console.log('MainLayout - user:', user);

  const userProfile = user ? {
    name: user.name,
    avatar: user.avatar
  } : undefined;

  const handleLogin = () => {
    navigate('/login');
  };

  const handleSignup = () => {
    navigate('/signup');
  };

  const handleLogout = () => {
    logout();
    navigate('/landing');
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
    </div>
  );
};

export default MainLayout;