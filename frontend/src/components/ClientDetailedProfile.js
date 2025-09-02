import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { 
  ArrowLeft, 
  User, 
  DollarSign, 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  Calendar,
  PieChart,
  BarChart3,
  ArrowUpRight,
  ArrowDownLeft
} from "lucide-react";
import axios from "axios";
import { format } from "date-fns";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart as RechartsPieChart, Cell } from "recharts";

const ClientDetailedProfile = ({ clientId, clientName, onBack }) => {
  const [profileData, setProfileData] = useState(null);
  const [loading, setLoading] = useState(true);

  const backendUrl = process.env.REACT_APP_BACKEND_URL;

  useEffect(() => {
    fetchClientProfile();
  }, [clientId]);

  const fetchClientProfile = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${backendUrl}/api/crm/client/${clientId}/profile`);
      setProfileData(response.data);
    } catch (error) {
      console.error('Error fetching client profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-600"></div>
      </div>
    );
  }

  if (!profileData) {
    return (
      <div className="text-center text-gray-400 py-8">
        Failed to load client profile. Please try again.
      </div>
    );
  }

  const fundColors = ['#06b6d4', '#10b981', '#f59e0b', '#ef4444'];
  
  // Prepare chart data
  const fundAllocationData = profileData.fund_portfolio.allocations.map((allocation, index) => ({
    name: allocation.fund_name,
    value: allocation.current_value,
    percentage: allocation.allocation_percentage,
    color: fundColors[index % fundColors.length]
  }));

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button
            variant="outline"
            onClick={onBack}
            className="border-slate-600 text-slate-300 hover:bg-slate-700"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
          <div>
            <h2 className="text-2xl font-bold text-white">{profileData.client_info.name}</h2>
            <p className="text-gray-400">Client Profile & Portfolio Overview</p>
          </div>
        </div>
        <Badge className="bg-green-600/20 text-green-400">
          {profileData.client_info.status}
        </Badge>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="bg-slate-800 border-slate-700">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-400">Total Assets</p>
                <p className="text-2xl font-bold text-white">{formatCurrency(profileData.total_assets)}</p>
              </div>
              <div className="h-12 w-12 bg-cyan-600/20 rounded-lg flex items-center justify-center">
                <DollarSign className="h-6 w-6 text-cyan-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-slate-800 border-slate-700">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-400">Fund Portfolio</p>
                <p className="text-2xl font-bold text-white">{formatCurrency(profileData.fund_portfolio.total_value)}</p>
              </div>
              <div className="h-12 w-12 bg-green-600/20 rounded-lg flex items-center justify-center">
                <PieChart className="h-6 w-6 text-green-600" />
              </div>
            </div>
            <div className="mt-2">
              <span className="text-sm text-gray-400">{profileData.fund_portfolio.number_of_funds} Funds</span>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-slate-800 border-slate-700">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-400">Trading Balance</p>
                <p className="text-2xl font-bold text-white">
                  {formatCurrency(profileData.trading_account.account_info?.balance || 0)}
                </p>
              </div>
              <div className="h-12 w-12 bg-yellow-600/20 rounded-lg flex items-center justify-center">
                <Activity className="h-6 w-6 text-yellow-600" />
              </div>
            </div>
            <div className="mt-2">
              <span className="text-sm text-gray-400">
                {profileData.trading_account.positions.summary.total_positions} Open Positions
              </span>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-slate-800 border-slate-700">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-400">Trading P&L</p>
                <p className={`text-2xl font-bold ${profileData.trading_account.positions.summary.total_profit >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {profileData.trading_account.positions.summary.total_profit >= 0 ? '+' : ''}
                  {formatCurrency(profileData.trading_account.positions.summary.total_profit)}
                </p>
              </div>
              <div className="h-12 w-12 bg-purple-600/20 rounded-lg flex items-center justify-center">
                {profileData.trading_account.positions.summary.total_profit >= 0 ? (
                  <TrendingUp className="h-6 w-6 text-green-600" />
                ) : (
                  <TrendingDown className="h-6 w-6 text-red-600" />
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs defaultValue="overview" className="w-full">
        <TabsList className="grid w-full grid-cols-4 bg-slate-800 border-slate-600">
          <TabsTrigger value="overview" className="data-[state=active]:bg-cyan-600">
            Overview
          </TabsTrigger>
          <TabsTrigger value="funds" className="data-[state=active]:bg-cyan-600">
            Fund Portfolio
          </TabsTrigger>
          <TabsTrigger value="trading" className="data-[state=active]:bg-cyan-600">
            Trading Account
          </TabsTrigger>
          <TabsTrigger value="flows" className="data-[state=active]:bg-cyan-600">
            Capital Flows
          </TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Client Information */}
            <Card className="bg-slate-800 border-slate-700">
              <CardHeader>
                <CardTitle className="text-white flex items-center">
                  <User className="h-5 w-5 mr-2" />
                  Client Information
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-400">Full Name</p>
                    <p className="text-white font-medium">{profileData.client_info.name}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-400">Email</p>
                    <p className="text-white">{profileData.client_info.email}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-400">Client ID</p>
                    <p className="text-white font-mono">{profileData.client_info.client_id}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-400">Status</p>
                    <Badge className="bg-green-600/20 text-green-400">{profileData.client_info.status}</Badge>
                  </div>
                  <div>
                    <p className="text-sm text-gray-400">Risk Tolerance</p>
                    <p className="text-white">{profileData.client_info.risk_tolerance}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-400">Join Date</p>
                    <p className="text-white">{profileData.client_info.join_date}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Asset Allocation Chart */}
            <Card className="bg-slate-800 border-slate-700">
              <CardHeader>
                <CardTitle className="text-white">Asset Allocation</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <RechartsPieChart>
                    <Pie
                      data={[
                        { name: 'Fund Portfolio', value: profileData.fund_portfolio.total_value, color: '#06b6d4' },
                        { name: 'Trading Account', value: profileData.trading_account.account_info?.balance || 0, color: '#10b981' }
                      ]}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={120}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      <Cell fill="#06b6d4" />
                      <Cell fill="#10b981" />
                    </Pie>
                    <Tooltip 
                      formatter={(value) => [formatCurrency(value), 'Value']}
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
        </TabsContent>

        <TabsContent value="funds" className="mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Fund Allocation Chart */}
            <Card className="bg-slate-800 border-slate-700">
              <CardHeader>
                <CardTitle className="text-white">Fund Allocation</CardTitle>
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
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip 
                      formatter={(value) => [formatCurrency(value), 'Value']}
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

            {/* Fund Details */}
            <Card className="bg-slate-800 border-slate-700">
              <CardHeader>
                <CardTitle className="text-white">Fund Details</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {profileData.fund_portfolio.allocations.map((allocation, index) => (
                    <div key={allocation.fund_name} className="p-4 bg-slate-700/50 rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center space-x-3">
                          <div 
                            className="w-3 h-3 rounded-full"
                            style={{ backgroundColor: fundColors[index % fundColors.length] }}
                          ></div>
                          <span className="font-medium text-white">{allocation.fund_name}</span>
                        </div>
                        <Badge variant="secondary" className="bg-slate-600 text-slate-200">
                          {allocation.allocation_percentage.toFixed(1)}%
                        </Badge>
                      </div>
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <p className="text-gray-400">Invested</p>
                          <p className="text-white font-medium">{formatCurrency(allocation.invested_amount)}</p>
                        </div>
                        <div>
                          <p className="text-gray-400">Current Value</p>
                          <p className="text-white font-medium">{formatCurrency(allocation.current_value)}</p>
                        </div>
                        <div>
                          <p className="text-gray-400">P&L</p>
                          <p className={`font-medium ${allocation.total_pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                            {allocation.total_pnl >= 0 ? '+' : ''}{formatCurrency(allocation.total_pnl)}
                          </p>
                        </div>
                        <div>
                          <p className="text-gray-400">P&L %</p>
                          <p className={`font-medium ${allocation.pnl_percentage >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                            {allocation.pnl_percentage >= 0 ? '+' : ''}{allocation.pnl_percentage.toFixed(2)}%
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="trading" className="mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Account Info */}
            <Card className="bg-slate-800 border-slate-700">
              <CardHeader>
                <CardTitle className="text-white">Trading Account Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-400">Account Number</p>
                    <p className="text-white font-mono">{profileData.trading_account.account_info?.account_number || 'N/A'}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-400">Balance</p>
                    <p className="text-white font-medium">{formatCurrency(profileData.trading_account.account_info?.balance || 0)}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-400">Equity</p>
                    <p className="text-white font-medium">{formatCurrency(profileData.trading_account.account_info?.equity || 0)}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-400">Free Margin</p>
                    <p className="text-white font-medium">{formatCurrency(profileData.trading_account.account_info?.free_margin || 0)}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-400">Leverage</p>
                    <p className="text-white">1:{profileData.trading_account.account_info?.leverage || 'N/A'}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-400">Open Positions</p>
                    <p className="text-white">{profileData.trading_account.positions.summary.total_positions}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Trading Statistics */}
            <Card className="bg-slate-800 border-slate-700">
              <CardHeader>
                <CardTitle className="text-white">Trading Statistics (30 Days)</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-400">Total Trades</p>
                    <p className="text-white font-medium">{profileData.trading_account.recent_history.summary.total_trades}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-400">Total Profit</p>
                    <p className={`font-medium ${profileData.trading_account.recent_history.summary.total_profit >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {profileData.trading_account.recent_history.summary.total_profit >= 0 ? '+' : ''}
                      {formatCurrency(profileData.trading_account.recent_history.summary.total_profit)}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-400">Winning Trades</p>
                    <p className="text-green-400 font-medium">{profileData.trading_account.recent_history.summary.winning_trades}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-400">Losing Trades</p>
                    <p className="text-red-400 font-medium">{profileData.trading_account.recent_history.summary.losing_trades}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-400">Win Rate</p>
                    <p className="text-white font-medium">
                      {((profileData.trading_account.recent_history.summary.winning_trades / profileData.trading_account.recent_history.summary.total_trades) * 100).toFixed(1)}%
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-400">Current Positions P&L</p>
                    <p className={`font-medium ${profileData.trading_account.positions.summary.total_profit >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {profileData.trading_account.positions.summary.total_profit >= 0 ? '+' : ''}
                      {formatCurrency(profileData.trading_account.positions.summary.total_profit)}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Open Positions */}
          <Card className="bg-slate-800 border-slate-700 mt-6">
            <CardHeader>
              <CardTitle className="text-white">Open Positions</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-slate-600">
                      <th className="text-left py-2 text-gray-400">Symbol</th>
                      <th className="text-left py-2 text-gray-400">Type</th>
                      <th className="text-right py-2 text-gray-400">Volume</th>
                      <th className="text-right py-2 text-gray-400">Open Price</th>
                      <th className="text-right py-2 text-gray-400">Current Price</th>
                      <th className="text-right py-2 text-gray-400">P&L</th>
                    </tr>
                  </thead>
                  <tbody>
                    {profileData.trading_account.positions.data.slice(0, 10).map((position) => (
                      <tr key={position.ticket} className="border-b border-slate-700">
                        <td className="py-2 text-white font-medium">{position.symbol}</td>
                        <td className="py-2">
                          <Badge className={position.type === 'buy' ? 'bg-green-600/20 text-green-400' : 'bg-red-600/20 text-red-400'}>
                            {position.type.toUpperCase()}
                          </Badge>
                        </td>
                        <td className="text-right py-2 text-white">{position.volume}</td>
                        <td className="text-right py-2 text-white">{position.open_price}</td>
                        <td className="text-right py-2 text-white">{position.current_price}</td>
                        <td className={`text-right py-2 font-medium ${position.profit >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                          {position.profit >= 0 ? '+' : ''}${position.profit.toFixed(2)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="flows" className="mt-6">
          <Card className="bg-slate-800 border-slate-700">
            <CardHeader>
              <CardTitle className="text-white">Recent Capital Flows</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4 mb-6">
                <div className="grid grid-cols-3 gap-4">
                  <div className="text-center p-4 bg-green-600/10 rounded-lg">
                    <div className="flex items-center justify-center mb-2">
                      <ArrowUpRight className="h-5 w-5 text-green-400" />
                    </div>
                    <p className="text-sm text-gray-400">Subscriptions</p>
                    <p className="text-lg font-bold text-green-400">
                      {formatCurrency(profileData.capital_flows.summary.total_subscriptions)}
                    </p>
                  </div>
                  <div className="text-center p-4 bg-red-600/10 rounded-lg">
                    <div className="flex items-center justify-center mb-2">
                      <ArrowDownLeft className="h-5 w-5 text-red-400" />
                    </div>
                    <p className="text-sm text-gray-400">Redemptions</p>
                    <p className="text-lg font-bold text-red-400">
                      {formatCurrency(profileData.capital_flows.summary.total_redemptions)}
                    </p>
                  </div>
                  <div className="text-center p-4 bg-blue-600/10 rounded-lg">
                    <div className="flex items-center justify-center mb-2">
                      <DollarSign className="h-5 w-5 text-blue-400" />
                    </div>
                    <p className="text-sm text-gray-400">Distributions</p>
                    <p className="text-lg font-bold text-blue-400">
                      {formatCurrency(profileData.capital_flows.summary.total_distributions)}
                    </p>
                  </div>
                </div>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-slate-600">
                      <th className="text-left py-2 text-gray-400">Date</th>
                      <th className="text-left py-2 text-gray-400">Fund</th>
                      <th className="text-left py-2 text-gray-400">Type</th>
                      <th className="text-right py-2 text-gray-400">Amount</th>
                      <th className="text-left py-2 text-gray-400">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {profileData.capital_flows.recent_flows.map((flow) => (
                      <tr key={flow.id} className="border-b border-slate-700">
                        <td className="py-2 text-gray-400">
                          {format(new Date(flow.trade_date), 'MMM dd, yyyy')}
                        </td>
                        <td className="py-2 text-white">{flow.fund_name}</td>
                        <td className="py-2">
                          <Badge 
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
                        <td className="text-right py-2 text-white font-medium">
                          {formatCurrency(flow.amount)}
                        </td>
                        <td className="py-2">
                          <Badge 
                            className={
                              flow.status === 'confirmed' 
                                ? 'bg-green-600/20 text-green-400' 
                                : 'bg-yellow-600/20 text-yellow-400'
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
      </Tabs>
    </div>
  );
};

export default ClientDetailedProfile;