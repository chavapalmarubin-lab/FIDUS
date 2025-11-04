import React, { useState, useEffect } from 'react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Card, CardContent } from '../ui/card';
import referralService from '../../services/referralService';
import SalespersonTable from './SalespersonTable';
import AddSalespersonModal from './AddSalespersonModal';

const ManageSalespeople = () => {
  const [salespeople, setSalespeople] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingSalesperson, setEditingSalesperson] = useState(null);
  const [showInactive, setShowInactive] = useState(false);

  useEffect(() => {
    loadSalespeople();
  }, [showInactive]);

  const loadSalespeople = async () => {
    try {
      setLoading(true);
      const data = await referralService.getSalespeople(!showInactive);
      setSalespeople(data.salespeople || []);
    } catch (error) {
      alert('Failed to load salespeople');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (data) => {
    try {
      if (editingSalesperson) {
        // Update existing
        await referralService.updateSalesperson(
          editingSalesperson.id || editingSalesperson._id,
          data
        );
      } else {
        // Create new
        await referralService.createSalesperson(data);
      }
      
      await loadSalespeople();
      setShowAddModal(false);
      setEditingSalesperson(null);
    } catch (error) {
      throw error; // Let modal handle error display
    }
  };

  const handleEdit = (salesperson) => {
    setEditingSalesperson(salesperson);
    setShowAddModal(true);
  };

  const handleToggleActive = async (id, newStatus) => {
    try {
      await referralService.updateSalesperson(id, { active: newStatus });
      await loadSalespeople();
      
      // Show notification
      const message = document.createElement('div');
      message.className = 'fixed top-4 right-4 bg-green-600 text-white px-6 py-3 rounded-lg shadow-lg z-50';
      message.textContent = newStatus ? 'Salesperson activated' : 'Salesperson deactivated';
      document.body.appendChild(message);
      setTimeout(() => message.remove(), 2000);
    } catch (error) {
      alert('Failed to update status');
      console.error(error);
    }
  };

  const handleExport = () => {
    // Export to CSV
    const csv = [
      ['Name', 'Email', 'Phone', 'Referral Code', 'Clients', 'Sales Volume', 'Commissions', 'Status'],
      ...salespeople.map(sp => [
        sp.name,
        sp.email,
        sp.phone || '',
        sp.referral_code,
        sp.total_clients_referred || 0,
        sp.total_sales_volume || 0,
        sp.total_commissions_earned || 0,
        sp.active ? 'Active' : 'Inactive'
      ])
    ].map(row => row.join(',')).join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `salespeople-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    
    // Show notification
    const message = document.createElement('div');
    message.className = 'fixed top-4 right-4 bg-green-600 text-white px-6 py-3 rounded-lg shadow-lg z-50';
    message.textContent = 'Exported to CSV';
    document.body.appendChild(message);
    setTimeout(() => message.remove(), 2000);
  };

  const filteredSalespeople = salespeople.filter(sp =>
    sp.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    sp.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
    sp.referral_code?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const totalClients = salespeople.reduce((sum, sp) => sum + (sp.total_clients_referred || 0), 0);
  const totalSales = salespeople.reduce((sum, sp) => sum + (sp.total_sales_volume || 0), 0);
  const activeCount = salespeople.filter(sp => sp.active).length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
            <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
          </div>
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Manage Salespeople</h2>
            <p className="text-sm text-gray-600">
              Add, edit, and manage your sales team
            </p>
          </div>
        </div>

        <Button
          onClick={() => {
            setEditingSalesperson(null);
            setShowAddModal(true);
          }}
          className="bg-blue-600 hover:bg-blue-700"
        >
          <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          Add Salesperson
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Salespeople</p>
                <p className="text-2xl font-bold text-gray-900">
                  {salespeople.length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Active</p>
                <p className="text-2xl font-bold text-green-600">
                  {activeCount}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Clients</p>
                <p className="text-2xl font-bold text-gray-900">
                  {totalClients}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Sales</p>
                <p className="text-2xl font-bold text-green-600">
                  ${(totalSales / 1000).toFixed(0)}K
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Search and Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <svg className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <Input
                placeholder="Search by name, email, or code..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>

            <div className="flex gap-2">
              <Button
                variant={showInactive ? "default" : "outline"}
                onClick={() => setShowInactive(!showInactive)}
              >
                {showInactive ? 'Show Active Only' : 'Show All'}
              </Button>

              <Button
                variant="outline"
                onClick={handleExport}
                disabled={salespeople.length === 0}
              >
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
                Export CSV
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Salespeople Table */}
      {loading ? (
        <Card>
          <CardContent className="py-12 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading salespeople...</p>
          </CardContent>
        </Card>
      ) : (
        <SalespersonTable
          salespeople={filteredSalespeople}
          onEdit={handleEdit}
          onToggleActive={handleToggleActive}
          onRefresh={loadSalespeople}
        />
      )}

      {/* Add/Edit Modal */}
      <AddSalespersonModal
        isOpen={showAddModal}
        onClose={() => {
          setShowAddModal(false);
          setEditingSalesperson(null);
        }}
        onSave={handleSave}
        editData={editingSalesperson}
      />
    </div>
  );
};

export default ManageSalespeople;
