import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import {
  CheckCircle,
  XCircle,
  AlertCircle,
  RefreshCw,
  Clock,
  Wifi,
  WifiOff,
  Settings,
  HelpCircle,
  TrendingUp,
  Activity,
  Zap,
  Mail,
  Calendar,
  FolderOpen,
  Video,
  BarChart3,
  Info,
  ChevronRight,
  Shield,
  Globe
} from 'lucide-react';
import apiAxios from '../utils/apiAxios';

const GoogleConnectionMonitor = () => {
  const [connectionStatus, setConnectionStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState(30); // seconds
  const [connectionHistory, setConnectionHistory] = useState([]);
  const [selectedService, setSelectedService] = useState(null);
  const [troubleshootingOpen, setTroubleshootingOpen] = useState(false);

  // Service configurations with Google Material Design approach
  const serviceConfigs = {
    gmail: {
      name: 'Gmail',
      icon: Mail,
      color: 'text-red-500',
      bgColor: 'bg-red-50',
      borderColor: 'border-red-200',
      description: 'Email communication and client correspondence'
    },
    calendar: {
      name: 'Calendar', 
      icon: Calendar,
      color: 'text-blue-500',
      bgColor: 'bg-blue-50', 
      borderColor: 'border-blue-200',
      description: 'Meeting scheduling and event management'
    },
    drive: {
      name: 'Drive',
      icon: FolderOpen,
      color: 'text-green-500',
      bgColor: 'bg-green-50',
      borderColor: 'border-green-200', 
      description: 'Document storage and file sharing'
    },
    meet: {
      name: 'Meet',
      icon: Video,
      color: 'text-purple-500',
      bgColor: 'bg-purple-50',
      borderColor: 'border-purple-200',
      description: 'Video conferencing and client meetings'
    }
  };

  // Fetch connection status from new automated endpoints
  const testAllConnections = useCallback(async () => {
    setLoading(true);
    try {
      // Use new automated monitoring endpoint
      const response = await apiAxios.get('/admin/google/monitor');
      
      if (response.data.success) {
        setConnectionStatus(response.data);
        
        // Add to connection history for trending
        const timestamp = new Date().toISOString();
        setConnectionHistory(prev => [
          ...prev.slice(-9), // Keep last 9 entries + new one = 10 total
          {
            timestamp,
            overall_health: response.data.overall_health,
            connected_services: response.data.services.filter(s => s.connected).length,
            total_services: response.data.services.length
          }
        ]);
        
        console.log('✅ PRODUCTION: Automated Google connection status retrieved');
      } else {
        console.error('❌ Failed to get connection status:', response.data.error);
        setConnectionStatus({
          success: false,
          title: "Connection Status Error",
          subtitle: response.data.error || "Failed to retrieve status",
          services: [],
          auto_managed: false
        });
      }
    } catch (error) {
      console.error('❌ Connection status fetch error:', error);
      setConnectionStatus({
        success: false,
        title: "Connection Error", 
        subtitle: "Failed to connect to monitoring system",
        services: [],
        auto_managed: false
      });
    } finally {
      setLoading(false);
    }
  }, []);

  // Test individual service
  const testSingleService = async (service) => {
    try {
      setSelectedService(service);
      const response = await apiAxios.get(`/google/connection/test/${service}`);
      
      // Update the specific service status
      if (connectionStatus) {
        setConnectionStatus(prev => ({
          ...prev,
          services: {
            ...prev.services,
            [service]: {
              status: response.data.status,
              message: response.data.message,
              response_time_ms: response.data.response_time_ms,
              last_success: response.data.status === 'connected' ? new Date().toISOString() : prev.services[service]?.last_success,
              last_error: response.data.status === 'error' ? new Date().toISOString() : prev.services[service]?.last_error
            }
          }
        }));
      }
      
      return response.data;
    } catch (error) {
      console.error(`❌ ${service} test failed:`, error);
      return { success: false, error: error.message };
    } finally {
      setSelectedService(null);
    }
  };

  // Load connection history
  const loadConnectionHistory = async () => {
    try {
      const response = await apiAxios.get('/google/connection/history');
      if (response.data.success) {
        setConnectionHistory(response.data.history);
      }
    } catch (error) {
      console.error('Failed to load connection history:', error);
    }
  };

  // Auto-refresh functionality
  useEffect(() => {
    let intervalId;
    
    if (autoRefresh && refreshInterval > 0) {
      // Initial test
      testAllConnections();
      
      // Set up interval
      intervalId = setInterval(() => {
        testAllConnections();
      }, refreshInterval * 1000);
    }
    
    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [autoRefresh, refreshInterval, testAllConnections]);

  // Load history on mount
  useEffect(() => {
    loadConnectionHistory();
  }, []);

  // Get status icon and color
  const getStatusIcon = (status) => {
    switch (status) {
      case 'connected':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'error':
      case 'no_auth':
        return <XCircle className="h-5 w-5 text-red-500" />;
      case 'dependency_error':
        return <AlertCircle className="h-5 w-5 text-yellow-500" />;
      default:
        return <AlertCircle className="h-5 w-5 text-gray-400" />;
    }
  };

  // Get overall status color for FIDUS brand integration
  const getOverallStatusColor = () => {
    if (!connectionStatus) return 'border-gray-200';
    
    switch (connectionStatus.overall_status) {
      case 'fully_connected':
        return 'border-cyan-400 shadow-cyan-100'; // FIDUS cyan
      case 'partially_connected': 
        return 'border-orange-400 shadow-orange-100'; // FIDUS orange
      case 'disconnected':
      case 'test_failed':
        return 'border-red-400 shadow-red-100';
      default:
        return 'border-gray-200';
    }
  };

  // Calculate uptime percentage
  const calculateUptime = () => {
    if (!connectionHistory.length) return 0;
    
    const connectedTests = connectionHistory.filter(h => h.success_rate > 80).length;
    return Math.round((connectedTests / connectionHistory.length) * 100);
  };

  return (
    <div className="w-full space-y-6">
      {/* Header Card - Google Material Design Style */}
      <Card className={`${getOverallStatusColor()} transition-all duration-300`}>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-lg">
                <Globe className="h-6 w-6 text-white" />
              </div>
              <div>
                <CardTitle className="text-xl font-semibold text-gray-900">
                  Google Workspace Connection Monitor
                </CardTitle>
                <p className="text-sm text-gray-600 mt-1">
                  Real-time API health monitoring and diagnostics
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              {/* Auto-refresh toggle */}
              <Button
                variant={autoRefresh ? "default" : "outline"}
                size="sm"
                onClick={() => setAutoRefresh(!autoRefresh)}
                className="text-xs"
              >
                <Activity className="h-4 w-4 mr-1" />
                Auto {autoRefresh ? 'ON' : 'OFF'}
              </Button>
              
              {/* Manual refresh */}
              <Button
                onClick={testAllConnections}
                disabled={loading}
                size="sm"
                variant="outline"
              >
                <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                Test Now
              </Button>
              
              {/* Settings */}
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setTroubleshootingOpen(true)}
              >
                <Settings className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardHeader>
        
        <CardContent>
          {/* Overall Status Display */}
          {connectionStatus && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
              {/* Connection Status */}
              <div className="text-center">
                <div className="flex justify-center mb-2">
                  {connectionStatus.overall_status === 'fully_connected' ? (
                    <Wifi className="h-8 w-8 text-green-500" />
                  ) : (
                    <WifiOff className="h-8 w-8 text-red-500" />
                  )}
                </div>
                <h3 className="font-medium text-gray-900 capitalize">
                  {connectionStatus.overall_status?.replace('_', ' ') || 'Unknown'}
                </h3>
                <p className="text-sm text-gray-600">Overall Status</p>
              </div>
              
              {/* Success Rate */}
              <div className="text-center">
                <div className="text-2xl font-bold text-cyan-600">
                  {connectionStatus.connection_quality?.success_rate || 0}%
                </div>
                <Progress 
                  value={connectionStatus.connection_quality?.success_rate || 0}
                  className="h-2 mt-2 mb-1"
                />
                <p className="text-sm text-gray-600">Success Rate</p>
              </div>
              
              {/* Response Time */}
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-500">
                  {Math.round(connectionStatus.connection_quality?.average_response_time_ms || 0)}ms
                </div>
                <div className="flex justify-center mt-2 mb-1">
                  <Zap className="h-4 w-4 text-orange-500" />
                </div>
                <p className="text-sm text-gray-600">Avg Response</p>
              </div>
            </div>
          )}
          
          {/* Last Test Time */}
          {connectionStatus?.connection_quality?.last_test_time && (
            <div className="text-center text-sm text-gray-500 mb-4">
              <Clock className="h-4 w-4 inline mr-1" />
              Last tested: {new Date(connectionStatus.connection_quality.last_test_time).toLocaleString()}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Service Status Grid - Google Material Design Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {Object.entries(serviceConfigs).map(([serviceKey, config]) => {
          const service = connectionStatus?.services?.[serviceKey];
          const Icon = config.icon;
          const isLoading = selectedService === serviceKey;
          
          return (
            <Card 
              key={serviceKey}
              className={`hover:shadow-lg transition-all duration-200 cursor-pointer ${
                service?.status === 'connected' ? config.borderColor : 'border-gray-200'
              }`}
              onClick={() => testSingleService(serviceKey)}
            >
              <CardContent className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className={`p-3 rounded-lg ${config.bgColor}`}>
                    <Icon className={`h-6 w-6 ${config.color}`} />
                  </div>
                  <div className="flex flex-col items-end">
                    {getStatusIcon(service?.status)}
                    {isLoading && (
                      <RefreshCw className="h-4 w-4 text-gray-400 animate-spin mt-1" />
                    )}
                  </div>
                </div>
                
                <h3 className="font-semibold text-gray-900 mb-1">{config.name}</h3>
                <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                  {config.description}
                </p>
                
                {service && (
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-xs text-gray-500">Status</span>
                      <Badge variant={service.status === 'connected' ? 'default' : 'destructive'}>
                        {service.status}
                      </Badge>
                    </div>
                    
                    {service.response_time_ms && (
                      <div className="flex justify-between items-center">
                        <span className="text-xs text-gray-500">Response</span>
                        <span className="text-xs font-medium">
                          {Math.round(service.response_time_ms)}ms
                        </span>
                      </div>
                    )}
                    
                    {service.last_success && (
                      <div className="flex justify-between items-center">
                        <span className="text-xs text-gray-500">Last Success</span>
                        <span className="text-xs text-green-600">
                          {new Date(service.last_success).toLocaleTimeString()}
                        </span>
                      </div>
                    )}
                  </div>
                )}
                
                {!service && (
                  <div className="text-center text-sm text-gray-400">
                    Click to test connection
                  </div>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Connection Quality Trends */}
      {connectionHistory.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <BarChart3 className="h-5 w-5 mr-2" />
              Connection Quality Trends
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold text-cyan-600">{calculateUptime()}%</div>
                <p className="text-sm text-gray-600">Uptime (24h)</p>
              </div>
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">
                  {connectionHistory[connectionHistory.length - 1]?.successful_services || 0}/4
                </div>
                <p className="text-sm text-gray-600">Services Online</p>
              </div>
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">
                  {Math.round(connectionHistory.reduce((acc, h) => acc + h.average_response_time_ms, 0) / connectionHistory.length) || 0}ms
                </div>
                <p className="text-sm text-gray-600">Avg Response</p>
              </div>
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold text-orange-600">{connectionHistory.length}</div>
                <p className="text-sm text-gray-600">Tests (24h)</p>
              </div>
            </div>
            
            {/* Mini trend chart representation */}
            <div className="flex items-end space-x-1 h-20 bg-gray-50 p-4 rounded-lg">
              {connectionHistory.slice(-24).map((point, index) => (
                <div
                  key={index}
                  className="bg-gradient-to-t from-cyan-500 to-cyan-400 rounded-t flex-1 transition-all duration-300"
                  style={{ 
                    height: `${Math.max(4, (point.success_rate / 100) * 100)}%`,
                    minHeight: '4px'
                  }}
                  title={`${point.success_rate}% at ${new Date(point.timestamp).toLocaleTimeString()}`}
                />
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Troubleshooting & Settings Modal */}
      {troubleshootingOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="w-full max-w-2xl mx-4 max-h-[90vh] overflow-y-auto">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center">
                  <Shield className="h-5 w-5 mr-2" />
                  Connection Troubleshooting
                </CardTitle>
                <Button 
                  variant="ghost" 
                  size="sm"
                  onClick={() => setTroubleshootingOpen(false)}
                >
                  ×
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Auto-refresh Settings */}
              <div>
                <h4 className="font-medium mb-3 flex items-center">
                  <Settings className="h-4 w-4 mr-2" />
                  Monitor Settings
                </h4>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <label className="text-sm">Auto-refresh</label>
                    <Button
                      variant={autoRefresh ? "default" : "outline"}
                      size="sm"
                      onClick={() => setAutoRefresh(!autoRefresh)}
                    >
                      {autoRefresh ? 'Enabled' : 'Disabled'}
                    </Button>
                  </div>
                  
                  {autoRefresh && (
                    <div className="flex items-center justify-between">
                      <label className="text-sm">Refresh Interval</label>
                      <select 
                        value={refreshInterval}
                        onChange={(e) => setRefreshInterval(Number(e.target.value))}
                        className="border rounded px-3 py-1 text-sm"
                      >
                        <option value={15}>15 seconds</option>
                        <option value={30}>30 seconds</option>
                        <option value={60}>1 minute</option>
                        <option value={300}>5 minutes</option>
                      </select>
                    </div>
                  )}
                </div>
              </div>
              
              {/* Common Issues */}
              <div>
                <h4 className="font-medium mb-3 flex items-center">
                  <HelpCircle className="h-4 w-4 mr-2" />
                  Common Issues & Solutions
                </h4>
                <div className="space-y-3">
                  <div className="border-l-4 border-yellow-400 pl-4 py-2 bg-yellow-50 rounded-r">
                    <h5 className="font-medium text-sm">Authentication Required</h5>
                    <p className="text-sm text-gray-600 mt-1">
                      Click "Connect Google Workspace" to authenticate with your Google account
                    </p>
                  </div>
                  
                  <div className="border-l-4 border-red-400 pl-4 py-2 bg-red-50 rounded-r">
                    <h5 className="font-medium text-sm">API Access Denied</h5>
                    <p className="text-sm text-gray-600 mt-1">
                      Check Google Cloud Console API settings and ensure all required scopes are enabled
                    </p>
                  </div>
                  
                  <div className="border-l-4 border-blue-400 pl-4 py-2 bg-blue-50 rounded-r">
                    <h5 className="font-medium text-sm">Slow Response Times</h5>
                    <p className="text-sm text-gray-600 mt-1">
                      Check your internet connection and Google API quota limits
                    </p>
                  </div>
                </div>
              </div>
              
              {/* OAuth Status */}
              {connectionStatus?.troubleshooting && (
                <div>
                  <h4 className="font-medium mb-3 flex items-center">
                    <Info className="h-4 w-4 mr-2" />
                    OAuth Status
                  </h4>
                  <div className="bg-gray-50 p-4 rounded-lg space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span>Authentication:</span>
                      <Badge variant={connectionStatus.troubleshooting.oauth_status === 'authenticated' ? 'default' : 'destructive'}>
                        {connectionStatus.troubleshooting.oauth_status}
                      </Badge>
                    </div>
                    {connectionStatus.troubleshooting.token_expiry && (
                      <div className="flex justify-between">
                        <span>Token Expiry:</span>
                        <span className="text-gray-600">
                          {new Date(connectionStatus.troubleshooting.token_expiry).toLocaleDateString()}
                        </span>
                      </div>
                    )}
                    <div className="flex justify-between">
                      <span>User:</span>
                      <span className="text-gray-600">
                        {connectionStatus.connection_quality?.user_email || 'Unknown'}
                      </span>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};

export default GoogleConnectionMonitor;