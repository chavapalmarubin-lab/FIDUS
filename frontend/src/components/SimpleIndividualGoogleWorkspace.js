import React, { useState, useEffect } from 'react';
import apiAxios from '../utils/apiAxios';

const SimpleIndividualGoogleWorkspace = () => {
  const [activeTab, setActiveTab] = useState('connection');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [googleStatus, setGoogleStatus] = useState(null);
  const [connectingToGoogle, setConnectingToGoogle] = useState(false);

  useEffect(() => {
    checkGoogleConnectionStatus();
    
    // Check for URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const oauthError = urlParams.get('oauth_error');
    
    // Handle OAuth error from URL
    if (oauthError) {
      setError(`OAuth Error: ${decodeURIComponent(oauthError)}`);
      
      // Clean URL
      const baseUrl = window.location.origin + window.location.pathname;
      const newUrl = `${baseUrl}?skip_animation=true`;
      window.history.replaceState({}, '', newUrl);
    }
  }, []);

  const checkGoogleConnectionStatus = async () => {
    try {
      setLoading(true);
      const response = await apiAxios.get('/admin/google/individual-status');
      
      if (response.data.success) {
        setGoogleStatus(response.data);
        console.log('✅ Google connection status:', response.data);
      }
    } catch (err) {
      console.error('❌ Failed to check Google status:', err);
      setError('Failed to check Google connection status');
    } finally {
      setLoading(false);
    }
  };

  const connectGoogleAccount = async () => {
    try {
      setConnectingToGoogle(true);
      setError(null);
      
      console.log('🚀 Initiating individual Google OAuth...');
      
      // Get individual Google OAuth URL
      const response = await apiAxios.get('/admin/google/individual-auth-url');
      
      if (response.data.success && response.data.auth_url) {
        console.log('✅ Redirecting to individual Google OAuth...');
        // Redirect to Google OAuth
        window.location.href = response.data.auth_url;
      } else {
        throw new Error(response.data.error || 'Failed to get OAuth URL');
      }
    } catch (err) {
      console.error('❌ Google connection failed:', err);
      setError(err.response?.data?.detail || err.message || 'Failed to connect Google account');
    } finally {
      setConnectingToGoogle(false);
    }
  };

  const disconnectGoogleAccount = async () => {
    try {
      setLoading(true);
      const response = await apiAxios.post('/admin/google/individual-disconnect');
      
      if (response.data.success) {
        setGoogleStatus(null);
        console.log('✅ Google account disconnected');
        alert('Google account disconnected successfully!');
      } else {
        throw new Error(response.data.message || 'Failed to disconnect');
      }
    } catch (err) {
      console.error('❌ Failed to disconnect:', err);
      setError('Failed to disconnect Google account');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Individual Google Workspace Integration</h2>
        <p className="text-gray-600">
          Each admin connects their personal Google account for Gmail, Calendar, Drive, and Sheets access
        </p>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-red-800">{error}</p>
              <button
                onClick={() => setError(null)}
                className="mt-2 text-sm text-red-600 hover:text-red-500"
              >
                Dismiss
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Connection Status */}
      <div className="bg-white rounded-lg shadow p-6">
        {!googleStatus ? (
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="flex-shrink-0">
                <svg className="h-8 w-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </div>
              <div>
                <h3 className="text-lg font-medium text-gray-900">No Google Account Connected</h3>
                <p className="text-sm text-gray-500">Connect your personal Google account to access Gmail, Calendar, Drive, and Sheets</p>
              </div>
            </div>
            <button
              onClick={connectGoogleAccount}
              disabled={connectingToGoogle}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              {connectingToGoogle ? (
                <>
                  <svg className="animate-spin -ml-1 mr-3 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Connecting...
                </>
              ) : (
                <>
                  <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                  Connect My Google Account
                </>
              )}
            </button>
          </div>
        ) : !googleStatus.connected ? (
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="flex-shrink-0">
                <svg className="h-8 w-8 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </div>
              <div>
                <h3 className="text-lg font-medium text-gray-900">Google Account Not Connected</h3>
                <p className="text-sm text-gray-500">Please connect your Google account to continue</p>
              </div>
            </div>
            <button
              onClick={connectGoogleAccount}
              disabled={connectingToGoogle}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              {connectingToGoogle ? 'Connecting...' : 'Connect Google Account'}
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="flex-shrink-0">
                  <svg className="h-8 w-8 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <div>
                  <h3 className="text-lg font-medium text-gray-900">Google Account Connected</h3>
                  <p className="text-sm text-gray-500">
                    Connected as <strong>{googleStatus.google_info?.name}</strong> ({googleStatus.google_info?.email})
                  </p>
                  <div className="flex items-center space-x-4 mt-2 text-xs text-gray-400">
                    <span>Connected: {new Date(googleStatus.google_info?.connected_at).toLocaleDateString()}</span>
                    {googleStatus.is_expired && (
                      <span className="px-2 py-1 bg-yellow-100 text-yellow-800 rounded-full">Token Expired</span>
                    )}
                  </div>
                </div>
              </div>
              <div className="flex space-x-2">
                {googleStatus.is_expired && (
                  <button
                    onClick={connectGoogleAccount}
                    className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-yellow-600 hover:bg-yellow-700"
                  >
                    Reconnect
                  </button>
                )}
                <button
                  onClick={disconnectGoogleAccount}
                  className="inline-flex items-center px-3 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                >
                  Disconnect
                </button>
              </div>
            </div>
            
            {/* Google Services Status */}
            <div className="grid grid-cols-4 gap-4 mt-4">
              {[
                { name: 'Gmail', connected: googleStatus.scopes?.includes('https://www.googleapis.com/auth/gmail.readonly') },
                { name: 'Calendar', connected: googleStatus.scopes?.includes('https://www.googleapis.com/auth/calendar') },
                { name: 'Drive', connected: googleStatus.scopes?.includes('https://www.googleapis.com/auth/drive') },
                { name: 'Sheets', connected: googleStatus.scopes?.includes('https://www.googleapis.com/auth/spreadsheets') }
              ].map((service) => (
                <div key={service.name} className={`p-3 rounded-lg text-center text-sm ${
                  service.connected ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
                }`}>
                  <div className="font-medium">{service.name}</div>
                  <div className="text-xs">{service.connected ? 'Connected' : 'Not Connected'}</div>
                </div>
              ))}
            </div>

            {/* Connection Details */}
            <div className="border-t pt-4">
              <h4 className="text-lg font-medium text-gray-900 mb-3">Account Details</h4>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="font-medium text-gray-500">Admin User:</span>
                  <p className="text-gray-900">{googleStatus.admin_info?.admin_username}</p>
                </div>
                <div>
                  <span className="font-medium text-gray-500">Google Account:</span>
                  <p className="text-gray-900">{googleStatus.google_info?.email}</p>
                </div>
                <div>
                  <span className="font-medium text-gray-500">Connected Date:</span>
                  <p className="text-gray-900">
                    {new Date(googleStatus.google_info?.connected_at).toLocaleString()}
                  </p>
                </div>
                <div>
                  <span className="font-medium text-gray-500">Token Expires:</span>
                  <p className="text-gray-900">
                    {googleStatus.token_expires_at ? 
                      new Date(googleStatus.token_expires_at).toLocaleString() : 'Unknown'}
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Loading State */}
      {loading && (
        <div className="flex justify-center items-center py-8">
          <svg className="animate-spin h-8 w-8 text-blue-600" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span className="ml-2 text-gray-600">Loading...</span>
        </div>
      )}
    </div>
  );
};

export default SimpleIndividualGoogleWorkspace;