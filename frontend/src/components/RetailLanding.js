import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Shield, TrendingUp, DollarSign, Clock, ChevronRight, CheckCircle, ArrowRight, Users, Calendar, Star, Lock, Globe, Play } from 'lucide-react';

const LUCRUM_SIGNUP = 'https://my.lucrumfx.com/auth/signup?ib=fiso3999&ref=STD%20IB';

const RetailLanding = () => {
  const [showVideo, setShowVideo] = useState(false);

  return (
    <div style={{ background: '#050a15', color: '#e2e8f0', minHeight: '100vh', fontFamily: "'Inter', -apple-system, sans-serif" }}>
      {/* Nav */}
      <nav style={{ position: 'sticky', top: 0, zIndex: 50, background: 'rgba(5,10,21,0.95)', backdropFilter: 'blur(12px)', borderBottom: '1px solid rgba(100,116,139,0.1)' }}>
        <div style={{ maxWidth: 1200, margin: '0 auto', padding: '16px 24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{ width: 36, height: 36, borderRadius: 10, background: 'linear-gradient(135deg, #0ea5e9, #06b6d4)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Shield size={20} color="white" />
            </div>
            <span style={{ fontSize: 20, fontWeight: 800, color: 'white', letterSpacing: '-0.02em' }}>FIDUS</span>
            <span style={{ fontSize: 11, color: '#0ea5e9', fontWeight: 600, padding: '2px 8px', background: 'rgba(14,165,233,0.1)', borderRadius: 6 }}>RETAIL</span>
          </div>
          <div style={{ display: 'flex', gap: 12 }}>
            <a href="/retail/login" style={{ padding: '8px 20px', color: '#94a3b8', fontSize: 14, textDecoration: 'none', fontWeight: 500 }}>Sign In</a>
            <a href={LUCRUM_SIGNUP} target="_blank" rel="noopener noreferrer" style={{ padding: '8px 24px', background: 'linear-gradient(135deg, #0ea5e9, #06b6d4)', color: 'white', borderRadius: 8, fontSize: 14, fontWeight: 600, textDecoration: 'none' }}>Open Account</a>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section style={{ maxWidth: 1200, margin: '0 auto', padding: '80px 24px 60px', textAlign: 'center' }}>
        <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.7 }}>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8, padding: '6px 16px', background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.2)', borderRadius: 20, marginBottom: 24 }}>
            <div style={{ width: 6, height: 6, borderRadius: '50%', background: '#10b981', animation: 'pulse 2s infinite' }} />
            <span style={{ color: '#10b981', fontSize: 13, fontWeight: 600 }}>No Lock-in. Withdraw Anytime.</span>
          </div>
          <h1 style={{ fontSize: 'clamp(36px, 6vw, 64px)', fontWeight: 800, lineHeight: 1.05, color: 'white', margin: '0 0 20px', letterSpacing: '-0.03em' }}>
            Earn <span style={{ color: '#0ea5e9' }}>1.5% Monthly</span><br />
            On Your Capital
          </h1>
          <p style={{ fontSize: 'clamp(16px, 2vw, 20px)', color: '#94a3b8', maxWidth: 600, margin: '0 auto 32px', lineHeight: 1.6 }}>
            FIDUS CORE manages your capital with institutional-grade risk controls.
            Minimum $100 USD. Monthly returns paid to your account. No contracts.
          </p>
          <div style={{ display: 'flex', gap: 12, justifyContent: 'center', flexWrap: 'wrap' }}>
            <a href={LUCRUM_SIGNUP} target="_blank" rel="noopener noreferrer" style={{ padding: '14px 32px', background: 'linear-gradient(135deg, #0ea5e9, #0284c7)', color: 'white', borderRadius: 12, fontSize: 16, fontWeight: 700, textDecoration: 'none', display: 'flex', alignItems: 'center', gap: 8 }}>
              Start Investing <ArrowRight size={18} />
            </a>
            <a href="/retail/login" style={{ padding: '14px 32px', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', color: 'white', borderRadius: 12, fontSize: 16, fontWeight: 600, textDecoration: 'none' }}>
              Client Login
            </a>
          </div>
        </motion.div>

        {/* Stats */}
        <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: 16, maxWidth: 700, margin: '60px auto 0' }}>
          {[
            { v: '1.5%', l: 'Monthly Return', c: '#10b981' },
            { v: '$100', l: 'Minimum', c: '#0ea5e9' },
            { v: '0', l: 'Lock-in Period', c: '#f59e0b' },
            { v: '18%', l: 'Annual Target', c: '#8b5cf6' },
          ].map((s, i) => (
            <div key={i} style={{ padding: 20, background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 12, textAlign: 'center' }}>
              <div style={{ fontSize: 28, fontWeight: 800, color: s.c, fontFamily: 'monospace' }}>{s.v}</div>
              <div style={{ fontSize: 12, color: '#64748b', marginTop: 4 }}>{s.l}</div>
            </div>
          ))}
        </motion.div>
      </section>

      {/* How It Works */}
      <section style={{ maxWidth: 1200, margin: '0 auto', padding: '60px 24px' }}>
        <h2 style={{ fontSize: 32, fontWeight: 800, color: 'white', textAlign: 'center', marginBottom: 48 }}>How It Works</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: 24 }}>
          {[
            { step: '1', title: 'Open Account at LUCRUM', desc: 'Create your free broker account through our secure link. Complete KYC verification.', icon: Users, action: 'Open Account', link: LUCRUM_SIGNUP },
            { step: '2', title: 'Fund Your Account', desc: 'Deposit minimum $100 USD via wire transfer, crypto, or card. Your capital stays in YOUR broker account.', icon: DollarSign },
            { step: '3', title: 'FIDUS Manages', desc: 'Our CORE strategy trades your account using institutional risk controls. Hull Risk Framework.', icon: Shield },
            { step: '4', title: 'Earn Monthly Returns', desc: '1.5% monthly returns paid directly to your broker account. Withdraw anytime — no lock-in.', icon: TrendingUp },
          ].map((s, i) => (
            <motion.div key={i} initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }}
              style={{ padding: 28, background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 16, position: 'relative' }}>
              <div style={{ position: 'absolute', top: -12, left: 20, width: 28, height: 28, borderRadius: 8, background: '#0ea5e9', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 14, fontWeight: 800, color: 'white' }}>{s.step}</div>
              <s.icon size={24} style={{ color: '#0ea5e9', marginBottom: 12, marginTop: 8 }} />
              <h3 style={{ color: 'white', fontSize: 18, fontWeight: 700, marginBottom: 8 }}>{s.title}</h3>
              <p style={{ color: '#94a3b8', fontSize: 14, lineHeight: 1.6, marginBottom: s.action ? 12 : 0 }}>{s.desc}</p>
              {s.action && <a href={s.link} target="_blank" rel="noopener noreferrer" style={{ color: '#0ea5e9', fontSize: 13, fontWeight: 600, textDecoration: 'none', display: 'flex', alignItems: 'center', gap: 4 }}>{s.action} <ChevronRight size={14} /></a>}
            </motion.div>
          ))}
        </div>
      </section>

      {/* Simulator */}
      <section style={{ maxWidth: 800, margin: '0 auto', padding: '60px 24px' }}>
        <h2 style={{ fontSize: 28, fontWeight: 800, color: 'white', textAlign: 'center', marginBottom: 8 }}>Investment Simulator</h2>
        <p style={{ color: '#64748b', textAlign: 'center', marginBottom: 32, fontSize: 14 }}>See how your money grows at 1.5% monthly</p>
        <SimulatorWidget />
      </section>

      {/* Trust */}
      <section style={{ maxWidth: 1200, margin: '0 auto', padding: '60px 24px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16 }}>
          {[
            { icon: Lock, title: 'Your Money, Your Account', desc: 'Capital stays in YOUR LUCRUM broker account. FIDUS only has trading access — never withdrawal access.' },
            { icon: Shield, title: 'Hull Risk Framework', desc: 'Institutional risk controls: max 1% per trade, 5% daily limit, force flat at market close.' },
            { icon: Globe, title: 'Regulated Broker', desc: 'LUCRUM Capital is a regulated broker. Segregated client accounts. Negative balance protection.' },
            { icon: Calendar, title: 'Monthly Payments', desc: '1.5% returns paid monthly. No contracts, no lock-in. Withdraw your capital anytime.' },
          ].map((t, i) => (
            <div key={i} style={{ padding: 20, background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 12 }}>
              <t.icon size={20} style={{ color: '#0ea5e9', marginBottom: 8 }} />
              <h4 style={{ color: 'white', fontSize: 14, fontWeight: 700, marginBottom: 4 }}>{t.title}</h4>
              <p style={{ color: '#94a3b8', fontSize: 12, lineHeight: 1.5 }}>{t.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section style={{ maxWidth: 800, margin: '0 auto', padding: '60px 24px', textAlign: 'center' }}>
        <div style={{ padding: 40, background: 'linear-gradient(135deg, rgba(14,165,233,0.1), rgba(6,182,212,0.05))', border: '1px solid rgba(14,165,233,0.2)', borderRadius: 20 }}>
          <h2 style={{ color: 'white', fontSize: 28, fontWeight: 800, marginBottom: 12 }}>Ready to Start?</h2>
          <p style={{ color: '#94a3b8', marginBottom: 24 }}>Open your LUCRUM account in minutes. Start with as little as $100 USD.</p>
          <a href={LUCRUM_SIGNUP} target="_blank" rel="noopener noreferrer" style={{ display: 'inline-flex', alignItems: 'center', gap: 8, padding: '14px 36px', background: 'linear-gradient(135deg, #0ea5e9, #0284c7)', color: 'white', borderRadius: 12, fontSize: 16, fontWeight: 700, textDecoration: 'none' }}>
            Open Account at LUCRUM <ArrowRight size={18} />
          </a>
        </div>
      </section>

      {/* Footer */}
      <footer style={{ borderTop: '1px solid rgba(100,116,139,0.1)', padding: '24px', textAlign: 'center' }}>
        <p style={{ color: '#475569', fontSize: 11, maxWidth: 700, margin: '0 auto', lineHeight: 1.6 }}>
          FIDUS Solutions LLC. Past performance does not guarantee future results. Trading involves risk of loss.
          Returns are targets, not guarantees. Your capital is at risk. FIDUS operates as a money manager through LUCRUM Capital.
          All client funds are held in segregated accounts at LUCRUM Capital.
        </p>
        <div style={{ marginTop: 12, display: 'flex', gap: 16, justifyContent: 'center', fontSize: 12, color: '#64748b' }}>
          <a href="/retail/login" style={{ color: '#64748b', textDecoration: 'none' }}>Client Portal</a>
          <a href="/retail/admin" style={{ color: '#64748b', textDecoration: 'none' }}>Admin</a>
          <a href="/franchise/login" style={{ color: '#64748b', textDecoration: 'none' }}>Franchise Partners</a>
          <a href="/" style={{ color: '#64748b', textDecoration: 'none' }}>FIDUS Institutional</a>
        </div>
      </footer>
    </div>
  );
};

// Simulator Widget
const SimulatorWidget = () => {
  const [amount, setAmount] = useState(5000);
  const monthly = amount * 0.015;
  const annual = amount * 0.015 * 12;
  const compounded = amount * Math.pow(1.015, 12) - amount;

  return (
    <div style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 16, padding: 28 }}>
      <div style={{ marginBottom: 20 }}>
        <label style={{ color: '#94a3b8', fontSize: 13, display: 'block', marginBottom: 8 }}>Investment Amount (USD)</label>
        <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
          {[100, 1000, 5000, 10000, 50000].map(v => (
            <button key={v} onClick={() => setAmount(v)}
              style={{ flex: 1, padding: '8px', background: amount === v ? '#0ea5e9' : 'rgba(255,255,255,0.05)', border: amount === v ? 'none' : '1px solid rgba(255,255,255,0.1)', borderRadius: 8, color: 'white', fontSize: 12, fontWeight: 600, cursor: 'pointer' }}>
              ${v.toLocaleString()}
            </button>
          ))}
        </div>
        <input type="range" min={100} max={100000} step={100} value={amount} onChange={e => setAmount(Number(e.target.value))}
          style={{ width: '100%', accentColor: '#0ea5e9' }} />
        <div style={{ textAlign: 'center', marginTop: 8 }}>
          <span style={{ color: 'white', fontSize: 32, fontWeight: 800, fontFamily: 'monospace' }}>${amount.toLocaleString()}</span>
        </div>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12 }}>
        <div style={{ padding: 16, background: 'rgba(16,185,129,0.08)', border: '1px solid rgba(16,185,129,0.15)', borderRadius: 12, textAlign: 'center' }}>
          <div style={{ color: '#10b981', fontSize: 24, fontWeight: 800, fontFamily: 'monospace' }}>${monthly.toFixed(0)}</div>
          <div style={{ color: '#64748b', fontSize: 11, marginTop: 2 }}>Monthly Return</div>
        </div>
        <div style={{ padding: 16, background: 'rgba(14,165,233,0.08)', border: '1px solid rgba(14,165,233,0.15)', borderRadius: 12, textAlign: 'center' }}>
          <div style={{ color: '#0ea5e9', fontSize: 24, fontWeight: 800, fontFamily: 'monospace' }}>${annual.toFixed(0)}</div>
          <div style={{ color: '#64748b', fontSize: 11, marginTop: 2 }}>Annual (Simple)</div>
        </div>
        <div style={{ padding: 16, background: 'rgba(139,92,246,0.08)', border: '1px solid rgba(139,92,246,0.15)', borderRadius: 12, textAlign: 'center' }}>
          <div style={{ color: '#8b5cf6', fontSize: 24, fontWeight: 800, fontFamily: 'monospace' }}>${compounded.toFixed(0)}</div>
          <div style={{ color: '#64748b', fontSize: 11, marginTop: 2 }}>Compounded</div>
        </div>
      </div>
    </div>
  );
};

export default RetailLanding;
