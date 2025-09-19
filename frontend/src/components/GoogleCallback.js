import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Loader2, CheckCircle, AlertCircle } from 'lucide-react';

const GoogleCallback = () => {
  const [status, setStatus] = useState('processing'); // processing, success, error
  const [message, setMessage] = useState('Processing Google authentication...');
  const [profile, setProfile] = useState(null);

  useEffect(() => {
    const processCallback = async () => {
      try {
        setStatus('processing');
        setMessage('Processing Google authentication...');

        // Check for Emergent OAuth session_id in URL fragment first
        const fragment = window.location.hash;
        const sessionIdMatch = fragment.match(/session_id=([^&]+)/);
        
        if (sessionIdMatch) {
          const sessionId = sessionIdMatch[1];
          console.log('Found Emergent OAuth session_id:', sessionId.substring(0, 20) + '...');
          console.log('Backend URL:', process.env.REACT_APP_BACKEND_URL);

          try {
            console.log('Sending session request to:', `${process.env.REACT_APP_BACKEND_URL}/api/admin/google/process-session`);
            
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/google/process-session`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json'
              },
              credentials: 'include',
              body: JSON.stringify({ 
                session_id: sessionId
              })
            });

            console.log('Response status:', response.status);
            const data = await response.json();
            console.log('Response data:', data);

            if (response.ok && data.success) {
              setStatus('success');
              setMessage(`Successfully authenticated as ${data.profile.name}`);
              setProfile(data.profile);
              
              // Store session token
              localStorage.setItem('google_session_token', data.session_token);
              
              console.log('Emergent OAuth authentication successful:', data.profile);
              
              // Clean URL fragment
              window.history.replaceState({}, document.title, window.location.pathname + window.location.search);
              
              // Trigger a custom event to notify other components about the authentication
              window.dispatchEvent(new CustomEvent('googleAuthSuccess', { 
                detail: { profile: data.profile, sessionToken: data.session_token }
              }));
              
              // Redirect to admin dashboard after 2 seconds
              setTimeout(() => {
                window.location.href = '/?skip_animation=true';
              }, 2000);
            } else {
              throw new Error(data.detail || 'Emergent OAuth authentication failed');
            }
          } catch (sessionError) {
            console.error('Session processing error:', sessionError);
            setStatus('error');
            setMessage(`Authentication failed: ${sessionError.message}`);
          }
          
          return; // Exit early for Emergent OAuth
        }

        // Fallback: Check for test mode
        const urlParams = new URLSearchParams(window.location.search);
        const testMode = urlParams.get('test');

        if (testMode === 'true') {
          console.log('Running in test mode...');
          console.log('Backend URL:', process.env.REACT_APP_BACKEND_URL);

          try {
            console.log('Sending test request to:', `${process.env.REACT_APP_BACKEND_URL}/api/admin/google/test-callback`);
            
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/google/test-callback`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json'
              },
              credentials: 'include',
              body: JSON.stringify({})
            });

            const data = await response.json();

            if (response.ok && data.success) {
              setStatus('success');
              setMessage(`Successfully authenticated as ${data.user_info.name} (TEST MODE)`);
              setProfile(data.user_info);
              
              localStorage.setItem('google_session_token', data.session_token);
              
              setTimeout(() => {
                window.location.href = '/?skip_animation=true';
              }, 3000);
            } else {
              throw new Error(data.detail || 'Test authentication failed');
            }
          } catch (testError) {
            setStatus('error');
            setMessage(`Test authentication failed: ${testError.message}`);
          }
          
          return; // Exit early for test mode
        }

        // If no session_id or test mode, show error
        throw new Error('No authentication data received. Please try signing in again.');

      } catch (err) {
        console.error('OAuth callback processing error:', err);
        setStatus('error');
        setMessage(`Failed to process Google authentication: ${err.message}`);
      }
    };

    // Wait a bit before processing to ensure the page is fully loaded
    const timer = setTimeout(processCallback, 1000);
    return () => clearTimeout(timer);
  }, []);

  const handleReturnToDashboard = () => {
    window.location.href = '/?skip_animation=true';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-slate-800 p-8 rounded-lg border border-slate-600 shadow-2xl max-w-md w-full mx-4"
      >
        <div className="text-center">
          {/* Status Icon */}
          <div className="mb-6">
            {status === 'processing' && (
              <Loader2 className="w-16 h-16 animate-spin text-blue-600 mx-auto" />
            )}
            {status === 'success' && (
              <CheckCircle className="w-16 h-16 text-green-600 mx-auto" />
            )}
            {status === 'error' && (
              <AlertCircle className="w-16 h-16 text-red-600 mx-auto" />
            )}
          </div>

          {/* FIDUS Branding */}
          <h1 className="text-2xl font-bold text-white mb-2">FIDUS</h1>
          <p className="text-slate-400 mb-6">Google Integration</p>

          {/* Status Message */}
          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-white">
              {status === 'processing' && 'Authenticating...'}
              {status === 'success' && 'Authentication Successful!'}
              {status === 'error' && 'Authentication Failed'}
            </h2>
            
            <p className="text-slate-300 text-sm">
              {message}
            </p>

            {status === 'success' && (
              <div className="mt-4 p-3 bg-green-900/30 border border-green-600/30 rounded-lg">
                <p className="text-green-400 text-sm">
                  Redirecting to admin dashboard...
                </p>
              </div>
            )}

            {status === 'error' && (
              <div className="mt-4 space-y-3">
                <div className="p-3 bg-red-900/30 border border-red-600/30 rounded-lg">
                  <p className="text-red-400 text-sm">
                    Please try again or contact support if the problem persists.
                  </p>
                </div>
                
                <button
                  onClick={handleReturnToDashboard}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-lg transition-colors"
                >
                  Return to Admin Dashboard
                </button>
              </div>
            )}
          </div>

          {/* Profile Preview (if available) */}
          {status === 'success' && profile && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="mt-6 p-4 bg-slate-700 rounded-lg border border-slate-600"
            >
              <div className="flex items-center gap-3">
                {profile.picture ? (
                  <img 
                    src={profile.picture} 
                    alt={profile.name}
                    className="w-10 h-10 rounded-full"
                  />
                ) : (
                  <div className="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center">
                    <span className="text-white font-medium">
                      {profile.name ? profile.name.charAt(0).toUpperCase() : 'U'}
                    </span>
                  </div>
                )}
                <div className="text-left">
                  <p className="text-white font-medium">{profile.name}</p>
                  <p className="text-slate-400 text-sm">{profile.email}</p>
                </div>
              </div>
            </motion.div>
          )}
        </div>
      </motion.div>
    </div>
  );
};

export default GoogleCallback;