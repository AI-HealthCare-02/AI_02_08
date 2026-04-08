// 기존 타입들
export interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
}

export interface LoginData {
  email: string;
  password: string;
}

export interface SignupData {
  email: string;
  password: string;
  passwordConfirm: string;
  verificationCode: string;
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
  accessToken: string;
  refreshToken: string;
  user: User;
}