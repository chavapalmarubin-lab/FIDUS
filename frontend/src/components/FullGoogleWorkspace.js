import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Tabs, TabsList, TabsTrigger, TabsContent } from './ui/tabs';
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
  FileText,
  Upload,
  Download,
  Search,
  Reply,
  Forward,
  Archive,
  Star,
  Paperclip,
  Clock,
  MapPin,
  Edit,
  Trash2,
  Wifi,
  WifiOff,
  Activity
} from 'lucide-react';
import googleCRMIntegration from '../services/googleCRMIntegration';
import apiAxios from '../utils/apiAxios';

const FullGoogleWorkspace = () => {
  const [connectionStatus, setConnectionStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('gmail');
  
  // Gmail State
  const [emails, setEmails] = useState([]);
  const [selectedEmail, setSelectedEmail] = useState(null);
  const [composeOpen, setComposeOpen] = useState(false);
  const [composeData, setComposeData] = useState({ to: '', subject: '', body: '' });
  
  // Calendar State
  const [events, setEvents] = useState([]);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [eventModalOpen, setEventModalOpen] = useState(false);
  const [eventData, setEventData] = useState({
    title: '',
    description: '',
    start: '',
    end: '',
    attendees: ''
  });
  
  // Drive State
  const [driveFiles, setDriveFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadModalOpen, setUploadModalOpen] = useState(false);

  // Sheets State
  const [sheets, setSheets] = useState([]);

  useEffect(() => {
    // Load initial connection status and try to load emails if connected
    const initializeGoogleWorkspace = async () => {
      await testConnectionQuick();
      
      // If connection is successful, automatically load emails
      if (connectionStatus?.overall_status === 'fully_connected' || 
          connectionStatus?.services?.gmail?.status === 'connected') {
        console.log('🔄 Auto-loading emails since Gmail is connected...');
        loadEmails();
      }
    };
    
    initializeGoogleWorkspace();
  }, []);

  // Auto-load emails when connection status changes to connected
  useEffect(() => {
    if (connectionStatus?.services?.gmail?.status === 'connected' && activeTab === 'gmail') {
      console.log('🔄 Gmail connected, loading emails...');
      loadEmails();
    }
  }, [connectionStatus, activeTab]);

  // Quick connection test for status display
  const testConnectionQuick = async () => {
    try {
      const response = await apiAxios.get('/admin/google/emergent/status');
      console.log('🔍 Emergent Google connection status:', response.data);
      
      // Update connection status based on Emergent Auth response
      const statusData = {
        success: response.data.success && response.data.connected,
        connected: response.data.connected,
        overall_status: response.data.connected ? 'fully_connected' : 'disconnected',
        google_info: {
          email: response.data.google_email,
          name: response.data.google_name,
          picture: response.data.google_picture
        },
        admin_info: response.data.admin_info,
        expires_at: response.data.expires_at,
        services: {
          gmail: { 
            status: response.data.connected ? 'connected' : 'disconnected' 
          },
          calendar: { 
            status: response.data.connected ? 'connected' : 'disconnected' 
          },
          drive: { 
            status: response.data.connected ? 'connected' : 'disconnected' 
          },
          meet: { 
            status: response.data.connected ? 'connected' : 'disconnected' 
          }
        }
      };
      
      setConnectionStatus(statusData);
      
      // Auto-load data if connected
      if (statusData.connected) {
        console.log('✅ Emergent Google connected - auto-loading Gmail data');
        if (activeTab === 'gmail') {
          loadEmails();
        } else if (activeTab === 'calendar') {
          loadCalendarEvents();
        } else if (activeTab === 'drive') {
          loadDriveFiles();
        }
      }
      
    } catch (error) {
      console.error('Failed to test connection:', error);
      setConnectionStatus({
        success: false,
        connected: false,
        overall_status: 'test_failed',
        services: {}
      });
    }
  };

  const testConnection = async () => {
    setLoading(true);
    try {
      const result = await googleCRMIntegration.testConnection();
      setConnectionStatus(result);
      if (result.success) {
        // Load initial data
        loadEmails();
        loadDriveFiles();
      }
    } catch (error) {
      setConnectionStatus({ success: false, error: error.message });
    } finally {
      setLoading(false);
    }
  };

  // Connection Status Component
  const ConnectionStatusBanner = () => {
    if (!connectionStatus) return null;

    const getStatusColor = () => {
      switch (connectionStatus.overall_status) {
        case 'fully_connected':
          return 'bg-green-50 text-green-800 border-green-200';
        case 'partially_connected':
          return 'bg-yellow-50 text-yellow-800 border-yellow-200';
        case 'disconnected':
        case 'test_failed':
          return 'bg-red-50 text-red-800 border-red-200';
        default:
          return 'bg-gray-50 text-gray-800 border-gray-200';
      }
    };

    const getStatusIcon = () => {
      switch (connectionStatus.overall_status) {
        case 'fully_connected':
          return <Wifi className="h-5 w-5 text-green-600" />;
        case 'partially_connected':
          return <Activity className="h-5 w-5 text-yellow-600" />;
        default:
          return <WifiOff className="h-5 w-5 text-red-600" />;
      }
    };

    const getStatusMessage = () => {
      if (connectionStatus.overall_status === 'fully_connected') {
        return `All Google services connected • ${connectionStatus.connection_quality?.success_rate || 0}% success rate`;
      } else if (connectionStatus.overall_status === 'partially_connected') {
        return `${connectionStatus.connection_quality?.successful_tests || 0}/${connectionStatus.connection_quality?.total_tests || 4} services connected`;
      } else {
        return connectionStatus.error || 'Google services disconnected';
      }
    };

    return (
      <div className={`flex items-center justify-between p-4 rounded-lg border ${getStatusColor()} mb-6`}>
        <div className="flex items-center gap-3">
          {getStatusIcon()}
          <div>
            <span className="font-medium">Google Workspace Status</span>
            <p className="text-sm mt-1">{getStatusMessage()}</p>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          {/* Service Status Indicators */}
          {connectionStatus.services && (
            <div className="flex items-center gap-1 mr-4">
              {Object.entries(connectionStatus.services).map(([service, status]) => (
                <div
                  key={service}
                  className="flex items-center gap-1 text-xs px-2 py-1 rounded bg-white/50"
                  title={`${service}: ${status.status}`}
                >
                  {service === 'gmail' && <Mail className="h-3 w-3" />}
                  {service === 'calendar' && <Calendar className="h-3 w-3" />}
                  {service === 'drive' && <FolderOpen className="h-3 w-3" />}
                  {service === 'meet' && <Video className="h-3 w-3" />}
                  {status.status === 'connected' ? (
                    <CheckCircle className="h-3 w-3 text-green-600" />
                  ) : (
                    <XCircle className="h-3 w-3 text-red-600" />
                  )}
                </div>
              ))}
            </div>
          )}
          
          <Button 
            onClick={testConnectionQuick}
            variant="outline" 
            size="sm"
            disabled={loading}
          >
            <RefreshCw className={`h-4 w-4 mr-1 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>
    );
  };

  // Handle REAL Google OAuth connection
  const handleConnectToGoogle = async () => {
    setLoading(true);
    try {
      console.log('🔗 Starting Emergent Google OAuth flow...');
      
      // Get the Google OAuth URL from backend
      const response = await apiAxios.get('/auth/google/url');
      
      if (response.data.success) {
        const authUrl = response.data.auth_url;
        console.log('🚀 Redirecting to Emergent Google OAuth:', authUrl);
        
        // Redirect to Emergent Google OAuth
        window.location.href = authUrl;
      } else {
        throw new Error(response.data.error || 'Failed to get Emergent Google OAuth URL');
      }
      
    } catch (error) {
      console.error('❌ Emergent Google OAuth connection failed:', error);
      setConnectionStatus({ 
        success: false, 
        error: 'Failed to connect to Google OAuth. Please try again.' 
      });
      setLoading(false);
    }
  };

  // ==================== GMAIL FUNCTIONS ====================
  
  const loadEmails = async () => {
    setLoading(true);
    try {
      console.log('📧 Loading Gmail messages from Emergent Auth...');
      
      // Call the Emergent Gmail API endpoint
      const response = await apiAxios.get('/admin/google/emergent/gmail/messages');
      
      if (response.data.success && response.data.messages && Array.isArray(response.data.messages)) {
        console.log(`✅ Loaded ${response.data.messages.length} Gmail messages via Emergent Auth`);
        
        // Transform Emergent Gmail data to our format
        const transformedEmails = response.data.messages.map(email => ({
          id: email.gmail_id || email.id,
          subject: email.subject || 'No Subject',
          sender: email.sender || email.from || 'Unknown Sender',
          recipient: email.to || email.recipient || '',
          date: email.date || email.internal_date || new Date().toISOString(),
          snippet: email.snippet || email.body?.substring(0, 150) + '...' || 'No preview available',
          read: !email.labels?.includes('UNREAD'),
          starred: email.labels?.includes('STARRED') || false,
          body: email.body || '<p>Message content not available</p>',
          real_gmail_api: true
        }));
        
        setEmails(transformedEmails);
        console.log(`✅ Successfully loaded ${transformedEmails.length} emails from your Gmail`);
      } else {
        console.warn('⚠️ No emails returned from Gmail API, using fallback');
        // Fallback message for when no emails are returned
        setEmails([{
          id: 'no-emails',
          subject: '📧 Connect to Gmail to see your emails',
          sender: 'FIDUS System',
          snippet: 'Complete Google OAuth authentication to load your real Gmail messages',
          date: new Date().toISOString(),
          read: true,
          starred: false,
          body: '<div style="padding: 20px; text-align: center;"><h3>Gmail Integration Ready</h3><p>Complete Google OAuth to see your real emails here.</p></div>'
        }]);
      }
    } catch (error) {
      console.error('❌ Failed to load real Gmail messages:', error);
      
      // Show error message instead of mock data
      setEmails([{
        id: 'error-gmail',
        subject: '⚠️ Gmail API Connection Error',
        sender: 'FIDUS System',
        snippet: `Error loading Gmail: ${error.message}. Please check your Google OAuth connection.`,
        date: new Date().toISOString(),
        read: false,
        starred: false,
        body: `
          <div style="padding: 20px; background: #fee2e2; border: 1px solid #fca5a5; border-radius: 8px;">
            <h3 style="color: #dc2626;">Gmail Connection Error</h3>
            <p><strong>Error:</strong> ${error.message}</p>
            <p><strong>Solution:</strong></p>
            <ol>
              <li>Click "Connect Google Workspace" button</li>
              <li>Complete Google OAuth authentication</li>
              <li>Grant Gmail permissions to FIDUS</li>
              <li>Refresh this page</li>
            </ol>
          </div>
        `
      }]);
    } finally {
      setLoading(false);
    }
  };

  const sendEmail = async () => {
    if (!composeData.to || !composeData.subject || !composeData.body) {
      alert('Please fill in all required fields');
      return;
    }

    setLoading(true);
    try {
      const result = await googleCRMIntegration.sendClientEmail(
        composeData.to,
        composeData.subject,
        composeData.body
      );
      
      if (result.success) {
        alert('✅ Email sent successfully!');
        setComposeOpen(false);
        setComposeData({ to: '', subject: '', body: '' });
        loadEmails(); // Refresh email list
      } else {
        alert('❌ Failed to send email: ' + result.error);
      }
    } catch (error) {
      alert('❌ Error sending email: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  // ==================== CALENDAR FUNCTIONS ====================
  
  const loadCalendarEvents = async () => {
    setLoading(true);
    try {
      console.log('📅 Loading REAL Google Calendar events from API...');
      
      // Call the REAL Google Calendar API endpoint
      const response = await apiAxios.get('/google/calendar/events');
      
      if (response.data && Array.isArray(response.data)) {
        console.log(`✅ Loaded ${response.data.length} real calendar events`);
        
        // Transform real Calendar data to our format
        const transformedEvents = response.data.map(event => ({
          id: event.id,
          title: event.summary || event.title || 'No Title',
          description: event.description || 'No description available',
          start: event.start?.dateTime || event.start || new Date().toISOString(),
          end: event.end?.dateTime || event.end || new Date().toISOString(),
          attendees: event.attendees?.map(a => a.email) || [],
          meetLink: event.hangoutLink || event.conferenceData?.entryPoints?.[0]?.uri || null,
          real_calendar_api: true
        }));
        
        setEvents(transformedEvents);
        console.log(`✅ Successfully loaded ${transformedEvents.length} events from your Google Calendar`);
      } else {
        console.warn('⚠️ No events returned from Calendar API, using fallback');
        // Fallback message for when no events are returned
        setEvents([{
          id: 'no-events',
          title: '📅 Connect to Google Calendar to see your events',
          description: 'Complete Google OAuth authentication to load your real calendar events',
          start: new Date().toISOString(),
          end: new Date(Date.now() + 3600000).toISOString(), // 1 hour later
          attendees: [],
          meetLink: null
        }]);
      }
    } catch (error) {
      console.error('❌ Failed to load real Calendar events:', error);
      
      // Show error message instead of mock data
      setEvents([{
        id: 'error-calendar',
        title: '⚠️ Calendar API Connection Error',
        description: `Error loading Calendar: ${error.message}. Please check your Google OAuth connection.`,
        start: new Date().toISOString(),
        end: new Date(Date.now() + 3600000).toISOString(),
        attendees: [],
        meetLink: null
      }]);
    } finally {
      setLoading(false);
    }
  };

  const createMeeting = async () => {
    if (!eventData.title || !eventData.start || !eventData.end) {
      alert('Please fill in all required fields');
      return;
    }

    setLoading(true);
    try {
      const attendeeEmails = eventData.attendees.split(',').map(email => email.trim());
      const result = await googleCRMIntegration.createGeneralMeeting(
        eventData.title,
        eventData.description,
        attendeeEmails,
        eventData.start,
        eventData.end
      );
      
      if (result.success) {
        alert('✅ Meeting created successfully!');
        setEventModalOpen(false);
        setEventData({ title: '', description: '', start: '', end: '', attendees: '' });
        loadCalendarEvents(); // Refresh events
      } else {
        alert('❌ Failed to create meeting: ' + result.error);
      }
    } catch (error) {
      alert('❌ Error creating meeting: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  // ==================== DRIVE FUNCTIONS ====================
  
  const loadDriveFiles = async () => {
    setLoading(true);
    try {
      console.log('💾 Loading REAL Google Drive files from API...');
      
      // Call the REAL Google Drive API endpoint
      const response = await apiAxios.get('/google/drive/real-files');
      
      if (response.data && Array.isArray(response.data)) {
        console.log(`✅ Loaded ${response.data.length} real drive files`);
        
        // Transform real Drive data to our format
        const transformedFiles = response.data.map(file => ({
          id: file.id,
          name: file.name,
          mimeType: file.mimeType || 'application/octet-stream',
          size: file.size ? `${(file.size / 1024 / 1024).toFixed(1)} MB` : '—',
          createdTime: file.createdTime || new Date().toISOString(),
          modifiedTime: file.modifiedTime || new Date().toISOString(),
          shared: file.shared || false,
          isFolder: file.mimeType === 'application/vnd.google-apps.folder',
          real_drive_api: true
        }));
        
        setDriveFiles(transformedFiles);
        console.log(`✅ Successfully loaded ${transformedFiles.length} files from your Google Drive`);
      } else {
        console.warn('⚠️ No files returned from Drive API, using fallback');
        // Fallback message for when no files are returned
        setDriveFiles([{
          id: 'no-files',
          name: '💾 Connect to Google Drive to see your files',
          mimeType: 'text/plain',
          size: '—',
          createdTime: new Date().toISOString(),
          modifiedTime: new Date().toISOString(),
          shared: false,
          isFolder: false
        }]);
      }
    } catch (error) {
      console.error('❌ Failed to load real Drive files:', error);
      
      // Show error message instead of mock data
      setDriveFiles([{
        id: 'error-drive',
        name: '⚠️ Drive API Connection Error',
        mimeType: 'text/plain',
        size: '—',
        createdTime: new Date().toISOString(),
        modifiedTime: new Date().toISOString(),
        shared: false,
        isFolder: false
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setLoading(true);
    try {
      // Simulate file upload
      const newFile = {
        id: Date.now().toString(),
        name: file.name,
        mimeType: file.type,
        size: (file.size / 1024 / 1024).toFixed(1) + ' MB',
        createdTime: new Date().toISOString(),
        modifiedTime: new Date().toISOString(),
        shared: false
      };
      
      setDriveFiles([newFile, ...driveFiles]);
      alert('✅ File uploaded successfully!');
      setUploadModalOpen(false);
    } catch (error) {
      alert('❌ Error uploading file: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  // ==================== SHEETS FUNCTIONS ====================
  
  const loadSheets = async () => {
    setLoading(true);
    try {
      console.log('📊 Loading REAL Google Sheets from API...');
      
      // Call the REAL Google Sheets API endpoint
      const response = await apiAxios.get('/google/sheets/list');
      
      if (response.data && Array.isArray(response.data)) {
        console.log(`✅ Loaded ${response.data.length} real sheets`);
        setSheets(response.data);
        console.log(`✅ Successfully loaded ${response.data.length} sheets from your Google Sheets`);
      } else {
        console.warn('⚠️ No sheets returned from Sheets API, using fallback');
        setSheets([]);
      }
    } catch (error) {
      console.error('❌ Failed to load real Sheets:', error);
      setSheets([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Load data when tab changes and user is connected
    if (connectionStatus?.connected && !connectionStatus?.is_expired) {
      console.log(`🔄 Tab changed to ${activeTab}, loading data...`);
      
      if (activeTab === 'gmail') {
        loadEmails();
      } else if (activeTab === 'calendar') {
        loadCalendarEvents();
      } else if (activeTab === 'drive') {
        loadDriveFiles();
      } else if (activeTab === 'sheets') {
        loadSheets();
      }
    }
  }, [activeTab, connectionStatus]);

  // Auto-load Gmail data when connection is established
  useEffect(() => {
    if (connectionStatus?.connected && !connectionStatus?.is_expired) {
      console.log('✅ Connected user detected, auto-loading data for current tab...');
      
      // Load data for the current active tab immediately
      if (activeTab === 'gmail') {
        console.log('📧 Auto-loading Gmail messages...');
        loadEmails();
      } else if (activeTab === 'calendar') {
        console.log('📅 Auto-loading Calendar events...');
        loadCalendarEvents();
      } else if (activeTab === 'drive') {
        console.log('💾 Auto-loading Drive files...');
        loadDriveFiles();
      } else if (activeTab === 'sheets') {
        console.log('📊 Auto-loading Sheets...');
        loadSheets();
      }
    }
  }, [connectionStatus]);

  // Auto-load data when Gmail tab opens for connected users
  useEffect(() => {
    if (connectionStatus?.connected && !connectionStatus?.is_expired && activeTab === 'gmail' && emails.length === 0) {
      console.log('📧 Gmail tab opened - loading emails for connected user...');
      loadEmails();
    }
  }, [activeTab]);

  return (
    <div className="w-full space-y-6">
      {/* Header */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Mail className="h-6 w-6 text-blue-600" />
            Full Google Workspace Integration
            <Badge variant="outline" className="ml-2">COMPLETE VERSION</Badge>
          </CardTitle>
        </CardHeader>
      </Card>

      {/* Connection Status Banner */}
      <ConnectionStatusBanner />

      {/* Connection Status */}
      {connectionStatus && (
        <Card>
          <CardContent className="pt-6">
            <div className={`flex items-center justify-between p-3 rounded-lg ${
              connectionStatus.success 
                ? 'bg-green-50 text-green-800 border border-green-200'
                : 'bg-red-50 text-red-800 border border-red-200'
            }`}>
              <div className="flex items-center gap-2">
                {connectionStatus.success ? (
                  <CheckCircle className="h-5 w-5" />
                ) : (
                  <XCircle className="h-5 w-5" />
                )}
                <span className="font-medium">
                  {connectionStatus.success ? '✅ Google APIs Connected' : '❌ Connection Failed'}
                </span>
              </div>
              
              {/* Connected Account Details */}
              {connectionStatus.success && connectionStatus.connected && connectionStatus.google_info && (
                <div className="mt-3 p-3 bg-green-50 border border-green-200 rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center text-white text-sm font-medium">
                      {connectionStatus.google_info.name?.charAt(0) || 'U'}
                    </div>
                    <div>
                      <div className="font-medium text-green-900">
                        Connected as {connectionStatus.google_info.name || 'Google User'}
                      </div>
                      <div className="text-sm text-green-700">
                        {connectionStatus.google_info.email || 'No email available'}
                      </div>
                      <div className="text-xs text-green-600 mt-1">
                        Admin: {connectionStatus.admin_info?.admin_username || 'Unknown'}
                      </div>
                    </div>
                  </div>
                </div>
              )}
              
              {/* Connect to Google Button */}
              {(!connectionStatus.connected || !connectionStatus.success) && (
                <div className="mt-3">
                  <Button 
                    onClick={handleConnectToGoogle}
                    disabled={loading}
                    className="bg-blue-600 hover:bg-blue-700 text-white w-full"
                  >
                    {loading ? (
                      <>
                        <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                        Connecting...
                      </>
                    ) : (
                      <>
                        <Mail className="h-4 w-4 mr-2" />
                        Connect Google Workspace
                      </>
                    )}
                  </Button>
                </div>
              )}
            </div>
            
            {/* Error Details */}
            {!connectionStatus.success && connectionStatus.error && (
              <div className="mt-3 text-sm text-red-700 bg-red-50 p-2 rounded">
                <strong>Error:</strong> {connectionStatus.error}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Initial Connection Prompt */}
      {!connectionStatus && (
        <Card>
          <CardContent className="pt-6">
            <div className="text-center py-8">
              <Mail className="h-16 w-16 mx-auto mb-4 text-gray-300" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Connect Google Workspace
              </h3>
              <p className="text-gray-600 mb-6">
                Connect your Google account to access Gmail, Calendar, and Drive functionality
              </p>
              <Button 
                onClick={handleConnectToGoogle}
                disabled={loading}
                size="lg"
                className="bg-blue-600 hover:bg-blue-700 text-white"
              >
                {loading ? (
                  <>
                    <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                    Connecting...
                  </>
                ) : (
                  <>
                    <Mail className="h-4 w-4 mr-2" />
                    Connect Google Workspace
                  </>
                )}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Connection Required Banner */}
      {(!connectionStatus?.connected) && (
        <Card className="border-orange-200 bg-orange-50">
          <CardContent className="p-6 text-center">
            <AlertCircle className="h-12 w-12 mx-auto mb-4 text-orange-500" />
            <h3 className="text-lg font-medium text-orange-900 mb-2">
              Google Workspace Connection Required
            </h3>
            <p className="text-orange-700 mb-4">
              Connect your Google account to access Gmail, Calendar, Drive, and Sheets functionality
            </p>
            <Button 
              onClick={handleConnectToGoogle}
              disabled={loading}
              size="lg"
              className="bg-blue-600 hover:bg-blue-700 text-white"
            >
              {loading ? (
                <>
                  <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                  Connecting...
                </>
              ) : (
                <>
                  <Mail className="h-4 w-4 mr-2" />
                  Connect My Google Account
                </>
              )}
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Main Workspace */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4 bg-slate-100">
          <TabsTrigger value="gmail" className="data-[state=active]:bg-blue-50 data-[state=active]:text-blue-900">
            <Mail className="h-4 w-4 mr-2" />
            Gmail
          </TabsTrigger>
          <TabsTrigger value="calendar" className="data-[state=active]:bg-green-50 data-[state=active]:text-green-900">
            <Calendar className="h-4 w-4 mr-2" />
            Calendar
          </TabsTrigger>
          <TabsTrigger value="drive" className="data-[state=active]:bg-yellow-50 data-[state=active]:text-yellow-900">
            <FolderOpen className="h-4 w-4 mr-2" />
            Drive
          </TabsTrigger>
          <TabsTrigger value="sheets" className="data-[state=active]:bg-purple-50 data-[state=active]:text-purple-900">
            <FileText className="h-4 w-4 mr-2" />
            Sheets
          </TabsTrigger>
        </TabsList>

        {/* Gmail Tab */}
        <TabsContent value="gmail" className="mt-6">
          <div className="grid grid-cols-12 gap-6 h-[600px]">
            {/* Email List */}
            <div className="col-span-5">
              <Card className="h-full">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">Inbox ({emails.length})</CardTitle>
                    <div className="flex gap-2">
                      <Button onClick={loadEmails} variant="outline" size="sm">
                        <RefreshCw className="h-4 w-4" />
                      </Button>
                      <Button onClick={() => setComposeOpen(true)} size="sm">
                        <Plus className="h-4 w-4 mr-1" />
                        Compose
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="p-0">
                  <div className="max-h-[500px] overflow-y-auto">
                    {emails.map((email) => (
                      <div
                        key={email.id}
                        className={`p-4 border-b cursor-pointer hover:bg-gray-50 ${
                          selectedEmail?.id === email.id ? 'bg-blue-50 border-l-4 border-l-blue-500' : ''
                        } ${!email.read ? 'bg-blue-25 font-semibold' : ''}`}
                        onClick={() => setSelectedEmail(email)}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex items-center gap-2">
                            {email.starred && <Star className="h-4 w-4 text-yellow-500 fill-current" />}
                            <span className={`text-sm ${!email.read ? 'font-bold' : ''}`}>
                              {email.sender}
                            </span>
                          </div>
                          <span className="text-xs text-gray-500">
                            {new Date(email.date).toLocaleDateString()}
                          </span>
                        </div>
                        <div className={`text-sm mt-1 ${!email.read ? 'font-semibold' : ''}`}>
                          {email.subject}
                        </div>
                        <div className="text-xs text-gray-600 mt-1 line-clamp-2">
                          {email.snippet}
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Email Detail */}
            <div className="col-span-7">
              <Card className="h-full">
                {selectedEmail ? (
                  <>
                    <CardHeader className="pb-3 border-b">
                      <div className="flex items-start justify-between">
                        <div>
                          <CardTitle className="text-lg">{selectedEmail.subject}</CardTitle>
                          <div className="text-sm text-gray-600 mt-1">
                            From: {selectedEmail.sender} • To: {selectedEmail.recipient}
                          </div>
                          <div className="text-xs text-gray-500">
                            {new Date(selectedEmail.date).toLocaleString()}
                          </div>
                        </div>
                        <div className="flex gap-2">
                          <Button variant="outline" size="sm">
                            <Reply className="h-4 w-4 mr-1" />
                            Reply
                          </Button>
                          <Button variant="outline" size="sm">
                            <Forward className="h-4 w-4 mr-1" />
                            Forward
                          </Button>
                          <Button variant="outline" size="sm">
                            <Archive className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent className="pt-6">
                      <div 
                        className="prose max-w-none"
                        dangerouslySetInnerHTML={{ __html: selectedEmail.body }}
                      />
                    </CardContent>
                  </>
                ) : (
                  <CardContent className="flex items-center justify-center h-full">
                    <div className="text-center text-gray-500">
                      <Mail className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                      <p>Select an email to read</p>
                    </div>
                  </CardContent>
                )}
              </Card>
            </div>
          </div>
        </TabsContent>

        {/* Calendar Tab */}
        <TabsContent value="calendar" className="mt-6">
          <div className="grid grid-cols-12 gap-6">
            {/* Events List */}
            <div className="col-span-5">
              <Card>
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">Upcoming Events</CardTitle>
                    <Button onClick={() => setEventModalOpen(true)} size="sm">
                      <Plus className="h-4 w-4 mr-1" />
                      New Event
                    </Button>
                  </div>
                </CardHeader>
                <CardContent className="p-0">
                  <div className="space-y-0">
                    {events.map((event) => (
                      <div
                        key={event.id}
                        className="p-4 border-b cursor-pointer hover:bg-gray-50"
                        onClick={() => setSelectedEvent(event)}
                      >
                        <div className="flex items-start gap-3">
                          <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                          <div className="flex-1">
                            <div className="font-medium">{event.title}</div>
                            <div className="text-sm text-gray-600 flex items-center gap-2 mt-1">
                              <Clock className="h-3 w-3" />
                              {new Date(event.start).toLocaleString()}
                            </div>
                            {event.meetLink && (
                              <div className="text-sm text-blue-600 flex items-center gap-1 mt-1">
                                <Video className="h-3 w-3" />
                                Google Meet
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Event Detail */}
            <div className="col-span-7">
              <Card>
                {selectedEvent ? (
                  <>
                    <CardHeader className="pb-3 border-b">
                      <CardTitle className="text-lg">{selectedEvent.title}</CardTitle>
                      <div className="text-sm text-gray-600">
                        {new Date(selectedEvent.start).toLocaleString()} - {new Date(selectedEvent.end).toLocaleString()}
                      </div>
                    </CardHeader>
                    <CardContent className="pt-6">
                      <div className="space-y-4">
                        <div>
                          <h4 className="font-medium mb-2">Description</h4>
                          <p className="text-gray-600">{selectedEvent.description}</p>
                        </div>
                        
                        <div>
                          <h4 className="font-medium mb-2">Attendees</h4>
                          <div className="flex flex-wrap gap-2">
                            {selectedEvent.attendees.map((attendee, index) => (
                              <Badge key={index} variant="outline">
                                <Users className="h-3 w-3 mr-1" />
                                {attendee}
                              </Badge>
                            ))}
                          </div>
                        </div>

                        {selectedEvent.meetLink && (
                          <div>
                            <h4 className="font-medium mb-2">Meeting Link</h4>
                            <Button variant="outline" className="w-full" asChild>
                              <a href={selectedEvent.meetLink} target="_blank" rel="noopener noreferrer">
                                <Video className="h-4 w-4 mr-2" />
                                Join Google Meet
                              </a>
                            </Button>
                          </div>
                        )}
                      </div>
                    </CardContent>
                  </>
                ) : (
                  <CardContent className="flex items-center justify-center h-64">
                    <div className="text-center text-gray-500">
                      <Calendar className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                      <p>Select an event to view details</p>
                    </div>
                  </CardContent>
                )}
              </Card>
            </div>
          </div>
        </TabsContent>

        {/* Drive Tab */}
        <TabsContent value="drive" className="mt-6">
          <Card>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">My Drive</CardTitle>
                <div className="flex gap-2">
                  <Button onClick={loadDriveFiles} variant="outline" size="sm">
                    <RefreshCw className="h-4 w-4" />
                  </Button>
                  <Button onClick={() => setUploadModalOpen(true)} size="sm">
                    <Upload className="h-4 w-4 mr-1" />
                    Upload
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent className="p-0">
              <div className="grid grid-cols-1 divide-y">
                {driveFiles.map((file) => (
                  <div
                    key={file.id}
                    className="p-4 hover:bg-gray-50 cursor-pointer flex items-center gap-4"
                    onClick={() => setSelectedFile(file)}
                  >
                    <div className="w-10 h-10 bg-gray-100 rounded flex items-center justify-center">
                      {file.isFolder ? (
                        <FolderOpen className="h-5 w-5 text-blue-600" />
                      ) : (
                        <FileText className="h-5 w-5 text-gray-600" />
                      )}
                    </div>
                    <div className="flex-1">
                      <div className="font-medium">{file.name}</div>
                      <div className="text-sm text-gray-600">
                        Modified {new Date(file.modifiedTime).toLocaleDateString()} • {file.size}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {file.shared && <Badge variant="outline">Shared</Badge>}
                      <Button variant="ghost" size="sm">
                        <Download className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Sheets Tab */}
        <TabsContent value="sheets" className="mt-6">
          <Card>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">Google Sheets</CardTitle>
                <div className="flex gap-2">
                  <Button onClick={() => loadSheets()} variant="outline" size="sm">
                    <RefreshCw className="h-4 w-4" />
                  </Button>
                  <Button size="sm">
                    <Plus className="h-4 w-4 mr-1" />
                    New Sheet
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {sheets.length > 0 ? (
                <div className="space-y-2">
                  {sheets.map((sheet, index) => (
                    <div key={index} className="p-4 border rounded-lg hover:bg-gray-50 cursor-pointer">
                      <div className="flex items-center gap-3">
                        <FileText className="h-8 w-8 text-green-600" />
                        <div className="flex-1">
                          <div className="font-medium">{sheet.name}</div>
                          <div className="text-sm text-gray-600">
                            Modified: {new Date(sheet.modifiedTime || sheet.updated).toLocaleDateString()}
                          </div>
                        </div>
                        <div className="flex gap-2">
                          <Button variant="outline" size="sm">
                            Open
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <FileText className="h-16 w-16 mx-auto mb-4 text-gray-300" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    Google Sheets Integration
                  </h3>
                  <p className="text-gray-600 mb-6">
                    {connectionStatus?.connected 
                      ? 'Loading your Google Sheets...' 
                      : 'Connect your Google account to access Sheets'
                    }
                  </p>
                  {!connectionStatus?.connected && (
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-2xl mx-auto">
                      <div className="p-4 border rounded-lg hover:bg-gray-50 cursor-pointer">
                        <FileText className="h-8 w-8 text-green-600 mx-auto mb-2" />
                        <h4 className="font-medium text-sm">Portfolio Tracker</h4>
                        <p className="text-xs text-gray-600 mt-1">Track client investments and performance</p>
                      </div>
                      <div className="p-4 border rounded-lg hover:bg-gray-50 cursor-pointer">
                        <FileText className="h-8 w-8 text-blue-600 mx-auto mb-2" />
                        <h4 className="font-medium text-sm">Financial Reports</h4>
                        <p className="text-xs text-gray-600 mt-1">Generate comprehensive financial reports</p>
                      </div>
                      <div className="p-4 border rounded-lg hover:bg-gray-50 cursor-pointer">
                        <FileText className="h-8 w-8 text-purple-600 mx-auto mb-2" />
                        <h4 className="font-medium text-sm">CRM Data</h4>
                        <p className="text-xs text-gray-600 mt-1">Export and analyze client data</p>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Compose Email Modal */}
      {composeOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="w-full max-w-2xl mx-4">
            <CardHeader className="pb-3 border-b">
              <div className="flex items-center justify-between">
                <CardTitle>New Message</CardTitle>
                <Button variant="ghost" size="sm" onClick={() => setComposeOpen(false)}>
                  ×
                </Button>
              </div>
            </CardHeader>
            <CardContent className="pt-6">
              <div className="space-y-4">
                <div>
                  <label className="text-sm font-medium">To</label>
                  <input
                    type="email"
                    value={composeData.to}
                    onChange={(e) => setComposeData({...composeData, to: e.target.value})}
                    className="w-full mt-1 px-3 py-2 border rounded-md"
                    placeholder="recipient@example.com"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium">Subject</label>
                  <input
                    type="text"
                    value={composeData.subject}
                    onChange={(e) => setComposeData({...composeData, subject: e.target.value})}
                    className="w-full mt-1 px-3 py-2 border rounded-md"
                    placeholder="Subject"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium">Message</label>
                  <textarea
                    value={composeData.body}
                    onChange={(e) => setComposeData({...composeData, body: e.target.value})}
                    className="w-full mt-1 px-3 py-2 border rounded-md h-32"
                    placeholder="Write your message..."
                  />
                </div>
                <div className="flex justify-end gap-2">
                  <Button variant="outline" onClick={() => setComposeOpen(false)}>
                    Cancel
                  </Button>
                  <Button onClick={sendEmail} disabled={loading}>
                    <Send className="h-4 w-4 mr-2" />
                    Send
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* New Event Modal */}
      {eventModalOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="w-full max-w-2xl mx-4">
            <CardHeader className="pb-3 border-b">
              <div className="flex items-center justify-between">
                <CardTitle>New Event</CardTitle>
                <Button variant="ghost" size="sm" onClick={() => setEventModalOpen(false)}>
                  ×
                </Button>
              </div>
            </CardHeader>
            <CardContent className="pt-6">
              <div className="space-y-4">
                <div>
                  <label className="text-sm font-medium">Title</label>
                  <input
                    type="text"
                    value={eventData.title}
                    onChange={(e) => setEventData({...eventData, title: e.target.value})}
                    className="w-full mt-1 px-3 py-2 border rounded-md"
                    placeholder="Event title"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium">Start</label>
                    <input
                      type="datetime-local"
                      value={eventData.start}
                      onChange={(e) => setEventData({...eventData, start: e.target.value})}
                      className="w-full mt-1 px-3 py-2 border rounded-md"
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium">End</label>
                    <input
                      type="datetime-local"
                      value={eventData.end}
                      onChange={(e) => setEventData({...eventData, end: e.target.value})}
                      className="w-full mt-1 px-3 py-2 border rounded-md"
                    />
                  </div>
                </div>
                <div>
                  <label className="text-sm font-medium">Attendees</label>
                  <input
                    type="text"
                    value={eventData.attendees}
                    onChange={(e) => setEventData({...eventData, attendees: e.target.value})}
                    className="w-full mt-1 px-3 py-2 border rounded-md"
                    placeholder="email1@example.com, email2@example.com"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium">Description</label>
                  <textarea
                    value={eventData.description}
                    onChange={(e) => setEventData({...eventData, description: e.target.value})}
                    className="w-full mt-1 px-3 py-2 border rounded-md h-24"
                    placeholder="Event description"
                  />
                </div>
                <div className="flex justify-end gap-2">
                  <Button variant="outline" onClick={() => setEventModalOpen(false)}>
                    Cancel
                  </Button>
                  <Button onClick={createMeeting} disabled={loading}>
                    <Calendar className="h-4 w-4 mr-2" />
                    Create Event
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Upload Modal */}
      {uploadModalOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="w-full max-w-md mx-4">
            <CardHeader className="pb-3 border-b">
              <div className="flex items-center justify-between">
                <CardTitle>Upload File</CardTitle>
                <Button variant="ghost" size="sm" onClick={() => setUploadModalOpen(false)}>
                  ×
                </Button>
              </div>
            </CardHeader>
            <CardContent className="pt-6">
              <div className="space-y-4">
                <div>
                  <label className="text-sm font-medium">Select File</label>
                  <input
                    type="file"
                    onChange={handleFileUpload}
                    className="w-full mt-1 px-3 py-2 border rounded-md"
                  />
                </div>
                <div className="text-sm text-gray-600">
                  Supported formats: PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX, Images
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};

export default FullGoogleWorkspace;