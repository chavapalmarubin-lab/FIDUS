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
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!profileData) {
    return (
      <div className="text-center py-8">
        <p className="text-slate-500">Failed to load client profile</p>
      </div>
    );
  }

  const fundColors = ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b'];
  
  const fundAllocationData = (profileData?.fund_portfolio?.allocations || []).map((allocation, index) => ({
    name: allocation.fund_code,
    value: allocation.amount,
    color: fundColors[index % fundColors.length]
  }));

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button 
          variant="ghost" 
          onClick={onBack}
          className="flex items-center gap-2 text-slate-600 hover:text-slate-900"
        >
          <ArrowLeft size={20} />
          Back to Clients
        </Button>
        <div>
          <h1 className="text-2xl font-bold text-slate-900">{clientName}</h1>
          <p className="text-slate-600">Client ID: {clientId}</p>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <DollarSign className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-slate-600">Total Portfolio</p>
                <p className="text-xl font-bold text-slate-900">
                  {formatCurrency(profileData.portfolio_summary.total_value)}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-100 rounded-lg">
                <TrendingUp className="h-5 w-5 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-slate-600">Total Gains</p>
                <p className="text-xl font-bold text-green-600">
                  {formatCurrency(profileData.portfolio_summary.total_gains)}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-purple-100 rounded-lg">
                <Activity className="h-5 w-5 text-purple-600" />
              </div>
              <div>
                <p className="text-sm text-slate-600">Active Funds</p>
                <p className="text-xl font-bold text-slate-900">
                  {profileData.portfolio_summary.active_funds}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className={`p-2 rounded-lg ${profileData.portfolio_summary.performance_ytd >= 0 ? 'bg-green-100' : 'bg-red-100'}`}>
                {profileData.portfolio_summary.performance_ytd >= 0 ? 
                  <TrendingUp className="h-5 w-5 text-green-600" /> : 
                  <TrendingDown className="h-5 w-5 text-red-600" />
                }
              </div>
              <div>
                <p className="text-sm text-slate-600">YTD Performance</p>
                <p className={`text-xl font-bold ${profileData.portfolio_summary.performance_ytd >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {profileData.portfolio_summary.performance_ytd >= 0 ? '+' : ''}{profileData.portfolio_summary.performance_ytd}%
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Content Tabs */}
      <Tabs defaultValue="portfolio" className="space-y-4">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="portfolio">Portfolio</TabsTrigger>
          <TabsTrigger value="trading">Trading</TabsTrigger>
          <TabsTrigger value="transactions">Transactions</TabsTrigger>
          <TabsTrigger value="documents">Documents</TabsTrigger>
        </TabsList>

        <TabsContent value="portfolio" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Fund Allocation Chart */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <PieChart size={20} />
                  Fund Allocation
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <RechartsPieChart>
                      <Pie
                        data={fundAllocationData}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={100}
                        paddingAngle={5}
                        dataKey="value"
                      >
                        {(fundAllocationData || []).map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip formatter={(value) => formatCurrency(value)} />
                      <Legend />
                    </RechartsPieChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            {/* Fund Breakdown */}
            <Card>
              <CardHeader>
                <CardTitle>Fund Breakdown</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {(profileData?.fund_portfolio?.allocations || []).map((allocation, index) => (
                    <div key={allocation.fund_code} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                      <div className="flex items-center gap-3">
                        <div 
                          className="w-4 h-4 rounded-full" 
                          style={{ backgroundColor: fundColors[index % fundColors.length] }}
                        ></div>
                        <div>
                          <p className="font-medium text-slate-900">{allocation.fund_name}</p>
                          <p className="text-sm text-slate-600">{allocation.fund_code}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-bold text-slate-900">{formatCurrency(allocation.amount)}</p>
                        <p className="text-sm text-slate-600">{allocation.percentage}%</p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Performance Chart */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 size={20} />
                Portfolio Performance (Last 12 Months)
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={profileData.performance_history || []}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip formatter={(value) => formatCurrency(value)} />
                    <Legend />
                    <Line 
                      type="monotone" 
                      dataKey="portfolio_value" 
                      stroke="#3b82f6" 
                      strokeWidth={2}
                      name="Portfolio Value"
                    />
                    <Line 
                      type="monotone" 
                      dataKey="gains" 
                      stroke="#10b981" 
                      strokeWidth={2}
                      name="Gains"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="trading" className="space-y-6">
          {/* Trading Account Summary */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardContent className="p-4">
                <div className="text-center">
                  <p className="text-sm text-slate-600 mb-1">Account Balance</p>
                  <p className="text-2xl font-bold text-slate-900">
                    {formatCurrency(profileData.trading_account?.balance || 0)}
                  </p>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4">
                <div className="text-center">
                  <p className="text-sm text-slate-600 mb-1">Equity</p>
                  <p className="text-2xl font-bold text-slate-900">
                    {formatCurrency(profileData.trading_account?.equity || 0)}
                  </p>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4">
                <div className="text-center">
                  <p className="text-sm text-slate-600 mb-1">Free Margin</p>
                  <p className="text-2xl font-bold text-slate-900">
                    {formatCurrency(profileData.trading_account?.free_margin || 0)}
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Current Positions */}
          <Card>
            <CardHeader>
              <CardTitle>Current Positions</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {(profileData?.trading_account?.positions?.data || []).slice(0, 10).map((position) => (
                  <div key={position.ticket} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <Badge variant={position.type === 'buy' ? 'default' : 'secondary'}>
                        {position.type.toUpperCase()}
                      </Badge>
                      <div>
                        <p className="font-medium text-slate-900">{position.symbol}</p>
                        <p className="text-sm text-slate-600">Volume: {position.volume}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-medium text-slate-900">{formatCurrency(position.profit)}</p>
                      <p className={`text-sm ${position.profit >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {position.profit >= 0 ? '+' : ''}{((position.profit / position.volume) * 100).toFixed(2)}%
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="transactions" className="space-y-6">
          {/* Recent Capital Flows */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity size={20} />
                Recent Capital Flows
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {(profileData?.capital_flows?.recent_flows || []).map((flow) => (
                  <div key={flow.id} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className={`p-2 rounded-lg ${flow.type === 'deposit' ? 'bg-green-100' : 'bg-red-100'}`}>
                        {flow.type === 'deposit' ? 
                          <ArrowDownLeft className="h-4 w-4 text-green-600" /> : 
                          <ArrowUpRight className="h-4 w-4 text-red-600" />
                        }
                      </div>
                      <div>
                        <p className="font-medium text-slate-900 capitalize">{flow.type}</p>
                        <p className="text-sm text-slate-600">
                          {format(new Date(flow.date), 'MMM dd, yyyy')}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className={`font-bold ${flow.type === 'deposit' ? 'text-green-600' : 'text-red-600'}`}>
                        {flow.type === 'deposit' ? '+' : '-'}{formatCurrency(flow.amount)}
                      </p>
                      <p className="text-sm text-slate-600">{flow.fund_code}</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="documents" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Client Documents</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <p className="text-slate-500">Document management integration coming soon</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default ClientDetailedProfile;