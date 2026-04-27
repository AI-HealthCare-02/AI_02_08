import apiClient from './apiClient';

export interface MedicationHistory {
  ocr_id: string;
  created_at: string;
  medications: {
    name: string;
    dosage: string | null;
    frequency: string | null;
    timing: string | null;
    start_date: string | null;
    end_date: string | null;
  }[];
}

export const getMedicationHistory = async (date: string): Promise<MedicationHistory[]> => {
  const response = await apiClient.get(`/medications/history?date=${date}`);
  return response.data;
};