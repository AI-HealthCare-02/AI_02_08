import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import './Navbar.css';

interface NavbarProps {
  isLoggedIn?: boolean;
  userProfile?: {
    name: string;
    avatar?: string;
  };
  onLogin?: () => void;
  onSignup?: () => void;
  onLogout?: () => void;
}

const Navbar: React.FC<NavbarProps> = ({
  onLogin,
  onSignup,
  onLogout
}) => {
  const location = useLocation();
  const { isLoggedIn, user } = useAuth();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  // 로그아웃 핸들러
  const handleLogout = () => {
  if (onLogout) {
    onLogout();
  }
};

  const isActive = (path: string) => {
    return location.pathname === path;
  };

  // 현재 페이지가 로그인/회원가입/비밀번호 재설정 페이지인지 확인
  const isAuthPage = location.pathname === '/login' || location.pathname === '/signup' || location.pathname === '/forgot-password';

  return (
    <nav className="navbar">
      <div className="navbar__container">
        {/* 로고 - 항상 표시 */}
        <Link to="/" className="navbar__logo">
          <img 
            src="/logo.png" 
            alt="이루도담" 
            className="navbar__logo-image"
          />
        </Link>

        {/* 네비게이션 메뉴 - 로그인 상태에 따라 다르게 표시 */}
        <div className={`navbar__nav ${isMobileMenuOpen ? 'navbar__nav--mobile-open' : ''}`}>
          {isLoggedIn ? (
            // 로그인 후 메뉴
            <>
              <Link 
                to="/home" 
                className={`navbar__nav-item ${isActive('/home') ? 'navbar__nav-item--active' : ''}`}
                onClick={() => setIsMobileMenuOpen(false)}
              >
                홈
              </Link>
              <Link 
                to="/medication" 
                className={`navbar__nav-item ${isActive('/medication') ? 'navbar__nav-item--active' : ''}`}
                onClick={() => setIsMobileMenuOpen(false)}
              >
                복약관리
              </Link>
              <Link 
                to="/mypage" 
                className={`navbar__nav-item ${isActive('/mypage') ? 'navbar__nav-item--active' : ''}`}
                onClick={() => setIsMobileMenuOpen(false)}
              >
                마이페이지
              </Link>
            </>
          ) : (
            // 로그인 전 메뉴
            <>
              <Link 
                to="/" 
                className={`navbar__nav-item ${isActive('/') ? 'navbar__nav-item--active' : ''}`}
                onClick={() => setIsMobileMenuOpen(false)}
              >
                홈
              </Link>
            </>
          )}
        </div>

        {/* 모바일 햄버거 메뉴 */}
        <button 
          className="navbar__mobile-toggle"
          onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          aria-label="메뉴 토글"
        >
          <span className={`navbar__hamburger ${isMobileMenuOpen ? 'navbar__hamburger--open' : ''}`}>
            <span></span>
            <span></span>
            <span></span>
          </span>
        </button>

        {/* 우측 액션 버튼 */}
        <div className="navbar__actions">
          {isLoggedIn && !isAuthPage ? (
            // 로그인 후 - 사용자 아이콘 + 로그아웃 버튼 (인증 페이지에서는 숨김)
            <div className="navbar__user">
              <div className="navbar__user-avatar">
                {user?.profileImage ? (
                  <img 
                    src={user.profileImage} 
                    alt="프로필" 
                    className="navbar__user-avatar-image"
                    style={{
                      width: '36px',
                      height: '36px',
                      borderRadius: '50%',
                      objectFit: 'cover'
                    }}
                  />
                ) : (
                  <div 
                    className="navbar__user-avatar-default"
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '16px',
                      fontWeight: 'bold',
                      color: 'white',
                      backgroundColor: '#78a085',
                      width: '36px',
                      height: '36px',
                      borderRadius: '50%'
                    }}
                  >
                    {(user?.nickname || user?.name)?.charAt(0).toUpperCase() || 'U'}
                  </div>
                )}
              </div>
              <span className="navbar__user-name">
                {user?.nickname || user?.name || '사용자'}님
              </span>
              <button 
                onClick={handleLogout}
                className="navbar__button navbar__button--secondary"
              >
                로그아웃
              </button>
            </div>
          ) : (
            // 로그인 전 - 로그인/회원가입 버튼 (인증 페이지에서는 숨김)
            !isAuthPage && (
              <div className="navbar__auth">
                <button 
                  onClick={onLogin}
                  className="navbar__button navbar__button--secondary"
                >
                  로그인
                </button>
                <button 
                  onClick={onSignup}
                  className="navbar__button navbar__button--primary"
                >
                  회원가입
                </button>
              </div>
            )
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;