import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import axios from 'axios';
import Constants from 'expo-constants';
import { Platform } from 'react-native';

// Conditionally import native-only modules
let SecureStore: any = null;
let LocalAuthentication: any = null;

if (Platform.OS !== 'web') {
  SecureStore = require('expo-secure-store');
  LocalAuthentication = require('expo-local-authentication');
}

// Use the backend URL from environment
const API_BASE = Constants.expoConfig?.extra?.EXPO_PUBLIC_BACKEND_URL || 
                 process.env.EXPO_PUBLIC_BACKEND_URL || 
                 'https://retail-investor-hub.preview.emergentagent.com';

interface PaymentScheduleItem {
  month: string;
  amount: number;
  status: 'Funded' | 'Pending';
}

interface NotificationPreferences {
  payment_reminders: boolean;
  deposit_alerts: boolean;
  monthly_reports: boolean;
  push_enabled: boolean;
}

interface User {
  id: string;
  name: string;
  email: string;
  phone?: string;
  balance: number;
  totalEarnings: number;
  monthlyReturn: number;
  biometricEnabled: boolean;
  termsAccepted: boolean;
  termsAcceptedAt?: string;
  notificationPreferences: NotificationPreferences;
  paymentSchedule: PaymentScheduleItem[];
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  biometricAvailable: boolean;
  login: (email: string, password: string) => Promise<boolean>;
  loginWithBiometric: () => Promise<boolean>;
  logout: () => Promise<void>;
  refreshUserData: () => Promise<void>;
  updateProfile: (name: string, phone: string) => Promise<boolean>;
  changePassword: (currentPassword: string, newPassword: string) => Promise<boolean>;
  toggleBiometric: (enabled: boolean) => Promise<boolean>;
  updateNotificationPreferences: (prefs: Partial<NotificationPreferences>) => Promise<boolean>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const AUTH_TOKEN_KEY = '@fidus_auth_token';
const USER_DATA_KEY = '@fidus_user_data';
const BIOMETRIC_CREDENTIALS_KEY = 'fidus_biometric_creds';

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [biometricAvailable, setBiometricAvailable] = useState(false);

  useEffect(() => {
    checkBiometricAvailability();
    loadStoredAuth();
  }, []);

  const checkBiometricAvailability = async () => {
    try {
      const compatible = await LocalAuthentication.hasHardwareAsync();
      const enrolled = await LocalAuthentication.isEnrolledAsync();
      setBiometricAvailable(compatible && enrolled);
    } catch (error) {
      console.error('Error checking biometric availability:', error);
      setBiometricAvailable(false);
    }
  };

  const loadStoredAuth = async () => {
    try {
      const [token, userData] = await Promise.all([
        AsyncStorage.getItem(AUTH_TOKEN_KEY),
        AsyncStorage.getItem(USER_DATA_KEY),
      ]);

      if (token && userData) {
        const parsedUser = JSON.parse(userData);
        setUser(parsedUser);
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
        headers: { 'Content-Type': 'application/json' }
      });

      if (response.data && response.data.success) {
        const { token, user: userData } = response.data;
        
        const transformedUser: User = {
          id: userData.id,
          name: userData.name,
          email: userData.email,
          phone: userData.phone,
          balance: userData.balance,
          totalEarnings: userData.totalEarnings,
          monthlyReturn: userData.monthlyReturn,
          biometricEnabled: userData.biometricEnabled || false,
          termsAccepted: userData.termsAccepted || false,
          termsAcceptedAt: userData.termsAcceptedAt,
          notificationPreferences: userData.notificationPreferences || {
            payment_reminders: true,
            deposit_alerts: true,
            monthly_reports: true,
            push_enabled: true,
          },
          paymentSchedule: userData.paymentSchedule || [],
        };

        await Promise.all([
          AsyncStorage.setItem(AUTH_TOKEN_KEY, token),
          AsyncStorage.setItem(USER_DATA_KEY, JSON.stringify(transformedUser)),
        ]);

        // Store credentials for biometric login if enabled
        if (transformedUser.biometricEnabled && Platform.OS !== 'web') {
          try {
            await SecureStore.setItemAsync(BIOMETRIC_CREDENTIALS_KEY, JSON.stringify({ email, password }));
          } catch (e) {
            console.log('Could not store biometric credentials');
          }
        }

        setUser(transformedUser);
        return true;
      }
      return false;
    } catch (error: any) {
      console.error('Login error:', error?.response?.data || error.message);
      return false;
    }
  };

  const loginWithBiometric = async (): Promise<boolean> => {
    try {
      if (Platform.OS === 'web') {
        return false;
      }

      const result = await LocalAuthentication.authenticateAsync({
        promptMessage: 'Authenticate to login',
        fallbackLabel: 'Use password',
        disableDeviceFallback: false,
      });

      if (result.success) {
        const credentialsStr = await SecureStore.getItemAsync(BIOMETRIC_CREDENTIALS_KEY);
        if (credentialsStr) {
          const { email, password } = JSON.parse(credentialsStr);
          return await login(email, password);
        }
      }
      return false;
    } catch (error) {
      console.error('Biometric login error:', error);
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
        } catch (e) {}
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
          phone: userData.phone,
          balance: userData.balance,
          totalEarnings: userData.totalEarnings,
          monthlyReturn: userData.monthlyReturn,
          biometricEnabled: userData.biometricEnabled || false,
          termsAccepted: userData.termsAccepted || false,
          termsAcceptedAt: userData.termsAcceptedAt,
          notificationPreferences: userData.notificationPreferences || {
            payment_reminders: true,
            deposit_alerts: true,
            monthly_reports: true,
            push_enabled: true,
          },
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

  const updateProfile = async (name: string, phone: string): Promise<boolean> => {
    try {
      const token = await AsyncStorage.getItem(AUTH_TOKEN_KEY);
      if (!token) return false;

      await axios.put(`${API_BASE}/api/user/profile`, { name, phone }, {
        headers: { Authorization: `Bearer ${token}` },
        timeout: 10000,
      });

      if (user) {
        const updatedUser = { ...user, name, phone };
        await AsyncStorage.setItem(USER_DATA_KEY, JSON.stringify(updatedUser));
        setUser(updatedUser);
      }
      return true;
    } catch (error) {
      console.error('Update profile error:', error);
      return false;
    }
  };

  const changePassword = async (currentPassword: string, newPassword: string): Promise<boolean> => {
    try {
      const token = await AsyncStorage.getItem(AUTH_TOKEN_KEY);
      if (!token) return false;

      await axios.post(`${API_BASE}/api/user/change-password`, 
        { current_password: currentPassword, new_password: newPassword },
        { headers: { Authorization: `Bearer ${token}` }, timeout: 10000 }
      );

      // Update stored biometric credentials if enabled
      if (user?.biometricEnabled && Platform.OS !== 'web') {
        try {
          await SecureStore.setItemAsync(BIOMETRIC_CREDENTIALS_KEY, 
            JSON.stringify({ email: user.email, password: newPassword }));
        } catch (e) {}
      }

      return true;
    } catch (error) {
      console.error('Change password error:', error);
      return false;
    }
  };

  const toggleBiometric = async (enabled: boolean): Promise<boolean> => {
    try {
      const token = await AsyncStorage.getItem(AUTH_TOKEN_KEY);
      if (!token) return false;

      await axios.put(`${API_BASE}/api/user/biometric?enabled=${enabled}`, {}, {
        headers: { Authorization: `Bearer ${token}` },
        timeout: 10000,
      });

      if (user) {
        const updatedUser = { ...user, biometricEnabled: enabled };
        await AsyncStorage.setItem(USER_DATA_KEY, JSON.stringify(updatedUser));
        setUser(updatedUser);
      }

      if (!enabled && Platform.OS !== 'web') {
        try {
          await SecureStore.deleteItemAsync(BIOMETRIC_CREDENTIALS_KEY);
        } catch (e) {}
      }

      return true;
    } catch (error) {
      console.error('Toggle biometric error:', error);
      return false;
    }
  };

  const updateNotificationPreferences = async (prefs: Partial<NotificationPreferences>): Promise<boolean> => {
    try {
      const token = await AsyncStorage.getItem(AUTH_TOKEN_KEY);
      if (!token) return false;

      await axios.put(`${API_BASE}/api/user/notifications`, prefs, {
        headers: { Authorization: `Bearer ${token}` },
        timeout: 10000,
      });

      if (user) {
        const updatedUser = {
          ...user,
          notificationPreferences: { ...user.notificationPreferences, ...prefs },
        };
        await AsyncStorage.setItem(USER_DATA_KEY, JSON.stringify(updatedUser));
        setUser(updatedUser);
      }
      return true;
    } catch (error) {
      console.error('Update notifications error:', error);
      return false;
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        biometricAvailable,
        login,
        loginWithBiometric,
        logout,
        refreshUserData,
        updateProfile,
        changePassword,
        toggleBiometric,
        updateNotificationPreferences,
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
