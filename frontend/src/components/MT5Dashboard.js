import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { RefreshCw, TrendingUp, TrendingDown, DollarSign, Users, Activity, Clock } from 'lucide-react';

const MT5Dashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [accountsData, setAccountsData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastRefresh, setLastRefresh] = useState(null);

  const fetchMT5Data = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const token = localStorage.getItem('fidus_token');
      const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      };

      // Fetch dashboard overview
      const dashboardResponse = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/mt5/dashboard/overview`,
        { headers }
      );

      // Fetch Alejandro's accounts (assuming client_alejandro)
      const accountsResponse = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/mt5/accounts/client_alejandro`,
        { headers }
      );

      if (!dashboardResponse.ok || !accountsResponse.ok) {
        throw new Error('Failed to fetch MT5 data');
      }

      const dashboardResult = await dashboardResponse.json();
      const accountsResult = await accountsResponse.json();

      setDashboardData(dashboardResult);
      setAccountsData(accountsResult);
      setLastRefresh(new Date());

    } catch (err) {
      setError(err.message);
      console.error('MT5 data fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMT5Data();
    
    // Auto-refresh every 5 minutes
    const interval = setInterval(fetchMT5Data, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const formatCurrency = (amount) => {
    if (amount === null || amount === undefined) return '$0.00';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(amount);
  };

  const formatPercentage = (percent) => {
    if (percent === null || percent === undefined) return '0.00%';
    const sign = percent >= 0 ? '+' : '';
    return `${sign}${percent.toFixed(2)}%`;
  };

  const getDataFreshnessColor = (dataSource) => {
    switch (dataSource) {
      case 'live': return 'bg-green-100 text-green-800';
      case 'cached': return 'bg-yellow-100 text-yellow-800';
      case 'stored': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getPerformanceColor = (percentage) => {
    if (percentage > 0) return 'text-green-600';
    if (percentage < 0) return 'text-red-600';
    return 'text-gray-600';
  };

  if (loading && !dashboardData) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex items-center space-x-2">
          <RefreshCw className="w-6 h-6 animate-spin" />
          <span>Loading MT5 data...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="text-red-600">
              <Activity className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-red-800 font-medium">Error loading MT5 data</h3>
              <p className="text-red-600 text-sm">{error}</p>
            </div>
          </div>
          <Button onClick={fetchMT5Data} variant="outline" size="sm">
            <RefreshCw className="w-4 h-4 mr-2" />
            Retry
          </Button>
        </div>
      </div>
    );
  }

  const dashboard = dashboardData?.dashboard || {};
  const accounts = accountsData?.accounts || [];
  const summary = accountsData?.summary || {};

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">MT5 Trading Dashboard</h2>
          <p className="text-gray-600">Live trading account monitoring and analytics</p>
        </div>
        <div className="flex items-center space-x-4">
          {lastRefresh && (
            <div className="flex items-center space-x-2 text-sm text-gray-500">
              <Clock className="w-4 h-4" />
              <span>Last updated: {lastRefresh.toLocaleTimeString()}</span>
            </div>
          )}
          <Button onClick={fetchMT5Data} disabled={loading}>
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Equity</p>
                <p className="text-2xl font-bold">{formatCurrency(dashboard.total_equity)}</p>
              </div>
              <div className="p-2 bg-blue-100 rounded-lg">
                <DollarSign className="w-6 h-6 text-blue-600" />
              </div>
            </div>
            <div className="mt-2">
              <span className={`text-sm ${getPerformanceColor(dashboard.overall_return_percent)}`}>
                {formatPercentage(dashboard.overall_return_percent)} overall return
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total P&L</p>
                <p className={`text-2xl font-bold ${getPerformanceColor(dashboard.total_profit)}`}>
                  {formatCurrency(dashboard.total_profit)}
                </p>
              </div>
              <div className="p-2 bg-green-100 rounded-lg">
                {dashboard.total_profit >= 0 ? (
                  <TrendingUp className="w-6 h-6 text-green-600" />
                ) : (
                  <TrendingDown className="w-6 h-6 text-red-600" />
                )}
              </div>
            </div>
            <div className="mt-2">
              <span className="text-sm text-gray-600">
                vs {formatCurrency(dashboard.total_allocated)} allocated
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Active Accounts</p>
                <p className="text-2xl font-bold">{dashboard.total_accounts}</p>
              </div>
              <div className="p-2 bg-purple-100 rounded-lg">
                <Users className="w-6 h-6 text-purple-600" />
              </div>
            </div>
            <div className="mt-2">
              <span className="text-sm text-gray-600">
                {dashboard.total_positions} open positions
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Data Quality</p>
                <p className="text-2xl font-bold">
                  {dashboard.data_quality?.live_accounts || 0}
                </p>
              </div>
              <div className="p-2 bg-orange-100 rounded-lg">
                <Activity className="w-6 h-6 text-orange-600" />
              </div>
            </div>
            <div className="mt-2">
              <span className="text-sm text-gray-600">
                live of {dashboard.total_accounts} accounts
              </span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Tabs */}
      <Tabs defaultValue="accounts" className="space-y-4">
        <TabsList>
          <TabsTrigger value="accounts">Account Details</TabsTrigger>
          <TabsTrigger value="funds">Fund Analysis</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
        </TabsList>

        <TabsContent value="accounts">
          <Card>
            <CardHeader>
              <CardTitle>MT5 Account Details</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {accounts.map((account, index) => (
                  <div key={account.mt5_login || index} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-3">
                        <h4 className="font-semibold">MT5 #{account.mt5_login}</h4>
                        <Badge variant="outline">{account.fund_code}</Badge>
                        <Badge className={getDataFreshnessColor(account.data_source)}>
                          {account.data_source}
                        </Badge>
                      </div>
                      <div className={`font-semibold ${getPerformanceColor(account.profit_loss)}`}>
                        {formatCurrency(account.profit_loss)}
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <p className="text-gray-600">Allocated</p>
                        <p className="font-medium">{formatCurrency(account.allocated_amount)}</p>
                      </div>
                      <div>
                        <p className="text-gray-600">Current Equity</p>
                        <p className="font-medium">{formatCurrency(account.current_equity)}</p>
                      </div>
                      <div>
                        <p className="text-gray-600">Return</p>
                        <p className={`font-medium ${getPerformanceColor(account.return_percent)}`}>
                          {formatPercentage(account.return_percent)}
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-600">Positions</p>
                        <p className="font-medium">{account.open_positions || 0}</p>
                      </div>
                    </div>
                    
                    {account.margin_used > 0 && (
                      <div className="mt-3 pt-3 border-t">
                        <div className="grid grid-cols-3 gap-4 text-sm">
                          <div>
                            <p className="text-gray-600">Margin Used</p>
                            <p className="font-medium">{formatCurrency(account.margin_used)}</p>
                          </div>
                          <div>
                            <p className="text-gray-600">Free Margin</p>
                            <p className="font-medium">{formatCurrency(account.margin_free)}</p>
                          </div>
                          <div>
                            <p className="text-gray-600">Last Sync</p>
                            <p className="font-medium">
                              {account.last_sync ? 
                                new Date(account.last_sync).toLocaleString() : 
                                'Never'
                              }
                            </p>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="funds">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {Object.entries(dashboard.by_fund || {}).map(([fundCode, fundData]) => (
              <Card key={fundCode}>
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <span>{fundCode} Fund</span>
                    <Badge variant="outline">{fundData.accounts} accounts</Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Allocated</span>
                      <span className="font-semibold">{formatCurrency(fundData.allocated)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Current Equity</span>
                      <span className="font-semibold">{formatCurrency(fundData.equity)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Profit/Loss</span>
                      <span className={`font-semibold ${getPerformanceColor(fundData.profit)}`}>
                        {formatCurrency(fundData.profit)}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Return</span>
                      <span className={`font-semibold ${getPerformanceColor(fundData.return_percent)}`}>
                        {formatPercentage(fundData.return_percent)}
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="performance">
          <Card>
            <CardHeader>
              <CardTitle>Performance Summary</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">
                    {dashboard.performance_summary?.profitable_accounts || 0}
                  </div>
                  <div className="text-sm text-gray-600">Profitable Accounts</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-red-600">
                    {dashboard.performance_summary?.losing_accounts || 0}
                  </div>
                  <div className="text-sm text-gray-600">Losing Accounts</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-600">
                    {dashboard.performance_summary?.break_even_accounts || 0}
                  </div>
                  <div className="text-sm text-gray-600">Break Even</div>
                </div>
              </div>
              
              {dashboard.performance_summary?.best_performer && (
                <div className="mt-6 pt-6 border-t">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="bg-green-50 p-4 rounded-lg">
                      <h4 className="font-semibold text-green-800 mb-2">Best Performer</h4>
                      <p className="text-sm">
                        Account {dashboard.performance_summary.best_performer.mt5_login} ({dashboard.performance_summary.best_performer.fund_code})
                      </p>
                      <p className="text-lg font-bold text-green-600">
                        {formatPercentage(dashboard.performance_summary.best_performer.return_percent)}
                      </p>
                    </div>
                    
                    {dashboard.performance_summary?.worst_performer && (
                      <div className="bg-red-50 p-4 rounded-lg">
                        <h4 className="font-semibold text-red-800 mb-2">Needs Attention</h4>
                        <p className="text-sm">
                          Account {dashboard.performance_summary.worst_performer.mt5_login} ({dashboard.performance_summary.worst_performer.fund_code})
                        </p>
                        <p className="text-lg font-bold text-red-600">
                          {formatPercentage(dashboard.performance_summary.worst_performer.return_percent)}
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default MT5Dashboard;