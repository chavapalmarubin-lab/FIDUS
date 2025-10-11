import React from 'react';

/**
 * ComponentCard - Displays individual system component information
 * Shows component status, metadata, and quick actions
 */
export default function ComponentCard({ component, health }) {
  // Status color mapping
  const statusColors = {
    online: 'bg-green-500',
    degraded: 'bg-yellow-500',
    offline: 'bg-red-500',
    unknown: 'bg-gray-400'
  };

  // Status text mapping
  const statusText = {
    online: 'Online',
    degraded: 'Degraded',
    offline: 'Offline',
    unknown: 'Unknown'
  };

  // Get component status (from health check if available, otherwise from registry)
  const componentStatus = health?.status || component.status || 'unknown';
  const statusColor = statusColors[componentStatus] || statusColors.unknown;

  // Format response time if available
  const responseTime = health?.response_time_ms 
    ? `${Math.round(health.response_time_ms)}ms` 
    : null;

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow">
      {/* Header with name and status */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="text-lg font-bold text-gray-900 mb-1">
            {component.name}
          </h3>
          <p className="text-sm text-gray-500">
            {component.type} • {component.platform}
          </p>
        </div>
        
        {/* Status indicator */}
        <div className="flex items-center space-x-2">
          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
            componentStatus === 'online' ? 'bg-green-100 text-green-800' :
            componentStatus === 'degraded' ? 'bg-yellow-100 text-yellow-800' :
            componentStatus === 'offline' ? 'bg-red-100 text-red-800' :
            'bg-gray-100 text-gray-800'
          }`}>
            <span className={`w-2 h-2 rounded-full ${statusColor} mr-1.5`}></span>
            {statusText[componentStatus]}
          </span>
        </div>
      </div>

      {/* Description */}
      <p className="text-sm text-gray-600 mb-4 line-clamp-2">
        {component.description}
      </p>

      {/* Health metrics */}
      {health && (
        <div className="mb-4 p-3 bg-gray-50 rounded-md">
          <div className="grid grid-cols-2 gap-2 text-xs">
            {responseTime && (
              <div>
                <span className="text-gray-500">Response:</span>
                <span className="ml-1 font-medium">{responseTime}</span>
              </div>
            )}
            {health.http_status && (
              <div>
                <span className="text-gray-500">HTTP:</span>
                <span className="ml-1 font-medium">{health.http_status}</span>
              </div>
            )}
            {health.last_sync && (
              <div className="col-span-2">
                <span className="text-gray-500">Last Sync:</span>
                <span className="ml-1 font-medium">
                  {health.minutes_since_sync?.toFixed(1)} min ago
                </span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Technology stack */}
      {component.tech_stack && component.tech_stack.length > 0 && (
        <div className="mb-4">
          <p className="text-xs font-semibold text-gray-700 mb-2">Tech Stack</p>
          <div className="flex flex-wrap gap-1">
            {component.tech_stack.slice(0, 3).map((tech, index) => (
              <span 
                key={index}
                className="inline-flex items-center px-2 py-0.5 rounded text-xs bg-blue-50 text-blue-700 border border-blue-200"
              >
                {tech}
              </span>
            ))}
            {component.tech_stack.length > 3 && (
              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs bg-gray-100 text-gray-600">
                +{component.tech_stack.length - 3} more
              </span>
            )}
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex items-center space-x-3 pt-4 border-t border-gray-100">
        {component.url && (
          <a
            href={component.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs text-blue-600 hover:text-blue-800 font-medium flex items-center"
          >
            View
            <svg className="w-3 h-3 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
          </a>
        )}
        
        {component.management?.dashboard && (
          <a
            href={component.management.dashboard}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs text-gray-600 hover:text-gray-800 font-medium flex items-center"
          >
            Dashboard
            <svg className="w-3 h-3 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </a>
        )}
      </div>

      {/* Error indicator */}
      {health?.error && (
        <div className="mt-3 p-2 bg-red-50 border border-red-200 rounded text-xs text-red-700">
          <span className="font-semibold">Error:</span> {health.error}
        </div>
      )}
    </div>
  );
}
