import React from 'react';
import { Activity, Database, Server, Cloud, Github, Box, Link, AlertCircle, CheckCircle, Clock, TrendingUp } from 'lucide-react';

const HealthMetricCard = ({ component, onRefresh }) => {
  // Get appropriate icon for component
  const getIcon = () => {
    const iconProps = { className: "w-6 h-6" };
    switch (component.component) {
      case 'frontend':
        return <Box {...iconProps} />;
      case 'backend':
        return <Server {...iconProps} />;
      case 'database':
        return <Database {...iconProps} />;
      case 'mt5_bridge':
        return <Activity {...iconProps} />;
      case 'google_apis':
        return <Link {...iconProps} />;
      case 'github':
        return <Github {...iconProps} />;
      case 'render_platform':
        return <Cloud {...iconProps} />;
      default:
        return <Server {...iconProps} />;
    }
  };

  // Get status color and indicator
  const getStatusStyle = () => {
    switch (component.status) {
      case 'healthy':
        return {
          bg: 'bg-green-50',
          border: 'border-green-200',
          indicator: 'bg-green-500',
          text: 'text-green-800',
          iconBg: 'bg-green-100',
          iconText: 'text-green-600'
        };
      case 'degraded':
      case 'slow':
        return {
          bg: 'bg-yellow-50',
          border: 'border-yellow-200',
          indicator: 'bg-yellow-500',
          text: 'text-yellow-800',
          iconBg: 'bg-yellow-100',
          iconText: 'text-yellow-600'
        };
      case 'offline':
      case 'error':
      case 'timeout':
        return {
          bg: 'bg-red-50',
          border: 'border-red-200',
          indicator: 'bg-red-500',
          text: 'text-red-800',
          iconBg: 'bg-red-100',
          iconText: 'text-red-600'
        };
      case 'not_configured':
      case 'token_expired':
        return {
          bg: 'bg-orange-50',
          border: 'border-orange-200',
          indicator: 'bg-orange-500',
          text: 'text-orange-800',
          iconBg: 'bg-orange-100',
          iconText: 'text-orange-600'
        };
      default:
        return {
          bg: 'bg-gray-50',
          border: 'border-gray-200',
          indicator: 'bg-gray-400',
          text: 'text-gray-600',
          iconBg: 'bg-gray-100',
          iconText: 'text-gray-600'
        };
    }
  };

  const statusStyle = getStatusStyle();

  // Get status display text
  const getStatusText = () => {
    switch (component.status) {
      case 'healthy':
        return 'Healthy';
      case 'degraded':
        return 'Degraded';
      case 'slow':
        return 'Slow Response';
      case 'offline':
        return 'Offline';
      case 'error':
        return 'Error';
      case 'timeout':
        return 'Timeout';
      case 'not_configured':
        return 'Not Configured';
      case 'token_expired':
        return 'Token Expired';
      default:
        return 'Unknown';
    }
  };

  // Format time ago
  const formatTimeAgo = (timestamp) => {
    if (!timestamp) return 'Never';
    
    try {
      const date = new Date(timestamp);
      const now = new Date();
      const seconds = Math.floor((now - date) / 1000);
      
      if (seconds < 60) return `${seconds}s ago`;
      if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
      if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
      return `${Math.floor(seconds / 86400)}d ago`;
    } catch {
      return 'Unknown';
    }
  };

  return (
    <div className={`rounded-lg border-2 ${statusStyle.border} ${statusStyle.bg} p-6 transition-all hover:shadow-lg`}>
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className={`p-3 rounded-lg ${statusStyle.iconBg}`}>
            <div className={statusStyle.iconText}>
              {getIcon()}
            </div>
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">{component.name}</h3>
            <div className="flex items-center space-x-2 mt-1">
              <div className={`w-2 h-2 rounded-full ${statusStyle.indicator} animate-pulse`}></div>
              <span className={`text-sm font-medium ${statusStyle.text}`}>
                {getStatusText()}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Metrics */}
      <div className="space-y-3 mb-4">
        {/* Response Time */}
        {component.response_time !== undefined && (
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <Clock className="w-4 h-4" />
              <span>Response Time</span>
            </div>
            <span className="text-sm font-semibold text-gray-900">
              {Math.round(component.response_time)}ms
            </span>
          </div>
        )}

        {/* Latency (for database) */}
        {component.latency !== undefined && (
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <Activity className="w-4 h-4" />
              <span>Latency</span>
            </div>
            <span className="text-sm font-semibold text-gray-900">
              {Math.round(component.latency)}ms
            </span>
          </div>
        )}

        {/* Connection Status */}
        {component.connection && (
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <CheckCircle className="w-4 h-4" />
              <span>Connection</span>
            </div>
            <span className={`text-sm font-semibold ${component.connection === 'established' ? 'text-green-600' : 'text-red-600'}`}>
              {component.connection}
            </span>
          </div>
        )}

        {/* Database Specific */}
        {component.collections_count !== undefined && (
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <Database className="w-4 h-4" />
              <span>Collections</span>
            </div>
            <span className="text-sm font-semibold text-gray-900">
              {component.collections_count}
            </span>
          </div>
        )}

        {/* Google APIs Specific */}
        {component.token_expires_in_days !== undefined && component.token_expires_in_days !== null && (
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <Clock className="w-4 h-4" />
              <span>Token Expires</span>
            </div>
            <span className={`text-sm font-semibold ${component.token_expires_in_days < 7 ? 'text-orange-600' : 'text-gray-900'}`}>
              {component.token_expires_in_days} days
            </span>
          </div>
        )}

        {/* MT5 Bridge Specific */}
        {component.accounts_connected !== undefined && (
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <Activity className="w-4 h-4" />
              <span>Accounts</span>
            </div>
            <span className="text-sm font-semibold text-gray-900">
              {component.accounts_connected}
            </span>
          </div>
        )}

        {/* GitHub Specific */}
        {component.default_branch && (
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <Github className="w-4 h-4" />
              <span>Branch</span>
            </div>
            <span className="text-sm font-semibold text-gray-900">
              {component.default_branch}
            </span>
          </div>
        )}
      </div>

      {/* Message */}
      {component.message && (
        <div className={`p-3 rounded-lg ${statusStyle.bg} border ${statusStyle.border} mb-4`}>
          <p className={`text-xs ${statusStyle.text}`}>
            {component.message}
          </p>
        </div>
      )}

      {/* Error Message */}
      {component.error && (
        <div className="p-3 rounded-lg bg-red-50 border border-red-200 mb-4">
          <div className="flex items-start space-x-2">
            <AlertCircle className="w-4 h-4 text-red-600 mt-0.5 flex-shrink-0" />
            <p className="text-xs text-red-700">
              {component.error}
            </p>
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between text-xs text-gray-500 pt-3 border-t border-gray-200">
        <span>Last check: {formatTimeAgo(component.last_check)}</span>
        {component.url && (
          <a
            href={component.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 hover:text-blue-800 font-medium"
          >
            View →
          </a>
        )}
      </div>
    </div>
  );
};

export default HealthMetricCard;
