import React, { useState, useEffect, useRef } from 'react';
import HealthMetricCard from './HealthMetricCard';
import { RefreshCw, Activity, AlertCircle, CheckCircle, Clock, Pause, Play } from 'lucide-react';

const SystemHealthDashboard = () => {
  const [healthData, setHealthData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [countdown, setCountdown] = useState(30);
  const intervalRef = useRef(null);
  const countdownRef = useRef(null);

  const backendUrl = process.env.REACT_APP_BACKEND_URL || '';

  // Fetch health data
  const fetchHealthData = async (showLoading = true) => {
    try {
      if (showLoading) {
        setRefreshing(true);
      }
      
      const response = await fetch(`${backendUrl}/api/system/health/all`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch health data');
      }

      const data = await response.json();
      setHealthData(data);
      setLastUpdated(new Date());
      setError(null);
      setCountdown(30); // Reset countdown
    } catch (err) {
      console.error('Error fetching health data:', err);
      setError(err.message);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  // Initial load
  useEffect(() => {
    fetchHealthData();
  }, []);

  // Auto-refresh setup
  useEffect(() => {
    if (autoRefresh) {
      // Refresh data every 30 seconds
      intervalRef.current = setInterval(() => {
        fetchHealthData(false);
      }, 30000);

      // Countdown timer (updates every second)
      countdownRef.current = setInterval(() => {
        setCountdown((prev) => {
          if (prev <= 1) {
            return 30;
          }
          return prev - 1;
        });
      }, 1000);
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      if (countdownRef.current) {
        clearInterval(countdownRef.current);
        countdownRef.current = null;
      }
    }

    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
      if (countdownRef.current) clearInterval(countdownRef.current);
    };
  }, [autoRefresh]);

  // Manual refresh
  const handleManualRefresh = () => {
    fetchHealthData();
  };

  // Toggle auto-refresh
  const toggleAutoRefresh = () => {
    setAutoRefresh(!autoRefresh);
    if (!autoRefresh) {
      setCountdown(30);
    }
  };

  // Get overall status style
  const getOverallStatusStyle = () => {
    if (!healthData) return { bg: 'bg-gray-100', text: 'text-gray-800', icon: 'text-gray-600' };

    switch (healthData.overall_status) {
      case 'healthy':
        return { bg: 'bg-green-100', text: 'text-green-800', icon: 'text-green-600', border: 'border-green-300' };
      case 'degraded':
        return { bg: 'bg-yellow-100', text: 'text-yellow-800', icon: 'text-yellow-600', border: 'border-yellow-300' };
      case 'critical':
        return { bg: 'bg-red-100', text: 'text-red-800', icon: 'text-red-600', border: 'border-red-300' };
      default:
        return { bg: 'bg-gray-100', text: 'text-gray-800', icon: 'text-gray-600', border: 'border-gray-300' };
    }
  };

  const overallStyle = getOverallStatusStyle();

  // Format last updated time
  const formatLastUpdated = () => {
    if (!lastUpdated) return 'Never';
    
    const now = new Date();
    const seconds = Math.floor((now - lastUpdated) / 1000);
    
    if (seconds < 10) return 'Just now';
    if (seconds < 60) return `${seconds} seconds ago`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)} minutes ago`;
    return lastUpdated.toLocaleTimeString();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 font-medium">Loading system health data...</p>
        </div>
      </div>
    );
  }

  if (error && !healthData) {
    return (
      <div className="bg-red-50 border-2 border-red-200 rounded-lg p-6">
        <div className="flex items-center space-x-3 text-red-800 mb-3">
          <AlertCircle className="w-6 h-6" />
          <h3 className="font-semibold text-lg">Error Loading Health Data</h3>
        </div>
        <p className="text-red-700 mb-4">{error}</p>
        <button
          onClick={handleManualRefresh}
          className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className={`rounded-lg border-2 ${overallStyle.border} ${overallStyle.bg} p-6`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className={`p-3 rounded-full bg-white shadow-sm`}>
              {healthData?.overall_status === 'healthy' ? (
                <CheckCircle className={`w-8 h-8 ${overallStyle.icon}`} />
              ) : healthData?.overall_status === 'critical' ? (
                <AlertCircle className={`w-8 h-8 ${overallStyle.icon}`} />
              ) : (
                <Activity className={`w-8 h-8 ${overallStyle.icon}`} />
              )}
            </div>
            <div>
              <h2 className={`text-2xl font-bold ${overallStyle.text}`}>
                System Status: {healthData?.overall_status?.toUpperCase() || 'UNKNOWN'}
              </h2>
              <p className={`text-sm ${overallStyle.text} mt-1`}>
                {healthData?.overall_message || 'Checking system health...'}
              </p>
              <div className="flex items-center space-x-4 mt-2">
                <div className="flex items-center space-x-2">
                  <Clock className={`w-4 h-4 ${overallStyle.text}`} />
                  <span className={`text-sm ${overallStyle.text}`}>
                    Last updated: {formatLastUpdated()}
                  </span>
                </div>
                {healthData?.health_percentage !== undefined && (
                  <div className="flex items-center space-x-2">
                    <Activity className={`w-4 h-4 ${overallStyle.text}`} />
                    <span className={`text-sm font-semibold ${overallStyle.text}`}>
                      {healthData.health_percentage}% Healthy
                    </span>
                  </div>
                )}
              </div>
            </div>
          </div>
          
          {/* Controls */}
          <div className="flex items-center space-x-3">
            {/* Auto-refresh toggle */}
            <button
              onClick={toggleAutoRefresh}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                autoRefresh
                  ? 'bg-blue-600 text-white hover:bg-blue-700'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
              title={autoRefresh ? 'Disable auto-refresh' : 'Enable auto-refresh'}
            >
              {autoRefresh ? (
                <>
                  <Pause className="w-4 h-4" />
                  <span className="text-sm font-medium">Auto ({countdown}s)</span>
                </>
              ) : (
                <>
                  <Play className="w-4 h-4" />
                  <span className="text-sm font-medium">Start Auto</span>
                </>
              )}
            </button>

            {/* Manual refresh */}
            <button
              onClick={handleManualRefresh}
              disabled={refreshing}
              className="flex items-center space-x-2 px-4 py-2 bg-white border-2 border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              title="Refresh now"
            >
              <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
              <span className="text-sm font-medium">Refresh</span>
            </button>
          </div>
        </div>

        {/* System Statistics */}
        {healthData && (
          <div className="mt-6 grid grid-cols-3 gap-4">
            <div className="bg-white rounded-lg p-4 shadow-sm">
              <div className="text-sm text-gray-600 mb-1">Total Components</div>
              <div className="text-2xl font-bold text-gray-900">{healthData.total_count}</div>
            </div>
            <div className="bg-white rounded-lg p-4 shadow-sm">
              <div className="text-sm text-gray-600 mb-1">Healthy</div>
              <div className="text-2xl font-bold text-green-600">{healthData.healthy_count}</div>
            </div>
            <div className="bg-white rounded-lg p-4 shadow-sm">
              <div className="text-sm text-gray-600 mb-1">Health Score</div>
              <div className="text-2xl font-bold text-blue-600">{healthData.health_percentage}%</div>
            </div>
          </div>
        )}
      </div>

      {/* Component Health Cards */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Component Status</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {healthData?.components?.map((component) => (
            <HealthMetricCard
              key={component.component}
              component={component}
              onRefresh={handleManualRefresh}
            />
          ))}
        </div>
      </div>

      {/* Refresh Indicator */}
      {refreshing && (
        <div className="fixed bottom-4 right-4 bg-blue-600 text-white px-4 py-2 rounded-lg shadow-lg flex items-center space-x-2">
          <RefreshCw className="w-4 h-4 animate-spin" />
          <span className="text-sm font-medium">Refreshing...</span>
        </div>
      )}
    </div>
  );
};

export default SystemHealthDashboard;
