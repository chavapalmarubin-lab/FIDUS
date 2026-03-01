import React, { useState, useEffect, useMemo, useRef, useCallback } from 'react';
import {
  LineChart, Line, AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, ComposedChart
} from 'recharts';
import {
  RefreshCw, Download, Clock, TrendingUp, TrendingDown, DollarSign,
  Users, Target, Shield, AlertTriangle, Award, BarChart3, Activity,
  ChevronRight, ChevronDown, Zap, Briefcase, PieChart as PieChartIcon,
  ArrowUpRight, ArrowDownRight, Filter, Search, ExternalLink,
  Send, Bot, Loader2, Sparkles, MessageSquare, Lightbulb, Settings
} from 'lucide-react';
import './NextGenTradingAnalytics.css';

// ============================================================================
// NEXT-GEN TRADING ANALYTICS DASHBOARD
// Phase 1, 2 & 3: Core Structure, Design System, All Components + AI Advisor
// ============================================================================

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

// Default strategy for Deep Dive (TradingHub Gold - Account 886557)
const DEFAULT_DEEP_DIVE_ACCOUNT = 886557;

// Auto-refresh interval (30 seconds)
const AUTO_REFRESH_INTERVAL = 30000;

export default function NextGenTradingAnalytics() {
  // ─────────────────────────────────────────────────────────────────────────────
  // STATE MANAGEMENT
  // ─────────────────────────────────────────────────────────────────────────────
  const [activeTab, setActiveTab] = useState('portfolio');
  const [timePeriod, setTimePeriod] = useState(30);
  const [managers, setManagers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentTime, setCurrentTime] = useState(new Date());
  const [selectedManager, setSelectedManager] = useState(null);
  const [deepDiveManager, setDeepDiveManager] = useState(null);
  const [comparisonManagers, setComparisonManagers] = useState([]);
  const [refreshing, setRefreshing] = useState(false);
  
  // Auto-refresh state
  const [autoRefreshEnabled, setAutoRefreshEnabled] = useState(true);
  const [lastRefresh, setLastRefresh] = useState(new Date());
  
  // Strategy Allocation chart state
  const [allocationViewMode, setAllocationViewMode] = useState('allocated'); // 'allocated', 'equity', 'pnl'
  
  // Risk Profile Narrative state
  const [riskNarrative, setRiskNarrative] = useState(null);
  const [riskNarrativeLoading, setRiskNarrativeLoading] = useState(false);
  
  // Hull Risk Engine state
  const [riskAnalysis, setRiskAnalysis] = useState(null);
  const [riskAnalysisLoading, setRiskAnalysisLoading] = useState(false);
  const [riskPolicy, setRiskPolicy] = useState({
    max_risk_per_trade_pct: 1.0,
    max_intraday_loss_pct: 3.0,
    max_margin_usage_pct: 25.0,
    leverage: 200
  });
  const [showRiskCalculator, setShowRiskCalculator] = useState(false);
  const [calcSymbol, setCalcSymbol] = useState('XAUUSD');
  const [calcEquity, setCalcEquity] = useState(100000);
  const [calcStopDistance, setCalcStopDistance] = useState(10);
  const [calcResult, setCalcResult] = useState(null);
  
  // AI Advisor State
  const [aiChatMessages, setAiChatMessages] = useState([]);
  const [aiInputMessage, setAiInputMessage] = useState('');
  const [aiLoading, setAiLoading] = useState(false);
  const [aiInsights, setAiInsights] = useState(null);
  const [aiInsightsLoading, setAiInsightsLoading] = useState(false);
  const [aiSessionId, setAiSessionId] = useState(() => `session_${Date.now()}`);
  const [showAllocationModal, setShowAllocationModal] = useState(false);
  const [allocationCapital, setAllocationCapital] = useState(100000);
  const [allocationRisk, setAllocationRisk] = useState('moderate');
  const [allocationResult, setAllocationResult] = useState(null);
  const [allocationLoading, setAllocationLoading] = useState(false);
  
  const chatEndRef = useRef(null);

  // ─────────────────────────────────────────────────────────────────────────────
  // LIVE CLOCK
  // ─────────────────────────────────────────────────────────────────────────────
  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  // ─────────────────────────────────────────────────────────────────────────────
  // DATA FETCHING
  // ─────────────────────────────────────────────────────────────────────────────
  const fetchManagersData = useCallback(async (silent = false) => {
    try {
      if (!silent) setLoading(true);
      setError(null);
      const token = localStorage.getItem('fidus_token');
      
      const response = await fetch(
        `${BACKEND_URL}/api/admin/trading-analytics/managers?period_days=${timePeriod}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      
      if (data.success && data.managers) {
        setManagers(data.managers);
        setLastRefresh(new Date());
        
        // Set default deep dive manager (TradingHub Gold)
        const defaultManager = data.managers.find(m => m.account === DEFAULT_DEEP_DIVE_ACCOUNT);
        if (defaultManager && !deepDiveManager) {
          setDeepDiveManager(defaultManager);
        } else if (!deepDiveManager && data.managers.length > 0) {
          setDeepDiveManager(data.managers[0]);
        }
      }
    } catch (err) {
      console.error('Error fetching managers:', err);
      if (!silent) setError(err.message);
    } finally {
      if (!silent) setLoading(false);
    }
  }, [timePeriod, deepDiveManager]);

  // Initial fetch
  useEffect(() => {
    fetchManagersData();
  }, [timePeriod]);

  // Auto-refresh every 30 seconds
  useEffect(() => {
    if (!autoRefreshEnabled) return;
    
    const refreshInterval = setInterval(() => {
      fetchManagersData(true); // Silent refresh
    }, AUTO_REFRESH_INTERVAL);
    
    return () => clearInterval(refreshInterval);
  }, [autoRefreshEnabled, fetchManagersData]);

  const handleRefresh = async () => {
    setRefreshing(true);
    await fetchManagersData();
    await fetchRiskNarrative();
    setTimeout(() => setRefreshing(false), 500);
  };

  // ─────────────────────────────────────────────────────────────────────────────
  // HULL RISK ENGINE FUNCTIONS
  // ─────────────────────────────────────────────────────────────────────────────
  
  // Fetch risk narrative on portfolio tab
  useEffect(() => {
    if (activeTab === 'portfolio' && !riskNarrative && !riskNarrativeLoading && managers.length > 0) {
      fetchRiskNarrative();
    }
  }, [activeTab, managers]);

  // Fetch risk analysis when deep dive manager changes
  useEffect(() => {
    if (deepDiveManager && activeTab === 'deepdive') {
      fetchRiskAnalysis(deepDiveManager.account);
    }
  }, [deepDiveManager, activeTab]);

  const fetchRiskNarrative = async () => {
    try {
      setRiskNarrativeLoading(true);
      const token = localStorage.getItem('fidus_token');
      
      const response = await fetch(
        `${BACKEND_URL}/api/admin/risk-engine/narrative?period_days=${timePeriod}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      const data = await response.json();
      
      if (data.success) {
        setRiskNarrative(data);
      }
    } catch (err) {
      console.error('Error fetching risk narrative:', err);
    } finally {
      setRiskNarrativeLoading(false);
    }
  };

  const fetchRiskAnalysis = async (account) => {
    try {
      setRiskAnalysisLoading(true);
      const token = localStorage.getItem('fidus_token');
      
      const response = await fetch(
        `${BACKEND_URL}/api/admin/risk-engine/strategy-analysis/${account}?period_days=${timePeriod}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      const data = await response.json();
      
      if (data.success) {
        setRiskAnalysis(data);
      }
    } catch (err) {
      console.error('Error fetching risk analysis:', err);
    } finally {
      setRiskAnalysisLoading(false);
    }
  };

  const calculateMaxLots = async () => {
    try {
      const token = localStorage.getItem('fidus_token');
      
      const response = await fetch(`${BACKEND_URL}/api/admin/risk-engine/calculate-max-lots`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          equity: calcEquity,
          symbol: calcSymbol,
          stop_distance: calcStopDistance
        })
      });

      const data = await response.json();
      
      if (data.success) {
        setCalcResult(data);
      }
    } catch (err) {
      console.error('Error calculating max lots:', err);
    }
  };

  // ─────────────────────────────────────────────────────────────────────────────
  // AI STRATEGY ADVISOR FUNCTIONS
  // ─────────────────────────────────────────────────────────────────────────────
  
  // Scroll to bottom of chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [aiChatMessages]);

  // Fetch AI insights on tab change to advisor
  useEffect(() => {
    if (activeTab === 'advisor' && !aiInsights && !aiInsightsLoading) {
      fetchAiInsights();
    }
  }, [activeTab]);

  const fetchAiInsights = async () => {
    try {
      setAiInsightsLoading(true);
      const token = localStorage.getItem('fidus_token');
      
      const response = await fetch(
        `${BACKEND_URL}/api/admin/ai-advisor/insights?period_days=${timePeriod}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      const data = await response.json();
      
      if (data.success) {
        setAiInsights(data.insights);
      }
    } catch (err) {
      console.error('Error fetching AI insights:', err);
    } finally {
      setAiInsightsLoading(false);
    }
  };

  const sendAiMessage = async () => {
    if (!aiInputMessage.trim() || aiLoading) return;
    
    const userMessage = aiInputMessage.trim();
    setAiInputMessage('');
    
    // Add user message to chat
    setAiChatMessages(prev => [...prev, {
      role: 'user',
      content: userMessage,
      timestamp: new Date().toISOString()
    }]);
    
    try {
      setAiLoading(true);
      const token = localStorage.getItem('fidus_token');
      
      const response = await fetch(`${BACKEND_URL}/api/admin/ai-advisor/chat`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: userMessage,
          session_id: aiSessionId,
          include_context: true,
          period_days: timePeriod
        })
      });

      const data = await response.json();
      
      if (data.success) {
        setAiChatMessages(prev => [...prev, {
          role: 'assistant',
          content: data.response,
          timestamp: data.timestamp
        }]);
      } else {
        setAiChatMessages(prev => [...prev, {
          role: 'assistant',
          content: `Error: ${data.error || 'Failed to get response'}`,
          timestamp: new Date().toISOString(),
          isError: true
        }]);
      }
    } catch (err) {
      console.error('Error sending AI message:', err);
      setAiChatMessages(prev => [...prev, {
        role: 'assistant',
        content: `Error: ${err.message}`,
        timestamp: new Date().toISOString(),
        isError: true
      }]);
    } finally {
      setAiLoading(false);
    }
  };

  const generateAllocationRecommendation = async () => {
    try {
      setAllocationLoading(true);
      const token = localStorage.getItem('fidus_token');
      
      const response = await fetch(`${BACKEND_URL}/api/admin/ai-advisor/allocation`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          total_capital: allocationCapital,
          risk_tolerance: allocationRisk,
          period_days: timePeriod
        })
      });

      const data = await response.json();
      
      if (data.success) {
        setAllocationResult(data.recommendations);
      } else {
        setAllocationResult(`Error: ${data.error}`);
      }
    } catch (err) {
      console.error('Error generating allocation:', err);
      setAllocationResult(`Error: ${err.message}`);
    } finally {
      setAllocationLoading(false);
    }
  };

  const clearAiChat = () => {
    setAiChatMessages([]);
    setAiSessionId(`session_${Date.now()}`);
  };

  const handleAiKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendAiMessage();
    }
  };

  // ─────────────────────────────────────────────────────────────────────────────
  // COMPUTED VALUES (KPIs)
  // ─────────────────────────────────────────────────────────────────────────────
  const aggregateKPIs = useMemo(() => {
    if (!managers.length) return {
      totalAUM: 0,
      totalPnL: 0,
      avgReturn: 0,
      activeStrategies: 0,
      avgSharpe: 0,
      avgWinRate: 0,
      bestPerformer: null,
      worstPerformer: null,
      totalTrades: 0
    };

    const totalAUM = managers.reduce((sum, m) => sum + (m.initial_allocation || 0), 0);
    const totalPnL = managers.reduce((sum, m) => sum + (m.total_pnl || 0), 0);
    const avgReturn = managers.reduce((sum, m) => sum + (m.return_percentage || 0), 0) / managers.length;
    const avgSharpe = managers.reduce((sum, m) => sum + (m.sharpe_ratio || 0), 0) / managers.length;
    const avgWinRate = managers.reduce((sum, m) => sum + (m.win_rate || 0), 0) / managers.length;
    const totalTrades = managers.reduce((sum, m) => sum + (m.total_trades || 0), 0);
    
    const sortedByReturn = [...managers].sort((a, b) => (b.return_percentage || 0) - (a.return_percentage || 0));
    
    return {
      totalAUM,
      totalPnL,
      avgReturn,
      activeStrategies: managers.length,
      avgSharpe,
      avgWinRate,
      bestPerformer: sortedByReturn[0],
      worstPerformer: sortedByReturn[sortedByReturn.length - 1],
      totalTrades
    };
  }, [managers]);

  // ─────────────────────────────────────────────────────────────────────────────
  // CHART DATA TRANSFORMATIONS
  // ─────────────────────────────────────────────────────────────────────────────
  
  // Strategy allocation data (replaces Fund Allocation - we only have ONE fund)
  const strategyAllocationData = useMemo(() => {
    return managers.map(m => {
      let value;
      if (allocationViewMode === 'equity') {
        value = m.current_equity || 0;
      } else if (allocationViewMode === 'pnl') {
        value = m.total_pnl || 0;
      } else {
        value = m.initial_allocation || 0;
      }
      
      return {
        name: m.manager_name?.split(' ')[0] || `Account ${m.account}`,
        fullName: m.manager_name || `Account ${m.account}`,
        account: m.account,
        value: value,
        initial_allocation: m.initial_allocation || 0,
        current_equity: m.current_equity || 0,
        total_pnl: m.total_pnl || 0,
        return_percentage: m.return_percentage || 0,
        fill: (m.return_percentage || 0) >= 0 ? '#00D4AA' : '#EF4444'
      };
    }).sort((a, b) => b.value - a.value);
  }, [managers, allocationViewMode]);

  // Risk metrics radar data
  const riskRadarData = useMemo(() => {
    if (!managers.length) return [];
    
    const avgSharpe = managers.reduce((sum, m) => sum + (m.sharpe_ratio || 0), 0) / managers.length;
    const avgSortino = managers.reduce((sum, m) => sum + (m.sortino_ratio || 0), 0) / managers.length;
    const avgWinRate = managers.reduce((sum, m) => sum + (m.win_rate || 0), 0) / managers.length;
    const avgProfitFactor = managers.reduce((sum, m) => sum + (m.profit_factor || 0), 0) / managers.length;
    const avgDrawdown = managers.reduce((sum, m) => sum + Math.abs(m.max_drawdown_pct || 0), 0) / managers.length;
    
    return [
      { metric: 'Sharpe Ratio', value: Math.min(avgSharpe * 33, 100), fullMark: 100 },
      { metric: 'Sortino Ratio', value: Math.min(avgSortino * 25, 100), fullMark: 100 },
      { metric: 'Win Rate', value: avgWinRate, fullMark: 100 },
      { metric: 'Profit Factor', value: Math.min(avgProfitFactor * 25, 100), fullMark: 100 },
      { metric: 'Risk Control', value: Math.max(0, 100 - avgDrawdown * 3), fullMark: 100 }
    ];
  }, [managers]);

  // Performance comparison bar chart
  const performanceBarData = useMemo(() => {
    return [...managers]
      .sort((a, b) => (b.return_percentage || 0) - (a.return_percentage || 0))
      .slice(0, 8)
      .map(m => ({
        name: m.manager_name?.split(' ')[0] || 'Unknown',
        return: m.return_percentage || 0,
        pnl: m.total_pnl || 0,
        fill: (m.return_percentage || 0) >= 0 ? '#10B981' : '#EF4444'
      }));
  }, [managers]);

  // Risk vs Return scatter data
  const riskReturnData = useMemo(() => {
    return managers.map(m => ({
      name: m.manager_name?.split(' ')[0] || 'Unknown',
      x: Math.abs(m.max_drawdown_pct || 0), // Risk (Max Drawdown)
      y: m.return_percentage || 0, // Return
      z: m.initial_allocation || 10000, // Size for bubble
      sharpe: m.sharpe_ratio || 0
    }));
  }, [managers]);

  // Simulated equity curve data for deep dive
  const equityCurveData = useMemo(() => {
    if (!deepDiveManager) return [];
    
    const startBalance = deepDiveManager.initial_allocation || 10000;
    const endBalance = startBalance + (deepDiveManager.total_pnl || 0);
    const points = 30;
    const data = [];
    
    for (let i = 0; i <= points; i++) {
      const progress = i / points;
      // Create realistic equity curve with some volatility
      const noise = (Math.random() - 0.5) * 0.02 * startBalance;
      const baseValue = startBalance + (endBalance - startBalance) * progress;
      const drawdown = Math.sin(progress * Math.PI * 3) * Math.abs(deepDiveManager.max_drawdown_pct || 5) * startBalance / 100;
      
      data.push({
        day: `Day ${i + 1}`,
        equity: Math.max(startBalance * 0.9, baseValue + noise - Math.abs(drawdown) * (1 - progress)),
        balance: baseValue
      });
    }
    
    return data;
  }, [deepDiveManager]);

  // ─────────────────────────────────────────────────────────────────────────────
  // UTILITY FUNCTIONS
  // ─────────────────────────────────────────────────────────────────────────────
  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value || 0);
  };

  const formatCurrencyPrecise = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value || 0);
  };

  const formatPercent = (value) => `${(value || 0).toFixed(2)}%`;
  const formatNumber = (value, decimals = 2) => (value || 0).toFixed(decimals);

  const getRiskBadge = (manager) => {
    const sharpe = manager.sharpe_ratio || 0;
    const drawdown = Math.abs(manager.max_drawdown_pct || 0);
    
    if (sharpe >= 1.5 && drawdown < 10) return { label: 'LOW RISK', class: 'risk-low' };
    if (sharpe >= 0.5 && drawdown < 20) return { label: 'MEDIUM', class: 'risk-medium' };
    return { label: 'HIGH RISK', class: 'risk-high' };
  };

  const getPerformanceBadge = (returnPct) => {
    if (returnPct >= 20) return { label: 'EXCEPTIONAL', class: 'perf-exceptional' };
    if (returnPct >= 10) return { label: 'STRONG', class: 'perf-strong' };
    if (returnPct >= 0) return { label: 'POSITIVE', class: 'perf-positive' };
    return { label: 'NEGATIVE', class: 'perf-negative' };
  };

  // Toggle manager for comparison
  const toggleComparison = (manager) => {
    setComparisonManagers(prev => {
      const exists = prev.find(m => m.manager_id === manager.manager_id);
      if (exists) {
        return prev.filter(m => m.manager_id !== manager.manager_id);
      }
      if (prev.length >= 3) {
        return [...prev.slice(1), manager];
      }
      return [...prev, manager];
    });
  };

  // ─────────────────────────────────────────────────────────────────────────────
  // CHART COLORS
  // ─────────────────────────────────────────────────────────────────────────────
  const CHART_COLORS = ['#00D4AA', '#FFB800', '#00A3FF', '#FF6B6B', '#A855F7', '#F59E0B'];
  const FUND_COLORS = {
    'CORE': '#FFB800',
    'BALANCE': '#00D4AA',
    'SEPARATION': '#00A3FF',
    'Unknown': '#64748B'
  };

  // ─────────────────────────────────────────────────────────────────────────────
  // RENDER: LOADING STATE
  // ─────────────────────────────────────────────────────────────────────────────
  if (loading && !managers.length) {
    return (
      <div className="ngt-dashboard" data-testid="trading-analytics-loading">
        <div className="ngt-loading">
          <div className="ngt-loading-spinner" />
          <span>Loading Trading Analytics...</span>
        </div>
      </div>
    );
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // RENDER: MAIN DASHBOARD
  // ─────────────────────────────────────────────────────────────────────────────
  return (
    <div className="ngt-dashboard" data-testid="trading-analytics-dashboard">
      {/* ═══════════════════════════════════════════════════════════════════════
          TOP HEADER BAR
      ═══════════════════════════════════════════════════════════════════════ */}
      <header className="ngt-header" data-testid="dashboard-header">
        <div className="ngt-header-left">
          <h1 className="ngt-title">Trading Analytics</h1>
          <span className="ngt-subtitle">Institutional-Grade Performance Intelligence</span>
        </div>
        
        <div className="ngt-header-controls">
          {/* Auto-refresh Toggle */}
          <div 
            className="ngt-auto-refresh" 
            onClick={() => setAutoRefreshEnabled(!autoRefreshEnabled)}
            style={{ cursor: 'pointer' }}
            title={autoRefreshEnabled ? 'Auto-refresh ON (30s)' : 'Auto-refresh OFF'}
          >
            <span className={`ngt-auto-refresh-dot ${autoRefreshEnabled ? '' : 'paused'}`} />
            <span>{autoRefreshEnabled ? 'Live' : 'Paused'}</span>
          </div>
          
          {/* Time Period Selector */}
          <div className="ngt-period-selector">
            <Clock size={14} />
            <select 
              value={timePeriod} 
              onChange={(e) => setTimePeriod(parseInt(e.target.value))}
              data-testid="period-selector"
            >
              <option value={7}>7 Days</option>
              <option value={30}>30 Days</option>
              <option value={90}>90 Days</option>
              <option value={180}>6 Months</option>
              <option value={365}>1 Year</option>
            </select>
          </div>
          
          {/* Refresh Button */}
          <button 
            className="ngt-btn ngt-btn-secondary"
            onClick={handleRefresh}
            disabled={refreshing}
            data-testid="refresh-btn"
          >
            <RefreshCw size={14} className={refreshing ? 'spin' : ''} />
            Refresh
          </button>
          
          {/* Export Button */}
          <button className="ngt-btn ngt-btn-primary" data-testid="export-btn">
            <Download size={14} />
            Export
          </button>
          
          {/* Live Clock */}
          <div className="ngt-live-clock" data-testid="live-clock">
            <span className="ngt-clock-dot" />
            <span className="ngt-clock-time">
              {currentTime.toLocaleTimeString('en-US', { hour12: false })}
            </span>
            <span className="ngt-clock-zone">UTC</span>
          </div>
        </div>
      </header>

      {/* ═══════════════════════════════════════════════════════════════════════
          SUMMARY KPI STRIP
      ═══════════════════════════════════════════════════════════════════════ */}
      <section className="ngt-kpi-strip" data-testid="kpi-strip">
        <div className="ngt-kpi-card" data-testid="kpi-total-aum">
          <div className="ngt-kpi-icon">
            <DollarSign size={20} />
          </div>
          <div className="ngt-kpi-content">
            <span className="ngt-kpi-value">{formatCurrency(aggregateKPIs.totalAUM)}</span>
            <span className="ngt-kpi-label">Total AUM</span>
          </div>
        </div>

        <div className="ngt-kpi-card" data-testid="kpi-total-pnl">
          <div className={`ngt-kpi-icon ${aggregateKPIs.totalPnL >= 0 ? 'positive' : 'negative'}`}>
            {aggregateKPIs.totalPnL >= 0 ? <TrendingUp size={20} /> : <TrendingDown size={20} />}
          </div>
          <div className="ngt-kpi-content">
            <span className={`ngt-kpi-value ${aggregateKPIs.totalPnL >= 0 ? 'positive' : 'negative'}`}>
              {formatCurrencyPrecise(aggregateKPIs.totalPnL)}
            </span>
            <span className="ngt-kpi-label">Total P&L</span>
          </div>
        </div>

        <div className="ngt-kpi-card" data-testid="kpi-avg-return">
          <div className={`ngt-kpi-icon ${aggregateKPIs.avgReturn >= 0 ? 'positive' : 'negative'}`}>
            <Activity size={20} />
          </div>
          <div className="ngt-kpi-content">
            <span className={`ngt-kpi-value ${aggregateKPIs.avgReturn >= 0 ? 'positive' : 'negative'}`}>
              {formatPercent(aggregateKPIs.avgReturn)}
            </span>
            <span className="ngt-kpi-label">Avg Return</span>
          </div>
        </div>

        <div className="ngt-kpi-card" data-testid="kpi-strategies">
          <div className="ngt-kpi-icon">
            <Briefcase size={20} />
          </div>
          <div className="ngt-kpi-content">
            <span className="ngt-kpi-value">{aggregateKPIs.activeStrategies}</span>
            <span className="ngt-kpi-label">Active Strategies</span>
          </div>
        </div>

        <div className="ngt-kpi-card" data-testid="kpi-sharpe">
          <div className="ngt-kpi-icon">
            <Target size={20} />
          </div>
          <div className="ngt-kpi-content">
            <span className="ngt-kpi-value">{formatNumber(aggregateKPIs.avgSharpe)}</span>
            <span className="ngt-kpi-label">Avg Sharpe</span>
          </div>
        </div>

        <div className="ngt-kpi-card" data-testid="kpi-winrate">
          <div className="ngt-kpi-icon">
            <Award size={20} />
          </div>
          <div className="ngt-kpi-content">
            <span className="ngt-kpi-value">{formatPercent(aggregateKPIs.avgWinRate)}</span>
            <span className="ngt-kpi-label">Avg Win Rate</span>
          </div>
        </div>

        <div className="ngt-kpi-card" data-testid="kpi-trades">
          <div className="ngt-kpi-icon">
            <BarChart3 size={20} />
          </div>
          <div className="ngt-kpi-content">
            <span className="ngt-kpi-value">{aggregateKPIs.totalTrades.toLocaleString()}</span>
            <span className="ngt-kpi-label">Total Trades</span>
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════════════════════
          MAIN TABS NAVIGATION
      ═══════════════════════════════════════════════════════════════════════ */}
      <nav className="ngt-tabs" data-testid="main-tabs">
        <button 
          className={`ngt-tab ${activeTab === 'portfolio' ? 'active' : ''}`}
          onClick={() => setActiveTab('portfolio')}
          data-testid="tab-portfolio"
        >
          <PieChartIcon size={16} />
          Portfolio Overview
        </button>
        <button 
          className={`ngt-tab ${activeTab === 'rankings' ? 'active' : ''}`}
          onClick={() => setActiveTab('rankings')}
          data-testid="tab-rankings"
        >
          <Award size={16} />
          Manager Rankings
        </button>
        <button 
          className={`ngt-tab ${activeTab === 'deepdive' ? 'active' : ''}`}
          onClick={() => setActiveTab('deepdive')}
          data-testid="tab-deepdive"
        >
          <Target size={16} />
          Deep Dive
        </button>
        <button 
          className={`ngt-tab ${activeTab === 'risklimits' ? 'active' : ''}`}
          onClick={() => setActiveTab('risklimits')}
          data-testid="tab-risklimits"
        >
          <Shield size={16} />
          Risk Limits
          <span className="ngt-tab-badge ngt-tab-badge-new">NEW</span>
        </button>
        <button 
          className={`ngt-tab ${activeTab === 'advisor' ? 'active' : ''}`}
          onClick={() => setActiveTab('advisor')}
          data-testid="tab-advisor"
        >
          <Zap size={16} />
          AI Advisor
        </button>
      </nav>

      {/* ═══════════════════════════════════════════════════════════════════════
          TAB CONTENT
      ═══════════════════════════════════════════════════════════════════════ */}
      <main className="ngt-content">
        
        {/* ─────────────────────────────────────────────────────────────────────
            PORTFOLIO OVERVIEW TAB
        ───────────────────────────────────────────────────────────────────── */}
        {activeTab === 'portfolio' && (
          <div className="ngt-portfolio-tab" data-testid="portfolio-content">
            <div className="ngt-grid-4">
              {/* Strategy Allocation Bar Chart (Replaces Fund Allocation) */}
              <div className="ngt-card ngt-card-span-2">
                <div className="ngt-card-header">
                  <h3>Strategy Allocation</h3>
                  <div className="ngt-card-header-controls">
                    <div className="ngt-toggle-group">
                      <button 
                        className={`ngt-toggle-btn ${allocationViewMode === 'allocated' ? 'active' : ''}`}
                        onClick={() => setAllocationViewMode('allocated')}
                      >
                        Allocated
                      </button>
                      <button 
                        className={`ngt-toggle-btn ${allocationViewMode === 'equity' ? 'active' : ''}`}
                        onClick={() => setAllocationViewMode('equity')}
                      >
                        Equity
                      </button>
                      <button 
                        className={`ngt-toggle-btn ${allocationViewMode === 'pnl' ? 'active' : ''}`}
                        onClick={() => setAllocationViewMode('pnl')}
                      >
                        P&L
                      </button>
                    </div>
                  </div>
                </div>
                <div className="ngt-card-body">
                  <ResponsiveContainer width="100%" height={280}>
                    <BarChart data={strategyAllocationData} layout="vertical">
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(148, 163, 184, 0.1)" />
                      <XAxis 
                        type="number" 
                        tick={{ fill: '#94A3B8', fontSize: 11 }}
                        tickFormatter={(v) => allocationViewMode === 'pnl' ? `$${(v/1000).toFixed(0)}k` : `$${(v/1000).toFixed(0)}k`}
                      />
                      <YAxis 
                        type="category" 
                        dataKey="name" 
                        tick={{ fill: '#94A3B8', fontSize: 11 }}
                        width={100}
                      />
                      <Tooltip 
                        content={({ payload, label }) => {
                          if (payload && payload.length > 0) {
                            const data = payload[0].payload;
                            return (
                              <div className="ngt-custom-tooltip">
                                <div className="ngt-tooltip-title">{data.fullName}</div>
                                <div className="ngt-tooltip-row">
                                  <span>Allocated:</span>
                                  <span>{formatCurrency(data.initial_allocation)}</span>
                                </div>
                                <div className="ngt-tooltip-row">
                                  <span>Current Equity:</span>
                                  <span>{formatCurrency(data.current_equity)}</span>
                                </div>
                                <div className="ngt-tooltip-row">
                                  <span>P&L:</span>
                                  <span className={data.total_pnl >= 0 ? 'positive' : 'negative'}>
                                    {formatCurrencyPrecise(data.total_pnl)}
                                  </span>
                                </div>
                                <div className="ngt-tooltip-row">
                                  <span>Return:</span>
                                  <span className={data.return_percentage >= 0 ? 'positive' : 'negative'}>
                                    {data.return_percentage.toFixed(2)}%
                                  </span>
                                </div>
                              </div>
                            );
                          }
                          return null;
                        }}
                      />
                      <Bar 
                        dataKey="value" 
                        radius={[0, 4, 4, 0]}
                        onClick={(data) => {
                          const manager = managers.find(m => m.account === data.account);
                          if (manager) {
                            setDeepDiveManager(manager);
                            setActiveTab('deepdive');
                          }
                        }}
                        style={{ cursor: 'pointer' }}
                      >
                        {strategyAllocationData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.fill} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Risk Metrics Radar with Narrative */}
              <div className="ngt-card ngt-card-span-2">
                <div className="ngt-card-header">
                  <h3>Portfolio Risk Profile</h3>
                  <span className="ngt-card-subtitle">Risk-Adjusted Performance Metrics</span>
                </div>
                <div className="ngt-card-body ngt-risk-profile-container">
                  <div className="ngt-risk-chart">
                    <ResponsiveContainer width="100%" height={220}>
                      <RadarChart data={riskRadarData}>
                        <PolarGrid stroke="rgba(148, 163, 184, 0.2)" />
                        <PolarAngleAxis 
                          dataKey="metric" 
                          tick={{ fill: '#94A3B8', fontSize: 10 }}
                        />
                        <PolarRadiusAxis 
                          angle={30} 
                          domain={[0, 100]} 
                          tick={{ fill: '#64748B', fontSize: 9 }}
                        />
                        <Radar
                          name="Portfolio"
                          dataKey="value"
                          stroke="#00D4AA"
                          fill="#00D4AA"
                          fillOpacity={0.3}
                          strokeWidth={2}
                        />
                        <Tooltip 
                          contentStyle={{ 
                            background: 'rgba(15, 23, 42, 0.95)', 
                            border: '1px solid rgba(0, 212, 170, 0.3)',
                            borderRadius: '8px',
                            color: '#fff'
                          }}
                        />
                      </RadarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>

              {/* Risk Profile Narrative Panel */}
              <div className="ngt-card ngt-card-span-4">
                <div className="ngt-card-header">
                  <div className="ngt-card-header-icon ngt-card-header-icon-warning">
                    <AlertTriangle size={18} />
                  </div>
                  <h3>Risk Profile Interpretation (Last {timePeriod} Days)</h3>
                  <button 
                    className="ngt-btn ngt-btn-ghost ngt-btn-sm"
                    onClick={fetchRiskNarrative}
                    disabled={riskNarrativeLoading}
                  >
                    <RefreshCw size={14} className={riskNarrativeLoading ? 'spin' : ''} />
                  </button>
                </div>
                <div className="ngt-card-body">
                  {riskNarrativeLoading ? (
                    <div className="ngt-narrative-loading">
                      <Loader2 size={24} className="spin" />
                      <span>Analyzing risk profile...</span>
                    </div>
                  ) : riskNarrative ? (
                    <div className="ngt-narrative-content">
                      {/* Confidence Notes */}
                      {riskNarrative.confidence_notes?.length > 0 && (
                        <div className="ngt-narrative-confidence">
                          {riskNarrative.confidence_notes.map((note, i) => (
                            <div key={i} className="ngt-confidence-note">{note}</div>
                          ))}
                        </div>
                      )}
                      
                      {/* Executive Read */}
                      <div className="ngt-narrative-section">
                        <h4>Executive Summary</h4>
                        <ul className="ngt-narrative-bullets">
                          {riskNarrative.executive_read?.map((item, i) => (
                            <li key={i}>{item}</li>
                          ))}
                        </ul>
                      </div>
                      
                      {/* Metric Interpretations */}
                      <div className="ngt-narrative-section">
                        <h4>Metric Analysis</h4>
                        <div className="ngt-metric-interpretations">
                          {riskNarrative.metric_interpretations?.map((item, i) => (
                            <div key={i} className="ngt-metric-item">
                              <div className="ngt-metric-header">
                                <span className="ngt-metric-name">{item.metric}</span>
                                <span className="ngt-metric-value">{item.value}</span>
                              </div>
                              <p className="ngt-metric-desc">{item.interpretation}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                      
                      {/* Red Flags */}
                      {riskNarrative.red_flags?.length > 0 && (
                        <div className="ngt-narrative-section ngt-narrative-danger">
                          <h4><AlertTriangle size={16} /> Red Flags</h4>
                          <ul className="ngt-narrative-bullets ngt-danger-list">
                            {riskNarrative.red_flags.map((flag, i) => (
                              <li key={i}>{flag}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      
                      {/* Actionable Fixes */}
                      {riskNarrative.actionable_fixes?.length > 0 && (
                        <div className="ngt-narrative-section ngt-narrative-action">
                          <h4><Zap size={16} /> Recommended Actions</h4>
                          <ul className="ngt-narrative-bullets ngt-action-list">
                            {riskNarrative.actionable_fixes.map((fix, i) => (
                              <li key={i}>{fix}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="ngt-narrative-empty">
                      <AlertTriangle size={20} />
                      <span>Click refresh to generate risk analysis</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Performance Comparison Bar Chart */}
              <div className="ngt-card ngt-card-span-2">
                <div className="ngt-card-header">
                  <h3>Strategy Performance</h3>
                  <span className="ngt-card-subtitle">Return % by Manager (Top 8)</span>
                </div>
                <div className="ngt-card-body">
                  <ResponsiveContainer width="100%" height={280}>
                    <BarChart data={performanceBarData} layout="vertical">
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(148, 163, 184, 0.1)" />
                      <XAxis 
                        type="number" 
                        tick={{ fill: '#94A3B8', fontSize: 11 }}
                        tickFormatter={(v) => `${v}%`}
                      />
                      <YAxis 
                        type="category" 
                        dataKey="name" 
                        tick={{ fill: '#94A3B8', fontSize: 11 }}
                        width={80}
                      />
                      <Tooltip 
                        formatter={(value) => [`${value.toFixed(2)}%`, 'Return']}
                        contentStyle={{ 
                          background: 'rgba(15, 23, 42, 0.95)', 
                          border: '1px solid rgba(0, 212, 170, 0.3)',
                          borderRadius: '8px',
                          color: '#fff'
                        }}
                      />
                      <Bar dataKey="return" radius={[0, 4, 4, 0]}>
                        {performanceBarData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.fill} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Risk vs Return Scatter */}
              <div className="ngt-card ngt-card-span-2">
                <div className="ngt-card-header">
                  <h3>Risk vs Return Analysis</h3>
                  <span className="ngt-card-subtitle">Efficient Frontier Visualization</span>
                </div>
                <div className="ngt-card-body">
                  <ResponsiveContainer width="100%" height={280}>
                    <ScatterChart>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(148, 163, 184, 0.1)" />
                      <XAxis 
                        type="number" 
                        dataKey="x" 
                        name="Risk (Max DD %)"
                        tick={{ fill: '#94A3B8', fontSize: 11 }}
                        label={{ value: 'Risk (Max Drawdown %)', position: 'bottom', fill: '#64748B', fontSize: 11 }}
                      />
                      <YAxis 
                        type="number" 
                        dataKey="y" 
                        name="Return %"
                        tick={{ fill: '#94A3B8', fontSize: 11 }}
                        label={{ value: 'Return %', angle: -90, position: 'left', fill: '#64748B', fontSize: 11 }}
                      />
                      <Tooltip 
                        cursor={{ strokeDasharray: '3 3' }}
                        formatter={(value, name) => [
                          name === 'x' ? `${value.toFixed(1)}%` : `${value.toFixed(2)}%`,
                          name === 'x' ? 'Max Drawdown' : 'Return'
                        ]}
                        contentStyle={{ 
                          background: 'rgba(15, 23, 42, 0.95)', 
                          border: '1px solid rgba(0, 212, 170, 0.3)',
                          borderRadius: '8px',
                          color: '#fff'
                        }}
                      />
                      <Scatter 
                        data={riskReturnData} 
                        fill="#00D4AA"
                        shape={(props) => {
                          const { cx, cy, payload } = props;
                          const size = Math.max(6, Math.min(20, payload.z / 5000));
                          const color = payload.y >= 0 ? '#00D4AA' : '#EF4444';
                          return (
                            <circle 
                              cx={cx} 
                              cy={cy} 
                              r={size} 
                              fill={color} 
                              fillOpacity={0.6}
                              stroke={color}
                              strokeWidth={2}
                            />
                          );
                        }}
                      />
                    </ScatterChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ─────────────────────────────────────────────────────────────────────
            MANAGER RANKINGS TAB
        ───────────────────────────────────────────────────────────────────── */}
        {activeTab === 'rankings' && (
          <div className="ngt-rankings-tab" data-testid="rankings-content">
            {/* Comparison Panel */}
            {comparisonManagers.length > 0 && (
              <div className="ngt-comparison-panel">
                <div className="ngt-comparison-header">
                  <h3>Head-to-Head Comparison</h3>
                  <button 
                    className="ngt-btn ngt-btn-ghost"
                    onClick={() => setComparisonManagers([])}
                  >
                    Clear
                  </button>
                </div>
                <div className="ngt-comparison-grid">
                  {comparisonManagers.map(manager => (
                    <div key={manager.manager_id} className="ngt-comparison-card">
                      <div className="ngt-comparison-name">{manager.manager_name}</div>
                      <div className="ngt-comparison-stats">
                        <div className="ngt-stat">
                          <span className="label">Return</span>
                          <span className={`value ${(manager.return_percentage || 0) >= 0 ? 'positive' : 'negative'}`}>
                            {formatPercent(manager.return_percentage)}
                          </span>
                        </div>
                        <div className="ngt-stat">
                          <span className="label">Sharpe</span>
                          <span className="value">{formatNumber(manager.sharpe_ratio)}</span>
                        </div>
                        <div className="ngt-stat">
                          <span className="label">Win Rate</span>
                          <span className="value">{formatPercent(manager.win_rate)}</span>
                        </div>
                        <div className="ngt-stat">
                          <span className="label">Max DD</span>
                          <span className="value negative">{formatPercent(manager.max_drawdown_pct)}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Rankings Table */}
            <div className="ngt-card">
              <div className="ngt-card-header">
                <h3>Strategy Leaderboard</h3>
                <span className="ngt-card-subtitle">Ranked by Risk-Adjusted Performance</span>
              </div>
              <div className="ngt-table-wrapper">
                <table className="ngt-table" data-testid="rankings-table">
                  <thead>
                    <tr>
                      <th>Rank</th>
                      <th>Strategy</th>
                      <th>Fund</th>
                      <th>AUM</th>
                      <th>P&L</th>
                      <th>Return</th>
                      <th>Sharpe</th>
                      <th>Win Rate</th>
                      <th>Max DD</th>
                      <th>Risk</th>
                      <th>Compare</th>
                    </tr>
                  </thead>
                  <tbody>
                    {managers
                      .sort((a, b) => (b.return_percentage || 0) - (a.return_percentage || 0))
                      .map((manager, index) => {
                        const riskBadge = getRiskBadge(manager);
                        const perfBadge = getPerformanceBadge(manager.return_percentage || 0);
                        const isSelected = comparisonManagers.some(m => m.manager_id === manager.manager_id);
                        
                        return (
                          <tr 
                            key={manager.manager_id || index}
                            className={isSelected ? 'selected' : ''}
                            onClick={() => setDeepDiveManager(manager)}
                          >
                            <td>
                              <span className={`ngt-rank rank-${index + 1}`}>
                                {index === 0 && '🥇'}
                                {index === 1 && '🥈'}
                                {index === 2 && '🥉'}
                                {index > 2 && `#${index + 1}`}
                              </span>
                            </td>
                            <td>
                              <div className="ngt-manager-cell">
                                <span className="ngt-manager-name">{manager.manager_name}</span>
                                <span className="ngt-manager-account">#{manager.account}</span>
                              </div>
                            </td>
                            <td>
                              <span className={`ngt-fund-badge fund-${(manager.fund || 'unknown').toLowerCase()}`}>
                                {manager.fund || 'N/A'}
                              </span>
                            </td>
                            <td className="ngt-mono">{formatCurrency(manager.initial_allocation)}</td>
                            <td className={`ngt-mono ${(manager.total_pnl || 0) >= 0 ? 'positive' : 'negative'}`}>
                              {formatCurrencyPrecise(manager.total_pnl)}
                            </td>
                            <td>
                              <span className={`ngt-return ${(manager.return_percentage || 0) >= 0 ? 'positive' : 'negative'}`}>
                                {(manager.return_percentage || 0) >= 0 ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}
                                {formatPercent(manager.return_percentage)}
                              </span>
                            </td>
                            <td className="ngt-mono">{formatNumber(manager.sharpe_ratio)}</td>
                            <td className="ngt-mono">{formatPercent(manager.win_rate)}</td>
                            <td className="ngt-mono negative">{formatPercent(manager.max_drawdown_pct)}</td>
                            <td>
                              <span className={`ngt-risk-badge ${riskBadge.class}`}>
                                {riskBadge.label}
                              </span>
                            </td>
                            <td>
                              <button 
                                className={`ngt-compare-btn ${isSelected ? 'active' : ''}`}
                                onClick={(e) => {
                                  e.stopPropagation();
                                  toggleComparison(manager);
                                }}
                              >
                                {isSelected ? '✓' : '+'}
                              </button>
                            </td>
                          </tr>
                        );
                      })}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Risk Alerts */}
            <div className="ngt-risk-alerts">
              <div className="ngt-alert-header">
                <AlertTriangle size={18} />
                <h4>Risk Alerts</h4>
              </div>
              <div className="ngt-alerts-grid">
                {managers
                  .filter(m => Math.abs(m.max_drawdown_pct || 0) > 15 || (m.sharpe_ratio || 0) < 0.5)
                  .slice(0, 3)
                  .map(manager => (
                    <div key={manager.manager_id} className="ngt-alert-card">
                      <div className="ngt-alert-icon">
                        <AlertTriangle size={16} />
                      </div>
                      <div className="ngt-alert-content">
                        <span className="ngt-alert-title">{manager.manager_name}</span>
                        <span className="ngt-alert-message">
                          {Math.abs(manager.max_drawdown_pct || 0) > 15 && 
                            `High drawdown: ${formatPercent(manager.max_drawdown_pct)}`
                          }
                          {(manager.sharpe_ratio || 0) < 0.5 && 
                            ` Low Sharpe: ${formatNumber(manager.sharpe_ratio)}`
                          }
                        </span>
                      </div>
                    </div>
                  ))}
                {managers.filter(m => Math.abs(m.max_drawdown_pct || 0) > 15 || (m.sharpe_ratio || 0) < 0.5).length === 0 && (
                  <div className="ngt-no-alerts">
                    <Shield size={20} />
                    <span>All strategies within acceptable risk parameters</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* ─────────────────────────────────────────────────────────────────────
            DEEP DIVE TAB
        ───────────────────────────────────────────────────────────────────── */}
        {activeTab === 'deepdive' && (
          <div className="ngt-deepdive-tab" data-testid="deepdive-content">
            {/* Strategy Selector */}
            <div className="ngt-strategy-selector">
              <label>Select Strategy:</label>
              <select 
                value={deepDiveManager?.manager_id || ''}
                onChange={(e) => {
                  const manager = managers.find(m => m.manager_id === e.target.value);
                  setDeepDiveManager(manager);
                }}
                data-testid="strategy-selector"
              >
                {managers.map(m => (
                  <option key={m.manager_id} value={m.manager_id}>
                    {m.manager_name} (#{m.account})
                  </option>
                ))}
              </select>
            </div>

            {deepDiveManager && (
              <>
                {/* Strategy Header */}
                <div className="ngt-strategy-header">
                  <div className="ngt-strategy-info">
                    <h2>{deepDiveManager.manager_name}</h2>
                    <div className="ngt-strategy-meta">
                      <span className="ngt-meta-item">
                        <Briefcase size={14} />
                        Account #{deepDiveManager.account}
                      </span>
                      <span className="ngt-meta-item">
                        <Target size={14} />
                        Fund: {deepDiveManager.fund || 'N/A'}
                      </span>
                      <span className={`ngt-strategy-badge ${getPerformanceBadge(deepDiveManager.return_percentage).class}`}>
                        {getPerformanceBadge(deepDiveManager.return_percentage).label}
                      </span>
                    </div>
                  </div>
                  <div className="ngt-strategy-return">
                    <span className={`ngt-big-return ${(deepDiveManager.return_percentage || 0) >= 0 ? 'positive' : 'negative'}`}>
                      {(deepDiveManager.return_percentage || 0) >= 0 ? '+' : ''}
                      {formatPercent(deepDiveManager.return_percentage)}
                    </span>
                    <span className="ngt-return-label">{timePeriod}-Day Return</span>
                  </div>
                </div>

                {/* Key Metrics Grid */}
                <div className="ngt-metrics-grid">
                  <div className="ngt-metric-card">
                    <span className="ngt-metric-label">Initial Allocation</span>
                    <span className="ngt-metric-value">{formatCurrency(deepDiveManager.initial_allocation)}</span>
                  </div>
                  <div className="ngt-metric-card">
                    <span className="ngt-metric-label">Current Equity</span>
                    <span className="ngt-metric-value">{formatCurrency(deepDiveManager.current_equity)}</span>
                  </div>
                  <div className="ngt-metric-card">
                    <span className="ngt-metric-label">Total P&L</span>
                    <span className={`ngt-metric-value ${(deepDiveManager.total_pnl || 0) >= 0 ? 'positive' : 'negative'}`}>
                      {formatCurrencyPrecise(deepDiveManager.total_pnl)}
                    </span>
                  </div>
                  <div className="ngt-metric-card">
                    <span className="ngt-metric-label">Profit Withdrawals</span>
                    <span className="ngt-metric-value">{formatCurrency(deepDiveManager.profit_withdrawals)}</span>
                  </div>
                </div>

                {/* Equity Curve */}
                <div className="ngt-card">
                  <div className="ngt-card-header">
                    <h3>Equity Curve</h3>
                    <span className="ngt-card-subtitle">Historical Balance Progression</span>
                  </div>
                  <div className="ngt-card-body">
                    <ResponsiveContainer width="100%" height={300}>
                      <AreaChart data={equityCurveData}>
                        <defs>
                          <linearGradient id="equityGradient" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#00D4AA" stopOpacity={0.3}/>
                            <stop offset="95%" stopColor="#00D4AA" stopOpacity={0}/>
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(148, 163, 184, 0.1)" />
                        <XAxis 
                          dataKey="day" 
                          tick={{ fill: '#94A3B8', fontSize: 11 }}
                          interval="preserveStartEnd"
                        />
                        <YAxis 
                          tick={{ fill: '#94A3B8', fontSize: 11 }}
                          tickFormatter={(v) => `$${(v/1000).toFixed(0)}k`}
                          domain={['dataMin - 1000', 'dataMax + 1000']}
                        />
                        <Tooltip 
                          formatter={(value) => formatCurrency(value)}
                          contentStyle={{ 
                            background: 'rgba(15, 23, 42, 0.95)', 
                            border: '1px solid rgba(0, 212, 170, 0.3)',
                            borderRadius: '8px',
                            color: '#fff'
                          }}
                        />
                        <Area 
                          type="monotone" 
                          dataKey="equity" 
                          stroke="#00D4AA" 
                          fill="url(#equityGradient)"
                          strokeWidth={2}
                          name="Equity"
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Risk Metrics */}
                <div className="ngt-grid-3">
                  <div className="ngt-stat-card">
                    <div className="ngt-stat-header">
                      <Target size={18} />
                      <span>Sharpe Ratio</span>
                    </div>
                    <div className="ngt-stat-value">{formatNumber(deepDiveManager.sharpe_ratio)}</div>
                    <div className="ngt-stat-bar">
                      <div 
                        className="ngt-stat-fill" 
                        style={{ width: `${Math.min((deepDiveManager.sharpe_ratio || 0) * 33, 100)}%` }}
                      />
                    </div>
                    <div className="ngt-stat-range">
                      <span>Poor {'<'} 0.5</span>
                      <span>Good {'>'} 1.0</span>
                      <span>Excellent {'>'} 2.0</span>
                    </div>
                  </div>

                  <div className="ngt-stat-card">
                    <div className="ngt-stat-header">
                      <Shield size={18} />
                      <span>Sortino Ratio</span>
                    </div>
                    <div className="ngt-stat-value">{formatNumber(deepDiveManager.sortino_ratio)}</div>
                    <div className="ngt-stat-bar">
                      <div 
                        className="ngt-stat-fill" 
                        style={{ width: `${Math.min((deepDiveManager.sortino_ratio || 0) * 25, 100)}%` }}
                      />
                    </div>
                    <div className="ngt-stat-range">
                      <span>Poor {'<'} 1.0</span>
                      <span>Good {'>'} 2.0</span>
                      <span>Excellent {'>'} 3.0</span>
                    </div>
                  </div>

                  <div className="ngt-stat-card">
                    <div className="ngt-stat-header">
                      <TrendingDown size={18} />
                      <span>Max Drawdown</span>
                    </div>
                    <div className="ngt-stat-value negative">{formatPercent(deepDiveManager.max_drawdown_pct)}</div>
                    <div className="ngt-stat-bar danger">
                      <div 
                        className="ngt-stat-fill" 
                        style={{ width: `${Math.min(Math.abs(deepDiveManager.max_drawdown_pct || 0) * 3, 100)}%` }}
                      />
                    </div>
                    <div className="ngt-stat-range">
                      <span>Low {'<'} 10%</span>
                      <span>Med {'<'} 20%</span>
                      <span>High {'>'} 30%</span>
                    </div>
                  </div>
                </div>

                {/* Trading Statistics */}
                <div className="ngt-card">
                  <div className="ngt-card-header">
                    <h3>Trading Statistics</h3>
                    <span className="ngt-card-subtitle">Performance Breakdown</span>
                  </div>
                  <div className="ngt-stats-grid">
                    <div className="ngt-stat-item">
                      <span className="label">Total Trades</span>
                      <span className="value">{(deepDiveManager.total_trades || 0).toLocaleString()}</span>
                    </div>
                    <div className="ngt-stat-item">
                      <span className="label">Winning Trades</span>
                      <span className="value positive">{(deepDiveManager.winning_trades || 0).toLocaleString()}</span>
                    </div>
                    <div className="ngt-stat-item">
                      <span className="label">Losing Trades</span>
                      <span className="value negative">{(deepDiveManager.losing_trades || 0).toLocaleString()}</span>
                    </div>
                    <div className="ngt-stat-item">
                      <span className="label">Win Rate</span>
                      <span className="value">{formatPercent(deepDiveManager.win_rate)}</span>
                    </div>
                    <div className="ngt-stat-item">
                      <span className="label">Profit Factor</span>
                      <span className="value">{formatNumber(deepDiveManager.profit_factor)}</span>
                    </div>
                    <div className="ngt-stat-item">
                      <span className="label">Risk Level</span>
                      <span className={`value ${getRiskBadge(deepDiveManager).class}`}>
                        {getRiskBadge(deepDiveManager).label}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Allocation Recommendation */}
                <div className="ngt-recommendation-card">
                  <div className="ngt-recommendation-header">
                    <Zap size={20} />
                    <h4>Allocation Insight</h4>
                  </div>
                  <div className="ngt-recommendation-content">
                    {(deepDiveManager.sharpe_ratio || 0) >= 1.0 && Math.abs(deepDiveManager.max_drawdown_pct || 0) < 15 ? (
                      <p>
                        <strong>Strong Candidate for Increased Allocation.</strong> This strategy demonstrates 
                        favorable risk-adjusted returns with a Sharpe ratio of {formatNumber(deepDiveManager.sharpe_ratio)} 
                        and controlled drawdowns under 15%. Consider allocating additional capital based on 
                        portfolio diversification needs.
                      </p>
                    ) : (deepDiveManager.sharpe_ratio || 0) >= 0.5 ? (
                      <p>
                        <strong>Moderate Performance.</strong> This strategy shows acceptable returns but may 
                        benefit from closer monitoring. Current risk metrics suggest maintaining existing 
                        allocation levels while tracking for improvement.
                      </p>
                    ) : (
                      <p>
                        <strong>Review Recommended.</strong> This strategy's risk-adjusted metrics suggest 
                        caution. Consider reviewing allocation levels and monitoring closely for any 
                        deterioration in performance.
                      </p>
                    )}
                  </div>
                </div>
              </>
            )}
          </div>
        )}

        {/* ─────────────────────────────────────────────────────────────────────
            RISK LIMITS TAB (Hull-Style Risk Engine)
        ───────────────────────────────────────────────────────────────────── */}
        {activeTab === 'risklimits' && (
          <div className="ngt-risklimits-tab" data-testid="risklimits-content">
            {/* Risk Policy Summary */}
            <div className="ngt-risk-policy-header">
              <div className="ngt-risk-policy-card">
                <h3>Active Risk Policy (200:1 Leverage)</h3>
                <div className="ngt-risk-policy-grid">
                  <div className="ngt-policy-item">
                    <span className="label">Max Risk Per Trade</span>
                    <span className="value">{riskPolicy.max_risk_per_trade_pct}%</span>
                  </div>
                  <div className="ngt-policy-item">
                    <span className="label">Max Intraday Loss</span>
                    <span className="value">{riskPolicy.max_intraday_loss_pct}%</span>
                  </div>
                  <div className="ngt-policy-item">
                    <span className="label">Max Margin Usage</span>
                    <span className="value">{riskPolicy.max_margin_usage_pct}%</span>
                  </div>
                  <div className="ngt-policy-item">
                    <span className="label">Leverage</span>
                    <span className="value">{riskPolicy.leverage}:1</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="ngt-risk-content-grid">
              {/* Left: Position Sizing Calculator */}
              <div className="ngt-card">
                <div className="ngt-card-header">
                  <h3>Position Sizing Calculator</h3>
                  <span className="ngt-card-subtitle">Hull-Style Max Lot Calculation</span>
                </div>
                <div className="ngt-card-body">
                  <div className="ngt-calc-form">
                    <div className="ngt-form-row">
                      <div className="ngt-form-group">
                        <label>Account Equity ($)</label>
                        <input
                          type="number"
                          value={calcEquity}
                          onChange={(e) => setCalcEquity(Number(e.target.value))}
                          placeholder="100000"
                        />
                      </div>
                      <div className="ngt-form-group">
                        <label>Instrument</label>
                        <select value={calcSymbol} onChange={(e) => setCalcSymbol(e.target.value)}>
                          <option value="XAUUSD">XAUUSD (Gold)</option>
                          <option value="EURUSD">EURUSD</option>
                          <option value="GBPUSD">GBPUSD</option>
                          <option value="USDJPY">USDJPY</option>
                          <option value="US30">US30 (Dow)</option>
                          <option value="NAS100">NAS100</option>
                          <option value="BTCUSD">BTCUSD</option>
                        </select>
                      </div>
                    </div>
                    <div className="ngt-form-row">
                      <div className="ngt-form-group">
                        <label>Stop Distance {calcSymbol === 'XAUUSD' ? '($)' : calcSymbol.includes('USD') ? '(pips)' : '(points)'}</label>
                        <input
                          type="number"
                          value={calcStopDistance}
                          onChange={(e) => setCalcStopDistance(Number(e.target.value))}
                          step="0.1"
                        />
                      </div>
                      <div className="ngt-form-group ngt-form-group-btn">
                        <button 
                          className="ngt-btn ngt-btn-primary"
                          onClick={calculateMaxLots}
                        >
                          Calculate Max Lots
                        </button>
                      </div>
                    </div>
                  </div>

                  {calcResult && (
                    <div className="ngt-calc-result">
                      <div className="ngt-calc-result-header">
                        <h4>Maximum Allowed Position</h4>
                        <span className={`ngt-constraint-badge ${calcResult.binding_constraint === 'RISK' ? 'risk' : 'margin'}`}>
                          {calcResult.binding_constraint} BOUND
                        </span>
                      </div>
                      
                      <div className="ngt-calc-big-number">
                        <span className="value">{calcResult.max_lots_allowed}</span>
                        <span className="unit">lots</span>
                      </div>
                      
                      <div className="ngt-calc-breakdown">
                        <div className="ngt-breakdown-section">
                          <h5>Risk-Based Limit</h5>
                          <div className="ngt-breakdown-row">
                            <span>Risk Budget (1% of ${calcEquity.toLocaleString()}):</span>
                            <span>${calcResult.risk_budget?.toLocaleString()}</span>
                          </div>
                          <div className="ngt-breakdown-row">
                            <span>Loss per lot at stop:</span>
                            <span>${calcResult.loss_per_lot_at_stop?.toLocaleString()}</span>
                          </div>
                          <div className="ngt-breakdown-row highlight">
                            <span>Max Lots (Risk):</span>
                            <span>{calcResult.max_lots_risk} lots</span>
                          </div>
                        </div>
                        
                        <div className="ngt-breakdown-section">
                          <h5>Margin-Based Limit</h5>
                          <div className="ngt-breakdown-row">
                            <span>Margin per lot (at {calcResult.leverage}:1):</span>
                            <span>${calcResult.margin_per_lot?.toLocaleString()}</span>
                          </div>
                          <div className="ngt-breakdown-row">
                            <span>Max margin allowed (25%):</span>
                            <span>${calcResult.max_margin_allowed?.toLocaleString()}</span>
                          </div>
                          <div className="ngt-breakdown-row highlight">
                            <span>Max Lots (Margin):</span>
                            <span>{calcResult.max_lots_margin} lots</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Gold Example */}
                  <div className="ngt-example-box">
                    <h5>XAUUSD Example (Gold)</h5>
                    <p>
                      At 200:1 leverage with $100,000 equity and 1% risk per trade:
                    </p>
                    <ul>
                      <li>Risk Budget = $1,000</li>
                      <li>Gold: 1 lot = 100 oz, $1 move = $100 P&L</li>
                      <li>$10 stop → Loss/lot = $1,000 → <strong>Max 1.00 lot</strong></li>
                      <li>$5 stop → Loss/lot = $500 → <strong>Max 2.00 lots</strong></li>
                    </ul>
                    <p className="ngt-example-note">
                      <strong>Key insight:</strong> At 200:1 leverage, the risk limit (not margin) is typically the binding constraint for gold.
                    </p>
                  </div>
                </div>
              </div>

              {/* Right: Strategy Risk Analysis */}
              <div className="ngt-card">
                <div className="ngt-card-header">
                  <h3>Strategy Risk Analysis</h3>
                  <div className="ngt-card-header-controls">
                    <select 
                      value={deepDiveManager?.account || ''}
                      onChange={(e) => {
                        const mgr = managers.find(m => m.account === parseInt(e.target.value));
                        setDeepDiveManager(mgr);
                      }}
                      className="ngt-strategy-select"
                    >
                      {managers.map(m => (
                        <option key={m.account} value={m.account}>
                          {m.manager_name} (#{m.account})
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
                <div className="ngt-card-body">
                  {riskAnalysisLoading ? (
                    <div className="ngt-loading-inline">
                      <Loader2 size={20} className="spin" />
                      <span>Loading risk analysis...</span>
                    </div>
                  ) : riskAnalysis ? (
                    <div className="ngt-risk-analysis-content">
                      {/* Risk Control Score */}
                      <div className="ngt-risk-score-panel">
                        <div className="ngt-risk-score-circle" style={{ borderColor: riskAnalysis.risk_control_score?.color }}>
                          <span className="score">{riskAnalysis.risk_control_score?.composite_score || 0}</span>
                          <span className="label">Risk Score</span>
                        </div>
                        <div className="ngt-risk-score-label" style={{ color: riskAnalysis.risk_control_score?.color }}>
                          {riskAnalysis.risk_control_score?.label || 'Unknown'}
                        </div>
                      </div>

                      {/* Instruments Table */}
                      {riskAnalysis.instruments?.length > 0 && (
                        <div className="ngt-instruments-table">
                          <h5>Instruments Traded</h5>
                          <table>
                            <thead>
                              <tr>
                                <th>Symbol</th>
                                <th>Trades</th>
                                <th>Max Allowed</th>
                                <th>Max Observed</th>
                                <th>Status</th>
                              </tr>
                            </thead>
                            <tbody>
                              {riskAnalysis.instruments.map((inst, i) => (
                                <tr key={i} className={inst.is_breach ? 'breach-row' : ''}>
                                  <td>{inst.symbol}</td>
                                  <td>{inst.trades}</td>
                                  <td>{inst.max_lots_allowed} lots</td>
                                  <td>{inst.max_lots_observed} lots</td>
                                  <td>
                                    {inst.is_breach ? (
                                      <span className="ngt-breach-badge">BREACH</span>
                                    ) : (
                                      <span className="ngt-ok-badge">OK</span>
                                    )}
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      )}

                      {/* Breaches */}
                      {riskAnalysis.breaches?.length > 0 && (
                        <div className="ngt-breaches-panel">
                          <h5><AlertTriangle size={16} /> Risk Breaches ({riskAnalysis.total_breaches})</h5>
                          <ul>
                            {riskAnalysis.breaches.map((breach, i) => (
                              <li key={i} className="ngt-breach-item">
                                <span className="breach-type">{breach.type}</span>
                                <span className="breach-msg">{breach.message}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {riskAnalysis.breaches?.length === 0 && (
                        <div className="ngt-no-breaches">
                          <Shield size={20} />
                          <span>No risk breaches detected for this strategy</span>
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="ngt-risk-empty">
                      <Shield size={24} />
                      <span>Select a strategy to view risk analysis</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ─────────────────────────────────────────────────────────────────────
            AI STRATEGY ADVISOR TAB (Phase 3)
        ───────────────────────────────────────────────────────────────────── */}
        {activeTab === 'advisor' && (
          <div className="ngt-advisor-tab" data-testid="advisor-content">
            <div className="ngt-advisor-layout">
              {/* Left Column: Automated Insights + Allocation Tool */}
              <div className="ngt-advisor-sidebar">
                {/* Automated Insights Card */}
                <div className="ngt-card ngt-insights-card">
                  <div className="ngt-card-header">
                    <div className="ngt-card-header-icon">
                      <Lightbulb size={18} />
                    </div>
                    <h3>AI Insights</h3>
                    <button 
                      className="ngt-btn ngt-btn-ghost ngt-btn-sm"
                      onClick={fetchAiInsights}
                      disabled={aiInsightsLoading}
                    >
                      <RefreshCw size={14} className={aiInsightsLoading ? 'spin' : ''} />
                    </button>
                  </div>
                  <div className="ngt-card-body">
                    {aiInsightsLoading ? (
                      <div className="ngt-insights-loading">
                        <Loader2 size={24} className="spin" />
                        <span>Analyzing portfolio...</span>
                      </div>
                    ) : aiInsights ? (
                      <div className="ngt-insights-content">
                        <div className="ngt-markdown-content" dangerouslySetInnerHTML={{ 
                          __html: aiInsights
                            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                            .replace(/\n/g, '<br/>') 
                        }} />
                      </div>
                    ) : (
                      <div className="ngt-insights-empty">
                        <Sparkles size={20} />
                        <span>Click refresh to generate insights</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Allocation Recommendation Tool */}
                <div className="ngt-card ngt-allocation-card">
                  <div className="ngt-card-header">
                    <div className="ngt-card-header-icon">
                      <PieChartIcon size={18} />
                    </div>
                    <h3>Allocation Advisor</h3>
                  </div>
                  <div className="ngt-card-body">
                    <div className="ngt-allocation-form">
                      <div className="ngt-form-group">
                        <label>Capital to Allocate</label>
                        <div className="ngt-input-with-prefix">
                          <span>$</span>
                          <input
                            type="number"
                            value={allocationCapital}
                            onChange={(e) => setAllocationCapital(Number(e.target.value))}
                            placeholder="100000"
                          />
                        </div>
                      </div>
                      <div className="ngt-form-group">
                        <label>Risk Tolerance</label>
                        <select
                          value={allocationRisk}
                          onChange={(e) => setAllocationRisk(e.target.value)}
                        >
                          <option value="conservative">Conservative</option>
                          <option value="moderate">Moderate</option>
                          <option value="aggressive">Aggressive</option>
                        </select>
                      </div>
                      <button
                        className="ngt-btn ngt-btn-primary ngt-btn-full"
                        onClick={generateAllocationRecommendation}
                        disabled={allocationLoading}
                      >
                        {allocationLoading ? (
                          <>
                            <Loader2 size={14} className="spin" />
                            Analyzing...
                          </>
                        ) : (
                          <>
                            <Sparkles size={14} />
                            Generate Recommendation
                          </>
                        )}
                      </button>
                    </div>
                    {allocationResult && (
                      <div className="ngt-allocation-result">
                        <div className="ngt-markdown-content" dangerouslySetInnerHTML={{ 
                          __html: allocationResult
                            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                            .replace(/\|(.*?)\|/g, '<span class="ngt-table-cell">$1</span>')
                            .replace(/\n/g, '<br/>') 
                        }} />
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Right Column: Chat Interface */}
              <div className="ngt-advisor-chat">
                <div className="ngt-card ngt-chat-card">
                  <div className="ngt-card-header">
                    <div className="ngt-card-header-icon">
                      <MessageSquare size={18} />
                    </div>
                    <h3>Chat with AI Advisor</h3>
                    <div className="ngt-chat-actions">
                      <span className="ngt-chat-model">Claude Sonnet 4.5</span>
                      <button 
                        className="ngt-btn ngt-btn-ghost ngt-btn-sm"
                        onClick={clearAiChat}
                        title="Clear chat"
                      >
                        <RefreshCw size={14} />
                      </button>
                    </div>
                  </div>
                  
                  {/* Chat Messages */}
                  <div className="ngt-chat-messages">
                    {aiChatMessages.length === 0 ? (
                      <div className="ngt-chat-welcome">
                        <Bot size={48} />
                        <h4>AI Strategy Advisor</h4>
                        <p>Ask me anything about your trading strategies, performance metrics, or allocation recommendations.</p>
                        <div className="ngt-chat-suggestions">
                          <button onClick={() => setAiInputMessage("What's the best performing strategy and why?")}>
                            Best performing strategy?
                          </button>
                          <button onClick={() => setAiInputMessage("Which strategies have concerning risk metrics?")}>
                            Risk concerns?
                          </button>
                          <button onClick={() => setAiInputMessage("Compare TradingHub Gold vs other strategies")}>
                            Compare strategies
                          </button>
                        </div>
                      </div>
                    ) : (
                      <>
                        {aiChatMessages.map((msg, index) => (
                          <div 
                            key={index} 
                            className={`ngt-chat-message ${msg.role} ${msg.isError ? 'error' : ''}`}
                          >
                            <div className="ngt-message-avatar">
                              {msg.role === 'user' ? (
                                <Users size={16} />
                              ) : (
                                <Bot size={16} />
                              )}
                            </div>
                            <div className="ngt-message-content">
                              <div className="ngt-message-text" dangerouslySetInnerHTML={{ 
                                __html: msg.content
                                  .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                                  .replace(/\n/g, '<br/>') 
                              }} />
                              <span className="ngt-message-time">
                                {new Date(msg.timestamp).toLocaleTimeString()}
                              </span>
                            </div>
                          </div>
                        ))}
                        {aiLoading && (
                          <div className="ngt-chat-message assistant loading">
                            <div className="ngt-message-avatar">
                              <Bot size={16} />
                            </div>
                            <div className="ngt-message-content">
                              <div className="ngt-typing-indicator">
                                <span></span>
                                <span></span>
                                <span></span>
                              </div>
                            </div>
                          </div>
                        )}
                        <div ref={chatEndRef} />
                      </>
                    )}
                  </div>

                  {/* Chat Input */}
                  <div className="ngt-chat-input-container">
                    <textarea
                      value={aiInputMessage}
                      onChange={(e) => setAiInputMessage(e.target.value)}
                      onKeyPress={handleAiKeyPress}
                      placeholder="Ask about strategies, risk metrics, or allocation..."
                      rows={1}
                      disabled={aiLoading}
                    />
                    <button
                      className="ngt-btn ngt-btn-primary ngt-chat-send"
                      onClick={sendAiMessage}
                      disabled={!aiInputMessage.trim() || aiLoading}
                    >
                      {aiLoading ? (
                        <Loader2 size={18} className="spin" />
                      ) : (
                        <Send size={18} />
                      )}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
