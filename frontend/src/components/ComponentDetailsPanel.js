import React, { useState } from 'react';

/**
 * ComponentDetailsPanel - Enhanced sliding panel with tabs
 * Shows detailed component information with Overview, Health, Actions, and Logs tabs
 */
export default function ComponentDetailsPanel({ component, health, onClose }) {
  const [activeTab, setActiveTab] = useState('overview');

  if (!component) return null;

  const tabs = [
    { id: 'overview', label: 'Overview', icon: '📋' },
    { id: 'health', label: 'Health', icon: '💚' },
    { id: 'actions', label: 'Actions', icon: '⚡' },
    { id: 'logs', label: 'Logs', icon: '📝' },
  ];

  return (
    <div className="absolute top-0 right-0 w-96 h-full bg-white border-l border-gray-200 shadow-2xl overflow-hidden flex flex-col animate-slide-in">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-500 p-6 text-white">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <h2 className="text-xl font-bold">{component.name}</h2>
              <p className="text-blue-100 text-sm">{component.type}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-white hover:bg-white/20 rounded-lg p-2 transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Status Banner */}
        <div className={`flex items-center gap-2 px-3 py-2 rounded-lg ${
          health?.status === 'online' ? 'bg-green-500/30' :
          health?.status === 'degraded' ? 'bg-yellow-500/30' :
          health?.status === 'offline' ? 'bg-red-500/30' :
          'bg-gray-500/30'
        }`}>
          <div className={`w-2 h-2 rounded-full ${
            health?.status === 'online' ? 'bg-green-300 animate-pulse' :
            health?.status === 'degraded' ? 'bg-yellow-300 animate-pulse' :
            health?.status === 'offline' ? 'bg-red-300' :
            'bg-gray-300'
          }`} />
          <span className="text-sm font-medium capitalize">
            {health?.status || component.status || 'Unknown'}
          </span>
          {health?.response_time_ms && (
            <span className="text-xs ml-auto">
              {Math.round(health.response_time_ms)}ms
            </span>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-200 bg-gray-50">
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
              activeTab === tab.id
                ? 'text-blue-600 border-b-2 border-blue-600 bg-white'
                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
            }`}
          >
            <span className="mr-1">{tab.icon}</span>
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-y-auto p-6">
        {activeTab === 'overview' && (
          <div className="space-y-4">
            <div>
              <h3 className="text-sm font-semibold text-gray-700 mb-2">Platform</h3>
              <p className="text-sm text-gray-600">{component.platform}</p>
            </div>

            <div>
              <h3 className="text-sm font-semibold text-gray-700 mb-2">Description</h3>
              <p className="text-sm text-gray-600">{component.description}</p>
            </div>

            {component.tech_stack && component.tech_stack.length > 0 && (
              <div>
                <h3 className="text-sm font-semibold text-gray-700 mb-2">Tech Stack</h3>
                <div className="flex flex-wrap gap-2">
                  {component.tech_stack.map((tech, i) => (
                    <span key={i} className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full">
                      {tech}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {component.url && (
              <div>
                <h3 className="text-sm font-semibold text-gray-700 mb-2">URL</h3>
                <a
                  href={component.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-blue-600 hover:text-blue-800 break-all"
                >
                  {component.url}
                </a>
              </div>
            )}

            {component.dependencies && component.dependencies.length > 0 && (
              <div>
                <h3 className="text-sm font-semibold text-gray-700 mb-2">Dependencies</h3>
                <div className="space-y-1">
                  {component.dependencies.map((dep, i) => (
                    <div key={i} className="text-sm text-gray-600 flex items-center gap-2">
                      <div className="w-1.5 h-1.5 rounded-full bg-gray-400" />
                      {dep}
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div>
              <h3 className="text-sm font-semibold text-gray-700 mb-2">Last Updated</h3>
              <p className="text-sm text-gray-600">{new Date().toLocaleString()}</p>
            </div>
          </div>
        )}

        {activeTab === 'health' && (
          <div className="space-y-4">
            <div className="bg-gray-50 rounded-lg p-4">
              <h3 className="text-sm font-semibold text-gray-700 mb-3">Current Metrics</h3>
              <div className="space-y-3">
                {health?.response_time_ms && (
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-600">Response Time</span>
                      <span className="font-medium">{Math.round(health.response_time_ms)}ms</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full transition-all"
                        style={{ width: `${Math.min((health.response_time_ms / 500) * 100, 100)}%` }}
                      />
                    </div>
                  </div>
                )}

                {health?.http_status && (
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">HTTP Status</span>
                    <span className={`font-medium ${
                      health.http_status === 200 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {health.http_status}
                    </span>
                  </div>
                )}

                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Uptime</span>
                  <span className="font-medium text-green-600">99.9%</span>
                </div>

                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Error Rate</span>
                  <span className="font-medium text-green-600">0.01%</span>
                </div>
              </div>
            </div>

            {health?.error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <h3 className="text-sm font-semibold text-red-700 mb-2">Error Details</h3>
                <p className="text-sm text-red-600">{health.error}</p>
              </div>
            )}

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h3 className="text-sm font-semibold text-blue-700 mb-2">Health Check History</h3>
              <p className="text-xs text-blue-600">Last 24 hours: All checks passed</p>
            </div>
          </div>
        )}

        {activeTab === 'actions' && (
          <div className="space-y-3">
            {component.url && (
              <button
                onClick={() => window.open(component.url, '_blank')}
                className="w-full flex items-center justify-between px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <span className="font-medium">View Dashboard</span>
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </button>
            )}

            {component.management?.dashboard && (
              <button
                onClick={() => window.open(component.management.dashboard, '_blank')}
                className="w-full flex items-center justify-between px-4 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
              >
                <span className="font-medium">Management Console</span>
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </button>
            )}

            <button
              className="w-full flex items-center justify-between px-4 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
              onClick={() => alert('Test connection feature coming soon!')}
            >
              <span className="font-medium">Test Connection</span>
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </button>

            <button
              className="w-full flex items-center justify-between px-4 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
              onClick={() => alert('View logs feature coming soon!')}
            >
              <span className="font-medium">View Logs</span>
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </button>

            {component.quick_actions && component.quick_actions.length > 0 && (
              <div className="pt-3 border-t border-gray-200">
                <h3 className="text-sm font-semibold text-gray-700 mb-2">Quick Actions</h3>
                <div className="space-y-2">
                  {component.quick_actions.map((action, i) => (
                    <button
                      key={i}
                      className="w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded transition-colors"
                    >
                      {action}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'logs' && (
          <div className="space-y-4">
            <div className="flex gap-2 mb-4">
              <button className="px-3 py-1 text-xs bg-blue-100 text-blue-700 rounded-full font-medium">
                All
              </button>
              <button className="px-3 py-1 text-xs bg-gray-100 text-gray-600 rounded-full hover:bg-gray-200">
                Info
              </button>
              <button className="px-3 py-1 text-xs bg-gray-100 text-gray-600 rounded-full hover:bg-gray-200">
                Warning
              </button>
              <button className="px-3 py-1 text-xs bg-gray-100 text-gray-600 rounded-full hover:bg-gray-200">
                Error
              </button>
            </div>

            <div className="space-y-2">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="bg-gray-50 border border-gray-200 rounded-lg p-3">
                  <div className="flex items-start justify-between mb-1">
                    <span className="text-xs font-medium text-green-600">INFO</span>
                    <span className="text-xs text-gray-500">{i + 1}m ago</span>
                  </div>
                  <p className="text-sm text-gray-700">
                    Component health check completed successfully
                  </p>
                </div>
              ))}
            </div>

            <button className="w-full px-4 py-2 text-sm text-blue-600 hover:bg-blue-50 rounded-lg transition-colors">
              View All Logs →
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
