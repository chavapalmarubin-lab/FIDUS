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
  Activity,
  Globe,
  Settings,
  MoreVertical
} from 'lucide-react';
import apiAxios from '../utils/apiAxios';

const RealGoogleWorkspace = () => {
  const [connectionStatus, setConnectionStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('gmail');
  
  // Gmail State
  const [emails, setEmails] = useState([]);
  const [selectedEmail, setSelectedEmail] = useState(null);
  const [composeOpen, setComposeOpen] = useState(false);
  const [composeData, setComposeData] = useState({ to: '', subject: '', body: '' });
  const [emailLoading, setEmailLoading] = useState(false);
  
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

  useEffect(() => {
    initializeWorkspace();
  }, []);

  const initializeWorkspace = async () => {
    await testConnectionStatus();
    
    // Auto-load data for all tabs if connected
    const status = connectionStatus || await getConnectionStatus();
    if (status?.overall_status === 'fully_connected' || 
        status?.overall_status === 'partially_connected') {
      console.log('🔄 Auto-loading Google Workspace data...');
      
      // Load Gmail data
      if (status.services?.gmail?.status === 'connected') {
        await loadRealGmailMessages();
      }
      
      // Load Calendar data
      if (status.services?.calendar?.status === 'connected') {
        await loadRealCalendarEvents();
      }
      
      // Load Drive data  
      if (status.services?.drive?.status === 'connected') {
        await loadRealDriveFiles();
      }
    }
  };

  // Helper to get current connection status
  const getConnectionStatus = async () => {
    try {
      const response = await apiAxios.get('/google/connection/test-all');
      return response.data;
    } catch (error) {
      return null;
    }
  };

  // Test Google API connection status
  const testConnectionStatus = async () => {
    try {
      const response = await apiAxios.get('/google/connection/test-all');
      setConnectionStatus(response.data);
      console.log('🔗 Google Connection Status:', response.data.overall_status);
    } catch (error) {
      console.error('❌ Connection test failed:', error);
      setConnectionStatus({
        success: false,
        overall_status: 'test_failed',
        error: error.message,
        services: {}
      });
    }
  };

  // Load REAL Gmail messages from API
  const loadRealGmailMessages = async () => {
    setEmailLoading(true);
    try {
      console.log('📧 Fetching REAL Gmail messages...');
      const response = await apiAxios.get('/google/gmail/real-messages');
      
      if (response.data?.success && Array.isArray(response.data.messages)) {
        console.log(`✅ Loaded ${response.data.messages.length} real Gmail messages from your account`);
        
        // Transform Gmail API response to our format
        const transformedEmails = response.data.messages.map(email => ({
          id: email.gmail_id || email.id || Math.random().toString(),
          subject: email.subject || 'No Subject',
          sender: email.sender || email.from || 'Unknown Sender',
          recipient: email.to || email.recipient || 'You',
          date: email.date || email.internal_date || new Date().toISOString(),
          snippet: email.snippet || (email.body && email.body.substring(0, 150) + '...') || 'No preview available',
          read: email.labels ? !email.labels.includes('UNREAD') : true,
          starred: email.labels ? email.labels.includes('STARRED') : false,
          body: email.body || '<div style="padding: 20px; color: #333;"><p>Email content not available in preview</p></div>',
          labels: email.labels || [],
          threadId: email.thread_id,
          real_gmail: true
        }));
        
        setEmails(transformedEmails);
        
        // Auto-select first email if none selected
        if (transformedEmails.length > 0 && !selectedEmail) {
          setSelectedEmail(transformedEmails[0]);
        }
        
      } else if (response.data && response.data.error) {
        throw new Error(response.data.error);
      } else {
        console.warn('⚠️ No emails returned from Gmail API');
        setEmails([]);
        showConnectionPrompt();
      }
    } catch (error) {
      console.error('❌ Failed to load Gmail messages:', error);
      showGmailError(error.message);
    } finally {
      setEmailLoading(false);
    }
  };

  const showConnectionPrompt = () => {
    setEmails([{
      id: 'connect-prompt',
      subject: '📧 Connect to see your Gmail messages',
      sender: 'FIDUS System',
      recipient: 'You',
      snippet: 'Complete Google OAuth authentication to load your real Gmail inbox',
      date: new Date().toISOString(),
      read: true,
      starred: false,
      body: `
        <div style="padding: 30px; text-align: center; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; color: #333;">
          <div style="margin-bottom: 20px;">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="#4285f4" style="margin: 0 auto; display: block;">
              <path d="M20,18H18V9.25L12,13L6,9.25V18H4V6H5.2L12,10.25L18.8,6H20V18M15,2H9V4H15V2Z"/>
            </svg>
          </div>
          <h3 style="color: #1f2937; margin-bottom: 15px;">Gmail Integration Ready</h3>
          <p style="color: #6b7280; margin-bottom: 20px;">Connect your Google account to see your real emails here.</p>
          <div style="background: #f3f4f6; padding: 15px; border-radius: 8px; text-align: left;">
            <p style="margin: 0; font-size: 14px; color: #374151;"><strong>What you'll get:</strong></p>
            <ul style="margin: 10px 0 0 20px; color: #6b7280; font-size: 14px;">
              <li>Read your real Gmail messages</li>
              <li>Send emails directly from FIDUS</li>
              <li>Professional client communication</li>
              <li>Integrated CRM email tracking</li>
            </ul>
          </div>
        </div>
      `
    }]);
  };

  const showGmailError = (errorMessage) => {
    setEmails([{
      id: 'gmail-error',
      subject: '⚠️ Gmail API Error',
      sender: 'FIDUS System',
      recipient: 'You',
      snippet: `Gmail connection error: ${errorMessage}. Click to see resolution steps.`,
      date: new Date().toISOString(),
      read: false,
      starred: false,
      body: `
        <div style="padding: 30px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; color: #333;">
          <div style="background: #fee2e2; border: 1px solid #fca5a5; border-radius: 8px; padding: 20px; margin-bottom: 20px;">
            <h3 style="color: #dc2626; margin: 0 0 10px 0;">Gmail Connection Error</h3>
            <p style="color: #b91c1c; margin: 0;"><strong>Error:</strong> ${errorMessage}</p>
          </div>
          
          <h4 style="color: #1f2937; margin: 20px 0 10px 0;">Resolution Steps:</h4>
          <ol style="color: #374151; line-height: 1.6; padding-left: 20px;">
            <li>Click "Connect Google Workspace" button in the main interface</li>
            <li>Complete Google OAuth authentication at accounts.google.com</li>
            <li>Grant Gmail API permissions to FIDUS</li>
            <li>Return to this page and refresh</li>
            <li>If the issue persists, check the Connection Monitor tab</li>
          </ol>
          
          <div style="background: #dbeafe; border: 1px solid #93c5fd; border-radius: 8px; padding: 15px; margin-top: 20px;">
            <p style="margin: 0; color: #1e40af;"><strong>Note:</strong> Make sure you're using a Gmail account and have granted all necessary permissions during OAuth.</p>
          </div>
        </div>
      `
    }]);
  };

  // Send email via Gmail API
  const sendRealEmail = async () => {
    if (!composeData.to || !composeData.subject || !composeData.body) {
      alert('Please fill in all required fields (To, Subject, Message)');
      return;
    }

    setLoading(true);
    try {
      console.log('📤 Sending email via Gmail API...', composeData);
      
      const response = await apiAxios.post('/google/gmail/real-send', {
        to: composeData.to,
        subject: composeData.subject,
        body: composeData.body,
        html: true
      });
      
      if (response.data && response.data.success) {
        alert('✅ Email sent successfully via Gmail!');
        setComposeOpen(false);
        setComposeData({ to: '', subject: '', body: '' });
        
        // Refresh emails to show sent message
        setTimeout(() => {
          loadRealGmailMessages();
        }, 1000);
      } else {
        throw new Error(response.data?.error || 'Failed to send email');
      }
      
    } catch (error) {
      console.error('❌ Email sending failed:', error);
      alert(`❌ Failed to send email: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Load real calendar events
  const loadRealCalendarEvents = async () => {
    try {
      console.log('📅 Loading real calendar events...');
      const response = await apiAxios.get('/google/calendar/events');
      
      if (response.data?.success && Array.isArray(response.data.events)) {
        console.log(`✅ Loaded ${response.data.events.length} calendar events`);
        setEvents(response.data.events);
      }
    } catch (error) {
      console.error('❌ Failed to load calendar events:', error);
    }
  };

  // Load real drive files
  const loadRealDriveFiles = async () => {
    try {
      console.log('📁 Loading real Drive files...');
      const response = await apiAxios.get('/google/drive/real-files');
      
      if (response.data?.success && Array.isArray(response.data.files)) {
        console.log(`✅ Loaded ${response.data.files.length} Drive files`);
        setDriveFiles(response.data.files);
      }
    } catch (error) {
      console.error('❌ Failed to load Drive files:', error);
    }
  };

  // Handle Google OAuth connection
  const connectToGoogle = async () => {
    setLoading(true);
    try {
      console.log('🔗 Initiating Google OAuth...');
      const response = await apiAxios.get('/auth/google/url');
      
      if (response.data.success) {
        console.log('🚀 Redirecting to Google OAuth...');
        window.location.href = response.data.auth_url;
      } else {
        throw new Error(response.data.error || 'Failed to get OAuth URL');
      }
    } catch (error) {
      console.error('❌ OAuth initiation failed:', error);
      alert('Failed to connect to Google. Please try again.');
      setLoading(false);
    }
  };

  // Connection Status Banner Component
  const ConnectionBanner = () => {
    if (!connectionStatus) return null;

    const isConnected = connectionStatus.overall_status === 'fully_connected';
    const isPartial = connectionStatus.overall_status === 'partially_connected';
    
    return (
      <div className={`p-4 rounded-lg border-l-4 mb-6 ${
        isConnected 
          ? 'bg-green-50 border-green-400 text-green-800'
          : isPartial
          ? 'bg-yellow-50 border-yellow-400 text-yellow-800'  
          : 'bg-red-50 border-red-400 text-red-800'
      }`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            {isConnected ? (
              <Wifi className="h-5 w-5 text-green-600" />
            ) : (
              <WifiOff className="h-5 w-5 text-red-600" />
            )}
            <div>
              <span className="font-medium">
                {isConnected ? '✅ Google Workspace Connected' : 
                 isPartial ? '⚠️ Partial Connection' : 
                 '❌ Not Connected'}
              </span>
              <p className="text-sm mt-1">
                {isConnected 
                  ? `All services online • ${connectionStatus.connection_quality?.success_rate || 0}% success rate`
                  : isPartial
                  ? `${connectionStatus.connection_quality?.successful_tests || 0}/${connectionStatus.connection_quality?.total_tests || 4} services working`
                  : 'Click "Connect Google Workspace" to get started'}
              </p>
            </div>
          </div>
          
          {!isConnected && (
            <Button 
              onClick={connectToGoogle}
              disabled={loading}
              className="bg-blue-600 hover:bg-blue-700 text-white"
            >
              {loading ? 'Connecting...' : 'Connect Google Workspace'}
            </Button>
          )}
        </div>
      </div>
    );
  };

  // Gmail Interface Component
  const GmailInterface = () => (
    <div className="grid grid-cols-12 gap-6 h-[700px]">
      {/* Email List */}
      <div className="col-span-5">
        <Card className="h-full">
          <CardHeader className="pb-3 border-b">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Mail className="h-5 w-5 text-red-500" />
                <CardTitle className="text-lg">
                  Inbox ({emails.length})
                </CardTitle>
                {emailLoading && <RefreshCw className="h-4 w-4 animate-spin text-blue-500" />}
              </div>
              <div className="flex gap-2">
                <Button 
                  onClick={loadRealGmailMessages} 
                  variant="outline" 
                  size="sm"
                  disabled={emailLoading}
                >
                  <RefreshCw className={`h-4 w-4 ${emailLoading ? 'animate-spin' : ''}`} />
                </Button>
                <Button onClick={() => setComposeOpen(true)} size="sm">
                  <Plus className="h-4 w-4 mr-1" />
                  Compose
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent className="p-0">
            <div className="max-h-[580px] overflow-y-auto">
              {emails.map((email) => (
                <div
                  key={email.id}
                  className={`p-4 border-b cursor-pointer hover:bg-gray-50 transition-colors ${
                    selectedEmail?.id === email.id ? 'bg-blue-50 border-l-4 border-l-blue-500' : ''
                  } ${!email.read ? 'bg-blue-25 font-semibold' : ''}`}
                  onClick={() => setSelectedEmail(email)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-2">
                      {email.starred && <Star className="h-4 w-4 text-yellow-500 fill-current" />}
                      {email.real_gmail && <Badge variant="outline" className="text-xs">Real</Badge>}
                      <span className={`text-sm ${!email.read ? 'font-bold text-gray-900' : 'text-gray-700'}`}>
                        {email.sender}
                      </span>
                    </div>
                    <span className="text-xs text-gray-500">
                      {new Date(email.date).toLocaleDateString()}
                    </span>
                  </div>
                  <div className={`text-sm mt-1 ${!email.read ? 'font-semibold text-gray-900' : 'text-gray-800'}`}>
                    {email.subject}
                  </div>
                  <div className="text-xs text-gray-600 mt-1 line-clamp-2">
                    {email.snippet}
                  </div>
                </div>
              ))}
              
              {emails.length === 0 && !emailLoading && (
                <div className="p-8 text-center text-gray-500">
                  <Mail className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                  <p>No emails loaded</p>
                  <Button 
                    onClick={loadRealGmailMessages} 
                    variant="outline" 
                    size="sm" 
                    className="mt-2"
                  >
                    Load Gmail Messages
                  </Button>
                </div>
              )}
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
                  <div className="flex-1">
                    <CardTitle className="text-lg">{selectedEmail.subject}</CardTitle>
                    <div className="text-sm text-gray-600 mt-1">
                      <span className="font-medium">From:</span> {selectedEmail.sender}
                    </div>
                    <div className="text-sm text-gray-600">
                      <span className="font-medium">To:</span> {selectedEmail.recipient}
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      {new Date(selectedEmail.date).toLocaleString()}
                    </div>
                  </div>
                  <div className="flex gap-2 ml-4">
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
              <CardContent className="pt-6 max-h-[520px] overflow-y-auto">
                <div 
                  className="prose max-w-none"
                  style={{ color: '#374151' }}
                  dangerouslySetInnerHTML={{ __html: selectedEmail.body }}
                />
              </CardContent>
            </>
          ) : (
            <CardContent className="flex items-center justify-center h-full">
              <div className="text-center text-gray-500">
                <Mail className="h-16 w-16 mx-auto mb-4 text-gray-300" />
                <p className="text-lg font-medium mb-2">Select an email to read</p>
                <p className="text-sm">Choose a message from your inbox to view its contents</p>
              </div>
            </CardContent>
          )}
        </Card>
      </div>
    </div>
  );

  // Auto-load data when tab changes
  useEffect(() => {
    switch (activeTab) {
      case 'gmail':
        if (connectionStatus?.services?.gmail?.status === 'connected') {
          loadRealGmailMessages();
        }
        break;
      case 'calendar':
        if (connectionStatus?.services?.calendar?.status === 'connected') {
          loadRealCalendarEvents();
        }
        break;
      case 'drive':
        if (connectionStatus?.services?.drive?.status === 'connected') {
          loadRealDriveFiles();
        }
        break;
    }
  }, [activeTab, connectionStatus]);

  return (
    <div className="w-full space-y-6">
      {/* Header */}
      <Card className="border-l-4 border-l-blue-500">
        <CardHeader>
          <CardTitle className="flex items-center gap-3">
            <div className="p-2 bg-gradient-to-r from-red-500 to-blue-500 rounded-lg">
              <Globe className="h-6 w-6 text-white" />
            </div>
            <div>
              <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-red-500 bg-clip-text text-transparent">
                Google Workspace
              </span>
              <p className="text-sm text-gray-600 mt-1 font-normal">
                Real Gmail, Calendar, and Drive integration for FIDUS
              </p>
            </div>
          </CardTitle>
        </CardHeader>
      </Card>

      {/* Connection Status */}
      <ConnectionBanner />

      {/* Main Interface */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-3 bg-gray-100 p-1">
          <TabsTrigger 
            value="gmail" 
            className="flex items-center gap-2 data-[state=active]:bg-white data-[state=active]:text-red-600 data-[state=active]:shadow-sm"
          >
            <Mail className="h-4 w-4" />
            Gmail
            {connectionStatus?.services?.gmail?.status === 'connected' && (
              <CheckCircle className="h-3 w-3 text-green-500" />
            )}
          </TabsTrigger>
          <TabsTrigger 
            value="calendar" 
            className="flex items-center gap-2 data-[state=active]:bg-white data-[state=active]:text-blue-600 data-[state=active]:shadow-sm"
          >
            <Calendar className="h-4 w-4" />
            Calendar
            {connectionStatus?.services?.calendar?.status === 'connected' && (
              <CheckCircle className="h-3 w-3 text-green-500" />
            )}
          </TabsTrigger>
          <TabsTrigger 
            value="drive" 
            className="flex items-center gap-2 data-[state=active]:bg-white data-[state=active]:text-green-600 data-[state=active]:shadow-sm"
          >
            <FolderOpen className="h-4 w-4" />
            Drive
            {connectionStatus?.services?.drive?.status === 'connected' && (
              <CheckCircle className="h-3 w-3 text-green-500" />
            )}
          </TabsTrigger>
        </TabsList>

        <TabsContent value="gmail" className="mt-6">
          <GmailInterface />
        </TabsContent>

        <TabsContent value="calendar" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="h-5 w-5 text-blue-600" />
                Google Calendar Events ({events.length})
                <Button 
                  onClick={loadRealCalendarEvents}
                  variant="outline" 
                  size="sm"
                  className="ml-auto"
                  disabled={connectionStatus?.services?.calendar?.status !== 'connected'}
                >
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Refresh
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent>
              {events.length > 0 ? (
                <div className="space-y-4 max-h-96 overflow-y-auto">
                  {events.map((event, index) => (
                    <div key={event.id || index} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h3 className="font-semibold text-gray-800 mb-2">{event.summary || 'No Title'}</h3>
                          <div className="text-sm text-gray-600 space-y-1">
                            <div className="flex items-center gap-2">
                              <Calendar className="h-4 w-4" />
                              <span>{new Date(event.start).toLocaleString()}</span>
                              {event.end && <span>→ {new Date(event.end).toLocaleString()}</span>}
                            </div>
                            {event.location && (
                              <div className="flex items-center gap-2">
                                <span>📍 {event.location}</span>
                              </div>
                            )}
                            {event.attendees && event.attendees.length > 0 && (
                              <div className="flex items-center gap-2">
                                <span>👥 {event.attendees.map(a => a.email).join(', ')}</span>
                              </div>
                            )}
                          </div>
                          {event.description && (
                            <div className="mt-2 text-sm text-gray-700 bg-gray-50 p-2 rounded">
                              {event.description.substring(0, 200)}
                              {event.description.length > 200 && '...'}
                            </div>
                          )}
                        </div>
                        <div className="ml-4 flex flex-col items-end gap-2">
                          <span className={`px-2 py-1 text-xs rounded ${
                            event.status === 'confirmed' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                          }`}>
                            {event.status || 'Unknown'}
                          </span>
                          {event.html_link && (
                            <a 
                              href={event.html_link} 
                              target="_blank" 
                              rel="noopener noreferrer"
                              className="text-blue-500 text-xs hover:underline"
                            >
                              View in Calendar
                            </a>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <Calendar className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                  <p>No calendar events found</p>
                  <Button 
                    onClick={loadRealCalendarEvents}
                    variant="outline" 
                    className="mt-4"
                    disabled={connectionStatus?.services?.calendar?.status !== 'connected'}
                  >
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Load Calendar Events
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="drive" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FolderOpen className="h-5 w-5 text-green-600" />
                Google Drive Integration
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-gray-500">
                <FolderOpen className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                <p>Drive interface coming in next update</p>
                <Button 
                  onClick={loadRealDriveFiles}
                  variant="outline" 
                  className="mt-4"
                  disabled={connectionStatus?.services?.drive?.status !== 'connected'}
                >
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Load Drive Files
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Compose Email Modal */}
      {composeOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="w-full max-w-2xl mx-4 max-h-[90vh] overflow-y-auto">
            <CardHeader className="pb-3 border-b">
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <Send className="h-5 w-5 text-blue-600" />
                  Compose Email
                </CardTitle>
                <Button 
                  variant="ghost" 
                  size="sm" 
                  onClick={() => setComposeOpen(false)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  ×
                </Button>
              </div>
            </CardHeader>
            <CardContent className="pt-6">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    To
                  </label>
                  <input
                    type="email"
                    value={composeData.to}
                    onChange={(e) => setComposeData({...composeData, to: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900"
                    placeholder="recipient@example.com"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Subject
                  </label>
                  <input
                    type="text"
                    value={composeData.subject}
                    onChange={(e) => setComposeData({...composeData, subject: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900"
                    placeholder="Email subject"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Message
                  </label>
                  <textarea
                    value={composeData.body}
                    onChange={(e) => setComposeData({...composeData, body: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md h-40 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none text-gray-900"
                    placeholder="Write your message here..."
                  />
                </div>
                
                <div className="flex justify-end gap-3 pt-4 border-t">
                  <Button 
                    variant="outline" 
                    onClick={() => setComposeOpen(false)}
                    className="px-6"
                  >
                    Cancel
                  </Button>
                  <Button 
                    onClick={sendRealEmail} 
                    disabled={loading || !composeData.to || !composeData.subject}
                    className="bg-blue-600 hover:bg-blue-700 px-6"
                  >
                    {loading ? (
                      <>
                        <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                        Sending...
                      </>
                    ) : (
                      <>
                        <Send className="h-4 w-4 mr-2" />
                        Send Email
                      </>
                    )}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};

export default RealGoogleWorkspace;