import React from 'react';
import { Handle, Position } from 'reactflow';

/**
 * IntegrationNode - Custom node for integration components (Google, Email, etc.)
 * Orange gradient with API status and connection info
 */
function IntegrationNode({ data }) {
  const component = data.component || {};
  const health = data.health || {};
  
  const status = health.status || component.status || 'unknown';
  
  const statusColors = {
    online: 'border-green-500',
    degraded: 'border-yellow-500',
    offline: 'border-red-500',
    unknown: 'border-gray-400'
  };

  const statusDots = {
    online: 'bg-green-400 animate-pulse',
    degraded: 'bg-yellow-400 animate-pulse',
    offline: 'bg-red-400',
    unknown: 'bg-gray-400'
  };

  return (
    <div className={`
      bg-gradient-to-br from-orange-500 to-orange-400
      rounded-xl shadow-lg hover:shadow-2xl
      border-4 ${statusColors[status]}
      p-4 min-w-[280px] transition-all duration-200
      hover:scale-105 cursor-pointer
    `}>
      {/* Input Handle */}
      <Handle 
        type="target" 
        position={Position.Top}
        className="w-3 h-3 bg-orange-600 border-2 border-white"
      />
      
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <svg className="text-white" width="24" height="24" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 4a2 2 0 114 0v1a1 1 0 001 1h3a1 1 0 011 1v3a1 1 0 01-1 1h-1a2 2 0 100 4h1a1 1 0 011 1v3a1 1 0 01-1 1h-3a1 1 0 01-1-1v-1a2 2 0 10-4 0v1a1 1 0 01-1 1H7a1 1 0 01-1-1v-3a1 1 0 00-1-1H4a2 2 0 110-4h1a1 1 0 001-1V7a1 1 0 011-1h3a1 1 0 001-1V4z" />
          </svg>
          <h3 className="text-white font-bold text-base">{component.name}</h3>
        </div>
        <div className={`w-3 h-3 rounded-full ${statusDots[status]}`} />
      </div>

      {/* APIs Used */}
      {component.apis_used && component.apis_used.length > 0 && (
        <div className="text-white text-sm mb-3 space-y-1">
          <div className="font-semibold">APIs:</div>
          {component.apis_used.slice(0, 3).map((api, i) => (
            <div key={i} className="text-xs">• {api.name || api}</div>
          ))}
        </div>
      )}

      {/* Connection Status */}
      <div className="flex items-center gap-2 text-white text-sm mb-3">
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
          status === 'online' ? 'bg-green-500/30' :
          status === 'degraded' ? 'bg-yellow-500/30' :
          'bg-red-500/30'
        }`}>
          {status === 'online' ? 'Connected' : status === 'degraded' ? 'Limited' : 'Disconnected'}
        </span>
      </div>

      {/* Response Time */}
      {health.response_time_ms && (
        <div className="text-white text-sm mb-3">
          Response: {Math.round(health.response_time_ms)}ms
        </div>
      )}

      {/* Action Button */}
      {component.management?.api_console && (
        <a
          href={component.management.api_console}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center justify-center gap-2 bg-white text-orange-600 rounded-lg px-3 py-2 text-sm font-medium hover:bg-orange-50 transition-colors"
          onClick={(e) => e.stopPropagation()}
        >
          Configure
          <svg width="14" height="14" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
          </svg>
        </a>
      )}

      {/* Output Handle */}
      <Handle 
        type="source" 
        position={Position.Bottom}
        className="w-3 h-3 bg-orange-600 border-2 border-white"
      />
    </div>
  );
}


// Memoize component for performance
export default React.memo(IntegrationNode);
