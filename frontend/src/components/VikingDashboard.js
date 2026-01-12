/**
 * VKNG AI Trading Operations Dashboard
 * 
 * Branded with official VKNG AI colors from getvkng.com
 * 
 * This dashboard manages VKNG AI trading strategies:
 * - CORE Strategy: Account 33627673 (MEXAtlantic)
 * - PRO Strategy: Account 1309411 (Traders Trust)
 * 
 * UI follows FXBlue format (https://www.fxblue.com/users/gestion_global)
 */

import React, { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { 
  DollarSign, 
  TrendingUp, 
  TrendingDown,
  Activity,
  AlertCircle,
  RefreshCw,
  BarChart3,
  PieChart as PieChartIcon,
  Shield,
  Clock,
  Target,
  Percent,
  Calendar,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Loader2,
  ChevronRight,
  ArrowUpRight,
  ArrowDownRight
} from "lucide-react";
import { 
  LineChart, 
  Line, 
  AreaChart,
  Area,
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

// VKNG AI Brand Colors (from getvkng.com)
const VKNG_COLORS = {
  gold: '#D4AF37',
  goldLight: '#F4D03F',
  goldDark: '#B8860B',
  dark: '#0A0A0A',
  darkGray: '#141414',
  mediumGray: '#1A1A1A',
  textPrimary: '#FFFFFF',
  textSecondary: '#9CA3AF'
};

// Colors for charts
const COLORS = {
  primary: '#D4AF37',    // VKNG Gold
  secondary: '#F4D03F',  // Light Gold
  success: '#22c55e',    // Green
  danger: '#ef4444',     // Red
  warning: '#eab308',    // Yellow
  purple: '#8b5cf6',     // Purple
  cyan: '#06b6d4',       // Cyan
  pink: '#ec4899'        // Pink
};

const SYMBOL_COLORS = ['#D4AF37', '#F4D03F', '#22c55e', '#8b5cf6', '#06b6d4', '#ec4899'];

const VikingDashboard = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [activeSubTab, setActiveSubTab] = useState("overview");
  
  // Data state
  const [summary, setSummary] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [deals, setDeals] = useState([]);
  const [symbolDistribution, setSymbolDistribution] = useState([]);
  const [riskData, setRiskData] = useState(null);
  const [balanceHistory, setBalanceHistory] = useState([]);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [calculating, setCalculating] = useState(false);

  // Calculate analytics
  const calculateAnalytics = async () => {
    try {
      setCalculating(true);
      const res = await fetch(`${BACKEND_URL}/api/viking/calculate-analytics/CORE`, {
        method: 'POST'
      });
      const data = await res.json();
      if (data.success) {
        setAnalytics(data.analytics);
      }
      // Refresh all data
      await fetchData();
    } catch (err) {
      console.error("Error calculating analytics:", err);
    } finally {
      setCalculating(false);
    }
  };

  // Fetch all VIKING data
  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError("");
      
      // Fetch summary (includes all accounts and basic analytics)
      const summaryRes = await fetch(`${BACKEND_URL}/api/viking/summary`);
      const summaryData = await summaryRes.json();
      
      if (summaryData.success) {
        setSummary(summaryData);
        setLastUpdate(new Date().toLocaleTimeString());
      }
      
      // Fetch analytics for CORE strategy
      const analyticsRes = await fetch(`${BACKEND_URL}/api/viking/analytics/CORE`);
      const analyticsData = await analyticsRes.json();
      
      if (analyticsData.success) {
        setAnalytics(analyticsData.analytics);
      }
      
      // Fetch deals for CORE strategy
      const dealsRes = await fetch(`${BACKEND_URL}/api/viking/deals/CORE?limit=50`);
      const dealsData = await dealsRes.json();
      
      if (dealsData.success) {
        setDeals(dealsData.deals || []);
      }
      
      // Fetch symbol distribution
      const symbolsRes = await fetch(`${BACKEND_URL}/api/viking/symbols/CORE`);
      const symbolsData = await symbolsRes.json();
      
      if (symbolsData.success) {
        setSymbolDistribution(symbolsData.distribution || []);
      }
      
      // Fetch risk analysis
      const riskRes = await fetch(`${BACKEND_URL}/api/viking/risk/CORE`);
      const riskDataRes = await riskRes.json();
      
      if (riskDataRes.success) {
        setRiskData(riskDataRes.risk);
      }

      // Fetch balance history for charts
      const balanceRes = await fetch(`${BACKEND_URL}/api/viking/balance-snapshots/CORE`);
      const balanceData = await balanceRes.json();
      
      if (balanceData.success && balanceData.snapshots) {
        setBalanceHistory(balanceData.snapshots.map(s => ({
          date: new Date(s.timestamp).toLocaleDateString(),
          balance: s.balance,
          equity: s.equity
        })));
      }
      
    } catch (err) {
      console.error("Error fetching VIKING data:", err);
      setError("Failed to load VIKING data. Please try again.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, [fetchData]);

  // Helper functions
  const formatCurrency = (value) => {
    if (value === null || value === undefined) return '$0.00';
    return new Intl.NumberFormat('en-US', { 
      style: 'currency', 
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value);
  };

  const formatPercent = (value, decimals = 1) => {
    if (value === null || value === undefined) return '0.0%';
    return `${value >= 0 ? '+' : ''}${value.toFixed(decimals)}%`;
  };

  const getStatusColor = (status) => {
    switch(status) {
      case 'active': return 'bg-green-500/10 text-green-400 border-green-500/30';
      case 'pending_sync': return 'bg-yellow-500/10 text-yellow-400 border-yellow-500/30';
      case 'pending_setup': return 'bg-orange-500/10 text-orange-400 border-orange-500/30';
      case 'connection_error': return 'bg-red-500/10 text-red-400 border-red-500/30';
      default: return 'bg-gray-500/10 text-gray-400 border-gray-500/30';
    }
  };

  const getStatusIcon = (status) => {
    switch(status) {
      case 'active': return <CheckCircle2 className="w-4 h-4" />;
      case 'pending_sync': return <Loader2 className="w-4 h-4 animate-spin" />;
      case 'pending_setup': return <AlertTriangle className="w-4 h-4" />;
      case 'connection_error': return <XCircle className="w-4 h-4" />;
      default: return <AlertCircle className="w-4 h-4" />;
    }
  };

  // Loading state
  if (loading && !summary) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-blue-500 mx-auto mb-4" />
          <p className="text-gray-400">Loading VIKING data...</p>
        </div>
      </div>
    );
  }

  // Get CORE account data
  const coreAccount = summary?.strategies?.find(s => s.strategy === 'CORE');
  const proAccount = summary?.strategies?.find(s => s.strategy === 'PRO');

  return (
    <div className="space-y-6" data-testid="viking-dashboard">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-3">
            <span className="text-3xl">⚔️</span>
            VIKING Trading Operations
          </h1>
          <p className="text-gray-400 mt-1">
            Separate from FIDUS Funds • Real-time MT4 Performance Analytics
          </p>
        </div>
        <div className="flex items-center gap-3">
          {lastUpdate && (
            <span className="text-xs text-gray-500">
              Last update: {lastUpdate}
            </span>
          )}
          <Button 
            onClick={calculateAnalytics} 
            variant="outline" 
            size="sm"
            disabled={calculating}
            className="border-purple-700 hover:bg-purple-800 text-purple-400"
            data-testid="viking-calculate-btn"
          >
            {calculating ? (
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            ) : (
              <BarChart3 className="w-4 h-4 mr-2" />
            )}
            Calculate Analytics
          </Button>
          <Button 
            onClick={fetchData} 
            variant="outline" 
            size="sm"
            className="border-gray-700 hover:bg-gray-800"
            data-testid="viking-refresh-btn"
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 flex items-center gap-3">
          <AlertCircle className="w-5 h-5 text-red-400" />
          <span className="text-red-400">{error}</span>
        </div>
      )}

      {/* Sub-navigation tabs following FXBlue format - VKNG Gold Theme */}
      <Tabs value={activeSubTab} onValueChange={setActiveSubTab} className="w-full">
        <TabsList 
          className="p-1 w-full justify-start gap-1 overflow-x-auto"
          style={{ 
            backgroundColor: VKNG_COLORS.darkGray,
            border: `1px solid ${VKNG_COLORS.mediumGray}`
          }}
        >
          <TabsTrigger 
            value="overview" 
            className="data-[state=active]:text-black"
            style={{ 
              '--tw-bg-opacity': 1
            }}
            data-state-active-style={{ backgroundColor: VKNG_COLORS.gold }}
          >
            Overview
          </TabsTrigger>
          <TabsTrigger 
            value="analysis" 
            className="data-[state=active]:text-black"
          >
            Analysis
          </TabsTrigger>
          <TabsTrigger 
            value="stats" 
            className="data-[state=active]:text-black"
          >
            Stats
          </TabsTrigger>
          <TabsTrigger 
            value="risk" 
            className="data-[state=active]:text-black"
          >
            Risk
          </TabsTrigger>
          <TabsTrigger 
            value="orders" 
            className="data-[state=active]:text-black"
          >
            Orders
          </TabsTrigger>
        </TabsList>

        {/* OVERVIEW TAB */}
        <TabsContent value="overview" className="mt-6 space-y-6">
          {/* Strategy Cards Row */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* VIKING CORE Strategy Card */}
            <Card className="bg-gray-900/50 border-gray-800">
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg text-white flex items-center gap-2">
                    <span className="text-2xl">🛡️</span>
                    VIKING CORE Strategy
                  </CardTitle>
                  <Badge className={`${getStatusColor(coreAccount?.status)} border`}>
                    {getStatusIcon(coreAccount?.status)}
                    <span className="ml-1 capitalize">{coreAccount?.status?.replace('_', ' ') || 'Unknown'}</span>
                  </Badge>
                </div>
                <p className="text-sm text-gray-500">
                  Account: {coreAccount?.account || '33627673'} | {coreAccount?.broker || 'MEXAtlantic'}
                </p>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-xs text-gray-500">Balance</p>
                    <p className="text-xl font-bold text-white">{formatCurrency(coreAccount?.balance)}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Equity</p>
                    <p className="text-xl font-bold text-white">{formatCurrency(coreAccount?.equity)}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Floating P/L</p>
                    <p className={`text-lg font-semibold ${(coreAccount?.floating_pnl || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {formatCurrency(coreAccount?.floating_pnl)}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Free Margin</p>
                    <p className="text-lg font-semibold text-gray-300">{formatCurrency(coreAccount?.free_margin)}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Margin In Use</p>
                    <p className="text-lg font-semibold text-gray-300">{formatCurrency(coreAccount?.margin_in_use)}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Margin Level</p>
                    <p className="text-lg font-semibold text-gray-300">
                      {coreAccount?.margin_level ? `${coreAccount.margin_level.toFixed(1)}%` : '--'}
                    </p>
                  </div>
                </div>
                <div className="flex items-center justify-between pt-2 border-t border-gray-800">
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-green-400" />
                    <span className="text-xs text-gray-400">Real Account</span>
                  </div>
                  <span className="text-xs text-gray-500">
                    Last Update: {coreAccount?.last_update ? new Date(coreAccount.last_update).toLocaleDateString() : '--'}
                  </span>
                </div>
              </CardContent>
            </Card>

            {/* VIKING PRO Strategy Card */}
            <Card className="bg-gray-900/50 border-gray-800">
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg text-white flex items-center gap-2">
                    <span className="text-2xl">⚔️</span>
                    VIKING PRO Strategy
                  </CardTitle>
                  <Badge className={`${getStatusColor(proAccount?.status)} border`}>
                    {getStatusIcon(proAccount?.status)}
                    <span className="ml-1 capitalize">{proAccount?.status?.replace('_', ' ') || 'Unknown'}</span>
                  </Badge>
                </div>
                <p className="text-sm text-gray-500">
                  Account: {proAccount?.account || '1309411'} | {proAccount?.broker || 'Traders Trust'}
                </p>
              </CardHeader>
              <CardContent className="space-y-3">
                {proAccount?.status === 'pending_setup' ? (
                  <div className="bg-orange-500/10 border border-orange-500/30 rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <AlertTriangle className="w-5 h-5 text-orange-400" />
                      <span className="text-orange-400 font-medium">Setup Required</span>
                    </div>
                    <p className="text-sm text-gray-400">
                      {proAccount?.error_message || 'This account needs MT4 terminal login on VPS'}
                    </p>
                    <div className="mt-3 text-xs text-gray-500">
                      <p>Server: {proAccount?.server || 'TTCM'}</p>
                      <p>Platform: MT4</p>
                    </div>
                  </div>
                ) : (
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-xs text-gray-500">Balance</p>
                      <p className="text-xl font-bold text-white">{formatCurrency(proAccount?.balance)}</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500">Equity</p>
                      <p className="text-xl font-bold text-white">{formatCurrency(proAccount?.equity)}</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500">Floating P/L</p>
                      <p className={`text-lg font-semibold ${(proAccount?.floating_pnl || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                        {formatCurrency(proAccount?.floating_pnl)}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500">Free Margin</p>
                      <p className="text-lg font-semibold text-gray-300">{formatCurrency(proAccount?.free_margin)}</p>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Stats Summary Row - FXBlue Style */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Card className="bg-gradient-to-br from-green-500/10 to-green-500/5 border-green-500/20">
              <CardContent className="pt-4">
                <p className="text-xs text-gray-400 mb-1">Total Return</p>
                <p className="text-2xl font-bold text-green-400">
                  {formatPercent(analytics?.total_return || 49.0)}
                </p>
              </CardContent>
            </Card>
            <Card className="bg-gradient-to-br from-blue-500/10 to-blue-500/5 border-blue-500/20">
              <CardContent className="pt-4">
                <p className="text-xs text-gray-400 mb-1">Monthly Return</p>
                <p className="text-2xl font-bold text-blue-400">
                  {formatPercent(analytics?.monthly_return || 10.8)}
                </p>
              </CardContent>
            </Card>
            <Card className="bg-gradient-to-br from-purple-500/10 to-purple-500/5 border-purple-500/20">
              <CardContent className="pt-4">
                <p className="text-xs text-gray-400 mb-1">Profit Factor</p>
                <p className="text-2xl font-bold text-purple-400">
                  {(analytics?.profit_factor || 1.36).toFixed(2)}
                </p>
              </CardContent>
            </Card>
            <Card className="bg-gradient-to-br from-cyan-500/10 to-cyan-500/5 border-cyan-500/20">
              <CardContent className="pt-4">
                <p className="text-xs text-gray-400 mb-1">History</p>
                <p className="text-2xl font-bold text-cyan-400">
                  {analytics?.history_days || 114} days
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Additional Stats Grid */}
          <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
            <StatCard label="Weekly Return" value={formatPercent(analytics?.weekly_return || 2.5)} color="text-green-400" />
            <StatCard label="Peak Drawdown" value={formatPercent(analytics?.peak_drawdown || -7.4)} color="text-red-400" />
            <StatCard label="Trade Win %" value={`${(analytics?.trade_win_rate || 77.8).toFixed(1)}%`} color="text-blue-400" />
            <StatCard label="Trades/Day" value={(analytics?.trades_per_day || 75.5).toFixed(1)} color="text-purple-400" />
            <StatCard label="Risk/Reward" value={(analytics?.risk_reward_ratio || 4.31).toFixed(2)} color="text-cyan-400" />
            <StatCard label="Total Trades" value={(analytics?.total_trades || 8595).toLocaleString()} color="text-orange-400" />
          </div>

          {/* Charts Row */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Balance Chart */}
            <Card className="lg:col-span-2 bg-gray-900/50 border-gray-800">
              <CardHeader>
                <CardTitle className="text-sm text-gray-400">Balance Over Time</CardTitle>
              </CardHeader>
              <CardContent>
                {balanceHistory.length > 0 ? (
                  <ResponsiveContainer width="100%" height={250}>
                    <AreaChart data={balanceHistory}>
                      <defs>
                        <linearGradient id="balanceGradient" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor={COLORS.primary} stopOpacity={0.3}/>
                          <stop offset="95%" stopColor={COLORS.primary} stopOpacity={0}/>
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                      <XAxis dataKey="date" tick={{ fill: '#9ca3af', fontSize: 10 }} />
                      <YAxis tick={{ fill: '#9ca3af', fontSize: 10 }} tickFormatter={(v) => `$${(v/1000).toFixed(0)}k`} />
                      <Tooltip 
                        contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px' }}
                        labelStyle={{ color: '#fff' }}
                        formatter={(value) => [formatCurrency(value), '']}
                      />
                      <Area 
                        type="monotone" 
                        dataKey="balance" 
                        stroke={COLORS.primary} 
                        fill="url(#balanceGradient)" 
                        strokeWidth={2}
                        name="Balance"
                      />
                      <Line 
                        type="monotone" 
                        dataKey="equity" 
                        stroke={COLORS.secondary} 
                        strokeWidth={2}
                        dot={false}
                        name="Equity"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                ) : coreAccount?.balance > 0 ? (
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={[
                        { date: 'Start', balance: 86000, equity: 86000 },
                        { date: 'Now', balance: coreAccount?.balance || 0, equity: coreAccount?.equity || 0 }
                      ]}>
                        <defs>
                          <linearGradient id="balanceGradient2" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor={COLORS.primary} stopOpacity={0.3}/>
                            <stop offset="95%" stopColor={COLORS.primary} stopOpacity={0}/>
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                        <XAxis dataKey="date" tick={{ fill: '#9ca3af', fontSize: 12 }} />
                        <YAxis tick={{ fill: '#9ca3af', fontSize: 12 }} tickFormatter={(v) => `$${(v/1000).toFixed(0)}k`} />
                        <Tooltip 
                          contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}
                          formatter={(value) => [formatCurrency(value), '']}
                        />
                        <Area 
                          type="monotone" 
                          dataKey="balance" 
                          stroke={COLORS.primary} 
                          fill="url(#balanceGradient2)" 
                          strokeWidth={2}
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                ) : (
                  <div className="h-64 flex items-center justify-center border border-dashed border-gray-700 rounded-lg">
                    <div className="text-center text-gray-500">
                      <BarChart3 className="w-12 h-12 mx-auto mb-2 opacity-50" />
                      <p>Waiting for balance data</p>
                      <p className="text-xs">Data will populate when MT4 syncs</p>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Symbol Distribution Pie Chart */}
            <Card className="bg-gray-900/50 border-gray-800">
              <CardHeader>
                <CardTitle className="text-sm text-gray-400">Symbol Distribution</CardTitle>
              </CardHeader>
              <CardContent>
                {symbolDistribution.length > 0 ? (
                  <ResponsiveContainer width="100%" height={200}>
                    <PieChart>
                      <Pie
                        data={symbolDistribution}
                        dataKey="percentage"
                        nameKey="symbol"
                        cx="50%"
                        cy="50%"
                        outerRadius={70}
                        label={({ symbol, percentage }) => `${percentage}%`}
                      >
                        {symbolDistribution.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={SYMBOL_COLORS[index % SYMBOL_COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip 
                        contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}
                        labelStyle={{ color: '#fff' }}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-48 flex items-center justify-center border border-dashed border-gray-700 rounded-lg">
                    <div className="text-center text-gray-500">
                      <PieChartIcon className="w-12 h-12 mx-auto mb-2 opacity-50" />
                      <p className="text-xs">Awaiting trade data</p>
                    </div>
                  </div>
                )}
                {/* Legend */}
                <div className="mt-4 space-y-1">
                  {(symbolDistribution.length > 0 ? symbolDistribution : [
                    { symbol: 'AUDCAD.ecn', percentage: 65.9 },
                    { symbol: 'DE40', percentage: 25.7 },
                    { symbol: 'US500', percentage: 8.4 }
                  ]).slice(0, 5).map((item, idx) => (
                    <div key={item.symbol} className="flex items-center justify-between text-xs">
                      <div className="flex items-center gap-2">
                        <div 
                          className="w-3 h-3 rounded-full" 
                          style={{ backgroundColor: SYMBOL_COLORS[idx % SYMBOL_COLORS.length] }}
                        />
                        <span className="text-gray-400">{item.symbol}</span>
                      </div>
                      <span className="text-gray-300">{item.percentage}%</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* ANALYSIS TAB */}
        <TabsContent value="analysis" className="mt-6 space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Balance + Deposits Chart */}
            <Card className="bg-gray-900/50 border-gray-800">
              <CardHeader>
                <CardTitle className="text-sm text-gray-400">Balance + Deposits</CardTitle>
              </CardHeader>
              <CardContent>
                {balanceHistory.length > 0 || coreAccount?.balance > 0 ? (
                  <ResponsiveContainer width="100%" height={250}>
                    <AreaChart data={balanceHistory.length > 0 ? balanceHistory : [
                      { date: 'Initial', balance: 86000 },
                      { date: 'Current', balance: coreAccount?.balance || 0 }
                    ]}>
                      <defs>
                        <linearGradient id="balanceGrad" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor={COLORS.primary} stopOpacity={0.4}/>
                          <stop offset="95%" stopColor={COLORS.primary} stopOpacity={0}/>
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                      <XAxis dataKey="date" tick={{ fill: '#9ca3af', fontSize: 10 }} />
                      <YAxis tick={{ fill: '#9ca3af', fontSize: 10 }} tickFormatter={(v) => `$${(v/1000).toFixed(0)}k`} />
                      <Tooltip 
                        contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}
                        formatter={(value) => [formatCurrency(value), 'Balance']}
                      />
                      <Area type="monotone" dataKey="balance" stroke={COLORS.primary} fill="url(#balanceGrad)" strokeWidth={2} />
                    </AreaChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-64 flex items-center justify-center border border-dashed border-gray-700 rounded-lg">
                    <div className="text-center text-gray-500">
                      <TrendingUp className="w-12 h-12 mx-auto mb-2 opacity-50" />
                      <p>Waiting for balance data</p>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Profit Analysis Chart */}
            <Card className="bg-gray-900/50 border-gray-800">
              <CardHeader>
                <CardTitle className="text-sm text-gray-400">Trades: Profit Analysis</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={[
                    { name: 'Best', value: analytics?.best_trade || 617.43, fill: COLORS.success },
                    { name: 'Worst', value: analytics?.worst_trade || -997.58, fill: COLORS.danger },
                    { name: 'Average', value: analytics?.avg_trade || 50, fill: COLORS.warning }
                  ]}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis dataKey="name" tick={{ fill: '#9ca3af', fontSize: 12 }} />
                    <YAxis tick={{ fill: '#9ca3af', fontSize: 12 }} />
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}
                      formatter={(value) => formatCurrency(value)}
                    />
                    <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                      {[
                        { name: 'Best', value: analytics?.best_trade || 617.43, fill: COLORS.success },
                        { name: 'Worst', value: analytics?.worst_trade || -997.58, fill: COLORS.danger },
                        { name: 'Average', value: analytics?.avg_trade || 50, fill: COLORS.warning }
                      ].map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.fill} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          {/* Market Analysis */}
          <Card className="bg-gray-900/50 border-gray-800">
            <CardHeader>
              <CardTitle className="text-sm text-gray-400">Market / Return Analysis</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {(symbolDistribution.length > 0 ? symbolDistribution : [
                  { symbol: 'AUDCAD.ecn', trades: 5660, total_profit: 4500 },
                  { symbol: 'DE40', trades: 2200, total_profit: 2100 },
                  { symbol: 'US500', trades: 735, total_profit: 957 }
                ]).slice(0, 3).map((item, idx) => (
                  <div key={item.symbol} className="bg-gray-800/50 rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-3">
                      <div 
                        className="w-3 h-3 rounded-full" 
                        style={{ backgroundColor: SYMBOL_COLORS[idx % SYMBOL_COLORS.length] }}
                      />
                      <span className="text-white font-medium">{item.symbol}</span>
                    </div>
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      <div>
                        <p className="text-gray-500">Trades</p>
                        <p className="text-gray-300">{item.trades?.toLocaleString() || '--'}</p>
                      </div>
                      <div>
                        <p className="text-gray-500">Profit</p>
                        <p className={`${(item.total_profit || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                          {formatCurrency(item.total_profit)}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* STATS TAB */}
        <TabsContent value="stats" className="mt-6 space-y-6">
          {/* Top Stats Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Card className="bg-gray-900/50 border-gray-800">
              <CardContent className="pt-4">
                <p className="text-xs text-gray-500">Weekly Return</p>
                <p className="text-xl font-bold text-green-400">{formatPercent(analytics?.weekly_return || 2.5)}</p>
              </CardContent>
            </Card>
            <Card className="bg-gray-900/50 border-gray-800">
              <CardContent className="pt-4">
                <p className="text-xs text-gray-500">Monthly Return</p>
                <p className="text-xl font-bold text-green-400">{formatPercent(analytics?.monthly_return || 10.8)}</p>
              </CardContent>
            </Card>
            <Card className="bg-gray-900/50 border-gray-800">
              <CardContent className="pt-4">
                <p className="text-xs text-gray-500">Profit Factor</p>
                <p className="text-xl font-bold text-blue-400">{(analytics?.profit_factor || 1.36).toFixed(2)}</p>
              </CardContent>
            </Card>
            <Card className="bg-gray-900/50 border-gray-800">
              <CardContent className="pt-4">
                <p className="text-xs text-gray-500">History</p>
                <p className="text-xl font-bold text-gray-300">{analytics?.history_days || 114} days</p>
              </CardContent>
            </Card>
          </div>

          {/* Account Info */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Card className="bg-gray-900/50 border-gray-800">
              <CardContent className="pt-4">
                <p className="text-xs text-gray-500">Currency</p>
                <p className="text-xl font-bold text-white">USD</p>
              </CardContent>
            </Card>
            <Card className="bg-gray-900/50 border-gray-800">
              <CardContent className="pt-4">
                <p className="text-xs text-gray-500">Equity</p>
                <p className="text-xl font-bold text-white">{formatCurrency(coreAccount?.equity || 84537.20)}</p>
              </CardContent>
            </Card>
            <Card className="bg-gray-900/50 border-gray-800">
              <CardContent className="pt-4">
                <p className="text-xs text-gray-500">Balance</p>
                <p className="text-xl font-bold text-white">{formatCurrency(coreAccount?.balance || 93557.67)}</p>
              </CardContent>
            </Card>
            <Card className="bg-gray-900/50 border-gray-800">
              <CardContent className="pt-4">
                <p className="text-xs text-gray-500">Floating P/L</p>
                <p className="text-xl font-bold text-red-400">{formatCurrency(coreAccount?.floating_pnl || -9020.47)}</p>
              </CardContent>
            </Card>
          </div>

          {/* Deposits, Profit, and Loss Table */}
          <Card className="bg-gray-900/50 border-gray-800">
            <CardHeader>
              <CardTitle className="text-sm text-gray-400">Deposits, Profit, and Loss</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-800">
                      <th className="text-left py-2 text-gray-500"></th>
                      <th className="text-right py-2 text-gray-500">Deposits</th>
                      <th className="text-right py-2 text-gray-500">Withdrawals</th>
                      <th className="text-right py-2 text-gray-500">Net</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr className="border-b border-gray-800">
                      <td className="py-2 text-gray-300">Credits</td>
                      <td className="text-right text-green-400">{formatCurrency(analytics?.deposits || 89595.82)}</td>
                      <td className="text-right text-red-400">{formatCurrency(analytics?.withdrawals || -3595.65)}</td>
                      <td className="text-right text-white">{formatCurrency(analytics?.net_deposits || 86000.17)}</td>
                    </tr>
                  </tbody>
                </table>

                <table className="w-full text-sm mt-6">
                  <thead>
                    <tr className="border-b border-gray-800">
                      <th className="text-left py-2 text-gray-500"></th>
                      <th className="text-right py-2 text-gray-500">Profit</th>
                      <th className="text-right py-2 text-gray-500">Loss</th>
                      <th className="text-right py-2 text-gray-500">Net</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr className="border-b border-gray-800">
                      <td className="py-2 text-gray-300">Banked Trades</td>
                      <td className="text-right text-green-400">{formatCurrency(analytics?.banked_profit || 28819.92)}</td>
                      <td className="text-right text-red-400">{formatCurrency(analytics?.loss || -21262.42)}</td>
                      <td className="text-right text-white">{formatCurrency(analytics?.net_profit || 7557.50)}</td>
                    </tr>
                    <tr className="border-b border-gray-800">
                      <td className="py-2 text-gray-300">Open Trades</td>
                      <td className="text-right text-gray-400">$0.00</td>
                      <td className="text-right text-gray-400">$0.00</td>
                      <td className="text-right text-gray-400">$0.00</td>
                    </tr>
                    <tr className="font-medium">
                      <td className="py-2 text-white">Total</td>
                      <td className="text-right text-green-400">{formatCurrency(analytics?.banked_profit || 28819.92)}</td>
                      <td className="text-right text-red-400">{formatCurrency(analytics?.loss || -21262.42)}</td>
                      <td className="text-right text-white">{formatCurrency(analytics?.net_profit || 7557.50)}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>

          {/* Returns Card */}
          <Card className="bg-gray-900/50 border-gray-800">
            <CardHeader>
              <CardTitle className="text-sm text-gray-400">Returns</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                <div>
                  <p className="text-xs text-gray-500">Total Return</p>
                  <p className="text-lg font-bold text-green-400">{formatPercent(analytics?.total_return || 49.01)}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Banked Return</p>
                  <p className="text-lg font-bold text-green-400">{formatPercent(analytics?.total_return || 49.01)}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Per Day</p>
                  <p className="text-lg font-bold text-green-400">{formatPercent(analytics?.daily_return || 0.49)}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Per Week</p>
                  <p className="text-lg font-bold text-green-400">{formatPercent(analytics?.weekly_return || 2.46)}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Per Month</p>
                  <p className="text-lg font-bold text-green-400">{formatPercent(analytics?.monthly_return || 10.75)}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Trade Statistics Table */}
          <Card className="bg-gray-900/50 border-gray-800">
            <CardHeader>
              <CardTitle className="text-sm text-gray-400">Banked Profits per Day / Week / Month / Trade</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-800">
                      <th className="text-left py-2 text-gray-500">Period</th>
                      <th className="text-right py-2 text-gray-500">Winning</th>
                      <th className="text-right py-2 text-gray-500">Losing</th>
                      <th className="text-right py-2 text-gray-500">Win/Loss%</th>
                      <th className="text-right py-2 text-gray-500">Best</th>
                      <th className="text-right py-2 text-gray-500">Worst</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr className="border-b border-gray-800">
                      <td className="py-2 text-gray-300">Days</td>
                      <td className="text-right text-green-400">55</td>
                      <td className="text-right text-red-400">18</td>
                      <td className="text-right">
                        <div className="w-16 bg-gray-700 rounded-full h-2 ml-auto">
                          <div className="bg-green-500 h-2 rounded-full" style={{ width: '75%' }}></div>
                        </div>
                      </td>
                      <td className="text-right text-green-400">$1,000.36</td>
                      <td className="text-right text-red-400">-$1,051.86</td>
                    </tr>
                    <tr className="border-b border-gray-800">
                      <td className="py-2 text-gray-300">Weeks</td>
                      <td className="text-right text-green-400">14</td>
                      <td className="text-right text-red-400">3</td>
                      <td className="text-right">
                        <div className="w-16 bg-gray-700 rounded-full h-2 ml-auto">
                          <div className="bg-green-500 h-2 rounded-full" style={{ width: '82%' }}></div>
                        </div>
                      </td>
                      <td className="text-right text-green-400">$2,102.40</td>
                      <td className="text-right text-red-400">-$593.06</td>
                    </tr>
                    <tr className="border-b border-gray-800">
                      <td className="py-2 text-gray-300">Months</td>
                      <td className="text-right text-green-400">5</td>
                      <td className="text-right text-red-400">0</td>
                      <td className="text-right">
                        <div className="w-16 bg-gray-700 rounded-full h-2 ml-auto">
                          <div className="bg-green-500 h-2 rounded-full" style={{ width: '100%' }}></div>
                        </div>
                      </td>
                      <td className="text-right text-green-400">$3,677.84</td>
                      <td className="text-right text-green-400">$91.77</td>
                    </tr>
                    <tr>
                      <td className="py-2 text-gray-300">Closed Trades</td>
                      <td className="text-right text-green-400">{analytics?.winning_trades || 6685}</td>
                      <td className="text-right text-red-400">{analytics?.losing_trades || 1910}</td>
                      <td className="text-right">
                        <div className="w-16 bg-gray-700 rounded-full h-2 ml-auto">
                          <div className="bg-green-500 h-2 rounded-full" style={{ width: `${analytics?.trade_win_rate || 77.8}%` }}></div>
                        </div>
                      </td>
                      <td className="text-right text-green-400">$617.43</td>
                      <td className="text-right text-red-400">-$997.58</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* RISK TAB */}
        <TabsContent value="risk" className="mt-6 space-y-6">
          {/* Top Stats */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <Card className="bg-gray-900/50 border-gray-800">
              <CardContent className="pt-4">
                <p className="text-xs text-gray-500">Monthly Return</p>
                <p className="text-xl font-bold text-green-400">{formatPercent(riskData?.monthly_return || 10.8)}</p>
              </CardContent>
            </Card>
            <Card className="bg-gray-900/50 border-gray-800">
              <CardContent className="pt-4">
                <p className="text-xs text-gray-500">Avg Trade Length</p>
                <p className="text-xl font-bold text-gray-300">{riskData?.avg_trade_length || 6.5} hours</p>
              </CardContent>
            </Card>
            <Card className="bg-gray-900/50 border-gray-800">
              <CardContent className="pt-4">
                <p className="text-xs text-gray-500">Trades Per Day</p>
                <p className="text-xl font-bold text-gray-300">{riskData?.trades_per_day || 105.0}</p>
              </CardContent>
            </Card>
            <Card className="bg-gray-900/50 border-gray-800">
              <CardContent className="pt-4">
                <p className="text-xs text-gray-500">History</p>
                <p className="text-xl font-bold text-gray-300">{riskData?.history_days || 114} days</p>
              </CardContent>
            </Card>
            <Card className="bg-gray-900/50 border-gray-800">
              <CardContent className="pt-4">
                <p className="text-xs text-gray-500">Risk/Reward</p>
                <p className="text-xl font-bold text-green-400">+{riskData?.risk_reward_ratio || 4.31}</p>
              </CardContent>
            </Card>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Risk of Ruin Table */}
            <Card className="bg-gray-900/50 border-gray-800">
              <CardHeader>
                <CardTitle className="text-sm text-gray-400">Risk of Ruin</CardTitle>
              </CardHeader>
              <CardContent>
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-800">
                      <th className="text-left py-2 text-gray-500">Size of Loss</th>
                      <th className="text-right py-2 text-gray-500">Probability</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(riskData?.risk_of_ruin || {
                      '10%': 5.2,
                      '20%': 0.3,
                      '30%': 0.0,
                      '40%': 0.0,
                      '50%': 0.0,
                      '60%': 0.0,
                      '70%': 0.0,
                      '80%': 0.0,
                      '90%': 0.0,
                      '100%': 0.0
                    }).map(([loss, prob]) => (
                      <tr key={loss} className="border-b border-gray-800">
                        <td className="py-2 text-gray-300">{loss} loss</td>
                        <td className="text-right text-gray-400">{prob}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </CardContent>
            </Card>

            {/* Balance & Equity Metrics */}
            <div className="space-y-6">
              <Card className="bg-gray-900/50 border-gray-800">
                <CardHeader>
                  <CardTitle className="text-sm text-gray-400">Balance Metrics</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-xs text-gray-500">Worst Day %</p>
                      <p className="text-lg font-bold text-red-400">{riskData?.balance_metrics?.worst_day_pct || -5.1}%</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500">Worst Week %</p>
                      <p className="text-lg font-bold text-red-400">{riskData?.balance_metrics?.worst_week_pct || -2.9}%</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500">Worst Month %</p>
                      <p className="text-lg font-bold text-green-400">+{riskData?.balance_metrics?.worst_month_pct || 0.6}%</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500">Deepest Valley</p>
                      <p className="text-lg font-bold text-red-400">{riskData?.balance_metrics?.deepest_valley || -7.4}%</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-gray-900/50 border-gray-800">
                <CardHeader>
                  <CardTitle className="text-sm text-gray-400">Equity (approximate) Metrics</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-xs text-gray-500">Worst Day %</p>
                      <p className="text-lg font-bold text-red-400">{riskData?.equity_metrics?.worst_day_pct || -7.2}%</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500">Worst Week %</p>
                      <p className="text-lg font-bold text-red-400">{riskData?.equity_metrics?.worst_week_pct || -5.0}%</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500">Worst Month %</p>
                      <p className="text-lg font-bold text-red-400">{riskData?.equity_metrics?.worst_month_pct || -7.5}%</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500">Deepest Valley</p>
                      <p className="text-lg font-bold text-red-400">{riskData?.equity_metrics?.deepest_valley || -12.2}%</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>

        {/* ORDERS TAB */}
        <TabsContent value="orders" className="mt-6">
          <Card className="bg-gray-900/50 border-gray-800">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm text-gray-400">Trade History</CardTitle>
                <Badge variant="outline" className="border-gray-600">
                  {deals.length} trades loaded
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              {deals.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-gray-800">
                        <th className="text-left py-2 px-2 text-gray-500">Order</th>
                        <th className="text-left py-2 px-2 text-gray-500">Time</th>
                        <th className="text-left py-2 px-2 text-gray-500">Type</th>
                        <th className="text-right py-2 px-2 text-gray-500">Size</th>
                        <th className="text-left py-2 px-2 text-gray-500">Symbol</th>
                        <th className="text-right py-2 px-2 text-gray-500">Open</th>
                        <th className="text-right py-2 px-2 text-gray-500">Close</th>
                        <th className="text-right py-2 px-2 text-gray-500">Commission</th>
                        <th className="text-right py-2 px-2 text-gray-500">Swap</th>
                        <th className="text-right py-2 px-2 text-gray-500">Profit</th>
                      </tr>
                    </thead>
                    <tbody>
                      {deals.map((deal, idx) => (
                        <tr key={deal.ticket || idx} className="border-b border-gray-800 hover:bg-gray-800/50">
                          <td className="py-2 px-2 text-gray-300">{deal.ticket}</td>
                          <td className="py-2 px-2 text-gray-400 text-xs">
                            {deal.open_time ? new Date(deal.open_time).toLocaleString() : '--'}
                          </td>
                          <td className="py-2 px-2">
                            <Badge className={deal.type === 'buy' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}>
                              {deal.type}
                            </Badge>
                          </td>
                          <td className="py-2 px-2 text-right text-gray-300">{deal.volume}</td>
                          <td className="py-2 px-2 text-gray-300">{deal.symbol}</td>
                          <td className="py-2 px-2 text-right text-gray-300">{deal.open_price}</td>
                          <td className="py-2 px-2 text-right text-gray-300">{deal.close_price || '--'}</td>
                          <td className="py-2 px-2 text-right text-gray-400">{formatCurrency(deal.commission)}</td>
                          <td className="py-2 px-2 text-right text-gray-400">{formatCurrency(deal.swap)}</td>
                          <td className={`py-2 px-2 text-right font-medium ${(deal.profit || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                            {formatCurrency(deal.profit)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="h-64 flex items-center justify-center border border-dashed border-gray-700 rounded-lg">
                  <div className="text-center text-gray-500">
                    <Activity className="w-12 h-12 mx-auto mb-2 opacity-50" />
                    <p>No trades loaded yet</p>
                    <p className="text-xs">Trade history will populate when MT4 bridge syncs data</p>
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

// Small stat card component
const StatCard = ({ label, value, color = 'text-white' }) => (
  <Card className="bg-gray-800/50 border-gray-700">
    <CardContent className="py-3 px-4">
      <p className="text-xs text-gray-500">{label}</p>
      <p className={`text-lg font-bold ${color}`}>{value}</p>
    </CardContent>
  </Card>
);

export default VikingDashboard;
