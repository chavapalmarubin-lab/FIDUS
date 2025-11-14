import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Users, Search, Filter, Plus, Mail, Phone, X } from 'lucide-react';
import Layout from '../../components/referral-agent/Layout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Input } from '../../components/ui/input';
import { Button } from '../../components/ui/button';
import { Alert, AlertDescription } from '../../components/ui/alert';
import { Badge } from '../../components/ui/badge';
import referralAgentApi from '../../services/referralAgentApi';
import StatusBadge from '../../components/referral-agent/StatusBadge';
import { format } from 'date-fns';

const Leads = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [leads, setLeads] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');

  useEffect(() => {
    fetchLeads();
  }, [statusFilter]);

  const fetchLeads = async () => {
    try {
      setLoading(true);
      const filters = {};
      if (statusFilter !== 'all') {
        filters.status = statusFilter;
      }
      const response = await referralAgentApi.getLeads(filters);
      if (response.success) {
        setLeads(response.leads || []);
      } else {
        setError('Failed to load leads');
      }
    } catch (err) {
      console.error('Leads error:', err);
      setError('An error occurred loading your leads');
    } finally {
      setLoading(false);
    }
  };

  const filteredLeads = leads.filter(lead => {
    if (!searchTerm) return true;
    const search = searchTerm.toLowerCase();
    return (
      (lead.email && lead.email.toLowerCase().includes(search)) ||
      (lead.name && lead.name.toLowerCase().includes(search)) ||
      (lead.phone && lead.phone.toLowerCase().includes(search))
    );
  });

  const statusCounts = {
    all: leads.length,
    pending: leads.filter(l => l.crmStatus === 'pending').length,
    contacted: leads.filter(l => l.crmStatus === 'contacted').length,
    qualified: leads.filter(l => l.crmStatus === 'qualified').length,
    converted: leads.filter(l => l.crmStatus === 'converted').length,
  };

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">Lead Management</h1>
            <p className="text-slate-400">Track and manage your prospects</p>
          </div>
          <Button
            onClick={() => navigate('/referral-agent/profile')}
            className="bg-cyan-600 hover:bg-cyan-700 text-white"
          >
            <Plus className="h-4 w-4 mr-2" />
            Get Referral Link
          </Button>
        </div>

        {error && (
          <Alert variant="destructive" className="bg-red-950 border-red-900 text-red-200">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Filters */}
        <Card className="bg-slate-900 border-slate-800">
          <CardContent className="p-4">
            <div className="flex flex-col md:flex-row gap-4">
              {/* Search */}
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
                  <Input
                    type="text"
                    placeholder="Search leads by email, name, or phone..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10 bg-slate-800 border-slate-700 text-white placeholder-slate-500"
                  />
                </div>
              </div>

              {/* Status Filter */}
              <div className="flex gap-2 bg-slate-800 p-1 rounded-lg">
                {['all', 'pending', 'contacted', 'qualified', 'converted'].map((status) => (
                  <button
                    key={status}
                    onClick={() => setStatusFilter(status)}
                    className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                      statusFilter === status
                        ? 'bg-cyan-600 text-white'
                        : 'text-slate-400 hover:text-white hover:bg-slate-700'
                    }`}
                  >
                    {status.charAt(0).toUpperCase() + status.slice(1)}
                    {statusCounts[status] > 0 && (
                      <Badge className="ml-2 bg-slate-700 text-white border-0">
                        {statusCounts[status]}
                      </Badge>
                    )}
                  </button>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Leads Grid */}
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[1, 2, 3].map((i) => (
              <Card key={i} className="bg-slate-900 border-slate-800">
                <CardContent className="p-6">
                  <div className="animate-pulse space-y-3">
                    <div className="h-6 bg-slate-800 rounded w-3/4"></div>
                    <div className="h-4 bg-slate-800 rounded w-1/2"></div>
                    <div className="h-4 bg-slate-800 rounded w-full"></div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : filteredLeads.length === 0 ? (
          <Card className="bg-slate-900 border-slate-800">
            <CardContent className="p-12 text-center">
              <Users className="h-16 w-16 text-slate-600 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-white mb-2">
                {searchTerm ? 'No Leads Found' : 'No Leads Yet'}
              </h3>
              <p className="text-slate-400 mb-6">
                {searchTerm
                  ? 'Try adjusting your search or filter'
                  : 'Share your referral link to start getting leads'}
              </p>
              {!searchTerm && (
                <Button
                  onClick={() => navigate('/referral-agent/profile')}
                  className="bg-cyan-600 hover:bg-cyan-700 text-white"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Get Your Referral Link
                </Button>
              )}
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredLeads.map((lead) => (
              <Card
                key={lead.id}
                className="bg-slate-900 border-slate-800 hover:border-cyan-600/50 transition-colors cursor-pointer"
                onClick={() => navigate(`/referral-agent/leads/${lead.id}`)}
              >
                <CardHeader>
                  <div className="flex justify-between items-start mb-2">
                    <CardTitle className="text-white text-lg">
                      {lead.email || 'No email'}
                    </CardTitle>
                    <StatusBadge status={lead.crmStatus || 'pending'} />
                  </div>
                  <CardDescription className="space-y-1">
                    {lead.name && (
                      <div className="text-slate-400 flex items-center gap-2">
                        <Users className="h-3 w-3" />
                        {lead.name}
                      </div>
                    )}
                    {lead.phone && (
                      <div className="text-slate-400 flex items-center gap-2">
                        <Phone className="h-3 w-3" />
                        {lead.phone}
                      </div>
                    )}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-400">Registered</span>
                      <span className="text-slate-300">
                        {lead.registrationDate
                          ? format(new Date(lead.registrationDate), 'MMM dd, yyyy')
                          : 'Unknown'}
                      </span>
                    </div>
                    {lead.lastContacted && (
                      <div className="flex justify-between text-sm">
                        <span className="text-slate-400">Last Contact</span>
                        <span className="text-slate-300">
                          {format(new Date(lead.lastContacted), 'MMM dd, yyyy')}
                        </span>
                      </div>
                    )}
                    {lead.nextFollowUp && (
                      <div className="flex justify-between text-sm">
                        <span className="text-slate-400">Follow Up</span>
                        <span className="text-cyan-400 font-medium">
                          {format(new Date(lead.nextFollowUp), 'MMM dd, yyyy')}
                        </span>
                      </div>
                    )}
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

export default Leads;