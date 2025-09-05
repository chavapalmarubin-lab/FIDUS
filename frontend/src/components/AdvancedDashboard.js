import React, { useState, useEffect, useMemo } from 'react';
import { motion } from 'framer-motion';
import { 
  TrendingUp, TrendingDown, DollarSign, Users, 
  PieChart, BarChart3, Target, Activity,
  AlertTriangle, CheckCircle, Clock, Filter
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Breadcrumb } from './ui/breadcrumb';
import { useToast } from './ui/toast';

const AdvancedDashboard = ({ user, userType, onTabChange }) => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [timeframe, setTimeframe] = useState('30d');
  const [selectedMetrics, setSelectedMetrics] = useState('all');
  const toast = useToast();

  useEffect(() => {
    fetchDashboardData();
  }, [timeframe, selectedMetrics]);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      // Simulate advanced dashboard data fetching
      const mockData = generateMockDashboardData(userType, timeframe);
      setDashboardData(mockData);
    } catch (error) {
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const generateMockDashboardData = (userType, timeframe) => {
    const baseAmount = userType === 'admin' ? 25000000 : 150000;
    const multiplier = timeframe === '7d' ? 0.8 : timeframe === '90d' ? 1.3 : 1.0;
    
    return {
      summary: {
        totalAssets: baseAmount * multiplier,
        totalClients: userType === 'admin' ? 247 : 1,
        activeInvestments: userType === 'admin' ? 156 : 3,
        monthlyGrowth: 8.7,
        yearlyReturn: 12.4,
        sharpeRatio: 1.8,
      },
      performance: {
        dailyReturns: generatePerformanceData(30),
        monthlyReturns: generatePerformanceData(12),
        yearlyReturns: generatePerformanceData(5),
      },
      allocation: {
        byFund: [
          { name: 'CORE', value: 35, amount: baseAmount * 0.35 },
          { name: 'BALANCE', value: 30, amount: baseAmount * 0.30 },
          { name: 'DYNAMIC', value: 25, amount: baseAmount * 0.25 },
          { name: 'UNLIMITED', value: 10, amount: baseAmount * 0.10 },
        ],
        byRisk: [
          { name: 'Conservative', value: 40, color: '#10B981' },
          { name: 'Moderate', value: 35, color: '#F59E0B' },
          { name: 'Aggressive', value: 25, color: '#EF4444' },
        ],
      },
      alerts: [
        { id: 1, type: 'warning', message: 'Portfolio rebalancing recommended', timestamp: '2 hours ago' },
        { id: 2, type: 'info', message: 'Monthly performance report available', timestamp: '1 day ago' },
        { id: 3, type: 'success', message: 'Investment goal 85% achieved', timestamp: '3 days ago' },
      ],
      recentActivity: [
        { id: 1, type: 'investment', description: 'CORE fund investment', amount: 25000, timestamp: '2024-01-15' },
        { id: 2, type: 'withdrawal', description: 'BALANCE fund redemption', amount: -10000, timestamp: '2024-01-12' },
        { id: 3, type: 'dividend', description: 'DYNAMIC fund dividend', amount: 1250, timestamp: '2024-01-10' },
      ],
    };
  };

  const generatePerformanceData = (periods) => {
    return Array.from({ length: periods }, (_, i) => ({
      period: `Period ${i + 1}`,
      value: 5 + Math.random() * 15,
      benchmark: 6 + Math.random() * 12,
    }));
  };

  const breadcrumbItems = [
    { label: 'Dashboard', active: true },
    { label: userType === 'admin' ? 'Admin Overview' : 'Portfolio Overview' },
  ];

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const MetricCard = ({ title, value, change, icon: Icon, trend, color = 'blue' }) => (
    <motion.div
      whileHover={{ scale: 1.02 }}
      transition={{ duration: 0.2 }}
    >
      <Card className="bg-slate-800 border-slate-700">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-slate-400 text-sm font-medium">{title}</p>
              <p className="text-2xl font-bold text-white mt-1">{value}</p>
              {change && (
                <div className={`flex items-center mt-2 text-sm ${
                  trend === 'up' ? 'text-green-400' : trend === 'down' ? 'text-red-400' : 'text-slate-400'
                }`}>
                  {trend === 'up' ? <TrendingUp size={16} className="mr-1" /> : 
                   trend === 'down' ? <TrendingDown size={16} className="mr-1" /> : null}
                  {change}
                </div>
              )}
            </div>
            <div className={`p-3 rounded-lg bg-${color}-500 bg-opacity-20`}>
              <Icon size={24} className={`text-${color}-400`} />
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );

  const PerformanceChart = ({ data, title }) => (
    <Card className="bg-slate-800 border-slate-700">
      <CardHeader>
        <CardTitle className="text-white">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-64 flex items-end justify-between space-x-2">
          {data.map((item, index) => (
            <div key={index} className="flex-1 flex flex-col items-center">
              <div className="w-full bg-slate-700 rounded-t-sm relative overflow-hidden">
                <div 
                  className="bg-gradient-to-t from-cyan-500 to-blue-500 rounded-t-sm transition-all duration-1000 ease-out"
                  style={{ height: `${(item.value / 20) * 200}px` }}
                />
                <div 
                  className="absolute top-0 left-0 w-full bg-gradient-to-t from-yellow-500 to-orange-500 opacity-50 rounded-t-sm"
                  style={{ height: `${(item.benchmark / 20) * 200}px` }}
                />
              </div>
              <p className="text-xs text-slate-400 mt-2 text-center">{item.period.split(' ')[1]}</p>
            </div>
          ))}
        </div>
        <div className="flex justify-center mt-4 space-x-6">
          <div className="flex items-center">
            <div className="w-4 h-4 bg-gradient-to-r from-cyan-500 to-blue-500 rounded mr-2" />
            <span className="text-sm text-slate-300">Portfolio</span>
          </div>
          <div className="flex items-center">
            <div className="w-4 h-4 bg-gradient-to-r from-yellow-500 to-orange-500 opacity-50 rounded mr-2" />
            <span className="text-sm text-slate-300">Benchmark</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );

  const AllocationChart = ({ data, title, type = 'fund' }) => (
    <Card className="bg-slate-800 border-slate-700">
      <CardHeader>
        <CardTitle className="text-white">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {data.map((item, index) => (
            <div key={index}>
              <div className="flex items-center justify-between mb-2">
                <span className="text-slate-300 text-sm">{item.name}</span>
                <div className="flex items-center space-x-2">
                  <span className="text-slate-400 text-sm">{item.value}%</span>
                  {type === 'fund' && (
                    <span className="text-slate-400 text-xs">{formatCurrency(item.amount)}</span>
                  )}
                </div>
              </div>
              <div className="w-full bg-slate-700 rounded-full h-2">
                <div 
                  className={`h-2 rounded-full transition-all duration-1000 ease-out ${
                    type === 'fund' 
                      ? index === 0 ? 'bg-blue-500' : index === 1 ? 'bg-green-500' : index === 2 ? 'bg-yellow-500' : 'bg-purple-500'
                      : 'bg-gradient-to-r from-cyan-500 to-blue-500'
                  }`}
                  style={{ 
                    width: `${item.value}%`,
                    backgroundColor: type === 'risk' ? item.color : undefined 
                  }}
                />
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );

  const AlertsPanel = ({ alerts }) => (
    <Card className="bg-slate-800 border-slate-700">
      <CardHeader>
        <CardTitle className="text-white flex items-center">
          <AlertTriangle size={20} className="mr-2" />
          Recent Alerts
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {alerts.map((alert) => (
            <div key={alert.id} className="flex items-start space-x-3 p-3 rounded-lg bg-slate-700">
              <div className={`mt-1 ${
                alert.type === 'warning' ? 'text-yellow-400' : 
                alert.type === 'info' ? 'text-blue-400' : 'text-green-400'
              }`}>
                {alert.type === 'warning' ? <AlertTriangle size={16} /> :
                 alert.type === 'info' ? <Clock size={16} /> : <CheckCircle size={16} />}
              </div>
              <div className="flex-1">
                <p className="text-slate-200 text-sm">{alert.message}</p>
                <p className="text-slate-400 text-xs mt-1">{alert.timestamp}</p>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-400 mx-auto mb-4" />
          <h2 className="text-xl text-white font-semibold">Loading Advanced Dashboard...</h2>
          <p className="text-slate-400 mt-2">Analyzing your portfolio data</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <Breadcrumb items={breadcrumbItems} />
          <div className="flex items-center justify-between mt-4">
            <div>
              <h1 className="text-3xl font-bold text-white">
                {userType === 'admin' ? 'Admin Dashboard' : 'Portfolio Overview'}
              </h1>
              <p className="text-slate-400 mt-2">
                {userType === 'admin' 
                  ? 'Comprehensive platform analytics and management' 
                  : 'Your investment performance and portfolio insights'
                }
              </p>
            </div>
            
            <div className="flex items-center space-x-4">
              <select 
                value={timeframe} 
                onChange={(e) => setTimeframe(e.target.value)}
                className="bg-slate-700 text-white border border-slate-600 rounded px-3 py-2"
              >
                <option value="7d">Last 7 Days</option>
                <option value="30d">Last 30 Days</option>
                <option value="90d">Last 90 Days</option>
              </select>
              
              <button 
                onClick={fetchDashboardData}
                className="bg-cyan-600 hover:bg-cyan-700 text-white px-4 py-2 rounded flex items-center"
              >
                <Activity size={16} className="mr-2" />
                Refresh
              </button>
            </div>
          </div>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <MetricCard
            title="Total Assets"
            value={formatCurrency(dashboardData.summary.totalAssets)}
            change="+8.7% this month"
            icon={DollarSign}
            trend="up"
            color="green"
          />
          <MetricCard
            title={userType === 'admin' ? 'Total Clients' : 'Active Investments'}
            value={userType === 'admin' ? dashboardData.summary.totalClients : dashboardData.summary.activeInvestments}
            change="+12% this month"
            icon={userType === 'admin' ? Users : Target}
            trend="up"
            color="blue"
          />
          <MetricCard
            title="Monthly Growth"
            value={`${dashboardData.summary.monthlyGrowth}%`}
            change="Above target"
            icon={TrendingUp}
            trend="up"
            color="cyan"
          />
          <MetricCard
            title="Sharpe Ratio"
            value={dashboardData.summary.sharpeRatio}
            change="Excellent risk-adjusted return"
            icon={BarChart3}
            color="purple"
          />
        </div>

        {/* Charts and Analytics */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <div className="lg:col-span-2">
            <PerformanceChart 
              data={dashboardData.performance.monthlyReturns}
              title="Monthly Performance vs Benchmark"
            />
          </div>
          <div>
            <AllocationChart
              data={dashboardData.allocation.byFund}
              title="Fund Allocation"
              type="fund"
            />
          </div>
        </div>

        {/* Additional Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <AllocationChart
            data={dashboardData.allocation.byRisk}
            title="Risk Profile Distribution"
            type="risk"
          />
          <AlertsPanel alerts={dashboardData.alerts} />
        </div>

        {/* Recent Activity */}
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white">Recent Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-slate-700">
                    <th className="text-left text-slate-400 py-3 px-4">Type</th>
                    <th className="text-left text-slate-400 py-3 px-4">Description</th>
                    <th className="text-left text-slate-400 py-3 px-4">Amount</th>
                    <th className="text-left text-slate-400 py-3 px-4">Date</th>
                  </tr>
                </thead>
                <tbody>
                  {dashboardData.recentActivity.map((activity) => (
                    <tr key={activity.id} className="border-b border-slate-700">
                      <td className="py-3 px-4">
                        <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                          activity.type === 'investment' ? 'bg-green-900 text-green-200' :
                          activity.type === 'withdrawal' ? 'bg-red-900 text-red-200' :
                          'bg-blue-900 text-blue-200'
                        }`}>
                          {activity.type.charAt(0).toUpperCase() + activity.type.slice(1)}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-slate-300">{activity.description}</td>
                      <td className={`py-3 px-4 font-medium ${
                        activity.amount > 0 ? 'text-green-400' : 'text-red-400'
                      }`}>
                        {formatCurrency(Math.abs(activity.amount))}
                      </td>
                      <td className="py-3 px-4 text-slate-400">{activity.timestamp}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default AdvancedDashboard;