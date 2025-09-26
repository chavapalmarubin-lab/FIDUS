import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Mail, Calendar, FolderOpen, Plus, RefreshCw, Send, 
  Eye, Share2, Download, AlertCircle, CheckCircle, Users, Clock
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Alert, AlertDescription } from './ui/alert';

const RealGoogleIntegration = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('gmail');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // Data states
  const [gmailMessages, setGmailMessages] = useState([]);
  const [calendarEvents, setCalendarEvents] = useState([]);
  const [driveFiles, setDriveFiles] = useState([]);
  const [userInfo, setUserInfo] = useState(null);

  // Compose email state
  const [showComposeModal, setShowComposeModal] = useState(false);
  const [composeData, setComposeData] = useState({
    to: '',
    subject: '',
    body: '',
    html_body: ''
  });

  useEffect(() => {
    checkAuthenticationStatus();
  }, []);

  const checkAuthenticationStatus = async () => {
    try {
      // Check if already authenticated by trying to load Gmail messages
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/google/gmail/real-messages`, {
        credentials: 'include'
      });

      const data = await response.json();
      
      if (data.success && data.source === 'real_gmail_api') {
        setIsAuthenticated(true);
        setGmailMessages(data.messages);
        loadTabData('gmail');
      } else if (data.source === 'no_google_auth') {
        setIsAuthenticated(false);
      }
    } catch (err) {
      console.error('Auth check error:', err);
      setIsAuthenticated(false);
    }
  };

  const handleGoogleAuth = async () => {
    try {
      setLoading(true);
      setError('');

      // Get OAuth URL from backend
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/auth/google/url`, {
        credentials: 'include'
      });

      const data = await response.json();

      if (response.ok && data.success) {
        // Redirect to Google OAuth
        window.location.href = data.oauth_url;
      } else {
        throw new Error(data.detail || 'Failed to get OAuth URL');
      }

    } catch (err) {
      console.error('Google auth error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadTabData = async (tab) => {
    try {
      setLoading(true);
      setError('');

      switch (tab) {
        case 'gmail':
          await loadGmailMessages();
          break;
        case 'calendar':
          await loadCalendarEvents();
          break;
        case 'drive':
          await loadDriveFiles();
          break;
        default:
          break;
      }
    } catch (err) {
      console.error(`Load ${tab} data error:`, err);
      setError(`Failed to load ${tab} data`);
    } finally {
      setLoading(false);
    }
  };

  const loadGmailMessages = async () => {
    const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/google/gmail/real-messages`, {
      credentials: 'include'
    });

    const data = await response.json();
    
    if (data.success) {
      setGmailMessages(data.messages);
      if (data.source === 'real_gmail_api') {
        setIsAuthenticated(true);
      }
    } else {
      throw new Error(data.detail || 'Failed to load Gmail messages');
    }
  };

  const loadCalendarEvents = async () => {
    const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/google/calendar/real-events`, {
      credentials: 'include'
    });

    const data = await response.json();
    
    if (data.success) {
      setCalendarEvents(data.events);
    } else {
      throw new Error(data.detail || 'Failed to load calendar events');
    }
  };

  const loadDriveFiles = async () => {
    const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/google/drive/real-files`, {
      credentials: 'include'
    });

    const data = await response.json();
    
    if (data.success) {
      setDriveFiles(data.files);
    } else {
      throw new Error(data.detail || 'Failed to load Drive files');
    }
  };

  const handleComposeEmail = async (e) => {
    e.preventDefault();
    
    try {
      setLoading(true);
      setError('');

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/google/gmail/real-send`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify(composeData)
      });

      const data = await response.json();

      if (data.success) {
        setSuccess('Email sent successfully via Gmail API!');
        setShowComposeModal(false);
        setComposeData({ to: '', subject: '', body: '', html_body: '' });
        // Refresh Gmail messages
        await loadGmailMessages();
      } else {
        throw new Error(data.error || 'Failed to send email');
      }

    } catch (err) {
      console.error('Send email error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center"
        >
          <Card className="bg-gradient-to-br from-blue-50 to-indigo-100 border-0 shadow-lg">
            <CardContent className="p-8">
              <div className="space-y-6">
                <div className="space-y-2">
                  <h2 className="text-3xl font-bold text-gray-900">
                    Real Google APIs Integration
                  </h2>
                  <p className="text-gray-600 text-lg">
                    Connect your Google account to access Gmail, Calendar, and Drive
                  </p>
                </div>

                {error && (
                  <Alert className="bg-red-50 border-red-200">
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription className="text-red-800">{error}</AlertDescription>
                  </Alert>
                )}

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 my-8">
                  <div className="text-center p-4 bg-white rounded-lg shadow-sm">
                    <Mail className="h-8 w-8 text-blue-600 mx-auto mb-2" />
                    <h3 className="font-semibold">Gmail Integration</h3>
                    <p className="text-sm text-gray-600">Read and send emails</p>
                  </div>
                  <div className="text-center p-4 bg-white rounded-lg shadow-sm">
                    <Calendar className="h-8 w-8 text-green-600 mx-auto mb-2" />
                    <h3 className="font-semibold">Calendar Access</h3>
                    <p className="text-sm text-gray-600">Manage events and meetings</p>
                  </div>
                  <div className="text-center p-4 bg-white rounded-lg shadow-sm">
                    <FolderOpen className="h-8 w-8 text-orange-600 mx-auto mb-2" />
                    <h3 className="font-semibold">Drive Integration</h3>
                    <p className="text-sm text-gray-600">Access and share files</p>
                  </div>
                </div>

                <Button
                  onClick={handleGoogleAuth}
                  disabled={loading}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 text-lg"
                >
                  {loading ? (
                    <>
                      <RefreshCw className="h-5 w-5 mr-2 animate-spin" />
                      Connecting...
                    </>
                  ) : (
                    <>
                      <svg className="h-5 w-5 mr-2" viewBox="0 0 24 24">
                        <path
                          fill="currentColor"
                          d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                        />
                        <path
                          fill="currentColor"
                          d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                        />
                        <path
                          fill="currentColor"
                          d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                        />
                        <path
                          fill="currentColor"
                          d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                        />
                      </svg>
                      Connect Google Account
                    </>
                  )}
                </Button>

                <p className="text-sm text-gray-500 mt-4">
                  Secure OAuth 2.0 authentication with comprehensive API access
                </p>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Google APIs Integration
        </h1>
        <p className="text-gray-600">
          Manage your Gmail, Calendar, and Drive from FIDUS
        </p>
      </div>

      {error && (
        <Alert className="bg-red-50 border-red-200 mb-4">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription className="text-red-800">{error}</AlertDescription>
        </Alert>
      )}

      {success && (
        <Alert className="bg-green-50 border-green-200 mb-4">
          <CheckCircle className="h-4 w-4" />
          <AlertDescription className="text-green-800">{success}</AlertDescription>
        </Alert>
      )}

      <Tabs value={activeTab} onValueChange={(value) => {
        setActiveTab(value);
        loadTabData(value);
      }}>
        <TabsList className="grid w-full grid-cols-3 bg-slate-100">
          <TabsTrigger value="gmail" className="data-[state=active]:bg-blue-50 data-[state=active]:text-blue-900">
            <Mail className="h-4 w-4 mr-2" />
            Gmail
          </TabsTrigger>
          <TabsTrigger value="calendar" className="data-[state=active]:bg-green-50 data-[state=active]:text-green-900">
            <Calendar className="h-4 w-4 mr-2" />
            Calendar
          </TabsTrigger>
          <TabsTrigger value="drive" className="data-[state=active]:bg-orange-50 data-[state=active]:text-orange-900">
            <FolderOpen className="h-4 w-4 mr-2" />
            Drive
          </TabsTrigger>
        </TabsList>

        {/* Gmail Tab */}
        <TabsContent value="gmail" className="space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">Gmail Messages</h2>
            <div className="space-x-2">
              <Button
                onClick={() => setShowComposeModal(true)}
                className="bg-blue-600 hover:bg-blue-700"
              >
                <Plus className="h-4 w-4 mr-2" />
                Compose Email
              </Button>
              <Button
                onClick={() => loadGmailMessages()}
                variant="outline"
                disabled={loading}
              >
                <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
            </div>
          </div>

          <div className="grid gap-4">
            {gmailMessages.map((message) => (
              <Card key={message.id} className="hover:shadow-md transition-shadow">
                <CardContent className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-1">
                        <h3 className="font-semibold text-gray-900">{message.subject}</h3>
                        {message.unread && (
                          <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">
                            New
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-gray-600 mb-2">{message.sender}</p>
                      <p className="text-gray-700">{message.snippet || message.preview}</p>
                    </div>
                    <div className="text-sm text-gray-500">
                      {new Date(message.date).toLocaleDateString()}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Calendar Tab */}
        <TabsContent value="calendar" className="space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">Calendar Events</h2>
            <Button
              onClick={() => loadCalendarEvents()}
              variant="outline"
              disabled={loading}
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>

          <div className="grid gap-4">
            {calendarEvents.map((event) => (
              <Card key={event.id} className="hover:shadow-md transition-shadow">
                <CardContent className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-1">
                        <Clock className="h-4 w-4 text-blue-600" />
                        <h3 className="font-semibold text-gray-900">{event.summary}</h3>
                      </div>
                      {event.description && (
                        <p className="text-gray-700 mb-2">{event.description}</p>
                      )}
                      {event.location && (
                        <p className="text-sm text-gray-600 mb-2">📍 {event.location}</p>
                      )}
                      {event.attendees && event.attendees.length > 0 && (
                        <div className="flex items-center space-x-1 text-sm text-gray-600">
                          <Users className="h-3 w-3" />
                          <span>{event.attendees.length} attendees</span>
                        </div>
                      )}
                    </div>
                    <div className="text-sm text-gray-500">
                      {new Date(event.start).toLocaleDateString()}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Drive Tab */}
        <TabsContent value="drive" className="space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">Drive Files</h2>
            <Button
              onClick={() => loadDriveFiles()}
              variant="outline"
              disabled={loading}
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>

          <div className="grid gap-4">
            {driveFiles.map((file) => (
              <Card key={file.id} className="hover:shadow-md transition-shadow">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <FolderOpen className="h-8 w-8 text-blue-600" />
                      <div>
                        <h3 className="font-semibold text-gray-900">{file.name}</h3>
                        <p className="text-sm text-gray-600">
                          {file.size ? `${Math.round(file.size / 1024)} KB` : 'Unknown size'} • 
                          Modified {new Date(file.modifiedTime).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    <div className="space-x-2">
                      {file.webViewLink && (
                        <Button
                          onClick={() => window.open(file.webViewLink, '_blank')}
                          variant="outline"
                          size="sm"
                        >
                          <Eye className="h-4 w-4 mr-1" />
                          View
                        </Button>
                      )}
                      <Button variant="outline" size="sm">
                        <Share2 className="h-4 w-4 mr-1" />
                        Share
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>
      </Tabs>

      {/* Compose Email Modal */}
      {showComposeModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-lg w-full max-w-2xl mx-4 max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">Compose Email (Gmail API)</h3>
                <button
                  onClick={() => setShowComposeModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>
              
              <form onSubmit={handleComposeEmail} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    To
                  </label>
                  <input
                    type="email"
                    required
                    value={composeData.to}
                    onChange={(e) => setComposeData(prev => ({ ...prev, to: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="recipient@example.com"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Subject
                  </label>
                  <input
                    type="text"
                    required
                    value={composeData.subject}
                    onChange={(e) => setComposeData(prev => ({ ...prev, subject: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Email subject"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Message
                  </label>
                  <textarea
                    rows={6}
                    required
                    value={composeData.body}
                    onChange={(e) => setComposeData(prev => ({ ...prev, body: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 resize-vertical"
                    placeholder="Type your message here..."
                  />
                </div>
                
                <div className="flex justify-end space-x-3">
                  <Button
                    type="button"
                    onClick={() => setShowComposeModal(false)}
                    variant="outline"
                  >
                    Cancel
                  </Button>
                  <Button
                    type="submit"
                    disabled={loading}
                    className="bg-blue-600 hover:bg-blue-700"
                  >
                    {loading ? (
                      <>
                        <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                        Sending...
                      </>
                    ) : (
                      <>
                        <Send className="h-4 w-4 mr-2" />
                        Send via Gmail API
                      </>
                    )}
                  </Button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RealGoogleIntegration;