import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Alert, AlertDescription } from './ui/alert';
import {
  Mail,
  Calendar,
  Shield,
  User,
  LogOut,
  CheckCircle,
  AlertCircle,
  Loader2,
  ExternalLink,
  Settings,
  Globe
} from 'lucide-react';
import useGoogleAdmin from '../hooks/useGoogleAdmin';

const GoogleAdminAuth = ({ onAuthSuccess, onAuthError, showProfileCard = true }) => {
  const {
    profile,
    loading,
    error,
    isAuthenticated,
    loginWithGoogle,
    logout,
    sendEmail,
    clearError
  } = useGoogleAdmin();

  const [testEmailSending, setTestEmailSending] = useState(false);

  const handleLogin = async () => {
    try {
      clearError();
      await loginWithGoogle();
      
      if (onAuthSuccess) {
        onAuthSuccess(profile);
      }
    } catch (err) {
      if (onAuthError) {
        onAuthError(err.message);
      }
    }
  };

  const handleLogout = async () => {
    try {
      clearError();
      await logout();
    } catch (err) {
      if (onAuthError) {
        onAuthError(err.message);
      }
    }
  };

  const testEmailFunctionality = async () => {
    try {
      setTestEmailSending(true);
      
      await sendEmail({
        to_email: profile.email,
        subject: 'FIDUS Google Integration Test',
        body: 'This is a test email to verify Google integration is working properly.',
        attachments: []
      });
      
      alert('Test email sent successfully!');
    } catch (err) {
      alert(`Failed to send test email: ${err.message}`);
    } finally {
      setTestEmailSending(false);
    }
  };

  const getGoogleScopes = () => {
    return [
      { name: 'Gmail Send', icon: Mail, description: 'Send emails to clients' },
      { name: 'Gmail Read', icon: Mail, description: 'Read email responses' },
      { name: 'Calendar', icon: Calendar, description: 'Schedule client meetings' },
      { name: 'Drive', icon: Settings, description: 'Share documents for signature' }
    ];
  };

  if (loading) {
    return (
      <Card className="w-full max-w-md mx-auto">
        <CardContent className="flex items-center justify-center p-8">
          <div className="text-center">
            <Loader2 className="w-8 h-8 animate-spin text-blue-600 mx-auto mb-4" />
            <p className="text-gray-600">Checking Google authentication...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {/* Error Display */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <Alert className="border-red-200 bg-red-50">
              <AlertCircle className="h-4 w-4 text-red-600" />
              <AlertDescription className="text-red-700">
                {error}
              </AlertDescription>
            </Alert>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Authentication Status */}
      {!isAuthenticated ? (
        <Card className="w-full max-w-md mx-auto">
          <CardHeader className="text-center">
            <CardTitle className="flex items-center justify-center gap-2">
              <Shield className="w-6 h-6 text-blue-600" />
              Google Admin Authentication
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="text-center">
              <p className="text-gray-600 mb-4">
                Connect your Google account to enable:
              </p>
              
              <div className="grid grid-cols-2 gap-3 mb-6">
                {getGoogleScopes().map((scope, index) => (
                  <div key={index} className="flex items-center gap-2 p-2 bg-gray-50 rounded-lg">
                    <scope.icon className="w-4 h-4 text-blue-600" />
                    <span className="text-sm font-medium">{scope.name}</span>
                  </div>
                ))}
              </div>
            </div>

            <Button
              onClick={handleLogin}
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white"
              size="lg"
            >
              <Globe className="w-5 h-5 mr-2" />
              Sign in with Google
            </Button>

            <div className="text-center">
              <p className="text-xs text-gray-500">
                Authorized for: chavapalmarubin@gmail.com
              </p>
            </div>
          </CardContent>
        </Card>
      ) : (
        showProfileCard && (
          <Card className="w-full max-w-md mx-auto">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-green-600" />
                Google Account Connected
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Profile Info */}
              <div className="flex items-center gap-3 p-4 bg-green-50 rounded-lg border border-green-200">
                {profile.picture ? (
                  <img 
                    src={profile.picture} 
                    alt={profile.name}
                    className="w-12 h-12 rounded-full"
                  />
                ) : (
                  <div className="w-12 h-12 rounded-full bg-blue-600 flex items-center justify-center">
                    <User className="w-6 h-6 text-white" />
                  </div>
                )}
                <div className="flex-1">
                  <h3 className="font-medium text-gray-900">{profile.name}</h3>
                  <p className="text-sm text-gray-600">{profile.email}</p>
                  <Badge variant="secondary" className="text-xs mt-1">
                    {profile.login_type === 'google_oauth' ? 'Google OAuth' : 'Connected'}
                  </Badge>
                </div>
              </div>

              {/* Google Scopes */}
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Available Services:</h4>
                <div className="grid grid-cols-2 gap-2">
                  {getGoogleScopes().map((scope, index) => (
                    <div key={index} className="flex items-center gap-2 p-2 bg-gray-50 rounded text-sm">
                      <scope.icon className="w-4 h-4 text-green-600" />
                      <span>{scope.name}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Test Email Button */}
              <Button
                onClick={testEmailFunctionality}
                disabled={testEmailSending}
                variant="outline"
                className="w-full"
              >
                {testEmailSending ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Sending Test Email...
                  </>
                ) : (
                  <>
                    <Mail className="w-4 h-4 mr-2" />
                    Send Test Email
                  </>
                )}
              </Button>

              {/* Logout Button */}
              <Button
                onClick={handleLogout}
                variant="outline"
                className="w-full text-red-600 border-red-300 hover:bg-red-50"
              >
                <LogOut className="w-4 h-4 mr-2" />
                Disconnect Google Account
              </Button>

              {/* Connection Info */}
              <div className="text-xs text-gray-500 text-center">
                Connected: {new Date(profile.connected_at).toLocaleDateString()}
              </div>
            </CardContent>
          </Card>
        )
      )}
    </div>
  );
};

export default GoogleAdminAuth;