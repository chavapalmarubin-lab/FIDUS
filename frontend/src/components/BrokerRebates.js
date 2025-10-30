import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { DollarSign, TrendingUp, Activity, Calendar, RefreshCw, AlertCircle } from 'lucide-react';
import mt5Service from '../services/mt5Service';

const REBATE_RATE = 5.05; // $ per lot

const BrokerRebates = () => {
  const [rebatesData, setRebatesData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [period, setPeriod] = useState('all'); // Changed from '30d' to 'all' to match wallet balance
  const [selectedAccount, setSelectedAccount] = useState('all');
  const [syncStatus, setSyncStatus] = useState('idle'); // idle, syncing, success, error
  const [syncMessage, setSyncMessage] = useState('');

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'https://fidus-invest.emergent.host';

  useEffect(() => {
    fetchRebates();
  }, [period, selectedAccount]);

  const fetchRebates = async () => {
    setLoading(true);
    try {
      // For 'all' period, don't send date filters to get all-time rebates
      const dateRange = period === 'all' ? {} : mt5Service.getDateRangeForPeriod(period);
      
      const response = await mt5Service.getRebates({
        start_date: dateRange.start_date,
        end_date: dateRange.end_date,
        account_number: selectedAccount !== 'all' ? parseInt(selectedAccount) : null,
        rebate_per_lot: REBATE_RATE
      });

      if (response.success) {
        setRebatesData(response.rebates);
        console.log('✅ [Phase 4A] Broker rebates loaded:', response.rebates);
      }
    } catch (error) {
      console.error('❌ Error fetching rebates:', error);
      setRebatesData(null);
    } finally {
      setLoading(false);
    }
  };

  const syncTradeHistory = async () => {
    setSyncStatus('syncing');
    setSyncMessage('Syncing trade history from all 7 accounts...');
    
    try {
      // Get auth token from localStorage
      const token = localStorage.getItem('token') || localStorage.getItem('authToken');
      
      if (!token) {
        setSyncStatus('error');
        setSyncMessage('Please login first');
        setTimeout(() => setSyncStatus('idle'), 5000);
        return;
      }

      const response = await fetch(`${BACKEND_URL}/api/admin/mt5-deals/sync-all`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setSyncStatus('success');
        const dealsCount = data.total_deals_synced || 0;
        const duration = data.duration_seconds || 0;
        setSyncMessage(`✅ Synced ${dealsCount} deals in ${duration}s!`);
        
        // Auto-refresh rebates after successful sync
        setTimeout(() => {
          fetchRebates();
          setSyncStatus('idle');
          setSyncMessage('');
        }, 3000);
      } else {
        const errorData = await response.json().catch(() => ({}));
        setSyncStatus('error');
        setSyncMessage(errorData.detail || 'Sync failed');
        setTimeout(() => setSyncStatus('idle'), 5000);
      }
    } catch (error) {
      console.error('Sync error:', error);
      setSyncStatus('error');
      setSyncMessage(error.message);
      setTimeout(() => setSyncStatus('idle'), 5000);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(amount || 0);
  };

  const getPeriodLabel = (period) => {
    switch(period) {
      case '7d': return 'Last 7 Days';
      case '30d': return 'Last 30 Days';
      case '90d': return 'Last 90 Days';
      default: return 'Custom Period';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-white">Broker Rebates Calculator</h1>
          <p className="text-slate-400 mt-1">
            Rebate Rate: <span className="text-cyan-400 font-semibold">${REBATE_RATE.toFixed(2)} per lot traded</span>
          </p>
        </div>
        <div className="flex gap-3">
          <Button 
            onClick={fetchRebates} 
            disabled={loading}
            className="bg-cyan-600 hover:bg-cyan-700 text-white"
          >
            <RefreshCw className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            {loading ? 'Loading...' : 'Refresh'}
          </Button>
          
          <Button 
            onClick={syncTradeHistory} 
            disabled={syncStatus === 'syncing'}
            className={
              syncStatus === 'success' 
                ? 'bg-green-600 hover:bg-green-700 text-white' 
                : syncStatus === 'error'
                ? 'bg-red-600 hover:bg-red-700 text-white'
                : 'bg-blue-600 hover:bg-blue-700 text-white'
            }
          >
            {syncStatus === 'syncing' ? (
              <>
                <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                Syncing...
              </>
            ) : syncStatus === 'success' ? (
              <>
                <Activity className="mr-2 h-4 w-4" />
                Synced!
              </>
            ) : (
              <>
                <Activity className="mr-2 h-4 w-4" />
                Sync Trade History
              </>
            )}
          </Button>
        </div>
      </div>

      {/* Sync Status Message */}
      {syncMessage && (
        <div className={`p-4 rounded-lg mb-4 ${
          syncStatus === 'success' 
            ? 'bg-green-900/20 border border-green-500/30 text-green-400' 
            : syncStatus === 'error'
            ? 'bg-red-900/20 border border-red-500/30 text-red-400'
            : 'bg-blue-900/20 border border-blue-500/30 text-blue-400'
        }`}>
          <p className="text-sm font-medium">{syncMessage}</p>
        </div>
      )}

      {/* Filters */}
      <Card className="dashboard-card">
        <CardContent className="pt-6">
          <div className="flex flex-wrap gap-4">
            <div className="flex-1 min-w-[200px]">
              <label className="block text-sm font-medium text-slate-400 mb-2">Period</label>
              <select
                value={period}
                onChange={(e) => setPeriod(e.target.value)}
                className="w-full px-3 py-2 bg-slate-700 border border-slate-600 text-white rounded-md focus:ring-2 focus:ring-cyan-500"
              >
                <option value="all">All Time (Cumulative)</option>
                <option value="7d">Last 7 Days</option>
                <option value="30d">Last 30 Days</option>
                <option value="90d">Last 90 Days</option>
              </select>
            </div>

            <div className="flex-1 min-w-[200px]">
              <label className="block text-sm font-medium text-slate-400 mb-2">Account</label>
              <select
                value={selectedAccount}
                onChange={(e) => setSelectedAccount(e.target.value)}
                className="w-full px-3 py-2 bg-slate-700 border border-slate-600 text-white rounded-md focus:ring-2 focus:ring-cyan-500"
              >
                <option value="all">All Accounts</option>
                <option value="885822">885822 - Core</option>
                <option value="886066">886066 - Secondary Balance</option>
                <option value="886528">886528 - Separation</option>
                <option value="886557">886557 - Main Balance</option>
                <option value="886602">886602 - Tertiary Balance</option>
                <option value="891215">891215 - Interest Trading</option>
                <option value="891234">891234 - CORE Fund</option>
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {loading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-cyan-400 mx-auto mb-4"></div>
          <p className="text-slate-400">Loading rebate data...</p>
        </div>
      ) : !rebatesData ? (
        <Card className="dashboard-card">
          <CardContent className="py-12 text-center">
            <AlertCircle className="h-16 w-16 mx-auto mb-4 text-yellow-400" />
            <p className="text-white text-lg mb-2">No Rebate Data Available</p>
            <p className="text-slate-400">Deal history collection may not be active yet.</p>
          </CardContent>
        </Card>
      ) : (
        <>
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card className="dashboard-card">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-slate-400">Total Volume</CardTitle>
                <Activity className="h-4 w-4 text-cyan-400" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-white">{rebatesData.total_volume?.toFixed(2) || '0.00'}</div>
                <p className="text-xs text-slate-400">Lots traded</p>
              </CardContent>
            </Card>

            <Card className="dashboard-card">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-slate-400">Total Rebates</CardTitle>
                <DollarSign className="h-4 w-4 text-green-400" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-400">
                  {formatCurrency(rebatesData.total_rebates)}
                </div>
                <p className="text-xs text-slate-400">
                  {rebatesData.total_volume?.toFixed(2) || '0'} lots × ${REBATE_RATE}
                </p>
              </CardContent>
            </Card>

            <Card className="dashboard-card">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-slate-400">Commission Paid</CardTitle>
                <TrendingUp className="h-4 w-4 text-red-400" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-red-400">
                  {formatCurrency(Math.abs(rebatesData.total_commission || 0))}
                </div>
                <p className="text-xs text-slate-400">Paid to broker</p>
              </CardContent>
            </Card>

            <Card className="dashboard-card">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-slate-400">Net Benefit</CardTitle>
                <Calendar className="h-4 w-4 text-cyan-400" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-cyan-400">
                  {formatCurrency((rebatesData.total_rebates || 0) + (rebatesData.total_commission || 0))}
                </div>
                <p className="text-xs text-slate-400">Rebates - Commission</p>
              </CardContent>
            </Card>
          </div>

          {/* Rebates by Account Chart */}
          {rebatesData.by_account && rebatesData.by_account.length > 0 && (
            <Card className="dashboard-card">
              <CardHeader>
                <CardTitle className="text-white">Rebates by Account ({getPeriodLabel(period)})</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={350}>
                  <BarChart data={rebatesData.by_account}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis 
                      dataKey="account" 
                      stroke="#94a3b8"
                      tick={{ fill: '#94a3b8' }}
                    />
                    <YAxis 
                      stroke="#94a3b8"
                      tick={{ fill: '#94a3b8' }}
                      tickFormatter={(value) => `$${value.toFixed(0)}`}
                    />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: '#1e293b', 
                        border: '1px solid #334155',
                        borderRadius: '8px'
                      }}
                      formatter={(value, name) => {
                        if (name === 'volume') return [`${value.toFixed(2)} lots`, 'Volume'];
                        if (name === 'rebates') return [formatCurrency(value), 'Rebates'];
                        return value;
                      }}
                      labelStyle={{ color: '#fff' }}
                    />
                    <Legend 
                      wrapperStyle={{ color: '#94a3b8' }}
                    />
                    <Bar dataKey="volume" fill="#06b6d4" name="Volume (lots)" radius={[8, 8, 0, 0]} />
                    <Bar dataKey="rebates" fill="#10b981" name="Rebates ($)" radius={[8, 8, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          )}

          {/* Rebates by Symbol Table & Chart */}
          {rebatesData.by_symbol && rebatesData.by_symbol.length > 0 && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Pie Chart */}
              <Card className="dashboard-card">
                <CardHeader>
                  <CardTitle className="text-white">Rebates by Symbol</CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={rebatesData.by_symbol.slice(0, 8)}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={(entry) => `${entry.symbol}: ${formatCurrency(entry.rebates)}`}
                        outerRadius={100}
                        fill="#8884d8"
                        dataKey="rebates"
                      >
                        {rebatesData.by_symbol.slice(0, 8).map((entry, index) => {
                          const colors = ['#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6', '#f97316'];
                          return <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />;
                        })}
                      </Pie>
                      <Tooltip 
                        contentStyle={{ 
                          backgroundColor: '#1e293b', 
                          border: '1px solid #334155',
                          borderRadius: '8px',
                          color: '#fff'
                        }}
                        formatter={(value) => formatCurrency(value)}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              {/* Table */}
              <Card className="dashboard-card">
                <CardHeader>
                  <CardTitle className="text-white">Top Symbols</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="overflow-y-auto max-h-[300px]">
                    <table className="w-full">
                      <thead className="sticky top-0 bg-slate-800">
                        <tr className="border-b border-slate-700">
                          <th className="text-left text-slate-400 font-semibold py-2 px-2">Symbol</th>
                          <th className="text-right text-slate-400 font-semibold py-2 px-2">Volume</th>
                          <th className="text-right text-slate-400 font-semibold py-2 px-2">Rebate</th>
                        </tr>
                      </thead>
                      <tbody>
                        {rebatesData.by_symbol.slice(0, 10).map((symbol, idx) => (
                          <tr key={idx} className="border-b border-slate-800 hover:bg-slate-800/30">
                            <td className="py-2 px-2">
                              <Badge className="bg-cyan-600 text-white">{symbol.symbol}</Badge>
                            </td>
                            <td className="text-right py-2 px-2 text-white">
                              {symbol.volume?.toFixed(2) || '0.00'}
                            </td>
                            <td className="text-right py-2 px-2 text-green-400 font-semibold">
                              {formatCurrency(symbol.rebates)}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Detailed Account Breakdown */}
          {rebatesData.by_account && rebatesData.by_account.length > 0 && (
            <Card className="dashboard-card">
              <CardHeader>
                <CardTitle className="text-white">Detailed Account Breakdown</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-slate-700">
                        <th className="text-left text-slate-400 font-semibold py-3 px-2">Account</th>
                        <th className="text-left text-slate-400 font-semibold py-3 px-2">Name</th>
                        <th className="text-center text-slate-400 font-semibold py-3 px-2">Fund Type</th>
                        <th className="text-right text-slate-400 font-semibold py-3 px-2">Volume (lots)</th>
                        <th className="text-right text-slate-400 font-semibold py-3 px-2">Commission</th>
                        <th className="text-right text-slate-400 font-semibold py-3 px-2">Rebate</th>
                        <th className="text-right text-slate-400 font-semibold py-3 px-2">Net Benefit</th>
                      </tr>
                    </thead>
                    <tbody>
                      {rebatesData.by_account.map((account, idx) => (
                        <tr key={idx} className="border-b border-slate-800 hover:bg-slate-800/30 transition-colors">
                          <td className="py-3 px-2">
                            <Badge className="bg-purple-600 text-white">{account.account}</Badge>
                          </td>
                          <td className="py-3 px-2 text-white">{account.account_name || 'N/A'}</td>
                          <td className="py-3 px-2 text-center">
                            <Badge className={`${
                              account.fund_type === 'CORE' ? 'bg-blue-600' :
                              account.fund_type === 'BALANCE' ? 'bg-green-600' :
                              'bg-orange-600'
                            } text-white`}>
                              {account.fund_type}
                            </Badge>
                          </td>
                          <td className="py-3 px-2 text-right text-white font-semibold">
                            {account.volume?.toFixed(2) || '0.00'}
                          </td>
                          <td className="py-3 px-2 text-right text-red-400">
                            {formatCurrency(Math.abs(account.commission || 0))}
                          </td>
                          <td className="py-3 px-2 text-right text-green-400 font-bold">
                            {formatCurrency(account.rebates)}
                          </td>
                          <td className="py-3 px-2 text-right text-cyan-400 font-bold">
                            {formatCurrency((account.rebates || 0) + (account.commission || 0))}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                    <tfoot className="border-t-2 border-slate-600">
                      <tr className="font-bold">
                        <td colSpan="3" className="py-3 px-2 text-white">TOTAL</td>
                        <td className="py-3 px-2 text-right text-white">
                          {rebatesData.total_volume?.toFixed(2) || '0.00'}
                        </td>
                        <td className="py-3 px-2 text-right text-red-400">
                          {formatCurrency(Math.abs(rebatesData.total_commission || 0))}
                        </td>
                        <td className="py-3 px-2 text-right text-green-400">
                          {formatCurrency(rebatesData.total_rebates)}
                        </td>
                        <td className="py-3 px-2 text-right text-cyan-400">
                          {formatCurrency((rebatesData.total_rebates || 0) + (rebatesData.total_commission || 0))}
                        </td>
                      </tr>
                    </tfoot>
                  </table>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Data Source Banner */}
          <Card className="dashboard-card bg-blue-900/20 border-blue-500/30">
            <CardContent className="p-4">
              <div className="flex items-start">
                <Activity className="h-5 w-5 text-blue-400 mr-3 mt-0.5 flex-shrink-0" />
                <div className="text-sm">
                  <div className="text-blue-300 font-semibold mb-1">Real-time MT5 Deal Data</div>
                  <div className="text-slate-300">
                    <strong>Rebate Calculation:</strong> Total Volume (lots) × ${REBATE_RATE.toFixed(2)} per lot = Total Rebates
                  </div>
                  <div className="text-slate-300 mt-1">
                    Data sourced from actual MT5 deal history via Phase 4A API endpoints. 
                    Updated every 5 minutes via VPS bridge service. 
                    Rebate rate is fixed at ${REBATE_RATE.toFixed(2)} per standard lot traded.
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
};

export default BrokerRebates;
