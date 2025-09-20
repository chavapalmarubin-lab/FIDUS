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
  LogOut
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
  const [clients, setClients] = useState([]);
  const [prospects, setProspects] = useState([]);
  
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
      
      setClients(clientsResponse.data.clients || []);
      setProspects(prospectsResponse.data.prospects || []);
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
      const response = await apiAxios.get('/google/gmail/messages');
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
      const response = await apiAxios.get('/google/drive/files');
      setDriveFiles(response.data.files || []);
    } catch (err) {
      console.error('Failed to load drive files:', err);
    } finally {
      setDriveLoading(false);
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
                <Button variant="outline" className="w-full">
                  <Users className="h-4 w-4 mr-2" />
                  Email Clients ({clients.length})
                </Button>
                <Button variant="outline" className="w-full">
                  <Users className="h-4 w-4 mr-2" />
                  Email Prospects ({prospects.length})
                </Button>
                <Button variant="outline" className="w-full">
                  <FileText className="h-4 w-4 mr-2" />
                  Request Documents
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
                <Button variant="outline" className="w-full">
                  <Video className="h-4 w-4 mr-2" />
                  Create Google Meet
                </Button>
                <Button variant="outline" className="w-full">
                  <Users className="h-4 w-4 mr-2" />
                  Meeting with Client
                </Button>
                <Button variant="outline" className="w-full">
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
                <Button 
                  onClick={() => setShowUploadModal(true)} 
                  className="w-full bg-orange-600 hover:bg-orange-700"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Upload Document
                </Button>
                <Button variant="outline" className="w-full">
                  <FileText className="h-4 w-4 mr-2" />
                  Investment Agreements
                </Button>
                <Button variant="outline" className="w-full">
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
                <Button variant="outline" className="w-full">
                  <Download className="h-4 w-4 mr-2" />
                  Client Portfolio Report
                </Button>
                <Button variant="outline" className="w-full">
                  <Download className="h-4 w-4 mr-2" />
                  Investment Summary
                </Button>
                <Button variant="outline" className="w-full">
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