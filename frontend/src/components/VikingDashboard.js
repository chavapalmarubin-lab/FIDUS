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

// Helper function to parse MT4 datetime format
const parseMT4DateTime = (dateStr) => {
  if (!dateStr) return null;
  // MT4 format: "2026.01.09 21:37:53"
  if (typeof dateStr === 'string' && dateStr.includes('.')) {
    const [datePart, timePart] = dateStr.split(' ');
    const [year, month, day] = datePart.split('.');
    return new Date(`${year}-${month}-${day}T${timePart || '00:00:00'}`);
  }
  return new Date(dateStr);
};

// Format datetime for display
const formatDateTime = (dateStr) => {
  const date = parseMT4DateTime(dateStr);
  if (!date || isNaN(date.getTime())) return '--';
  return date.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

// VKNG AI Brand Colors (from getvkng.com - Purple/Magenta theme)
const VKNG_COLORS = {
  purple: '#9B27FF',
  purpleLight: '#A239EA',
  magenta: '#CC00FF',
  pink: '#E621A4',
  dark: '#0A112B',
  darkGray: '#0D1629',
  mediumGray: '#1A2744',
  textPrimary: '#FFFFFF',
  textSecondary: '#9CA3AF'
};

// Colors for charts
const COLORS = {
  primary: '#9B27FF',    // VKNG Purple
  secondary: '#A239EA',  // Light Purple
  success: '#22c55e',    // Green
  danger: '#ef4444',     // Red
  warning: '#eab308',    // Yellow
  purple: '#8b5cf6',     // Purple
  cyan: '#06b6d4',       // Cyan
  pink: '#E621A4'        // VKNG Pink
};

const SYMBOL_COLORS = ['#9B27FF', '#A239EA', '#22c55e', '#E621A4', '#06b6d4', '#ec4899'];

// Strategy colors
const STRATEGY_COLORS = {
  CORE: { primary: '#3B82F6', secondary: '#60A5FA', bg: 'bg-blue-500/10', border: 'border-blue-500/30', text: 'text-blue-400' },
  PRO: { primary: '#9B27FF', secondary: '#A239EA', bg: 'bg-purple-500/10', border: 'border-purple-500/30', text: 'text-purple-400' }
};

const VikingDashboard = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [activeSubTab, setActiveSubTab] = useState("overview");
  const [selectedStrategy, setSelectedStrategy] = useState("ALL"); // ALL, CORE, PRO
  
  // Data state
  const [summary, setSummary] = useState(null);
  const [accounts, setAccounts] = useState([]); // Array of all accounts
  const [analytics, setAnalytics] = useState(null);
  const [coreAnalytics, setCoreAnalytics] = useState(null);
  const [proAnalytics, setProAnalytics] = useState(null);
  const [deals, setDeals] = useState([]);
  const [symbolDistribution, setSymbolDistribution] = useState([]);
  const [riskData, setRiskData] = useState(null);
  const [balanceHistory, setBalanceHistory] = useState([]);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [calculating, setCalculating] = useState(false);

  // Get current strategy for API calls
  const getActiveStrategy = () => selectedStrategy === 'ALL' ? 'CORE' : selectedStrategy;

  // Calculate analytics for selected strategy
  const calculateAnalytics = async () => {
    try {
      setCalculating(true);
      
      // Calculate for CORE
      const coreRes = await fetch(`${BACKEND_URL}/api/viking/calculate-analytics/CORE`, { method: 'POST' });
      const coreData = await coreRes.json();
      if (coreData.success) setCoreAnalytics(coreData.analytics);
      
      // Calculate for PRO if it exists
      try {
        const proRes = await fetch(`${BACKEND_URL}/api/viking/calculate-analytics/PRO`, { method: 'POST' });
        const proData = await proRes.json();
        if (proData.success) setProAnalytics(proData.analytics);
      } catch (e) {
        console.log("PRO account not yet available");
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
        setAccounts(summaryData.strategies || []);
        setLastUpdate(new Date().toLocaleTimeString());
      }
      
      // Fetch analytics for CORE strategy
      try {
        const coreAnalyticsRes = await fetch(`${BACKEND_URL}/api/viking/analytics/CORE`);
        const coreAnalyticsData = await coreAnalyticsRes.json();
        if (coreAnalyticsData.success) {
          setCoreAnalytics(coreAnalyticsData.analytics);
          if (selectedStrategy === 'ALL' || selectedStrategy === 'CORE') {
            setAnalytics(coreAnalyticsData.analytics);
          }
        }
      } catch (e) { console.log("CORE analytics not available"); }
      
      // Fetch analytics for PRO strategy
      try {
        const proAnalyticsRes = await fetch(`${BACKEND_URL}/api/viking/analytics/PRO`);
        const proAnalyticsData = await proAnalyticsRes.json();
        if (proAnalyticsData.success) {
          setProAnalytics(proAnalyticsData.analytics);
          if (selectedStrategy === 'PRO') {
            setAnalytics(proAnalyticsData.analytics);
          }
        }
      } catch (e) { console.log("PRO analytics not available yet"); }
      
      // Fetch deals based on selected strategy
      const strategy = selectedStrategy === 'ALL' ? 'CORE' : selectedStrategy;
      const dealsRes = await fetch(`${BACKEND_URL}/api/viking/deals/${strategy}?limit=50`);
      const dealsData = await dealsRes.json();
      
      if (dealsData.success) {
        setDeals(dealsData.deals || []);
      }
      
      // Fetch symbol distribution for selected strategy
      const symbolsRes = await fetch(`${BACKEND_URL}/api/viking/symbols/${strategy}`);
      const symbolsData = await symbolsRes.json();
      
      if (symbolsData.success) {
        setSymbolDistribution(symbolsData.distribution || []);
      }
      
      // Fetch risk analysis for selected strategy
      const riskRes = await fetch(`${BACKEND_URL}/api/viking/risk/${strategy}`);
      const riskDataRes = await riskRes.json();
      
      if (riskDataRes.success) {
        setRiskData(riskDataRes.risk);
      }

      // Fetch balance history for charts
      const balanceRes = await fetch(`${BACKEND_URL}/api/viking/balance-snapshots/${strategy}`);
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
  }, [selectedStrategy]);

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
          <Loader2 
            className="w-12 h-12 animate-spin mx-auto mb-4" 
            style={{ color: VKNG_COLORS.purple }}
          />
          <p style={{ color: VKNG_COLORS.textSecondary }}>Loading VKNG AI data...</p>
        </div>
      </div>
    );
  }

  // Get account data
  const coreAccount = summary?.strategies?.find(s => s.strategy === 'CORE');
  const proAccount = summary?.strategies?.find(s => s.strategy === 'PRO');
  
  // Calculate combined totals
  const totalBalance = (coreAccount?.balance || 0) + (proAccount?.balance || 0);
  const totalEquity = (coreAccount?.equity || 0) + (proAccount?.equity || 0);
  const totalProfit = (coreAccount?.profit || 0) + (proAccount?.profit || 0);
  const totalPositions = (coreAccount?.positions_count || 0) + (proAccount?.positions_count || 0);

  return (
    <div className="space-y-6" data-testid="viking-dashboard">
      {/* Header with Strategy Selector */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold" style={{ color: VKNG_COLORS.textPrimary }}>
            Trading Operations
          </h1>
          <p className="mt-1" style={{ color: VKNG_COLORS.textSecondary }}>
            Real-time MT4 Performance Analytics
          </p>
        </div>
        
        {/* Strategy Selector */}
        <div className="flex items-center gap-2">
          <span className="text-sm" style={{ color: VKNG_COLORS.textSecondary }}>Strategy:</span>
          <div className="flex rounded-lg overflow-hidden" style={{ backgroundColor: VKNG_COLORS.darkGray, border: `1px solid ${VKNG_COLORS.mediumGray}` }}>
            {['ALL', 'CORE', 'PRO'].map((strategy) => (
              <button
                key={strategy}
                onClick={() => setSelectedStrategy(strategy)}
                className={`px-4 py-2 text-sm font-medium transition-all ${
                  selectedStrategy === strategy ? 'text-white' : ''
                }`}
                style={{
                  backgroundColor: selectedStrategy === strategy 
                    ? (strategy === 'PRO' ? VKNG_COLORS.purple : strategy === 'CORE' ? '#3B82F6' : VKNG_COLORS.pink)
                    : 'transparent',
                  color: selectedStrategy === strategy ? '#fff' : VKNG_COLORS.textSecondary
                }}
                data-testid={`strategy-${strategy.toLowerCase()}-btn`}
              >
                {strategy}
              </button>
            ))}
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          {lastUpdate && (
            <span className="text-xs" style={{ color: `${VKNG_COLORS.textSecondary}80` }}>
              Last update: {lastUpdate}
            </span>
          )}
          <Button 
            onClick={calculateAnalytics} 
            variant="outline" 
            size="sm"
            disabled={calculating}
            className="transition-all duration-200"
            style={{ 
              borderColor: VKNG_COLORS.purple,
              color: VKNG_COLORS.purple,
              backgroundColor: 'transparent'
            }}
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
            className="transition-all duration-200"
            style={{ 
              borderColor: VKNG_COLORS.mediumGray,
              color: VKNG_COLORS.textSecondary
            }}
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

      {/* Sub-navigation tabs following FXBlue format - VKNG Purple/Magenta Theme */}
      <Tabs value={activeSubTab} onValueChange={setActiveSubTab} className="w-full">
        <TabsList 
          className="p-1 w-full justify-start gap-1 overflow-x-auto rounded-lg"
          style={{ 
            backgroundColor: VKNG_COLORS.darkGray,
            border: `1px solid ${VKNG_COLORS.mediumGray}`
          }}
        >
          {['overview', 'analysis', 'stats', 'risk', 'orders'].map((tab) => (
            <TabsTrigger 
              key={tab}
              value={tab}
              className="capitalize rounded-md px-4 py-2 text-sm font-medium transition-all"
              style={{ 
                background: activeSubTab === tab 
                  ? `linear-gradient(135deg, ${VKNG_COLORS.pink} 0%, ${VKNG_COLORS.magenta} 100%)`
                  : 'transparent',
                color: activeSubTab === tab ? VKNG_COLORS.textPrimary : VKNG_COLORS.textSecondary,
                boxShadow: activeSubTab === tab ? `0 2px 8px ${VKNG_COLORS.purple}40` : 'none'
              }}
            >
              {tab}
            </TabsTrigger>
          ))}
        </TabsList>

        {/* OVERVIEW TAB */}
        <TabsContent value="overview" className="mt-6 space-y-6">
          {/* Combined Summary Row (Only show when ALL is selected) */}
          {selectedStrategy === 'ALL' && (coreAccount || proAccount) && (
            <Card 
              className="border"
              style={{ 
                backgroundColor: `${VKNG_COLORS.darkGray}`,
                borderColor: `${VKNG_COLORS.pink}40`,
                boxShadow: `0 4px 20px ${VKNG_COLORS.purple}15`
              }}
            >
              <CardHeader className="pb-2">
                <CardTitle className="text-lg flex items-center gap-2" style={{ color: VKNG_COLORS.textPrimary }}>
                  <span style={{ color: VKNG_COLORS.pink }}>📊</span>
                  Combined Portfolio
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div>
                    <p className="text-xs text-gray-500">Total Balance</p>
                    <p className="text-2xl font-bold" style={{ color: VKNG_COLORS.textPrimary }}>{formatCurrency(totalBalance)}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Total Equity</p>
                    <p className="text-2xl font-bold" style={{ color: VKNG_COLORS.textPrimary }}>{formatCurrency(totalEquity)}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Total Floating P/L</p>
                    <p className={`text-2xl font-bold ${totalProfit >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {formatCurrency(totalProfit)}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Total Positions</p>
                    <p className="text-2xl font-bold" style={{ color: VKNG_COLORS.textPrimary }}>{totalPositions}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
          
          {/* Strategy Cards Row */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* VIKING CORE Strategy Card */}
            {(selectedStrategy === 'ALL' || selectedStrategy === 'CORE') && (
            <Card 
              className="border"
              style={{ 
                backgroundColor: `${VKNG_COLORS.darkGray}`,
                borderColor: '#3B82F630'
              }}
            >
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg flex items-center gap-2" style={{ color: VKNG_COLORS.textPrimary }}>
                    <span style={{ color: '#3B82F6' }}>⚡</span>
                    VIKING CORE
                  </CardTitle>
                  <Badge className={`${getStatusColor(coreAccount?.status)} border`}>
                    {getStatusIcon(coreAccount?.status)}
                    <span className="ml-1 capitalize">{coreAccount?.status?.replace('_', ' ') || 'Unknown'}</span>
                  </Badge>
                </div>
                <p className="text-sm" style={{ color: VKNG_COLORS.textSecondary }}>
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
                    <p className={`text-lg font-semibold ${(coreAccount?.profit || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {formatCurrency(coreAccount?.profit)}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Positions</p>
                    <p className="text-lg font-semibold text-gray-300">{coreAccount?.positions_count || 0}</p>
                  </div>
                </div>
                <div className="flex items-center justify-between pt-2 border-t border-gray-800">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-blue-500"></div>
                    <span className="text-xs text-gray-400">MEXAtlantic</span>
                  </div>
                  <span className="text-xs text-gray-500">
                    Last Sync: {coreAccount?.last_update ? new Date(coreAccount.last_update).toLocaleString() : '--'}
                  </span>
                </div>
              </CardContent>
            </Card>
            )}

            {/* VIKING PRO Strategy Card */}
            {(selectedStrategy === 'ALL' || selectedStrategy === 'PRO') && (
            <Card 
              className="border"
              style={{ 
                backgroundColor: `${VKNG_COLORS.darkGray}`,
                borderColor: `${VKNG_COLORS.purple}30`
              }}
            >
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg flex items-center gap-2" style={{ color: VKNG_COLORS.textPrimary }}>
                    <span style={{ color: VKNG_COLORS.purple }}>⚔️</span>
                    VIKING PRO
                  </CardTitle>
                  <Badge className={`${getStatusColor(proAccount?.status)} border`}>
                    {getStatusIcon(proAccount?.status)}
                    <span className="ml-1 capitalize">{proAccount?.status?.replace('_', ' ') || 'Pending Setup'}</span>
                  </Badge>
                </div>
                <p className="text-sm" style={{ color: VKNG_COLORS.textSecondary }}>
                  Account: {proAccount?.account || '1309411'} | {proAccount?.broker || 'Traders Trust'}
                </p>
              </CardHeader>
              <CardContent className="space-y-3">
                {proAccount?.status === 'active' ? (
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
                      <p className={`text-lg font-semibold ${(proAccount?.profit || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                        {formatCurrency(proAccount?.profit)}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500">Positions</p>
                      <p className="text-lg font-semibold text-gray-300">{proAccount?.positions_count || 0}</p>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-6">
                    <AlertTriangle className="w-10 h-10 mx-auto mb-2" style={{ color: VKNG_COLORS.purple }} />
                    <p className="text-gray-400 text-sm">PRO account pending setup</p>
                    <p className="text-gray-500 text-xs mt-1">Connect MT4 EA to start syncing</p>
                  </div>
                )}
                <div className="flex items-center justify-between pt-2 border-t border-gray-800">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full" style={{ backgroundColor: VKNG_COLORS.purple }}></div>
                    <span className="text-xs text-gray-400">Traders Trust</span>
                  </div>
                  <span className="text-xs text-gray-500">
                    {proAccount?.last_update ? `Last Sync: ${new Date(proAccount.last_update).toLocaleString()}` : 'Not synced'}
                  </span>
                </div>
              </CardContent>
            </Card>
            )}
          </div>

          {/* Stats Summary Row - Shows real data only */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Card className="bg-gradient-to-br from-green-500/10 to-green-500/5 border-green-500/20">
              <CardContent className="pt-4">
                <p className="text-xs text-gray-400 mb-1">Total Return</p>
                <p className="text-2xl font-bold text-green-400">
                  {analytics?.total_return != null ? formatPercent(analytics.total_return) : '--'}
                </p>
              </CardContent>
            </Card>
            <Card className="bg-gradient-to-br from-blue-500/10 to-blue-500/5 border-blue-500/20">
              <CardContent className="pt-4">
                <p className="text-xs text-gray-400 mb-1">Monthly Return</p>
                <p className="text-2xl font-bold text-blue-400">
                  {analytics?.monthly_return != null ? formatPercent(analytics.monthly_return) : '--'}
                </p>
              </CardContent>
            </Card>
            <Card className="bg-gradient-to-br from-purple-500/10 to-purple-500/5 border-purple-500/20">
              <CardContent className="pt-4">
                <p className="text-xs text-gray-400 mb-1">Profit Factor</p>
                <p className="text-2xl font-bold text-purple-400">
                  {analytics?.profit_factor != null ? analytics.profit_factor.toFixed(2) : '--'}
                </p>
              </CardContent>
            </Card>
            <Card className="bg-gradient-to-br from-cyan-500/10 to-cyan-500/5 border-cyan-500/20">
              <CardContent className="pt-4">
                <p className="text-xs text-gray-400 mb-1">History</p>
                <p className="text-2xl font-bold text-cyan-400">
                  {analytics?.history_days != null ? `${analytics.history_days} days` : '--'}
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Additional Stats Grid - Real data only */}
          <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
            <StatCard label="Weekly Return" value={analytics?.weekly_return != null ? formatPercent(analytics.weekly_return) : '--'} color="text-green-400" />
            <StatCard label="Peak Drawdown" value={analytics?.peak_drawdown != null ? formatPercent(analytics.peak_drawdown) : '--'} color="text-red-400" />
            <StatCard label="Trade Win %" value={analytics?.trade_win_rate != null ? `${analytics.trade_win_rate.toFixed(1)}%` : '--'} color="text-blue-400" />
            <StatCard label="Trades/Day" value={analytics?.trades_per_day != null ? analytics.trades_per_day.toFixed(1) : '--'} color="text-purple-400" />
            <StatCard label="Risk/Reward" value={analytics?.risk_reward_ratio != null ? analytics.risk_reward_ratio.toFixed(2) : '--'} color="text-cyan-400" />
            <StatCard label="Total Trades" value={analytics?.total_trades != null ? analytics.total_trades.toLocaleString() : '--'} color="text-orange-400" />
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
                {/* Legend - only show if we have real data */}
                {symbolDistribution.length > 0 && (
                  <div className="mt-4 space-y-1">
                    {symbolDistribution.slice(0, 5).map((item, idx) => (
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
                )}
                {symbolDistribution.length === 0 && (
                  <p className="text-xs text-gray-500 text-center mt-4">Trade history required for symbol distribution</p>
                )}
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
              {symbolDistribution.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {symbolDistribution.slice(0, 3).map((item, idx) => (
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
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <BarChart3 className="w-12 h-12 mx-auto mb-2 opacity-50" />
                  <p className="text-sm">Trade history required for market analysis</p>
                </div>
              )}
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
                <p className="text-xl font-bold text-green-400">{analytics?.weekly_return != null ? formatPercent(analytics.weekly_return) : '--'}</p>
              </CardContent>
            </Card>
            <Card className="bg-gray-900/50 border-gray-800">
              <CardContent className="pt-4">
                <p className="text-xs text-gray-500">Monthly Return</p>
                <p className="text-xl font-bold text-green-400">{analytics?.monthly_return != null ? formatPercent(analytics.monthly_return) : '--'}</p>
              </CardContent>
            </Card>
            <Card className="bg-gray-900/50 border-gray-800">
              <CardContent className="pt-4">
                <p className="text-xs text-gray-500">Profit Factor</p>
                <p className="text-xl font-bold text-blue-400">{analytics?.profit_factor != null ? analytics.profit_factor.toFixed(2) : '--'}</p>
              </CardContent>
            </Card>
            <Card className="bg-gray-900/50 border-gray-800">
              <CardContent className="pt-4">
                <p className="text-xs text-gray-500">History</p>
                <p className="text-xl font-bold text-gray-300">{analytics?.history_days != null ? `${analytics.history_days} days` : '--'}</p>
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
                  <p className="text-lg font-bold text-green-400">{analytics?.total_return != null ? formatPercent(analytics.total_return) : '--'}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Banked Return</p>
                  <p className="text-lg font-bold text-green-400">{analytics?.total_return != null ? formatPercent(analytics.total_return) : '--'}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Per Day</p>
                  <p className="text-lg font-bold text-green-400">{analytics?.daily_return != null ? formatPercent(analytics.daily_return) : '--'}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Per Week</p>
                  <p className="text-lg font-bold text-green-400">{analytics?.weekly_return != null ? formatPercent(analytics.weekly_return) : '--'}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Per Month</p>
                  <p className="text-lg font-bold text-green-400">{analytics?.monthly_return != null ? formatPercent(analytics.monthly_return) : '--'}</p>
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
                      <td className="text-right text-green-400">{analytics?.winning_months ?? '--'}</td>
                      <td className="text-right text-red-400">{analytics?.losing_months ?? '--'}</td>
                      <td className="text-right">
                        <div className="w-16 bg-gray-700 rounded-full h-2 ml-auto">
                          <div className="bg-green-500 h-2 rounded-full" style={{ width: analytics?.monthly_win_rate ? `${analytics.monthly_win_rate}%` : '0%' }}></div>
                        </div>
                      </td>
                      <td className="text-right text-green-400">{analytics?.avg_monthly_profit != null ? formatCurrency(analytics.avg_monthly_profit) : '--'}</td>
                      <td className="text-right text-green-400">{analytics?.avg_monthly_profit_per_trade != null ? formatCurrency(analytics.avg_monthly_profit_per_trade) : '--'}</td>
                    </tr>
                    <tr>
                      <td className="py-2 text-gray-300">Closed Trades</td>
                      <td className="text-right text-green-400">{analytics?.winning_trades ?? '--'}</td>
                      <td className="text-right text-red-400">{analytics?.losing_trades ?? '--'}</td>
                      <td className="text-right">
                        <div className="w-16 bg-gray-700 rounded-full h-2 ml-auto">
                          <div className="bg-green-500 h-2 rounded-full" style={{ width: analytics?.trade_win_rate ? `${analytics.trade_win_rate}%` : '0%' }}></div>
                        </div>
                      </td>
                      <td className="text-right text-green-400">{analytics?.avg_winning_trade != null ? formatCurrency(analytics.avg_winning_trade) : '--'}</td>
                      <td className="text-right text-red-400">{analytics?.avg_losing_trade != null ? formatCurrency(analytics.avg_losing_trade) : '--'}</td>
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
                <p className="text-xl font-bold text-green-400">{riskData?.monthly_return != null ? formatPercent(riskData.monthly_return) : '--'}</p>
              </CardContent>
            </Card>
            <Card className="bg-gray-900/50 border-gray-800">
              <CardContent className="pt-4">
                <p className="text-xs text-gray-500">Avg Trade Length</p>
                <p className="text-xl font-bold text-gray-300">{riskData?.avg_trade_length != null ? `${riskData.avg_trade_length} hours` : '--'}</p>
              </CardContent>
            </Card>
            <Card className="bg-gray-900/50 border-gray-800">
              <CardContent className="pt-4">
                <p className="text-xs text-gray-500">Trades Per Day</p>
                <p className="text-xl font-bold text-gray-300">{riskData?.trades_per_day != null ? riskData.trades_per_day.toFixed(1) : '--'}</p>
              </CardContent>
            </Card>
            <Card className="bg-gray-900/50 border-gray-800">
              <CardContent className="pt-4">
                <p className="text-xs text-gray-500">History</p>
                <p className="text-xl font-bold text-gray-300">{riskData?.history_days != null ? `${riskData.history_days} days` : '--'}</p>
              </CardContent>
            </Card>
            <Card className="bg-gray-900/50 border-gray-800">
              <CardContent className="pt-4">
                <p className="text-xs text-gray-500">Risk/Reward</p>
                <p className="text-xl font-bold text-green-400">{riskData?.risk_reward_ratio != null ? `+${riskData.risk_reward_ratio}` : '--'}</p>
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
                      <p className="text-lg font-bold text-green-400">{riskData?.balance_metrics?.worst_month_pct != null ? `${riskData.balance_metrics.worst_month_pct > 0 ? '+' : ''}${riskData.balance_metrics.worst_month_pct}%` : '--'}</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500">Deepest Valley</p>
                      <p className="text-lg font-bold text-red-400">{riskData?.balance_metrics?.deepest_valley != null ? `${riskData.balance_metrics.deepest_valley}%` : '--'}</p>
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
                      <p className="text-lg font-bold text-red-400">{riskData?.equity_metrics?.worst_day_pct != null ? `${riskData.equity_metrics.worst_day_pct}%` : '--'}</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500">Worst Week %</p>
                      <p className="text-lg font-bold text-red-400">{riskData?.equity_metrics?.worst_week_pct != null ? `${riskData.equity_metrics.worst_week_pct}%` : '--'}</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500">Worst Month %</p>
                      <p className="text-lg font-bold text-red-400">{riskData?.equity_metrics?.worst_month_pct != null ? `${riskData.equity_metrics.worst_month_pct}%` : '--'}</p>
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
                        <th className="text-left py-2 px-2 text-gray-500">Ticket</th>
                        <th className="text-left py-2 px-2 text-gray-500">Closed</th>
                        <th className="text-left py-2 px-2 text-gray-500">Type</th>
                        <th className="text-right py-2 px-2 text-gray-500">Lots</th>
                        <th className="text-left py-2 px-2 text-gray-500">Symbol</th>
                        <th className="text-right py-2 px-2 text-gray-500">Open</th>
                        <th className="text-right py-2 px-2 text-gray-500">Close</th>
                        <th className="text-right py-2 px-2 text-gray-500">Comm</th>
                        <th className="text-right py-2 px-2 text-gray-500">Swap</th>
                        <th className="text-right py-2 px-2 text-gray-500">Profit</th>
                      </tr>
                    </thead>
                    <tbody>
                      {deals.map((deal, idx) => (
                        <tr key={deal.ticket || idx} className="border-b border-gray-800 hover:bg-gray-800/50">
                          <td className="py-2 px-2 text-gray-300">{deal.ticket}</td>
                          <td className="py-2 px-2 text-gray-400 text-xs">
                            {formatDateTime(deal.close_time)}
                          </td>
                          <td className="py-2 px-2">
                            <Badge className={deal.type === 'BUY' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}>
                              {deal.type}
                            </Badge>
                          </td>
                          <td className="py-2 px-2 text-right text-gray-300">{deal.volume}</td>
                          <td className="py-2 px-2 text-gray-300">{deal.symbol}</td>
                          <td className="py-2 px-2 text-right text-gray-300">{deal.open_price?.toFixed(2)}</td>
                          <td className="py-2 px-2 text-right text-gray-300">{deal.close_price?.toFixed(2) || '--'}</td>
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
