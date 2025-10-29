import React, { useState, useEffect, Suspense, lazy } from 'react';
import ComponentCard from './ComponentCard';
import Button from './ui/Button';
import LoadingSpinner from './ui/LoadingSpinner';
import Badge from './ui/Badge';
import { COLORS, SPACING, TYPOGRAPHY } from '../constants/styles';
import ReactMarkdown from 'react-markdown';

// Lazy load heavy components for better performance (Phase 7)
const ArchitectureDiagram = lazy(() => import('./ArchitectureDiagram'));
const CredentialsVault = lazy(() => import('./CredentialsVault'));
const ApiDocumentation = lazy(() => import('./ApiDocumentation'));
const SystemHealthDashboard = lazy(() => import('./SystemHealthDashboard'));
const QuickActionsPanel = lazy(() => import('./QuickActionsPanel'));
const QuickActionsButtons = lazy(() => import('./QuickActionsButtons'));

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
  const [viewMode, setViewMode] = useState('diagram'); // 'grid', 'diagram', 'credentials', 'documentation'
  const [documentation, setDocumentation] = useState('');
  const [loadingDocs, setLoadingDocs] = useState(false);
  const [docsError, setDocsError] = useState(null);

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

  // Fetch documentation when tab is active
  useEffect(() => {
    if (viewMode === 'documentation' && !documentation) {
      setLoadingDocs(true);
      setDocsError(null);
      
      // Try to fetch from local file first (for development)
      fetch('/docs/TECHNICAL_DOCUMENTATION.md')
        .then(res => {
          if (!res.ok) {
            // If local file not found, try GitHub
            // User can update this URL with their GitHub repo
            throw new Error('Local file not found, using fallback');
          }
          return res.text();
        })
        .then(text => {
          setDocumentation(text);
          setLoadingDocs(false);
        })
        .catch(err => {
          console.log('Using embedded documentation');
          // Fallback to embedded documentation
          fetch(`${backendUrl}/api/system/documentation`)
            .then(res => {
              if (!res.ok) {
                throw new Error('Documentation not available');
              }
              return res.text();
            })
            .then(text => {
              setDocumentation(text);
              setLoadingDocs(false);
            })
            .catch(finalErr => {
              console.error('Error loading documentation:', finalErr);
              setDocsError('Documentation could not be loaded. Please check the configuration.');
              setLoadingDocs(false);
            });
        });
    }
  }, [viewMode, documentation, backendUrl]);

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
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner size="lg" text="Loading system components..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="max-w-md w-full bg-slate-800/80 border border-red-500/30 rounded-lg p-6 shadow-lg backdrop-blur-sm">
          <div className="flex items-center mb-4">
            <svg className="w-6 h-6 text-red-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h2 className="text-lg font-bold text-white">Error Loading System Data</h2>
          </div>
          <p className="text-sm text-slate-400 mb-4">{error}</p>
          <Button variant="primary" onClick={fetchData} className="w-full">
            Retry
          </Button>
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
              onClick={() => setViewMode('actions')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center ${
                viewMode === 'actions'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-200'
              }`}
            >
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              Quick Actions
            </button>
            <button
              onClick={() => setViewMode('mt5-actions')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center ${
                viewMode === 'mt5-actions'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-200'
              }`}
            >
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
              </svg>
              MT5 Bridge Control
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
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 6v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
              </svg>
              Grid View
            </button>
            <button
              onClick={() => setViewMode('documentation')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center ${
                viewMode === 'documentation'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-200'
              }`}
            >
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Full Documentation
            </button>
          </div>
        </div>

        {/* Conditional View Rendering with Lazy Loading (Phase 7) */}
        <Suspense fallback={<LoadingSpinner size="lg" message="Loading view..." fullPage />}>
          {viewMode === 'mt5-actions' ? (
            /* MT5 Bridge Control Panel */
            <QuickActionsButtons />
          ) : viewMode === 'actions' ? (
            /* Quick Actions Panel View */
            <QuickActionsPanel />
          ) : viewMode === 'health' ? (
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
          ) : viewMode === 'documentation' ? (
            /* Full Documentation View */
            <div className="bg-white border border-gray-200 rounded-lg shadow-sm">
              {loadingDocs ? (
                <div className="p-12 text-center">
                  <LoadingSpinner size="lg" message="Loading documentation..." />
                </div>
              ) : docsError ? (
                <div className="p-12 text-center">
                  <div className="inline-flex items-center justify-center w-16 h-16 bg-red-100 rounded-full mb-4">
                    <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <p className="text-red-600 font-medium mb-2">Error Loading Documentation</p>
                  <p className="text-sm text-gray-600 mb-4">{docsError}</p>
                  <button
                    onClick={() => {
                      setDocumentation('');
                      setDocsError(null);
                    }}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors text-sm font-medium"
                  >
                    Retry
                  </button>
                </div>
              ) : (
                <div className="prose prose-slate max-w-none p-8">
                  <ReactMarkdown>{documentation}</ReactMarkdown>
                </div>
              )}
            </div>
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
        </Suspense>

        {/* Footer Info */}
        <div className="mt-8 text-center text-sm text-gray-500">
          <p>Phase 1-7 Complete ✅ • Component Registry • Live Health Monitoring • Interactive Architecture</p>
          <p className="mt-1">Credentials Vault • API Documentation • System Health Dashboard • Quick Actions ⚡ • Optimized Performance 🚀</p>
        </div>
      </div>
    </div>
  );
}
