import React, { useState, useEffect } from 'react';
import { Search, ChevronDown, ChevronRight, Play, Copy, Check, AlertCircle, Code } from 'lucide-react';

const ApiDocumentation = () => {
  const [apiData, setApiData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedCategories, setExpandedCategories] = useState({});
  const [expandedEndpoints, setExpandedEndpoints] = useState({});
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedEndpoint, setSelectedEndpoint] = useState(null);
  const [showTryIt, setShowTryIt] = useState(false);
  const [tryItParams, setTryItParams] = useState({});
  const [tryItBody, setTryItBody] = useState('');
  const [tryItResponse, setTryItResponse] = useState(null);
  const [tryItLoading, setTryItLoading] = useState(false);
  const [copiedCode, setCopiedCode] = useState(null);

  const backendUrl = process.env.REACT_APP_BACKEND_URL || '';

  useEffect(() => {
    loadApiDocumentation();
  }, []);

  const loadApiDocumentation = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${backendUrl}/api/system/api-docs`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to load API documentation');
      }

      const data = await response.json();
      setApiData(data.documentation);
      setError(null);
    } catch (err) {
      console.error('Error loading API documentation:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const toggleCategory = (categoryId) => {
    setExpandedCategories(prev => ({
      ...prev,
      [categoryId]: !prev[categoryId]
    }));
  };

  const toggleEndpoint = (endpointId) => {
    setExpandedEndpoints(prev => ({
      ...prev,
      [endpointId]: !prev[endpointId]
    }));
  };

  const getMethodColor = (method) => {
    const colors = {
      'GET': 'bg-blue-100 text-blue-800 border-blue-300',
      'POST': 'bg-green-100 text-green-800 border-green-300',
      'PUT': 'bg-yellow-100 text-yellow-800 border-yellow-300',
      'DELETE': 'bg-red-100 text-red-800 border-red-300',
      'PATCH': 'bg-purple-100 text-purple-800 border-purple-300'
    };
    return colors[method] || 'bg-gray-100 text-gray-800 border-gray-300';
  };

  const getAuthBadge = (auth) => {
    if (auth === 'None (public)') {
      return <span className="px-2 py-1 text-xs rounded-full bg-green-100 text-green-800">Public</span>;
    } else if (auth.includes('Admin')) {
      return <span className="px-2 py-1 text-xs rounded-full bg-purple-100 text-purple-800">Admin Only</span>;
    } else {
      return <span className="px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800">Authenticated</span>;
    }
  };

  const generateCodeExample = (endpoint, language) => {
    const baseUrl = backendUrl || 'https://fidus-invest.emergent.host/api';
    const fullUrl = `${baseUrl}${endpoint.path}`;
    const needsAuth = !endpoint.authentication.includes('None');
    
    const requestBodyExample = endpoint.request_body?.schema 
      ? JSON.stringify(
          Object.keys(endpoint.request_body.schema).reduce((acc, key) => {
            acc[key] = endpoint.request_body.schema[key].example || `<${endpoint.request_body.schema[key].type}>`;
            return acc;
          }, {}),
          null,
          2
        )
      : null;

    if (language === 'javascript') {
      return `// JavaScript (Fetch API)
const response = await fetch('${fullUrl}', {
  method: '${endpoint.method}',${needsAuth ? `
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN_HERE',
    'Content-Type': 'application/json'
  },` : ''}${requestBodyExample ? `
  body: JSON.stringify(${requestBodyExample})` : ''}
});

const data = await response.json();
console.log(data);`;
    } else if (language === 'python') {
      return `# Python (requests library)
import requests

response = requests.${endpoint.method.toLowerCase()}(
    '${fullUrl}',${needsAuth ? `
    headers={
        'Authorization': 'Bearer YOUR_TOKEN_HERE',
        'Content-Type': 'application/json'
    },` : ''}${requestBodyExample ? `
    json=${requestBodyExample}` : ''}
)

data = response.json()
print(data)`;
    } else if (language === 'curl') {
      return `# cURL
curl -X ${endpoint.method} '${fullUrl}' \\${needsAuth ? `
  -H 'Authorization: Bearer YOUR_TOKEN_HERE' \\
  -H 'Content-Type: application/json' \\` : ''}${requestBodyExample ? `
  -d '${requestBodyExample.replace(/\n/g, ' ').replace(/\s+/g, ' ')}'` : ''}`;
    }
  };

  const copyToClipboard = (text, id) => {
    navigator.clipboard.writeText(text);
    setCopiedCode(id);
    setTimeout(() => setCopiedCode(null), 2000);
  };

  const tryEndpoint = async () => {
    setTryItLoading(true);
    setTryItResponse(null);

    try {
      const token = localStorage.getItem('token');
      const needsAuth = !selectedEndpoint.authentication.includes('None');

      // Build URL with query parameters
      let url = `${backendUrl}${selectedEndpoint.path}`;
      const queryParams = Object.entries(tryItParams)
        .filter(([_, value]) => value)
        .map(([key, value]) => `${key}=${encodeURIComponent(value)}`)
        .join('&');
      if (queryParams) {
        url += `?${queryParams}`;
      }

      const options = {
        method: selectedEndpoint.method,
        headers: {
          'Content-Type': 'application/json'
        }
      };

      if (needsAuth && token) {
        options.headers['Authorization'] = `Bearer ${token}`;
      }

      if (selectedEndpoint.method !== 'GET' && tryItBody) {
        options.body = tryItBody;
      }

      const response = await fetch(url, options);
      const data = await response.json();

      setTryItResponse({
        status: response.status,
        statusText: response.statusText,
        data: data
      });
    } catch (err) {
      setTryItResponse({
        status: 0,
        statusText: 'Error',
        data: { error: err.message }
      });
    } finally {
      setTryItLoading(false);
    }
  };

  const filteredCategories = apiData?.categories.filter(category => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      category.name.toLowerCase().includes(query) ||
      category.description.toLowerCase().includes(query) ||
      category.endpoints.some(endpoint =>
        endpoint.path.toLowerCase().includes(query) ||
        endpoint.summary.toLowerCase().includes(query) ||
        endpoint.description.toLowerCase().includes(query)
      )
    );
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading API Documentation...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="flex items-center space-x-2 text-red-800">
          <AlertCircle className="w-5 h-5" />
          <p className="font-semibold">Error loading API documentation</p>
        </div>
        <p className="mt-2 text-red-700">{error}</p>
        <button
          onClick={loadApiDocumentation}
          className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg p-6">
        <h1 className="text-3xl font-bold mb-2">FIDUS API Documentation</h1>
        <p className="text-blue-100">
          Complete API reference with {apiData?.categories.length} categories and{' '}
          {apiData?.categories.reduce((sum, cat) => sum + cat.endpoints.length, 0)} endpoints
        </p>
      </div>

      {/* Search Bar */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            placeholder="Search endpoints, methods, descriptions..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
      </div>

      {/* API Categories */}
      <div className="space-y-4">
        {filteredCategories?.map((category) => (
          <div key={category.id} className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
            {/* Category Header */}
            <button
              onClick={() => toggleCategory(category.id)}
              className="w-full px-6 py-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
              style={{ borderLeft: `4px solid ${category.color}` }}
            >
              <div className="flex items-center space-x-3">
                <span className="text-2xl">{category.icon}</span>
                <div className="text-left">
                  <h3 className="text-lg font-semibold text-gray-900">{category.name}</h3>
                  <p className="text-sm text-gray-600">{category.description}</p>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <span className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm font-medium">
                  {category.endpoints.length} endpoints
                </span>
                {expandedCategories[category.id] ? (
                  <ChevronDown className="w-5 h-5 text-gray-400" />
                ) : (
                  <ChevronRight className="w-5 h-5 text-gray-400" />
                )}
              </div>
            </button>

            {/* Category Endpoints */}
            {expandedCategories[category.id] && (
              <div className="border-t border-gray-200">
                {category.endpoints.map((endpoint) => (
                  <div key={endpoint.id} className="border-b border-gray-100 last:border-b-0">
                    {/* Endpoint Header */}
                    <button
                      onClick={() => toggleEndpoint(endpoint.id)}
                      className="w-full px-6 py-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
                    >
                      <div className="flex items-center space-x-4 flex-1">
                        <span className={`px-3 py-1 rounded text-xs font-bold border ${getMethodColor(endpoint.method)}`}>
                          {endpoint.method}
                        </span>
                        <code className="text-sm font-mono text-gray-700">{endpoint.path}</code>
                        <span className="text-sm text-gray-900 font-medium">{endpoint.summary}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        {getAuthBadge(endpoint.authentication)}
                        {expandedEndpoints[endpoint.id] ? (
                          <ChevronDown className="w-4 h-4 text-gray-400" />
                        ) : (
                          <ChevronRight className="w-4 h-4 text-gray-400" />
                        )}
                      </div>
                    </button>

                    {/* Endpoint Details */}
                    {expandedEndpoints[endpoint.id] && (
                      <div className="px-6 pb-6 space-y-6 bg-gray-50">
                        {/* Description */}
                        <div>
                          <p className="text-gray-700">{endpoint.description}</p>
                        </div>

                        {/* Authentication */}
                        <div>
                          <h4 className="text-sm font-semibold text-gray-900 mb-2">Authentication</h4>
                          <p className="text-sm text-gray-700 bg-white px-3 py-2 rounded border border-gray-200">
                            {endpoint.authentication}
                          </p>
                        </div>

                        {/* Parameters */}
                        {endpoint.parameters && endpoint.parameters.length > 0 && (
                          <div>
                            <h4 className="text-sm font-semibold text-gray-900 mb-2">Parameters</h4>
                            <div className="bg-white rounded border border-gray-200 overflow-hidden">
                              <table className="w-full text-sm">
                                <thead className="bg-gray-100">
                                  <tr>
                                    <th className="px-4 py-2 text-left font-medium text-gray-700">Name</th>
                                    <th className="px-4 py-2 text-left font-medium text-gray-700">Type</th>
                                    <th className="px-4 py-2 text-left font-medium text-gray-700">Required</th>
                                    <th className="px-4 py-2 text-left font-medium text-gray-700">Description</th>
                                  </tr>
                                </thead>
                                <tbody>
                                  {endpoint.parameters.map((param, idx) => (
                                    <tr key={idx} className="border-t border-gray-100">
                                      <td className="px-4 py-2 font-mono text-xs">{param.name}</td>
                                      <td className="px-4 py-2 text-gray-600">{param.type}</td>
                                      <td className="px-4 py-2">
                                        {param.required ? (
                                          <span className="text-red-600 font-medium">Yes</span>
                                        ) : (
                                          <span className="text-gray-500">No</span>
                                        )}
                                      </td>
                                      <td className="px-4 py-2 text-gray-700">{param.description}</td>
                                    </tr>
                                  ))}
                                </tbody>
                              </table>
                            </div>
                          </div>
                        )}

                        {/* Request Body */}
                        {endpoint.request_body && (
                          <div>
                            <h4 className="text-sm font-semibold text-gray-900 mb-2">Request Body</h4>
                            <div className="bg-gray-900 rounded-lg p-4 overflow-x-auto">
                              <pre className="text-xs text-gray-100 font-mono">
                                {JSON.stringify(
                                  Object.keys(endpoint.request_body.schema).reduce((acc, key) => {
                                    acc[key] = endpoint.request_body.schema[key].example || `<${endpoint.request_body.schema[key].type}>`;
                                    return acc;
                                  }, {}),
                                  null,
                                  2
                                )}
                              </pre>
                            </div>
                          </div>
                        )}

                        {/* Responses */}
                        {endpoint.responses && (
                          <div>
                            <h4 className="text-sm font-semibold text-gray-900 mb-2">Responses</h4>
                            <div className="space-y-3">
                              {Object.entries(endpoint.responses).map(([code, response]) => (
                                <div key={code} className="bg-white rounded border border-gray-200 p-4">
                                  <div className="flex items-center space-x-2 mb-2">
                                    <span className={`px-2 py-1 rounded text-xs font-bold ${
                                      code.startsWith('2') ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                                    }`}>
                                      {code}
                                    </span>
                                    <span className="text-sm text-gray-700">{response.description}</span>
                                  </div>
                                  {response.example && (
                                    <div className="bg-gray-900 rounded p-3 overflow-x-auto mt-2">
                                      <pre className="text-xs text-gray-100 font-mono">
                                        {JSON.stringify(response.example, null, 2)}
                                      </pre>
                                    </div>
                                  )}
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Code Examples */}
                        <div>
                          <h4 className="text-sm font-semibold text-gray-900 mb-2">Code Examples</h4>
                          <div className="space-y-3">
                            {['javascript', 'python', 'curl'].map((lang) => (
                              <div key={lang} className="bg-gray-900 rounded-lg overflow-hidden">
                                <div className="flex items-center justify-between px-4 py-2 bg-gray-800">
                                  <span className="text-xs font-medium text-gray-300 uppercase">{lang}</span>
                                  <button
                                    onClick={() => copyToClipboard(generateCodeExample(endpoint, lang), `${endpoint.id}-${lang}`)}
                                    className="text-gray-400 hover:text-white transition-colors"
                                  >
                                    {copiedCode === `${endpoint.id}-${lang}` ? (
                                      <Check className="w-4 h-4" />
                                    ) : (
                                      <Copy className="w-4 h-4" />
                                    )}
                                  </button>
                                </div>
                                <div className="p-4 overflow-x-auto">
                                  <pre className="text-xs text-gray-100 font-mono whitespace-pre">
                                    {generateCodeExample(endpoint, lang)}
                                  </pre>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>

                        {/* Try It Button */}
                        <div>
                          <button
                            onClick={() => {
                              setSelectedEndpoint(endpoint);
                              setShowTryIt(true);
                              setTryItParams({});
                              setTryItBody('');
                              setTryItResponse(null);
                            }}
                            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                          >
                            <Play className="w-4 h-4" />
                            <span>Try It Out</span>
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Try It Modal */}
      {showTryIt && selectedEndpoint && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Try API Endpoint</h3>
                <div className="flex items-center space-x-2 mt-1">
                  <span className={`px-2 py-1 rounded text-xs font-bold ${getMethodColor(selectedEndpoint.method)}`}>
                    {selectedEndpoint.method}
                  </span>
                  <code className="text-sm font-mono text-gray-700">{selectedEndpoint.path}</code>
                </div>
              </div>
              <button
                onClick={() => setShowTryIt(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>

            <div className="p-6 space-y-4">
              {/* Parameters Input */}
              {selectedEndpoint.parameters && selectedEndpoint.parameters.length > 0 && (
                <div>
                  <h4 className="text-sm font-semibold text-gray-900 mb-2">Parameters</h4>
                  <div className="space-y-2">
                    {selectedEndpoint.parameters.map((param) => (
                      <div key={param.name}>
                        <label className="block text-sm text-gray-700 mb-1">
                          {param.name} {param.required && <span className="text-red-600">*</span>}
                        </label>
                        <input
                          type="text"
                          placeholder={param.description}
                          value={tryItParams[param.name] || ''}
                          onChange={(e) => setTryItParams({ ...tryItParams, [param.name]: e.target.value })}
                          className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Request Body Input */}
              {selectedEndpoint.request_body && (
                <div>
                  <h4 className="text-sm font-semibold text-gray-900 mb-2">Request Body (JSON)</h4>
                  <textarea
                    value={tryItBody}
                    onChange={(e) => setTryItBody(e.target.value)}
                    placeholder={JSON.stringify(
                      Object.keys(selectedEndpoint.request_body.schema).reduce((acc, key) => {
                        acc[key] = selectedEndpoint.request_body.schema[key].example || `<${selectedEndpoint.request_body.schema[key].type}>`;
                        return acc;
                      }, {}),
                      null,
                      2
                    )}
                    rows={8}
                    className="w-full px-3 py-2 border border-gray-300 rounded font-mono text-sm focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              )}

              {/* Execute Button */}
              <button
                onClick={tryEndpoint}
                disabled={tryItLoading}
                className="w-full px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
              >
                {tryItLoading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                    <span>Executing...</span>
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4" />
                    <span>Execute Request</span>
                  </>
                )}
              </button>

              {/* Response */}
              {tryItResponse && (
                <div>
                  <h4 className="text-sm font-semibold text-gray-900 mb-2">Response</h4>
                  <div className="bg-gray-900 rounded-lg overflow-hidden">
                    <div className="px-4 py-2 bg-gray-800 flex items-center justify-between">
                      <span className={`px-2 py-1 rounded text-xs font-bold ${
                        tryItResponse.status >= 200 && tryItResponse.status < 300
                          ? 'bg-green-100 text-green-800'
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {tryItResponse.status} {tryItResponse.statusText}
                      </span>
                    </div>
                    <div className="p-4 overflow-x-auto">
                      <pre className="text-xs text-gray-100 font-mono">
                        {JSON.stringify(tryItResponse.data, null, 2)}
                      </pre>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ApiDocumentation;
