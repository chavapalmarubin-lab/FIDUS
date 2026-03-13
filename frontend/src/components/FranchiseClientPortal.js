import React, { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import {
  Wallet, DollarSign, TrendingUp, Clock, LogOut, RefreshCw,
  ArrowLeft, Loader2, Calendar, FileText, Shield, CheckCircle,
  ArrowUpRight, Building2
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Input } from './ui/input';
import { Label } from './ui/label';

const API_URL = process.env.REACT_APP_BACKEND_URL;
const fmt = (v) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(v || 0);

// ─────────────────────────────────────────
// CLIENT LOGIN
// ─────────────────────────────────────────
const ClientLogin = ({ onLogin }) => {
  const [creds, setCreds] = useState({ email: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!creds.email || !creds.password) { setError('Enter email and password'); return; }
    setLoading(true); setError('');
    try {
      const res = await fetch(`${API_URL}/api/franchise/auth/client/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: creds.email.trim(), password: creds.password.trim() })
      });
      const data = await res.json();
      if (!res.ok) { setError(data.detail || 'Login failed'); return; }
      if (data.success) {
        localStorage.setItem('franchise_client_token', data.token);
        localStorage.setItem('franchise_client_data', JSON.stringify(data.client));
        localStorage.setItem('franchise_client_company', JSON.stringify(data.company));
        onLogin(data);
      }
    } catch { setError('Network error'); }
    finally { setLoading(false); }
  };

  return (
    <div data-testid="franchise-client-login-page" className="min-h-screen flex items-center justify-center" style={{ background: 'linear-gradient(135deg, #0c1222 0%, #111d35 50%, #0a1628 100%)' }}>
      <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }} className="w-full max-w-md mx-4">
        <Card className="border-0 shadow-2xl" style={{ background: 'rgba(15, 23, 42, 0.95)', border: '1px solid rgba(16, 185, 129, 0.2)' }}>
          <CardHeader className="text-center pb-2">
            <div className="flex justify-center mb-4">
              <div className="w-16 h-16 rounded-2xl flex items-center justify-center" style={{ background: 'linear-gradient(135deg, #10b981, #059669)' }}>
                <Wallet className="w-8 h-8 text-white" />
              </div>
            </div>
            <CardTitle className="text-2xl font-bold text-white">Investor Portal</CardTitle>
            <p className="text-sm text-slate-400 mt-1">View your investment performance</p>
          </CardHeader>
          <CardContent className="pt-4">
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label className="text-slate-300 text-sm">Email</Label>
                <Input data-testid="client-login-email" type="email" placeholder="your@email.com" value={creds.email} onChange={(e) => setCreds({...creds, email: e.target.value})} className="bg-slate-800/60 border-slate-700 text-white placeholder:text-slate-500 focus:border-emerald-500" />
              </div>
              <div className="space-y-2">
                <Label className="text-slate-300 text-sm">Password</Label>
                <Input data-testid="client-login-password" type="password" placeholder="Enter password" value={creds.password} onChange={(e) => setCreds({...creds, password: e.target.value})} className="bg-slate-800/60 border-slate-700 text-white placeholder:text-slate-500 focus:border-emerald-500" />
              </div>
              {error && <div data-testid="client-login-error" className="text-red-400 text-sm bg-red-500/10 border border-red-500/20 rounded-lg p-3">{error}</div>}
              <Button data-testid="client-login-submit" type="submit" disabled={loading} className="w-full h-11 font-semibold text-white" style={{ background: 'linear-gradient(135deg, #10b981, #059669)' }}>
                {loading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}{loading ? 'Signing in...' : 'Sign In'}
              </Button>
            </form>
            <div className="mt-6 text-center">
              <a href="/franchise/login" className="text-xs text-slate-500 hover:text-emerald-400 transition-colors flex items-center justify-center gap-1"><ArrowLeft className="w-3 h-3" /> Company Admin Portal</a>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
};

// ─────────────────────────────────────────
// CLIENT DASHBOARD
// ─────────────────────────────────────────
const ClientDashboard = ({ authData, onLogout }) => {
  const [overview, setOverview] = useState(null);
  const [loading, setLoading] = useState(true);

  const token = authData?.token || localStorage.getItem('franchise_client_token');
  const clientInfo = authData?.client || JSON.parse(localStorage.getItem('franchise_client_data') || '{}');
  const company = authData?.company || JSON.parse(localStorage.getItem('franchise_client_company') || '{}');

  const fetchData = useCallback(async () => {
    try {
      const res = await fetch(`${API_URL}/api/franchise/dashboard/client/overview`, { headers: { 'Authorization': `Bearer ${token}` } });
      const data = await res.json();
      if (data.success) setOverview(data);
    } catch (e) { console.error('Client overview error:', e); }
    finally { setLoading(false); }
  }, [token]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const handleLogout = () => {
    localStorage.removeItem('franchise_client_token');
    localStorage.removeItem('franchise_client_data');
    localStorage.removeItem('franchise_client_company');
    onLogout();
  };

  const client = overview?.client || clientInfo;
  const summary = overview?.summary || {};
  const investments = overview?.investments || [];
  const terms = overview?.fund_terms || {};

  return (
    <div data-testid="franchise-client-portal" className="min-h-screen" style={{ background: '#0a0f1a' }}>
      <header className="border-b border-slate-800" style={{ background: 'rgba(10, 15, 26, 0.95)', backdropFilter: 'blur(12px)' }}>
        <div className="max-w-5xl mx-auto px-4 sm:px-6 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl flex items-center justify-center" style={{ background: `linear-gradient(135deg, ${company.primary_color || '#10b981'}, ${company.primary_color || '#10b981'}dd)` }}>
              <Wallet className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-white leading-tight">{company.company_name || 'Investor Portal'}</h1>
              <p className="text-xs text-slate-500">{client.first_name} {client.last_name}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm" onClick={fetchData} className="text-slate-400 hover:text-white"><RefreshCw className="w-4 h-4" /></Button>
            <Button data-testid="client-logout-btn" variant="ghost" size="sm" onClick={handleLogout} className="text-slate-400 hover:text-red-400"><LogOut className="w-4 h-4" /></Button>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 sm:px-6 py-6 space-y-6">
        {loading ? (
          <div className="flex items-center justify-center py-20"><Loader2 className="w-8 h-8 animate-spin text-emerald-400" /></div>
        ) : (
          <>
            {/* KPI Cards */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              <KPI icon={DollarSign} label="Total Invested" value={fmt(summary.total_invested)} color="#0ea5e9" />
              <KPI icon={TrendingUp} label="Returns Earned" value={fmt(summary.total_returns_earned)} color="#10b981" />
              <KPI icon={ArrowUpRight} label="Returns Paid" value={fmt(summary.total_returns_paid)} color="#f59e0b" />
              <KPI icon={Clock} label="Pending Returns" value={fmt(summary.pending_returns)} color="#8b5cf6" />
            </div>

            {/* Account Status */}
            <Card className="border-slate-700/50 bg-slate-800/40">
              <CardHeader className="pb-3"><CardTitle className="text-base text-slate-200">Account Status</CardTitle></CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div><span className="text-slate-500">Status</span>
                    <div className="mt-1"><Badge variant="outline" className={client.status === 'active' ? 'border-emerald-500/40 text-emerald-400' : 'border-amber-500/40 text-amber-400'}>{client.status || 'pending'}</Badge></div>
                  </div>
                  <div><span className="text-slate-500">KYC</span>
                    <div className="mt-1"><Badge variant="outline" className={client.kyc_status === 'approved' ? 'border-emerald-500/40 text-emerald-400' : 'border-amber-500/40 text-amber-400'}>{client.kyc_status || 'pending'}</Badge></div>
                  </div>
                  <div><span className="text-slate-500">Return Rate</span><p className="text-emerald-400 font-semibold mt-1">{summary.visible_return_pct || 2.0}% monthly</p></div>
                  <div><span className="text-slate-500">Payment</span><p className="text-slate-200 font-medium mt-1 capitalize">{terms.payment_frequency || 'quarterly'}</p></div>
                </div>
              </CardContent>
            </Card>

            {/* Contract Timeline */}
            <Card className="border-slate-700/50 bg-slate-800/40">
              <CardHeader className="pb-3"><CardTitle className="text-base text-slate-200">Contract Timeline</CardTitle></CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div><span className="text-slate-500">Investment Date</span><p className="text-slate-200 mt-1">{client.investment_date ? new Date(client.investment_date).toLocaleDateString() : '-'}</p></div>
                  <div><span className="text-slate-500">Incubation Ends</span><p className="text-amber-400 mt-1">{client.incubation_end_date ? new Date(client.incubation_end_date).toLocaleDateString() : '-'}</p></div>
                  <div><span className="text-slate-500">Contract Start</span><p className="text-slate-200 mt-1">{client.contract_start_date ? new Date(client.contract_start_date).toLocaleDateString() : '-'}</p></div>
                  <div><span className="text-slate-500">Contract End</span><p className="text-sky-400 mt-1">{client.contract_end_date ? new Date(client.contract_end_date).toLocaleDateString() : '-'}</p></div>
                </div>
              </CardContent>
            </Card>

            {/* Investments Table */}
            <Card className="border-slate-700/50 bg-slate-800/40">
              <CardHeader className="pb-3"><CardTitle className="text-base text-slate-200">Investments ({investments.length})</CardTitle></CardHeader>
              <CardContent>
                {investments.length === 0 ? (
                  <div className="text-center py-8 text-slate-500"><FileText className="w-10 h-10 mx-auto mb-2 opacity-30" /><p>No investments yet.</p></div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead><tr className="border-b border-slate-700/50 text-slate-400">
                        <th className="text-left p-3">Fund</th><th className="text-right p-3">Amount</th><th className="text-right p-3">Returns Earned</th><th className="text-right p-3">Returns Paid</th><th className="text-center p-3">Status</th>
                      </tr></thead>
                      <tbody>
                        {investments.map((inv, i) => (
                          <tr key={i} className="border-b border-slate-700/30">
                            <td className="p-3 text-slate-200 font-medium">{inv.fund_type || 'BALANCE'}</td>
                            <td className="p-3 text-right text-slate-200">{fmt(inv.amount)}</td>
                            <td className="p-3 text-right text-emerald-400">{fmt(inv.total_returns_earned)}</td>
                            <td className="p-3 text-right text-sky-400">{fmt(inv.total_returns_paid)}</td>
                            <td className="p-3 text-center"><Badge variant="outline" className={inv.status === 'active' ? 'border-emerald-500/40 text-emerald-400' : 'border-amber-500/40 text-amber-400'}>{inv.status}</Badge></td>
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
// MAIN EXPORT: Client Portal App
// ─────────────────────────────────────────
const FranchiseClientPortal = () => {
  const [authData, setAuthData] = useState(null);
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('franchise_client_token');
    const clientData = localStorage.getItem('franchise_client_data');
    const company = localStorage.getItem('franchise_client_company');
    if (token && clientData && company) {
      setAuthData({ token, client: JSON.parse(clientData), company: JSON.parse(company) });
    }
    setChecking(false);
  }, []);

  if (checking) return null;
  if (!authData) return <ClientLogin onLogin={(data) => setAuthData(data)} />;
  return <ClientDashboard authData={authData} onLogout={() => setAuthData(null)} />;
};

export default FranchiseClientPortal;
