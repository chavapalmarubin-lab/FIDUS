import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { Mail, Shield, CheckCircle, AlertCircle, RefreshCw } from "lucide-react";
import axios from "axios";

const GmailSettings = () => {
  const [gmailStatus, setGmailStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [authenticating, setAuthenticating] = useState(false);

  const backendUrl = process.env.REACT_APP_BACKEND_URL;

  const authenticateGmail = async () => {
    try {
      setAuthenticating(true);
      
      const response = await axios.post(`${backendUrl}/api/gmail/authenticate`);
      
      if (response.data.success) {
        setGmailStatus(response.data);
      }
    } catch (error) {
      console.error('Gmail authentication error:', error);
      alert('Gmail authentication failed. Please check server logs.');
    } finally {
      setAuthenticating(false);
    }
  };

  const refreshStatus = async () => {
    try {
      setLoading(true);
      // Try to call authenticate to check current status
      await authenticateGmail();
    } finally {
      setLoading(false);
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

        {/* Action Buttons */}
        <div className="flex gap-3">
          <Button
            onClick={authenticateGmail}
            disabled={authenticating}
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
                {gmailStatus?.success ? 'Re-authenticate' : 'Authenticate Gmail'}
              </>
            )}
          </Button>

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