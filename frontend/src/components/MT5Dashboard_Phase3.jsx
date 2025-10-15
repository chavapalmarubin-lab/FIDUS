/**
 * MT5 Dashboard - Phase 3 Version
 * Uses unified MT5 data service (no mock data)
 */

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { RefreshCw, TrendingUp, TrendingDown, DollarSign, Users, Activity, AlertCircle } from 'lucide-react';
import { useMT5Data, useMT5FundTotals } from '../hooks/useMT5Data';
import MT5HealthIndicator from './MT5HealthIndicator';

const MT5Dashboard = () => {
  const { accounts, summary, loading, error, lastUpdated, refresh, isFresh } = useMT5Data();
  const { totals, loading: totalsLoading } = useMT5FundTotals();

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4 text-blue-500" />
          <p className="text-gray-600">Loading MT5 data from VPS Bridge...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-500 mt-0.5" />
              <div>
                <h3 className="font-semibold text-red-900">Failed to load MT5 data</h3>
                <p className="text-sm text-red-700 mt-1">{error}</p>
                <Button onClick={refresh} size="sm" className="mt-3">
                  Try Again
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  const formatCurrency = (value) => {
    if (value === null || value === undefined) return '$0.00';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(value);
  };

  const formatPercent = (value) => {
    if (value === null || value === undefined) return '0.00%';
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  return (
    <div className="space-y-6">
      {/* Header with Health Indicator */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold">MT5 Trading Accounts</h1>
          <p className="text-gray-600 mt-1">
            Real-time data from VPS MT5 Bridge
            {lastUpdated && (
              <span className="ml-2 text-sm text-gray-500">
                (Updated: {lastUpdated.toLocaleTimeString()})
              </span>
            )}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <MT5HealthIndicator />
          <Button onClick={() => refresh()} size="sm" variant="outline">
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Data Freshness Warning */}
      {!isFresh && (
        <Card className="border-yellow-200 bg-yellow-50">
          <CardContent className="pt-4">
            <div className="flex items-center gap-2 text-yellow-800">
              <AlertCircle className="w-5 h-5" />
              <span className="font-medium">
                Some account data is stale (older than 10 minutes)
              </span>
            </div>
            <p className="text-sm text-yellow-700 mt-1 ml-7">
              VPS MT5 Bridge may not be syncing. Contact support if this persists.
            </p>
          </CardContent>
        </Card>
      )}

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">
              Total Accounts
            </CardTitle>
            <Users className="w-4 h-4 text-gray-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{summary.total_accounts || 0}</div>
            <p className="text-xs text-gray-500 mt-1">
              Fresh: {summary.fresh_accounts || 0} | Stale: {summary.stale_accounts || 0}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">
              Total Equity
            </CardTitle>
            <DollarSign className="w-4 h-4 text-gray-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatCurrency(summary.total_equity)}
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Allocated: {formatCurrency(summary.total_allocated)}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">
              Total P&L
            </CardTitle>
            {(summary.total_profit_loss || 0) >= 0 ? (
              <TrendingUp className="w-4 h-4 text-green-500" />
            ) : (
              <TrendingDown className="w-4 h-4 text-red-500" />
            )}
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${
              (summary.total_profit_loss || 0) >= 0 ? 'text-green-600' : 'text-red-600'
            }`}>
              {formatCurrency(summary.total_profit_loss)}
            </div>
            <p className="text-xs text-gray-500 mt-1">
              ROI: {formatPercent(summary.overall_performance_percentage)}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">
              System Status
            </CardTitle>
            <Activity className="w-4 h-4 text-gray-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {isFresh ? (
                <span className="text-green-600">Active</span>
              ) : (
                <span className="text-yellow-600">Degraded</span>
              )}
            </div>
            <p className="text-xs text-gray-500 mt-1">
              VPS Bridge sync: {isFresh ? 'OK' : 'Delayed'}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Accounts by Fund Type */}
      <Card>
        <CardHeader>
          <CardTitle>Accounts by Fund Type</CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="all" className="w-full">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="all">All ({accounts.length})</TabsTrigger>
              <TabsTrigger value="BALANCE">
                Balance ({accounts.filter(a => a.fund_code === 'BALANCE').length})
              </TabsTrigger>
              <TabsTrigger value="CORE">
                Core ({accounts.filter(a => a.fund_code === 'CORE').length})
              </TabsTrigger>
              <TabsTrigger value="SEPARATION">
                Separation ({accounts.filter(a => a.fund_code === 'SEPARATION').length})
              </TabsTrigger>
            </TabsList>

            <TabsContent value="all" className="mt-4">
              <AccountsTable accounts={accounts} formatCurrency={formatCurrency} />
            </TabsContent>

            <TabsContent value="BALANCE" className="mt-4">
              <AccountsTable 
                accounts={accounts.filter(a => a.fund_code === 'BALANCE')} 
                formatCurrency={formatCurrency} 
              />
            </TabsContent>

            <TabsContent value="CORE" className="mt-4">
              <AccountsTable 
                accounts={accounts.filter(a => a.fund_code === 'CORE')} 
                formatCurrency={formatCurrency} 
              />
            </TabsContent>

            <TabsContent value="SEPARATION" className="mt-4">
              <AccountsTable 
                accounts={accounts.filter(a => a.fund_code === 'SEPARATION')} 
                formatCurrency={formatCurrency} 
              />
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
};

// Accounts Table Component
const AccountsTable = ({ accounts, formatCurrency }) => {
  if (accounts.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        No accounts in this category
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Account</th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
            <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Balance</th>
            <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Equity</th>
            <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">P&L</th>
            <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">Status</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200">
          {accounts.map((account) => (
            <tr key={account.mt5_login} className="hover:bg-gray-50">
              <td className="px-4 py-3 text-sm font-medium text-gray-900">
                {account.mt5_login}
              </td>
              <td className="px-4 py-3 text-sm text-gray-600">
                {account.broker_name}
              </td>
              <td className="px-4 py-3 text-sm text-right text-gray-900">
                {formatCurrency(account.balance)}
              </td>
              <td className="px-4 py-3 text-sm text-right text-gray-900">
                {formatCurrency(account.current_equity)}
              </td>
              <td className={`px-4 py-3 text-sm text-right font-medium ${
                (account.profit_loss || 0) >= 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                {formatCurrency(account.profit_loss)}
              </td>
              <td className="px-4 py-3 text-center">
                {account.is_fresh ? (
                  <Badge variant="success" className="bg-green-100 text-green-800">
                    Fresh
                  </Badge>
                ) : (
                  <Badge variant="warning" className="bg-yellow-100 text-yellow-800">
                    Stale ({account.data_age_minutes?.toFixed(0)}m)
                  </Badge>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default MT5Dashboard;
