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
  MoreVertical,
  Eye,
  ExternalLink
} from 'lucide-react';
import apiAxios from '../utils/apiAxios';

const ClientGoogleWorkspace = ({ user }) => {
  const [connectionStatus, setConnectionStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('emails');
  
  // Client-specific Google data
  const [clientEmails, setClientEmails] = useState([]);
  const [clientMeetings, setClientMeetings] = useState([]);
  const [clientDocuments, setClientDocuments] = useState([]);
  const [googleLoading, setGoogleLoading] = useState(false);
  
  // Compose states
  const [composeOpen, setComposeOpen] = useState(false);
  const [composeData, setComposeData] = useState({ to: 'admin@fidus.com', subject: '', body: '' });
  const [meetingModalOpen, setMeetingModalOpen] = useState(false);
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);

  useEffect(() => {
    initializeClientGoogleWorkspace();
  }, [user]);

  const initializeClientGoogleWorkspace = async () => {
    await testClientGoogleConnection();
    await loadClientGoogleData();
  };

  // Test Google connection for this client
  const testClientGoogleConnection = async () => {
    try {
      const response = await apiAxios.get('/google/client-connection/test-all', {
        headers: {
          'X-Client-Email': user.email,
          'X-Client-ID': user.id
        }
      });
      setConnectionStatus(response.data);
      console.log('🔗 Client Google Connection Status:', response.data.overall_status);
    } catch (error) {
      console.error('❌ Client connection test failed:', error);
      setConnectionStatus({
        success: false,
        overall_status: 'test_failed',
        error: error.message,
        services: {}
      });
    }
  };

  // Load client-specific FIDUS data (not personal Google data)
  const loadClientGoogleData = async () => {
    setGoogleLoading(true);
    try {
      console.log('🔍 Loading FIDUS data for client:', user.email);

      // Load emails that FIDUS has sent TO this client (not from client's Gmail)
      const emailResponse = await apiAxios.get(`/fidus/client-communications/${user.id}`);
      if (emailResponse.data.success) {
        setClientEmails(emailResponse.data.emails);
        console.log(`📧 Loaded ${emailResponse.data.emails.length} FIDUS communications for ${user.name}`);
      }

      // Load meeting requests and scheduled meetings for this client
      const meetingsResponse = await apiAxios.get(`/fidus/client-meetings/${user.id}`);
      if (meetingsResponse.data.success) {
        setClientMeetings(meetingsResponse.data.meetings);
        console.log(`📅 Loaded ${meetingsResponse.data.meetings.length} FIDUS meetings for ${user.name}`);
      }

      // Load client's FIDUS document folder (pre-created by admin)
      const documentsResponse = await apiAxios.get(`/fidus/client-drive-folder/${user.id}`);
      if (documentsResponse.data.success) {
        setClientDocuments(documentsResponse.data.documents);
        console.log(`📁 Loaded ${documentsResponse.data.documents.length} documents from client FIDUS folder`);
      }

    } catch (error) {
      console.error('❌ Failed to load client FIDUS data:', error);
      // Set empty arrays on error
      setClientEmails([]);
      setClientMeetings([]);
      setClientDocuments([]);
    } finally {
      setGoogleLoading(false);
    }
  };

  // Send email to admin/FIDUS team
  const sendEmailToFIDUS = async () => {
    if (!composeData.subject || !composeData.body) {
      alert('Please fill in subject and message');
      return;
    }

    setLoading(true);
    try {
      const response = await apiAxios.post('/google/gmail/client-send', {
        from_client: user.email,
        client_name: user.name,
        to: composeData.to,
        subject: composeData.subject,
        body: composeData.body,
        client_id: user.id,
        html: true
      });

      if (response.data.success) {
        alert('✅ Message sent to FIDUS team successfully!');
        setComposeOpen(false);
        setComposeData({ to: 'admin@fidus.com', subject: '', body: '' });
        
        // Refresh emails
        setTimeout(() => {
          loadClientGoogleData();
        }, 1000);
      } else {
        throw new Error(response.data.error || 'Failed to send message');
      }
    } catch (error) {
      console.error('❌ Message sending failed:', error);
      alert(`❌ Failed to send message: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Request meeting with FIDUS team (sends to admin portal)
  const requestMeetingWithFIDUS = async () => {
    if (!composeData.subject || !composeData.body) {
      alert('Please provide meeting subject and details');
      return;
    }

    setLoading(true);
    try {
      const response = await apiAxios.post('/fidus/client-meeting-request', {
        client_id: user.id,
        client_name: user.name,
        client_email: user.email,
        meeting_subject: composeData.subject,
        meeting_details: composeData.body,
        requested_at: new Date().toISOString()
      });

      if (response.data.success) {
        alert('✅ Meeting request sent to FIDUS team! You will be contacted to schedule your meeting.');
        setComposeOpen(false);
        setComposeData({ to: 'admin@fidus.com', subject: '', body: '' });
        
        // Refresh meetings to show the request
        setTimeout(() => {
          loadClientGoogleData();
        }, 1000);
      } else {
        throw new Error(response.data.error || 'Failed to send meeting request');
      }
    } catch (error) {
      console.error('❌ Meeting request failed:', error);
      alert(`❌ Failed to send meeting request: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Upload document to client's FIDUS folder
  const uploadDocumentToFIDUS = async (file) => {
    if (!file) return;

    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('client_id', user.id);
      formData.append('client_name', user.name);

      const response = await apiAxios.post('/fidus/client-document-upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      if (response.data.success) {
        alert('✅ Document uploaded successfully to your FIDUS folder!');
        
        // Refresh documents
        setTimeout(() => {
          loadClientGoogleData();
        }, 1000);
      } else {
        throw new Error(response.data.error || 'Failed to upload document');
      }
    } catch (error) {
      console.error('❌ Document upload failed:', error);
      alert(`Failed to upload document: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Connection Status Banner Component
  const ClientConnectionBanner = () => {
    if (!connectionStatus) return null;

    const isConnected = connectionStatus.overall_status === 'fully_connected';
    const isPartial = connectionStatus.overall_status === 'partially_connected';
    
    return (
      <div className={`p-4 rounded-lg border-l-4 mb-6 ${
        isConnected 
          ? 'bg-green-50 border-green-400 text-green-800'
          : isPartial
          ? 'bg-yellow-50 border-yellow-400 text-yellow-800'  
          : 'bg-blue-50 border-blue-400 text-blue-800'
      }`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            {isConnected ? (
              <Wifi className="h-5 w-5 text-green-600" />
            ) : (
              <Globe className="h-5 w-5 text-blue-600" />
            )}
            <div>
              <span className="font-medium">
                {isConnected ? '✅ Your FIDUS Google Integration Active' : 
                 isPartial ? '⚠️ Partial Google Services' : 
                 '📧 FIDUS Communication Hub'}
              </span>
              <p className="text-sm mt-1">
                {isConnected 
                  ? `All your communications and documents are synced with FIDUS • ${connectionStatus.connection_quality?.success_rate || 0}% uptime`
                  : isPartial
                  ? `${connectionStatus.connection_quality?.successful_tests || 0}/${connectionStatus.connection_quality?.total_tests || 4} services active`
                  : 'View your communication history and documents with the FIDUS team'}
              </p>
            </div>
          </div>
          
          <Button 
            onClick={loadClientGoogleData}
            variant="outline" 
            size="sm"
            disabled={googleLoading}
          >
            <RefreshCw className={`h-4 w-4 mr-1 ${googleLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>
    );
  };

  return (
    <div className="w-full space-y-6">
      {/* Header */}
      <Card className="border-l-4 border-l-cyan-500">
        <CardHeader>
          <CardTitle className="flex items-center gap-3">
            <div className="p-2 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-lg">
              <Globe className="h-6 w-6 text-white" />
            </div>
            <div>
              <span className="text-xl font-bold bg-gradient-to-r from-cyan-600 to-blue-500 bg-clip-text text-transparent">
                My FIDUS Workspace
              </span>
              <p className="text-sm text-gray-600 mt-1 font-normal">
                Your personalized communication and document hub
              </p>
            </div>
          </CardTitle>
        </CardHeader>
      </Card>

      {/* Connection Status */}
      <ClientConnectionBanner />

      {/* Main Interface */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-3 bg-gray-100 p-1">
          <TabsTrigger 
            value="emails" 
            className="flex items-center gap-2 data-[state=active]:bg-white data-[state=active]:text-red-600 data-[state=active]:shadow-sm"
          >
            <Mail className="h-4 w-4" />
            My Emails
            {clientEmails.length > 0 && (
              <Badge className="bg-red-100 text-red-800 text-xs ml-1">
                {clientEmails.length}
              </Badge>
            )}
          </TabsTrigger>
          <TabsTrigger 
            value="meetings" 
            className="flex items-center gap-2 data-[state=active]:bg-white data-[state=active]:text-blue-600 data-[state=active]:shadow-sm"
          >
            <Calendar className="h-4 w-4" />
            My Meetings
            {clientMeetings.length > 0 && (
              <Badge className="bg-blue-100 text-blue-800 text-xs ml-1">
                {clientMeetings.length}
              </Badge>
            )}
          </TabsTrigger>
          <TabsTrigger 
            value="documents" 
            className="flex items-center gap-2 data-[state=active]:bg-white data-[state=active]:text-green-600 data-[state=active]:shadow-sm"
          >
            <FolderOpen className="h-4 w-4" />
            My Documents
            {clientDocuments.length > 0 && (
              <Badge className="bg-green-100 text-green-800 text-xs ml-1">
                {clientDocuments.length}
              </Badge>
            )}
          </TabsTrigger>
        </TabsList>

        {/* Emails Tab */}
        <TabsContent value="emails" className="mt-6">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold">Communications from FIDUS</h3>
              <Button
                onClick={() => setComposeOpen(true)}
                className="bg-red-500 hover:bg-red-600 text-white"
              >
                <Plus className="w-4 h-4 mr-2" />
                Contact FIDUS
              </Button>
            </div>

            {googleLoading ? (
              <div className="flex items-center justify-center py-8">
                <RefreshCw className="w-6 h-6 animate-spin text-blue-500" />
                <span className="ml-2">Loading your emails...</span>
              </div>
            ) : clientEmails.length > 0 ? (
              <div className="space-y-3">
                {clientEmails.map((email, index) => (
                  <Card key={index} className="hover:shadow-md transition-shadow border-l-4 border-l-red-200">
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <Mail className="w-4 h-4 text-red-500" />
                            <span className="font-medium text-sm">{email.subject}</span>
                            {email.labels?.includes('UNREAD') && (
                              <Badge className="bg-blue-100 text-blue-800 text-xs">New</Badge>
                            )}
                          </div>
                          <p className="text-xs text-gray-600 mb-1">
                            <span className="font-medium">From:</span> {email.from} 
                            <span className="mx-2">•</span>
                            <span className="font-medium">Date:</span> {new Date(email.date).toLocaleString()}
                          </p>
                          <p className="text-sm text-gray-700">{email.snippet}</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : (
              <Card>
                <CardContent className="p-8 text-center">
                  <Mail className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                  <p className="text-gray-500 mb-4">No communications from FIDUS yet</p>
                  <Button
                    onClick={() => setComposeOpen(true)}
                    className="bg-red-500 hover:bg-red-600"
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    Send First Message
                  </Button>
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>

        {/* Meetings Tab */}
        <TabsContent value="meetings" className="mt-6">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold">My Meetings with FIDUS</h3>
              <Button
                onClick={() => setMeetingModalOpen(true)}
                className="bg-blue-500 hover:bg-blue-600 text-white"
              >
                <Calendar className="w-4 h-4 mr-2" />
                Request Meeting
              </Button>
            </div>

            {googleLoading ? (
              <div className="flex items-center justify-center py-8">
                <RefreshCw className="w-6 h-6 animate-spin text-blue-500" />
                <span className="ml-2">Loading your meetings...</span>
              </div>
            ) : clientMeetings.length > 0 ? (
              <div className="space-y-3">
                {clientMeetings.map((meeting, index) => (
                  <Card key={index} className="hover:shadow-md transition-shadow border-l-4 border-l-blue-200">
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <Calendar className="w-4 h-4 text-blue-500" />
                            <span className="font-medium">{meeting.title}</span>
                            {meeting.status === 'upcoming' && (
                              <Badge className="bg-green-100 text-green-800 text-xs">Upcoming</Badge>
                            )}
                          </div>
                          <p className="text-sm text-gray-600 mb-2">
                            {new Date(meeting.start_time).toLocaleString()}
                          </p>
                          {meeting.description && (
                            <p className="text-sm text-gray-700 mb-2">{meeting.description}</p>
                          )}
                          {meeting.meet_link && (
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => window.open(meeting.meet_link, '_blank')}
                            >
                              <Video className="w-4 h-4 mr-2" />
                              Join Meeting
                            </Button>
                          )}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : (
              <Card>
                <CardContent className="p-8 text-center">
                  <Calendar className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                  <p className="text-gray-500 mb-4">No meetings scheduled with FIDUS yet</p>
                  <Button
                    onClick={() => setComposeOpen(true)}
                    className="bg-blue-500 hover:bg-blue-600"
                  >
                    <Calendar className="w-4 h-4 mr-2" />
                    Request First Meeting
                  </Button>
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>

        {/* Documents Tab */}
        <TabsContent value="documents" className="mt-6">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold">My FIDUS Document Folder</h3>
              <Button
                onClick={() => setUploadModalOpen(true)}
                className="bg-green-500 hover:bg-green-600 text-white"
                disabled={loading}
              >
                <Upload className="w-4 h-4 mr-2" />
                Upload Document
              </Button>
            </div>

            {googleLoading ? (
              <div className="flex items-center justify-center py-8">
                <RefreshCw className="w-6 h-6 animate-spin text-green-500" />
                <span className="ml-2">Loading your documents...</span>
              </div>
            ) : clientDocuments.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {clientDocuments.map((doc, index) => (
                  <Card key={index} className="hover:shadow-md transition-shadow border-l-4 border-l-green-200">
                    <CardContent className="p-4">
                      <div className="flex items-start gap-3">
                        <FileText className="w-8 h-8 text-green-500 mt-1" />
                        <div className="flex-1">
                          <h4 className="font-medium text-sm mb-1">{doc.name}</h4>
                          <p className="text-xs text-gray-600 mb-2">
                            Modified: {new Date(doc.modified_time).toLocaleDateString()}
                          </p>
                          <div className="flex gap-1">
                            {doc.web_view_link && (
                              <Button 
                                variant="outline" 
                                size="sm"
                                onClick={() => window.open(doc.web_view_link, '_blank')}
                              >
                                <Eye className="w-3 h-3 mr-1" />
                                View
                              </Button>
                            )}
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : (
              <Card>
                <CardContent className="p-8 text-center">
                  <FolderOpen className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                  <p className="text-gray-500 mb-4">Your FIDUS document folder is ready</p>
                  <p className="text-sm text-gray-400 mb-4">
                    Upload documents to share with the FIDUS team securely
                  </p>
                  <Button
                    onClick={() => setUploadModalOpen(true)}
                    className="bg-green-500 hover:bg-green-600"
                    disabled={loading}
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    Upload First Document
                  </Button>
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>
      </Tabs>

      {/* Compose Message Modal */}
      {composeOpen && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
          <Card className="w-full max-w-2xl mx-4">
            <CardHeader className="border-b">
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <Mail className="w-5 h-5 text-red-500" />
                  Contact FIDUS Team
                </CardTitle>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setComposeOpen(false)}
                >
                  ✕
                </Button>
              </div>
            </CardHeader>
            <CardContent className="p-6">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    To
                  </label>
                  <select
                    value={composeData.to}
                    onChange={(e) => setComposeData({...composeData, to: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-red-500 focus:border-red-500"
                  >
                    <option value="admin@fidus.com">FIDUS Admin Team</option>
                    <option value="support@fidus.com">FIDUS Support</option>
                    <option value="portfolio@fidus.com">Portfolio Management</option>
                    <option value="compliance@fidus.com">Compliance Team</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Subject
                  </label>
                  <input
                    type="text"
                    value={composeData.subject}
                    onChange={(e) => setComposeData({...composeData, subject: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-red-500 focus:border-red-500"
                    placeholder="Subject of your message"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Message
                  </label>
                  <textarea
                    value={composeData.body}
                    onChange={(e) => setComposeData({...composeData, body: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md h-40 focus:ring-2 focus:ring-red-500 focus:border-red-500 resize-none"
                    placeholder="Write your message to the FIDUS team..."
                  />
                </div>
                
                <div className="flex justify-end gap-3 pt-4 border-t">
                  <Button
                    variant="outline"
                    onClick={() => setComposeOpen(false)}
                  >
                    Cancel
                  </Button>
                  <Button
                    onClick={sendEmailToFIDUS}
                    disabled={loading || !composeData.subject || !composeData.body}
                    className="bg-red-500 hover:bg-red-600"
                  >
                    {loading ? (
                      <>
                        <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                        Sending...
                      </>
                    ) : (
                      <>
                        <Send className="w-4 h-4 mr-2" />
                        Send Message
                      </>
                    )}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Meeting Request Modal */}
      {meetingModalOpen && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
          <Card className="w-full max-w-2xl mx-4">
            <CardHeader className="border-b">
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <Calendar className="w-5 h-5 text-blue-500" />
                  Request Meeting with FIDUS Team
                </CardTitle>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setMeetingModalOpen(false)}
                >
                  ✕
                </Button>
              </div>
            </CardHeader>
            <CardContent className="p-6">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Meeting Subject
                  </label>
                  <input
                    type="text"
                    value={composeData.subject}
                    onChange={(e) => setComposeData({...composeData, subject: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="What would you like to discuss?"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Meeting Details
                  </label>
                  <textarea
                    value={composeData.body}
                    onChange={(e) => setComposeData({...composeData, body: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md h-32 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
                    placeholder="Please provide details about the meeting purpose, preferred dates/times, and any specific topics you'd like to cover..."
                  />
                </div>
                
                <div className="flex justify-end gap-3 pt-4 border-t">
                  <Button
                    variant="outline"
                    onClick={() => setMeetingModalOpen(false)}
                  >
                    Cancel
                  </Button>
                  <Button
                    onClick={requestMeetingWithFIDUS}
                    disabled={loading || !composeData.subject || !composeData.body}
                    className="bg-blue-500 hover:bg-blue-600"
                  >
                    {loading ? (
                      <>
                        <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                        Sending Request...
                      </>
                    ) : (
                      <>
                        <Calendar className="w-4 h-4 mr-2" />
                        Send Meeting Request
                      </>
                    )}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Document Upload Modal */}
      {uploadModalOpen && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
          <Card className="w-full max-w-xl mx-4">
            <CardHeader className="border-b">
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <Upload className="w-5 h-5 text-green-500" />
                  Upload Document to FIDUS
                </CardTitle>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    setUploadModalOpen(false);
                    setSelectedFile(null);
                  }}
                >
                  ✕
                </Button>
              </div>
            </CardHeader>
            <CardContent className="p-6">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Select Document
                  </label>
                  <input
                    type="file"
                    onChange={(e) => setSelectedFile(e.target.files[0])}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-green-500 focus:border-green-500"
                    accept=".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.jpg,.jpeg,.png,.txt"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Accepted formats: PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX, JPG, PNG, TXT
                  </p>
                </div>
                
                {selectedFile && (
                  <div className="bg-gray-50 p-3 rounded-lg">
                    <p className="text-sm font-medium">Selected File:</p>
                    <p className="text-sm text-gray-600">{selectedFile.name}</p>
                    <p className="text-xs text-gray-500">
                      Size: {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                )}
                
                <div className="flex justify-end gap-3 pt-4 border-t">
                  <Button
                    variant="outline"
                    onClick={() => {
                      setUploadModalOpen(false);
                      setSelectedFile(null);
                    }}
                  >
                    Cancel
                  </Button>
                  <Button
                    onClick={() => uploadDocumentToFIDUS(selectedFile)}
                    disabled={loading || !selectedFile}
                    className="bg-green-500 hover:bg-green-600"
                  >
                    {loading ? (
                      <>
                        <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                        Uploading...
                      </>
                    ) : (
                      <>
                        <Upload className="w-4 h-4 mr-2" />
                        Upload Document
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

export default ClientGoogleWorkspace;