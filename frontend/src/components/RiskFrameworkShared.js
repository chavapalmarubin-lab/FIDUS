import React, { useState, useEffect } from 'react';
import { AlertTriangle, Bell, Shield, Calendar, TrendingDown } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

/**
 * Shared risk state hook — used across ALL FIDUS tabs.
 * Fetches risk status, prohibited calendar, and compliance data once,
 * then provides it to any component that needs it.
 */
export function useRiskFramework() {
  const [riskData, setRiskData] = useState({
    calendar: null,
    riskStatus: null,
    loading: true,
    todayProhibited: false,
    tomorrowProhibited: false,
    nextEvent: null,
    activeAlerts: [],
    portfolioBreached: false,
    portfolioDD: 0,
  });

  useEffect(() => {
    const token = localStorage.getItem('fidus_token');
    if (!token) return;
    const h = { 'Authorization': `Bearer ${token}` };

    Promise.all([
      fetch(`${API}/api/admin/risk-framework/prohibited-calendar`, { headers: h }).then(r => r.json()).catch(() => null),
      fetch(`${API}/api/admin/risk/status`, { headers: h }).then(r => r.json()).catch(() => null),
      fetch(`${API}/api/admin/risk/alerts/unresolved-count`, { headers: h }).then(r => r.json()).catch(() => null),
    ]).then(([calData, statusData, alertData]) => {
      const cal = calData?.success ? calData : null;
      const status = statusData?.success ? statusData : null;
      
      // Check if tomorrow is prohibited
      const tomorrow = new Date();
      tomorrow.setDate(tomorrow.getDate() + 1);
      const tomorrowStr = tomorrow.toISOString().slice(0, 10);
      const tomorrowEvents = (cal?.events || []).filter(e => e.date === tomorrowStr);

      setRiskData({
        calendar: cal,
        riskStatus: status,
        loading: false,
        todayProhibited: cal?.today_is_prohibited || false,
        tomorrowProhibited: tomorrowEvents.length > 0,
        tomorrowEvents,
        nextEvent: cal?.next_event || null,
        activeToday: cal?.active_today || [],
        alertCount: alertData?.count || 0,
        criticalAlerts: alertData?.critical || 0,
        portfolioBreached: status?.portfolio?.breached || false,
        portfolioDD: status?.portfolio?.drawdown_pct || 0,
        accounts: status?.accounts || [],
      });
    });
  }, []);

  return riskData;
}

/**
 * Global Risk Banner — displays at the top of ANY tab.
 * Shows: prohibited day warning, portfolio breach, upcoming events, alert count.
 */
export function RiskBanner({ risk }) {
  if (!risk || risk.loading) return null;
  
  const banners = [];

  // 1. TODAY IS PROHIBITED
  if (risk.todayProhibited && risk.activeToday?.length > 0) {
    banners.push(
      <div key="today" className="flex items-center gap-3 p-3 bg-red-900/40 border border-red-500/50 rounded-lg animate-pulse">
        <AlertTriangle className="w-5 h-5 text-red-400 flex-shrink-0" />
        <div className="flex-1">
          <span className="text-red-400 font-bold text-sm">PROHIBITED TRADING DAY — </span>
          <span className="text-red-300 text-sm">{risk.activeToday.map(e => e.name).join(', ')}</span>
          <span className="text-red-400/70 text-xs ml-2">Action: {risk.activeToday[0]?.action}</span>
        </div>
      </div>
    );
  }

  // 2. TOMORROW IS PROHIBITED
  if (risk.tomorrowProhibited && risk.tomorrowEvents?.length > 0) {
    banners.push(
      <div key="tomorrow" className="flex items-center gap-3 p-3 bg-amber-900/20 border border-amber-500/30 rounded-lg">
        <Bell className="w-5 h-5 text-amber-400 flex-shrink-0" />
        <div className="flex-1">
          <span className="text-amber-400 font-bold text-sm">TOMORROW: </span>
          <span className="text-amber-300 text-sm">{risk.tomorrowEvents.map(e => e.name).join(', ')}</span>
          <span className="text-amber-400/70 text-xs ml-2">— {risk.tomorrowEvents[0]?.action}</span>
        </div>
      </div>
    );
  }

  // 3. PORTFOLIO BREACHED
  if (risk.portfolioBreached) {
    banners.push(
      <div key="breach" className="flex items-center gap-3 p-3 bg-red-900/30 border border-red-500/40 rounded-lg">
        <TrendingDown className="w-5 h-5 text-red-400 flex-shrink-0" />
        <span className="text-red-400 font-bold text-sm">PORTFOLIO PROTECTION LINE BREACHED — DD: {risk.portfolioDD?.toFixed(2)}%</span>
        {risk.criticalAlerts > 0 && <span className="text-red-300 text-xs ml-2">({risk.criticalAlerts} critical alerts)</span>}
      </div>
    );
  }

  // 4. UPCOMING EVENT (within 3 days)
  if (!risk.todayProhibited && !risk.tomorrowProhibited && risk.nextEvent && risk.nextEvent.days_away <= 3) {
    banners.push(
      <div key="upcoming" className="flex items-center gap-3 p-2 bg-slate-800/50 border border-slate-700/30 rounded-lg">
        <Calendar className="w-4 h-4 text-slate-400 flex-shrink-0" />
        <span className="text-slate-400 text-xs">Upcoming: <strong className="text-amber-400">{risk.nextEvent.name}</strong> in {risk.nextEvent.days_away}d — {risk.nextEvent.action}</span>
      </div>
    );
  }

  if (banners.length === 0) return null;

  return <div className="space-y-2 mb-4">{banners}</div>;
}

/**
 * Compact risk badge for account/manager cards.
 */
export function RiskGradeBadge({ drawdownPct, size = 'sm' }) {
  const dd = Math.abs(drawdownPct || 0);
  let label, color, bg;
  if (dd >= 10) { label = 'CRITICAL'; color = '#ef4444'; bg = 'rgba(239,68,68,0.1)'; }
  else if (dd >= 5) { label = 'HALT'; color = '#f59e0b'; bg = 'rgba(245,158,11,0.1)'; }
  else if (dd >= 3) { label = 'WARN'; color = '#eab308'; bg = 'rgba(234,179,8,0.1)'; }
  else { label = 'OK'; color = '#10b981'; bg = 'rgba(16,185,129,0.1)'; }

  const s = size === 'lg' ? { fontSize: '12px', padding: '3px 10px' } : { fontSize: '9px', padding: '1px 6px' };
  return (
    <span style={{ ...s, color, background: bg, border: `1px solid ${color}30`, borderRadius: '4px', fontWeight: 'bold', display: 'inline-flex', alignItems: 'center', gap: '3px' }}>
      <span style={{ width: size === 'lg' ? 6 : 4, height: size === 'lg' ? 6 : 4, borderRadius: '50%', background: color, display: 'inline-block' }} />
      {label}
    </span>
  );
}

/**
 * Next prohibited event countdown — small inline widget.
 */
export function NextEventCountdown({ risk }) {
  if (!risk?.nextEvent) return null;
  const ev = risk.nextEvent;
  const urgent = ev.days_away <= 1;
  return (
    <div className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs ${urgent ? 'bg-red-900/20 border border-red-500/30' : 'bg-slate-800/50 border border-slate-700/30'}`}>
      <Bell className={`w-3 h-3 ${urgent ? 'text-red-400' : 'text-amber-400'}`} />
      <span className={urgent ? 'text-red-400' : 'text-slate-400'}>
        <strong className={urgent ? 'text-red-300' : 'text-amber-400'}>{ev.name}</strong> in {ev.days_away}d
      </span>
    </div>
  );
}
