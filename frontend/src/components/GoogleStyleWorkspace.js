import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Tabs, TabsList, TabsTrigger, TabsContent } from './ui/tabs';
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
  Search,
  Star,
  Archive,
  Reply,
  Forward,
  Upload,
  Download,
  Users,
  Settings,
  Shield,
  Wifi,
  WifiOff
} from 'lucide-react';
import googleCRMIntegration from '../services/googleCRMIntegration';
import apiAxios from '../utils/apiAxios';

const GoogleStyleWorkspace = () => {
  const [connectionStatus, setConnectionStatus] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('connection');
  
  // Google-style data states
  const [emails, setEmails] = useState([]);
  const [driveFiles, setDriveFiles] = useState([]);
  const [calendarEvents, setCalendarEvents] = useState([]);

  useEffect(() => {
    checkConnectionStatus();
  }, []);

  const checkConnectionStatus = async () => {
    setLoading(true);
    try {
      const result = await googleCRMIntegration.testConnection();
      setConnectionStatus(result);
      setIsConnected(result.success);
      
      if (result.success) {
        // Load Google data if connected
        loadGoogleData();
      }
    } catch (error) {
      setConnectionStatus({ success: false, error: error.message });
      setIsConnected(false);
    } finally {
      setLoading(false);
    }
  };

  const handleConnect = async () => {
    setLoading(true);
    try {
      console.log('🔗 Starting Google OAuth connection...');
      const response = await apiAxios.get('/auth/google/url');
      
      if (response.data.success) {
        console.log('🚀 Redirecting to Google OAuth...');
        window.location.href = response.data.auth_url;
      } else {
        throw new Error(response.data.error || 'Failed to get OAuth URL');
      }
    } catch (error) {
      console.error('❌ OAuth connection failed:', error);
      setConnectionStatus({ 
        success: false, 
        error: 'Failed to connect to Google OAuth. Please try again.' 
      });
      setLoading(false);
    }
  };

  const loadGoogleData = async () => {
    try {
      // Load emails
      const emailResult = await googleCRMIntegration.getEmails(10);
      if (emailResult.success) {
        setEmails(emailResult.emails || []);
      }

      // Load drive files
      const driveResult = await googleCRMIntegration.getDriveFiles(10);
      if (driveResult.success) {
        setDriveFiles(driveResult.files || []);
      }
    } catch (error) {
      console.error('Failed to load Google data:', error);
    }
  };

  return (
    <div className="w-full space-y-4">
      {/* Google-Style Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-100">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center">
                <Mail className="h-5 w-5 text-white" />
              </div>
              <div>
                <h2 className="text-xl font-medium text-gray-900">Google Workspace</h2>
                <p className="text-sm text-gray-600">Gmail, Calendar, Drive integration</p>
              </div>
            </div>
            
            {/* Google-Style Connection Status */}
            <div className="flex items-center gap-3">
              {loading ? (
                <div className="flex items-center gap-2 px-3 py-2 bg-gray-50 rounded-full">
                  <RefreshCw className="h-4 w-4 animate-spin text-gray-600" />
                  <span className="text-sm text-gray-600">Connecting...</span>
                </div>
              ) : isConnected ? (
                <div className="flex items-center gap-2 px-3 py-2 bg-green-50 rounded-full border border-green-200">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <Wifi className="h-4 w-4 text-green-600" />
                  <span className="text-sm text-green-700 font-medium">Connected</span>
                </div>
              ) : (
                <div className="flex items-center gap-2 px-3 py-2 bg-red-50 rounded-full border border-red-200">
                  <WifiOff className="h-4 w-4 text-red-600" />
                  <span className="text-sm text-red-700 font-medium">Not Connected</span>
                </div>
              )}
              
              <Button
                onClick={isConnected ? checkConnectionStatus : handleConnect}
                variant={isConnected ? "outline" : "default"}
                className={isConnected ? "border-gray-300" : "bg-blue-600 hover:bg-blue-700 text-white"}
                disabled={loading}
              >
                {isConnected ? (
                  <>
                    <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                    Refresh
                  </>
                ) : (
                  <>
                    <Mail className="h-4 w-4 mr-2" />
                    Connect to Google
                  </>
                )}
              </Button>
            </div>
          </div>
        </div>

        {/* Google-Style Service Status */}
        {connectionStatus && (
          <div className="px-6 py-4 bg-gray-50 border-b border-gray-100">
            <div className="grid grid-cols-3 gap-4">
              <div className="flex items-center gap-3 p-3 bg-white rounded-lg border border-gray-200">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                  connectionStatus.services?.gmail?.status === 'connected' 
                    ? 'bg-red-100' : 'bg-gray-100'
                }`}>
                  <Mail className={`h-4 w-4 ${
                    connectionStatus.services?.gmail?.status === 'connected' 
                      ? 'text-red-600' : 'text-gray-400'
                  }`} />
                </div>
                <div className="flex-1">
                  <div className="font-medium text-sm text-gray-900">Gmail</div>
                  <div className="text-xs text-gray-600">
                    {connectionStatus.services?.gmail?.status === 'connected' ? 'Active' : 'Inactive'}
                  </div>
                </div>
                {connectionStatus.services?.gmail?.status === 'connected' && (
                  <CheckCircle className="h-4 w-4 text-green-500" />
                )}
              </div>

              <div className="flex items-center gap-3 p-3 bg-white rounded-lg border border-gray-200">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                  connectionStatus.services?.calendar?.status === 'connected' 
                    ? 'bg-blue-100' : 'bg-gray-100'
                }`}>
                  <Calendar className={`h-4 w-4 ${
                    connectionStatus.services?.calendar?.status === 'connected' 
                      ? 'text-blue-600' : 'text-gray-400'
                  }`} />
                </div>
                <div className="flex-1">
                  <div className="font-medium text-sm text-gray-900">Calendar</div>
                  <div className="text-xs text-gray-600">
                    {connectionStatus.services?.calendar?.status === 'connected' ? 'Active' : 'Inactive'}
                  </div>
                </div>
                {connectionStatus.services?.calendar?.status === 'connected' && (
                  <CheckCircle className="h-4 w-4 text-green-500" />
                )}
              </div>

              <div className="flex items-center gap-3 p-3 bg-white rounded-lg border border-gray-200">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                  connectionStatus.services?.drive?.status === 'connected' 
                    ? 'bg-yellow-100' : 'bg-gray-100'
                }`}>
                  <FolderOpen className={`h-4 w-4 ${
                    connectionStatus.services?.drive?.status === 'connected' 
                      ? 'text-yellow-600' : 'text-gray-400'
                  }`} />
                </div>
                <div className="flex-1">
                  <div className="font-medium text-sm text-gray-900">Drive</div>
                  <div className="text-xs text-gray-600">
                    {connectionStatus.services?.drive?.status === 'connected' ? 'Active' : 'Inactive'}
                  </div>
                </div>
                {connectionStatus.services?.drive?.status === 'connected' && (
                  <CheckCircle className="h-4 w-4 text-green-500" />
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Connection Instructions */}
      {!isConnected && (
        <div className="bg-blue-50 rounded-lg border border-blue-200 p-6">
          <div className="flex items-start gap-4">
            <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
              <Shield className="h-5 w-5 text-blue-600" />
            </div>
            <div className="flex-1">
              <h3 className="font-medium text-blue-900 mb-2">Connect to Google Workspace</h3>
              <p className="text-blue-800 text-sm mb-4">
                To access Gmail, Calendar, and Drive functionality, you need to connect your Google account. 
                This will allow FIDUS to integrate with your Google services for CRM and document management.
              </p>
              <div className="space-y-2 text-sm text-blue-700">
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-blue-600" />
                  <span>Send and receive emails through Gmail</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-blue-600" />
                  <span>Schedule meetings and manage calendar events</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-blue-600" />
                  <span>Upload and manage documents in Drive</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-blue-600" />
                  <span>Create Google Meet links for client meetings</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Google-Style Tabs */}
      {isConnected && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="border-b border-gray-100">
            <nav className="px-6">
              <div className="flex space-x-8">
                <button
                  onClick={() => setActiveTab('gmail')}
                  className={`py-4 px-1 text-sm font-medium border-b-2 ${
                    activeTab === 'gmail'
                      ? 'border-red-500 text-red-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <Mail className="h-4 w-4" />
                    Gmail
                  </div>
                </button>
                <button
                  onClick={() => setActiveTab('calendar')}
                  className={`py-4 px-1 text-sm font-medium border-b-2 ${
                    activeTab === 'calendar'
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <Calendar className="h-4 w-4" />
                    Calendar
                  </div>
                </button>
                <button
                  onClick={() => setActiveTab('drive')}
                  className={`py-4 px-1 text-sm font-medium border-b-2 ${
                    activeTab === 'drive'
                      ? 'border-yellow-500 text-yellow-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <FolderOpen className="h-4 w-4" />
                    Drive
                  </div>
                </button>
              </div>
            </nav>
          </div>

          {/* Tab Content */}
          <div className="p-6">
            {activeTab === 'gmail' && (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-medium text-gray-900">Gmail Integration</h3>
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm">
                      <Search className="h-4 w-4 mr-2" />
                      Search
                    </Button>
                    <Button size="sm" className="bg-red-600 hover:bg-red-700 text-white">
                      <Plus className="h-4 w-4 mr-2" />
                      Compose
                    </Button>
                  </div>
                </div>
                
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="text-center text-gray-600">
                    <Mail className="h-12 w-12 mx-auto mb-2 text-gray-400" />
                    <p className="font-medium">Gmail Connected Successfully</p>
                    <p className="text-sm">You can now send emails through your CRM</p>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'calendar' && (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-medium text-gray-900">Calendar Integration</h3>
                  <Button size="sm" className="bg-blue-600 hover:bg-blue-700 text-white">
                    <Plus className="h-4 w-4 mr-2" />
                    New Event
                  </Button>
                </div>
                
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="text-center text-gray-600">
                    <Calendar className="h-12 w-12 mx-auto mb-2 text-gray-400" />
                    <p className="font-medium">Calendar Connected Successfully</p>
                    <p className="text-sm">Schedule meetings with Google Meet integration</p>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'drive' && (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-medium text-gray-900">Drive Integration</h3>
                  <Button size="sm" className="bg-yellow-600 hover:bg-yellow-700 text-white">
                    <Upload className="h-4 w-4 mr-2" />
                    Upload
                  </Button>
                </div>
                
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="text-center text-gray-600">
                    <FolderOpen className="h-12 w-12 mx-auto mb-2 text-gray-400" />
                    <p className="font-medium">Drive Connected Successfully</p>
                    <p className="text-sm">Manage documents and share files</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default GoogleStyleWorkspace;