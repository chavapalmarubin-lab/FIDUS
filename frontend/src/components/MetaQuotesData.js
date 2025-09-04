import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Badge } from "./ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { 
  Shield, 
  Activity, 
  TrendingUp, 
  TrendingDown, 
  RefreshCw, 
  Settings, 
  CheckCircle, 
  AlertCircle,
  BarChart3,
  PieChart,
  DollarSign,
  Clock
} from "lucide-react";
import axios from "axios";
import { format } from "date-fns";

const MetaQuotesData = () => {
  const [credentials, setCredentials] = useState({
    login: '',
    password: '',
    server: ''
  });
  const [connectionStatus, setConnectionStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [accountInfo, setAccountInfo] = useState(null);
  const [positions, setPositions] = useState([]);
  const [dealsHistory, setDealsHistory] = useState([]);
  const [marketData, setMarketData] = useState({});
  const [showCredentials, setShowCredentials] = useState(false);

  const backendUrl = process.env.REACT_APP_BACKEND_URL;

  const handleConnect = async () => {
    try {
      setLoading(true);
      
      const formData = new FormData();
      formData.append('login', credentials.login);
      formData.append('password', credentials.password);
      formData.append('server', credentials.server);
      
      const response = await axios.post(`${backendUrl}/api/metaquotes/connect`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      setConnectionStatus(response.data);
      
      if (response.data.success) {
        setShowCredentials(false);
        await fetchAllData();
      }
    } catch (error) {
      console.error('MetaQuotes connection error:', error);
      setConnectionStatus({
        success: false,
        error: error.response?.data?.detail || 'Connection failed'
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchAllData = async () => {
    try {
      // Fetch account info
      const accountRes = await axios.get(`${backendUrl}/api/metaquotes/account-info`);
      if (accountRes.data.success) {
        setAccountInfo(accountRes.data.account_info);
      }

      // Fetch positions
      const positionsRes = await axios.get(`${backendUrl}/api/metaquotes/positions`);
      if (positionsRes.data.success) {
        setPositions(positionsRes.data.positions);
      }

      // Fetch deals history
      const dealsRes = await axios.get(`${backendUrl}/api/metaquotes/deals-history?days=30`);
      if (dealsRes.data.success) {
        setDealsHistory(dealsRes.data.deals);
      }

      // Fetch market data
      const marketRes = await axios.get(`${backendUrl}/api/metaquotes/market-data`);
      if (marketRes.data.success) {
        setMarketData(marketRes.data.market_data);
      }
    } catch (error) {
      console.error('Error fetching MetaQuotes data:', error);
    }
  };

  const handleDisconnect = async () => {
    try {
      await axios.post(`${backendUrl}/api/metaquotes/disconnect`);
      setConnectionStatus(null);
      setAccountInfo(null);
      setPositions([]);
      setDealsHistory([]);
      setMarketData({});
    } catch (error) {
      console.error('Disconnect error:', error);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(amount);
  };

  const formatTimestamp = (timestamp) => {
    return format(new Date(timestamp * 1000), 'MMM dd, yyyy HH:mm');
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-white mb-2">MetaQuotes Data</h2>
          <p className="text-gray-400">Real-time MetaTrader 4/5 integration and monitoring</p>
        </div>
        <div className="flex gap-2">
          <Button
            onClick={() => setShowCredentials(!showCredentials)}
            variant="outline"
            className="border-slate-600 text-slate-300 hover:bg-slate-700"
          >
            <Settings className="h-4 w-4 mr-2" />
            {showCredentials ? 'Hide' : 'Settings'}
          </Button>
          {connectionStatus?.success && (
            <Button
              onClick={fetchAllData}
              className="bg-cyan-600 hover:bg-cyan-700"
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </Button>
          )}
        </div>
      </div>

      {/* Connection Status */}
      <Card className="bg-slate-800 border-slate-700">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className={`h-3 w-3 rounded-full ${connectionStatus?.success ? 'bg-green-400' : 'bg-red-400'}`}></div>
              <span className="text-white font-medium">
                MetaTrader Connection: {connectionStatus?.success ? 'Connected' : 'Disconnected'}
              </span>
              {connectionStatus?.success && (
                <Badge className="bg-green-600/20 text-green-400">
                  <CheckCircle className="h-3 w-3 mr-1" />
                  Online
                </Badge>
              )}
            </div>
            {connectionStatus?.success && (
              <Button
                onClick={handleDisconnect}
                variant="outline"
                size="sm"
                className="border-red-600 text-red-400 hover:bg-red-600/10"
              >
                Disconnect
              </Button>
            )}
          </div>
          {connectionStatus?.error && (
            <div className="mt-3 p-3 bg-red-600/10 border border-red-600/20 rounded-lg">
              <div className="flex items-center text-red-400">
                <AlertCircle className="h-4 w-4 mr-2" />
                <span className="text-sm">{connectionStatus.error}</span>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Credentials Form */}
      {showCredentials && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
          className="overflow-hidden"
        >
          <Card className="bg-slate-800 border-slate-700">
            <CardHeader>
              <CardTitle className="text-white flex items-center">
                <Shield className="h-5 w-5 mr-2" />
                MetaTrader Connection Settings
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="login" className="text-gray-400">Account Login</Label>
                  <Input
                    id="login"
                    type="text"
                    placeholder="Account number"
                    value={credentials.login}
                    onChange={(e) => setCredentials({...credentials, login: e.target.value})}
                    className="bg-slate-700 border-slate-600 text-white"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="password" className="text-gray-400">Password</Label>
                  <Input
                    id="password"
                    type="password"
                    placeholder="Account password"
                    value={credentials.password}
                    onChange={(e) => setCredentials({...credentials, password: e.target.value})}
                    className="bg-slate-700 border-slate-600 text-white"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="server" className="text-gray-400">Server</Label>
                  <Input
                    id="server"
                    type="text"
                    placeholder="Broker server name"
                    value={credentials.server}
                    onChange={(e) => setCredentials({...credentials, server: e.target.value})}
                    className="bg-slate-700 border-slate-600 text-white"
                  />
                </div>
              </div>
              
              <div className="bg-slate-700/50 rounded-lg p-4">
                <h4 className="text-white font-medium mb-2">Demo Credentials (for testing):</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                  <div>
                    <p className="text-gray-400">Login:</p>
                    <p className="text-white font-mono">5001000 - 5001004</p>
                  </div>
                  <div>
                    <p className="text-gray-400">Password:</p>
                    <p className="text-white font-mono">demo123</p>
                  </div>
                  <div>
                    <p className="text-gray-400">Server:</p>
                    <p className="text-white font-mono">MetaQuotes-Demo</p>
                  </div>
                </div>
              </div>

              <div className="flex justify-end">
                <Button
                  onClick={handleConnect}
                  disabled={loading || !credentials.login || !credentials.password || !credentials.server}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  {loading ? (
                    <>
                      <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                      Connecting...
                    </>
                  ) : (
                    <>
                      <Shield className="h-4 w-4 mr-2" />
                      Connect to MetaTrader
                    </>
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Main Data Display */}
      {connectionStatus?.success && accountInfo && (
        <div className="space-y-6">
          {/* Account Summary */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card className="bg-slate-800 border-slate-700">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-400">Account Balance</p>
                    <p className="text-2xl font-bold text-white">{formatCurrency(accountInfo.balance)}</p>
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
                    <p className="text-sm font-medium text-gray-400">Equity</p>
                    <p className="text-2xl font-bold text-white">{formatCurrency(accountInfo.equity)}</p>
                  </div>
                  <div className="h-12 w-12 bg-blue-600/20 rounded-lg flex items-center justify-center">
                    <BarChart3 className="h-6 w-6 text-blue-600" />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-slate-800 border-slate-700">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-400">Open Positions</p>
                    <p className="text-2xl font-bold text-white">{positions.length}</p>
                  </div>
                  <div className="h-12 w-12 bg-yellow-600/20 rounded-lg flex items-center justify-center">
                    <Activity className="h-6 w-6 text-yellow-600" />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-slate-800 border-slate-700">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-400">Margin Level</p>
                    <p className="text-2xl font-bold text-white">{accountInfo.margin_level?.toFixed(2) || '0.00'}%</p>
                  </div>
                  <div className="h-12 w-12 bg-purple-600/20 rounded-lg flex items-center justify-center">
                    <PieChart className="h-6 w-6 text-purple-600" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Data Tabs */}
          <Tabs defaultValue="account" className="w-full">
            <TabsList className="grid w-full grid-cols-4 bg-slate-800 border-slate-600">
              <TabsTrigger value="account" className="data-[state=active]:bg-cyan-600">
                Account Info
              </TabsTrigger>
              <TabsTrigger value="positions" className="data-[state=active]:bg-cyan-600">
                Open Positions
              </TabsTrigger>
              <TabsTrigger value="history" className="data-[state=active]:bg-cyan-600">
                Trade History
              </TabsTrigger>
              <TabsTrigger value="market" className="data-[state=active]:bg-cyan-600">
                Market Data
              </TabsTrigger>
            </TabsList>

            <TabsContent value="account" className="mt-6">
              <Card className="bg-slate-800 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white">Account Information</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    <div className="space-y-4">
                      <h4 className="text-white font-medium">Basic Information</h4>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-gray-400">Login:</span>
                          <span className="text-white font-mono">{accountInfo.login}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">Name:</span>
                          <span className="text-white">{accountInfo.name}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">Company:</span>
                          <span className="text-white">{accountInfo.company}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">Server:</span>
                          <span className="text-white">{accountInfo.server}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">Currency:</span>
                          <span className="text-white">{accountInfo.currency}</span>
                        </div>
                      </div>
                    </div>

                    <div className="space-y-4">
                      <h4 className="text-white font-medium">Account Metrics</h4>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-gray-400">Balance:</span>
                          <span className="text-white font-medium">{formatCurrency(accountInfo.balance)}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">Equity:</span>
                          <span className="text-white font-medium">{formatCurrency(accountInfo.equity)}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">Margin:</span>
                          <span className="text-white font-medium">{formatCurrency(accountInfo.margin)}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">Free Margin:</span>
                          <span className="text-white font-medium">{formatCurrency(accountInfo.free_margin)}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">Profit:</span>
                          <span className={`font-medium ${accountInfo.profit >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                            {accountInfo.profit >= 0 ? '+' : ''}{formatCurrency(accountInfo.profit)}
                          </span>
                        </div>
                      </div>
                    </div>

                    <div className="space-y-4">
                      <h4 className="text-white font-medium">Trading Settings</h4>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-gray-400">Leverage:</span>
                          <span className="text-white">1:{accountInfo.leverage}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">Margin Level:</span>
                          <span className="text-white">{accountInfo.margin_level?.toFixed(2) || '0.00'}%</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">Trade Allowed:</span>
                          <Badge className={accountInfo.trade_allowed ? 'bg-green-600/20 text-green-400' : 'bg-red-600/20 text-red-400'}>
                            {accountInfo.trade_allowed ? 'Yes' : 'No'}
                          </Badge>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">Expert Allowed:</span>
                          <Badge className={accountInfo.expert_allowed ? 'bg-green-600/20 text-green-400' : 'bg-red-600/20 text-red-400'}>
                            {accountInfo.expert_allowed ? 'Yes' : 'No'}
                          </Badge>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="positions" className="mt-6">
              <Card className="bg-slate-800 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white">Open Positions ({positions.length})</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b border-slate-600">
                          <th className="text-left py-3 px-4 text-gray-400 font-medium">Ticket</th>
                          <th className="text-left py-3 px-4 text-gray-400 font-medium">Symbol</th>
                          <th className="text-left py-3 px-4 text-gray-400 font-medium">Type</th>
                          <th className="text-right py-3 px-4 text-gray-400 font-medium">Volume</th>
                          <th className="text-right py-3 px-4 text-gray-400 font-medium">Open Price</th>
                          <th className="text-right py-3 px-4 text-gray-400 font-medium">Current</th>
                          <th className="text-right py-3 px-4 text-gray-400 font-medium">P&L</th>
                          <th className="text-right py-3 px-4 text-gray-400 font-medium">Swap</th>
                        </tr>
                      </thead>
                      <tbody>
                        {(positions || []).map((position) => (
                          <tr key={position.ticket} className="border-b border-slate-700 hover:bg-slate-700/50">
                            <td className="py-3 px-4 text-white font-mono">{position.ticket}</td>
                            <td className="py-3 px-4 text-white font-medium">{position.symbol}</td>
                            <td className="py-3 px-4">
                              <Badge className={position.type === 0 ? 'bg-green-600/20 text-green-400' : 'bg-red-600/20 text-red-400'}>
                                {position.type === 0 ? 'BUY' : 'SELL'}
                              </Badge>
                            </td>
                            <td className="text-right py-3 px-4 text-white">{position.volume}</td>
                            <td className="text-right py-3 px-4 text-white">{position.price_open}</td>
                            <td className="text-right py-3 px-4 text-white">{position.price_current}</td>
                            <td className={`text-right py-3 px-4 font-medium ${position.profit >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                              {position.profit >= 0 ? '+' : ''}${position.profit.toFixed(2)}
                            </td>
                            <td className={`text-right py-3 px-4 ${position.swap >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                              {position.swap >= 0 ? '+' : ''}${position.swap.toFixed(2)}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="history" className="mt-6">
              <Card className="bg-slate-800 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white">Trade History (Last 30 Days)</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b border-slate-600">
                          <th className="text-left py-3 px-4 text-gray-400 font-medium">Ticket</th>
                          <th className="text-left py-3 px-4 text-gray-400 font-medium">Time</th>
                          <th className="text-left py-3 px-4 text-gray-400 font-medium">Symbol</th>
                          <th className="text-left py-3 px-4 text-gray-400 font-medium">Type</th>
                          <th className="text-right py-3 px-4 text-gray-400 font-medium">Volume</th>
                          <th className="text-right py-3 px-4 text-gray-400 font-medium">Price</th>
                          <th className="text-right py-3 px-4 text-gray-400 font-medium">Profit</th>
                        </tr>
                      </thead>
                      <tbody>
                        {dealsHistory.slice(0, 50).map((deal) => (
                          <tr key={deal.ticket} className="border-b border-slate-700 hover:bg-slate-700/50">
                            <td className="py-3 px-4 text-white font-mono">{deal.ticket}</td>
                            <td className="py-3 px-4 text-gray-400">{formatTimestamp(deal.time)}</td>
                            <td className="py-3 px-4 text-white font-medium">{deal.symbol}</td>
                            <td className="py-3 px-4">
                              <Badge className={deal.type === 0 ? 'bg-green-600/20 text-green-400' : 'bg-red-600/20 text-red-400'}>
                                {deal.type === 0 ? 'BUY' : 'SELL'}
                              </Badge>
                            </td>
                            <td className="text-right py-3 px-4 text-white">{deal.volume}</td>
                            <td className="text-right py-3 px-4 text-white">{deal.price}</td>
                            <td className={`text-right py-3 px-4 font-medium ${deal.profit >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                              {deal.profit >= 0 ? '+' : ''}${deal.profit.toFixed(2)}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="market" className="mt-6">
              <Card className="bg-slate-800 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white">Market Data</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {Object.entries(marketData).map(([symbol, data]) => (
                      <div key={symbol} className="p-4 bg-slate-700/50 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="text-white font-medium">{symbol}</h4>
                          <Badge variant="secondary" className="bg-slate-600 text-slate-200">
                            {data.spread} pips
                          </Badge>
                        </div>
                        <div className="grid grid-cols-2 gap-2 text-sm">
                          <div>
                            <p className="text-gray-400">Bid</p>
                            <p className="text-white font-medium">{data.bid}</p>
                          </div>
                          <div>
                            <p className="text-gray-400">Ask</p>
                            <p className="text-white font-medium">{data.ask}</p>
                          </div>
                          <div>
                            <p className="text-gray-400">Last</p>
                            <p className="text-white">{data.last}</p>
                          </div>
                          <div>
                            <p className="text-gray-400">Volume</p>
                            <p className="text-white">{data.volume}</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      )}

      {/* No Connection State */}
      {!connectionStatus?.success && (
        <Card className="bg-slate-800 border-slate-700">
          <CardContent className="p-12 text-center">
            <div className="h-16 w-16 bg-slate-700 rounded-lg flex items-center justify-center mx-auto mb-4">
              <Activity className="h-8 w-8 text-gray-400" />
            </div>
            <h3 className="text-white font-medium mb-2">Connect to MetaTrader</h3>
            <p className="text-gray-400 mb-4">
              Enter your MetaTrader account credentials to view real-time trading data and account information.
            </p>
            <Button
              onClick={() => setShowCredentials(true)}
              className="bg-blue-600 hover:bg-blue-700"
            >
              <Shield className="h-4 w-4 mr-2" />
              Setup Connection
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default MetaQuotesData;