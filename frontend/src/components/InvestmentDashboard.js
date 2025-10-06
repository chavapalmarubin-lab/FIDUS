import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Badge } from "./ui/badge";
import { Alert, AlertDescription } from "./ui/alert";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { 
  DollarSign, 
  TrendingUp, 
  Calendar, 
  Clock, 
  PieChart, 
  BarChart3,
  Target,
  Eye,
  Plus,
  AlertCircle,
  CheckCircle,
  Timer,
  Wallet,
  ArrowUpRight,
  ArrowDownRight,
  RefreshCw,
  Download,
  Calculator
} from "lucide-react";
import InvestmentCreationWithMT5 from "./InvestmentCreationWithMT5";
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer, 
  PieChart as RechartsPieChart, 
  Cell, 
  BarChart, 
  Bar, 
  Pie,
  Area,
  AreaChart
} from "recharts";
import apiAxios from "../utils/apiAxios";
import { format, addMonths, differenceInDays } from "date-fns";

// Safe date parsing utility to prevent "Invalid time value" errors
const safeParseDate = (dateValue) => {
  if (!dateValue) return new Date(); // Return current date if no value
  
  try {
    // Handle both string and Date object inputs
    const dateStr = typeof dateValue === 'string' ? dateValue : dateValue.toString();
    
    // Check if Date.parse can handle it
    const parsedTime = Date.parse(dateStr);
    if (isNaN(parsedTime)) {
      console.warn(`Invalid date value: ${dateStr}, using current date`);
      return new Date();
    }
    
    const date = new Date(parsedTime);
    
    // Additional validation - check if the date is reasonable (not too far in past/future)
    const currentYear = new Date().getFullYear();
    const dateYear = date.getFullYear();
    
    if (dateYear < 2020 || dateYear > 2030) {
      console.warn(`Date year ${dateYear} seems unreasonable, using current date`);
      return new Date();
    }
    
    return date;
  } catch (error) {
    console.error(`Error parsing date: ${dateValue}`, error);
    return new Date(); // Fallback to current date
  }
};

// Safe date formatting utility
const safeFormatDate = (dateValue, formatStr = 'MMM dd, yyyy') => {
  try {
    const date = safeParseDate(dateValue);
    return format(date, formatStr);
  } catch (error) {
    console.error(`Error formatting date: ${dateValue}`, error);
    return 'Invalid Date';
  }
};

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const COLORS = ['#0891b2', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

const FUND_COLORS = {
  CORE: '#0891b2',
  BALANCE: '#10b981', 
  DYNAMIC: '#f59e0b',
  UNLIMITED: '#8b5cf6'
};

const InvestmentDashboard = ({ user, userType }) => {
  const [investments, setInvestments] = useState([]);
  const [portfolioStats, setPortfolioStats] = useState({});
  const [fundConfigs, setFundConfigs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [showInvestModal, setShowInvestModal] = useState(false);
  const [selectedInvestment, setSelectedInvestment] = useState(null);
  const [activeTab, setActiveTab] = useState("overview");
  const [refreshing, setRefreshing] = useState(false);

  // Investment form states
  const [investmentForm, setInvestmentForm] = useState({
    fund_code: "",
    amount: ""
  });

  useEffect(() => {
    fetchInvestments();
    fetchFundConfigs();
  }, []);

  const fetchInvestments = async () => {
    try {
      setLoading(true);
      const response = await apiAxios.get(`/investments/client/${user.id}`);
      setInvestments(response.data.investments);
      setPortfolioStats(response.data.portfolio_stats);
    } catch (err) {
      setError("Failed to fetch investments");
      console.error("Error fetching investments:", err);
    } finally {
      setLoading(false);
    }
  };

  const fetchFundConfigs = async () => {
    try {
      const response = await apiAxios.get(`/investments/funds/config`);
      setFundConfigs(response.data.funds);
    } catch (err) {
      console.error("Error fetching fund configs:", err);
    }
  };

  const handleCreateInvestment = async () => {
    try {
      if (!investmentForm.fund_code || !investmentForm.amount) {
        setError("Please select a fund and enter an amount");
        return;
      }

      const amount = parseFloat(investmentForm.amount);
      if (isNaN(amount) || amount <= 0) {
        setError("Please enter a valid amount");
        return;
      }

      const response = await apiAxios.post(`/investments/create`, {
        client_id: user.id,
        fund_code: investmentForm.fund_code,
        amount: amount
      });

      if (response.data.success) {
        setSuccess(response.data.message);
        setShowInvestModal(false);
        resetInvestmentForm();
        fetchInvestments();
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to create investment");
    }
  };

  const resetInvestmentForm = () => {
    setInvestmentForm({
      fund_code: "",
      amount: ""
    });
  };

  const refreshData = async () => {
    setRefreshing(true);
    await fetchInvestments();
    setRefreshing(false);
  };

  const getStatusBadge = (investment) => {
    const now = new Date();
    const incubationEnd = safeParseDate(investment.incubation_end_date);
    const minHoldEnd = safeParseDate(investment.minimum_hold_end_date);

    if (now < incubationEnd) {
      return <Badge className="bg-yellow-500 text-white">Incubating</Badge>;
    } else if (now < minHoldEnd) {
      return <Badge className="bg-blue-500 text-white">Active</Badge>;
    } else {
      return <Badge className="bg-green-500 text-white">Can Redeem</Badge>;
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(amount);
  };

  const preparePortfolioChartData = () => {
    return (investments || []).map(inv => ({
      name: inv.fund_code,
      value: inv.current_value,
      color: FUND_COLORS[inv.fund_code] || '#6b7280'
    }));
  };

  const prepareProjectionsChartData = () => {
    const chartData = [];
    const baseDate = new Date();
    
    for (let i = 0; i <= 24; i++) {
      const date = addMonths(baseDate, i);
      let totalValue = 0;
      
      investments.forEach(inv => {
        const interestStartDate = safeParseDate(inv.interest_start_date);
        const monthsFromStart = Math.max(0, i - Math.max(0, differenceInDays(interestStartDate, baseDate) / 30));
        let projectedValue = inv.principal_amount;
        
        if (monthsFromStart > 0 && inv.interest_rate > 0) {
          const interest = inv.principal_amount * (inv.interest_rate / 100) * monthsFromStart;
          projectedValue += interest;
        }
        
        totalValue += projectedValue;
      });
      
      chartData.push({
        month: safeFormatDate(date, 'MMM yyyy'),
        value: Math.round(totalValue)
      });
    }
    
    return chartData;
  };

  const calculateTimelineInfo = (investment) => {
    const daysUntilIncubationEnds = Math.max(0, differenceInDays(safeParseDate(investment.incubation_end_date), new Date()));
    const daysUntilCanRedeem = Math.max(0, differenceInDays(safeParseDate(investment.minimum_hold_end_date), new Date()));
    
    return { daysUntilIncubationEnds, daysUntilCanRedeem };
  };

  const renderInvestmentCard = (investment) => {
    const { daysUntilIncubationEnds, daysUntilCanRedeem } = calculateTimelineInfo(investment);
    
    return (
      <motion.div
        key={investment.investment_id}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-slate-800 rounded-lg border border-slate-700 p-6 hover:border-cyan-500 transition-colors"
      >
        <div className="flex items-start justify-between mb-4">
          <div>
            <h3 className="text-xl font-semibold text-white">{investment.fund_name}</h3>
            <p className="text-slate-400">Investment ID: {investment.investment_id.slice(0, 8)}...</p>
          </div>
          {getStatusBadge(investment)}
        </div>

        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <p className="text-slate-400 text-sm">Principal Amount</p>
            <p className="text-white font-semibold">{formatCurrency(investment.principal_amount)}</p>
          </div>
          <div>
            <p className="text-slate-400 text-sm">Current Value</p>
            <p className="text-white font-semibold">{formatCurrency(investment.current_value)}</p>
          </div>
          <div>
            <p className="text-slate-400 text-sm">Interest Earned</p>
            <p className="text-green-400 font-semibold">+{formatCurrency(investment.earned_interest)}</p>
          </div>
          <div>
            <p className="text-slate-400 text-sm">Interest Rate</p>
            <p className="text-cyan-400 font-semibold">{investment.interest_rate}% /month</p>
          </div>
        </div>

        <div className="space-y-2 text-sm">
          <div className="flex items-center justify-between">
            <span className="text-slate-400">Deposit Date:</span>
            <span className="text-white">{safeFormatDate(investment.deposit_date, 'MMM dd, yyyy')}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-slate-400">Interest Starts:</span>
            <span className="text-white">{safeFormatDate(investment.interest_start_date, 'MMM dd, yyyy')}</span>
          </div>
          {daysUntilIncubationEnds > 0 && (
            <div className="flex items-center justify-between">
              <span className="text-slate-400">Incubation Ends:</span>
              <span className="text-yellow-400">{daysUntilIncubationEnds} days</span>
            </div>
          )}
          {daysUntilCanRedeem > 0 && (
            <div className="flex items-center justify-between">
              <span className="text-slate-400">Can Redeem In:</span>
              <span className="text-blue-400">{daysUntilCanRedeem} days</span>
            </div>
          )}
        </div>

        <div className="mt-4 pt-4 border-t border-slate-700">
          <Button
            size="sm"
            variant="outline"
            onClick={() => setSelectedInvestment(investment)}
            className="w-full"
          >
            <Eye size={14} className="mr-2" />
            View Projections
          </Button>
        </div>
      </motion.div>
    );
  };

  const renderStatsCards = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <Card className="bg-slate-800 border-slate-700">
        <CardContent className="p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-cyan-500/20 rounded-full">
              <Wallet className="h-5 w-5 text-cyan-400" />
            </div>
            <div>
              <p className="text-sm text-slate-400">Total Invested</p>
              <p className="text-xl font-semibold text-white">{formatCurrency(portfolioStats.total_invested || 0)}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className="bg-slate-800 border-slate-700">
        <CardContent className="p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-500/20 rounded-full">
              <TrendingUp className="h-5 w-5 text-green-400" />
            </div>
            <div>
              <p className="text-sm text-slate-400">Current Value</p>
              <p className="text-xl font-semibold text-white">{formatCurrency(portfolioStats.total_current_value || 0)}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className="bg-slate-800 border-slate-700">
        <CardContent className="p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-yellow-500/20 rounded-full">
              <DollarSign className="h-5 w-5 text-yellow-400" />
            </div>
            <div>
              <p className="text-sm text-slate-400">Interest Earned</p>
              <p className="text-xl font-semibold text-green-400">+{formatCurrency(portfolioStats.total_earned_interest || 0)}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className="bg-slate-800 border-slate-700">
        <CardContent className="p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-500/20 rounded-full">
              <Target className="h-5 w-5 text-purple-400" />
            </div>
            <div>
              <p className="text-sm text-slate-400">Return %</p>
              <p className="text-xl font-semibold text-white">
                {portfolioStats.overall_return_percentage ? `+${portfolioStats.overall_return_percentage.toFixed(2)}%` : '0%'}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="text-slate-400 text-xl">Loading investments...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">Investment Dashboard</h2>
          <p className="text-slate-400">View your FIDUS fund investments</p>
        </div>
        
        <div className="flex gap-3">
          <Button
            variant="outline"
            onClick={refreshData}
            disabled={refreshing}
            className="border-slate-600 text-slate-300"
          >
            <RefreshCw size={16} className={`mr-2 ${refreshing ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          {/* Investment creation only available for admins */}
          {userType === "admin" && (
            <InvestmentCreationWithMT5 
              user={user}
              onInvestmentCreated={fetchInvestments}
            />
          )}
        </div>
      </div>

      {/* Success/Error Messages */}
      {error && (
        <Alert className="bg-red-900/20 border-red-500/50">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription className="text-red-300">{error}</AlertDescription>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setError("")}
            className="ml-auto text-red-400"
          >
            ×
          </Button>
        </Alert>
      )}

      {success && (
        <Alert className="bg-green-900/20 border-green-500/50">
          <CheckCircle className="h-4 w-4" />
          <AlertDescription className="text-green-300">{success}</AlertDescription>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setSuccess("")}
            className="ml-auto text-green-400"
          >
            ×
          </Button>
        </Alert>
      )}

      {/* Stats Cards */}
      {renderStatsCards()}

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="bg-slate-800 border-slate-600">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="investments">My Investments</TabsTrigger>
          <TabsTrigger value="projections">Projections</TabsTrigger>
          <TabsTrigger value="timeline">Timeline</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Portfolio Allocation Chart */}
            <Card className="bg-slate-800 border-slate-700">
              <CardHeader>
                <CardTitle className="text-white">Portfolio Allocation</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <RechartsPieChart>
                    <Pie
                      data={preparePortfolioChartData()}
                      cx="50%"
                      cy="50%"
                      outerRadius={100}
                      fill="#8884d8"
                      dataKey="value"
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    >
                      {preparePortfolioChartData().map((entry, index) => (
                        <Cell key={`investment-portfolio-cell-${index}-${entry.name}-${entry.value}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => formatCurrency(value)} />
                  </RechartsPieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Growth Projection Chart */}
            <Card className="bg-slate-800 border-slate-700">
              <CardHeader>
                <CardTitle className="text-white">Portfolio Growth Projection</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={prepareProjectionsChartData()}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis dataKey="month" stroke="#9ca3af" />
                    <YAxis stroke="#9ca3af" tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`} />
                    <Tooltip 
                      formatter={(value) => [formatCurrency(value), "Portfolio Value"]}
                      labelStyle={{ color: '#000' }}
                    />
                    <Area 
                      type="monotone" 
                      dataKey="value" 
                      stroke="#0891b2" 
                      fill="#0891b2" 
                      fillOpacity={0.3}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="investments" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {(investments || []).map(renderInvestmentCard)}
          </div>
          
          {(investments || []).length === 0 && (
            <Card className="bg-slate-800 border-slate-700">
              <CardContent className="p-12 text-center">
                <Wallet size={48} className="mx-auto mb-4 text-slate-400" />
                <h3 className="text-lg font-medium text-white mb-2">No Investments Yet</h3>
                <p className="text-slate-400 mb-4">
                  {userType === "admin" 
                    ? "Start creating client investments with FIDUS funds"
                    : "Contact your investment advisor to create investments in FIDUS funds"
                  }
                </p>
                {userType === "admin" && (
                  <Button
                    onClick={() => setShowInvestModal(true)}
                    className="bg-cyan-600 hover:bg-cyan-700"
                  >
                    <Plus size={16} className="mr-2" />
                    Create Client Investment
                  </Button>
                )}
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="projections" className="space-y-4">
          <Card className="bg-slate-800 border-slate-700">
            <CardHeader>
              <CardTitle className="text-white">Investment Projections</CardTitle>
              <p className="text-slate-400">Projected returns for the next 24 months</p>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={prepareProjectionsChartData()}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="month" stroke="#9ca3af" />
                  <YAxis stroke="#9ca3af" tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`} />
                  <Tooltip 
                    formatter={(value) => [formatCurrency(value), "Projected Value"]}
                    labelStyle={{ color: '#000' }}
                  />
                  <Legend />
                  <Line 
                    type="monotone" 
                    dataKey="value" 
                    stroke="#0891b2" 
                    strokeWidth={2}
                    dot={{ fill: '#0891b2', strokeWidth: 2, r: 4 }}
                    name="Portfolio Value"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="timeline" className="space-y-4">
          <div className="space-y-4">
            {(investments || []).map(investment => (
              <Card key={investment.investment_id} className="bg-slate-800 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white">{investment.fund_name}</CardTitle>
                  <p className="text-slate-400">{formatCurrency(investment.principal_amount)} Investment</p>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex items-center gap-3">
                      <CheckCircle className="h-5 w-5 text-green-400" />
                      <div>
                        <p className="text-white font-medium">Investment Created</p>
                        <p className="text-slate-400 text-sm">{safeFormatDate(investment.deposit_date, 'MMM dd, yyyy')}</p>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-3">
                      {new Date() >= safeParseDate(investment.incubation_end_date) ? (
                        <CheckCircle className="h-5 w-5 text-green-400" />
                      ) : (
                        <Timer className="h-5 w-5 text-yellow-400" />
                      )}
                      <div>
                        <p className="text-white font-medium">Incubation Period Ends</p>
                        <p className="text-slate-400 text-sm">{safeFormatDate(investment.incubation_end_date, 'MMM dd, yyyy')}</p>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-3">
                      {new Date() >= safeParseDate(investment.interest_start_date) ? (
                        <CheckCircle className="h-5 w-5 text-green-400" />
                      ) : (
                        <Clock className="h-5 w-5 text-blue-400" />
                      )}
                      <div>
                        <p className="text-white font-medium">Interest Payments Begin</p>
                        <p className="text-slate-400 text-sm">{safeFormatDate(investment.interest_start_date, 'MMM dd, yyyy')}</p>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-3">
                      {new Date() >= safeParseDate(investment.minimum_hold_end_date) ? (
                        <CheckCircle className="h-5 w-5 text-green-400" />
                      ) : (
                        <Clock className="h-5 w-5 text-slate-400" />
                      )}
                      <div>
                        <p className="text-white font-medium">Minimum Hold Period Ends</p>
                        <p className="text-slate-400 text-sm">{safeFormatDate(investment.minimum_hold_end_date, 'MMM dd, yyyy')}</p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>
      </Tabs>

      {/* New Investment Modal */}
      <AnimatePresence>
        {showInvestModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
            onClick={() => setShowInvestModal(false)}
          >
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.8, opacity: 0 }}
              className="bg-slate-800 rounded-lg p-6 max-w-md w-full mx-4"
              onClick={(e) => e.stopPropagation()}
            >
              <h3 className="text-xl font-semibold text-white mb-4">New Investment</h3>
              
              <div className="space-y-4">
                <div>
                  <Label className="text-slate-300">Select Fund</Label>
                  <Select value={investmentForm.fund_code} onValueChange={(value) => setInvestmentForm({...investmentForm, fund_code: value})}>
                    <SelectTrigger className="mt-1 bg-slate-700 border-slate-600 text-white">
                      <SelectValue placeholder="Choose a fund" />
                    </SelectTrigger>
                    <SelectContent className="bg-slate-700 border-slate-600">
                      {(fundConfigs || []).map(fund => (
                        <SelectItem key={fund.fund_code} value={fund.fund_code} className="text-white">
                          <div>
                            <div className="font-medium">{fund.name}</div>
                            <div className="text-sm text-slate-400">
                              {fund.interest_rate > 0 ? `${fund.interest_rate}% monthly` : 'No fixed return'} • 
                              Min: {formatCurrency(fund.minimum_investment)}
                              {fund.invitation_only && ' • Invitation Only'}
                            </div>
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                
                <div>
                  <Label className="text-slate-300">Investment Amount</Label>
                  <Input
                    type="number"
                    value={investmentForm.amount}
                    onChange={(e) => setInvestmentForm({...investmentForm, amount: e.target.value})}
                    placeholder="Enter amount in USD"
                    className="mt-1 bg-slate-700 border-slate-600 text-white"
                  />
                  {investmentForm.fund_code && (
                    <p className="text-slate-400 text-sm mt-1">
                      Minimum: {formatCurrency(fundConfigs.find(f => f.fund_code === investmentForm.fund_code)?.minimum_investment || 0)}
                    </p>
                  )}
                </div>
              </div>

              <div className="flex gap-3 mt-6">
                <Button
                  variant="outline"
                  onClick={() => {
                    setShowInvestModal(false);
                    resetInvestmentForm();
                  }}
                  className="flex-1 border-slate-600 text-slate-300"
                >
                  Cancel
                </Button>
                <Button
                  onClick={handleCreateInvestment}
                  className="flex-1 bg-cyan-600 hover:bg-cyan-700"
                >
                  Create Investment
                </Button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default InvestmentDashboard;