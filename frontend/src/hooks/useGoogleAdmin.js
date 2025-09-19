import { useState, useEffect, useCallback } from 'react';
import { getAuthHeaders, getCurrentUser, getAuthToken } from '../utils/auth';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const useGoogleAdmin = () => {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Check for existing session on mount
  useEffect(() => {
    checkExistingSession();
    
    // Listen for authentication success events from callback
    const handleAuthSuccess = (event) => {
      console.log('✅ Google auth success event received:', event.detail);
      setProfile(event.detail.profile);
      setIsAuthenticated(true);
      setLoading(false);
      setError(null);
    };
    
    window.addEventListener('googleAuthSuccess', handleAuthSuccess);
    
    return () => {
      window.removeEventListener('googleAuthSuccess', handleAuthSuccess);
    };
  }, []);

  // Check for session ID in URL fragment (Emergent OAuth callback)
  useEffect(() => {
    const processSessionFromURL = async () => {
      const fragment = window.location.hash;
      const sessionIdMatch = fragment.match(/session_id=([^&]+)/);
      
      if (sessionIdMatch) {
        const sessionId = sessionIdMatch[1];
        console.log('Found session_id in URL fragment:', sessionId.substring(0, 20) + '...');
        
        setLoading(true);
        setError(null);
        
        try {
          await processSessionId(sessionId);
          // Clean URL fragment after processing
          window.history.replaceState({}, document.title, window.location.pathname + window.location.search);
        } catch (err) {
          console.error('Failed to process session from URL:', err);
          setError('Failed to process authentication');
        }
      }
    };

    processSessionFromURL();
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
          console.log('✅ Existing Google session found:', data.profile.email);
        }
      } else if (response.status !== 401) {
        console.log('Session check failed:', response.status);
      }
    } catch (err) {
      console.error('Session check error:', err);
    } finally {
      setLoading(false);
    }
  };

  const loginWithGoogle = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Get JWT token for admin authentication
      const jwtToken = getAuthToken();
      if (!jwtToken) {
        throw new Error('Admin not authenticated. Please login first.');
      }
      
      const response = await fetch(`${API}/admin/google/auth-url`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${jwtToken}`,
          'Content-Type': 'application/json'
        }
      });

      const data = await response.json();
      
      if (data.success && data.auth_url) {
        // Redirect to Emergent OAuth
        window.location.href = data.auth_url;
      } else {
        throw new Error(data.detail || 'Failed to get auth URL');
      }
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
        
        // Set httpOnly cookie via response headers (backend handles this)
        console.log('✅ Google authentication successful:', data.profile.email);
        
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

      if (response.ok) {
        setProfile(null);
        setIsAuthenticated(false);
        console.log('✅ Google logout successful');
      } else {
        const data = await response.json();
        throw new Error(data.detail || 'Logout failed');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
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
    refreshProfile,
    clearError: () => setError(null)
  };
};

export default useGoogleAdmin;