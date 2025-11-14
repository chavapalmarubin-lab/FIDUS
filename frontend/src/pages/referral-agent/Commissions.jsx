import React, { useState, useEffect } from 'react';
import Layout from '../../components/referral-agent/Layout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Alert, AlertDescription } from '../../components/ui/alert';
import { DollarSign, Calendar, CheckCircle, Clock } from 'lucide-react';
import { Badge } from '../../components/ui/badge';
import referralAgentApi from '../../services/referralAgentApi';
import { format } from 'date-fns';

const Commissions = () => {
  const [commissions, setCommissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [stats, setStats] = useState({
    total: 0,
    paid: 0,
    pending: 0,
  });

  useEffect(() => {
    fetchCommissions();
  }, []);

  const fetchCommissions = async () => {
    try {
      setLoading(true);
      const response = await referralAgentApi.getCommissions();
      if (response.success) {
        const comms = response.commissions || [];
        setCommissions(comms);
        
        // Calculate stats
        const total = comms.reduce((sum, c) => sum + (c.commissionAmount || 0), 0);
        const paid = comms
          .filter(c => c.status === 'paid')
          .reduce((sum, c) => sum + (c.commissionAmount || 0), 0);
        const pending = comms
          .filter(c => c.status === 'pending')
          .reduce((sum, c) => sum + (c.commissionAmount || 0), 0);
        
        setStats({ total, paid, pending });
      } else {
        setError('Failed to load commissions');
      }
    } catch (err) {
      console.error('Commissions error:', err);
      setError('An error occurred loading commissions');
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const config = {
      paid: { label: 'Paid', className: 'bg-green-100 text-green-800 hover:bg-green-100', icon: CheckCircle },
      pending: { label: 'Pending', className: 'bg-yellow-100 text-yellow-800 hover:bg-yellow-100', icon: Clock },
      scheduled: { label: 'Scheduled', className: 'bg-blue-100 text-blue-800 hover:bg-blue-100', icon: Calendar },
    };

    const config_ = config[status] || config.pending;
    const Icon = config_.icon;

    return (
      <Badge className={config_.className} variant="secondary">
        <Icon className="h-3 w-3 mr-1" />
        {config_.label}
      </Badge>
    );
  };

  return (
    <Layout>
      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Commission Schedule</h2>
        <p className="text-gray-600 mt-1">Track your earnings and payment schedule</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 mb-6">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-500">Total Earned</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  ${loading ? '...' : stats.total.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </p>
              </div>
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                <DollarSign className="h-6 w-6 text-blue-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-500">Paid</p>
                <p className="text-2xl font-bold text-green-600 mt-1">
                  ${loading ? '...' : stats.paid.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </p>
              </div>
              <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                <CheckCircle className="h-6 w-6 text-green-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-500">Pending</p>
                <p className="text-2xl font-bold text-yellow-600 mt-1">
                  ${loading ? '...' : stats.pending.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </p>
              </div>
              <div className="w-12 h-12 bg-yellow-100 rounded-full flex items-center justify-center">
                <Clock className="h-6 w-6 text-yellow-600" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Commissions Table */}
      <Card>
        <CardHeader>
          <CardTitle>Commission History</CardTitle>
          <CardDescription>All your commission payments and scheduled payouts</CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="animate-pulse">
                  <div className="h-16 bg-gray-200 rounded"></div>
                </div>
              ))}
            </div>
          ) : commissions.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Client</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Amount</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Date</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {commissions.map((commission, idx) => (
                    <tr key={idx} className="border-b last:border-0 hover:bg-gray-50">
                      <td className="py-3 px-4">
                        <p className="font-medium text-gray-900">{commission.clientName || 'N/A'}</p>
                        {commission.fundCode && (
                          <p className="text-sm text-gray-500">{commission.fundCode}</p>
                        )}
                      </td>
                      <td className="py-3 px-4">
                        <span className="font-semibold text-gray-900">
                          ${commission.commissionAmount?.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-gray-600">
                        {commission.paymentDate ? format(new Date(commission.paymentDate), 'MMM d, yyyy') : 'N/A'}
                      </td>
                      <td className="py-3 px-4">
                        {getStatusBadge(commission.status)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-12">
              <DollarSign className="h-16 w-16 mx-auto text-gray-300 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No Commissions Yet</h3>
              <p className="text-gray-600">
                Your commissions will appear here when your clients make investments.
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </Layout>
  );
};

export default Commissions;
