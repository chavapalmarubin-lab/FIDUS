import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Badge } from "./ui/badge";
import { Alert, AlertDescription } from "./ui/alert";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { 
  DollarSign, 
  TrendingUp, 
  Users, 
  PieChart, 
  BarChart3,
  RefreshCw,
  Eye,
  Download,
  Calendar,
  Target,
  Wallet,
  Clock,
  CheckCircle,
  AlertCircle,
  Plus
} from "lucide-react";
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
  Pie
} from "recharts";
import axios from "axios";
import { format, differenceInDays } from "date-fns";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const COLORS = ['#0891b2', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

const FUND_COLORS = {
  CORE: '#0891b2',
  BALANCE: '#10b981', 
  DYNAMIC: '#f59e0b',
  UNLIMITED: '#8b5cf6'
};

const AdminInvestmentManagement = () => {
  const [overviewData, setOverviewData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [refreshing, setRefreshing] = useState(false);
  const [activeTab, setActiveTab] = useState("overview");
  const [showCreateInvestmentModal, setShowCreateInvestmentModal] = useState(false);
  const [fundConfigs, setFundConfigs] = useState([]);

  // Investment creation form state
  const [investmentForm, setInvestmentForm] = useState({
    client_id: "",
    fund_code: "",
    amount: ""
  });

  useEffect(() => {
    fetchOverviewData();
    fetchFundConfigs();
  }, []);

  const fetchFundConfigs = async () => {
    try {
      const response = await axios.get(`${API}/investments/funds/config`);
      setFundConfigs(response.data.funds);
    } catch (err) {
      console.error("Error fetching fund configs:", err);
    }
  };

  const fetchOverviewData = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/investments/admin/overview`);
      setOverviewData(response.data);
    } catch (err) {
      setError("Failed to fetch investment overview");
      console.error("Error fetching investment overview:", err);
    } finally {
      setLoading(false);
    }
  };

  const refreshData = async () => {
    setRefreshing(true);
    await fetchOverviewData();
    setRefreshing(false);
  };

  const handleCreateInvestment = async () => {
    try {
      if (!investmentForm.client_id || !investmentForm.fund_code || !investmentForm.amount) {
        setError("Please fill in all fields");
        return;
      }

      const amount = parseFloat(investmentForm.amount);
      if (isNaN(amount) || amount <= 0) {
        setError("Please enter a valid amount");
        return;
      }

      const response = await axios.post(`${API}/investments/create`, {
        client_id: investmentForm.client_id,
        fund_code: investmentForm.fund_code,
        amount: amount
      });

      if (response.data.success) {
        setSuccess(`Investment created successfully: ${response.data.message}`);
        setShowCreateInvestmentModal(false);
        resetInvestmentForm();
        fetchOverviewData();
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to create investment");
    }
  };

  const resetInvestmentForm = () => {
    setInvestmentForm({
      client_id: "",
      fund_code: "",
      amount: ""
    });
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(amount);
  };

  const getStatusBadge = (investment) => {
    const now = new Date();
    const incubationEnd = new Date(investment.incubation_end_date);
    const minHoldEnd = new Date(investment.minimum_hold_end_date);

    if (now < incubationEnd) {
      return <Badge className="bg-yellow-500 text-white">Incubating</Badge>;
    } else if (now < minHoldEnd) {
      return <Badge className="bg-blue-500 text-white">Active</Badge>;
    } else {
      return <Badge className="bg-green-500 text-white">Can Redeem</Badge>;
    }
  };

  const prepareFundAllocationData = () => {
    if (!overviewData?.fund_summaries) return [];
    
    return overviewData.fund_summaries.map((fund, index) => ({
      name: fund.fund_name,
      value: fund.total_current_value,
      color: FUND_COLORS[fund.fund_code] || COLORS[index % COLORS.length]
    }));
  };

  const prepareInvestmentVolumeData = () => {
    if (!overviewData?.fund_summaries) return [];
    
    return overviewData.fund_summaries.map(fund => ({
      fund: fund.fund_code,
      investors: fund.total_investors,
      aum: fund.total_current_value / 1000, // In thousands
      avgInvestment: fund.average_investment / 1000 // In thousands
    }));
  };

  const renderOverviewStats = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <Card className="bg-slate-800 border-slate-700">
        <CardContent className="p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-cyan-500/20 rounded-full">
              <DollarSign className="h-5 w-5 text-cyan-400" />
            </div>
            <div>
              <p className="text-sm text-slate-400">Total AUM</p>
              <p className="text-xl font-semibold text-white">{formatCurrency(overviewData?.total_aum || 0)}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className="bg-slate-800 border-slate-700">
        <CardContent className="p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-500/20 rounded-full">
              <Target className="h-5 w-5 text-green-400" />
            </div>
            <div>
              <p className="text-sm text-slate-400">Total Investments</p>
              <p className="text-xl font-semibold text-white">{overviewData?.total_investments || 0}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className="bg-slate-800 border-slate-700">
        <CardContent className="p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-500/20 rounded-full">
              <Users className="h-5 w-5 text-purple-400" />
            </div>
            <div>
              <p className="text-sm text-slate-400">Active Clients</p>
              <p className="text-xl font-semibold text-white">{overviewData?.total_clients || 0}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className="bg-slate-800 border-slate-700">
        <CardContent className="p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-yellow-500/20 rounded-full">
              <TrendingUp className="h-5 w-5 text-yellow-400" />
            </div>
            <div>
              <p className="text-sm text-slate-400">Avg Investment</p>
              <p className="text-xl font-semibold text-white">
                {overviewData?.total_investments > 0 
                  ? formatCurrency((overviewData?.total_aum || 0) / overviewData?.total_investments)
                  : formatCurrency(0)
                }
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
        <div className="text-slate-400 text-xl">Loading investment data...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">Investment Management</h2>
          <p className="text-slate-400">Monitor and manage FIDUS fund investments</p>
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
          <Button
            onClick={() => setShowCreateInvestmentModal(true)}
            className="bg-cyan-600 hover:bg-cyan-700"
          >
            <Plus size={16} className="mr-2" />
            Create Investment
          </Button>
          <Button
            variant="outline"
            className="border-slate-600 text-slate-300"
          >
            <Download size={16} className="mr-2" />
            Export Report
          </Button>
        </div>
      </div>

      {/* Error Display */}
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

      {/* Overview Stats */}
      {renderOverviewStats()}

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="bg-slate-800 border-slate-600">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="funds">Fund Analysis</TabsTrigger>
          <TabsTrigger value="investments">All Investments</TabsTrigger>
          <TabsTrigger value="clients">Client Portfolio</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Fund Allocation Chart */}
            <Card className="bg-slate-800 border-slate-700">
              <CardHeader>
                <CardTitle className="text-white">AUM Distribution by Fund</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <RechartsPieChart>
                    <Pie
                      data={prepareFundAllocationData()}
                      cx="50%"
                      cy="50%"
                      outerRadius={100}
                      fill="#8884d8"
                      dataKey="value"
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    >
                      {prepareFundAllocationData().map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => formatCurrency(value)} />
                  </RechartsPieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Investment Volume by Fund */}
            <Card className="bg-slate-800 border-slate-700">
              <CardHeader>
                <CardTitle className="text-white">Investment Volume by Fund</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={prepareInvestmentVolumeData()}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis dataKey="fund" stroke="#9ca3af" />
                    <YAxis stroke="#9ca3af" />
                    <Tooltip 
                      formatter={(value, name) => [
                        name === 'aum' ? formatCurrency(value * 1000) : 
                        name === 'avgInvestment' ? formatCurrency(value * 1000) : value,
                        name === 'aum' ? 'AUM' : 
                        name === 'avgInvestment' ? 'Avg Investment' : 'Investors'
                      ]}
                      labelStyle={{ color: '#000' }}
                    />
                    <Legend />
                    <Bar dataKey="investors" fill="#0891b2" name="Investors" />
                    <Bar dataKey="aum" fill="#10b981" name="AUM (k)" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="funds" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {overviewData?.fund_summaries?.map(fund => (
              <Card key={fund.fund_code} className="bg-slate-800 border-slate-700">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-white text-lg">{fund.fund_name}</CardTitle>
                    <Badge 
                      className="text-white"
                      style={{ backgroundColor: FUND_COLORS[fund.fund_code] }}
                    >
                      {fund.fund_code}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div>
                    <p className="text-slate-400 text-sm">Total AUM</p>
                    <p className="text-white font-semibold">{formatCurrency(fund.total_current_value)}</p>
                  </div>
                  <div>
                    <p className="text-slate-400 text-sm">Investors</p>
                    <p className="text-white font-semibold">{fund.total_investors}</p>
                  </div>
                  <div>
                    <p className="text-slate-400 text-sm">Avg Investment</p>
                    <p className="text-white font-semibold">{formatCurrency(fund.average_investment)}</p>
                  </div>
                  <div>
                    <p className="text-slate-400 text-sm">Interest Paid</p>
                    <p className="text-green-400 font-semibold">+{formatCurrency(fund.total_interest_paid)}</p>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="investments" className="space-y-4">
          <div className="bg-slate-800 rounded-lg border border-slate-700">
            <div className="p-4 border-b border-slate-700">
              <h3 className="text-white font-semibold">All Client Investments</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-slate-700">
                  <tr>
                    <th className="px-4 py-3 text-left text-slate-300 font-medium">Client</th>
                    <th className="px-4 py-3 text-left text-slate-300 font-medium">Fund</th>
                    <th className="px-4 py-3 text-left text-slate-300 font-medium">Principal</th>
                    <th className="px-4 py-3 text-left text-slate-300 font-medium">Current Value</th>
                    <th className="px-4 py-3 text-left text-slate-300 font-medium">Interest Earned</th>
                    <th className="px-4 py-3 text-left text-slate-300 font-medium">Status</th>
                    <th className="px-4 py-3 text-left text-slate-300 font-medium">Date</th>
                  </tr>
                </thead>
                <tbody>
                  {overviewData?.all_investments?.map(investment => (
                    <tr key={investment.investment_id} className="border-b border-slate-700 hover:bg-slate-700/50">
                      <td className="px-4 py-3 text-white">{investment.client_name}</td>
                      <td className="px-4 py-3">
                        <Badge 
                          className="text-white"
                          style={{ backgroundColor: FUND_COLORS[investment.fund_code] }}
                        >
                          {investment.fund_code}
                        </Badge>
                      </td>
                      <td className="px-4 py-3 text-white">{formatCurrency(investment.principal_amount)}</td>
                      <td className="px-4 py-3 text-white">{formatCurrency(investment.current_value)}</td>
                      <td className="px-4 py-3 text-green-400">+{formatCurrency(investment.earned_interest)}</td>
                      <td className="px-4 py-3">{getStatusBadge(investment)}</td>
                      <td className="px-4 py-3 text-slate-400">{format(new Date(investment.deposit_date), 'MMM dd, yyyy')}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              
              {(!overviewData?.all_investments || overviewData.all_investments.length === 0) && (
                <div className="p-8 text-center">
                  <Wallet size={48} className="mx-auto mb-4 text-slate-400" />
                  <h3 className="text-lg font-medium text-white mb-2">No Investments Yet</h3>
                  <p className="text-slate-400">Client investments will appear here once created</p>
                </div>
              )}
            </div>
          </div>
        </TabsContent>

        <TabsContent value="clients" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {/* This would show individual client portfolios */}
            <Card className="bg-slate-800 border-slate-700">
              <CardHeader>
                <CardTitle className="text-white">Client Portfolio Overview</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-slate-400">Client portfolio analysis coming soon...</p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AdminInvestmentManagement;