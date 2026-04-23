import { OcrMedicationItem } from '../api/ocrApi';

const OCR_RESULTS_KEY = 'ocr_results';
const OCR_STATUS_KEY = 'ocr_status';
const OCR_PREVIEW_KEY = 'ocr_preview';
const MEDICATIONS_KEY = 'medications';

export interface StoredMedication {
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

// OCR 결과 저장/불러오기
export const saveOcrResults = (results: OcrMedicationItem[]) => {
  sessionStorage.setItem(OCR_RESULTS_KEY, JSON.stringify(results));
};

export const loadOcrResults = (): OcrMedicationItem[] | null => {
  const data = sessionStorage.getItem(OCR_RESULTS_KEY);
  return data ? JSON.parse(data) : null;
};

export const saveOcrStatus = (status: string) => {
  sessionStorage.setItem(OCR_STATUS_KEY, status);
};

export const loadOcrStatus = (): string => {
  return sessionStorage.getItem(OCR_STATUS_KEY) || 'idle';
};

export const saveOcrPreview = (url: string) => {
  sessionStorage.setItem(OCR_PREVIEW_KEY, url);
};

export const loadOcrPreview = (): string | null => {
  return sessionStorage.getItem(OCR_PREVIEW_KEY);
};

// 복약관리 데이터 저장/불러오기
export const saveMedications = (medications: StoredMedication[]) => {
  sessionStorage.setItem(MEDICATIONS_KEY, JSON.stringify(medications));
};

export const loadMedications = (): StoredMedication[] => {
  const data = sessionStorage.getItem(MEDICATIONS_KEY);
  return data ? JSON.parse(data) : [];
};

// OCR 결과를 복약관리 약물로 변환
export const ocrToMedication = (item: OcrMedicationItem): StoredMedication => ({
  id: Date.now().toString() + Math.random().toString(36).slice(2),
  name: item.name,
  dosage: item.dosage,
  frequency: item.frequency,
  timing: item.timing,
  startDate: new Date().toISOString().split('T')[0],
  notes: item.description,
  isActive: true,
});
