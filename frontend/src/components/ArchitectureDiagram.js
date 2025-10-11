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

  // Initialize nodes from components data
  useEffect(() => {
    if (!components || Object.keys(components).length === 0) return;

    const initialNodes = [];
    let yOffset = 0;
    
    // Define positions for each category (manual layout for now)
    const positions = {
      // GitHub at the top center
      github: { x: 600, y: 50 },
      
      // Applications layer
      frontend: { x: 300, y: 200 },
      backend: { x: 600, y: 200 },
      
      // Databases
      mongodb: { x: 600, y: 350 },
      
      // Services
      vps: { x: 900, y: 200 },
      mt5_bridge: { x: 1050, y: 350 },
      mt5_terminal: { x: 1050, y: 500 },
      
      // Infrastructure
      load_balancer: { x: 300, y: 500 },
      cdn: { x: 150, y: 500 },
      
      // Integrations (bottom row)
      google_workspace: { x: 200, y: 700 },
      email_service: { x: 400, y: 700 },
    };

    // Flatten all components from categories
    Object.entries(components).forEach(([category, categoryComponents]) => {
      categoryComponents.forEach((component) => {
        const health = healthData?.[component.id] || {};
        const position = positions[component.id] || { 
          x: Math.random() * 800 + 100, 
          y: yOffset 
        };
        
        yOffset += 150;

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
  }, [components, healthData]);

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

  return (
    <div className="relative w-full h-[800px] bg-gray-50 rounded-lg border border-gray-200 overflow-hidden">
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
          animated: true,
          style: { strokeWidth: 2 }
        }}
      >
        <Background 
          color="#9CA3AF" 
          gap={16} 
          size={1}
          variant="dots"
        />
        <Controls 
          showInteractive={false}
          className="bg-white border border-gray-200 rounded-lg shadow-sm"
        />
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
      </ReactFlow>

      {/* Selected Node Details Panel (will be enhanced in later steps) */}
      {selectedNode && (
        <div className="absolute top-0 right-0 w-96 h-full bg-white border-l border-gray-200 shadow-xl overflow-y-auto">
          <div className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold text-gray-900">
                {selectedNode.name}
              </h3>
              <button
                onClick={() => setSelectedNode(null)}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <p className="text-sm text-gray-500 mb-1">Type</p>
                <p className="text-base font-medium text-gray-900">{selectedNode.type}</p>
              </div>

              <div>
                <p className="text-sm text-gray-500 mb-1">Platform</p>
                <p className="text-base font-medium text-gray-900">{selectedNode.platform}</p>
              </div>

              <div>
                <p className="text-sm text-gray-500 mb-1">Description</p>
                <p className="text-sm text-gray-700">{selectedNode.description}</p>
              </div>

              {selectedNode.url && (
                <div>
                  <a
                    href={selectedNode.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center text-blue-600 hover:text-blue-800 text-sm font-medium"
                  >
                    View Component
                    <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                  </a>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
