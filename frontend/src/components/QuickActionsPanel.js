import React, { useState, useEffect } from 'react';
import ActionCard from './ActionCard';
import LoadingSpinner from './LoadingSpinner';
import { Rocket, Database, Wrench, Clock, Activity, RefreshCw } from 'lucide-react';
import { GRIDS, TYPOGRAPHY, SPACING } from '../constants/uiConstants';

const QuickActionsPanel = () => {
  const [loading, setLoading] = useState({});
  const [results, setResults] = useState({});
  const [success, setSuccess] = useState({});
  const [errors, setErrors] = useState({});
  const [recentActions, setRecentActions] = useState([]);
  const [loadingRecent, setLoadingRecent] = useState(true);

  const backendUrl = process.env.REACT_APP_BACKEND_URL || '';

  // Fetch recent actions
  const fetchRecentActions = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/actions/recent?limit=10`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setRecentActions(data.actions || []);
      }
    } catch (error) {
      console.error('Error fetching recent actions:', error);
    } finally {
      setLoadingRecent(false);
    }
  };

  useEffect(() => {
    fetchRecentActions();
  }, []);

  // Execute action
  const executeAction = async (actionId, endpoint, actionName) => {
    // Reset previous state for this action
    setResults(prev => ({ ...prev, [actionId]: null }));
    setSuccess(prev => ({ ...prev, [actionId]: false }));
    setErrors(prev => ({ ...prev, [actionId]: null }));
    
    // Set loading state
    setLoading(prev => ({ ...prev, [actionId]: true }));

    try {
      const response = await fetch(`${backendUrl}${endpoint}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        }
      });

      const data = await response.json();

      if (data.success) {
        // Success!
        setSuccess(prev => ({ ...prev, [actionId]: true }));
        setResults(prev => ({ 
          ...prev, 
          [actionId]: data.message || 'Action completed successfully' 
        }));

        // Refresh recent actions
        fetchRecentActions();

        // Clear success state after 5 seconds
        setTimeout(() => {
          setSuccess(prev => ({ ...prev, [actionId]: false }));
          setResults(prev => ({ ...prev, [actionId]: null }));
        }, 5000);
      } else {
        // Error from backend
        throw new Error(data.message || data.error || 'Action failed');
      }
    } catch (error) {
      console.error(`Error executing action ${actionName}:`, error);
      setErrors(prev => ({ 
        ...prev, 
        [actionId]: error.message || 'Failed to execute action' 
      }));

      // Clear error state after 10 seconds
      setTimeout(() => {
        setErrors(prev => ({ ...prev, [actionId]: null }));
      }, 10000);
    } finally {
      setLoading(prev => ({ ...prev, [actionId]: false }));
    }
  };

  // Format timestamp
  const formatTimestamp = (timestamp) => {
    if (!timestamp) return '';
    try {
      const date = new Date(timestamp);
      const now = new Date();
      const diffMs = now - date;
      const diffMins = Math.floor(diffMs / 60000);
      const diffHours = Math.floor(diffMs / 3600000);

      if (diffMins < 1) return 'Just now';
      if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
      if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
      
      return date.toLocaleString();
    } catch (e) {
      return timestamp;
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 flex items-center space-x-2 mb-2">
          <span>⚡</span>
          <span>Quick Actions</span>
        </h2>
        <p className="text-gray-600">
          One-click admin tools for deployment, data management, and system maintenance
        </p>
      </div>

      {/* Deployment Section */}
      <section>
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
          <Rocket className="w-5 h-5 text-blue-600" />
          <span>Deployment</span>
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <ActionCard
            icon="🌐"
            title="Deploy Frontend"
            description="Trigger frontend redeployment on Render platform"
            loading={loading.deployFrontend}
            success={success.deployFrontend}
            error={errors.deployFrontend}
            result={results.deployFrontend}
            onClick={() => executeAction('deployFrontend', '/api/actions/restart-frontend', 'Deploy Frontend')}
          />
          <ActionCard
            icon="🔧"
            title="Deploy Backend"
            description="Restart backend API service on Render platform"
            loading={loading.deployBackend}
            success={success.deployBackend}
            error={errors.deployBackend}
            result={results.deployBackend}
            onClick={() => executeAction('deployBackend', '/api/actions/restart-backend', 'Deploy Backend')}
          />
          <ActionCard
            icon="🔄"
            title="Restart All Services"
            description="Restart both frontend and backend services"
            loading={loading.restartAll}
            success={success.restartAll}
            error={errors.restartAll}
            result={results.restartAll}
            onClick={() => executeAction('restartAll', '/api/actions/restart-all', 'Restart All')}
          />
        </div>
      </section>

      {/* Data Management Section */}
      <section>
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
          <Database className="w-5 h-5 text-purple-600" />
          <span>Data Management</span>
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <ActionCard
            icon="📊"
            title="Sync MT5 Data"
            description="Trigger immediate MT5 account data synchronization"
            loading={loading.syncMT5}
            success={success.syncMT5}
            error={errors.syncMT5}
            result={results.syncMT5}
            onClick={() => executeAction('syncMT5', '/api/actions/sync-mt5', 'Sync MT5 Data')}
          />
          <ActionCard
            icon="💰"
            title="Refresh Performance"
            description="Recalculate fund performance metrics and analytics"
            loading={loading.refreshPerf}
            success={success.refreshPerf}
            error={errors.refreshPerf}
            result={results.refreshPerf}
            onClick={() => executeAction('refreshPerf', '/api/actions/refresh-performance', 'Refresh Performance')}
          />
          <ActionCard
            icon="🗄️"
            title="Backup Database"
            description="Initiate MongoDB Atlas automatic backup"
            loading={loading.backup}
            success={success.backup}
            error={errors.backup}
            result={results.backup}
            onClick={() => executeAction('backup', '/api/actions/backup-database', 'Backup Database')}
          />
        </div>
      </section>

      {/* System Tools Section */}
      <section>
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
          <Wrench className="w-5 h-5 text-orange-600" />
          <span>System Tools</span>
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <ActionCard
            icon="🧪"
            title="Test Integrations"
            description="Run health checks on all system integrations"
            loading={loading.testIntegrations}
            success={success.testIntegrations}
            error={errors.testIntegrations}
            result={results.testIntegrations}
            onClick={() => executeAction('testIntegrations', '/api/actions/test-integrations', 'Test Integrations')}
          />
          <ActionCard
            icon="📜"
            title="View Logs"
            description="View recent system logs and activity"
            onClick={() => window.open(`${backendUrl}/api/actions/logs`, '_blank')}
          />
          <ActionCard
            icon="📊"
            title="Generate Report"
            description="Generate comprehensive system status report"
            loading={loading.systemReport}
            success={success.systemReport}
            error={errors.systemReport}
            result={results.systemReport}
            onClick={() => executeAction('systemReport', '/api/actions/generate-report', 'Generate Report')}
          />
        </div>
      </section>

      {/* Recent Actions Timeline */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center space-x-2">
            <Clock className="w-5 h-5 text-gray-600" />
            <span>Recent Actions</span>
          </h3>
          <button
            onClick={fetchRecentActions}
            className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
            title="Refresh recent actions"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>

        <div className="bg-white border-2 border-gray-200 rounded-lg overflow-hidden">
          {loadingRecent ? (
            <div className="p-8 text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-2 text-sm text-gray-600">Loading recent actions...</p>
            </div>
          ) : recentActions.length === 0 ? (
            <div className="p-8 text-center">
              <Activity className="w-12 h-12 text-gray-300 mx-auto mb-3" />
              <p className="text-gray-500">No recent actions yet</p>
              <p className="text-sm text-gray-400 mt-1">Actions will appear here when executed</p>
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {recentActions.map((action, index) => (
                <div
                  key={action._id || index}
                  className="p-4 hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3">
                        <div className={`w-2 h-2 rounded-full ${
                          action.status === 'success' 
                            ? 'bg-green-500' 
                            : action.status === 'failed'
                            ? 'bg-red-500'
                            : 'bg-yellow-500'
                        }`}></div>
                        <span className="font-medium text-gray-900 capitalize">
                          {action.action_name?.replace(/_/g, ' ') || 'Unknown Action'}
                        </span>
                        <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                          action.status === 'success'
                            ? 'bg-green-100 text-green-700'
                            : action.status === 'failed'
                            ? 'bg-red-100 text-red-700'
                            : 'bg-yellow-100 text-yellow-700'
                        }`}>
                          {action.status}
                        </span>
                      </div>
                      <p className="text-sm text-gray-500 mt-1 ml-5">
                        {formatTimestamp(action.timestamp)}
                      </p>
                      {action.error && (
                        <p className="text-xs text-red-600 mt-1 ml-5">
                          Error: {action.error}
                        </p>
                      )}
                    </div>
                    <span className="text-xs text-gray-400 uppercase tracking-wide">
                      {action.action_type?.replace(/_/g, ' ')}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </section>
    </div>
  );
};

export default QuickActionsPanel;
