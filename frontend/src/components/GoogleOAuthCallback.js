import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { RefreshCw, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import apiAxios from '../utils/apiAxios';

const GoogleOAuthCallback = () => {
  const [status, setStatus] = useState('processing'); // processing, success, error
  const [message, setMessage] = useState('Processing Google OAuth callback...');
  const [details, setDetails] = useState(null);
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    processOAuthCallback();
  }, []);

  const processOAuthCallback = async () => {
    try {
      // Extract code and state from URL params
      const urlParams = new URLSearchParams(location.search);
      const code = urlParams.get('code');
      const state = urlParams.get('state');
      const error = urlParams.get('error');

      // Check for OAuth error
      if (error) {
        setStatus('error');
        setMessage(`OAuth Error: ${error}`);
        
        // Redirect back after showing error
        setTimeout(() => {
          navigate('/admin/google-workspace');
        }, 3000);
        return;
      }

      // Check if we have the required parameters
      if (!code || !state) {
        setStatus('error');
        setMessage('Missing authorization code or state parameter');
        
        setTimeout(() => {
          navigate('/admin/google-workspace');
        }, 3000);
        return;
      }

      console.log('🔄 Processing individual Google OAuth callback...');
      console.log('Code:', code.substring(0, 20) + '...');
      console.log('State:', state);

      // Send callback data to backend
      const response = await apiAxios.post('/admin/google/individual-callback', {
        code: code,
        state: state
      });

      if (response.data.success) {
        setStatus('success');
        setMessage('Google account connected successfully!');
        setDetails(response.data);
        
        console.log('✅ Individual Google OAuth successful:', response.data);
        
        // Redirect to Google Workspace tab after success
        setTimeout(() => {
          navigate('/admin/google-workspace?tab=connection');
        }, 2000);
      } else {
        throw new Error(response.data.message || 'Unknown error occurred');
      }

    } catch (err) {
      console.error('❌ OAuth callback processing failed:', err);
      
      setStatus('error');
      setMessage(err.response?.data?.detail || err.message || 'Failed to process OAuth callback');
      
      // Redirect back after showing error
      setTimeout(() => {
        navigate('/admin/google-workspace');
      }, 3000);
    }
  };

  const getStatusIcon = () => {
    switch (status) {
      case 'processing':
        return <RefreshCw className="w-12 h-12 text-blue-500 animate-spin" />;
      case 'success':
        return <CheckCircle className="w-12 h-12 text-green-500" />;
      case 'error':
        return <XCircle className="w-12 h-12 text-red-500" />;
      default:
        return <AlertCircle className="w-12 h-12 text-gray-500" />;
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case 'processing':
        return 'border-blue-200 bg-blue-50';
      case 'success':
        return 'border-green-200 bg-green-50';
      case 'error':
        return 'border-red-200 bg-red-50';
      default:
        return 'border-gray-200 bg-gray-50';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <Card className={`w-full max-w-md ${getStatusColor()}`}>
        <CardHeader>
          <CardTitle className="text-center">
            Google OAuth Integration
          </CardTitle>
        </CardHeader>
        <CardContent className="text-center space-y-4">
          {getStatusIcon()}
          
          <div>
            <h3 className={`text-lg font-semibold mb-2 ${
              status === 'success' ? 'text-green-800' :
              status === 'error' ? 'text-red-800' :
              'text-blue-800'
            }`}>
              {status === 'processing' ? 'Processing...' :
               status === 'success' ? 'Success!' :
               'Error'}
            </h3>
            
            <p className={`text-sm ${
              status === 'success' ? 'text-green-700' :
              status === 'error' ? 'text-red-700' :
              'text-blue-700'
            }`}>
              {message}
            </p>
          </div>

          {details && status === 'success' && (
            <div className="text-left bg-white p-4 rounded-lg border">
              <h4 className="font-medium text-gray-900 mb-2">Connection Details</h4>
              <div className="space-y-2 text-sm text-gray-600">
                <div>
                  <span className="font-medium">Admin:</span> {details.admin_info?.admin_name} ({details.admin_info?.admin_username})
                </div>
                <div>
                  <span className="font-medium">Google Account:</span> {details.google_info?.email}
                </div>
                <div>
                  <span className="font-medium">Scopes:</span> {details.scopes?.length || 0} permissions granted
                </div>
              </div>
            </div>
          )}

          <div className="text-xs text-gray-500">
            {status === 'processing' ? 'Please wait while we complete the setup...' :
             status === 'success' ? 'Redirecting to Google Workspace...' :
             'Redirecting back...'}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default GoogleOAuthCallback;