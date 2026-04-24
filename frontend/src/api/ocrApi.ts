import axios from 'axios';
import apiClient from './apiClient';

export interface OcrMedicationItem {
  name: string;
  dosage: string;
  frequency: string;
  timing: string;
  description?: string;
}

export interface OcrResult {
  ocrId: string;
  status: string;
  medications: OcrMedicationItem[];
}

export const analyzePrescription = async (image: File): Promise<OcrResult> => {
  const formData = new FormData();
  formData.append('image', image);

  try {
    const response = await apiClient.post('/ai/ocr/prescription', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 60000,
    });
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const status = error.response?.status;
      const detail = error.response?.data?.detail;

      if (status === 400 && detail) {
        throw new Error(detail);
      }
      if (status === 502) {
        throw new Error('OCR 서비스가 일시적으로 지연되고 있습니다. 잠시 후 다시 시도해주세요.');
      }
      if (status && status >= 500) {
        throw new Error('서버에 일시적인 문제가 발생했습니다. 잠시 후 다시 시도해주세요.');
      }
    }
    throw new Error('서버와 통신 중 오류가 발생했습니다. 네트워크 연결을 확인해주세요.');
  }
};

/**
 * OCR 결과 확정 → 백엔드 DB에 MedicationLog 저장
 */
export const confirmPrescription = async (
  ocrId: string,
  medications: OcrMedicationItem[]
): Promise<{ registeredCount: number; medicationIds: number[] }> => {
  const response = await apiClient.post(`/ai/ocr/prescription/${ocrId}/confirm`, {
    medications,
  });
  return response.data;
};