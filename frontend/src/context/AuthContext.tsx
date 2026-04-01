import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import axios from 'axios';
import Constants from 'expo-constants';

// Use the backend URL from environment
const API_BASE = Constants.expoConfig?.extra?.EXPO_PUBLIC_BACKEND_URL || 
                 process.env.EXPO_PUBLIC_BACKEND_URL || 
                 'https://retail-investor-hub.preview.emergentagent.com';

interface PaymentScheduleItem {
  month: string;
  amount: number;
  status: 'Funded' | 'Pending';
}

interface User {
  id: string;
  name: string;
  email: string;
  balance: number;
  totalEarnings: number;
  monthlyReturn: number;
  paymentSchedule: PaymentScheduleItem[];
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<boolean>;
  logout: () => Promise<void>;
  refreshUserData: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const AUTH_TOKEN_KEY = '@fidus_auth_token';
const USER_DATA_KEY = '@fidus_user_data';

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadStoredAuth();
  }, []);

  const loadStoredAuth = async () => {
    try {
      const [token, userData] = await Promise.all([
        AsyncStorage.getItem(AUTH_TOKEN_KEY),
        AsyncStorage.getItem(USER_DATA_KEY),
      ]);

      if (token && userData) {
        const parsedUser = JSON.parse(userData);
        setUser(parsedUser);
        // Refresh data in background
        refreshUserDataInternal(token);
      }
    } catch (error) {
      console.error('Error loading stored auth:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (email: string, password: string): Promise<boolean> => {
    try {
      console.log('Attempting login to:', `${API_BASE}/api/auth/login`);
      
      const response = await axios.post(`${API_BASE}/api/auth/login`, {
        email: email.toLowerCase(),
        password,
      }, {
        timeout: 15000,
        headers: {
          'Content-Type': 'application/json',
        }
      });

      console.log('Login response:', response.data);

      if (response.data && response.data.success) {
        const { token, user: userData } = response.data;
        
        const transformedUser: User = {
          id: userData.id,
          name: userData.name,
          email: userData.email,
          balance: userData.balance,
          totalEarnings: userData.totalEarnings,
          monthlyReturn: userData.monthlyReturn,
          paymentSchedule: userData.paymentSchedule || [],
        };

        await Promise.all([
          AsyncStorage.setItem(AUTH_TOKEN_KEY, token),
          AsyncStorage.setItem(USER_DATA_KEY, JSON.stringify(transformedUser)),
        ]);

        setUser(transformedUser);
        return true;
      }
      return false;
    } catch (error: any) {
      console.error('Login error:', error?.response?.data || error.message);
      return false;
    }
  };

  const logout = async () => {
    try {
      const token = await AsyncStorage.getItem(AUTH_TOKEN_KEY);
      
      if (token) {
        try {
          await axios.post(`${API_BASE}/api/auth/logout`, {}, {
            headers: { Authorization: `Bearer ${token}` },
            timeout: 5000,
          });
        } catch (e) {
          // Ignore logout API errors
        }
      }
      
      await Promise.all([
        AsyncStorage.removeItem(AUTH_TOKEN_KEY),
        AsyncStorage.removeItem(USER_DATA_KEY),
      ]);
      setUser(null);
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  const refreshUserDataInternal = async (token: string) => {
    try {
      const response = await axios.get(`${API_BASE}/api/user/profile`, {
        headers: { Authorization: `Bearer ${token}` },
        timeout: 10000,
      });

      if (response.data) {
        const userData = response.data;
        const transformedUser: User = {
          id: userData.id,
          name: userData.name,
          email: userData.email,
          balance: userData.balance,
          totalEarnings: userData.totalEarnings,
          monthlyReturn: userData.monthlyReturn,
          paymentSchedule: userData.paymentSchedule || [],
        };

        await AsyncStorage.setItem(USER_DATA_KEY, JSON.stringify(transformedUser));
        setUser(transformedUser);
      }
    } catch (error) {
      console.error('Error refreshing user data:', error);
    }
  };

  const refreshUserData = async () => {
    const token = await AsyncStorage.getItem(AUTH_TOKEN_KEY);
    if (token) {
      await refreshUserDataInternal(token);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        logout,
        refreshUserData,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
