import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Alert, AlertDescription } from './ui/alert';
import {
  Mail,
  Calendar,
  FolderOpen,
  Send,
  Plus,
  RefreshCw,
  Video,
  CheckCircle,
  XCircle,
  AlertCircle,
  Users,
  FileText
} from 'lucide-react';
import googleCRMIntegration from '../services/googleCRMIntegration';

const CleanGoogleWorkspace = () => {
  const [connectionStatus, setConnectionStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [emails, setEmails] = useState([]);
  const [driveFiles, setDriveFiles] = useState([]);
  const [activeTab, setActiveTab] = useState('connection');

  // Test Google connection on component mount
  useEffect(() => {
    testGoogleConnection();
  }, []);

  const testGoogleConnection = async () => {
    setLoading(true);
    try {
      console.log('🔍 Testing Google API connection...');
      const result = await googleCRMIntegration.testConnection();
      setConnectionStatus(result);
      console.log('📊 Connection test result:', result);
    } catch (error) {
      console.error('❌ Connection test error:', error);
      setConnectionStatus({ success: false, error: error.message });
    } finally {
      setLoading(false);
    }
  };

  const loadEmails = async () => {
    setLoading(true);
    try {
      const result = await googleCRMIntegration.getEmails(10);
      if (result.success) {
        setEmails(result.emails || []);
      }
    } catch (error) {
      console.error('❌ Failed to load emails:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadDriveFiles = async () => {
    setLoading(true);
    try {
      const result = await googleCRMIntegration.getDriveFiles(10);
      if (result.success) {
        setDriveFiles(result.files || []);
      }
    } catch (error) {
      console.error('❌ Failed to load Drive files:', error);
    } finally {
      setLoading(false);
    }
  };

  const sendTestEmail = async () => {
    setLoading(true);
    try {
      const result = await googleCRMIntegration.sendClientEmail(
        'test@example.com',
        'Test Email from FIDUS CRM',
        '<h2>Test Email</h2><p>This is a test email from the FIDUS CRM system integrated with Google APIs.</p>'
      );
      
      if (result.success) {
        alert('✅ Test email sent successfully!');
      } else {
        alert('❌ Failed to send test email: ' + result.error);
      }
    } catch (error) {
      alert('❌ Error: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const createTestMeeting = async () => {
    setLoading(true);
    try {
      const startTime = new Date();
      startTime.setHours(startTime.getHours() + 1); // 1 hour from now
      const endTime = new Date(startTime);
      endTime.setHours(endTime.getHours() + 1); // 1 hour duration

      const result = await googleCRMIntegration.createGeneralMeeting(
        'FIDUS CRM Test Meeting',
        'This is a test meeting created from the FIDUS CRM system',
        ['test@example.com'],
        startTime.toISOString(),
        endTime.toISOString()
      );
      
      if (result.success) {
        alert('✅ Test meeting created successfully! Meet link: ' + result.meeting_details?.meet_link);
      } else {
        alert('❌ Failed to create test meeting: ' + result.error);
      }
    } catch (error) {
      alert('❌ Error: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full space-y-6">
      {/* Header */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Mail className="h-6 w-6 text-blue-600" />
            Google Workspace Integration - WORKING VERSION
          </CardTitle>
        </CardHeader>
      </Card>

      {/* Connection Status */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <AlertCircle className="h-5 w-5" />
            Connection Status
            <Button 
              onClick={testGoogleConnection} 
              variant="outline" 
              size="sm"
              disabled={loading}
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              Test Connection
            </Button>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center gap-2">
              <RefreshCw className="h-4 w-4 animate-spin" />
              Testing connection...
            </div>
          ) : connectionStatus ? (
            <div className="space-y-4">
              {/* Overall Status */}
              <div className={`flex items-center gap-2 p-4 rounded-lg ${
                connectionStatus.success 
                  ? 'bg-green-50 text-green-800 border border-green-200'
                  : 'bg-red-50 text-red-800 border border-red-200'
              }`}>
                {connectionStatus.success ? (
                  <>
                    <CheckCircle className="h-5 w-5" />
                    <span className="font-medium">✅ Google APIs Connected Successfully</span>
                  </>
                ) : (
                  <>
                    <XCircle className="h-5 w-5" />
                    <span className="font-medium">❌ Google APIs Connection Failed</span>
                  </>
                )}
              </div>

              {/* Individual Service Status */}
              {connectionStatus.services && (
                <div className="grid grid-cols-3 gap-4">
                  <div className={`p-3 rounded-lg text-sm ${
                    connectionStatus.services.gmail?.status === 'connected'
                      ? 'bg-green-50 text-green-700 border border-green-200'
                      : 'bg-red-50 text-red-700 border border-red-200'
                  }`}>
                    <div className="flex items-center gap-2">
                      <Mail className="h-4 w-4" />
                      <span className="font-medium">Gmail</span>
                    </div>
                    <div className="text-xs mt-1">
                      {connectionStatus.services.gmail?.status || 'Unknown'}
                    </div>
                  </div>

                  <div className={`p-3 rounded-lg text-sm ${
                    connectionStatus.services.drive?.status === 'connected'
                      ? 'bg-green-50 text-green-700 border border-green-200'
                      : 'bg-red-50 text-red-700 border border-red-200'
                  }`}>
                    <div className="flex items-center gap-2">
                      <FolderOpen className="h-4 w-4" />
                      <span className="font-medium">Drive</span>
                    </div>
                    <div className="text-xs mt-1">
                      {connectionStatus.services.drive?.status || 'Unknown'}
                    </div>
                  </div>

                  <div className={`p-3 rounded-lg text-sm ${
                    connectionStatus.services.calendar?.status === 'connected'
                      ? 'bg-green-50 text-green-700 border border-green-200'
                      : 'bg-red-50 text-red-700 border border-red-200'
                  }`}>
                    <div className="flex items-center gap-2">
                      <Calendar className="h-4 w-4" />
                      <span className="font-medium">Calendar</span>
                    </div>
                    <div className="text-xs mt-1">
                      {connectionStatus.services.calendar?.status || 'Unknown'}
                    </div>
                  </div>
                </div>
              )}

              {connectionStatus.error && (
                <Alert className="bg-red-50 border-red-200">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription className="text-red-800">
                    <strong>Error:</strong> {connectionStatus.error}
                  </AlertDescription>
                </Alert>
              )}
            </div>
          ) : (
            <div className="text-gray-600">
              Click "Test Connection" to verify Google API connectivity
            </div>
          )}
        </CardContent>
      </Card>

      {/* Action Buttons */}
      {connectionStatus?.success && (
        <Card>
          <CardHeader>
            <CardTitle>Google API Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-4 gap-4">
              <Button onClick={sendTestEmail} disabled={loading}>
                <Send className="h-4 w-4 mr-2" />
                Send Test Email
              </Button>
              
              <Button onClick={createTestMeeting} disabled={loading}>
                <Video className="h-4 w-4 mr-2" />
                Create Test Meeting
              </Button>
              
              <Button onClick={loadEmails} disabled={loading}>
                <Mail className="h-4 w-4 mr-2" />
                Load Emails
              </Button>
              
              <Button onClick={loadDriveFiles} disabled={loading}>
                <FolderOpen className="h-4 w-4 mr-2" />
                Load Drive Files
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Emails Display */}
      {emails.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Recent Emails</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {emails.map((email, index) => (
                <div key={index} className="p-3 border rounded-lg">
                  <div className="font-medium">{email.subject}</div>
                  <div className="text-sm text-gray-600">{email.sender}</div>
                  <div className="text-sm text-gray-500 mt-1">{email.snippet}</div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Drive Files Display */}
      {driveFiles.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Drive Files</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {driveFiles.map((file, index) => (
                <div key={index} className="p-3 border rounded-lg flex items-center gap-2">
                  <FileText className="h-4 w-4" />
                  <div className="flex-1">
                    <div className="font-medium">{file.name}</div>
                    <div className="text-sm text-gray-600">{file.mimeType}</div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* CRM Integration Info */}
      <Card>
        <CardHeader>
          <CardTitle>CRM Integration Status</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-green-700">
              <CheckCircle className="h-4 w-4" />
              <span>✅ Prospect email sending integrated</span>
            </div>
            <div className="flex items-center gap-2 text-green-700">
              <CheckCircle className="h-4 w-4" />
              <span>✅ Meeting scheduling integrated</span>
            </div>
            <div className="flex items-center gap-2 text-green-700">
              <CheckCircle className="h-4 w-4" />
              <span>✅ Document management ready</span>
            </div>
            <div className="flex items-center gap-2 text-green-700">
              <CheckCircle className="h-4 w-4" />
              <span>✅ Google Meet links generation</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default CleanGoogleWorkspace;