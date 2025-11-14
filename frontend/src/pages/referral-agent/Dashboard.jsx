import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Users, UserCheck, DollarSign, TrendingUp } from 'lucide-react';
import Layout from '../../components/referral-agent/Layout';
import StatsCard from '../../components/referral-agent/StatsCard';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Alert, AlertDescription } from '../../components/ui/alert';
import referralAgentApi from '../../services/referralAgentApi';
import StatusBadge from '../../components/referral-agent/StatusBadge';
import { format } from 'date-fns';

const Dashboard = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [dashboardData, setDashboardData] = useState(null);

  useEffect(() => {
    fetchDashboard();
  }, []);

  const fetchDashboard = async () => {
    try {
      setLoading(true);
      const response = await referralAgentApi.getDashboard();
      if (response.success) {
        setDashboardData(response.data);
      } else {
        setError('Failed to load dashboard data');
      }
    } catch (err) {
      console.error('Dashboard error:', err);
      setError('An error occurred loading your dashboard');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      {error && (
        <Alert variant="destructive" className="mb-6 bg-red-950 border-red-900 text-red-200">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4 mb-6">
        <div onClick={() => navigate('/referral-agent/leads')}>
          <StatsCard
            title="Total Leads"
            value={dashboardData?.stats.totalLeads || 0}
            icon={Users}
            loading={loading}
          />
        </div>
        <div onClick={() => navigate('/referral-agent/clients')}>
          <StatsCard
            title="Active Clients"
            value={dashboardData?.stats.activeClients || 0}
            icon={UserCheck}
            loading={loading}
          />
        </div>
        <div onClick={() => navigate('/referral-agent/commissions')}>
          <StatsCard
            title="Total Commissions"
            value={`$${(dashboardData?.stats.totalCommissionsEarned || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
            icon={DollarSign}
            loading={loading}
          />
        </div>
        <StatsCard
          title="Conversion Rate"
          value={`${dashboardData?.stats.conversionRate || 0}%`}
          icon={TrendingUp}
          loading={loading}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Leads */}
        <Card className="bg-slate-900 border-slate-800">
          <CardHeader>
            <CardTitle className="text-white">Recent Leads</CardTitle>
            <CardDescription className="text-slate-400">Your most recent lead activities</CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="space-y-3">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="animate-pulse">
                    <div className="h-16 bg-slate-800 rounded"></div>
                  </div>
                ))}
              </div>
            ) : dashboardData?.recentLeads && dashboardData.recentLeads.length > 0 ? (
              <div className="space-y-4">
                {dashboardData.recentLeads.slice(0, 5).map((lead) => (
                  <div key={lead.id} className="flex items-center justify-between py-2 border-b border-slate-800 last:border-0 hover:bg-slate-800 cursor-pointer rounded px-2 transition-colors" onClick={() => navigate(`/referral-agent/leads/${lead.id}`)}>
                    <div className="flex-1">
                      <p className="font-medium text-white">{lead.name || lead.email}</p>
                      <p className="text-sm text-slate-400">{lead.email}</p>
                    </div>
                    <StatusBadge status={lead.crmStatus} />
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-slate-500 text-center py-8">No leads yet</p>
            )}
          </CardContent>
        </Card>

        {/* Upcoming Follow-ups */}
        <Card className="bg-slate-900 border-slate-800">
          <CardHeader>
            <CardTitle className="text-white">Upcoming Follow-ups</CardTitle>
            <CardDescription className="text-slate-400">Leads that need your attention</CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="space-y-3">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="animate-pulse">
                    <div className="h-16 bg-slate-800 rounded"></div>
                  </div>
                ))}
              </div>
            ) : dashboardData?.upcomingFollowUps && dashboardData.upcomingFollowUps.length > 0 ? (
              <div className="space-y-4">
                {dashboardData.upcomingFollowUps.map((lead) => (
                  <div key={lead.id} className="flex items-center justify-between py-2 border-b border-slate-800 last:border-0 hover:bg-slate-800 cursor-pointer rounded px-2 transition-colors" onClick={() => navigate(`/referral-agent/leads/${lead.id}`)}>
                    <div className="flex-1">
                      <p className="font-medium text-white">{lead.name || lead.email}</p>
                      <p className="text-sm text-cyan-400">
                        {lead.nextFollowUp && format(new Date(lead.nextFollowUp), 'MMM d, yyyy')}
                      </p>
                    </div>
                    <StatusBadge status={lead.crmStatus} />
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-slate-500 text-center py-8">No follow-ups scheduled</p>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Pipeline Overview */}
      <Card className="mt-6 bg-slate-900 border-slate-800">
        <CardHeader>
          <CardTitle className="text-white">Lead Pipeline</CardTitle>
          <CardDescription className="text-slate-400">Distribution of leads by status</CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="h-32 bg-slate-800 rounded animate-pulse"></div>
          ) : dashboardData?.pipelineBreakdown ? (
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              {Object.entries(dashboardData.pipelineBreakdown).map(([status, count]) => (
                <div key={status} className="text-center p-4 bg-slate-800 rounded-lg hover:bg-slate-700 cursor-pointer transition-colors" onClick={() => navigate(`/referral-agent/leads?status=${status}`)}>
                  <p className="text-2xl font-bold text-white mb-2">{count}</p>
                  <StatusBadge status={status} />
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-slate-500 text-center py-8">No pipeline data</p>
          )}
        </CardContent>
      </Card>
    </Layout>
  );
};

export default Dashboard;
