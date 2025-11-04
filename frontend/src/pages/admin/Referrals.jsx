import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Badge } from '../../components/ui/badge';
import referralService from '../../services/referralService';
import SalespersonCard from '../../components/referrals/SalespersonCard';
import CommissionCalendar from '../../components/referrals/CommissionCalendar';
import SalespersonDetail from './SalespersonDetail';

const Referrals = () => {
  // View state management for tab-based navigation
  const [currentView, setCurrentView] = useState('list'); // 'list' | 'detail' | 'calendar' | 'new'
  const [selectedSalespersonId, setSelectedSalespersonId] = useState(null);
  
  const [salespeople, setSalespeople] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [activeOnly, setActiveOnly] = useState(true);
  const [stats, setStats] = useState({
    totalSalespeople: 0,
    totalClients: 0,
    totalSales: 0,
    totalCommissions: 0,
    commissionsPaid: 0,
    commissionsPending: 0
  });

  useEffect(() => {
    loadData();
  }, [activeOnly]);

  const loadData = async () => {
    try {
      setLoading(true);
      const data = await referralService.getSalespeople(activeOnly);
      setSalespeople(data.salespeople || []);
      
      const stats = {
        totalSalespeople: data.salespeople?.length || 0,
        totalClients: data.salespeople?.reduce((sum, sp) => sum + (sp.total_clients_referred || 0), 0),
        totalSales: data.salespeople?.reduce((sum, sp) => sum + parseFloat(sp.total_sales_volume || 0), 0),
        totalCommissions: data.salespeople?.reduce((sum, sp) => sum + parseFloat(sp.total_commissions_earned || 0), 0),
        commissionsPaid: data.salespeople?.reduce((sum, sp) => sum + parseFloat(sp.commissions_paid_to_date || 0), 0),
        commissionsPending: data.salespeople?.reduce((sum, sp) => sum + parseFloat(sp.commissions_pending || 0), 0)
      };
      setStats(stats);
    } catch (error) {
      console.error('Failed to load salespeople:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredSalespeople = salespeople.filter(sp =>
    sp.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    sp.referral_code?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    sp.email?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value || 0);
  };

  const handleViewSalesperson = (salespersonId) => {
    setSelectedSalespersonId(salespersonId);
    setCurrentView('detail');
  };

  const handleBackToList = () => {
    setCurrentView('list');
    setSelectedSalespersonId(null);
    loadData(); // Refresh data when returning to list
  };

  // Show detail view if selected
  if (currentView === 'detail' && selectedSalespersonId) {
    return (
      <SalespersonDetail 
        salespersonId={selectedSalespersonId}
        onBack={handleBackToList}
      />
    );
  }

  // Show full calendar view if selected
  if (currentView === 'calendar') {
    return (
      <div className="max-w-7xl mx-auto p-6 space-y-6">
        <div className="flex items-center gap-4 mb-6">
          <Button
            variant="outline"
            onClick={() => setCurrentView('list')}
            className="flex items-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back to Referrals
          </Button>
          <h1 className="text-3xl font-bold text-gray-900">Commission Payment Calendar</h1>
        </div>
        <CommissionCalendar compact={false} />
      </div>
    );
  }

  // Show main list view
  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Referrals & Commissions</h1>
          <p className="text-gray-600 mt-1">Manage salespeople and track commission payments</p>
        </div>
        <Button
          onClick={() => alert('Add Salesperson feature coming soon')}
          className="bg-blue-600 hover:bg-blue-700"
        >
          <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          Add Salesperson
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Active Salespeople</p>
                <p className="text-2xl font-bold text-gray-900">{stats.totalSalespeople}</p>
              </div>
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Sales Volume</p>
                <p className="text-2xl font-bold text-gray-900">{formatCurrency(stats.totalSales)}</p>
              </div>
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Commissions</p>
                <p className="text-2xl font-bold text-gray-900">{formatCurrency(stats.totalCommissions)}</p>
              </div>
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Pending Commissions</p>
                <p className="text-2xl font-bold text-orange-900">{formatCurrency(stats.commissionsPending)}</p>
              </div>
              <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <svg className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <Input
                placeholder="Search by name, email, or referral code..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <div className="flex gap-2">
              <Button
                variant={activeOnly ? "default" : "outline"}
                onClick={() => setActiveOnly(!activeOnly)}
              >
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
                </svg>
                {activeOnly ? 'Active Only' : 'Show All'}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="space-y-4">
        <h2 className="text-xl font-semibold text-gray-900">Salespeople</h2>
        
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading salespeople...</p>
          </div>
        ) : filteredSalespeople.length === 0 ? (
          <Card>
            <CardContent className="py-12 text-center">
              <svg className="w-12 h-12 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
              <p className="text-gray-600">No salespeople found</p>
              <Button
                onClick={() => alert('Add Salesperson feature coming soon')}
                className="mt-4"
                variant="outline"
              >
                Add First Salesperson
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredSalespeople.map((salesperson) => (
              <SalespersonCard
                key={salesperson.id || salesperson._id}
                salesperson={salesperson}
                onClick={() => handleViewSalesperson(salesperson.id || salesperson._id)}
              />
            ))}
          </div>
        )}
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            Upcoming Commission Payments
          </CardTitle>
        </CardHeader>
        <CardContent>
          <CommissionCalendar compact={true} />
          <div className="mt-4 text-center">
            <Button
              variant="outline"
              onClick={() => navigate('/admin/referrals/calendar')}
            >
              View Full Calendar
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Referrals;