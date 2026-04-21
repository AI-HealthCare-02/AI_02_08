// 기존 타입들
export interface User {
  id: string;
  email: string;
  name: string;
  nickname?: string;
  avatar?: string;
  profileImage?: string;
}

export interface LoginData {
  email: string;
  password: string;
}

export interface SignupData {
  email: string;
  password: string;
  passwordConfirm: string;
  name: string;
  gender: 'MALE' | 'FEMALE';
  birthDate: string;        // (YYYY-MM-DD)
  phoneNumber: string;
  agreeTerms: boolean;
  agreePrivacy: boolean;
}

export interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isLoggedIn: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  signup: (userData: SignupData) => Promise<void>;
}

// API 응답 타입들
export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
}

export interface LoginResponse {
  access_token: string;  // accessToken → access_token (백엔드 기준)
}