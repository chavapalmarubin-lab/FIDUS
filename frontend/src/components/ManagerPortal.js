import React, { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import {
  Shield, LogOut, RefreshCw, Loader2, ArrowLeft, Activity,
  TrendingUp, TrendingDown, DollarSign, AlertTriangle, Target,
  FileText, Download, CheckCircle, XCircle, Clock
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Input } from './ui/input';
import { Label } from './ui/label';

const API_URL = process.env.REACT_APP_BACKEND_URL;
const fmt = (v) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(v || 0);

// ─── LOGIN ───
const ManagerLogin = ({ onLogin }) => {
  const [creds, setCreds] = useState({ email: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!creds.email || !creds.password) { setError('Enter email and password'); return; }
    setLoading(true); setError('');
    try {
      const res = await fetch(`${API_URL}/api/manager/login`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: creds.email.trim(), password: creds.password.trim() })
      });
      const data = await res.json();
      if (!res.ok) { setError(data.detail || 'Login failed'); return; }
      if (data.success) {
        localStorage.setItem('manager_token', data.token);
        localStorage.setItem('manager_data', JSON.stringify(data.manager));
        onLogin(data);
      }
    } catch { setError('Network error'); }
    finally { setLoading(false); }
  };

  return (
    <div data-testid="manager-login-page" className="min-h-screen flex items-center justify-center" style={{ background: 'linear-gradient(135deg, #0c1222 0%, #1a0a2e 50%, #0a1628 100%)' }}>
      <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} className="w-full max-w-md mx-4">
        <Card className="border-0 shadow-2xl" style={{ background: 'rgba(15, 23, 42, 0.95)', border: '1px solid rgba(168, 85, 247, 0.2)' }}>
          <CardHeader className="text-center pb-2">
            <div className="flex justify-center mb-4">
              <div className="w-16 h-16 rounded-2xl flex items-center justify-center" style={{ background: 'linear-gradient(135deg, #a855f7, #7c3aed)' }}>
                <Shield className="w-8 h-8 text-white" />
              </div>
            </div>
            <CardTitle className="text-2xl font-bold text-white">Manager Portal</CardTitle>
            <p className="text-sm text-slate-400 mt-1">View your strategy risk analysis & compliance</p>
          </CardHeader>
          <CardContent className="pt-4">
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label className="text-slate-300 text-sm">Email</Label>
                <Input data-testid="manager-login-email" type="email" placeholder="manager@fidus.com" value={creds.email} onChange={e => setCreds({...creds, email: e.target.value})} className="bg-slate-800/60 border-slate-700 text-white placeholder:text-slate-500 focus:border-purple-500" />
              </div>
              <div className="space-y-2">
                <Label className="text-slate-300 text-sm">Password</Label>
                <Input data-testid="manager-login-password" type="password" placeholder="Enter password" value={creds.password} onChange={e => setCreds({...creds, password: e.target.value})} className="bg-slate-800/60 border-slate-700 text-white placeholder:text-slate-500 focus:border-purple-500" />
              </div>
              {error && <div className="text-red-400 text-sm bg-red-500/10 border border-red-500/20 rounded-lg p-3">{error}</div>}
              <Button data-testid="manager-login-submit" type="submit" disabled={loading} className="w-full h-11 font-semibold text-white" style={{ background: 'linear-gradient(135deg, #a855f7, #7c3aed)' }}>
                {loading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}{loading ? 'Signing in...' : 'Sign In'}
              </Button>
            </form>
            <div className="mt-6 text-center">
              <a href="/" className="text-xs text-slate-500 hover:text-purple-400 flex items-center justify-center gap-1"><ArrowLeft className="w-3 h-3" /> Back to FIDUS</a>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
};

// ─── RISK PARAMS ───
const RISK_PARAMS = [
  { p: 'Risk Per Trade', v: '0.25–0.75%' }, { p: 'Intraday Max DD', v: '5% (hard stop)' },
  { p: 'Weekly Max Loss', v: '6%' }, { p: 'Monthly Max DD', v: '10%' },
  { p: 'Max Margin', v: '25%' }, { p: 'Leverage', v: '200:1' },
  { p: 'Force Flat', v: '21:50 UTC' }, { p: 'Overnight', v: 'PROHIBITED' },
];

const SIZING = [
  { asset: 'GOLD', lots: '0.10–0.30', risk: 'HIGH', max: 3 },
  { asset: 'FOREX Majors', lots: '0.50–1.00', risk: 'MEDIUM', max: '5–7' },
  { asset: 'FOREX Crosses', lots: '0.30–0.70', risk: 'MEDIUM', max: '4–5' },
  { asset: 'INDICES', lots: '1.0–3.0', risk: 'MED-HIGH', max: '3–5' },
  { asset: 'BTC', lots: '0.10–0.30', risk: 'HIGH', max: '2–3' },
];

// ─── DASHBOARD ───
const ManagerDashboard = ({ authData, onLogout }) => {
  const [strategies, setStrategies] = useState([]);
  const [selectedAccount, setSelectedAccount] = useState(null);
  const [riskAnalysis, setRiskAnalysis] = useState(null);
  const [dailyPnl, setDailyPnl] = useState(null);
  const [trades, setTrades] = useState([]);
  const [loading, setLoading] = useState(true);
  const [analysisLoading, setAnalysisLoading] = useState(false);

  const token = authData?.token || localStorage.getItem('manager_token');
  const manager = authData?.manager || JSON.parse(localStorage.getItem('manager_data') || '{}');
  const headers = { 'Authorization': `Bearer ${token}` };

  const fetchStrategies = useCallback(async () => {
    try {
      const res = await fetch(`${API_URL}/api/manager/strategies`, { headers });
      const data = await res.json();
      if (data.success) {
        setStrategies(data.strategies);
        if (data.strategies.length > 0 && !selectedAccount) setSelectedAccount(data.strategies[0].account);
      }
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  }, [token]);

  useEffect(() => { fetchStrategies(); }, [fetchStrategies]);

  const fetchRiskAnalysis = useCallback(async (accId) => {
    setAnalysisLoading(true); setRiskAnalysis(null); setDailyPnl(null); setTrades([]);
    try {
      const [riskRes, pnlRes, tradeRes] = await Promise.all([
        fetch(`${API_URL}/api/manager/risk-analysis/${accId}`, { headers }),
        fetch(`${API_URL}/api/manager/daily-pnl/${accId}?days=30`, { headers }),
        fetch(`${API_URL}/api/manager/trade-history/${accId}?days=14`, { headers })
      ]);
      const riskData = await riskRes.json();
      const pnlData = await pnlRes.json();
      const tradeData = await tradeRes.json();
      if (riskData.success) setRiskAnalysis(riskData.analysis);
      if (pnlData.success) setDailyPnl(pnlData);
      if (tradeData.success) setTrades(tradeData.trades || []);
    } catch (e) { console.error(e); }
    finally { setAnalysisLoading(false); }
  }, [token]);

  useEffect(() => { if (selectedAccount) fetchRiskAnalysis(selectedAccount); }, [selectedAccount, fetchRiskAnalysis]);

  const handleLogout = () => { localStorage.removeItem('manager_token'); localStorage.removeItem('manager_data'); onLogout(); };

  const sel = strategies.find(s => s.account === selectedAccount) || {};
  const dd = sel.initial_allocation ? ((sel.equity - sel.initial_allocation) / sel.initial_allocation * 100) : 0;
  const riskScore = riskAnalysis?.risk_control_score?.score ?? riskAnalysis?.risk_control?.risk_control_score?.score ?? riskAnalysis?.risk_control?.score ?? 0;
  const riskLabel = riskScore >= 80 ? 'Strong' : riskScore >= 60 ? 'Moderate' : riskScore >= 40 ? 'Weak' : 'Critical';
  const riskColor = riskScore >= 80 ? '#10b981' : riskScore >= 60 ? '#0ea5e9' : riskScore >= 40 ? '#f59e0b' : '#ef4444';
  const maxDD = riskAnalysis?.risk_control_score?.drawdown?.max_pct || riskAnalysis?.risk_control?.risk_control_score?.drawdown?.max_pct || Math.abs(dd);
  const currentDD = riskAnalysis?.risk_control_score?.drawdown?.current_pct || riskAnalysis?.risk_control?.risk_control_score?.drawdown?.current_pct || 0;
  const ddStatus = riskAnalysis?.risk_control_score?.drawdown?.status || riskAnalysis?.risk_control?.risk_control_score?.drawdown?.status || 'unknown';

  return (
    <div data-testid="manager-portal" className="min-h-screen" style={{ background: '#080c18' }}>
      {/* Header */}
      <header className="border-b border-purple-900/30" style={{ background: 'rgba(8, 12, 24, 0.95)', backdropFilter: 'blur(12px)' }}>
        <div className="max-w-6xl mx-auto px-4 sm:px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl flex items-center justify-center" style={{ background: 'linear-gradient(135deg, #a855f7, #7c3aed)' }}>
              <Shield className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-white">{manager.name} — Risk Dashboard</h1>
              <p className="text-xs text-slate-500">FIDUS Manager Portal | {manager.allowed_account_names?.join(' + ') || ''}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm" onClick={fetchStrategies} className="text-slate-400 hover:text-white"><RefreshCw className="w-4 h-4" /></Button>
            <Button data-testid="manager-logout" variant="ghost" size="sm" onClick={handleLogout} className="text-slate-400 hover:text-red-400"><LogOut className="w-4 h-4" /></Button>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 sm:px-6 py-6 space-y-6">
        {loading ? (
          <div className="flex justify-center py-20"><Loader2 className="w-8 h-8 animate-spin text-purple-400" /></div>
        ) : (
          <>
            {/* Strategy Selector */}
            <div className="flex gap-3">
              {strategies.map(s => (
                <button key={s.account} onClick={() => setSelectedAccount(s.account)}
                  className={`flex-1 p-4 rounded-xl border transition-all ${selectedAccount === s.account ? 'border-purple-500/50 bg-purple-900/20' : 'border-slate-700/30 bg-slate-800/30 hover:border-slate-600/50'}`}>
                  <div className="text-left">
                    <div className="text-white font-bold text-sm">{s.manager_name}</div>
                    <div className="text-slate-500 text-xs">#{s.account}</div>
                    <div className="text-purple-400 font-bold text-lg mt-1">{fmt(s.equity)}</div>
                    <div className="text-slate-400 text-xs">{s.total_trades} trades | {s.win_rate}% WR</div>
                  </div>
                </button>
              ))}
            </div>

            {/* Drawdown Banner */}
            {maxDD >= 5 && (
              <div className={`p-4 rounded-lg border flex items-center gap-3 ${maxDD >= 10 ? 'bg-red-900/20 border-red-500/40' : 'bg-amber-900/20 border-amber-500/40'}`}>
                <AlertTriangle className={`w-6 h-6 ${maxDD >= 10 ? 'text-red-400' : 'text-amber-400'}`} />
                <div>
                  <h3 className={`font-bold ${maxDD >= 10 ? 'text-red-400' : 'text-amber-400'}`}>{maxDD >= 10 ? 'CRITICAL — STOP TRADING' : 'WARNING — REDUCE EXPOSURE'}</h3>
                  <p className="text-slate-300 text-sm">Max Drawdown: {maxDD.toFixed(2)}% | Current: {currentDD.toFixed(2)}% | Status: {ddStatus.toUpperCase()}</p>
                </div>
              </div>
            )}

            {/* KPI Strip */}
            <div className="grid grid-cols-3 md:grid-cols-6 gap-3 p-4 bg-slate-800/30 rounded-xl border border-slate-700/20">
              {[
                { l: 'EQUITY', v: fmt(sel.equity), c: '#a855f7' },
                { l: 'INITIAL', v: fmt(sel.initial_allocation), c: '#64748b' },
                { l: 'DRAWDOWN', v: `${dd.toFixed(2)}%`, c: dd < -5 ? '#ef4444' : dd < -3 ? '#f59e0b' : '#10b981' },
                { l: 'TRADES', v: sel.total_trades, c: '#0ea5e9' },
                { l: 'WIN RATE', v: `${sel.win_rate}%`, c: sel.win_rate >= 50 ? '#10b981' : '#ef4444' },
                { l: 'RISK SCORE', v: riskScore || '...', c: riskColor },
              ].map((k, i) => (
                <div key={i} className="text-center">
                  <div className="text-lg font-bold font-mono" style={{ color: k.c }}>{k.v}</div>
                  <div className="text-[10px] text-slate-500">{k.l}</div>
                </div>
              ))}
            </div>

            {/* Risk Analysis Content */}
            {analysisLoading ? (
              <div className="flex justify-center py-16"><Loader2 className="w-8 h-8 animate-spin text-purple-400" /></div>
            ) : riskAnalysis ? (
              <div className="space-y-4">
                {/* Risk Policy */}
                {(riskAnalysis.risk_control_score || riskAnalysis.risk_control?.risk_control_score) && (
                  <Card className="border-slate-700/30 bg-slate-800/20">
                    <CardHeader className="pb-3">
                      <CardTitle className="text-sm text-slate-200">Risk Policy (Drawdown Priority)</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-5 gap-3 text-center text-sm">
                        <div className="p-3 bg-red-900/20 border border-red-500/20 rounded-lg"><div className="text-red-400 text-xs">DD WARNING</div><div className="text-red-400 font-bold text-lg">5%</div></div>
                        <div className="p-3 bg-red-900/30 border border-red-500/30 rounded-lg"><div className="text-red-400 text-xs">DD CRITICAL</div><div className="text-red-400 font-bold text-lg">10%</div></div>
                        <div className="p-3 bg-slate-700/30 rounded-lg"><div className="text-slate-400 text-xs">MAX RISK/TRADE</div><div className="text-white font-bold text-lg">1%</div></div>
                        <div className="p-3 bg-slate-700/30 rounded-lg"><div className="text-slate-400 text-xs">MAX DAILY LOSS</div><div className="text-white font-bold text-lg">3%</div></div>
                        <div className="p-3 rounded-lg" style={{ border: `2px solid ${riskColor}`, background: `${riskColor}10` }}>
                          <div className="text-3xl font-black font-mono" style={{ color: riskColor }}>{riskScore}</div>
                          <div className="text-xs font-bold" style={{ color: riskColor }}>{riskLabel.toUpperCase()}</div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )}

                {/* Compliance Checklist */}
                <Card className="border-slate-700/30 bg-slate-800/20">
                  <CardHeader className="pb-3 flex flex-row items-center justify-between">
                    <CardTitle className="text-sm text-slate-200">Compliance Status</CardTitle>
                    <button onClick={() => {
                      fetch(`${API_URL}/api/admin/risk/report/pdf/${selectedAccount}`, { headers })
                        .then(r => r.blob()).then(b => { const u = URL.createObjectURL(b); const a = document.createElement('a'); a.href = u; a.download = `FIDUS_Risk_Report_${sel.manager_name?.replace(/\s+/g,'_')}_${selectedAccount}.pdf`; a.click(); });
                    }}
                      style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '6px 14px', background: 'linear-gradient(135deg, #ef4444, #dc2626)', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '11px', fontWeight: 'bold' }}>
                      <Download size={12} /> Download PDF
                    </button>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {[
                        { check: 'Max Drawdown ≤ 10%', actual: `${maxDD.toFixed(2)}%`, sev: maxDD > 10 ? 'FAIL' : maxDD > 5 ? 'WARN' : 'PASS' },
                        { check: 'Current DD ≤ 5%', actual: `${currentDD.toFixed(2)}%`, sev: currentDD > 5 ? 'FAIL' : currentDD > 3 ? 'WARN' : 'PASS' },
                        { check: 'Win Rate ≥ 30%', actual: `${sel.win_rate}%`, sev: sel.win_rate >= 30 ? 'PASS' : 'FAIL' },
                        { check: 'Profit Factor ≥ 1.0', actual: `${sel.profit_factor}`, sev: sel.profit_factor >= 1.5 ? 'PASS' : sel.profit_factor >= 1.0 ? 'WARN' : 'FAIL' },
                        { check: 'Risk Score ≥ 60', actual: `${riskScore}/100`, sev: riskScore >= 80 ? 'PASS' : riskScore >= 60 ? 'WARN' : 'FAIL' },
                      ].map((c, i) => {
                        const colors = { PASS: '#10b981', WARN: '#f59e0b', FAIL: '#ef4444' };
                        return (
                          <div key={i} className="flex justify-between items-center p-2 rounded-lg" style={{ background: `${colors[c.sev]}08`, border: `1px solid ${colors[c.sev]}20` }}>
                            <span className="text-slate-300 text-xs">{c.check}</span>
                            <div className="flex items-center gap-2">
                              <span className="text-slate-400 text-xs font-mono">{c.actual}</span>
                              <span className="text-[10px] font-bold px-2 py-0.5 rounded" style={{ color: colors[c.sev], background: `${colors[c.sev]}15` }}>{c.sev}</span>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </CardContent>
                </Card>

                {/* Risk Params + Position Sizing */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Card className="border-red-500/10 bg-slate-800/20">
                    <CardHeader className="pb-2"><CardTitle className="text-xs text-red-400">FIDUS Risk Parameters — MANDATORY</CardTitle></CardHeader>
                    <CardContent>
                      <div className="space-y-1">
                        {RISK_PARAMS.map((r, i) => (
                          <div key={i} className="flex justify-between text-xs py-1">
                            <span className="text-slate-400">{r.p}</span>
                            <span className="text-red-300 font-mono font-bold">{r.v}</span>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                  <Card className="border-cyan-500/10 bg-slate-800/20">
                    <CardHeader className="pb-2"><CardTitle className="text-xs text-cyan-400">Position Sizing Per Asset</CardTitle></CardHeader>
                    <CardContent>
                      <table className="w-full text-xs">
                        <thead><tr className="text-slate-500"><th className="text-left py-1">Asset</th><th className="text-right">Lots/$100K</th><th className="text-right">Max Trades</th></tr></thead>
                        <tbody>
                          {SIZING.map((s, i) => (
                            <tr key={i} className="border-t border-slate-700/20">
                              <td className="py-1 text-slate-300">{s.asset}</td>
                              <td className="py-1 text-right text-cyan-400 font-mono">{s.lots}</td>
                              <td className="py-1 text-right text-slate-400 font-mono">{s.max}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </CardContent>
                  </Card>
                </div>

                {/* Daily P&L with Breach Detection */}
                {dailyPnl && (
                  <Card className="border-slate-700/30 bg-slate-800/20">
                    <CardHeader className="pb-3 flex flex-row items-center justify-between">
                      <CardTitle className="text-sm text-slate-200 flex items-center gap-2">
                        <Activity size={16} className="text-amber-400" /> Daily P&L — Breach Analysis
                      </CardTitle>
                      <div className="flex gap-3 text-xs">
                        <span className="text-emerald-400">{dailyPnl.summary?.profitable_days || 0} profitable</span>
                        <span className="text-red-400">{dailyPnl.summary?.losing_days || 0} losing</span>
                        <span className="text-amber-400">{dailyPnl.summary?.breach_days || 0} breach days</span>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-1.5 max-h-[500px] overflow-y-auto">
                        {(dailyPnl.daily_pnl || []).map((day, i) => (
                          <div key={i} className={`p-3 rounded-lg border ${day.has_breach ? 'border-red-500/30 bg-red-900/10' : day.daily_pnl < 0 ? 'border-amber-500/10 bg-amber-900/5' : 'border-slate-700/20 bg-slate-800/20'}`}>
                            <div className="flex items-center justify-between">
                              <div className="flex items-center gap-3">
                                <span className="text-white font-mono text-xs font-bold w-20">{day.date}</span>
                                <span className={`font-mono font-bold text-sm ${day.daily_pnl >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                                  ${day.daily_pnl >= 0 ? '+' : ''}{day.daily_pnl.toLocaleString(undefined, {minimumFractionDigits: 2})}
                                </span>
                                <span className="text-slate-500 text-xs">{day.trade_count}T ({day.wins}W/{day.losses}L)</span>
                              </div>
                              <div className="flex items-center gap-3">
                                <span className="text-slate-400 text-xs font-mono">Eq: ${day.running_equity?.toLocaleString()}</span>
                                <span className={`text-xs font-mono ${day.drawdown_from_peak <= -5 ? 'text-red-400' : day.drawdown_from_peak <= -3 ? 'text-amber-400' : 'text-slate-500'}`}>
                                  DD: {day.drawdown_from_peak?.toFixed(2)}%
                                </span>
                                {day.symbols && <span className="text-slate-600 text-[10px]">{day.symbols.join(', ')}</span>}
                              </div>
                            </div>
                            {day.has_breach && (
                              <div className="mt-2 flex gap-2 flex-wrap">
                                {day.breaches.map((b, j) => (
                                  <span key={j} className={`text-[10px] px-2 py-0.5 rounded ${b.severity === 'CRITICAL' ? 'bg-red-500/20 text-red-400 border border-red-500/30' : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'}`}>
                                    {b.rule}: {b.value}
                                  </span>
                                ))}
                              </div>
                            )}
                            {day.max_single_loss < -100 && (
                              <div className="mt-1 text-[10px] text-red-400/70">
                                Worst trade: ${day.max_single_loss.toLocaleString()} | Best: ${day.max_single_win?.toLocaleString()}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}

                {/* Recent Trades */}
                {trades.length > 0 && (
                  <Card className="border-slate-700/30 bg-slate-800/20">
                    <CardHeader className="pb-3">
                      <CardTitle className="text-sm text-slate-200">Recent Trades (Last 14 Days) — {trades.length} trades</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="overflow-x-auto max-h-[400px] overflow-y-auto">
                        <table className="w-full text-xs">
                          <thead className="sticky top-0 bg-slate-900">
                            <tr className="text-slate-500 border-b border-slate-700/30">
                              <th className="text-left py-2 px-2">Time</th>
                              <th className="text-left py-2 px-2">Symbol</th>
                              <th className="text-right py-2 px-2">Volume</th>
                              <th className="text-right py-2 px-2">Price</th>
                              <th className="text-right py-2 px-2">P&L</th>
                              <th className="text-center py-2 px-2">Type</th>
                            </tr>
                          </thead>
                          <tbody>
                            {trades.slice(0, 100).map((t, i) => (
                              <tr key={i} className="border-b border-slate-700/10 hover:bg-slate-800/30">
                                <td className="py-1.5 px-2 text-slate-400 font-mono">{t.time ? new Date(t.time).toLocaleString('en-US', {month:'short', day:'numeric', hour:'2-digit', minute:'2-digit'}) : '-'}</td>
                                <td className="py-1.5 px-2 text-white font-medium">{t.symbol || '-'}</td>
                                <td className="py-1.5 px-2 text-right text-slate-300 font-mono">{t.volume?.toFixed(2)}</td>
                                <td className="py-1.5 px-2 text-right text-slate-400 font-mono">{t.price?.toFixed(2)}</td>
                                <td className={`py-1.5 px-2 text-right font-mono font-bold ${(t.profit || 0) >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                                  ${(t.profit || 0) >= 0 ? '+' : ''}{(t.profit || 0).toFixed(2)}
                                </td>
                                <td className="py-1.5 px-2 text-center">
                                  <span className={`text-[9px] px-1.5 py-0.5 rounded ${t.entry === 0 ? 'bg-sky-500/15 text-sky-400' : 'bg-slate-600/30 text-slate-400'}`}>
                                    {t.entry === 0 ? 'OPEN' : 'CLOSE'}
                                  </span>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </CardContent>
                  </Card>
                )}
              </div>
            ) : (
              <div className="text-center py-16 text-slate-500">
                <Shield className="w-12 h-12 mx-auto mb-3 opacity-30" />
                <p>Select a strategy to view risk analysis.</p>
              </div>
            )}
          </>
        )}
      </main>
      <footer className="border-t border-slate-800/50 mt-12 py-4 text-center"><p className="text-xs text-slate-600">FIDUS Investment Management | Manager Portal | Read-Only Risk View</p></footer>
    </div>
  );
};

// ─── MAIN ───
const ManagerPortal = () => {
  const [authData, setAuthData] = useState(null);
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('manager_token');
    const data = localStorage.getItem('manager_data');
    if (token && data) setAuthData({ token, manager: JSON.parse(data) });
    setChecking(false);
  }, []);

  if (checking) return null;
  if (!authData) return <ManagerLogin onLogin={setAuthData} />;
  return <ManagerDashboard authData={authData} onLogout={() => setAuthData(null)} />;
};

export default ManagerPortal;
