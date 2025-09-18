import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { Mail, Shield, CheckCircle, AlertCircle, RefreshCw, ExternalLink, ArrowRight } from "lucide-react";
import useGoogleAdmin from '../hooks/useGoogleAdmin';

const GmailSettings = () => {
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
  const [emailStatus, setEmailStatus] = useState(null);

  const testGmailFunctionality = async () => {
    if (!isAuthenticated || !profile) {
      setEmailStatus("❌ Please authenticate with Google first");
      return;
    }

    try {
      setTestEmailSending(true);
      setEmailStatus("📧 Sending test email...");
      
      await sendEmail({
        to_email: profile.email,
        subject: 'FIDUS Gmail Integration Test',
        body: `Hello ${profile.name},\n\nThis is a test email from FIDUS Investment Management platform to verify Gmail integration is working properly.\n\nBest regards,\nFIDUS Admin Team`,
        attachments: []
      });
      
      setEmailStatus("✅ Test email sent successfully!");
      setTimeout(() => setEmailStatus(null), 5000);
    } catch (err) {
      setEmailStatus(`❌ Failed to send test email: ${err.message}`);
    } finally {
      setTestEmailSending(false);
    }
  };

  const handleAuthenticate = async () => {
    try {
      clearError();
      await loginWithGoogle();
    } catch (err) {
      console.error('Gmail authentication error:', err);
    }
  };

  const handleDisconnect = async () => {
    try {
      await logout();
    } catch (err) {
      console.error('Gmail disconnect error:', err);
    }
  };

  return (
    <Card className="bg-slate-800 border-slate-700">
      <CardHeader>
        <CardTitle className="text-white flex items-center">
          <Mail className="h-5 w-5 mr-2" />
          Gmail Integration Settings
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Migration Notice */}
        <div className="bg-blue-600/10 border border-blue-600/20 rounded-lg p-4">
          <div className="flex items-start text-blue-400">
            <ArrowRight className="h-4 w-4 mr-2 mt-0.5 flex-shrink-0" />
            <div>
              <span className="font-medium">Updated Gmail Integration</span>
              <p className="text-sm mt-1">
                Gmail settings now use the unified Google Integration system. Please use the 
                <strong> Google Integration tab</strong> to authenticate and manage your Google account.
              </p>
            </div>
          </div>
        </div>

        {/* Status Display */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-gray-400">Gmail Status:</span>
            {isAuthenticated && profile ? (
              <Badge className="bg-green-600/20 text-green-400">
                <CheckCircle className="h-4 w-4 mr-1" />
                Connected
              </Badge>
            ) : (
              <Badge className="bg-yellow-600/20 text-yellow-400">
                <AlertCircle className="h-4 w-4 mr-1" />
                Not Connected
              </Badge>
            )}
          </div>

          {profile?.email && (
            <div className="flex items-center justify-between">
              <span className="text-gray-400">Connected Account:</span>
              <span className="text-white font-medium">{profile.email}</span>
            </div>
          )}

          {profile?.name && (
            <div className="flex items-center justify-between">
              <span className="text-gray-400">Account Name:</span>
              <span className="text-white">{profile.name}</span>
            </div>
          )}
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-600/10 border border-red-600/20 rounded-lg p-4">
            <div className="flex items-start text-red-400">
              <AlertCircle className="h-4 w-4 mr-2 mt-0.5 flex-shrink-0" />
              <div>
                <span className="font-medium">Authentication Issue</span>
                <p className="text-sm mt-1">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Email Status */}
        {emailStatus && (
          <div className={`border rounded-lg p-4 ${
            emailStatus.includes('✅') 
              ? 'bg-green-600/10 border-green-600/20' 
              : emailStatus.includes('❌')
              ? 'bg-red-600/10 border-red-600/20'
              : 'bg-blue-600/10 border-blue-600/20'
          }`}>
            <div className={`flex items-start ${
              emailStatus.includes('✅') ? 'text-green-400' : 
              emailStatus.includes('❌') ? 'text-red-400' : 'text-blue-400'
            }`}>
              <div>
                <p className="text-sm">{emailStatus}</p>
              </div>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-3">
          {!isAuthenticated ? (
            <Button
              onClick={handleAuthenticate}
              disabled={loading}
              className="bg-blue-600 hover:bg-blue-700 flex-1"
            >
              {loading ? (
                <>
                  <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                  Authenticating...
                </>
              ) : (
                <>
                  <Shield className="h-4 w-4 mr-2" />
                  Authenticate Gmail
                </>
              )}
            </Button>
          ) : (
            <>
              <Button
                onClick={testGmailFunctionality}
                disabled={testEmailSending}
                className="bg-green-600 hover:bg-green-700 flex-1"
              >
                {testEmailSending ? (
                  <>
                    <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                    Sending...
                  </>
                ) : (
                  <>
                    <Mail className="h-4 w-4 mr-2" />
                    Send Test Email
                  </>
                )}
              </Button>
              
              <Button
                onClick={handleDisconnect}
                variant="outline"
                className="border-red-600 text-red-400 hover:bg-red-600/10"
              >
                Disconnect
              </Button>
            </>
          )}
        </div>

        {/* Gmail Integration Features */}
        <div className="bg-slate-700/50 rounded-lg p-4">
          <h4 className="text-white font-medium mb-2">Gmail Integration Features:</h4>
          <ul className="text-sm text-gray-400 space-y-1">
            <li>• Send documents as email attachments</li>
            <li>• Professional FIDUS email templates</li>
            <li>• Document viewing links</li>
            <li>• Email delivery tracking</li>
            <li>• Secure OAuth2 authentication via Emergent</li>
            <li>• Unified Google services (Gmail + Calendar + Drive)</li>
          </ul>
        </div>

        {/* Setup Instructions */}
        {!isAuthenticated && (
          <div className="bg-blue-600/10 border border-blue-600/20 rounded-lg p-4">
            <div className="flex items-start text-blue-400">
              <ExternalLink className="h-4 w-4 mr-2 mt-0.5 flex-shrink-0" />
              <div>
                <span className="font-medium">Setup Required</span>
                <p className="text-sm mt-1">
                  Click "Authenticate Gmail" to connect your Google account using our secure OAuth system. 
                  This will enable Gmail integration for sending documents and notifications.
                </p>
              </div>
            </div>
          </div>
        )}

        {isAuthenticated && profile && (
          <div className="bg-green-600/10 border border-green-600/20 rounded-lg p-4">
            <div className="flex items-center text-green-400 mb-2">
              <CheckCircle className="h-4 w-4 mr-2" />
              <span className="font-medium">Gmail Ready!</span>
            </div>
            <p className="text-sm text-green-300">
              Gmail integration is active and ready to use. You can now send documents and notifications 
              through your Gmail account ({profile.email}) with professional FIDUS templates.
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default GmailSettings;