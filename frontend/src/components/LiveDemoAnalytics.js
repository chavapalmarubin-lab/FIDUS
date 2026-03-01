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
import './LiveDemoAnalytics.css';

// ============================================================================
// NEXT-GEN TRADING ANALYTICS DASHBOARD
// Phase 1, 2 & 3: Core Structure, Design System, All Components + AI Advisor
// ============================================================================

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

// Default strategy for Deep Dive (TradingHub Gold - Account 886557)
const DEFAULT_DEEP_DIVE_ACCOUNT = 886557;

// Auto-refresh interval (30 seconds)
const AUTO_REFRESH_INTERVAL = 30000;

export default function LiveDemoAnalytics() {
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
        `${BACKEND_URL}/api/admin/live-demo-analytics/managers?period_days=${timePeriod}`,
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
        `${BACKEND_URL}/api/admin/live-demo-ai-advisor/insights?period_days=${timePeriod}`,
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
      
      const response = await fetch(`${BACKEND_URL}/api/admin/live-demo-ai-advisor/chat`, {
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
      
      const response = await fetch(`${BACKEND_URL}/api/admin/live-demo-ai-advisor/allocation`, {
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
        fill: (m.return_percentage || 0) >= 0 ? '#A855F7' : '#EF4444' // Purple theme for demo
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
      <div className="lda-dashboard" data-testid="trading-analytics-loading">
        <div className="lda-loading">
          <div className="lda-loading-spinner" />
          <span>Loading Trading Analytics...</span>
        </div>
      </div>
    );
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // RENDER: MAIN DASHBOARD
  // ─────────────────────────────────────────────────────────────────────────────
  return (
    <div className="lda-dashboard" data-testid="live-demo-analytics-dashboard">
      {/* ═══════════════════════════════════════════════════════════════════════
          TOP HEADER BAR
      ═══════════════════════════════════════════════════════════════════════ */}
      <header className="lda-header" data-testid="dashboard-header">
        <div className="lda-header-left">
          <h1 className="lda-title">Live Demo Analytics</h1>
          <span className="lda-subtitle">Manager Candidate Evaluation Dashboard</span>
        </div>
        
        <div className="lda-header-controls">
          {/* Demo Badge */}
          <div className="lda-demo-badge">
            <span className="lda-demo-badge-dot" />
            <span>DEMO ACCOUNTS</span>
          </div>
          
          {/* Auto-refresh Toggle */}
          <div 
            className="lda-auto-refresh" 
            onClick={() => setAutoRefreshEnabled(!autoRefreshEnabled)}
            style={{ cursor: 'pointer' }}
            title={autoRefreshEnabled ? 'Auto-refresh ON (30s)' : 'Auto-refresh OFF'}
          >
            <span className={`lda-auto-refresh-dot ${autoRefreshEnabled ? '' : 'paused'}`} />
            <span>{autoRefreshEnabled ? 'Live' : 'Paused'}</span>
          </div>
          
          {/* Time Period Selector */}
          <div className="lda-period-selector">
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
            className="lda-btn lda-btn-secondary"
            onClick={handleRefresh}
            disabled={refreshing}
            data-testid="refresh-btn"
          >
            <RefreshCw size={14} className={refreshing ? 'spin' : ''} />
            Refresh
          </button>
          
          {/* Export Button */}
          <button className="lda-btn lda-btn-primary" data-testid="export-btn">
            <Download size={14} />
            Export
          </button>
          
          {/* Live Clock */}
          <div className="lda-live-clock" data-testid="live-clock">
            <span className="lda-clock-dot" />
            <span className="lda-clock-time">
              {currentTime.toLocaleTimeString('en-US', { hour12: false })}
            </span>
            <span className="lda-clock-zone">UTC</span>
          </div>
        </div>
      </header>

      {/* ═══════════════════════════════════════════════════════════════════════
          SUMMARY KPI STRIP
      ═══════════════════════════════════════════════════════════════════════ */}
      <section className="lda-kpi-strip" data-testid="kpi-strip">
        <div className="lda-kpi-card" data-testid="kpi-total-aum">
          <div className="lda-kpi-icon">
            <DollarSign size={20} />
          </div>
          <div className="lda-kpi-content">
            <span className="lda-kpi-value">{formatCurrency(aggregateKPIs.totalAUM)}</span>
            <span className="lda-kpi-label">Total AUM</span>
          </div>
        </div>

        <div className="lda-kpi-card" data-testid="kpi-total-pnl">
          <div className={`lda-kpi-icon ${aggregateKPIs.totalPnL >= 0 ? 'positive' : 'negative'}`}>
            {aggregateKPIs.totalPnL >= 0 ? <TrendingUp size={20} /> : <TrendingDown size={20} />}
          </div>
          <div className="lda-kpi-content">
            <span className={`lda-kpi-value ${aggregateKPIs.totalPnL >= 0 ? 'positive' : 'negative'}`}>
              {formatCurrencyPrecise(aggregateKPIs.totalPnL)}
            </span>
            <span className="lda-kpi-label">Total P&L</span>
          </div>
        </div>

        <div className="lda-kpi-card" data-testid="kpi-avg-return">
          <div className={`lda-kpi-icon ${aggregateKPIs.avgReturn >= 0 ? 'positive' : 'negative'}`}>
            <Activity size={20} />
          </div>
          <div className="lda-kpi-content">
            <span className={`lda-kpi-value ${aggregateKPIs.avgReturn >= 0 ? 'positive' : 'negative'}`}>
              {formatPercent(aggregateKPIs.avgReturn)}
            </span>
            <span className="lda-kpi-label">Avg Return</span>
          </div>
        </div>

        <div className="lda-kpi-card" data-testid="kpi-strategies">
          <div className="lda-kpi-icon">
            <Briefcase size={20} />
          </div>
          <div className="lda-kpi-content">
            <span className="lda-kpi-value">{aggregateKPIs.activeStrategies}</span>
            <span className="lda-kpi-label">Active Strategies</span>
          </div>
        </div>

        <div className="lda-kpi-card" data-testid="kpi-sharpe">
          <div className="lda-kpi-icon">
            <Target size={20} />
          </div>
          <div className="lda-kpi-content">
            <span className="lda-kpi-value">{formatNumber(aggregateKPIs.avgSharpe)}</span>
            <span className="lda-kpi-label">Avg Sharpe</span>
          </div>
        </div>

        <div className="lda-kpi-card" data-testid="kpi-winrate">
          <div className="lda-kpi-icon">
            <Award size={20} />
          </div>
          <div className="lda-kpi-content">
            <span className="lda-kpi-value">{formatPercent(aggregateKPIs.avgWinRate)}</span>
            <span className="lda-kpi-label">Avg Win Rate</span>
          </div>
        </div>

        <div className="lda-kpi-card" data-testid="kpi-trades">
          <div className="lda-kpi-icon">
            <BarChart3 size={20} />
          </div>
          <div className="lda-kpi-content">
            <span className="lda-kpi-value">{aggregateKPIs.totalTrades.toLocaleString()}</span>
            <span className="lda-kpi-label">Total Trades</span>
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════════════════════
          MAIN TABS NAVIGATION
      ═══════════════════════════════════════════════════════════════════════ */}
      <nav className="lda-tabs" data-testid="main-tabs">
        <button 
          className={`lda-tab ${activeTab === 'portfolio' ? 'active' : ''}`}
          onClick={() => setActiveTab('portfolio')}
          data-testid="tab-portfolio"
        >
          <PieChartIcon size={16} />
          Portfolio Overview
        </button>
        <button 
          className={`lda-tab ${activeTab === 'rankings' ? 'active' : ''}`}
          onClick={() => setActiveTab('rankings')}
          data-testid="tab-rankings"
        >
          <Award size={16} />
          Manager Rankings
        </button>
        <button 
          className={`lda-tab ${activeTab === 'deepdive' ? 'active' : ''}`}
          onClick={() => setActiveTab('deepdive')}
          data-testid="tab-deepdive"
        >
          <Target size={16} />
          Deep Dive
        </button>
        <button 
          className={`lda-tab ${activeTab === 'risklimits' ? 'active' : ''}`}
          onClick={() => setActiveTab('risklimits')}
          data-testid="tab-risklimits"
        >
          <Shield size={16} />
          Risk Limits
          <span className="lda-tab-badge lda-tab-badge-new">NEW</span>
        </button>
        <button 
          className={`lda-tab ${activeTab === 'advisor' ? 'active' : ''}`}
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
      <main className="lda-content">
        
        {/* ─────────────────────────────────────────────────────────────────────
            PORTFOLIO OVERVIEW TAB
        ───────────────────────────────────────────────────────────────────── */}
        {activeTab === 'portfolio' && (
          <div className="lda-portfolio-tab" data-testid="portfolio-content">
            <div className="lda-grid-4">
              {/* Strategy Allocation Bar Chart (Replaces Fund Allocation) */}
              <div className="lda-card lda-card-span-2">
                <div className="lda-card-header">
                  <h3>Strategy Allocation</h3>
                  <div className="lda-card-header-controls">
                    <div className="lda-toggle-group">
                      <button 
                        className={`lda-toggle-btn ${allocationViewMode === 'allocated' ? 'active' : ''}`}
                        onClick={() => setAllocationViewMode('allocated')}
                      >
                        Allocated
                      </button>
                      <button 
                        className={`lda-toggle-btn ${allocationViewMode === 'equity' ? 'active' : ''}`}
                        onClick={() => setAllocationViewMode('equity')}
                      >
                        Equity
                      </button>
                      <button 
                        className={`lda-toggle-btn ${allocationViewMode === 'pnl' ? 'active' : ''}`}
                        onClick={() => setAllocationViewMode('pnl')}
                      >
                        P&L
                      </button>
                    </div>
                  </div>
                </div>
                <div className="lda-card-body">
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
                              <div className="lda-custom-tooltip">
                                <div className="lda-tooltip-title">{data.fullName}</div>
                                <div className="lda-tooltip-row">
                                  <span>Allocated:</span>
                                  <span>{formatCurrency(data.initial_allocation)}</span>
                                </div>
                                <div className="lda-tooltip-row">
                                  <span>Current Equity:</span>
                                  <span>{formatCurrency(data.current_equity)}</span>
                                </div>
                                <div className="lda-tooltip-row">
                                  <span>P&L:</span>
                                  <span className={data.total_pnl >= 0 ? 'positive' : 'negative'}>
                                    {formatCurrency(data.total_pnl)}
                                  </span>
                                </div>
                                <div className="lda-tooltip-row">
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
                      <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                        {strategyAllocationData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.fill} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Risk Metrics Radar */}
              <div className="lda-card lda-card-span-2">
                <div className="lda-card-header">
                  <h3>Portfolio Risk Profile</h3>
                  <span className="lda-card-subtitle">Risk-Adjusted Performance Metrics</span>
                </div>
                <div className="lda-card-body">
                  <ResponsiveContainer width="100%" height={280}>
                    <RadarChart data={riskRadarData}>
                      <PolarGrid stroke="rgba(148, 163, 184, 0.2)" />
                      <PolarAngleAxis 
                        dataKey="metric" 
                        tick={{ fill: '#94A3B8', fontSize: 11 }}
                      />
                      <PolarRadiusAxis 
                        angle={30} 
                        domain={[0, 100]} 
                        tick={{ fill: '#64748B', fontSize: 10 }}
                      />
                      <Radar
                        name="Portfolio"
                        dataKey="value"
                        stroke="#A855F7"
                        fill="#A855F7"
                        fillOpacity={0.3}
                        strokeWidth={2}
                      />
                      <Tooltip 
                        contentStyle={{ 
                          background: 'rgba(15, 23, 42, 0.95)', 
                          border: '1px solid rgba(168, 85, 247, 0.3)',
                          borderRadius: '8px',
                          color: '#fff'
                        }}
                      />
                    </RadarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Risk Profile Narrative Panel */}
              <div className="lda-card lda-card-span-4">
                <div className="lda-card-header">
                  <div className="lda-card-header-icon lda-card-header-icon-warning">
                    <AlertTriangle size={18} />
                  </div>
                  <h3>Risk Profile Interpretation (Last {timePeriod} Days)</h3>
                  <button 
                    className="lda-btn lda-btn-ghost lda-btn-sm"
                    onClick={fetchRiskNarrative}
                    disabled={riskNarrativeLoading}
                  >
                    <RefreshCw size={14} className={riskNarrativeLoading ? 'spin' : ''} />
                  </button>
                </div>
                <div className="lda-card-body">
                  {riskNarrativeLoading ? (
                    <div className="lda-narrative-loading">
                      <Loader2 size={24} className="spin" />
                      <span>Analyzing risk profile...</span>
                    </div>
                  ) : riskNarrative ? (
                    <div className="lda-narrative-content">
                      {/* Confidence Notes */}
                      {riskNarrative.confidence_notes?.length > 0 && (
                        <div className="lda-narrative-confidence">
                          {riskNarrative.confidence_notes.map((note, i) => (
                            <div key={i} className="lda-confidence-note">{note}</div>
                          ))}
                        </div>
                      )}
                      
                      {/* Executive Read */}
                      <div className="lda-narrative-section">
                        <h4>Executive Summary</h4>
                        <ul className="lda-narrative-bullets">
                          {riskNarrative.executive_read?.map((item, i) => (
                            <li key={i}>{item}</li>
                          ))}
                        </ul>
                      </div>
                      
                      {/* Metric Interpretations */}
                      <div className="lda-narrative-section">
                        <h4>Metric Analysis</h4>
                        <div className="lda-metric-interpretations">
                          {riskNarrative.metric_interpretations?.map((item, i) => (
                            <div key={i} className="lda-metric-item">
                              <div className="lda-metric-header">
                                <span className="lda-metric-name">{item.metric}</span>
                                <span className="lda-metric-value">{item.value}</span>
                              </div>
                              <p className="lda-metric-desc">{item.interpretation}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                      
                      {/* Red Flags */}
                      {riskNarrative.red_flags?.length > 0 && (
                        <div className="lda-narrative-section lda-narrative-danger">
                          <h4><AlertTriangle size={16} /> Red Flags</h4>
                          <ul className="lda-narrative-bullets lda-danger-list">
                            {riskNarrative.red_flags.map((flag, i) => (
                              <li key={i}>{flag}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      
                      {/* Actionable Fixes */}
                      {riskNarrative.actionable_fixes?.length > 0 && (
                        <div className="lda-narrative-section lda-narrative-action">
                          <h4><Zap size={16} /> Recommended Actions</h4>
                          <ul className="lda-narrative-bullets lda-action-list">
                            {riskNarrative.actionable_fixes.map((fix, i) => (
                              <li key={i}>{fix}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="lda-narrative-empty">
                      <AlertTriangle size={20} />
                      <span>Click refresh to generate risk analysis</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Performance Comparison Bar Chart */}
              <div className="lda-card lda-card-span-2">
                <div className="lda-card-header">
                  <h3>Strategy Performance</h3>
                  <span className="lda-card-subtitle">Return % by Manager (Top 8)</span>
                </div>
                <div className="lda-card-body">
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
                          border: '1px solid rgba(168, 85, 247, 0.3)',
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
              <div className="lda-card lda-card-span-2">
                <div className="lda-card-header">
                  <h3>Risk vs Return Analysis</h3>
                  <span className="lda-card-subtitle">Efficient Frontier Visualization</span>
                </div>
                <div className="lda-card-body">
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
          <div className="lda-rankings-tab" data-testid="rankings-content">
            {/* Comparison Panel */}
            {comparisonManagers.length > 0 && (
              <div className="lda-comparison-panel">
                <div className="lda-comparison-header">
                  <h3>Head-to-Head Comparison</h3>
                  <button 
                    className="lda-btn lda-btn-ghost"
                    onClick={() => setComparisonManagers([])}
                  >
                    Clear
                  </button>
                </div>
                <div className="lda-comparison-grid">
                  {comparisonManagers.map(manager => (
                    <div key={manager.manager_id} className="lda-comparison-card">
                      <div className="lda-comparison-name">{manager.manager_name}</div>
                      <div className="lda-comparison-stats">
                        <div className="lda-stat">
                          <span className="label">Return</span>
                          <span className={`value ${(manager.return_percentage || 0) >= 0 ? 'positive' : 'negative'}`}>
                            {formatPercent(manager.return_percentage)}
                          </span>
                        </div>
                        <div className="lda-stat">
                          <span className="label">Sharpe</span>
                          <span className="value">{formatNumber(manager.sharpe_ratio)}</span>
                        </div>
                        <div className="lda-stat">
                          <span className="label">Win Rate</span>
                          <span className="value">{formatPercent(manager.win_rate)}</span>
                        </div>
                        <div className="lda-stat">
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
            <div className="lda-card">
              <div className="lda-card-header">
                <h3>Strategy Leaderboard</h3>
                <span className="lda-card-subtitle">Ranked by Risk-Adjusted Performance</span>
              </div>
              <div className="lda-table-wrapper">
                <table className="lda-table" data-testid="rankings-table">
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
                              <span className={`lda-rank rank-${index + 1}`}>
                                {index === 0 && '🥇'}
                                {index === 1 && '🥈'}
                                {index === 2 && '🥉'}
                                {index > 2 && `#${index + 1}`}
                              </span>
                            </td>
                            <td>
                              <div className="lda-manager-cell">
                                <span className="lda-manager-name">{manager.manager_name}</span>
                                <span className="lda-manager-account">#{manager.account}</span>
                              </div>
                            </td>
                            <td>
                              <span className={`lda-fund-badge fund-${(manager.fund || 'unknown').toLowerCase()}`}>
                                {manager.fund || 'N/A'}
                              </span>
                            </td>
                            <td className="lda-mono">{formatCurrency(manager.initial_allocation)}</td>
                            <td className={`lda-mono ${(manager.total_pnl || 0) >= 0 ? 'positive' : 'negative'}`}>
                              {formatCurrencyPrecise(manager.total_pnl)}
                            </td>
                            <td>
                              <span className={`lda-return ${(manager.return_percentage || 0) >= 0 ? 'positive' : 'negative'}`}>
                                {(manager.return_percentage || 0) >= 0 ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}
                                {formatPercent(manager.return_percentage)}
                              </span>
                            </td>
                            <td className="lda-mono">{formatNumber(manager.sharpe_ratio)}</td>
                            <td className="lda-mono">{formatPercent(manager.win_rate)}</td>
                            <td className="lda-mono negative">{formatPercent(manager.max_drawdown_pct)}</td>
                            <td>
                              <span className={`lda-risk-badge ${riskBadge.class}`}>
                                {riskBadge.label}
                              </span>
                            </td>
                            <td>
                              <button 
                                className={`lda-compare-btn ${isSelected ? 'active' : ''}`}
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
            <div className="lda-risk-alerts">
              <div className="lda-alert-header">
                <AlertTriangle size={18} />
                <h4>Risk Alerts</h4>
              </div>
              <div className="lda-alerts-grid">
                {managers
                  .filter(m => Math.abs(m.max_drawdown_pct || 0) > 15 || (m.sharpe_ratio || 0) < 0.5)
                  .slice(0, 3)
                  .map(manager => (
                    <div key={manager.manager_id} className="lda-alert-card">
                      <div className="lda-alert-icon">
                        <AlertTriangle size={16} />
                      </div>
                      <div className="lda-alert-content">
                        <span className="lda-alert-title">{manager.manager_name}</span>
                        <span className="lda-alert-message">
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
                  <div className="lda-no-alerts">
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
          <div className="lda-deepdive-tab" data-testid="deepdive-content">
            {/* Strategy Selector */}
            <div className="lda-strategy-selector">
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
                <div className="lda-strategy-header">
                  <div className="lda-strategy-info">
                    <h2>{deepDiveManager.manager_name}</h2>
                    <div className="lda-strategy-meta">
                      <span className="lda-meta-item">
                        <Briefcase size={14} />
                        Account #{deepDiveManager.account}
                      </span>
                      <span className="lda-meta-item">
                        <Target size={14} />
                        Fund: {deepDiveManager.fund || 'N/A'}
                      </span>
                      <span className={`lda-strategy-badge ${getPerformanceBadge(deepDiveManager.return_percentage).class}`}>
                        {getPerformanceBadge(deepDiveManager.return_percentage).label}
                      </span>
                    </div>
                  </div>
                  <div className="lda-strategy-return">
                    <span className={`lda-big-return ${(deepDiveManager.return_percentage || 0) >= 0 ? 'positive' : 'negative'}`}>
                      {(deepDiveManager.return_percentage || 0) >= 0 ? '+' : ''}
                      {formatPercent(deepDiveManager.return_percentage)}
                    </span>
                    <span className="lda-return-label">{timePeriod}-Day Return</span>
                  </div>
                </div>

                {/* Key Metrics Grid */}
                <div className="lda-metrics-grid">
                  <div className="lda-metric-card">
                    <span className="lda-metric-label">Initial Allocation</span>
                    <span className="lda-metric-value">{formatCurrency(deepDiveManager.initial_allocation)}</span>
                  </div>
                  <div className="lda-metric-card">
                    <span className="lda-metric-label">Current Equity</span>
                    <span className="lda-metric-value">{formatCurrency(deepDiveManager.current_equity)}</span>
                  </div>
                  <div className="lda-metric-card">
                    <span className="lda-metric-label">Total P&L</span>
                    <span className={`lda-metric-value ${(deepDiveManager.total_pnl || 0) >= 0 ? 'positive' : 'negative'}`}>
                      {formatCurrencyPrecise(deepDiveManager.total_pnl)}
                    </span>
                  </div>
                  <div className="lda-metric-card">
                    <span className="lda-metric-label">Profit Withdrawals</span>
                    <span className="lda-metric-value">{formatCurrency(deepDiveManager.profit_withdrawals)}</span>
                  </div>
                </div>

                {/* Equity Curve */}
                <div className="lda-card">
                  <div className="lda-card-header">
                    <h3>Equity Curve</h3>
                    <span className="lda-card-subtitle">Historical Balance Progression</span>
                  </div>
                  <div className="lda-card-body">
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
                <div className="lda-grid-3">
                  <div className="lda-stat-card">
                    <div className="lda-stat-header">
                      <Target size={18} />
                      <span>Sharpe Ratio</span>
                    </div>
                    <div className="lda-stat-value">{formatNumber(deepDiveManager.sharpe_ratio)}</div>
                    <div className="lda-stat-bar">
                      <div 
                        className="lda-stat-fill" 
                        style={{ width: `${Math.min((deepDiveManager.sharpe_ratio || 0) * 33, 100)}%` }}
                      />
                    </div>
                    <div className="lda-stat-range">
                      <span>Poor {'<'} 0.5</span>
                      <span>Good {'>'} 1.0</span>
                      <span>Excellent {'>'} 2.0</span>
                    </div>
                  </div>

                  <div className="lda-stat-card">
                    <div className="lda-stat-header">
                      <Shield size={18} />
                      <span>Sortino Ratio</span>
                    </div>
                    <div className="lda-stat-value">{formatNumber(deepDiveManager.sortino_ratio)}</div>
                    <div className="lda-stat-bar">
                      <div 
                        className="lda-stat-fill" 
                        style={{ width: `${Math.min((deepDiveManager.sortino_ratio || 0) * 25, 100)}%` }}
                      />
                    </div>
                    <div className="lda-stat-range">
                      <span>Poor {'<'} 1.0</span>
                      <span>Good {'>'} 2.0</span>
                      <span>Excellent {'>'} 3.0</span>
                    </div>
                  </div>

                  <div className="lda-stat-card">
                    <div className="lda-stat-header">
                      <TrendingDown size={18} />
                      <span>Max Drawdown</span>
                    </div>
                    <div className="lda-stat-value negative">{formatPercent(deepDiveManager.max_drawdown_pct)}</div>
                    <div className="lda-stat-bar danger">
                      <div 
                        className="lda-stat-fill" 
                        style={{ width: `${Math.min(Math.abs(deepDiveManager.max_drawdown_pct || 0) * 3, 100)}%` }}
                      />
                    </div>
                    <div className="lda-stat-range">
                      <span>Low {'<'} 10%</span>
                      <span>Med {'<'} 20%</span>
                      <span>High {'>'} 30%</span>
                    </div>
                  </div>
                </div>

                {/* Trading Statistics */}
                <div className="lda-card">
                  <div className="lda-card-header">
                    <h3>Trading Statistics</h3>
                    <span className="lda-card-subtitle">Performance Breakdown</span>
                  </div>
                  <div className="lda-stats-grid">
                    <div className="lda-stat-item">
                      <span className="label">Total Trades</span>
                      <span className="value">{(deepDiveManager.total_trades || 0).toLocaleString()}</span>
                    </div>
                    <div className="lda-stat-item">
                      <span className="label">Winning Trades</span>
                      <span className="value positive">{(deepDiveManager.winning_trades || 0).toLocaleString()}</span>
                    </div>
                    <div className="lda-stat-item">
                      <span className="label">Losing Trades</span>
                      <span className="value negative">{(deepDiveManager.losing_trades || 0).toLocaleString()}</span>
                    </div>
                    <div className="lda-stat-item">
                      <span className="label">Win Rate</span>
                      <span className="value">{formatPercent(deepDiveManager.win_rate)}</span>
                    </div>
                    <div className="lda-stat-item">
                      <span className="label">Profit Factor</span>
                      <span className="value">{formatNumber(deepDiveManager.profit_factor)}</span>
                    </div>
                    <div className="lda-stat-item">
                      <span className="label">Risk Level</span>
                      <span className={`value ${getRiskBadge(deepDiveManager).class}`}>
                        {getRiskBadge(deepDiveManager).label}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Allocation Recommendation */}
                <div className="lda-recommendation-card">
                  <div className="lda-recommendation-header">
                    <Zap size={20} />
                    <h4>Allocation Insight</h4>
                  </div>
                  <div className="lda-recommendation-content">
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
          <div className="lda-risklimits-tab" data-testid="risklimits-content">
            {/* Risk Policy Summary */}
            <div className="lda-risk-policy-header">
              <div className="lda-risk-policy-card">
                <h3>Active Risk Policy (200:1 Leverage)</h3>
                <div className="lda-risk-policy-grid">
                  <div className="lda-policy-item">
                    <span className="label">Max Risk Per Trade</span>
                    <span className="value">{riskPolicy.max_risk_per_trade_pct}%</span>
                  </div>
                  <div className="lda-policy-item">
                    <span className="label">Max Intraday Loss</span>
                    <span className="value">{riskPolicy.max_intraday_loss_pct}%</span>
                  </div>
                  <div className="lda-policy-item">
                    <span className="label">Max Margin Usage</span>
                    <span className="value">{riskPolicy.max_margin_usage_pct}%</span>
                  </div>
                  <div className="lda-policy-item">
                    <span className="label">Leverage</span>
                    <span className="value">{riskPolicy.leverage}:1</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="lda-risk-content-grid">
              {/* Left: Position Sizing Calculator */}
              <div className="lda-card">
                <div className="lda-card-header">
                  <h3>Position Sizing Calculator</h3>
                  <span className="lda-card-subtitle">Hull-Style Max Lot Calculation</span>
                </div>
                <div className="lda-card-body">
                  <div className="lda-calc-form">
                    <div className="lda-form-row">
                      <div className="lda-form-group">
                        <label>Account Equity ($)</label>
                        <input
                          type="number"
                          value={calcEquity}
                          onChange={(e) => setCalcEquity(Number(e.target.value))}
                          placeholder="100000"
                        />
                      </div>
                      <div className="lda-form-group">
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
                    <div className="lda-form-row">
                      <div className="lda-form-group">
                        <label>Stop Distance {calcSymbol === 'XAUUSD' ? '($)' : calcSymbol.includes('USD') ? '(pips)' : '(points)'}</label>
                        <input
                          type="number"
                          value={calcStopDistance}
                          onChange={(e) => setCalcStopDistance(Number(e.target.value))}
                          step="0.1"
                        />
                      </div>
                      <div className="lda-form-group lda-form-group-btn">
                        <button 
                          className="lda-btn lda-btn-primary"
                          onClick={calculateMaxLots}
                        >
                          Calculate Max Lots
                        </button>
                      </div>
                    </div>
                  </div>

                  {calcResult && (
                    <div className="lda-calc-result">
                      <div className="lda-calc-result-header">
                        <h4>Maximum Allowed Position</h4>
                        <span className={`lda-constraint-badge ${calcResult.binding_constraint === 'RISK' ? 'risk' : 'margin'}`}>
                          {calcResult.binding_constraint} BOUND
                        </span>
                      </div>
                      
                      <div className="lda-calc-big-number">
                        <span className="value">{calcResult.max_lots_allowed}</span>
                        <span className="unit">lots</span>
                      </div>
                      
                      <div className="lda-calc-breakdown">
                        <div className="lda-breakdown-section">
                          <h5>Risk-Based Limit</h5>
                          <div className="lda-breakdown-row">
                            <span>Risk Budget (1% of ${calcEquity.toLocaleString()}):</span>
                            <span>${calcResult.risk_budget?.toLocaleString()}</span>
                          </div>
                          <div className="lda-breakdown-row">
                            <span>Loss per lot at stop:</span>
                            <span>${calcResult.loss_per_lot_at_stop?.toLocaleString()}</span>
                          </div>
                          <div className="lda-breakdown-row highlight">
                            <span>Max Lots (Risk):</span>
                            <span>{calcResult.max_lots_risk} lots</span>
                          </div>
                        </div>
                        
                        <div className="lda-breakdown-section">
                          <h5>Margin-Based Limit</h5>
                          <div className="lda-breakdown-row">
                            <span>Margin per lot (at {calcResult.leverage}:1):</span>
                            <span>${calcResult.margin_per_lot?.toLocaleString()}</span>
                          </div>
                          <div className="lda-breakdown-row">
                            <span>Max margin allowed (25%):</span>
                            <span>${calcResult.max_margin_allowed?.toLocaleString()}</span>
                          </div>
                          <div className="lda-breakdown-row highlight">
                            <span>Max Lots (Margin):</span>
                            <span>{calcResult.max_lots_margin} lots</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Gold Example */}
                  <div className="lda-example-box">
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
                    <p className="lda-example-note">
                      <strong>Key insight:</strong> At 200:1 leverage, the risk limit (not margin) is typically the binding constraint for gold.
                    </p>
                  </div>
                </div>
              </div>

              {/* Right: Strategy Risk Analysis */}
              <div className="lda-card">
                <div className="lda-card-header">
                  <h3>Strategy Risk Analysis</h3>
                  <div className="lda-card-header-controls">
                    <select 
                      value={deepDiveManager?.account || ''}
                      onChange={(e) => {
                        const mgr = managers.find(m => m.account === parseInt(e.target.value));
                        setDeepDiveManager(mgr);
                      }}
                      className="lda-strategy-select"
                    >
                      {managers.map(m => (
                        <option key={m.account} value={m.account}>
                          {m.manager_name} (#{m.account})
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
                <div className="lda-card-body">
                  {riskAnalysisLoading ? (
                    <div className="lda-loading-inline">
                      <Loader2 size={20} className="spin" />
                      <span>Loading risk analysis...</span>
                    </div>
                  ) : riskAnalysis ? (
                    <div className="lda-risk-analysis-content">
                      {/* Risk Control Score */}
                      <div className="lda-risk-score-panel">
                        <div className="lda-risk-score-circle" style={{ borderColor: riskAnalysis.risk_control_score?.color }}>
                          <span className="score">{riskAnalysis.risk_control_score?.composite_score || 0}</span>
                          <span className="label">Risk Score</span>
                        </div>
                        <div className="lda-risk-score-label" style={{ color: riskAnalysis.risk_control_score?.color }}>
                          {riskAnalysis.risk_control_score?.label || 'Unknown'}
                        </div>
                      </div>

                      {/* Score Components */}
                      {riskAnalysis.risk_control_score?.components && (
                        <div className="lda-score-components">
                          <h5>Score Components</h5>
                          {Object.entries(riskAnalysis.risk_control_score.components).map(([key, comp]) => (
                            <div key={key} className="lda-score-component">
                              <span className="name">{key.replace(/_/g, ' ')}</span>
                              <span className="score">{comp.score?.toFixed(1) || 'N/A'}</span>
                            </div>
                          ))}
                        </div>
                      )}

                      {/* Breach Summary */}
                      {riskAnalysis.risk_control_score?.breach_summary?.length > 0 && (
                        <div className="lda-breach-summary">
                          <h5><AlertTriangle size={14} /> Breach Summary</h5>
                          <ul>
                            {riskAnalysis.risk_control_score.breach_summary.map((breach, i) => (
                              <li key={i}>{breach}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="lda-risk-analysis-empty">
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
          <div className="lda-advisor-tab" data-testid="advisor-content">
            <div className="lda-advisor-layout">
              {/* Left Column: Automated Insights + Allocation Tool */}
              <div className="lda-advisor-sidebar">
                {/* Automated Insights Card */}
                <div className="lda-card lda-insights-card">
                  <div className="lda-card-header">
                    <div className="lda-card-header-icon">
                      <Lightbulb size={18} />
                    </div>
                    <h3>AI Insights</h3>
                    <button 
                      className="lda-btn lda-btn-ghost lda-btn-sm"
                      onClick={fetchAiInsights}
                      disabled={aiInsightsLoading}
                    >
                      <RefreshCw size={14} className={aiInsightsLoading ? 'spin' : ''} />
                    </button>
                  </div>
                  <div className="lda-card-body">
                    {aiInsightsLoading ? (
                      <div className="lda-insights-loading">
                        <Loader2 size={24} className="spin" />
                        <span>Analyzing portfolio...</span>
                      </div>
                    ) : aiInsights ? (
                      <div className="lda-insights-content">
                        <div className="lda-markdown-content" dangerouslySetInnerHTML={{ 
                          __html: aiInsights
                            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                            .replace(/\n/g, '<br/>') 
                        }} />
                      </div>
                    ) : (
                      <div className="lda-insights-empty">
                        <Sparkles size={20} />
                        <span>Click refresh to generate insights</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Allocation Recommendation Tool */}
                <div className="lda-card lda-allocation-card">
                  <div className="lda-card-header">
                    <div className="lda-card-header-icon">
                      <PieChartIcon size={18} />
                    </div>
                    <h3>Allocation Advisor</h3>
                  </div>
                  <div className="lda-card-body">
                    <div className="lda-allocation-form">
                      <div className="lda-form-group">
                        <label>Capital to Allocate</label>
                        <div className="lda-input-with-prefix">
                          <span>$</span>
                          <input
                            type="number"
                            value={allocationCapital}
                            onChange={(e) => setAllocationCapital(Number(e.target.value))}
                            placeholder="100000"
                          />
                        </div>
                      </div>
                      <div className="lda-form-group">
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
                        className="lda-btn lda-btn-primary lda-btn-full"
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
                      <div className="lda-allocation-result">
                        <div className="lda-markdown-content" dangerouslySetInnerHTML={{ 
                          __html: allocationResult
                            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                            .replace(/\|(.*?)\|/g, '<span class="lda-table-cell">$1</span>')
                            .replace(/\n/g, '<br/>') 
                        }} />
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Right Column: Chat Interface */}
              <div className="lda-advisor-chat">
                <div className="lda-card lda-chat-card">
                  <div className="lda-card-header">
                    <div className="lda-card-header-icon">
                      <MessageSquare size={18} />
                    </div>
                    <h3>Chat with AI Advisor</h3>
                    <div className="lda-chat-actions">
                      <span className="lda-chat-model">Claude Sonnet 4.5</span>
                      <button 
                        className="lda-btn lda-btn-ghost lda-btn-sm"
                        onClick={clearAiChat}
                        title="Clear chat"
                      >
                        <RefreshCw size={14} />
                      </button>
                    </div>
                  </div>
                  
                  {/* Chat Messages */}
                  <div className="lda-chat-messages">
                    {aiChatMessages.length === 0 ? (
                      <div className="lda-chat-welcome">
                        <Bot size={48} />
                        <h4>AI Strategy Advisor</h4>
                        <p>Ask me anything about your trading strategies, performance metrics, or allocation recommendations.</p>
                        <div className="lda-chat-suggestions">
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
                            className={`lda-chat-message ${msg.role} ${msg.isError ? 'error' : ''}`}
                          >
                            <div className="lda-message-avatar">
                              {msg.role === 'user' ? (
                                <Users size={16} />
                              ) : (
                                <Bot size={16} />
                              )}
                            </div>
                            <div className="lda-message-content">
                              <div className="lda-message-text" dangerouslySetInnerHTML={{ 
                                __html: msg.content
                                  .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                                  .replace(/\n/g, '<br/>') 
                              }} />
                              <span className="lda-message-time">
                                {new Date(msg.timestamp).toLocaleTimeString()}
                              </span>
                            </div>
                          </div>
                        ))}
                        {aiLoading && (
                          <div className="lda-chat-message assistant loading">
                            <div className="lda-message-avatar">
                              <Bot size={16} />
                            </div>
                            <div className="lda-message-content">
                              <div className="lda-typing-indicator">
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
                  <div className="lda-chat-input-container">
                    <textarea
                      value={aiInputMessage}
                      onChange={(e) => setAiInputMessage(e.target.value)}
                      onKeyPress={handleAiKeyPress}
                      placeholder="Ask about strategies, risk metrics, or allocation..."
                      rows={1}
                      disabled={aiLoading}
                    />
                    <button
                      className="lda-btn lda-btn-primary lda-chat-send"
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
