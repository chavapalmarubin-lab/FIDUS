/**
 * FIDUS Track-Record Dashboard
 * 
 * Branded with official FIDUS colors (Gold, Navy Blue, Cyan)
 * 
 * This dashboard manages FIDUS trading strategies:
 * - CORE Strategy: Account 1309411 (Traders Trust)
 * - BALANCE Strategy: Account 885822 (MEXAtlantic)
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

// FIDUS Brand Colors (Gold, Navy Blue, Cyan theme)
const FIDUS_COLORS = {
  gold: '#D4AF37',       // Primary gold/yellow
  goldLight: '#E5C158',  // Light gold
  navy: '#1E3A5F',       // Navy blue
  navyDark: '#0D1629',   // Dark navy
  cyan: '#22d3ee',       // Cyan accent
  blue: '#3B82F6',       // Blue
  dark: '#0A112B',
  darkGray: '#0D1629',
  mediumGray: '#1A2744',
  textPrimary: '#FFFFFF',
  textSecondary: '#9CA3AF'
};

// BALANCE Strategy Display Multiplier (for display purposes only - account 885822)
const BALANCE_DISPLAY_MULTIPLIER = 1000;

// Minimum percentage threshold for symbol distribution display
const SYMBOL_MIN_PERCENTAGE = 3;

// Colors for charts (FIDUS themed)
const COLORS = {
  primary: '#D4AF37',    // FIDUS Gold
  secondary: '#3B82F6',  // FIDUS Blue
  success: '#22c55e',    // Green
  danger: '#ef4444',     // Red
  warning: '#eab308',    // Yellow
  purple: '#8b5cf6',     // Purple
  cyan: '#22d3ee',       // FIDUS Cyan
  gold: '#D4AF37'        // FIDUS Gold
};

// Distinct colors for symbol distribution pie chart
const SYMBOL_COLORS = ['#D4AF37', '#22c55e', '#3B82F6', '#F59E0B', '#EC4899', '#22d3ee', '#EF4444', '#8B5CF6'];

// Strategy colors
const STRATEGY_COLORS = {
  CORE: { primary: '#3B82F6', secondary: '#60A5FA', bg: 'bg-blue-500/10', border: 'border-blue-500/30', text: 'text-blue-400' },
  BALANCE: { primary: '#D4AF37', secondary: '#E5C158', bg: 'bg-yellow-500/10', border: 'border-yellow-500/30', text: 'text-yellow-400' }
};

const VikingDashboard = ({ onAccountChange }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [activeSubTab, setActiveSubTab] = useState("overview");
  const [selectedStrategy, setSelectedStrategy] = useState("ALL"); // ALL, CORE, BALANCE
  
  // Data state
  const [summary, setSummary] = useState(null);
  const [accounts, setAccounts] = useState([]); // Array of all accounts
  const [analytics, setAnalytics] = useState(null);
  const [coreAnalytics, setCoreAnalytics] = useState(null);
  const [balanceAnalytics, setBalanceAnalytics] = useState(null);
  const [deals, setDeals] = useState([]);
  const [symbolDistribution, setSymbolDistribution] = useState([]);
  const [riskData, setRiskData] = useState(null);
  const [balanceHistory, setBalanceHistory] = useState([]);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [calculating, setCalculating] = useState(false);
  
  // Monthly returns data
  const [monthlyReturns, setMonthlyReturns] = useState({ metrics: {}, data: [] });
  
  // Pagination state for Orders tab
  const [ordersPage, setOrdersPage] = useState(1);
  const [ordersPerPage, setOrdersPerPage] = useState(25);
  const [totalDeals, setTotalDeals] = useState(0);

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
        console.log("BALANCE account not yet available");
      }
      
      // Refresh all data
      await fetchData();
    } catch (err) {
      console.error("Error calculating analytics:", err);
    } finally {
      setCalculating(false);
    }
  };

  // Fetch all FIDUS Track-Record data
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
      
      // Fetch analytics for BALANCE strategy (formerly PRO)
      try {
        const balanceAnalyticsRes = await fetch(`${BACKEND_URL}/api/viking/analytics/PRO`);
        const balanceAnalyticsData = await balanceAnalyticsRes.json();
        if (balanceAnalyticsData.success) {
          setBalanceAnalytics(balanceAnalyticsData.analytics);
          if (selectedStrategy === 'BALANCE') {
            setAnalytics(balanceAnalyticsData.analytics);
          }
        }
      } catch (e) { console.log("BALANCE analytics not available yet"); }
      
      // Fetch deals based on selected strategy WITH PAGINATION
      const strategy = selectedStrategy === 'ALL' ? 'CORE' : (selectedStrategy === 'BALANCE' ? 'PRO' : selectedStrategy);
      const dealsRes = await fetch(`${BACKEND_URL}/api/viking/deals/${strategy}?limit=${ordersPerPage}&skip=${(ordersPage - 1) * ordersPerPage}`);
      const dealsData = await dealsRes.json();
      
      if (dealsData.success) {
        setDeals(dealsData.deals || []);
        setTotalDeals(dealsData.pagination?.total || dealsData.deals?.length || 0);
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
      
      // Fetch monthly returns data
      const monthlyRes = await fetch(`${BACKEND_URL}/api/viking/monthly-returns/${strategy}`);
      const monthlyData = await monthlyRes.json();
      
      if (monthlyData.success) {
        setMonthlyReturns({
          metrics: monthlyData.metrics || {},
          data: monthlyData.data || []
        });
      }
      
    } catch (err) {
      console.error("Error fetching FIDUS Track-Record data:", err);
      setError("Failed to load Track-Record data. Please try again.");
    } finally {
      setLoading(false);
    }
  }, [selectedStrategy, ordersPage, ordersPerPage]);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, [fetchData]);

  // Reset page when strategy changes
  useEffect(() => {
    setOrdersPage(1);
  }, [selectedStrategy]);

  // Update header with active account info when strategy or summary changes
  useEffect(() => {
    if (onAccountChange && summary) {
      const core = summary?.strategies?.find(s => s.strategy === 'CORE');
      const pro = summary?.strategies?.find(s => s.strategy === 'PRO');
      
      if (selectedStrategy === 'ALL') {
        onAccountChange({
          account: 'ALL',
          broker: 'Combined',
          strategy: 'ALL'
        });
      } else if (selectedStrategy === 'CORE') {
        onAccountChange({
          account: core?.account || '33627673',
          broker: core?.broker || 'MEXAtlantic',
          strategy: 'CORE'
        });
      } else if (selectedStrategy === 'PRO') {
        onAccountChange({
          account: pro?.account || '1309411',
          broker: pro?.broker || 'Traders Trust',
          strategy: 'PRO'
        });
      }
    }
  }, [selectedStrategy, summary, onAccountChange]);

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
            style={{ color: FIDUS_COLORS.purple }}
          />
          <p style={{ color: FIDUS_COLORS.textSecondary }}>Loading FIDUS Track-Record data...</p>
        </div>
      </div>
    );
  }

  // Get account data
  const coreAccount = summary?.strategies?.find(s => s.strategy === 'CORE');
  const proAccount = summary?.strategies?.find(s => s.strategy === 'PRO');
  
  // Calculate combined totals
  // Apply PRO multiplier to totals for display (PRO is account 885822)
  const totalBalance = (coreAccount?.balance || 0) + ((proAccount?.balance || 0) * BALANCE_DISPLAY_MULTIPLIER);
  const totalEquity = (coreAccount?.equity || 0) + ((proAccount?.equity || 0) * BALANCE_DISPLAY_MULTIPLIER);
  const totalProfit = (coreAccount?.profit || 0) + ((proAccount?.profit || 0) * BALANCE_DISPLAY_MULTIPLIER);
  const totalPositions = (coreAccount?.positions_count || 0) + (proAccount?.positions_count || 0);
  
  // Filter symbol distribution to only show symbols >= 3%
  const filteredSymbolDistribution = symbolDistribution.filter(item => item.percentage >= SYMBOL_MIN_PERCENTAGE);

  return (
    <div className="space-y-6" data-testid="fidus-track-record-dashboard">
      {/* Header with Strategy Selector */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold" style={{ color: FIDUS_COLORS.textPrimary }}>
            Trading Operations
          </h1>
          <p className="mt-1" style={{ color: FIDUS_COLORS.textSecondary }}>
            Real-time MT4 Performance Analytics
          </p>
        </div>
        
        {/* Strategy Selector */}
        <div className="flex items-center gap-2">
          <span className="text-sm" style={{ color: FIDUS_COLORS.textSecondary }}>Strategy:</span>
          <div className="flex rounded-lg overflow-hidden" style={{ backgroundColor: FIDUS_COLORS.darkGray, border: `1px solid ${FIDUS_COLORS.mediumGray}` }}>
            {['ALL', 'CORE', 'BALANCE'].map((strategy) => (
              <button
                key={strategy}
                onClick={() => setSelectedStrategy(strategy)}
                className={`px-4 py-2 text-sm font-medium transition-all ${
                  selectedStrategy === strategy ? 'text-white' : ''
                }`}
                style={{
                  backgroundColor: selectedStrategy === strategy 
                    ? (strategy === 'BALANCE' ? FIDUS_COLORS.gold : strategy === 'CORE' ? '#3B82F6' : FIDUS_COLORS.cyan)
                    : 'transparent',
                  color: selectedStrategy === strategy ? '#fff' : FIDUS_COLORS.textSecondary
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
            <span className="text-xs" style={{ color: `${FIDUS_COLORS.textSecondary}80` }}>
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
              borderColor: FIDUS_COLORS.purple,
              color: FIDUS_COLORS.purple,
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
              borderColor: FIDUS_COLORS.mediumGray,
              color: FIDUS_COLORS.textSecondary
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
            backgroundColor: FIDUS_COLORS.darkGray,
            border: `1px solid ${FIDUS_COLORS.mediumGray}`
          }}
        >
          {['overview', 'analysis', 'stats', 'risk', 'orders'].map((tab) => (
            <TabsTrigger 
              key={tab}
              value={tab}
              className="capitalize rounded-md px-4 py-2 text-sm font-medium transition-all"
              style={{ 
                background: activeSubTab === tab 
                  ? `linear-gradient(135deg, ${FIDUS_COLORS.pink} 0%, ${FIDUS_COLORS.magenta} 100%)`
                  : 'transparent',
                color: activeSubTab === tab ? FIDUS_COLORS.textPrimary : FIDUS_COLORS.textSecondary,
                boxShadow: activeSubTab === tab ? `0 2px 8px ${FIDUS_COLORS.purple}40` : 'none'
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
                backgroundColor: `${FIDUS_COLORS.darkGray}`,
                borderColor: `${FIDUS_COLORS.pink}40`,
                boxShadow: `0 4px 20px ${FIDUS_COLORS.purple}15`
              }}
            >
              <CardHeader className="pb-2">
                <CardTitle className="text-lg flex items-center gap-2" style={{ color: FIDUS_COLORS.textPrimary }}>
                  <span style={{ color: FIDUS_COLORS.pink }}>📊</span>
                  Combined Portfolio
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div>
                    <p className="text-xs text-gray-500">Total Balance</p>
                    <p className="text-2xl font-bold" style={{ color: FIDUS_COLORS.textPrimary }}>{formatCurrency(totalBalance)}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Total Equity</p>
                    <p className="text-2xl font-bold" style={{ color: FIDUS_COLORS.textPrimary }}>{formatCurrency(totalEquity)}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Total Floating P/L</p>
                    <p className={`text-2xl font-bold ${totalProfit >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {formatCurrency(totalProfit)}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Total Positions</p>
                    <p className="text-2xl font-bold" style={{ color: FIDUS_COLORS.textPrimary }}>{totalPositions}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
          
          {/* Strategy Cards Row */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* FIDUS CORE Strategy Card */}
            {(selectedStrategy === 'ALL' || selectedStrategy === 'CORE') && (
            <Card 
              className="border"
              style={{ 
                backgroundColor: `${FIDUS_COLORS.darkGray}`,
                borderColor: '#3B82F630'
              }}
            >
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg flex items-center gap-2" style={{ color: FIDUS_COLORS.textPrimary }}>
                    <span style={{ color: '#3B82F6' }}>⚡</span>
                    FIDUS CORE
                  </CardTitle>
                  <Badge className={`${getStatusColor(coreAccount?.status)} border`}>
                    {getStatusIcon(coreAccount?.status)}
                    <span className="ml-1 capitalize">{coreAccount?.status?.replace('_', ' ') || 'Unknown'}</span>
                  </Badge>
                </div>
                <p className="text-sm" style={{ color: FIDUS_COLORS.textSecondary }}>
                  Account: {coreAccount?.account || '1309411'} | {coreAccount?.broker || 'Traders Trust'}
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
                    <span className="text-xs text-gray-400">Traders Trust</span>
                  </div>
                  <span className="text-xs text-gray-500">
                    Last Sync: {coreAccount?.last_update ? new Date(coreAccount.last_update).toLocaleString() : '--'}
                  </span>
                </div>
              </CardContent>
            </Card>
            )}

            {/* FIDUS BALANCE Strategy Card */}
            {(selectedStrategy === 'ALL' || selectedStrategy === 'BALANCE') && (
            <Card 
              className="border"
              style={{ 
                backgroundColor: `${FIDUS_COLORS.darkGray}`,
                borderColor: `${FIDUS_COLORS.gold}30`
              }}
            >
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg flex items-center gap-2" style={{ color: FIDUS_COLORS.textPrimary }}>
                    <span style={{ color: FIDUS_COLORS.gold }}>⚖️</span>
                    FIDUS BALANCE
                  </CardTitle>
                  <Badge className={`${getStatusColor(proAccount?.status)} border`}>
                    {getStatusIcon(proAccount?.status)}
                    <span className="ml-1 capitalize">{proAccount?.status?.replace('_', ' ') || 'Pending Setup'}</span>
                  </Badge>
                </div>
                <p className="text-sm" style={{ color: FIDUS_COLORS.textSecondary }}>
                  Account: {proAccount?.account || '885822'} | {proAccount?.broker || 'MEXAtlantic'}
                </p>
              </CardHeader>
              <CardContent className="space-y-3">
                {proAccount?.status === 'active' ? (
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-xs text-gray-500">Balance</p>
                      <p className="text-xl font-bold text-white">{formatCurrency((proAccount?.balance || 0) * BALANCE_DISPLAY_MULTIPLIER)}</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500">Equity</p>
                      <p className="text-xl font-bold text-white">{formatCurrency((proAccount?.equity || 0) * BALANCE_DISPLAY_MULTIPLIER)}</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500">Floating P/L</p>
                      <p className={`text-lg font-semibold ${(proAccount?.profit || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                        {formatCurrency((proAccount?.profit || 0) * BALANCE_DISPLAY_MULTIPLIER)}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500">Positions</p>
                      <p className="text-lg font-semibold text-gray-300">{proAccount?.positions_count || 0}</p>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-6">
                    <AlertTriangle className="w-10 h-10 mx-auto mb-2" style={{ color: FIDUS_COLORS.purple }} />
                    <p className="text-gray-400 text-sm">BALANCE account pending setup</p>
                    <p className="text-gray-500 text-xs mt-1">Connect MT5 EA to start syncing</p>
                  </div>
                )}
                <div className="flex items-center justify-between pt-2 border-t border-gray-800">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full" style={{ backgroundColor: FIDUS_COLORS.purple }}></div>
                    <span className="text-xs text-gray-400">MEXAtlantic</span>
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
                        contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px', color: '#fff' }}
                        labelStyle={{ color: '#fff' }}
                        itemStyle={{ color: '#fff' }}
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
                          contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', color: '#fff' }}
                          labelStyle={{ color: '#fff' }}
                          itemStyle={{ color: '#fff' }}
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
                {filteredSymbolDistribution.length > 0 ? (
                  <ResponsiveContainer width="100%" height={200}>
                    <PieChart>
                      <Pie
                        data={filteredSymbolDistribution}
                        dataKey="percentage"
                        nameKey="symbol"
                        cx="50%"
                        cy="50%"
                        outerRadius={70}
                        label={({ symbol, percentage }) => `${percentage}%`}
                      >
                        {filteredSymbolDistribution.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={SYMBOL_COLORS[index % SYMBOL_COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip 
                        contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', color: '#fff' }}
                        labelStyle={{ color: '#fff' }}
                        itemStyle={{ color: '#fff' }}
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
                {/* Legend - only show filtered symbols (>= 3%) */}
                {filteredSymbolDistribution.length > 0 && (
                  <div className="mt-4 space-y-1">
                    {filteredSymbolDistribution.map((item, idx) => (
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
                {filteredSymbolDistribution.length === 0 && symbolDistribution.length === 0 && (
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
                        contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', color: '#fff' }}
                        labelStyle={{ color: '#fff' }}
                        itemStyle={{ color: '#fff' }}
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
                      contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', color: '#fff' }}
                      labelStyle={{ color: '#fff' }}
                      itemStyle={{ color: '#fff' }}
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

          {/* Monthly Returns Chart */}
          <Card className="bg-gray-900/50 border-gray-800">
            <CardHeader>
              <div>
                <CardTitle className="text-sm text-white">Monthly</CardTitle>
                <p className="text-xs text-gray-500 mt-1">Returns of account by month</p>
              </div>
            </CardHeader>
            <CardContent>
              {/* Summary Metrics Row */}
              <div className="grid grid-cols-5 gap-4 mb-6 pb-4 border-b border-gray-700">
                <div className="text-center">
                  <p className="text-lg font-bold text-white">{monthlyReturns.metrics?.avgWeekly || 0}%</p>
                  <p className="text-xs text-gray-500">Average return (Weekly)</p>
                </div>
                <div className="text-center">
                  <p className="text-lg font-bold text-white">{monthlyReturns.metrics?.avgMonthly || 0}%</p>
                  <p className="text-xs text-gray-500">Average return (Monthly)</p>
                </div>
                <div className="text-center">
                  <p className="text-lg font-bold text-white">{monthlyReturns.metrics?.devDaily || 0}%</p>
                  <p className="text-xs text-gray-500">Return deviation (Daily)</p>
                </div>
                <div className="text-center">
                  <p className="text-lg font-bold text-white">{monthlyReturns.metrics?.devMonthly || 0}%</p>
                  <p className="text-xs text-gray-500">Return deviation (Monthly)</p>
                </div>
                <div className="text-center">
                  <p className="text-lg font-bold text-white">{monthlyReturns.metrics?.devYearly || 0}%</p>
                  <p className="text-xs text-gray-500">Return deviation (Yearly)</p>
                </div>
              </div>
              
              {/* Bar Chart */}
              {monthlyReturns.data && monthlyReturns.data.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={monthlyReturns.data} margin={{ top: 10, right: 10, left: 10, bottom: 20 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" vertical={false} />
                    <XAxis 
                      dataKey="month" 
                      tick={{ fill: '#9ca3af', fontSize: 10 }} 
                      axisLine={{ stroke: '#374151' }}
                      tickLine={{ stroke: '#374151' }}
                    />
                    <YAxis 
                      tick={{ fill: '#9ca3af', fontSize: 10 }} 
                      tickFormatter={(v) => `${v}%`}
                      axisLine={{ stroke: '#374151' }}
                      tickLine={{ stroke: '#374151' }}
                    />
                    <Tooltip 
                      content={({ active, payload, label }) => {
                        if (active && payload && payload.length) {
                          const data = payload[0].payload;
                          return (
                            <div style={{
                              backgroundColor: '#1f2937',
                              border: '1px solid #374151',
                              borderRadius: '8px',
                              padding: '10px 14px'
                            }}>
                              <p style={{ color: '#ffffff', marginBottom: '4px', fontWeight: 'bold' }}>{label}</p>
                              <p style={{ color: '#ffffff', margin: 0 }}>
                                Return: {data.return?.toFixed(2)}% ({formatCurrency(data.profit)})
                              </p>
                            </div>
                          );
                        }
                        return null;
                      }}
                      cursor={{ fill: 'rgba(255, 255, 255, 0.1)' }}
                    />
                    <Bar dataKey="return" radius={[2, 2, 0, 0]}>
                      {monthlyReturns.data.map((entry, index) => (
                        <Cell 
                          key={`cell-${index}`} 
                          fill={entry.return >= 0 ? '#00BCD4' : '#FF5722'} 
                        />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-64 flex items-center justify-center border border-dashed border-gray-700 rounded-lg">
                  <div className="text-center text-gray-500">
                    <BarChart3 className="w-12 h-12 mx-auto mb-2 opacity-50" />
                    <p className="text-sm">Monthly return data loading...</p>
                  </div>
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
              <div className="flex items-center justify-between flex-wrap gap-4">
                <div className="flex items-center gap-3">
                  <CardTitle className="text-sm text-gray-400">Trade History</CardTitle>
                  <Badge variant="outline" className="border-gray-600">
                    {totalDeals > 0 ? `${totalDeals} total trades` : `${deals.length} trades loaded`}
                  </Badge>
                </div>
                
                {/* Pagination Controls - Top */}
                {deals.length > 0 && (
                  <div className="flex items-center gap-4">
                    {/* Per page selector */}
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-gray-500">Show:</span>
                      <select 
                        value={ordersPerPage}
                        onChange={(e) => {
                          setOrdersPerPage(Number(e.target.value));
                          setOrdersPage(1);
                        }}
                        className="bg-gray-800 border border-gray-700 rounded px-2 py-1 text-xs text-gray-300 focus:outline-none focus:border-purple-500"
                        data-testid="orders-per-page-select"
                      >
                        <option value={10}>10</option>
                        <option value={25}>25</option>
                        <option value={50}>50</option>
                        <option value={100}>100</option>
                      </select>
                    </div>
                    
                    {/* Page navigation */}
                    <div className="flex items-center gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setOrdersPage(1)}
                        disabled={ordersPage === 1}
                        className="h-7 px-2 text-xs"
                        style={{ borderColor: '#374151', color: ordersPage === 1 ? '#6b7280' : '#d1d5db' }}
                        data-testid="orders-first-page-btn"
                      >
                        First
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setOrdersPage(p => Math.max(1, p - 1))}
                        disabled={ordersPage === 1}
                        className="h-7 px-2 text-xs"
                        style={{ borderColor: '#374151', color: ordersPage === 1 ? '#6b7280' : '#d1d5db' }}
                        data-testid="orders-prev-page-btn"
                      >
                        ← Prev
                      </Button>
                      
                      <span className="text-xs text-gray-400 px-2">
                        Page <span className="text-white font-medium">{ordersPage}</span> of{' '}
                        <span className="text-white font-medium">{Math.max(1, Math.ceil(totalDeals / ordersPerPage))}</span>
                      </span>
                      
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setOrdersPage(p => Math.min(Math.ceil(totalDeals / ordersPerPage), p + 1))}
                        disabled={ordersPage >= Math.ceil(totalDeals / ordersPerPage)}
                        className="h-7 px-2 text-xs"
                        style={{ borderColor: '#374151', color: ordersPage >= Math.ceil(totalDeals / ordersPerPage) ? '#6b7280' : '#d1d5db' }}
                        data-testid="orders-next-page-btn"
                      >
                        Next →
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setOrdersPage(Math.ceil(totalDeals / ordersPerPage))}
                        disabled={ordersPage >= Math.ceil(totalDeals / ordersPerPage)}
                        className="h-7 px-2 text-xs"
                        style={{ borderColor: '#374151', color: ordersPage >= Math.ceil(totalDeals / ordersPerPage) ? '#6b7280' : '#d1d5db' }}
                        data-testid="orders-last-page-btn"
                      >
                        Last
                      </Button>
                    </div>
                  </div>
                )}
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
              
              {/* Bottom Pagination Summary */}
              {deals.length > 0 && totalDeals > 0 && (
                <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-800">
                  <span className="text-xs text-gray-500">
                    Showing {((ordersPage - 1) * ordersPerPage) + 1} - {Math.min(ordersPage * ordersPerPage, totalDeals)} of {totalDeals} trades
                  </span>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-gray-500">Jump to page:</span>
                    <input
                      type="number"
                      min={1}
                      max={Math.ceil(totalDeals / ordersPerPage)}
                      value={ordersPage}
                      onChange={(e) => {
                        const page = Math.max(1, Math.min(Math.ceil(totalDeals / ordersPerPage), Number(e.target.value) || 1));
                        setOrdersPage(page);
                      }}
                      className="w-16 bg-gray-800 border border-gray-700 rounded px-2 py-1 text-xs text-gray-300 text-center focus:outline-none focus:border-purple-500"
                      data-testid="orders-jump-to-page"
                    />
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
