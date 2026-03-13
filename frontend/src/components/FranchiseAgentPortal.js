import React, { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import {
  Users, DollarSign, TrendingUp, Clock, LogOut, RefreshCw,
  ArrowLeft, Loader2, UserPlus, FileText, ArrowUpRight, Building2
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Input } from './ui/input';
import { Label } from './ui/label';

const API_URL = process.env.REACT_APP_BACKEND_URL;
const fmt = (v) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(v || 0);

// ─────────────────────────────────────────
// AGENT LOGIN
// ─────────────────────────────────────────
const AgentLogin = ({ onLogin }) => {
  const [creds, setCreds] = useState({ email: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!creds.email || !creds.password) { setError('Enter email and password'); return; }
    setLoading(true); setError('');
    try {
      const res = await fetch(`${API_URL}/api/franchise/auth/agent/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: creds.email.trim(), password: creds.password.trim() })
      });
      const data = await res.json();
      if (!res.ok) { setError(data.detail || 'Login failed'); return; }
      if (data.success) {
        localStorage.setItem('franchise_agent_token', data.token);
        localStorage.setItem('franchise_agent_data', JSON.stringify(data.agent));
        localStorage.setItem('franchise_agent_company', JSON.stringify(data.company));
        onLogin(data);
      }
    } catch { setError('Network error'); }
    finally { setLoading(false); }
  };

  return (
    <div data-testid="franchise-agent-login-page" className="min-h-screen flex items-center justify-center" style={{ background: 'linear-gradient(135deg, #0c1222 0%, #111d35 50%, #0a1628 100%)' }}>
      <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }} className="w-full max-w-md mx-4">
        <Card className="border-0 shadow-2xl" style={{ background: 'rgba(15, 23, 42, 0.95)', border: '1px solid rgba(245, 158, 11, 0.2)' }}>
          <CardHeader className="text-center pb-2">
            <div className="flex justify-center mb-4">
              <div className="w-16 h-16 rounded-2xl flex items-center justify-center" style={{ background: 'linear-gradient(135deg, #f59e0b, #d97706)' }}>
                <UserPlus className="w-8 h-8 text-white" />
              </div>
            </div>
            <CardTitle className="text-2xl font-bold text-white">Referral Agent Portal</CardTitle>
            <p className="text-sm text-slate-400 mt-1">Track your referrals and commissions</p>
          </CardHeader>
          <CardContent className="pt-4">
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label className="text-slate-300 text-sm">Email</Label>
                <Input data-testid="agent-login-email" type="email" placeholder="agent@email.com" value={creds.email} onChange={(e) => setCreds({...creds, email: e.target.value})} className="bg-slate-800/60 border-slate-700 text-white placeholder:text-slate-500 focus:border-amber-500" />
              </div>
              <div className="space-y-2">
                <Label className="text-slate-300 text-sm">Password</Label>
                <Input data-testid="agent-login-password" type="password" placeholder="Enter password" value={creds.password} onChange={(e) => setCreds({...creds, password: e.target.value})} className="bg-slate-800/60 border-slate-700 text-white placeholder:text-slate-500 focus:border-amber-500" />
              </div>
              {error && <div data-testid="agent-login-error" className="text-red-400 text-sm bg-red-500/10 border border-red-500/20 rounded-lg p-3">{error}</div>}
              <Button data-testid="agent-login-submit" type="submit" disabled={loading} className="w-full h-11 font-semibold text-white" style={{ background: 'linear-gradient(135deg, #f59e0b, #d97706)' }}>
                {loading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}{loading ? 'Signing in...' : 'Sign In'}
              </Button>
            </form>
            <div className="mt-6 text-center">
              <a href="/franchise/login" className="text-xs text-slate-500 hover:text-amber-400 transition-colors flex items-center justify-center gap-1"><ArrowLeft className="w-3 h-3" /> Company Admin Portal</a>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
};

// ─────────────────────────────────────────
// AGENT DASHBOARD
// ─────────────────────────────────────────
const AgentDashboard = ({ authData, onLogout }) => {
  const [overview, setOverview] = useState(null);
  const [loading, setLoading] = useState(true);

  const token = authData?.token || localStorage.getItem('franchise_agent_token');
  const agentInfo = authData?.agent || JSON.parse(localStorage.getItem('franchise_agent_data') || '{}');
  const company = authData?.company || JSON.parse(localStorage.getItem('franchise_agent_company') || '{}');

  const fetchData = useCallback(async () => {
    try {
      const res = await fetch(`${API_URL}/api/franchise/dashboard/agent/overview`, { headers: { 'Authorization': `Bearer ${token}` } });
      const data = await res.json();
      if (data.success) setOverview(data);
    } catch (e) { console.error('Agent overview error:', e); }
    finally { setLoading(false); }
  }, [token]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const handleLogout = () => {
    localStorage.removeItem('franchise_agent_token');
    localStorage.removeItem('franchise_agent_data');
    localStorage.removeItem('franchise_agent_company');
    onLogout();
  };

  const agent = overview?.agent || agentInfo;
  const summary = overview?.summary || {};
  const clients = overview?.clients || [];
  const transactions = overview?.transactions || [];

  return (
    <div data-testid="franchise-agent-portal" className="min-h-screen" style={{ background: '#0a0f1a' }}>
      <header className="border-b border-slate-800" style={{ background: 'rgba(10, 15, 26, 0.95)', backdropFilter: 'blur(12px)' }}>
        <div className="max-w-5xl mx-auto px-4 sm:px-6 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl flex items-center justify-center" style={{ background: `linear-gradient(135deg, #f59e0b, #d97706)` }}>
              <UserPlus className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-white leading-tight">{company.company_name || 'Agent Portal'}</h1>
              <p className="text-xs text-slate-500">{agent.first_name} {agent.last_name} | Tier {agent.commission_tier || 50}%</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm" onClick={fetchData} className="text-slate-400 hover:text-white"><RefreshCw className="w-4 h-4" /></Button>
            <Button data-testid="agent-logout-btn" variant="ghost" size="sm" onClick={handleLogout} className="text-slate-400 hover:text-red-400"><LogOut className="w-4 h-4" /></Button>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 sm:px-6 py-6 space-y-6">
        {loading ? (
          <div className="flex items-center justify-center py-20"><Loader2 className="w-8 h-8 animate-spin text-amber-400" /></div>
        ) : (
          <>
            {/* KPI Cards */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              <KPI icon={Users} label="Clients Referred" value={summary.total_clients_referred || 0} color="#0ea5e9" />
              <KPI icon={DollarSign} label="AUM Referred" value={fmt(summary.total_aum_referred)} color="#10b981" />
              <KPI icon={TrendingUp} label="Commission Earned" value={fmt(summary.total_commission_earned)} color="#f59e0b" />
              <KPI icon={Clock} label="Active Clients" value={summary.active_clients || 0} color="#8b5cf6" />
            </div>

            {/* Referred Clients */}
            <Card className="border-slate-700/50 bg-slate-800/40">
              <CardHeader className="pb-3"><CardTitle className="text-base text-slate-200">Referred Clients ({clients.length})</CardTitle></CardHeader>
              <CardContent>
                {clients.length === 0 ? (
                  <div className="text-center py-8 text-slate-500"><Users className="w-10 h-10 mx-auto mb-2 opacity-30" /><p>No referred clients yet. Start referring investors.</p></div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead><tr className="border-b border-slate-700/50 text-slate-400">
                        <th className="text-left p-3">Client</th><th className="text-right p-3">Investment</th><th className="text-left p-3">Date</th><th className="text-center p-3">Status</th>
                      </tr></thead>
                      <tbody>
                        {clients.map((c) => (
                          <tr key={c.client_id} className="border-b border-slate-700/30 hover:bg-slate-700/20 transition-colors">
                            <td className="p-3 text-slate-200 font-medium">{c.first_name} {c.last_name}</td>
                            <td className="p-3 text-right text-sky-400">{fmt(c.investment_amount)}</td>
                            <td className="p-3 text-slate-400">{c.investment_date ? new Date(c.investment_date).toLocaleDateString() : '-'}</td>
                            <td className="p-3 text-center"><Badge variant="outline" className={c.status === 'active' ? 'border-emerald-500/40 text-emerald-400' : 'border-amber-500/40 text-amber-400'}>{c.status}</Badge></td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Commission Transactions */}
            <Card className="border-slate-700/50 bg-slate-800/40">
              <CardHeader className="pb-3"><CardTitle className="text-base text-slate-200">Commission History</CardTitle></CardHeader>
              <CardContent>
                {transactions.length === 0 ? (
                  <div className="text-center py-8 text-slate-500"><FileText className="w-10 h-10 mx-auto mb-2 opacity-30" /><p>No commission transactions yet.</p></div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead><tr className="border-b border-slate-700/50 text-slate-400">
                        <th className="text-left p-3">Period</th><th className="text-left p-3">Type</th><th className="text-right p-3">Amount</th><th className="text-center p-3">Status</th>
                      </tr></thead>
                      <tbody>
                        {transactions.map((tx, i) => (
                          <tr key={i} className="border-b border-slate-700/30">
                            <td className="p-3 text-slate-200">{tx.period || '-'}</td>
                            <td className="p-3 text-slate-400">{tx.transaction_type || '-'}</td>
                            <td className="p-3 text-right text-amber-400">{fmt(tx.amount)}</td>
                            <td className="p-3 text-center"><Badge variant="outline" className={tx.status === 'paid' ? 'border-emerald-500/40 text-emerald-400' : 'border-amber-500/40 text-amber-400'}>{tx.status || 'pending'}</Badge></td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </CardContent>
            </Card>
          </>
        )}
      </main>
      <footer className="border-t border-slate-800 mt-12 py-4"><div className="max-w-5xl mx-auto px-4 sm:px-6 text-center"><p className="text-xs text-slate-600">Powered by FIDUS Investment Management</p></div></footer>
    </div>
  );
};

const KPI = ({ icon: Icon, label, value, color }) => (
  <Card className="border-slate-700/50 bg-slate-800/40">
    <CardContent className="p-4 flex items-center gap-3">
      <div className="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0" style={{ background: `${color}20` }}><Icon className="w-5 h-5" style={{ color }} /></div>
      <div className="min-w-0"><div className="text-xs text-slate-500 truncate">{label}</div><div className="text-lg font-bold text-slate-100 truncate">{value}</div></div>
    </CardContent>
  </Card>
);

// ─────────────────────────────────────────
// MAIN EXPORT: Agent Portal App
// ─────────────────────────────────────────
const FranchiseAgentPortal = () => {
  const [authData, setAuthData] = useState(null);
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('franchise_agent_token');
    const agentData = localStorage.getItem('franchise_agent_data');
    const company = localStorage.getItem('franchise_agent_company');
    if (token && agentData && company) {
      setAuthData({ token, agent: JSON.parse(agentData), company: JSON.parse(company) });
    }
    setChecking(false);
  }, []);

  if (checking) return null;
  if (!authData) return <AgentLogin onLogin={(data) => setAuthData(data)} />;
  return <AgentDashboard authData={authData} onLogout={() => setAuthData(null)} />;
};

export default FranchiseAgentPortal;
