import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Tabs, TabsList, TabsTrigger, TabsContent } from './ui/tabs';
import { Badge } from './ui/badge';
import { Alert, AlertDescription } from './ui/alert';
import {
  User,
  Mail,
  Calendar,
  FolderOpen,
  Phone,
  MapPin,
  Building,
  CreditCard,
  FileText,
  Send,
  Video,
  Upload,
  Download,
  Clock,
  CheckCircle,
  XCircle,
  Star,
  Archive,
  Reply,
  Forward,
  Edit,
  Trash2,
  Plus,
  RefreshCw,
  Activity,
  Globe,
  Shield,
  DollarSign,
  TrendingUp,
  Eye,
  ExternalLink,
  Filter,
  Search,
  MoreVertical,
  Paperclip
} from 'lucide-react';
import apiAxios from '../utils/apiAxios';

const ClientDetailModal = ({ client, isOpen, onClose }) => {
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(false);
  
  // Google Integration Data
  const [clientEmails, setClientEmails] = useState([]);
  const [clientMeetings, setClientMeetings] = useState([]);
  const [clientDocuments, setClientDocuments] = useState([]);
  const [googleLoading, setGoogleLoading] = useState(false);
  
  // Client interaction data
  const [interactionHistory, setInteractionHistory] = useState([]);
  const [portfolioData, setPortfolioData] = useState(null);
  const [kycStatus, setKycStatus] = useState(null);
  
  // Compose states
  const [composeOpen, setComposeOpen] = useState(false);
  const [composeData, setComposeData] = useState({ subject: '', body: '' });
  const [meetingData, setMeetingData] = useState({
    title: '',
    date: '',
    time: '',
    duration: 60,
    agenda: ''
  });
  const [meetingModalOpen, setMeetingModalOpen] = useState(false);

  useEffect(() => {
    if (isOpen && client) {
      loadClientData();
      loadGoogleIntegratedData();
    }
  }, [isOpen, client]);

  const loadClientData = async () => {
    setLoading(true);
    try {
      // Load client portfolio data
      const portfolioResponse = await apiAxios.get(`/clients/${client.id}/portfolio`);
      if (portfolioResponse.data.success) {
        setPortfolioData(portfolioResponse.data.portfolio);
      }

      // Load KYC status
      const kycResponse = await apiAxios.get(`/clients/${client.id}/kyc-status`);
      if (kycResponse.data.success) {
        setKycStatus(kycResponse.data.kyc_status);
      }

      // Load interaction history
      const historyResponse = await apiAxios.get(`/clients/${client.id}/interactions`);
      if (historyResponse.data.success) {
        setInteractionHistory(historyResponse.data.interactions);
      }

    } catch (error) {
      console.error('Failed to load client data:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadGoogleIntegratedData = async () => {
    setGoogleLoading(true);
    try {
      console.log('🔍 Loading Google integrated data for client:', client.email);

      // Load client-specific emails from Gmail
      const emailResponse = await apiAxios.get(`/google/gmail/client-emails/${client.email}`);
      if (emailResponse.data.success) {
        setClientEmails(emailResponse.data.emails);
        console.log(`📧 Loaded ${emailResponse.data.emails.length} emails for ${client.name}`);
      }

      // Load client meetings from Google Calendar
      const meetingsResponse = await apiAxios.get(`/google/calendar/client-meetings/${client.email}`);
      if (meetingsResponse.data.success) {
        setClientMeetings(meetingsResponse.data.meetings);
        console.log(`📅 Loaded ${meetingsResponse.data.meetings.length} meetings for ${client.name}`);
      }

      // Load client documents from Google Drive (PRIVACY SECURE: client-specific folder only)
      const documentsResponse = await apiAxios.get(`/fidus/client-drive-folder/${client.id}`);
      if (documentsResponse.data.success) {
        setClientDocuments(documentsResponse.data.documents);
        console.log(`📁 PRIVACY SECURE: Loaded ${documentsResponse.data.documents.length} documents from ${client.name}'s folder ONLY`);
      }

    } catch (error) {
      console.error('❌ Failed to load Google integrated data:', error);
      // Set empty arrays on error
      setClientEmails([]);
      setClientMeetings([]);
      setClientDocuments([]);
    } finally {
      setGoogleLoading(false);
    }
  };

  const sendClientEmail = async () => {
    if (!composeData.subject || !composeData.body) {
      alert('Please fill in subject and message');
      return;
    }

    setLoading(true);
    try {
      const response = await apiAxios.post('/google/gmail/real-send', {
        to: client.email,
        subject: composeData.subject,
        body: composeData.body,
        client_id: client.id,
        html: true
      });

      if (response.data.success) {
        alert('✅ Email sent successfully!');
        setComposeOpen(false);
        setComposeData({ subject: '', body: '' });
        
        // Refresh emails
        setTimeout(() => {
          loadGoogleIntegratedData();
        }, 1000);
      } else {
        throw new Error(response.data.error || 'Failed to send email');
      }
    } catch (error) {
      console.error('❌ Email sending failed:', error);
      alert(`Failed to send email: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const scheduleClientMeeting = async () => {
    if (!meetingData.title || !meetingData.date || !meetingData.time) {
      alert('Please fill in meeting title, date, and time');
      return;
    }

    setLoading(true);
    try {
      const startDateTime = new Date(`${meetingData.date}T${meetingData.time}`);
      const endDateTime = new Date(startDateTime.getTime() + (meetingData.duration * 60000));

      const response = await apiAxios.post('/google/calendar/create-event', {
        title: meetingData.title,
        description: meetingData.agenda || `Meeting with ${client.name}`,
        start_time: startDateTime.toISOString(),
        end_time: endDateTime.toISOString(),
        attendees: [client.email],
        client_id: client.id
      });

      if (response.data.success) {
        alert(`✅ Meeting scheduled successfully! Google Meet link: ${response.data.meet_link || 'Will be provided'}`);
        setMeetingModalOpen(false);
        setMeetingData({ title: '', date: '', time: '', duration: 60, agenda: '' });
        
        // Refresh meetings
        setTimeout(() => {
          loadGoogleIntegratedData();
        }, 1000);
      } else {
        throw new Error(response.data.error || 'Failed to create meeting');
      }
    } catch (error) {
      console.error('❌ Meeting creation failed:', error);
      alert(`Failed to schedule meeting: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const createClientDriveFolder = async () => {
    setLoading(true);
    try {
      const response = await apiAxios.post('/google/drive/create-client-folder', {
        client_id: client.id,
        client_name: client.name,
        folder_name: `${client.name} - FIDUS Documents`
      });

      if (response.data.success) {
        alert('✅ Client folder created in Google Drive!');
        // Refresh documents
        setTimeout(() => {
          loadGoogleIntegratedData();
        }, 1000);
      } else {
        throw new Error(response.data.error || 'Failed to create folder');
      }
    } catch (error) {
      console.error('❌ Folder creation failed:', error);
      alert(`Failed to create Drive folder: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleDocumentUpload = async (event) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    setGoogleLoading(true);
    try {
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const formData = new FormData();
        formData.append('file', file);
        formData.append('client_id', client.id);
        formData.append('client_name', client.name);
        formData.append('folder_name', `${client.name} - FIDUS Documents`);

        // Upload to client's specific Google Drive folder
        const response = await apiAxios.post('/google/drive/upload-to-client-folder', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });

        if (!response.data.success) {
          throw new Error(response.data.error || `Failed to upload ${file.name}`);
        }
      }

      alert(`✅ Successfully uploaded ${files.length} document(s) to ${client.name}'s Drive folder!`);
      
      // Refresh documents list
      setTimeout(() => {
        loadGoogleIntegratedData();
      }, 1000);
      
      // Clear the file input
      event.target.value = '';
      
    } catch (error) {
      console.error('❌ Document upload failed:', error);
      alert(`Failed to upload documents: ${error.message}`);
    } finally {
      setGoogleLoading(false);
    }
  };

  if (!isOpen || !client) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg w-full max-w-7xl max-h-[95vh] overflow-hidden flex flex-col">
        
        {/* Header */}
        <div className="border-b p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                <span className="text-xl font-bold text-white">
                  {client.name?.charAt(0)?.toUpperCase() || 'C'}
                </span>
              </div>
              <div>
                <h2 className="text-2xl font-bold text-gray-900">{client.name}</h2>
                <p className="text-gray-600">{client.email}</p>
                <div className="flex items-center gap-4 mt-1 text-sm text-gray-500">
                  <span className="flex items-center gap-1">
                    <Phone className="w-4 h-4" />
                    {client.phone}
                  </span>
                  {client.stage && (
                    <Badge className="bg-blue-100 text-blue-800 text-xs">
                      {client.stage.charAt(0).toUpperCase() + client.stage.slice(1)}
                    </Badge>
                  )}
                </div>
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              <Button
                onClick={() => setComposeOpen(true)}
                className="bg-red-500 hover:bg-red-600 text-white"
              >
                <Mail className="w-4 h-4 mr-2" />
                Send Email
              </Button>
              
              <Button
                onClick={() => setMeetingModalOpen(true)}
                className="bg-blue-500 hover:bg-blue-600 text-white"
              >
                <Video className="w-4 h-4 mr-2" />
                Schedule Meeting
              </Button>
              
              <Button
                onClick={onClose}
                variant="outline"
                className="px-4"
              >
                ✕
              </Button>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-hidden">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="h-full flex flex-col">
            <TabsList className="w-full justify-start px-6 bg-gray-50">
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="emails" className="relative">
                Emails
                {clientEmails.length > 0 && (
                  <Badge className="ml-2 text-xs bg-red-100 text-red-800">
                    {clientEmails.length}
                  </Badge>
                )}
              </TabsTrigger>
              <TabsTrigger value="meetings" className="relative">
                Meetings
                {clientMeetings.length > 0 && (
                  <Badge className="ml-2 text-xs bg-blue-100 text-blue-800">
                    {clientMeetings.length}
                  </Badge>
                )}
              </TabsTrigger>
              <TabsTrigger value="documents" className="relative">
                Documents
                {clientDocuments.length > 0 && (
                  <Badge className="ml-2 text-xs bg-green-100 text-green-800">
                    {clientDocuments.length}
                  </Badge>
                )}
              </TabsTrigger>
              <TabsTrigger value="portfolio">Portfolio</TabsTrigger>
              <TabsTrigger value="kyc">KYC/AML</TabsTrigger>
            </TabsList>

            <div className="flex-1 overflow-auto">
              
              {/* Overview Tab */}
              <TabsContent value="overview" className="p-6 space-y-6">
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  
                  {/* Client Information */}
                  <Card className="lg:col-span-2">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <User className="w-5 h-5" />
                        Client Information
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <label className="text-sm font-medium text-gray-500">Full Name</label>
                          <p className="text-gray-900 font-medium">{client.name}</p>
                        </div>
                        <div>
                          <label className="text-sm font-medium text-gray-500">Email Address</label>
                          <p className="text-gray-900">{client.email}</p>
                        </div>
                        <div>
                          <label className="text-sm font-medium text-gray-500">Phone Number</label>
                          <p className="text-gray-900">{client.phone}</p>
                        </div>
                        <div>
                          <label className="text-sm font-medium text-gray-500">Client Since</label>
                          <p className="text-gray-900">
                            {client.created_at ? new Date(client.created_at).toLocaleDateString() : 'N/A'}
                          </p>
                        </div>
                        {client.notes && (
                          <div className="md:col-span-2">
                            <label className="text-sm font-medium text-gray-500">Notes</label>
                            <p className="text-gray-900">{client.notes}</p>
                          </div>
                        )}
                      </div>
                    </CardContent>
                  </Card>

                  {/* Quick Stats */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Activity className="w-5 h-5" />
                        Quick Stats
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">Total Emails</span>
                        <Badge variant="outline">{clientEmails.length}</Badge>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">Meetings</span>
                        <Badge variant="outline">{clientMeetings.length}</Badge>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">Documents</span>
                        <Badge variant="outline">{clientDocuments.length}</Badge>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">Last Contact</span>
                        <span className="text-xs text-gray-500">
                          {client.last_contact ? new Date(client.last_contact).toLocaleDateString() : 'None'}
                        </span>
                      </div>
                    </CardContent>
                  </Card>
                </div>

                {/* Recent Activity */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Clock className="w-5 h-5" />
                      Recent Activity
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    {interactionHistory.length > 0 ? (
                      <div className="space-y-3">
                        {interactionHistory.slice(0, 5).map((interaction, index) => (
                          <div key={index} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                            <div className="flex-1">
                              <p className="text-sm font-medium">{interaction.type}</p>
                              <p className="text-xs text-gray-600">{interaction.description}</p>
                            </div>
                            <span className="text-xs text-gray-500">
                              {new Date(interaction.date).toLocaleDateString()}
                            </span>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-gray-500 text-sm">No recent activity</p>
                    )}
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Emails Tab */}
              <TabsContent value="emails" className="p-6">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-semibold">Email Communications</h3>
                    <div className="flex gap-2">
                      <Button
                        onClick={loadGoogleIntegratedData}
                        variant="outline"
                        size="sm"
                        disabled={googleLoading}
                      >
                        <RefreshCw className={`w-4 h-4 ${googleLoading ? 'animate-spin' : ''}`} />
                      </Button>
                      <Button
                        onClick={() => setComposeOpen(true)}
                        size="sm"
                        className="bg-red-500 hover:bg-red-600"
                      >
                        <Plus className="w-4 h-4 mr-2" />
                        New Email
                      </Button>
                    </div>
                  </div>

                  {googleLoading ? (
                    <div className="flex items-center justify-center py-8">
                      <RefreshCw className="w-6 h-6 animate-spin text-blue-500" />
                      <span className="ml-2">Loading emails...</span>
                    </div>
                  ) : clientEmails.length > 0 ? (
                    <div className="space-y-2">
                      {clientEmails.map((email, index) => (
                        <Card key={index} className="hover:shadow-md transition-shadow">
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
                              <div className="flex gap-1 ml-4">
                                <Button variant="ghost" size="sm">
                                  <Reply className="w-4 h-4" />
                                </Button>
                                <Button variant="ghost" size="sm">
                                  <Forward className="w-4 h-4" />
                                </Button>
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
                        <p className="text-gray-500 mb-4">No email communications found with this client</p>
                        <Button
                          onClick={() => setComposeOpen(true)}
                          className="bg-red-500 hover:bg-red-600"
                        >
                          <Plus className="w-4 h-4 mr-2" />
                          Send First Email
                        </Button>
                      </CardContent>
                    </Card>
                  )}
                </div>
              </TabsContent>

              {/* Meetings Tab */}
              <TabsContent value="meetings" className="p-6">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-semibold">Meeting History</h3>
                    <div className="flex gap-2">
                      <Button
                        onClick={loadGoogleIntegratedData}
                        variant="outline"
                        size="sm"
                        disabled={googleLoading}
                      >
                        <RefreshCw className={`w-4 h-4 ${googleLoading ? 'animate-spin' : ''}`} />
                      </Button>
                      <Button
                        onClick={() => setMeetingModalOpen(true)}
                        size="sm"
                        className="bg-blue-500 hover:bg-blue-600"
                      >
                        <Plus className="w-4 h-4 mr-2" />
                        Schedule Meeting
                      </Button>
                    </div>
                  </div>

                  {googleLoading ? (
                    <div className="flex items-center justify-center py-8">
                      <RefreshCw className="w-6 h-6 animate-spin text-blue-500" />
                      <span className="ml-2">Loading meetings...</span>
                    </div>
                  ) : clientMeetings.length > 0 ? (
                    <div className="space-y-2">
                      {clientMeetings.map((meeting, index) => (
                        <Card key={index} className="hover:shadow-md transition-shadow">
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
                                  {new Date(meeting.start_time).toLocaleString()} - 
                                  {new Date(meeting.end_time).toLocaleString()}
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
                        <p className="text-gray-500 mb-4">No meetings scheduled with this client</p>
                        <Button
                          onClick={() => setMeetingModalOpen(true)}
                          className="bg-blue-500 hover:bg-blue-600"
                        >
                          <Plus className="w-4 h-4 mr-2" />
                          Schedule First Meeting
                        </Button>
                      </CardContent>
                    </Card>
                  )}
                </div>
              </TabsContent>

              {/* Documents Tab */}
              <TabsContent value="documents" className="p-6">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-semibold">Client Documents</h3>
                    <div className="flex gap-2">
                      <Button
                        onClick={loadGoogleIntegratedData}
                        variant="outline"
                        size="sm"
                        disabled={googleLoading}
                      >
                        <RefreshCw className={`w-4 h-4 ${googleLoading ? 'animate-spin' : ''}`} />
                      </Button>
                      <Button
                        onClick={() => document.getElementById('document-upload').click()}
                        size="sm"
                        className="bg-blue-500 hover:bg-blue-600"
                        disabled={googleLoading}
                      >
                        <Upload className="w-4 h-4 mr-2" />
                        Upload Document
                      </Button>
                    </div>
                  </div>
                  
                  {/* Hidden file input */}
                  <input
                    id="document-upload"
                    type="file"
                    multiple
                    style={{ display: 'none' }}
                    onChange={handleDocumentUpload}
                    accept=".pdf,.doc,.docx,.jpg,.jpeg,.png,.txt"
                  />

                  {googleLoading ? (
                    <div className="flex items-center justify-center py-8">
                      <RefreshCw className="w-6 h-6 animate-spin text-green-500" />
                      <span className="ml-2">Loading documents...</span>
                    </div>
                  ) : clientDocuments.length > 0 ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {clientDocuments.map((doc, index) => (
                        <Card key={index} className="hover:shadow-md transition-shadow">
                          <CardContent className="p-4">
                            <div className="flex items-start gap-3">
                              <FileText className="w-8 h-8 text-green-500 mt-1" />
                              <div className="flex-1">
                                <h4 className="font-medium text-sm mb-1">{doc.name}</h4>
                                <p className="text-xs text-gray-600 mb-2">
                                  Modified: {new Date(doc.modified_time).toLocaleDateString()}
                                </p>
                                <div className="flex gap-1">
                                  <Button variant="outline" size="sm">
                                    <Eye className="w-3 h-3 mr-1" />
                                    View
                                  </Button>
                                  <Button variant="outline" size="sm">
                                    <Download className="w-3 h-3" />
                                  </Button>
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
                        <p className="text-gray-500 mb-4">Google Drive folder will be created automatically when you upload documents</p>
                        <Button
                          onClick={() => document.getElementById('document-upload').click()}
                          className="bg-blue-500 hover:bg-blue-600"
                        >
                          <Upload className="w-4 h-4 mr-2" />
                          Upload First Document
                        </Button>
                      </CardContent>
                    </Card>
                  )}
                </div>
              </TabsContent>

              {/* Portfolio Tab */}
              <TabsContent value="portfolio" className="p-6">
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold">Investment Portfolio</h3>
                  {portfolioData ? (
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <Card>
                        <CardContent className="p-4 text-center">
                          <DollarSign className="w-8 h-8 mx-auto mb-2 text-green-500" />
                          <h4 className="font-medium">Total Value</h4>
                          <p className="text-2xl font-bold text-green-600">
                            ${portfolioData.total_value?.toLocaleString() || '0'}
                          </p>
                        </CardContent>
                      </Card>
                      <Card>
                        <CardContent className="p-4 text-center">
                          <TrendingUp className="w-8 h-8 mx-auto mb-2 text-blue-500" />
                          <h4 className="font-medium">Return</h4>
                          <p className="text-2xl font-bold text-blue-600">
                            {portfolioData.return_percentage || '0'}%
                          </p>
                        </CardContent>
                      </Card>
                      <Card>
                        <CardContent className="p-4 text-center">
                          <Activity className="w-8 h-8 mx-auto mb-2 text-purple-500" />
                          <h4 className="font-medium">Risk Level</h4>
                          <p className="text-lg font-semibold text-purple-600">
                            {portfolioData.risk_level || 'Moderate'}
                          </p>
                        </CardContent>
                      </Card>
                    </div>
                  ) : (
                    <Card>
                      <CardContent className="p-8 text-center">
                        <DollarSign className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                        <p className="text-gray-500">No portfolio data available</p>
                      </CardContent>
                    </Card>
                  )}
                </div>
              </TabsContent>

              {/* KYC/AML Tab */}
              <TabsContent value="kyc" className="p-6">
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold">KYC/AML Status</h3>
                  {kycStatus ? (
                    <Card>
                      <CardContent className="p-4">
                        <div className="flex items-center gap-3">
                          <Shield className={`w-6 h-6 ${
                            kycStatus.status === 'approved' ? 'text-green-500' : 
                            kycStatus.status === 'pending' ? 'text-yellow-500' : 
                            'text-red-500'
                          }`} />
                          <div>
                            <h4 className="font-medium">Status: {kycStatus.status}</h4>
                            <p className="text-sm text-gray-600">{kycStatus.description}</p>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ) : (
                    <Card>
                      <CardContent className="p-8 text-center">
                        <Shield className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                        <p className="text-gray-500">KYC/AML process not started</p>
                      </CardContent>
                    </Card>
                  )}
                </div>
              </TabsContent>
            </div>
          </Tabs>
        </div>
      </div>

      {/* Compose Email Modal */}
      {composeOpen && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-[60]">
          <Card className="w-full max-w-2xl mx-4">
            <CardHeader className="border-b">
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <Mail className="w-5 h-5 text-red-500" />
                  Compose Email to {client.name}
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
                  <input
                    type="email"
                    value={client.email}
                    disabled
                    className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-600"
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
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-red-500 focus:border-red-500"
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
                    className="w-full px-3 py-2 border border-gray-300 rounded-md h-40 focus:ring-2 focus:ring-red-500 focus:border-red-500 resize-none"
                    placeholder="Write your message here..."
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
                    onClick={sendClientEmail}
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

      {/* Schedule Meeting Modal */}
      {meetingModalOpen && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-[60]">
          <Card className="w-full max-w-2xl mx-4">
            <CardHeader className="border-b">
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <Video className="w-5 h-5 text-blue-500" />
                  Schedule Meeting with {client.name}
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
                    Meeting Title
                  </label>
                  <input
                    type="text"
                    value={meetingData.title}
                    onChange={(e) => setMeetingData({...meetingData, title: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Meeting title"
                  />
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Date
                    </label>
                    <input
                      type="date"
                      value={meetingData.date}
                      onChange={(e) => setMeetingData({...meetingData, date: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      min={new Date().toISOString().split('T')[0]}
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Time
                    </label>
                    <input
                      type="time"
                      value={meetingData.time}
                      onChange={(e) => setMeetingData({...meetingData, time: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Duration (minutes)
                  </label>
                  <select
                    value={meetingData.duration}
                    onChange={(e) => setMeetingData({...meetingData, duration: parseInt(e.target.value)})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value={30}>30 minutes</option>
                    <option value={45}>45 minutes</option>
                    <option value={60}>1 hour</option>
                    <option value={90}>1.5 hours</option>
                    <option value={120}>2 hours</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Agenda (Optional)
                  </label>
                  <textarea
                    value={meetingData.agenda}
                    onChange={(e) => setMeetingData({...meetingData, agenda: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md h-24 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
                    placeholder="Meeting agenda or notes..."
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
                    onClick={scheduleClientMeeting}
                    disabled={loading || !meetingData.title || !meetingData.date || !meetingData.time}
                    className="bg-blue-500 hover:bg-blue-600"
                  >
                    {loading ? (
                      <>
                        <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                        Scheduling...
                      </>
                    ) : (
                      <>
                        <Video className="w-4 h-4 mr-2" />
                        Schedule Meeting
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

export default ClientDetailModal;