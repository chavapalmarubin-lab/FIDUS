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
        setMessage('Processing Google authentication...');
        
        // Check if we have a session_id in the URL hash or query params
        const hash = window.location.hash;
        const search = window.location.search;
        
        console.log('URL hash:', hash);
        console.log('URL search:', search);
        
        let sessionId = null;
        
        // Try to extract session_id from hash first
        if (hash) {
          const sessionIdMatch = hash.match(/session_id=([^&]+)/);
          if (sessionIdMatch) {
            sessionId = sessionIdMatch[1];
          }
        }
        
        // Fallback to query parameters
        if (!sessionId && search) {
          const urlParams = new URLSearchParams(search);
          sessionId = urlParams.get('session_id');
        }

        if (!sessionId) {
          setStatus('error');
          setMessage('No authentication data received from Google. Please try again.');
          return;
        }

        console.log('Processing session ID:', sessionId);
        setMessage('Validating authentication with Google...');

        // Now process the session ID using the Google admin hook
        try {
          const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/google/process-session`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${localStorage.getItem('fidus_user') ? JSON.parse(localStorage.getItem('fidus_user')).token : ''}`
            },
            credentials: 'include',
            body: JSON.stringify({ session_id: sessionId })
          });

          const data = await response.json();

          if (response.ok && data.success) {
            setStatus('success');
            setMessage(`Successfully authenticated as ${data.profile.name}`);
            
            // Store the Google profile info if needed
            console.log('Google authentication successful:', data.profile);
            
            // Redirect to admin dashboard after 3 seconds
            setTimeout(() => {
              window.location.href = '/?skip_animation=true';
            }, 3000);
          } else {
            throw new Error(data.detail || 'Authentication failed');
          }
        } catch (processError) {
          console.error('Session processing error:', processError);
          setStatus('error');
          setMessage(`Authentication failed: ${processError.message}`);
        }

      } catch (err) {
        console.error('Callback processing error:', err);
        setStatus('error');
        setMessage('Failed to process authentication');
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