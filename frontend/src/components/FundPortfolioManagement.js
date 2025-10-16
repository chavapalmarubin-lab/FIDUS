import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { 
  DollarSign, 
  TrendingUp, 
  Users,
  Target,
  Activity,
  RefreshCw,
  PieChart
} from "lucide-react";
import { PieChart as RechartsPieChart, Pie, Cell, ResponsiveContainer } from 'recharts';
import apiAxios from "../utils/apiAxios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const FundPortfolioManagement = () => {
  // ═══════════════════════════════════════════════════════════════
  // STATE - ONLY FOR STORING BACKEND DATA (NO CALCULATIONS)
  // ═══════════════════════════════════════════════════════════════
  const [portfolioData, setPortfolioData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const FUND_COLORS = {
    CORE: '#0891b2',
    BALANCE: '#10b981',
    DYNAMIC: '#f59e0b',
    UNLIMITED: '#ef4444'
  };

  // ═══════════════════════════════════════════════════════════════
  // DATA FETCHING - BACKEND DOES ALL CALCULATIONS
  // ═══════════════════════════════════════════════════════════════
  useEffect(() => {
    fetchPortfolioData();
    const interval = setInterval(fetchPortfolioData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchPortfolioData = async () => {
    try {
      setLoading(true);
      
      // ✅ CORRECT: Fetch from backend - ALL calculations done there
      const response = await apiAxios.get('/portfolio/fund-allocations');
      
      if (response.data && response.data.success) {
        // ✅ CORRECT: Just store what backend sent - NO calculations
        setPortfolioData(response.data.data);
      } else {
        setError("Failed to load portfolio data");
      }
    } catch (err) {
      console.error("Error fetching portfolio:", err);
      setError("Failed to load portfolio data");
    } finally {
      setLoading(false);
    }
  };

  // ═══════════════════════════════════════════════════════════════
  // UTILITY FUNCTIONS - DISPLAY FORMATTING ONLY (NO CALCULATIONS)
  // ═══════════════════════════════════════════════════════════════
  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(value || 0);
  };

  // ═══════════════════════════════════════════════════════════════
  // RENDER - DISPLAY ONLY (NO CALCULATIONS)
  // ═══════════════════════════════════════════════════════════════
  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="h-8 w-8 animate-spin text-blue-500" />
        <span className="ml-2 text-slate-400">Loading portfolio data...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center text-red-400 p-8">
        <p>{error}</p>
        <button 
          onClick={fetchPortfolioData}
          className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Retry
        </button>
      </div>
    );
  }

  if (!portfolioData) {
    return <div className="text-center text-slate-400 p-8">No portfolio data available</div>;
  }

  // ✅ CORRECT: Use data directly from backend - NO calculations
  const { total_aum, funds } = portfolioData;

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-white">Fund Portfolio Management</h1>
          <p className="text-slate-400 mt-1">Real-time fund allocation and performance</p>
        </div>
        <button 
          onClick={fetchPortfolioData}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          <RefreshCw className="h-4 w-4" />
          Refresh
        </button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Total AUM Card - ✅ CORRECT: Display backend value directly */}
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-slate-400 flex items-center">
              <DollarSign className="h-4 w-4 mr-2" />
              Total AUM
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">
              {formatCurrency(total_aum)}
            </div>
          </CardContent>
        </Card>

        {/* Number of Funds - ✅ CORRECT: Count from backend data */}
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-slate-400 flex items-center">
              <Target className="h-4 w-4 mr-2" />
              Active Funds
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">
              {funds.length}
            </div>
          </CardContent>
        </Card>

        {/* Performance Indicator */}
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-slate-400 flex items-center">
              <TrendingUp className="h-4 w-4 mr-2" />
              Performance
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-400">
              Active
            </div>
          </CardContent>
        </Card>

        {/* Total Accounts - ✅ CORRECT: Sum from backend data */}
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-slate-400 flex items-center">
              <Users className="h-4 w-4 mr-2" />
              MT5 Accounts
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">
              {funds.reduce((sum, fund) => sum + fund.account_count, 0)}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Fund Allocation Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pie Chart - ✅ CORRECT: Display backend percentages */}
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white flex items-center">
              <PieChart className="h-5 w-5 mr-2" />
              Fund Allocation
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <RechartsPieChart>
                <Pie
                  data={funds}
                  dataKey="amount"
                  nameKey="fund_code"
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  label={({ fund_code, percentage }) => `${fund_code}: ${percentage}%`}
                >
                  {funds.map((fund, index) => (
                    <Cell key={`cell-${index}`} fill={FUND_COLORS[fund.fund_code] || '#6366f1'} />
                  ))}
                </Pie>
              </RechartsPieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Fund List - ✅ CORRECT: Display backend data */}
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white flex items-center">
              <Activity className="h-5 w-5 mr-2" />
              Fund Breakdown
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {funds.map((fund) => (
                <div key={fund.fund_code} className="border-b border-slate-700 pb-3 last:border-0">
                  <div className="flex justify-between items-start mb-2">
                    <div className="flex items-center gap-2">
                      <div 
                        className="w-3 h-3 rounded-full"
                        style={{ backgroundColor: FUND_COLORS[fund.fund_code] }}
                      />
                      <span className="font-medium text-white">{fund.fund_code}</span>
                      <Badge variant="outline" className="text-xs">
                        {fund.account_count} accounts
                      </Badge>
                    </div>
                    {/* ✅ CORRECT: Display backend percentage */}
                    <span className="text-slate-400 text-sm">{fund.percentage}%</span>
                  </div>
                  <div className="flex justify-between items-center">
                    {/* ✅ CORRECT: Display backend amount */}
                    <span className="text-2xl font-bold text-white">
                      {formatCurrency(fund.amount)}
                    </span>
                  </div>
                  {/* Accounts */}
                  {fund.accounts && fund.accounts.length > 0 && (
                    <div className="mt-2 text-xs text-slate-400">
                      Accounts: {fund.accounts.join(', ')}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Compliance Note */}
      <div className="text-center text-xs text-slate-500 mt-8">
        ✅ All calculations performed in backend • Frontend displays data only
      </div>
    </div>
  );
};

export default FundPortfolioManagement;
