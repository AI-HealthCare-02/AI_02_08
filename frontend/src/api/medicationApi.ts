import apiClient from './apiClient';

export interface MedicationHistory {
  id: number;
  name: string;
  dosage: string;
  frequency: string;
  timing: string;
}

export const getMedicationHistory = async (date: string): Promise<MedicationHistory[]> => {
  const response = await apiClient.get(`/medications/history?date=${date}`);
  return response.data;
};

export const deleteMedication = async (medicationId: number): Promise<void> => {
  await apiClient.delete(`/medications/${medicationId}`);
};