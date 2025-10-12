import React from 'react';
import { Handle, Position } from 'reactflow';

/**
 * ApplicationNode - Custom node for application components (Frontend, Backend)
 * Blue gradient with tech stack and response time
 */
function ApplicationNode({ data }) {
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
      bg-gradient-to-br from-blue-500 to-blue-400
      rounded-xl shadow-lg hover:shadow-2xl
      border-4 ${statusColors[status]}
      p-4 min-w-[280px] transition-all duration-200
      hover:scale-105 cursor-pointer
    `}>
      {/* Input Handle */}
      <Handle 
        type="target" 
        position={Position.Top}
        className="w-3 h-3 bg-blue-600 border-2 border-white"
      />
      
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <svg className="text-white" width="24" height="24" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
          <h3 className="text-white font-bold text-base">{component.name}</h3>
        </div>
        <div className={`w-3 h-3 rounded-full ${statusDots[status]}`} />
      </div>

      {/* Tech Stack */}
      {component.tech_stack && component.tech_stack.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-3">
          {component.tech_stack.slice(0, 2).map((tech, i) => (
            <span key={i} className="text-xs bg-white/20 text-white px-2 py-1 rounded-full">
              {tech}
            </span>
          ))}
          {component.tech_stack.length > 2 && (
            <span className="text-xs bg-white/20 text-white px-2 py-1 rounded-full">
              +{component.tech_stack.length - 2}
            </span>
          )}
        </div>
      )}

      {/* Metrics */}
      <div className="text-white text-sm mb-3 space-y-1">
        {health.response_time_ms && (
          <div>Response: {Math.round(health.response_time_ms)}ms</div>
        )}
        {health.http_status && (
          <div>Status: {health.http_status}</div>
        )}
      </div>

      {/* Action Button */}
      {component.url && (
        <a
          href={component.url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center justify-center gap-2 bg-white text-blue-600 rounded-lg px-3 py-2 text-sm font-medium hover:bg-blue-50 transition-colors"
          onClick={(e) => e.stopPropagation()}
        >
          View Dashboard
          <svg width="14" height="14" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
          </svg>
        </a>
      )}

      {/* Output Handle */}
      <Handle 
        type="source" 
        position={Position.Bottom}
        className="w-3 h-3 bg-blue-600 border-2 border-white"
      />
    </div>
  );
}
