import React, { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import {
  Building2, Users, DollarSign, TrendingUp, LogOut, PieChart,
  BarChart3, Shield, Activity, UserPlus, RefreshCw, ChevronRight,
  Wallet, ArrowUpRight, ArrowDownRight, Clock, FileText, Loader2
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Utility
const fmt = (amount) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(amount || 0);
const fmtPct = (v) => `${(v || 0).toFixed(2)}%`;

// ─────────────────────────────────────────
// OVERVIEW TAB
// ─────────────────────────────────────────
const OverviewTab = ({ overview, loading }) => {
  if (loading) return <LoadingSkeleton />;
  if (!overview) return <EmptyState msg="No overview data available" />;

  const stats = overview.stats || {};
  const projections = overview.monthly_projections || {};
  const company = overview.company || {};

  return (
    <div className="space-y-6" data-testid="franchise-overview-tab">
      {/* KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard icon={DollarSign} label="Total AUM" value={fmt(stats.total_aum)} color="#0ea5e9" />
        <KPICard icon={Users} label="Total Clients" value={stats.total_clients || 0} color="#10b981" />
        <KPICard icon={UserPlus} label="Referral Agents" value={stats.total_agents || 0} color="#f59e0b" />
        <KPICard icon={TrendingUp} label="Monthly Commission" value={fmt(projections.company_share)} color="#8b5cf6" />
      </div>

      {/* Monthly Projections */}
      <Card className="border-slate-700/50 bg-slate-800/40">
        <CardHeader className="pb-3">
          <CardTitle className="text-base text-slate-200">Monthly Projections</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <ProjectionItem label="Gross Return (2.5%)" value={fmt(projections.gross_return)} color="#10b981" />
            <ProjectionItem label="Client Payments (2.0%)" value={fmt(projections.client_payments)} color="#ef4444" />
            <ProjectionItem label="Commission Pool (0.5%)" value={fmt(projections.commission_pool)} color="#f59e0b" />
            <ProjectionItem label="Company Share" value={fmt(projections.company_share)} color="#0ea5e9" />
            <ProjectionItem label="Agent Share" value={fmt(projections.agent_share)} color="#8b5cf6" />
          </div>
        </CardContent>
      </Card>

      {/* Company Info */}
      <Card className="border-slate-700/50 bg-slate-800/40">
        <CardHeader className="pb-3">
          <CardTitle className="text-base text-slate-200">Company Details</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div><span className="text-slate-500">Company</span><p className="text-slate-200 font-medium">{company.name || '-'}</p></div>
            <div><span className="text-slate-500">Code</span><p className="text-slate-200 font-medium">{company.code || '-'}</p></div>
            <div><span className="text-slate-500">Subdomain</span><p className="text-sky-400 font-medium">{company.subdomain || '-'}</p></div>
            <div><span className="text-slate-500">Status</span><Badge variant="outline" className="border-emerald-500/40 text-emerald-400 mt-1">{company.status || 'active'}</Badge></div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// ─────────────────────────────────────────
// FUND PORTFOLIO TAB
// ─────────────────────────────────────────
const PortfolioTab = ({ token, loading: parentLoading }) => {
  const [portfolio, setPortfolio] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPortfolio = async () => {
      try {
        const res = await fetch(`${API_URL}/api/franchise/dashboard/portfolio`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json();
        if (data.success) setPortfolio(data.portfolio);
      } catch (e) { console.error('Portfolio fetch error:', e); }
      finally { setLoading(false); }
    };
    fetchPortfolio();
  }, [token]);

  if (loading || parentLoading) return <LoadingSkeleton />;
  if (!portfolio) return <EmptyState msg="No portfolio data" />;

  const returns = portfolio.returns || {};
  const monthly = returns.monthly || {};
  const quarterly = returns.quarterly || {};
  const terms = portfolio.contract_terms || {};

  return (
    <div className="space-y-6" data-testid="franchise-portfolio-tab">
      {/* Portfolio Summary */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard icon={Wallet} label="Total AUM" value={fmt(portfolio.total_aum)} color="#0ea5e9" />
        <KPICard icon={Users} label="Total Clients" value={portfolio.total_clients || 0} color="#10b981" />
        <KPICard icon={PieChart} label="Fund Type" value={portfolio.fund_type || 'BALANCE'} color="#f59e0b" />
        <KPICard icon={Activity} label="Omnibus Account" value={portfolio.omnibus_account || 'Not Assigned'} color="#8b5cf6" />
      </div>

      {/* Returns Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card className="border-slate-700/50 bg-slate-800/40">
          <CardHeader className="pb-3">
            <CardTitle className="text-base text-slate-200">Monthly Returns</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <ReturnRow label="Gross Return" pct={`${returns.gross_return_pct}%`} value={fmt(monthly.gross_return)} up />
            <ReturnRow label="Client Obligation" pct={`${returns.client_return_pct}%`} value={fmt(monthly.client_obligation)} down />
            <ReturnRow label="Commission Pool" pct={`${returns.commission_pool_pct}%`} value={fmt(monthly.commission_pool)} up />
          </CardContent>
        </Card>

        <Card className="border-slate-700/50 bg-slate-800/40">
          <CardHeader className="pb-3">
            <CardTitle className="text-base text-slate-200">Quarterly Projections</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <ReturnRow label="Gross Return" value={fmt(quarterly.gross_return)} up />
            <ReturnRow label="Client Obligation" value={fmt(quarterly.client_obligation)} down />
            <ReturnRow label="Company Share" value={fmt(quarterly.company_share)} up />
            <ReturnRow label="Agent Share" value={fmt(quarterly.agent_share)} up />
          </CardContent>
        </Card>
      </div>

      {/* Contract Terms */}
      <Card className="border-slate-700/50 bg-slate-800/40">
        <CardHeader className="pb-3">
          <CardTitle className="text-base text-slate-200">Contract Terms</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-4 text-sm">
            <div><span className="text-slate-500">Duration</span><p className="text-slate-200 font-semibold">{terms.duration_months || 14} months</p></div>
            <div><span className="text-slate-500">Incubation</span><p className="text-slate-200 font-semibold">{terms.incubation_months || 2} months</p></div>
            <div><span className="text-slate-500">Payment</span><p className="text-slate-200 font-semibold capitalize">{terms.payment_frequency || 'quarterly'}</p></div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// ─────────────────────────────────────────
// CASH FLOW TAB
// ─────────────────────────────────────────
const CashFlowTab = ({ token }) => {
  const [cashflow, setCashflow] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCashflow = async () => {
      try {
        const res = await fetch(`${API_URL}/api/franchise/dashboard/cashflow`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json();
        if (data.success) setCashflow(data.cashflow);
      } catch (e) { console.error('Cashflow fetch error:', e); }
      finally { setLoading(false); }
    };
    fetchCashflow();
  }, [token]);

  if (loading) return <LoadingSkeleton />;
  if (!cashflow) return <EmptyState msg="No cash flow data" />;

  const summary = cashflow.summary || {};
  const proj = cashflow.monthly_projection || {};

  return (
    <div className="space-y-6" data-testid="franchise-cashflow-tab">
      {/* Summary Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard icon={DollarSign} label="Total Invested" value={fmt(summary.total_invested)} color="#0ea5e9" />
        <KPICard icon={TrendingUp} label="Returns Earned" value={fmt(summary.total_returns_earned)} color="#10b981" />
        <KPICard icon={ArrowUpRight} label="Returns Paid" value={fmt(summary.total_returns_paid)} color="#f59e0b" />
        <KPICard icon={Clock} label="Pending Payments" value={fmt(summary.pending_payments)} color="#ef4444" />
      </div>

      {/* Monthly Projection */}
      <Card className="border-slate-700/50 bg-slate-800/40">
        <CardHeader className="pb-3">
          <CardTitle className="text-base text-slate-200">Monthly Cash Flow Projection</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <ProjectionItem label="Gross Return" value={fmt(proj.gross_return)} color="#10b981" />
            <ProjectionItem label="Client Payments" value={fmt(proj.client_payments)} color="#ef4444" />
            <ProjectionItem label="Commission Pool" value={fmt(proj.commission_pool)} color="#f59e0b" />
            <ProjectionItem label="Company Share" value={fmt(proj.company_share)} color="#0ea5e9" />
            <ProjectionItem label="Agent Share" value={fmt(proj.agent_share)} color="#8b5cf6" />
          </div>
        </CardContent>
      </Card>

      {/* Investment Stats */}
      <Card className="border-slate-700/50 bg-slate-800/40">
        <CardHeader className="pb-3">
          <CardTitle className="text-base text-slate-200">Investment Breakdown</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-4 text-sm text-center">
            <div className="p-3 bg-slate-700/30 rounded-lg">
              <div className="text-2xl font-bold text-sky-400">{cashflow.investment_count || 0}</div>
              <div className="text-slate-500">Total Investments</div>
            </div>
            <div className="p-3 bg-slate-700/30 rounded-lg">
              <div className="text-2xl font-bold text-emerald-400">{cashflow.active_investments || 0}</div>
              <div className="text-slate-500">Active</div>
            </div>
            <div className="p-3 bg-slate-700/30 rounded-lg">
              <div className="text-2xl font-bold text-amber-400">{cashflow.incubation_investments || 0}</div>
              <div className="text-slate-500">Incubation</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// ─────────────────────────────────────────
// CLIENTS TAB
// ─────────────────────────────────────────
const ClientsTab = ({ token }) => {
  const [clients, setClients] = useState([]);
  const [summary, setSummary] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchClients = async () => {
      try {
        const res = await fetch(`${API_URL}/api/franchise/dashboard/clients`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json();
        if (data.success) {
          setClients(data.clients || []);
          setSummary(data.summary || {});
        }
      } catch (e) { console.error('Clients fetch error:', e); }
      finally { setLoading(false); }
    };
    fetchClients();
  }, [token]);

  if (loading) return <LoadingSkeleton />;

  return (
    <div className="space-y-6" data-testid="franchise-clients-tab">
      {/* Client Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard icon={Users} label="Total Clients" value={summary.total_clients || 0} color="#0ea5e9" />
        <KPICard icon={Activity} label="Active Clients" value={summary.active_clients || 0} color="#10b981" />
        <KPICard icon={Clock} label="In Incubation" value={summary.incubation_clients || 0} color="#f59e0b" />
        <KPICard icon={DollarSign} label="Total AUM" value={fmt(summary.total_aum)} color="#8b5cf6" />
      </div>

      {/* Client Table */}
      <Card className="border-slate-700/50 bg-slate-800/40">
        <CardHeader className="pb-3">
          <CardTitle className="text-base text-slate-200">Client List</CardTitle>
        </CardHeader>
        <CardContent>
          {clients.length === 0 ? (
            <div className="text-center py-12 text-slate-500">
              <Users className="w-12 h-12 mx-auto mb-3 opacity-30" />
              <p>No clients yet. Start onboarding your first client.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-700/50 text-slate-400">
                    <th className="text-left p-3">Client</th>
                    <th className="text-left p-3">Email</th>
                    <th className="text-right p-3">Invested</th>
                    <th className="text-right p-3">Returns</th>
                    <th className="text-center p-3">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {clients.map((client) => (
                    <tr key={client.client_id} className="border-b border-slate-700/30 hover:bg-slate-700/20 transition-colors">
                      <td className="p-3 text-slate-200 font-medium">{client.first_name} {client.last_name}</td>
                      <td className="p-3 text-slate-400">{client.email}</td>
                      <td className="p-3 text-right text-slate-200">{fmt(client.total_invested)}</td>
                      <td className="p-3 text-right text-emerald-400">{fmt(client.total_returns)}</td>
                      <td className="p-3 text-center">
                        <Badge variant="outline" className={
                          client.status === 'active' ? 'border-emerald-500/40 text-emerald-400' :
                          client.status === 'incubation' ? 'border-amber-500/40 text-amber-400' :
                          'border-slate-500/40 text-slate-400'
                        }>
                          {client.status || 'pending'}
                        </Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

// ─────────────────────────────────────────
// REFERRAL AGENTS TAB
// ─────────────────────────────────────────
const AgentsTab = ({ token }) => {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAgents = async () => {
      try {
        const res = await fetch(`${API_URL}/api/franchise/dashboard/agents`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json();
        if (data.success) setAgents(data.agents || []);
      } catch (e) { console.error('Agents fetch error:', e); }
      finally { setLoading(false); }
    };
    fetchAgents();
  }, [token]);

  if (loading) return <LoadingSkeleton />;

  return (
    <div className="space-y-6" data-testid="franchise-agents-tab">
      <Card className="border-slate-700/50 bg-slate-800/40">
        <CardHeader className="pb-3">
          <CardTitle className="text-base text-slate-200">Referral Agents ({agents.length})</CardTitle>
        </CardHeader>
        <CardContent>
          {agents.length === 0 ? (
            <div className="text-center py-12 text-slate-500">
              <UserPlus className="w-12 h-12 mx-auto mb-3 opacity-30" />
              <p>No referral agents yet.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-700/50 text-slate-400">
                    <th className="text-left p-3">Agent</th>
                    <th className="text-left p-3">Email</th>
                    <th className="text-right p-3">Clients Referred</th>
                    <th className="text-right p-3">AUM Referred</th>
                    <th className="text-right p-3">Commission Tier</th>
                    <th className="text-center p-3">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {agents.map((agent) => (
                    <tr key={agent.agent_id} className="border-b border-slate-700/30 hover:bg-slate-700/20 transition-colors">
                      <td className="p-3 text-slate-200 font-medium">{agent.first_name} {agent.last_name}</td>
                      <td className="p-3 text-slate-400">{agent.email}</td>
                      <td className="p-3 text-right text-slate-200">{agent.total_clients_referred || 0}</td>
                      <td className="p-3 text-right text-sky-400">{fmt(agent.total_aum_referred)}</td>
                      <td className="p-3 text-right text-amber-400">{agent.commission_tier || 50}%</td>
                      <td className="p-3 text-center">
                        <Badge variant="outline" className="border-emerald-500/40 text-emerald-400">
                          {agent.status || 'active'}
                        </Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

// ─────────────────────────────────────────
// COMMISSIONS TAB
// ─────────────────────────────────────────
const CommissionsTab = ({ token }) => {
  const [commissions, setCommissions] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCommissions = async () => {
      try {
        const res = await fetch(`${API_URL}/api/franchise/dashboard/commissions`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json();
        if (data.success) setCommissions(data.commissions);
      } catch (e) { console.error('Commissions fetch error:', e); }
      finally { setLoading(false); }
    };
    fetchCommissions();
  }, [token]);

  if (loading) return <LoadingSkeleton />;
  if (!commissions) return <EmptyState msg="No commission data" />;

  const split = commissions.split || {};
  const totals = commissions.totals || {};

  return (
    <div className="space-y-6" data-testid="franchise-commissions-tab">
      {/* Commission Split */}
      <Card className="border-slate-700/50 bg-slate-800/40">
        <CardHeader className="pb-3">
          <CardTitle className="text-base text-slate-200">Commission Split Structure</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-4">
            <div className="flex-1 bg-sky-500/20 rounded-lg p-4 text-center">
              <div className="text-3xl font-bold text-sky-400">{split.company || 50}%</div>
              <div className="text-sm text-slate-400 mt-1">Company Share</div>
            </div>
            <div className="text-slate-600 text-xl font-bold">/</div>
            <div className="flex-1 bg-purple-500/20 rounded-lg p-4 text-center">
              <div className="text-3xl font-bold text-purple-400">{split.agent || 50}%</div>
              <div className="text-sm text-slate-400 mt-1">Agent Share</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Commission Totals */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
        <KPICard icon={DollarSign} label="Total Pool" value={fmt(totals.pool)} color="#f59e0b" />
        <KPICard icon={Building2} label="Company Share" value={fmt(totals.company_share)} color="#0ea5e9" />
        <KPICard icon={Users} label="Agent Share" value={fmt(totals.agent_share)} color="#8b5cf6" />
        <KPICard icon={ArrowUpRight} label="Paid" value={fmt(totals.paid)} color="#10b981" />
        <KPICard icon={Clock} label="Pending" value={fmt(totals.pending)} color="#ef4444" />
      </div>

      {/* Transactions */}
      <Card className="border-slate-700/50 bg-slate-800/40">
        <CardHeader className="pb-3">
          <CardTitle className="text-base text-slate-200">Recent Transactions</CardTitle>
        </CardHeader>
        <CardContent>
          {(!commissions.transactions || commissions.transactions.length === 0) ? (
            <div className="text-center py-8 text-slate-500">
              <FileText className="w-10 h-10 mx-auto mb-2 opacity-30" />
              <p>No commission transactions yet.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-700/50 text-slate-400">
                    <th className="text-left p-3">Period</th>
                    <th className="text-left p-3">Type</th>
                    <th className="text-right p-3">Amount</th>
                    <th className="text-center p-3">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {commissions.transactions.map((tx, i) => (
                    <tr key={i} className="border-b border-slate-700/30">
                      <td className="p-3 text-slate-200">{tx.period || '-'}</td>
                      <td className="p-3 text-slate-400">{tx.transaction_type || '-'}</td>
                      <td className="p-3 text-right text-slate-200">{fmt(tx.amount)}</td>
                      <td className="p-3 text-center">
                        <Badge variant="outline" className={tx.status === 'paid' ? 'border-emerald-500/40 text-emerald-400' : 'border-amber-500/40 text-amber-400'}>
                          {tx.status || 'pending'}
                        </Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

// ─────────────────────────────────────────
// INSTRUMENTS TAB (read-only view of FIDUS instruments)
// ─────────────────────────────────────────
const InstrumentsTab = ({ token }) => {
  const [instruments, setInstruments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchInstruments = async () => {
      try {
        const res = await fetch(`${API_URL}/api/franchise/dashboard/instruments`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json();
        if (data.instruments) setInstruments(data.instruments);
        else if (Array.isArray(data)) setInstruments(data);
      } catch (e) { console.error('Instruments fetch error:', e); }
      finally { setLoading(false); }
    };
    fetchInstruments();
  }, [token]);

  if (loading) return <LoadingSkeleton />;

  return (
    <div className="space-y-6" data-testid="franchise-instruments-tab">
      <Card className="border-slate-700/50 bg-slate-800/40">
        <CardHeader className="pb-3">
          <CardTitle className="text-base text-slate-200">FIDUS Tier-1 Instrument Specifications</CardTitle>
        </CardHeader>
        <CardContent>
          {instruments.length === 0 ? (
            <EmptyState msg="No instrument specifications available" />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-700/50 text-slate-400">
                    <th className="text-left p-3">Symbol</th>
                    <th className="text-left p-3">Name</th>
                    <th className="text-left p-3">Asset Class</th>
                    <th className="text-right p-3">Contract Size</th>
                    <th className="text-right p-3">Leverage</th>
                    <th className="text-right p-3">Pip Size</th>
                    <th className="text-right p-3">Stop Proxy ($)</th>
                  </tr>
                </thead>
                <tbody>
                  {instruments.map((inst) => (
                    <tr key={inst.symbol} className="border-b border-slate-700/30 hover:bg-slate-700/20 transition-colors">
                      <td className="p-3 text-sky-400 font-mono font-semibold">{inst.symbol}</td>
                      <td className="p-3 text-slate-200">{inst.description || inst.name}</td>
                      <td className="p-3"><Badge variant="outline" className="border-slate-600 text-slate-300">{inst.asset_class}</Badge></td>
                      <td className="p-3 text-right text-slate-200">{inst.contract_size?.toLocaleString()}</td>
                      <td className="p-3 text-right text-slate-200">{inst.margin_leverage || 200}:1</td>
                      <td className="p-3 text-right text-slate-400">{inst.pip_size}</td>
                      <td className="p-3 text-right text-amber-400">${inst.default_stop_proxy_usd}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

// ─────────────────────────────────────────
// RISK PARAMETERS TAB (read-only view)
// ─────────────────────────────────────────
const RiskParamsTab = ({ token }) => {
  const [policy, setPolicy] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPolicy = async () => {
      try {
        const res = await fetch(`${API_URL}/api/franchise/dashboard/risk-policy`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json();
        if (data.policy) setPolicy(data.policy);
        else setPolicy(data);
      } catch (e) { console.error('Risk policy fetch error:', e); }
      finally { setLoading(false); }
    };
    fetchPolicy();
  }, [token]);

  if (loading) return <LoadingSkeleton />;
  if (!policy) return <EmptyState msg="No risk policy data" />;

  const params = [
    { label: 'Max Risk Per Trade', value: fmtPct(policy.max_risk_per_trade_pct), color: '#ef4444' },
    { label: 'Max Intraday Loss', value: fmtPct(policy.max_intraday_loss_pct), color: '#f59e0b' },
    { label: 'Max Weekly Loss', value: fmtPct(policy.max_weekly_loss_pct), color: '#f59e0b' },
    { label: 'Max Monthly Drawdown', value: fmtPct(policy.max_monthly_dd_pct), color: '#ef4444' },
    { label: 'Max Margin Usage', value: fmtPct(policy.max_margin_usage_pct), color: '#8b5cf6' },
    { label: 'Leverage', value: `${policy.leverage || 200}:1`, color: '#0ea5e9' },
    { label: 'Drawdown Warning', value: fmtPct(policy.drawdown_warning_pct), color: '#f59e0b' },
    { label: 'Drawdown Critical', value: fmtPct(policy.drawdown_critical_pct), color: '#ef4444' },
  ];

  return (
    <div className="space-y-6" data-testid="franchise-risk-params-tab">
      <Card className="border-slate-700/50 bg-slate-800/40">
        <CardHeader className="pb-3">
          <CardTitle className="text-base text-slate-200">FIDUS Risk Policy Parameters</CardTitle>
          <p className="text-xs text-slate-500 mt-1">Hull-Style Institutional Risk Management</p>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {params.map((p) => (
              <div key={p.label} className="bg-slate-700/30 rounded-lg p-4 text-center">
                <div className="text-xl font-bold" style={{ color: p.color }}>{p.value}</div>
                <div className="text-xs text-slate-400 mt-1">{p.label}</div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Risk Score Labels */}
      <Card className="border-slate-700/50 bg-slate-800/40">
        <CardHeader className="pb-3">
          <CardTitle className="text-base text-slate-200">Risk Control Score Labels</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-4 gap-3 text-center text-sm">
            <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-lg p-3">
              <div className="text-lg font-bold text-emerald-400">80-100</div>
              <div className="text-slate-400">Strong</div>
            </div>
            <div className="bg-sky-500/10 border border-sky-500/20 rounded-lg p-3">
              <div className="text-lg font-bold text-sky-400">60-79</div>
              <div className="text-slate-400">Moderate</div>
            </div>
            <div className="bg-amber-500/10 border border-amber-500/20 rounded-lg p-3">
              <div className="text-lg font-bold text-amber-400">40-59</div>
              <div className="text-slate-400">Weak</div>
            </div>
            <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3">
              <div className="text-lg font-bold text-red-400">0-39</div>
              <div className="text-slate-400">Critical</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// ─────────────────────────────────────────
// GAP ANALYSIS TAB
// ─────────────────────────────────────────
const GapAnalysisTab = ({ token, overview }) => {
  // Gap analysis: compare company AUM to fund terms, show revenue gaps
  const stats = overview?.stats || {};
  const proj = overview?.monthly_projections || {};
  const totalAum = stats.total_aum || 0;

  const benchmarks = [
    { label: 'Target AUM $500K', target: 500000, current: totalAum },
    { label: 'Target AUM $1M', target: 1000000, current: totalAum },
    { label: 'Target AUM $5M', target: 5000000, current: totalAum },
  ];

  return (
    <div className="space-y-6" data-testid="franchise-gap-analysis-tab">
      {/* Current vs Target */}
      <Card className="border-slate-700/50 bg-slate-800/40">
        <CardHeader className="pb-3">
          <CardTitle className="text-base text-slate-200">AUM Growth Targets</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {benchmarks.map((b) => {
            const pct = b.target > 0 ? Math.min((b.current / b.target) * 100, 100) : 0;
            const gap = b.target - b.current;
            return (
              <div key={b.label} className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-slate-300">{b.label}</span>
                  <span className="text-slate-400">{pct.toFixed(1)}% ({fmt(b.current)} / {fmt(b.target)})</span>
                </div>
                <div className="w-full bg-slate-700/50 rounded-full h-3">
                  <div
                    className="h-3 rounded-full transition-all duration-500"
                    style={{
                      width: `${pct}%`,
                      background: pct >= 100 ? '#10b981' : pct >= 50 ? '#0ea5e9' : '#f59e0b'
                    }}
                  />
                </div>
                {gap > 0 && <div className="text-xs text-slate-500">Gap: {fmt(gap)} remaining</div>}
              </div>
            );
          })}
        </CardContent>
      </Card>

      {/* Revenue Projections at scale */}
      <Card className="border-slate-700/50 bg-slate-800/40">
        <CardHeader className="pb-3">
          <CardTitle className="text-base text-slate-200">Revenue at Scale (Monthly)</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-700/50 text-slate-400">
                  <th className="text-left p-3">AUM Level</th>
                  <th className="text-right p-3">Gross (2.5%)</th>
                  <th className="text-right p-3">Client Pay (2.0%)</th>
                  <th className="text-right p-3">Commission Pool</th>
                  <th className="text-right p-3">Company Revenue</th>
                </tr>
              </thead>
              <tbody>
                {[100000, 500000, 1000000, 5000000, 10000000].map((aum) => (
                  <tr key={aum} className="border-b border-slate-700/30">
                    <td className="p-3 text-slate-200 font-medium">{fmt(aum)}</td>
                    <td className="p-3 text-right text-emerald-400">{fmt(aum * 0.025)}</td>
                    <td className="p-3 text-right text-red-400">{fmt(aum * 0.02)}</td>
                    <td className="p-3 text-right text-amber-400">{fmt(aum * 0.005)}</td>
                    <td className="p-3 text-right text-sky-400 font-semibold">{fmt(aum * 0.005 * 0.5)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="text-xs text-slate-500 mt-3">* Company revenue assumes 50/50 commission split. Actual split may differ.</p>
        </CardContent>
      </Card>
    </div>
  );
};

// ─────────────────────────────────────────
// SHARED COMPONENTS
// ─────────────────────────────────────────
const KPICard = ({ icon: Icon, label, value, color }) => (
  <Card className="border-slate-700/50 bg-slate-800/40">
    <CardContent className="p-4 flex items-center gap-3">
      <div className="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0" style={{ background: `${color}20` }}>
        <Icon className="w-5 h-5" style={{ color }} />
      </div>
      <div className="min-w-0">
        <div className="text-xs text-slate-500 truncate">{label}</div>
        <div className="text-lg font-bold text-slate-100 truncate">{value}</div>
      </div>
    </CardContent>
  </Card>
);

const ProjectionItem = ({ label, value, color }) => (
  <div className="text-center p-3 bg-slate-700/30 rounded-lg">
    <div className="text-lg font-bold" style={{ color }}>{value}</div>
    <div className="text-xs text-slate-500 mt-1">{label}</div>
  </div>
);

const ReturnRow = ({ label, pct, value, up, down }) => (
  <div className="flex items-center justify-between py-2 border-b border-slate-700/30 last:border-0">
    <div className="flex items-center gap-2">
      {up && <ArrowUpRight className="w-4 h-4 text-emerald-400" />}
      {down && <ArrowDownRight className="w-4 h-4 text-red-400" />}
      <span className="text-slate-300 text-sm">{label}</span>
      {pct && <span className="text-xs text-slate-500">({pct})</span>}
    </div>
    <span className={`font-semibold text-sm ${up ? 'text-emerald-400' : down ? 'text-red-400' : 'text-slate-200'}`}>{value}</span>
  </div>
);

const LoadingSkeleton = () => (
  <div className="space-y-4 animate-pulse">
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      {[1, 2, 3, 4].map((i) => <div key={i} className="h-20 bg-slate-800/60 rounded-lg" />)}
    </div>
    <div className="h-48 bg-slate-800/60 rounded-lg" />
  </div>
);

const EmptyState = ({ msg }) => (
  <div className="text-center py-16 text-slate-500">
    <BarChart3 className="w-12 h-12 mx-auto mb-3 opacity-30" />
    <p>{msg}</p>
  </div>
);

// ─────────────────────────────────────────
// MAIN PORTAL
// ─────────────────────────────────────────
const FranchisePortal = ({ authData, onLogout }) => {
  const [overview, setOverview] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  const token = authData?.token || localStorage.getItem('franchise_token');
  const company = authData?.company || JSON.parse(localStorage.getItem('franchise_company') || '{}');
  const admin = authData?.admin || JSON.parse(localStorage.getItem('franchise_admin') || '{}');

  const primaryColor = company.primary_color || '#0ea5e9';

  const fetchOverview = useCallback(async () => {
    try {
      const res = await fetch(`${API_URL}/api/franchise/dashboard/overview`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await res.json();
      if (data.success) setOverview(data.overview);
    } catch (e) { console.error('Overview fetch error:', e); }
    finally { setLoading(false); }
  }, [token]);

  useEffect(() => { fetchOverview(); }, [fetchOverview]);

  const handleLogout = () => {
    localStorage.removeItem('franchise_token');
    localStorage.removeItem('franchise_admin');
    localStorage.removeItem('franchise_company');
    onLogout();
  };

  return (
    <div data-testid="franchise-portal" className="min-h-screen" style={{ background: '#0a0f1a' }}>
      {/* Header */}
      <header className="border-b border-slate-800" style={{ background: 'rgba(10, 15, 26, 0.95)', backdropFilter: 'blur(12px)' }}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            {company.logo_url ? (
              <img src={company.logo_url} alt={company.company_name} className="h-8 w-auto" />
            ) : (
              <div className="w-9 h-9 rounded-xl flex items-center justify-center" style={{ background: `linear-gradient(135deg, ${primaryColor}, ${primaryColor}dd)` }}>
                <Building2 className="w-5 h-5 text-white" />
              </div>
            )}
            <div>
              <h1 className="text-lg font-bold text-white leading-tight">{company.company_name || 'Franchise Portal'}</h1>
              <p className="text-xs text-slate-500">{company.subdomain || 'Powered by FIDUS'}</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-sm text-slate-400 hidden sm:block">{admin.first_name} {admin.last_name}</span>
            <Button
              data-testid="franchise-refresh-btn"
              variant="ghost"
              size="sm"
              onClick={fetchOverview}
              className="text-slate-400 hover:text-white"
            >
              <RefreshCw className="w-4 h-4" />
            </Button>
            <Button
              data-testid="franchise-logout-btn"
              variant="ghost"
              size="sm"
              onClick={handleLogout}
              className="text-slate-400 hover:text-red-400"
            >
              <LogOut className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 py-6">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <div className="overflow-x-auto pb-2">
            <TabsList className="bg-slate-800/50 border border-slate-700/50 inline-flex w-auto min-w-full sm:min-w-0">
              <TabsTrigger value="overview" className="flex-shrink-0" data-testid="tab-overview">Overview</TabsTrigger>
              <TabsTrigger value="portfolio" className="flex-shrink-0" data-testid="tab-portfolio">Fund Portfolio</TabsTrigger>
              <TabsTrigger value="cashflow" className="flex-shrink-0" data-testid="tab-cashflow">Cash Flow</TabsTrigger>
              <TabsTrigger value="instruments" className="flex-shrink-0" data-testid="tab-instruments">Instruments</TabsTrigger>
              <TabsTrigger value="risk" className="flex-shrink-0" data-testid="tab-risk">Risk Parameters</TabsTrigger>
              <TabsTrigger value="gap" className="flex-shrink-0" data-testid="tab-gap">Gap Analysis</TabsTrigger>
              <TabsTrigger value="clients" className="flex-shrink-0" data-testid="tab-clients">Clients</TabsTrigger>
              <TabsTrigger value="agents" className="flex-shrink-0" data-testid="tab-agents">Referrals</TabsTrigger>
              <TabsTrigger value="commissions" className="flex-shrink-0" data-testid="tab-commissions">Commissions</TabsTrigger>
            </TabsList>
          </div>

          <div className="mt-6">
            <TabsContent value="overview"><OverviewTab overview={overview} loading={loading} /></TabsContent>
            <TabsContent value="portfolio"><PortfolioTab token={token} loading={loading} /></TabsContent>
            <TabsContent value="cashflow"><CashFlowTab token={token} /></TabsContent>
            <TabsContent value="instruments"><InstrumentsTab token={token} /></TabsContent>
            <TabsContent value="risk"><RiskParamsTab token={token} /></TabsContent>
            <TabsContent value="gap"><GapAnalysisTab token={token} overview={overview} /></TabsContent>
            <TabsContent value="clients"><ClientsTab token={token} /></TabsContent>
            <TabsContent value="agents"><AgentsTab token={token} /></TabsContent>
            <TabsContent value="commissions"><CommissionsTab token={token} /></TabsContent>
          </div>
        </Tabs>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800 mt-12 py-4">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 text-center">
          <p className="text-xs text-slate-600">Powered by FIDUS Investment Management | White Label Franchise System</p>
        </div>
      </footer>
    </div>
  );
};

export default FranchisePortal;
