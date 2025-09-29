import React, { useState, useEffect } from 'react';
import apiAxios from '../utils/apiAxios';

const IndividualGoogleWorkspace = () => {
  const [activeTab, setActiveTab] = useState('connection');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Google Connection State
  const [googleStatus, setGoogleStatus] = useState(null);
  const [connectingToGoogle, setConnectingToGoogle] = useState(false);

  useEffect(() => {
    checkGoogleConnectionStatus();
    loadCRMData();
    
    // Check for URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const oauthError = urlParams.get('oauth_error');
    const tabParam = urlParams.get('tab');
    
    // Handle OAuth error from URL
    if (oauthError) {
      setError(`OAuth Error: ${decodeURIComponent(oauthError)}`);
      
      // Clean URL
      const baseUrl = window.location.origin + window.location.pathname;
      const newUrl = `${baseUrl}?skip_animation=true`;
      window.history.replaceState({}, '', newUrl);
    }
    
    // Handle tab parameter
    if (tabParam === 'google-workspace') {
      setActiveTab('connection');
    }
  }, []);

  const checkGoogleConnectionStatus = async () => {
    try {
      setLoading(true);
      const response = await apiAxios.get('/admin/google/individual-status');
      
      if (response.data.success) {
        setGoogleStatus(response.data);
        console.log('✅ Google connection status:', response.data);
        
        // If connected and not expired, load Google data
        if (response.data.connected && !response.data.is_expired) {
          loadGoogleWorkspaceData();
        }
      }
    } catch (err) {
      console.error('❌ Failed to check Google status:', err);
      setError('Failed to check Google connection status');
    } finally {
      setLoading(false);
    }
  };

  const connectGoogleAccount = async () => {
    try {
      setConnectingToGoogle(true);
      setError(null);
      
      console.log('🚀 Initiating individual Google OAuth...');
      
      // Get individual Google OAuth URL
      const response = await apiAxios.get('/admin/google/individual-auth-url');
      
      if (response.data.success && response.data.auth_url) {
        console.log('✅ Redirecting to individual Google OAuth...');
        // Redirect to Google OAuth
        window.location.href = response.data.auth_url;
      } else {
        throw new Error(response.data.error || 'Failed to get OAuth URL');
      }
    } catch (err) {
      console.error('❌ Google connection failed:', err);
      setError(err.response?.data?.detail || err.message || 'Failed to connect Google account');
    } finally {
      setConnectingToGoogle(false);
    }
  };

  const disconnectGoogleAccount = async () => {
    try {
      setLoading(true);
      const response = await apiAxios.post('/admin/google/individual-disconnect');
      
      if (response.data.success) {
        setGoogleStatus(null);
        setEmails([]);
        setEvents([]);
        setDriveFiles([]);
        setSheets([]);
        
        console.log('✅ Google account disconnected');
        alert('Google account disconnected successfully!');
      } else {
        throw new Error(response.data.message || 'Failed to disconnect');
      }
    } catch (err) {
      console.error('❌ Failed to disconnect:', err);
      setError('Failed to disconnect Google account');
    } finally {
      setLoading(false);
    }
  };

  const loadAllAdminConnections = async () => {
    try {
      setLoading(true);
      const response = await apiAxios.get('/admin/google/all-connections');
      
      if (response.data.success) {
        setAllAdminConnections(response.data.connections);
        setShowAllConnections(true);
        console.log('✅ Loaded all admin connections:', response.data.connections);
      }
    } catch (err) {
      console.error('❌ Failed to load admin connections:', err);
      setError('Failed to load admin connections');
    } finally {
      setLoading(false);
    }
  };

  const loadCRMData = async () => {
    try {
      const [clientsResponse, prospectsResponse] = await Promise.all([
        apiAxios.get('/admin/clients'),
        apiAxios.get('/crm/prospects')
      ]);
      
      setCrmClients(clientsResponse.data.clients || []);
      setCrmProspects(prospectsResponse.data.prospects || []);
    } catch (err) {
      console.error('Failed to load CRM data:', err);
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
      setLoading(true);
      const response = await apiAxios.get('/google/gmail/real-messages');
      setEmails(response.data.messages || []);
    } catch (err) {
      console.error('Failed to load emails:', err);
      setError('Failed to load emails');
    } finally {
      setLoading(false);
    }
  };

  const loadCalendarEvents = async () => {
    try {
      setLoading(true);
      const response = await apiAxios.get('/google/calendar/events');
      setEvents(response.data.events || []);
    } catch (err) {
      console.error('Failed to load calendar events:', err);
      setError('Failed to load calendar events');
    } finally {
      setLoading(false);
    }
  };

  const loadDriveFiles = async () => {
    try {
      setLoading(true);
      const response = await apiAxios.get('/google/drive/real-files');
      setDriveFiles(response.data.files || []);
    } catch (err) {
      console.error('Failed to load drive files:', err);
      setError('Failed to load drive files');
    } finally {
      setLoading(false);
    }
  };

  const loadSheets = async () => {
    try {
      setLoading(true);
      const response = await apiAxios.get('/google/sheets/list');
      setSheets(response.data.sheets || []);
    } catch (err) {
      console.error('Failed to load sheets:', err);
      setError('Failed to load sheets');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (googleStatus?.connected && !googleStatus?.is_expired) {
      loadGoogleWorkspaceData();
    }
  }, [activeTab, googleStatus]);

  // Connection Status Component
  const ConnectionStatus = () => {
    if (!googleStatus) {
      return (
        <Card className="border-l-4 border-l-gray-400">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <XCircle className="w-8 h-8 text-gray-400" />
                <div>
                  <h3 className="font-semibold text-gray-900">No Google Account Connected</h3>
                  <p className="text-sm text-gray-600">Connect your personal Google account to access Gmail, Calendar, Drive, and Sheets</p>
                </div>
              </div>
              <Button
                onClick={connectGoogleAccount}
                disabled={connectingToGoogle}
                className="bg-blue-600 hover:bg-blue-700"
              >
                {connectingToGoogle ? (
                  <>
                    <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                    Connecting...
                  </>
                ) : (
                  <>
                    <Mail className="w-4 h-4 mr-2" />
                    Connect My Google Account
                  </>
                )}
              </Button>
            </div>
          </CardContent>
        </Card>
      );
    }

    if (!googleStatus.connected) {
      return (
        <Card className="border-l-4 border-l-red-400">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <XCircle className="w-8 h-8 text-red-500" />
                <div>
                  <h3 className="font-semibold text-gray-900">Google Account Not Connected</h3>
                  <p className="text-sm text-gray-600">Please connect your Google account to continue</p>
                </div>
              </div>
              <Button
                onClick={connectGoogleAccount}
                disabled={connectingToGoogle}
                className="bg-blue-600 hover:bg-blue-700"
              >
                {connectingToGoogle ? (
                  <>
                    <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                    Connecting...
                  </>
                ) : (
                  <>
                    <Mail className="w-4 h-4 mr-2" />
                    Connect Google Account
                  </>
                )}
              </Button>
            </div>
          </CardContent>
        </Card>
      );
    }

    return (
      <Card className="border-l-4 border-l-green-400">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <CheckCircle className="w-8 h-8 text-green-500" />
              <div>
                <h3 className="font-semibold text-gray-900">Google Account Connected</h3>
                <p className="text-sm text-gray-600">
                  Connected as <strong>{googleStatus.google_info?.name}</strong> ({googleStatus.google_info?.email})
                </p>
                <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                  <span>Connected: {new Date(googleStatus.google_info?.connected_at).toLocaleDateString()}</span>
                  {googleStatus.is_expired && (
                    <Badge className="bg-yellow-100 text-yellow-800">Token Expired</Badge>
                  )}
                </div>
              </div>
            </div>
            <div className="flex gap-2">
              {googleStatus.is_expired && (
                <Button
                  onClick={connectGoogleAccount}
                  size="sm"
                  className="bg-yellow-600 hover:bg-yellow-700"
                >
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Reconnect
                </Button>
              )}
              <Button
                onClick={disconnectGoogleAccount}
                variant="outline"
                size="sm"
              >
                <LogOut className="w-4 h-4 mr-2" />
                Disconnect
              </Button>
            </div>
          </div>
          
          {/* Google Services Status */}
          <div className="mt-4 grid grid-cols-4 gap-3">
            {[
              { name: 'Gmail', icon: Mail, connected: googleStatus.scopes?.includes('https://www.googleapis.com/auth/gmail.readonly') },
              { name: 'Calendar', icon: Calendar, connected: googleStatus.scopes?.includes('https://www.googleapis.com/auth/calendar') },
              { name: 'Drive', icon: FolderOpen, connected: googleStatus.scopes?.includes('https://www.googleapis.com/auth/drive') },
              { name: 'Sheets', icon: FileSpreadsheet, connected: googleStatus.scopes?.includes('https://www.googleapis.com/auth/spreadsheets') }
            ].map((service) => (
              <div key={service.name} className={`p-2 rounded-lg text-center text-xs ${
                service.connected ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
              }`}>
                <service.icon className="w-4 h-4 mx-auto mb-1" />
                <div className="font-medium">{service.name}</div>
                <div>{service.connected ? 'Connected' : 'Not Connected'}</div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  };

  // All Admin Connections Component
  const AllAdminConnections = () => (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Shield className="w-5 h-5" />
            All Admin Google Connections
          </CardTitle>
          <Button
            onClick={loadAllAdminConnections}
            variant="outline"
            size="sm"
            disabled={loading}
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {allAdminConnections.length > 0 ? (
          <div className="space-y-3">
            {allAdminConnections.map((connection, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <User className="w-5 h-5 text-gray-500" />
                  <div>
                    <div className="font-medium">{connection.admin_name}</div>
                    <div className="text-sm text-gray-600">{connection.admin_email}</div>
                    <div className="text-xs text-gray-500">
                      Google: {connection.google_email}
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <Badge className={`text-xs ${
                    connection.connection_status === 'active' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {connection.connection_status}
                  </Badge>
                  <div className="text-xs text-gray-500 mt-1">
                    Last used: {connection.last_used ? new Date(connection.last_used).toLocaleDateString() : 'Never'}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <Users className="w-12 h-12 mx-auto mb-2 text-gray-300" />
            <p>No admin connections found</p>
          </div>
        )}
      </CardContent>
    </Card>
  );

  return (
    <div className="w-full space-y-6">
      {/* Header */}
      <Card>
        <CardHeader>
          <CardTitle>Individual Google Workspace Integration</CardTitle>
          <p className="text-sm text-gray-600">
            Each admin connects their personal Google account for Gmail, Calendar, Drive, and Sheets access
          </p>
        </CardHeader>
      </Card>

      {/* Error Display */}
      {error && (
        <Alert className="border-red-200 bg-red-50">
          <AlertCircle className="h-4 w-4 text-red-600" />
          <AlertDescription className="text-red-800">
            {error}
            <Button
              variant="link"
              size="sm"
              onClick={() => setError(null)}
              className="ml-2 p-0 h-auto text-red-600"
            >
              Dismiss
            </Button>
          </AlertDescription>
        </Alert>
      )}

      {/* Main Content */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="connection">Connection</TabsTrigger>
          <TabsTrigger value="gmail" disabled={!googleStatus?.connected || googleStatus?.is_expired}>
            Gmail
            {emails.length > 0 && (
              <Badge className="ml-2 text-xs bg-red-100 text-red-800">
                {emails.length}
              </Badge>
            )}
          </TabsTrigger>
          <TabsTrigger value="calendar" disabled={!googleStatus?.connected || googleStatus?.is_expired}>
            Calendar
            {events.length > 0 && (
              <Badge className="ml-2 text-xs bg-blue-100 text-blue-800">
                {events.length}
              </Badge>
            )}
          </TabsTrigger>
          <TabsTrigger value="drive" disabled={!googleStatus?.connected || googleStatus?.is_expired}>
            Drive
            {driveFiles.length > 0 && (
              <Badge className="ml-2 text-xs bg-green-100 text-green-800">
                {driveFiles.length}
              </Badge>
            )}
          </TabsTrigger>
          <TabsTrigger value="sheets" disabled={!googleStatus?.connected || googleStatus?.is_expired}>
            Sheets
          </TabsTrigger>
          <TabsTrigger value="admin">All Admins</TabsTrigger>
        </TabsList>

        {/* Connection Tab */}
        <TabsContent value="connection" className="space-y-4">
          <ConnectionStatus />
          
          {googleStatus?.connected && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Google Account Details</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium text-gray-500">Admin User</label>
                    <p className="font-medium">{googleStatus.admin_info?.admin_username}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">Google Account</label>
                    <p className="font-medium">{googleStatus.google_info?.email}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">Connected Date</label>
                    <p className="text-sm text-gray-600">
                      {new Date(googleStatus.google_info?.connected_at).toLocaleString()}
                    </p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">Token Expires</label>
                    <p className="text-sm text-gray-600">
                      {googleStatus.token_expires_at ? 
                        new Date(googleStatus.token_expires_at).toLocaleString() : 'Unknown'}
                    </p>
                  </div>
                </div>
                
                <div>
                  <label className="text-sm font-medium text-gray-500 mb-2 block">Granted Permissions</label>
                  <div className="flex flex-wrap gap-2">
                    {googleStatus.scopes?.map((scope, index) => (
                      <Badge key={index} variant="outline" className="text-xs">
                        {scope.replace('https://www.googleapis.com/auth/', '')}
                      </Badge>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Gmail Tab */}
        <TabsContent value="gmail" className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">Gmail Messages</h3>
            <Button
              onClick={loadEmails}
              variant="outline"
              size="sm"
              disabled={loading}
            >
              <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
          
          {emails.length > 0 ? (
            <div className="space-y-2">
              {emails.map((email, index) => (
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
                          <span className="font-medium">From:</span> {email.sender || email.from}
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
                <p className="text-gray-500">No emails found</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Calendar Tab */}
        <TabsContent value="calendar" className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">Calendar Events</h3>
            <Button
              onClick={loadCalendarEvents}
              variant="outline"
              size="sm"
              disabled={loading}
            >
              <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
          
          {events.length > 0 ? (
            <div className="space-y-2">
              {events.map((event, index) => (
                <Card key={index} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <Calendar className="w-4 h-4 text-blue-500" />
                          <span className="font-medium">{event.summary}</span>
                        </div>
                        <p className="text-sm text-gray-600 mb-2">
                          {new Date(event.start?.dateTime || event.start).toLocaleString()} - 
                          {new Date(event.end?.dateTime || event.end).toLocaleString()}
                        </p>
                        {event.description && (
                          <p className="text-sm text-gray-700">{event.description}</p>
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
                <p className="text-gray-500">No calendar events found</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Drive Tab */}
        <TabsContent value="drive" className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">Drive Files</h3>
            <Button
              onClick={loadDriveFiles}
              variant="outline"
              size="sm"
              disabled={loading}
            >
              <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
          
          {driveFiles.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {driveFiles.map((file, index) => (
                <Card key={index} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-4">
                    <div className="flex items-start gap-3">
                      <FileText className="w-8 h-8 text-blue-500 mt-1" />
                      <div className="flex-1">
                        <h4 className="font-medium text-sm mb-1">{file.name}</h4>
                        <p className="text-xs text-gray-600 mb-2">
                          Modified: {new Date(file.modifiedTime).toLocaleDateString()}
                        </p>
                        <div className="flex gap-1">
                          <Button variant="outline" size="sm">
                            <Eye className="w-3 h-3 mr-1" />
                            View
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
                <p className="text-gray-500">No drive files found</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Sheets Tab */}
        <TabsContent value="sheets" className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">Google Sheets</h3>
            <Button
              onClick={loadSheets}
              variant="outline"
              size="sm"
              disabled={loading}
            >
              <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
          
          <Card>
            <CardContent className="p-8 text-center">
              <FileSpreadsheet className="w-12 h-12 mx-auto mb-4 text-gray-300" />
              <p className="text-gray-500">Google Sheets integration coming soon</p>
            </CardContent>
          </Card>
        </TabsContent>

        {/* All Admins Tab */}
        <TabsContent value="admin" className="space-y-4">
          <AllAdminConnections />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default IndividualGoogleWorkspace;