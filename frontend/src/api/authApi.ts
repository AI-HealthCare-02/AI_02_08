import apiClient from './apiClient';
import { LoginData, SignupData, LoginResponse } from '../types/auth';

// 이메일 중복 확인
export const checkEmailDuplicate = async (email: string): Promise<boolean> => {
  const response = await apiClient.get(`/auth/check-email?email=${encodeURIComponent(email)}`);
  return response.data.is_duplicate;
};

// 인증 이메일 재발송
export const sendVerificationCode = async (email: string): Promise<void> => {
  await apiClient.post('/auth/resend-verification', { email });
};

// 이메일 인증 코드 확인
export const verifyEmailCode = async (email: string, code: string): Promise<boolean> => {
  try {
    await apiClient.get(`/auth/verify-email?email=${encodeURIComponent(email)}&code=${encodeURIComponent(code)}`);
    return true;
  } catch (error) {
    return false;
  }
};

// 회원가입
export const signup = async (userData: SignupData): Promise<void> => {
  await apiClient.post('/auth/signup', {
    email: userData.email,
    password: userData.password,
    name: userData.name,
    gender: userData.gender,
    birth_date: userData.birthDate,
    phone_number: userData.phoneNumber,
    agree_terms: userData.agreeTerms,
    agree_privacy: userData.agreePrivacy,
  });
};

// 로그인
export const login = async (loginData: LoginData): Promise<LoginResponse> => {
  const response = await apiClient.post('/auth/login', loginData);
  return response.data;
};

// 로그아웃
export const logout = async (): Promise<void> => {
  const refreshToken = localStorage.getItem('accessToken');
  await apiClient.post('/auth/logout', { refresh_token: refreshToken });
};

// 토큰 갱신
export const refreshToken = async (): Promise<{ accessToken: string }> => {
  const response = await apiClient.get('/auth/token/refresh');
  return { accessToken: response.data.access_token };
};