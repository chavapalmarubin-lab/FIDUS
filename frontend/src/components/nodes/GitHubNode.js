import React from 'react';
import { Handle, Position } from 'reactflow';

/**
 * GitHubNode - Special custom node for GitHub (Central Hub)
 * Gold gradient, larger size, deployment status lights
 */
function GitHubNode({ data }) {
  const component = data.component || {};
  const health = data.health || {};
  
  const status = health.status || component.status || 'documented';

  // Mock deployment statuses
  const deployments = [
    { name: 'Frontend', status: 'success', time: '2h ago' },
    { name: 'Backend', status: 'success', time: '3h ago' },
    { name: 'Registry', status: 'success', time: '5h ago' },
  ];

  return (
    <div className="
      bg-gradient-to-br from-yellow-500 to-yellow-400
      rounded-2xl shadow-2xl hover:shadow-3xl
      border-4 border-yellow-600
      p-6 min-w-[350px] transition-all duration-200
      hover:scale-105 cursor-pointer
      relative
    ">
      {/* Special Badge */}
      <div className="absolute -top-3 -right-3 bg-yellow-600 text-white text-xs font-bold px-3 py-1 rounded-full shadow-lg">
        SOURCE OF TRUTH
      </div>

      {/* Input/Output Handles - Multiple for central hub */}
      <Handle 
        type="target" 
        position={Position.Top}
        className="w-4 h-4 bg-yellow-600 border-2 border-white"
        id="top"
      />
      <Handle 
        type="source" 
        position={Position.Left}
        className="w-4 h-4 bg-yellow-600 border-2 border-white"
        id="left"
      />
      <Handle 
        type="source" 
        position={Position.Right}
        className="w-4 h-4 bg-yellow-600 border-2 border-white"
        id="right"
      />
      <Handle 
        type="source" 
        position={Position.Bottom}
        className="w-4 h-4 bg-yellow-600 border-2 border-white"
        id="bottom"
      />
      
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <svg className="text-white" width="32" height="32" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
          </svg>
          <div>
            <h3 className="text-white font-bold text-lg">{component.name}</h3>
            <p className="text-white/80 text-xs">Main Branch • Last push: 2h ago</p>
          </div>
        </div>
        <div className="w-4 h-4 rounded-full bg-green-400 animate-pulse" />
      </div>

      {/* Deployment Status Lights */}
      <div className="space-y-2 mb-4">
        <div className="text-white text-xs font-semibold mb-2">Deployment Status:</div>
        {deployments.map((deploy, i) => (
          <div key={i} className="flex items-center justify-between bg-white/10 rounded-lg px-3 py-2">
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${
                deploy.status === 'success' ? 'bg-green-400' :
                deploy.status === 'pending' ? 'bg-yellow-400 animate-pulse' :
                'bg-red-400'
              }`} />
              <span className="text-white text-sm">{deploy.name}</span>
            </div>
            <span className="text-white/70 text-xs">{deploy.time}</span>
          </div>
        ))}
      </div>

      {/* Repository Info */}
      {component.repository_structure && (
        <div className="text-white text-sm mb-4">
          <div className="flex items-center gap-2 text-xs">
            <svg width="14" height="14" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
            </svg>
            <span>{Object.keys(component.repository_structure).length} directories</span>
          </div>
        </div>
      )}

      {/* Action Button */}
      {component.url && (
        <a
          href={component.url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center justify-center gap-2 bg-white text-yellow-600 rounded-lg px-4 py-2 text-sm font-bold hover:bg-yellow-50 transition-colors"
          onClick={(e) => e.stopPropagation()}
        >
          View Repository
          <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
          </svg>
        </a>
      )}
    </div>
  );


// Memoize component for performance
export default React.memo(GitHubNode);
