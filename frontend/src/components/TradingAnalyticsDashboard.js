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

const TradingAnalyticsDashboard = () => {
  const [analyticsData, setAnalyticsData] = useState(null);
  const [dailyPerformance, setDailyPerformance] = useState([]);
  const [recentTrades, setRecentTrades] = useState([]);
  const [selectedAccount, setSelectedAccount] = useState('all');
  const [selectedPeriod, setSelectedPeriod] = useState('30d');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [lastUpdated, setLastUpdated] = useState(null);

  // Account options for Phase 1A (start with 886557), Phase 1B (all accounts)
  const MT5_ACCOUNTS = [
    { id: 'all', name: 'All Accounts', number: null },
    { id: '886557', name: 'BALANCE Fund (886557)', number: 886557 },
    // Phase 1B: Add other accounts
    // { id: '886066', name: 'CORE Fund A (886066)', number: 886066 },
    // { id: '886602', name: 'CORE Fund B (886602)', number: 886602 },
    // { id: '885822', name: 'DYNAMIC Fund (885822)', number: 885822 }
  ];

  useEffect(() => {
    fetchAnalyticsData();
  }, [selectedAccount, selectedPeriod]);

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);
      setError("");

      // Phase 1A: Use real API endpoints with fallback to mock data
      const account = selectedAccount === 'all' ? null : parseInt(selectedAccount);
      const days = selectedPeriod === '7d' ? 7 : 
                   selectedPeriod === '30d' ? 30 : 
                   selectedPeriod === '90d' ? 90 : 
                   selectedPeriod === 'ytd' ? 365 : 30;

      try {
        // Fetch analytics overview
        const overviewResponse = await apiAxios.get('/admin/trading/analytics/overview');
        
        // Fetch daily performance
        const dailyResponse = await apiAxios.get('/admin/trading/analytics/daily', {
          params: { days, account }
        });
        
        // Fetch recent trades
        const tradesResponse = await apiAxios.get('/admin/trading/analytics/trades', {
          params: { limit: 20, account }
        });

        if (overviewResponse.data.success && dailyResponse.data.success && tradesResponse.data.success) {
          setAnalyticsData(overviewResponse.data.analytics);
          setDailyPerformance(dailyResponse.data.daily_performance || []);
          setRecentTrades(tradesResponse.data.trades || []);
          setLastUpdated(new Date(overviewResponse.data.analytics.last_sync));
        } else {
          throw new Error("API returned unsuccessful response");
        }

      } catch (apiError) {
        console.warn("API endpoints not available yet, using mock data:", apiError.message);
        
        // Fallback to mock data for Phase 1A development
        const mockAnalyticsData = {
          overview: {
            total_pnl: 2909.31,
            total_trades: 23,
            winning_trades: 12,
            losing_trades: 11,
            breakeven_trades: 0,
            win_rate: 52.17,
            profit_factor: 1.89,
            largest_win: 1234.56,
            largest_loss: -856.78,
            avg_win: 445.23,
            avg_loss: -298.45,
            gross_profit: 5342.76,
            gross_loss: -2433.45,
            avg_trade: 126.49,
            max_drawdown: -1456.78,
            recovery_factor: 2.0,
            sharpe_ratio: 1.45
          },
          period_start: '2025-09-09',
          period_end: '2025-10-09',
          last_sync: '2025-10-09T23:05:00Z'
        };

        const mockDailyData = generateMockDailyData();
        const mockTradesData = generateMockTradesData();

        setAnalyticsData(mockAnalyticsData);
        setDailyPerformance(mockDailyData);
        setRecentTrades(mockTradesData);
        setLastUpdated(new Date(mockAnalyticsData.last_sync));
      }

    } catch (err) {
      console.error("Trading analytics fetch error:", err);
      setError("Failed to load trading analytics data");
    } finally {
      setLoading(false);
    }
  };

  // Mock data generators for Phase 1A testing
  const generateMockDailyData = () => {
    const days = [];
    const today = new Date();
    for (let i = 29; i >= 0; i--) {
      const date = new Date(today);
      date.setDate(date.getDate() - i);
      
      // Simulate realistic trading data
      const hasTrading = Math.random() > 0.3; // 70% chance of trading
      const numTrades = hasTrading ? Math.floor(Math.random() * 5) + 1 : 0;
      const dailyPnL = hasTrading ? (Math.random() - 0.4) * 1000 : 0; // Slightly positive bias

      days.push({
        date: date.toISOString().split('T')[0],
        total_trades: numTrades,
        total_pnl: parseFloat(dailyPnL.toFixed(2)),
        winning_trades: Math.floor(numTrades * 0.6),
        losing_trades: Math.floor(numTrades * 0.4),
        status: dailyPnL > 0 ? 'profitable' : dailyPnL < 0 ? 'loss' : 'breakeven'
      });
    }
    return days;
  };

  const generateMockTradesData = () => {
    const symbols = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCHF', 'GOLD', 'SILVER'];
    const trades = [];
    
    for (let i = 0; i < 20; i++) {
      const closeTime = new Date();
      closeTime.setHours(closeTime.getHours() - Math.random() * 48); // Last 2 days
      
      const profit = (Math.random() - 0.4) * 500; // Slightly positive bias
      const volume = (Math.random() * 2 + 0.1).toFixed(2);
      
      trades.push({
        ticket: 123456789 + i,
        symbol: symbols[Math.floor(Math.random() * symbols.length)],
        type: Math.random() > 0.5 ? 'BUY' : 'SELL',
        volume: parseFloat(volume),
        profit: parseFloat(profit.toFixed(2)),
        close_time: closeTime.toISOString(),
        duration_minutes: Math.floor(Math.random() * 300) + 5 // 5-305 minutes
      });
    }
    
    return trades.sort((a, b) => new Date(b.close_time) - new Date(a.close_time));
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
      <div className="flex items-center justify-center p-8">
        <div className="text-white text-xl flex items-center">
          <RefreshCw className="animate-spin mr-2" />
          Loading trading analytics...
        </div>
      </div>
    );
  }

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
            {MT5_ACCOUNTS.map(account => (
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

      {/* Phase 1A Development Notice */}
      <div className="bg-blue-900/20 border border-blue-600 rounded-lg p-4">
        <div className="flex items-center">
          <Activity className="h-5 w-5 text-blue-400 mr-2" />
          <div>
            <p className="text-blue-400 font-medium">Phase 1A: Core Analytics Development</p>
            <p className="text-blue-300 text-sm mt-1">
              Currently displaying mock data for testing. Real MT5 data integration in progress.
              Testing with account 886557 (BALANCE Fund).
            </p>
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
                <CardTitle className="text-white text-sm font-medium flex items-center">
                  <DollarSign className="h-4 w-4 mr-2 text-green-400" />
                  Total P&L
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className={`text-2xl font-bold ${analyticsData.overview.total_pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {formatCurrency(analyticsData.overview.total_pnl)}
                </div>
                <div className="flex items-center mt-2">
                  <div className="text-sm text-slate-400">
                    Gross: {formatCurrency(analyticsData.overview.gross_profit)} / {formatCurrency(analyticsData.overview.gross_loss)}
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
};

export default TradingAnalyticsDashboard;