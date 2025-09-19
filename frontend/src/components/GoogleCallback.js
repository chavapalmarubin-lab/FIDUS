import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Loader2, CheckCircle, AlertCircle } from 'lucide-react';

const GoogleCallback = () => {
  const [status, setStatus] = useState('processing');
  const [message, setMessage] = useState('Processing Google authentication...');
  const [profile, setProfile] = useState(null);

  useEffect(() => {
    const processCallback = async () => {
      try {
        setStatus('processing');
        setMessage('Processing Google authentication...');

        // Get URL parameters (Google OAuth sends code and state as URL params)
        const urlParams = new URLSearchParams(window.location.search);
        const code = urlParams.get('code');
        const state = urlParams.get('state');
        const error = urlParams.get('error');

        if (error) {
          throw new Error(`Google OAuth error: ${error}`);
        }

        if (!code) {
          throw new Error('No authorization code received from Google');
        }

        console.log('Processing Google OAuth callback with code:', code.substring(0, 20) + '...');

        try {
          const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/google/process-callback`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({ 
              code: code,
              state: state 
            })
          });

          const data = await response.json();

          if (response.ok && data.success) {
            setStatus('success');
            setMessage(`Successfully authenticated as ${data.profile.name}`);
            setProfile(data.profile);
            
            console.log('✅ Google authentication successful:', data.profile);
            
            // Clean URL parameters
            window.history.replaceState({}, document.title, window.location.pathname);
            
            // Notify other components
            window.dispatchEvent(new CustomEvent('googleAuthSuccess', { 
              detail: { profile: data.profile, sessionToken: data.session_token }
            }));
            
            // Redirect to admin dashboard after successful authentication
            setTimeout(() => {
              // Simulate admin login by setting the proper state and redirecting
              const adminUser = {
                id: data.profile.id,
                username: data.profile.email,
                name: data.profile.name,
                email: data.profile.email,
                type: "admin",
                picture: data.profile.picture
              };
              
              // Store user data in localStorage for persistence
              localStorage.setItem('user', JSON.stringify(adminUser));
              
              // Redirect to main app with admin state
              window.location.href = '/?admin=true';
            }, 2000);
          } else {
            throw new Error(data.detail || 'Authentication failed');
          }
        } catch (processError) {
          console.error('Callback processing error:', processError);
          setStatus('error');
          setMessage(`Authentication failed: ${processError.message}`);
        }

      } catch (err) {
        console.error('OAuth callback processing error:', err);
        setStatus('error');
        setMessage(`Failed to process Google authentication: ${err.message}`);
      }
    };

    // Process callback immediately
    processCallback();
  }, []);

  const handleReturnToDashboard = () => {
    window.location.href = '/admin/dashboard';
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

          {/* Profile Preview */}
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