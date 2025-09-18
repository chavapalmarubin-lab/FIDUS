import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Loader2, CheckCircle, AlertCircle } from 'lucide-react';
import useGoogleAdmin from '../hooks/useGoogleAdmin';

const GoogleCallback = () => {
  const [status, setStatus] = useState('processing'); // processing, success, error
  const [message, setMessage] = useState('Processing Google authentication...');
  const { profile, loading, error, isAuthenticated } = useGoogleAdmin();

  useEffect(() => {
    // The useGoogleAdmin hook will automatically handle the session_id from URL
    // and process the authentication
    
    const timer = setTimeout(() => {
      if (isAuthenticated && profile) {
        setStatus('success');
        setMessage(`Successfully authenticated as ${profile.name}`);
        
        // Redirect to admin dashboard after 2 seconds
        setTimeout(() => {
          window.location.href = '/admin';
        }, 2000);
      } else if (error) {
        setStatus('error');
        setMessage(error);
      }
    }, 1000);

    return () => clearTimeout(timer);
  }, [isAuthenticated, profile, error]);

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
                  onClick={() => window.location.href = '/admin'}
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
                      {profile.name.charAt(0).toUpperCase()}
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