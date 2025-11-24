import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { RefreshCw, Server, AlertTriangle, CheckCircle2, XCircle, Clock } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

export default function BridgeHealthMonitor() {
  const [healthData, setHealthData] = useState(null);
  const [accounts, setAccounts] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch health status
      const healthRes = await fetch(`${BACKEND_URL}/api/bridges/health`);
      const healthJson = await healthRes.json();
      setHealthData(healthJson);

      // Fetch accounts
      const accountsRes = await fetch(`${BACKEND_URL}/api/bridges/accounts`);
      const accountsJson = await accountsRes.json();
      setAccounts(accountsJson.accounts || []);

      // Fetch alerts
      const alertsRes = await fetch(`${BACKEND_URL}/api/bridges/alerts`);
      const alertsJson = await alertsRes.json();
      setAlerts(alertsJson.alerts || []);

    } catch (err) {
      console.error('Error fetching bridge data:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  const getBridgeStatusIcon = (healthy) => {
    if (healthy) {
      return <CheckCircle2 className="h-5 w-5 text-green-500" />;
    } else {
      return <XCircle className="h-5 w-5 text-red-500" />;
    }
  };

  const getBridgeName = (bridgeId) => {
    const names = {
      mexatlantic_mt5: 'MEXAtlantic MT5',
      lucrum_mt5: 'Lucrum MT5',
      mexatlantic_mt4: 'MEXAtlantic MT4'
    };
    return names[bridgeId] || bridgeId;
  };

  const formatLastSync = (timestamp) => {
    if (!timestamp) return 'Never';
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins === 1) return '1 minute ago';
    if (diffMins < 60) return `${diffMins} minutes ago`;
    
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours === 1) return '1 hour ago';
    if (diffHours < 24) return `${diffHours} hours ago`;
    
    return date.toLocaleString();
  };

  if (loading && !healthData) {
    return (
      <div className="flex items-center justify-center p-8">
        <RefreshCw className="h-8 w-8 animate-spin text-gray-400" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
        <p className="text-red-800">Error loading bridge health: {error}</p>
        <Button onClick={fetchData} className="mt-2">
          <RefreshCw className="h-4 w-4 mr-2" />
          Retry
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Bridge Health Monitor</h2>
          <p className="text-sm text-gray-500">3-Bridge Architecture Status</p>
        </div>
        <Button onClick={fetchData} variant="outline" size="sm">
          <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {/* Overall Status */}
      {healthData && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>Overall System Status</span>
              <Badge variant={healthData.status === 'healthy' ? 'success' : 'warning'}>
                {healthData.status === 'healthy' ? '✅ Healthy' : '⚠️ Degraded'}
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-600">
                  {healthData.total_accounts}
                </div>
                <div className="text-sm text-gray-500">Total Accounts</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-green-600">
                  {Object.values(healthData.bridges).filter(b => b.healthy).length}
                </div>
                <div className="text-sm text-gray-500">Healthy Bridges</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-red-600">
                  {alerts.length}
                </div>
                <div className="text-sm text-gray-500">Active Alerts</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-purple-600">3</div>
                <div className="text-sm text-gray-500">Total Bridges</div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Alerts Section */}
      {alerts.length > 0 && (
        <Card className="border-orange-200 bg-orange-50">
          <CardHeader>
            <CardTitle className="flex items-center text-orange-800">
              <AlertTriangle className="h-5 w-5 mr-2" />
              Active Alerts ({alerts.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {alerts.map((alert, idx) => (
                <div
                  key={idx}
                  className={`p-3 rounded-lg border ${
                    alert.severity === 'critical'
                      ? 'bg-red-50 border-red-300'
                      : 'bg-yellow-50 border-yellow-300'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="font-semibold">
                        {getBridgeName(alert.bridge)}
                      </div>
                      <div className="text-sm mt-1">{alert.message}</div>
                    </div>
                    <Badge
                      variant={alert.severity === 'critical' ? 'destructive' : 'warning'}
                    >
                      {alert.severity}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Bridge Status Cards */}
      {healthData && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {Object.entries(healthData.bridges).map(([bridgeId, bridge]) => (
            <Card key={bridgeId} className={bridge.healthy ? '' : 'border-orange-300'}>
              <CardHeader>
                <CardTitle className="flex items-center justify-between text-base">
                  <div className="flex items-center gap-2">
                    <Server className="h-4 w-4" />
                    {getBridgeName(bridgeId)}
                  </div>
                  {getBridgeStatusIcon(bridge.healthy)}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div>
                    <div className="text-sm text-gray-500">Broker</div>
                    <div className="font-medium">{bridge.broker}</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-500">Platform</div>
                    <div className="font-medium">{bridge.platform}</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-500">Accounts</div>
                    <div className="font-medium">
                      {bridge.accounts} / {bridge.expected_accounts}
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-500 flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      Last Sync
                    </div>
                    <div className="text-sm font-medium">
                      {formatLastSync(bridge.last_sync)}
                    </div>
                  </div>
                  <div>
                    <Badge
                      variant={
                        bridge.status === 'running'
                          ? 'success'
                          : bridge.status === 'stale_data'
                          ? 'warning'
                          : 'destructive'
                      }
                    >
                      {bridge.status}
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Accounts Table */}
      <Card>
        <CardHeader>
          <CardTitle>All Trading Accounts ({accounts.length})</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-2">Account</th>
                  <th className="text-left p-2">Broker</th>
                  <th className="text-left p-2">Platform</th>
                  <th className="text-left p-2">Bridge</th>
                  <th className="text-right p-2">Balance</th>
                  <th className="text-right p-2">Equity</th>
                  <th className="text-center p-2">Positions</th>
                  <th className="text-left p-2">Last Sync</th>
                </tr>
              </thead>
              <tbody>
                {accounts.map((account) => (
                  <tr key={account.account} className="border-b hover:bg-gray-50">
                    <td className="p-2 font-mono font-semibold">{account.account}</td>
                    <td className="p-2">{account.broker}</td>
                    <td className="p-2">
                      <Badge variant={account.platform === 'MT4' ? 'secondary' : 'default'}>
                        {account.platform}
                      </Badge>
                    </td>
                    <td className="p-2 text-xs text-gray-500">
                      {getBridgeName(account.bridge)}
                    </td>
                    <td className="p-2 text-right font-medium">
                      ${account.balance.toLocaleString('en-US', {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2
                      })}
                    </td>
                    <td className="p-2 text-right font-medium">
                      ${account.equity.toLocaleString('en-US', {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2
                      })}
                    </td>
                    <td className="p-2 text-center">{account.positions_count}</td>
                    <td className="p-2 text-xs text-gray-500">
                      {formatLastSync(account.last_sync)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
