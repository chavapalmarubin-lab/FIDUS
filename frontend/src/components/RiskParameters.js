import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/input';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import {
  Shield, Save, RefreshCw, AlertTriangle, CheckCircle, Settings,
  Percent, TrendingDown, Clock, DollarSign, Zap, Info, Edit2, X,
  Calendar, BookOpen, Calculator, Activity, Target, Bell
} from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;
const fmt = (v) => `$${(v||0).toLocaleString(undefined,{minimumFractionDigits:0,maximumFractionDigits:0})}`;

const RiskParameters = () => {
  const [activeTab, setActiveTab] = useState('framework');
  const [policy, setPolicy] = useState(null);
  const [calendar, setCalendar] = useState(null);
  const [sizing, setSizing] = useState(null);
  const [stress, setStress] = useState(null);
  const [compliance, setCompliance] = useState(null);
  const [sizingEquity, setSizingEquity] = useState(100000);
  const [sizingRisk, setSizingRisk] = useState(0.5);
  const [editing, setEditing] = useState(false);
  const [editPolicy, setEditPolicy] = useState({});

  const token = localStorage.getItem('fidus_token');
  const h = { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' };

  useEffect(() => {
    fetch(`${API}/api/admin/risk-engine/policy`, { headers: h }).then(r=>r.json()).then(d => { if(d.success) setPolicy(d.policy); });
    fetch(`${API}/api/admin/risk-framework/prohibited-calendar`, { headers: h }).then(r=>r.json()).then(d => { if(d.success) setCalendar(d); });
    fetch(`${API}/api/admin/risk-framework/position-calculator?equity=${sizingEquity}&risk_pct=${sizingRisk}`, { headers: h }).then(r=>r.json()).then(d => { if(d.success) setSizing(d); });
    fetch(`${API}/api/admin/risk-framework/stress-test?equity=407316`, { headers: h }).then(r=>r.json()).then(d => { if(d.success) setStress(d); });
    fetch(`${API}/api/admin/risk/status`, { headers: h }).then(r=>r.json()).then(d => { if(d.success) setCompliance(d); });
  }, []);

  const recalcSizing = () => {
    fetch(`${API}/api/admin/risk-framework/position-calculator?equity=${sizingEquity}&risk_pct=${sizingRisk}`, { headers: h }).then(r=>r.json()).then(d => { if(d.success) setSizing(d); });
  };

  const savePolicy = async () => {
    const res = await fetch(`${API}/api/admin/risk-engine/policy`, { method: 'PUT', headers: h, body: JSON.stringify(editPolicy) });
    const d = await res.json();
    if (d.success) { setPolicy({...policy, ...editPolicy}); setEditing(false); }
  };

  const tabs = [
    { id: 'framework', label: 'Hull Framework', icon: BookOpen },
    { id: 'policy', label: 'FIDUS Policy', icon: Shield },
    { id: 'calendar', label: 'Prohibited Calendar', icon: Calendar },
    { id: 'sizing', label: 'Position Sizing', icon: Calculator },
    { id: 'stress', label: 'Stress Testing', icon: Activity },
    { id: 'compliance', label: 'Compliance', icon: Target },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2"><Shield className="w-6 h-6 text-cyan-400" /> FIDUS Risk Management Framework</h2>
          <p className="text-slate-400 text-sm mt-1">Institutional risk controls based on John C. Hull methodology</p>
        </div>
        {calendar?.today_is_prohibited && (
          <div className="px-4 py-2 bg-red-900/30 border border-red-500/40 rounded-lg flex items-center gap-2 animate-pulse">
            <AlertTriangle className="w-5 h-5 text-red-400" />
            <span className="text-red-400 font-bold text-sm">PROHIBITED TRADING TODAY</span>
          </div>
        )}
        {calendar?.next_event && !calendar.today_is_prohibited && (
          <div className="px-4 py-2 bg-amber-900/20 border border-amber-500/30 rounded-lg flex items-center gap-2">
            <Bell className="w-4 h-4 text-amber-400" />
            <span className="text-amber-400 text-xs">Next: <strong>{calendar.next_event.name}</strong> in {calendar.next_event.days_away}d</span>
          </div>
        )}
      </div>

      {/* Sub-tabs */}
      <div className="flex gap-1 p-1 bg-slate-800/50 rounded-lg border border-slate-700/30 overflow-x-auto">
        {tabs.map(t => (
          <button key={t.id} onClick={() => setActiveTab(t.id)}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-md text-xs font-medium transition-all whitespace-nowrap ${activeTab === t.id ? 'bg-cyan-600 text-white' : 'text-slate-400 hover:text-white hover:bg-slate-700/50'}`}>
            <t.icon size={14} /> {t.label}
          </button>
        ))}
      </div>

      {/* ═══ TAB 1: HULL FRAMEWORK ═══ */}
      {activeTab === 'framework' && (
        <div className="space-y-6">
          {/* Core Principle */}
          <Card className="border-cyan-500/20 bg-gradient-to-br from-slate-800/50 to-cyan-900/10">
            <CardContent className="p-6">
              <h3 className="text-lg font-bold text-cyan-400 mb-3">The Hull Principle: Drawdown is the Paramount Risk Metric</h3>
              <p className="text-slate-300 text-sm leading-relaxed">
                In John C. Hull's framework for institutional risk management, <strong className="text-white">maximum drawdown</strong> — not Sharpe ratio, not volatility — is the primary measure of risk.
                A fund that never breaches its drawdown limit preserves capital and maintains investor confidence. FIDUS enforces this through a layered defense system.
              </p>
            </CardContent>
          </Card>

          {/* Three Pillars */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[
              { title: 'Position Sizing', sub: 'Hull Risk Budget', desc: 'Size = (Equity × Risk%) ÷ (ATR × Stop Mult). Never risk more than 1% per trade. This formula ensures position sizes automatically scale down during drawdowns.', color: '#0ea5e9', formula: 'L = (E × r) / (ATR × σ × C)' },
              { title: 'Value at Risk (VaR)', sub: '95% Confidence', desc: 'Historical VaR: sort daily P&L, take the 5th percentile. This is the maximum expected daily loss 95% of the time. CVaR (Expected Shortfall) averages the worst 5% of days — the true tail risk.', color: '#f59e0b', formula: 'VaR₉₅ = P(5th percentile)' },
              { title: 'Drawdown Control', sub: 'Cascade Defense', desc: '3% daily warning → 5% daily halt → 6% weekly review → 10% monthly critical. Each level triggers progressively stronger intervention. The March 18 incident proved: display-only limits fail. FIDUS now enforces at Layer 2.', color: '#ef4444', formula: 'DD = (Peak - Current) / Peak' },
            ].map((p, i) => (
              <Card key={i} className="border-slate-700/30 bg-slate-800/30">
                <CardContent className="p-5">
                  <div className="text-xs font-medium mb-1" style={{color: p.color}}>{p.sub}</div>
                  <h4 className="text-white font-bold text-base mb-2">{p.title}</h4>
                  <p className="text-slate-400 text-xs leading-relaxed mb-3">{p.desc}</p>
                  <code className="block text-xs px-3 py-2 bg-slate-900/50 rounded border border-slate-700/30 font-mono" style={{color: p.color}}>{p.formula}</code>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Risk-Adjusted Returns */}
          <Card className="border-slate-700/30 bg-slate-800/30">
            <CardHeader className="pb-3"><CardTitle className="text-sm text-slate-200">Risk-Adjusted Return Metrics (Hull Chapter 24)</CardTitle></CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {[
                  { name: 'Sharpe Ratio', formula: 'S = (Rp - Rf) / σp', desc: 'Excess return per unit of total risk. Target > 1.0.', note: 'Uses std dev of ALL returns' },
                  { name: 'Sortino Ratio', formula: 'So = (Rp - Rf) / σd', desc: 'Excess return per unit of downside risk only. Target > 1.5.', note: 'Only penalizes negative volatility' },
                  { name: 'Calmar Ratio', formula: 'C = Annual Return / Max DD', desc: 'Return relative to worst drawdown. Target > 2.0.', note: 'Best for drawdown-focused funds' },
                  { name: 'Kelly Criterion', formula: 'f* = (bp - q) / b', desc: 'Optimal bet size for geometric growth. FIDUS uses fractional Kelly (25%).', note: 'b=odds, p=win prob, q=lose prob' },
                ].map((m, i) => (
                  <div key={i} className="p-3 bg-slate-700/20 rounded-lg border border-slate-700/20">
                    <div className="text-cyan-400 font-bold text-sm mb-1">{m.name}</div>
                    <code className="text-[10px] text-emerald-400 font-mono block mb-2">{m.formula}</code>
                    <p className="text-slate-400 text-[10px] leading-relaxed">{m.desc}</p>
                    <p className="text-slate-600 text-[9px] mt-1 italic">{m.note}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Correlation & Diversification */}
          <Card className="border-slate-700/30 bg-slate-800/30">
            <CardHeader className="pb-3"><CardTitle className="text-sm text-slate-200">Copy Trading Risk — Correlation is Hidden Leverage</CardTitle></CardHeader>
            <CardContent>
              <div className="p-4 bg-red-900/10 border border-red-500/20 rounded-lg mb-3">
                <p className="text-red-400 text-sm font-bold mb-1">Lesson from March 18, 2026:</p>
                <p className="text-slate-300 text-xs">One Gold strategy on master account 2210 created simultaneous XAUUSD exposure across 3 follower accounts. When Gold reversed, all accounts lost simultaneously. Copy trading with correlated strategies creates <strong className="text-red-400">hidden multi-account leverage</strong> that defeats diversification.</p>
              </div>
              <div className="grid grid-cols-3 gap-3 text-center text-xs">
                <div className="p-3 bg-slate-700/20 rounded-lg"><div className="text-red-400 font-bold text-lg">ρ = 1.0</div><div className="text-slate-500">Perfect correlation</div><div className="text-slate-600 text-[10px]">No diversification benefit</div></div>
                <div className="p-3 bg-slate-700/20 rounded-lg"><div className="text-amber-400 font-bold text-lg">ρ = 0.5</div><div className="text-slate-500">Moderate correlation</div><div className="text-slate-600 text-[10px]">Partial diversification</div></div>
                <div className="p-3 bg-slate-700/20 rounded-lg"><div className="text-emerald-400 font-bold text-lg">ρ = 0.0</div><div className="text-slate-500">Zero correlation</div><div className="text-slate-600 text-[10px]">Full diversification</div></div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* ═══ TAB 2: FIDUS POLICY ═══ */}
      {activeTab === 'policy' && policy && (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-bold text-white">FIDUS Risk Policy Configuration</h3>
            {!editing ? (
              <Button onClick={() => { setEditing(true); setEditPolicy({...policy}); }} className="bg-blue-600 hover:bg-blue-500 gap-2"><Edit2 size={14}/> Edit Parameters</Button>
            ) : (
              <div className="flex gap-2">
                <Button onClick={savePolicy} className="bg-emerald-600 hover:bg-emerald-500 gap-2"><Save size={14}/> Save</Button>
                <Button variant="outline" onClick={() => setEditing(false)} className="border-slate-600 text-slate-400"><X size={14}/></Button>
              </div>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Trade Risk Limits */}
            <Card className="border-slate-700/30 bg-slate-800/30">
              <CardHeader className="pb-2"><CardTitle className="text-sm text-slate-200 flex items-center gap-2"><Percent size={16} className="text-cyan-400"/> Trade Risk Limits</CardTitle></CardHeader>
              <CardContent className="space-y-4">
                <PolicyField label="MAX RISK PER TRADE" value={editing ? editPolicy.max_risk_per_trade_pct : policy.max_risk_per_trade_pct} unit="%" note="@ $100k = $1,000 max loss per trade" editing={editing} onChange={v => setEditPolicy({...editPolicy, max_risk_per_trade_pct: parseFloat(v)})} />
                <PolicyField label="MAX MARGIN USAGE" value={editing ? editPolicy.max_margin_usage_pct : policy.max_margin_usage_pct} unit="%" note="Maximum equity to use as margin" editing={editing} onChange={v => setEditPolicy({...editPolicy, max_margin_usage_pct: parseFloat(v)})} />
              </CardContent>
            </Card>

            {/* Loss Limits */}
            <Card className="border-slate-700/30 bg-slate-800/30">
              <CardHeader className="pb-2"><CardTitle className="text-sm text-slate-200 flex items-center gap-2"><TrendingDown size={16} className="text-red-400"/> Loss Limits</CardTitle></CardHeader>
              <CardContent className="space-y-4">
                <PolicyField label="MAX INTRADAY LOSS" value={editing ? editPolicy.max_intraday_loss_pct : policy.max_intraday_loss_pct} unit="%" note="@ $100k = $3,000 daily limit" editing={editing} onChange={v => setEditPolicy({...editPolicy, max_intraday_loss_pct: parseFloat(v)})} />
                <PolicyField label="MAX WEEKLY LOSS" value={editing ? editPolicy.max_weekly_loss_pct : policy.max_weekly_loss_pct} unit="%" note="@ $100k = $6,000 weekly limit" editing={editing} onChange={v => setEditPolicy({...editPolicy, max_weekly_loss_pct: parseFloat(v)})} />
                <PolicyField label="MAX MONTHLY DRAWDOWN" value={editing ? editPolicy.max_monthly_dd_pct : policy.max_monthly_dd_pct} unit="%" note="@ $100k = $10,000 max drawdown" editing={editing} onChange={v => setEditPolicy({...editPolicy, max_monthly_dd_pct: parseFloat(v)})} />
              </CardContent>
            </Card>

            {/* Force Flat */}
            <Card className="border-slate-700/30 bg-slate-800/30">
              <CardHeader className="pb-2"><CardTitle className="text-sm text-slate-200 flex items-center gap-2"><Clock size={16} className="text-amber-400"/> Force Flat (EOD)</CardTitle></CardHeader>
              <CardContent className="space-y-4">
                <PolicyField label="FORCE FLAT TIME" value={policy.force_flat_time_utc || '21:50'} unit="" note="Close all positions at this time" editing={false} />
                <PolicyField label="TIMEZONE" value="America/New_York" unit="" note="4:50 PM ET" editing={false} />
                <div className="p-3 bg-red-900/15 border border-red-500/20 rounded-lg">
                  <p className="text-red-400 text-xs font-bold">NO OVERNIGHT POSITIONS</p>
                  <p className="text-slate-500 text-[10px]">Penalty: -15 pts per occurrence (max -45)</p>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Penalty Structure */}
          <Card className="border-slate-700/30 bg-slate-800/30">
            <CardHeader className="pb-3"><CardTitle className="text-sm text-slate-200 flex items-center gap-2"><AlertTriangle size={16} className="text-amber-400"/> Risk Score Penalty Structure</CardTitle></CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3">
                {[
                  { name: 'Lot Size Breach', pts: -6, cap: -30 },
                  { name: 'Risk/Trade Breach', pts: -8, cap: -40 },
                  { name: 'Margin Breach', pts: -10, cap: -25 },
                  { name: 'Daily Loss Breach', pts: -20, cap: -40 },
                  { name: 'Weekly Loss Breach', pts: -25, cap: -50 },
                  { name: 'Monthly DD Breach', pts: -40, cap: 'ONE-TIME' },
                  { name: 'Overnight Position', pts: -15, cap: -45 },
                ].map((p, i) => (
                  <div key={i} className="p-3 bg-slate-800/50 border border-slate-700/30 rounded-lg text-center">
                    <div className="text-slate-400 text-[10px] mb-1">{p.name}</div>
                    <div className="text-red-400 font-bold text-xl font-mono">{p.pts}</div>
                    <div className="text-slate-600 text-[9px]">Cap: {p.cap}</div>
                  </div>
                ))}
              </div>
              <div className="flex gap-2 mt-4 justify-center">
                {[{ r: '80-100', l: 'Strong', c: '#10b981' }, { r: '60-79', l: 'Moderate', c: '#0ea5e9' }, { r: '40-59', l: 'Weak', c: '#f59e0b' }, { r: '0-39', l: 'Critical', c: '#ef4444' }].map(s => (
                  <span key={s.l} className="text-xs px-3 py-1 rounded-full border" style={{ borderColor: `${s.c}40`, color: s.c }}>{s.r}: {s.l}</span>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* ═══ TAB 3: PROHIBITED CALENDAR ═══ */}
      {activeTab === 'calendar' && calendar && (
        <div className="space-y-6">
          {/* Today's Alert */}
          {calendar.today_is_prohibited && calendar.active_today.map((ev, i) => (
            <div key={i} className="p-4 bg-red-900/30 border-2 border-red-500/50 rounded-lg animate-pulse flex items-center gap-3">
              <AlertTriangle className="w-8 h-8 text-red-400" />
              <div>
                <div className="text-red-400 font-bold text-lg">TRADING PROHIBITED TODAY — {ev.name}</div>
                <div className="text-red-300 text-sm">Action: {ev.action} | Instruments: {ev.instruments}</div>
              </div>
            </div>
          ))}

          {/* Next Event Countdown */}
          {calendar.next_event && (
            <Card className="border-amber-500/20 bg-amber-900/10">
              <CardContent className="p-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Bell className="w-6 h-6 text-amber-400" />
                  <div>
                    <div className="text-white font-bold">{calendar.next_event.name}</div>
                    <div className="text-slate-400 text-xs">{calendar.next_event.date} | {calendar.next_event.action}</div>
                  </div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-black text-amber-400 font-mono">{calendar.next_event.days_away}</div>
                  <div className="text-xs text-slate-500">days away</div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Calendar by Month */}
          {Object.entries(calendar.by_month || {}).filter(([mk]) => mk >= new Date().toISOString().slice(0,7)).slice(0, 6).map(([month, events]) => (
            <Card key={month} className="border-slate-700/30 bg-slate-800/30">
              <CardHeader className="pb-2"><CardTitle className="text-sm text-slate-200">{new Date(month+'-01').toLocaleString('en-US', {month:'long', year:'numeric'})}</CardTitle></CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {events.filter(e => !e.is_past).map((ev, i) => {
                    const colors = { CRITICAL: 'border-red-500/30 bg-red-900/10 text-red-400', HIGH: 'border-amber-500/30 bg-amber-900/10 text-amber-400', CLOSED: 'border-slate-500/30 bg-slate-800/30 text-slate-400', REDUCED: 'border-yellow-500/30 bg-yellow-900/10 text-yellow-400' };
                    const c = colors[ev.impact] || colors.HIGH;
                    return (
                      <div key={i} className={`p-3 rounded-lg border ${c} flex items-center justify-between`}>
                        <div className="flex items-center gap-3">
                          <span className="text-white font-mono text-xs w-20">{ev.date.slice(5)}</span>
                          <Badge variant="outline" className={`text-[9px] ${c}`}>{ev.type}</Badge>
                          <span className="text-sm font-medium">{ev.name}</span>
                        </div>
                        <div className="flex items-center gap-3 text-xs">
                          <span className="text-slate-500">{ev.instruments}</span>
                          <Badge className={`text-[9px] ${ev.impact === 'CRITICAL' ? 'bg-red-600' : ev.impact === 'HIGH' ? 'bg-amber-600' : 'bg-slate-600'} text-white`}>{ev.action}</Badge>
                          {ev.days_away >= 0 && <span className="text-slate-400 font-mono w-8 text-right">{ev.days_away}d</span>}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* ═══ TAB 4: POSITION SIZING CALCULATOR ═══ */}
      {activeTab === 'sizing' && (
        <div className="space-y-6">
          <Card className="border-cyan-500/15 bg-slate-800/30">
            <CardHeader className="pb-3"><CardTitle className="text-sm text-slate-200">Hull Position Sizing Calculator</CardTitle></CardHeader>
            <CardContent>
              <p className="text-slate-400 text-xs mb-4">Lots = (Equity × Risk%) ÷ (ATR × Stop Multiplier × Pip Value)</p>
              <div className="flex gap-4 items-end">
                <div className="flex-1">
                  <label className="text-xs text-slate-400">Account Equity ($)</label>
                  <Input type="number" value={sizingEquity} onChange={e => setSizingEquity(Number(e.target.value))} className="bg-slate-900/50 border-slate-700 text-white mt-1" />
                </div>
                <div className="flex-1">
                  <label className="text-xs text-slate-400">Risk Per Trade (%)</label>
                  <Input type="number" value={sizingRisk} step={0.1} onChange={e => setSizingRisk(Number(e.target.value))} className="bg-slate-900/50 border-slate-700 text-white mt-1" />
                </div>
                <Button onClick={recalcSizing} className="bg-cyan-600 hover:bg-cyan-500 gap-2"><Calculator size={14}/> Calculate</Button>
              </div>
              {sizing && <div className="mt-2 text-xs text-cyan-400">Risk Budget: {fmt(sizing.risk_budget)} per trade at {sizingRisk}% risk</div>}
            </CardContent>
          </Card>

          {sizing && (
            <Card className="border-slate-700/30 bg-slate-800/30">
              <CardContent className="p-0">
                <table className="w-full text-xs">
                  <thead><tr className="border-b border-slate-700/30 text-slate-400">
                    <th className="text-left p-3">Instrument</th><th className="text-left p-3">Class</th>
                    <th className="text-right p-3">Hull Lots</th><th className="text-right p-3">Max Lots</th>
                    <th className="text-right p-3 text-cyan-400">Recommended</th>
                    <th className="text-right p-3">Stop Dist.</th><th className="text-right p-3">Max Loss</th>
                  </tr></thead>
                  <tbody>
                    {sizing.instruments.map((inst, i) => (
                      <tr key={i} className="border-b border-slate-700/10 hover:bg-slate-700/10">
                        <td className="p-3 text-white font-medium">{inst.symbol}</td>
                        <td className="p-3"><Badge variant="outline" className="text-[9px] border-slate-600 text-slate-400">{inst.asset_class}</Badge></td>
                        <td className="p-3 text-right text-slate-300 font-mono">{inst.hull_lots}</td>
                        <td className="p-3 text-right text-amber-400 font-mono">{inst.max_lots}</td>
                        <td className="p-3 text-right text-cyan-400 font-mono font-bold">{inst.recommended_lots}</td>
                        <td className="p-3 text-right text-slate-400 font-mono">{inst.stop_distance}</td>
                        <td className="p-3 text-right text-red-400 font-mono">{fmt(inst.max_loss_at_stop)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* ═══ TAB 5: STRESS TESTING ═══ */}
      {activeTab === 'stress' && stress && (
        <div className="space-y-6">
          <Card className="border-slate-700/30 bg-slate-800/30">
            <CardHeader className="pb-3"><CardTitle className="text-sm text-slate-200">Stress Test Scenarios at Portfolio Equity {fmt(stress.equity)}</CardTitle></CardHeader>
            <CardContent>
              <div className="space-y-3">
                {stress.scenarios.map((sc, i) => (
                  <div key={i} className={`p-4 rounded-lg border ${sc.severity === 'CRITICAL' ? 'border-red-500/30 bg-red-900/10' : sc.severity === 'HIGH' ? 'border-amber-500/30 bg-amber-900/10' : 'border-slate-700/30 bg-slate-800/20'}`}>
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <Badge className={`text-[9px] ${sc.severity === 'CRITICAL' ? 'bg-red-600' : sc.severity === 'HIGH' ? 'bg-amber-600' : 'bg-slate-600'} text-white`}>{sc.severity}</Badge>
                        <span className="text-white font-bold text-sm">{sc.name}</span>
                      </div>
                      <span className="text-red-400 font-mono font-bold text-lg">-{sc.loss_pct}%</span>
                    </div>
                    <p className="text-slate-400 text-xs mb-3">{sc.description}</p>
                    <div className="grid grid-cols-4 gap-3 text-center text-xs">
                      <div><div className="text-red-400 font-bold">{fmt(sc.loss_amount)}</div><div className="text-slate-500">Loss</div></div>
                      <div><div className="text-white font-bold">{fmt(sc.surviving_equity)}</div><div className="text-slate-500">Surviving</div></div>
                      <div><div className="text-amber-400 font-bold">{sc.recovery_pct_needed}%</div><div className="text-slate-500">Recovery Needed</div></div>
                      <div><div className="text-cyan-400 font-bold">{sc.months_to_recover} mo</div><div className="text-slate-500">Time to Recover</div></div>
                    </div>
                    {sc.breaches_10pct && <div className="mt-2 p-2 bg-red-900/20 rounded text-red-400 text-[10px] text-center font-bold">BREACHES 10% PROTECTION LINE</div>}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* ═══ TAB 6: COMPLIANCE ═══ */}
      {activeTab === 'compliance' && compliance && (
        <div className="space-y-6">
          {/* Portfolio Status */}
          <Card className={`border-2 ${compliance.portfolio?.breached ? 'border-red-500/40 bg-red-900/10' : 'border-emerald-500/20 bg-emerald-900/5'}`}>
            <CardContent className="p-5">
              <div className="flex items-center justify-between">
                <div>
                  <div className={`text-2xl font-bold ${compliance.portfolio?.breached ? 'text-red-400' : 'text-emerald-400'}`}>
                    {compliance.portfolio?.breached ? 'PORTFOLIO BREACHED' : 'PORTFOLIO COMPLIANT'}
                  </div>
                  <div className="text-slate-400 text-sm">Drawdown: {compliance.portfolio?.drawdown_pct?.toFixed(2)}% | Protection: {fmt(compliance.portfolio?.protection_line)}</div>
                </div>
                <div className="text-right">
                  <div className="text-3xl font-black text-white font-mono">{fmt(compliance.portfolio?.total_equity)}</div>
                  <div className="text-slate-500 text-xs">of {fmt(compliance.portfolio?.total_initial)}</div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Per-Account */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {(compliance.accounts || []).map(acc => {
              const color = acc.drawdown_pct <= -10 ? '#ef4444' : acc.drawdown_pct <= -5 ? '#f59e0b' : acc.drawdown_pct <= -3 ? '#eab308' : '#10b981';
              return (
                <Card key={acc.account} className="border-slate-700/30 bg-slate-800/30">
                  <CardContent className="p-4">
                    <div className="flex justify-between items-center mb-3">
                      <div className="text-white font-bold text-sm">{acc.manager_name}</div>
                      <Badge style={{ borderColor: `${color}40`, color }}>{acc.alert_status}</Badge>
                    </div>
                    <div className="space-y-2 text-xs">
                      <div className="flex justify-between"><span className="text-slate-400">Equity</span><span className="text-white font-mono">{fmt(acc.equity)}</span></div>
                      <div className="flex justify-between"><span className="text-slate-400">Drawdown</span><span style={{color}} className="font-mono font-bold">{acc.drawdown_pct?.toFixed(2)}%</span></div>
                      <div className="w-full bg-slate-700/50 rounded-full h-2">
                        <div className="h-2 rounded-full" style={{ width: `${Math.min(Math.abs(acc.drawdown_pct || 0) / 20 * 100, 100)}%`, background: color }} />
                      </div>
                      <div className="flex justify-between text-[9px] text-slate-600"><span>0%</span><span>-10%</span><span>-20%</span></div>
                      {acc.unresolved_alerts > 0 && <div className="p-1.5 bg-red-900/20 rounded text-red-400 text-[10px] text-center">{acc.unresolved_alerts} unresolved alert(s)</div>}
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

const PolicyField = ({ label, value, unit, note, editing, onChange }) => (
  <div>
    <div className="text-slate-400 text-[10px] font-medium mb-1">{label}</div>
    {editing && onChange ? (
      <div className="flex items-center gap-1">
        <Input type="number" value={value} onChange={e => onChange(e.target.value)} className="bg-slate-900/50 border-slate-700 text-white h-9 text-lg font-mono" step={0.5} />
        {unit && <span className="text-slate-400 text-sm">{unit}</span>}
      </div>
    ) : (
      <div className="text-white text-2xl font-bold font-mono">{value}{unit}</div>
    )}
    {note && <div className="text-slate-600 text-[10px] mt-1">{note}</div>}
  </div>
);

export default RiskParameters;
