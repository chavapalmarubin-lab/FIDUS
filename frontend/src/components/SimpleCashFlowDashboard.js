import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import {
  DollarSign,
  TrendingUp,
  TrendingDown,
  Activity,
  AlertCircle
} from "lucide-react";

const SimpleCashFlowDashboard = () => {
  const [cashFlowData, setCashFlowData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchCashFlowData();
  }, []);

  const fetchCashFlowData = async () => {
    try {
      setLoading(true);
      setError("");

      const token = localStorage.getItem('fidus_token');
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/admin/cashflow/complete`,
        { headers: { 'Authorization': `Bearer ${token}` } }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      if (data.success) {
        setCashFlowData(data);
      } else {
        throw new Error(data.message || 'Failed to fetch cash flow data');
      }

    } catch (err) {
      console.error('Error fetching cash flow data:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value) => {
    if (value === null || value === undefined) return '$0.00';
    const formatted = Math.abs(value).toLocaleString('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    });
    return value < 0 ? `-$${formatted}` : `$${formatted}`;
  };

  const MetricCard = ({ title, value, icon: Icon, trend, description }) => {
    const isNegative = value < 0;
    const TrendIcon = isNegative ? TrendingDown : TrendingUp;

    return (
      <Card className="hover:shadow-lg transition-shadow">
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="text-sm font-medium text-gray-600">
            {title}
          </CardTitle>
          <Icon className="h-5 w-5 text-gray-400" />
        </CardHeader>
        <CardContent>
          <div className="flex items-baseline justify-between">
            <div className="text-2xl font-bold">
              <span className={isNegative ? 'text-red-600' : ''}>
                {formatCurrency(value)}
              </span>
            </div>
            {trend !== undefined && (
              <Badge variant={isNegative ? 'destructive' : 'success'} className="ml-2">
                <TrendIcon className="h-3 w-3 mr-1" />
                {Math.abs(trend)}%
              </Badge>
            )}
          </div>
          {description && (
            <p className="text-xs text-gray-500 mt-2">{description}</p>
          )}
        </CardContent>
      </Card>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Card className="max-w-md">
          <CardContent className="flex items-center gap-4 p-6">
            <AlertCircle className="h-8 w-8 text-red-500" />
            <div>
              <h3 className="font-semibold text-red-600">Error Loading Cash Flow Data</h3>
              <p className="text-sm text-gray-600">{error}</p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!cashFlowData) {
    return null;
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Cash Flow & Performance Analysis
        </h1>
        <p className="text-gray-600">
          Simplified view showing key fund metrics from all {cashFlowData.account_count || 15} trading accounts
        </p>
      </div>

      {/* Fund Assets Section */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
          <Activity className="h-5 w-5 mr-2 text-cyan-600" />
          Fund Assets
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <MetricCard
            title="Total Equity"
            value={cashFlowData.total_equity}
            icon={DollarSign}
            description={`Sum from ${cashFlowData.account_count || 15} MT5 accounts`}
          />
          <MetricCard
            title="Broker Rebates"
            value={cashFlowData.broker_rebates}
            icon={TrendingUp}
            description="Commission from trading volume"
          />
          <MetricCard
            title="Total Fund Assets"
            value={cashFlowData.total_fund_assets}
            icon={Activity}
            description="Equity + Rebates"
          />
        </div>
      </div>

      {/* Fund Performance Section */}
      <div>
        <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
          <TrendingUp className="h-5 w-5 mr-2 text-green-600" />
          Fund Performance
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <MetricCard
            title="Fund Revenue"
            value={cashFlowData.fund_revenue}
            icon={TrendingUp}
            description="Total Equity - Client Investment"
          />
          <MetricCard
            title="Fund Obligations"
            value={cashFlowData.fund_obligations}
            icon={DollarSign}
            description="Client interest obligations"
          />
          <MetricCard
            title="Net Profit"
            value={cashFlowData.net_profit}
            icon={cashFlowData.net_profit >= 0 ? TrendingUp : TrendingDown}
            description="Revenue - Obligations"
          />
        </div>
      </div>

      {/* Summary Banner */}
      <Card className="mt-8 bg-gradient-to-r from-cyan-50 to-blue-50 border-cyan-200">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-1">
                Current Fund Status
              </h3>
              <p className="text-sm text-gray-600">
                Based on {cashFlowData.active_investments_count || 0} active investments
                {cashFlowData.current_month && ` • ${cashFlowData.current_month}`}
              </p>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-500 mb-1">Total Trades</p>
              <p className="text-2xl font-bold text-cyan-600">
                {cashFlowData.trades_count || 0}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default SimpleCashFlowDashboard;
