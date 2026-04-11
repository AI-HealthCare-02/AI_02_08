import { useState, useEffect } from 'react';

interface User {
  id: string;
  name: string;
  email: string;
  nickname?: string;
  avatar?: string;
  profileImage?: string;
}

interface AuthState {
  isLoggedIn: boolean;
  user: User | null;
  login: (email: string, password: string) => Promise<boolean>;
  logout: () => void;
  signup: (name: string, email: string, password: string) => Promise<boolean>;
  updateUser: (userData: Partial<User>) => void;
}

export const useAuth = (): AuthState => {
  const [isLoggedIn, setIsLoggedIn] = useState<boolean>(() => {
    const savedUser = localStorage.getItem('mockUser');
    return !!savedUser;
  });
  const [user, setUser] = useState<User | null>(() => {
    const savedUser = localStorage.getItem('mockUser');
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
    console.log('로그인 상태:', isLoggedIn, '사용자:', user);
  }, [isLoggedIn, user]);

  const login = async (email: string, password: string): Promise<boolean> => {
    if (email && password) {
      const mockUser: User = {
        id: '1',
        name: email.split('@')[0],
        email: email
      };
      
      setUser(mockUser);
      setIsLoggedIn(true);
      localStorage.setItem('mockUser', JSON.stringify(mockUser));
      return true;
    }
    return false;
  };

  const logout = () => {
    setUser(null);
    setIsLoggedIn(false);
    localStorage.removeItem('mockUser');
  };

  const signup = async (name: string, email: string, password: string): Promise<boolean> => {
    if (name && email && password) {
      const mockUser: User = {
        id: '1',
        name: name,
        email: email
      };
      
      setUser(mockUser);
      setIsLoggedIn(true);
      localStorage.setItem('mockUser', JSON.stringify(mockUser));
      return true;
    }
    return false;
  };

  const updateUser = (userData: Partial<User>) => {
    if (user) {
      const updatedUser = { ...user, ...userData };
      setUser(updatedUser);
      localStorage.setItem('mockUser', JSON.stringify(updatedUser));
    }
  };

  return {
    isLoggedIn,
    user,
    login,
    logout,
    signup,
    updateUser
  };
};