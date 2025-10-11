import React from 'react';
import { Handle, Position } from 'reactflow';

/**
 * DatabaseNode - Custom node for database components (MongoDB)
 * Green gradient with storage and collection info
 */
export default function DatabaseNode({ data }) {
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
      bg-gradient-to-br from-green-500 to-green-400
      rounded-xl shadow-lg hover:shadow-2xl
      border-4 ${statusColors[status]}
      p-4 min-w-[280px] transition-all duration-200
      hover:scale-105 cursor-pointer
    `}>
      {/* Input Handle */}
      <Handle 
        type="target" 
        position={Position.Top}
        className="w-3 h-3 bg-green-600 border-2 border-white"
      />
      
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <svg className="text-white" width="24" height="24" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" />
          </svg>
          <h3 className="text-white font-bold text-base">{component.name}</h3>
        </div>
        <div className={`w-3 h-3 rounded-full ${statusDots[status]}`} />
      </div>

      {/* Database Info */}
      {component.database_info && (
        <div className="text-white text-sm mb-3 space-y-1">
          {component.database_info.collections && (
            <div>Collections: {component.database_info.collections.length || component.database_info.collections}</div>
          )}
          {health.collections && (
            <div>Active: {health.collections}</div>
          )}
        </div>
      )}

      {/* Response Time */}
      {health.response_time_ms && (
        <div className="text-white text-sm mb-3">
          Ping: {Math.round(health.response_time_ms)}ms
        </div>
      )}

      {/* Storage Bar (Mock for now) */}
      <div className="mb-3">
        <div className="flex justify-between text-white text-xs mb-1">
          <span>Storage</span>
          <span>Active</span>
        </div>
        <div className="w-full bg-white/20 rounded-full h-2">
          <div 
            className="bg-white h-2 rounded-full transition-all duration-300" 
            style={{ width: '45%' }}
          />
        </div>
      </div>

      {/* Action Button */}
      {component.management?.dashboard && (
        <a
          href={component.management.dashboard}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center justify-center gap-2 bg-white text-green-600 rounded-lg px-3 py-2 text-sm font-medium hover:bg-green-50 transition-colors"
          onClick={(e) => e.stopPropagation()}
        >
          View Metrics
          <svg width="14" height="14" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
          </svg>
        </a>
      )}

      {/* Output Handle */}
      <Handle 
        type="source" 
        position={Position.Bottom}
        className="w-3 h-3 bg-green-600 border-2 border-white"
      />
    </div>
  );
}
