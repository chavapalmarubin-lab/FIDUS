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
  Download
} from "lucide-react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts';
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const CashFlowManagement = () => {
  const [cashFlowData, setCashFlowData] = useState([]);
  const [redemptionSchedule, setRedemptionSchedule] = useState([]);
  const [monthlyProjections, setMonthlyProjections] = useState([]);
  const [fundBreakdown, setFundBreakdown] = useState({});
  const [selectedTimeframe, setSelectedTimeframe] = useState('3months');
  const [selectedFund, setSelectedFund] = useState('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

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
      
      // Fetch cash flow data
      const cashFlowResponse = await axios.get(`${API}/admin/cashflow/overview`, {
        params: { timeframe: selectedTimeframe, fund: selectedFund }
      });
      
      // Fetch redemption schedule
      const redemptionResponse = await axios.get(`${API}/admin/cashflow/redemption-schedule`, {
        params: { timeframe: selectedTimeframe }
      });
      
      // Fetch projections
      const projectionsResponse = await axios.get(`${API}/admin/cashflow/projections`, {
        params: { months: getMonthsFromTimeframe(selectedTimeframe) }
      });

      if (cashFlowResponse.data.success) {
        setCashFlowData(cashFlowResponse.data.cash_flows || []);
        setRedemptionSchedule(redemptionResponse.data.redemption_schedule || []);
        setMonthlyProjections(projectionsResponse.data.projections || []);
        setFundBreakdown(cashFlowResponse.data.fund_breakdown || {});
      }
    } catch (err) {
      setError("Failed to load cash flow data");
      // Generate mock data for development
      generateMockCashFlowData();
    } finally {
      setLoading(false);
    }
  };

  const generateMockCashFlowData = () => {
    // Generate mock cash flow data for demonstration
    const mockCashFlows = [];
    const mockRedemptions = [];
    const mockProjections = [];
    
    const today = new Date();
    for (let i = 90; i >= 0; i--) {
      const date = new Date(today);
      date.setDate(date.getDate() - i);
      const dateStr = date.toISOString().split('T')[0];
      
      // Mock cash inflow (new investments)
      if (Math.random() > 0.7) {
        mockCashFlows.push({
          id: `inflow-${i}`,
          date: dateStr,
          type: 'inflow',
          amount: Math.floor(Math.random() * 500000) + 50000,
          fund_code: ['CORE', 'BALANCE', 'DYNAMIC', 'UNLIMITED'][Math.floor(Math.random() * 4)],
          client_name: `Client ${Math.floor(Math.random() * 100)}`,
          description: 'New Investment'
        });
      }
      
      // Mock cash outflow (redemptions)
      if (Math.random() > 0.85) {
        mockCashFlows.push({
          id: `outflow-${i}`,
          date: dateStr,
          type: 'outflow',
          amount: Math.floor(Math.random() * 200000) + 10000,
          fund_code: ['CORE', 'BALANCE', 'DYNAMIC', 'UNLIMITED'][Math.floor(Math.random() * 4)],
          client_name: `Client ${Math.floor(Math.random() * 100)}`,
          description: Math.random() > 0.5 ? 'Interest Redemption' : 'Principal Redemption'
        });
      }
    }

    // Generate upcoming redemption schedule
    for (let i = 1; i <= 30; i++) {
      const date = new Date(today);
      date.setDate(date.getDate() + i);
      const dateStr = date.toISOString().split('T')[0];
      
      if (Math.random() > 0.8) {
        mockRedemptions.push({
          date: dateStr,
          fund_code: ['CORE', 'BALANCE', 'DYNAMIC', 'UNLIMITED'][Math.floor(Math.random() * 4)],
          client_name: `Client ${Math.floor(Math.random() * 100)}`,
          potential_amount: Math.floor(Math.random() * 150000) + 5000,
          type: Math.random() > 0.7 ? 'principal' : 'interest',
          certainty: Math.random() > 0.5 ? 'high' : 'medium'
        });
      }
    }

    // Generate monthly projections
    for (let i = 0; i < 12; i++) {
      const date = new Date(today);
      date.setMonth(date.getMonth() + i);
      const monthYear = date.toISOString().substring(0, 7);
      
      mockProjections.push({
        month: monthYear,
        projected_inflow: Math.floor(Math.random() * 2000000) + 500000,
        projected_outflow: Math.floor(Math.random() * 800000) + 200000,
        net_flow: 0 // Will be calculated
      });
    }

    // Calculate net flow
    mockProjections.forEach(proj => {
      proj.net_flow = proj.projected_inflow - proj.projected_outflow;
    });

    setCashFlowData(mockCashFlows);
    setRedemptionSchedule(mockRedemptions);
    setMonthlyProjections(mockProjections);
    
    // Mock fund breakdown
    setFundBreakdown({
      CORE: { inflow: 2500000, outflow: 800000 },
      BALANCE: { inflow: 1800000, outflow: 600000 },
      DYNAMIC: { inflow: 3200000, outflow: 1200000 },
      UNLIMITED: { inflow: 900000, outflow: 300000 }
    });
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

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const calculateTotalInflow = () => {
    return cashFlowData
      .filter(item => item.type === 'inflow')
      .reduce((sum, item) => sum + item.amount, 0);
  };

  const calculateTotalOutflow = () => {
    return cashFlowData
      .filter(item => item.type === 'outflow')
      .reduce((sum, item) => sum + item.amount, 0);
  };

  const getNetCashFlow = () => {
    return calculateTotalInflow() - calculateTotalOutflow();
  };

  const getUpcomingRedemptions = (days = 7) => {
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() + days);
    
    return redemptionSchedule.filter(redemption => {
      const redemptionDate = new Date(redemption.date);
      return redemptionDate <= cutoffDate;
    });
  };

  const getCashFlowTrend = () => {
    // Group cash flows by date and calculate daily net flow
    const dailyFlows = {};
    
    cashFlowData.forEach(flow => {
      if (!dailyFlows[flow.date]) {
        dailyFlows[flow.date] = { inflow: 0, outflow: 0 };
      }
      
      if (flow.type === 'inflow') {
        dailyFlows[flow.date].inflow += flow.amount;
      } else {
        dailyFlows[flow.date].outflow += flow.amount;
      }
    });

    return Object.entries(dailyFlows)
      .map(([date, flows]) => ({
        date,
        inflow: flows.inflow,
        outflow: flows.outflow,
        net_flow: flows.inflow - flows.outflow
      }))
      .sort((a, b) => new Date(a.date) - new Date(b.date));
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-white text-xl">Loading cash flow data...</div>
      </div>
    );
  }

  const trendData = getCashFlowTrend();
  const upcomingRedemptions = getUpcomingRedemptions();

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

      {/* Cash Flow Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="dashboard-card">
          <CardContent className="p-6">
            <div className="flex items-center">
              <ArrowUpCircle className="h-8 w-8 text-green-400" />
              <div className="ml-4">
                <p className="text-sm font-medium text-slate-400">Total Inflow</p>
                <p className="text-2xl font-bold text-green-400">
                  {formatCurrency(calculateTotalInflow())}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="dashboard-card">
          <CardContent className="p-6">
            <div className="flex items-center">
              <ArrowDownCircle className="h-8 w-8 text-red-400" />
              <div className="ml-4">
                <p className="text-sm font-medium text-slate-400">Total Outflow</p>
                <p className="text-2xl font-bold text-red-400">
                  {formatCurrency(calculateTotalOutflow())}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="dashboard-card">
          <CardContent className="p-6">
            <div className="flex items-center">
              <DollarSign className={`h-8 w-8 ${getNetCashFlow() >= 0 ? 'text-green-400' : 'text-red-400'}`} />
              <div className="ml-4">
                <p className="text-sm font-medium text-slate-400">Net Cash Flow</p>
                <p className={`text-2xl font-bold ${getNetCashFlow() >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {formatCurrency(getNetCashFlow())}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="dashboard-card">
          <CardContent className="p-6">
            <div className="flex items-center">
              <AlertTriangle className="h-8 w-8 text-yellow-400" />
              <div className="ml-4">
                <p className="text-sm font-medium text-slate-400">Upcoming Redemptions</p>
                <p className="text-2xl font-bold text-yellow-400">
                  {upcomingRedemptions.length}
                </p>
                <p className="text-xs text-slate-400">Next 7 days</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Cash Flow Trend Chart */}
      <Card className="dashboard-card">
        <CardHeader>
          <CardTitle className="text-white flex items-center">
            <TrendingUp className="mr-2 h-5 w-5 text-cyan-400" />
            Cash Flow Trend
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trendData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="date" stroke="#9CA3AF" />
                <YAxis stroke="#9CA3AF" />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#1f2937', 
                    border: '1px solid #374151',
                    borderRadius: '8px' 
                  }}
                  formatter={(value) => [formatCurrency(value), '']}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="inflow"
                  stroke="#10b981"
                  strokeWidth={2}
                  name="Cash Inflow"
                />
                <Line
                  type="monotone"
                  dataKey="outflow"
                  stroke="#ef4444"
                  strokeWidth={2}
                  name="Cash Outflow"
                />
                <Line
                  type="monotone"
                  dataKey="net_flow"
                  stroke="#0891b2"
                  strokeWidth={3}
                  name="Net Cash Flow"
                  strokeDasharray="5 5"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Monthly Projections */}
      <Card className="dashboard-card">
        <CardHeader>
          <CardTitle className="text-white flex items-center">
            <Calendar className="mr-2 h-5 w-5 text-cyan-400" />
            12-Month Cash Flow Projections
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={monthlyProjections}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="month" stroke="#9CA3AF" />
                <YAxis stroke="#9CA3AF" />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#1f2937', 
                    border: '1px solid #374151',
                    borderRadius: '8px' 
                  }}
                  formatter={(value) => [formatCurrency(value), '']}
                />
                <Legend />
                <Bar dataKey="projected_inflow" fill="#10b981" name="Projected Inflow" />
                <Bar dataKey="projected_outflow" fill="#ef4444" name="Projected Outflow" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Upcoming Redemptions */}
      <Card className="dashboard-card">
        <CardHeader>
          <CardTitle className="text-white flex items-center">
            <Clock className="mr-2 h-5 w-5 text-yellow-400" />
            Upcoming Redemption Schedule (Next 7 Days)
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {upcomingRedemptions.map((redemption, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-slate-700/50 rounded-lg border-l-4 border-yellow-400">
                <div className="flex items-center">
                  <div className="mr-4">
                    <Badge 
                      className="mb-1"
                      style={{ backgroundColor: FUND_COLORS[redemption.fund_code] }}
                    >
                      {redemption.fund_code}
                    </Badge>
                    <div className="text-white font-medium">{redemption.client_name}</div>
                    <div className="text-slate-400 text-sm capitalize">
                      {redemption.type} Redemption • {redemption.certainty} certainty
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-yellow-400 font-bold">
                    {formatCurrency(redemption.potential_amount)}
                  </div>
                  <div className="text-slate-400 text-sm">
                    {formatDate(redemption.date)}
                  </div>
                </div>
              </div>
            ))}
            {upcomingRedemptions.length === 0 && (
              <div className="text-center py-8 text-slate-400">
                No redemptions scheduled for the next 7 days
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Fund Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="dashboard-card">
          <CardHeader>
            <CardTitle className="text-white flex items-center">
              <Users className="mr-2 h-5 w-5 text-cyan-400" />
              Fund Cash Flow Breakdown
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {Object.entries(fundBreakdown).map(([fundCode, data]) => (
                <div key={fundCode} className="flex items-center justify-between p-3 bg-slate-700/50 rounded-lg">
                  <div className="flex items-center">
                    <div 
                      className="w-4 h-4 rounded-full mr-3"
                      style={{ backgroundColor: FUND_COLORS[fundCode] }}
                    ></div>
                    <div>
                      <div className="text-white font-medium">{fundCode} Fund</div>
                      <div className="text-slate-400 text-sm">
                        Net: {formatCurrency((data.inflow || 0) - (data.outflow || 0))}
                      </div>
                    </div>
                  </div>
                  <div className="text-right text-sm">
                    <div className="text-green-400">↑ {formatCurrency(data.inflow || 0)}</div>
                    <div className="text-red-400">↓ {formatCurrency(data.outflow || 0)}</div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card className="dashboard-card">
          <CardHeader>
            <CardTitle className="text-white flex items-center">
              <Filter className="mr-2 h-5 w-5 text-cyan-400" />
              Recent Transactions
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 max-h-80 overflow-y-auto">
              {cashFlowData.slice(0, 10).map((transaction) => (
                <div key={transaction.id} className="flex items-center justify-between p-3 bg-slate-700/50 rounded-lg">
                  <div className="flex items-center">
                    {transaction.type === 'inflow' ? (
                      <ArrowUpCircle className="h-5 w-5 text-green-400 mr-3" />
                    ) : (
                      <ArrowDownCircle className="h-5 w-5 text-red-400 mr-3" />
                    )}
                    <div>
                      <div className="text-white font-medium">{transaction.client_name}</div>
                      <div className="text-slate-400 text-sm">
                        {transaction.description} • {transaction.fund_code}
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className={`font-bold ${
                      transaction.type === 'inflow' ? 'text-green-400' : 'text-red-400'
                    }`}>
                      {transaction.type === 'inflow' ? '+' : '-'}{formatCurrency(transaction.amount)}
                    </div>
                    <div className="text-slate-400 text-xs">
                      {formatDate(transaction.date)}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default CashFlowManagement;