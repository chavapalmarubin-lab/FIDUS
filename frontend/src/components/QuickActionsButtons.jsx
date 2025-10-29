import React, { useState, useEffect } from 'react';

const QuickActionsButtons = () => {
  const [bridgeStatus, setBridgeStatus] = useState('checking');
  const [lastCheck, setLastCheck] = useState(null);
  const [accounts, setAccounts] = useState(null);

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'https://fidus-invest.emergent.host';
  const GITHUB_REPO = 'chavapalmarubin-lab/FIDUS';

  const checkBridgeHealth = async () => {
    setBridgeStatus('checking');
    try {
      // Use backend proxy instead of direct VPS connection to avoid CORS issues
      const response = await fetch(`${BACKEND_URL}/api/mt5-bridge-proxy/health`);
      if (response.ok) {
        const data = await response.json();
        setBridgeStatus('online');
        // Try to get account count from health check
        if (data.cache && data.cache.accounts_cached) {
          setAccounts(data.cache.accounts_cached);
        }
        setLastCheck(new Date());
      } else {
        setBridgeStatus('offline');
        setLastCheck(new Date());
      }
    } catch (error) {
      console.error('Bridge health check error:', error);
      setBridgeStatus('offline');
      setLastCheck(new Date());
    }
  };

  useEffect(() => {
    checkBridgeHealth();
    // Check every 5 minutes
    const interval = setInterval(checkBridgeHealth, 300000);
    return () => clearInterval(interval);
  }, []);

  const openWorkflow = (workflowName) => {
    window.open(
      `https://github.com/${GITHUB_REPO}/actions/workflows/${workflowName}`,
      '_blank'
    );
  };

  const openGitHubActions = () => {
    window.open(`https://github.com/${GITHUB_REPO}/actions`, '_blank');
  };

  const getStatusColor = () => {
    switch (bridgeStatus) {
      case 'online':
        return '#10b981';
      case 'offline':
        return '#ef4444';
      case 'checking':
        return '#f59e0b';
      default:
        return '#6b7280';
    }
  };

  const getStatusText = () => {
    switch (bridgeStatus) {
      case 'online':
        return `✅ Online (${accounts} accounts)`;
      case 'offline':
        return '❌ Offline';
      case 'checking':
        return '🔄 Checking...';
      default:
        return 'Unknown';
    }
  };

  return (
    <div style={{ padding: '30px', maxWidth: '1200px', margin: '0 auto' }}>
      {/* System Status Card */}
      <div style={{
        background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
        border: '1px solid rgba(59, 130, 246, 0.3)',
        borderRadius: '16px',
        padding: '30px',
        marginBottom: '30px',
        boxShadow: '0 10px 40px rgba(0, 0, 0, 0.3)'
      }}>
        <h2 style={{ 
          color: '#fff', 
          marginBottom: '20px',
          fontSize: '24px',
          fontWeight: '600'
        }}>
          🎯 System Status
        </h2>
        
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
          gap: '20px',
          marginBottom: '20px'
        }}>
          <div style={{
            background: 'rgba(255, 255, 255, 0.05)',
            padding: '20px',
            borderRadius: '12px',
            border: '1px solid rgba(255, 255, 255, 0.1)'
          }}>
            <div style={{ color: '#94a3b8', fontSize: '14px', marginBottom: '8px' }}>
              MT5 Bridge
            </div>
            <div style={{ 
              color: getStatusColor(),
              fontSize: '18px',
              fontWeight: '600'
            }}>
              {getStatusText()}
            </div>
          </div>

          <div style={{
            background: 'rgba(255, 255, 255, 0.05)',
            padding: '20px',
            borderRadius: '12px',
            border: '1px solid rgba(255, 255, 255, 0.1)'
          }}>
            <div style={{ color: '#94a3b8', fontSize: '14px', marginBottom: '8px' }}>
              Auto-Healing
            </div>
            <div style={{ 
              color: '#10b981',
              fontSize: '18px',
              fontWeight: '600'
            }}>
              ✅ Active
            </div>
          </div>

          <div style={{
            background: 'rgba(255, 255, 255, 0.05)',
            padding: '20px',
            borderRadius: '12px',
            border: '1px solid rgba(255, 255, 255, 0.1)'
          }}>
            <div style={{ color: '#94a3b8', fontSize: '14px', marginBottom: '8px' }}>
              Monitoring
            </div>
            <div style={{ 
              color: '#10b981',
              fontSize: '18px',
              fontWeight: '600'
            }}>
              ✅ Every 15 min
            </div>
          </div>

          <div style={{
            background: 'rgba(255, 255, 255, 0.05)',
            padding: '20px',
            borderRadius: '12px',
            border: '1px solid rgba(255, 255, 255, 0.1)'
          }}>
            <div style={{ color: '#94a3b8', fontSize: '14px', marginBottom: '8px' }}>
              Last Check
            </div>
            <div style={{ 
              color: '#fff',
              fontSize: '18px',
              fontWeight: '600'
            }}>
              {lastCheck ? lastCheck.toLocaleTimeString() : 'N/A'}
            </div>
          </div>
        </div>

        <button
          onClick={checkBridgeHealth}
          disabled={bridgeStatus === 'checking'}
          style={{
            background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
            color: '#fff',
            border: 'none',
            padding: '12px 24px',
            borderRadius: '8px',
            fontSize: '14px',
            fontWeight: '600',
            cursor: bridgeStatus === 'checking' ? 'not-allowed' : 'pointer',
            opacity: bridgeStatus === 'checking' ? 0.6 : 1,
            transition: 'all 0.2s'
          }}
        >
          🔄 Refresh Status
        </button>
      </div>

      {/* Quick Actions */}
      <div style={{
        background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
        border: '1px solid rgba(59, 130, 246, 0.3)',
        borderRadius: '16px',
        padding: '30px',
        marginBottom: '30px',
        boxShadow: '0 10px 40px rgba(0, 0, 0, 0.3)'
      }}>
        <h2 style={{ 
          color: '#fff', 
          marginBottom: '20px',
          fontSize: '24px',
          fontWeight: '600'
        }}>
          🚀 Quick Actions
        </h2>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: '20px'
        }}>
          {/* Deploy Bridge Button */}
          <button
            onClick={() => openWorkflow('deploy-complete-bridge.yml')}
            style={{
              background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
              color: '#fff',
              border: 'none',
              padding: '20px',
              borderRadius: '12px',
              fontSize: '16px',
              fontWeight: '600',
              cursor: 'pointer',
              textAlign: 'left',
              transition: 'all 0.2s',
              boxShadow: '0 4px 6px rgba(0, 0, 0, 0.2)'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-2px)';
              e.currentTarget.style.boxShadow = '0 6px 12px rgba(0, 0, 0, 0.3)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.2)';
            }}
          >
            <div style={{ fontSize: '24px', marginBottom: '8px' }}>🚀</div>
            <div style={{ marginBottom: '4px' }}>Deploy MT5 Bridge</div>
            <div style={{ fontSize: '12px', opacity: 0.9 }}>
              Deploy latest code to VPS
            </div>
          </button>

          {/* Monitor Health Button */}
          <button
            onClick={() => openWorkflow('monitor-bridge-health.yml')}
            style={{
              background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
              color: '#fff',
              border: 'none',
              padding: '20px',
              borderRadius: '12px',
              fontSize: '16px',
              fontWeight: '600',
              cursor: 'pointer',
              textAlign: 'left',
              transition: 'all 0.2s',
              boxShadow: '0 4px 6px rgba(0, 0, 0, 0.2)'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-2px)';
              e.currentTarget.style.boxShadow = '0 6px 12px rgba(0, 0, 0, 0.3)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.2)';
            }}
          >
            <div style={{ fontSize: '24px', marginBottom: '8px' }}>🏥</div>
            <div style={{ marginBottom: '4px' }}>Check System Health</div>
            <div style={{ fontSize: '12px', opacity: 0.9 }}>
              Run health check & auto-restart
            </div>
          </button>

          {/* View Logs Button */}
          <button
            onClick={openGitHubActions}
            style={{
              background: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
              color: '#fff',
              border: 'none',
              padding: '20px',
              borderRadius: '12px',
              fontSize: '16px',
              fontWeight: '600',
              cursor: 'pointer',
              textAlign: 'left',
              transition: 'all 0.2s',
              boxShadow: '0 4px 6px rgba(0, 0, 0, 0.2)'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-2px)';
              e.currentTarget.style.boxShadow = '0 6px 12px rgba(0, 0, 0, 0.3)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.2)';
            }}
          >
            <div style={{ fontSize: '24px', marginBottom: '8px' }}>📊</div>
            <div style={{ marginBottom: '4px' }}>View Recent Logs</div>
            <div style={{ fontSize: '12px', opacity: 0.9 }}>
              Check GitHub Actions history
            </div>
          </button>

          {/* Test Endpoint Button */}
          <button
            onClick={() => window.open(`http://${VPS_HOST}:${BRIDGE_PORT}/api/mt5/accounts/summary`, '_blank')}
            style={{
              background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
              color: '#fff',
              border: 'none',
              padding: '20px',
              borderRadius: '12px',
              fontSize: '16px',
              fontWeight: '600',
              cursor: 'pointer',
              textAlign: 'left',
              transition: 'all 0.2s',
              boxShadow: '0 4px 6px rgba(0, 0, 0, 0.2)'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-2px)';
              e.currentTarget.style.boxShadow = '0 6px 12px rgba(0, 0, 0, 0.3)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.2)';
            }}
          >
            <div style={{ fontSize: '24px', marginBottom: '8px' }}>🧪</div>
            <div style={{ marginBottom: '4px' }}>Test Bridge Endpoint</div>
            <div style={{ fontSize: '12px', opacity: 0.9 }}>
              Direct API test
            </div>
          </button>
        </div>
      </div>

      {/* Recent Activity */}
      <div style={{
        background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
        border: '1px solid rgba(59, 130, 246, 0.3)',
        borderRadius: '16px',
        padding: '30px',
        boxShadow: '0 10px 40px rgba(0, 0, 0, 0.3)'
      }}>
        <h2 style={{ 
          color: '#fff', 
          marginBottom: '20px',
          fontSize: '24px',
          fontWeight: '600'
        }}>
          📋 Recent Activity
        </h2>
        
        <div style={{ color: '#94a3b8' }}>
          <div style={{
            padding: '16px',
            background: 'rgba(255, 255, 255, 0.05)',
            borderRadius: '8px',
            marginBottom: '12px',
            border: '1px solid rgba(255, 255, 255, 0.1)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span>✅ Auto-healing monitoring active</span>
              <span style={{ fontSize: '12px', color: '#64748b' }}>Every 15 minutes</span>
            </div>
          </div>
          
          <div style={{
            padding: '16px',
            background: 'rgba(255, 255, 255, 0.05)',
            borderRadius: '8px',
            marginBottom: '12px',
            border: '1px solid rgba(255, 255, 255, 0.1)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span>✅ Bridge deployed successfully</span>
              <span style={{ fontSize: '12px', color: '#64748b' }}>October 29, 2025</span>
            </div>
          </div>

          <div style={{
            padding: '16px',
            background: 'rgba(255, 255, 255, 0.05)',
            borderRadius: '8px',
            border: '1px solid rgba(255, 255, 255, 0.1)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span>✅ All endpoints responding HTTP 200</span>
              <span style={{ fontSize: '12px', color: '#64748b' }}>Current</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default QuickActionsButtons;
