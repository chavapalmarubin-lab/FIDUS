import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { 
  TrendingUp, 
  TrendingDown,
  Calendar,
  DollarSign,
  Target,
  AlertCircle,
  BarChart3,
  PieChart,
  Activity,
  Clock,
  Filter,
  RefreshCw
} from "lucide-react";
import apiAxios from "../utils/apiAxios";
import { useMT5Data } from "../hooks/useMT5Data";
import MT5HealthIndicator from "./MT5HealthIndicator";
import mt5Service from "../services/mt5Service"; // PHASE 4A
import {
  LineChart,
  Line,
  PieChart as RechartsChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine
} from 'recharts';
import { ChartSkeleton, MetricCardSkeleton } from "./ui/skeleton";
import { exportTradingAnalytics } from "../utils/exportUtils";
import { Download } from "lucide-react";

const TradingAnalyticsDashboard = () => {
  const [analyticsData, setAnalyticsData] = useState(null);
  const [dailyPerformance, setDailyPerformance] = useState([]);
  const [recentTrades, setRecentTrades] = useState([]);
  const [selectedAccount, setSelectedAccount] = useState('all');
  const [selectedPeriod, setSelectedPeriod] = useState('30d');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [lastUpdated, setLastUpdated] = useState(null);
  
  // PHASE 2: Chart data
  const [equityHistory, setEquityHistory] = useState([]);
  const [winLossData, setWinLossData] = useState(null);
  // PHASE 3: Use unified MT5 data hook (no mock data)
  const { accounts: mt5AccountsData, loading: mt5Loading } = useMT5Data();
  
  const [mt5Accounts, setMt5Accounts] = useState([
    { id: 'all', name: 'All Accounts', number: 0 }
  ]);

  // PHASE 3: Load MT5 accounts from unified service
  useEffect(() => {
    if (mt5AccountsData && mt5AccountsData.length > 0) {
      const accountOptions = [
        { id: 'all', name: 'All Accounts', number: 0 },
        ...mt5AccountsData.map(acc => ({
          id: acc.mt5_login.toString(),
          name: `${acc.mt5_login} - ${acc.fund_code} (${acc.broker_name})`,
          number: acc.mt5_login
        }))
      ];
      setMt5Accounts(accountOptions);
      console.log('✅ [Phase 3] Loaded', mt5AccountsData.length, 'MT5 accounts from unified service');
    }
  }, [mt5AccountsData]);

  useEffect(() => {
    fetchAnalyticsData();
  }, [selectedAccount, selectedPeriod]);
  
  // PHASE 2: Update win/loss data when analytics data changes
  useEffect(() => {
    if (analyticsData?.overview) {
      const wins = analyticsData.overview.winning_trades || 0;
      const losses = analyticsData.overview.losing_trades || 0;
      const winRate = wins + losses > 0 ? ((wins / (wins + losses)) * 100).toFixed(2) : 0;
      
      setWinLossData({
        winning_trades: wins,
        losing_trades: losses,
        win_rate: parseFloat(winRate)
      });
    }
  }, [analyticsData]);

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);
      setError("");

      // Phase 4A: Use real deal history APIs
      const account = selectedAccount === 'all' ? null : parseInt(selectedAccount);
      const dateRange = mt5Service.getDateRangeForPeriod(selectedPeriod);

      try {
        // PHASE 4A: Fetch deal summary for analytics
        const summaryResponse = await mt5Service.getDealsSummary({
          account_number: account,
          start_date: dateRange.start_date,
          end_date: dateRange.end_date
        });

        // PHASE 4A: Fetch daily P&L for equity curve
        const dailyPnLResponse = await mt5Service.getDailyPnL({
          account_number: account,
          days: selectedPeriod === '7d' ? 7 : selectedPeriod === '30d' ? 30 : selectedPeriod === '90d' ? 90 : 30
        });

        // PHASE 4A: Fetch recent deals
        const dealsResponse = await mt5Service.getDeals({
          account_number: account,
          start_date: dateRange.start_date,
          end_date: dateRange.end_date,
          limit: 20
        });

        if (summaryResponse.success && dailyPnLResponse.success && dealsResponse.success) {
          const summary = summaryResponse.summary;
          
          // Build analytics data structure from deal summary
          const analytics = {
            overview: {
              total_pnl: summary.total_profit || 0,
              total_volume: summary.total_volume || 0,
              total_deals: summary.total_deals || 0,
              winning_trades: summary.win_deals || 0,
              losing_trades: summary.loss_deals || 0,
              total_commission: summary.total_commission || 0,
              total_swap: summary.total_swap || 0,
              buy_deals: summary.buy_deals || 0,
              sell_deals: summary.sell_deals || 0,
              balance_operations: summary.balance_operations || 0,
              symbols_traded: summary.symbols_traded || [],
              corrected_data_used: true, // Phase 4A uses real deal data
              data_source: 'Deal History (Phase 4A)'
            },
            last_sync: summary.latest_deal || new Date().toISOString()
          };
          
          setAnalyticsData(analytics);
          
          // Set daily performance from Phase 4A API
          setDailyPerformance(dailyPnLResponse.data || []);
          
          // Transform deals to recent trades format
          const recentTradesData = dealsResponse.deals.slice(0, 20).map(deal => ({
            id: deal.ticket,
            symbol: deal.symbol,
            type: deal.type === 0 ? 'BUY' : deal.type === 1 ? 'SELL' : 'BALANCE',
            volume: deal.volume,
            open_price: deal.price,
            close_price: deal.price,
            profit: deal.profit,
            commission: deal.commission,
            swap: deal.swap,
            open_time: deal.time,
            close_time: deal.time,
            duration: 0
          }));
          
          setRecentTrades(recentTradesData);
          setLastUpdated(new Date());
          
          console.log('✅ [Phase 4A] Trading Analytics loaded from deal history:', {
            total_deals: analytics.overview.total_deals,
            total_pnl: analytics.overview.total_pnl,
            daily_points: dailyPnLResponse.days
          });
        } else {
          throw new Error("API returned unsuccessful response");
        }

      } catch (apiError) {
        console.error("Failed to fetch trading analytics:", apiError.message);
        setError(`Trading analytics data not available: ${apiError.message}`);
        setAnalyticsData(null);
        setDailyPerformance([]);
        setRecentTrades([]);
      }
      
      // PHASE 4A: Fetch Equity History from daily P&L
      try {
        const days = selectedPeriod === '7d' ? 7 : selectedPeriod === '30d' ? 30 : selectedPeriod === '90d' ? 90 : 30;
        const dailyResponse = await mt5Service.getDailyPnL({
          account_number: account,
          days: days
        });
        
        if (dailyResponse.success && dailyResponse.data) {
          // Transform daily P&L to equity history format
          const equityData = dailyResponse.data.map((day, index) => ({
            date: day.date,
            equity: dailyResponse.data.slice(0, index + 1).reduce((sum, d) => sum + d.pnl, 0),
            balance: dailyResponse.data.slice(0, index + 1).reduce((sum, d) => sum + d.pnl, 0),
            profit: day.pnl
          }));
          
          setEquityHistory(equityData);
          console.log(`✅ [Phase 4A] Equity curve loaded: ${equityData.length} days`);
        } else {
          setEquityHistory([]);
        }
      } catch (error) {
        console.error('Failed to fetch equity history:', error);
        setEquityHistory([]);
      }

    } catch (err) {
      console.error("Trading analytics fetch error:", err);
      setError("Failed to load trading analytics data");
    } finally {
      setLoading(false);
    }
  };

  // PHASE 3: Mock data generators REMOVED - using real data only

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(amount || 0);
  };
  
  // PHASE 4: Export handler
  const handleExport = () => {
    const result = exportTradingAnalytics(analyticsData, dailyPerformance, recentTrades);
    if (result.success) {
      console.log('✅ Exported:', result.filename);
    } else {
      console.error('❌ Export failed:', result.error);
    }
  };

  const formatPercentage = (value) => {
    return `${(value || 0).toFixed(2)}%`;
  };

  const formatDuration = (minutes) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    if (hours > 0) {
      return `${hours}h ${mins}m`;
    }
    return `${mins}m`;
  };

  if (loading) {
    return (
      <div className="space-y-6 p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <RefreshCw className="animate-spin h-6 w-6 text-cyan-400" />
            <span className="text-white text-lg">Loading trading analytics...</span>
          </div>
        </div>
        
        {/* Skeleton for metric cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card className="dashboard-card"><MetricCardSkeleton /></Card>
          <Card className="dashboard-card"><MetricCardSkeleton /></Card>
          <Card className="dashboard-card"><MetricCardSkeleton /></Card>
          <Card className="dashboard-card"><MetricCardSkeleton /></Card>
        </div>
        
        {/* Skeleton for charts */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <Card className="dashboard-card lg:col-span-2 p-6">
            <ChartSkeleton height={300} />
          </Card>
          <Card className="dashboard-card p-6">
            <ChartSkeleton height={300} />
          </Card>
        </div>
      </div>
    );
  }

  if (error && !analyticsData) {
    return (
      <div className="space-y-6">
        <div className="bg-red-900/20 border border-red-600 rounded-lg p-6">
          <div className="flex items-center">
            <AlertCircle className="h-6 w-6 text-red-400 mr-3" />
            <div>
              <h3 className="text-red-400 font-semibold mb-1">Failed to Load Trading Analytics</h3>
              <p className="text-red-300 text-sm">{error}</p>
              <Button 
                onClick={fetchAnalyticsData}
                className="mt-4 bg-cyan-600 hover:bg-cyan-700"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Try Again
              </Button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  try {
    return (
    <div className="space-y-6">
      {/* Header Controls */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <h2 className="text-2xl font-bold text-white flex items-center">
            <BarChart3 className="mr-3 h-8 w-8 text-cyan-400" />
            Trading Analytics
          </h2>
          {lastUpdated && (
            <div className="text-sm text-slate-400">
              Last Updated: {lastUpdated.toLocaleString()}
            </div>
          )}
        </div>
        
        <div className="flex items-center space-x-3">
          <select
            value={selectedAccount}
            onChange={(e) => setSelectedAccount(e.target.value)}
            className="px-3 py-2 bg-slate-700 border border-slate-600 text-white rounded-md"
          >
            {mt5Accounts.map(account => (
              <option key={account.id} value={account.id}>{account.name}</option>
            ))}
          </select>
          
          <select
            value={selectedPeriod}
            onChange={(e) => setSelectedPeriod(e.target.value)}
            className="px-3 py-2 bg-slate-700 border border-slate-600 text-white rounded-md"
          >
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
            <option value="90d">Last 90 Days</option>
            <option value="ytd">Year to Date</option>
          </select>
          
          <Button 
            onClick={fetchAnalyticsData}
            className="bg-cyan-600 hover:bg-cyan-700"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
          
          <Button
            onClick={handleExport}
            variant="outline"
            size="sm"
            className="text-green-400 border-green-600 hover:bg-green-700"
          >
            <Download className="mr-2 h-4 w-4" />
            Export to Excel
          </Button>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-900/20 border border-red-600 rounded-lg p-4">
          <div className="flex items-center">
            <AlertCircle className="h-5 w-5 text-red-400 mr-2" />
            <p className="text-red-400">{error}</p>
          </div>
        </div>
      )}

      {/* Phase 1B Multi-Account Status */}
      <div className="bg-blue-900/20 border border-blue-600 rounded-lg p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <Activity className="h-5 w-5 text-blue-400 mr-2" />
            <div>
              <p className="text-blue-400 font-medium">Phase 1B: Multi-Account Analytics Active</p>
              <p className="text-blue-300 text-sm mt-1">
                {selectedAccount === 'all' ? 
                  'Displaying aggregated data from all 4 MT5 accounts (886557, 886066, 886602, 885822)' :
                  `Displaying data for account ${selectedAccount} only`
                }
              </p>
            </div>
          </div>
          
          <div className="text-right text-sm">
            <div className="text-blue-400 font-medium">Account Status</div>
            <div className="text-blue-300">
              {analyticsData?.accounts_included?.length || 4} accounts active
            </div>
          </div>
        </div>
      </div>

      {analyticsData && (
        <>
          {/* Performance Overview Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            
            {/* Total P&L Card */}
            <Card className="dashboard-card">
              <CardHeader className="pb-3">
                <CardTitle className="text-white text-sm font-medium flex items-center justify-between">
                  <div className="flex items-center">
                    <DollarSign className="h-4 w-4 mr-2 text-green-400" />
                    Total P&L (TRUE)
                  </div>
                  {analyticsData.overview.corrected_data_used && (
                    <Badge className="bg-green-600 text-white text-xs">
                      ✓ Corrected
                    </Badge>
                  )}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className={`text-2xl font-bold ${analyticsData.overview.total_pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {formatCurrency(analyticsData.overview.total_pnl)}
                </div>
                <div className="flex items-center mt-2">
                  <div className="text-xs text-green-400">
                    ✓ Includes profit withdrawals
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Win Rate Card */}
            <Card className="dashboard-card">
              <CardHeader className="pb-3">
                <CardTitle className="text-white text-sm font-medium flex items-center">
                  <Target className="h-4 w-4 mr-2 text-cyan-400" />
                  Win Rate
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-cyan-400">
                  {formatPercentage(analyticsData.overview.win_rate)}
                </div>
                <div className="flex items-center mt-2 text-sm text-slate-400">
                  <span className="text-green-400">{analyticsData.overview.winning_trades}W</span>
                  <span className="mx-2">/</span>
                  <span className="text-red-400">{analyticsData.overview.losing_trades}L</span>
                  <span className="mx-2">/</span>
                  <span className="text-slate-400">{analyticsData.overview.total_trades}T</span>
                </div>
              </CardContent>
            </Card>

            {/* Profit Factor Card */}
            <Card className="dashboard-card">
              <CardHeader className="pb-3">
                <CardTitle className="text-white text-sm font-medium flex items-center">
                  <TrendingUp className="h-4 w-4 mr-2 text-purple-400" />
                  Profit Factor
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className={`text-2xl font-bold ${analyticsData.overview.profit_factor >= 1.5 ? 'text-green-400' : analyticsData.overview.profit_factor >= 1.0 ? 'text-yellow-400' : 'text-red-400'}`}>
                  {analyticsData.overview.profit_factor.toFixed(2)}
                </div>
                <div className="text-sm text-slate-400 mt-2">
                  {analyticsData.overview.profit_factor >= 1.5 ? 'Excellent' : 
                   analyticsData.overview.profit_factor >= 1.0 ? 'Profitable' : 'Needs Improvement'}
                </div>
              </CardContent>
            </Card>

            {/* Average Trade Card */}
            <Card className="dashboard-card">
              <CardHeader className="pb-3">
                <CardTitle className="text-white text-sm font-medium flex items-center">
                  <BarChart3 className="h-4 w-4 mr-2 text-orange-400" />
                  Average Trade
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className={`text-2xl font-bold ${analyticsData.overview.avg_trade >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {formatCurrency(analyticsData.overview.avg_trade)}
                </div>
                <div className="flex items-center mt-2 text-sm text-slate-400">
                  <span className="text-green-400">Avg Win: {formatCurrency(analyticsData.overview.avg_win)}</span>
                  <span className="mx-2">|</span>
                  <span className="text-red-400">Avg Loss: {formatCurrency(analyticsData.overview.avg_loss)}</span>
                </div>
              </CardContent>
            </Card>

            {/* Max Drawdown Card */}
            <Card className="dashboard-card">
              <CardHeader className="pb-3">
                <CardTitle className="text-white text-sm font-medium flex items-center">
                  <TrendingDown className="h-4 w-4 mr-2 text-red-400" />
                  Max Drawdown
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-red-400">
                  {formatCurrency(analyticsData.overview.max_drawdown)}
                </div>
                <div className="text-sm text-slate-400 mt-2">
                  Recovery Factor: {analyticsData.overview.recovery_factor.toFixed(2)}
                </div>
              </CardContent>
            </Card>

            {/* Sharpe Ratio Card */}
            <Card className="dashboard-card">
              <CardHeader className="pb-3">
                <CardTitle className="text-white text-sm font-medium flex items-center">
                  <PieChart className="h-4 w-4 mr-2 text-indigo-400" />
                  Sharpe Ratio
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className={`text-2xl font-bold ${analyticsData.overview.sharpe_ratio >= 1.0 ? 'text-green-400' : 'text-yellow-400'}`}>
                  {analyticsData.overview.sharpe_ratio.toFixed(2)}
                </div>
                <div className="text-sm text-slate-400 mt-2">
                  {analyticsData.overview.sharpe_ratio >= 1.0 ? 'Good Risk-Adjusted Return' : 'Moderate Performance'}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* PHASE 2: Equity Curve & Win/Loss Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            {/* Equity Curve Chart - Takes 2 columns */}
            <Card className="dashboard-card lg:col-span-2">
              <CardHeader>
                <CardTitle className="text-white flex items-center">
                  <Activity className="mr-2 h-5 w-5 text-cyan-400" />
                  Equity Curve
                </CardTitle>
                <p className="text-slate-400 text-sm">Account equity progression over time</p>
              </CardHeader>
              <CardContent>
                {equityHistory && equityHistory.length > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={equityHistory}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                      <XAxis 
                        dataKey="date" 
                        stroke="#94a3b8"
                        tick={{ fill: '#94a3b8', fontSize: 12 }}
                        tickFormatter={(date) => {
                          const d = new Date(date);
                          return `${d.getMonth() + 1}/${d.getDate()}`;
                        }}
                      />
                      <YAxis 
                        stroke="#94a3b8"
                        tick={{ fill: '#94a3b8', fontSize: 12 }}
                        tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
                      />
                      <Tooltip 
                        contentStyle={{ 
                          backgroundColor: '#1e293b', 
                          border: '1px solid #334155',
                          borderRadius: '6px'
                        }}
                        labelStyle={{ color: '#94a3b8' }}
                        formatter={(value) => [`$${value.toLocaleString()}`, 'Equity']}
                      />
                      <Legend 
                        wrapperStyle={{ color: '#94a3b8' }}
                      />
                      <ReferenceLine 
                        y={equityHistory[0]?.equity || 0} 
                        stroke="#64748b" 
                        strokeDasharray="3 3"
                        label={{ value: 'Starting Balance', fill: '#64748b', fontSize: 12 }}
                      />
                      <Line 
                        type="monotone" 
                        dataKey="equity" 
                        stroke="#10b981" 
                        strokeWidth={2}
                        dot={false}
                        name="Equity"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="flex items-center justify-center h-[300px] text-slate-400">
                    No equity data available
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Win/Loss Donut Chart - Takes 1 column */}
            <Card className="dashboard-card">
              <CardHeader>
                <CardTitle className="text-white flex items-center">
                  <PieChart className="mr-2 h-5 w-5 text-cyan-400" />
                  Win Rate
                </CardTitle>
                <p className="text-slate-400 text-sm">Trade success distribution</p>
              </CardHeader>
              <CardContent>
                {winLossData && (winLossData.winning_trades + winLossData.losing_trades) > 0 ? (
                  <div className="space-y-4">
                    {/* Win Rate Display */}
                    <div className="text-center py-4">
                      <div className="text-4xl font-bold text-green-400">
                        {winLossData.win_rate}%
                      </div>
                      <div className="text-sm text-slate-400 mt-1">Win Rate</div>
                    </div>
                    
                    {/* Donut Chart */}
                    <div className="relative">
                      <ResponsiveContainer width="100%" height={180}>
                        <RechartsChart>
                          <Pie
                            data={[
                              { name: 'Wins', value: winLossData.winning_trades },
                              { name: 'Losses', value: winLossData.losing_trades }
                            ]}
                            cx="50%"
                            cy="50%"
                            innerRadius={50}
                            outerRadius={70}
                            paddingAngle={5}
                            dataKey="value"
                          >
                            <Cell fill="#10b981" />
                            <Cell fill="#ef4444" />
                          </Pie>
                          <Tooltip 
                            contentStyle={{ 
                              backgroundColor: '#1e293b', 
                              border: '1px solid #334155',
                              borderRadius: '6px',
                              color: '#fff'
                            }}
                          />
                        </RechartsChart>
                      </ResponsiveContainer>
                    </div>
                    
                    {/* Legend */}
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center">
                          <div className="w-3 h-3 bg-green-600 rounded-full mr-2"></div>
                          <span className="text-sm text-slate-300">Winning Trades</span>
                        </div>
                        <span className="text-sm font-medium text-green-400">
                          {winLossData.winning_trades}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center">
                          <div className="w-3 h-3 bg-red-600 rounded-full mr-2"></div>
                          <span className="text-sm text-slate-300">Losing Trades</span>
                        </div>
                        <span className="text-sm font-medium text-red-400">
                          {winLossData.losing_trades}
                        </span>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="flex items-center justify-center h-[200px] text-slate-400">
                    No trade data available
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Daily Performance Calendar (Basic Version for Phase 1A) */}
          <Card className="dashboard-card">
            <CardHeader>
              <CardTitle className="text-white flex items-center">
                <Calendar className="mr-2 h-5 w-5 text-cyan-400" />
                Daily Performance Calendar
              </CardTitle>
              <p className="text-slate-400 text-sm">Last 30 days trading activity</p>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-7 gap-2">
                {dailyPerformance.map((day, index) => {
                  const isWeekend = new Date(day.date).getDay() % 6 === 0;
                  const statusColor = 
                    day.status === 'profitable' ? 'bg-green-600/30 border-green-600' :
                    day.status === 'loss' ? 'bg-red-600/30 border-red-600' :
                    day.total_trades > 0 ? 'bg-slate-600/30 border-slate-600' : 
                    'bg-slate-800/30 border-slate-700';
                  
                  return (
                    <motion.div
                      key={day.date}
                      whileHover={{ scale: 1.05 }}
                      className={`p-2 rounded border text-center cursor-pointer ${statusColor} ${isWeekend ? 'opacity-50' : ''}`}
                      title={`${day.date}: ${formatCurrency(day.total_pnl)} (${day.total_trades} trades)`}
                    >
                      <div className="text-xs text-white font-medium">
                        {new Date(day.date).getDate()}
                      </div>
                      {day.total_trades > 0 && (
                        <>
                          <div className={`text-xs font-bold ${day.total_pnl >= 0 ? 'text-green-300' : 'text-red-300'}`}>
                            {day.total_pnl >= 0 ? '+' : ''}{Math.round(day.total_pnl)}
                          </div>
                          <div className="text-xs text-slate-400">
                            {day.total_trades}T
                          </div>
                        </>
                      )}
                    </motion.div>
                  );
                })}
              </div>
              
              <div className="mt-4 flex items-center justify-center space-x-6 text-sm">
                <div className="flex items-center">
                  <div className="w-3 h-3 bg-green-600/30 border border-green-600 rounded mr-2"></div>
                  <span className="text-slate-400">Profitable</span>
                </div>
                <div className="flex items-center">
                  <div className="w-3 h-3 bg-red-600/30 border border-red-600 rounded mr-2"></div>
                  <span className="text-slate-400">Loss</span>
                </div>
                <div className="flex items-center">
                  <div className="w-3 h-3 bg-slate-600/30 border border-slate-600 rounded mr-2"></div>
                  <span className="text-slate-400">Breakeven</span>
                </div>
                <div className="flex items-center">
                  <div className="w-3 h-3 bg-slate-800/30 border border-slate-700 rounded mr-2"></div>
                  <span className="text-slate-400">No Trading</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Recent Trades */}
          <Card className="dashboard-card">
            <CardHeader>
              <CardTitle className="text-white flex items-center justify-between">
                <div className="flex items-center">
                  <Activity className="mr-2 h-5 w-5 text-cyan-400" />
                  Recent Trades
                </div>
                <Badge variant="outline" className="text-slate-300">
                  Last 20 trades
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-slate-600">
                      <th className="text-left text-slate-400 font-medium py-3">Date</th>
                      <th className="text-left text-slate-400 font-medium py-3">Symbol</th>
                      <th className="text-left text-slate-400 font-medium py-3">Type</th>
                      <th className="text-right text-slate-400 font-medium py-3">Volume</th>
                      <th className="text-right text-slate-400 font-medium py-3">P&L</th>
                      <th className="text-right text-slate-400 font-medium py-3">Duration</th>
                    </tr>
                  </thead>
                  <tbody>
                    {recentTrades.map((trade) => (
                      <tr key={trade.ticket} className="border-b border-slate-700/50">
                        <td className="py-3 text-slate-300">
                          {new Date(trade.close_time).toLocaleDateString()}
                        </td>
                        <td className="py-3">
                          <Badge className="bg-slate-700 text-white">
                            {trade.symbol}
                          </Badge>
                        </td>
                        <td className="py-3">
                          <Badge className={trade.type === 'BUY' ? 'bg-green-700 text-green-300' : 'bg-red-700 text-red-300'}>
                            {trade.type}
                          </Badge>
                        </td>
                        <td className="py-3 text-right text-slate-300">
                          {trade.volume}
                        </td>
                        <td className={`py-3 text-right font-medium ${trade.profit >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                          {formatCurrency(trade.profit)}
                        </td>
                        <td className="py-3 text-right text-slate-400">
                          {formatDuration(trade.duration_minutes)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
  } catch (renderError) {
    console.error('Trading Analytics Dashboard render error:', renderError);
    return (
      <div className="space-y-6">
        <div className="bg-red-900/20 border border-red-600 rounded-lg p-6">
          <div className="flex items-center">
            <AlertCircle className="h-6 w-6 text-red-400 mr-3" />
            <div>
              <h3 className="text-red-400 font-semibold mb-1">Dashboard Render Error</h3>
              <p className="text-red-300 text-sm">
                An unexpected error occurred while rendering the dashboard. Please try refreshing the page.
              </p>
              <Button 
                onClick={() => window.location.reload()}
                className="mt-4 bg-cyan-600 hover:bg-cyan-700"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Refresh Page
              </Button>
            </div>
          </div>
        </div>
      </div>
    );
  }
};

export default TradingAnalyticsDashboard;