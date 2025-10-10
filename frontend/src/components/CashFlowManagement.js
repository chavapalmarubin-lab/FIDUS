import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { 
  ArrowUpCircle, 
  ArrowDownCircle,
  Calendar,
  DollarSign,
  TrendingUp,
  AlertTriangle,
  Users,
  Clock,
  Filter,
  Download,
  Plus
} from "lucide-react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts';
import apiAxios from "../utils/apiAxios";

const CashFlowManagement = () => {
  const [cashFlowData, setCashFlowData] = useState([]);
  const [fundAccounting, setFundAccounting] = useState({});
  const [fundBreakdown, setFundBreakdown] = useState({});
  const [rebatesSummary, setRebatesSummary] = useState({});
  const [cashFlowCalendar, setCashFlowCalendar] = useState(null);  // New calendar data
  const [selectedTimeframe, setSelectedTimeframe] = useState('3months');
  const [selectedFund, setSelectedFund] = useState('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showAddRebateModal, setShowAddRebateModal] = useState(false);
  const [newRebate, setNewRebate] = useState({
    fund_code: '',
    amount: '',
    broker: '',
    lots_traded: '',
    rebate_per_lot: '',
    description: ''
  });

  const FUND_COLORS = {
    CORE: '#0891b2',
    BALANCE: '#10b981', 
    DYNAMIC: '#f59e0b',
    UNLIMITED: '#ef4444'
  };

  useEffect(() => {
    fetchCashFlowData();
  }, [selectedTimeframe, selectedFund]);

  const fetchCashFlowData = async () => {
    try {
      setLoading(true);
      setError("");
      
      // Fetch fund accounting cash flow data
      const cashFlowResponse = await apiAxios.get(`/admin/cashflow/overview`, {
        params: { timeframe: selectedTimeframe, fund: selectedFund }
      });
      
      // Fetch cash flow calendar data
      const calendarResponse = await apiAxios.get(`/admin/cashflow/calendar`, {
        params: { timeframe: selectedTimeframe, fund: selectedFund }
      });
      
      if (cashFlowResponse.data.success) {
        // Map API summary data to fund accounting structure
        const summary = cashFlowResponse.data.summary || {};
        const fundAccountingData = {
          assets: {
            mt5_trading_profits: summary.mt5_trading_profits || 0,
            separation_interest: summary.separation_interest || 0,  // New separation account line item
            broker_rebates: summary.broker_rebates || 0,
            total_inflows: summary.fund_revenue || 0
          },
          liabilities: {
            client_obligations: summary.client_interest_obligations || 0,
            fund_obligations: summary.fund_obligations || 0,
            total_outflows: summary.fund_obligations || 0
          },
          net_profit: summary.net_profit || 0,
          net_fund_profitability: summary.net_profit || 0  // Map to expected field name
        };
        
        setCashFlowData(cashFlowResponse.data.monthly_breakdown || []);
        setFundAccounting(fundAccountingData);
        setFundBreakdown(cashFlowResponse.data.fund_breakdown || {});
        setRebatesSummary(cashFlowResponse.data.rebates_summary || {});
        
        // Process calendar data if available
        if (calendarResponse.data.success) {
          setCashFlowCalendar(calendarResponse.data.calendar || null);
          console.log("✅ Cash flow calendar data loaded successfully:", calendarResponse.data.calendar);
        }
        
        console.log("✅ Fund accounting cash flow data loaded successfully:", cashFlowResponse.data.fund_accounting);
      } else {
        throw new Error("API returned unsuccessful response");
      }
    } catch (err) {
      console.error("❌ Cash flow API error:", err);
      setError("Failed to load cash flow data");
      // Set example fund accounting data
      setFundAccounting({
        assets: {
          mt5_trading_profits: 0,
          broker_rebates: 0,
          total_inflows: 0
        },
        liabilities: {
          client_obligations: 0,
          upcoming_redemptions: 0,
          total_outflows: 0
        },
        net_fund_profitability: 0
      });
    } finally {
      setLoading(false);
    }
  };

  const handleAddRebate = async () => {
    try {
      if (!newRebate.fund_code || !newRebate.amount || !newRebate.broker) {
        setError("Please fill in all required fields");
        return;
      }

      const response = await apiAxios.post('/admin/rebates/add', {
        fund_code: newRebate.fund_code,
        amount: parseFloat(newRebate.amount),
        broker: newRebate.broker,
        lots_traded: parseFloat(newRebate.lots_traded) || 0,
        rebate_per_lot: parseFloat(newRebate.rebate_per_lot) || 0,
        description: newRebate.description || `Lot-based rebate from ${newRebate.broker}`,
        date: new Date().toISOString().split('T')[0] // Today's date
      });

      if (response.data.success) {
        // Reset form
        setNewRebate({
          fund_code: '',
          amount: '',
          broker: '',
          lots_traded: '',
          rebate_per_lot: '',
          description: ''
        });
        setShowAddRebateModal(false);
        
        // Refresh data
        await fetchCashFlowData();
        
        console.log("✅ Rebate added successfully:", response.data.rebate);
      } else {
        throw new Error("Failed to add rebate");
      }
    } catch (err) {
      console.error("❌ Add rebate error:", err);
      setError("Failed to add rebate");
    }
  };

  const getMonthsFromTimeframe = (timeframe) => {
    switch (timeframe) {
      case '1month': return 1;
      case '3months': return 3;
      case '6months': return 6;
      case '1year': return 12;
      default: return 3;
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

  // Performance Analysis Helper Functions
  const calculatePerformanceMetrics = () => {
    if (!fundAccounting?.assets || !fundAccounting?.liabilities || !cashFlowCalendar?.summary) {
      return null;
    }

    // Get current fund data
    const totalObligations = cashFlowCalendar.summary.total_future_obligations || 0;
    const currentRevenue = cashFlowCalendar.current_revenue || fundAccounting.assets.total_inflows || 0;
    const investmentStartDate = new Date('2025-10-01');
    const contractEndDate = new Date('2026-12-01');
    const today = new Date();
    
    // Calculate time periods
    const totalContractDays = Math.ceil((contractEndDate - investmentStartDate) / (1000 * 60 * 60 * 24));
    const daysElapsed = Math.max(1, Math.ceil((today - investmentStartDate) / (1000 * 60 * 60 * 24)));
    const daysRemaining = Math.max(1, Math.ceil((contractEndDate - today) / (1000 * 60 * 60 * 24)));
    
    // Required Performance Metrics
    const stillNeeded = Math.max(0, totalObligations - currentRevenue);
    const percentComplete = totalObligations > 0 ? (currentRevenue / totalObligations) * 100 : 0;
    const requiredDailyAvg = stillNeeded / daysRemaining;
    const requiredMonthlyAvg = requiredDailyAvg * 30;
    
    // Actual Performance Metrics
    const mt5Trading = fundAccounting.assets.mt5_trading_profits || 0;
    const separationInterest = fundAccounting.assets.separation_interest || 0;
    const brokerRebates = fundAccounting.assets.broker_rebates || 0;
    const netRevenue = currentRevenue;
    const actualDailyAvg = netRevenue / daysElapsed;
    const actualMonthlyProjection = actualDailyAvg * 30;
    
    // Gap Analysis
    const monthlyGap = actualMonthlyProjection - requiredMonthlyAvg;
    const performanceRate = requiredMonthlyAvg > 0 ? (actualMonthlyProjection / requiredMonthlyAvg) * 100 : 0;
    const projectedTotal = actualDailyAvg * totalContractDays;
    const projectedSurplusDeficit = projectedTotal - totalObligations;
    
    // Status determination
    let status, statusClass, statusMessage;
    if (performanceRate >= 100) {
      status = 'on_track';
      statusClass = 'success';
      statusMessage = '✅ ON TRACK';
    } else if (performanceRate >= 80) {
      status = 'at_risk';
      statusClass = 'warning';
      statusMessage = '⚠️ AT RISK';
    } else {
      status = 'behind';
      statusClass = 'danger';
      statusMessage = '🚨 BEHIND SCHEDULE';
    }
    
    return {
      required: {
        totalNeeded: totalObligations,
        alreadyEarned: currentRevenue,
        stillNeeded: stillNeeded,
        percentComplete: percentComplete,
        requiredDailyAvg: requiredDailyAvg,
        requiredMonthlyAvg: requiredMonthlyAvg,
        daysRemaining: daysRemaining
      },
      actual: {
        mt5Trading: mt5Trading,
        separationInterest: separationInterest,
        brokerRebates: brokerRebates,
        netRevenue: netRevenue,
        daysElapsed: daysElapsed,
        actualDailyAvg: actualDailyAvg,
        actualMonthlyProjection: actualMonthlyProjection
      },
      gap: {
        monthlyGap: monthlyGap,
        performanceRate: performanceRate,
        projectedTotal: projectedTotal,
        projectedSurplusDeficit: projectedSurplusDeficit,
        status: status,
        statusClass: statusClass,
        statusMessage: statusMessage
      },
      timing: {
        totalContractDays: totalContractDays,
        daysElapsed: daysElapsed,
        daysRemaining: daysRemaining,
        investmentStartDate: investmentStartDate,
        contractEndDate: contractEndDate
      }
    };
  };

  const getRiskAssessmentMessage = (metrics) => {
    if (!metrics) return "Performance analysis not available";
    
    const { gap, actual, timing } = metrics;
    
    if (timing.daysElapsed < 30) {
      // Early stage assessment
      if (gap.performanceRate >= 100) {
        return `Fund is currently exceeding performance targets. Monitor over longer period to confirm sustainability. Current high rate driven by separation interest (${formatCurrency(actual.separationInterest)}) offsetting MT5 losses (${formatCurrency(actual.mt5Trading)}).`;
      } else {
        return `Fund performance is below target in early stages. Monitor closely over next 30 days. Focus on improving MT5 trading performance to supplement separation interest.`;
      }
    } else {
      // Mature assessment
      if (gap.performanceRate >= 120) {
        return `Fund is significantly exceeding targets with ${gap.performanceRate.toFixed(0)}% of required performance. Current trajectory projects ${formatCurrency(gap.projectedSurplusDeficit)} surplus by contract end. Consider strategies for deploying excess returns.`;
      } else if (gap.performanceRate >= 100) {
        return `Fund is on track to meet all obligations with ${gap.performanceRate.toFixed(0)}% of required performance. Continue monitoring to maintain current trajectory. Projected surplus: ${formatCurrency(gap.projectedSurplusDeficit)}.`;
      } else if (gap.performanceRate >= 80) {
        return `⚠️ Fund is at risk of falling short of obligations. Currently achieving ${gap.performanceRate.toFixed(0)}% of required performance. Immediate action needed to improve returns by ${formatCurrency(Math.abs(gap.monthlyGap))}/month. Projected deficit: ${formatCurrency(Math.abs(gap.projectedSurplusDeficit))}.`;
      } else {
        return `🚨 Fund is significantly behind required performance at ${gap.performanceRate.toFixed(0)}% of target. Urgent intervention required to avoid defaulting on client obligations. Projected deficit: ${formatCurrency(Math.abs(gap.projectedSurplusDeficit))}. Review MT5 strategies immediately.`;
      }
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-white text-xl">Loading cash flow data...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white flex items-center">
          <TrendingUp className="mr-3 h-8 w-8 text-cyan-400" />
          Cash Flow Management
        </h2>
        <div className="flex gap-3">
          <select
            value={selectedTimeframe}
            onChange={(e) => setSelectedTimeframe(e.target.value)}
            className="px-3 py-2 bg-slate-700 border border-slate-600 text-white rounded-md"
          >
            <option value="1month">Last Month</option>
            <option value="3months">Last 3 Months</option>
            <option value="6months">Last 6 Months</option>
            <option value="1year">Last Year</option>
          </select>
          <select
            value={selectedFund}
            onChange={(e) => setSelectedFund(e.target.value)}
            className="px-3 py-2 bg-slate-700 border border-slate-600 text-white rounded-md"
          >
            <option value="all">All Funds</option>
            <option value="CORE">CORE Fund</option>
            <option value="BALANCE">BALANCE Fund</option>
            <option value="DYNAMIC">DYNAMIC Fund</option>
            <option value="UNLIMITED">UNLIMITED Fund</option>
          </select>
          <Button className="bg-cyan-600 hover:bg-cyan-700">
            <Download className="w-4 h-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-900/20 border border-red-600 rounded-lg p-3">
          <p className="text-red-400">{error}</p>
        </div>
      )}

      {/* FUND ACCOUNTING OVERVIEW */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* FUND ASSETS (What Fund Owns) */}
        <Card className="dashboard-card">
          <CardHeader>
            <CardTitle className="text-white flex items-center">
              <ArrowUpCircle className="mr-2 h-5 w-5 text-green-400" />
              Fund Assets (Income Sources)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* MT5 Trading Profits */}
              <div className="flex justify-between items-center p-3 bg-slate-800/50 rounded-lg">
                <div>
                  <p className="text-sm text-slate-400">MT5 Trading Profits</p>
                  <p className="text-xs text-slate-500">Fund's investment performance</p>
                </div>
                <div className="text-right">
                  <p className={`text-lg font-bold ${(fundAccounting?.assets?.mt5_trading_profits || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {formatCurrency(fundAccounting?.assets?.mt5_trading_profits || 0)}
                  </p>
                </div>
              </div>
              
              {/* Separation Interest */}
              <div className="flex justify-between items-center p-3 bg-slate-800/50 rounded-lg">
                <div>
                  <p className="text-sm text-slate-400">Separation Interest</p>
                  <p className="text-xs text-slate-500">Interest earned in separation accounts</p>
                </div>
                <div className="text-right">
                  <p className="text-lg font-bold text-green-400">
                    {formatCurrency(fundAccounting?.assets?.separation_interest || 0)}
                  </p>
                </div>
              </div>
              
              {/* Broker Rebates */}
              <div className="flex justify-between items-center p-3 bg-slate-800/50 rounded-lg">
                <div>
                  <p className="text-sm text-slate-400">Broker Rebates</p>
                  <p className="text-xs text-slate-500">Commission from trading volume</p>
                </div>
                <div className="text-right">
                  <p className="text-lg font-bold text-cyan-400">
                    {formatCurrency(fundAccounting?.assets?.broker_rebates || 0)}
                  </p>
                </div>
              </div>
              
              {/* Total Assets */}
              <div className="border-t border-slate-600 pt-3">
                <div className="flex justify-between items-center">
                  <p className="text-white font-semibold">Total Fund Assets</p>
                  <p className="text-xl font-bold text-green-400">
                    {formatCurrency(fundAccounting?.assets?.total_inflows || 0)}
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* FUND LIABILITIES (What Fund Owes) */}
        <Card className="dashboard-card">
          <CardHeader>
            <CardTitle className="text-white flex items-center">
              <ArrowDownCircle className="mr-2 h-5 w-5 text-red-400" />
              Fund Liabilities (Obligations)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* Client Obligations */}
              <div className="flex justify-between items-center p-3 bg-slate-800/50 rounded-lg">
                <div>
                  <p className="text-sm text-slate-400">Client Interest Obligations</p>
                  <p className="text-xs text-slate-500">Promised returns to clients</p>
                </div>
                <div className="text-right">
                  <p className="text-lg font-bold text-red-400">
                    {formatCurrency(fundAccounting?.liabilities?.client_obligations || 0)}
                  </p>
                </div>
              </div>
              
              {/* Upcoming Redemptions */}
              <div className="flex justify-between items-center p-3 bg-slate-800/50 rounded-lg">
                <div>
                  <p className="text-sm text-slate-400">Upcoming Redemptions</p>
                  <p className="text-xs text-slate-500">Scheduled client withdrawals</p>
                </div>
                <div className="text-right">
                  <p className="text-lg font-bold text-yellow-400">
                    {formatCurrency(fundAccounting?.liabilities?.upcoming_redemptions || 0)}
                  </p>
                </div>
              </div>
              
              {/* Total Liabilities */}
              <div className="border-t border-slate-600 pt-3">
                <div className="flex justify-between items-center">
                  <p className="text-white font-semibold">Total Fund Liabilities</p>
                  <p className="text-xl font-bold text-red-400">
                    {formatCurrency(fundAccounting?.liabilities?.total_outflows || 0)}
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* NET FUND PROFITABILITY */}
      <Card className="dashboard-card">
        <CardHeader>
          <CardTitle className="text-white flex items-center">
            <DollarSign className="mr-2 h-5 w-5 text-cyan-400" />
            Net Fund Profitability Analysis
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center p-6 bg-green-900/20 rounded-lg border border-green-600/30">
              <ArrowUpCircle className="h-12 w-12 text-green-400 mx-auto mb-2" />
              <p className="text-green-400 font-semibold">Fund Revenue</p>
              <p className="text-2xl font-bold text-green-400">
                {formatCurrency(fundAccounting?.assets?.total_inflows || 0)}
              </p>
              <p className="text-xs text-slate-400 mt-1">Trading + Rebates</p>
            </div>
            
            <div className="text-center p-6 bg-red-900/20 rounded-lg border border-red-600/30">
              <ArrowDownCircle className="h-12 w-12 text-red-400 mx-auto mb-2" />
              <p className="text-red-400 font-semibold">Fund Obligations</p>
              <p className="text-2xl font-bold text-red-400">
                {formatCurrency(fundAccounting?.liabilities?.total_outflows || 0)}
              </p>
              <p className="text-xs text-slate-400 mt-1">Client Commitments</p>
            </div>
            
            <div className={`text-center p-6 rounded-lg border ${
              (fundAccounting?.net_fund_profitability || 0) >= 0 
                ? 'bg-cyan-900/20 border-cyan-600/30' 
                : 'bg-red-900/20 border-red-600/30'
            }`}>
              <DollarSign className={`h-12 w-12 mx-auto mb-2 ${
                (fundAccounting?.net_fund_profitability || 0) >= 0 ? 'text-cyan-400' : 'text-red-400'
              }`} />
              <p className={`font-semibold ${
                (fundAccounting?.net_fund_profitability || 0) >= 0 ? 'text-cyan-400' : 'text-red-400'
              }`}>Net Profit</p>
              <p className={`text-2xl font-bold ${
                (fundAccounting?.net_fund_profitability || 0) >= 0 ? 'text-cyan-400' : 'text-red-400'
              }`}>
                {formatCurrency(fundAccounting?.net_fund_profitability || 0)}
              </p>
              <p className="text-xs text-slate-400 mt-1">
                {(fundAccounting?.net_fund_profitability || 0) >= 0 ? 'Profitable' : 'Loss Making'}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* PERFORMANCE ANALYSIS SECTION - NEW */}
      <Card className="dashboard-card">
        <CardHeader>
          <CardTitle className="text-white flex items-center">
            <TrendingUp className="mr-2 h-5 w-5 text-cyan-400" />
            📊 Fund Performance Analysis
          </CardTitle>
          <p className="text-slate-400 text-sm mt-1">
            Track actual fund performance against required returns to meet all client obligations
          </p>
        </CardHeader>
        <CardContent>
          <PerformanceAnalysisSection 
            fundAccounting={fundAccounting}
            cashFlowCalendar={cashFlowCalendar}
          />
        </CardContent>
      </Card>

      {/* REBATES COMMISSION BREAKDOWN */}
      <Card className="dashboard-card">
        <CardHeader>
          <CardTitle className="text-white flex items-center justify-between">
            <div className="flex items-center">
              <TrendingUp className="mr-2 h-5 w-5 text-cyan-400" />
              Broker Rebates & Commission Structure
            </div>
            <Button 
              onClick={() => setShowAddRebateModal(true)}
              className="bg-cyan-600 hover:bg-cyan-700"
              size="sm"
            >
              <Plus className="h-4 w-4 mr-2" />
              Add Rebate
            </Button>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="text-white font-semibold mb-3">Rebate Summary</h4>
              <div className="space-y-3">
                <div className="flex justify-between items-center p-3 bg-slate-800/50 rounded-lg">
                  <span className="text-slate-400">Total Rebates Earned</span>
                  <span className="text-cyan-400 font-bold">
                    {formatCurrency(rebatesSummary?.total_rebates || 0)}
                  </span>
                </div>
                <div className="text-sm text-slate-300">
                  <p><strong>Revenue Source:</strong> Broker commissions based on trading volume (lots)</p>
                  <p><strong>Structure:</strong> Variable rate per lot traded on MT5 accounts</p>
                  <p><strong>Calculation:</strong> Total lots × rebate per lot = total rebate</p>
                </div>
              </div>
            </div>
            
            <div>
              <h4 className="text-white font-semibold mb-3">Commission by Fund</h4>
              <div className="space-y-2">
                {Object.entries(rebatesSummary?.rebate_breakdown || {}).map(([fundCode, amount]) => (
                  <div key={fundCode} className="flex justify-between items-center">
                    <div className="flex items-center">
                      <div 
                        className="w-3 h-3 rounded-full mr-2"
                        style={{ backgroundColor: FUND_COLORS[fundCode] }}
                      ></div>
                      <span className="text-slate-300">{fundCode} Fund</span>
                    </div>
                    <span className="text-cyan-400 font-medium">
                      {formatCurrency(amount)}
                    </span>
                  </div>
                ))}
                {Object.keys(rebatesSummary?.rebate_breakdown || {}).length === 0 && (
                  <p className="text-slate-400 text-sm">No rebates recorded yet. Click "Add Rebate" to start tracking.</p>
                )}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
      
      {/* CASH FLOW OBLIGATIONS CALENDAR */}
      {cashFlowCalendar && (
        <Card className="dashboard-card">
          <CardHeader>
            <CardTitle className="text-white flex items-center">
              <Calendar className="mr-2 h-5 w-5 text-cyan-400" />
              Cash Flow Obligations Calendar
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              
              {/* Current Status Summary */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 bg-slate-800/50 rounded-lg">
                <div className="text-center">
                  <p className="text-sm text-slate-400">Current Fund Revenue</p>
                  <p className="text-xl font-bold text-green-400">
                    {formatCurrency(cashFlowCalendar.current_revenue || 0)}
                  </p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-slate-400">Total Future Obligations</p>
                  <p className="text-xl font-bold text-orange-400">
                    {formatCurrency(cashFlowCalendar.summary?.total_future_obligations || 0)}
                  </p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-slate-400">Net Position</p>
                  <p className={`text-xl font-bold ${
                    (cashFlowCalendar.current_revenue - cashFlowCalendar.summary?.total_future_obligations) >= 0 
                      ? 'text-green-400' : 'text-red-400'
                  }`}>
                    {formatCurrency((cashFlowCalendar.current_revenue || 0) - (cashFlowCalendar.summary?.total_future_obligations || 0))}
                  </p>
                </div>
              </div>

              {/* Key Milestones */}
              {cashFlowCalendar.milestones && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {cashFlowCalendar.milestones.next_payment && (
                    <div className="p-4 bg-blue-900/20 border border-blue-600/30 rounded-lg">
                      <h4 className="text-sm font-medium text-blue-400 mb-2">⏰ Next Payment Due</h4>
                      <p className="text-white font-bold">{cashFlowCalendar.milestones.next_payment.date}</p>
                      <p className="text-green-400 font-bold">{formatCurrency(cashFlowCalendar.milestones.next_payment.amount)}</p>
                      <p className="text-xs text-slate-400">{cashFlowCalendar.milestones.next_payment.days_away} days away</p>
                    </div>
                  )}
                  
                  {cashFlowCalendar.milestones.first_large_payment && (
                    <div className="p-4 bg-yellow-900/20 border border-yellow-600/30 rounded-lg">
                      <h4 className="text-sm font-medium text-yellow-400 mb-2">⚠️ First Large Payment</h4>
                      <p className="text-white font-bold">{cashFlowCalendar.milestones.first_large_payment.date}</p>
                      <p className="text-yellow-400 font-bold">{formatCurrency(cashFlowCalendar.milestones.first_large_payment.amount)}</p>
                      <p className="text-xs text-slate-400">{cashFlowCalendar.milestones.first_large_payment.days_away} days away</p>
                    </div>
                  )}
                  
                  {cashFlowCalendar.milestones.contract_end && (
                    <div className="p-4 bg-red-900/20 border border-red-600/30 rounded-lg">
                      <h4 className="text-sm font-medium text-red-400 mb-2">🚨 Contract End</h4>
                      <p className="text-white font-bold">{cashFlowCalendar.milestones.contract_end.date}</p>
                      <p className="text-red-400 font-bold">{formatCurrency(cashFlowCalendar.milestones.contract_end.amount)}</p>
                      <p className="text-xs text-slate-400">{cashFlowCalendar.milestones.contract_end.days_away} days away</p>
                    </div>
                  )}
                </div>
              )}

              {/* Monthly Timeline */}
              <div className="space-y-3">
                <h4 className="text-lg font-semibold text-white mb-4">📅 Monthly Obligations Timeline</h4>
                
                {Object.entries(cashFlowCalendar.monthly_obligations || {})
                  .sort(([a], [b]) => a.localeCompare(b))
                  .slice(0, 12) // Show next 12 months
                  .map(([monthKey, monthData]) => {
                    const statusColors = {
                      funded: 'border-green-600/30 bg-green-900/20',
                      warning: 'border-yellow-600/30 bg-yellow-900/20', 
                      critical: 'border-red-600/30 bg-red-900/20'
                    };
                    
                    const statusIcons = {
                      funded: '✅',
                      warning: '⚠️',
                      critical: '🚨'
                    };
                    
                    return (
                      <div key={monthKey} className={`p-4 border rounded-lg ${statusColors[monthData.status] || statusColors.funded}`}>
                        <div className="flex justify-between items-start mb-3">
                          <div>
                            <h5 className="font-bold text-white">
                              {statusIcons[monthData.status]} {new Date(monthData.date).toLocaleDateString('en-US', { 
                                month: 'long', 
                                year: 'numeric' 
                              })}
                            </h5>
                            <p className="text-xs text-slate-400">{monthData.days_away} days away</p>
                          </div>
                          <div className="text-right">
                            <p className="text-lg font-bold text-white">{formatCurrency(monthData.total_due)}</p>
                            <p className="text-xs text-slate-400">Total Due</p>
                          </div>
                        </div>
                        
                        {/* Obligation Breakdown */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-3">
                          {monthData.core_interest > 0 && (
                            <div className="text-sm">
                              <span className="text-slate-400">CORE Interest:</span>
                              <span className="text-blue-400 ml-2 font-medium">{formatCurrency(monthData.core_interest)}</span>
                            </div>
                          )}
                          {monthData.balance_interest > 0 && (
                            <div className="text-sm">
                              <span className="text-slate-400">BALANCE Interest:</span>
                              <span className="text-purple-400 ml-2 font-medium">{formatCurrency(monthData.balance_interest)}</span>
                            </div>
                          )}
                          {monthData.principal_redemptions > 0 && (
                            <div className="text-sm">
                              <span className="text-slate-400">Principal:</span>
                              <span className="text-red-400 ml-2 font-medium">{formatCurrency(monthData.principal_redemptions)}</span>
                            </div>
                          )}
                        </div>
                        
                        {/* Running Balance */}
                        <div className="flex justify-between items-center pt-3 border-t border-slate-600/30">
                          <span className="text-sm text-slate-400">Running Balance After Payment:</span>
                          <span className={`font-bold ${
                            monthData.running_balance_after >= 0 ? 'text-green-400' : 'text-red-400'
                          }`}>
                            {formatCurrency(monthData.running_balance_after)}
                          </span>
                        </div>
                      </div>
                    );
                  })
                }
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* FUND ACCOUNTING BREAKDOWN TABLE */}
      <Card className="dashboard-card">
        <CardHeader>
          <CardTitle className="text-white flex items-center">
            <TrendingUp className="mr-2 h-5 w-5 text-cyan-400" />
            Fund Accounting Breakdown - Assets vs Liabilities
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-600">
                  <th className="text-left text-slate-400 font-medium py-3">Fund</th>
                  <th className="text-right text-slate-400 font-medium py-3">MT5 Profits</th>
                  <th className="text-right text-slate-400 font-medium py-3">Rebates</th>
                  <th className="text-right text-slate-400 font-medium py-3">Total Assets</th>
                  <th className="text-right text-slate-400 font-medium py-3">Client Obligations</th>
                  <th className="text-right text-slate-400 font-medium py-3">Net Position</th>
                  <th className="text-right text-slate-400 font-medium py-3">Status</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(fundBreakdown).map(([fundCode, data]) => {
                  const netPosition = (data.net_flow || 0);
                  return (
                    <tr key={fundCode} className="border-b border-slate-700/50">
                      <td className="py-4">
                        <div className="flex items-center">
                          <div 
                            className="w-3 h-3 rounded-full mr-3"
                            style={{ backgroundColor: FUND_COLORS[fundCode] }}
                          ></div>
                          <span className="text-white font-medium">{fundCode} Fund</span>
                        </div>
                      </td>
                      <td className="text-right text-green-400 font-medium py-4">
                        {formatCurrency(data.mt5_profits || 0)}
                      </td>
                      <td className="text-right text-cyan-400 font-medium py-4">
                        {formatCurrency(data.rebates || 0)}
                      </td>
                      <td className="text-right text-blue-400 font-medium py-4">
                        {formatCurrency(data.total_inflows || 0)}
                      </td>
                      <td className="text-right text-red-400 font-medium py-4">
                        {formatCurrency(data.client_obligations || 0)}
                      </td>
                      <td className={`text-right font-bold py-4 ${netPosition >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                        {formatCurrency(netPosition)}
                      </td>
                      <td className="text-right py-4">
                        <Badge className={netPosition >= 0 ? 'bg-green-600' : 'bg-red-600'}>
                          {netPosition >= 0 ? 'Profitable' : 'At Risk'}
                        </Badge>
                      </td>
                    </tr>
                  );
                })}
                {/* TOTAL FUND POSITION */}
                <tr className="border-t-2 border-cyan-600 bg-slate-800/50">
                  <td className="py-4">
                    <span className="text-cyan-400 font-bold text-lg">TOTAL FUND</span>
                  </td>
                  <td className="text-right text-green-400 font-bold text-lg py-4">
                    {formatCurrency(fundAccounting?.assets?.mt5_trading_profits || 0)}
                  </td>
                  <td className="text-right text-cyan-400 font-bold text-lg py-4">
                    {formatCurrency(fundAccounting?.assets?.broker_rebates || 0)}
                  </td>
                  <td className="text-right text-blue-400 font-bold text-lg py-4">
                    {formatCurrency(fundAccounting?.assets?.total_inflows || 0)}
                  </td>
                  <td className="text-right text-red-400 font-bold text-lg py-4">
                    {formatCurrency(fundAccounting?.liabilities?.total_outflows || 0)}
                  </td>
                  <td className={`text-right font-bold text-lg py-4 ${(fundAccounting?.net_fund_profitability || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {formatCurrency(fundAccounting?.net_fund_profitability || 0)}
                  </td>
                  <td className="text-right py-4">
                    <Badge className={`text-lg ${(fundAccounting?.net_fund_profitability || 0) >= 0 ? 'bg-green-600' : 'bg-red-600'}`}>
                      {(fundAccounting?.net_fund_profitability || 0) >= 0 ? 'PROFITABLE' : 'AT RISK'}
                    </Badge>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Status Information */}
      <Card className="dashboard-card">
        <CardHeader>
          <CardTitle className="text-white flex items-center">
            <Clock className="mr-2 h-5 w-5 text-cyan-400" />
            Cash Flow Status
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="text-white font-semibold mb-3">System Status</h4>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-slate-400">Data Source</span>
                  <span className="text-green-400">✅ Real Investment Data</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-400">Last Updated</span>
                  <span className="text-white">{new Date().toLocaleString()}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-400">Calculation Method</span>
                  <span className="text-cyan-400">Aggregated Totals</span>
                </div>
              </div>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-3">Summary</h4>
              <div className="space-y-2">
                <div className="text-sm text-slate-300">
                  Cash flow totals now represent the <span className="text-cyan-400 font-semibold">sum of all funds</span> instead of individual fund data.
                </div>
                <div className="text-sm text-slate-300">
                  This provides a comprehensive view of the overall financial health across all investment funds.
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* ADD REBATE MODAL */}
      {showAddRebateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-slate-800 rounded-lg p-6 w-full max-w-md">
            <h3 className="text-xl font-bold text-white mb-4">Add Broker Rebate</h3>
            <p className="text-sm text-slate-400 mb-4">Rebates are variable based on trading volume (lots)</p>
            
            <div className="space-y-4">
              {/* Fund Selection */}
              <div>
                <label className="block text-sm font-medium text-slate-400 mb-2">Fund *</label>
                <select
                  value={newRebate.fund_code}
                  onChange={(e) => setNewRebate({...newRebate, fund_code: e.target.value})}
                  className="w-full px-3 py-2 bg-slate-700 border border-slate-600 text-white rounded-md"
                  required
                >
                  <option value="">Select Fund</option>
                  <option value="CORE">CORE Fund</option>
                  <option value="BALANCE">BALANCE Fund</option>
                  <option value="DYNAMIC">DYNAMIC Fund</option>
                  <option value="UNLIMITED">UNLIMITED Fund</option>
                </select>
              </div>

              {/* Total Rebate Amount */}
              <div>
                <label className="block text-sm font-medium text-slate-400 mb-2">Total Rebate Amount ($) *</label>
                <input
                  type="number"
                  step="0.01"
                  value={newRebate.amount}
                  onChange={(e) => setNewRebate({...newRebate, amount: e.target.value})}
                  className="w-full px-3 py-2 bg-slate-700 border border-slate-600 text-white rounded-md"
                  placeholder="0.00"
                  required
                />
              </div>

              {/* Broker */}
              <div>
                <label className="block text-sm font-medium text-slate-400 mb-2">Broker *</label>
                <select
                  value={newRebate.broker}
                  onChange={(e) => setNewRebate({...newRebate, broker: e.target.value})}
                  className="w-full px-3 py-2 bg-slate-700 border border-slate-600 text-white rounded-md"
                  required
                >
                  <option value="">Select Broker</option>
                  <option value="Multibank">Multibank</option>
                  <option value="DooTechnology">DooTechnology</option>
                  <option value="IC Markets">IC Markets</option>
                  <option value="FXCM">FXCM</option>
                  <option value="Other">Other</option>
                </select>
              </div>

              {/* Optional Trading Details */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-slate-400 mb-2">Lots Traded (Optional)</label>
                  <input
                    type="number"
                    step="0.01"
                    value={newRebate.lots_traded}
                    onChange={(e) => setNewRebate({...newRebate, lots_traded: e.target.value})}
                    className="w-full px-3 py-2 bg-slate-700 border border-slate-600 text-white rounded-md"
                    placeholder="0.00"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-400 mb-2">$ per Lot (Optional)</label>
                  <input
                    type="number"
                    step="0.01"
                    value={newRebate.rebate_per_lot}
                    onChange={(e) => setNewRebate({...newRebate, rebate_per_lot: e.target.value})}
                    className="w-full px-3 py-2 bg-slate-700 border border-slate-600 text-white rounded-md"
                    placeholder="0.00"
                  />
                </div>
              </div>

              {/* Description */}
              <div>
                <label className="block text-sm font-medium text-slate-400 mb-2">Notes (Optional)</label>
                <textarea
                  value={newRebate.description}
                  onChange={(e) => setNewRebate({...newRebate, description: e.target.value})}
                  className="w-full px-3 py-2 bg-slate-700 border border-slate-600 text-white rounded-md"
                  rows="2"
                  placeholder="Additional notes about this rebate..."
                />
              </div>

              {/* Info Note */}
              <div className="bg-blue-900/20 border border-blue-600/30 rounded-lg p-3">
                <p className="text-blue-400 text-xs">
                  <strong>Note:</strong> Rebates are variable based on trading volume. API automation for lot tracking will be implemented later.
                </p>
              </div>
            </div>

            {/* Error Message */}
            {error && (
              <div className="mt-4 p-3 bg-red-900/20 border border-red-600 rounded-lg">
                <p className="text-red-400 text-sm">{error}</p>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex justify-end space-x-3 mt-6">
              <Button
                onClick={() => {
                  setShowAddRebateModal(false);
                  setNewRebate({fund_code: '', amount: '', broker: '', lots_traded: '', rebate_per_lot: '', description: ''});
                  setError('');
                }}
                variant="outline"
                className="border-slate-600 text-slate-300 hover:bg-slate-700"
              >
                Cancel
              </Button>
              <Button
                onClick={handleAddRebate}
                className="bg-cyan-600 hover:bg-cyan-700"
              >
                Add Rebate
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CashFlowManagement;