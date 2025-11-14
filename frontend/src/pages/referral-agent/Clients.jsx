import React, { useState, useEffect } from 'react';
import Layout from '../../components/referral-agent/Layout';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Alert, AlertDescription } from '../../components/ui/alert';
import { UserCheck, DollarSign, TrendingUp, Calendar } from 'lucide-react';
import referralAgentApi from '../../services/referralAgentApi';
import { format } from 'date-fns';

const Clients = () => {
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchClients();
  }, []);

  const fetchClients = async () => {
    try {
      setLoading(true);
      const response = await referralAgentApi.getClients();
      if (response.success) {
        setClients(response.clients || []);
      } else {
        setError('Failed to load clients');
      }
    } catch (err) {
      console.error('Clients error:', err);
      setError('An error occurred loading clients');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Your Clients</h2>
        <p className="text-gray-600 mt-1">Track your converted leads and their investments</p>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <div key={i} className="bg-white p-6 rounded-lg shadow animate-pulse">
              <div className="h-6 bg-gray-200 rounded w-3/4 mb-4"></div>
              <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
              <div className="h-4 bg-gray-200 rounded w-2/3"></div>
            </div>
          ))}
        </div>
      ) : clients.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {clients.map((client) => (
            <Card key={client.clientId} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span className="text-lg">{client.clientName}</span>
                  <UserCheck className="h-5 w-5 text-green-600" />
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {/* Total Investment */}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center text-gray-600">
                      <DollarSign className="h-4 w-4 mr-2" />
                      <span className="text-sm">Total Invested</span>
                    </div>
                    <span className="font-semibold text-gray-900">
                      ${client.totalInvestment?.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || '0.00'}
                    </span>
                  </div>

                  {/* Active Investments */}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center text-gray-600">
                      <TrendingUp className="h-4 w-4 mr-2" />
                      <span className="text-sm">Active Investments</span>
                    </div>
                    <span className="font-semibold text-gray-900">
                      {client.activeInvestments || 0}
                    </span>
                  </div>

                  {/* Join Date */}
                  {client.joinDate && (
                    <div className="flex items-center justify-between">
                      <div className="flex items-center text-gray-600">
                        <Calendar className="h-4 w-4 mr-2" />
                        <span className="text-sm">Client Since</span>
                      </div>
                      <span className="text-sm text-gray-900">
                        {format(new Date(client.joinDate), 'MMM yyyy')}
                      </span>
                    </div>
                  )}

                  {/* Investments Breakdown */}
                  {client.investments && client.investments.length > 0 && (
                    <div className="pt-4 border-t">
                      <p className="text-xs font-medium text-gray-500 mb-2">INVESTMENTS</p>
                      <div className="space-y-2">
                        {client.investments.map((inv, idx) => (
                          <div key={idx} className="flex items-center justify-between text-sm">
                            <span className="text-gray-600">{inv.fundCode}</span>
                            <span className="font-medium text-gray-900">
                              ${inv.amount?.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <UserCheck className="h-16 w-16 mx-auto text-gray-300 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Clients Yet</h3>
          <p className="text-gray-600">
            When your leads convert into clients, they'll appear here.
          </p>
        </div>
      )}
    </Layout>
  );
};

export default Clients;
