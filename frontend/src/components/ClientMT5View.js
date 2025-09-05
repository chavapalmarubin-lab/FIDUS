import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';

const ClientMT5View = ({ clientId }) => {
    const [fundCommitments, setFundCommitments] = useState([]);
    const [summary, setSummary] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (clientId) {
            fetchClientFundCommitments();
        }
    }, [clientId]);

    const fetchClientFundCommitments = async () => {
        try {
            // Fetch client investments (fund commitments) instead of real MT5 data
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/investments/client/${clientId}`);
            const data = await response.json();

            if (data.success) {
                // Group investments by fund for MT5 account mapping display
                const fundGroups = {};
                let totalCommitted = 0;
                let totalCurrentValue = 0;

                data.investments.forEach(investment => {
                    if (!fundGroups[investment.fund_code]) {
                        fundGroups[investment.fund_code] = {
                            fund_code: investment.fund_code,
                            fund_name: investment.fund_name,
                            total_committed: 0,
                            total_current_value: 0,
                            investment_count: 0,
                            investments: []
                        };
                    }

                    fundGroups[investment.fund_code].total_committed += investment.principal_amount;
                    fundGroups[investment.fund_code].total_current_value += investment.current_value;
                    fundGroups[investment.fund_code].investment_count += 1;
                    fundGroups[investment.fund_code].investments.push(investment);

                    totalCommitted += investment.principal_amount;
                    totalCurrentValue += investment.current_value;
                });

                setFundCommitments(Object.values(fundGroups));
                setSummary({
                    total_funds: Object.keys(fundGroups).length,
                    total_committed: totalCommitted,
                    total_current_value: totalCurrentValue,
                    total_gain_loss: totalCurrentValue - totalCommitted,
                    total_gain_loss_percentage: totalCommitted > 0 ? ((totalCurrentValue - totalCommitted) / totalCommitted * 100) : 0
                });
            }

            setLoading(false);
        } catch (error) {
            console.error('Error fetching fund commitments:', error);
            setLoading(false);
        }
    };

    const formatCurrency = (amount) => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 2,
        }).format(amount);
    };

    const formatDate = (dateString) => {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center h-64">
                <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-indigo-600"></div>
            </div>
        );
    }

    return (
        <div className="p-6 max-w-6xl mx-auto">
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-gray-900 mb-2">Your FIDUS Fund Commitments</h1>
                <p className="text-gray-600">Overview of your investments across FIDUS funds</p>
            </div>

            {/* Summary Cards */}
            {summary && (
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                    <Card>
                        <CardContent className="p-6">
                            <div className="text-2xl font-bold text-indigo-600">
                                {summary.total_funds}
                            </div>
                            <div className="text-sm text-gray-600">Funds Invested</div>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardContent className="p-6">
                            <div className="text-2xl font-bold text-blue-600">
                                {formatCurrency(summary.total_committed)}
                            </div>
                            <div className="text-sm text-gray-600">Total Committed</div>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardContent className="p-6">
                            <div className="text-2xl font-bold text-green-600">
                                {formatCurrency(summary.total_current_value)}
                            </div>
                            <div className="text-sm text-gray-600">Current Value</div>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardContent className="p-6">
                            <div className={`text-2xl font-bold ${summary.total_gain_loss >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                {summary.total_gain_loss_percentage.toFixed(2)}%
                            </div>
                            <div className="text-sm text-gray-600">Total Return</div>
                            <div className={`text-xs ${summary.total_gain_loss >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                {formatCurrency(summary.total_gain_loss)}
                            </div>
                        </CardContent>
                    </Card>
                </div>
            )}

            {/* Fund Commitments */}
            <div className="space-y-6">
                {fundCommitments.map((fund) => (
                    <Card key={fund.fund_code}>
                        <CardHeader>
                            <CardTitle className="flex items-center justify-between">
                                <div>
                                    <span className="text-xl">{fund.fund_name}</span>
                                    <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800 ml-3">
                                        {fund.fund_code}
                                    </span>
                                </div>
                                <div className="text-right">
                                    <div className="text-sm text-gray-600">{fund.investment_count} investments</div>
                                    <div className={`text-lg font-semibold ${(fund.total_current_value - fund.total_committed) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                        {formatCurrency(fund.total_current_value - fund.total_committed)}
                                    </div>
                                </div>
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                                <div className="space-y-2">
                                    <div className="flex justify-between">
                                        <span className="text-gray-600">Total Committed:</span>
                                        <span className="font-semibold">{formatCurrency(fund.total_committed)}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-gray-600">Current Value:</span>
                                        <span className="font-semibold">{formatCurrency(fund.total_current_value)}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-gray-600">Gain/Loss:</span>
                                        <span className={`font-semibold ${(fund.total_current_value - fund.total_committed) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                            {formatCurrency(fund.total_current_value - fund.total_committed)}
                                        </span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-gray-600">Return %:</span>
                                        <span className={`font-semibold ${(fund.total_current_value - fund.total_committed) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                            {fund.total_committed > 0 ? (((fund.total_current_value - fund.total_committed) / fund.total_committed) * 100).toFixed(2) : 0}%
                                        </span>
                                    </div>
                                </div>
                                <div className="bg-gray-50 p-4 rounded-lg">
                                    <h4 className="font-semibold text-gray-800 mb-2">Fund Information</h4>
                                    <div className="text-sm text-gray-600 space-y-1">
                                        <div>📈 Professional fund management</div>
                                        <div>🔒 Secure MT5 integration</div>
                                        <div>📊 Real-time performance tracking</div>
                                        <div>💼 Diversified investment strategy</div>
                                    </div>
                                </div>
                            </div>

                            {/* Individual Investments */}
                            <div>
                                <h4 className="font-semibold text-gray-800 mb-3">Investment Details</h4>
                                <div className="overflow-x-auto">
                                    <table className="w-full border-collapse">
                                        <thead>
                                            <tr className="border-b bg-gray-50">
                                                <th className="text-left p-3 font-semibold text-sm">Investment Date</th>
                                                <th className="text-left p-3 font-semibold text-sm">Principal</th>
                                                <th className="text-left p-3 font-semibold text-sm">Current Value</th>
                                                <th className="text-left p-3 font-semibold text-sm">Interest Earned</th>
                                                <th className="text-left p-3 font-semibold text-sm">Status</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {fund.investments.map((investment) => (
                                                <tr key={investment.investment_id} className="border-b hover:bg-gray-50">
                                                    <td className="p-3 text-sm">{formatDate(investment.deposit_date)}</td>
                                                    <td className="p-3 text-sm font-medium">{formatCurrency(investment.principal_amount)}</td>
                                                    <td className="p-3 text-sm font-medium">{formatCurrency(investment.current_value)}</td>
                                                    <td className="p-3 text-sm text-green-600 font-medium">
                                                        {formatCurrency(investment.interest_earned)}
                                                    </td>
                                                    <td className="p-3">
                                                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                                                            investment.status === 'active' 
                                                                ? 'bg-green-100 text-green-800' 
                                                                : 'bg-yellow-100 text-yellow-800'
                                                        }`}>
                                                            {investment.status === 'active' ? 'Earning Interest' : 'Incubating'}
                                                        </span>
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                ))}
            </div>

            {fundCommitments.length === 0 && (
                <Card>
                    <CardContent className="p-8 text-center">
                        <div className="text-gray-500 mb-4">
                            <svg className="mx-auto h-16 w-16 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                            </svg>
                        </div>
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">No Fund Commitments Yet</h3>
                        <p className="text-gray-600">
                            You haven't made any investments in FIDUS funds yet. Contact your investment advisor to get started.
                        </p>
                    </CardContent>
                </Card>
            )}

            {/* Information Card */}
            <Card className="mt-8">
                <CardContent className="p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-3">About MT5 Integration</h3>
                    <div className="text-gray-600 space-y-2">
                        <p>
                            Your FIDUS fund investments are managed through professional MT5 trading accounts. Each fund you invest in 
                            is allocated to a dedicated MT5 account that executes the fund's investment strategy.
                        </p>
                        <p>
                            <strong>Key Benefits:</strong>
                        </p>
                        <ul className="list-disc list-inside space-y-1 ml-4">
                            <li>Professional fund management with MT5 platform</li>
                            <li>Real-time execution of investment strategies</li>
                            <li>Segregated accounts for each fund type</li>
                            <li>Transparent performance tracking</li>
                            <li>Secure integration with Multibank</li>
                        </ul>
                        <p className="text-sm text-gray-500 mt-4">
                            Note: The values shown here reflect your fund commitments and calculated returns based on each fund's performance. 
                            Detailed MT5 trading data is available to administrators for oversight and risk management.
                        </p>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
};

export default ClientMT5View;