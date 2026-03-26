import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Shield, LogOut, Plus, Minus, Info, MoreHorizontal, ChevronRight,
  DollarSign, TrendingUp, Calendar, ArrowUpRight, ArrowDownRight,
  Calculator, CreditCard, Clock, CheckCircle, Home, PieChart,
  Settings, Loader2, ArrowLeft, X
} from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;
const LUCRUM_SIGNUP = 'https://my.lucrumfx.com/auth/signup?ib=fiso3999&ref=STD%20IB';
const LUCRUM_DEPOSIT = 'https://my.lucrumfx.com';
const fmt = v => `$${(v||0).toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2})}`;

// ─── LOGIN ───
const RetailLogin = ({ onLogin }) => {
  const [creds, setCreds] = useState({ email: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!creds.email || !creds.password) { setError('Enter email and password'); return; }
    setLoading(true); setError('');
    try {
      const res = await fetch(`${API}/api/retail/login`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: creds.email.trim(), password: creds.password.trim() })
      });
      const data = await res.json();
      if (!res.ok) { setError(data.detail || 'Login failed'); return; }
      if (data.success) {
        localStorage.setItem('retail_token', data.token);
        localStorage.setItem('retail_client', JSON.stringify(data.client));
        onLogin(data);
      }
    } catch { setError('Network error'); }
    finally { setLoading(false); }
  };

  return (
    <div style={{ background: '#050a15', minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20 }}>
      <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} style={{ width: '100%', maxWidth: 400 }}>
        {/* Logo */}
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <div style={{ width: 56, height: 56, borderRadius: 16, background: 'linear-gradient(135deg, #0ea5e9, #06b6d4)', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', marginBottom: 12 }}>
            <Shield size={28} color="white" />
          </div>
          <h1 style={{ color: 'white', fontSize: 24, fontWeight: 800, margin: '0 0 4px' }}>FIDUS</h1>
          <p style={{ color: '#64748b', fontSize: 13 }}>Retail Investment Portal</p>
        </div>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          <input placeholder="Email" type="email" value={creds.email} onChange={e => setCreds({...creds, email: e.target.value})}
            style={{ width: '100%', padding: '14px 16px', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 12, color: 'white', fontSize: 15, outline: 'none', boxSizing: 'border-box' }} />
          <input placeholder="Password" type="password" value={creds.password} onChange={e => setCreds({...creds, password: e.target.value})}
            style={{ width: '100%', padding: '14px 16px', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 12, color: 'white', fontSize: 15, outline: 'none', boxSizing: 'border-box' }} />
          {error && <div style={{ color: '#ef4444', fontSize: 13, padding: '8px 12px', background: 'rgba(239,68,68,0.1)', borderRadius: 8 }}>{error}</div>}
          <button type="submit" disabled={loading}
            style={{ width: '100%', padding: '14px', background: 'linear-gradient(135deg, #0ea5e9, #0284c7)', color: 'white', border: 'none', borderRadius: 12, fontSize: 15, fontWeight: 700, cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}>
            {loading ? <Loader2 size={18} className="animate-spin" /> : null} {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <div style={{ textAlign: 'center', marginTop: 20 }}>
          <p style={{ color: '#64748b', fontSize: 13 }}>Don't have an account?</p>
          <a href={LUCRUM_SIGNUP} target="_blank" rel="noopener noreferrer" style={{ color: '#0ea5e9', fontSize: 14, fontWeight: 600, textDecoration: 'none' }}>Open Account at LUCRUM</a>
        </div>
        <div style={{ textAlign: 'center', marginTop: 12 }}>
          <a href="/retail" style={{ color: '#475569', fontSize: 12, textDecoration: 'none' }}>Back to FIDUS Retail</a>
        </div>
      </motion.div>
    </div>
  );
};

// ─── REVOLUT-STYLE APP ───
const RetailApp = ({ authData, onLogout }) => {
  const [activeView, setActiveView] = useState('home');
  const [clientData, setClientData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [simAmount, setSimAmount] = useState(1000);

  const token = authData?.token || localStorage.getItem('retail_token');
  const clientInfo = authData?.client || JSON.parse(localStorage.getItem('retail_client') || '{}');

  const fetchData = useCallback(async () => {
    try {
      const res = await fetch(`${API}/api/retail/dashboard`, { headers: { 'Authorization': `Bearer ${token}` } });
      const data = await res.json();
      if (data.success) setClientData(data);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  }, [token]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const handleLogout = () => {
    localStorage.removeItem('retail_token');
    localStorage.removeItem('retail_client');
    onLogout();
  };

  const client = clientData?.client || clientInfo;
  const balance = clientData?.balance || 0;
  const totalReturns = clientData?.total_returns || 0;
  const monthlyReturn = balance * 0.015;
  const payments = clientData?.payments || [];
  const fundHealth = clientData?.fund_health || [];

  if (loading) return <div style={{ background: '#050a15', minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}><Loader2 size={32} color="#0ea5e9" className="animate-spin" /></div>;

  return (
    <div style={{ background: '#050a15', minHeight: '100vh', maxWidth: 480, margin: '0 auto', position: 'relative', paddingBottom: 80 }}>
      {/* ─── HOME VIEW ─── */}
      {activeView === 'home' && (
        <div>
          {/* Header */}
          <div style={{ padding: '16px 20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <p style={{ color: '#64748b', fontSize: 13 }}>Welcome back</p>
              <h2 style={{ color: 'white', fontSize: 18, fontWeight: 700, margin: 0 }}>{client.first_name || client.name}</h2>
            </div>
            <button onClick={handleLogout} style={{ background: 'none', border: 'none', cursor: 'pointer' }}><LogOut size={20} color="#64748b" /></button>
          </div>

          {/* Balance Card */}
          <div style={{ margin: '8px 20px 24px', padding: 28, background: 'linear-gradient(135deg, #0c1829, #0f2140)', border: '1px solid rgba(14,165,233,0.15)', borderRadius: 20, textAlign: 'center' }}>
            <p style={{ color: '#64748b', fontSize: 13, marginBottom: 4 }}>Total Balance</p>
            <h1 style={{ color: 'white', fontSize: 40, fontWeight: 800, margin: '0 0 4px', fontFamily: 'monospace' }}>{fmt(balance)}</h1>
            <p style={{ color: '#10b981', fontSize: 14, fontWeight: 600 }}>+{fmt(totalReturns)} earned</p>
            <div style={{ marginTop: 16, display: 'flex', gap: 8, justifyContent: 'center' }}>
              <div style={{ padding: '6px 14px', background: 'rgba(16,185,129,0.1)', borderRadius: 8, color: '#10b981', fontSize: 12, fontWeight: 600 }}>1.5% monthly</div>
              <div style={{ padding: '6px 14px', background: 'rgba(14,165,233,0.1)', borderRadius: 8, color: '#0ea5e9', fontSize: 12, fontWeight: 600 }}>FIDUS CORE</div>
            </div>
          </div>

          {/* Quick Actions */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 8, padding: '0 20px', marginBottom: 24 }}>
            {[
              { icon: Plus, label: 'Add Money', color: '#10b981', action: () => window.open(LUCRUM_DEPOSIT, '_blank') },
              { icon: Minus, label: 'Withdraw', color: '#f59e0b', action: () => setActiveView('withdraw') },
              { icon: Info, label: 'Product', color: '#0ea5e9', action: () => setActiveView('info') },
              { icon: Calculator, label: 'Simulator', color: '#8b5cf6', action: () => setActiveView('simulator') },
            ].map((a, i) => (
              <button key={i} onClick={a.action} style={{ padding: 14, background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 14, cursor: 'pointer', textAlign: 'center' }}>
                <div style={{ width: 40, height: 40, borderRadius: 12, background: `${a.color}15`, display: 'inline-flex', alignItems: 'center', justifyContent: 'center', marginBottom: 6 }}>
                  <a.icon size={20} color={a.color} />
                </div>
                <div style={{ color: '#94a3b8', fontSize: 11, fontWeight: 500 }}>{a.label}</div>
              </button>
            ))}
          </div>

          {/* Next Payment */}
          <div style={{ margin: '0 20px 20px', padding: 16, background: 'rgba(16,185,129,0.05)', border: '1px solid rgba(16,185,129,0.15)', borderRadius: 14, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <p style={{ color: '#64748b', fontSize: 11, margin: '0 0 2px' }}>Next Payment</p>
              <p style={{ color: 'white', fontSize: 16, fontWeight: 700, margin: 0 }}>{fmt(monthlyReturn)}</p>
            </div>
            <div style={{ textAlign: 'right' }}>
              <p style={{ color: '#10b981', fontSize: 13, fontWeight: 600, margin: 0 }}>End of Month</p>
              <p style={{ color: '#64748b', fontSize: 11, margin: 0 }}>1.5% return</p>
            </div>
          </div>

          {/* Payment Calendar */}
          <div style={{ padding: '0 20px' }}>
            <h3 style={{ color: 'white', fontSize: 16, fontWeight: 700, marginBottom: 12 }}>Payment Schedule</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {Array.from({length: 6}, (_, i) => {
                const d = new Date(); d.setMonth(d.getMonth() + i);
                const mk = `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}`;
                const health = fundHealth.find(f => f.month === mk);
                const funded = health ? health.status === 'green' : true;
                return (
                  <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 14px', background: 'rgba(255,255,255,0.02)', border: `1px solid ${funded ? 'rgba(16,185,129,0.15)' : 'rgba(239,68,68,0.15)'}`, borderRadius: 10 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                      <div style={{ width: 8, height: 8, borderRadius: '50%', background: funded ? '#10b981' : '#ef4444' }} />
                      <span style={{ color: 'white', fontSize: 14, fontWeight: 500 }}>{d.toLocaleString('en-US', { month: 'long', year: 'numeric' })}</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <span style={{ color: '#10b981', fontSize: 14, fontWeight: 700, fontFamily: 'monospace' }}>{fmt(monthlyReturn)}</span>
                      <span style={{ fontSize: 9, padding: '2px 6px', borderRadius: 4, background: funded ? 'rgba(16,185,129,0.1)' : 'rgba(239,68,68,0.1)', color: funded ? '#10b981' : '#ef4444', fontWeight: 600 }}>{funded ? 'Funded' : 'Review'}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* ─── SIMULATOR VIEW ─── */}
      {activeView === 'simulator' && (
        <div style={{ padding: 20 }}>
          <button onClick={() => setActiveView('home')} style={{ background: 'none', border: 'none', color: '#64748b', display: 'flex', alignItems: 'center', gap: 4, marginBottom: 20, cursor: 'pointer', fontSize: 14 }}><ArrowLeft size={18} /> Back</button>
          <h2 style={{ color: 'white', fontSize: 22, fontWeight: 800, marginBottom: 4 }}>Investment Simulator</h2>
          <p style={{ color: '#64748b', fontSize: 13, marginBottom: 20 }}>See what happens if you add more funds</p>

          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 16 }}>
            {[500, 1000, 5000, 10000, 25000].map(v => (
              <button key={v} onClick={() => setSimAmount(v)}
                style={{ padding: '8px 14px', background: simAmount === v ? '#0ea5e9' : 'rgba(255,255,255,0.05)', border: simAmount === v ? 'none' : '1px solid rgba(255,255,255,0.1)', borderRadius: 8, color: 'white', fontSize: 13, fontWeight: 600, cursor: 'pointer' }}>
                +${v.toLocaleString()}
              </button>
            ))}
          </div>

          <div style={{ marginBottom: 24 }}>
            <input type="range" min={100} max={50000} step={100} value={simAmount} onChange={e => setSimAmount(Number(e.target.value))}
              style={{ width: '100%', accentColor: '#0ea5e9' }} />
            <div style={{ textAlign: 'center' }}>
              <span style={{ color: '#0ea5e9', fontSize: 28, fontWeight: 800, fontFamily: 'monospace' }}>+${simAmount.toLocaleString()}</span>
              <span style={{ color: '#64748b', fontSize: 14, marginLeft: 8 }}>additional deposit</span>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            <div style={{ padding: 16, background: 'rgba(255,255,255,0.03)', borderRadius: 12, textAlign: 'center' }}>
              <div style={{ color: '#64748b', fontSize: 11 }}>Current Monthly</div>
              <div style={{ color: 'white', fontSize: 20, fontWeight: 800, fontFamily: 'monospace' }}>{fmt(monthlyReturn)}</div>
            </div>
            <div style={{ padding: 16, background: 'rgba(16,185,129,0.05)', border: '1px solid rgba(16,185,129,0.15)', borderRadius: 12, textAlign: 'center' }}>
              <div style={{ color: '#64748b', fontSize: 11 }}>New Monthly</div>
              <div style={{ color: '#10b981', fontSize: 20, fontWeight: 800, fontFamily: 'monospace' }}>{fmt((balance + simAmount) * 0.015)}</div>
            </div>
            <div style={{ padding: 16, background: 'rgba(255,255,255,0.03)', borderRadius: 12, textAlign: 'center' }}>
              <div style={{ color: '#64748b', fontSize: 11 }}>Current Annual</div>
              <div style={{ color: 'white', fontSize: 20, fontWeight: 800, fontFamily: 'monospace' }}>{fmt(monthlyReturn * 12)}</div>
            </div>
            <div style={{ padding: 16, background: 'rgba(139,92,246,0.05)', border: '1px solid rgba(139,92,246,0.15)', borderRadius: 12, textAlign: 'center' }}>
              <div style={{ color: '#64748b', fontSize: 11 }}>New Annual</div>
              <div style={{ color: '#8b5cf6', fontSize: 20, fontWeight: 800, fontFamily: 'monospace' }}>{fmt((balance + simAmount) * 0.015 * 12)}</div>
            </div>
          </div>

          <a href={LUCRUM_DEPOSIT} target="_blank" rel="noopener noreferrer"
            style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8, width: '100%', padding: '14px', background: 'linear-gradient(135deg, #10b981, #059669)', color: 'white', borderRadius: 12, fontSize: 15, fontWeight: 700, textDecoration: 'none', marginTop: 20, boxSizing: 'border-box' }}>
            <Plus size={18} /> Deposit ${simAmount.toLocaleString()} Now
          </a>
        </div>
      )}

      {/* ─── WITHDRAW VIEW ─── */}
      {activeView === 'withdraw' && (
        <div style={{ padding: 20 }}>
          <button onClick={() => setActiveView('home')} style={{ background: 'none', border: 'none', color: '#64748b', display: 'flex', alignItems: 'center', gap: 4, marginBottom: 20, cursor: 'pointer', fontSize: 14 }}><ArrowLeft size={18} /> Back</button>
          <h2 style={{ color: 'white', fontSize: 22, fontWeight: 800, marginBottom: 8 }}>Withdraw Funds</h2>
          <p style={{ color: '#64748b', fontSize: 13, marginBottom: 20 }}>Withdrawals are processed through LUCRUM Capital</p>
          <div style={{ padding: 20, background: 'rgba(245,158,11,0.05)', border: '1px solid rgba(245,158,11,0.2)', borderRadius: 14, marginBottom: 16 }}>
            <p style={{ color: '#f59e0b', fontSize: 14, fontWeight: 600, margin: '0 0 8px' }}>How to Withdraw</p>
            <ol style={{ color: '#94a3b8', fontSize: 13, lineHeight: 1.8, margin: 0, paddingLeft: 16 }}>
              <li>Log in to your LUCRUM account at <a href={LUCRUM_DEPOSIT} target="_blank" rel="noopener noreferrer" style={{ color: '#0ea5e9' }}>my.lucrumfx.com</a></li>
              <li>Go to "Billetera" (Wallet) section</li>
              <li>Select "Withdrawal" and enter the amount</li>
              <li>Processing time: 1-3 business days</li>
            </ol>
          </div>
          <a href={LUCRUM_DEPOSIT} target="_blank" rel="noopener noreferrer"
            style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8, width: '100%', padding: '14px', background: 'linear-gradient(135deg, #f59e0b, #d97706)', color: 'white', borderRadius: 12, fontSize: 15, fontWeight: 700, textDecoration: 'none', boxSizing: 'border-box' }}>
            Go to LUCRUM <ArrowUpRight size={18} />
          </a>
        </div>
      )}

      {/* ─── INFO VIEW ─── */}
      {activeView === 'info' && (
        <div style={{ padding: 20 }}>
          <button onClick={() => setActiveView('home')} style={{ background: 'none', border: 'none', color: '#64748b', display: 'flex', alignItems: 'center', gap: 4, marginBottom: 20, cursor: 'pointer', fontSize: 14 }}><ArrowLeft size={18} /> Back</button>
          <h2 style={{ color: 'white', fontSize: 22, fontWeight: 800, marginBottom: 4 }}>FIDUS CORE</h2>
          <p style={{ color: '#0ea5e9', fontSize: 14, fontWeight: 600, marginBottom: 20 }}>Retail Investment Product</p>
          {[
            { q: 'What is the return?', a: '1.5% monthly on your capital (18% annual target). Returns paid end of each month.' },
            { q: 'Minimum investment?', a: '$100 USD. No maximum.' },
            { q: 'Can I withdraw anytime?', a: 'Yes. No contracts, no lock-in period. Withdraw through your LUCRUM account at any time.' },
            { q: 'Where is my money?', a: 'In YOUR broker account at LUCRUM Capital. FIDUS has trading access only — never withdrawal access.' },
            { q: 'How does FIDUS make money?', a: 'FIDUS earns from the spread between gross returns (2.5%) and your return (1.5%). We only profit when you profit.' },
            { q: 'What are the risks?', a: 'Trading involves risk of loss. FIDUS uses institutional risk controls (Hull Risk Framework) to limit drawdown to 10% maximum. Past performance does not guarantee future results.' },
          ].map((item, i) => (
            <div key={i} style={{ padding: 14, background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 12, marginBottom: 8 }}>
              <p style={{ color: 'white', fontSize: 14, fontWeight: 600, margin: '0 0 4px' }}>{item.q}</p>
              <p style={{ color: '#94a3b8', fontSize: 13, margin: 0, lineHeight: 1.5 }}>{item.a}</p>
            </div>
          ))}
        </div>
      )}

      {/* ─── BOTTOM NAV ─── */}
      <div style={{ position: 'fixed', bottom: 0, left: '50%', transform: 'translateX(-50%)', width: '100%', maxWidth: 480, background: 'rgba(5,10,21,0.95)', backdropFilter: 'blur(12px)', borderTop: '1px solid rgba(255,255,255,0.06)', padding: '10px 0', display: 'flex', justifyContent: 'space-around', zIndex: 50 }}>
        {[
          { view: 'home', icon: Home, label: 'Home' },
          { view: 'simulator', icon: Calculator, label: 'Invest' },
          { view: 'info', icon: Info, label: 'Info' },
          { view: 'withdraw', icon: Settings, label: 'Settings' },
        ].map(n => (
          <button key={n.view} onClick={() => setActiveView(n.view)}
            style={{ background: 'none', border: 'none', cursor: 'pointer', textAlign: 'center', padding: '4px 0' }}>
            <n.icon size={22} color={activeView === n.view ? '#0ea5e9' : '#475569'} />
            <div style={{ fontSize: 10, color: activeView === n.view ? '#0ea5e9' : '#475569', fontWeight: 600, marginTop: 2 }}>{n.label}</div>
          </button>
        ))}
      </div>
    </div>
  );
};

// ─── MAIN ───
const RetailClientPortal = () => {
  const [authData, setAuthData] = useState(null);
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('retail_token');
    const client = localStorage.getItem('retail_client');
    if (token && client) setAuthData({ token, client: JSON.parse(client) });
    setChecking(false);
  }, []);

  if (checking) return null;
  if (!authData) return <RetailLogin onLogin={setAuthData} />;
  return <RetailApp authData={authData} onLogout={() => setAuthData(null)} />;
};

export default RetailClientPortal;
