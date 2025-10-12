import React from 'react';
import { Handle, Position } from 'reactflow';

/**
 * InfrastructureNode - Custom node for infrastructure components (Load Balancer, CDN)
 * Gray gradient with traffic and latency info
 */
function InfrastructureNode({ data }) {
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
      bg-gradient-to-br from-gray-600 to-gray-500
      rounded-xl shadow-lg hover:shadow-2xl
      border-4 ${statusColors[status]}
      p-4 min-w-[280px] transition-all duration-200
      hover:scale-105 cursor-pointer
    `}>
      {/* Input Handle */}
      <Handle 
        type="target" 
        position={Position.Top}
        className="w-3 h-3 bg-gray-700 border-2 border-white"
      />
      
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <svg className="text-white" width="24" height="24" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h3 className="text-white font-bold text-base">{component.name}</h3>
        </div>
        <div className={`w-3 h-3 rounded-full ${statusDots[status]}`} />
      </div>

      {/* Features */}
      {component.features && (
        <div className="text-white text-sm mb-3 space-y-1">
          {Object.entries(component.features).slice(0, 3).map(([key, value], i) => (
            value && (
              <div key={i} className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-green-400" />
                <span className="capitalize text-xs">{key.replace(/_/g, ' ')}</span>
              </div>
            )
          ))}
        </div>
      )}

      {/* Traffic Indicator (Mock) */}
      <div className="text-white text-sm mb-3 space-y-1">
        <div>Traffic: 1.2K req/min</div>
        {health.response_time_ms && (
          <div>Latency: {Math.round(health.response_time_ms)}ms avg</div>
        )}
      </div>

      {/* Performance Bar */}
      <div className="mb-3">
        <div className="flex justify-between text-white text-xs mb-1">
          <span>Load</span>
          <span>23%</span>
        </div>
        <div className="w-full bg-white/20 rounded-full h-2">
          <div 
            className="bg-white h-2 rounded-full transition-all duration-300" 
            style={{ width: '23%' }}
          />
        </div>
      </div>

      {/* Action Button */}
      {component.management?.dashboard && (
        <a
          href={component.management.dashboard}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center justify-center gap-2 bg-white text-gray-600 rounded-lg px-3 py-2 text-sm font-medium hover:bg-gray-50 transition-colors"
          onClick={(e) => e.stopPropagation()}
        >
          Monitor
          <svg width="14" height="14" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
          </svg>
        </a>
      )}

      {/* Output Handle */}
      <Handle 
        type="source" 
        position={Position.Bottom}
        className="w-3 h-3 bg-gray-700 border-2 border-white"
      />
    </div>
  );

// Memoize component for performance
export default React.memo(InfrastructureNode);
