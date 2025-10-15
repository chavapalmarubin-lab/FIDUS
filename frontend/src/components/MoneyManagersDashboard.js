import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { 
  Users, 
  TrendingUp, 
  TrendingDown,
  DollarSign,
  Target,
  BarChart3,
  Eye,
  Edit,
  Copy,
  Building2,
  AlertCircle,
  RefreshCw,
  Plus,
  ExternalLink,
  Activity
} from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';
import apiAxios from "../utils/apiAxios";
import mt5Service from "../services/mt5Service"; // PHASE 4A

const MoneyManagersDashboard = () => {
  const [managers, setManagers] = useState([]);
  const [selectedManager, setSelectedManager] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [viewMode, setViewMode] = useState('overview'); // overview, comparison, detailed
  
  // PHASE 4A: MT5 Manager Performance state
  const [mt5Performance, setMt5Performance] = useState([]);
  const [mt5Loading, setMt5Loading] = useState(false);
  const [mt5Period, setMt5Period] = useState('30d'); // 7d, 30d, 90d

  useEffect(() => {
    fetchManagers();
  }, []);

  const fetchManagers = async () => {
    try {
      setLoading(true);
      setError("");

      // Try to fetch managers from API
      try {
        const response = await apiAxios.get('/admin/money-managers');
        
        if (response.data.success) {
          setManagers(response.data.managers);
        } else {
          throw new Error(response.data.error || "Failed to fetch managers");
        }
      } catch (apiError) {
        // If API fails, try to initialize managers first
        console.warn("Managers API not ready, attempting initialization...");
        
        try {
          const initResponse = await apiAxios.post('/admin/money-managers/initialize');
          if (initResponse.data.success) {
            // After successful initialization, try to fetch again
            const fetchResponse = await apiAxios.get('/admin/money-managers');
            if (fetchResponse.data.success) {
              setManagers(fetchResponse.data.managers);
            } else {
              throw new Error("Failed to fetch after initialization");
            }
          } else {
            throw new Error("Failed to initialize managers");
          }
        } catch (initError) {
          console.warn("API returned no manager data");
          setManagers([]);
          setError("No money manager data available");
        }
      }

    } catch (err) {
      console.error("Money managers fetch error:", err);
      setError("Failed to load money managers data");
    } finally {
      setLoading(false);
    }
  };

  // PHASE 3: Mock data generator REMOVED - using real API data only

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(amount || 0);
  };

  const formatPercentage = (value) => {
    return `${(value || 0).toFixed(2)}%`;
  };

  const getExecutionTypeIcon = (type) => {
    return type === 'copy_trade' ? Copy : Building2;
  };

  const getRiskProfileColor = (risk) => {
    switch (risk) {
      case 'high': return 'text-red-400 border-red-400';
      case 'medium': return 'text-yellow-400 border-yellow-400';
      case 'low': return 'text-green-400 border-green-400';
      default: return 'text-slate-400 border-slate-400';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-white text-xl flex items-center">
          <RefreshCw className="animate-spin mr-2" />
          Loading money managers...
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white flex items-center">
          <Users className="mr-3 h-8 w-8 text-cyan-400" />
          Money Managers
        </h2>
        
        <div className="flex items-center space-x-3">
          <Button 
            onClick={() => setViewMode('overview')}
            variant={viewMode === 'overview' ? 'default' : 'outline'}
            className="text-white"
          >
            Overview
          </Button>
          <Button 
            onClick={() => setViewMode('comparison')}
            variant={viewMode === 'comparison' ? 'default' : 'outline'}
            className="text-white"
          >
            Compare
          </Button>
          <Button 
            onClick={fetchManagers}
            className="bg-cyan-600 hover:bg-cyan-700"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Subtitle */}
      <p className="text-slate-400">
        Manage and compare trading strategies across different money managers and execution methods
      </p>

      {/* Error Display */}
      {error && (
        <div className="bg-red-900/20 border border-red-600 rounded-lg p-4">
          <div className="flex items-center">
            <AlertCircle className="h-5 w-5 text-red-400 mr-2" />
            <p className="text-red-400">{error}</p>
          </div>
        </div>
      )}

      {/* Phase 1 Development Notice */}
      <div className="bg-blue-900/20 border border-blue-600 rounded-lg p-4">
        <div className="flex items-center">
          <Activity className="h-5 w-5 text-blue-400 mr-2" />
          <div>
            <p className="text-blue-400 font-medium">Phase 1: Money Managers Profile System</p>
            <p className="text-blue-300 text-sm mt-1">
              Basic manager profiles and performance tracking. {managers.length} managers configured 
              across Copy Trade and MAM execution types.
            </p>
          </div>
        </div>
      </div>

      {viewMode === 'overview' && (
        <>
          {/* PHASE 2: Performance Comparison Bar Chart */}
          <Card className="dashboard-card mb-8">
            <CardHeader>
              <CardTitle className="text-white flex items-center">
                <BarChart3 className="mr-2 h-5 w-5 text-cyan-400" />
                Manager Performance Comparison
              </CardTitle>
              <p className="text-slate-400 text-sm">TRUE P&L and return percentage by manager</p>
            </CardHeader>
            <CardContent>
              {managers && managers.length > 0 ? (
                <ResponsiveContainer width="100%" height={400}>
                  <BarChart
                    data={managers
                      .map(manager => ({
                        name: manager.manager_name || 'Unknown',
                        true_pnl: manager.performance?.true_pnl || 0,
                        return_pct: manager.performance?.return_pct || 0,
                        win_rate: manager.performance?.win_rate || 0,
                        manager_id: manager.manager_id
                      }))
                      .sort((a, b) => b.true_pnl - a.true_pnl)
                    }
                    layout="vertical"
                    margin={{ top: 5, right: 30, left: 100, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis 
                      type="number"
                      stroke="#94a3b8"
                      tick={{ fill: '#94a3b8', fontSize: 12 }}
                      tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
                    />
                    <YAxis 
                      type="category"
                      dataKey="name"
                      stroke="#94a3b8"
                      tick={{ fill: '#94a3b8', fontSize: 12 }}
                      width={90}
                    />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: '#1e293b', 
                        border: '1px solid #334155',
                        borderRadius: '6px',
                        color: '#fff'
                      }}
                      formatter={(value, name) => {
                        if (name === 'true_pnl') return [`$${value.toLocaleString()}`, 'TRUE P&L'];
                        if (name === 'return_pct') return [`${value.toFixed(2)}%`, 'Return'];
                        if (name === 'win_rate') return [`${value.toFixed(2)}%`, 'Win Rate'];
                        return [value, name];
                      }}
                    />
                    <Legend 
                      wrapperStyle={{ color: '#94a3b8' }}
                      formatter={(value) => {
                        if (value === 'true_pnl') return 'TRUE P&L';
                        if (value === 'return_pct') return 'Return %';
                        if (value === 'win_rate') return 'Win Rate %';
                        return value;
                      }}
                    />
                    <Bar 
                      dataKey="true_pnl" 
                      fill="#10b981"
                      radius={[0, 8, 8, 0]}
                    >
                      {managers.map((manager, index) => (
                        <Cell 
                          key={`cell-${index}`}
                          fill={manager.performance?.true_pnl >= 0 ? '#10b981' : '#ef4444'}
                        />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex items-center justify-center h-[400px] text-slate-400">
                  No manager data available
                </div>
              )}
            </CardContent>
          </Card>

          {/* Managers Overview Cards */}
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
            {managers.map((manager) => {
              const ExecutionIcon = getExecutionTypeIcon(manager.execution_type);
              const performance = manager.performance || {};
              
              return (
                <motion.div
                  key={manager.manager_id}
                  whileHover={{ scale: 1.02 }}
                  className="group"
                >
                  <Card className="dashboard-card h-full">
                    <CardHeader className="pb-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center">
                          <ExecutionIcon className="h-5 w-5 text-cyan-400 mr-2" />
                          <Badge 
                            className={`${getRiskProfileColor(manager.risk_profile)} bg-transparent border text-xs`}
                          >
                            {manager.risk_profile} risk
                          </Badge>
                        </div>
                        <Badge className={`${manager.status === 'active' ? 'bg-green-600' : 'bg-slate-600'} text-white`}>
                          {manager.status}
                        </Badge>
                      </div>
                      
                      <CardTitle className="text-white text-lg">
                        {manager.display_name || manager.name}
                      </CardTitle>
                      <p className="text-slate-400 text-sm">
                        {manager.strategy_name}
                      </p>
                    </CardHeader>
                    
                    <CardContent className="space-y-4">
                      {/* Execution Details */}
                      <div className="bg-slate-800/30 rounded p-3">
                        <div className="text-xs text-slate-400 mb-2">Execution Method</div>
                        <div className="flex items-center justify-between">
                          <span className="text-white font-medium">
                            {manager.execution_type === 'copy_trade' ? 'Copy Trade' : 'MAM'}
                          </span>
                          <span className="text-slate-300 text-sm">
                            {manager.broker}
                          </span>
                        </div>
                      </div>

                      {/* Account Assignment */}
                      <div>
                        <div className="text-xs text-slate-400 mb-2">
                          Assigned Accounts ({manager.assigned_accounts?.length || 0})
                        </div>
                        {manager.account_details?.map((account) => (
                          <div key={account.account} className="flex items-center justify-between py-1">
                            <span className="text-slate-300 text-sm">
                              {account.account} ({account.name})
                            </span>
                            <span className="text-cyan-400 text-sm font-medium">
                              {formatCurrency(account.allocation)}
                            </span>
                          </div>
                        ))}
                      </div>

                      {/* Performance Metrics */}
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <span className="text-slate-400 text-sm">Initial Allocation:</span>
                          <span className="text-white font-bold">
                            {formatCurrency(performance.total_allocated)}
                          </span>
                        </div>
                        
                        {/* NEW: Current Equity */}
                        <div className="flex items-center justify-between">
                          <span className="text-slate-400 text-sm">Current Equity:</span>
                          <span className="text-cyan-400 font-medium">
                            {formatCurrency(performance.current_equity || 0)}
                          </span>
                        </div>
                        
                        {/* NEW: Withdrawals */}
                        <div className="flex items-center justify-between">
                          <span className="text-slate-400 text-sm">Withdrawals:</span>
                          <span className="text-blue-400 font-medium">
                            {formatCurrency(performance.total_withdrawals || 0)}
                          </span>
                        </div>
                        
                        <div className="flex items-center justify-between">
                          <span className="text-slate-400 text-sm">TRUE P&L:</span>
                          <span className={`font-bold flex items-center ${
                            performance.total_pnl >= 0 ? 'text-green-400' : 'text-red-400'
                          }`}>
                            {performance.total_pnl >= 0 ? (
                              <TrendingUp className="w-3 h-3 mr-1" />
                            ) : (
                              <TrendingDown className="w-3 h-3 mr-1" />
                            )}
                            {formatCurrency(performance.total_pnl)}
                            <span className="text-xs ml-1">
                              ({performance.return_percentage >= 0 ? '+' : ''}{formatPercentage(performance.return_percentage)})
                            </span>
                          </span>
                        </div>
                        
                        <div className="text-xs text-slate-500 bg-slate-800/50 p-2 rounded">
                          ✓ Corrected: Equity ({formatCurrency(performance.current_equity || 0)}) + Withdrawals ({formatCurrency(performance.total_withdrawals || 0)})
                        </div>
                        
                        <div className="flex items-center justify-between">
                          <span className="text-slate-400 text-sm">Win Rate:</span>
                          <span className="text-cyan-400 font-medium">
                            {formatPercentage(performance.win_rate)}
                            <span className="text-xs text-slate-400 ml-1">
                              ({performance.winning_trades}W/{performance.total_trades}T)
                            </span>
                          </span>
                        </div>
                        
                        <div className="flex items-center justify-between">
                          <span className="text-slate-400 text-sm">Profit Factor:</span>
                          <span className={`font-medium ${
                            performance.profit_factor >= 1.5 ? 'text-green-400' : 
                            performance.profit_factor >= 1.0 ? 'text-yellow-400' : 'text-red-400'
                          }`}>
                            {performance.profit_factor?.toFixed(2)}
                          </span>
                        </div>
                      </div>

                      {/* Action Buttons */}
                      <div className="flex space-x-2 pt-3 border-t border-slate-700">
                        {manager.profile_url && (
                          <Button 
                            size="sm" 
                            variant="outline"
                            onClick={() => window.open(manager.profile_url, '_blank')}
                            className="flex-1 text-white border-slate-600 hover:bg-slate-700"
                          >
                            <ExternalLink className="w-3 h-3 mr-1" />
                            Profile
                          </Button>
                        )}
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => setSelectedManager(manager)}
                          className="flex-1 text-white border-slate-600 hover:bg-slate-700"
                        >
                          <Eye className="w-3 h-3 mr-1" />
                          Details
                        </Button>
                        <Button 
                          size="sm" 
                          variant="outline"
                          className="flex-1 text-white border-slate-600 hover:bg-slate-700"
                        >
                          <Edit className="w-3 h-3 mr-1" />
                          Edit
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              );
            })}
          </div>

          {/* Manager Comparison Table */}
          <Card className="dashboard-card">
            <CardHeader>
              <CardTitle className="text-white flex items-center">
                <BarChart3 className="mr-2 h-5 w-5 text-cyan-400" />
                Manager Comparison Table
              </CardTitle>
              <p className="text-slate-400 text-sm">
                Side-by-side comparison of all money managers
              </p>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-slate-600">
                      <th className="text-left text-slate-400 font-medium py-3">Manager</th>
                      <th className="text-left text-slate-400 font-medium py-3">Execution</th>
                      <th className="text-right text-slate-400 font-medium py-3">Accounts</th>
                      <th className="text-right text-slate-400 font-medium py-3">Allocated</th>
                      <th className="text-right text-slate-400 font-medium py-3">Equity</th>
                      <th className="text-right text-slate-400 font-medium py-3">Withdrawals</th>
                      <th className="text-right text-slate-400 font-medium py-3">TRUE P&L</th>
                      <th className="text-right text-slate-400 font-medium py-3">Win Rate</th>
                      <th className="text-right text-slate-400 font-medium py-3">PF</th>
                    </tr>
                  </thead>
                  <tbody>
                    {managers.map((manager) => {
                      const performance = manager.performance || {};
                      return (
                        <tr 
                          key={manager.manager_id} 
                          className="border-b border-slate-700/50 hover:bg-slate-800/30 cursor-pointer"
                          onClick={() => setSelectedManager(manager)}
                        >
                          <td className="py-4">
                            <div>
                              <div className="text-white font-medium">
                                {manager.display_name || manager.name}
                              </div>
                              <div className="text-slate-400 text-xs">
                                {manager.strategy_name}
                              </div>
                            </div>
                          </td>
                          <td className="py-4">
                            <Badge className={`${
                              manager.execution_type === 'copy_trade' ? 'bg-blue-700' : 'bg-purple-700'
                            } text-white`}>
                              {manager.execution_type === 'copy_trade' ? 'Copy' : 'MAM'}
                            </Badge>
                          </td>
                          <td className="py-4 text-right text-white">
                            {manager.assigned_accounts?.length || 0}
                          </td>
                          <td className="py-4 text-right text-white font-medium">
                            {formatCurrency(performance.total_allocated)}
                          </td>
                          <td className="py-4 text-right text-cyan-400 font-medium">
                            {formatCurrency(performance.current_equity || 0)}
                          </td>
                          <td className="py-4 text-right text-blue-400 font-medium">
                            {formatCurrency(performance.total_withdrawals || 0)}
                          </td>
                          <td className={`py-4 text-right font-medium ${
                            performance.total_pnl >= 0 ? 'text-green-400' : 'text-red-400'
                          }`}>
                            {performance.total_pnl >= 0 ? '+' : ''}{formatCurrency(performance.total_pnl)}
                          </td>
                          <td className="py-4 text-right text-cyan-400 font-medium">
                            {formatPercentage(performance.win_rate)}
                          </td>
                          <td className={`py-4 text-right font-medium ${
                            performance.profit_factor >= 1.5 ? 'text-green-400' : 
                            performance.profit_factor >= 1.0 ? 'text-yellow-400' : 'text-red-400'
                          }`}>
                            {performance.profit_factor?.toFixed(2)}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
              
              {managers.length === 0 && (
                <div className="text-center py-8">
                  <Users className="mx-auto h-12 w-12 mb-4 text-slate-400 opacity-50" />
                  <p className="text-slate-400">No money managers found</p>
                </div>
              )}
            </CardContent>
          </Card>
        </>
      )}

      {/* Manager Details Modal */}
      <AnimatePresence>
        {selectedManager && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
            onClick={() => setSelectedManager(null)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-slate-900 rounded-lg p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-bold text-white">
                  Manager Profile: {selectedManager.display_name || selectedManager.name}
                </h3>
                <Button 
                  onClick={() => setSelectedManager(null)}
                  variant="outline"
                  size="sm"
                  className="text-white"
                >
                  Close
                </Button>
              </div>

              <div className="space-y-6">
                {/* Manager Information */}
                <div>
                  <h4 className="text-white font-medium mb-3">Manager Information</h4>
                  <div className="bg-slate-800/50 rounded p-4 space-y-2">
                    <div className="flex justify-between">
                      <span className="text-slate-400">Manager ID:</span>
                      <span className="text-white">{selectedManager.manager_id}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Execution Type:</span>
                      <span className="text-white">
                        {selectedManager.execution_type === 'copy_trade' ? 'Copy Trade' : 'MAM'}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Broker:</span>
                      <span className="text-white">{selectedManager.broker}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Risk Profile:</span>
                      <Badge className={`${getRiskProfileColor(selectedManager.risk_profile)} bg-transparent border`}>
                        {selectedManager.risk_profile}
                      </Badge>
                    </div>
                  </div>
                </div>

                {/* Strategy Description */}
                {selectedManager.strategy_description && (
                  <div>
                    <h4 className="text-white font-medium mb-3">Strategy Description</h4>
                    <div className="bg-slate-800/50 rounded p-4">
                      <p className="text-slate-300 text-sm leading-relaxed">
                        {selectedManager.strategy_description}
                      </p>
                    </div>
                  </div>
                )}

                {/* Assigned Accounts */}
                <div>
                  <h4 className="text-white font-medium mb-3">Assigned Accounts</h4>
                  <div className="space-y-3">
                    {selectedManager.account_details?.map((account) => (
                      <div key={account.account} className="bg-slate-800/50 rounded p-4">
                        <div className="flex justify-between items-center mb-2">
                          <span className="text-white font-medium">
                            Account {account.account} ({account.name})
                          </span>
                          <Badge className="bg-green-600 text-white">
                            Active
                          </Badge>
                        </div>
                        <div className="grid grid-cols-2 gap-4 text-sm">
                          <div className="flex justify-between">
                            <span className="text-slate-400">Allocation:</span>
                            <span className="text-white">{formatCurrency(account.allocation)}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-slate-400">Current Equity:</span>
                            <span className="text-white">{formatCurrency(account.current_equity)}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-slate-400">P&L:</span>
                            <span className={account.pnl >= 0 ? 'text-green-400' : 'text-red-400'}>
                              {account.pnl >= 0 ? '+' : ''}{formatCurrency(account.pnl)}
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-slate-400">Return %:</span>
                            <span className={account.pnl >= 0 ? 'text-green-400' : 'text-red-400'}>
                              {((account.pnl / account.allocation) * 100).toFixed(2)}%
                            </span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Combined Performance */}
                <div>
                  <h4 className="text-white font-medium mb-3">Combined Performance</h4>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    <div className="bg-slate-800/50 rounded p-3 text-center">
                      <div className="text-2xl font-bold text-cyan-400">
                        {formatCurrency(selectedManager.performance?.total_pnl || 0)}
                      </div>
                      <div className="text-xs text-slate-400">Total P&L</div>
                    </div>
                    <div className="bg-slate-800/50 rounded p-3 text-center">
                      <div className="text-2xl font-bold text-green-400">
                        {formatPercentage(selectedManager.performance?.win_rate || 0)}
                      </div>
                      <div className="text-xs text-slate-400">Win Rate</div>
                    </div>
                    <div className="bg-slate-800/50 rounded p-3 text-center">
                      <div className="text-2xl font-bold text-purple-400">
                        {selectedManager.performance?.profit_factor?.toFixed(2) || '0.00'}
                      </div>
                      <div className="text-xs text-slate-400">Profit Factor</div>
                    </div>
                  </div>
                </div>

                {/* Profile Widget */}
                {selectedManager.profile_url && (
                  <div>
                    <h4 className="text-white font-medium mb-3">MexAtlantic Profile</h4>
                    <div className="bg-slate-800/50 rounded p-4">
                      <div className="flex items-center justify-between mb-3">
                        <span className="text-slate-300">External Profile</span>
                        <Button
                          size="sm"
                          onClick={() => window.open(selectedManager.profile_url, '_blank')}
                          className="bg-cyan-600 hover:bg-cyan-700"
                        >
                          <ExternalLink className="w-3 h-3 mr-1" />
                          View on MexAtlantic
                        </Button>
                      </div>
                      <p className="text-slate-400 text-sm">
                        Click the button above to view detailed ratings and performance statistics 
                        on the MexAtlantic platform.
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default MoneyManagersDashboard;