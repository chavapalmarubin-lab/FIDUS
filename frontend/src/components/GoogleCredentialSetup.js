import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { CheckCircle, AlertCircle, Mail, Settings, User } from 'lucide-react';
import apiAxios from '../utils/apiAxios';

const GoogleCredentialSetup = ({ currentUser, onCredentialsSet }) => {
  const [googleAccount, setGoogleAccount] = useState(null);
  const [showSetup, setShowSetup] = useState(false);
  const [loading, setLoading] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState(null);

  useEffect(() => {
    checkGoogleConnection();
  }, []);

  const checkGoogleConnection = async () => {
    try {
      const response = await apiAxios.get('/admin/google/user-connection-status');
      if (response.data.success && response.data.google_email) {
        setGoogleAccount(response.data.google_email);
        setConnectionStatus(response.data.connection_status);
      } else {
        setShowSetup(true);
      }
    } catch (err) {
      console.error('Failed to check Google connection:', err);
      setShowSetup(true);
    }
  };

  const initiateGoogleOAuth = async () => {
    try {
      setLoading(true);
      const response = await apiAxios.get('/auth/google/url');
      
      if (response.data.success && response.data.auth_url) {
        // Store the current admin info for callback processing
        localStorage.setItem('google_oauth_admin_id', currentUser.id);
        window.location.href = response.data.auth_url;
      } else {
        throw new Error('Failed to get OAuth URL');
      }
    } catch (err) {
      console.error('OAuth initiation failed:', err);
      alert('Failed to initiate Google OAuth: ' + err.message);
      setLoading(false);
    }
  };

  const disconnectGoogle = async () => {
    try {
      setLoading(true);
      await apiAxios.post('/admin/google/disconnect');
      
      setGoogleAccount(null);
      setConnectionStatus(null);
      setShowSetup(true);
      setLoading(false);
    } catch (err) {
      console.error('Disconnect failed:', err);
      alert('Failed to disconnect Google account');
      setLoading(false);
    }
  };

  if (!showSetup && googleAccount) {
    return (
      <Card className="w-full max-w-2xl mx-auto">
        <CardHeader className="pb-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <CheckCircle className="h-6 w-6 text-green-500" />
              <div>
                <CardTitle className="text-lg">Google Account Connected</CardTitle>
                <p className="text-sm text-slate-600 mt-1">
                  Your personal Google services are linked to this admin account
                </p>
              </div>
            </div>
            <Badge className="bg-green-100 text-green-800 border-green-200">
              <CheckCircle className="h-3 w-3 mr-1" />
              Connected
            </Badge>
          </div>
        </CardHeader>
        
        <CardContent className="space-y-4">
          {/* Connected Google Account Info */}
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="flex items-center gap-3">
              <User className="h-5 w-5 text-green-600" />
              <div>
                <div className="font-medium text-green-800">Connected as:</div>
                <div className="text-green-700">{googleAccount}</div>
              </div>
            </div>
          </div>

          {/* Service Status */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {connectionStatus?.services && Object.entries(connectionStatus.services).map(([service, status]) => (
              <div key={service} className={`p-3 rounded-lg text-center ${
                status.connected 
                  ? 'bg-green-50 text-green-800 border border-green-200' 
                  : 'bg-red-50 text-red-800 border border-red-200'
              }`}>
                <div className="text-sm font-medium capitalize">{service}</div>
                <div className="text-xs mt-1">
                  {status.connected ? '✅ Active' : '❌ Inactive'}
                </div>
              </div>
            ))}
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-2">
            <Button 
              onClick={() => onCredentialsSet && onCredentialsSet()}
              className="flex-1"
            >
              Access Google Workspace
            </Button>
            <Button 
              variant="outline" 
              onClick={disconnectGoogle}
              disabled={loading}
            >
              <Settings className="h-4 w-4 mr-2" />
              Disconnect
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader className="pb-4">
        <div className="flex items-center gap-3">
          <AlertCircle className="h-6 w-6 text-amber-500" />
          <div>
            <CardTitle className="text-lg">Connect Your Google Account</CardTitle>
            <p className="text-sm text-slate-600 mt-1">
              Link your personal Google account to access Gmail, Calendar, Drive, and Meet
            </p>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-6">
        {/* Admin Info */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center gap-3">
            <User className="h-5 w-5 text-blue-600" />
            <div>
              <div className="font-medium text-blue-800">Admin Account:</div>
              <div className="text-blue-700">{currentUser?.name} ({currentUser?.email})</div>
            </div>
          </div>
        </div>

        {/* What will be connected */}
        <div className="space-y-3">
          <div className="text-sm font-medium text-slate-800">Services that will be connected:</div>
          <div className="grid grid-cols-2 gap-3">
            <div className="flex items-center gap-2 text-sm text-slate-600">
              <Mail className="h-4 w-4" />
              <span>Gmail - Send & receive emails</span>
            </div>
            <div className="flex items-center gap-2 text-sm text-slate-600">
              <CheckCircle className="h-4 w-4" />
              <span>Calendar - Manage events</span>
            </div>
            <div className="flex items-center gap-2 text-sm text-slate-600">
              <CheckCircle className="h-4 w-4" />
              <span>Drive - Access & manage files</span>
            </div>
            <div className="flex items-center gap-2 text-sm text-slate-600">
              <CheckCircle className="h-4 w-4" />
              <span>Meet - Schedule meetings</span>
            </div>
          </div>
        </div>

        {/* Connect Button */}
        <Button 
          onClick={initiateGoogleOAuth}
          disabled={loading}
          className="w-full"
          size="lg"
        >
          {loading ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              Connecting to Google...
            </>
          ) : (
            <>
              <Mail className="h-4 w-4 mr-2" />
              Connect My Google Account
            </>
          )}
        </Button>

        <div className="text-xs text-slate-500 text-center">
          You'll be redirected to Google to authorize FIDUS to access your account
        </div>
      </CardContent>
    </Card>
  );
};

export default GoogleCredentialSetup;