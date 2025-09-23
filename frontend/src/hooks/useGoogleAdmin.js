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

      // Check if we have Google API authentication in localStorage
      const googleApiAuth = localStorage.getItem('google_api_authenticated');
      const userData = localStorage.getItem('fidus_user');
      
      // If we have authentication flag and user data, use it and validate with backend
      if (googleApiAuth === 'true' && userData) {
        try {
          const user = JSON.parse(userData);
          if (user && user.isGoogleAuth && user.googleApiAccess) {
            console.log('Found Google API session in localStorage:', user.email);
            
            // Set the profile from local data first
            setProfile({
              id: user.id,
              email: user.email,
              name: user.name,
              picture: user.picture
            });
            setIsAuthenticated(true);
            
            // Then validate with backend using JWT token
            const jwtToken = localStorage.getItem('fidus_token');
            if (jwtToken) {
              try {
                const response = await fetch(`${API}/admin/google/profile`, {
                  method: 'GET',
                  headers: {
                    'Authorization': `Bearer ${jwtToken}`,
                    'Content-Type': 'application/json'
                  },
                  credentials: 'include'
                });

                if (response.ok) {
                  const data = await response.json();
                  if (data.success && data.profile) {
                    // Update profile with backend data
                    setProfile(data.profile);
                    console.log('✅ Google API session validated with backend:', data.profile.email);
                  }
                }
              } catch (backendError) {
                console.log('Backend validation failed, using local data:', backendError.message);
              }
            }
            
            return;
          }
        } catch (parseError) {
          console.error('Error parsing stored user data:', parseError);
        }
      }

      // If no local authentication, set unauthenticated state
      setIsAuthenticated(false);
      setProfile(null);
      
    } catch (err) {
      console.error('Session check error:', err);
      setIsAuthenticated(false);
      setProfile(null);
    } finally {
      setLoading(false);
    }
  };

  const loginWithGoogle = async () => {
    try {
      setLoading(true);
      setError(null);

      // Get JWT token for admin authentication
      const jwtToken = localStorage.getItem('fidus_token');
      
      if (!jwtToken) {
        throw new Error('Admin authentication required');
      }

      // Use the working Emergent OAuth integration that was functioning before
      console.log('Using Emergent OAuth integration for Google...');
      
      const response = await fetch(`${API}/admin/google/oauth-session-id`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${jwtToken}`,
          'Content-Type': 'application/json'
        },
        credentials: 'include'
      });

      const data = await response.json();
      
      if (data.success && data.session_id) {
        // Use Emergent OAuth session approach that was working
        const sessionUrl = `https://api.emergentagent.com/oauth/google/initiate?session_id=${data.session_id}&redirect_uri=${encodeURIComponent(window.location.origin + '/admin')}`;
        console.log('Redirecting to working Emergent OAuth...');
        window.location.href = sessionUrl;
      } else {
        throw new Error(data.detail || 'Failed to get OAuth session');
      }
    } catch (err) {
      console.error('Google OAuth error:', err);
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
          'Content-Type': 'application/json',
          'X-Session-ID': sessionId  // Use X-Session-ID header as per Emergent OAuth spec
        },
        credentials: 'include'
      });

      const data = await response.json();

      if (response.ok && data.success) {
        setProfile(data.profile);
        setIsAuthenticated(true);
        
        // Store session data in localStorage for persistence
        localStorage.setItem('google_session_token', data.session_token);
        localStorage.setItem('fidus_user', JSON.stringify({
          ...data.profile,
          isGoogleAuth: true
        }));
        
        console.log('✅ Emergent OAuth authentication successful:', data.profile.email);
        
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

  const logoutGoogle = () => {
    setProfile(null);
    setIsAuthenticated(false);
    setError(null);
    
    // Clear Google API authentication data
    localStorage.removeItem('google_api_authenticated');
    localStorage.removeItem('google_session_token'); // Legacy cleanup
    
    // Keep the main fidus_user if it's not a Google-only login
    const userData = localStorage.getItem('fidus_user');
    if (userData) {
      try {
        const user = JSON.parse(userData);
        if (user.isGoogleAuth) {
          // If this was a Google-only login, clear everything
          localStorage.removeItem('fidus_user');
        } else {
          // Otherwise, just remove Google-specific properties
          delete user.isGoogleAuth;
          delete user.googleApiAccess;
          delete user.picture;
          localStorage.setItem('fidus_user', JSON.stringify(user));
        }
      } catch (err) {
        console.error('Error cleaning up user data:', err);
      }
    }
  };

  return {
    profile,
    loading,
    error,
    isAuthenticated,
    loginWithGoogle,
    logout,
    logoutGoogle,
    refreshProfile,
    clearError: () => setError(null)
  };
};

export default useGoogleAdmin;