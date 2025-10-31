import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Loader2, CheckCircle, AlertCircle } from 'lucide-react';

const GoogleCallback = () => {
  const [status, setStatus] = useState('processing');
  const [message, setMessage] = useState('Processing Google authentication...');

  useEffect(() => {
    const processCallback = async () => {
      try {
        // Get URL parameters
        const urlParams = new URLSearchParams(window.location.search);
        const code = urlParams.get('code');
        const error = urlParams.get('error');

        if (error) {
          setStatus('error');
          setMessage(`Google OAuth error: ${error}`);
          return;
        }

        if (!code) {
          setStatus('error');
          setMessage('No authorization code received from Google');
          return;
        }

        setMessage('Exchanging authorization code...');

        // Send to backend for real Google OAuth processing
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/google/oauth-callback`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({ code, state: urlParams.get('state') })
        });

        const data = await response.json();

        if (response.ok && data.success) {
          setStatus('success');
          setMessage(`Welcome ${data.user_info?.name || 'User'}!`);

          // Store auth data with the new response format
          const adminUser = {
            id: data.user_info?.id,
            username: data.user_info?.email,
            name: data.user_info?.name,
            email: data.user_info?.email,
            type: "admin",
            picture: data.user_info?.picture,
            isGoogleAuth: true,
            googleApiAccess: true,
            scopes: data.scopes || []
          };

          localStorage.setItem('fidus_user', JSON.stringify(adminUser));
          
          // Set a flag to indicate Google API authentication is complete
          localStorage.setItem('google_api_authenticated', 'true');

          // Simple redirect after success
          setTimeout(() => {
            window.location = '/';
          }, 2000);
        } else {
          setStatus('error');
          setMessage(data.detail || 'Authentication failed');
        }
      } catch (err) {
        setStatus('error');
        setMessage(`Failed to process authentication: ${err.message}`);
      }
    };

    processCallback();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-slate-800 p-8 rounded-lg border border-slate-600 shadow-2xl max-w-md w-full mx-4"
      >
        <div className="text-center">
          <div className="mb-6">
            {status === 'processing' && <Loader2 className="w-16 h-16 animate-spin text-blue-600 mx-auto" />}
            {status === 'success' && <CheckCircle className="w-16 h-16 text-green-600 mx-auto" />}
            {status === 'error' && <AlertCircle className="w-16 h-16 text-red-600 mx-auto" />}
          </div>

          <h1 className="text-2xl font-bold text-white mb-2">FIDUS</h1>
          <p className="text-slate-400 mb-6">Google Integration</p>

          <h2 className="text-lg font-semibold text-white mb-4">
            {status === 'processing' && 'Authenticating...'}
            {status === 'success' && 'Authentication Successful!'}
            {status === 'error' && 'Authentication Failed'}
          </h2>
          
          <p className="text-slate-300 text-sm">{message}</p>

          {status === 'success' && (
            <div className="mt-4 p-3 bg-green-900/30 border border-green-600/30 rounded-lg">
              <p className="text-green-400 text-sm">Redirecting to dashboard...</p>
            </div>
          )}

          {status === 'error' && (
            <button
              onClick={() => window.location.href = '/'}
              className="mt-4 w-full bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-lg transition-colors"
            >
              Return to Dashboard
            </button>
          )}
        </div>
      </motion.div>
    </div>
  );
};

export default GoogleCallback;