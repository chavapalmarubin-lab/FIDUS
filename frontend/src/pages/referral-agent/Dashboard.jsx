import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Users, UserCheck, DollarSign, TrendingUp, PieChart, Calendar, Plus } from 'lucide-react';
import Layout from '../../components/referral-agent/Layout';
import StatsCard from '../../components/referral-agent/StatsCard';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Alert, AlertDescription } from '../../components/ui/alert';
import referralAgentApi from '../../services/referralAgentApi';
import StatusBadge from '../../components/referral-agent/StatusBadge';
import { format } from 'date-fns';
import InvestmentSimulator from '../../components/InvestmentSimulator';

const Dashboard = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [dashboardData, setDashboardData] = useState(null);
  const [showSimulator, setShowSimulator] = useState(false);

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
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">Dashboard</h1>
            <p className="text-slate-400">Welcome back! Here's your referral performance overview</p>
          </div>
          <Button
            onClick={() => setShowSimulator(!showSimulator)}
            className="bg-cyan-600 hover:bg-cyan-700 text-white"
          >
            <PieChart className="h-4 w-4 mr-2" />
            {showSimulator ? 'Hide' : 'Show'} Investment Calculator
          </Button>
        </div>

        {error && (
          <Alert variant="destructive" className="bg-red-950 border-red-900 text-red-200">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Investment Simulator */}
        {showSimulator && (
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader>
              <CardTitle className="text-white">Investment Simulator</CardTitle>
              <CardDescription className="text-slate-400">
                Show prospects how their investment can grow with FIDUS funds
              </CardDescription>
            </CardHeader>
            <CardContent>
              <InvestmentSimulator />
            </CardContent>
          </Card>
        )}

        {/* Stats Grid */}
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
          <div onClick={() => navigate('/referral-agent/leads')} className="cursor-pointer transform hover:scale-105 transition-transform">
            <Card className="bg-gradient-to-br from-blue-600 to-blue-800 border-blue-700 overflow-hidden">
              <CardContent className="p-6">
                {loading ? (
                  <div className="animate-pulse">
                    <div className="h-4 w-20 bg-blue-400/30 rounded mb-3"></div>
                    <div className="h-8 w-16 bg-blue-400/30 rounded"></div>
                  </div>
                ) : (
                  <>
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <p className="text-blue-100 text-sm font-medium mb-1">Total Leads</p>
                        <p className="text-4xl font-bold text-white">{dashboardData?.stats.totalLeads || 0}</p>
                      </div>
                      <Users className="h-10 w-10 text-blue-200/50" />
                    </div>
                  </>
                )}
              </CardContent>
            </Card>
          </div>
          <div onClick={() => navigate('/referral-agent/clients')} className="cursor-pointer transform hover:scale-105 transition-transform">
            <Card className="bg-gradient-to-br from-green-600 to-green-800 border-green-700 overflow-hidden">
              <CardContent className="p-6">
                {loading ? (
                  <div className="animate-pulse">
                    <div className="h-4 w-20 bg-green-400/30 rounded mb-3"></div>
                    <div className="h-8 w-16 bg-green-400/30 rounded"></div>
                  </div>
                ) : (
                  <>
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <p className="text-green-100 text-sm font-medium mb-1">Active Clients</p>
                        <p className="text-4xl font-bold text-white">{dashboardData?.stats.activeClients || 0}</p>
                      </div>
                      <UserCheck className="h-10 w-10 text-green-200/50" />
                    </div>
                  </>
                )}
              </CardContent>
            </Card>
          </div>
          <div onClick={() => navigate('/referral-agent/commissions')} className="cursor-pointer transform hover:scale-105 transition-transform">
            <Card className="bg-gradient-to-br from-cyan-600 to-cyan-800 border-cyan-700 overflow-hidden">
              <CardContent className="p-6">
                {loading ? (
                  <div className="animate-pulse">
                    <div className="h-4 w-20 bg-cyan-400/30 rounded mb-3"></div>
                    <div className="h-8 w-24 bg-cyan-400/30 rounded"></div>
                  </div>
                ) : (
                  <>
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <p className="text-cyan-100 text-sm font-medium mb-1">Total Commissions</p>
                        <p className="text-4xl font-bold text-white">
                          ${(dashboardData?.stats.totalCommissionsEarned || 0).toLocaleString('en-US', { 
                            minimumFractionDigits: 2, 
                            maximumFractionDigits: 2 
                          })}
                        </p>
                      </div>
                      <DollarSign className="h-10 w-10 text-cyan-200/50" />
                    </div>
                  </>
                )}
              </CardContent>
            </Card>
          </div>
          <Card className="bg-gradient-to-br from-purple-600 to-purple-800 border-purple-700 overflow-hidden">
            <CardContent className="p-6">
              {loading ? (
                <div className="animate-pulse">
                  <div className="h-4 w-20 bg-purple-400/30 rounded mb-3"></div>
                  <div className="h-8 w-16 bg-purple-400/30 rounded"></div>
                </div>
              ) : (
                <>
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <p className="text-purple-100 text-sm font-medium mb-1">Conversion Rate</p>
                      <p className="text-4xl font-bold text-white">{dashboardData?.stats.conversionRate || 0}%</p>
                    </div>
                    <TrendingUp className="h-10 w-10 text-purple-200/50" />
                  </div>
                </>
              )}
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Pipeline Overview */}
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader>
              <CardTitle className="text-white flex items-center justify-between">
                <span className="flex items-center gap-2">
                  <PieChart className="h-5 w-5 text-cyan-400" />
                  Sales Pipeline
                </span>
                <Button
                  onClick={() => navigate('/referral-agent/leads')}
                  variant="ghost"
                  size="sm"
                  className="text-cyan-400 hover:text-cyan-300 hover:bg-slate-800"
                >
                  View All
                </Button>
              </CardTitle>
              <CardDescription className="text-slate-400">Lead status breakdown</CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="space-y-3">
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="animate-pulse">
                      <div className="h-12 bg-slate-800 rounded"></div>
                    </div>
                  ))}
                </div>
              ) : Object.keys(dashboardData?.pipelineBreakdown || {}).length > 0 ? (
                <div className="space-y-3">
                  {Object.entries(dashboardData.pipelineBreakdown).map(([status, count]) => {
                    const total = Object.values(dashboardData.pipelineBreakdown).reduce((a, b) => a + b, 0);
                    const percentage = total > 0 ? Math.round((count / total) * 100) : 0;
                    return (
                      <div key={status} className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span className="text-slate-300 capitalize">{status.replace('_', ' ')}</span>
                          <span className="text-slate-400">{count} ({percentage}%)</span>
                        </div>
                        <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-cyan-600 rounded-full transition-all"
                            style={{ width: `${percentage}%` }}
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="text-center py-8">
                  <PieChart className="h-12 w-12 text-slate-600 mx-auto mb-3" />
                  <p className="text-slate-400 mb-4">No leads in pipeline yet</p>
                  <Button
                    onClick={() => navigate('/referral-agent/profile')}
                    className="bg-cyan-600 hover:bg-cyan-700 text-white"
                    size="sm"
                  >
                    <Plus className="h-4 w-4 mr-2" />
                    Get Your Referral Link
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Recent Activity */}
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Calendar className="h-5 w-5 text-cyan-400" />
                Recent Leads
              </CardTitle>
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
                <div className="space-y-3">
                  {dashboardData.recentLeads.slice(0, 5).map((lead) => (
                    <div
                      key={lead.id}
                      className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg border border-slate-700 hover:border-cyan-600/50 cursor-pointer transition-colors"
                      onClick={() => navigate(`/referral-agent/leads/${lead.id}`)}
                    >
                      <div className="flex-1">
                        <div className="text-white font-medium">{lead.email || 'No email'}</div>
                        <div className="text-sm text-slate-400">
                          {lead.registration_date ? format(new Date(lead.registration_date), 'MMM dd, yyyy') : 'Date unknown'}
                        </div>
                      </div>
                      <StatusBadge status={lead.crm_status || 'pending'} />
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <Users className="h-12 w-12 text-slate-600 mx-auto mb-3" />
                  <p className="text-slate-400 mb-4">No leads yet</p>
                  <p className="text-sm text-slate-500 mb-4">Share your referral link to start getting leads</p>
                  <Button
                    onClick={() => navigate('/referral-agent/profile')}
                    className="bg-cyan-600 hover:bg-cyan-700 text-white"
                    size="sm"
                  >
                    View Referral Link
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Upcoming Follow-ups */}
        {dashboardData?.upcomingFollowUps && dashboardData.upcomingFollowUps.length > 0 && (
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Calendar className="h-5 w-5 text-cyan-400" />
                Upcoming Follow-ups
              </CardTitle>
              <CardDescription className="text-slate-400">Leads that need your attention</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {dashboardData.upcomingFollowUps.map((lead) => (
                  <div
                    key={lead.id}
                    className="flex items-center justify-between p-4 bg-slate-800/50 rounded-lg border border-slate-700 hover:border-cyan-600/50 cursor-pointer transition-colors"
                    onClick={() => navigate(`/referral-agent/leads/${lead.id}`)}
                  >
                    <div className="flex-1">
                      <div className="text-white font-medium mb-1">{lead.email || 'No email'}</div>
                      <div className="text-sm text-slate-400">
                        Follow up: {lead.next_follow_up ? format(new Date(lead.next_follow_up), 'MMM dd, yyyy') : 'Not scheduled'}
                      </div>
                    </div>
                    <StatusBadge status={lead.crm_status || 'pending'} />
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Quick Actions */}
        <Card className="bg-gradient-to-br from-cyan-900/20 to-slate-900 border-cyan-800/50">
          <CardContent className="p-6">
            <div className="flex flex-col md:flex-row items-center justify-between gap-4">
              <div>
                <h3 className="text-xl font-bold text-white mb-2">Ready to grow your network?</h3>
                <p className="text-slate-300">Share your referral link and start earning commissions on every investment</p>
              </div>
              <Button
                onClick={() => navigate('/referral-agent/profile')}
                className="bg-cyan-600 hover:bg-cyan-700 text-white whitespace-nowrap"
                size="lg"
              >
                Get Referral Link
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </Layout>
  );
};

export default Dashboard;