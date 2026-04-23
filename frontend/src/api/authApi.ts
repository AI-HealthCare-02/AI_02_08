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

// 카카오 로그인 URL 생성
export const getKakaoLoginUrl = (): string => {
  const KAKAO_CLIENT_ID = import.meta.env.VITE_KAKAO_CLIENT_ID;
  const REDIRECT_URI = import.meta.env.VITE_KAKAO_REDIRECT_URI || 'http://localhost:3000/auth/kakao/callback';
  return `https://kauth.kakao.com/oauth/authorize?client_id=${KAKAO_CLIENT_ID}&redirect_uri=${REDIRECT_URI}&response_type=code`;
};

// 로그아웃
export const logout = async (): Promise<void> => {
  await apiClient.post('/auth/logout');
};

// 토큰 갱신
export const refreshToken = async (): Promise<{ accessToken: string }> => {
  const response = await apiClient.get('/auth/token/refresh');
  return { accessToken: response.data.access_token };
};

// 비밀번호 재설정 이메일 발송
export const sendPasswordResetEmail = async (email: string): Promise<void> => {
  await apiClient.post('/auth/password/reset-request', { email });
};

// 비밀번호 재설정
export const resetPassword = async (
  email: string,
  code: string,
  newPassword: string,
  newPasswordConfirm: string
): Promise<void> => {
  await apiClient.post('/auth/password/reset', {
    email,
    code,
    new_password: newPassword,
    new_password_confirm: newPasswordConfirm,
  });
};

// 비밀번호 변경 (로그인 상태)
export const changePassword = async (
  currentPassword: string,
  newPassword: string,
  newPasswordConfirm: string
): Promise<void> => {
  await apiClient.patch('/auth/password/change', {
    current_password: currentPassword,
    new_password: newPassword,
    new_password_confirm: newPasswordConfirm,
  });
};

// 회원탈퇴
export const deleteAccount = async (): Promise<void> => {
  await apiClient.delete('/users/me');
};

// 프로필 수정
export const updateUserInfo = async (data: {
  name?: string;
  phone_number?: string;
  birth_date?: string;
  gender?: string;
}): Promise<void> => {
  await apiClient.patch('/users/me', data);
};