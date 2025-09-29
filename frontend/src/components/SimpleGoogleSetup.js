import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { CheckCircle, Mail, User, Settings } from 'lucide-react';

const SimpleGoogleSetup = () => {
  const [googleEmail, setGoogleEmail] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [showSetup, setShowSetup] = useState(false);

  const handleConnect = async () => {
    try {
      const token = localStorage.getItem('fidus_token');
      if (!token) {
        alert('Please login as admin first');
        return;
      }

      // Get Google OAuth URL
      const response = await fetch(`https://fidus-invest.emergent.host/api/auth/google/url`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      const data = await response.json();
      if (data.success && data.auth_url) {
        // Save admin info for callback
        localStorage.setItem('google_oauth_admin', 'admin_001');
        // Redirect to Google OAuth
        window.location.href = data.auth_url;
      } else {
        alert('Failed to get Google OAuth URL: ' + (data.error || 'Unknown error'));
      }
    } catch (error) {
      console.error('OAuth error:', error);
      alert('Error connecting to Google: ' + error.message);
    }
  };

  const handleDisconnect = () => {
    setIsConnected(false);
    setGoogleEmail('');
    localStorage.removeItem('google_connected_email');
  };

  // Check if already connected (simplified)
  React.useEffect(() => {
    const connectedEmail = localStorage.getItem('google_connected_email');
    if (connectedEmail) {
      setGoogleEmail(connectedEmail);
      setIsConnected(true);
    }
  }, []);

  if (isConnected) {
    return (
      <div className="w-full max-w-4xl mx-auto space-y-6">
        {/* Connected Status */}
        <Card>
          <CardHeader className="pb-4">
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-green-500" />
                  Google Workspace Connected
                </CardTitle>
                <p className="text-sm text-slate-600 mt-1">
                  Connected as {googleEmail} • Access to Gmail, Calendar, Drive, and Meet
                </p>
              </div>
              <Button variant="outline" onClick={handleDisconnect} size="sm">
                <Settings className="h-4 w-4 mr-2" />
                Change Account
              </Button>
            </div>
          </CardHeader>
        </Card>

        {/* Google Services */}
        <Card>
          <CardHeader>
            <CardTitle>Your Google Services</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-4 bg-green-50 border border-green-200 rounded-lg">
                <Mail className="h-8 w-8 mx-auto text-green-600 mb-2" />
                <div className="text-sm font-medium">Gmail</div>
                <div className="text-xs text-green-600">Connected</div>
              </div>
              <div className="text-center p-4 bg-green-50 border border-green-200 rounded-lg">
                <CheckCircle className="h-8 w-8 mx-auto text-green-600 mb-2" />
                <div className="text-sm font-medium">Calendar</div>
                <div className="text-xs text-green-600">Connected</div>
              </div>
              <div className="text-center p-4 bg-green-50 border border-green-200 rounded-lg">
                <CheckCircle className="h-8 w-8 mx-auto text-green-600 mb-2" />
                <div className="text-sm font-medium">Drive</div>
                <div className="text-xs text-green-600">Connected</div>
              </div>
              <div className="text-center p-4 bg-green-50 border border-green-200 rounded-lg">
                <CheckCircle className="h-8 w-8 mx-auto text-green-600 mb-2" />
                <div className="text-sm font-medium">Meet</div>
                <div className="text-xs text-green-600">Connected</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="w-full max-w-4xl mx-auto">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Mail className="h-5 w-5 text-blue-500" />
            Connect Your Google Account
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Admin Info */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-center gap-3">
              <User className="h-5 w-5 text-blue-600" />
              <div>
                <div className="font-medium text-blue-800">Admin Account: Chava Palma</div>
                <div className="text-blue-700">ic@fidus.com</div>
              </div>
            </div>
          </div>

          {/* Instructions */}
          <div className="space-y-4">
            <h3 className="font-medium">Connect your personal Google account to access:</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="flex items-center gap-2 text-sm">
                <Mail className="h-4 w-4 text-blue-500" />
                <span>Gmail - Send & receive emails</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <CheckCircle className="h-4 w-4 text-blue-500" />
                <span>Calendar - Manage events</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <CheckCircle className="h-4 w-4 text-blue-500" />
                <span>Drive - Access & manage files</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <CheckCircle className="h-4 w-4 text-blue-500" />
                <span>Meet - Schedule meetings</span>
              </div>
            </div>
          </div>

          {/* Connect Button */}
          <div className="text-center">
            <Button onClick={handleConnect} size="lg" className="w-full max-w-sm">
              <Mail className="h-4 w-4 mr-2" />
              Connect My Google Account
            </Button>
            <div className="text-xs text-slate-500 mt-2">
              You'll be redirected to Google to authorize FIDUS
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default SimpleGoogleSetup;