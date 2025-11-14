import React, { useState, useEffect } from 'react';
import { DollarSign, Calendar, TrendingUp, Clock, CheckCircle2 } from 'lucide-react';
import Layout from '../../components/referral-agent/Layout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Alert, AlertDescription } from '../../components/ui/alert';
import { Badge } from '../../components/ui/badge';
import referralAgentApi from '../../services/referralAgentApi';
import { format, parseISO } from 'date-fns';

const Commissions = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [commissions, setCommissions] = useState([]);
  const [summary, setSummary] = useState(null);
  const [filter, setFilter] = useState('all'); // all, pending, paid

  useEffect(() => {
    fetchCommissions();
  }, []);

  const fetchCommissions = async () => {
    try {
      setLoading(true);
      const response = await referralAgentApi.getCommissions();
      if (response.success) {
        setCommissions(response.commissions || []);
        setSummary(response.summary || {});
      } else {
        setError('Failed to load commission data');
      }
    } catch (err) {
      console.error('Commissions error:', err);
      setError('An error occurred loading your commissions');
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      paid: { color: 'bg-green-500/20 text-green-400 border-green-500/50', label: 'Paid' },
      pending: { color: 'bg-blue-500/20 text-blue-400 border-blue-500/50', label: 'Pending' },
      ready_to_pay: { color: 'bg-cyan-500/20 text-cyan-400 border-cyan-500/50', label: 'Ready' },
      approved: { color: 'bg-purple-500/20 text-purple-400 border-purple-500/50', label: 'Approved' }
    };
    const config = statusConfig[status] || statusConfig.pending;
    return (
      <Badge className={`${config.color} border`}>
        {config.label}
      </Badge>
    );
  };

  const filteredCommissions = commissions.filter(c => {
    if (filter === 'all') return true;
    if (filter === 'paid') return c.status === 'paid';
    if (filter === 'pending') return ['pending', 'ready_to_pay', 'approved'].includes(c.status);
    return true;
  });

  // Group commissions by month for calendar view
  const groupedByMonth = {};
  filteredCommissions.forEach(commission => {
    if (!commission.paymentDate) return;
    const date = parseISO(commission.paymentDate);
    const monthKey = format(date, 'yyyy-MM');
    if (!groupedByMonth[monthKey]) {
      groupedByMonth[monthKey] = {
        month: format(date, 'MMMM yyyy'),
        commissions: []
      };
    }
    groupedByMonth[monthKey].commissions.push(commission);
  });

  const monthGroups = Object.values(groupedByMonth).sort((a, b) => b.month.localeCompare(a.month));

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Commission Schedule</h1>
          <p className="text-slate-400">Track your earnings and payment schedule</p>
        </div>

        {error && (
          <Alert variant="destructive" className="bg-red-950 border-red-900 text-red-200">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="bg-gradient-to-br from-slate-900 to-slate-800 border-slate-700">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-slate-400 flex items-center gap-2">
                <DollarSign className="h-4 w-4" />
                Total Earned
              </CardTitle>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="h-8 w-32 bg-slate-700 animate-pulse rounded"></div>
              ) : (
                <div className="text-3xl font-bold text-white">
                  ${(summary?.totalEarned || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </div>
              )}
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-green-900/20 to-slate-900 border-green-700/50">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-slate-400 flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 text-green-400" />
                Total Paid
              </CardTitle>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="h-8 w-32 bg-slate-700 animate-pulse rounded"></div>
              ) : (
                <div className="text-3xl font-bold text-green-400">
                  ${(summary?.totalPaid || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </div>
              )}
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-cyan-900/20 to-slate-900 border-cyan-700/50">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-slate-400 flex items-center gap-2">
                <Clock className="h-4 w-4 text-cyan-400" />
                Pending
              </CardTitle>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="h-8 w-32 bg-slate-700 animate-pulse rounded"></div>
              ) : (
                <div className="text-3xl font-bold text-cyan-400">
                  ${(summary?.totalPending || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Filter Tabs */}
        <div className="flex gap-2 bg-slate-900 p-1 rounded-lg border border-slate-800 w-fit">
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              filter === 'all'
                ? 'bg-cyan-600 text-white'
                : 'text-slate-400 hover:text-white hover:bg-slate-800'
            }`}
          >
            All ({commissions.length})
          </button>
          <button
            onClick={() => setFilter('pending')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              filter === 'pending'
                ? 'bg-cyan-600 text-white'
                : 'text-slate-400 hover:text-white hover:bg-slate-800'
            }`}
          >
            Pending ({commissions.filter(c => ['pending', 'ready_to_pay', 'approved'].includes(c.status)).length})
          </button>
          <button
            onClick={() => setFilter('paid')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              filter === 'paid'
                ? 'bg-cyan-600 text-white'
                : 'text-slate-400 hover:text-white hover:bg-slate-800'
            }`}
          >
            Paid ({commissions.filter(c => c.status === 'paid').length})
          </button>
        </div>

        {/* Commission Calendar View */}
        {loading ? (
          <Card className="bg-slate-900 border-slate-800">
            <CardContent className="p-6">
              <div className="space-y-4">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="animate-pulse">
                    <div className="h-6 w-32 bg-slate-800 rounded mb-3"></div>
                    <div className="space-y-2">
                      <div className="h-20 bg-slate-800 rounded"></div>
                      <div className="h-20 bg-slate-800 rounded"></div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        ) : filteredCommissions.length === 0 ? (
          <Card className="bg-slate-900 border-slate-800">
            <CardContent className="p-12 text-center">
              <Calendar className="h-12 w-12 text-slate-600 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-white mb-2">No Commissions Yet</h3>
              <p className="text-slate-400">Your commission schedule will appear here once clients invest</p>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-6">
            {monthGroups.map((monthGroup, idx) => (
              <Card key={idx} className="bg-slate-900 border-slate-800">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <Calendar className="h-5 w-5 text-cyan-400" />
                    {monthGroup.month}
                  </CardTitle>
                  <CardDescription className="text-slate-400">
                    {monthGroup.commissions.length} payment{monthGroup.commissions.length !== 1 ? 's' : ''} •
                    ${monthGroup.commissions.reduce((sum, c) => sum + c.commissionAmount, 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {monthGroup.commissions.map((commission, commIdx) => (
                      <div
                        key={commIdx}
                        className="flex items-center justify-between p-4 bg-slate-800/50 rounded-lg border border-slate-700 hover:border-cyan-600/50 transition-colors"
                      >
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <span className="text-white font-medium">{commission.clientName}</span>
                            <Badge className="bg-slate-700 text-slate-300 border-slate-600">
                              {commission.fundType}
                            </Badge>
                            {getStatusBadge(commission.status)}
                          </div>
                          <div className="text-sm text-slate-400">
                            Payment #{commission.paymentNumber} • {commission.paymentDate ? format(parseISO(commission.paymentDate), 'MMM dd, yyyy') : 'Date TBD'}
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-xl font-bold text-cyan-400">
                            ${commission.commissionAmount.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </Layout>
  );
};

export default Commissions;