import React, { useState, useEffect } from 'react';
import ComponentCard from './ComponentCard';
import ArchitectureDiagram from './ArchitectureDiagram';
import CredentialsVault from './CredentialsVault';
import ApiDocumentation from './ApiDocumentation';
import SystemHealthDashboard from './SystemHealthDashboard';
import QuickActionsPanel from './QuickActionsPanel';

/**
 * TechnicalDocumentation - Interactive Technical Command Center
 * Phase 1: Component Registry and Live Health Monitoring
 * Phase 2: Interactive Architecture Diagram
 * Phase 3: Secure Credentials Vault
 * Phase 4: API Documentation & Testing Interface ✅
 * Phase 5: Real-time System Health Dashboard ✅
 */
export default function TechnicalDocumentation() {
  const [components, setComponents] = useState({});
  const [healthData, setHealthData] = useState({});
  const [connections, setConnections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [overallStatus, setOverallStatus] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [viewMode, setViewMode] = useState('diagram'); // 'grid', 'diagram', or 'credentials'

  const backendUrl = process.env.REACT_APP_BACKEND_URL || '';

  // Fetch components and health data
  const fetchData = async () => {
    try {
      setError(null);
      
      // Fetch components
      const componentsResponse = await fetch(`${backendUrl}/api/system/components`);
      if (!componentsResponse.ok) {
        throw new Error(`Failed to fetch components: ${componentsResponse.status}`);
      }
      const componentsData = await componentsResponse.json();
      
      // Fetch health status
      const statusResponse = await fetch(`${backendUrl}/api/system/status`);
      if (!statusResponse.ok) {
        throw new Error(`Failed to fetch status: ${statusResponse.status}`);
      }
      const statusData = await statusResponse.json();
      
      // Fetch connections
      const connectionsResponse = await fetch(`${backendUrl}/api/system/connections`);
      if (connectionsResponse.ok) {
        const connectionsData = await connectionsResponse.json();
        setConnections(connectionsData.connections || []);
      }
      
      setComponents(componentsData.components);
      setHealthData(statusData.components);
      setOverallStatus(statusData.overall_status);
      setLastUpdated(new Date());
      setLoading(false);
      
    } catch (err) {
      console.error('Error fetching system data:', err);
      setError(err.message);
      setLoading(false);
    }
  };

  // Initial fetch
  useEffect(() => {
    fetchData();
  }, []);

  // Auto-refresh every 30 seconds
  useEffect(() => {
    if (!autoRefresh) return;
    
    const interval = setInterval(() => {
      fetchData();
    }, 30000); // 30 seconds

    return () => clearInterval(interval);
  }, [autoRefresh]);

  // Get all components as a flat array
  const getAllComponents = () => {
    const allComponents = [];
    Object.entries(components).forEach(([category, items]) => {
      items.forEach(component => {
        allComponents.push({
          ...component,
          categoryName: category
        });
      });
    });
    return allComponents;
  };

  // Filter components by category
  const getFilteredComponents = () => {
    if (selectedCategory === 'all') {
      return getAllComponents();
    }
    return components[selectedCategory] || [];
  };

  // Get category counts
  const getCategoryCounts = () => {
    const counts = { all: 0 };
    Object.entries(components).forEach(([category, items]) => {
      counts[category] = items.length;
      counts.all += items.length;
    });
    return counts;
  };

  // Overall status display
  const getOverallStatusDisplay = () => {
    if (!overallStatus) return { text: 'Loading...', color: 'gray' };
    
    const statusMap = {
      'all_systems_operational': { 
        text: 'All Systems Operational', 
        color: 'green',
        bgColor: 'bg-green-50',
        textColor: 'text-green-700',
        borderColor: 'border-green-200'
      },
      'degraded_performance': { 
        text: 'Degraded Performance', 
        color: 'yellow',
        bgColor: 'bg-yellow-50',
        textColor: 'text-yellow-700',
        borderColor: 'border-yellow-200'
      },
      'partial_outage': { 
        text: 'Partial Outage', 
        color: 'red',
        bgColor: 'bg-red-50',
        textColor: 'text-red-700',
        borderColor: 'border-red-200'
      },
      'unknown': { 
        text: 'Status Unknown', 
        color: 'gray',
        bgColor: 'bg-gray-50',
        textColor: 'text-gray-700',
        borderColor: 'border-gray-200'
      }
    };
    
    return statusMap[overallStatus] || statusMap.unknown;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading system components...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="max-w-md w-full bg-white border border-red-200 rounded-lg p-6 shadow-sm">
          <div className="flex items-center mb-4">
            <svg className="w-6 h-6 text-red-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h2 className="text-lg font-bold text-gray-900">Error Loading System Data</h2>
          </div>
          <p className="text-sm text-gray-600 mb-4">{error}</p>
          <button
            onClick={fetchData}
            className="w-full bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors text-sm font-medium"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  const filteredComponents = getFilteredComponents();
  const categoryCounts = getCategoryCounts();
  const statusDisplay = getOverallStatusDisplay();

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Technical Documentation
          </h1>
          <p className="text-gray-600">
            Interactive system architecture and health monitoring
          </p>
        </div>

        {/* Overall Status Banner */}
        <div className={`mb-6 p-4 rounded-lg border ${statusDisplay.bgColor} ${statusDisplay.borderColor}`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className={`w-3 h-3 rounded-full bg-${statusDisplay.color}-500 animate-pulse mr-3`}></div>
              <div>
                <h2 className={`text-lg font-bold ${statusDisplay.textColor}`}>
                  {statusDisplay.text}
                </h2>
                <p className="text-sm text-gray-600 mt-0.5">
                  {lastUpdated && `Last updated: ${lastUpdated.toLocaleTimeString()}`}
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              {/* Auto-refresh toggle */}
              <label className="flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={autoRefresh}
                  onChange={(e) => setAutoRefresh(e.target.checked)}
                  className="sr-only"
                />
                <div className={`relative w-10 h-6 rounded-full transition-colors ${autoRefresh ? 'bg-blue-600' : 'bg-gray-300'}`}>
                  <div className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full transition-transform ${autoRefresh ? 'transform translate-x-4' : ''}`}></div>
                </div>
                <span className="ml-2 text-sm text-gray-700">Auto-refresh</span>
              </label>
              
              {/* Refresh button */}
              <button
                onClick={fetchData}
                className="p-2 text-gray-600 hover:text-gray-900 hover:bg-white rounded-md transition-colors"
                title="Refresh now"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
              </button>
            </div>
          </div>
        </div>

        {/* View Toggle */}
        <div className="mb-6 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setViewMode('diagram')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center ${
                viewMode === 'diagram'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-200'
              }`}
            >
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
              </svg>
              Architecture Diagram
            </button>
            <button
              onClick={() => setViewMode('credentials')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center ${
                viewMode === 'credentials'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-200'
              }`}
            >
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
              Credentials Vault
            </button>
            <button
              onClick={() => setViewMode('health')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center ${
                viewMode === 'health'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-200'
              }`}
            >
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              System Health
            </button>
            <button
              onClick={() => setViewMode('api')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center ${
                viewMode === 'api'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-200'
              }`}
            >
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
              </svg>
              API Documentation
            </button>
            <button
              onClick={() => setViewMode('grid')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center ${
                viewMode === 'grid'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-200'
              }`}
            >
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
              </svg>
              Grid View
            </button>
          </div>
        </div>

        {/* Conditional View Rendering */}
        {viewMode === 'health' ? (
          /* System Health Dashboard View */
          <SystemHealthDashboard />
        ) : viewMode === 'api' ? (
          /* API Documentation View */
          <ApiDocumentation />
        ) : viewMode === 'diagram' ? (
          /* Architecture Diagram View */
          <ArchitectureDiagram 
            components={components}
            healthData={healthData}
            connections={connections}
          />
        ) : viewMode === 'credentials' ? (
          /* Credentials Vault View */
          <CredentialsVault />
        ) : (
          /* Grid View */
          <>
            {/* Category Filter */}
            <div className="mb-6 flex flex-wrap gap-2">
              <button
                onClick={() => setSelectedCategory('all')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  selectedCategory === 'all'
                    ? 'bg-blue-600 text-white'
                    : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-200'
                }`}
              >
                All Components ({categoryCounts.all || 0})
              </button>
              
              {Object.keys(components).map((category) => (
                <button
                  key={category}
                  onClick={() => setSelectedCategory(category)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors capitalize ${
                    selectedCategory === category
                      ? 'bg-blue-600 text-white'
                      : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-200'
                  }`}
                >
                  {category} ({categoryCounts[category] || 0})
                </button>
              ))}
            </div>

            {/* Components Grid */}
            {filteredComponents.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredComponents.map((component) => (
                  <ComponentCard
                    key={component.id}
                    component={component}
                    health={healthData[component.id]}
                  />
                ))}
              </div>
            ) : (
              <div className="text-center py-12 bg-white border border-gray-200 rounded-lg">
                <p className="text-gray-500">No components found in this category</p>
              </div>
            )}
          </>
        )}

        {/* Footer Info */}
        <div className="mt-8 text-center text-sm text-gray-500">
          <p>Phase 1 & 2: Component Registry • Live Health Monitoring • Interactive Architecture Diagram</p>
          <p className="mt-1">Credentials Vault • API Documentation • Enhanced Monitoring coming in Phase 3-7</p>
        </div>
      </div>
    </div>
  );
}
