import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Building2, Users, DollarSign, Percent, Plus, Edit, Trash2, 
  ExternalLink, RefreshCw, Check, X, Eye, Settings,
  TrendingUp, UserPlus, Globe, Palette, FileText, PieChart
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';

const WhiteLabelDashboard = () => {
  const [companies, setCompanies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);
  const [selectedCompany, setSelectedCompany] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [commissionSplits, setCommissionSplits] = useState([]);
  const [viewMode, setViewMode] = useState('overview'); // overview, companies, analytics

  // Form state for creating new company
  const [newCompany, setNewCompany] = useState({
    company_name: '',
    company_code: '',
    contact_email: '',
    contact_phone: '',
    commission_split_company: 50,
    commission_split_agent: 50,
    primary_color: '#0ea5e9',
    secondary_color: '#1e293b'
  });
  const [creating, setCreating] = useState(false);

  const API_URL = process.env.REACT_APP_BACKEND_URL;

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [companiesRes, statsRes, splitsRes] = await Promise.all([
        fetch(`${API_URL}/api/franchise/companies`),
        fetch(`${API_URL}/api/franchise/dashboard/stats`),
        fetch(`${API_URL}/api/franchise/commission-splits`)
      ]);

      const companiesData = await companiesRes.json();
      const statsData = await statsRes.json();
      const splitsData = await splitsRes.json();

      if (companiesData.success) setCompanies(companiesData.companies);
      if (statsData.success) setStats(statsData.stats);
      if (splitsData.success) setCommissionSplits(splitsData.commission_splits);
    } catch (err) {
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  };

  const createCompany = async () => {
    setCreating(true);
    try {
      const response = await fetch(`${API_URL}/api/franchise/companies`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newCompany)
      });

      const data = await response.json();
      if (data.success) {
        setShowCreateModal(false);
        setNewCompany({
          company_name: '',
          company_code: '',
          contact_email: '',
          contact_phone: '',
          commission_split_company: 50,
          commission_split_agent: 50,
          primary_color: '#0ea5e9',
          secondary_color: '#1e293b'
        });
        fetchData();
      } else {
        alert(data.detail || 'Failed to create company');
      }
    } catch (err) {
      console.error('Error creating company:', err);
      alert('Failed to create company');
    } finally {
      setCreating(false);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount || 0);
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A';
    return new Date(dateStr).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="w-8 h-8 text-cyan-500 animate-spin" />
        <span className="ml-3 text-slate-400">Loading White Label Dashboard...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center">
            <Building2 className="w-7 h-7 mr-3 text-purple-500" />
            White Label Franchise Management
          </h1>
          <p className="text-slate-400 mt-1">
            Manage franchise companies selling FIDUS BALANCE fund
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button
            onClick={() => setViewMode('overview')}
            variant={viewMode === 'overview' ? 'default' : 'outline'}
            className={viewMode === 'overview' ? 'bg-purple-600' : ''}
          >
            <PieChart className="w-4 h-4 mr-2" />
            Overview
          </Button>
          <Button
            onClick={() => setViewMode('companies')}
            variant={viewMode === 'companies' ? 'default' : 'outline'}
            className={viewMode === 'companies' ? 'bg-purple-600' : ''}
          >
            <Building2 className="w-4 h-4 mr-2" />
            Companies
          </Button>
          <Button
            onClick={() => setShowCreateModal(true)}
            className="bg-green-600 hover:bg-green-700"
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Franchise
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <Card className="bg-gradient-to-br from-purple-900/50 to-slate-900 border-purple-700/50">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-purple-300">Franchise Companies</p>
                <p className="text-2xl font-bold text-white">{stats?.total_companies || 0}</p>
              </div>
              <Building2 className="w-8 h-8 text-purple-400" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-blue-900/50 to-slate-900 border-blue-700/50">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-blue-300">Total End Clients</p>
                <p className="text-2xl font-bold text-white">{stats?.total_clients || 0}</p>
              </div>
              <Users className="w-8 h-8 text-blue-400" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-cyan-900/50 to-slate-900 border-cyan-700/50">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-cyan-300">Total AUM</p>
                <p className="text-2xl font-bold text-white">{formatCurrency(stats?.total_aum)}</p>
              </div>
              <DollarSign className="w-8 h-8 text-cyan-400" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-green-900/50 to-slate-900 border-green-700/50">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-green-300">Sales Agents</p>
                <p className="text-2xl font-bold text-white">{stats?.total_agents || 0}</p>
              </div>
              <UserPlus className="w-8 h-8 text-green-400" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-amber-900/50 to-slate-900 border-amber-700/50">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-amber-300">Commission Pool</p>
                <p className="text-2xl font-bold text-white">{formatCurrency(stats?.commission?.pool)}</p>
              </div>
              <Percent className="w-8 h-8 text-amber-400" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Fund Terms Card */}
      <Card className="bg-slate-800/50 border-slate-700">
        <CardHeader className="pb-3">
          <CardTitle className="text-lg text-white flex items-center">
            <FileText className="w-5 h-5 mr-2 text-purple-400" />
            FIDUS BALANCE White Label Terms
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
            <div className="bg-slate-700/50 rounded-lg p-3">
              <p className="text-xs text-slate-400">Gross Return (FIDUS)</p>
              <p className="text-lg font-bold text-green-400">2.5% /mo</p>
            </div>
            <div className="bg-slate-700/50 rounded-lg p-3">
              <p className="text-xs text-slate-400">Client Return</p>
              <p className="text-lg font-bold text-cyan-400">2.0% /mo</p>
            </div>
            <div className="bg-slate-700/50 rounded-lg p-3">
              <p className="text-xs text-slate-400">Commission Pool</p>
              <p className="text-lg font-bold text-amber-400">0.5% /mo</p>
            </div>
            <div className="bg-slate-700/50 rounded-lg p-3">
              <p className="text-xs text-slate-400">Contract Duration</p>
              <p className="text-lg font-bold text-white">14 months</p>
            </div>
            <div className="bg-slate-700/50 rounded-lg p-3">
              <p className="text-xs text-slate-400">Incubation Period</p>
              <p className="text-lg font-bold text-white">2 months</p>
            </div>
            <div className="bg-slate-700/50 rounded-lg p-3">
              <p className="text-xs text-slate-400">Payment Frequency</p>
              <p className="text-lg font-bold text-white">Quarterly</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Commission Split Options */}
      <Card className="bg-slate-800/50 border-slate-700">
        <CardHeader className="pb-3">
          <CardTitle className="text-lg text-white flex items-center">
            <PieChart className="w-5 h-5 mr-2 text-amber-400" />
            Commission Split Options (Company vs Agent)
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {commissionSplits.map((split, idx) => (
              <div key={idx} className="bg-slate-700/50 rounded-lg p-4 border border-slate-600">
                <div className="flex items-center justify-between mb-3">
                  <Badge className="bg-purple-600 text-white text-lg px-3 py-1">
                    {split.name}
                  </Badge>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-slate-400">Company Share:</span>
                    <span className="text-green-400 font-bold">{split.company_share}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Agent Share:</span>
                    <span className="text-cyan-400 font-bold">{split.agent_share}%</span>
                  </div>
                  <div className="h-2 bg-slate-600 rounded-full overflow-hidden mt-2">
                    <div 
                      className="h-full bg-gradient-to-r from-green-500 to-cyan-500"
                      style={{ width: `${split.company_share}%` }}
                    />
                  </div>
                  <p className="text-xs text-slate-500 mt-2">{split.description}</p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Companies List */}
      {viewMode === 'companies' && (
        <Card className="bg-slate-800/50 border-slate-700">
          <CardHeader>
            <CardTitle className="text-lg text-white flex items-center justify-between">
              <span className="flex items-center">
                <Building2 className="w-5 h-5 mr-2 text-purple-400" />
                Franchise Companies ({companies.length})
              </span>
              <Button
                size="sm"
                onClick={fetchData}
                variant="outline"
                className="text-slate-300"
              >
                <RefreshCw className="w-4 h-4 mr-1" />
                Refresh
              </Button>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {companies.length === 0 ? (
              <div className="text-center py-12">
                <Building2 className="w-16 h-16 text-slate-600 mx-auto mb-4" />
                <p className="text-slate-400 text-lg">No franchise companies yet</p>
                <p className="text-slate-500 text-sm mt-1">Click "Add Franchise" to create your first white-label partner</p>
                <Button
                  onClick={() => setShowCreateModal(true)}
                  className="mt-4 bg-purple-600 hover:bg-purple-700"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Add First Franchise
                </Button>
              </div>
            ) : (
              <div className="space-y-4">
                {companies.map((company) => (
                  <motion.div
                    key={company.company_id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-slate-700/50 rounded-lg p-4 border border-slate-600 hover:border-purple-500/50 transition-colors"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-4">
                        {/* Logo placeholder */}
                        <div 
                          className="w-12 h-12 rounded-lg flex items-center justify-center text-white font-bold text-lg"
                          style={{ backgroundColor: company.primary_color || '#0ea5e9' }}
                        >
                          {company.company_name?.charAt(0) || '?'}
                        </div>
                        <div>
                          <h3 className="text-lg font-semibold text-white">{company.company_name}</h3>
                          <div className="flex items-center gap-2 mt-1">
                            <Globe className="w-3 h-3 text-slate-400" />
                            <span className="text-sm text-cyan-400">{company.subdomain}</span>
                            <Badge className={`text-xs ${company.status === 'active' ? 'bg-green-600' : 'bg-red-600'}`}>
                              {company.status}
                            </Badge>
                          </div>
                          <p className="text-sm text-slate-400 mt-1">
                            Since {formatDate(company.agreement_date)}
                          </p>
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-2">
                        <Button size="sm" variant="outline" className="text-slate-300">
                          <Eye className="w-4 h-4 mr-1" />
                          View
                        </Button>
                        <Button size="sm" variant="outline" className="text-slate-300">
                          <Settings className="w-4 h-4 mr-1" />
                          Settings
                        </Button>
                        <Button size="sm" variant="outline" className="text-cyan-400">
                          <ExternalLink className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>

                    {/* Stats Row */}
                    <div className="grid grid-cols-4 gap-4 mt-4 pt-4 border-t border-slate-600">
                      <div>
                        <p className="text-xs text-slate-400">Clients</p>
                        <p className="text-lg font-bold text-white">{company.total_clients || 0}</p>
                      </div>
                      <div>
                        <p className="text-xs text-slate-400">AUM</p>
                        <p className="text-lg font-bold text-cyan-400">{formatCurrency(company.total_aum)}</p>
                      </div>
                      <div>
                        <p className="text-xs text-slate-400">Agents</p>
                        <p className="text-lg font-bold text-white">{company.total_agents || 0}</p>
                      </div>
                      <div>
                        <p className="text-xs text-slate-400">Commission Split</p>
                        <p className="text-lg font-bold text-amber-400">
                          {company.commission_split?.company || 50}-{company.commission_split?.agent || 50}
                        </p>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Create Company Modal */}
      <AnimatePresence>
        {showCreateModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4"
            onClick={() => setShowCreateModal(false)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="bg-slate-800 rounded-xl border border-slate-700 w-full max-w-lg"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="p-4 border-b border-slate-700 flex items-center justify-between">
                <h2 className="text-xl font-bold text-white flex items-center">
                  <Building2 className="w-5 h-5 mr-2 text-purple-400" />
                  Add Franchise Company
                </h2>
                <Button variant="ghost" onClick={() => setShowCreateModal(false)} className="text-slate-400">
                  <X className="w-5 h-5" />
                </Button>
              </div>

              <div className="p-4 space-y-4">
                <div>
                  <label className="block text-sm text-slate-400 mb-1">Company Name *</label>
                  <input
                    type="text"
                    value={newCompany.company_name}
                    onChange={(e) => setNewCompany(prev => ({ ...prev, company_name: e.target.value }))}
                    placeholder="Acme Investment Group"
                    className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white focus:border-purple-500 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-sm text-slate-400 mb-1">Company Code (for subdomain) *</label>
                  <div className="flex items-center gap-2">
                    <input
                      type="text"
                      value={newCompany.company_code}
                      onChange={(e) => setNewCompany(prev => ({ ...prev, company_code: e.target.value.toLowerCase().replace(/[^a-z0-9]/g, '') }))}
                      placeholder="acme"
                      className="flex-1 bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white focus:border-purple-500 focus:outline-none"
                    />
                    <span className="text-slate-400 text-sm">.fidus-balance.com</span>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm text-slate-400 mb-1">Contact Email *</label>
                    <input
                      type="email"
                      value={newCompany.contact_email}
                      onChange={(e) => setNewCompany(prev => ({ ...prev, contact_email: e.target.value }))}
                      placeholder="admin@acme.com"
                      className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white focus:border-purple-500 focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-slate-400 mb-1">Contact Phone</label>
                    <input
                      type="tel"
                      value={newCompany.contact_phone}
                      onChange={(e) => setNewCompany(prev => ({ ...prev, contact_phone: e.target.value }))}
                      placeholder="+1 555-0123"
                      className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white focus:border-purple-500 focus:outline-none"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm text-slate-400 mb-1">Commission Split</label>
                  <div className="flex gap-2">
                    {['70-30', '60-40', '50-50'].map((split) => {
                      const [company, agent] = split.split('-').map(Number);
                      const isSelected = newCompany.commission_split_company === company;
                      return (
                        <button
                          key={split}
                          onClick={() => setNewCompany(prev => ({
                            ...prev,
                            commission_split_company: company,
                            commission_split_agent: agent
                          }))}
                          className={`flex-1 py-2 rounded-lg border transition-colors ${
                            isSelected 
                              ? 'bg-purple-600 border-purple-500 text-white' 
                              : 'bg-slate-700 border-slate-600 text-slate-300 hover:border-purple-500'
                          }`}
                        >
                          {split}
                        </button>
                      );
                    })}
                  </div>
                  <p className="text-xs text-slate-500 mt-1">
                    Company gets {newCompany.commission_split_company}% of 0.5% pool, Agent gets {newCompany.commission_split_agent}%
                  </p>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm text-slate-400 mb-1">Primary Color</label>
                    <div className="flex items-center gap-2">
                      <input
                        type="color"
                        value={newCompany.primary_color}
                        onChange={(e) => setNewCompany(prev => ({ ...prev, primary_color: e.target.value }))}
                        className="w-10 h-10 rounded cursor-pointer"
                      />
                      <input
                        type="text"
                        value={newCompany.primary_color}
                        onChange={(e) => setNewCompany(prev => ({ ...prev, primary_color: e.target.value }))}
                        className="flex-1 bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white text-sm"
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm text-slate-400 mb-1">Secondary Color</label>
                    <div className="flex items-center gap-2">
                      <input
                        type="color"
                        value={newCompany.secondary_color}
                        onChange={(e) => setNewCompany(prev => ({ ...prev, secondary_color: e.target.value }))}
                        className="w-10 h-10 rounded cursor-pointer"
                      />
                      <input
                        type="text"
                        value={newCompany.secondary_color}
                        onChange={(e) => setNewCompany(prev => ({ ...prev, secondary_color: e.target.value }))}
                        className="flex-1 bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white text-sm"
                      />
                    </div>
                  </div>
                </div>
              </div>

              <div className="p-4 border-t border-slate-700 flex justify-end gap-3">
                <Button variant="outline" onClick={() => setShowCreateModal(false)} className="text-slate-300">
                  Cancel
                </Button>
                <Button
                  onClick={createCompany}
                  disabled={creating || !newCompany.company_name || !newCompany.company_code || !newCompany.contact_email}
                  className="bg-purple-600 hover:bg-purple-700"
                >
                  {creating ? (
                    <>
                      <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                      Creating...
                    </>
                  ) : (
                    <>
                      <Check className="w-4 h-4 mr-2" />
                      Create Franchise
                    </>
                  )}
                </Button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default WhiteLabelDashboard;
