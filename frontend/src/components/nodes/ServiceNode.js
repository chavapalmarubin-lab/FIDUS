import React from 'react';
import { Handle, Position } from 'reactflow';

/**
 * ServiceNode - Custom node for service components (VPS, MT5)
 * Purple gradient with uptime and performance metrics
 */
function ServiceNode({ data }) {
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
      bg-gradient-to-br from-purple-500 to-purple-400
      rounded-xl shadow-lg hover:shadow-2xl
      border-4 ${statusColors[status]}
      p-4 min-w-[280px] transition-all duration-200
      hover:scale-105 cursor-pointer
    `}>
      {/* Input Handle */}
      <Handle 
        type="target" 
        position={Position.Top}
        className="w-3 h-3 bg-purple-600 border-2 border-white"
      />
      
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <svg className="text-white" width="24" height="24" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01" />
          </svg>
          <h3 className="text-white font-bold text-base">{component.name}</h3>
        </div>
        <div className={`w-3 h-3 rounded-full ${statusDots[status]}`} />
      </div>

      {/* Service Info */}
      <div className="text-white text-sm mb-3 space-y-1">
        {health.last_sync && (
          <div>Last Sync: {health.minutes_since_sync?.toFixed(0)}m ago</div>
        )}
        {health.response_time_ms && (
          <div>Response: {Math.round(health.response_time_ms)}ms</div>
        )}
        {component.environment?.ram && (
          <div>RAM: {component.environment.ram}</div>
        )}
      </div>

      {/* Uptime Display (Mock - 99.9%) */}
      <div className="text-white text-sm mb-3">
        <div className="flex justify-between items-center">
          <span>Uptime:</span>
          <span className="font-bold">99.9%</span>
        </div>
      </div>

      {/* Performance Bar */}
      <div className="mb-3">
        <div className="flex justify-between text-white text-xs mb-1">
          <span>Performance</span>
          <span>{status === 'online' ? '92%' : status === 'degraded' ? '65%' : '0%'}</span>
        </div>
        <div className="w-full bg-white/20 rounded-full h-2">
          <div 
            className="bg-white h-2 rounded-full transition-all duration-300" 
            style={{ 
              width: status === 'online' ? '92%' : status === 'degraded' ? '65%' : '0%'
            }}
          />
        </div>
      </div>

      {/* Action Button */}
      {component.management?.dashboard && (
        <a
          href={component.management.dashboard}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center justify-center gap-2 bg-white text-purple-600 rounded-lg px-3 py-2 text-sm font-medium hover:bg-purple-50 transition-colors"
          onClick={(e) => e.stopPropagation()}
        >
          Connect
          <svg width="14" height="14" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
          </svg>
        </a>
      )}

      {/* Output Handle */}
      <Handle 
        type="source" 
        position={Position.Bottom}
        className="w-3 h-3 bg-purple-600 border-2 border-white"
      />
    </div>
  );

  );
}

// Memoize component for performance
export default React.memo(ServiceNode);
