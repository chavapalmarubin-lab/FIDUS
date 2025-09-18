import { useState, useEffect, useCallback } from 'react';
import { getCurrentUser } from '../utils/auth';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const useGoogleAdmin = () => {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Get JWT token from existing auth system
  const getAuthHeaders = () => {
    const user = getCurrentUser();
    const token = localStorage.getItem('fidus_token');
    
    const headers = {
      'Content-Type': 'application/json'
    };
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    return headers;
  };

  // Check for existing session on mount
  useEffect(() => {
    checkExistingSession();
  }, []);

  // Check for session ID in URL fragment on mount
  useEffect(() => {
    const handleSessionFromURL = async () => {
      const fragment = window.location.hash;
      const sessionIdMatch = fragment.match(/session_id=([^&]+)/);
      
      if (sessionIdMatch) {
        const sessionId = sessionIdMatch[1];
        setLoading(true);
        
        try {
          await processSessionId(sessionId);
          // Clean URL fragment
          window.history.replaceState({}, document.title, window.location.pathname + window.location.search);
        } catch (err) {
          setError('Failed to process authentication');
        }
      }
    };

    handleSessionFromURL();
  }, []);

  const checkExistingSession = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API}/admin/google/profile`, {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success && data.profile) {
          setProfile(data.profile);
          setIsAuthenticated(true);
        }
      } else if (response.status !== 401) {
        // Only set error for non-401 responses (401 just means not authenticated)
        const errorData = await response.json().catch(() => ({}));
        setError(errorData.detail || 'Failed to check authentication status');
      }
    } catch (err) {
      console.error('Session check error:', err);
      // Don't set error for network issues during session check
    } finally {
      setLoading(false);
    }
  };

  const getGoogleAuthUrl = async () => {
    try {
      const response = await fetch(`${API}/admin/google/auth-url`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      const data = await response.json();
      
      if (data.success) {
        return data.auth_url;
      } else {
        throw new Error(data.detail || 'Failed to get auth URL');
      }
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  const loginWithGoogle = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const authUrl = await getGoogleAuthUrl();
      
      // Redirect to Google OAuth
      window.location.href = authUrl;
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  const processSessionId = async (sessionId) => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API}/admin/google/process-session`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({ session_id: sessionId })
      });

      const data = await response.json();

      if (response.ok && data.success) {
        setProfile(data.profile);
        setIsAuthenticated(true);
        
        // Set session cookie (browser should handle this automatically)
        // The backend sets httpOnly cookie, so we don't need to do anything here
        
        return data.profile;
      } else {
        throw new Error(data.detail || 'Authentication failed');
      }
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API}/admin/google/logout`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      const data = await response.json();

      if (response.ok && data.success) {
        setProfile(null);
        setIsAuthenticated(false);
        
        // Optionally redirect to login page
        // window.location.href = '/admin/login';
      } else {
        throw new Error(data.detail || 'Logout failed');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const sendEmail = async (emailData) => {
    try {
      const response = await fetch(`${API}/admin/google/send-email`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(emailData)
      });

      const data = await response.json();

      if (response.ok && data.success) {
        return data;
      } else {
        throw new Error(data.detail || 'Failed to send email');
      }
    } catch (err) {
      throw err;
    }
  };

  const refreshProfile = useCallback(async () => {
    await checkExistingSession();
  }, []);

  return {
    profile,
    loading,
    error,
    isAuthenticated,
    loginWithGoogle,
    logout,
    sendEmail,
    refreshProfile,
    clearError: () => setError(null)
  };
};

export default useGoogleAdmin;