import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { 
  Users, 
  TrendingUp, 
  TrendingDown,
  DollarSign,
  Target,
  BarChart3,
  Eye,
  Edit,
  Copy,
  Building2,
  AlertCircle,
  RefreshCw,
  Plus,
  ExternalLink,
  Activity,
  TestTube,
  UserCheck
} from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';

const API = process.env.REACT_APP_BACKEND_URL;

const LiveDemoDashboard = () => {
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [viewMode, setViewMode] = useState('overview');

  useEffect(() => {
    fetchLiveDemoAccounts();
  }, []);

  const fetchLiveDemoAccounts = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await fetch(`${API}/api/live-demo/accounts`);
      const data = await response.json();
      
      if (data.success) {
        setAccounts(data.accounts || []);
      } else {
        throw new Error(data.message || "Failed to fetch live demo accounts");
      }

    } catch (err) {
      console.error("Live demo accounts fetch error:", err);
      setError("Failed to load live demo accounts data");
      setAccounts([]);
    } finally {
      setLoading(false);
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

  const formatPercentage = (value) => {
    return `${(value || 0).toFixed(2)}%`;
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'bg-green-600';
      case 'inactive': return 'bg-slate-600';
      case 'evaluating': return 'bg-yellow-600';
      default: return 'bg-slate-600';
    }
  };

  const getPnlColor = (pnl) => {
    if (pnl > 0) return 'text-green-400';
    if (pnl < 0) return 'text-red-400';
    return 'text-slate-400';
  };

  // Calculate totals with P&L based on initial allocation
  const totals = accounts.reduce((acc, account) => {
    const balance = account.balance || 0;
    const initial = account.initial_allocation || 0;
    const pnl = initial > 0 ? balance - initial : 0;
    
    return {
      balance: acc.balance + balance,
      equity: acc.equity + (account.equity || 0),
      profit: acc.profit + pnl,
      initial: acc.initial + initial
    };
  }, { balance: 0, equity: 0, profit: 0, initial: 0 });
  
  // Calculate total ROI
  const totalROI = totals.initial > 0 ? (totals.profit / totals.initial * 100) : 0;

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-white text-xl flex items-center">
          <RefreshCw className="animate-spin mr-2" />
          Loading live demo accounts...
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white flex items-center">
          <TestTube className="mr-3 h-8 w-8 text-purple-400" />
          Live Demo Accounts
        </h2>
        
        <div className="flex items-center space-x-3">
          <Button 
            onClick={() => setViewMode('overview')}
            variant={viewMode === 'overview' ? 'default' : 'outline'}
            className="text-white"
          >
            Overview
          </Button>
          <Button 
            onClick={() => setViewMode('comparison')}
            variant={viewMode === 'comparison' ? 'default' : 'outline'}
            className="text-white"
          >
            Compare
          </Button>
          <Button 
            onClick={fetchLiveDemoAccounts}
            className="bg-purple-600 hover:bg-purple-700"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Subtitle */}
      <p className="text-slate-400">
        Evaluate new money managers with live demo accounts before allocating real capital
      </p>

      {/* Error Display */}
      {error && (
        <div className="bg-red-900/20 border border-red-600 rounded-lg p-4">
          <div className="flex items-center">
            <AlertCircle className="h-5 w-5 text-red-400 mr-2" />
            <p className="text-red-400">{error}</p>
          </div>
        </div>
      )}

      {/* Info Notice */}
      <div className="bg-purple-900/20 border border-purple-600 rounded-lg p-4">
        <div className="flex items-center">
          <UserCheck className="h-5 w-5 text-purple-400 mr-2" />
          <div>
            <p className="text-purple-400 font-medium">Manager Evaluation System</p>
            <p className="text-purple-300 text-sm mt-1">
              {accounts.length} demo account{accounts.length !== 1 ? 's' : ''} configured for evaluating potential money managers. 
              These accounts behave like real funded accounts but contain no actual capital.
            </p>
          </div>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <Card className="dashboard-card">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">Total Accounts</p>
                <p className="text-2xl font-bold text-white">{accounts.length}</p>
              </div>
              <TestTube className="h-8 w-8 text-purple-400" />
            </div>
          </CardContent>
        </Card>

        <Card className="dashboard-card">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">Initial Allocation</p>
                <p className="text-2xl font-bold text-white">{formatCurrency(totals.initial)}</p>
              </div>
              <Target className="h-8 w-8 text-orange-400" />
            </div>
          </CardContent>
        </Card>

        <Card className="dashboard-card">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">Current Balance</p>
                <p className="text-2xl font-bold text-white">{formatCurrency(totals.balance)}</p>
              </div>
              <DollarSign className="h-8 w-8 text-cyan-400" />
            </div>
          </CardContent>
        </Card>

        <Card className="dashboard-card">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">Total P&L</p>
                <p className={`text-2xl font-bold ${getPnlColor(totals.profit)}`}>
                  {formatCurrency(totals.profit)}
                </p>
              </div>
              {totals.profit >= 0 ? (
                <TrendingUp className="h-8 w-8 text-green-400" />
              ) : (
                <TrendingDown className="h-8 w-8 text-red-400" />
              )}
            </div>
          </CardContent>
        </Card>

        <Card className="dashboard-card">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">Total ROI</p>
                <p className={`text-2xl font-bold ${getPnlColor(totalROI)}`}>
                  {totalROI >= 0 ? '+' : ''}{totalROI.toFixed(2)}%
                </p>
              </div>
              <Activity className="h-8 w-8 text-purple-400" />
            </div>
          </CardContent>
        </Card>
      </div>

      {viewMode === 'overview' && accounts.length > 0 && (
        <>
          {/* Performance Comparison Bar Chart */}
          <Card className="dashboard-card mb-8">
            <CardHeader>
              <CardTitle className="text-white flex items-center">
                <BarChart3 className="mr-2 h-5 w-5 text-purple-400" />
                Demo Account Performance Comparison
              </CardTitle>
              <p className="text-slate-400 text-sm">P&L by demo account - Evaluate manager performance</p>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart
                  data={accounts.map(acc => ({
                    name: acc.manager_name || `Account ${acc.account}`,
                    account: acc.account,
                    pnl: acc.profit || 0,
                    balance: acc.balance || 0
                  })).sort((a, b) => b.pnl - a.pnl)}
                  layout="vertical"
                  margin={{ top: 5, right: 30, left: 120, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis 
                    type="number"
                    stroke="#94a3b8"
                    tick={{ fill: '#94a3b8', fontSize: 12 }}
                    tickFormatter={(value) => `$${(value / 1000).toFixed(1)}k`}
                  />
                  <YAxis 
                    type="category"
                    dataKey="name"
                    stroke="#94a3b8"
                    tick={{ fill: '#94a3b8', fontSize: 12 }}
                    width={110}
                  />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#1e293b', 
                      border: '1px solid #334155',
                      borderRadius: '6px',
                      color: '#fff'
                    }}
                    formatter={(value, name) => {
                      if (name === 'pnl') return [`$${value.toLocaleString()}`, 'P&L'];
                      if (name === 'balance') return [`$${value.toLocaleString()}`, 'Balance'];
                      return [value, name];
                    }}
                  />
                  <Legend wrapperStyle={{ color: '#94a3b8' }} />
                  <Bar dataKey="pnl" name="P&L" radius={[0, 8, 8, 0]}>
                    {accounts.map((acc, index) => {
                      const pnl = acc.profit || 0;
                      const color = pnl > 0 ? '#a855f7' : pnl < 0 ? '#ef4444' : '#64748b';
                      return <Cell key={`cell-${index}`} fill={color} />;
                    })}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Account Cards */}
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
            {accounts.map((account) => {
              const initial = account.initial_allocation || 0;
              const balance = account.balance || 0;
              const pnl = initial > 0 ? balance - initial : 0;
              const returnPct = initial > 0 ? (pnl / initial * 100) : 0;

              return (
                <motion.div
                  key={account.account}
                  whileHover={{ scale: 1.02 }}
                  className="group"
                >
                  <Card className="dashboard-card h-full border-purple-600/30 hover:border-purple-500/50 transition-all">
                    <CardHeader className="pb-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center">
                          <TestTube className="h-5 w-5 text-purple-400 mr-2" />
                          <Badge className="bg-purple-600/20 text-purple-400 border border-purple-500">
                            DEMO
                          </Badge>
                        </div>
                        <Badge className={`${getStatusColor(account.status)} text-white`}>
                          {account.status || 'evaluating'}
                        </Badge>
                      </div>
                      
                      <CardTitle className="text-white text-lg mt-2">
                        {account.manager_name || `Manager Candidate`}
                      </CardTitle>
                      <p className="text-slate-400 text-sm">
                        Account #{account.account} • {account.broker || 'LUCRUM Capital'}
                      </p>
                    </CardHeader>
                    
                    <CardContent className="space-y-4">
                      {/* Initial Allocation */}
                      <div className="bg-orange-900/20 rounded p-3 border border-orange-600/30">
                        <div className="text-xs text-orange-400 mb-1">Initial Allocation</div>
                        <div className="text-orange-400 font-semibold text-lg">
                          {formatCurrency(initial)}
                        </div>
                      </div>

                      {/* Balance & Equity */}
                      <div className="grid grid-cols-2 gap-3">
                        <div className="bg-slate-800/50 rounded p-3">
                          <div className="text-xs text-slate-400 mb-1">Current Balance</div>
                          <div className="text-cyan-400 font-semibold">
                            {formatCurrency(balance)}
                          </div>
                        </div>
                        <div className="bg-slate-800/50 rounded p-3">
                          <div className="text-xs text-slate-400 mb-1">Equity</div>
                          <div className="text-green-400 font-semibold">
                            {formatCurrency(account.equity)}
                          </div>
                        </div>
                      </div>

                      {/* P&L with ROI */}
                      <div className="bg-slate-800/50 rounded p-3">
                        <div className="text-xs text-slate-400 mb-1">Profit/Loss (ROI)</div>
                        <div className="flex items-center justify-between">
                          <span className={`font-bold text-lg ${getPnlColor(pnl)}`}>
                            {formatCurrency(pnl)}
                          </span>
                          <span className={`text-sm font-semibold px-2 py-1 rounded ${
                            returnPct > 0 ? 'bg-green-900/30 text-green-400' : 
                            returnPct < 0 ? 'bg-red-900/30 text-red-400' : 
                            'bg-slate-700 text-slate-400'
                          }`}>
                            {returnPct >= 0 ? '+' : ''}{returnPct.toFixed(2)}%
                          </span>
                        </div>
                      </div>

                      {/* Account Details */}
                      <div className="bg-slate-800/30 rounded p-3">
                        <div className="text-xs text-slate-400 mb-2">Account Details</div>
                        <div className="flex items-center justify-between">
                          <span className="text-white font-medium">
                            {account.platform || 'MT5'}
                          </span>
                          <span className="text-slate-300 text-sm">
                            {account.server || 'Lucrumcapital-Live'}
                          </span>
                        </div>
                      </div>

                      {/* Balance & Equity */}
                      <div className="grid grid-cols-2 gap-3">
                        <div className="bg-slate-800/50 rounded p-3">
                          <div className="text-xs text-slate-400 mb-1">Balance</div>
                          <div className="text-cyan-400 font-semibold">
                            {formatCurrency(account.balance)}
                          </div>
                        </div>
                        <div className="bg-slate-800/50 rounded p-3">
                          <div className="text-xs text-slate-400 mb-1">Equity</div>
                          <div className="text-green-400 font-semibold">
                            {formatCurrency(account.equity)}
                          </div>
                        </div>
                      </div>

                      {/* P&L */}
                      <div className="bg-slate-800/50 rounded p-3">
                        <div className="text-xs text-slate-400 mb-1">Profit/Loss</div>
                        <div className="flex items-center justify-between">
                          <span className={`font-bold text-lg ${getPnlColor(pnl)}`}>
                            {formatCurrency(pnl)}
                          </span>
                          <span className={`text-sm ${getPnlColor(returnPct)}`}>
                            {formatPercentage(returnPct)}
                          </span>
                        </div>
                      </div>

                      {/* Evaluation Notes */}
                      {account.evaluation_notes && (
                        <div className="bg-purple-900/20 rounded p-3 border border-purple-600/30">
                          <div className="text-xs text-purple-400 mb-1">Evaluation Notes</div>
                          <div className="text-slate-300 text-sm">
                            {account.evaluation_notes}
                          </div>
                        </div>
                      )}

                      {/* Last Updated */}
                      <div className="text-xs text-slate-500 text-right">
                        Last updated: {account.updated_at 
                          ? new Date(account.updated_at).toLocaleString() 
                          : 'N/A'}
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              );
            })}
          </div>
        </>
      )}

      {viewMode === 'comparison' && accounts.length > 0 && (
        <Card className="dashboard-card">
          <CardHeader>
            <CardTitle className="text-white flex items-center">
              <Target className="mr-2 h-5 w-5 text-purple-400" />
              Side-by-Side Comparison
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-700">
                    <th className="text-left py-3 px-4 text-slate-400 font-medium">Manager</th>
                    <th className="text-left py-3 px-4 text-slate-400 font-medium">Account</th>
                    <th className="text-right py-3 px-4 text-slate-400 font-medium">Balance</th>
                    <th className="text-right py-3 px-4 text-slate-400 font-medium">Equity</th>
                    <th className="text-right py-3 px-4 text-slate-400 font-medium">P&L</th>
                    <th className="text-right py-3 px-4 text-slate-400 font-medium">Return %</th>
                    <th className="text-center py-3 px-4 text-slate-400 font-medium">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {accounts.map((account) => {
                    const pnl = account.profit || 0;
                    const returnPct = account.initial_allocation > 0 
                      ? ((pnl / account.initial_allocation) * 100) 
                      : 0;
                    
                    return (
                      <tr key={account.account} className="border-b border-slate-800 hover:bg-slate-800/50">
                        <td className="py-3 px-4 text-white font-medium">
                          {account.manager_name || 'Candidate'}
                        </td>
                        <td className="py-3 px-4 text-slate-300">
                          {account.account}
                        </td>
                        <td className="py-3 px-4 text-right text-cyan-400">
                          {formatCurrency(account.balance)}
                        </td>
                        <td className="py-3 px-4 text-right text-green-400">
                          {formatCurrency(account.equity)}
                        </td>
                        <td className={`py-3 px-4 text-right font-medium ${getPnlColor(pnl)}`}>
                          {formatCurrency(pnl)}
                        </td>
                        <td className={`py-3 px-4 text-right ${getPnlColor(returnPct)}`}>
                          {formatPercentage(returnPct)}
                        </td>
                        <td className="py-3 px-4 text-center">
                          <Badge className={`${getStatusColor(account.status)} text-white text-xs`}>
                            {account.status || 'evaluating'}
                          </Badge>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}

      {accounts.length === 0 && !loading && (
        <Card className="dashboard-card">
          <CardContent className="py-12 text-center">
            <TestTube className="h-16 w-16 text-slate-600 mx-auto mb-4" />
            <p className="text-slate-400 text-lg">No live demo accounts configured</p>
            <p className="text-slate-500 text-sm mt-2">
              Add demo accounts in Account Management to start evaluating new money managers
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default LiveDemoDashboard;
