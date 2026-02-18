/**
 * FIDUS Fund Portfolio Management
 * 
 * CORRECT ARCHITECTURE:
 * - MT5 Accounts = "THE FUND" (one pool, not divided by product type)
 * - Client Products (CORE, BALANCE, DYNAMIC) = Determine OBLIGATIONS only
 * 
 * This component shows:
 * 1. Total Fund Assets (sum of ALL MT5 accounts)
 * 2. Client Obligations by Product
 * 3. Coverage Ratio (Can we meet obligations?)
 * 4. MT5 Accounts (without fund_type labels)
 */

import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { 
  DollarSign, 
  TrendingUp, 
  TrendingDown,
  Users,
  Target,
  Activity,
  AlertCircle,
  RefreshCw,
  BarChart3,
  PieChart,
  Wallet,
  PiggyBank,
  Shield,
  Building2,
  ChevronDown,
  ChevronUp,
  CheckCircle2,
  AlertTriangle
} from "lucide-react";
import { PieChart as RechartsPieChart, Pie, Cell, ResponsiveContainer, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';
import apiAxios from "../utils/apiAxios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

// Product colors for Client Obligations
const PRODUCT_COLORS = {
  CORE: '#0891b2',      // Cyan
  BALANCE: '#8b5cf6',   // Purple  
  DYNAMIC: '#f59e0b'    // Orange
};

const FundPortfolioManagement = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  
  // Fund data (THE FUND - one pool)
  const [totalFundAssets, setTotalFundAssets] = useState(0);
  const [totalPnL, setTotalPnL] = useState(0);
  const [mt5Accounts, setMt5Accounts] = useState([]);
  
  // Client Obligations (by product)
  const [clientObligations, setClientObligations] = useState({
    CORE: { amount: 0, clients: 0, rate: '1.5%/month', frequency: 'Monthly' },
    BALANCE: { amount: 0, clients: 0, rate: '2.5%/month', frequency: 'Quarterly' },
    DYNAMIC: { amount: 0, clients: 0, rate: '3.5%/month', frequency: 'Semi-Annual' }
  });
  const [totalObligations, setTotalObligations] = useState(0);
  const [totalClients, setTotalClients] = useState(0);
  
  // UI state
  const [showAllAccounts, setShowAllAccounts] = useState(false);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      // Get auth token
      const token = localStorage.getItem('fidus_token') || localStorage.getItem('token');
      
      if (!token) {
        console.warn('No auth token found');
        setError("Please log in to view fund portfolio data");
        setLoading(false);
        return;
      }
      
      const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      };
      
      // Fetch MT5 accounts (THE FUND)
      const mt5Response = await fetch(`${BACKEND_URL}/api/mt5/accounts/corrected`, { headers });
      const mt5Data = await mt5Response.json();
      
      if (mt5Data.success && mt5Data.accounts) {
        // Calculate total fund assets from ALL accounts (no fund_type filter)
        let totalEquity = 0;
        
        const accounts = mt5Data.accounts.map(acc => {
          const equity = parseFloat(acc.equity || acc.balance || 0);
          const allocation = parseFloat(acc.initial_allocation || 0);
          const pnl = equity - allocation;
          
          totalEquity += equity;
          
          return {
            account: acc.account,
            broker: acc.broker,
            manager: acc.manager_name || 'Unassigned',
            equity: equity,
            allocation: allocation,
            pnl: pnl
          };
        });
        
        // Sort by equity descending
        accounts.sort((a, b) => b.equity - a.equity);
        
        setMt5Accounts(accounts);
        setTotalFundAssets(totalEquity);
        // NOTE: totalPnL will be calculated after we get client money
        // Fund P&L = Total Equity - Client Money (NOT sum of individual account P&Ls)
      }
      
      // Fetch Client Obligations (from investments)
      const investResponse = await fetch(`${BACKEND_URL}/api/admin/client-money/total`, { headers });
      const investData = await investResponse.json();
      
      if (investData.success) {
        // Group by product type
        const obligations = {
          CORE: { amount: 0, clients: new Set(), rate: '1.5%/month', frequency: 'Monthly' },
          BALANCE: { amount: 0, clients: new Set(), rate: '2.5%/month', frequency: 'Quarterly' },
          DYNAMIC: { amount: 0, clients: new Set(), rate: '3.5%/month', frequency: 'Semi-Annual' }
        };
        
        const investments = investData.investments || [];
        investments.forEach(inv => {
          const product = inv.fund_code || inv.fund_type || 'UNKNOWN';
          const amount = parseFloat(inv.principal_amount) || 0;
          // Use client_name as fallback if client_id is missing
          const clientId = inv.client_id || inv.client_name;
          
          if (obligations[product]) {
            obligations[product].amount += amount;
            if (clientId) obligations[product].clients.add(clientId);
          }
        });
        
        // Convert Sets to counts
        const finalObligations = {};
        let total = 0;
        const allClients = new Set();
        
        Object.entries(obligations).forEach(([product, data]) => {
          finalObligations[product] = {
            amount: data.amount,
            clients: data.clients.size,
            rate: data.rate,
            frequency: data.frequency
          };
          total += data.amount;
          data.clients.forEach(c => allClients.add(c));
        });
        
        setClientObligations(finalObligations);
        setTotalObligations(total);
        setTotalClients(allClients.size);
        
        // CORRECT Fund P&L Calculation:
        // Fund P&L = Total Equity (Fund Assets) - Total Client Money (Obligations)
        // This is the TRUE profit/loss for the fund
        const correctPnL = totalFundAssets - total;
        setTotalPnL(correctPnL);
      }
      
    } catch (err) {
      console.error('Error fetching data:', err);
      setError("Failed to load fund portfolio data");
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(amount || 0);
  };

  // Calculate coverage ratio
  const coverageRatio = totalObligations > 0 
    ? ((totalFundAssets / totalObligations) * 100).toFixed(1)
    : 100;
  
  // Determine health status
  const getHealthStatus = () => {
    const ratio = parseFloat(coverageRatio);
    if (ratio >= 110) return { status: 'Excellent', color: 'emerald', icon: CheckCircle2 };
    if (ratio >= 100) return { status: 'Healthy', color: 'green', icon: CheckCircle2 };
    if (ratio >= 90) return { status: 'Warning', color: 'yellow', icon: AlertTriangle };
    return { status: 'Critical', color: 'red', icon: AlertCircle };
  };
  
  const health = getHealthStatus();
  const HealthIcon = health.icon;

  // Prepare pie chart data for client obligations
  const obligationsPieData = Object.entries(clientObligations)
    .filter(([_, data]) => data.amount > 0)
    .map(([product, data]) => ({
      name: `${product} Product`,
      value: data.amount,
      product: product
    }));

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <RefreshCw className="w-8 h-8 text-cyan-400 animate-spin mr-3" />
        <div className="text-white text-xl">Loading fund portfolio data...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center">
            <Building2 className="mr-3 h-8 w-8 text-cyan-400" />
            Fund Portfolio
          </h2>
          <p className="text-slate-400 text-sm mt-1">
            THE FUND is one pool • Client products determine obligations
          </p>
        </div>
        <div className="flex items-center gap-4">
          <div className={`px-4 py-2 rounded-full bg-${health.color}-500/20 border border-${health.color}-500/30 flex items-center gap-2`}>
            <HealthIcon className={`w-5 h-5 text-${health.color}-400`} />
            <span className={`text-${health.color}-400 font-semibold`}>
              Fund Status: {health.status}
            </span>
          </div>
          <Button
            onClick={fetchData}
            className="bg-cyan-600 hover:bg-cyan-700"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {error && (
        <div className="bg-red-900/20 border border-red-600 rounded-lg p-3">
          <p className="text-red-400">{error}</p>
        </div>
      )}

      {/* ================================================================== */}
      {/* FUND OVERVIEW - THE FUND (One Pool) */}
      {/* ================================================================== */}
      <Card className="dashboard-card border-2 border-cyan-500/30 bg-gradient-to-br from-cyan-900/20 to-slate-900">
        <CardHeader>
          <CardTitle className="text-white flex items-center text-xl">
            <Wallet className="mr-3 h-6 w-6 text-cyan-400" />
            FUND OVERVIEW
            <Badge className="ml-3 bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">
              THE FUND - One Pool
            </Badge>
          </CardTitle>
          <p className="text-slate-400 text-sm">
            Sum of ALL MT5 accounts across all brokers (not divided by product type)
          </p>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {/* Total Fund Assets */}
            <div className="bg-gradient-to-br from-cyan-500/10 to-blue-500/10 rounded-xl p-5 border border-cyan-500/20">
              <div className="flex items-center justify-between mb-2">
                <span className="text-slate-400 text-sm">Total Fund Assets</span>
                <DollarSign className="w-6 h-6 text-cyan-400" />
              </div>
              <p className="text-3xl font-bold text-cyan-400">{formatCurrency(totalFundAssets)}</p>
              <p className="text-xs text-slate-500 mt-2">Real-time from {mt5Accounts.length} MT5 accounts</p>
            </div>

            {/* Total Client Obligations */}
            <div className="bg-gradient-to-br from-purple-500/10 to-pink-500/10 rounded-xl p-5 border border-purple-500/20">
              <div className="flex items-center justify-between mb-2">
                <span className="text-slate-400 text-sm">Client Obligations</span>
                <PiggyBank className="w-6 h-6 text-purple-400" />
              </div>
              <p className="text-3xl font-bold text-purple-400">{formatCurrency(totalObligations)}</p>
              <p className="text-xs text-slate-500 mt-2">What FIDUS owes to {totalClients} clients</p>
            </div>

            {/* Coverage Ratio */}
            <div className={`bg-gradient-to-br from-${health.color}-500/10 to-${health.color}-600/10 rounded-xl p-5 border border-${health.color}-500/20`}>
              <div className="flex items-center justify-between mb-2">
                <span className="text-slate-400 text-sm">Coverage Ratio</span>
                <Shield className={`w-6 h-6 text-${health.color}-400`} />
              </div>
              <p className={`text-3xl font-bold text-${health.color}-400`}>{coverageRatio}%</p>
              <p className="text-xs text-slate-500 mt-2">
                {parseFloat(coverageRatio) >= 100 ? '✅ Can meet all obligations' : '⚠️ Below obligations'}
              </p>
            </div>

            {/* Fund P&L */}
            <div className={`bg-gradient-to-br ${totalPnL >= 0 ? 'from-green-500/10 to-emerald-500/10' : 'from-red-500/10 to-orange-500/10'} rounded-xl p-5 border ${totalPnL >= 0 ? 'border-green-500/20' : 'border-red-500/20'}`}>
              <div className="flex items-center justify-between mb-2">
                <span className="text-slate-400 text-sm">Fund P&L</span>
                {totalPnL >= 0 ? (
                  <TrendingUp className="w-6 h-6 text-green-400" />
                ) : (
                  <TrendingDown className="w-6 h-6 text-red-400" />
                )}
              </div>
              <p className={`text-3xl font-bold ${totalPnL >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {totalPnL >= 0 ? '+' : ''}{formatCurrency(totalPnL)}
              </p>
              <p className="text-xs text-slate-500 mt-2">Trading profits/losses</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* ================================================================== */}
      {/* CLIENT OBLIGATIONS BY PRODUCT */}
      {/* ================================================================== */}
      <Card className="dashboard-card border-2 border-purple-500/30">
        <CardHeader>
          <CardTitle className="text-white flex items-center text-xl">
            <PiggyBank className="mr-3 h-6 w-6 text-purple-400" />
            CLIENT OBLIGATIONS BY PRODUCT
            <Badge className="ml-3 bg-purple-500/20 text-purple-400 border border-purple-500/30">
              What FIDUS Owes
            </Badge>
          </CardTitle>
          <p className="text-slate-400 text-sm">
            Products determine payment schedule and interest rates - NOT how the fund deploys capital
          </p>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Pie Chart */}
            <div className="flex items-center justify-center">
              {obligationsPieData.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <RechartsPieChart>
                    <Pie
                      data={obligationsPieData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name.replace(' Product', '')}: ${(percent * 100).toFixed(1)}%`}
                      outerRadius={100}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {obligationsPieData.map((entry, index) => (
                        <Cell 
                          key={`cell-${index}`} 
                          fill={PRODUCT_COLORS[entry.product] || '#64748b'}
                          stroke="#1e293b"
                          strokeWidth={2}
                        />
                      ))}
                    </Pie>
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: '#1e293b', 
                        border: '1px solid #334155',
                        borderRadius: '6px',
                        color: '#fff'
                      }}
                      formatter={(value) => [formatCurrency(value), 'Principal']}
                    />
                  </RechartsPieChart>
                </ResponsiveContainer>
              ) : (
                <div className="text-slate-400">No client obligations</div>
              )}
            </div>

            {/* Product Details */}
            <div className="space-y-4">
              <div className="text-center lg:text-left mb-4">
                <div className="text-3xl font-bold text-white">
                  {formatCurrency(totalObligations)}
                </div>
                <div className="text-sm text-slate-400">Total Principal Obligations ({totalClients} clients)</div>
              </div>

              {Object.entries(clientObligations).map(([product, data]) => {
                const percentage = totalObligations > 0 
                  ? ((data.amount / totalObligations) * 100).toFixed(1)
                  : 0;
                
                return (
                  <div key={product} className="p-4 bg-slate-800/50 rounded-lg border border-slate-700/50">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center">
                        <div 
                          className="w-4 h-4 rounded-full mr-3"
                          style={{ backgroundColor: PRODUCT_COLORS[product] }}
                        ></div>
                        <div>
                          <div className="text-lg font-semibold text-white">{product} Product</div>
                          <div className="text-xs text-slate-400">
                            {data.rate} • {data.frequency} payments
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-xl font-bold text-white">
                          {formatCurrency(data.amount)}
                        </div>
                        <div className="text-xs text-slate-400">
                          {data.clients} client{data.clients !== 1 ? 's' : ''} • {percentage}%
                        </div>
                      </div>
                    </div>
                    
                    {/* Progress bar */}
                    <div className="w-full bg-slate-700 rounded-full h-2 mt-2">
                      <div 
                        className="h-2 rounded-full transition-all duration-500"
                        style={{ 
                          width: `${percentage}%`,
                          backgroundColor: PRODUCT_COLORS[product]
                        }}
                      ></div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* ================================================================== */}
      {/* MT5 ACCOUNTS (THE FUND) */}
      {/* ================================================================== */}
      <Card className="dashboard-card">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-white flex items-center text-xl">
                <Activity className="mr-3 h-6 w-6 text-cyan-400" />
                MT5 ACCOUNTS (THE FUND)
              </CardTitle>
              <p className="text-slate-400 text-sm mt-1">
                All trading accounts that generate returns • NOT divided by product type
              </p>
            </div>
            <Button
              variant="outline"
              onClick={() => setShowAllAccounts(!showAllAccounts)}
              className="border-slate-600 text-slate-300"
            >
              {showAllAccounts ? (
                <>
                  <ChevronUp className="w-4 h-4 mr-2" />
                  Show Top 10
                </>
              ) : (
                <>
                  <ChevronDown className="w-4 h-4 mr-2" />
                  Show All ({mt5Accounts.length})
                </>
              )}
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-700">
                  <th className="text-left py-3 px-4 text-slate-400 font-medium">Account</th>
                  <th className="text-left py-3 px-4 text-slate-400 font-medium">Broker</th>
                  <th className="text-left py-3 px-4 text-slate-400 font-medium">Manager</th>
                  <th className="text-right py-3 px-4 text-slate-400 font-medium">Equity</th>
                  <th className="text-right py-3 px-4 text-slate-400 font-medium">Allocation</th>
                  <th className="text-right py-3 px-4 text-slate-400 font-medium">P&L</th>
                </tr>
              </thead>
              <tbody>
                {(showAllAccounts ? mt5Accounts : mt5Accounts.slice(0, 10)).map((acc, idx) => (
                  <tr key={idx} className="border-b border-slate-800 hover:bg-slate-800/50">
                    <td className="py-3 px-4 text-white font-mono">{acc.account}</td>
                    <td className="py-3 px-4 text-slate-300">{acc.broker}</td>
                    <td className="py-3 px-4 text-slate-300">{acc.manager}</td>
                    <td className="py-3 px-4 text-right text-cyan-400 font-semibold">
                      {formatCurrency(acc.equity)}
                    </td>
                    <td className="py-3 px-4 text-right text-slate-400">
                      {formatCurrency(acc.allocation)}
                    </td>
                    <td className={`py-3 px-4 text-right font-semibold ${acc.pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {acc.pnl >= 0 ? '+' : ''}{formatCurrency(acc.pnl)}
                    </td>
                  </tr>
                ))}
              </tbody>
              <tfoot>
                <tr className="border-t-2 border-cyan-500/30 bg-slate-800/50">
                  <td colSpan="3" className="py-4 px-4 text-white font-bold">
                    TOTAL FUND ASSETS
                  </td>
                  <td className="py-4 px-4 text-right text-cyan-400 font-bold text-lg">
                    {formatCurrency(totalFundAssets)}
                  </td>
                  <td className="py-4 px-4 text-right text-slate-400">
                    {formatCurrency(mt5Accounts.reduce((sum, a) => sum + a.allocation, 0))}
                  </td>
                  <td className={`py-4 px-4 text-right font-bold text-lg ${totalPnL >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {totalPnL >= 0 ? '+' : ''}{formatCurrency(totalPnL)}
                  </td>
                </tr>
              </tfoot>
            </table>
          </div>
          
          {/* Summary note */}
          <div className="mt-4 p-4 bg-slate-800/30 rounded-lg border border-slate-700/50">
            <p className="text-sm text-slate-400">
              <span className="text-cyan-400 font-semibold">Note:</span> These MT5 accounts are "THE FUND" - 
              a single pool of capital used to generate returns. The fund is NOT divided by client product type. 
              Client products (CORE, BALANCE, DYNAMIC) only determine what FIDUS owes each client.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default FundPortfolioManagement;
