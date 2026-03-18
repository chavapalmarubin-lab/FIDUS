import React, { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import {
  AlertTriangle, Shield, CheckCircle, Clock, Bell, X, RefreshCw,
  Activity, Users, DollarSign, TrendingDown, Eye, ChevronDown, ChevronUp
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';

const API_URL = process.env.REACT_APP_BACKEND_URL;
const fmt = (v) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(v || 0);

const RiskAlertsDashboard = () => {
  const [alerts, setAlerts] = useState([]);
  const [unresolvedCount, setUnresolvedCount] = useState(0);
  const [riskStatus, setRiskStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showResolved, setShowResolved] = useState(false);
  const [expandedAlert, setExpandedAlert] = useState(null);

  const token = localStorage.getItem('fidus_token');
  const headers = { 'Authorization': `Bearer ${token}` };

  const fetchAll = useCallback(async () => {
    try {
      const [alertsRes, statusRes] = await Promise.all([
        fetch(`${API_URL}/api/admin/risk/alerts?status=${showResolved ? 'all' : 'unresolved'}&limit=50`, { headers }),
        fetch(`${API_URL}/api/admin/risk/status`, { headers })
      ]);
      const alertsData = await alertsRes.json();
      const statusData = await statusRes.json();
      if (alertsData.success) { setAlerts(alertsData.alerts || []); setUnresolvedCount(alertsData.unresolved_count || 0); }
      if (statusData.success) setRiskStatus(statusData);
    } catch (e) { console.error('Risk fetch error:', e); }
    finally { setLoading(false); }
  }, [showResolved]);

  useEffect(() => { fetchAll(); const iv = setInterval(fetchAll, 30000); return () => clearInterval(iv); }, [fetchAll]);

  const resolveAlert = async (alertId) => {
    try {
      await fetch(`${API_URL}/api/admin/risk/alerts/${alertId}/resolve`, { method: 'POST', headers });
      fetchAll();
    } catch (e) { console.error('Resolve error:', e); }
  };

  const portfolio = riskStatus?.portfolio || {};
  const accounts = riskStatus?.accounts || [];

  const getStatusColor = (dd) => {
    if (dd <= -10) return { bg: 'bg-red-500/10', border: 'border-red-500/30', text: 'text-red-400', label: 'CRITICAL' };
    if (dd <= -5) return { bg: 'bg-red-500/10', border: 'border-red-500/20', text: 'text-red-400', label: 'HALT ZONE' };
    if (dd <= -3) return { bg: 'bg-amber-500/10', border: 'border-amber-500/20', text: 'text-amber-400', label: 'WARNING' };
    return { bg: 'bg-emerald-500/10', border: 'border-emerald-500/20', text: 'text-emerald-400', label: 'OK' };
  };

  if (loading) return <div className="flex justify-center py-20"><RefreshCw className="w-8 h-8 animate-spin text-cyan-400" /></div>;

  return (
    <div className="space-y-6" data-testid="risk-alerts-dashboard">
      {/* Portfolio Risk Banner */}
      {portfolio.breached && (
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}
          className="p-4 bg-red-900/30 border border-red-500/40 rounded-lg flex items-center gap-3">
          <AlertTriangle className="w-6 h-6 text-red-400 flex-shrink-0" />
          <div className="flex-1">
            <h3 className="text-red-400 font-bold">PORTFOLIO PROTECTION LINE BREACHED</h3>
            <p className="text-red-300/80 text-sm">
              Portfolio equity ${fmt(portfolio.total_equity)} is ${fmt(portfolio.protection_line - portfolio.total_equity)} below the 10% protection line (${fmt(portfolio.protection_line)}).
              Drawdown: {portfolio.drawdown_pct?.toFixed(2)}%
            </p>
          </div>
        </motion.div>
      )}

      {/* Portfolio KPIs */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 p-4 bg-slate-800/50 rounded-lg border border-slate-700/30">
        <div className="text-center">
          <p className="text-sm text-slate-400">Portfolio Equity</p>
          <p className={`text-2xl font-bold ${portfolio.breached ? 'text-red-400' : 'text-white'}`}>{fmt(portfolio.total_equity)}</p>
        </div>
        <div className="text-center">
          <p className="text-sm text-slate-400">Initial Capital</p>
          <p className="text-2xl font-bold text-white">{fmt(portfolio.total_initial)}</p>
        </div>
        <div className="text-center">
          <p className="text-sm text-slate-400">Drawdown</p>
          <p className={`text-2xl font-bold ${portfolio.drawdown_pct <= -10 ? 'text-red-400' : portfolio.drawdown_pct <= -5 ? 'text-amber-400' : 'text-emerald-400'}`}>
            {portfolio.drawdown_pct?.toFixed(2)}%
          </p>
        </div>
        <div className="text-center">
          <p className="text-sm text-slate-400">Protection Line</p>
          <p className="text-2xl font-bold text-slate-300">{fmt(portfolio.protection_line)}</p>
        </div>
        <div className="text-center">
          <p className="text-sm text-slate-400">Active Alerts</p>
          <p className={`text-2xl font-bold ${unresolvedCount > 0 ? 'text-red-400' : 'text-emerald-400'}`}>{unresolvedCount}</p>
        </div>
      </div>

      {/* Per-Account Risk Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {accounts.map((acc) => {
          const st = getStatusColor(acc.drawdown_pct);
          return (
            <Card key={acc.account} className={`${st.border} ${st.bg} border`}>
              <CardContent className="p-4">
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <h3 className="text-white font-bold">{acc.manager_name}</h3>
                    <p className="text-slate-400 text-xs">Account #{acc.account}</p>
                  </div>
                  <Badge className={`${st.text} bg-transparent border ${st.border}`}>{st.label}</Badge>
                </div>
                {/* Drawdown Bar */}
                <div className="mb-3">
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-slate-400">Drawdown</span>
                    <span className={st.text}>{acc.drawdown_pct?.toFixed(2)}%</span>
                  </div>
                  <div className="w-full bg-slate-700/50 rounded-full h-2.5">
                    <div className={`h-2.5 rounded-full transition-all ${acc.drawdown_pct <= -10 ? 'bg-red-500' : acc.drawdown_pct <= -5 ? 'bg-amber-500' : acc.drawdown_pct <= -3 ? 'bg-yellow-500' : 'bg-emerald-500'}`}
                      style={{ width: `${Math.min(Math.abs(acc.drawdown_pct || 0) / 20 * 100, 100)}%` }} />
                  </div>
                  <div className="flex justify-between text-[10px] text-slate-600 mt-0.5">
                    <span>0%</span><span className="text-amber-600">-3%</span><span className="text-red-600">-5%</span><span>-10%</span><span>-20%</span>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div><span className="text-slate-500">Equity</span><p className="text-white font-medium">{fmt(acc.equity)}</p></div>
                  <div><span className="text-slate-500">Initial</span><p className="text-white font-medium">{fmt(acc.initial_allocation)}</p></div>
                  <div><span className="text-slate-500">Warn</span><p className="text-amber-400">{acc.warning_threshold}%</p></div>
                  <div><span className="text-slate-500">Halt</span><p className="text-red-400">{acc.halt_threshold}%</p></div>
                </div>
                {acc.unresolved_alerts > 0 && (
                  <div className="mt-2 p-2 bg-red-500/10 rounded text-xs text-red-400 flex items-center gap-1">
                    <Bell className="w-3 h-3" /> {acc.unresolved_alerts} unresolved alert(s)
                  </div>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Alert List */}
      <Card className="border-slate-700/50 bg-slate-800/40">
        <CardHeader className="pb-3 flex flex-row items-center justify-between">
          <CardTitle className="text-base text-slate-200 flex items-center gap-2">
            <Bell className="w-4 h-4 text-amber-400" /> Risk Alerts ({unresolvedCount} unresolved)
          </CardTitle>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={() => setShowResolved(!showResolved)}
              className={`text-xs ${showResolved ? 'bg-slate-700 text-white' : 'border-slate-600 text-slate-400'}`}>
              {showResolved ? 'Showing All' : 'Unresolved Only'}
            </Button>
            <Button variant="ghost" size="sm" onClick={fetchAll} className="text-slate-400"><RefreshCw className="w-4 h-4" /></Button>
          </div>
        </CardHeader>
        <CardContent>
          {alerts.length === 0 ? (
            <div className="text-center py-8 text-slate-500"><Shield className="w-10 h-10 mx-auto mb-2 opacity-30" /><p>No alerts.</p></div>
          ) : (
            <div className="space-y-2">
              {alerts.map((alert, idx) => {
                const isCritical = alert.alert_type === 'halt' || alert.alert_type === 'portfolio_critical';
                const isResolved = !!alert.resolved_at;
                return (
                  <div key={idx} className={`p-3 rounded-lg border ${isResolved ? 'border-slate-700/30 bg-slate-800/20 opacity-60' : isCritical ? 'border-red-500/30 bg-red-900/10' : 'border-amber-500/30 bg-amber-900/10'}`}>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        {isCritical ? <AlertTriangle className="w-4 h-4 text-red-400" /> : <Activity className="w-4 h-4 text-amber-400" />}
                        <span className="text-white font-medium text-sm">
                          {alert.alert_type === 'portfolio_critical' ? 'PORTFOLIO CRITICAL' : alert.alert_type === 'portfolio_warning' ? 'Portfolio Warning' : `Account ${alert.account} — ${alert.manager_name || ''}`}
                        </span>
                        <Badge variant="outline" className={`text-[10px] ${isCritical ? 'border-red-500/40 text-red-400' : 'border-amber-500/40 text-amber-400'}`}>
                          {alert.alert_type?.toUpperCase()}
                        </Badge>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-slate-500">{alert.sent_at ? new Date(alert.sent_at).toLocaleString() : ''}</span>
                        {!isResolved && (
                          <Button size="sm" variant="ghost" onClick={() => resolveAlert(alert._id || alert.sent_at)} className="text-emerald-400 hover:text-emerald-300 text-xs h-7">
                            <CheckCircle className="w-3 h-3 mr-1" /> Resolve
                          </Button>
                        )}
                        {isResolved && <Badge variant="outline" className="border-emerald-500/30 text-emerald-500 text-[10px]">RESOLVED</Badge>}
                      </div>
                    </div>
                    <div className="mt-1 text-xs text-slate-400">
                      Drawdown: <span className={isCritical ? 'text-red-400' : 'text-amber-400'}>{alert.drawdown_pct?.toFixed(2)}%</span>
                      {' '} | Equity: {fmt(alert.actual_value)} | Threshold: {alert.threshold}%
                      {alert.email_sent !== undefined && <span> | Email: {alert.email_sent ? 'Sent' : 'Failed'}</span>}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default RiskAlertsDashboard;
