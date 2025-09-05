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
import apiAxios from "../utils/apiAxios";
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
  const [readyClients, setReadyClients] = useState([]);

  // Investment creation form state
  const [investmentForm, setInvestmentForm] = useState({
    client_id: "",
    fund_code: "",
    amount: "",
    deposit_date: "",
    // Payment confirmation fields
    payment_method: "fiat", // fiat or crypto
    wire_confirmation_number: "",
    bank_reference: "",
    transaction_hash: "",
    blockchain_network: "",
    wallet_address: "",
    payment_notes: ""
  });

  useEffect(() => {
    fetchOverviewData();
    fetchFundConfigs();
    fetchReadyClients();
  }, []);

  const fetchFundConfigs = async () => {
    try {
      const response = await apiAxios.get(`/investments/funds/config`);
      setFundConfigs(response.data.funds);
    } catch (err) {
      console.error("Error fetching fund configs:", err);
    }
  };

  const fetchReadyClients = async () => {
    try {
      const response = await apiAxios.get(`/clients/ready-for-investment`);
      setReadyClients(response.data.ready_clients);
    } catch (err) {
      console.error("Error fetching ready clients:", err);
    }
  };

  const fetchOverviewData = async () => {
    try {
      setLoading(true);
      const response = await apiAxios.get(`/investments/admin/overview`);
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
      if (!investmentForm.client_id || !investmentForm.fund_code || !investmentForm.amount || !investmentForm.deposit_date) {
        setError("Please fill in all fields including the deposit date");
        return;
      }

      const amount = parseFloat(investmentForm.amount);
      if (isNaN(amount) || amount <= 0) {
        setError("Please enter a valid amount");
        return;
      }

      // Validate payment confirmation fields based on method
      if (investmentForm.payment_method === "fiat") {
        if (!investmentForm.wire_confirmation_number) {
          setError("Please enter wire confirmation number for FIAT payment");
          return;
        }
      } else if (investmentForm.payment_method === "crypto") {
        if (!investmentForm.transaction_hash) {
          setError("Please enter transaction hash for crypto payment");
          return;
        }
      }

      // First create the investment
      const investmentResponse = await axios.post(`${API}/investments/create`, {
        client_id: investmentForm.client_id,
        fund_code: investmentForm.fund_code,
        amount: amount,
        deposit_date: investmentForm.deposit_date
      });

      if (investmentResponse.data.success) {
        const investmentId = investmentResponse.data.investment_id;
        
        // Then confirm the deposit payment
        const confirmationData = {
          investment_id: investmentId,
          payment_method: investmentForm.payment_method,
          amount: amount,
          currency: "USD",
          notes: investmentForm.payment_notes
        };

        // Add method-specific fields
        if (investmentForm.payment_method === "fiat") {
          confirmationData.wire_confirmation_number = investmentForm.wire_confirmation_number;
          confirmationData.bank_reference = investmentForm.bank_reference;
        } else {
          confirmationData.transaction_hash = investmentForm.transaction_hash;
          confirmationData.blockchain_network = investmentForm.blockchain_network;
          confirmationData.wallet_address = investmentForm.wallet_address;
        }

        const confirmationResponse = await axios.post(`${API}/payments/deposit/confirm`, confirmationData);

        if (confirmationResponse.data.success) {
          setSuccess(`Investment created and deposit confirmed via ${investmentForm.payment_method.toUpperCase()}: ${investmentResponse.data.message}`);
        } else {
          setSuccess(`Investment created but payment confirmation failed: ${investmentResponse.data.message}`);
        }

        setShowCreateInvestmentModal(false);
        resetInvestmentForm();
        fetchOverviewData();
        fetchReadyClients(); // Refresh client list
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to create investment");
    }
  };

  const resetInvestmentForm = () => {
    setInvestmentForm({
      client_id: "",
      fund_code: "",
      amount: "",
      deposit_date: "",
      // Payment confirmation fields
      payment_method: "fiat",
      wire_confirmation_number: "",
      bank_reference: "",
      transaction_hash: "",
      blockchain_network: "",
      wallet_address: "",
      payment_notes: ""
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
    
    return (overviewData?.fund_summaries || []).map((fund, index) => ({
      name: fund.fund_name,
      value: fund.total_current_value,
      color: FUND_COLORS[fund.fund_code] || COLORS[index % COLORS.length]
    }));
  };

  const prepareInvestmentVolumeData = () => {
    if (!overviewData?.fund_summaries) return [];
    
    return (overviewData?.fund_summaries || []).map(fund => ({
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

      {/* Success Display */}
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
                      {(prepareFundAllocationData() || []).map((entry, index) => (
                        <Cell key={`admin-investment-cell-${index}-${entry.name}-${entry.value}`} fill={entry.color} />
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

      {/* Create Investment Modal */}
      <AnimatePresence>
        {showCreateInvestmentModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
            onClick={() => setShowCreateInvestmentModal(false)}
          >
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.8, opacity: 0 }}
              className="bg-slate-800 rounded-lg w-full max-w-2xl max-h-[90vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="p-6">
                <h3 className="text-xl font-semibold text-white mb-4">Create Client Investment</h3>
                
                <div className="space-y-4">
                  {/* Debug information */}
                  <div className="mb-2 p-2 bg-blue-900/20 rounded text-xs text-blue-300">
                    Debug: Ready clients: {readyClients.length} | Selected: {investmentForm.client_id || 'None'}
                    <br />API Status: {readyClients.length > 0 ? 'Loaded successfully' : 'Loading or no data'}
                  </div>
                
                <div>
                  <Label htmlFor="client-select" className="text-slate-300 text-sm font-medium mb-2 block">Select Client *</Label>
                  
                  {/* Fallback HTML select to ensure functionality */}
                  <select 
                    id="client-select"
                    value={investmentForm.client_id}
                    onChange={(e) => {
                      console.log('Client selected:', e.target.value);
                      setInvestmentForm({...investmentForm, client_id: e.target.value});
                    }}
                    className="w-full min-h-[42px] px-3 py-2 bg-slate-700 border-2 border-slate-600 text-white rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="" disabled>Choose a client ready for investment</option>
                    {(readyClients || []).map(client => (
                      <option 
                        key={client.client_id} 
                        value={client.client_id}
                        className="bg-slate-700 text-white"
                      >
                        {client.name} - {client.email} (Investments: {client.total_investments})
                      </option>
                    ))}
                  </select>
                  
                  {readyClients.length === 0 && (
                    <p className="text-yellow-400 text-sm mt-1">
                      ⚠️ No clients ready for investment. Complete AML/KYC and Agreement in Client Management.
                    </p>
                  )}
                </div>
                
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
                
                <div>
                  <Label className="text-slate-300 flex items-center">
                    <Calendar className="w-4 h-4 mr-2" />
                    Date of Deposit (Sets Investment Timeline) *
                  </Label>
                  <Input
                    type="date"
                    value={investmentForm.deposit_date}
                    onChange={(e) => setInvestmentForm({...investmentForm, deposit_date: e.target.value})}
                    className="mt-1 bg-slate-700 border-slate-600 text-white"
                  />
                  <p className="text-xs text-slate-400 mt-1">
                    This date determines the 2-month incubation period and all investment timelines
                  </p>
                </div>
                </div>

                {/* Payment Confirmation Section */}
                <div className="border-t border-slate-600 pt-4">
                  <h4 className="text-lg font-medium text-white mb-4 flex items-center">
                    <Wallet className="w-5 h-5 mr-2 text-green-400" />
                    Deposit Payment Confirmation
                  </h4>
                  
                  <div className="space-y-4">
                    <div>
                      <Label className="text-slate-300">Payment Method *</Label>
                      <Select value={investmentForm.payment_method} onValueChange={(value) => setInvestmentForm({...investmentForm, payment_method: value})}>
                        <SelectTrigger className="mt-1 bg-slate-700 border-slate-600 text-white">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent className="bg-slate-700 border-slate-600">
                          <SelectItem value="fiat" className="text-white">💳 FIAT (Bank Wire)</SelectItem>
                          <SelectItem value="crypto" className="text-white">₿ Crypto Currency</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    {investmentForm.payment_method === "fiat" && (
                      <>
                        <div>
                          <Label className="text-slate-300">Wire Confirmation Number *</Label>
                          <Input
                            type="text"
                            value={investmentForm.wire_confirmation_number}
                            onChange={(e) => setInvestmentForm({...investmentForm, wire_confirmation_number: e.target.value})}
                            placeholder="Enter wire confirmation number"
                            className="mt-1 bg-slate-700 border-slate-600 text-white"
                          />
                        </div>
                        
                        <div>
                          <Label className="text-slate-300">Bank Reference (Optional)</Label>
                          <Input
                            type="text"
                            value={investmentForm.bank_reference}
                            onChange={(e) => setInvestmentForm({...investmentForm, bank_reference: e.target.value})}
                            placeholder="Bank reference number"
                            className="mt-1 bg-slate-700 border-slate-600 text-white"
                          />
                        </div>
                      </>
                    )}

                    {investmentForm.payment_method === "crypto" && (
                      <>
                        <div>
                          <Label className="text-slate-300">Transaction Hash *</Label>
                          <Input
                            type="text"
                            value={investmentForm.transaction_hash}
                            onChange={(e) => setInvestmentForm({...investmentForm, transaction_hash: e.target.value})}
                            placeholder="Enter blockchain transaction hash"
                            className="mt-1 bg-slate-700 border-slate-600 text-white"
                          />
                        </div>
                        
                        <div>
                          <Label className="text-slate-300">Blockchain Network (Optional)</Label>
                          <Input
                            type="text"
                            value={investmentForm.blockchain_network}
                            onChange={(e) => setInvestmentForm({...investmentForm, blockchain_network: e.target.value})}
                            placeholder="e.g., Bitcoin, Ethereum, BSC"
                            className="mt-1 bg-slate-700 border-slate-600 text-white"
                          />
                        </div>
                        
                        <div>
                          <Label className="text-slate-300">Wallet Address (Optional)</Label>
                          <Input
                            type="text"
                            value={investmentForm.wallet_address}
                            onChange={(e) => setInvestmentForm({...investmentForm, wallet_address: e.target.value})}
                            placeholder="Client's wallet address"
                            className="mt-1 bg-slate-700 border-slate-600 text-white"
                          />
                        </div>
                      </>
                    )}

                    <div>
                      <Label className="text-slate-300">Payment Notes (Optional)</Label>
                      <textarea
                        value={investmentForm.payment_notes}
                        onChange={(e) => setInvestmentForm({...investmentForm, payment_notes: e.target.value})}
                        placeholder="Additional notes about the payment..."
                        className="mt-1 w-full min-h-16 px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-white resize-none"
                      />
                    </div>

                    <div className="bg-green-900/20 border border-green-600 rounded-lg p-3">
                      <div className="flex items-start">
                        <CheckCircle className="h-5 w-5 text-green-400 mr-2 mt-0.5" />
                        <div className="text-sm text-green-300">
                          <p className="font-medium mb-1">Payment Confirmation Required</p>
                          <p>Confirming payment receipt will complete the investment creation process and start the timeline calculations.</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Fixed Footer with buttons */}
              <div className="p-6 border-t border-slate-600 bg-slate-800 rounded-b-lg">
                <div className="flex gap-3">
                  <Button
                    variant="outline"
                    onClick={() => {
                      setShowCreateInvestmentModal(false);
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
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default AdminInvestmentManagement;