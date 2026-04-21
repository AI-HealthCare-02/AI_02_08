import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import apiClient from '../../api/apiClient';

const TermsAgreementPage: React.FC = () => {
  const navigate = useNavigate();

  const [agreements, setAgreements] = useState({
    all: false,
    terms: false,
    privacy: false,
  });

  const handleAllCheck = (e: React.ChangeEvent<HTMLInputElement>) => {
    const checked = e.target.checked;
    setAgreements({
      all: checked,
      terms: checked,
      privacy: checked,
    });
  };

  const handleSingleCheck = (name: 'terms' | 'privacy') => (e: React.ChangeEvent<HTMLInputElement>) => {
    const newAgreements = {
      ...agreements,
      [name]: e.target.checked,
    };
    newAgreements.all = newAgreements.terms && newAgreements.privacy;
    setAgreements(newAgreements);
  };

  const handleSubmit = async () => {
    if (!agreements.terms || !agreements.privacy) {
      alert('필수 약관에 모두 동의해주세요.');
      return;
    }

    try {
      const accessToken = localStorage.getItem('accessToken'); //추가

      await apiClient.post('/auth/terms/agree', {
        agree_terms: agreements.terms,
        agree_privacy: agreements.privacy,
      }, {
        headers: { Authorization: `Bearer ${accessToken}` },
      });

      // 추가 정보 입력 페이지로!
      navigate('/auth/kakao/additional-info');
    } catch (error) {
      console.error('약관 동의 실패:', error);
      alert('약관 동의 처리 중 오류가 발생했습니다.');
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <div style={styles.header}>
          <div style={styles.appIcon}>APP</div>
          <h2 style={styles.appName}>이루도담</h2>
          <p style={styles.appSubtitle}>Irudodam</p>
        </div>

        <div style={styles.section}>
          <label style={styles.checkboxLabel}>
            <input
              type="checkbox"
              checked={agreements.all}
              onChange={handleAllCheck}
              style={styles.checkbox}
            />
            <span style={styles.labelText}>전체 동의하기</span>
          </label>
          <p style={styles.description}>
            전체동의는 선택목적에 대한 동의를 포함하고 있으며, 선택목적에 대한 동의를 거부해도 서비스 이용이 가능합니다.
          </p>
        </div>

        <div style={styles.divider}></div>

        <div style={styles.section}>
          <h3 style={styles.sectionTitle}>서비스 이용약관 동의</h3>

          <label style={styles.checkboxLabel}>
            <input
              type="checkbox"
              checked={agreements.terms}
              onChange={handleSingleCheck('terms')}
              style={styles.checkbox}
            />
            <span style={styles.labelText}>[필수] 이용약관</span>
            <a href="/terms" style={styles.link}>보기</a>
          </label>

          <label style={styles.checkboxLabel}>
            <input
              type="checkbox"
              checked={agreements.privacy}
              onChange={handleSingleCheck('privacy')}
              style={styles.checkbox}
            />
            <span style={styles.labelText}>[필수] 개인정보 처리방침</span>
            <a href="/privacy" style={styles.link}>보기</a>
          </label>
        </div>

        <button
          onClick={handleSubmit}
          disabled={!agreements.terms || !agreements.privacy}
          style={{
            ...styles.submitButton,
            backgroundColor: agreements.terms && agreements.privacy ? '#FEE500' : '#cccccc',
            cursor: agreements.terms && agreements.privacy ? 'pointer' : 'not-allowed',
            opacity: agreements.terms && agreements.privacy ? 1 : 0.6,
          }}
        >
          확인하고 계속하기
        </button>
      </div>
    </div>
  );
};

const styles: { [key: string]: React.CSSProperties } = {
  container: {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#f5f5f5',
    padding: '20px',
  },
  card: {
    backgroundColor: 'white',
    borderRadius: '12px',
    padding: '40px',
    maxWidth: '500px',
    width: '100%',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
  },
  header: {
    textAlign: 'center',
    marginBottom: '30px',
  },
  appIcon: {
    width: '80px',
    height: '80px',
    borderRadius: '50%',
    backgroundColor: '#e0e0e0',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    margin: '0 auto 15px',
    fontSize: '24px',
    color: '#666',
  },
  appName: {
    fontSize: '24px',
    fontWeight: 'bold',
    margin: '10px 0 5px',
  },
  appSubtitle: {
    color: '#666',
    fontSize: '14px',
  },
  section: {
    marginBottom: '20px',
  },
  checkboxLabel: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    padding: '12px 0',
    cursor: 'pointer',
  },
  checkbox: {
    width: '20px',
    height: '20px',
    cursor: 'pointer',
  },
  labelText: {
    flex: 1,
    fontSize: '15px',
  },
  link: {
    color: '#666',
    fontSize: '14px',
    textDecoration: 'underline',
  },
  description: {
    fontSize: '13px',
    color: '#666',
    lineHeight: '1.5',
    marginTop: '5px',
  },
  divider: {
    height: '1px',
    backgroundColor: '#e0e0e0',
    margin: '20px 0',
  },
  sectionTitle: {
    fontSize: '16px',
    fontWeight: 'bold',
    marginBottom: '15px',
  },
  submitButton: {
    width: '100%',
    padding: '16px',
    border: 'none',
    borderRadius: '8px',
    fontSize: '16px',
    fontWeight: 'bold',
    marginTop: '30px',
  },
};

export default TermsAgreementPage;