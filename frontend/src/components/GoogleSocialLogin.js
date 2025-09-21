import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { LogIn, RefreshCw } from 'lucide-react';

const GoogleSocialLogin = ({ onLoginSuccess, redirectTo = '/dashboard' }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleGoogleLogin = async () => {
    try {
      setLoading(true);
      setError(null);

      // Get Google login URL from backend
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/auth/google/login-url`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      const data = await response.json();

      if (response.ok && data.success) {
        // Redirect to Google OAuth via Emergent
        window.location.href = data.login_url;
      } else {
        throw new Error(data.detail || 'Failed to get login URL');
      }

    } catch (err) {
      console.error('Google login error:', err);
      setError(err.message);
      setLoading(false);
    }
  };

  // Process session ID from URL fragment after OAuth callback
  useEffect(() => {
    const processSessionId = async () => {
      // Check if there's a session_id in the URL fragment
      const fragment = window.location.hash.substring(1);
      const params = new URLSearchParams(fragment);
      const sessionId = params.get('session_id');

      if (sessionId) {
        try {
          setLoading(true);
          console.log('Processing session ID from OAuth callback:', sessionId);

          // Call backend to process the session
          const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/auth/google/process-session`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-Session-ID': sessionId
            },
            credentials: 'include'
          });

          const data = await response.json();

          if (response.ok && data.success) {
            // Store user data and token
            localStorage.setItem('fidus_user', JSON.stringify(data.user));
            localStorage.setItem('fidus_token', data.token);

            // Clear the URL fragment
            window.history.replaceState({}, document.title, window.location.pathname);

            console.log('✅ Google social login successful:', data.user.email);

            // Call success callback if provided
            if (onLoginSuccess) {
              onLoginSuccess(data.user, data.token);
            }

            // Navigate to dashboard or specified redirect
            navigate(redirectTo);

          } else {
            throw new Error(data.detail || 'Authentication failed');
          }

        } catch (err) {
          console.error('Session processing error:', err);
          setError(err.message);
          // Clear the URL fragment even on error
          window.history.replaceState({}, document.title, window.location.pathname);
        } finally {
          setLoading(false);
        }
      }
    };

    processSessionId();
  }, [navigate, onLoginSuccess, redirectTo]);

  return (
    <div className="google-social-login">
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-3 mb-4">
          <div className="text-red-800 text-sm">
            <strong>Authentication Error:</strong> {error}
          </div>
        </div>
      )}

      <button
        onClick={handleGoogleLogin}
        disabled={loading}
        className="w-full flex items-center justify-center px-4 py-3 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? (
          <>
            <RefreshCw className="h-5 w-5 mr-3 animate-spin" />
            {loading && window.location.hash.includes('session_id') ? 'Completing login...' : 'Connecting to Google...'}
          </>
        ) : (
          <>
            <svg className="h-5 w-5 mr-3" viewBox="0 0 24 24">
              <path
                fill="#4285F4"
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              />
              <path
                fill="#34A853"
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              />
              <path
                fill="#FBBC05"
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
              />
              <path
                fill="#EA4335"
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
              />
            </svg>
            Continue with Google
          </>
        )}
      </button>

      <div className="mt-3 text-xs text-gray-500 text-center">
        By continuing, you agree to our Terms of Service and Privacy Policy
      </div>
    </div>
  );
};

export default GoogleSocialLogin;