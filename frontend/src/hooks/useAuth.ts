import { useState, useEffect } from 'react';
import { login as loginApi, logout as logoutApi } from '../api/authApi';
import apiClient from '../api/apiClient';

interface User {
  id: string;
  name: string;
  email: string;
  birthday?: string;
  nickname?: string;
  avatar?: string;
  profileImage?: string;
}

interface AuthState {
  isLoggedIn: boolean;
  user: User | null;
  login: (email: string, password: string) => Promise<boolean>;
  logout: () => void;
}

export const useAuth = (): AuthState => {
  const [isLoggedIn, setIsLoggedIn] = useState<boolean>(() => {
    return !!localStorage.getItem('accessToken');
  });
  const [user, setUser] = useState<User | null>(() => {
    const savedUser = localStorage.getItem('user');
    if (savedUser) {
      try {
        return JSON.parse(savedUser);
      } catch {
        return null;
      }
    }
    return null;
  });

  useEffect(() => {
    if (isLoggedIn && !user) {
      fetchUserInfo();
    }
  }, [isLoggedIn]);

  const fetchUserInfo = async () => {
    try {
      const response = await apiClient.get('/users/me');
      const userInfo: User = {
        id: String(response.data.id),
        name: response.data.name,
        email: response.data.email,
        birthday: response.data.birthday,
        phoneNumber: response.data.phone_number,
      };
      setUser(userInfo);
      localStorage.setItem('user', JSON.stringify(userInfo));
    } catch (error) {
      console.error('유저 정보 가져오기 실패:', error);
    }
  };

  const login = async (email: string, password: string): Promise<boolean> => {
    try {
      const response = await loginApi({ email, password });
      localStorage.setItem('accessToken', response.access_token);

      const userResponse = await apiClient.get('/users/me');
      const userInfo: User = {
        id: String(userResponse.data.id),
        name: userResponse.data.name,  // ✅ 실제 이름
        email: userResponse.data.email,
      };
      setUser(userInfo);
      setIsLoggedIn(true);
      localStorage.setItem('user', JSON.stringify(userInfo));
      return true;
    } catch (error: any) {
      console.error('로그인 실패:', error);
      return false;
    }
  };

  const logout = () => {
    logoutApi().catch(console.error);
    setUser(null);
    setIsLoggedIn(false);
    localStorage.removeItem('accessToken');
    localStorage.removeItem('user');
  };

  return {
    isLoggedIn,
    user,
    login,
    logout,
  };
};