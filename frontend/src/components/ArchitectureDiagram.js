import React, { useState, useEffect, useCallback } from 'react';
import ReactFlow, {
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  MarkerType,
} from 'reactflow';
import 'reactflow/dist/style.css';

// Import custom node components
import ApplicationNode from './nodes/ApplicationNode';
import DatabaseNode from './nodes/DatabaseNode';
import ServiceNode from './nodes/ServiceNode';
import IntegrationNode from './nodes/IntegrationNode';
import InfrastructureNode from './nodes/InfrastructureNode';
import GitHubNode from './nodes/GitHubNode';
import ComponentDetailsPanel from './ComponentDetailsPanel';
import DiagramSettings from './DiagramSettings';

// Define custom node types
const nodeTypes = {
  application: ApplicationNode,
  database: DatabaseNode,
  service: ServiceNode,
  integration: IntegrationNode,
  infrastructure: InfrastructureNode,
  github: GitHubNode,
};

/**
 * ArchitectureDiagram - Interactive System Architecture Visualization
 * Phase 2: Visual diagram with draggable nodes, zoom controls, and real-time status
 */
export default function ArchitectureDiagram({ components, healthData, connections }) {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [selectedNode, setSelectedNode] = useState(null);
  const [showSettings, setShowSettings] = useState(false);
  const [viewMode, setViewMode] = useState('simple'); // 'simple' or 'detailed'
  const [diagramSettings, setDiagramSettings] = useState(() => {
    const saved = localStorage.getItem('fidus_diagram_settings');
    return saved ? JSON.parse(saved) : {
      showMiniMap: true,
      showLabels: true,
      showGrid: true,
      enableFlowAnimation: true,
    };
  });

  // Initialize nodes from components data
  useEffect(() => {
    if (!components || Object.keys(components).length === 0) return;

    const initialNodes = [];
    let yOffset = 0;
    
    // Define positions for each category with INCREASED SPACING (Phase 7 fix)
    const positions = {
      // Core components only for simple view
      simple: {
        frontend: { x: 200, y: 200 },
        backend: { x: 600, y: 200 },
        mongodb: { x: 600, y: 450 },
        mt5_bridge: { x: 1000, y: 350 },
        github: { x: 600, y: 50 },
      },
      
      // All components for detailed view - INCREASED SPACING
      detailed: {
        // GitHub at the top center
        github: { x: 700, y: 50 },
        
        // Applications layer - More spacing
        frontend: { x: 250, y: 250 },
        backend: { x: 700, y: 250 },
        
        // Databases - Further down
        mongodb: { x: 700, y: 500 },
        
        // Services - Spread out more
        vps: { x: 1100, y: 250 },
        mt5_bridge: { x: 1300, y: 400 },
        mt5_terminal: { x: 1300, y: 650 },
        
        // Infrastructure - Lower and spread
        load_balancer: { x: 250, y: 700 },
        cdn: { x: 50, y: 700 },
        render_platform: { x: 450, y: 700 },
        
        // Integrations (bottom row) - More spacing
        google_workspace: { x: 200, y: 900 },
        email_service: { x: 500, y: 900 },
        google_apis: { x: 800, y: 900 },
      }
    };
    
    // Get positions based on view mode
    const currentPositions = viewMode === 'simple' ? positions.simple : positions.detailed;

    // Core components for simple view
    const coreComponents = ['frontend', 'backend', 'mongodb', 'mt5_bridge', 'github'];
    
    // Flatten all components from categories
    Object.entries(components).forEach(([category, categoryComponents]) => {
      categoryComponents.forEach((component) => {
        // In simple view, only show core components
        if (viewMode === 'simple' && !coreComponents.includes(component.id)) {
          return; // Skip non-core components
        }
        
        const health = healthData?.[component.id] || {};
        const position = currentPositions[component.id] || { 
          x: Math.random() * 800 + 100, 
          y: yOffset 
        };
        
        yOffset += 200; // Increased from 150 for better spacing

        // Determine node type based on category
        let nodeType = 'default';
        if (category === 'applications') nodeType = 'application';
        else if (category === 'databases') nodeType = 'database';
        else if (category === 'services') nodeType = 'service';
        else if (category === 'integrations') nodeType = 'integration';
        else if (category === 'infrastructure') nodeType = 'infrastructure';

        // Special handling for GitHub
        if (component.id === 'github') nodeType = 'github';

        initialNodes.push({
          id: component.id,
          type: nodeType,
          position: position,
          data: {
            label: component.name,
            component: component,
            health: health,
            onExpand: () => setSelectedNode(component),
          },
          style: getNodeStyle(component.type, health.status || component.status),
        });
      });
    });

    setNodes(initialNodes);
  }, [components, healthData, viewMode]); // Re-render when view mode changes

  // Initialize edges from connections data
  useEffect(() => {
    if (!connections || connections.length === 0) return;

    const initialEdges = connections.map((conn, index) => ({
      id: `edge-${index}`,
      source: conn.from,
      target: conn.to,
      type: 'smoothstep',
      animated: true,
      style: { 
        stroke: getConnectionColor(conn.type),
        strokeWidth: 2,
      },
      markerEnd: {
        type: MarkerType.ArrowClosed,
        color: getConnectionColor(conn.type),
      },
      label: conn.type,
      labelStyle: { 
        fill: '#6B7280', 
        fontSize: 10,
        fontWeight: 500,
      },
      labelBgStyle: { 
        fill: 'white',
        fillOpacity: 0.8,
      },
    }));

    setEdges(initialEdges);
  }, [connections]);

  // Get node style based on type and status
  const getNodeStyle = (type, status) => {
    const baseStyle = {
      padding: 15,
      borderRadius: 8,
      border: '2px solid',
      fontSize: 12,
      fontWeight: 600,
      minWidth: 180,
      textAlign: 'center',
    };

    // Status border colors
    const borderColors = {
      online: '#10B981',
      degraded: '#F59E0B',
      offline: '#EF4444',
      unknown: '#6B7280',
    };

    // Type backgrounds
    const backgrounds = {
      application: 'linear-gradient(135deg, #3B82F6 0%, #60A5FA 100%)',
      database: 'linear-gradient(135deg, #10B981 0%, #34D399 100%)',
      service: 'linear-gradient(135deg, #8B5CF6 0%, #A78BFA 100%)',
      integration: 'linear-gradient(135deg, #F97316 0%, #FB923C 100%)',
      infrastructure: 'linear-gradient(135deg, #6B7280 0%, #9CA3AF 100%)',
      github: 'linear-gradient(135deg, #F59E0B 0%, #FBBF24 100%)',
    };

    return {
      ...baseStyle,
      background: backgrounds[type] || backgrounds.application,
      borderColor: borderColors[status] || borderColors.unknown,
      color: 'white',
      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    };
  };

  // Get connection color based on type
  const getConnectionColor = (type) => {
    const colors = {
      'REST API': '#3B82F6',
      'Database': '#10B981',
      'API Integration': '#F97316',
      'SMTP': '#EF4444',
      'Data Sync': '#8B5CF6',
      'Traffic Distribution': '#6B7280',
      'Deployment': '#F59E0B',
      'Asset Delivery': '#06B6D4',
    };

    return colors[type] || '#9CA3AF';
  };

  // Handle node click
  const onNodeClick = useCallback((event, node) => {
    setSelectedNode(node.data.component);
  }, []);

  // Handle connection (edge creation)
  const onConnect = useCallback(
    (params) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  // Save node positions to localStorage when they change
  useEffect(() => {
    if (nodes.length > 0) {
      const positions = {};
      nodes.forEach(node => {
        positions[node.id] = node.position;
      });
      localStorage.setItem('fidus_node_positions', JSON.stringify(positions));
    }
  }, [nodes]);

  // Load saved positions on mount
  useEffect(() => {
    const savedPositions = localStorage.getItem('fidus_node_positions');
    if (savedPositions && nodes.length > 0) {
      const positions = JSON.parse(savedPositions);
      const updatedNodes = nodes.map(node => ({
        ...node,
        position: positions[node.id] || node.position
      }));
      setNodes(updatedNodes);
    }
  }, []); // Only run once on mount

  // Handle settings save
  const handleSettingsSave = (newSettings) => {
    setDiagramSettings(newSettings);
  };

  return (
    <div className="relative w-full h-[800px] bg-gray-50 rounded-lg border border-gray-200 overflow-hidden">
      {/* Control Buttons */}
      <div className="absolute top-4 right-4 z-10 flex items-center space-x-2">
        {/* View Mode Toggle (Phase 7) */}
        <div className="bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden flex">
          <button
            onClick={() => setViewMode('simple')}
            className={`px-3 py-2 text-sm font-medium transition-colors ${
              viewMode === 'simple'
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-50'
            }`}
            title="Simple View - Core components only"
          >
            Simple
          </button>
          <button
            onClick={() => setViewMode('detailed')}
            className={`px-3 py-2 text-sm font-medium transition-colors border-l ${
              viewMode === 'detailed'
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-50'
            }`}
            title="Detailed View - All components"
          >
            Detailed
          </button>
        </div>
        
        {/* Settings Button */}
        <button
          onClick={() => setShowSettings(true)}
          className="bg-white border border-gray-200 rounded-lg p-2 shadow-sm hover:shadow-md transition-all hover:bg-gray-50"
          title="Diagram Settings"
        >
          <svg className="w-5 h-5 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
        </button>
      </div>

      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeClick={onNodeClick}
        nodeTypes={nodeTypes}
        fitView
        attributionPosition="bottom-right"
        minZoom={0.2}
        maxZoom={2}
        defaultEdgeOptions={{
          animated: diagramSettings.enableFlowAnimation,
          style: { strokeWidth: 2 }
        }}
      >
        {diagramSettings.showGrid && (
          <Background 
            color="#9CA3AF" 
            gap={16} 
            size={1}
            variant="dots"
          />
        )}
        <Controls 
          showInteractive={false}
          className="bg-white border border-gray-200 rounded-lg shadow-sm"
        />
        {diagramSettings.showMiniMap && (
          <MiniMap 
            nodeColor={(node) => {
              const status = node.data?.health?.status || node.data?.component?.status;
              if (status === 'online') return '#10B981';
              if (status === 'degraded') return '#F59E0B';
              if (status === 'offline') return '#EF4444';
              return '#6B7280';
            }}
            maskColor="rgba(0, 0, 0, 0.1)"
            className="bg-white border border-gray-200 rounded-lg shadow-sm"
          />
        )}
      </ReactFlow>

      {/* Enhanced Details Panel */}
      {selectedNode && (
        <ComponentDetailsPanel
          component={selectedNode}
          health={healthData?.[selectedNode.id]}
          onClose={() => setSelectedNode(null)}
        />
      )}

      {/* Settings Modal */}
      <DiagramSettings
        isOpen={showSettings}
        onClose={() => setShowSettings(false)}
        onSave={handleSettingsSave}
      />
    </div>
  );
}
