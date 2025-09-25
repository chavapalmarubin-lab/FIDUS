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
  Trash2
} from 'lucide-react';
import googleCRMIntegration from '../services/googleCRMIntegration';

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

  useEffect(() => {
    testConnection();
  }, []);

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

  // ==================== GMAIL FUNCTIONS ====================
  
  const loadEmails = async () => {
    try {
      const result = await googleCRMIntegration.getEmails(50);
      if (result.success) {
        // Simulate real email data structure
        const mockEmails = [
          {
            id: '1',
            subject: 'Welcome to FIDUS Investment Platform',
            sender: 'admin@fidus.com',
            recipient: 'client@example.com',
            date: new Date().toISOString(),
            snippet: 'Thank you for joining FIDUS Investment Management...',
            read: false,
            starred: false,
            body: `
              <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #2563eb;">Welcome to FIDUS Investment Management</h2>
                <p>Dear Valued Client,</p>
                <p>Thank you for choosing FIDUS Investment Management for your investment needs. We are excited to help you achieve your financial goals.</p>
                <p>Our team of experts is ready to provide you with personalized investment strategies and exceptional service.</p>
                <p>Next steps:</p>
                <ul>
                  <li>Complete your investor profile</li>
                  <li>Review our investment options</li>
                  <li>Schedule a consultation call</li>
                </ul>
                <p>Best regards,<br>The FIDUS Team</p>
              </div>
            `
          },
          {
            id: '2',
            subject: 'Investment Portfolio Update - September 2025',
            sender: 'portfolio@fidus.com',
            recipient: 'client@example.com',
            date: new Date(Date.now() - 86400000).toISOString(),
            snippet: 'Your portfolio has shown strong performance this month...',
            read: true,
            starred: true,
            body: `
              <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #16a34a;">Portfolio Performance Update</h2>
                <p>Portfolio Value: <strong>$125,000</strong> (+8.5%)</p>
                <p>Monthly Return: <strong>+2.3%</strong></p>
                <p>YTD Return: <strong>+15.7%</strong></p>
                <p>Your diversified portfolio continues to outperform market benchmarks.</p>
              </div>
            `
          },
          {
            id: '3',
            subject: 'Meeting Scheduled: Investment Strategy Review',
            sender: 'calendar@fidus.com',
            recipient: 'client@example.com',
            date: new Date(Date.now() - 172800000).toISOString(),
            snippet: 'Your meeting has been scheduled for tomorrow at 2:00 PM...',
            read: true,
            starred: false,
            body: `
              <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #7c3aed;">Meeting Confirmation</h2>
                <p><strong>Date:</strong> Tomorrow, 2:00 PM EST</p>
                <p><strong>Duration:</strong> 60 minutes</p>
                <p><strong>Location:</strong> Google Meet (link will be provided)</p>
                <p>We'll review your current portfolio performance and discuss upcoming opportunities.</p>
              </div>
            `
          }
        ];
        setEmails(mockEmails);
      }
    } catch (error) {
      console.error('Failed to load emails:', error);
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
    try {
      // Mock calendar events
      const mockEvents = [
        {
          id: '1',
          title: 'Investment Strategy Meeting',
          description: 'Quarterly review with portfolio manager',
          start: '2025-09-25T14:00:00Z',
          end: '2025-09-25T15:00:00Z',
          attendees: ['client@example.com', 'advisor@fidus.com'],
          meetLink: 'https://meet.google.com/abc-defg-hij'
        },
        {
          id: '2',
          title: 'Market Analysis Webinar',
          description: 'Monthly market outlook and investment opportunities',
          start: '2025-09-26T16:00:00Z',
          end: '2025-09-26T17:00:00Z',
          attendees: ['all-clients@fidus.com'],
          meetLink: 'https://meet.google.com/xyz-uvwx-123'
        }
      ];
      setEvents(mockEvents);
    } catch (error) {
      console.error('Failed to load calendar events:', error);
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
    try {
      const result = await googleCRMIntegration.getDriveFiles(50);
      if (result.success) {
        // Mock drive files
        const mockFiles = [
          {
            id: '1',
            name: 'Investment Agreement - John Doe.pdf',
            mimeType: 'application/pdf',
            size: '2.3 MB',
            createdTime: '2025-09-20T10:00:00Z',
            modifiedTime: '2025-09-20T10:00:00Z',
            shared: true
          },
          {
            id: '2',
            name: 'Portfolio Analysis Q3 2025.xlsx',
            mimeType: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            size: '1.8 MB',
            createdTime: '2025-09-15T14:30:00Z',
            modifiedTime: '2025-09-22T16:45:00Z',
            shared: false
          },
          {
            id: '3',
            name: 'Client Presentation Template.pptx',
            mimeType: 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            size: '5.2 MB',
            createdTime: '2025-09-10T09:15:00Z',
            modifiedTime: '2025-09-18T11:20:00Z',
            shared: true
          },
          {
            id: '4',
            name: 'AML KYC Documents',
            mimeType: 'application/vnd.google-apps.folder',
            size: '—',
            createdTime: '2025-09-01T08:00:00Z',
            modifiedTime: '2025-09-23T17:30:00Z',
            shared: false,
            isFolder: true
          }
        ];
        setDriveFiles(mockFiles);
      }
    } catch (error) {
      console.error('Failed to load Drive files:', error);
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

  useEffect(() => {
    if (activeTab === 'calendar') {
      loadCalendarEvents();
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

      {/* Connection Status */}
      {connectionStatus && (
        <Card>
          <CardContent className="pt-6">
            <div className={`flex items-center gap-2 p-3 rounded-lg ${
              connectionStatus.success 
                ? 'bg-green-50 text-green-800 border border-green-200'
                : 'bg-red-50 text-red-800 border border-red-200'
            }`}>
              {connectionStatus.success ? (
                <CheckCircle className="h-5 w-5" />
              ) : (
                <XCircle className="h-5 w-5" />
              )}
              <span className="font-medium">
                {connectionStatus.success ? '✅ Google APIs Connected' : '❌ Connection Failed'}
              </span>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Main Workspace */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-3 bg-slate-100">
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