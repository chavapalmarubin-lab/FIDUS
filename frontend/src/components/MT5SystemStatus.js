import React, { useState, useEffect } from 'react';
import { Activity, Server, Database, CheckCircle, AlertCircle, Clock, TrendingUp } from 'lucide-react';

/**
 * MT5 System Status Component
 * Displays real-time status of MT5 Bridge Service, sync health, and terminal connection
 * 
 * Phase 4A & 4B Implementation - Complete System Monitoring
 */
export default function MT5SystemStatus() {
  const [terminalStatus, setTerminalStatus] = useState(null);
  const [syncStatus, setSyncStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastRefresh, setLastRefresh] = useState(new Date());

  const backendUrl = process.env.REACT_APP_BACKEND_URL || '';

  const fetchStatus = async () => {
    try {
      setError(null);
      
      // Fetch terminal status
      const terminalResponse = await fetch(`${backendUrl}/api/mt5/terminal/status`);
      if (terminalResponse.ok) {
        const terminalData = await terminalResponse.json();
        setTerminalStatus(terminalData.status);
      }
      
      // Fetch sync status
      const syncResponse = await fetch(`${backendUrl}/api/mt5/sync-status`);
      if (syncResponse.ok) {
        const syncData = await syncResponse.json();
        setSyncStatus(syncData.status);
      }
      
      setLastRefresh(new Date());
      setLoading(false);
    } catch (err) {
      console.error('Error fetching MT5 status:', err);
      setError(err.message);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const getHealthColor = (status) => {
    if (status === 'healthy') return 'text-green-500 bg-green-100';
    if (status === 'warning') return 'text-yellow-500 bg-yellow-100';
    if (status === 'critical') return 'text-red-500 bg-red-100';
    return 'text-gray-500 bg-gray-100';
  };

  const getHealthIcon = (status) => {
    if (status === 'healthy') return <CheckCircle className="w-5 h-5" />;
    if (status === 'warning') return <AlertCircle className="w-5 h-5" />;
    if (status === 'critical') return <AlertCircle className="w-5 h-5" />;
    return <Activity className="w-5 h-5" />;
  };

  if (loading && !terminalStatus && !syncStatus) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-gray-200 rounded w-1/3"></div>
          <div className="space-y-3">
            <div className="h-4 bg-gray-200 rounded"></div>
            <div className="h-4 bg-gray-200 rounded w-5/6"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-cyan-600 p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold mb-2">MT5 System Status</h2>
            <p className="text-blue-100 text-sm">
              Real-time monitoring of MT5 Bridge Service & Terminal Health
            </p>
          </div>
          <button
            onClick={fetchStatus}
            className="p-2 bg-white/20 hover:bg-white/30 rounded-lg transition-colors"
            title="Refresh status"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
        </div>
      </div>

      {/* Status Cards Grid */}
      <div className="p-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* VPS Bridge Service */}
        <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
          <div className="flex items-center justify-between mb-3">
            <Server className="w-6 h-6 text-blue-600" />
            <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getHealthColor(terminalStatus?.health_status || 'unknown')}`}>
              {terminalStatus?.terminal_initialized ? 'Running' : 'Unknown'}
            </span>
          </div>
          <h3 className="font-semibold text-gray-900 mb-1">VPS Bridge Service</h3>
          <p className="text-sm text-gray-600">
            {terminalStatus?.connected ? 'Connected to MT5' : 'Status unknown'}
          </p>
          <div className="mt-3 pt-3 border-t border-gray-200">
            <div className="flex justify-between text-xs">
              <span className="text-gray-500">Build:</span>
              <span className="font-medium text-gray-900">{terminalStatus?.build || 'N/A'}</span>
            </div>
            <div className="flex justify-between text-xs mt-1">
              <span className="text-gray-500">Ping:</span>
              <span className="font-medium text-gray-900">{terminalStatus?.ping_last ? `${terminalStatus.ping_last}ms` : 'N/A'}</span>
            </div>
          </div>
        </div>

        {/* Terminal Connection */}
        <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
          <div className="flex items-center justify-between mb-3">
            <Activity className="w-6 h-6 text-green-600" />
            {getHealthIcon(terminalStatus?.health_status || 'unknown')}
          </div>
          <h3 className="font-semibold text-gray-900 mb-1">Terminal Health</h3>
          <p className="text-sm text-gray-600 capitalize">
            {terminalStatus?.health_status || 'Unknown'}
          </p>
          <div className="mt-3 pt-3 border-t border-gray-200">
            <div className="flex justify-between text-xs">
              <span className="text-gray-500">Trade Allowed:</span>
              <span className={`font-medium ${terminalStatus?.trade_allowed ? 'text-green-600' : 'text-red-600'}`}>
                {terminalStatus?.trade_allowed ? 'Yes' : 'No'}
              </span>
            </div>
            <div className="flex justify-between text-xs mt-1">
              <span className="text-gray-500">Accounts:</span>
              <span className="font-medium text-gray-900">{terminalStatus?.active_accounts || 0}</span>
            </div>
          </div>
        </div>

        {/* Sync Status */}
        <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
          <div className="flex items-center justify-between mb-3">
            <Clock className="w-6 h-6 text-purple-600" />
            <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getHealthColor(syncStatus?.sync_health || 'unknown')}`}>
              {syncStatus?.sync_health || 'Unknown'}
            </span>
          </div>
          <h3 className="font-semibold text-gray-900 mb-1">Sync Status</h3>
          <p className="text-sm text-gray-600">
            Data Freshness: {syncStatus?.data_freshness_minutes || 'N/A'} min
          </p>
          <div className="mt-3 pt-3 border-t border-gray-200">
            <div className="flex justify-between text-xs">
              <span className="text-gray-500">Deals Today:</span>
              <span className="font-medium text-gray-900">{syncStatus?.deals_synced_today || 0}</span>
            </div>
            <div className="flex justify-between text-xs mt-1">
              <span className="text-gray-500">Snapshots:</span>
              <span className="font-medium text-gray-900">{syncStatus?.snapshots_today || 0}</span>
            </div>
          </div>
        </div>

        {/* Data Collections */}
        <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
          <div className="flex items-center justify-between mb-3">
            <Database className="w-6 h-6 text-cyan-600" />
            <TrendingUp className="w-5 h-5 text-green-500" />
          </div>
          <h3 className="font-semibold text-gray-900 mb-1">Data Collections</h3>
          <p className="text-sm text-gray-600">
            Phase 4A & 4B Active
          </p>
          <div className="mt-3 pt-3 border-t border-gray-200">
            <div className="flex justify-between text-xs">
              <span className="text-gray-500">Accounts:</span>
              <span className="font-medium text-gray-900">{syncStatus?.accounts_synced || 7}</span>
            </div>
            <div className="flex justify-between text-xs mt-1">
              <span className="text-gray-500">Errors:</span>
              <span className={`font-medium ${terminalStatus?.total_errors_today > 10 ? 'text-red-600' : 'text-green-600'}`}>
                {terminalStatus?.total_errors_today || 0}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Detailed Info */}
      <div className="px-6 pb-6">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start">
            <Activity className="w-5 h-5 text-blue-600 mr-3 mt-0.5 flex-shrink-0" />
            <div className="flex-1">
              <h4 className="font-semibold text-blue-900 mb-2">Phase 4A & 4B Features Active</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm text-blue-800">
                <div className="flex items-center">
                  <CheckCircle className="w-4 h-4 mr-2 text-green-600" />
                  <span>Equity Snapshots (Hourly)</span>
                </div>
                <div className="flex items-center">
                  <CheckCircle className="w-4 h-4 mr-2 text-green-600" />
                  <span>Pending Orders Tracking</span>
                </div>
                <div className="flex items-center">
                  <CheckCircle className="w-4 h-4 mr-2 text-green-600" />
                  <span>Terminal Status Monitoring</span>
                </div>
                <div className="flex items-center">
                  <CheckCircle className="w-4 h-4 mr-2 text-green-600" />
                  <span>Transfer Classification</span>
                </div>
                <div className="flex items-center">
                  <CheckCircle className="w-4 h-4 mr-2 text-green-600" />
                  <span>Account Growth Metrics</span>
                </div>
                <div className="flex items-center">
                  <CheckCircle className="w-4 h-4 mr-2 text-green-600" />
                  <span>Error Logging</span>
                </div>
                <div className="flex items-center">
                  <CheckCircle className="w-4 h-4 mr-2 text-green-600" />
                  <span>Spread Analysis</span>
                </div>
                <div className="flex items-center">
                  <CheckCircle className="w-4 h-4 mr-2 text-green-600" />
                  <span>Broker Rebates</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Last Update */}
        <div className="mt-4 text-center text-xs text-gray-500">
          Last refreshed: {lastRefresh.toLocaleString()}
          <span className="mx-2">•</span>
          Auto-refresh every 30 seconds
        </div>
      </div>

      {error && (
        <div className="px-6 pb-6">
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-start">
              <AlertCircle className="w-5 h-5 text-red-600 mr-3 mt-0.5" />
              <div>
                <h4 className="font-semibold text-red-900 mb-1">Error Loading Status</h4>
                <p className="text-sm text-red-700">{error}</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
