import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Alert, AlertDescription } from './ui/alert';
import { 
    DollarSign, 
    Calendar, 
    Shield, 
    TrendingUp, 
    Clock,
    Users,
    AlertCircle,
    CheckCircle,
    ArrowLeft
} from 'lucide-react';
import apiAxios from '../utils/apiAxios';

const InvestmentDetailView = ({ investmentId, onBack }) => {
    const [investment, setInvestment] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (investmentId) {
            fetchInvestmentDetails();
        }
    }, [investmentId]);

    const fetchInvestmentDetails = async () => {
        try {
            setLoading(true);
            const response = await apiAxios.get(`/investments/${investmentId}`);
            setInvestment(response.data);
        } catch (err) {
            console.error('Error fetching investment details:', err);
            setError('Failed to load investment details');
        } finally {
            setLoading(false);
        }
    };

    const formatDate = (dateString) => {
        if (!dateString) return 'N/A';
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    };

    const formatCurrency = (amount) => {
        if (!amount) return '$0.00';
        return new Decimal(amount).toFixed(2);
    };

    const getStatusColor = (status) => {
        switch(status?.toLowerCase()) {
            case 'incubation':
                return 'bg-yellow-500';
            case 'active':
                return 'bg-green-500';
            case 'completed':
                return 'bg-blue-500';
            case 'cancelled':
                return 'bg-red-500';
            default:
                return 'bg-gray-500';
        }
    };

    const getStatusIcon = (status) => {
        switch(status?.toLowerCase()) {
            case 'incubation':
                return <Clock className="h-4 w-4" />;
            case 'active':
                return <CheckCircle className="h-4 w-4" />;
            case 'completed':
                return <TrendingUp className="h-4 w-4" />;
            case 'cancelled':
                return <AlertCircle className="h-4 w-4" />;
            default:
                return <Clock className="h-4 w-4" />;
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-500 mx-auto"></div>
                    <p className="text-slate-400 mt-2">Loading investment details...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
            </Alert>
        );
    }

    if (!investment) {
        return (
            <Alert>
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>Investment not found</AlertDescription>
            </Alert>
        );
    }

    const isIncubationPeriod = investment.status?.toLowerCase() === 'incubation';
    const daysUntilInterest = investment.interest_start_date 
        ? Math.ceil((new Date(investment.interest_start_date) - new Date()) / (1000 * 60 * 60 * 24))
        : null;

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center gap-4">
                <Button variant="ghost" onClick={onBack} className="text-slate-400 hover:text-white">
                    <ArrowLeft className="h-4 w-4 mr-2" />
                    Back to Investments
                </Button>
            </div>

            {/* Investment Summary */}
            <Card className="bg-slate-800 border-slate-700">
                <CardHeader>
                    <div className="flex items-center justify-between">
                        <CardTitle className="text-white flex items-center gap-2">
                            <DollarSign className="h-5 w-5" />
                            Investment Summary
                        </CardTitle>
                        <Badge className={`${getStatusColor(investment.status)} text-white`}>
                            {getStatusIcon(investment.status)}
                            <span className="ml-1 capitalize">{investment.status}</span>
                        </Badge>
                    </div>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="p-4 bg-slate-700 rounded-lg">
                            <h4 className="text-slate-400 text-sm">Client</h4>
                            <p className="text-white font-medium">{investment.client_name || investment.client_id}</p>
                        </div>
                        <div className="p-4 bg-slate-700 rounded-lg">
                            <h4 className="text-slate-400 text-sm">Product</h4>
                            <p className="text-white font-medium">FIDUS {investment.fund_code}</p>
                        </div>
                        <div className="p-4 bg-slate-700 rounded-lg">
                            <h4 className="text-slate-400 text-sm">Principal Amount</h4>
                            <p className="text-white font-medium text-xl">${formatCurrency(investment.principal_amount)}</p>
                        </div>
                    </div>

                    {isIncubationPeriod && (
                        <Alert className="border-yellow-500 bg-yellow-950/50">
                            <Clock className="h-4 w-4 text-yellow-500" />
                            <AlertDescription className="text-yellow-200">
                                <strong>Incubation Period:</strong> This investment is in its 2-month incubation period.
                                {daysUntilInterest && daysUntilInterest > 0 && (
                                    <span> Interest payments will begin in {daysUntilInterest} days.</span>
                                )}
                            </AlertDescription>
                        </Alert>
                    )}
                </CardContent>
            </Card>

            {/* Investment Timeline */}
            <Card className="bg-slate-800 border-slate-700">
                <CardHeader>
                    <CardTitle className="text-white flex items-center gap-2">
                        <Calendar className="h-5 w-5" />
                        Investment Timeline
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="space-y-3">
                            <div>
                                <h4 className="text-slate-400 text-sm">Creation Date</h4>
                                <p className="text-white">{formatDate(investment.creation_date)}</p>
                            </div>
                            <div>
                                <h4 className="text-slate-400 text-sm">Incubation Period</h4>
                                <p className="text-white">
                                    {formatDate(investment.incubation_start_date)} - {formatDate(investment.incubation_end_date)}
                                </p>
                            </div>
                            <div>
                                <h4 className="text-slate-400 text-sm">Interest Payments Begin</h4>
                                <p className="text-white">{formatDate(investment.interest_start_date)}</p>
                            </div>
                        </div>
                        <div className="space-y-3">
                            <div>
                                <h4 className="text-slate-400 text-sm">Next Redemption Date</h4>
                                <p className="text-white">{formatDate(investment.next_redemption_date)}</p>
                            </div>
                            <div>
                                <h4 className="text-slate-400 text-sm">Contract End Date</h4>
                                <p className="text-white">{formatDate(investment.contract_end_date)}</p>
                            </div>
                            <div>
                                <h4 className="text-slate-400 text-sm">Next Interest Payment</h4>
                                <p className="text-white">{formatDate(investment.next_interest_payment_date)}</p>
                            </div>
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* MT5 Account Allocations */}
            <Card className="bg-slate-800 border-slate-700">
                <CardHeader>
                    <CardTitle className="text-white flex items-center gap-2">
                        <Shield className="h-5 w-5" />
                        MT5 Account Allocations
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    {investment.mt5_accounts && investment.mt5_accounts.length > 0 ? (
                        <div className="space-y-3">
                            {investment.mt5_accounts.map((account, index) => (
                                <div key={index} className="p-4 bg-slate-700 rounded-lg">
                                    <div className="flex items-center justify-between">
                                        <div>
                                            <h4 className="text-white font-medium">MT5 Account #{account.mt5_account_number}</h4>
                                            <p className="text-slate-400 text-sm">{account.broker_name} • {account.mt5_server}</p>
                                        </div>
                                        <div className="text-right">
                                            <p className="text-white font-medium">${formatCurrency(account.allocated_amount)}</p>
                                            <p className="text-slate-400 text-sm">
                                                {((account.allocated_amount / investment.principal_amount) * 100).toFixed(1)}%
                                            </p>
                                        </div>
                                    </div>
                                    {account.allocation_notes && (
                                        <p className="text-slate-300 text-sm mt-2">{account.allocation_notes}</p>
                                    )}
                                </div>
                            ))}
                        </div>
                    ) : (
                        <p className="text-slate-400">No MT5 allocations found</p>
                    )}
                </CardContent>
            </Card>

            {/* Separation Accounts */}
            {(investment.interest_separation_account || investment.gains_separation_account) && (
                <Card className="bg-slate-800 border-slate-700">
                    <CardHeader>
                        <CardTitle className="text-white flex items-center gap-2">
                            <Users className="h-5 w-5" />
                            Separation Tracking Accounts
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {investment.interest_separation_account && (
                                <div className="p-4 bg-slate-700 rounded-lg">
                                    <h4 className="text-white font-medium mb-2">Interest Separation</h4>
                                    <p className="text-slate-300">MT5 Account #{investment.interest_separation_account.mt5_account_number}</p>
                                    <p className="text-slate-400 text-sm">{investment.interest_separation_account.broker_name}</p>
                                </div>
                            )}
                            {investment.gains_separation_account && (
                                <div className="p-4 bg-slate-700 rounded-lg">
                                    <h4 className="text-white font-medium mb-2">Gains Separation</h4>
                                    <p className="text-slate-300">MT5 Account #{investment.gains_separation_account.mt5_account_number}</p>
                                    <p className="text-slate-400 text-sm">{investment.gains_separation_account.broker_name}</p>
                                </div>
                            )}
                        </div>
                    </CardContent>
                </Card>
            )}

            {/* Financial Tracking */}
            <Card className="bg-slate-800 border-slate-700">
                <CardHeader>
                    <CardTitle className="text-white flex items-center gap-2">
                        <TrendingUp className="h-5 w-5" />
                        Financial Performance
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="p-4 bg-slate-700 rounded-lg text-center">
                            <h4 className="text-slate-400 text-sm">Current Value</h4>
                            <p className="text-white font-medium text-xl">${formatCurrency(investment.current_value)}</p>
                        </div>
                        <div className="p-4 bg-slate-700 rounded-lg text-center">
                            <h4 className="text-slate-400 text-sm">Total Interest Paid</h4>
                            <p className="text-white font-medium text-xl">${formatCurrency(investment.total_interest_paid)}</p>
                        </div>
                        <div className="p-4 bg-slate-700 rounded-lg text-center">
                            <h4 className="text-slate-400 text-sm">Total Return</h4>
                            <p className="text-white font-medium text-xl">
                                {investment.current_value && investment.principal_amount 
                                    ? `${(((investment.current_value - investment.principal_amount) / investment.principal_amount) * 100).toFixed(2)}%`
                                    : 'N/A'
                                }
                            </p>
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
};

export default InvestmentDetailView;