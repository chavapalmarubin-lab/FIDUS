import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Alert, AlertDescription } from './ui/alert';
import { Badge } from './ui/badge';
import { 
    TrendingUp, 
    TrendingDown, 
    AlertTriangle,
    DollarSign,
    BarChart3,
    Users,
    Target,
    Activity,
    ArrowUpCircle,
    ArrowDownCircle,
    RefreshCw,
    CheckCircle,
    XCircle
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts';

const FundPerformanceDashboard = () => {
    const [dashboardData, setDashboardData] = useState(null);
    const [performanceGaps, setPerformanceGaps] = useState([]);
    const [fundCommitments, setFundCommitments] = useState({});
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [selectedView, setSelectedView] = useState('overview');
    const [autoRefresh, setAutoRefresh] = useState(true);

    useEffect(() => {
        fetchDashboardData();
        
        // Auto-refresh every 30 seconds if enabled
        let interval;
        if (autoRefresh) {
            interval = setInterval(fetchDashboardData, 30000);
        }
        
        return () => {
            if (interval) clearInterval(interval);
        };
    }, [autoRefresh]);

    const fetchDashboardData = async () => {
        try {
            setError('');
            
            const token = JSON.parse(localStorage.getItem('fidus_user')).token;
            const headers = {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            };

            // Fetch fund performance dashboard
            const dashboardResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/fund-performance/dashboard`, {
                headers
            });

            // Fetch performance gaps
            const gapsResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/fund-performance/gaps`, {
                headers
            });

            // Fetch fund commitments
            const commitmentsResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/fund-commitments`, {
                headers
            });

            if (dashboardResponse.ok && gapsResponse.ok && commitmentsResponse.ok) {
                const dashboardData = await dashboardResponse.json();
                const gapsData = await gapsResponse.json();
                const commitmentsData = await commitmentsResponse.json();

                setDashboardData(dashboardData.dashboard);
                setPerformanceGaps(gapsData.performance_gaps || []);
                setFundCommitments(commitmentsData.fund_commitments || {});
            } else {
                setError('Failed to load fund performance data');
            }
        } catch (err) {
            setError('Error connecting to fund performance API');
            console.error('Fund performance fetch error:', err);
        } finally {
            setLoading(false);
        }
    };

    const formatCurrency = (amount) => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(amount || 0);
    };

    const getRiskColor = (riskLevel) => {
        switch (riskLevel?.toUpperCase()) {
            case 'CRITICAL': return 'bg-red-600 text-white';
            case 'HIGH': return 'bg-orange-600 text-white';
            case 'MEDIUM': return 'bg-yellow-600 text-black';
            case 'LOW': return 'bg-green-600 text-white';
            default: return 'bg-gray-600 text-white';
        }
    };

    const getGapIcon = (gapAmount) => {
        if (gapAmount > 0) {
            return <ArrowUpCircle className="text-green-500" size={20} />;
        } else if (gapAmount < 0) {
            return <ArrowDownCircle className="text-red-500" size={20} />;
        }
        return <CheckCircle className="text-blue-500" size={20} />;
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center p-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-400"></div>
                <span className="ml-2 text-slate-400">Loading fund performance data...</span>
            </div>
        );
    }

    return (
        <div className="fund-performance-dashboard p-6 space-y-6">
            {/* Header */}
            <div className="flex justify-between items-center">
                <div>
                    <h2 className="text-2xl font-bold text-white mb-2">Fund Performance vs MT5 Reality</h2>
                    <p className="text-slate-400">Compare FIDUS fund commitments with actual MT5 trading performance</p>
                </div>
                <div className="flex gap-3">
                    <Button
                        variant={autoRefresh ? "default" : "outline"}
                        onClick={() => setAutoRefresh(!autoRefresh)}
                        className="bg-blue-600 hover:bg-blue-700"
                    >
                        <RefreshCw size={16} className={autoRefresh ? "animate-spin" : ""} />
                        Auto Refresh
                    </Button>
                    <Button onClick={fetchDashboardData} className="bg-cyan-600 hover:bg-cyan-700">
                        Refresh Now
                    </Button>
                </div>
            </div>

            {error && (
                <Alert className="border-red-500 bg-red-500/10">
                    <AlertTriangle className="h-4 w-4" />
                    <AlertDescription className="text-red-400">{error}</AlertDescription>
                </Alert>
            )}

            {/* View Selector */}
            <div className="flex gap-2">
                <Button
                    variant={selectedView === 'overview' ? 'default' : 'outline'}
                    onClick={() => setSelectedView('overview')}
                >
                    Overview
                </Button>
                <Button
                    variant={selectedView === 'gaps' ? 'default' : 'outline'}
                    onClick={() => setSelectedView('gaps')}
                >
                    Performance Gaps
                </Button>
                <Button
                    variant={selectedView === 'commitments' ? 'default' : 'outline'}
                    onClick={() => setSelectedView('commitments')}
                >
                    Fund Commitments
                </Button>
            </div>

            {/* Overview View */}
            {selectedView === 'overview' && (
                <>
                    {/* Key Metrics */}
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                        <Card className="bg-slate-800 border-slate-700">
                            <CardContent className="p-4">
                                <div className="flex items-center">
                                    <Target className="h-8 w-8 text-blue-500" />
                                    <div className="ml-4">
                                        <p className="text-sm font-medium text-slate-400">Active Positions</p>
                                        <p className="text-2xl font-bold text-white">{performanceGaps.length}</p>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>

                        <Card className="bg-slate-800 border-slate-700">
                            <CardContent className="p-4">
                                <div className="flex items-center">
                                    <AlertTriangle className="h-8 w-8 text-orange-500" />
                                    <div className="ml-4">
                                        <p className="text-sm font-medium text-slate-400">Action Required</p>
                                        <p className="text-2xl font-bold text-white">
                                            {performanceGaps.filter(gap => gap.action_required).length}
                                        </p>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>

                        <Card className="bg-slate-800 border-slate-700">
                            <CardContent className="p-4">
                                <div className="flex items-center">
                                    <DollarSign className="h-8 w-8 text-green-500" />
                                    <div className="ml-4">
                                        <p className="text-sm font-medium text-slate-400">Total Gap</p>
                                        <p className="text-2xl font-bold text-white">
                                            {formatCurrency(performanceGaps.reduce((sum, gap) => sum + gap.gap_amount, 0))}
                                        </p>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>

                        <Card className="bg-slate-800 border-slate-700">
                            <CardContent className="p-4">
                                <div className="flex items-center">
                                    <Activity className="h-8 w-8 text-cyan-500" />
                                    <div className="ml-4">
                                        <p className="text-sm font-medium text-slate-400">Avg Gap %</p>
                                        <p className="text-2xl font-bold text-white">
                                            {performanceGaps.length > 0 
                                                ? (performanceGaps.reduce((sum, gap) => sum + gap.gap_percentage, 0) / performanceGaps.length).toFixed(1)
                                                : 0}%
                                        </p>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    </div>

                    {/* Risk Summary */}
                    {dashboardData?.risk_summary && (
                        <Card className="bg-slate-800 border-slate-700">
                            <CardHeader>
                                <CardTitle className="text-white">Risk Distribution</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                    {Object.entries(dashboardData.risk_summary).map(([riskLevel, count]) => (
                                        <div key={riskLevel} className="text-center">
                                            <Badge className={`${getRiskColor(riskLevel)} mb-2`}>
                                                {riskLevel}
                                            </Badge>
                                            <p className="text-2xl font-bold text-white">{count}</p>
                                            <p className="text-sm text-slate-400">positions</p>
                                        </div>
                                    ))}
                                </div>
                            </CardContent>
                        </Card>
                    )}

                    {/* Action Items */}
                    {dashboardData?.action_items && dashboardData.action_items.length > 0 && (
                        <Card className="bg-slate-800 border-slate-700">
                            <CardHeader>
                                <CardTitle className="text-white">Action Items</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-3">
                                    {dashboardData.action_items.map((item, index) => (
                                        <div key={index} className="p-4 bg-slate-750 rounded-lg">
                                            <div className="flex justify-between items-start">
                                                <div>
                                                    <div className="flex items-center gap-2 mb-2">
                                                        <Badge className={item.priority === 'HIGH' ? 'bg-red-600' : 'bg-orange-600'}>
                                                            {item.priority}
                                                        </Badge>
                                                        <span className="text-white font-medium">
                                                            {item.client_id} - {item.fund_code}
                                                        </span>
                                                    </div>
                                                    <p className="text-slate-300 mb-2">{item.issue}</p>
                                                    <p className="text-sm text-slate-400">{item.recommendation}</p>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </CardContent>
                        </Card>
                    )}
                </>
            )}

            {/* Performance Gaps View */}
            {selectedView === 'gaps' && (
                <Card className="bg-slate-800 border-slate-700">
                    <CardHeader>
                        <CardTitle className="text-white">Performance Gaps Analysis</CardTitle>
                        <p className="text-slate-400">FIDUS Commitments vs MT5 Actual Performance</p>
                    </CardHeader>
                    <CardContent>
                        <div className="overflow-x-auto">
                            <table className="w-full">
                                <thead>
                                    <tr className="border-b border-slate-600">
                                        <th className="text-left py-3 px-4 text-slate-300">Client</th>
                                        <th className="text-left py-3 px-4 text-slate-300">Fund</th>
                                        <th className="text-left py-3 px-4 text-slate-300">Expected</th>
                                        <th className="text-left py-3 px-4 text-slate-300">Actual MT5</th>
                                        <th className="text-left py-3 px-4 text-slate-300">Gap</th>
                                        <th className="text-left py-3 px-4 text-slate-300">Gap %</th>
                                        <th className="text-left py-3 px-4 text-slate-300">Risk</th>
                                        <th className="text-left py-3 px-4 text-slate-300">Action</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {performanceGaps.map((gap, index) => (
                                        <tr key={index} className="border-b border-slate-700 hover:bg-slate-750">
                                            <td className="py-3 px-4 text-white">{gap.client_id}</td>
                                            <td className="py-3 px-4">
                                                <Badge className="bg-blue-600 text-white">
                                                    {gap.fund_code}
                                                </Badge>
                                            </td>
                                            <td className="py-3 px-4 text-white">
                                                {formatCurrency(gap.expected_performance)}
                                            </td>
                                            <td className="py-3 px-4 text-white">
                                                {formatCurrency(gap.actual_mt5_performance)}
                                            </td>
                                            <td className="py-3 px-4">
                                                <div className="flex items-center gap-2">
                                                    {getGapIcon(gap.gap_amount)}
                                                    <span className={`font-medium ${gap.gap_amount >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                                        {formatCurrency(gap.gap_amount)}
                                                    </span>
                                                </div>
                                            </td>
                                            <td className="py-3 px-4">
                                                <span className={`font-medium ${gap.gap_percentage >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                                    {gap.gap_percentage.toFixed(1)}%
                                                </span>
                                            </td>
                                            <td className="py-3 px-4">
                                                <Badge className={getRiskColor(gap.risk_level)}>
                                                    {gap.risk_level}
                                                </Badge>
                                            </td>
                                            <td className="py-3 px-4">
                                                {gap.action_required ? (
                                                    <CheckCircle className="text-orange-500" size={20} />
                                                ) : (
                                                    <XCircle className="text-green-500" size={20} />
                                                )}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </CardContent>
                </Card>
            )}

            {/* Fund Commitments View */}
            {selectedView === 'commitments' && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {Object.entries(fundCommitments).map(([fundCode, commitment]) => (
                        <Card key={fundCode} className="bg-slate-800 border-slate-700">
                            <CardHeader>
                                <CardTitle className="text-white flex items-center gap-2">
                                    <Badge className="bg-blue-600 text-white">{fundCode}</Badge>
                                    Fund Commitment
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-4">
                                    <div className="grid grid-cols-2 gap-4">
                                        <div>
                                            <p className="text-sm text-slate-400">Monthly Return</p>
                                            <p className="text-xl font-bold text-green-400">
                                                {commitment.monthly_return}%
                                            </p>
                                        </div>
                                        <div>
                                            <p className="text-sm text-slate-400">Redemption Frequency</p>
                                            <p className="text-xl font-bold text-white">
                                                {commitment.redemption_frequency} months
                                            </p>
                                        </div>
                                    </div>
                                    
                                    <div className="grid grid-cols-2 gap-4">
                                        <div>
                                            <p className="text-sm text-slate-400">Risk Level</p>
                                            <Badge className={getRiskColor(commitment.risk_level)}>
                                                {commitment.risk_level}
                                            </Badge>
                                        </div>
                                        <div>
                                            <p className="text-sm text-slate-400">Guaranteed</p>
                                            <Badge className={commitment.guaranteed ? 'bg-green-600' : 'bg-orange-600'}>
                                                {commitment.guaranteed ? 'Yes' : 'No'}
                                            </Badge>
                                        </div>
                                    </div>
                                    
                                    {commitment.minimum_investment && (
                                        <div>
                                            <p className="text-sm text-slate-400">Minimum Investment</p>
                                            <p className="text-lg font-bold text-white">
                                                {formatCurrency(commitment.minimum_investment)}
                                            </p>
                                        </div>
                                    )}
                                    
                                    <div>
                                        <p className="text-sm text-slate-400">Description</p>
                                        <p className="text-white">{commitment.description}</p>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    ))}
                </div>
            )}
        </div>
    );
};

export default FundPerformanceDashboard;