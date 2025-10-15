/**
 * MT5 Health Indicator - Phase 3
 * Shows real-time sync status and data freshness
 */

import React from 'react';
import { useMT5Health } from '../hooks/useMT5Data';
import { AlertCircle, CheckCircle, Clock, XCircle } from 'lucide-react';

const MT5HealthIndicator = ({ showDetails = false, className = '' }) => {
  const { health, loading } = useMT5Health();

  if (loading) {
    return (
      <div className={`flex items-center gap-2 text-sm text-gray-500 ${className}`}>
        <Clock className="w-4 h-4 animate-spin" />
        <span>Checking sync status...</span>
      </div>
    );
  }

  if (!health) {
    return null;
  }

  const getStatusIcon = () => {
    if (health.healthy) {
      return <CheckCircle className="w-4 h-4 text-green-500" />;
    } else if (health.status === 'degraded') {
      return <AlertCircle className="w-4 h-4 text-yellow-500" />;
    } else {
      return <XCircle className="w-4 h-4 text-red-500" />;
    }
  };

  const getStatusColor = () => {
    if (health.healthy) return 'text-green-600';
    if (health.status === 'degraded') return 'text-yellow-600';
    return 'text-red-600';
  };

  const getStatusBackground = () => {
    if (health.healthy) return 'bg-green-50 border-green-200';
    if (health.status === 'degraded') return 'bg-yellow-50 border-yellow-200';
    return 'bg-red-50 border-red-200';
  };

  return (
    <div className={`${className}`}>
      {/* Compact view */}
      {!showDetails && (
        <div className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border ${getStatusBackground()}`}>
          {getStatusIcon()}
          <span className={`text-sm font-medium ${getStatusColor()}`}>
            {health.message}
          </span>
        </div>
      )}

      {/* Detailed view */}
      {showDetails && (
        <div className={`p-4 rounded-lg border ${getStatusBackground()}`}>
          <div className="flex items-start gap-3">
            {getStatusIcon()}
            <div className="flex-1">
              <div className={`font-medium ${getStatusColor()}`}>
                MT5 Data Sync Status
              </div>
              <div className="text-sm text-gray-600 mt-1">
                {health.message}
              </div>
              
              {health.accounts_count > 0 && (
                <div className="mt-2 space-y-1 text-xs text-gray-500">
                  <div>Total Accounts: {health.accounts_count}</div>
                  <div>Fresh Data: {health.fresh_accounts} accounts</div>
                  {health.stale_accounts_count > 0 && (
                    <div className="text-yellow-600 font-medium">
                      Stale Data: {health.stale_accounts_count} accounts (>10 min old)
                    </div>
                  )}
                </div>
              )}

              {health.stale_accounts && health.stale_accounts.length > 0 && (
                <details className="mt-2">
                  <summary className="text-xs text-gray-500 cursor-pointer hover:text-gray-700">
                    View stale accounts
                  </summary>
                  <div className="mt-1 pl-4 space-y-1">
                    {health.stale_accounts.map(acc => (
                      <div key={acc.account} className="text-xs text-gray-600">
                        Account {acc.account}: {acc.minutes_old.toFixed(1)} min old
                      </div>
                    ))}
                  </div>
                </details>
              )}

              {health.timestamp && (
                <div className="mt-2 text-xs text-gray-400">
                  Last checked: {new Date(health.timestamp).toLocaleTimeString()}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MT5HealthIndicator;
