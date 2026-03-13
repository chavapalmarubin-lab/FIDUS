import React, { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import {
  DollarSign, TrendingUp, Users, Building2, ArrowRight,
  ArrowDown, Percent, Calculator, PieChart, BarChart3
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';

const fmt = (v) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(v || 0);
const fmtK = (v) => {
  if (v >= 1000000) return `$${(v / 1000000).toFixed(1)}M`;
  if (v >= 1000) return `$${(v / 1000).toFixed(0)}K`;
  return fmt(v);
};

const FranchiseSimulator = () => {
  const [aum, setAum] = useState(10000000);
  const [companySplit, setCompanySplit] = useState(50);
  const [clientPct, setClientPct] = useState(2.0);
  const [avgInvestment, setAvgInvestment] = useState(150000);
  const [agentCount, setAgentCount] = useState(5);

  const agentSplit = 100 - companySplit;
  const grossPct = 2.5;
  const spreadPct = parseFloat((grossPct - clientPct).toFixed(2));

  const calc = useMemo(() => {
    const monthlyGross = aum * (grossPct / 100);
    const monthlyClientPay = aum * (clientPct / 100);
    const monthlyPool = aum * (spreadPct / 100);
    const monthlyCompany = monthlyPool * (companySplit / 100);
    const monthlyAgent = monthlyPool * (agentSplit / 100);

    const quarterlyCompany = monthlyCompany * 3;
    const quarterlyAgent = monthlyAgent * 3;
    const annualCompany = monthlyCompany * 12;
    const annualAgent = monthlyAgent * 12;
    const annualPool = monthlyPool * 12;

    const clientCount = Math.floor(aum / avgInvestment);
    const clientsPerAgent = agentCount > 0 ? Math.ceil(clientCount / agentCount) : clientCount;
    const monthlyPerAgent = agentCount > 0 ? monthlyAgent / agentCount : 0;

    // 14-month contract projection
    const contractPool = monthlyPool * 12; // 12 earning months (2 incubation)
    const contractCompany = contractPool * (companySplit / 100);

    return {
      monthlyGross, monthlyClientPay, monthlyPool,
      monthlyCompany, monthlyAgent,
      quarterlyCompany, quarterlyAgent,
      annualCompany, annualAgent, annualPool,
      clientCount, clientsPerAgent, monthlyPerAgent,
      contractPool, contractCompany,
    };
  }, [aum, companySplit, agentSplit, avgInvestment, agentCount, clientPct, spreadPct, grossPct]);

  // AUM presets
  const aumPresets = [
    { label: '$1M', value: 1000000 },
    { label: '$5M', value: 5000000 },
    { label: '$10M', value: 10000000 },
    { label: '$25M', value: 25000000 },
    { label: '$50M', value: 50000000 },
  ];

  return (
    <div data-testid="franchise-simulator" className="min-h-screen" style={{ background: '#060a14' }}>
      {/* Header */}
      <header className="border-b border-slate-800/50" style={{ background: 'rgba(6, 10, 20, 0.95)', backdropFilter: 'blur(12px)' }}>
        <div className="max-w-6xl mx-auto px-4 sm:px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: 'linear-gradient(135deg, #0ea5e9, #6366f1)' }}>
              <Calculator className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-white tracking-tight">FIDUS Franchise Revenue Simulator</h1>
              <p className="text-xs text-slate-500">White Label Investment Fund | BALANCE Product</p>
            </div>
          </div>
          <a href="/franchise/login" className="text-sm text-sky-400 hover:text-sky-300 transition-colors">Franchise Portal</a>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 sm:px-6 py-8 space-y-8">

        {/* The Spread Explanation */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
          <Card className="border-0 overflow-hidden" style={{ background: 'linear-gradient(135deg, rgba(14, 165, 233, 0.08), rgba(99, 102, 241, 0.08))' }}>
            <CardContent className="p-6">
              <div className="flex flex-col md:flex-row items-center justify-center gap-3 md:gap-6 text-center">
                <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-xl px-6 py-4 min-w-[140px]">
                  <div className="text-3xl font-black text-emerald-400">{grossPct}%</div>
                  <div className="text-xs text-slate-400 mt-1">FIDUS Returns</div>
                  <div className="text-[10px] text-slate-500">Monthly Gross</div>
                </div>
                <ArrowRight className="w-6 h-6 text-slate-600 hidden md:block" />
                <ArrowDown className="w-6 h-6 text-slate-600 md:hidden" />
                <div className="bg-sky-500/10 border border-sky-500/20 rounded-xl px-6 py-4 min-w-[140px]">
                  <div className="text-3xl font-black text-sky-400">{clientPct}%</div>
                  <div className="text-xs text-slate-400 mt-1">Client Gets</div>
                  <div className="text-[10px] text-slate-500">Monthly Net</div>
                </div>
                <ArrowRight className="w-6 h-6 text-slate-600 hidden md:block" />
                <ArrowDown className="w-6 h-6 text-slate-600 md:hidden" />
                <div className="bg-amber-500/10 border border-amber-500/20 rounded-xl px-6 py-4 min-w-[140px] ring-2 ring-amber-500/20">
                  <div className="text-3xl font-black text-amber-400">{spreadPct}%</div>
                  <div className="text-xs text-slate-400 mt-1">Your Revenue</div>
                  <div className="text-[10px] text-slate-500">Commission Pool</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Controls */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* AUM Slider */}
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <Card className="border-slate-700/30 bg-slate-900/50">
              <CardContent className="p-5 space-y-4">
                <div className="flex items-center justify-between">
                  <label className="text-sm font-medium text-slate-300">Assets Under Management</label>
                  <span className="text-lg font-bold text-sky-400">{fmtK(aum)}</span>
                </div>
                <input
                  data-testid="aum-slider"
                  type="range"
                  min={500000} max={100000000} step={500000}
                  value={aum}
                  onChange={(e) => setAum(Number(e.target.value))}
                  className="w-full h-2 bg-slate-700 rounded-full appearance-none cursor-pointer accent-sky-500"
                />
                <div className="flex gap-2 flex-wrap">
                  {aumPresets.map((p) => (
                    <Button key={p.value} variant="outline" size="sm" onClick={() => setAum(p.value)}
                      className={`text-xs ${aum === p.value ? 'bg-sky-600 text-white border-sky-500' : 'border-slate-600 text-slate-400 hover:text-white'}`}>
                      {p.label}
                    </Button>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Client Return Rate */}
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.12 }}>
            <Card className="border-slate-700/30 bg-slate-900/50">
              <CardContent className="p-5 space-y-4">
                <div className="flex items-center justify-between">
                  <label className="text-sm font-medium text-slate-300">Client Return Rate</label>
                  <span className="text-sm text-slate-400">Client <span className="text-sky-400 font-bold">{clientPct}%</span> / Spread <span className="text-amber-400 font-bold">{spreadPct}%</span></span>
                </div>
                <input
                  data-testid="client-rate-slider"
                  type="range"
                  min={0.5} max={2.0} step={0.25}
                  value={clientPct}
                  onChange={(e) => setClientPct(parseFloat(e.target.value))}
                  className="w-full h-2 bg-slate-700 rounded-full appearance-none cursor-pointer accent-sky-400"
                />
                <div className="flex gap-2 flex-wrap">
                  {[{l:'0.5%',v:0.5},{l:'1.0%',v:1.0},{l:'1.5%',v:1.5},{l:'2.0%',v:2.0}].map((p) => (
                    <Button key={p.v} variant="outline" size="sm" onClick={() => setClientPct(p.v)}
                      className={`text-xs ${clientPct === p.v ? 'bg-sky-600 text-white border-sky-500' : 'border-slate-600 text-slate-400 hover:text-white'}`}>
                      {p.l}
                    </Button>
                  ))}
                </div>
                <div className="bg-amber-500/5 border border-amber-500/10 rounded-lg p-2 text-center">
                  <span className="text-xs text-slate-500">Your spread: </span>
                  <span className="text-sm font-bold text-amber-400">{grossPct}% - {clientPct}% = {spreadPct}%</span>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Commission Split */}
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}>
            <Card className="border-slate-700/30 bg-slate-900/50">
              <CardContent className="p-5 space-y-4">
                <div className="flex items-center justify-between">
                  <label className="text-sm font-medium text-slate-300">Commission Split</label>
                  <span className="text-sm text-slate-400">Company <span className="text-amber-400 font-bold">{companySplit}%</span> / Agent <span className="text-purple-400 font-bold">{agentSplit}%</span></span>
                </div>
                <input
                  data-testid="split-slider"
                  type="range"
                  min={30} max={80} step={5}
                  value={companySplit}
                  onChange={(e) => setCompanySplit(Number(e.target.value))}
                  className="w-full h-2 bg-slate-700 rounded-full appearance-none cursor-pointer accent-amber-500"
                />
                <div className="flex gap-2">
                  {[{ l: '50/50', v: 50 }, { l: '60/40', v: 60 }, { l: '70/30', v: 70 }].map((p) => (
                    <Button key={p.v} variant="outline" size="sm" onClick={() => setCompanySplit(p.v)}
                      className={`text-xs ${companySplit === p.v ? 'bg-amber-600 text-white border-amber-500' : 'border-slate-600 text-slate-400 hover:text-white'}`}>
                      {p.l}
                    </Button>
                  ))}
                </div>

                <div className="grid grid-cols-2 gap-3 pt-2">
                  <div>
                    <label className="text-xs text-slate-500">Avg Client Investment</label>
                    <input type="number" value={avgInvestment} onChange={e => setAvgInvestment(Number(e.target.value) || 100000)}
                      className="w-full mt-1 rounded-md bg-slate-800/60 border border-slate-700 text-white px-3 py-1.5 text-sm" />
                  </div>
                  <div>
                    <label className="text-xs text-slate-500">Number of Agents</label>
                    <input type="number" value={agentCount} onChange={e => setAgentCount(Number(e.target.value) || 1)}
                      className="w-full mt-1 rounded-md bg-slate-800/60 border border-slate-700 text-white px-3 py-1.5 text-sm" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </div>

        {/* Revenue Results */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <ResultCard label="Monthly Company Revenue" value={fmt(calc.monthlyCompany)} sub={`${fmtK(aum)} x ${spreadPct}% x ${companySplit}%`} color="#f59e0b" icon={Building2} />
            <ResultCard label="Quarterly Company Revenue" value={fmt(calc.quarterlyCompany)} sub="3 months" color="#0ea5e9" icon={TrendingUp} />
            <ResultCard label="Annual Company Revenue" value={fmt(calc.annualCompany)} sub="12 months" color="#10b981" icon={DollarSign} big />
            <ResultCard label="Annual Agent Payouts" value={fmt(calc.annualAgent)} sub={`Split to ${agentCount} agents`} color="#8b5cf6" icon={Users} />
          </div>
        </motion.div>

        {/* Flow of Money */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}>
          <Card className="border-slate-700/30 bg-slate-900/50">
            <CardHeader className="pb-3">
              <CardTitle className="text-base text-slate-200">Monthly Money Flow</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <FlowRow label="FIDUS generates on your AUM" sublabel={`${grossPct}% monthly`} value={fmt(calc.monthlyGross)} color="#10b981" pct={100} />
                <FlowRow label="Paid to your clients" sublabel={`${clientPct}% monthly`} value={`-${fmt(calc.monthlyClientPay)}`} color="#ef4444" pct={80} />
                <div className="border-t border-dashed border-slate-700 my-2" />
                <FlowRow label="Commission Pool (your revenue)" sublabel={`${spreadPct}% spread`} value={fmt(calc.monthlyPool)} color="#f59e0b" pct={20} highlight />
                <div className="pl-6 space-y-2">
                  <FlowRow label="Your company keeps" sublabel={`${companySplit}% of pool`} value={fmt(calc.monthlyCompany)} color="#f59e0b" pct={companySplit * 0.2} />
                  <FlowRow label="Paid to your agents" sublabel={`${agentSplit}% of pool`} value={fmt(calc.monthlyAgent)} color="#8b5cf6" pct={agentSplit * 0.2} />
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Scale Table */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <Card className="border-slate-700/30 bg-slate-900/50">
            <CardHeader className="pb-3">
              <CardTitle className="text-base text-slate-200">Revenue at Scale ({companySplit}/{agentSplit} Split, {spreadPct}% Spread)</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-slate-700/50 text-slate-400">
                      <th className="text-left p-3">AUM</th>
                      <th className="text-right p-3">Clients</th>
                      <th className="text-right p-3">Monthly Pool ({spreadPct}%)</th>
                      <th className="text-right p-3">Monthly Company</th>
                      <th className="text-right p-3">Annual Company</th>
                      <th className="text-right p-3">Per Agent/mo</th>
                    </tr>
                  </thead>
                  <tbody>
                    {[1000000, 5000000, 10000000, 25000000, 50000000, 100000000].map((a) => {
                      const pool = a * (spreadPct / 100);
                      const comp = pool * (companySplit / 100);
                      const ag = pool * (agentSplit / 100);
                      const isActive = a === aum;
                      return (
                        <tr key={a} className={`border-b border-slate-700/30 cursor-pointer transition-colors ${isActive ? 'bg-sky-500/10' : 'hover:bg-slate-800/30'}`} onClick={() => setAum(a)}>
                          <td className={`p-3 font-medium ${isActive ? 'text-sky-400' : 'text-slate-200'}`}>{fmtK(a)}</td>
                          <td className="p-3 text-right text-slate-400">{Math.floor(a / avgInvestment).toLocaleString()}</td>
                          <td className="p-3 text-right text-amber-400">{fmt(pool)}</td>
                          <td className="p-3 text-right text-amber-300 font-semibold">{fmt(comp)}</td>
                          <td className="p-3 text-right text-emerald-400 font-bold">{fmt(comp * 12)}</td>
                          <td className="p-3 text-right text-purple-400">{agentCount > 0 ? fmt(ag / agentCount) : '-'}</td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Key Stats */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35 }}>
          <Card className="border-slate-700/30 bg-slate-900/50">
            <CardHeader className="pb-3">
              <CardTitle className="text-base text-slate-200">Your Business at {fmtK(aum)} AUM</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                <div className="bg-slate-800/40 rounded-lg p-4">
                  <div className="text-2xl font-bold text-sky-400">{calc.clientCount.toLocaleString()}</div>
                  <div className="text-xs text-slate-500 mt-1">Total Clients</div>
                </div>
                <div className="bg-slate-800/40 rounded-lg p-4">
                  <div className="text-2xl font-bold text-amber-400">{agentCount}</div>
                  <div className="text-xs text-slate-500 mt-1">Agents</div>
                </div>
                <div className="bg-slate-800/40 rounded-lg p-4">
                  <div className="text-2xl font-bold text-purple-400">{calc.clientsPerAgent}</div>
                  <div className="text-xs text-slate-500 mt-1">Clients per Agent</div>
                </div>
                <div className="bg-slate-800/40 rounded-lg p-4">
                  <div className="text-2xl font-bold text-emerald-400">{fmt(calc.monthlyPerAgent)}</div>
                  <div className="text-xs text-slate-500 mt-1">Per Agent / Month</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Fund Terms */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
          <Card className="border-slate-700/30 bg-slate-900/50">
            <CardHeader className="pb-3">
              <CardTitle className="text-base text-slate-200">FIDUS BALANCE Fund Terms</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-sm text-center">
                <div className="bg-slate-800/40 rounded-lg p-3"><div className="text-lg font-bold text-emerald-400">{grossPct}%</div><div className="text-xs text-slate-500">Gross Monthly Return</div></div>
                <div className="bg-slate-800/40 rounded-lg p-3"><div className="text-lg font-bold text-sky-400">{clientPct}%</div><div className="text-xs text-slate-500">Client Monthly Return</div></div>
                <div className="bg-slate-800/40 rounded-lg p-3"><div className="text-lg font-bold text-amber-400">{spreadPct}%</div><div className="text-xs text-slate-500">Commission Pool</div></div>
                <div className="bg-slate-800/40 rounded-lg p-3"><div className="text-lg font-bold text-slate-200">14 mo</div><div className="text-xs text-slate-500">Contract Duration</div></div>
                <div className="bg-slate-800/40 rounded-lg p-3"><div className="text-lg font-bold text-slate-200">2 mo</div><div className="text-xs text-slate-500">Incubation Period</div></div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </main>

      <footer className="border-t border-slate-800/50 mt-12 py-6">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 text-center">
          <p className="text-xs text-slate-600">FIDUS Investment Management | White Label Franchise Program</p>
          <p className="text-[10px] text-slate-700 mt-1">This simulation is for illustrative purposes. Past performance does not guarantee future results.</p>
        </div>
      </footer>
    </div>
  );
};

// Sub-components
const ResultCard = ({ label, value, sub, color, icon: Icon, big }) => (
  <Card className={`border-slate-700/30 ${big ? 'bg-gradient-to-br from-slate-900/80 to-emerald-900/10 ring-1 ring-emerald-500/20' : 'bg-slate-900/50'}`}>
    <CardContent className="p-4">
      <div className="flex items-start gap-3">
        <div className="w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0" style={{ background: `${color}15` }}>
          <Icon className="w-4 h-4" style={{ color }} />
        </div>
        <div>
          <div className="text-xs text-slate-500">{label}</div>
          <div className={`font-bold ${big ? 'text-xl' : 'text-lg'}`} style={{ color }}>{value}</div>
          <div className="text-[10px] text-slate-600 mt-0.5">{sub}</div>
        </div>
      </div>
    </CardContent>
  </Card>
);

const FlowRow = ({ label, sublabel, value, color, pct, highlight }) => (
  <div className={`flex items-center justify-between py-2 px-3 rounded-lg ${highlight ? 'bg-amber-500/5 border border-amber-500/10' : ''}`}>
    <div className="flex items-center gap-3 flex-1">
      <div className="w-1 h-8 rounded-full" style={{ background: color }} />
      <div>
        <div className={`text-sm ${highlight ? 'font-semibold text-white' : 'text-slate-300'}`}>{label}</div>
        <div className="text-[10px] text-slate-500">{sublabel}</div>
      </div>
    </div>
    <div className={`text-sm font-bold`} style={{ color }}>{value}</div>
  </div>
);

export default FranchiseSimulator;
