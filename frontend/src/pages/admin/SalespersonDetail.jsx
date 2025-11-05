import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../components/ui/tabs';
import referralService from '../../services/referralService';
import CommissionCalendar from '../../components/referrals/CommissionCalendar';
import ApproveModal from '../../components/referrals/ApproveModal';
import MarkPaidModal from '../../components/referrals/MarkPaidModal';

const SalespersonDetail = ({ salespersonId: propSalespersonId, onBack }) => {
  // Get salesperson ID from URL parameter or prop
  const { salespersonId: urlSalespersonId } = useParams();
  const navigate = useNavigate();
  const salespersonId = urlSalespersonId || propSalespersonId;
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedCommission, setSelectedCommission] = useState(null);
  const [showApproveModal, setShowApproveModal] = useState(false);
  const [showPaidModal, setShowPaidModal] = useState(false);

  useEffect(() => {
    loadData();
  }, [salespersonId]);

  const loadData = async () => {
    try {
      setLoading(true);
      const response = await referralService.getSalespersonById(salespersonId);
      setData(response);
    } catch (error) {
      console.error('Failed to load salesperson:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = (commission) => {
    setSelectedCommission(commission);
    setShowApproveModal(true);
  };

  const handleMarkPaid = (commission) => {
    setSelectedCommission(commission);
    setShowPaidModal(true);
  };

  const handleApproveSuccess = () => {
    setShowApproveModal(false);
    loadData();
  };

  const handlePaidSuccess = () => {
    setShowPaidModal(false);
    loadData();
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(value || 0);
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A';
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto p-6">
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading salesperson details...</p>
        </div>
      </div>
    );
  }

  if (!data || !data.name) {
    return (
      <div className="max-w-7xl mx-auto p-6">
        <Card>
          <CardContent className="py-12 text-center">
            <p className="text-gray-600">Salesperson not found</p>
            <Button onClick={onBack || (() => navigate('/referrals'))} className="mt-4" variant="outline">
              Back to Referrals
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  // API returns data at root level with correct field names (camelCase)
  const salesperson = {
    ...data,
    referral_code: data.referralCode,
    referral_link: data.referralLink,
    total_sales_volume: data.totalSalesVolume,
    total_commissions_earned: data.totalCommissions,
    commissions_pending: data.pendingCommissions,
    commissions_paid_to_date: data.paidCommissions
  };
  
  // Extract data from response
  const clients = data.clients || [];
  const investments = data.investments || [];
  const commissions = data.commissions || [];

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="outline" onClick={onBack || (() => navigate('/referrals'))}>
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back
          </Button>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{salesperson.name}</h1>
            <div className="flex items-center gap-2 mt-1">
              <Badge variant="outline">{salesperson.referralCode}</Badge>
              {salesperson.active && (
                <Badge className="bg-green-100 text-green-800 border-green-200">Active</Badge>
              )}
            </div>
          </div>
        </div>
        <Button variant="outline">
          <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
          </svg>
          Edit
        </Button>
      </div>

      {/* Contact Info Card */}
      <Card>
        <CardHeader>
          <CardTitle>Contact Information</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <p className="text-sm text-gray-600">Email</p>
              <p className="font-medium">{salesperson.email}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Phone</p>
              <p className="font-medium">{salesperson.phone || 'N/A'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Joined</p>
              <p className="font-medium">{formatDate(salesperson.joinedDate)}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Referral Link</p>
              <a href={salesperson.referralLink} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline text-sm">
                {salesperson.referralLink?.substring(0, 40)}...
              </a>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Performance Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-sm text-gray-600">Total Clients</p>
              <p className="text-3xl font-bold text-gray-900">{clients.length || 0}</p>
              <p className="text-xs text-gray-500 mt-1">{clients.length || 0} active</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-sm text-gray-600">Sales Volume</p>
              <p className="text-3xl font-bold text-gray-900">{formatCurrency(salesperson.total_sales_volume)}</p>
              <p className="text-xs text-gray-500 mt-1">{investments.length || 0} investments</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-sm text-gray-600">Total Commissions</p>
              <p className="text-3xl font-bold text-gray-900">{formatCurrency(salesperson.total_commissions_earned)}</p>
              <p className="text-xs text-gray-500 mt-1">{formatCurrency(salesperson.commissions_paid_to_date)} paid</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-sm text-gray-600">Pending Commissions</p>
              <p className="text-3xl font-bold text-blue-600">{formatCurrency(salesperson.commissions_pending)}</p>
              <p className="text-xs text-gray-500 mt-1">
                {commissions.length} payments
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="commissions" className="space-y-4">
        <TabsList>
          <TabsTrigger value="commissions">Commissions</TabsTrigger>
          <TabsTrigger value="clients">Clients</TabsTrigger>
          <TabsTrigger value="calendar">Calendar</TabsTrigger>
          <TabsTrigger value="payment">Payment Info</TabsTrigger>
        </TabsList>

        {/* Commissions Tab */}
        <TabsContent value="commissions" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Commission History</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {commissions.all?.length === 0 ? (
                  <p className="text-center text-gray-500 py-8">No commissions yet</p>
                ) : (
                  commissions?.map((commission) => (
                    <div
                      key={commission.commissionId}
                      className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50"
                    >
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <p className="font-medium text-gray-900">{formatDate(commission.paymentDate)}</p>
                          <Badge
                            variant={
                              commission.status === 'paid' ? 'success' :
                              commission.status === 'approved' ? 'info' :
                              commission.status === 'ready_to_pay' ? 'warning' :
                              'default'
                            }
                          >
                            {commission.status ? commission.status.replace('_', ' ') : 'pending'}
                          </Badge>
                        </div>
                        <p className="text-sm text-gray-600 mt-1">
                          {commission.fundType ? commission.fundType.replace('FIDUS_', '') : 'Unknown'} - {commission.paymentMonth}
                        </p>
                      </div>
                      <div className="flex items-center gap-4">
                        <p className="font-semibold text-gray-900">{formatCurrency(commission.commissionAmount)}</p>
                        {commission.status === 'pending' && (
                          <Button size="sm" onClick={() => handleApprove(commission)}>
                            Approve
                          </Button>
                        )}
                        {commission.status === 'approved' && (
                          <Button size="sm" onClick={() => handleMarkPaid(commission)}>
                            Mark Paid
                          </Button>
                        )}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Clients Tab */}
        <TabsContent value="clients" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Referred Clients</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {clients?.length === 0 ? (
                  <p className="text-center text-gray-500 py-8">No clients yet</p>
                ) : (
                  clients?.map((client) => (
                    <div key={client.clientId} className="p-4 border rounded-lg">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="font-medium text-gray-900">{client.name}</p>
                          <p className="text-sm text-gray-600">{client.email}</p>
                        </div>
                        <div className="text-right">
                          <p className="font-semibold">
                            {formatCurrency(client.total_commissions_generated)}
                          </p>
                          <p className="text-xs text-gray-500">commissions generated</p>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Calendar Tab */}
        <TabsContent value="calendar">
          <Card>
            <CardHeader>
              <CardTitle>Commission Calendar</CardTitle>
            </CardHeader>
            <CardContent>
              <CommissionCalendar salespersonId={salespersonId} compact={false} />
            </CardContent>
          </Card>
        </TabsContent>

        {/* Payment Info Tab */}
        <TabsContent value="payment">
          <Card>
            <CardHeader>
              <CardTitle>Payment Information</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <p className="text-sm text-gray-600">Payment Method</p>
                  <p className="font-medium">{salesperson.preferred_payment_method?.replace('_', ' ') || 'Not set'}</p>
                </div>
                {salesperson.wallet_details && (
                  <div className="space-y-3">
                    <div>
                      <p className="text-sm text-gray-600">Wallet Type</p>
                      <p className="font-medium">{salesperson.wallet_details.wallet_type || 'N/A'}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Wallet Address</p>
                      <p className="font-mono text-sm">{salesperson.wallet_details.wallet_address || 'Not provided'}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Network</p>
                      <p className="font-medium">{salesperson.wallet_details.network || 'N/A'}</p>
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Modals */}
      {showApproveModal && selectedCommission && (
        <ApproveModal
          commission={selectedCommission}
          onClose={() => setShowApproveModal(false)}
          onSuccess={handleApproveSuccess}
        />
      )}

      {showPaidModal && selectedCommission && (
        <MarkPaidModal
          commission={selectedCommission}
          onClose={() => setShowPaidModal(false)}
          onSuccess={handlePaidSuccess}
        />
      )}
    </div>
  );
};

export default SalespersonDetail;