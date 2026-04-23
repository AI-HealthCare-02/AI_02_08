import React, { useState, useEffect } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { useSearchParams } from 'react-router-dom';
import { useToast } from '../../contexts/ToastContext';
import { changePassword, deleteAccount, updateUserInfo } from '../../api/authApi';
import './MyPage.css';

type TabType = 'profile' | 'report' | 'history' | 'account';

const MyPage: React.FC = () => {
  const { user, logout, setUser, setIsLoggedIn } = useAuth();
  const [searchParams] = useSearchParams();
  const { showToast } = useToast();
  const [activeTab, setActiveTab] = useState<TabType>('profile');
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showProfileEditModal, setShowProfileEditModal] = useState(false);

  useEffect(() => {
    const tab = searchParams.get('tab') as TabType;
    if (tab && ['profile', 'report', 'history', 'account'].includes(tab)) {
      setActiveTab(tab);
    }
  }, [searchParams]);

  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });
  const [showCurrentPw, setShowCurrentPw] = useState(false);
  const [showNewPw, setShowNewPw] = useState(false);
  const [showConfirmPw, setShowConfirmPw] = useState(false);

  const togglePwVisibility = (setter: React.Dispatch<React.SetStateAction<boolean>>) => {
    setter(true);
    setTimeout(() => setter(false), 1000);
  };

  const [profileData, setProfileData] = useState({
    name: user?.name || '',
    email: user?.email || '',
    phone: user?.phoneNumber || '',
    birthDate: user?.birthday || '',
    gender: user?.gender || '',
    profileImage: user?.profileImage || ''
  });

  React.useEffect(() => {
    setProfileData({
      name: user?.name || '',
      email: user?.email || '',
      phone: user?.phoneNumber || '',
      birthDate: user?.birthday || '',
      gender: user?.gender || '',
      profileImage: user?.profileImage || ''
    });
  }, [user]);

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const imageUrl = e.target?.result as string;
        setProfileData({...profileData, profileImage: imageUrl});
      };
      reader.readAsDataURL(file);
    }
  };

  const handleImageRemove = () => {
    setProfileData({...profileData, profileImage: ''});
  };

  const handlePasswordChange = async () => {
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      showToast({
        type: 'error',
        title: '비밀번호 불일치',
        message: '새 비밀번호가 일치하지 않습니다.',
      });
      return;
    }

    try {
      await changePassword(
        passwordData.currentPassword,
        passwordData.newPassword,
        passwordData.confirmPassword,
      );
      setPasswordData({ currentPassword: '', newPassword: '', confirmPassword: '' });
      setShowPasswordModal(false);
      showToast({
        type: 'success',
        title: '비밀번호 변경 완료',
        message: '비밀번호가 성공적으로 변경되었습니다.',
      });
    } catch (error: any) {
      const message = error.response?.data?.detail || '비밀번호 변경에 실패했습니다.';
      showToast({
        type: 'error',
        title: '비밀번호 변경 실패',
        message,
      });
    }
  };

  const handleProfileUpdate = async () => {
    try {
      const updateData: {
        name?: string;
        phone_number?: string;
        birth_date?: string;
        gender?: string;
        profile_image?: string;
      } = {};

      if (profileData.name && profileData.name !== user?.name) {
        updateData.name = profileData.name;
      }
      if (profileData.phone && profileData.phone !== user?.phoneNumber) {
        updateData.phone_number = profileData.phone;
      }
      if (profileData.birthDate && profileData.birthDate !== user?.birthday) {
        updateData.birth_date = profileData.birthDate;
      }
      if (profileData.gender && profileData.gender !== user?.gender) {
        updateData.gender = profileData.gender;
      }
      if (profileData.profileImage !== user?.profileImage) {
        updateData.profile_image = profileData.profileImage;
      }

      await updateUserInfo(updateData);
      window.location.reload();
      setShowProfileEditModal(false);
      showToast({
        type: 'success',
        title: '프로필 업데이트 완료',
        message: '프로필 정보가 성공적으로 업데이트되었습니다.',
      });
    } catch (error: any) {
      const message = error.response?.data?.detail || '프로필 수정에 실패했습니다.';
      showToast({
        type: 'error',
        title: '프로필 수정 실패',
        message,
      });
    }
  };

  const handleDeleteAccount = async () => {
    try {
      await deleteAccount();
      setUser(null);
      setIsLoggedIn(false);
      localStorage.removeItem('accessToken');
      localStorage.removeItem('user');
      window.location.href = '/';
    } catch (error: any) {
      const message = error.response?.data?.detail || '회원탈퇴에 실패했습니다.';
      showToast({
        type: 'error',
        title: '회원탈퇴 실패',
        message,
      });
    }
    setShowDeleteModal(false);
  };

  const handleLogout = () => {
    if (confirm('정말 로그아웃하시겠습니까?')) {
      logout();
      window.location.href = '/';
    }
  };

  const reportData = {
    completionRate: 87,
    streakDays: 14,
    totalMedications: 3,
    weeklyData: [85, 90, 78, 95, 88, 92, 87]
  };

  const historyData = [
    { id: '1', name: '타이레놀정 500mg', date: '2024.04.09', time: '08:00', status: '복용완료' },
    { id: '2', name: '루코페트정 250mg', date: '2024.04.09', time: '12:30', status: '복용완료' },
    { id: '3', name: '비타민D 1000IU', date: '2024.04.09', time: '19:00', status: '복용완료' },
    { id: '4', name: '타이레놀정 500mg', date: '2024.04.08', time: '08:00', status: '미복용' }
  ];

  const renderTabContent = () => {
    switch (activeTab) {
      case 'profile':
        return (
          <div className="mypage__tab-content">
            <div className="mypage__profile-info-card">
              <div className="mypage__profile-row">
                <div className="mypage__profile-field">
                  <label>이름</label>
                  <span>{user?.name || '-'}</span>
                </div>
                <div className="mypage__profile-field">
                  <label>연락처</label>
                  <span>{profileData.phone || '-'}</span>
                </div>
              </div>
              <div className="mypage__profile-row">
                <div className="mypage__profile-field">
                  <label>이메일</label>
                  <span>{user?.email || '-'}</span>
                </div>
                <div className="mypage__profile-field">
                  <label>성별</label>
                  <span>{profileData.gender === 'MALE' ? '남성' : profileData.gender === 'FEMALE' ? '여성' : '-'}</span>
                </div>
              </div>
              <div className="mypage__profile-row">
                <div className="mypage__profile-field">
                  <label>생년월일</label>
                  <span>{profileData.birthDate || '-'}</span>
                </div>
              </div>
            </div>
          </div>
        );

      case 'report':
        return (
          <div className="mypage__tab-content">
            <div className="mypage__report-stats">
              <div className="mypage__report-card">
                <span className="mypage__report-label">이번 주 복용률</span>
                <span className="mypage__report-value">{reportData.completionRate}%</span>
              </div>
              <div className="mypage__report-card">
                <span className="mypage__report-label">연속 복용</span>
                <span className="mypage__report-value">{reportData.streakDays}일</span>
              </div>
              <div className="mypage__report-card">
                <span className="mypage__report-label">복용 중인 약물</span>
                <span className="mypage__report-value">{reportData.totalMedications}</span>
              </div>
            </div>
            <div className="mypage__chart-section">
              <h4>복약 준수율 (최근 7일)</h4>
              <div className="mypage__chart">
                {reportData.weeklyData.map((value, index) => (
                  <div key={index} className="mypage__chart-bar">
                    <div className="mypage__chart-fill" style={{ height: `${value}%` }}></div>
                    <span className="mypage__chart-label">{index + 1}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="mypage__medication-list">
              <h4>복용 중인 약물</h4>
              <div className="mypage__med-item">
                <span>타이레놀정 500mg</span>
                <span className="mypage__med-status">복용중</span>
              </div>
              <div className="mypage__med-item">
                <span>루코페트정 250mg</span>
                <span className="mypage__med-status">복용중</span>
              </div>
            </div>
            <div className="mypage__tips">
              <h4>건강 관리 팁</h4>
              <ul>
                <li>• 약물 복용 시간을 일정하게 유지하면 치료 효과가 높아집니다</li>
                <li>• 복용량과 복용법을 정확히 지켜주세요</li>
                <li>• 약물 복용 중 이상 증상이 있으면 즉시 의사와 상담하세요</li>
              </ul>
            </div>
          </div>
        );

      case 'history':
        return (
          <div className="mypage__tab-content">
            <div className="mypage__history-list">
              {historyData.map(item => (
                <div key={item.id} className="mypage__history-item">
                  <div className="mypage__history-info">
                    <h4>{item.name}</h4>
                    <span className="mypage__history-date">{item.date} {item.time}</span>
                  </div>
                  <span className={`mypage__history-status ${item.status === '복용완료' ? 'mypage__history-status--completed' : 'mypage__history-status--missed'}`}>
                    {item.status}
                  </span>
                </div>
              ))}
            </div>
          </div>
        );

      case 'account':
        return (
          <div className="mypage__tab-content">
            <div className="mypage__account-section">
              <div className="mypage__account-item">
                <div className="mypage__account-info">
                  <span className="mypage__account-title">비밀번호 변경</span>
                  <span className="mypage__account-desc">계정 보안을 위해 정기적으로 변경하세요</span>
                </div>
                <button onClick={() => setShowPasswordModal(true)} className="mypage__account-btn">
                  변경
                </button>
              </div>
              <div className="mypage__account-item mypage__account-item--danger">
                <div className="mypage__account-info">
                  <span className="mypage__account-title">회원탈퇴</span>
                  <span className="mypage__account-desc">계정과 모든 데이터가 영구적으로 삭제됩니다</span>
                </div>
                <button onClick={() => setShowDeleteModal(true)} className="mypage__account-btn mypage__account-btn--danger">
                  탈퇴
                </button>
              </div>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="mypage">
      <div className="mypage__sidebar">
        <div className="mypage__profile">
          <div className="mypage__avatar">
            <div className="mypage__avatar-circle">
              {user?.profileImage ? (
                <img src={user.profileImage} alt="프로필" className="mypage__avatar-image" />
              ) : (
                <span className="mypage__avatar-text">
                  {user?.name?.charAt(0).toUpperCase() || 'U'}
                </span>
              )}
            </div>
          </div>
          <div className="mypage__user-info">
            <h3 className="mypage__username">{user?.name || '사용자'}</h3>
            <p className="mypage__user-email">{user?.email || 'user@example.com'}</p>
          </div>
        </div>

        <nav className="mypage__nav">
          <button className={`mypage__nav-item ${activeTab === 'profile' ? 'mypage__nav-item--active' : ''}`} onClick={() => setActiveTab('profile')}>프로필</button>
          <button className={`mypage__nav-item ${activeTab === 'report' ? 'mypage__nav-item--active' : ''}`} onClick={() => setActiveTab('report')}>내 리포트</button>
          <button className={`mypage__nav-item ${activeTab === 'history' ? 'mypage__nav-item--active' : ''}`} onClick={() => setActiveTab('history')}>복약 히스토리</button>
          <button className={`mypage__nav-item ${activeTab === 'account' ? 'mypage__nav-item--active' : ''}`} onClick={() => setActiveTab('account')}>보안 / 계정</button>
        </nav>

        <div className="mypage__sidebar-footer">
          <button onClick={handleLogout} className="mypage__logout-btn">로그아웃</button>
        </div>
      </div>

      <div className="mypage__main">
        <div className="mypage__header">
          <h2 className="mypage__page-title">
            {activeTab === 'profile' && '프로필'}
            {activeTab === 'report' && '내 리포트'}
            {activeTab === 'history' && '복약 히스토리'}
            {activeTab === 'account' && '보안 / 계정'}
          </h2>
          {activeTab === 'profile' && (
            <button onClick={() => setShowProfileEditModal(true)} className="mypage__edit-btn">수정</button>
          )}
        </div>
        {renderTabContent()}
      </div>

      {/* 프로필 편집 모달 */}
      {showProfileEditModal && (
        <div className="mypage__modal-overlay">
          <div className="mypage__modal">
            <div className="mypage__modal-header">
              <h3>프로필 편집</h3>
              <button onClick={() => setShowProfileEditModal(false)} className="mypage__modal-close">✕</button>
            </div>
            <div className="mypage__modal-form">
              <div className="mypage__form-group">
                <label>프로필 사진</label>
                <div className="mypage__profile-image-section">
                  <div className="mypage__profile-image-preview">
                    {profileData.profileImage ? (
                      <img src={profileData.profileImage} alt="프로필 미리보기" className="mypage__profile-image" />
                    ) : (
                      <div className="mypage__profile-image-placeholder">
                        {profileData.name?.charAt(0).toUpperCase() || 'U'}
                      </div>
                    )}
                  </div>
                  <div className="mypage__profile-image-actions">
                    <input type="file" accept="image/*" onChange={handleImageUpload} className="mypage__file-input" id="profile-image-upload" />
                    <label htmlFor="profile-image-upload" className="mypage__image-btn mypage__image-btn--upload">사진 선택</label>
                    {profileData.profileImage && (
                      <button type="button" onClick={handleImageRemove} className="mypage__image-btn mypage__image-btn--remove">사진 제거</button>
                    )}
                  </div>
                </div>
              </div>
              <div className="mypage__form-group">
                <label>이름</label>
                <input type="text" value={profileData.name} onChange={(e) => setProfileData({...profileData, name: e.target.value})} className="mypage__form-input" />
              </div>
              <div className="mypage__form-group">
                <label>이메일</label>
                <input type="email" value={profileData.email} onChange={(e) => setProfileData({...profileData, email: e.target.value})} className="mypage__form-input" />
              </div>
              <div className="mypage__form-group">
                <label>연락처</label>
                <input type="tel" value={profileData.phone} onChange={(e) => setProfileData({...profileData, phone: e.target.value})} className="mypage__form-input" />
              </div>
              <div className="mypage__form-group">
                <label>생년월일</label>
                <input
                  type="date"
                  value={profileData.birthDate}
                  onChange={(e) => setProfileData({...profileData, birthDate: e.target.value})}
                  className="mypage__form-input"
                  max={new Date().toISOString().split('T')[0]}
                />
              </div>
              <div className="mypage__form-group">
                <label>성별</label>
                <select value={profileData.gender} onChange={(e) => setProfileData({...profileData, gender: e.target.value})} className="mypage__form-input">
                  <option value="">선택하세요</option>
                  <option value="MALE">남성</option>
                  <option value="FEMALE">여성</option>
                </select>
              </div>
            </div>
            <div className="mypage__modal-buttons">
              <button onClick={() => setShowProfileEditModal(false)} className="mypage__modal-btn mypage__modal-btn--secondary">취소</button>
              <button onClick={handleProfileUpdate} className="mypage__modal-btn mypage__modal-btn--primary">저장</button>
            </div>
          </div>
        </div>
      )}

      {/* 비밀번호 변경 모달 */}
      {showPasswordModal && (
        <div className="mypage__modal-overlay">
          <div className="mypage__modal">
            <div className="mypage__modal-header">
              <h3>비밀번호 변경</h3>
              <button onClick={() => setShowPasswordModal(false)} className="mypage__modal-close">✕</button>
            </div>
            <div className="mypage__modal-form">
              <div className="mypage__form-group">
                <label>현재 비밀번호</label>
                <div className="mypage__input-wrapper">
                  <input type={showCurrentPw ? 'text' : 'password'} placeholder="현재 비밀번호를 입력하세요" value={passwordData.currentPassword} onChange={(e) => setPasswordData({...passwordData, currentPassword: e.target.value})} className="mypage__form-input" />
                  <button type="button" className="mypage__pw-toggle" onClick={() => togglePwVisibility(setShowCurrentPw)}>{showCurrentPw ? '숨기기' : '보기'}</button>
                </div>
              </div>
              <div className="mypage__form-group">
                <label>새 비밀번호</label>
                <div className="mypage__input-wrapper">
                  <input type={showNewPw ? 'text' : 'password'} placeholder="새 비밀번호를 입력하세요" value={passwordData.newPassword} onChange={(e) => setPasswordData({...passwordData, newPassword: e.target.value})} className="mypage__form-input" />
                  <button type="button" className="mypage__pw-toggle" onClick={() => togglePwVisibility(setShowNewPw)}>{showNewPw ? '숨기기' : '보기'}</button>
                </div>
              </div>
              <div className="mypage__form-group">
                <label>새 비밀번호 확인</label>
                <div className="mypage__input-wrapper">
                  <input type={showConfirmPw ? 'text' : 'password'} placeholder="새 비밀번호를 다시 입력하세요" value={passwordData.confirmPassword} onChange={(e) => setPasswordData({...passwordData, confirmPassword: e.target.value})} className="mypage__form-input" />
                  <button type="button" className="mypage__pw-toggle" onClick={() => togglePwVisibility(setShowConfirmPw)}>{showConfirmPw ? '숨기기' : '보기'}</button>
                </div>
              </div>
            </div>
            <div className="mypage__modal-buttons">
              <button onClick={() => setShowPasswordModal(false)} className="mypage__modal-btn mypage__modal-btn--secondary">취소</button>
              <button onClick={handlePasswordChange} className="mypage__modal-btn mypage__modal-btn--primary" disabled={!passwordData.currentPassword || !passwordData.newPassword || !passwordData.confirmPassword}>변경</button>
            </div>
          </div>
        </div>
      )}

      {/* 회원탈퇴 모달 */}
      {showDeleteModal && (
        <div className="mypage__modal-overlay">
          <div className="mypage__modal">
            <div className="mypage__modal-header">
              <h3>회원탈퇴</h3>
              <button onClick={() => setShowDeleteModal(false)} className="mypage__modal-close">✕</button>
            </div>
            <div className="mypage__modal-content">
              <p>정말로 회원탈퇴하시겠습니까?</p>
              <p>탈퇴 시 모든 데이터가 영구적으로 삭제되며, 복구할 수 없습니다.</p>
            </div>
            <div className="mypage__modal-buttons">
              <button onClick={() => setShowDeleteModal(false)} className="mypage__modal-btn mypage__modal-btn--secondary">취소</button>
              <button onClick={handleDeleteAccount} className="mypage__modal-btn mypage__modal-btn--danger">탈퇴하기</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MyPage;