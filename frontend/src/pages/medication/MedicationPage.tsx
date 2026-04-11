import React, { useState } from 'react';
import './MedicationPage.css';

interface Medication {
  id: string;
  name: string;
  dosage: string;
  frequency: string;
  timing: string;
  startDate: string;
  endDate?: string;
  notes?: string;
  isActive: boolean;
}

const MedicationPage: React.FC = () => {
  const [medications, setMedications] = useState<Medication[]>([
    {
      id: '1',
      name: '타이레놀정',
      dosage: '500mg',
      frequency: '1일 3회',
      timing: '식후',
      startDate: '2024-04-01',
      endDate: '2024-04-15',
      notes: '두통이 심할 때만 복용',
      isActive: true
    },
    {
      id: '2',
      name: '루코페트정',
      dosage: '250mg',
      frequency: '1일 2회',
      timing: '식전',
      startDate: '2024-04-05',
      notes: '위장 보호를 위해 복용',
      isActive: false
    }
  ]);

  const [activeFilter, setActiveFilter] = useState<'all' | 'active' | 'inactive'>('all');
  const [showAddModal, setShowAddModal] = useState(false);
  const [newMedication, setNewMedication] = useState<Partial<Medication>>({
    name: '',
    dosage: '',
    frequency: '',
    timing: '',
    startDate: '',
    endDate: '',
    notes: '',
    isActive: true
  });

  const handleAddMedication = () => {
    if (newMedication.name && newMedication.dosage) {
      const medication: Medication = {
        id: Date.now().toString(),
        name: newMedication.name!,
        dosage: newMedication.dosage!,
        frequency: newMedication.frequency || '1일 1회',
        timing: newMedication.timing || '식후',
        startDate: newMedication.startDate || new Date().toISOString().split('T')[0],
        endDate: newMedication.endDate,
        notes: newMedication.notes,
        isActive: true
      };
      
      setMedications([...medications, medication]);
      setNewMedication({
        name: '',
        dosage: '',
        frequency: '',
        timing: '',
        startDate: '',
        endDate: '',
        notes: '',
        isActive: true
      });
      setShowAddModal(false);
    }
  };

  const toggleMedicationStatus = (id: string) => {
    setMedications(medications.map(med => 
      med.id === id ? { ...med, isActive: !med.isActive } : med
    ));
  };

  const deleteMedication = (id: string) => {
    setMedications(medications.filter(med => med.id !== id));
  };

  // 필터링된 약물 목록 가져오기
  const getFilteredMedications = () => {
    switch (activeFilter) {
      case 'active':
        return medications.filter(med => med.isActive);
      case 'inactive':
        return medications.filter(med => !med.isActive);
      default:
        return medications;
    }
  };

  return (
    <div className="medication-page">
      {/* 헤더 섹션 */}
      <div className="medication-page__header">
        <h1 className="medication-page__title">복약 관리</h1>
        <p className="medication-page__subtitle">내 약물을 체계적으로 관리하세요</p>
        
        <button 
          onClick={() => setShowAddModal(true)}
          className="medication-page__add-btn"
        >
          + 새 약물 추가
        </button>
      </div>

      {/* 통계 카드 */}
      <div className="medication-page__stats">
        <div className="medication-page__stat-card">
          <h3>복용 중인 약물</h3>
          <span className="medication-page__stat-number">
            {medications.filter(med => med.isActive).length}
          </span>
        </div>
        <div className="medication-page__stat-card">
          <h3>오늘 복용할 약물</h3>
          <span className="medication-page__stat-number">
            {medications.filter(med => med.isActive).length}
          </span>
        </div>
        <div className="medication-page__stat-card">
          <h3>중단된 약물</h3>
          <span className="medication-page__stat-number">
            {medications.filter(med => !med.isActive).length}
          </span>
        </div>
      </div>

      {/* 약물 목록 */}
      <div className="medication-page__content">
        <div className="medication-page__list-header">
          <h2>내 약물 목록</h2>
          <div className="medication-page__filters">
            <button 
              className={`medication-page__filter-btn ${activeFilter === 'all' ? 'medication-page__filter-btn--active' : ''}`}
              onClick={() => setActiveFilter('all')}
            >
              전체
            </button>
            <button 
              className={`medication-page__filter-btn ${activeFilter === 'active' ? 'medication-page__filter-btn--active' : ''}`}
              onClick={() => setActiveFilter('active')}
            >
              복용 중
            </button>
            <button 
              className={`medication-page__filter-btn ${activeFilter === 'inactive' ? 'medication-page__filter-btn--active' : ''}`}
              onClick={() => setActiveFilter('inactive')}
            >
              중단됨
            </button>
          </div>
        </div>

        <div className="medication-page__list">
          {getFilteredMedications().map(medication => (
            <div 
              key={medication.id} 
              className={`medication-page__card ${!medication.isActive ? 'medication-page__card--inactive' : ''}`}
            >
              <div className="medication-page__card-header">
                <h3 className="medication-page__card-title">{medication.name}</h3>
                <div className="medication-page__card-actions">
                  <button 
                    onClick={() => toggleMedicationStatus(medication.id)}
                    className={`medication-page__toggle-btn ${medication.isActive ? 'medication-page__toggle-btn--active' : ''}`}
                  >
                    {medication.isActive ? '복용 중' : '중단됨'}
                  </button>
                  <button 
                    onClick={() => deleteMedication(medication.id)}
                    className="medication-page__delete-btn"
                  >
                    삭제
                  </button>
                </div>
              </div>
              
              <div className="medication-page__card-content">
                <div className="medication-page__card-info">
                  <span className="medication-page__info-label">용량:</span>
                  <span>{medication.dosage}</span>
                </div>
                <div className="medication-page__card-info">
                  <span className="medication-page__info-label">복용법:</span>
                  <span>{medication.frequency}</span>
                </div>
                <div className="medication-page__card-info">
                  <span className="medication-page__info-label">복용 시기:</span>
                  <span>{medication.timing}</span>
                </div>
                <div className="medication-page__card-info">
                  <span className="medication-page__info-label">복용 기간:</span>
                  <span>{medication.startDate} ~ {medication.endDate || '지속'}</span>
                </div>
                {medication.notes && (
                  <div className="medication-page__card-notes">
                    <span className="medication-page__info-label">메모:</span>
                    <span>{medication.notes}</span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 약물 추가 모달 */}
      {showAddModal && (
        <div className="medication-page__modal-overlay">
          <div className="medication-page__modal">
            <div className="medication-page__modal-header">
              <h3>새 약물 추가</h3>
              <button 
                onClick={() => setShowAddModal(false)}
                className="medication-page__modal-close"
              >
                ✕
              </button>
            </div>
            
            <div className="medication-page__modal-form">
              <div className="medication-page__form-group">
                <label>약물명 *</label>
                <input 
                  type="text"
                  placeholder="약물명을 입력하세요"
                  value={newMedication.name || ''}
                  onChange={(e) => setNewMedication({...newMedication, name: e.target.value})}
                  className="medication-page__form-input"
                />
              </div>
              
              <div className="medication-page__form-group">
                <label>용량 *</label>
                <input 
                  type="text"
                  placeholder="ex) 500mg"
                  value={newMedication.dosage || ''}
                  onChange={(e) => setNewMedication({...newMedication, dosage: e.target.value})}
                  className="medication-page__form-input"
                />
              </div>
              
              <div className="medication-page__form-group">
                <label>복용법</label>
                <select 
                  value={newMedication.frequency || ''}
                  onChange={(e) => setNewMedication({...newMedication, frequency: e.target.value})}
                  className="medication-page__form-select"
                >
                  <option value="">선택하세요</option>
                  <option value="1일 1회">1일 1회</option>
                  <option value="1일 2회">1일 2회</option>
                  <option value="1일 3회">1일 3회</option>
                  <option value="필요시">필요시</option>
                </select>
              </div>
              
              <div className="medication-page__form-group">
                <label>복용 시기</label>
                <select 
                  value={newMedication.timing || ''}
                  onChange={(e) => setNewMedication({...newMedication, timing: e.target.value})}
                  className="medication-page__form-select"
                >
                  <option value="">선택하세요</option>
                  <option value="식전">식전</option>
                  <option value="식후">식후</option>
                  <option value="취침전">취침전</option>
                  <option value="공복시">공복시</option>
                </select>
              </div>
              
              <div className="medication-page__form-row">
                <div className="medication-page__form-group">
                  <label>시작일</label>
                  <input 
                    type="date"
                    value={newMedication.startDate || ''}
                    onChange={(e) => setNewMedication({...newMedication, startDate: e.target.value})}
                    className="medication-page__form-input"
                  />
                </div>
                
                <div className="medication-page__form-group">
                  <label>종료일 (선택)</label>
                  <input 
                    type="date"
                    value={newMedication.endDate || ''}
                    onChange={(e) => setNewMedication({...newMedication, endDate: e.target.value})}
                    className="medication-page__form-input"
                  />
                </div>
              </div>
              
              <div className="medication-page__form-group">
                <label>메모 (선택)</label>
                <textarea 
                  placeholder="복용 시 주의사항이나 메모를 입력하세요"
                  value={newMedication.notes || ''}
                  onChange={(e) => setNewMedication({...newMedication, notes: e.target.value})}
                  className="medication-page__form-textarea"
                  rows={3}
                />
              </div>
            </div>
            
            <div className="medication-page__modal-buttons">
              <button 
                onClick={() => setShowAddModal(false)}
                className="medication-page__modal-btn medication-page__modal-btn--secondary"
              >
                취소
              </button>
              <button 
                onClick={handleAddMedication}
                className="medication-page__modal-btn medication-page__modal-btn--primary"
                disabled={!newMedication.name || !newMedication.dosage}
              >
                추가
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MedicationPage;