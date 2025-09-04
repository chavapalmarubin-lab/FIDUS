import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { Badge } from "./ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  Users, 
  PieChart, 
  Activity, 
  ArrowUpRight, 
  ArrowDownRight,
  RefreshCw,
  Eye,
  Briefcase,
  Target,
  Clock,
  BarChart3,
  Database,
  ArrowLeft
} from "lucide-react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart as RechartsPieChart, Cell, BarChart, Bar, Pie } from "recharts";
import axios from "axios";
import { format } from "date-fns";
import FundInvestorsDetail from "./FundInvestorsDetail";
import ClientDetailedProfile from "./ClientDetailedProfile";
import MetaQuotesData from "./MetaQuotesData";
import ProspectManagement from "./ProspectManagement";

const CRMDashboard = ({ user }) => {
  const [crmData, setCrmData] = useState(null);
  const [selectedClient, setSelectedClient] = useState("");
  const [clientMT5Data, setClientMT5Data] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [currentView, setCurrentView] = useState('dashboard'); // dashboard, fund-investors, client-profile, all-clients
  const [selectedFund, setSelectedFund] = useState(null);
  const [selectedClientProfile, setSelectedClientProfile] = useState(null);
  const [allClientsData, setAllClientsData] = useState(null);

  const backendUrl = process.env.REACT_APP_BACKEND_URL;

  useEffect(() => {
    fetchCRMData();
  }, []);

  const fetchCRMData = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${backendUrl}/api/crm/admin/dashboard`);
      setCrmData(response.data);
    } catch (error) {
      console.error('Error fetching CRM data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchClientMT5Data = async (clientId) => {
    try {
      setRefreshing(true);
      
      // Fetch account, positions, and history
      const [accountRes, positionsRes, historyRes] = await Promise.all([
        axios.get(`${backendUrl}/api/crm/mt5/client/${clientId}/account`),
        axios.get(`${backendUrl}/api/crm/mt5/client/${clientId}/positions`),
        axios.get(`${backendUrl}/api/crm/mt5/client/${clientId}/history?days=30`)
      ]);

      setClientMT5Data({
        account: accountRes.data.account,
        positions: positionsRes.data,
        history: historyRes.data
      });
    } catch (error) {
      console.error('Error fetching client MT5 data:', error);
    } finally {
      setRefreshing(false);
    }
  };

  const handleViewFundInvestors = (fund) => {
    setSelectedFund(fund);
    setCurrentView('fund-investors');
  };

  const handleViewClientProfile = (clientId, clientName) => {
    setSelectedClientProfile({ clientId, clientName });
    setCurrentView('client-profile');
  };

  const handleViewAllClients = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${backendUrl}/api/crm/clients/all-details`);
      setAllClientsData(response.data);
      setCurrentView('all-clients');
    } catch (error) {
      console.error('Error fetching all clients:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleBackToDashboard = () => {
    setCurrentView('dashboard');
    setSelectedFund(null);
    setSelectedClientProfile(null);
    setAllClientsData(null);
    setSelectedClient("");
    setClientMT5Data(null);
  };

  const handleClientSelect = (clientId) => {
    setSelectedClient(clientId);
    if (clientId && clientId !== "all_clients") {
      fetchClientMT5Data(clientId);
    } else {
      setClientMT5Data(null);
    }
  };

  const handleRefresh = () => {
    fetchCRMData();
    if (selectedClient) {
      fetchClientMT5Data(selectedClient);
    }
  };

  if (currentView === 'fund-investors' && selectedFund) {
    return (
      <FundInvestorsDetail
        fundId={selectedFund.id}
        fundName={selectedFund.name}
        onBack={handleBackToDashboard}
      />
    );
  }

  if (currentView === 'client-profile' && selectedClientProfile) {
    return (
      <ClientDetailedProfile
        clientId={selectedClientProfile.clientId}
        clientName={selectedClientProfile.clientName}
        onBack={handleBackToDashboard}
      />
    );
  }

  if (currentView === 'all-clients' && allClientsData) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Button
              variant="outline"
              onClick={handleBackToDashboard}
              className="border-slate-600 text-slate-300 hover:bg-slate-700"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to CRM Dashboard
            </Button>
            <div>
              <h2 className="text-2xl font-bold text-white">All Clients Details</h2>
              <p className="text-gray-400">Comprehensive client information and portfolios</p>
            </div>
          </div>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card className="bg-slate-800 border-slate-700">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-400">Total Clients</p>
                  <p className="text-2xl font-bold text-white">{allClientsData.summary.total_clients}</p>
                </div>
                <div className="h-12 w-12 bg-cyan-600/20 rounded-lg flex items-center justify-center">
                  <Users className="h-6 w-6 text-cyan-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-slate-800 border-slate-700">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-400">Total Assets</p>
                  <p className="text-2xl font-bold text-white">{formatCurrency(allClientsData.summary.total_assets)}</p>
                </div>
                <div className="h-12 w-12 bg-green-600/20 rounded-lg flex items-center justify-center">
                  <DollarSign className="h-6 w-6 text-green-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-slate-800 border-slate-700">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-400">Fund Assets</p>
                  <p className="text-2xl font-bold text-white">{formatCurrency(allClientsData.summary.total_fund_assets)}</p>
                </div>
                <div className="h-12 w-12 bg-blue-600/20 rounded-lg flex items-center justify-center">
                  <Briefcase className="h-6 w-6 text-blue-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-slate-800 border-slate-700">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-400">Trading Assets</p>
                  <p className="text-2xl font-bold text-white">{formatCurrency(allClientsData.summary.total_trading_assets)}</p>
                </div>
                <div className="h-12 w-12 bg-yellow-600/20 rounded-lg flex items-center justify-center">
                  <Activity className="h-6 w-6 text-yellow-600" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Clients Table */}
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white">Client Details</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-600">
                    <th className="text-left py-3 px-4 text-gray-400 font-medium">Client</th>
                    <th className="text-right py-3 px-4 text-gray-400 font-medium">Total Assets</th>
                    <th className="text-right py-3 px-4 text-gray-400 font-medium">Fund Portfolio</th>
                    <th className="text-right py-3 px-4 text-gray-400 font-medium">Trading Balance</th>
                    <th className="text-right py-3 px-4 text-gray-400 font-medium">Open Positions</th>
                    <th className="text-right py-3 px-4 text-gray-400 font-medium">Recent Activity</th>
                    <th className="text-center py-3 px-4 text-gray-400 font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {(allClientsData?.clients || []).map((client) => (
                    <tr key={client.client_id} className="border-b border-slate-700 hover:bg-slate-700/50">
                      <td className="py-3 px-4">
                        <div>
                          <div className="font-medium text-white">{client.name}</div>
                          <div className="text-xs text-gray-400">{client.email}</div>
                        </div>
                      </td>
                      <td className="text-right py-3 px-4 text-white font-medium">
                        {formatCurrency(client.total_assets)}
                      </td>
                      <td className="text-right py-3 px-4 text-white">
                        {formatCurrency(client.fund_portfolio.total_value)}
                        <div className="text-xs text-gray-400">{client.fund_portfolio.number_of_funds} funds</div>
                      </td>
                      <td className="text-right py-3 px-4 text-white">
                        {formatCurrency(client.trading_account.balance)}
                      </td>
                      <td className="text-right py-3 px-4 text-white">
                        {client.trading_account.open_positions}
                      </td>
                      <td className="text-right py-3 px-4 text-gray-400">
                        {client.recent_activity.last_capital_flow 
                          ? format(new Date(client.recent_activity.last_capital_flow), 'MMM dd')
                          : 'No recent activity'
                        }
                      </td>
                      <td className="text-center py-3 px-4">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleViewClientProfile(client.client_id, client.name)}
                          className="border-slate-600 text-slate-300 hover:bg-slate-700"
                        >
                          <Eye className="h-4 w-4" />
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-600"></div>
      </div>
    );
  }

  if (!crmData) {
    return (
      <div className="text-center text-gray-400 py-8">
        Failed to load CRM data. Please try again.
      </div>
    );
  }

  const fundColors = ['#06b6d4', '#10b981', '#f59e0b', '#ef4444'];
  
  // Format currency
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  // Prepare chart data
  const fundPerformanceData = (crmData?.funds?.data || []).map((fund, index) => ({
    name: fund.name,
    ytd: fund.performance_ytd,
    '1y': fund.performance_1y,
    '3y': fund.performance_3y,
    aum: fund.aum,
    color: fundColors[index]
  }));

  const fundAllocationData = (crmData?.funds?.data || []).map((fund, index) => ({
    name: fund.name,
    value: fund.aum,
    percentage: ((fund.aum / crmData.funds.summary.total_aum) * 100).toFixed(1),
    color: fundColors[index]
  }));

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-white mb-2">CRM Dashboard</h2>
          <p className="text-gray-400">Comprehensive fund management and client monitoring</p>
        </div>
        <Button
          onClick={handleRefresh}
          disabled={refreshing}
          className="bg-cyan-600 hover:bg-cyan-700"
        >
          <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="bg-slate-800 border-slate-700">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-400">Total Client Assets</p>
                <p className="text-2xl font-bold text-white">
                  {formatCurrency(crmData.overview.total_client_assets)}
                </p>
              </div>
              <div className="h-12 w-12 bg-cyan-600/20 rounded-lg flex items-center justify-center">
                <DollarSign className="h-6 w-6 text-cyan-600" />
              </div>
            </div>
            <div className="mt-4 flex items-center text-sm">
              <Badge variant="secondary" className="bg-cyan-600/20 text-cyan-400">
                Fund: {crmData.overview.fund_assets_percentage}% | Trading: {crmData.overview.trading_assets_percentage}%
              </Badge>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-slate-800 border-slate-700">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-400">Fund AUM</p>
                <p className="text-2xl font-bold text-white">
                  {formatCurrency(crmData.funds.summary.total_aum)}
                </p>
              </div>
              <div className="h-12 w-12 bg-green-600/20 rounded-lg flex items-center justify-center">
                <Briefcase className="h-6 w-6 text-green-600" />
              </div>
            </div>
            <div className="mt-4 flex items-center text-sm">
              <span className="text-gray-400">{crmData.funds.summary.total_funds} Funds</span>
              <span className="mx-2 text-gray-600">•</span>
              <span className="text-gray-400">{crmData.funds.summary.total_investors} Investors</span>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-slate-800 border-slate-700">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-400">Trading Balance</p>
                <p className="text-2xl font-bold text-white">
                  {formatCurrency(crmData.trading.summary.total_balance)}
                </p>
              </div>
              <div className="h-12 w-12 bg-yellow-600/20 rounded-lg flex items-center justify-center">
                <Activity className="h-6 w-6 text-yellow-600" />
              </div>
            </div>
            <div className="mt-4 flex items-center text-sm">
              <span className="text-gray-400">{crmData.trading.summary.total_positions} Open Positions</span>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-slate-800 border-slate-700">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-400">Recent Net Flow</p>
                <p className="text-2xl font-bold text-white">
                  {formatCurrency(crmData.capital_flows.summary.net_flow)}
                </p>
              </div>
              <div className="h-12 w-12 bg-purple-600/20 rounded-lg flex items-center justify-center">
                {crmData.capital_flows.summary.net_flow >= 0 ? (
                  <ArrowUpRight className="h-6 w-6 text-green-600" />
                ) : (
                  <ArrowDownRight className="h-6 w-6 text-red-600" />
                )}
              </div>
            </div>
            <div className="mt-4 flex items-center text-sm">
              <span className="text-gray-400">{crmData.capital_flows.summary.total_recent_flows} Recent Flows</span>
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="prospects" className="w-full">
        <TabsList className="grid w-full grid-cols-5 bg-slate-800 border-slate-600">
          <TabsTrigger value="prospects" className="data-[state=active]:bg-cyan-600">
            <Users className="h-4 w-4 mr-2" />
            Prospects
          </TabsTrigger>
          <TabsTrigger value="funds" className="data-[state=active]:bg-cyan-600">
            <PieChart className="h-4 w-4 mr-2" />
            Fund Management
          </TabsTrigger>
          <TabsTrigger value="trading" className="data-[state=active]:bg-cyan-600">
            <Activity className="h-4 w-4 mr-2" />
            Trading Monitor
          </TabsTrigger>
          <TabsTrigger value="flows" className="data-[state=active]:bg-cyan-600">
            <BarChart3 className="h-4 w-4 mr-2" />
            Capital Flows
          </TabsTrigger>
          <TabsTrigger value="metaquotes" className="data-[state=active]:bg-cyan-600">
            <Database className="h-4 w-4 mr-2" />
            MetaQuotes Data
          </TabsTrigger>
        </TabsList>

        <TabsContent value="prospects" className="mt-6">
          <ProspectManagement />
        </TabsContent>

        <TabsContent value="funds" className="mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Fund Performance Chart */}
            <Card className="bg-slate-800 border-slate-700">
              <CardHeader>
                <CardTitle className="text-white">Fund Performance</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={fundPerformanceData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis dataKey="name" stroke="#9CA3AF" />
                    <YAxis stroke="#9CA3AF" />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: '#1F2937', 
                        border: '1px solid #374151',
                        borderRadius: '8px'
                      }}
                    />
                    <Legend />
                    <Bar dataKey="ytd" name="YTD %" fill="#06b6d4" />
                    <Bar dataKey="1y" name="1Y %" fill="#10b981" />
                    <Bar dataKey="3y" name="3Y %" fill="#f59e0b" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Fund Allocation Pie Chart */}
            <Card className="bg-slate-800 border-slate-700">
              <CardHeader>
                <CardTitle className="text-white">AUM Distribution</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <RechartsPieChart>
                    <Pie
                      data={fundAllocationData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={120}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {fundAllocationData.map((entry, index) => (
                        <Cell key={`crm-cell-${index}-${entry.name}-${entry.value}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip 
                      formatter={(value) => [formatCurrency(value), 'AUM']}
                      contentStyle={{ 
                        backgroundColor: '#1F2937', 
                        border: '1px solid #374151',
                        borderRadius: '8px'
                      }}
                    />
                    <Legend />
                  </RechartsPieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          {/* Fund Details Table */}
          <Card className="bg-slate-800 border-slate-700 mt-6">
            <CardHeader>
              <CardTitle className="text-white">Fund Details</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-slate-600">
                      <th className="text-left py-3 px-4 text-gray-400 font-medium">Fund</th>
                      <th className="text-right py-3 px-4 text-gray-400 font-medium">AUM</th>
                      <th className="text-right py-3 px-4 text-gray-400 font-medium">NAV/Share</th>
                      <th className="text-right py-3 px-4 text-gray-400 font-medium">YTD</th>
                      <th className="text-right py-3 px-4 text-gray-400 font-medium">Investors</th>
                      <th className="text-right py-3 px-4 text-gray-400 font-medium">Min Investment</th>
                      <th className="text-center py-3 px-4 text-gray-400 font-medium">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(crmData?.funds?.data || []).map((fund, index) => (
                      <tr key={fund.id} className="border-b border-slate-700 hover:bg-slate-700/50">
                        <td className="py-3 px-4">
                          <div className="flex items-center space-x-3">
                            <div className={`w-3 h-3 rounded-full`} style={{ backgroundColor: fundColors[index] }}></div>
                            <div>
                              <div className="font-medium text-white">{fund.name}</div>
                              <div className="text-xs text-gray-400">{fund.fund_type}</div>
                            </div>
                          </div>
                        </td>
                        <td className="text-right py-3 px-4 text-white font-medium">
                          {formatCurrency(fund.aum)}
                        </td>
                        <td className="text-right py-3 px-4 text-white">
                          ${fund.nav_per_share.toFixed(2)}
                        </td>
                        <td className="text-right py-3 px-4">
                          <span className={`font-medium ${fund.performance_ytd >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                            {fund.performance_ytd >= 0 ? '+' : ''}{fund.performance_ytd.toFixed(1)}%
                          </span>
                        </td>
                        <td className="text-right py-3 px-4 text-white">
                          <Button
                            variant="link"
                            onClick={() => handleViewFundInvestors(fund)}
                            className="text-cyan-400 hover:text-cyan-300 p-0 h-auto font-medium"
                          >
                            {fund.total_investors}
                          </Button>
                        </td>
                        <td className="text-right py-3 px-4 text-gray-400">
                          {formatCurrency(fund.minimum_investment)}
                        </td>
                        <td className="text-center py-3 px-4">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleViewFundInvestors(fund)}
                            className="border-slate-600 text-slate-300 hover:bg-slate-700"
                          >
                            <Eye className="h-4 w-4 mr-1" />
                            View
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="trading" className="mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Client Selection */}
            <Card className="bg-slate-800 border-slate-700">
              <CardHeader>
                <CardTitle className="text-white">Client Monitor</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <Label className="text-gray-400">Select Client</Label>
                    <Select value={selectedClient} onValueChange={handleClientSelect}>
                      <SelectTrigger className="bg-slate-700 border-slate-600 text-white">
                        <SelectValue placeholder="Choose client to monitor" />
                      </SelectTrigger>
                      <SelectContent className="bg-slate-700 border-slate-600">
                        <SelectItem value="all_clients">All Clients Overview</SelectItem>
                        {(crmData?.trading?.clients || []).map((client) => (
                          <SelectItem key={client.client_id} value={client.client_id}>
                            {client.client_name} - {client.account_number}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Trading Summary */}
            <Card className="bg-slate-800 border-slate-700 lg:col-span-2">
              <CardHeader>
                <CardTitle className="text-white">Trading Overview</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-white">
                      {crmData.trading.summary.total_clients}
                    </div>
                    <div className="text-sm text-gray-400">Active Accounts</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-white">
                      {formatCurrency(crmData.trading.summary.total_balance)}
                    </div>
                    <div className="text-sm text-gray-400">Total Balance</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-white">
                      {crmData.trading.summary.total_positions}
                    </div>
                    <div className="text-sm text-gray-400">Open Positions</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-white">
                      {formatCurrency(crmData.trading.summary.avg_balance_per_client)}
                    </div>
                    <div className="text-sm text-gray-400">Avg Balance</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Client Detail View */}
          {selectedClient && selectedClient !== "all_clients" && clientMT5Data && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
              {/* Account Info */}
              <Card className="bg-slate-800 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white">Account Information</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex justify-between">
                      <span className="text-gray-400">Account Number:</span>
                      <span className="text-white font-medium">{clientMT5Data.account.account_number}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Balance:</span>
                      <span className="text-white font-medium">{formatCurrency(clientMT5Data.account.balance)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Equity:</span>
                      <span className="text-white font-medium">{formatCurrency(clientMT5Data.account.equity)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Margin:</span>
                      <span className="text-white font-medium">{formatCurrency(clientMT5Data.account.margin)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Free Margin:</span>
                      <span className="text-white font-medium">{formatCurrency(clientMT5Data.account.free_margin)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Leverage:</span>
                      <span className="text-white font-medium">1:{clientMT5Data.account.leverage}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Recent Positions */}
              <Card className="bg-slate-800 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white">Open Positions ({clientMT5Data.positions.summary.total_positions})</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3 max-h-64 overflow-y-auto">
                    {clientMT5Data.positions.positions.map((position) => (
                      <div key={position.ticket} className="flex justify-between items-center p-3 bg-slate-700/50 rounded-lg">
                        <div>
                          <div className="font-medium text-white">{position.symbol}</div>
                          <div className="text-sm text-gray-400">
                            {position.type.toUpperCase()} {position.volume}
                          </div>
                        </div>
                        <div className="text-right">
                          <div className={`font-medium ${position.profit >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                            {position.profit >= 0 ? '+' : ''}${position.profit.toFixed(2)}
                          </div>
                          <div className="text-sm text-gray-400">
                            {position.current_price}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                  <div className="mt-4 pt-4 border-t border-slate-600">
                    <div className="flex justify-between">
                      <span className="text-gray-400">Total P&L:</span>
                      <span className={`font-medium ${clientMT5Data.positions.summary.total_profit >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                        {clientMT5Data.positions.summary.total_profit >= 0 ? '+' : ''}${clientMT5Data.positions.summary.total_profit.toFixed(2)}
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* All Clients Table */}
          {(!selectedClient || selectedClient === "all_clients") && (
            <Card className="bg-slate-800 border-slate-700 mt-6">
              <CardHeader>
                <CardTitle className="text-white">All Trading Accounts</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-slate-600">
                        <th className="text-left py-3 px-4 text-gray-400 font-medium">Client</th>
                        <th className="text-right py-3 px-4 text-gray-400 font-medium">Account</th>
                        <th className="text-right py-3 px-4 text-gray-400 font-medium">Balance</th>
                        <th className="text-right py-3 px-4 text-gray-400 font-medium">Equity</th>
                        <th className="text-right py-3 px-4 text-gray-400 font-medium">Positions</th>
                        <th className="text-right py-3 px-4 text-gray-400 font-medium">Last Activity</th>
                        <th className="text-center py-3 px-4 text-gray-400 font-medium">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {crmData.trading.clients.map((client) => (
                        <tr key={client.client_id} className="border-b border-slate-700 hover:bg-slate-700/50">
                          <td className="py-3 px-4">
                            <div className="font-medium text-white">{client.client_name}</div>
                          </td>
                          <td className="text-right py-3 px-4 text-gray-400">
                            {client.account_number}
                          </td>
                          <td className="text-right py-3 px-4 text-white font-medium">
                            {formatCurrency(client.balance)}
                          </td>
                          <td className="text-right py-3 px-4 text-white">
                            {formatCurrency(client.equity)}
                          </td>
                          <td className="text-right py-3 px-4 text-white">
                            {client.open_positions}
                          </td>
                          <td className="text-right py-3 px-4 text-gray-400">
                            {format(new Date(client.last_activity), 'MMM dd, HH:mm')}
                          </td>
                          <td className="text-center py-3 px-4">
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleViewClientProfile(client.client_id, client.client_name)}
                              className="border-slate-600 text-slate-300 hover:bg-slate-700"
                            >
                              <Eye className="h-4 w-4" />
                            </Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="flows" className="mt-6">
          <Card className="bg-slate-800 border-slate-700">
            <CardHeader>
              <CardTitle className="text-white">Recent Capital Flows</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-slate-600">
                      <th className="text-left py-3 px-4 text-gray-400 font-medium">Date</th>
                      <th className="text-left py-3 px-4 text-gray-400 font-medium">Client</th>
                      <th className="text-left py-3 px-4 text-gray-400 font-medium">Fund</th>
                      <th className="text-left py-3 px-4 text-gray-400 font-medium">Type</th>
                      <th className="text-right py-3 px-4 text-gray-400 font-medium">Amount</th>
                      <th className="text-right py-3 px-4 text-gray-400 font-medium">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {crmData.capital_flows.recent_flows.map((flow) => (
                      <tr key={flow.id} className="border-b border-slate-700 hover:bg-slate-700/50">
                        <td className="py-3 px-4 text-gray-400">
                          {format(new Date(flow.trade_date), 'MMM dd, yyyy')}
                        </td>
                        <td className="py-3 px-4 text-white">
                          {/* Find client name from flow.client_id */}
                          Client {flow.client_id.slice(-4)}
                        </td>
                        <td className="py-3 px-4 text-white">
                          {flow.fund_name}
                        </td>
                        <td className="py-3 px-4">
                          <Badge 
                            variant="secondary" 
                            className={
                              flow.flow_type === 'subscription' 
                                ? 'bg-green-600/20 text-green-400' 
                                : flow.flow_type === 'redemption'
                                ? 'bg-red-600/20 text-red-400'
                                : 'bg-blue-600/20 text-blue-400'
                            }
                          >
                            {flow.flow_type.charAt(0).toUpperCase() + flow.flow_type.slice(1)}
                          </Badge>
                        </td>
                        <td className="text-right py-3 px-4 text-white font-medium">
                          {formatCurrency(flow.amount)}
                        </td>
                        <td className="text-right py-3 px-4">
                          <Badge 
                            variant="secondary" 
                            className={
                              flow.status === 'confirmed' 
                                ? 'bg-green-600/20 text-green-400' 
                                : flow.status === 'pending'
                                ? 'bg-yellow-600/20 text-yellow-400'
                                : 'bg-gray-600/20 text-gray-400'
                            }
                          >
                            {flow.status.charAt(0).toUpperCase() + flow.status.slice(1)}
                          </Badge>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="metaquotes" className="mt-6">
          <MetaQuotesData />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default CRMDashboard;