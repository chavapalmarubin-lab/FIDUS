import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Tabs, TabsList, TabsTrigger, TabsContent } from './ui/tabs';
import { Badge } from './ui/badge';
import { Alert, AlertDescription } from './ui/alert';
import {
  Mail,
  Calendar,
  FolderOpen,
  FileSpreadsheet,
  Send,
  Plus,
  Download,
  Eye,
  Users,
  Clock,
  FileText,
  Paperclip,
  Search,
  Filter,
  RefreshCw,
  Video,
  Edit3,
  Share2,
  Signature,
  LogOut,
  X,
  AlertCircle
} from 'lucide-react';
import useGoogleAdmin from '../hooks/useGoogleAdmin';
import apiAxios from '../utils/apiAxios';

const GoogleWorkspaceIntegration = () => {
  const {
    profile,
    loading,
    error,
    isAuthenticated,
    loginWithGoogle,
    logout
  } = useGoogleAdmin();

  const [activeTab, setActiveTab] = useState('gmail');
  const [crmClients, setCrmClients] = useState([]);
  const [crmProspects, setCrmProspects] = useState([]);
  
  // Gmail State
  const [emails, setEmails] = useState([]);
  const [emailDrafts, setEmailDrafts] = useState([]);
  const [showComposeModal, setShowComposeModal] = useState(false);
  const [emailLoading, setEmailLoading] = useState(false);
  
  // Calendar State
  const [events, setEvents] = useState([]);
  const [showEventModal, setShowEventModal] = useState(false);
  const [calendarLoading, setCalendarLoading] = useState(false);
  
  // Drive State
  const [driveFiles, setDriveFiles] = useState([]);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [driveLoading, setDriveLoading] = useState(false);
  
  // Sheets State
  const [sheets, setSheets] = useState([]);
  const [showCreateSheetModal, setShowCreateSheetModal] = useState(false);
  const [sheetsLoading, setSheetsLoading] = useState(false);

  useEffect(() => {
    if (isAuthenticated) {
      fetchClientsAndProspects();
      loadGoogleWorkspaceData();
    }
  }, [isAuthenticated]);

  const fetchClientsAndProspects = async () => {
    try {
      const [clientsResponse, prospectsResponse] = await Promise.all([
        apiAxios.get('/admin/clients'),
        apiAxios.get('/crm/prospects')
      ]);
      
      setCrmClients(clientsResponse.data.clients || []);
      setCrmProspects(prospectsResponse.data.prospects || []);
    } catch (err) {
      console.error('Failed to fetch clients and prospects:', err);
    }
  };

  const loadGoogleWorkspaceData = async () => {
    if (activeTab === 'gmail') {
      await loadEmails();
    } else if (activeTab === 'calendar') {
      await loadCalendarEvents();
    } else if (activeTab === 'drive') {
      await loadDriveFiles();
    } else if (activeTab === 'sheets') {
      await loadSheets();
    }
  };

  const loadEmails = async () => {
    try {
      setEmailLoading(true);
      const response = await apiAxios.get('/google/gmail/real-messages');
      setEmails(response.data.messages || []);
    } catch (err) {
      console.error('Failed to load emails:', err);
    } finally {
      setEmailLoading(false);
    }
  };

  const loadCalendarEvents = async () => {
    try {
      setCalendarLoading(true);
      const response = await apiAxios.get('/google/calendar/events');
      setEvents(response.data.events || []);
    } catch (err) {
      console.error('Failed to load calendar events:', err);
    } finally {
      setCalendarLoading(false);
    }
  };

  const loadDriveFiles = async () => {
    try {
      setDriveLoading(true);
      const response = await apiAxios.get('/google/drive/real-files');
      setDriveFiles(response.data.files || []);
    } catch (err) {
      console.error('Failed to load drive files:', err);
    } finally {
      setDriveLoading(false);
    }
  };

  // ===== NEW CRM INTEGRATION FUNCTIONS =====
  
  // Load clients and prospects from CRM (using existing state)
  const [selectedRecipients, setSelectedRecipients] = useState([]);
  const [showRecipientModal, setShowRecipientModal] = useState(false);
  const [emailAction, setEmailAction] = useState(''); // 'clients', 'prospects', 'documents'
  const [documentRequestType, setDocumentRequestType] = useState('');
  
  // Email Clients Action
  const handleEmailClients = () => {
    setEmailAction('clients');
    setSelectedRecipients([]);
    setShowRecipientModal(true);
  };

  // Email Prospects Action
  const handleEmailProspects = () => {
    setEmailAction('prospects');
    setSelectedRecipients([]);
    setShowRecipientModal(true);
  };

  // Request Documents Action
  const handleRequestDocuments = (documentType = 'general') => {
    setEmailAction('documents');
    setDocumentRequestType(documentType);
    setSelectedRecipients([]);
    setShowRecipientModal(true);
  };

  // Send bulk email with Gmail API
  const sendBulkEmail = async (recipients, subject, body, htmlBody = null) => {
    const results = [];
    
    for (const recipient of recipients) {
      try {
        const response = await apiAxios.post('/google/gmail/send', {
          to: recipient.email,
          subject: subject.replace('{name}', recipient.name),
          body: body.replace('{name}', recipient.name),
          html_body: htmlBody ? htmlBody.replace('{name}', recipient.name) : null
        });
        
        if (response.data.success) {
          results.push({ ...recipient, status: 'sent' });
        } else {
          results.push({ ...recipient, status: 'failed', error: response.data.error });
        }
      } catch (error) {
        results.push({ ...recipient, status: 'failed', error: error.message });
      }
      
      // Add delay between emails to avoid rate limiting
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
    
    return results;
  };

  // Process bulk email sending
  const processBulkEmailSending = async () => {
    if (selectedRecipients.length === 0) {
      alert('Please select at least one recipient');
      return;
    }

    let subject, body, htmlBody;

    switch (emailAction) {
      case 'clients':
        subject = 'Important Update from FIDUS Investment Management';
        body = `Dear {name},

We hope this message finds you well. We wanted to reach out with an important update regarding your investment portfolio.

Our team has been working diligently to optimize your investment strategy and we have some exciting developments to share with you.

Please don't hesitate to reach out if you have any questions or would like to schedule a consultation.

Best regards,
FIDUS Investment Management Team`;
        
        htmlBody = `<html><body>
<h2>Important Update from FIDUS Investment Management</h2>
<p>Dear {name},</p>
<p>We hope this message finds you well. We wanted to reach out with an important update regarding your investment portfolio.</p>
<p>Our team has been working diligently to optimize your investment strategy and we have some exciting developments to share with you.</p>
<p>Please don't hesitate to reach out if you have any questions or would like to schedule a consultation.</p>
<p>Best regards,<br><strong>FIDUS Investment Management Team</strong></p>
</body></html>`;
        break;

      case 'prospects':
        subject = 'Investment Opportunity - FIDUS Investment Management';
        body = `Dear {name},

Thank you for your interest in FIDUS Investment Management. We specialize in creating customized investment solutions that align with your financial goals.

Our experienced team would love to discuss how we can help you achieve your investment objectives. We offer comprehensive portfolio management, risk assessment, and personalized investment strategies.

Would you be available for a brief consultation this week? We can arrange a call at your convenience.

Best regards,
FIDUS Investment Management Team`;
        
        htmlBody = `<html><body>
<h2>Investment Opportunity - FIDUS Investment Management</h2>
<p>Dear {name},</p>
<p>Thank you for your interest in FIDUS Investment Management. We specialize in creating customized investment solutions that align with your financial goals.</p>
<p>Our experienced team would love to discuss how we can help you achieve your investment objectives. We offer:</p>
<ul>
<li>Comprehensive portfolio management</li>
<li>Risk assessment and mitigation</li>
<li>Personalized investment strategies</li>
</ul>
<p>Would you be available for a brief consultation this week? We can arrange a call at your convenience.</p>
<p>Best regards,<br><strong>FIDUS Investment Management Team</strong></p>
</body></html>`;
        break;

      case 'documents':
        const docTypeLabel = documentRequestType === 'aml_kyc' ? 'AML/KYC Documentation' : 'Required Documents';
        subject = `Document Request - ${docTypeLabel}`;
        body = `Dear {name},

As part of our compliance and onboarding process, we need to collect some additional documentation from you.

Required documents for ${docTypeLabel.toLowerCase()}:
${documentRequestType === 'aml_kyc' ? `
- Government-issued photo ID (passport, driver's license, or national ID)
- Proof of residence (utility bill, bank statement, or lease agreement - max 3 months old)
- Bank statement (recent statement from your primary bank account)
- Source of funds documentation (salary slip, business registration, or investment statements)
` : `
- Please provide the requested documentation as discussed
`}

You can upload these documents securely through our client portal or respond to this email with the attachments.

If you have any questions about the required documentation, please don't hesitate to contact us.

Best regards,
FIDUS Investment Management Team`;
        
        htmlBody = `<html><body>
<h2>Document Request - ${docTypeLabel}</h2>
<p>Dear {name},</p>
<p>As part of our compliance and onboarding process, we need to collect some additional documentation from you.</p>
<h3>Required documents for ${docTypeLabel.toLowerCase()}:</h3>
${documentRequestType === 'aml_kyc' ? `
<ul>
<li>Government-issued photo ID (passport, driver's license, or national ID)</li>
<li>Proof of residence (utility bill, bank statement, or lease agreement - max 3 months old)</li>
<li>Bank statement (recent statement from your primary bank account)</li>
<li>Source of funds documentation (salary slip, business registration, or investment statements)</li>
</ul>
` : `
<p>Please provide the requested documentation as discussed.</p>
`}
<p>You can upload these documents securely through our client portal or respond to this email with the attachments.</p>
<p>If you have any questions about the required documentation, please don't hesitate to contact us.</p>
<p>Best regards,<br><strong>FIDUS Investment Management Team</strong></p>
</body></html>`;
        break;

      default:
        alert('Invalid email action');
        return;
    }

    try {
      const results = await sendBulkEmail(selectedRecipients, subject, body, htmlBody);
      
      const successCount = results.filter(r => r.status === 'sent').length;
      const failCount = results.filter(r => r.status === 'failed').length;
      
      if (successCount > 0) {
        alert(`Successfully sent ${successCount} email(s)${failCount > 0 ? `. ${failCount} failed.` : '!'}`);
      } else {
        alert(`Failed to send emails. Please check your Google authentication and try again.`);
      }
      
      setShowRecipientModal(false);
      setSelectedRecipients([]);
    } catch (error) {
      console.error('Bulk email error:', error);
      alert('Failed to send emails. Please try again.');
    }
  };

  const loadSheets = async () => {
    try {
      setSheetsLoading(true);
      const response = await apiAxios.get('/google/sheets/spreadsheets');
      setSheets(response.data.sheets || []);
    } catch (err) {
      console.error('Failed to load sheets:', err);
    } finally {
      setSheetsLoading(false);
    }
  };

  // Calendar Actions
  const createGoogleMeet = async () => {
    try {
      const meetConfig = {
        name: 'FIDUS Investment Meeting',
        description: 'Investment consultation meeting',
        start_time: new Date(Date.now() + 30 * 60 * 1000).toISOString(), // 30 minutes from now
        end_time: new Date(Date.now() + 90 * 60 * 1000).toISOString(), // 1.5 hours from now
        attendees: []
      };

      const response = await apiAxios.post('/google/meet/create-space', meetConfig);
      
      if (response.data.success) {
        alert(`Google Meet created successfully! Join link: ${response.data.meet_link}`);
        // Refresh calendar events to show the new meeting
        await loadCalendarEvents();
      } else {
        alert(`Failed to create Google Meet: ${response.data.error}`);
      }
    } catch (error) {
      console.error('Error creating Google Meet:', error);
      alert('Failed to create Google Meet. Please try again.');
    }
  };

  const createClientMeeting = async () => {
    try {
      const eventData = {
        summary: 'Client Meeting - FIDUS Investment',
        description: 'Scheduled client consultation meeting',
        start: {
          dateTime: new Date(Date.now() + 60 * 60 * 1000).toISOString(), // 1 hour from now
          timeZone: 'UTC'
        },
        end: {
          dateTime: new Date(Date.now() + 120 * 60 * 1000).toISOString(), // 2 hours from now
          timeZone: 'UTC'
        },
        conferenceData: {
          createRequest: {
            requestId: `client-meeting-${Date.now()}`,
            conferenceSolutionKey: { type: 'hangoutsMeet' }
          }
        }
      };

      const response = await apiAxios.post('/google/calendar/create-event', eventData);
      
      if (response.data.success) {
        alert('Client meeting scheduled successfully!');
        await loadCalendarEvents();
      } else {
        alert(`Failed to schedule meeting: ${response.data.error}`);
      }
    } catch (error) {
      console.error('Error creating client meeting:', error);
      alert('Failed to schedule meeting. Please try again.');
    }
  };

  const createProspectMeeting = async () => {
    try {
      const eventData = {
        summary: 'Prospect Meeting - FIDUS Investment',
        description: 'Initial consultation with investment prospect',
        start: {
          dateTime: new Date(Date.now() + 120 * 60 * 1000).toISOString(), // 2 hours from now
          timeZone: 'UTC'
        },
        end: {
          dateTime: new Date(Date.now() + 180 * 60 * 1000).toISOString(), // 3 hours from now
          timeZone: 'UTC'
        },
        conferenceData: {
          createRequest: {
            requestId: `prospect-meeting-${Date.now()}`,
            conferenceSolutionKey: { type: 'hangoutsMeet' }
          }
        }
      };

      const response = await apiAxios.post('/google/calendar/create-event', eventData);
      
      if (response.data.success) {
        alert('Prospect meeting scheduled successfully!');
        await loadCalendarEvents();
      } else {
        alert(`Failed to schedule meeting: ${response.data.error}`);
      }
    } catch (error) {
      console.error('Error creating prospect meeting:', error);
      alert('Failed to schedule meeting. Please try again.');
    }
  };

  // Drive Actions
  const handleDocumentUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/documents/upload`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('fidus_token')}`
        },
        body: formData
      });

      const result = await response.json();
      
      if (result.success) {
        alert('Document uploaded successfully!');
        await loadDriveFiles();
      } else {
        alert(`Upload failed: ${result.error}`);
      }
    } catch (error) {
      console.error('Error uploading document:', error);
      alert('Failed to upload document. Please try again.');
    }
  };

  const sendForSignature = async () => {
    const recipientEmail = prompt('Enter recipient email for signature:');
    const documentName = prompt('Enter document name:');
    
    if (!recipientEmail || !documentName) return;

    try {
      const response = await apiAxios.post('/documents/doc123/send-notification', {
        recipient_email: recipientEmail,
        recipient_name: 'Client',
        document_name: documentName,
        signing_url: 'https://fidus-workspace.preview.emergentagent.com/documents/sign'
      });

      if (response.data.success) {
        alert('Signature request sent successfully!');
      } else {
        alert(`Failed to send request: ${response.data.error}`);
      }
    } catch (error) {
      console.error('Error sending signature request:', error);
      alert('Failed to send signature request. Please try again.');
    }
  };

  // Sheets Actions
  const createPortfolioReport = async () => {
    // For now, we'll create a simple alert. In production, this would generate a Google Sheet
    alert('Portfolio report generation coming soon! This will create a comprehensive client portfolio report in Google Sheets.');
  };

  const createInvestmentSummary = async () => {
    alert('Investment summary generation coming soon! This will create an investment performance summary in Google Sheets.');
  };

  const createMT5Report = async () => {
    alert('MT5 trading report generation coming soon! This will pull MT5 data and create a trading performance report.');
  };

  if (!isAuthenticated) {
    return (
      <Card className="w-full max-w-4xl mx-auto">
        <CardHeader>
          <CardTitle>Google Workspace Integration</CardTitle>
        </CardHeader>
        <CardContent className="text-center py-12">
          <div className="space-y-4">
            <div className="text-slate-600">
              Please authenticate with Google to access Gmail, Calendar, Drive, and Sheets functionality.
            </div>
            <Button onClick={loginWithGoogle} disabled={loading} className="bg-blue-600 hover:bg-blue-700">
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
    );
  }

  return (
    <div className="w-full space-y-6">
      {/* Header with Profile */}
      <Card>
        <CardHeader className="pb-4">
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Google Workspace Integration</CardTitle>
              <p className="text-sm text-slate-600 mt-1">
                Connected as {profile?.email} • Full access to Gmail, Calendar, Drive, and Sheets
              </p>
            </div>
            <Button variant="outline" onClick={logout} size="sm">
              <LogOut className="h-4 w-4 mr-2" />
              Disconnect
            </Button>
          </div>
        </CardHeader>
      </Card>

      {/* Main Workspace Tabs */}
      <Tabs value={activeTab} onValueChange={(value) => {
        setActiveTab(value);
        setTimeout(() => loadGoogleWorkspaceData(), 100);
      }}>
        <TabsList className="grid w-full grid-cols-4 bg-slate-100">
          <TabsTrigger value="gmail" className="data-[state=active]:bg-blue-50 data-[state=active]:text-blue-900 data-[state=active]:border-blue-200">
            <Mail className="h-4 w-4 mr-2" />
            Gmail
          </TabsTrigger>
          <TabsTrigger value="calendar" className="data-[state=active]:bg-green-50 data-[state=active]:text-green-900 data-[state=active]:border-green-200">
            <Calendar className="h-4 w-4 mr-2" />
            Calendar
          </TabsTrigger>
          <TabsTrigger value="drive" className="data-[state=active]:bg-orange-50 data-[state=active]:text-orange-900 data-[state=active]:border-orange-200">
            <FolderOpen className="h-4 w-4 mr-2" />
            Drive
          </TabsTrigger>
          <TabsTrigger value="sheets" className="data-[state=active]:bg-emerald-50 data-[state=active]:text-emerald-900 data-[state=active]:border-emerald-200">
            <FileSpreadsheet className="h-4 w-4 mr-2" />
            Sheets
          </TabsTrigger>
        </TabsList>

        {/* Gmail Tab */}
        <TabsContent value="gmail" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Email Actions */}
            <Card className="lg:col-span-1">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Send className="h-5 w-5 mr-2" />
                  Email Actions
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button 
                  onClick={() => setShowComposeModal(true)} 
                  className="w-full bg-blue-600 hover:bg-blue-700"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Compose Email
                </Button>
                <Button 
                  variant="outline" 
                  className="w-full"
                  onClick={handleEmailClients}
                >
                  <Users className="h-4 w-4 mr-2" />
                  Email Clients ({crmClients.length})
                </Button>
                <Button 
                  variant="outline" 
                  className="w-full"
                  onClick={handleEmailProspects}
                >
                  <Users className="h-4 w-4 mr-2" />
                  Email Prospects ({crmProspects.length})
                </Button>
                <Button 
                  variant="outline" 
                  className="w-full"
                  onClick={() => handleRequestDocuments('aml_kyc')}
                >
                  <FileText className="h-4 w-4 mr-2" />
                  Request AML/KYC Documents
                </Button>
              </CardContent>
            </Card>

            {/* Recent Emails */}
            <Card className="lg:col-span-2">
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle>Recent Emails</CardTitle>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm" onClick={loadEmails}>
                    <RefreshCw className="h-4 w-4" />
                  </Button>
                  <Button variant="outline" size="sm">
                    <Search className="h-4 w-4" />
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                {emailLoading ? (
                  <div className="flex items-center justify-center py-8">
                    <RefreshCw className="h-6 w-6 animate-spin mr-2" />
                    Loading emails...
                  </div>
                ) : emails.length > 0 ? (
                  <div className="space-y-3">
                    {emails.slice(0, 10).map((email, index) => (
                      <div key={index} className="p-3 border rounded-lg hover:bg-slate-50">
                        <div className="flex items-center justify-between">
                          <div className="flex-1">
                            <div className="font-medium">{email.subject || 'No Subject'}</div>
                            <div className="text-sm text-slate-600">{email.sender || 'Unknown Sender'}</div>
                          </div>
                          <Badge variant="outline">{email.unread ? 'Unread' : 'Read'}</Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-slate-600">
                    <Mail className="h-12 w-12 mx-auto mb-4 text-slate-400" />
                    No emails found. Click refresh to load emails.
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Calendar Tab */}
        <TabsContent value="calendar" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Calendar Actions */}
            <Card className="lg:col-span-1">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Calendar className="h-5 w-5 mr-2" />
                  Calendar Actions
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button 
                  onClick={() => setShowEventModal(true)} 
                  className="w-full bg-green-600 hover:bg-green-700"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Schedule Meeting
                </Button>
                <Button 
                  variant="outline" 
                  className="w-full"
                  onClick={createGoogleMeet}
                >
                  <Video className="h-4 w-4 mr-2" />
                  Create Google Meet
                </Button>
                <Button 
                  variant="outline" 
                  className="w-full"
                  onClick={createClientMeeting}
                >
                  <Users className="h-4 w-4 mr-2" />
                  Meeting with Client
                </Button>
                <Button 
                  variant="outline" 
                  className="w-full"
                  onClick={createProspectMeeting}
                >
                  <Users className="h-4 w-4 mr-2" />
                  Meeting with Prospect
                </Button>
              </CardContent>
            </Card>

            {/* Upcoming Events */}
            <Card className="lg:col-span-2">
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle>Upcoming Events</CardTitle>
                <Button variant="outline" size="sm" onClick={loadCalendarEvents}>
                  <RefreshCw className="h-4 w-4" />
                </Button>
              </CardHeader>
              <CardContent>
                {calendarLoading ? (
                  <div className="flex items-center justify-center py-8">
                    <RefreshCw className="h-6 w-6 animate-spin mr-2" />
                    Loading events...
                  </div>
                ) : events.length > 0 ? (
                  <div className="space-y-3">
                    {events.slice(0, 10).map((event, index) => (
                      <div key={index} className="p-3 border rounded-lg hover:bg-slate-50">
                        <div className="flex items-center justify-between">
                          <div className="flex-1">
                            <div className="font-medium">{event.summary || 'No Title'}</div>
                            <div className="text-sm text-slate-600 flex items-center">
                              <Clock className="h-4 w-4 mr-1" />
                              {event.start || 'No Date'}
                            </div>
                          </div>
                          {event.meetLink && (
                            <Button size="sm" variant="outline">
                              <Video className="h-4 w-4 mr-1" />
                              Join
                            </Button>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-slate-600">
                    <Calendar className="h-12 w-12 mx-auto mb-4 text-slate-400" />
                    No events scheduled. Create your first meeting.
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Drive Tab */}
        <TabsContent value="drive" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Drive Actions */}
            <Card className="lg:col-span-1">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <FolderOpen className="h-5 w-5 mr-2" />
                  Drive Actions
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <input
                    type="file"
                    id="document-upload"
                    style={{ display: 'none' }}
                    accept=".pdf,.doc,.docx"
                    onChange={handleDocumentUpload}
                  />
                  <Button 
                    onClick={() => document.getElementById('document-upload').click()} 
                    className="w-full bg-orange-600 hover:bg-orange-700"
                  >
                    <Plus className="h-4 w-4 mr-2" />
                    Upload Document
                  </Button>
                </div>
                <Button variant="outline" className="w-full">
                  <FileText className="h-4 w-4 mr-2" />
                  Investment Agreements
                </Button>
                <Button 
                  variant="outline" 
                  className="w-full"
                  onClick={sendForSignature}
                >
                  <Signature className="h-4 w-4 mr-2" />
                  Send for Signature
                </Button>
                <Button variant="outline" className="w-full">
                  <Share2 className="h-4 w-4 mr-2" />
                  Share with Client
                </Button>
              </CardContent>
            </Card>

            {/* Drive Files */}
            <Card className="lg:col-span-2">
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle>Recent Documents</CardTitle>
                <Button variant="outline" size="sm" onClick={loadDriveFiles}>
                  <RefreshCw className="h-4 w-4" />
                </Button>
              </CardHeader>
              <CardContent>
                {driveLoading ? (
                  <div className="flex items-center justify-center py-8">
                    <RefreshCw className="h-6 w-6 animate-spin mr-2" />
                    Loading files...
                  </div>
                ) : driveFiles.length > 0 ? (
                  <div className="space-y-3">
                    {driveFiles.slice(0, 10).map((file, index) => (
                      <div key={index} className="p-3 border rounded-lg hover:bg-slate-50">
                        <div className="flex items-center justify-between">
                          <div className="flex-1">
                            <div className="font-medium">{file.name}</div>
                            <div className="text-sm text-slate-600">{file.type} • {file.size}</div>
                          </div>
                          <div className="flex gap-2">
                            <Button size="sm" variant="outline">
                              <Eye className="h-4 w-4" />
                            </Button>
                            <Button size="sm" variant="outline">
                              <Share2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-slate-600">
                    <FolderOpen className="h-12 w-12 mx-auto mb-4 text-slate-400" />
                    No documents found. Upload your first document.
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Sheets Tab */}
        <TabsContent value="sheets" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Sheets Actions */}
            <Card className="lg:col-span-1">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <FileSpreadsheet className="h-5 w-5 mr-2" />
                  Sheets Actions
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button 
                  onClick={() => setShowCreateSheetModal(true)} 
                  className="w-full bg-emerald-600 hover:bg-emerald-700"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Create Report
                </Button>
                <Button 
                  variant="outline" 
                  className="w-full"
                  onClick={createPortfolioReport}
                >
                  <Download className="h-4 w-4 mr-2" />
                  Client Portfolio Report
                </Button>
                <Button 
                  variant="outline" 
                  className="w-full"
                  onClick={createInvestmentSummary}
                >
                  <Download className="h-4 w-4 mr-2" />
                  Investment Summary
                </Button>
                <Button 
                  variant="outline" 
                  className="w-full"
                  onClick={createMT5Report}
                >
                  <Download className="h-4 w-4 mr-2" />
                  MT5 Trading Report
                </Button>
              </CardContent>
            </Card>

            {/* Recent Sheets */}
            <Card className="lg:col-span-2">
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle>Recent Reports</CardTitle>
                <Button variant="outline" size="sm" onClick={loadSheets}>
                  <RefreshCw className="h-4 w-4" />
                </Button>
              </CardHeader>
              <CardContent>
                {sheetsLoading ? (
                  <div className="flex items-center justify-center py-8">
                    <RefreshCw className="h-6 w-6 animate-spin mr-2" />
                    Loading sheets...
                  </div>
                ) : sheets.length > 0 ? (
                  <div className="space-y-3">
                    {sheets.slice(0, 10).map((sheet, index) => (
                      <div key={index} className="p-3 border rounded-lg hover:bg-slate-50">
                        <div className="flex items-center justify-between">
                          <div className="flex-1">
                            <div className="font-medium">{sheet.name}</div>
                            <div className="text-sm text-slate-600">
                              Last modified: {sheet.modifiedTime || 'Unknown'}
                            </div>
                          </div>
                          <div className="flex gap-2">
                            <Button size="sm" variant="outline">
                              <Edit3 className="h-4 w-4" />
                            </Button>
                            <Button size="sm" variant="outline">
                              <Download className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-slate-600">
                    <FileSpreadsheet className="h-12 w-12 mx-auto mb-4 text-slate-400" />
                    No reports found. Create your first report.
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>

      {/* Compose Email Modal */}
      {showComposeModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-lg w-full max-w-2xl mx-4 max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">Compose Email</h3>
                <button
                  onClick={() => setShowComposeModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="h-6 w-6" />
                </button>
              </div>
              
              <form onSubmit={async (e) => {
                e.preventDefault();
                const formData = new FormData(e.target);
                try {
                  const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/google/gmail/send`, {
                    method: 'POST',
                    headers: {
                      'Content-Type': 'application/json',
                      'Authorization': `Bearer ${localStorage.getItem('fidus_token')}`
                    },
                    credentials: 'include',
                    body: JSON.stringify({
                      to: formData.get('to'),
                      subject: formData.get('subject'),
                      body: formData.get('body')
                    })
                  });
                  
                  if (response.ok) {
                    alert('Email sent successfully!');
                    setShowComposeModal(false);
                    loadEmails(); // Refresh email list
                  } else {
                    alert('Failed to send email');
                  }
                } catch (error) {
                  console.error('Send email error:', error);
                  alert('Error sending email');
                }
              }} className="space-y-4">
                
                <div>
                  <label htmlFor="to" className="block text-sm font-medium text-gray-700 mb-1">
                    To
                  </label>
                  <input
                    type="email"
                    name="to"
                    id="to"
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="recipient@example.com"
                  />
                </div>
                
                <div>
                  <label htmlFor="subject" className="block text-sm font-medium text-gray-700 mb-1">
                    Subject
                  </label>
                  <input
                    type="text"
                    name="subject"
                    id="subject"
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Email subject"
                  />
                </div>
                
                <div>
                  <label htmlFor="body" className="block text-sm font-medium text-gray-700 mb-1">
                    Message
                  </label>
                  <textarea
                    name="body"
                    id="body"
                    rows={6}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 resize-vertical"
                    placeholder="Type your message here..."
                  />
                </div>
                
                <div className="flex justify-end space-x-3">
                  <button
                    type="button"
                    onClick={() => setShowComposeModal(false)}
                    className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                  >
                    Send Email
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Recipient Selection Modal */}
      {showRecipientModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-lg w-full max-w-2xl mx-4 max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">
                  Select Recipients - {
                    emailAction === 'clients' ? 'Email Clients' :
                    emailAction === 'prospects' ? 'Email Prospects' :
                    emailAction === 'documents' ? 'Request Documents' : 'Select Recipients'
                  }
                </h3>
                <button
                  onClick={() => setShowRecipientModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="h-6 w-6" />
                </button>
              </div>
              
              <div className="space-y-4">
                {/* Document Type Selection for Document Requests */}
                {emailAction === 'documents' && (
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Document Request Type
                    </label>
                    <select
                      value={documentRequestType}
                      onChange={(e) => setDocumentRequestType(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="general">General Documents</option>
                      <option value="aml_kyc">AML/KYC Documentation</option>
                    </select>
                  </div>
                )}

                {/* Recipient List */}
                <div className="max-h-60 overflow-y-auto border rounded-lg">
                  {(emailAction === 'clients' ? clients : 
                    emailAction === 'prospects' ? prospects : 
                    [...clients, ...prospects]).map((recipient, index) => (
                    <div key={index} className="p-3 border-b last:border-b-0 hover:bg-gray-50">
                      <label className="flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          checked={selectedRecipients.some(r => r.email === recipient.email)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setSelectedRecipients([...selectedRecipients, recipient]);
                            } else {
                              setSelectedRecipients(selectedRecipients.filter(r => r.email !== recipient.email));
                            }
                          }}
                          className="mr-3"
                        />
                        <div className="flex-1">
                          <div className="font-medium">{recipient.name}</div>
                          <div className="text-sm text-gray-600">{recipient.email}</div>
                        </div>
                      </label>
                    </div>
                  ))}
                </div>

                {/* Selected Count */}
                <div className="text-sm text-gray-600">
                  Selected: {selectedRecipients.length} recipient(s)
                </div>

                {/* Action Buttons */}
                <div className="flex justify-end space-x-3">
                  <button
                    type="button"
                    onClick={() => setShowRecipientModal(false)}
                    className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                  <button
                    type="button"
                    onClick={processBulkEmailSending}
                    disabled={selectedRecipients.length === 0}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
                  >
                    {emailAction === 'documents' ? 'Send Document Requests' : 'Send Emails'} ({selectedRecipients.length})
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {error && (
        <Alert className="bg-red-50 border-red-200">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription className="text-red-800">{error}</AlertDescription>
        </Alert>
      )}
    </div>
  );
};

export default GoogleWorkspaceIntegration;