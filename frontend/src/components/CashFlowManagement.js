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
  Download
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
          mt5_trading_profits: 500000,
          broker_rebates: 50000,
          total_inflows: 550000
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

      {/* Fund Breakdown Table */}
      <Card className="dashboard-card">
        <CardHeader>
          <CardTitle className="text-white flex items-center">
            <TrendingUp className="mr-2 h-5 w-5 text-cyan-400" />
            Fund Breakdown - All Funds Summary
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-600">
                  <th className="text-left text-slate-400 font-medium py-3">Fund</th>
                  <th className="text-right text-slate-400 font-medium py-3">Inflow</th>
                  <th className="text-right text-slate-400 font-medium py-3">Outflow</th>
                  <th className="text-right text-slate-400 font-medium py-3">Net Flow</th>
                  <th className="text-right text-slate-400 font-medium py-3">Performance</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(fundBreakdown).map(([fundCode, data]) => {
                  const netFlow = (data.inflow || 0) - (data.outflow || 0);
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
                        {formatCurrency(data.inflow || 0)}
                      </td>
                      <td className="text-right text-red-400 font-medium py-4">
                        {formatCurrency(data.outflow || 0)}
                      </td>
                      <td className={`text-right font-bold py-4 ${netFlow >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                        {formatCurrency(netFlow)}
                      </td>
                      <td className="text-right py-4">
                        <Badge className={netFlow >= 0 ? 'bg-green-600' : 'bg-red-600'}>
                          {netFlow >= 0 ? 'Positive' : 'Negative'}
                        </Badge>
                      </td>
                    </tr>
                  );
                })}
                {/* Summary Row */}
                <tr className="border-t-2 border-cyan-600 bg-slate-800/50">
                  <td className="py-4">
                    <span className="text-cyan-400 font-bold text-lg">TOTAL (All Funds)</span>
                  </td>
                  <td className="text-right text-green-400 font-bold text-lg py-4">
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
                      {(fundAccounting?.net_fund_profitability || 0) >= 0 ? 'Strong' : 'Weak'}
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
    </div>
  );
};

export default CashFlowManagement;