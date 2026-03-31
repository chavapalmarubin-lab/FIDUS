import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Shield, Users, DollarSign, TrendingUp, LogOut, Plus, RefreshCw,
  Search, Download, Calendar, Activity, ChevronRight, Clock,
  ArrowUpRight, UserPlus, PieChart, X, Check, Loader2, BarChart3
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Input } from './ui/input';
import { Label } from './ui/label';

const API = process.env.REACT_APP_BACKEND_URL;
const fmt = v => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(v || 0);

// ─── ADMIN LOGIN ───
const AdminLogin = ({ onLogin }) => {
  const [creds, setCreds] = useState({ email: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!creds.email || !creds.password) { setError('Enter email and password'); return; }
    setLoading(true); setError('');
    try {
      const res = await fetch(`${API}/api/retail/admin/login`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: creds.email.trim(), password: creds.password.trim() })
      });
      const data = await res.json();
      if (!res.ok) { setError(data.detail || 'Login failed'); return; }
      if (data.success) {
        localStorage.setItem('retail_admin_token', data.token);
        localStorage.setItem('retail_admin_data', JSON.stringify(data.admin));
        onLogin(data);
      }
    } catch { setError('Network error'); }
    finally { setLoading(false); }
  };

  return (
    <div style={{ background: '#050a15', minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20 }}>
      <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} style={{ width: '100%', maxWidth: 400 }}>
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <img src="/fidus-logo.png" alt="FIDUS" style={{ height: 56, margin: '0 auto 12px', display: 'block' }} />
          <h1 style={{ color: 'white', fontSize: 24, fontWeight: 800, margin: '0 0 4px' }}>FIDUS Retail</h1>
          <p style={{ color: '#64748b', fontSize: 13 }}>Portal de Administracion</p>
        </div>
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          <input placeholder="Admin Email" type="email" value={creds.email} onChange={e => setCreds({...creds, email: e.target.value})}
            style={{ width: '100%', padding: '14px 16px', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 12, color: 'white', fontSize: 15, outline: 'none', boxSizing: 'border-box' }} />
          <input placeholder="Password" type="password" value={creds.password} onChange={e => setCreds({...creds, password: e.target.value})}
            style={{ width: '100%', padding: '14px 16px', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 12, color: 'white', fontSize: 15, outline: 'none', boxSizing: 'border-box' }} />
          {error && <div style={{ color: '#ef4444', fontSize: 13, padding: '8px 12px', background: 'rgba(239,68,68,0.1)', borderRadius: 8 }}>{error}</div>}
          <button type="submit" disabled={loading}
            style={{ width: '100%', padding: '14px', background: 'linear-gradient(135deg, #0ea5e9, #0284c7)', color: 'white', border: 'none', borderRadius: 12, fontSize: 15, fontWeight: 700, cursor: 'pointer' }}>
            {loading ? 'Signing in...' : 'Admin Sign In'}
          </button>
        </form>
        <div style={{ textAlign: 'center', marginTop: 16 }}>
          <a href="/retail" style={{ color: '#475569', fontSize: 12, textDecoration: 'none' }}>Back to FIDUS Retail</a>
        </div>
      </motion.div>
    </div>
  );
};

// ─── CSV HELPER ───
const downloadCSV = (rows, headers, filename) => {
  const csv = [headers.join(','), ...rows.map(r => headers.map(h => `"${String(r[h] ?? '').replace(/"/g, '""')}"`).join(','))].join('\n');
  const blob = new Blob([csv], { type: 'text/csv' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a'); a.href = url; a.download = filename; a.click();
  URL.revokeObjectURL(url);
};

// ─── ADMIN DASHBOARD ───
const RetailAdminDashboard = ({ authData, onLogout }) => {
  const [activeTab, setActiveTab] = useState('overview');
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showAddClient, setShowAddClient] = useState(false);
  const [addForm, setAddForm] = useState({ first_name: '', last_name: '', email: '', phone: '', password: '', balance: '' });
  const [addError, setAddError] = useState('');
  const [addResult, setAddResult] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  const token = authData?.token || localStorage.getItem('retail_admin_token');
  const admin = authData?.admin || JSON.parse(localStorage.getItem('retail_admin_data') || '{}');
  const h = { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' };

  const fetchDashboard = useCallback(async () => {
    try {
      const res = await fetch(`${API}/api/retail/admin/dashboard`, { headers: h });
      const data = await res.json();
      if (data.success) setDashboard(data);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  }, [token]);

  useEffect(() => { fetchDashboard(); }, [fetchDashboard]);

  const handleAddClient = async () => {
    if (!addForm.first_name || !addForm.last_name || !addForm.email || !addForm.password) {
      setAddError('Fill all required fields'); return;
    }
    setSubmitting(true); setAddError('');
    try {
      const res = await fetch(`${API}/api/retail/admin/add-client`, {
        method: 'POST', headers: h,
        body: JSON.stringify({ ...addForm, balance: parseFloat(addForm.balance) || 0 })
      });
      const data = await res.json();
      if (!res.ok) { setAddError(data.detail || 'Failed'); return; }
      setAddResult(data);
      fetchDashboard();
    } catch { setAddError('Network error'); }
    finally { setSubmitting(false); }
  };

  const handleLogout = () => { localStorage.removeItem('retail_admin_token'); localStorage.removeItem('retail_admin_data'); onLogout(); };

  if (loading) return <div className="flex justify-center items-center min-h-screen" style={{ background: '#050a15' }}><Loader2 className="w-8 h-8 animate-spin text-cyan-400" /></div>;

  const clients = dashboard?.clients || [];
  const stats = dashboard?.stats || {};
  const calendar = dashboard?.payment_calendar || [];
  const filtered = clients.filter(c => !searchTerm || `${c.first_name} ${c.last_name} ${c.email}`.toLowerCase().includes(searchTerm.toLowerCase()));

  return (
    <div style={{ background: '#050a15', minHeight: '100vh' }}>
      {/* Header */}
      <header style={{ borderBottom: '1px solid rgba(255,255,255,0.06)', background: 'rgba(5,10,21,0.95)', backdropFilter: 'blur(12px)' }}>
        <div style={{ maxWidth: 1200, margin: '0 auto', padding: '16px 24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <img src="/fidus-logo.png" alt="FIDUS" style={{ height: 36 }} />
            <div>
              <h1 style={{ color: 'white', fontSize: 18, fontWeight: 800, margin: 0 }}>FIDUS Retail — Admin</h1>
              <p style={{ color: '#64748b', fontSize: 12, margin: 0 }}>{admin.name || admin.email}</p>
            </div>
          </div>
          <div style={{ display: 'flex', gap: 8 }}>
            <Button variant="ghost" size="sm" onClick={fetchDashboard} className="text-slate-400"><RefreshCw className="w-4 h-4" /></Button>
            <Button variant="ghost" size="sm" onClick={handleLogout} className="text-slate-400 hover:text-red-400"><LogOut className="w-4 h-4" /></Button>
          </div>
        </div>
      </header>

      <main style={{ maxWidth: 1200, margin: '0 auto', padding: '24px' }}>
        {/* Tabs */}
        <div style={{ display: 'flex', gap: 4, padding: 4, background: 'rgba(255,255,255,0.03)', borderRadius: 10, marginBottom: 24, border: '1px solid rgba(255,255,255,0.06)' }}>
          {[{ id: 'overview', label: 'Resumen', icon: BarChart3 }, { id: 'clients', label: 'Clientes', icon: Users }, { id: 'fund', label: 'Fondo', icon: DollarSign }, { id: 'calendar', label: 'Calendario de Pagos', icon: Calendar }].map(t => (
            <button key={t.id} onClick={() => setActiveTab(t.id)}
              style={{ flex: 1, padding: '10px 16px', background: activeTab === t.id ? '#0ea5e9' : 'transparent', borderRadius: 8, border: 'none', color: activeTab === t.id ? 'white' : '#64748b', fontSize: 13, fontWeight: 600, cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6 }}>
              <t.icon size={14} /> {t.label}
            </button>
          ))}
        </div>

        {/* ═══ OVERVIEW ═══ */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              {[
                { l: 'Total AUM', v: fmt(stats.total_aum), c: '#0ea5e9', icon: DollarSign },
                { l: 'Total Clients', v: stats.total_clients || 0, c: '#10b981', icon: Users },
                { l: 'Active Clients', v: stats.active_clients || 0, c: '#8b5cf6', icon: Activity },
                { l: 'In Incubation', v: stats.incubation_clients || 0, c: '#f59e0b', icon: Clock },
                { l: 'Monthly Revenue', v: fmt(stats.monthly_revenue), c: '#f59e0b', icon: TrendingUp },
                { l: 'Avg Balance', v: fmt(stats.avg_balance), c: '#06b6d4', icon: PieChart },
              ].map((s, i) => (
                <Card key={i} className="border-slate-700/20 bg-slate-800/20">
                  <CardContent className="p-4 flex items-center gap-3">
                    <div style={{ width: 40, height: 40, borderRadius: 10, background: `${s.c}15`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      <s.icon size={20} color={s.c} />
                    </div>
                    <div>
                      <div style={{ color: '#64748b', fontSize: 11 }}>{s.l}</div>
                      <div style={{ color: 'white', fontSize: 20, fontWeight: 800, fontFamily: 'monospace' }}>{s.v}</div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Top Clients */}
            <Card className="border-slate-700/20 bg-slate-800/20">
              <CardHeader className="pb-3"><CardTitle className="text-sm text-slate-200">Top Clients by Balance</CardTitle></CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {clients.sort((a, b) => (b.balance || 0) - (a.balance || 0)).slice(0, 10).map((c, i) => (
                    <div key={i} className="flex items-center justify-between p-3 rounded-lg border border-slate-700/10 bg-slate-800/10 hover:bg-slate-700/10">
                      <div className="flex items-center gap-3">
                        <span className="text-slate-500 text-sm font-mono w-6">#{i + 1}</span>
                        <div>
                          <span className="text-white font-medium text-sm">{c.first_name} {c.last_name}</span>
                          <span className="text-slate-500 text-xs ml-2">{c.email}</span>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-white font-bold font-mono">{fmt(c.balance)}</div>
                        <div className="text-emerald-400 text-xs font-mono">+{fmt((c.balance || 0) * 0.015)}/mo</div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* ═══ CLIENTS ═══ */}
        {activeTab === 'clients' && (
          <div className="space-y-4">
            <div className="flex gap-3 items-center">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                <Input placeholder="Search clients..." value={searchTerm} onChange={e => setSearchTerm(e.target.value)} className="pl-10 bg-slate-900/50 border-slate-700 text-white" />
              </div>
              <Button onClick={() => downloadCSV(clients.map(c => ({ name: `${c.first_name} ${c.last_name}`, email: c.email, phone: c.phone || '', balance: c.balance || 0, returns: c.total_returns || 0, status: c.status || '' })), ['name', 'email', 'phone', 'balance', 'returns', 'status'], 'retail_clients.csv')} variant="outline" className="border-slate-600 text-slate-300 gap-1"><Download className="w-3.5 h-3.5" /> CSV</Button>
              <Button onClick={() => { setShowAddClient(true); setAddResult(null); }} className="bg-cyan-600 hover:bg-cyan-500 gap-1"><Plus className="w-3.5 h-3.5" /> Add Client</Button>
            </div>

            <Card className="border-slate-700/20 bg-slate-800/20">
              <CardContent className="p-0">
                <table className="w-full text-sm">
                  <thead><tr className="border-b border-slate-700/30 text-slate-400">
                    <th className="text-left p-3">Client</th><th className="text-left p-3">Email</th><th className="text-left p-3">Phone</th>
                    <th className="text-right p-3">Balance</th><th className="text-right p-3">Monthly</th><th className="text-right p-3">Returns</th><th className="text-center p-3">Status</th>
                  </tr></thead>
                  <tbody>
                    {filtered.map((c, i) => (
                      <tr key={i} className="border-b border-slate-700/10 hover:bg-slate-700/10">
                        <td className="p-3 text-white font-medium">{c.first_name} {c.last_name}</td>
                        <td className="p-3 text-slate-400">{c.email}</td>
                        <td className="p-3 text-slate-400">{c.phone || '-'}</td>
                        <td className="p-3 text-right text-white font-mono font-bold">{fmt(c.balance)}</td>
                        <td className="p-3 text-right text-emerald-400 font-mono">{fmt((c.balance || 0) * 0.015)}</td>
                        <td className="p-3 text-right text-cyan-400 font-mono">{fmt(c.total_returns)}</td>
                        <td className="p-3 text-center"><Badge variant="outline" className={c.status === 'active' ? 'border-emerald-500/40 text-emerald-400' : 'border-slate-500/40 text-slate-400'}>{c.status || 'active'}</Badge></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </CardContent>
            </Card>
          </div>
        )}


        {/* ═══ FUND TAB — Cash Flow & Performance ═══ */}
        {activeTab === 'fund' && (() => {
          const fp = dashboard?.fund_performance || {};
          return (
          <div className="space-y-6">
            {/* Fund Source + Retail Performance */}
            <Card className="border-cyan-500/15 bg-cyan-900/5">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-xs text-slate-400">Performance Source: Account {fp.source_account} ({fp.source_name})</div>
                    <div className="text-white font-bold">Fund Return: {fp.fund_return_pct}% → Applied to Retail AUM</div>
                    <div className="text-slate-500 text-xs">{fp.days_since_start} days since inception | Daily rates applied to ${fmt(fp.retail_aum)}</div>
                  </div>
                  <div className="text-right">
                    <div className={`text-2xl font-bold font-mono ${fp.retail_return_pct >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>+{fmt(fp.retail_gross_return)}</div>
                    <div className="text-xs text-slate-400">Retail Fund P&L ({fp.retail_return_pct}%)</div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* KPIs */}
            <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
              {[
                { l: 'Retail AUM', v: fmt(fp.retail_aum), c: '#0ea5e9' },
                { l: 'Retail Equity', v: fmt(fp.retail_equity), c: '#8b5cf6' },
                { l: 'Retail P&L', v: `${fp.retail_gross_return >= 0 ? '+' : ''}${fmt(fp.retail_gross_return)}`, c: fp.retail_gross_return >= 0 ? '#10b981' : '#ef4444' },
                { l: 'Clients', v: `${stats.total_clients} (${stats.incubation_clients || 0} incub)`, c: '#f59e0b' },
                { l: 'Return %', v: `${fp.retail_return_pct >= 0 ? '+' : ''}${fp.retail_return_pct}%`, c: fp.retail_return_pct >= 0 ? '#10b981' : '#ef4444' },
              ].map((s, i) => (
                <Card key={i} className="border-slate-700/20 bg-slate-800/20">
                  <CardContent className="p-3 text-center">
                    <div style={{ color: s.c }} className="text-lg font-bold font-mono">{s.v}</div>
                    <div className="text-[10px] text-slate-500">{s.l}</div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Performance Fee Waterfall */}
            <Card className="border-slate-700/20 bg-slate-800/20">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm text-slate-200 flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-emerald-400" /> Performance Fee Calculation (Waterfall)
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between py-2">
                    <span className="text-slate-400">Retail Fund Gross Return ({fp.retail_return_pct}% on ${fmt(fp.retail_aum)})</span>
                    <span className={`font-mono font-bold ${fp.retail_gross_return >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>{fp.retail_gross_return >= 0 ? '+' : ''}{fmt(fp.retail_gross_return)}</span>
                  </div>
                  <div className="flex justify-between py-2 border-t border-slate-700/30">
                    <span className="text-slate-400">- Performance Fee ({fp.performance_fee_pct}%)</span>
                    <span className="text-red-400 font-mono">-{fmt(fp.performance_fee)}</span>
                  </div>
                  <div className="flex justify-between py-2 border-t border-dashed border-cyan-500/30 bg-cyan-900/10 px-3 rounded-lg">
                    <span className="text-cyan-400 font-bold">= Net After Performance Fee</span>
                    <span className={`font-mono font-bold ${fp.net_after_fee >= 0 ? 'text-cyan-400' : 'text-red-400'}`}>{fmt(fp.net_after_fee)}</span>
                  </div>
                  <div className="flex justify-between py-2 border-t border-slate-700/30">
                    <span className="text-slate-400">- Client Payouts (1.5% × {stats.total_clients} clients)</span>
                    <span className="text-red-400 font-mono">-{fmt(fp.client_payout_monthly)}</span>
                  </div>
                  <div className="flex justify-between py-2 border-t border-dashed border-emerald-500/30 bg-emerald-900/10 px-3 rounded-lg">
                    <span className="text-emerald-400 font-bold">= FIDUS Net Revenue</span>
                    <span className={`font-mono font-bold text-lg ${fp.fidus_net_revenue >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>{fmt(fp.fidus_net_revenue)}</span>
                  </div>
                </div>
              </CardContent>
            </Card>


            {/* Daily Performance */}
            {fp.daily_performance && fp.daily_performance.length > 0 && (
              <Card className="border-slate-700/20 bg-slate-800/20">
                <CardHeader className="pb-3"><CardTitle className="text-sm text-slate-200">Daily Performance (Retail Fund)</CardTitle></CardHeader>
                <CardContent>
                  <table className="w-full text-xs">
                    <thead><tr className="border-b border-slate-700/30 text-slate-400">
                      <th className="text-left p-2">Date</th><th className="text-right p-2">2210 Rate</th><th className="text-right p-2">Retail P&L</th><th className="text-right p-2">Retail Equity</th>
                    </tr></thead>
                    <tbody>
                      {fp.daily_performance.map((d, i) => (
                        <tr key={i} className="border-b border-slate-700/10">
                          <td className="p-2 text-white font-mono">{d.date}</td>
                          <td className={`p-2 text-right font-mono ${d.rate_pct >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>{d.rate_pct >= 0 ? '+' : ''}{d.rate_pct}%</td>
                          <td className={`p-2 text-right font-mono font-bold ${d.retail_pnl >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>${d.retail_pnl >= 0 ? '+' : ''}{d.retail_pnl.toLocaleString()}</td>
                          <td className="p-2 text-right text-white font-mono">${d.retail_equity.toLocaleString()}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </CardContent>
              </Card>
            )}

            {/* Revenue Scaling */}
            <Card className="border-slate-700/20 bg-slate-800/20">
              <CardHeader className="pb-3"><CardTitle className="text-sm text-slate-200">Revenue at Scale (with 30% Performance Fee)</CardTitle></CardHeader>
              <CardContent>
                <table className="w-full text-xs">
                  <thead><tr className="border-b border-slate-700/30 text-slate-400">
                    <th className="text-left p-2">AUM</th><th className="text-right p-2">Clients</th><th className="text-right p-2">Gross ({fp.fund_return_pct}%)</th><th className="text-right p-2 text-red-400">Perf Fee (30%)</th><th className="text-right p-2">Client Pay (1.5%)</th><th className="text-right p-2 text-emerald-400">FIDUS Net</th>
                  </tr></thead>
                  <tbody>
                    {[50000, 100000, 500000, 1000000, 5000000].map(aum => {
                      const gross = aum * (fp.fund_return_pct / 100);
                      const fee = gross > 0 ? gross * 0.30 : 0;
                      const net = gross - fee;
                      const clientPay = aum * 0.015;
                      const fidusNet = net > clientPay ? net - clientPay : 0;
                      const isActive = Math.abs(aum - fp.retail_aum) < aum * 0.5;
                      return (
                        <tr key={aum} className={`border-b border-slate-700/10 ${isActive ? 'bg-cyan-900/10' : ''}`}>
                          <td className={`p-2 font-medium ${isActive ? 'text-cyan-400' : 'text-slate-200'}`}>{fmt(aum)}</td>
                          <td className="p-2 text-right text-slate-400">{Math.round(aum / (stats.avg_balance || 950))}</td>
                          <td className="p-2 text-right text-emerald-400 font-mono">{fmt(gross)}</td>
                          <td className="p-2 text-right text-red-400 font-mono">-{fmt(fee)}</td>
                          <td className="p-2 text-right text-amber-400 font-mono">-{fmt(clientPay)}</td>
                          <td className="p-2 text-right text-emerald-400 font-bold font-mono">{fmt(fidusNet)}</td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </CardContent>
            </Card>

            {/* Fund Terms */}
            <Card className="border-slate-700/20 bg-slate-800/20">
              <CardHeader className="pb-3"><CardTitle className="text-sm text-slate-200">Retail Fund Structure</CardTitle></CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm text-center">
                  <div className="p-3 bg-slate-700/20 rounded-lg"><div className="text-lg font-bold text-emerald-400">1.5%</div><div className="text-xs text-slate-500">Client Monthly Return</div></div>
                  <div className="p-3 bg-slate-700/20 rounded-lg"><div className="text-lg font-bold text-red-400">30%</div><div className="text-xs text-slate-500">Performance Fee</div></div>
                  <div className="p-3 bg-slate-700/20 rounded-lg"><div className="text-lg font-bold text-amber-400">1 mo</div><div className="text-xs text-slate-500">Incubation Period</div></div>
                  <div className="p-3 bg-slate-700/20 rounded-lg"><div className="text-lg font-bold text-white">EOM</div><div className="text-xs text-slate-500">Payment: End of Month</div></div>
                </div>
              </CardContent>
            </Card>
          </div>
          );
        })()}

        {/* ═══ PAYMENT CALENDAR ═══ */}
        {activeTab === 'calendar' && (
          <div className="space-y-4">
            <Card className="border-slate-700/20 bg-slate-800/20">
              <CardHeader className="pb-3 flex flex-row items-center justify-between">
                <CardTitle className="text-sm text-slate-200 flex items-center gap-2"><Calendar className="w-4 h-4 text-cyan-400" /> Payment Obligations Calendar</CardTitle>
                <Button variant="outline" size="sm" onClick={() => downloadCSV(calendar.map(m => ({ month: m.month, clients: m.client_count, total_due: m.total_due?.toFixed(2), aum: m.aum?.toFixed(2) })), ['month', 'clients', 'total_due', 'aum'], 'retail_payments.csv')} className="border-slate-600 text-slate-300 gap-1"><Download className="w-3 h-3" /> CSV</Button>
              </CardHeader>
              <CardContent>
                {/* Summary */}
                <div className="grid grid-cols-3 gap-4 mb-6 p-4 bg-slate-800/50 rounded-lg">
                  <div className="text-center"><div className="text-2xl font-bold text-cyan-400 font-mono">{fmt(stats.total_aum)}</div><div className="text-xs text-slate-500">Total AUM</div></div>
                  <div className="text-center"><div className="text-2xl font-bold text-emerald-400 font-mono">{fmt(stats.monthly_revenue)}</div><div className="text-xs text-slate-500">Monthly Payout (1.5%)</div></div>
                  <div className="text-center"><div className="text-2xl font-bold text-amber-400 font-mono">{fmt((stats.monthly_revenue || 0) * 12)}</div><div className="text-xs text-slate-500">Annual Obligation</div></div>
                </div>

                {/* Monthly Timeline */}
                <div className="space-y-3">
                  {calendar.map((m, i) => (
                    <div key={i} className="p-4 rounded-lg border border-slate-700/20 bg-slate-800/10">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <Calendar className="w-4 h-4 text-cyan-400" />
                          <span className="text-white font-bold">{m.month_name || m.month}</span>
                          <span className="text-slate-500 text-xs">{m.client_count} clients</span>
                        </div>
                        <span className="text-emerald-400 font-bold font-mono text-lg">{fmt(m.total_due)}</span>
                      </div>
                      {/* Per-client breakdown */}
                      {m.clients && m.clients.length > 0 && (
                        <div className="mt-2 space-y-1">
                          {m.clients.slice(0, 5).map((c, j) => (
                            <div key={j} className="flex justify-between text-xs py-1 px-2 rounded bg-slate-700/20">
                              <span className="text-slate-300">{c.name}</span>
                              <span className="text-emerald-400 font-mono">{fmt(c.amount)}</span>
                            </div>
                          ))}
                          {m.clients.length > 5 && <div className="text-xs text-slate-500 text-center">+{m.clients.length - 5} more clients</div>}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* ═══ ADD CLIENT MODAL ═══ */}
        <AnimatePresence>
          {showAddClient && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
              <motion.div initial={{ scale: 0.95 }} animate={{ scale: 1 }} exit={{ scale: 0.95 }} style={{ width: '100%', maxWidth: 480, background: '#0f172a', borderRadius: 16, border: '1px solid rgba(255,255,255,0.1)', padding: 24 }}>
                {addResult ? (
                  <div>
                    <div className="flex items-center gap-2 mb-4"><Check className="w-5 h-5 text-emerald-400" /><h3 className="text-lg font-bold text-white">Client Added</h3></div>
                    <div className="bg-slate-800/80 rounded-lg p-4 space-y-2 border border-emerald-500/20">
                      <div><span className="text-slate-400 text-sm">Email</span><p className="text-white font-mono">{addResult.email}</p></div>
                      <div><span className="text-slate-400 text-sm">Password</span><p className="text-emerald-400 font-mono text-lg">{addResult.password}</p></div>
                      <div><span className="text-slate-400 text-sm">Login URL</span><p className="text-cyan-400 font-mono text-sm">/retail/login</p></div>
                    </div>
                    <Button onClick={() => { setShowAddClient(false); setAddResult(null); }} className="w-full mt-4 bg-slate-700 hover:bg-slate-600 text-white">Close</Button>
                  </div>
                ) : (
                  <>
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-bold text-white">Add Retail Client</h3>
                      <Button variant="ghost" size="sm" onClick={() => setShowAddClient(false)} className="text-slate-400"><X className="w-4 h-4" /></Button>
                    </div>
                    <div className="space-y-3">
                      <div className="grid grid-cols-2 gap-3">
                        <div><Label className="text-slate-300 text-xs">First Name *</Label><Input value={addForm.first_name} onChange={e => setAddForm({...addForm, first_name: e.target.value})} className="bg-slate-800/60 border-slate-700 text-white mt-1" /></div>
                        <div><Label className="text-slate-300 text-xs">Last Name *</Label><Input value={addForm.last_name} onChange={e => setAddForm({...addForm, last_name: e.target.value})} className="bg-slate-800/60 border-slate-700 text-white mt-1" /></div>
                      </div>
                      <div><Label className="text-slate-300 text-xs">Email *</Label><Input type="email" value={addForm.email} onChange={e => setAddForm({...addForm, email: e.target.value})} className="bg-slate-800/60 border-slate-700 text-white mt-1" /></div>
                      <div className="grid grid-cols-2 gap-3">
                        <div><Label className="text-slate-300 text-xs">Phone</Label><Input value={addForm.phone} onChange={e => setAddForm({...addForm, phone: e.target.value})} className="bg-slate-800/60 border-slate-700 text-white mt-1" /></div>
                        <div><Label className="text-slate-300 text-xs">Initial Balance ($)</Label><Input type="number" value={addForm.balance} onChange={e => setAddForm({...addForm, balance: e.target.value})} className="bg-slate-800/60 border-slate-700 text-white mt-1" placeholder="0" /></div>
                      </div>
                      <div><Label className="text-slate-300 text-xs">Password *</Label><Input value={addForm.password} onChange={e => setAddForm({...addForm, password: e.target.value})} className="bg-slate-800/60 border-slate-700 text-white mt-1" placeholder="Fidus26@" /></div>
                      {addError && <div className="text-red-400 text-sm bg-red-500/10 border border-red-500/20 rounded-lg p-2">{addError}</div>}
                      <Button disabled={submitting} onClick={handleAddClient} className="w-full bg-cyan-600 hover:bg-cyan-500 text-white">
                        {submitting ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Plus className="w-4 h-4 mr-2" />}{submitting ? 'Creating...' : 'Add Client'}
                      </Button>
                    </div>
                  </>
                )}
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
};

// ─── MAIN ───
const RetailAdmin = () => {
  const [authData, setAuthData] = useState(null);
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('retail_admin_token');
    const admin = localStorage.getItem('retail_admin_data');
    if (token && admin) setAuthData({ token, admin: JSON.parse(admin) });
    setChecking(false);
  }, []);

  if (checking) return null;
  if (!authData) return <AdminLogin onLogin={setAuthData} />;
  return <RetailAdminDashboard authData={authData} onLogout={() => setAuthData(null)} />;
};

export default RetailAdmin;
