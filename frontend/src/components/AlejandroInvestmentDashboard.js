import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Tabs, TabsList, TabsTrigger, TabsContent } from './ui/tabs';
import { Badge } from './ui/badge';
import { Alert, AlertDescription } from './ui/alert';
import { Progress } from './ui/progress';
import {
  DollarSign,
  TrendingUp,
  Calendar,
  Building2,
  Shield,
  Activity,
  RefreshCw,
  Eye,
  ExternalLink,
  PieChart,
  BarChart3,
  Wallet,
  Target,
  Clock,
  CheckCircle,
  AlertCircle,
  Users,
  Globe
} from 'lucide-react';
import apiAxios from '../utils/apiAxios';

const AlejandroInvestmentDashboard = () => {
  const [loading, setLoading] = useState(true);
  const [clientData, setClientData] = useState(null);
  const [investments, setInvestments] = useState([]);
  const [mt5Accounts, setMt5Accounts] = useState([]);
  const [readiness, setReadiness] = useState(null);
  const [error, setError] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadAlejandroData();
  }, []);

  const loadAlejandroData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Load all Alejandro's data
      const [readinessRes, investmentsRes, mt5AccountsRes] = await Promise.allSettled([
        apiAxios.get('/api/clients/client_alejandro_mariscal/readiness'),
        apiAxios.get('/api/clients/client_alejandro_mariscal/investments'),
        apiAxios.get('/api/mt5/accounts/client_alejandro_mariscal')
      ]);

      if (readinessRes.status === 'fulfilled') {
        setReadiness(readinessRes.value.data.readiness);
        setClientData({
          client_id: 'client_alejandro_mariscal',
          name: 'Alejandro Mariscal',
          email: 'alexmar7609@gmail.com',
          username: 'alejandrom',
          type: 'client'
        });
      }

      if (investmentsRes.status === 'fulfilled') {
        setInvestments(investmentsRes.value.data.investments || []);
      }

      if (mt5AccountsRes.status === 'fulfilled') {
        setMt5Accounts(mt5AccountsRes.value.data.accounts || []);
      }

    } catch (err) {
      console.error('Error loading Alejandro data:', err);
      setError('Failed to load client data');
    } finally {
      setLoading(false);
    }
  };

  const refreshData = async () => {
    setRefreshing(true);
    await loadAlejandroData();
    setRefreshing(false);
  };

  const calculateTotalInvestment = () => {
    return investments.reduce((total, inv) => total + (inv.principal_amount || 0), 0);
  };

  const calculateCurrentValue = () => {
    return investments.reduce((total, inv) => total + (inv.current_value || 0), 0);
  };

  const getPerformanceColor = (amount) => {
    if (amount > 0) return 'text-green-600';
    if (amount < 0) return 'text-red-600';
    return 'text-gray-600';
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount || 0);
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="flex items-center space-x-2">
          <RefreshCw className="h-6 w-6 animate-spin" />
          <span>Loading Alejandro's portfolio...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <Alert className="m-4">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  const totalInvestment = calculateTotalInvestment();
  const currentValue = calculateCurrentValue();
  const totalReturn = currentValue - totalInvestment;
  const returnPercentage = totalInvestment > 0 ? ((totalReturn / totalInvestment) * 100) : 0;

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Alejandro Mariscal</h1>
          <p className="text-gray-600">First Production Client - Investment Portfolio</p>
        </div>
        <Button onClick={refreshData} disabled={refreshing} className="flex items-center space-x-2">
          <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </Button>
      </div>

      {/* Client Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Shield className="h-5 w-5" />
            <span>Client Status</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-center space-x-3">
              <CheckCircle className="h-5 w-5 text-green-600" />
              <div>
                <p className="font-medium">Investment Ready</p>
                <p className="text-sm text-gray-600">
                  {readiness?.investment_ready ? 'Approved' : 'Pending'}
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <Users className="h-5 w-5 text-blue-600" />
              <div>
                <p className="font-medium">KYC/AML Status</p>
                <p className="text-sm text-gray-600">
                  {readiness?.aml_kyc_completed ? 'Completed' : 'Pending'}
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <FileText className="h-5 w-5 text-purple-600" />
              <div>
                <p className="font-medium">Agreement</p>
                <p className="text-sm text-gray-600">
                  {readiness?.agreement_signed ? 'Signed' : 'Pending'}
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Portfolio Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-2">
              <DollarSign className="h-8 w-8 text-green-600" />
              <div>
                <p className="text-sm font-medium text-gray-600">Total Investment</p>
                <p className="text-2xl font-bold">{formatCurrency(totalInvestment)}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-2">
              <Wallet className="h-8 w-8 text-blue-600" />
              <div>
                <p className="text-sm font-medium text-gray-600">Current Value</p>
                <p className="text-2xl font-bold">{formatCurrency(currentValue)}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-2">
              <TrendingUp className={`h-8 w-8 ${getPerformanceColor(totalReturn)}`} />
              <div>
                <p className="text-sm font-medium text-gray-600">Total Return</p>
                <p className={`text-2xl font-bold ${getPerformanceColor(totalReturn)}`}>
                  {formatCurrency(totalReturn)}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-2">
              <BarChart3 className={`h-8 w-8 ${getPerformanceColor(returnPercentage)}`} />
              <div>
                <p className="text-sm font-medium text-gray-600">Return %</p>
                <p className={`text-2xl font-bold ${getPerformanceColor(returnPercentage)}`}>
                  {returnPercentage.toFixed(2)}%
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Investment Details */}
      <Tabs defaultValue="investments" className="w-full">
        <TabsList>
          <TabsTrigger value="investments">Investments</TabsTrigger>
          <TabsTrigger value="mt5">MT5 Accounts</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
        </TabsList>

        <TabsContent value="investments" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Investment Portfolio</CardTitle>
            </CardHeader>
            <CardContent>
              {investments.length === 0 ? (
                <Alert>
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>
                    No investments found. Investment data may still be loading or requires API endpoint verification.
                  </AlertDescription>
                </Alert>
              ) : (
                <div className="space-y-4">
                  {investments.map((investment, index) => (
                    <Card key={investment.investment_id || index} className="border-l-4 border-l-blue-500">
                      <CardContent className="p-4">
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                          <div>
                            <p className="text-sm font-medium text-gray-600">Fund</p>
                            <Badge variant="outline">{investment.fund_code}</Badge>
                          </div>
                          <div>
                            <p className="text-sm font-medium text-gray-600">Principal Amount</p>
                            <p className="text-lg font-semibold">{formatCurrency(investment.principal_amount)}</p>
                          </div>
                          <div>
                            <p className="text-sm font-medium text-gray-600">Current Value</p>
                            <p className="text-lg font-semibold">{formatCurrency(investment.current_value)}</p>
                          </div>
                          <div>
                            <p className="text-sm font-medium text-gray-600">Deposit Date</p>
                            <p className="text-sm">{formatDate(investment.deposit_date)}</p>
                          </div>
                        </div>
                        <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                          <div>
                            <p className="font-medium text-gray-600">Incubation Ends:</p>
                            <p>{formatDate(investment.incubation_end_date)}</p>
                          </div>
                          <div>
                            <p className="font-medium text-gray-600">Interest Starts:</p>
                            <p>{formatDate(investment.interest_start_date)}</p>
                          </div>
                          <div>
                            <p className="font-medium text-gray-600">Minimum Hold Until:</p>
                            <p>{formatDate(investment.minimum_hold_end_date)}</p>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="mt5" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>MT5 Trading Accounts</CardTitle>
            </CardHeader>
            <CardContent>
              {mt5Accounts.length === 0 ? (
                <Alert>
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>
                    No MT5 accounts found. Expected 4 MEXAtlantic accounts:
                    <br />• Login 886557: $80,000 (BALANCE)
                    <br />• Login 886066: $10,000 (BALANCE)  
                    <br />• Login 886602: $10,000 (BALANCE)
                    <br />• Login 885822: $18,151.41 (CORE)
                  </AlertDescription>
                </Alert>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {mt5Accounts.map((account, index) => (
                    <Card key={account.account_id || index} className="border-l-4 border-l-green-500">
                      <CardContent className="p-4">
                        <div className="flex items-center justify-between mb-3">
                          <h4 className="font-semibold">MT5 Account</h4>
                          <Badge variant={account.is_active ? 'default' : 'secondary'}>
                            {account.is_active ? 'Active' : 'Inactive'}
                          </Badge>
                        </div>
                        <div className="space-y-2 text-sm">
                          <div className="flex justify-between">
                            <span className="text-gray-600">Login:</span>
                            <span className="font-mono">{account.mt5_login}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">Broker:</span>
                            <span>{account.broker_name}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">Server:</span>
                            <span className="font-mono text-xs">{account.mt5_server}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">Allocated:</span>
                            <span className="font-semibold">{formatCurrency(account.total_allocated)}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">Current Equity:</span>
                            <span className="font-semibold">{formatCurrency(account.current_equity)}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">P&L:</span>
                            <span className={`font-semibold ${getPerformanceColor(account.profit_loss)}`}>
                              {formatCurrency(account.profit_loss)}
                            </span>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="performance" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Performance Analytics</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <Alert>
                  <Activity className="h-4 w-4" />
                  <AlertDescription>
                    Real-time performance data will be available once MT5 accounts are properly connected and synchronized.
                  </AlertDescription>
                </Alert>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="font-semibold mb-3">Expected Account Structure</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span>BALANCE Fund Total:</span>
                        <span className="font-mono">$100,000.00</span>
                      </div>
                      <div className="ml-4 space-y-1 text-gray-600">
                        <div className="flex justify-between">
                          <span>• Account 886557:</span>
                          <span>$80,000.00</span>
                        </div>
                        <div className="flex justify-between">
                          <span>• Account 886066:</span>
                          <span>$10,000.00</span>
                        </div>
                        <div className="flex justify-between">
                          <span>• Account 886602:</span>
                          <span>$10,000.00</span>
                        </div>
                      </div>
                      <div className="flex justify-between">
                        <span>CORE Fund Total:</span>
                        <span className="font-mono">$18,151.41</span>
                      </div>
                      <div className="ml-4 text-gray-600">
                        <div className="flex justify-between">
                          <span>• Account 885822:</span>
                          <span>$18,151.41</span>
                        </div>
                      </div>
                      <hr />
                      <div className="flex justify-between font-semibold">
                        <span>Total Investment:</span>
                        <span>$118,151.41</span>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h4 className="font-semibold mb-3">Key Dates</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span>Investment Date:</span>
                        <span>October 1, 2025</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Incubation Ends:</span>
                        <span>December 1, 2025</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Interest Starts:</span>
                        <span>December 1, 2025</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Minimum Hold Until:</span>
                        <span>December 1, 2026</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AlejandroInvestmentDashboard;