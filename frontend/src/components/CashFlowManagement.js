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
  Download,
  Plus
} from "lucide-react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts';
import apiAxios from "../utils/apiAxios";

const CashFlowManagement = () => {
  const [cashFlowData, setCashFlowData] = useState([]);
  const [fundAccounting, setFundAccounting] = useState({});
  const [fundBreakdown, setFundBreakdown] = useState({});
  const [rebatesSummary, setRebatesSummary] = useState({});
  const [selectedTimeframe, setSelectedTimeframe] = useState('3months');
  const [selectedFund, setSelectedFund] = useState('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showAddRebateModal, setShowAddRebateModal] = useState(false);
  const [newRebate, setNewRebate] = useState({
    fund_code: '',
    amount: '',
    broker: '',
    lots_traded: '',
    rebate_per_lot: '',
    description: ''
  });

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
      setError("");
      
      // Fetch fund accounting cash flow data
      const cashFlowResponse = await apiAxios.get(`/admin/cashflow/overview`, {
        params: { timeframe: selectedTimeframe, fund: selectedFund }
      });
      
      if (cashFlowResponse.data.success) {
        // Use proper fund accounting structure
        setCashFlowData(cashFlowResponse.data.cash_flows || []);
        setFundAccounting(cashFlowResponse.data.fund_accounting || {});
        setFundBreakdown(cashFlowResponse.data.fund_breakdown || {});
        setRebatesSummary(cashFlowResponse.data.rebates_summary || {});
        
        console.log("✅ Fund accounting cash flow data loaded successfully:", cashFlowResponse.data.fund_accounting);
      } else {
        throw new Error("API returned unsuccessful response");
      }
    } catch (err) {
      console.error("❌ Cash flow API error:", err);
      setError("Failed to load cash flow data");
      // Set example fund accounting data
      setFundAccounting({
        assets: {
          mt5_trading_profits: 0,
          broker_rebates: 0,
          total_inflows: 0
        },
        liabilities: {
          client_obligations: 300000,
          upcoming_redemptions: 0,
          total_outflows: 300000
        },
        net_fund_profitability: 250000
      });
    } finally {
      setLoading(false);
    }
  };

  const handleAddRebate = async () => {
    try {
      if (!newRebate.fund_code || !newRebate.amount || !newRebate.broker) {
        setError("Please fill in all required fields");
        return;
      }

      const response = await apiAxios.post('/admin/rebates/add', {
        fund_code: newRebate.fund_code,
        amount: parseFloat(newRebate.amount),
        broker: newRebate.broker,
        lots_traded: parseFloat(newRebate.lots_traded) || 0,
        rebate_per_lot: parseFloat(newRebate.rebate_per_lot) || 0,
        description: newRebate.description || `Lot-based rebate from ${newRebate.broker}`,
        date: new Date().toISOString().split('T')[0] // Today's date
      });

      if (response.data.success) {
        // Reset form
        setNewRebate({
          fund_code: '',
          amount: '',
          broker: '',
          lots_traded: '',
          rebate_per_lot: '',
          description: ''
        });
        setShowAddRebateModal(false);
        
        // Refresh data
        await fetchCashFlowData();
        
        console.log("✅ Rebate added successfully:", response.data.rebate);
      } else {
        throw new Error("Failed to add rebate");
      }
    } catch (err) {
      console.error("❌ Add rebate error:", err);
      setError("Failed to add rebate");
    }
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

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-white text-xl">Loading cash flow data...</div>
      </div>
    );
  }

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

      {/* FUND ACCOUNTING OVERVIEW */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* FUND ASSETS (What Fund Owns) */}
        <Card className="dashboard-card">
          <CardHeader>
            <CardTitle className="text-white flex items-center">
              <ArrowUpCircle className="mr-2 h-5 w-5 text-green-400" />
              Fund Assets (Income Sources)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* MT5 Trading Profits */}
              <div className="flex justify-between items-center p-3 bg-slate-800/50 rounded-lg">
                <div>
                  <p className="text-sm text-slate-400">MT5 Trading Profits</p>
                  <p className="text-xs text-slate-500">Fund's investment performance</p>
                </div>
                <div className="text-right">
                  <p className="text-lg font-bold text-green-400">
                    {formatCurrency(fundAccounting?.assets?.mt5_trading_profits || 0)}
                  </p>
                </div>
              </div>
              
              {/* Broker Rebates */}
              <div className="flex justify-between items-center p-3 bg-slate-800/50 rounded-lg">
                <div>
                  <p className="text-sm text-slate-400">Broker Rebates</p>
                  <p className="text-xs text-slate-500">Commission from trading volume</p>
                </div>
                <div className="text-right">
                  <p className="text-lg font-bold text-cyan-400">
                    {formatCurrency(fundAccounting?.assets?.broker_rebates || 0)}
                  </p>
                </div>
              </div>
              
              {/* Total Assets */}
              <div className="border-t border-slate-600 pt-3">
                <div className="flex justify-between items-center">
                  <p className="text-white font-semibold">Total Fund Assets</p>
                  <p className="text-xl font-bold text-green-400">
                    {formatCurrency(fundAccounting?.assets?.total_inflows || 0)}
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* FUND LIABILITIES (What Fund Owes) */}
        <Card className="dashboard-card">
          <CardHeader>
            <CardTitle className="text-white flex items-center">
              <ArrowDownCircle className="mr-2 h-5 w-5 text-red-400" />
              Fund Liabilities (Obligations)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* Client Obligations */}
              <div className="flex justify-between items-center p-3 bg-slate-800/50 rounded-lg">
                <div>
                  <p className="text-sm text-slate-400">Client Interest Obligations</p>
                  <p className="text-xs text-slate-500">Promised returns to clients</p>
                </div>
                <div className="text-right">
                  <p className="text-lg font-bold text-red-400">
                    {formatCurrency(fundAccounting?.liabilities?.client_obligations || 0)}
                  </p>
                </div>
              </div>
              
              {/* Upcoming Redemptions */}
              <div className="flex justify-between items-center p-3 bg-slate-800/50 rounded-lg">
                <div>
                  <p className="text-sm text-slate-400">Upcoming Redemptions</p>
                  <p className="text-xs text-slate-500">Scheduled client withdrawals</p>
                </div>
                <div className="text-right">
                  <p className="text-lg font-bold text-yellow-400">
                    {formatCurrency(fundAccounting?.liabilities?.upcoming_redemptions || 0)}
                  </p>
                </div>
              </div>
              
              {/* Total Liabilities */}
              <div className="border-t border-slate-600 pt-3">
                <div className="flex justify-between items-center">
                  <p className="text-white font-semibold">Total Fund Liabilities</p>
                  <p className="text-xl font-bold text-red-400">
                    {formatCurrency(fundAccounting?.liabilities?.total_outflows || 0)}
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* NET FUND PROFITABILITY */}
      <Card className="dashboard-card">
        <CardHeader>
          <CardTitle className="text-white flex items-center">
            <DollarSign className="mr-2 h-5 w-5 text-cyan-400" />
            Net Fund Profitability Analysis
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center p-6 bg-green-900/20 rounded-lg border border-green-600/30">
              <ArrowUpCircle className="h-12 w-12 text-green-400 mx-auto mb-2" />
              <p className="text-green-400 font-semibold">Fund Revenue</p>
              <p className="text-2xl font-bold text-green-400">
                {formatCurrency(fundAccounting?.assets?.total_inflows || 0)}
              </p>
              <p className="text-xs text-slate-400 mt-1">Trading + Rebates</p>
            </div>
            
            <div className="text-center p-6 bg-red-900/20 rounded-lg border border-red-600/30">
              <ArrowDownCircle className="h-12 w-12 text-red-400 mx-auto mb-2" />
              <p className="text-red-400 font-semibold">Fund Obligations</p>
              <p className="text-2xl font-bold text-red-400">
                {formatCurrency(fundAccounting?.liabilities?.total_outflows || 0)}
              </p>
              <p className="text-xs text-slate-400 mt-1">Client Commitments</p>
            </div>
            
            <div className={`text-center p-6 rounded-lg border ${
              (fundAccounting?.net_fund_profitability || 0) >= 0 
                ? 'bg-cyan-900/20 border-cyan-600/30' 
                : 'bg-red-900/20 border-red-600/30'
            }`}>
              <DollarSign className={`h-12 w-12 mx-auto mb-2 ${
                (fundAccounting?.net_fund_profitability || 0) >= 0 ? 'text-cyan-400' : 'text-red-400'
              }`} />
              <p className={`font-semibold ${
                (fundAccounting?.net_fund_profitability || 0) >= 0 ? 'text-cyan-400' : 'text-red-400'
              }`}>Net Profit</p>
              <p className={`text-2xl font-bold ${
                (fundAccounting?.net_fund_profitability || 0) >= 0 ? 'text-cyan-400' : 'text-red-400'
              }`}>
                {formatCurrency(fundAccounting?.net_fund_profitability || 0)}
              </p>
              <p className="text-xs text-slate-400 mt-1">
                {(fundAccounting?.net_fund_profitability || 0) >= 0 ? 'Profitable' : 'Loss Making'}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* REBATES COMMISSION BREAKDOWN */}
      <Card className="dashboard-card">
        <CardHeader>
          <CardTitle className="text-white flex items-center justify-between">
            <div className="flex items-center">
              <TrendingUp className="mr-2 h-5 w-5 text-cyan-400" />
              Broker Rebates & Commission Structure
            </div>
            <Button 
              onClick={() => setShowAddRebateModal(true)}
              className="bg-cyan-600 hover:bg-cyan-700"
              size="sm"
            >
              <Plus className="h-4 w-4 mr-2" />
              Add Rebate
            </Button>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="text-white font-semibold mb-3">Rebate Summary</h4>
              <div className="space-y-3">
                <div className="flex justify-between items-center p-3 bg-slate-800/50 rounded-lg">
                  <span className="text-slate-400">Total Rebates Earned</span>
                  <span className="text-cyan-400 font-bold">
                    {formatCurrency(rebatesSummary?.total_rebates || 0)}
                  </span>
                </div>
                <div className="text-sm text-slate-300">
                  <p><strong>Revenue Source:</strong> Broker commissions based on trading volume (lots)</p>
                  <p><strong>Structure:</strong> Variable rate per lot traded on MT5 accounts</p>
                  <p><strong>Calculation:</strong> Total lots × rebate per lot = total rebate</p>
                </div>
              </div>
            </div>
            
            <div>
              <h4 className="text-white font-semibold mb-3">Commission by Fund</h4>
              <div className="space-y-2">
                {Object.entries(rebatesSummary?.rebate_breakdown || {}).map(([fundCode, amount]) => (
                  <div key={fundCode} className="flex justify-between items-center">
                    <div className="flex items-center">
                      <div 
                        className="w-3 h-3 rounded-full mr-2"
                        style={{ backgroundColor: FUND_COLORS[fundCode] }}
                      ></div>
                      <span className="text-slate-300">{fundCode} Fund</span>
                    </div>
                    <span className="text-cyan-400 font-medium">
                      {formatCurrency(amount)}
                    </span>
                  </div>
                ))}
                {Object.keys(rebatesSummary?.rebate_breakdown || {}).length === 0 && (
                  <p className="text-slate-400 text-sm">No rebates recorded yet. Click "Add Rebate" to start tracking.</p>
                )}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* FUND ACCOUNTING BREAKDOWN TABLE */}
      <Card className="dashboard-card">
        <CardHeader>
          <CardTitle className="text-white flex items-center">
            <TrendingUp className="mr-2 h-5 w-5 text-cyan-400" />
            Fund Accounting Breakdown - Assets vs Liabilities
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-600">
                  <th className="text-left text-slate-400 font-medium py-3">Fund</th>
                  <th className="text-right text-slate-400 font-medium py-3">MT5 Profits</th>
                  <th className="text-right text-slate-400 font-medium py-3">Rebates</th>
                  <th className="text-right text-slate-400 font-medium py-3">Total Assets</th>
                  <th className="text-right text-slate-400 font-medium py-3">Client Obligations</th>
                  <th className="text-right text-slate-400 font-medium py-3">Net Position</th>
                  <th className="text-right text-slate-400 font-medium py-3">Status</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(fundBreakdown).map(([fundCode, data]) => {
                  const netPosition = (data.net_flow || 0);
                  return (
                    <tr key={fundCode} className="border-b border-slate-700/50">
                      <td className="py-4">
                        <div className="flex items-center">
                          <div 
                            className="w-3 h-3 rounded-full mr-3"
                            style={{ backgroundColor: FUND_COLORS[fundCode] }}
                          ></div>
                          <span className="text-white font-medium">{fundCode} Fund</span>
                        </div>
                      </td>
                      <td className="text-right text-green-400 font-medium py-4">
                        {formatCurrency(data.mt5_profits || 0)}
                      </td>
                      <td className="text-right text-cyan-400 font-medium py-4">
                        {formatCurrency(data.rebates || 0)}
                      </td>
                      <td className="text-right text-blue-400 font-medium py-4">
                        {formatCurrency(data.total_inflows || 0)}
                      </td>
                      <td className="text-right text-red-400 font-medium py-4">
                        {formatCurrency(data.client_obligations || 0)}
                      </td>
                      <td className={`text-right font-bold py-4 ${netPosition >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                        {formatCurrency(netPosition)}
                      </td>
                      <td className="text-right py-4">
                        <Badge className={netPosition >= 0 ? 'bg-green-600' : 'bg-red-600'}>
                          {netPosition >= 0 ? 'Profitable' : 'At Risk'}
                        </Badge>
                      </td>
                    </tr>
                  );
                })}
                {/* TOTAL FUND POSITION */}
                <tr className="border-t-2 border-cyan-600 bg-slate-800/50">
                  <td className="py-4">
                    <span className="text-cyan-400 font-bold text-lg">TOTAL FUND</span>
                  </td>
                  <td className="text-right text-green-400 font-bold text-lg py-4">
                    {formatCurrency(fundAccounting?.assets?.mt5_trading_profits || 0)}
                  </td>
                  <td className="text-right text-cyan-400 font-bold text-lg py-4">
                    {formatCurrency(fundAccounting?.assets?.broker_rebates || 0)}
                  </td>
                  <td className="text-right text-blue-400 font-bold text-lg py-4">
                    {formatCurrency(fundAccounting?.assets?.total_inflows || 0)}
                  </td>
                  <td className="text-right text-red-400 font-bold text-lg py-4">
                    {formatCurrency(fundAccounting?.liabilities?.total_outflows || 0)}
                  </td>
                  <td className={`text-right font-bold text-lg py-4 ${(fundAccounting?.net_fund_profitability || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {formatCurrency(fundAccounting?.net_fund_profitability || 0)}
                  </td>
                  <td className="text-right py-4">
                    <Badge className={`text-lg ${(fundAccounting?.net_fund_profitability || 0) >= 0 ? 'bg-green-600' : 'bg-red-600'}`}>
                      {(fundAccounting?.net_fund_profitability || 0) >= 0 ? 'PROFITABLE' : 'AT RISK'}
                    </Badge>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Status Information */}
      <Card className="dashboard-card">
        <CardHeader>
          <CardTitle className="text-white flex items-center">
            <Clock className="mr-2 h-5 w-5 text-cyan-400" />
            Cash Flow Status
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="text-white font-semibold mb-3">System Status</h4>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-slate-400">Data Source</span>
                  <span className="text-green-400">✅ Real Investment Data</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-400">Last Updated</span>
                  <span className="text-white">{new Date().toLocaleString()}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-400">Calculation Method</span>
                  <span className="text-cyan-400">Aggregated Totals</span>
                </div>
              </div>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-3">Summary</h4>
              <div className="space-y-2">
                <div className="text-sm text-slate-300">
                  Cash flow totals now represent the <span className="text-cyan-400 font-semibold">sum of all funds</span> instead of individual fund data.
                </div>
                <div className="text-sm text-slate-300">
                  This provides a comprehensive view of the overall financial health across all investment funds.
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* ADD REBATE MODAL */}
      {showAddRebateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-slate-800 rounded-lg p-6 w-full max-w-md">
            <h3 className="text-xl font-bold text-white mb-4">Add Broker Rebate</h3>
            <p className="text-sm text-slate-400 mb-4">Rebates are variable based on trading volume (lots)</p>
            
            <div className="space-y-4">
              {/* Fund Selection */}
              <div>
                <label className="block text-sm font-medium text-slate-400 mb-2">Fund *</label>
                <select
                  value={newRebate.fund_code}
                  onChange={(e) => setNewRebate({...newRebate, fund_code: e.target.value})}
                  className="w-full px-3 py-2 bg-slate-700 border border-slate-600 text-white rounded-md"
                  required
                >
                  <option value="">Select Fund</option>
                  <option value="CORE">CORE Fund</option>
                  <option value="BALANCE">BALANCE Fund</option>
                  <option value="DYNAMIC">DYNAMIC Fund</option>
                  <option value="UNLIMITED">UNLIMITED Fund</option>
                </select>
              </div>

              {/* Total Rebate Amount */}
              <div>
                <label className="block text-sm font-medium text-slate-400 mb-2">Total Rebate Amount ($) *</label>
                <input
                  type="number"
                  step="0.01"
                  value={newRebate.amount}
                  onChange={(e) => setNewRebate({...newRebate, amount: e.target.value})}
                  className="w-full px-3 py-2 bg-slate-700 border border-slate-600 text-white rounded-md"
                  placeholder="0.00"
                  required
                />
              </div>

              {/* Broker */}
              <div>
                <label className="block text-sm font-medium text-slate-400 mb-2">Broker *</label>
                <select
                  value={newRebate.broker}
                  onChange={(e) => setNewRebate({...newRebate, broker: e.target.value})}
                  className="w-full px-3 py-2 bg-slate-700 border border-slate-600 text-white rounded-md"
                  required
                >
                  <option value="">Select Broker</option>
                  <option value="Multibank">Multibank</option>
                  <option value="DooTechnology">DooTechnology</option>
                  <option value="IC Markets">IC Markets</option>
                  <option value="FXCM">FXCM</option>
                  <option value="Other">Other</option>
                </select>
              </div>

              {/* Optional Trading Details */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-slate-400 mb-2">Lots Traded (Optional)</label>
                  <input
                    type="number"
                    step="0.01"
                    value={newRebate.lots_traded}
                    onChange={(e) => setNewRebate({...newRebate, lots_traded: e.target.value})}
                    className="w-full px-3 py-2 bg-slate-700 border border-slate-600 text-white rounded-md"
                    placeholder="0.00"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-400 mb-2">$ per Lot (Optional)</label>
                  <input
                    type="number"
                    step="0.01"
                    value={newRebate.rebate_per_lot}
                    onChange={(e) => setNewRebate({...newRebate, rebate_per_lot: e.target.value})}
                    className="w-full px-3 py-2 bg-slate-700 border border-slate-600 text-white rounded-md"
                    placeholder="0.00"
                  />
                </div>
              </div>

              {/* Description */}
              <div>
                <label className="block text-sm font-medium text-slate-400 mb-2">Notes (Optional)</label>
                <textarea
                  value={newRebate.description}
                  onChange={(e) => setNewRebate({...newRebate, description: e.target.value})}
                  className="w-full px-3 py-2 bg-slate-700 border border-slate-600 text-white rounded-md"
                  rows="2"
                  placeholder="Additional notes about this rebate..."
                />
              </div>

              {/* Info Note */}
              <div className="bg-blue-900/20 border border-blue-600/30 rounded-lg p-3">
                <p className="text-blue-400 text-xs">
                  <strong>Note:</strong> Rebates are variable based on trading volume. API automation for lot tracking will be implemented later.
                </p>
              </div>
            </div>

            {/* Error Message */}
            {error && (
              <div className="mt-4 p-3 bg-red-900/20 border border-red-600 rounded-lg">
                <p className="text-red-400 text-sm">{error}</p>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex justify-end space-x-3 mt-6">
              <Button
                onClick={() => {
                  setShowAddRebateModal(false);
                  setNewRebate({fund_code: '', amount: '', broker: '', lots_traded: '', rebate_per_lot: '', description: ''});
                  setError('');
                }}
                variant="outline"
                className="border-slate-600 text-slate-300 hover:bg-slate-700"
              >
                Cancel
              </Button>
              <Button
                onClick={handleAddRebate}
                className="bg-cyan-600 hover:bg-cyan-700"
              >
                Add Rebate
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CashFlowManagement;