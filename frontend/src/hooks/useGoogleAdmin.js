import { useState, useEffect } from 'react';
import apiAxios from '../utils/apiAxios';

const useGoogleAdmin = () => {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Check authentication status on mount
  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      // Check localStorage for authentication flag
      const googleAuth = localStorage.getItem('google_api_authenticated');
      const authCompleted = localStorage.getItem('google_auth_completed');
      
      console.log('🔍 Checking Google auth status:', { googleAuth, authCompleted });
      
      if (googleAuth === 'true') {
        setIsAuthenticated(true);
        
        // Try to get profile from API
        try {
          const response = await apiAxios.get('/admin/google/profile');
          if (response.data.success && response.data.profile) {
            setProfile(response.data.profile);
            console.log('✅ Google profile loaded:', response.data.profile);
          }
        } catch (err) {
          console.log('ℹ️ Profile not available, but authentication exists');
          // Still keep authenticated status but without profile
        }
      } else {
        setIsAuthenticated(false);
        setProfile(null);
      }
    } catch (err) {
      console.error('Error checking Google auth status:', err);
      setError('Failed to check authentication status');
    }
  };

  const loginWithGoogle = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Get Google OAuth URL
      const response = await apiAxios.get('/auth/google/url');
      
      if (response.data.success && response.data.auth_url) {
        console.log('🚀 Redirecting to Google OAuth...');
        window.location.href = response.data.auth_url;
      } else {
        throw new Error(response.data.error || 'Failed to get OAuth URL');
      }
    } catch (err) {
      console.error('Google login error:', err);
      setError(err.message || 'Failed to initiate Google login');
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      setLoading(true);
      
      // Clear local storage
      localStorage.removeItem('google_api_authenticated');
      localStorage.removeItem('google_auth_completed');
      localStorage.removeItem('google_session_token');
      
      // Reset state
      setIsAuthenticated(false);
      setProfile(null);
      setError(null);
      
      // Call logout endpoint
      try {
        await apiAxios.post('/admin/google/logout');
      } catch (err) {
        console.log('Logout API call failed, but local state cleared');
      }
      
      console.log('✅ Google authentication cleared');
    } catch (err) {
      console.error('Logout error:', err);
      setError('Failed to logout completely');
    } finally {
      setLoading(false);
    }
  };

  const refreshAuth = () => {
    checkAuthStatus();
  };

  return {
    profile,
    loading,
    error,
    isAuthenticated,
    loginWithGoogle,
    logout,
    refreshAuth
  };
};

export default useGoogleAdmin;