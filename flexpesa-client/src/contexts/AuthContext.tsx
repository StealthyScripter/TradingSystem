'use client';
import { createContext, useContext, useEffect, useState } from 'react';
import { portfolioAPI } from '@/lib/api';
import { User, RegisterRequest, LoginRequest } from '@/types';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<boolean>;
  register: (userData: RegisterRequest) => Promise<boolean>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const checkAuth = async () => {
    try {
      // Use the correct API method that exists in API.ts
      const userProfile = await portfolioAPI.getUserProfile();

      // Transform UserProfile to User format
      const user: User = {
        id: userProfile.user_id,
        email: userProfile.email || '',
        first_name: userProfile.first_name || '',
        last_name: userProfile.last_name || '',
        is_active: true
      };

      setUser(user);
    } catch (error) {
      console.log('Not authenticated');
      // Don't set error state for auth check failures
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (email: string, password: string): Promise<boolean> => {
    try {
      const credentials: LoginRequest = { email, password };
      const response = await portfolioAPI.login(credentials);
      setUser(response.user);
      return true;
    } catch (error) {
      console.error('Login failed:', error);
      return false;
    }
  };

  const register = async (userData: RegisterRequest): Promise<boolean> => {
    try {
      const newUser = await portfolioAPI.register(userData);
      // Auto-login after registration
      return await login(userData.email, userData.password);
    } catch (error) {
      console.error('Registration failed:', error);
      return false;
    }
  };

  const logout = async () => {
    try {
      // Note: API.ts doesn't have a logout method, so just clear local state
      // If the API had a logout endpoint, we would call it here
    } catch (error) {
      console.error('Logout error:', error);
      // Continue with logout even if API call fails
    } finally {
      setUser(null);
    }
  };

  useEffect(() => {
    checkAuth();
  }, []);

  return (
    <AuthContext.Provider value={{ user, isLoading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
