import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { Mail, Shield, CheckCircle, AlertCircle, RefreshCw, ExternalLink } from "lucide-react";
import axios from "axios";

const GmailSettings = () => {
  const [gmailStatus, setGmailStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [authenticating, setAuthenticating] = useState(false);
  const [authError, setAuthError] = useState(null);

  const backendUrl = process.env.REACT_APP_BACKEND_URL;

  useEffect(() => {
    // Check authentication status on component mount
    checkAuthStatus();
    
    // Handle OAuth callback parameters
    handleOAuthCallback();
  }, []);

  const handleOAuthCallback = () => {
    console.log("Checking for OAuth callback parameters...");
    
    const urlParams = new URLSearchParams(window.location.search);
    const gmailAuth = urlParams.get('gmail_auth');
    const email = urlParams.get('email');
    const message = urlParams.get('message');
    
    // Check if we were in the middle of OAuth flow
    const authInProgress = localStorage.getItem('gmail_auth_in_progress');
    const authTimestamp = localStorage.getItem('gmail_auth_timestamp');
    
    console.log(`OAuth callback check: gmail_auth=${gmailAuth}, email=${email}, authInProgress=${authInProgress}`);

    if (gmailAuth === 'success' && email) {
      // OAuth was successful
      console.log("OAuth success detected!");
      
      setAuthError(null);
      setAuthenticating(false);
      
      // Clear localStorage flags
      localStorage.removeItem('gmail_auth_in_progress');
      localStorage.removeItem('gmail_auth_timestamp');
      
      // Show success message temporarily with green styling
      setAuthError(`✅ Gmail authentication successful! Connected as ${email}`);
      setTimeout(() => {
        setAuthError(null);
      }, 5000);
      
      // Clean up URL parameters
      const newUrl = window.location.pathname;
      window.history.replaceState({}, document.title, newUrl);
      
      // Refresh status to get updated authentication info
      setTimeout(() => {
        console.log("Refreshing Gmail status after successful auth...");
        checkAuthStatus();
      }, 1000);
      
    } else if (gmailAuth === 'error') {
      // OAuth failed
      console.log("OAuth error detected!");
      
      setAuthenticating(false);
      
      // Clear localStorage flags
      localStorage.removeItem('gmail_auth_in_progress');
      localStorage.removeItem('gmail_auth_timestamp');
      
      // Show error message
      const errorMsg = message ? decodeURIComponent(message.replace(/\+/g, ' ')) : 'Unknown authentication error';
      setAuthError(`❌ Gmail authentication failed: ${errorMsg}`);
      
      // Clean up URL parameters
      const newUrl = window.location.pathname;
      window.history.replaceState({}, document.title, newUrl);
      
    } else if (authInProgress) {
      // We were in OAuth flow but no callback params - might still be in progress
      const timestamp = parseInt(authTimestamp || '0');
      const timeElapsed = Date.now() - timestamp;
      
      if (timeElapsed > 300000) { // 5 minutes timeout
        console.log("OAuth timeout detected, clearing state");
        localStorage.removeItem('gmail_auth_in_progress');
        localStorage.removeItem('gmail_auth_timestamp');
        setAuthenticating(false);
        setAuthError("❌ Authentication timed out. Please try again.");
      } else {
        console.log("OAuth still in progress...");
        setAuthenticating(true);
      }
    }
  };

  const checkAuthStatus = async () => {
    try {
      setLoading(true);
      const response = await axios.post(`${backendUrl}/api/gmail/authenticate`);
      
      if (response.data.success) {
        setGmailStatus(response.data);
        setAuthError(null);
      } else {
        setGmailStatus(null);
      }
    } catch (error) {
      console.error('Error checking Gmail auth status:', error);
      setGmailStatus(null);
    } finally {
      setLoading(false);
    }
  };

  const authenticateGmail = async () => {
    try {
      setAuthenticating(true);
      setAuthError(null);
      
      // Always force fresh OAuth flow - no cached credentials
      console.log("Starting Gmail OAuth flow...");
      
      // Get OAuth URL from backend
      const authUrlResponse = await axios.get(`${backendUrl}/api/gmail/auth-url`);
      
      if (authUrlResponse.data.success) {
        console.log("Got OAuth URL, redirecting...");
        
        // Store authentication state in localStorage
        localStorage.setItem('gmail_auth_in_progress', 'true');
        localStorage.setItem('gmail_auth_timestamp', Date.now().toString());
        
        // Direct redirect to Google OAuth - this is the ONLY reliable method
        // Popup/iframe approaches are blocked by Google's security policies
        window.location.href = authUrlResponse.data.authorization_url;
        
      } else {
        throw new Error("Failed to generate OAuth URL: " + (authUrlResponse.data.error || "Unknown error"));
      }
      
    } catch (error) {
      console.error('Gmail authentication error:', error);
      setAuthenticating(false);
      
      let errorMessage = "Gmail authentication failed. ";
      if (error.response?.data?.detail) {
        errorMessage += error.response.data.detail;
      } else if (error.response?.data?.error) {
        errorMessage += error.response.data.error;
      } else if (error.message) {
        errorMessage += error.message;
      } else {
        errorMessage += "Please check your internet connection and try again.";
      }
      
      setAuthError(errorMessage);
    }
  };

  const refreshStatus = async () => {
    await checkAuthStatus();
  };

  const resetAuth = () => {
    setGmailStatus(null);
    setAuthError(null);
    setAuthenticating(false);
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
        {/* Status Display */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-gray-400">Gmail Status:</span>
            {gmailStatus?.success ? (
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

          {gmailStatus?.email_address && (
            <div className="flex items-center justify-between">
              <span className="text-gray-400">Connected Account:</span>
              <span className="text-white font-medium">{gmailStatus.email_address}</span>
            </div>
          )}

          {gmailStatus?.messages_total && (
            <div className="flex items-center justify-between">
              <span className="text-gray-400">Total Messages:</span>
              <span className="text-white">{gmailStatus.messages_total.toLocaleString()}</span>
            </div>
          )}
        </div>

        {/* Error/Success Display */}
        {authError && (
          <div className={`border rounded-lg p-4 ${
            authError.includes('successful') 
              ? 'bg-green-600/10 border-green-600/20' 
              : 'bg-red-600/10 border-red-600/20'
          }`}>
            <div className={`flex items-start ${
              authError.includes('successful') ? 'text-green-400' : 'text-red-400'
            }`}>
              {authError.includes('successful') ? (
                <CheckCircle className="h-4 w-4 mr-2 mt-0.5 flex-shrink-0" />
              ) : (
                <AlertCircle className="h-4 w-4 mr-2 mt-0.5 flex-shrink-0" />
              )}
              <div>
                <span className="font-medium">
                  {authError.includes('successful') ? 'Success' : 'Authentication Issue'}
                </span>
                <p className="text-sm mt-1">{authError}</p>
              </div>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-3">
          {!gmailStatus?.success ? (
            <Button
              onClick={authenticateGmail}
              disabled={authenticating || loading}
              className="bg-blue-600 hover:bg-blue-700 flex-1"
            >
              {authenticating ? (
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
            <Button
              onClick={resetAuth}
              variant="outline"
              className="border-red-600 text-red-400 hover:bg-red-600/10 flex-1"
            >
              Disconnect Gmail
            </Button>
          )}

          <Button
            onClick={refreshStatus}
            disabled={loading}
            variant="outline"
            className="border-slate-600 text-slate-300 hover:bg-slate-700"
          >
            {loading ? (
              <RefreshCw className="h-4 w-4 animate-spin" />
            ) : (
              <RefreshCw className="h-4 w-4" />
            )}
          </Button>
        </div>

        {/* Information */}
        <div className="bg-slate-700/50 rounded-lg p-4">
          <h4 className="text-white font-medium mb-2">Gmail Integration Features:</h4>
          <ul className="text-sm text-gray-400 space-y-1">
            <li>• Send documents as email attachments</li>
            <li>• Professional FIDUS email templates</li>
            <li>• Document viewing links</li>
            <li>• Email delivery tracking</li>
            <li>• Secure OAuth2 authentication</li>
          </ul>
        </div>

        {/* Setup Instructions */}
        {!gmailStatus?.success && !authenticating && (
          <div className="bg-blue-600/10 border border-blue-600/20 rounded-lg p-4">
            <div className="flex items-start text-blue-400">
              <ExternalLink className="h-4 w-4 mr-2 mt-0.5 flex-shrink-0" />
              <div>
                <span className="font-medium">Setup Required</span>
                <p className="text-sm mt-1">
                  Click "Authenticate Gmail" to connect your Gmail account. You'll be redirected to Google to grant permissions, then automatically returned to this page.
                </p>
              </div>
            </div>
          </div>
        )}

        {gmailStatus?.success && (
          <div className="bg-green-600/10 border border-green-600/20 rounded-lg p-4">
            <div className="flex items-center text-green-400 mb-2">
              <CheckCircle className="h-4 w-4 mr-2" />
              <span className="font-medium">Gmail Ready!</span>
            </div>
            <p className="text-sm text-green-300">
              The Document Portal can now send emails through your Gmail account. 
              Documents will be sent with professional templates and both attachments and viewing links.
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default GmailSettings;