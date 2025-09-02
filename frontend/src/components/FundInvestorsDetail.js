import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { ArrowLeft, Users, TrendingUp, TrendingDown, DollarSign, Calendar, Activity, Eye } from "lucide-react";
import axios from "axios";
import { format } from "date-fns";

const FundInvestorsDetail = ({ fundId, fundName, onBack }) => {
  const [investorsData, setInvestorsData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedInvestor, setSelectedInvestor] = useState(null);

  const backendUrl = process.env.REACT_APP_BACKEND_URL;

  useEffect(() => {
    fetchFundInvestors();
  }, [fundId]);

  const fetchFundInvestors = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${backendUrl}/api/crm/fund/${fundId}/investors`);
      setInvestorsData(response.data);
    } catch (error) {
      console.error('Error fetching fund investors:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const handleViewInvestorProfile = (investor) => {
    setSelectedInvestor(investor);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-600"></div>
      </div>
    );
  }

  if (!investorsData) {
    return (
      <div className="text-center text-gray-400 py-8">
        Failed to load investor data. Please try again.
      </div>
    );
  }

  if (selectedInvestor) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <Button
            variant="outline"
            onClick={() => setSelectedInvestor(null)}
            className="border-slate-600 text-slate-300 hover:bg-slate-700"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Investors List
          </Button>
        </div>

        <Card className="bg-slate-800 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white">Investor Profile: {selectedInvestor.client_name}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="space-y-4">
                <h4 className="text-white font-medium">Client Information</h4>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Name:</span>
                    <span className="text-white">{selectedInvestor.client_name}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Email:</span>
                    <span className="text-white">{selectedInvestor.client_email}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Status:</span>
                    <Badge className="bg-green-600/20 text-green-400">{selectedInvestor.status}</Badge>
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <h4 className="text-white font-medium">Fund Investment</h4>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Invested Amount:</span>
                    <span className="text-white font-medium">{formatCurrency(selectedInvestor.fund_allocation.invested_amount)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Current Value:</span>
                    <span className="text-white font-medium">{formatCurrency(selectedInvestor.fund_allocation.current_value)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">P&L:</span>
                    <span className={`font-medium ${selectedInvestor.fund_allocation.total_pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {selectedInvestor.fund_allocation.total_pnl >= 0 ? '+' : ''}{formatCurrency(selectedInvestor.fund_allocation.total_pnl)} 
                      ({selectedInvestor.fund_allocation.pnl_percentage >= 0 ? '+' : ''}{selectedInvestor.fund_allocation.pnl_percentage.toFixed(2)}%)
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Entry Date:</span>
                    <span className="text-white">{format(new Date(selectedInvestor.fund_allocation.entry_date), 'MMM dd, yyyy')}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Days Invested:</span>
                    <span className="text-white">{selectedInvestor.fund_allocation.days_invested} days</span>
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <h4 className="text-white font-medium">Trading Account</h4>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Account:</span>
                    <span className="text-white">{selectedInvestor.trading_account.account_number || 'N/A'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Balance:</span>
                    <span className="text-white font-medium">{formatCurrency(selectedInvestor.trading_account.balance)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Equity:</span>
                    <span className="text-white font-medium">{formatCurrency(selectedInvestor.trading_account.equity)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Open Positions:</span>
                    <span className="text-white">{selectedInvestor.trading_account.open_positions}</span>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button
            variant="outline"
            onClick={onBack}
            className="border-slate-600 text-slate-300 hover:bg-slate-700"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Funds
          </Button>
          <div>
            <h2 className="text-2xl font-bold text-white">{fundName} Investors</h2>
            <p className="text-gray-400">Detailed investor information and allocations</p>
          </div>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="bg-slate-800 border-slate-700">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-400">Total Investors</p>
                <p className="text-2xl font-bold text-white">{investorsData.summary.total_investors}</p>
              </div>
              <div className="h-12 w-12 bg-cyan-600/20 rounded-lg flex items-center justify-center">
                <Users className="h-6 w-6 text-cyan-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-slate-800 border-slate-700">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-400">Total Invested</p>
                <p className="text-2xl font-bold text-white">{formatCurrency(investorsData.summary.total_invested)}</p>
              </div>
              <div className="h-12 w-12 bg-green-600/20 rounded-lg flex items-center justify-center">
                <DollarSign className="h-6 w-6 text-green-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-slate-800 border-slate-700">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-400">Current Value</p>
                <p className="text-2xl font-bold text-white">{formatCurrency(investorsData.summary.total_current_value)}</p>
              </div>
              <div className="h-12 w-12 bg-blue-600/20 rounded-lg flex items-center justify-center">
                <Activity className="h-6 w-6 text-blue-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-slate-800 border-slate-700">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-400">Total P&L</p>
                <p className={`text-2xl font-bold ${investorsData.summary.total_pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {investorsData.summary.total_pnl >= 0 ? '+' : ''}{formatCurrency(investorsData.summary.total_pnl)}
                </p>
              </div>
              <div className="h-12 w-12 bg-purple-600/20 rounded-lg flex items-center justify-center">
                {investorsData.summary.total_pnl >= 0 ? (
                  <TrendingUp className="h-6 w-6 text-green-600" />
                ) : (
                  <TrendingDown className="h-6 w-6 text-red-600" />
                )}
              </div>
            </div>
            <div className="mt-2">
              <span className={`text-sm ${investorsData.summary.total_pnl_percentage >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {investorsData.summary.total_pnl_percentage >= 0 ? '+' : ''}{investorsData.summary.total_pnl_percentage.toFixed(2)}%
              </span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Investors Table */}
      <Card className="bg-slate-800 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white">Investor Details</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-600">
                  <th className="text-left py-3 px-4 text-gray-400 font-medium">Investor</th>
                  <th className="text-right py-3 px-4 text-gray-400 font-medium">Invested</th>
                  <th className="text-right py-3 px-4 text-gray-400 font-medium">Current Value</th>
                  <th className="text-right py-3 px-4 text-gray-400 font-medium">P&L</th>
                  <th className="text-right py-3 px-4 text-gray-400 font-medium">Allocation %</th>
                  <th className="text-right py-3 px-4 text-gray-400 font-medium">Entry Date</th>
                  <th className="text-right py-3 px-4 text-gray-400 font-medium">Trading Balance</th>
                  <th className="text-center py-3 px-4 text-gray-400 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {investorsData.investors.map((investor, index) => (
                  <tr key={investor.client_id} className="border-b border-slate-700 hover:bg-slate-700/50">
                    <td className="py-3 px-4">
                      <div>
                        <div className="font-medium text-white">{investor.client_name}</div>
                        <div className="text-xs text-gray-400">{investor.client_email}</div>
                      </div>
                    </td>
                    <td className="text-right py-3 px-4 text-white font-medium">
                      {formatCurrency(investor.fund_allocation.invested_amount)}
                    </td>
                    <td className="text-right py-3 px-4 text-white font-medium">
                      {formatCurrency(investor.fund_allocation.current_value)}
                    </td>
                    <td className="text-right py-3 px-4">
                      <div className={`font-medium ${investor.fund_allocation.total_pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                        {investor.fund_allocation.total_pnl >= 0 ? '+' : ''}{formatCurrency(investor.fund_allocation.total_pnl)}
                      </div>
                      <div className={`text-xs ${investor.fund_allocation.pnl_percentage >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                        {investor.fund_allocation.pnl_percentage >= 0 ? '+' : ''}{investor.fund_allocation.pnl_percentage.toFixed(2)}%
                      </div>
                    </td>
                    <td className="text-right py-3 px-4 text-white">
                      {investor.fund_allocation.allocation_percentage.toFixed(1)}%
                    </td>
                    <td className="text-right py-3 px-4 text-gray-400">
                      {format(new Date(investor.fund_allocation.entry_date), 'MMM dd, yyyy')}
                    </td>
                    <td className="text-right py-3 px-4 text-white font-medium">
                      {formatCurrency(investor.trading_account.balance)}
                    </td>
                    <td className="text-center py-3 px-4">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleViewInvestorProfile(investor)}
                        className="border-slate-600 text-slate-300 hover:bg-slate-700"
                      >
                        <Eye className="h-4 w-4" />
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default FundInvestorsDetail;