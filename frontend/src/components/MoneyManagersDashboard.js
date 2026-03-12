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
  Activity,
  Calendar
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
  
  // Allocation date edit state
  const [editingAllocationDate, setEditingAllocationDate] = useState(false);
  const [newAllocationDate, setNewAllocationDate] = useState('');
  const [savingDate, setSavingDate] = useState(false);

  // Edit modal state
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [editingAccount, setEditingAccount] = useState(null);
  const [editFormData, setEditFormData] = useState({
    manager_name: '',
    initial_allocation: '',
    allocation_start_date: '',
    notes: '',
    copy_sources: []
  });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchManagers();
  }, []);

  const fetchManagers = async () => {
    try {
      setLoading(true);
      setError("");

      // Fetch managers from new SSOT endpoint
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/v2/derived/money-managers`);
      const data = await response.json();
      
      if (data.success) {
        // Convert managers object to array for easier iteration
        const managersArray = Object.values(data.managers);
        setManagers(managersArray);
      } else {
        throw new Error(data.message || "Failed to fetch managers");
      }

    } catch (err) {
      console.error("Money managers fetch error:", err);
      setError("Failed to load money managers data");
      setManagers([]);
    } finally {
      setLoading(false);
    }
  };

  // PHASE 4A: Fetch MT5 Manager Performance by Magic Number
  const fetchMT5Performance = async () => {
    try {
      setMt5Loading(true);
      
      const dateRange = mt5Service.getDateRangeForPeriod(mt5Period);
      
      const response = await mt5Service.getManagerPerformance({
        start_date: dateRange.start_date,
        end_date: dateRange.end_date
      });
      
      if (response.success) {
        setMt5Performance(response.managers);
        console.log(`✅ [Phase 4A] Fetched MT5 performance for ${response.count} managers`);
      }
    } catch (error) {
      console.error('❌ [Phase 4A] Error fetching MT5 manager performance:', error);
    } finally {
      setMt5Loading(false);
    }
  };

  // PHASE 4A: Fetch MT5 performance when component mounts or period changes
  useEffect(() => {
    fetchMT5Performance();
  }, [mt5Period]);

  // Save allocation date for a manager
  const saveAllocationDate = async (managerName) => {
    if (!newAllocationDate) {
      alert('Please select a date');
      return;
    }
    
    setSavingDate(true);
    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/v2/managers/allocation-date?manager_name=${encodeURIComponent(managerName)}&allocation_start_date=${newAllocationDate}`,
        { method: 'POST' }
      );
      
      if (response.ok) {
        const data = await response.json();
        console.log('✅ Allocation date saved:', data);
        // Refresh managers data
        fetchManagers();
        setEditingAllocationDate(false);
        setNewAllocationDate('');
      } else {
        const errorData = await response.json();
        alert(`Failed to save: ${errorData.detail || 'Unknown error'}`);
      }
    } catch (err) {
      console.error('Error saving allocation date:', err);
      alert('Failed to save allocation date');
    } finally {
      setSavingDate(false);
    }
  };

  // Open edit modal for an account
  const openEditModal = (account, managerName) => {
    setEditingAccount({ ...account, managerName });
    setEditFormData({
      manager_name: managerName || '',
      initial_allocation: account.allocation || '',
      allocation_start_date: account.allocation_start_date ? account.allocation_start_date.split('T')[0] : '',
      notes: account.notes || '',
      copy_sources: account.copy_sources || []
    });
    setEditModalOpen(true);
  };

  // Close edit modal
  const closeEditModal = () => {
    setEditModalOpen(false);
    setEditingAccount(null);
    setEditFormData({
      manager_name: '',
      initial_allocation: '',
      allocation_start_date: '',
      notes: '',
      copy_sources: []
    });
  };

  // Add a new copy source
  const addCopySource = () => {
    setEditFormData(prev => ({
      ...prev,
      copy_sources: [
        ...prev.copy_sources,
        {
          master_account: '',
          master_broker: 'LUCRUM',
          master_name: '',
          copy_type: 'ratio',
          ratio: 0.5,
          fixed_lot: null
        }
      ]
    }));
  };

  // Remove a copy source
  const removeCopySource = (index) => {
    setEditFormData(prev => ({
      ...prev,
      copy_sources: prev.copy_sources.filter((_, i) => i !== index)
    }));
  };

  // Update a copy source field
  const updateCopySource = (index, field, value) => {
    setEditFormData(prev => ({
      ...prev,
      copy_sources: prev.copy_sources.map((source, i) => {
        if (i === index) {
          const updated = { ...source, [field]: value };
          // Clear ratio/fixed_lot based on copy_type
          if (field === 'copy_type') {
            if (value === 'ratio') {
              updated.fixed_lot = null;
              updated.ratio = updated.ratio || 0.5;
            } else {
              updated.ratio = null;
              updated.fixed_lot = updated.fixed_lot || 0.1;
            }
          }
          return updated;
        }
        return source;
      })
    }));
  };

  // Save account profile and copy sources
  const saveAccountEdit = async () => {
    if (!editingAccount) return;
    
    setSaving(true);
    try {
      // Update profile
      const profileResponse = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/v2/accounts/${editingAccount.account}/profile`,
        {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            manager_name: editFormData.manager_name,
            initial_allocation: parseFloat(editFormData.initial_allocation) || 0,
            allocation_start_date: editFormData.allocation_start_date || null,
            notes: editFormData.notes
          })
        }
      );

      if (!profileResponse.ok) {
        const errorData = await profileResponse.json();
        throw new Error(errorData.detail || 'Failed to update profile');
      }

      // Update copy sources
      const copyResponse = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/v2/accounts/${editingAccount.account}/copy-sources`,
        {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(editFormData.copy_sources.map(source => ({
            ...source,
            master_account: parseInt(source.master_account) || 0,
            ratio: source.copy_type === 'ratio' ? parseFloat(source.ratio) : null,
            fixed_lot: source.copy_type === 'fixed_lot' ? parseFloat(source.fixed_lot) : null
          })))
        }
      );

      if (!copyResponse.ok) {
        const errorData = await copyResponse.json();
        throw new Error(errorData.detail || 'Failed to update copy sources');
      }

      console.log('✅ Account updated successfully');
      closeEditModal();
      fetchManagers(); // Refresh data
    } catch (err) {
      console.error('Error saving account:', err);
      alert(`Failed to save: ${err.message}`);
    } finally {
      setSaving(false);
    }
  };

  // PHASE 3: Mock data generator REMOVED - using real API data only

  // Filter managers to hide those with no allocations (except IB COMMISSIONS)
  const filteredManagers = managers.filter(manager => {
    // Always show IB COMMISSIONS
    if (manager.name?.toUpperCase().includes('IB COMMISSIONS') || 
        manager.name?.toUpperCase().includes('COMMISSIONS')) {
      return true;
    }
    // Show managers with total allocation > 0
    const totalAllocation = manager.account_details?.reduce((sum, acc) => sum + (acc.allocation || 0), 0) || 0;
    return totalAllocation > 0;
  });

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

  const formatDate = (dateStr) => {
    if (!dateStr) return 'Not set';
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
      });
    } catch {
      return 'Not set';
    }
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
          {/* PHASE 2: Performance Comparison Bar Chart - TRUE P&L Only */}
          <Card className="dashboard-card mb-8">
            <CardHeader>
              <CardTitle className="text-white flex items-center">
                <BarChart3 className="mr-2 h-5 w-5 text-cyan-400" />
                Manager Performance Comparison
              </CardTitle>
              <p className="text-slate-400 text-sm">TRUE P&L by manager - Shows actual profit/loss performance</p>
            </CardHeader>
            <CardContent>
              {filteredManagers && filteredManagers.length > 0 ? (
                <ResponsiveContainer width="100%" height={400}>
                  <BarChart
                    data={filteredManagers
                      .map(manager => ({
                        name: manager.manager_name || 'Unknown',
                        true_pnl: manager.performance?.true_pnl || 0,
                        return_pct: manager.performance?.return_pct || 0,
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
                        if (name === 'return_pct') return [`${value.toFixed(2)}%`, 'Return %'];
                        return [value, name];
                      }}
                    />
                    <Legend 
                      wrapperStyle={{ color: '#94a3b8' }}
                      formatter={(value) => {
                        if (value === 'true_pnl') return 'TRUE P&L';
                        return value;
                      }}
                    />
                    <Bar 
                      dataKey="true_pnl" 
                      radius={[0, 8, 8, 0]}
                      name="true_pnl"
                    >
                      {filteredManagers.map((manager, index) => {
                        const performance = manager.performance || {};
                        const truePnl = performance.true_pnl || 0;
                        // Color code based on P&L: green if positive, red if negative, gray if zero
                        const color = truePnl > 0 ? '#10b981' : truePnl < 0 ? '#ef4444' : '#64748b';
                        return (
                          <Cell 
                            key={`cell-${index}`}
                            fill={color}
                          />
                        );
                      })}
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
            {filteredManagers.map((manager) => {
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
                        {manager.manager_name || manager.display_name || manager.name}
                      </CardTitle>
                      <p className="text-slate-400 text-sm">
                        {manager.strategy || manager.strategy_name || 'Active Trading Strategy'}
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
                          <div key={account.account} className="flex items-center justify-between py-1 group">
                            <span className="text-slate-300 text-sm">
                              {account.account} ({account.name})
                            </span>
                            <div className="flex items-center gap-2">
                              <span className="text-cyan-400 text-sm font-medium">
                                {formatCurrency(account.allocation)}
                              </span>
                              <Button
                                size="sm"
                                variant="ghost"
                                className="opacity-0 group-hover:opacity-100 h-6 w-6 p-0 text-slate-400 hover:text-cyan-400"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  openEditModal(account, manager.name);
                                }}
                              >
                                <Edit className="h-3 w-3" />
                              </Button>
                            </div>
                          </div>
                        ))}
                      </div>

                      {/* Copy Configuration - Show if any account has copy_sources */}
                      {manager.account_details?.some(acc => acc.copy_sources?.length > 0) && (
                        <div className="bg-blue-900/20 rounded-lg p-3 border border-blue-700/30">
                          <div className="text-xs text-blue-300 mb-2 flex items-center">
                            <Copy className="w-3 h-3 mr-1" />
                            Copy Trading Configuration
                          </div>
                          {manager.account_details?.map((account) => (
                            account.copy_sources?.length > 0 && (
                              <div key={`copy-${account.account}`} className="mb-2 last:mb-0">
                                <div className="text-xs text-slate-400 mb-1">
                                  Account {account.account}:
                                </div>
                                {account.copy_sources.map((source, idx) => (
                                  <div key={idx} className="flex items-center justify-between py-1 pl-2 border-l-2 border-blue-600/50">
                                    <div className="text-sm">
                                      <span className="text-white">{source.master_broker} </span>
                                      <span className="text-cyan-400 font-mono">{source.master_account}</span>
                                      {source.master_name && (
                                        <span className="text-slate-400 text-xs ml-1">({source.master_name})</span>
                                      )}
                                    </div>
                                    <Badge className={`${source.copy_type === 'ratio' ? 'bg-purple-700' : 'bg-orange-700'} text-white text-xs`}>
                                      {source.copy_type === 'ratio' 
                                        ? `${source.ratio}x ratio` 
                                        : `${source.fixed_lot} lot fixed`}
                                    </Badge>
                                  </div>
                                ))}
                              </div>
                            )
                          ))}
                        </div>
                      )}

                      {/* Performance Metrics */}
                      <div className="space-y-3">
                        {/* SSOT: Display Total Equity as primary metric */}
                        <div className="flex items-center justify-between bg-cyan-900/20 p-3 rounded-lg border border-cyan-700/30">
                          <span className="text-cyan-300 text-sm font-semibold">Total Equity:</span>
                          <span className="text-cyan-400 font-bold text-lg">
                            {formatCurrency(manager.total_equity || 0)}
                          </span>
                        </div>
                        
                        <div className="flex items-center justify-between">
                          <span className="text-slate-400 text-sm">Initial Allocation:</span>
                          <span className="text-white font-medium">
                            {formatCurrency(performance.total_allocated)}
                          </span>
                        </div>
                        
                        {/* Allocation Start Date */}
                        <div className="flex items-center justify-between">
                          <span className="text-slate-400 text-sm flex items-center">
                            <Calendar className="w-3 h-3 mr-1" />
                            Allocation Date:
                          </span>
                          <span className="text-purple-400 font-medium">
                            {formatDate(manager.allocation_start_date)}
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
                      <th className="text-center text-slate-400 font-medium py-3">Alloc Date</th>
                      <th className="text-right text-slate-400 font-medium py-3">Accounts</th>
                      <th className="text-right text-slate-400 font-medium py-3">Allocated</th>
                      <th className="text-right text-slate-400 font-medium py-3">Equity</th>
                      <th className="text-right text-slate-400 font-medium py-3">TRUE P&L</th>
                      <th className="text-right text-slate-400 font-medium py-3">Win Rate</th>
                      <th className="text-right text-slate-400 font-medium py-3">PF</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredManagers.map((manager) => {
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
                                {manager.manager_name || manager.display_name || manager.name}
                              </div>
                              <div className="text-slate-400 text-xs">
                                {manager.strategy || manager.strategy_name || 'Active Trading'}
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
                          <td className="py-4 text-center text-purple-400 text-sm">
                            {formatDate(manager.allocation_start_date)}
                          </td>
                          <td className="py-4 text-right text-white">
                            {manager.assigned_accounts?.length || 0}
                          </td>
                          <td className="py-4 text-right text-white font-medium">
                            {formatCurrency(performance.total_allocated)}
                          </td>
                          <td className="py-4 text-right text-cyan-400 font-medium">
                            {formatCurrency(manager.total_equity || 0)}
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
                  Manager Profile: {selectedManager.manager_name || selectedManager.display_name || selectedManager.name}
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
                    
                    {/* Allocation Start Date - Editable */}
                    <div className="flex justify-between items-center pt-2 border-t border-slate-700">
                      <span className="text-slate-400 flex items-center">
                        <Calendar className="w-4 h-4 mr-1" />
                        Allocation Start Date:
                      </span>
                      {editingAllocationDate ? (
                        <div className="flex items-center gap-2">
                          <input
                            type="date"
                            value={newAllocationDate}
                            onChange={(e) => setNewAllocationDate(e.target.value)}
                            className="px-2 py-1 bg-slate-700 border border-slate-600 text-white text-sm rounded"
                          />
                          <Button
                            size="sm"
                            onClick={() => saveAllocationDate(selectedManager.manager_name)}
                            disabled={savingDate}
                            className="bg-green-600 hover:bg-green-700 text-white h-7"
                          >
                            {savingDate ? 'Saving...' : 'Save'}
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => {
                              setEditingAllocationDate(false);
                              setNewAllocationDate('');
                            }}
                            className="text-white h-7"
                          >
                            Cancel
                          </Button>
                        </div>
                      ) : (
                        <div className="flex items-center gap-2">
                          <span className="text-purple-400 font-medium">
                            {formatDate(selectedManager.allocation_start_date)}
                          </span>
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => {
                              setEditingAllocationDate(true);
                              // Pre-fill with existing date if available
                              if (selectedManager.allocation_start_date) {
                                const d = new Date(selectedManager.allocation_start_date);
                                setNewAllocationDate(d.toISOString().split('T')[0]);
                              }
                            }}
                            className="text-cyan-400 h-7 px-2"
                          >
                            <Edit className="w-3 h-3" />
                          </Button>
                        </div>
                      )}
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

      {/* PHASE 4A: MT5 Manager Performance - Real Deal Data */}
      <Card className="dashboard-card">
        <CardHeader>
          <CardTitle className="text-white flex items-center justify-between">
            <div className="flex items-center">
              <Activity className="mr-2 h-5 w-5 text-cyan-400" />
              MT5 Manager Performance (Real Deal Data)
            </div>
            <div className="flex items-center gap-2">
              <select
                value={mt5Period}
                onChange={(e) => setMt5Period(e.target.value)}
                className="px-3 py-1 bg-slate-700 border border-slate-600 text-white text-sm rounded-md"
              >
                <option value="7d">Last 7 Days</option>
                <option value="30d">Last 30 Days</option>
                <option value="90d">Last 90 Days</option>
              </select>
              <Button
                onClick={fetchMT5Performance}
                variant="outline"
                size="sm"
                disabled={mt5Loading}
                className="text-cyan-400 border-cyan-400 hover:bg-cyan-400 hover:text-white"
              >
                {mt5Loading ? 'Loading...' : 'Refresh'}
              </Button>
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {mt5Loading ? (
            <div className="text-center py-8 text-slate-400">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-400 mx-auto mb-4"></div>
              Loading MT5 performance data...
            </div>
          ) : mt5Performance.length === 0 ? (
            <div className="text-center py-8 text-slate-400">
              <AlertCircle className="h-12 w-12 mx-auto mb-4 text-yellow-400" />
              <p>No MT5 performance data available for the selected period.</p>
              <p className="text-sm mt-2">Deal history collection may not be active yet.</p>
            </div>
          ) : (
            <>
              {/* Performance Table */}
              <div className="overflow-x-auto mb-6">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-slate-700">
                      <th className="text-left text-slate-400 font-semibold py-3 px-2">Manager/Strategy</th>
                      <th className="text-center text-slate-400 font-semibold py-3 px-2">Magic #</th>
                      <th className="text-right text-slate-400 font-semibold py-3 px-2">Total P&L</th>
                      <th className="text-right text-slate-400 font-semibold py-3 px-2">Volume (Lots)</th>
                      <th className="text-center text-slate-400 font-semibold py-3 px-2">Total Deals</th>
                      <th className="text-center text-slate-400 font-semibold py-3 px-2">Win Rate</th>
                      <th className="text-right text-slate-400 font-semibold py-3 px-2">Avg P&L/Deal</th>
                      <th className="text-center text-slate-400 font-semibold py-3 px-2">Accounts</th>
                    </tr>
                  </thead>
                  <tbody>
                    {mt5Performance.map((manager, index) => (
                      <tr 
                        key={manager.magic || index}
                        className="border-b border-slate-800 hover:bg-slate-800/30 transition-colors"
                      >
                        <td className="py-3 px-2">
                          <div className="flex items-center">
                            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center text-white font-bold text-sm mr-3">
                              {manager.manager_name.substring(0, 2).toUpperCase()}
                            </div>
                            <div>
                              <div className="text-white font-semibold">
                                {manager.manager_name}
                              </div>
                              <div className="text-slate-400 text-xs">
                                {manager.win_deals} wins / {manager.loss_deals} losses
                              </div>
                            </div>
                          </div>
                        </td>
                        <td className="py-3 px-2 text-center">
                          <Badge className="bg-purple-600 text-white">
                            {manager.magic}
                          </Badge>
                        </td>
                        <td className={`py-3 px-2 text-right font-bold ${
                          manager.total_profit >= 0 ? 'text-green-400' : 'text-red-400'
                        }`}>
                          {formatCurrency(manager.total_profit)}
                        </td>
                        <td className="py-3 px-2 text-right text-white font-semibold">
                          {manager.total_volume.toFixed(2)}
                        </td>
                        <td className="py-3 px-2 text-center text-white">
                          {manager.total_deals}
                        </td>
                        <td className="py-3 px-2 text-center">
                          <Badge className={`${
                            manager.win_rate >= 60 ? 'bg-green-600' :
                            manager.win_rate >= 50 ? 'bg-yellow-600' :
                            'bg-red-600'
                          } text-white`}>
                            {manager.win_rate}%
                          </Badge>
                        </td>
                        <td className={`py-3 px-2 text-right font-semibold ${
                          manager.avg_profit_per_deal >= 0 ? 'text-green-400' : 'text-red-400'
                        }`}>
                          {formatCurrency(manager.avg_profit_per_deal)}
                        </td>
                        <td className="py-3 px-2 text-center text-slate-300 text-sm">
                          {manager.accounts_used.length} account{manager.accounts_used.length > 1 ? 's' : ''}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Performance Bar Chart */}
              <div className="bg-slate-800/30 rounded-lg p-4">
                <h4 className="text-white font-medium mb-4">P&L by Manager</h4>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={mt5Performance}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis 
                      dataKey="managerName" 
                      stroke="#94a3b8"
                      tick={{ fill: '#94a3b8', fontSize: 12 }}
                      angle={-45}
                      textAnchor="end"
                      height={80}
                    />
                    <YAxis 
                      stroke="#94a3b8"
                      tick={{ fill: '#94a3b8' }}
                      tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
                    />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: '#1e293b', 
                        border: '1px solid #334155',
                        borderRadius: '8px',
                        color: '#fff'
                      }}
                      formatter={(value) => [formatCurrency(value), 'Total P&L']}
                    />
                    <Bar dataKey="total_profit" radius={[8, 8, 0, 0]}>
                      {mt5Performance.map((entry, index) => (
                        <Cell 
                          key={`cell-${index}`} 
                          fill={entry.total_profit >= 0 ? '#10b981' : '#ef4444'} 
                        />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>

              {/* Summary Stats */}
              <div className="mt-6 grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-slate-800/50 rounded-lg p-4">
                  <div className="text-slate-400 text-sm">Total Managers</div>
                  <div className="text-white text-2xl font-bold">{mt5Performance.length}</div>
                </div>
                <div className="bg-slate-800/50 rounded-lg p-4">
                  <div className="text-slate-400 text-sm">Total P&L</div>
                  <div className={`text-2xl font-bold ${
                    mt5Performance.reduce((sum, m) => sum + m.total_profit, 0) >= 0 ? 'text-green-400' : 'text-red-400'
                  }`}>
                    {formatCurrency(mt5Performance.reduce((sum, m) => sum + m.total_profit, 0))}
                  </div>
                </div>
                <div className="bg-slate-800/50 rounded-lg p-4">
                  <div className="text-slate-400 text-sm">Total Volume</div>
                  <div className="text-cyan-400 text-2xl font-bold">
                    {mt5Performance.reduce((sum, m) => sum + m.total_volume, 0).toFixed(2)} lots
                  </div>
                </div>
                <div className="bg-slate-800/50 rounded-lg p-4">
                  <div className="text-slate-400 text-sm">Total Deals</div>
                  <div className="text-white text-2xl font-bold">
                    {mt5Performance.reduce((sum, m) => sum + m.total_deals, 0)}
                  </div>
                </div>
              </div>

              {/* Data Source Info */}
              <div className="mt-4 p-3 bg-blue-900/20 border border-blue-500/30 rounded-lg">
                <div className="flex items-start">
                  <Activity className="h-5 w-5 text-blue-400 mr-2 mt-0.5" />
                  <div className="text-sm">
                    <div className="text-blue-300 font-semibold">Real-time MT5 Deal Data</div>
                    <div className="text-slate-300 mt-1">
                      Performance metrics calculated from actual MT5 deal history. 
                      Magic numbers identify trading strategies/providers. Updated every 5 minutes via VPS bridge.
                    </div>
                  </div>
                </div>
              </div>
            </>
          )}
        </CardContent>
      </Card>

      {/* Edit Account Modal */}
      <AnimatePresence>
        {editModalOpen && editingAccount && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4"
            onClick={closeEditModal}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="bg-slate-800 rounded-xl border border-slate-700 w-full max-w-2xl max-h-[90vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Modal Header */}
              <div className="sticky top-0 bg-slate-800 border-b border-slate-700 p-4 flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-bold text-white">Edit Account {editingAccount.account}</h2>
                  <p className="text-slate-400 text-sm">{editingAccount.name}</p>
                </div>
                <Button variant="ghost" onClick={closeEditModal} className="text-slate-400 hover:text-white">
                  ✕
                </Button>
              </div>

              {/* Modal Body */}
              <div className="p-4 space-y-6">
                {/* Profile Section */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-cyan-400 flex items-center">
                    <Users className="w-4 h-4 mr-2" />
                    Account Profile
                  </h3>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm text-slate-400 mb-1">Manager Name</label>
                      <input
                        type="text"
                        value={editFormData.manager_name}
                        onChange={(e) => setEditFormData(prev => ({ ...prev, manager_name: e.target.value }))}
                        className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white focus:border-cyan-500 focus:outline-none"
                      />
                    </div>
                    <div>
                      <label className="block text-sm text-slate-400 mb-1">Initial Allocation ($)</label>
                      <input
                        type="number"
                        value={editFormData.initial_allocation}
                        onChange={(e) => setEditFormData(prev => ({ ...prev, initial_allocation: e.target.value }))}
                        className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white focus:border-cyan-500 focus:outline-none"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm text-slate-400 mb-1">Allocation Start Date</label>
                    <input
                      type="date"
                      value={editFormData.allocation_start_date}
                      onChange={(e) => setEditFormData(prev => ({ ...prev, allocation_start_date: e.target.value }))}
                      className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white focus:border-cyan-500 focus:outline-none"
                    />
                  </div>

                  <div>
                    <label className="block text-sm text-slate-400 mb-1">Notes</label>
                    <textarea
                      value={editFormData.notes}
                      onChange={(e) => setEditFormData(prev => ({ ...prev, notes: e.target.value }))}
                      rows={2}
                      className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white focus:border-cyan-500 focus:outline-none resize-none"
                      placeholder="Account notes..."
                    />
                  </div>
                </div>

                {/* Copy Configuration Section */}
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-semibold text-blue-400 flex items-center">
                      <Copy className="w-4 h-4 mr-2" />
                      Copy Trading Configuration
                    </h3>
                    <Button
                      size="sm"
                      onClick={addCopySource}
                      className="bg-blue-600 hover:bg-blue-700 text-white"
                    >
                      <Plus className="w-4 h-4 mr-1" />
                      Add Source
                    </Button>
                  </div>

                  {editFormData.copy_sources.length === 0 ? (
                    <div className="text-center py-6 bg-slate-700/30 rounded-lg border border-dashed border-slate-600">
                      <Copy className="w-8 h-8 text-slate-500 mx-auto mb-2" />
                      <p className="text-slate-400">No copy sources configured</p>
                      <p className="text-slate-500 text-sm">Click "Add Source" to configure copy trading</p>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {editFormData.copy_sources.map((source, index) => (
                        <div key={index} className="bg-slate-700/50 rounded-lg p-3 border border-slate-600">
                          <div className="flex items-start justify-between mb-3">
                            <span className="text-sm font-medium text-slate-300">Copy Source #{index + 1}</span>
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => removeCopySource(index)}
                              className="text-red-400 hover:text-red-300 h-6 w-6 p-0"
                            >
                              ✕
                            </Button>
                          </div>
                          
                          <div className="grid grid-cols-2 gap-3">
                            <div>
                              <label className="block text-xs text-slate-400 mb-1">Master Account</label>
                              <input
                                type="number"
                                value={source.master_account}
                                onChange={(e) => updateCopySource(index, 'master_account', e.target.value)}
                                placeholder="e.g., 2210"
                                className="w-full bg-slate-600 border border-slate-500 rounded px-2 py-1.5 text-white text-sm focus:border-cyan-500 focus:outline-none"
                              />
                            </div>
                            <div>
                              <label className="block text-xs text-slate-400 mb-1">Broker</label>
                              <select
                                value={source.master_broker}
                                onChange={(e) => updateCopySource(index, 'master_broker', e.target.value)}
                                className="w-full bg-slate-600 border border-slate-500 rounded px-2 py-1.5 text-white text-sm focus:border-cyan-500 focus:outline-none"
                              >
                                <option value="LUCRUM">LUCRUM</option>
                                <option value="MEX Atlantic">MEX Atlantic</option>
                                <option value="Other">Other</option>
                              </select>
                            </div>
                            <div>
                              <label className="block text-xs text-slate-400 mb-1">Master Name (Optional)</label>
                              <input
                                type="text"
                                value={source.master_name}
                                onChange={(e) => updateCopySource(index, 'master_name', e.target.value)}
                                placeholder="e.g., GOLD DAY TRADING"
                                className="w-full bg-slate-600 border border-slate-500 rounded px-2 py-1.5 text-white text-sm focus:border-cyan-500 focus:outline-none"
                              />
                            </div>
                            <div>
                              <label className="block text-xs text-slate-400 mb-1">Copy Type</label>
                              <select
                                value={source.copy_type}
                                onChange={(e) => updateCopySource(index, 'copy_type', e.target.value)}
                                className="w-full bg-slate-600 border border-slate-500 rounded px-2 py-1.5 text-white text-sm focus:border-cyan-500 focus:outline-none"
                              >
                                <option value="ratio">Ratio</option>
                                <option value="fixed_lot">Fixed Lot</option>
                              </select>
                            </div>
                          </div>
                          
                          <div className="mt-3">
                            {source.copy_type === 'ratio' ? (
                              <div>
                                <label className="block text-xs text-slate-400 mb-1">Copy Ratio</label>
                                <div className="flex items-center gap-2">
                                  <input
                                    type="number"
                                    step="0.05"
                                    min="0.01"
                                    max="10"
                                    value={source.ratio || 0.5}
                                    onChange={(e) => updateCopySource(index, 'ratio', parseFloat(e.target.value))}
                                    className="w-24 bg-slate-600 border border-slate-500 rounded px-2 py-1.5 text-white text-sm focus:border-cyan-500 focus:outline-none"
                                  />
                                  <span className="text-slate-400 text-sm">x (e.g., 0.5 = 50% of master position)</span>
                                </div>
                              </div>
                            ) : (
                              <div>
                                <label className="block text-xs text-slate-400 mb-1">Fixed Lot Size</label>
                                <div className="flex items-center gap-2">
                                  <input
                                    type="number"
                                    step="0.01"
                                    min="0.01"
                                    value={source.fixed_lot || 0.1}
                                    onChange={(e) => updateCopySource(index, 'fixed_lot', parseFloat(e.target.value))}
                                    className="w-24 bg-slate-600 border border-slate-500 rounded px-2 py-1.5 text-white text-sm focus:border-cyan-500 focus:outline-none"
                                  />
                                  <span className="text-slate-400 text-sm">lots (fixed size regardless of master)</span>
                                </div>
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              {/* Modal Footer */}
              <div className="sticky bottom-0 bg-slate-800 border-t border-slate-700 p-4 flex justify-end gap-3">
                <Button variant="outline" onClick={closeEditModal} className="text-slate-300 border-slate-600">
                  Cancel
                </Button>
                <Button
                  onClick={saveAccountEdit}
                  disabled={saving}
                  className="bg-cyan-600 hover:bg-cyan-700 text-white"
                >
                  {saving ? (
                    <>
                      <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                      Saving...
                    </>
                  ) : (
                    'Save Changes'
                  )}
                </Button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

    </div>
  );
};

export default MoneyManagersDashboard;