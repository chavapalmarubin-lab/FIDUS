/**
 * FIDUS Wealth Calendar Component
 * 
 * Visualizes fund health, cash flow projections, and performance requirements
 * 
 * Features:
 * - Fund Health Gauge (Current Revenue vs Obligations)
 * - Monthly Cash Flow Timeline
 * - Performance Gap Analysis
 * - Upcoming Milestones
 */

import React, { useState, useEffect } from 'react';
import {
  Calendar,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  DollarSign,
  Clock,
  CheckCircle2,
  XCircle,
  ArrowRight,
  Activity,
  Target,
  Wallet,
  PiggyBank,
  AlertCircle,
  ChevronRight
} from 'lucide-react';

// Format currency helper
const formatCurrency = (value) => {
  if (value === null || value === undefined) return '$0.00';
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value);
};

// Format date helper
const formatDate = (dateStr) => {
  if (!dateStr) return 'N/A';
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
};

// Health status calculator
const getHealthStatus = (revenue, obligations) => {
  if (!obligations || obligations === 0) return { status: 'healthy', color: 'emerald', label: 'Healthy' };
  const ratio = revenue / obligations;
  if (ratio >= 1.5) return { status: 'excellent', color: 'emerald', label: 'Excellent' };
  if (ratio >= 1.0) return { status: 'healthy', color: 'green', label: 'Healthy' };
  if (ratio >= 0.7) return { status: 'warning', color: 'yellow', label: 'Warning' };
  if (ratio >= 0.5) return { status: 'critical', color: 'orange', label: 'Critical' };
  return { status: 'danger', color: 'red', label: 'Danger' };
};

const WealthCalendar = ({ calendarData, clientMoney, totalEquity }) => {
  const [selectedMonth, setSelectedMonth] = useState(null);
  const [showAllMonths, setShowAllMonths] = useState(false);

  if (!calendarData) {
    return (
      <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700/50">
        <div className="flex items-center justify-center h-48">
          <div className="text-slate-400">Loading Wealth Calendar...</div>
        </div>
      </div>
    );
  }

  const {
    current_revenue = 0,
    total_equity = 0,
    client_money = 0,
    monthly_obligations = {},
    milestones = {},
    summary = {}
  } = calendarData;

  // Use values from backend if provided, otherwise use props
  const actualClientMoney = client_money || clientMoney || 380536.05;
  const actualTotalEquity = total_equity || totalEquity || (actualClientMoney + current_revenue);
  const fundAssets = summary.fund_assets || actualTotalEquity;

  const sortedMonths = Object.keys(monthly_obligations).sort();
  const displayMonths = showAllMonths ? sortedMonths : sortedMonths.slice(0, 6);
  
  // Calculate totals
  const totalFutureObligations = summary.total_future_obligations || 0;
  const monthsUntilShortfall = summary.months_until_shortfall || 'N/A';
  const finalBalance = summary.final_balance || 0;
  
  // Calculate health metrics
  const next3MonthsObligations = sortedMonths.slice(0, 3).reduce((sum, month) => {
    return sum + (monthly_obligations[month]?.total_due || 0);
  }, 0);
  
  const healthStatus = getHealthStatus(current_revenue, next3MonthsObligations);
  const coverageRatio = next3MonthsObligations > 0 ? (current_revenue / next3MonthsObligations * 100).toFixed(1) : 100;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-gradient-to-br from-cyan-500/20 to-blue-500/20 rounded-lg">
            <Calendar className="w-6 h-6 text-cyan-400" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white">Wealth Calendar</h2>
            <p className="text-sm text-slate-400">Fund health & cash flow projections</p>
          </div>
        </div>
        <div className={`px-4 py-2 rounded-full bg-${healthStatus.color}-500/20 border border-${healthStatus.color}-500/30`}>
          <span className={`text-${healthStatus.color}-400 font-semibold flex items-center gap-2`}>
            {healthStatus.status === 'excellent' || healthStatus.status === 'healthy' ? (
              <CheckCircle2 className="w-4 h-4" />
            ) : (
              <AlertTriangle className="w-4 h-4" />
            )}
            Fund Status: {healthStatus.label}
          </span>
        </div>
      </div>

      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Current Revenue */}
        <div className="bg-gradient-to-br from-emerald-500/10 to-green-500/10 rounded-xl p-4 border border-emerald-500/20">
          <div className="flex items-center justify-between mb-2">
            <span className="text-slate-400 text-sm">Fund Revenue (P&L)</span>
            <Wallet className="w-5 h-5 text-emerald-400" />
          </div>
          <p className="text-2xl font-bold text-emerald-400">{formatCurrency(current_revenue)}</p>
          <p className="text-xs text-slate-500 mt-1">Available to pay interest</p>
        </div>

        {/* Client Money (Principal - Cannot use for interest) */}
        <div className="bg-gradient-to-br from-blue-500/10 to-cyan-500/10 rounded-xl p-4 border border-blue-500/20">
          <div className="flex items-center justify-between mb-2">
            <span className="text-slate-400 text-sm">Client Money</span>
            <PiggyBank className="w-5 h-5 text-blue-400" />
          </div>
          <p className="text-2xl font-bold text-blue-400">{formatCurrency(actualClientMoney)}</p>
          <p className="text-xs text-slate-500 mt-1">Principal (not for interest)</p>
        </div>

        {/* Coverage Ratio */}
        <div className={`bg-gradient-to-br from-${healthStatus.color}-500/10 to-${healthStatus.color}-600/10 rounded-xl p-4 border border-${healthStatus.color}-500/20`}>
          <div className="flex items-center justify-between mb-2">
            <span className="text-slate-400 text-sm">3-Month Coverage</span>
            <Target className="w-5 h-5 text-yellow-400" />
          </div>
          <p className={`text-2xl font-bold text-${healthStatus.color}-400`}>{coverageRatio}%</p>
          <p className="text-xs text-slate-500 mt-1">Revenue vs upcoming obligations</p>
        </div>

        {/* Performance Gap */}
        <div className={`bg-gradient-to-br ${finalBalance >= 0 ? 'from-green-500/10 to-emerald-500/10' : 'from-red-500/10 to-orange-500/10'} rounded-xl p-4 border ${finalBalance >= 0 ? 'border-green-500/20' : 'border-red-500/20'}`}>
          <div className="flex items-center justify-between mb-2">
            <span className="text-slate-400 text-sm">Projected Balance</span>
            {finalBalance >= 0 ? (
              <TrendingUp className="w-5 h-5 text-green-400" />
            ) : (
              <TrendingDown className="w-5 h-5 text-red-400" />
            )}
          </div>
          <p className={`text-2xl font-bold ${finalBalance >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {formatCurrency(Math.abs(finalBalance))}
          </p>
          <p className="text-xs text-slate-500 mt-1">
            {finalBalance >= 0 ? 'Surplus at contract end' : 'Shortfall projected'}
          </p>
        </div>
      </div>

      {/* Upcoming Milestones */}
      <div className="bg-slate-800/50 rounded-xl p-5 border border-slate-700/50">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <Clock className="w-5 h-5 text-cyan-400" />
          Upcoming Milestones
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Next Payment */}
          {milestones.next_payment && (
            <div className="bg-slate-700/30 rounded-lg p-4 border border-slate-600/30">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-2 h-2 bg-cyan-400 rounded-full animate-pulse"></div>
                <span className="text-slate-400 text-sm">Next Payment</span>
              </div>
              <p className="text-white font-semibold">{milestones.next_payment.date}</p>
              <p className="text-cyan-400 font-bold text-lg">{formatCurrency(milestones.next_payment.amount)}</p>
              <p className="text-xs text-slate-500 mt-1">
                {milestones.next_payment.days_away} days away
              </p>
            </div>
          )}

          {/* First Large Payment */}
          {milestones.first_large_payment && (
            <div className="bg-slate-700/30 rounded-lg p-4 border border-orange-500/30">
              <div className="flex items-center gap-2 mb-2">
                <AlertCircle className="w-4 h-4 text-orange-400" />
                <span className="text-slate-400 text-sm">First Large Payment</span>
              </div>
              <p className="text-white font-semibold">{milestones.first_large_payment.date}</p>
              <p className="text-orange-400 font-bold text-lg">{formatCurrency(milestones.first_large_payment.amount)}</p>
              <p className="text-xs text-slate-500 mt-1">
                {milestones.first_large_payment.days_away} days away
              </p>
            </div>
          )}

          {/* Contract End */}
          {milestones.contract_end && (
            <div className="bg-slate-700/30 rounded-lg p-4 border border-purple-500/30">
              <div className="flex items-center gap-2 mb-2">
                <Target className="w-4 h-4 text-purple-400" />
                <span className="text-slate-400 text-sm">Contract End</span>
              </div>
              <p className="text-white font-semibold">{milestones.contract_end.date}</p>
              <p className="text-purple-400 font-bold text-lg">{formatCurrency(milestones.contract_end.amount)}</p>
              <p className="text-xs text-slate-500 mt-1">
                {milestones.contract_end.days_away} days away
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Monthly Cash Flow Timeline */}
      <div className="bg-slate-800/50 rounded-xl p-5 border border-slate-700/50">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white flex items-center gap-2">
            <Activity className="w-5 h-5 text-cyan-400" />
            Monthly Cash Flow Timeline
          </h3>
          <button
            onClick={() => setShowAllMonths(!showAllMonths)}
            className="text-sm text-cyan-400 hover:text-cyan-300 flex items-center gap-1"
          >
            {showAllMonths ? 'Show Less' : `Show All (${sortedMonths.length} months)`}
            <ChevronRight className={`w-4 h-4 transition-transform ${showAllMonths ? 'rotate-90' : ''}`} />
          </button>
        </div>

        {/* Timeline Grid */}
        <div className="space-y-3">
          {displayMonths.map((monthKey, index) => {
            const monthData = monthly_obligations[monthKey];
            const totalDue = monthData?.total_due || 0;
            const coreInterest = monthData?.core_interest || 0;
            const dynamicInterest = monthData?.dynamic_interest || 0;
            const balanceInterest = monthData?.balance_interest || 0;
            const referralComm = monthData?.referral_commissions || 0;
            const principalRedemptions = monthData?.principal_redemptions || 0;
            const performanceFees = monthData?.performance_fees || 0;
            
            // Determine if this is a high-obligation month
            const isHighObligation = totalDue > 5000;
            const isSelected = selectedMonth === monthKey;
            
            // Parse month for display
            const [year, month] = monthKey.split('-');
            const monthName = new Date(year, parseInt(month) - 1).toLocaleString('default', { month: 'short' });

            return (
              <div
                key={monthKey}
                className={`rounded-lg border transition-all cursor-pointer ${
                  isSelected 
                    ? 'bg-slate-700/50 border-cyan-500/50' 
                    : isHighObligation 
                      ? 'bg-orange-500/5 border-orange-500/30 hover:bg-orange-500/10' 
                      : 'bg-slate-700/20 border-slate-600/30 hover:bg-slate-700/30'
                }`}
                onClick={() => setSelectedMonth(isSelected ? null : monthKey)}
              >
                <div className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      {/* Month Badge */}
                      <div className={`w-14 h-14 rounded-lg flex flex-col items-center justify-center ${
                        isHighObligation ? 'bg-orange-500/20' : 'bg-slate-600/50'
                      }`}>
                        <span className="text-xs text-slate-400">{year}</span>
                        <span className={`text-lg font-bold ${isHighObligation ? 'text-orange-400' : 'text-white'}`}>
                          {monthName}
                        </span>
                      </div>
                      
                      {/* Summary */}
                      <div>
                        <p className={`font-semibold ${isHighObligation ? 'text-orange-400' : 'text-white'}`}>
                          {formatCurrency(totalDue)}
                        </p>
                        <p className="text-sm text-slate-400">
                          {monthData?.clients_breakdown?.length || 0} client payments
                        </p>
                      </div>
                    </div>

                    {/* Quick Breakdown */}
                    <div className="hidden md:flex items-center gap-6 text-sm">
                      {coreInterest > 0 && (
                        <div className="text-center">
                          <p className="text-blue-400 font-medium">{formatCurrency(coreInterest)}</p>
                          <p className="text-xs text-slate-500">CORE</p>
                        </div>
                      )}
                      {balanceInterest > 0 && (
                        <div className="text-center">
                          <p className="text-purple-400 font-medium">{formatCurrency(balanceInterest)}</p>
                          <p className="text-xs text-slate-500">BALANCE</p>
                        </div>
                      )}
                      {dynamicInterest > 0 && (
                        <div className="text-center">
                          <p className="text-emerald-400 font-medium">{formatCurrency(dynamicInterest)}</p>
                          <p className="text-xs text-slate-500">DYNAMIC</p>
                        </div>
                      )}
                      {referralComm > 0 && (
                        <div className="text-center">
                          <p className="text-green-400 font-medium">{formatCurrency(referralComm)}</p>
                          <p className="text-xs text-slate-500">Referrals</p>
                        </div>
                      )}
                      {principalRedemptions > 0 && (
                        <div className="text-center">
                          <p className="text-red-400 font-medium">{formatCurrency(principalRedemptions)}</p>
                          <p className="text-xs text-slate-500">Principal</p>
                        </div>
                      )}
                    </div>

                    <ChevronRight className={`w-5 h-5 text-slate-400 transition-transform ${isSelected ? 'rotate-90' : ''}`} />
                  </div>

                  {/* Expanded Details */}
                  {isSelected && monthData?.clients_breakdown && (
                    <div className="mt-4 pt-4 border-t border-slate-600/50">
                      <p className="text-sm font-semibold text-cyan-400 mb-3">👤 Client Breakdown</p>
                      <div className="space-y-2">
                        {monthData.clients_breakdown.map((client, idx) => (
                          <div key={idx} className="bg-slate-800/50 rounded-lg p-3">
                            <div className="flex justify-between items-center">
                              <span className="text-white font-medium">{client.client_name}</span>
                              <span className="text-cyan-400 font-semibold">
                                {formatCurrency(client.total_interest + (client.principal_return || 0))}
                              </span>
                            </div>
                            {client.payments && client.payments.length > 0 && (
                              <div className="mt-2 space-y-1">
                                {client.payments.map((payment, pIdx) => (
                                  <div key={pIdx} className="flex justify-between text-xs">
                                    <span className="text-slate-400">
                                      {payment.fund_type || payment.fund_code} {payment.type === 'final_payment' ? '(Final)' : ''}
                                    </span>
                                    <span className={`${
                                      (payment.fund_type || payment.fund_code) === 'CORE' ? 'text-blue-400' :
                                      (payment.fund_type || payment.fund_code) === 'BALANCE' ? 'text-purple-400' :
                                      'text-emerald-400'
                                    }`}>
                                      {formatCurrency(payment.interest || payment.amount)}
                                    </span>
                                  </div>
                                ))}
                              </div>
                            )}
                            {client.referral_commissions && client.referral_commissions.length > 0 && (
                              <div className="mt-2 pt-2 border-t border-slate-600/30">
                                {client.referral_commissions.map((comm, cIdx) => (
                                  <div key={cIdx} className="flex justify-between text-xs">
                                    <span className="text-green-400/80">💰 {comm.agent_name}</span>
                                    <span className="text-green-400">{formatCurrency(comm.amount)}</span>
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Performance Requirements Alert */}
      {finalBalance < 0 && (
        <div className="bg-red-500/10 rounded-xl p-5 border border-red-500/30">
          <div className="flex items-start gap-4">
            <div className="p-2 bg-red-500/20 rounded-lg">
              <AlertTriangle className="w-6 h-6 text-red-400" />
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-red-400 mb-2">Interest Payment Gap Alert</h3>
              <p className="text-slate-300 mb-4">
                Based on current projections, the fund needs to generate an additional{' '}
                <span className="font-bold text-red-400">{formatCurrency(Math.abs(finalBalance))}</span>{' '}
                in trading profits to cover all interest obligations. Client money (principal) cannot be used to pay interest.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                <div className="bg-slate-800/50 rounded-lg p-3">
                  <p className="text-slate-400">Total Interest Obligations</p>
                  <p className="text-white font-bold">{formatCurrency(totalFutureObligations)}</p>
                  <p className="text-xs text-slate-500">Must be paid from revenue</p>
                </div>
                <div className="bg-slate-800/50 rounded-lg p-3">
                  <p className="text-slate-400">Available Revenue (P&L)</p>
                  <p className={`font-bold ${current_revenue >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                    {formatCurrency(current_revenue)}
                  </p>
                  <p className="text-xs text-slate-500">Current trading profits</p>
                </div>
                <div className="bg-slate-800/50 rounded-lg p-3">
                  <p className="text-slate-400">Interest Gap</p>
                  <p className="text-red-400 font-bold">{formatCurrency(Math.abs(finalBalance))}</p>
                  <p className="text-xs text-slate-500">Additional revenue needed</p>
                </div>
              </div>
              <div className="mt-4 bg-blue-500/10 rounded-lg p-3 border border-blue-500/20">
                <p className="text-sm text-blue-300">
                  <strong>Note:</strong> Client Money ({formatCurrency(actualClientMoney)}) is held as principal and will be returned at contract end. 
                  It cannot be used to pay interest obligations - only trading revenue can cover those costs.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Summary Footer */}
      <div className="bg-gradient-to-r from-slate-800/80 to-slate-700/80 rounded-xl p-4 border border-slate-600/50">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <Activity className="w-5 h-5 text-cyan-400" />
            <span className="text-slate-300">
              Total Future Obligations:{' '}
              <span className="font-bold text-white">{formatCurrency(totalFutureObligations)}</span>
            </span>
          </div>
          <div className="flex items-center gap-3">
            <Clock className="w-5 h-5 text-yellow-400" />
            <span className="text-slate-300">
              Time to Shortfall:{' '}
              <span className={`font-bold ${monthsUntilShortfall < 12 ? 'text-orange-400' : 'text-green-400'}`}>
                {typeof monthsUntilShortfall === 'number' ? `${monthsUntilShortfall} months` : monthsUntilShortfall}
              </span>
            </span>
          </div>
          <div className="flex items-center gap-3">
            <Target className="w-5 h-5 text-purple-400" />
            <span className="text-slate-300">
              Tracking:{' '}
              <span className="font-bold">{sortedMonths.length} months</span>
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WealthCalendar;
