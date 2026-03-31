import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Shield, TrendingUp, DollarSign, Clock, ChevronRight, CheckCircle, ArrowRight, Users, Calendar, Star, Lock, Globe, Play, X, ExternalLink } from 'lucide-react';

const LUCRUM_SIGNUP = 'https://my.lucrumfx.com/auth/signup?ib=fiso3999&ref=STD%20IB';
const LUCRUM_PORTAL = 'https://my.lucrumfx.com';

// ─── TRANSLATIONS ───
const T = {
  es: {
    badge: 'Sin contrato. Retira cuando quieras.',
    hero1: 'Gana', hero2: '1.5% Mensual', hero3: 'Sobre Tu Capital',
    heroDesc: 'FIDUS CORE administra tu capital con controles de riesgo institucional. Minimo $100 USD. Rendimientos mensuales depositados en tu cuenta. Sin contratos.',
    startBtn: 'Comenzar a Invertir', loginBtn: 'Acceso Clientes',
    stat1: 'Rendimiento Mensual', stat2: 'Minimo', stat3: 'Periodo de Bloqueo', stat4: 'Meta Anual',
    howTitle: 'Como Funciona',
    step1t: 'Abre Cuenta en LUCRUM', step1d: 'Crea tu cuenta de broker gratuita a traves de nuestro enlace seguro. Completa la verificacion KYC.',
    step2t: 'Fondea Tu Cuenta', step2d: 'Deposita minimo $100 USD por transferencia, crypto o tarjeta. Tu capital permanece en TU cuenta de broker.',
    step3t: 'FIDUS Administra', step3d: 'Nuestra estrategia CORE opera tu cuenta con controles de riesgo institucional. Framework de Riesgo Hull.',
    step4t: 'Recibe Rendimientos', step4d: '1.5% de rendimiento mensual depositado directamente en tu cuenta de broker. Retira cuando quieras.',
    openAccount: 'Abrir Cuenta',
    simTitle: 'Simulador de Inversion', simDesc: 'Mira como crece tu dinero al 1.5% mensual',
    simInvest: 'Monto de Inversion (USD)', simMonthly: 'Rendimiento Mensual', simAnnual: 'Anual (Simple)', simCompound: 'Compuesto',
    trust1t: 'Tu Dinero, Tu Cuenta', trust1d: 'Tu capital permanece en TU cuenta de broker LUCRUM. FIDUS solo tiene acceso de operacion — nunca de retiro.',
    trust2t: 'Framework de Riesgo Hull', trust2d: 'Controles de riesgo institucional: maximo 1% por operacion, limite diario 5%, cierre al final del dia.',
    trust3t: 'Broker Regulado', trust3d: 'LUCRUM Capital es un broker regulado. Cuentas segregadas. Proteccion de saldo negativo.',
    trust4t: 'Pagos Mensuales', trust4d: '1.5% de rendimiento mensual. Sin contratos, sin periodo de bloqueo. Retira tu capital cuando quieras.',
    ctaTitle: 'Listo para Comenzar?', ctaDesc: 'Abre tu cuenta LUCRUM en minutos. Comienza con tan solo $100 USD.',
    ctaBtn: 'Abrir Cuenta en LUCRUM',
    footer: 'FIDUS Solutions LLC. El rendimiento pasado no garantiza resultados futuros. Operar implica riesgo de perdida. Los rendimientos son metas, no garantias. Tu capital esta en riesgo. FIDUS opera como administrador de dinero a traves de LUCRUM Capital.',
    clientPortal: 'Portal Clientes', admin: 'Administracion', franchise: 'Socios Franquicia', institutional: 'FIDUS Institucional',
    signIn: 'Iniciar Sesion',
  },
  en: {
    badge: 'No Lock-in. Withdraw Anytime.',
    hero1: 'Earn', hero2: '1.5% Monthly', hero3: 'On Your Capital',
    heroDesc: 'FIDUS CORE manages your capital with institutional-grade risk controls. Minimum $100 USD. Monthly returns paid to your account. No contracts.',
    startBtn: 'Start Investing', loginBtn: 'Client Login',
    stat1: 'Monthly Return', stat2: 'Minimum', stat3: 'Lock-in Period', stat4: 'Annual Target',
    howTitle: 'How It Works',
    step1t: 'Open Account at LUCRUM', step1d: 'Create your free broker account through our secure link. Complete KYC verification.',
    step2t: 'Fund Your Account', step2d: 'Deposit minimum $100 USD via wire transfer, crypto, or card. Your capital stays in YOUR broker account.',
    step3t: 'FIDUS Manages', step3d: 'Our CORE strategy trades your account using institutional risk controls. Hull Risk Framework.',
    step4t: 'Earn Monthly Returns', step4d: '1.5% monthly returns paid directly to your broker account. Withdraw anytime — no lock-in.',
    openAccount: 'Open Account',
    simTitle: 'Investment Simulator', simDesc: 'See how your money grows at 1.5% monthly',
    simInvest: 'Investment Amount (USD)', simMonthly: 'Monthly Return', simAnnual: 'Annual (Simple)', simCompound: 'Compounded',
    trust1t: 'Your Money, Your Account', trust1d: 'Capital stays in YOUR LUCRUM broker account. FIDUS only has trading access — never withdrawal access.',
    trust2t: 'Hull Risk Framework', trust2d: 'Institutional risk controls: max 1% per trade, 5% daily limit, force flat at market close.',
    trust3t: 'Regulated Broker', trust3d: 'LUCRUM Capital is a regulated broker. Segregated client accounts. Negative balance protection.',
    trust4t: 'Monthly Payments', trust4d: '1.5% returns paid monthly. No contracts, no lock-in. Withdraw your capital anytime.',
    ctaTitle: 'Ready to Start?', ctaDesc: 'Open your LUCRUM account in minutes. Start with as little as $100 USD.',
    ctaBtn: 'Open Account at LUCRUM',
    footer: 'FIDUS Solutions LLC. Past performance does not guarantee future results. Trading involves risk of loss. Returns are targets, not guarantees. Your capital is at risk.',
    clientPortal: 'Client Portal', admin: 'Admin', franchise: 'Franchise Partners', institutional: 'FIDUS Institutional',
    signIn: 'Sign In',
  }
};

const RetailLanding = () => {
  const [lang, setLang] = useState('es');
  const [showLucrumFrame, setShowLucrumFrame] = useState(false);
  const t = T[lang];

  return (
    <div style={{ background: '#050a15', color: '#e2e8f0', minHeight: '100vh', fontFamily: "'Inter', -apple-system, sans-serif" }}>
      {/* Nav */}
      <nav style={{ position: 'sticky', top: 0, zIndex: 50, background: 'rgba(5,10,21,0.95)', backdropFilter: 'blur(12px)', borderBottom: '1px solid rgba(100,116,139,0.1)' }}>
        <div style={{ maxWidth: 1200, margin: '0 auto', padding: '12px 24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <img src="/fidus-logo.png" alt="FIDUS" style={{ height: 40, width: 'auto' }} />
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            {/* Language Toggle */}
            <div style={{ display: 'flex', background: 'rgba(255,255,255,0.06)', borderRadius: 6, overflow: 'hidden', border: '1px solid rgba(255,255,255,0.08)' }}>
              <button onClick={() => setLang('es')} style={{ padding: '5px 10px', background: lang === 'es' ? '#0ea5e9' : 'transparent', color: lang === 'es' ? 'white' : '#64748b', border: 'none', fontSize: 12, fontWeight: 600, cursor: 'pointer' }}>ES</button>
              <button onClick={() => setLang('en')} style={{ padding: '5px 10px', background: lang === 'en' ? '#0ea5e9' : 'transparent', color: lang === 'en' ? 'white' : '#64748b', border: 'none', fontSize: 12, fontWeight: 600, cursor: 'pointer' }}>EN</button>
            </div>
            <a href="/retail/login" style={{ padding: '8px 20px', color: '#94a3b8', fontSize: 14, textDecoration: 'none', fontWeight: 500 }}>{t.signIn}</a>
            <button onClick={() => setShowLucrumFrame(true)} style={{ padding: '8px 24px', background: 'linear-gradient(135deg, #0ea5e9, #06b6d4)', color: 'white', borderRadius: 8, fontSize: 14, fontWeight: 600, border: 'none', cursor: 'pointer' }}>{t.openAccount}</button>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section style={{ maxWidth: 1200, margin: '0 auto', padding: '80px 24px 60px', textAlign: 'center' }}>
        <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.7 }}>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8, padding: '6px 16px', background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.2)', borderRadius: 20, marginBottom: 24 }}>
            <div style={{ width: 6, height: 6, borderRadius: '50%', background: '#10b981' }} />
            <span style={{ color: '#10b981', fontSize: 13, fontWeight: 600 }}>{t.badge}</span>
          </div>
          <h1 style={{ fontSize: 'clamp(36px, 6vw, 64px)', fontWeight: 800, lineHeight: 1.05, color: 'white', margin: '0 0 20px', letterSpacing: '-0.03em' }}>
            {t.hero1} <span style={{ color: '#0ea5e9' }}>{t.hero2}</span><br />{t.hero3}
          </h1>
          <p style={{ fontSize: 'clamp(16px, 2vw, 20px)', color: '#94a3b8', maxWidth: 600, margin: '0 auto 32px', lineHeight: 1.6 }}>{t.heroDesc}</p>
          <div style={{ display: 'flex', gap: 12, justifyContent: 'center', flexWrap: 'wrap' }}>
            <button onClick={() => setShowLucrumFrame(true)} style={{ padding: '14px 32px', background: 'linear-gradient(135deg, #0ea5e9, #0284c7)', color: 'white', borderRadius: 12, fontSize: 16, fontWeight: 700, border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 8 }}>
              {t.startBtn} <ArrowRight size={18} />
            </button>
            <a href="/retail/login" style={{ padding: '14px 32px', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', color: 'white', borderRadius: 12, fontSize: 16, fontWeight: 600, textDecoration: 'none' }}>{t.loginBtn}</a>
          </div>
        </motion.div>

        {/* Stats */}
        <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: 16, maxWidth: 700, margin: '60px auto 0' }}>
          {[
            { v: '1.5%', l: t.stat1, c: '#10b981' },
            { v: '$100', l: t.stat2, c: '#0ea5e9' },
            { v: '0', l: t.stat3, c: '#f59e0b' },
            { v: '18%', l: t.stat4, c: '#8b5cf6' },
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
        <h2 style={{ fontSize: 32, fontWeight: 800, color: 'white', textAlign: 'center', marginBottom: 48 }}>{t.howTitle}</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: 24 }}>
          {[
            { step: '1', title: t.step1t, desc: t.step1d, icon: Users, action: t.openAccount, onClick: () => setShowLucrumFrame(true) },
            { step: '2', title: t.step2t, desc: t.step2d, icon: DollarSign },
            { step: '3', title: t.step3t, desc: t.step3d, icon: Shield },
            { step: '4', title: t.step4t, desc: t.step4d, icon: TrendingUp },
          ].map((s, i) => (
            <motion.div key={i} initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }}
              style={{ padding: 28, background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 16, position: 'relative' }}>
              <div style={{ position: 'absolute', top: -12, left: 20, width: 28, height: 28, borderRadius: 8, background: '#0ea5e9', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 14, fontWeight: 800, color: 'white' }}>{s.step}</div>
              <s.icon size={24} style={{ color: '#0ea5e9', marginBottom: 12, marginTop: 8 }} />
              <h3 style={{ color: 'white', fontSize: 18, fontWeight: 700, marginBottom: 8 }}>{s.title}</h3>
              <p style={{ color: '#94a3b8', fontSize: 14, lineHeight: 1.6, marginBottom: s.action ? 12 : 0 }}>{s.desc}</p>
              {s.action && <button onClick={s.onClick || (() => {})} style={{ color: '#0ea5e9', fontSize: 13, fontWeight: 600, background: 'none', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 4, padding: 0 }}>{s.action} <ChevronRight size={14} /></button>}
            </motion.div>
          ))}
        </div>
      </section>

      {/* Simulator */}
      <section style={{ maxWidth: 800, margin: '0 auto', padding: '60px 24px' }}>
        <h2 style={{ fontSize: 28, fontWeight: 800, color: 'white', textAlign: 'center', marginBottom: 8 }}>{t.simTitle}</h2>
        <p style={{ color: '#64748b', textAlign: 'center', marginBottom: 32, fontSize: 14 }}>{t.simDesc}</p>
        <SimulatorWidget t={t} />
      </section>

      {/* Trust */}
      <section style={{ maxWidth: 1200, margin: '0 auto', padding: '60px 24px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16 }}>
          {[
            { icon: Lock, title: t.trust1t, desc: t.trust1d },
            { icon: Shield, title: t.trust2t, desc: t.trust2d },
            { icon: Globe, title: t.trust3t, desc: t.trust3d },
            { icon: Calendar, title: t.trust4t, desc: t.trust4d },
          ].map((tr, i) => (
            <div key={i} style={{ padding: 20, background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 12 }}>
              <tr.icon size={20} style={{ color: '#0ea5e9', marginBottom: 8 }} />
              <h4 style={{ color: 'white', fontSize: 14, fontWeight: 700, marginBottom: 4 }}>{tr.title}</h4>
              <p style={{ color: '#94a3b8', fontSize: 12, lineHeight: 1.5 }}>{tr.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section style={{ maxWidth: 800, margin: '0 auto', padding: '60px 24px', textAlign: 'center' }}>
        <div style={{ padding: 40, background: 'linear-gradient(135deg, rgba(14,165,233,0.1), rgba(6,182,212,0.05))', border: '1px solid rgba(14,165,233,0.2)', borderRadius: 20 }}>
          <h2 style={{ color: 'white', fontSize: 28, fontWeight: 800, marginBottom: 12 }}>{t.ctaTitle}</h2>
          <p style={{ color: '#94a3b8', marginBottom: 24 }}>{t.ctaDesc}</p>
          <button onClick={() => setShowLucrumFrame(true)} style={{ display: 'inline-flex', alignItems: 'center', gap: 8, padding: '14px 36px', background: 'linear-gradient(135deg, #0ea5e9, #0284c7)', color: 'white', borderRadius: 12, fontSize: 16, fontWeight: 700, border: 'none', cursor: 'pointer' }}>
            {t.ctaBtn} <ArrowRight size={18} />
          </button>
        </div>
      </section>

      {/* Footer */}

      {/* LUCRUM Iframe Overlay */}
      {showLucrumFrame && (
        <div style={{ position: 'fixed', inset: 0, zIndex: 9999, background: 'rgba(0,0,0,0.85)', display: 'flex', flexDirection: 'column' }}>
          <div style={{ background: '#050a15', borderBottom: '1px solid rgba(14,165,233,0.2)', padding: '10px 20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <img src="/fidus-logo.png" alt="FIDUS" style={{ height: 32 }} />
              <span style={{ color: '#0ea5e9', fontSize: 13, fontWeight: 600 }}>Apertura de Cuenta LUCRUM Capital</span>
            </div>
            <button onClick={() => setShowLucrumFrame(false)} style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', color: '#ef4444', padding: '6px 16px', borderRadius: 6, cursor: 'pointer', fontSize: 13, fontWeight: 600 }}>
              Cerrar
            </button>
          </div>
          <iframe src={LUCRUM_SIGNUP} style={{ flex: 1, border: 'none', width: '100%' }} title="LUCRUM Account Opening" />
        </div>
      )}


      <footer style={{ borderTop: '1px solid rgba(100,116,139,0.1)', padding: '24px', textAlign: 'center' }}>
        <img src="/fidus-logo.png" alt="FIDUS" style={{ height: 32, margin: '0 auto 12px', display: 'block' }} />
        <p style={{ color: '#475569', fontSize: 11, maxWidth: 700, margin: '0 auto', lineHeight: 1.6 }}>{t.footer}</p>
        <div style={{ marginTop: 12, display: 'flex', gap: 16, justifyContent: 'center', fontSize: 12, color: '#64748b' }}>
          <a href="/retail/login" style={{ color: '#64748b', textDecoration: 'none' }}>{t.clientPortal}</a>
          <a href="/retail/admin" style={{ color: '#64748b', textDecoration: 'none' }}>{t.admin}</a>
          <a href="/franchise/login" style={{ color: '#64748b', textDecoration: 'none' }}>{t.franchise}</a>
          <a href="/" style={{ color: '#64748b', textDecoration: 'none' }}>{t.institutional}</a>
        </div>
      </footer>
    </div>
  );
};

const SimulatorWidget = ({ t }) => {
  const [amount, setAmount] = useState(5000);
  const monthly = amount * 0.015;
  const annual = amount * 0.015 * 12;
  const compounded = amount * Math.pow(1.015, 12) - amount;

  return (
    <div style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 16, padding: 28 }}>
      <div style={{ marginBottom: 20 }}>
        <label style={{ color: '#94a3b8', fontSize: 13, display: 'block', marginBottom: 8 }}>{t.simInvest}</label>
        <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
          {[100, 1000, 5000, 10000, 50000].map(v => (
            <button key={v} onClick={() => setAmount(v)}
              style={{ flex: 1, padding: '8px', background: amount === v ? '#0ea5e9' : 'rgba(255,255,255,0.05)', border: amount === v ? 'none' : '1px solid rgba(255,255,255,0.1)', borderRadius: 8, color: 'white', fontSize: 12, fontWeight: 600, cursor: 'pointer' }}>
              ${v.toLocaleString()}
            </button>
          ))}
        </div>
        <input type="range" min={100} max={100000} step={100} value={amount} onChange={e => setAmount(Number(e.target.value))} style={{ width: '100%', accentColor: '#0ea5e9' }} />
        <div style={{ textAlign: 'center', marginTop: 8 }}>
          <span style={{ color: 'white', fontSize: 32, fontWeight: 800, fontFamily: 'monospace' }}>${amount.toLocaleString()}</span>
        </div>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12 }}>
        <div style={{ padding: 16, background: 'rgba(16,185,129,0.08)', border: '1px solid rgba(16,185,129,0.15)', borderRadius: 12, textAlign: 'center' }}>
          <div style={{ color: '#10b981', fontSize: 24, fontWeight: 800, fontFamily: 'monospace' }}>${monthly.toFixed(0)}</div>
          <div style={{ color: '#64748b', fontSize: 11, marginTop: 2 }}>{t.simMonthly}</div>
        </div>
        <div style={{ padding: 16, background: 'rgba(14,165,233,0.08)', border: '1px solid rgba(14,165,233,0.15)', borderRadius: 12, textAlign: 'center' }}>
          <div style={{ color: '#0ea5e9', fontSize: 24, fontWeight: 800, fontFamily: 'monospace' }}>${annual.toFixed(0)}</div>
          <div style={{ color: '#64748b', fontSize: 11, marginTop: 2 }}>{t.simAnnual}</div>
        </div>
        <div style={{ padding: 16, background: 'rgba(139,92,246,0.08)', border: '1px solid rgba(139,92,246,0.15)', borderRadius: 12, textAlign: 'center' }}>
          <div style={{ color: '#8b5cf6', fontSize: 24, fontWeight: 800, fontFamily: 'monospace' }}>${compounded.toFixed(0)}</div>
          <div style={{ color: '#64748b', fontSize: 11, marginTop: 2 }}>{t.simCompound}</div>
        </div>
      </div>
    </div>
  );
};

export default RetailLanding;
