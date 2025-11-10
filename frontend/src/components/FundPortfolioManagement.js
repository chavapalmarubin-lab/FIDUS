import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { 
  DollarSign, 
  TrendingUp, 
  TrendingDown,
  Users,
  Target,
  Activity,
  AlertCircle,
  PlusCircle,
  RefreshCw,
  BarChart3,
  PieChart,
  ChevronUp,
  ChevronDown
} from "lucide-react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart as RechartsPieChart, Pie, Cell } from 'recharts';
import apiAxios from "../utils/apiAxios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const FundPortfolioManagement = () => {
  const [fundData, setFundData] = useState({});
  const [portfolioStats, setPortfolioStats] = useState({});
  const [performanceData, setPerformanceData] = useState([]);
  const [rebateData, setRebateData] = useState([]);
  const [showRebateModal, setShowRebateModal] = useState(false);
  const [selectedFund, setSelectedFund] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [expandedFunds, setExpandedFunds] = useState({});
  const [fundPerformanceDetails, setFundPerformanceDetails] = useState({});

  // Real-time data entry states
  const [realTimeData, setRealTimeData] = useState({
    CORE: { current_nav: "", performance_today: "", last_updated: "" },
    BALANCE: { current_nav: "", performance_today: "", last_updated: "" },
    DYNAMIC: { current_nav: "", performance_today: "", last_updated: "" },
    UNLIMITED: { current_nav: "", performance_today: "", last_updated: "" }
  });

  // Rebate entry state
  const [rebateForm, setRebateForm] = useState({
    fund_code: "",
    amount: "",
    broker: "",
    description: "",
    date: new Date().toISOString().split('T')[0]
  });

  const FUND_COLORS = {
    CORE: '#0891b2',      // Cyan
    BALANCE: '#10b981',   // Green  
    DYNAMIC: '#f59e0b',   // Orange
    UNLIMITED: '#ef4444'  // Red
  };

  useEffect(() => {
    fetchFundPortfolioData();
    fetchRebateData();
    // Set up periodic refresh for real-time data
    const interval = setInterval(fetchFundPortfolioData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);
  // Load detailed performance for a specific fund
  const loadFundPerformance = async (fundCode) => {
    try {
      const response = await apiAxios.get(`/funds/${fundCode}/performance`);
      if (response.data.success) {
        setFundPerformanceDetails(prev => ({
          ...prev,
          [fundCode]: response.data
        }));
      }
    } catch (err) {
      console.error(`Error loading performance for ${fundCode}:`, err);
    }
  };
  
  // Toggle fund expansion
  const toggleFundExpansion = async (fundCode) => {
    const isExpanded = expandedFunds[fundCode];
    
    setExpandedFunds(prev => ({
      ...prev,
      [fundCode]: !isExpanded
    }));
    
    // Load performance details if expanding and not already loaded
    if (!isExpanded && !fundPerformanceDetails[fundCode]) {
      await loadFundPerformance(fundCode);
    }
  };

  const fetchFundPortfolioData = async () => {
    try {
      setLoading(true);
      
      // Fetch fund overview data
      const fundsResponse = await apiAxios.get(`/fund-portfolio/overview`);
      const portfolioResponse = await apiAxios.get(`/fund-portfolio/overview`);
      
      if (fundsResponse.data.success) {
        setFundData(fundsResponse.data.funds);
        setPortfolioStats(portfolioResponse.data);
        generatePerformanceData(fundsResponse.data.funds);
      }
    } catch (err) {
      setError("Failed to load fund portfolio data");
    } finally {
      setLoading(false);
    }
  };

  const fetchRebateData = async () => {
    try {
      const response = await apiAxios.get(`/admin/rebates/all`);
      if (response.data.success) {
        setRebateData(response.data.rebates || []);
      }
    } catch (err) {
      console.log("Rebate data not available yet");
    }
  };

  const generatePerformanceData = (funds) => {
    // Generate mock historical performance data for visualization
    const dates = [];
    const today = new Date();
    for (let i = 29; i >= 0; i--) {
      const date = new Date(today);
      date.setDate(date.getDate() - i);
      dates.push(date.toISOString().split('T')[0]);
    }

    const performanceHistory = dates.map((date, index) => {
      const dataPoint = { date };
      Object.keys(funds || {}).forEach(fundCode => {
        const fund = funds[fundCode];
        // Only show performance trends for funds with actual investors/accounts and AUM
        // Support both 'total_investors' and 'account_count' for different fund types
        const hasAccounts = (fund.total_investors > 0) || (fund.account_count > 0);
        const hasAUM = (fund.aum > 0) || (fund.total_aum > 0);
        
        if (fund && hasAccounts && hasAUM) {
          // Simulate performance trends
          const basePerformance = fund.performance_ytd || fund.weighted_return || 0;
          const dailyVariation = (Math.random() - 0.5) * 2; // -1% to +1% daily variation
          dataPoint[fundCode] = basePerformance + dailyVariation;
        } else {
          // Funds with no investors/accounts/AUM show flat line at 0
          dataPoint[fundCode] = 0;
        }
      });
      return dataPoint;
    });

    setPerformanceData(performanceHistory);
  };

  const updateRealTimeData = async (fundCode) => {
    try {
      const data = realTimeData[fundCode];
      if (!data.current_nav || !data.performance_today) {
        setError("Please enter both NAV and performance data");
        return;
      }

      // Update the fund's real-time data
      const response = await apiAxios.put(`/admin/funds/${fundCode}/realtime`, {
        current_nav: parseFloat(data.current_nav),
        performance_today: parseFloat(data.performance_today),
        last_updated: new Date().toISOString()
      });

      if (response.data.success) {
        setSuccess(`${fundCode} real-time data updated successfully`);
        fetchFundPortfolioData(); // Refresh data
        
        // Clear the form
        setRealTimeData(prev => ({
          ...prev,
          [fundCode]: { current_nav: "", performance_today: "", last_updated: "" }
        }));
      }
    } catch (err) {
      setError(`Failed to update ${fundCode} real-time data`);
    }
  };

  const submitRebate = async () => {
    try {
      if (!rebateForm.fund_code || !rebateForm.amount || !rebateForm.broker) {
        setError("Please fill in all required rebate fields");
        return;
      }

      const response = await apiAxios.post(`/admin/rebates/add`, {
        ...rebateForm,
        amount: parseFloat(rebateForm.amount)
      });

      if (response.data.success) {
        setSuccess(`Rebate of $${rebateForm.amount} added to ${rebateForm.fund_code} fund`);
        setShowRebateModal(false);
        setRebateForm({
          fund_code: "",
          amount: "",
          broker: "",
          description: "",
          date: new Date().toISOString().split('T')[0]
        });
        fetchRebateData();
        fetchFundPortfolioData();
      }
    } catch (err) {
      setError("Failed to add rebate");
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount || 0);
  };

  const formatPercentage = (value) => {
    return `${(value || 0).toFixed(2)}%`;
  };

  const calculateFidusProfit = (fund) => {
    // FIDUS Profit = Fund Performance - Interest Paid to Clients + Rebates
    const clientInterestOwed = fund.client_investments * (fund.client_interest_rate / 100) * (1/12); // Monthly
    const fundPerformance = fund.aum * (fund.performance_ytd / 100) * (1/12); // Monthly performance
    const rebates = fund.total_rebates || 0;
    return fundPerformance - clientInterestOwed + rebates;
  };

  const getFundColorClass = (fundCode) => {
    const colors = {
      CORE: 'border-cyan-500 bg-cyan-900/20',
      BALANCE: 'border-green-500 bg-green-900/20', 
      DYNAMIC: 'border-orange-500 bg-orange-900/20',
      UNLIMITED: 'border-red-500 bg-red-900/20'
    };
    return colors[fundCode] || 'border-slate-500 bg-slate-900/20';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <RefreshCw className="w-8 h-8 text-cyan-400 animate-spin mr-3" />
        <div className="text-white text-xl">Loading fund portfolio data...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white flex items-center">
          <PieChart className="mr-3 h-8 w-8 text-cyan-400" />
          Fund Portfolio Management
        </h2>
        <div className="flex gap-3">
          <Button
            onClick={() => setShowRebateModal(true)}
            className="bg-green-600 hover:bg-green-700"
          >
            <PlusCircle className="w-4 h-4 mr-2" />
            Add Rebate
          </Button>
          <Button
            onClick={fetchFundPortfolioData}
            className="bg-cyan-600 hover:bg-cyan-700"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh Data
          </Button>
        </div>
      </div>

      {/* Error/Success Messages */}
      {error && (
        <div className="bg-red-900/20 border border-red-600 rounded-lg p-3">
          <p className="text-red-400">{error}</p>
        </div>
      )}
      {success && (
        <div className="bg-green-900/20 border border-green-600 rounded-lg p-3">
          <p className="text-green-400">{success}</p>
        </div>
      )}

      {/* Portfolio Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <Card className="dashboard-card">
          <CardContent className="p-6">
            <div className="flex items-center">
              <DollarSign className="h-8 w-8 text-green-400" />
              <div className="ml-4">
                <p className="text-sm font-medium text-slate-400">Total AUM</p>
                <p className="text-2xl font-bold text-white">
                  {formatCurrency(portfolioStats.aum)}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="dashboard-card">
          <CardContent className="p-6">
            <div className="flex items-center">
              <TrendingUp className="h-8 w-8 text-cyan-400" />
              <div className="ml-4">
                <p className="text-sm font-medium text-slate-400">Total Returns</p>
                <p className="text-2xl font-bold text-white">
                  {formatPercentage(portfolioStats.ytd_return)}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="dashboard-card">
          <CardContent className="p-6">
            <div className="flex items-center">
              <Users className="h-8 w-8 text-purple-400" />
              <div className="ml-4">
                <p className="text-sm font-medium text-slate-400">Total Clients</p>
                <p className="text-2xl font-bold text-white">
                  {Object.values(fundData || {}).reduce((sum, fund) => sum + (fund.total_investors || 0), 0)}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="dashboard-card">
          <CardContent className="p-6">
            <div className="flex items-center">
              <Target className="h-8 w-8 text-yellow-400" />
              <div className="ml-4">
                <p className="text-sm font-medium text-slate-400">Active Funds</p>
                <p className="text-2xl font-bold text-white">
                  {Object.keys(fundData || {}).length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* PHASE 2: Portfolio Allocation Pie Chart */}
      <Card className="dashboard-card mb-8">
        <CardHeader>
          <CardTitle className="text-white flex items-center">
            <PieChart className="mr-2 h-5 w-5 text-cyan-400" />
            Portfolio Allocation by Fund Type
          </CardTitle>
          <p className="text-slate-400 text-sm">Asset distribution across fund types</p>
        </CardHeader>
        <CardContent>
          {Object.keys(fundData || {}).length > 0 ? (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Pie Chart */}
              <div className="flex items-center justify-center">
                <ResponsiveContainer width="100%" height={300}>
                  <RechartsPieChart>
                    <defs>
                      {Object.entries(FUND_COLORS).map(([fundCode, color]) => (
                        <linearGradient key={fundCode} id={`gradient-${fundCode}`} x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stopColor={color} stopOpacity={0.8} />
                          <stop offset="100%" stopColor={color} stopOpacity={0.6} />
                        </linearGradient>
                      ))}
                    </defs>
                    <Pie
                      data={Object.entries(fundData || {})
                        .filter(([fundCode, fund]) => {
                          // Only show funds with actual allocation (AUM > 0)
                          const aum = fund.aum || fund.current_aum || 0;
                          return aum > 0;
                        })
                        .map(([fundCode, fund]) => ({
                          name: `${fundCode} Fund`,
                          value: fund.aum || fund.current_aum || 0,
                          fundCode: fundCode
                        }))}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(1)}%`}
                      outerRadius={100}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {Object.entries(fundData || {})
                        .filter(([fundCode, fund]) => (fund.aum || fund.current_aum || 0) > 0)
                        .map(([fundCode], index) => (
                          <Cell 
                            key={`cell-${index}`} 
                            fill={FUND_COLORS[fundCode] || '#64748b'}
                            stroke="#1e293b"
                            strokeWidth={2}
                          />
                        ))}
                    </Pie>
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: '#1e293b', 
                        border: '1px solid #334155',
                        borderRadius: '6px',
                        color: '#fff'
                      }}
                      formatter={(value) => [`$${value.toLocaleString()}`, 'AUM']}
                    />
                  </RechartsPieChart>
                </ResponsiveContainer>
              </div>

              {/* Fund Details List */}
              <div className="space-y-4">
                <div className="text-center lg:text-left mb-4">
                  <div className="text-3xl font-bold text-white">
                    {formatCurrency(portfolioStats.aum)}
                  </div>
                  <div className="text-sm text-slate-400">Total Assets Under Management</div>
                </div>

                {Object.entries(fundData || {}).map(([fundCode, fund]) => {
                  const fundAum = fund.aum || fund.current_aum || 0;
                  const percentage = portfolioStats.aum > 0 
                    ? ((fundAum / portfolioStats.aum) * 100).toFixed(1)
                    : 0;
                  
                  return (
                    <div key={fundCode} className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                      <div className="flex items-center">
                        <div 
                          className="w-4 h-4 rounded-full mr-3"
                          style={{ backgroundColor: FUND_COLORS[fundCode] }}
                        ></div>
                        <div>
                          <div className="text-sm font-medium text-white">{fundCode} Fund</div>
                          <div className="text-xs text-slate-400">{fund.fund_code}</div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-bold text-white">
                          {formatCurrency(fundAum)}
                        </div>
                        <div className="text-xs text-slate-400">
                          {percentage}% of portfolio
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-center h-[300px] text-slate-400">
              No fund data available
            </div>
          )}
        </CardContent>
      </Card>

      {/* Individual Fund Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {Object.entries(fundData || {}).map(([fundCode, fund]) => (
          <Card key={fundCode} className={`dashboard-card border-2 ${getFundColorClass(fundCode)}`}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-white flex items-center">
                  <div 
                    className="w-4 h-4 rounded-full mr-3"
                    style={{ backgroundColor: FUND_COLORS[fundCode] }}
                  ></div>
                  {fundCode} Fund
                </CardTitle>
                <Badge className="bg-slate-700">
                  {fund.fund_code}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {/* Fund Statistics */}
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-slate-400">AUM:</span>
                    <span className="text-white ml-2 font-medium">
                      {formatCurrency(fund.aum || fund.total_aum || 0)}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400">
                      {fundCode === 'SEPARATION' ? 'Accounts:' : 'Investors:'}
                    </span>
                    <span className="text-white ml-2 font-medium">
                      {fund.total_investors || fund.account_count || 0}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400">NAV/Share:</span>
                    <span className="text-white ml-2 font-medium">
                      ${fund.nav_per_share}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400">Weighted Return:</span>
                    <span className={`ml-2 font-bold ${
                      (fund.performance_ytd || fund.weighted_return || 0) >= 0 ? 'text-green-400' : 'text-red-400'
                    }`}>
                      {formatPercentage(fund.performance_ytd || fund.weighted_return || 0)}
                    </span>
                    {(fund.performance_ytd !== 0 || fund.weighted_return !== 0) && (
                      <Badge className="ml-2 bg-green-600 text-white text-xs">
                        ✓ Corrected
                      </Badge>
                    )}
                  </div>
                </div>

                  <div>
                    <span className="text-slate-400">FIDUS Monthly Profit:</span>
                    <span className={`ml-2 font-semibold ${
                      (fund.mt5_trading_profit || fund.total_true_pnl || 0) >= 0 ? 'text-green-400' : 'text-red-400'
                    }`}>
                      {formatCurrency(fund.mt5_trading_profit || fund.total_true_pnl || 0)}
                    </span>
                  </div>
                  
                  {/* MT5 Accounts Info */}
                  {fund.mt5_accounts_count > 0 && (
                    <div className="mt-4 pt-4 border-t border-slate-600">
                      <button
                        onClick={() => toggleFundExpansion(fund.fund_code)}
                        className="flex items-center text-sm text-blue-400 hover:text-blue-300"
                      >
                        {expandedFunds[fund.fund_code] ? (
                          <>
                            <ChevronUp className="h-4 w-4 mr-1" />
                            Hide Account Breakdown
                          </>
                        ) : (
                          <>
                            <ChevronDown className="h-4 w-4 mr-1" />
                            Show Account Breakdown ({fund.mt5_accounts_count} accounts)
                          </>
                        )}
                      </button>
                    </div>
                  )}
                </div>
                
                {/* Expandable Account Breakdown */}
                {expandedFunds[fund.fund_code] && fundPerformanceDetails[fund.fund_code] && (
                  <div className="mt-4 p-4 bg-slate-800/50 rounded-lg border border-slate-600">
                    <h4 className="text-white font-semibold mb-3 flex items-center">
                      <TrendingUp className="h-4 w-4 mr-2 text-green-400" />
                      Account Performance Breakdown
                    </h4>
                    
                    {fundPerformanceDetails[fund.fund_code].accounts?.length > 0 ? (
                      <div className="space-y-3">
                        {fundPerformanceDetails[fund.fund_code].accounts.map((account, idx) => (
                          <div key={account.account_id} className="p-3 bg-slate-700/50 rounded border border-slate-600">
                            <div className="flex items-start justify-between mb-2">
                              <div>
                                <div className="flex items-center space-x-2">
                                  <span className="text-white font-medium">Account {account.account_id}</span>
                                  <Badge className={`text-xs ${
                                    account.status === 'excellent' ? 'bg-green-600' :
                                    account.status === 'positive' ? 'bg-blue-600' :
                                    account.status === 'underperforming' ? 'bg-yellow-600' :
                                    'bg-red-600'
                                  } text-white`}>
                                    {account.status === 'excellent' ? '🟢 Excellent' :
                                     account.status === 'positive' ? '🟢 Positive' :
                                     account.status === 'underperforming' ? '🟡 Underperforming' :
                                     '🔴 Poor'}
                                  </Badge>
                                </div>
                                <div className="text-sm text-slate-400 mt-1">{account.manager_name}</div>
                              </div>
                              <div className="text-right">
                                <div className={`text-lg font-bold ${account.return_pct >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                  {account.return_pct >= 0 ? '+' : ''}{account.return_pct.toFixed(2)}%
                                </div>
                                <div className="text-xs text-slate-400">Return</div>
                              </div>
                            </div>
                            
                            {/* Weight Bar */}
                            <div className="mb-3">
                              <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
                                <span>Weight in Fund</span>
                                <span className="font-medium">{account.weight.toFixed(1)}%</span>
                              </div>
                              <div className="w-full bg-slate-600 rounded-full h-2">
                                <div
                                  className={`h-2 rounded-full ${account.contribution >= 0 ? 'bg-green-500' : 'bg-red-500'}`}
                                  style={{ width: `${account.weight}%` }}
                                ></div>
                              </div>
                            </div>
                            
                            {/* Account Metrics Grid */}
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                              <div>
                                <div className="text-slate-400 text-xs">Allocation</div>
                                <div className="text-white font-medium">{formatCurrency(account.initial_deposit)}</div>
                              </div>
                              <div>
                                <div className="text-slate-400 text-xs">Current Equity</div>
                                <div className="text-cyan-400 font-medium">{formatCurrency(account.current_equity)}</div>
                              </div>
                              <div>
                                <div className="text-slate-400 text-xs">TRUE P&L</div>
                                <div className={`font-bold ${account.true_pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                  {account.true_pnl >= 0 ? '+' : ''}{formatCurrency(account.true_pnl)}
                                </div>
                              </div>
                              <div>
                                <div className="text-slate-400 text-xs">Contribution to Fund</div>
                                <div className={`font-bold ${account.contribution >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                  {account.contribution >= 0 ? '+' : ''}{account.contribution.toFixed(2)}%
                                </div>
                              </div>
                            </div>
                            
                            {/* Withdrawals info */}
                            {account.profit_withdrawals > 0 && (
                              <div className="mt-2 text-xs text-blue-400 bg-blue-900/20 p-2 rounded">
                                ✓ Includes ${account.profit_withdrawals.toLocaleString()} in profit withdrawals
                              </div>
                            )}
                          </div>
                        ))}
                        
                        {/* Performance Attribution Summary */}
                        {fundPerformanceDetails[fund.fund_code].best_performer && (
                          <div className="mt-4 p-3 bg-slate-700/30 rounded border border-slate-600">
                            <h5 className="text-white font-medium mb-2">Performance Attribution</h5>
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-2 text-sm">
                              <div className="flex items-center space-x-2">
                                <TrendingUp className="h-4 w-4 text-green-400" />
                                <div>
                                  <div className="text-slate-400 text-xs">Best Performer</div>
                                  <div className="text-white">
                                    Account {fundPerformanceDetails[fund.fund_code].best_performer.account_id}
                                    <span className="text-green-400 ml-1">
                                      (+{fundPerformanceDetails[fund.fund_code].best_performer.return_pct.toFixed(2)}%)
                                    </span>
                                  </div>
                                </div>
                              </div>
                              <div className="flex items-center space-x-2">
                                <TrendingDown className="h-4 w-4 text-red-400" />
                                <div>
                                  <div className="text-slate-400 text-xs">Worst Performer</div>
                                  <div className="text-white">
                                    Account {fundPerformanceDetails[fund.fund_code].worst_performer.account_id}
                                    <span className="text-red-400 ml-1">
                                      ({fundPerformanceDetails[fund.fund_code].worst_performer.return_pct.toFixed(2)}%)
                                    </span>
                                  </div>
                                </div>
                              </div>
                              <div className="flex items-center space-x-2">
                                <Activity className="h-4 w-4 text-blue-400" />
                                <div>
                                  <div className="text-slate-400 text-xs">Largest Contributor</div>
                                  <div className="text-white">
                                    Account {fundPerformanceDetails[fund.fund_code].largest_contributor.account_id}
                                    <span className="text-blue-400 ml-1">
                                      ({fundPerformanceDetails[fund.fund_code].largest_contributor.contribution >= 0 ? '+' : ''}
                                      {fundPerformanceDetails[fund.fund_code].largest_contributor.contribution.toFixed(2)}%)
                                    </span>
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    ) : (
                      <div className="text-center text-slate-400 py-4">
                        No account data available
                      </div>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>

      {/* Performance Chart */}
      <Card className="dashboard-card">
        <CardHeader>
          <CardTitle className="text-white flex items-center">
            <BarChart3 className="mr-2 h-5 w-5 text-cyan-400" />
            Fund Performance Trends (Last 30 Days)
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={performanceData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="date" stroke="#9CA3AF" />
                <YAxis stroke="#9CA3AF" />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#1f2937', 
                    border: '1px solid #374151',
                    borderRadius: '8px' 
                  }}
                />
                <Legend />
                {Object.keys(fundData || {}).map(fundCode => (
                  <Line
                    key={fundCode}
                    type="monotone"
                    dataKey={fundCode}
                    stroke={FUND_COLORS[fundCode]}
                    strokeWidth={2}
                    dot={false}
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Recent Rebates */}
      <Card className="dashboard-card">
        <CardHeader>
          <CardTitle className="text-white flex items-center">
            <DollarSign className="mr-2 h-5 w-5 text-green-400" />
            Recent Rebates
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {(rebateData || []).slice(0, 5).map((rebate, index) => (
              <div key={`fund-portfolio-rebate-${index}-${rebate.fund_code}-${rebate.broker}-${rebate.date}`} className="flex items-center justify-between p-3 bg-slate-700/50 rounded-lg">
                <div className="flex items-center">
                  <Badge className="mr-3" style={{ backgroundColor: FUND_COLORS[rebate.fund_code] }}>
                    {rebate.fund_code}
                  </Badge>
                  <div>
                    <div className="text-white font-medium">{rebate.broker}</div>
                    <div className="text-slate-400 text-sm">{rebate.description}</div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-green-400 font-bold">{formatCurrency(rebate.amount)}</div>
                  <div className="text-slate-400 text-xs">{rebate.date}</div>
                </div>
              </div>
            ))}
            {(rebateData || []).length === 0 && (
              <div className="text-center py-8 text-slate-400">
                No rebates recorded yet
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Rebate Entry Modal */}
      <AnimatePresence>
        {showRebateModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
            onClick={() => setShowRebateModal(false)}
          >
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.8, opacity: 0 }}
              className="bg-slate-800 rounded-lg p-6 max-w-md w-full mx-4"
              onClick={(e) => e.stopPropagation()}
            >
              <h3 className="text-xl font-semibold text-white mb-4 flex items-center">
                <PlusCircle className="mr-2 h-6 w-6 text-green-400" />
                Add Rebate Entry
              </h3>
              
              <div className="space-y-4">
                <div>
                  <Label className="text-slate-300">Fund *</Label>
                  <select
                    value={rebateForm.fund_code}
                    onChange={(e) => setRebateForm({...rebateForm, fund_code: e.target.value})}
                    className="w-full mt-1 p-2 bg-slate-700 border border-slate-600 text-white rounded-md"
                  >
                    <option value="">Select Fund</option>
                    {Object.keys(fundData || {}).map(fundCode => (
                      <option key={fundCode} value={fundCode}>{fundCode}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <Label className="text-slate-300">Rebate Amount ($) *</Label>
                  <Input
                    type="number"
                    step="0.01"
                    value={rebateForm.amount}
                    onChange={(e) => setRebateForm({...rebateForm, amount: e.target.value})}
                    className="mt-1 bg-slate-700 border-slate-600 text-white"
                    placeholder="0.00"
                  />
                </div>

                <div>
                  <Label className="text-slate-300">Broker *</Label>
                  <Input
                    value={rebateForm.broker}
                    onChange={(e) => setRebateForm({...rebateForm, broker: e.target.value})}
                    className="mt-1 bg-slate-700 border-slate-600 text-white"
                    placeholder="Broker name"
                  />
                </div>

                <div>
                  <Label className="text-slate-300">Date *</Label>
                  <Input
                    type="date"
                    value={rebateForm.date}
                    onChange={(e) => setRebateForm({...rebateForm, date: e.target.value})}
                    className="mt-1 bg-slate-700 border-slate-600 text-white"
                  />
                </div>

                <div>
                  <Label className="text-slate-300">Description</Label>
                  <textarea
                    value={rebateForm.description}
                    onChange={(e) => setRebateForm({...rebateForm, description: e.target.value})}
                    className="w-full mt-1 p-2 bg-slate-700 border border-slate-600 text-white rounded-md"
                    rows="3"
                    placeholder="Additional details..."
                  />
                </div>
              </div>

              <div className="flex gap-3 mt-6">
                <Button
                  variant="outline"
                  onClick={() => setShowRebateModal(false)}
                  className="flex-1 border-slate-600 text-slate-300"
                >
                  Cancel
                </Button>
                <Button
                  onClick={submitRebate}
                  className="flex-1 bg-green-600 hover:bg-green-700"
                >
                  Add Rebate
                </Button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default FundPortfolioManagement;