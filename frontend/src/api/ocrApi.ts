import apiClient from './apiClient';

export interface OcrMedicationItem {
  name: string;
  dosage: string;
  frequency: string;
  timing: string;
}

export interface OcrResult {
  ocrId: string;
  status: string;
  medications: OcrMedicationItem[];
}

export const analyzePrescription = async (image: File): Promise<OcrResult> => {
  const formData = new FormData();
  formData.append('image', image);

  const response = await apiClient.post('/ai/ocr/prescription', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};