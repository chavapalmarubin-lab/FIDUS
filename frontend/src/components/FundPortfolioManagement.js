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
  PieChart
} from "lucide-react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart as RechartsPieChart, Cell } from 'recharts';
import axios from "axios";

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

  const fetchFundPortfolioData = async () => {
    try {
      setLoading(true);
      
      // Fetch fund overview data
      const fundsResponse = await axios.get(`${API}/admin/funds-overview`);
      const portfolioResponse = await axios.get(`${API}/admin/portfolio-summary`);
      
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
      const response = await axios.get(`${API}/admin/rebates/all`);
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
      Object.keys(funds).forEach(fundCode => {
        // Simulate performance trends
        const basePerformance = funds[fundCode].performance_ytd || 0;
        const dailyVariation = (Math.random() - 0.5) * 2; // -1% to +1% daily variation
        dataPoint[fundCode] = basePerformance + dailyVariation;
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
      const response = await axios.put(`${API}/admin/funds/${fundCode}/realtime`, {
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

      const response = await axios.post(`${API}/admin/rebates/add`, {
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
                  {Object.values(fundData).reduce((sum, fund) => sum + (fund.total_investors || 0), 0)}
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
                  {Object.keys(fundData).length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Individual Fund Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {Object.entries(fundData).map(([fundCode, fund]) => (
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
                  {fund.fund_type}
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
                      {formatCurrency(fund.aum)}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400">Investors:</span>
                    <span className="text-white ml-2 font-medium">
                      {fund.total_investors || 0}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400">NAV/Share:</span>
                    <span className="text-white ml-2 font-medium">
                      ${fund.nav_per_share}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400">YTD Return:</span>
                    <span className={`ml-2 font-medium ${
                      fund.performance_ytd >= 0 ? 'text-green-400' : 'text-red-400'
                    }`}>
                      {formatPercentage(fund.performance_ytd)}
                    </span>
                  </div>
                </div>

                {/* FIDUS Profitability */}
                <div className="bg-slate-700/50 rounded-lg p-3">
                  <div className="text-sm text-slate-300 mb-2">FIDUS Monthly Profit</div>
                  <div className="text-lg font-bold text-green-400">
                    {formatCurrency(calculateFidusProfit(fund))}
                  </div>
                  <div className="text-xs text-slate-400 mt-1">
                    Performance - Client Interest + Rebates
                  </div>
                </div>

                {/* Real-time Data Entry */}
                <div className="bg-slate-800/50 rounded-lg p-3">
                  <div className="text-sm text-slate-300 mb-3 flex items-center">
                    <Activity className="w-4 h-4 mr-2" />
                    Real-time Data Entry
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <Input
                        type="number"
                        step="0.01"
                        placeholder="Current NAV"
                        value={realTimeData[fundCode].current_nav}
                        onChange={(e) => setRealTimeData(prev => ({
                          ...prev,
                          [fundCode]: { ...prev[fundCode], current_nav: e.target.value }
                        }))}
                        className="bg-slate-700 border-slate-600 text-white text-sm"
                      />
                    </div>
                    <div>
                      <Input
                        type="number"
                        step="0.01"
                        placeholder="Today's %"
                        value={realTimeData[fundCode].performance_today}
                        onChange={(e) => setRealTimeData(prev => ({
                          ...prev,
                          [fundCode]: { ...prev[fundCode], performance_today: e.target.value }
                        }))}
                        className="bg-slate-700 border-slate-600 text-white text-sm"
                      />
                    </div>
                  </div>
                  <Button
                    onClick={() => updateRealTimeData(fundCode)}
                    className="w-full mt-3 bg-cyan-600 hover:bg-cyan-700 text-sm"
                    disabled={!realTimeData[fundCode].current_nav || !realTimeData[fundCode].performance_today}
                  >
                    Update Real-time Data
                  </Button>
                </div>
              </div>
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
                {Object.keys(fundData).map(fundCode => (
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
            {rebateData.slice(0, 5).map((rebate, index) => (
              <div key={`rebate-${rebate.fund_code}-${rebate.month}-${index}`} className="flex items-center justify-between p-3 bg-slate-700/50 rounded-lg">
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
            {rebateData.length === 0 && (
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
                    {Object.keys(fundData).map(fundCode => (
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