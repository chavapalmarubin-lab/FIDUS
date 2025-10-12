import React, { useState } from 'react';

/**
 * CredentialCard - Individual credential display card
 * Shows metadata, status, and provides actions (test, view dashboard, etc.)
 */
export default function CredentialCard({ id, credential, onRefresh }) {
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState(null);

  const backendUrl = process.env.REACT_APP_BACKEND_URL || '';

  // Status icon mapping
  const statusIcons = {
    configured: (
      <svg className="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
    partial: (
      <svg className="w-5 h-5 text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
      </svg>
    ),
    missing: (
      <svg className="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
    not_configured: (
      <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    )
  };

  // Type colors for gradient headers
  const typeColors = {
    database: 'from-green-500 to-green-400',
    infrastructure: 'from-purple-500 to-purple-400',
    integration: 'from-orange-500 to-orange-400',
    service: 'from-blue-500 to-blue-400',
    trading: 'from-red-500 to-red-400'
  };

  const handleTest = async () => {
    setTesting(true);
    setTestResult(null);
    
    try {
      const response = await fetch(`${backendUrl}/api/credentials/test/${id}`, {
        method: 'POST'
      });
      
      const result = await response.json();
      setTestResult(result);
      
      // Clear result after 5 seconds
      setTimeout(() => setTestResult(null), 5000);
    } catch (error) {
      console.error('Test failed:', error);
      setTestResult({ 
        success: false, 
        test_result: { test_passed: false, error: error.message }
      });
    } finally {
      setTesting(false);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-lg hover:shadow-2xl transition-all border-2 border-gray-100">
      {/* Header with gradient */}
      <div className={`bg-gradient-to-r ${typeColors[credential.type] || 'from-gray-500 to-gray-400'} p-4 rounded-t-xl`}>
        <div className="flex items-center justify-between">
          <h3 className="text-white font-bold text-lg">{credential.name}</h3>
          {statusIcons[credential.status]}
        </div>
        <p className="text-white text-sm opacity-90 capitalize mt-1">{credential.type}</p>
      </div>

      {/* Body */}
      <div className="p-4 space-y-3">
        {/* Category */}
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600">Category:</span>
          <span className="font-medium text-gray-900">{credential.category}</span>
        </div>

        {/* Storage Type */}
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600">Storage:</span>
          <span className="font-medium text-gray-900 capitalize">{credential.storage.replace('_', ' ')}</span>
        </div>

        {/* Status */}
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600">Status:</span>
          <span className={`font-medium capitalize ${
            credential.status === 'configured' ? 'text-green-600' :
            credential.status === 'partial' ? 'text-yellow-600' :
            credential.status === 'missing' ? 'text-red-600' :
            'text-gray-600'
          }`}>
            {credential.status.replace('_', ' ')}
          </span>
        </div>

        {/* Environment Variables */}
        {credential.env_keys && credential.env_keys.length > 0 && (
          <div className="bg-gray-50 rounded p-3 border border-gray-200">
            <p className="text-xs font-semibold text-gray-700 mb-2">Environment Variables:</p>
            <div className="space-y-1">
              {credential.env_keys.map((key, i) => (
                <div key={i} className="text-xs font-mono bg-white px-2 py-1 rounded border border-gray-200">
                  {key}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Fields */}
        {credential.fields && credential.fields.length > 0 && (
          <div>
            <p className="text-xs font-semibold text-gray-700 mb-2">Fields:</p>
            <div className="flex flex-wrap gap-1">
              {credential.fields.slice(0, 4).map((field, i) => (
                <span key={i} className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">
                  {field}
                </span>
              ))}
              {credential.fields.length > 4 && (
                <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
                  +{credential.fields.length - 4} more
                </span>
              )}
            </div>
          </div>
        )}

        {/* Last Rotated */}
        {credential.last_rotated !== undefined && (
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>Last rotated: {credential.last_rotated || 'Never'}</span>
          </div>
        )}

        {/* Rotation Recommendation */}
        {credential.rotation_recommended_days && (
          <div className="text-xs text-yellow-700 bg-yellow-50 px-2 py-1 rounded">
            ⚠️ Rotation recommended every {credential.rotation_recommended_days} days
          </div>
        )}

        {/* Notes */}
        {credential.notes && (
          <div className="text-xs text-gray-600 bg-gray-50 p-2 rounded border border-gray-200">
            <span className="font-semibold">Note:</span> {credential.notes}
          </div>
        )}

        {/* Test Result */}
        {testResult && (
          <div className={`p-3 rounded text-sm ${
            testResult.test_result?.test_passed
              ? 'bg-green-50 border border-green-200 text-green-700'
              : 'bg-red-50 border border-red-200 text-red-700'
          }`}>
            <div className="flex items-center gap-2">
              {testResult.test_result?.test_passed ? (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              ) : (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              )}
              <span className="font-medium">
                {testResult.test_result?.test_passed ? 'Test Passed' : 'Test Failed'}
              </span>
            </div>
            {testResult.test_result?.error && (
              <p className="text-xs mt-1 ml-7">{testResult.test_result.error}</p>
            )}
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="p-4 border-t border-gray-200 flex gap-2">
        {/* Test Connection */}
        <button
          onClick={handleTest}
          disabled={testing || credential.status === 'not_configured'}
          className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm font-medium"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
          </svg>
          {testing ? 'Testing...' : 'Test'}
        </button>

        {/* View Dashboard */}
        {credential.dashboard_url && (
          <a
            href={credential.dashboard_url}
            target="_blank"
            rel="noopener noreferrer"
            className="px-3 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors flex items-center justify-center"
            title="View Dashboard"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
          </a>
        )}

        {/* Documentation */}
        {credential.documentation_url && (
          <a
            href={credential.documentation_url}
            target="_blank"
            rel="noopener noreferrer"
            className="px-3 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors flex items-center justify-center"
            title="View Documentation"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </a>
        )}
      </div>
    </div>
  );
}
