import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Alert, AlertDescription } from '../components/ui/alert';
import { Badge } from '../components/ui/badge';
import {
    Plus, X, AlertCircle, DollarSign, Shield, Eye, EyeOff,
    CheckCircle, XCircle, Calculator, Users, Building2
} from 'lucide-react';
import apiAxios from '../utils/apiAxios';

// Helper functions for date calculations
const addMonths = (date, months) => {
    const newDate = new Date(date);
    newDate.setMonth(newDate.getMonth() + months);
    return newDate;
};

const calculateNextRedemption = (product, startDate) => {
    switch(product) {
        case 'CORE':
            return addMonths(startDate, 3); // Monthly after 2 month incubation + 1 month
        case 'BALANCE':
            return addMonths(startDate, 5); // Quarterly after 2 month incubation + 3 months
        case 'DYNAMIC':
            return addMonths(startDate, 8); // Semi-annual after 2 month incubation + 6 months
        case 'UNLIMITED':
            return addMonths(startDate, 14); // At contract end
        default:
            return addMonths(startDate, 3);
    }
};

const InvestmentCreationWithMT5 = () => {
    console.log('🚀 InvestmentCreationWithMT5 COMPONENT MOUNTED');
    
    // Form state
    const [formData, setFormData] = useState({
        client_id: '',
        fund_code: 'CORE',
        principal_amount: '',
        currency: 'USD',
        notes: '',
        creation_notes: '',
        mt5_accounts: [{
            mt5_account_number: '',
            investor_password: '',
            broker_name: 'MULTIBANK',
            allocated_amount: '',
            allocation_notes: '',
            mt5_server: ''
        }],
        interest_separation_account: {
            mt5_account_number: '',
            investor_password: '',
            broker_name: 'MULTIBANK',
            mt5_server: '',
            notes: ''
        },
        gains_separation_account: {
            mt5_account_number: '',
            investor_password: '',
            broker_name: 'MULTIBANK',
            mt5_server: '',
            notes: ''
        }
    });

    const [validation, setValidation] = useState({
        totalAllocated: 0,
        isValid: false,
        errors: [],
        accountAvailability: {}
    });

    const [showPasswords, setShowPasswords] = useState({});
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [submitResult, setSubmitResult] = useState(null);
    const [clients, setClients] = useState([]);
    const [loading, setLoading] = useState(false);

    // Fund configurations
    const fundConfigs = {
        CORE: {
            name: 'FIDUS CORE',
            minimum: 10000,
            monthlyReturn: 1.5,
            redemption: 'Monthly redemptions'
        },
        BALANCE: {
            name: 'FIDUS BALANCE',
            minimum: 50000,
            monthlyReturn: 2.5,
            redemption: 'Quarterly redemptions'
        },
        DYNAMIC: {
            name: 'FIDUS DYNAMIC',
            minimum: 250000,
            monthlyReturn: 3.5,
            redemption: 'Semi-annual redemptions'
        },
        UNLIMITED: {
            name: 'FIDUS UNLIMITED',
            minimum: 100000,
            monthlyReturn: 4.0,
            redemption: 'TBD'
        }
    };

    const brokers = [
        { value: 'MULTIBANK', label: 'Multibank', server: 'MultiBank-Live' },
        { value: 'DOOTECHNOLOGY', label: 'DooTechnology', server: 'DooTechnology-Live' },
        { value: 'VTMARKETS', label: 'VT Markets', server: 'VTMarkets-Live' }
    ];

    // Load clients on component mount
    useEffect(() => {
        fetchClients();
    }, []);

    // Recalculate validation when MT5 accounts or principal amount changes
    useEffect(() => {
        calculateValidation();
    }, [formData.mt5_accounts, formData.principal_amount]);

    const fetchClients = async () => {
        try {
            const response = await apiAxios.get('/users');
            setClients(response.data.filter(user => user.type === 'client'));
        } catch (error) {
            console.error('Error fetching clients:', error);
        }
    };

    const calculateValidation = () => {
        const totalAllocated = formData.mt5_accounts.reduce((sum, account) => {
            return sum + (parseFloat(account.allocated_amount) || 0);
        }, 0);

        const principalAmount = parseFloat(formData.principal_amount) || 0;
        const difference = Math.abs(totalAllocated - principalAmount);
        const isValid = difference < 0.01 && principalAmount > 0 && totalAllocated > 0;

        const errors = [];
        if (principalAmount > 0 && totalAllocated === 0) {
            errors.push('Add at least one MT5 account allocation');
        }
        if (principalAmount > 0 && difference >= 0.01) {
            errors.push(`Allocation difference: $${difference.toFixed(2)} (must be $0.00)`);
        }

        // Check fund minimum
        const fundConfig = fundConfigs[formData.fund_code];
        if (principalAmount > 0 && principalAmount < fundConfig.minimum) {
            errors.push(`Minimum investment for ${fundConfig.name} is $${fundConfig.minimum.toLocaleString()}`);
        }

        setValidation({
            totalAllocated,
            isValid,
            errors,
            accountAvailability: validation.accountAvailability
        });
    };

    const checkAccountAvailability = async (accountNumber, index) => {
        if (!accountNumber || accountNumber.length < 6) return;

        try {
            const response = await apiAxios.post('/mt5/pool/validate-account-availability', {
                mt5_account_number: parseInt(accountNumber)
            });

            setValidation(prev => ({
                ...prev,
                accountAvailability: {
                    ...prev.accountAvailability,
                    [accountNumber]: response.data
                }
            }));
        } catch (error) {
            console.error('Error checking account availability:', error);
            setValidation(prev => ({
                ...prev,
                accountAvailability: {
                    ...prev.accountAvailability,
                    [accountNumber]: {
                        is_available: false,
                        reason: 'Error checking availability'
                    }
                }
            }));
        }
    };

    const addMT5Account = () => {
        setFormData(prev => ({
            ...prev,
            mt5_accounts: [
                ...prev.mt5_accounts,
                {
                    mt5_account_number: '',
                    investor_password: '',
                    broker_name: 'MULTIBANK',
                    allocated_amount: '',
                    allocation_notes: '',
                    mt5_server: ''
                }
            ]
        }));
    };

    const removeMT5Account = (index) => {
        setFormData(prev => ({
            ...prev,
            mt5_accounts: prev.mt5_accounts.filter((_, i) => i !== index)
        }));
    };

    const updateMT5Account = (index, field, value) => {
        setFormData(prev => {
            const updated = [...prev.mt5_accounts];
            updated[index] = { ...updated[index], [field]: value };

            // Auto-set MT5 server based on broker
            if (field === 'broker_name') {
                const broker = brokers.find(b => b.value === value);
                updated[index].mt5_server = broker ? broker.server : '';
            }

            return { ...prev, mt5_accounts: updated };
        });

        // Check availability when account number changes
        if (field === 'mt5_account_number') {
            checkAccountAvailability(value, index);
        }
    };

    const updateSeparationAccount = (type, field, value) => {
        setFormData(prev => {
            const updated = { ...prev[type] };
            updated[field] = value;

            // Auto-set MT5 server based on broker
            if (field === 'broker_name') {
                const broker = brokers.find(b => b.value === value);
                updated.mt5_server = broker ? broker.server : '';
            }

            return { ...prev, [type]: updated };
        });
    };

    const togglePasswordVisibility = (accountIndex) => {
        setShowPasswords(prev => ({
            ...prev,
            [accountIndex]: !prev[accountIndex]
        }));
    };

    const submitInvestment = async () => {
        if (!validation.isValid) {
            alert('Please fix validation errors before submitting');
            return;
        }

        setIsSubmitting(true);
        setSubmitResult(null);

        try {
            const currentDate = new Date();
            const submissionData = {
                ...formData,
                principal_amount: parseFloat(formData.principal_amount),
                mt5_accounts: formData.mt5_accounts.map(acc => ({
                    ...acc,
                    mt5_account_number: parseInt(acc.mt5_account_number),
                    allocated_amount: parseFloat(acc.allocated_amount)
                })),
                interest_separation_account: formData.interest_separation_account.mt5_account_number ? {
                    ...formData.interest_separation_account,
                    mt5_account_number: parseInt(formData.interest_separation_account.mt5_account_number),
                    account_type: 'INTEREST_SEPARATION'
                } : null,
                gains_separation_account: formData.gains_separation_account.mt5_account_number ? {
                    ...formData.gains_separation_account,
                    mt5_account_number: parseInt(formData.gains_separation_account.mt5_account_number),
                    account_type: 'GAINS_SEPARATION'
                } : null,
                // Investment timeline and status
                creation_date: currentDate.toISOString(),
                incubation_start_date: currentDate.toISOString(),
                incubation_end_date: addMonths(currentDate, 2).toISOString(),
                interest_start_date: addMonths(currentDate, 2).toISOString(),
                contract_end_date: addMonths(currentDate, 14).toISOString(),
                next_redemption_date: calculateNextRedemption(formData.fund_code, currentDate).toISOString(),
                status: 'incubation',
                current_value: parseFloat(formData.principal_amount),
                total_interest_paid: 0.00,
                last_interest_payment_date: null,
                next_interest_payment_date: addMonths(currentDate, 2).toISOString()
            };

            const response = await apiAxios.post('/mt5/pool/create-investment-with-mt5', submissionData);

            setSubmitResult({
                success: true,
                data: response.data,
                message: `✅ Investment ${response.data.investment_id} created successfully!`
            });

            // Reset form
            setFormData({
                client_id: '',
                fund_code: 'CORE',
                principal_amount: '',
                currency: 'USD',
                notes: '',
                creation_notes: '',
                mt5_accounts: [{
                    mt5_account_number: '',
                    investor_password: '',
                    broker_name: 'MULTIBANK',
                    allocated_amount: '',
                    allocation_notes: '',
                    mt5_server: ''
                }],
                interest_separation_account: {
                    mt5_account_number: '',
                    investor_password: '',
                    broker_name: 'MULTIBANK',
                    mt5_server: '',
                    notes: ''
                },
                gains_separation_account: {
                    mt5_account_number: '',
                    investor_password: '',
                    broker_name: 'MULTIBANK',
                    mt5_server: '',
                    notes: ''
                }
            });

        } catch (error) {
            console.error('Error creating investment:', error);
            setSubmitResult({
                success: false,
                message: error.response?.data?.detail || 'Failed to create investment',
                error: error
            });
        } finally {
            setIsSubmitting(false);
        }
    };

    const getAvailabilityBadge = (accountNumber) => {
        const availability = validation.accountAvailability[accountNumber];
        if (!availability) return null;

        if (availability.is_available) {
            return <Badge className="bg-green-600 text-white">✓ Available</Badge>;
        } else {
            return <Badge className="bg-red-600 text-white">✗ {availability.reason}</Badge>;
        }
    };

    return (
        <div className="investment-creation p-6 max-w-6xl mx-auto">
            {/* Header */}
            <div className="mb-6">
                <h1 className="text-3xl font-bold text-white mb-2">Create Investment with MT5 Accounts</h1>
                <p className="text-slate-400">Enter investment details and MT5 account allocations in one step</p>
            </div>

            {/* CRITICAL INVESTOR PASSWORD WARNING */}
            <Alert className="mb-6 border-red-500 bg-red-950/50">
                <AlertCircle className="h-5 w-5 text-red-400" />
                <AlertDescription className="text-red-200 font-bold text-base">
                    🚨 CRITICAL SYSTEM REQUIREMENT 🚨
                    <br />
                    This system ONLY accepts INVESTOR PASSWORDS for all MT5 accounts
                    <br />
                    <strong>DO NOT enter trading passwords - they will not function in this system</strong>
                </AlertDescription>
            </Alert>

            {/* Success/Error Messages */}
            {submitResult && (
                <Alert className={`mb-6 ${submitResult.success ? 'border-green-500 bg-green-950/50' : 'border-red-500 bg-red-950/50'}`}>
                    {submitResult.success ? <CheckCircle className="h-4 w-4 text-green-400" /> : <XCircle className="h-4 w-4 text-red-400" />}
                    <AlertDescription className={submitResult.success ? 'text-green-200' : 'text-red-200'}>
                        {submitResult.message}
                    </AlertDescription>
                </Alert>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Main Form */}
                <div className="lg:col-span-2 space-y-6">
                    {/* Investment Details */}
                    <Card className="bg-slate-800 border-slate-700">
                        <CardHeader>
                            <h2 className="text-xl font-semibold text-white flex items-center gap-2">
                                <Building2 className="h-5 w-5" />
                                Investment Details
                            </h2>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            {/* Client Selection */}
                            <div>
                                <Label className="text-slate-300">Client *</Label>
                                <select
                                    value={formData.client_id}
                                    onChange={(e) => setFormData(prev => ({ ...prev, client_id: e.target.value }))}
                                    className="w-full bg-slate-700 border-slate-600 text-white rounded px-3 py-2"
                                >
                                    <option value="">Select Client</option>
                                    {clients.map(client => (
                                        <option key={client.id} value={client.id}>
                                            {client.full_name} ({client.id})
                                        </option>
                                    ))}
                                </select>
                            </div>

                            {/* Fund Selection */}
                            <div>
                                <Label className="text-slate-300">Investment Product *</Label>
                                <select
                                    value={formData.fund_code}
                                    onChange={(e) => setFormData(prev => ({ ...prev, fund_code: e.target.value }))}
                                    className="w-full bg-slate-700 border-slate-600 text-white rounded px-3 py-2"
                                >
                                    {Object.entries(fundConfigs).map(([code, config]) => (
                                        <option key={code} value={code}>
                                            {config.name} - ${config.minimum.toLocaleString()} min | {config.monthlyReturn}% monthly
                                        </option>
                                    ))}
                                </select>
                                <p className="text-xs text-slate-400 mt-1">
                                    {fundConfigs[formData.fund_code].redemption}
                                </p>
                            </div>

                            {/* Investment Amount */}
                            <div>
                                <Label className="text-slate-300">Total Investment Amount *</Label>
                                <div className="relative">
                                    <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
                                    <Input
                                        type="number"
                                        value={formData.principal_amount}
                                        onChange={(e) => setFormData(prev => ({ ...prev, principal_amount: e.target.value }))}
                                        className="bg-slate-700 border-slate-600 text-white pl-10"
                                        placeholder="100000.00"
                                        step="0.01"
                                    />
                                </div>
                                <p className="text-xs text-slate-400 mt-1">
                                    Minimum: ${fundConfigs[formData.fund_code].minimum.toLocaleString()}
                                </p>
                            </div>

                            {/* Creation Notes */}
                            <div>
                                <Label className="text-slate-300">Investment Strategy Notes *</Label>
                                <textarea
                                    value={formData.creation_notes}
                                    onChange={(e) => setFormData(prev => ({ ...prev, creation_notes: e.target.value }))}
                                    className="w-full bg-slate-700 border-slate-600 text-white rounded px-3 py-2"
                                    rows="3"
                                    placeholder="Explain the investment strategy and MT5 allocation approach (minimum 20 characters)"
                                />
                                <p className="text-xs text-slate-400 mt-1">
                                    {formData.creation_notes.length}/20 characters minimum
                                </p>
                            </div>
                        </CardContent>
                    </Card>

                    {/* MT5 Account Allocations */}
                    <Card className="bg-slate-800 border-slate-700">
                        <CardHeader>
                            <div className="flex justify-between items-center">
                                <h2 className="text-xl font-semibold text-white flex items-center gap-2">
                                    <Shield className="h-5 w-5" />
                                    MT5 Account Allocations
                                </h2>
                                <Button
                                    onClick={addMT5Account}
                                    className="bg-blue-600 hover:bg-blue-700 text-white"
                                    size="sm"
                                >
                                    <Plus className="h-4 w-4 mr-1" />
                                    Add Account
                                </Button>
                            </div>
                        </CardHeader>
                        <CardContent>
                            {/* Individual MT5 Accounts */}
                            {formData.mt5_accounts.map((account, index) => (
                                <div key={index} className="border border-slate-600 rounded-lg p-4 mb-4">
                                    <div className="flex justify-between items-center mb-3">
                                        <h3 className="text-white font-medium">Account {index + 1}</h3>
                                        {formData.mt5_accounts.length > 1 && (
                                            <Button
                                                onClick={() => removeMT5Account(index)}
                                                variant="outline"
                                                size="sm"
                                                className="border-red-600 text-red-400 hover:bg-red-900"
                                            >
                                                <X className="h-4 w-4" />
                                            </Button>
                                        )}
                                    </div>

                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        {/* MT5 Account Number */}
                                        <div>
                                            <Label className="text-slate-300">MT5 Account Number *</Label>
                                            <Input
                                                type="number"
                                                value={account.mt5_account_number}
                                                onChange={(e) => updateMT5Account(index, 'mt5_account_number', e.target.value)}
                                                className="bg-slate-700 border-slate-600 text-white"
                                                placeholder="886557"
                                            />
                                            {account.mt5_account_number && getAvailabilityBadge(account.mt5_account_number)}
                                        </div>

                                        {/* Broker */}
                                        <div>
                                            <Label className="text-slate-300">Broker *</Label>
                                            <select
                                                value={account.broker_name}
                                                onChange={(e) => updateMT5Account(index, 'broker_name', e.target.value)}
                                                className="w-full bg-slate-700 border-slate-600 text-white rounded px-3 py-2"
                                            >
                                                {brokers.map(broker => (
                                                    <option key={broker.value} value={broker.value}>
                                                        {broker.label}
                                                    </option>
                                                ))}
                                            </select>
                                        </div>

                                        {/* Investor Password */}
                                        <div>
                                            <Label className="text-slate-300 flex items-center gap-2">
                                                🔒 Investor Password *
                                                <AlertCircle className="h-4 w-4 text-amber-500" />
                                            </Label>
                                            <div className="relative">
                                                <Input
                                                    type={showPasswords[index] ? "text" : "password"}
                                                    value={account.investor_password}
                                                    onChange={(e) => updateMT5Account(index, 'investor_password', e.target.value)}
                                                    className="bg-slate-700 border-slate-600 text-white pr-10"
                                                    placeholder="Enter investor password only"
                                                />
                                                <Button
                                                    type="button"
                                                    onClick={() => togglePasswordVisibility(index)}
                                                    className="absolute right-2 top-1/2 transform -translate-y-1/2 p-1 h-auto bg-transparent hover:bg-slate-600"
                                                >
                                                    {showPasswords[index] ? <EyeOff className="h-4 w-4 text-slate-400" /> : <Eye className="h-4 w-4 text-slate-400" />}
                                                </Button>
                                            </div>
                                            <p className="text-xs text-amber-300 mt-1">
                                                ⚠️ INVESTOR PASSWORD ONLY (read-only access)
                                            </p>
                                        </div>

                                        {/* Allocation Amount */}
                                        <div>
                                            <Label className="text-slate-300">Allocation Amount *</Label>
                                            <div className="relative">
                                                <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
                                                <Input
                                                    type="number"
                                                    value={account.allocated_amount}
                                                    onChange={(e) => updateMT5Account(index, 'allocated_amount', e.target.value)}
                                                    className="bg-slate-700 border-slate-600 text-white pl-10"
                                                    placeholder="80000.00"
                                                    step="0.01"
                                                />
                                            </div>
                                        </div>
                                    </div>

                                    {/* Allocation Notes */}
                                    <div className="mt-4">
                                        <Label className="text-slate-300">Allocation Notes *</Label>
                                        <textarea
                                            value={account.allocation_notes}
                                            onChange={(e) => updateMT5Account(index, 'allocation_notes', e.target.value)}
                                            className="w-full bg-slate-700 border-slate-600 text-white rounded px-3 py-2"
                                            rows="2"
                                            placeholder="Explain this specific MT5 allocation (minimum 10 characters)"
                                        />
                                        <p className="text-xs text-slate-400 mt-1">
                                            {account.allocation_notes.length}/10 characters minimum
                                        </p>
                                    </div>
                                </div>
                            ))}
                        </CardContent>
                    </Card>

                    {/* Separation Accounts */}
                    <Card className="bg-slate-800 border-slate-700">
                        <CardHeader>
                            <h2 className="text-xl font-semibold text-white flex items-center gap-2">
                                <Users className="h-5 w-5" />
                                Separation Tracking Accounts (Optional)
                            </h2>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            {/* Interest Separation Account */}
                            <div className="border border-slate-600 rounded-lg p-4">
                                <h3 className="text-white font-medium mb-3">Interest Separation Account</h3>
                                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                    <div>
                                        <Label className="text-slate-300">MT5 Account Number</Label>
                                        <Input
                                            type="number"
                                            value={formData.interest_separation_account.mt5_account_number}
                                            onChange={(e) => updateSeparationAccount('interest_separation_account', 'mt5_account_number', e.target.value)}
                                            className="bg-slate-700 border-slate-600 text-white"
                                            placeholder="886528"
                                        />
                                    </div>
                                    <div>
                                        <Label className="text-slate-300">Broker</Label>
                                        <select
                                            value={formData.interest_separation_account.broker_name}
                                            onChange={(e) => updateSeparationAccount('interest_separation_account', 'broker_name', e.target.value)}
                                            className="w-full bg-slate-700 border-slate-600 text-white rounded px-3 py-2"
                                        >
                                            {brokers.map(broker => (
                                                <option key={broker.value} value={broker.value}>
                                                    {broker.label}
                                                </option>
                                            ))}
                                        </select>
                                    </div>
                                    <div>
                                        <Label className="text-slate-300 flex items-center gap-1">
                                            🔒 Investor Password <AlertCircle className="h-3 w-3 text-amber-500" />
                                        </Label>
                                        <Input
                                            type="password"
                                            value={formData.interest_separation_account.investor_password}
                                            onChange={(e) => updateSeparationAccount('interest_separation_account', 'investor_password', e.target.value)}
                                            className="bg-slate-700 border-slate-600 text-white"
                                            placeholder="Investor password only"
                                        />
                                    </div>
                                </div>
                            </div>

                            {/* Gains Separation Account */}
                            <div className="border border-slate-600 rounded-lg p-4">
                                <h3 className="text-white font-medium mb-3">Gains Separation Account</h3>
                                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                    <div>
                                        <Label className="text-slate-300">MT5 Account Number</Label>
                                        <Input
                                            type="number"
                                            value={formData.gains_separation_account.mt5_account_number}
                                            onChange={(e) => updateSeparationAccount('gains_separation_account', 'mt5_account_number', e.target.value)}
                                            className="bg-slate-700 border-slate-600 text-white"
                                            placeholder="886529"
                                        />
                                    </div>
                                    <div>
                                        <Label className="text-slate-300">Broker</Label>
                                        <select
                                            value={formData.gains_separation_account.broker_name}
                                            onChange={(e) => updateSeparationAccount('gains_separation_account', 'broker_name', e.target.value)}
                                            className="w-full bg-slate-700 border-slate-600 text-white rounded px-3 py-2"
                                        >
                                            {brokers.map(broker => (
                                                <option key={broker.value} value={broker.value}>
                                                    {broker.label}
                                                </option>
                                            ))}
                                        </select>
                                    </div>
                                    <div>
                                        <Label className="text-slate-300 flex items-center gap-1">
                                            🔒 Investor Password <AlertCircle className="h-3 w-3 text-amber-500" />
                                        </Label>
                                        <Input
                                            type="password"
                                            value={formData.gains_separation_account.investor_password}
                                            onChange={(e) => updateSeparationAccount('gains_separation_account', 'investor_password', e.target.value)}
                                            className="bg-slate-700 border-slate-600 text-white"
                                            placeholder="Investor password only"
                                        />
                                    </div>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </div>

                {/* Validation & Summary Sidebar */}
                <div className="space-y-6">
                    {/* Allocation Summary */}
                    <Card className="bg-slate-800 border-slate-700">
                        <CardHeader>
                            <h2 className="text-lg font-semibold text-white flex items-center gap-2">
                                <Calculator className="h-5 w-5" />
                                Allocation Summary
                            </h2>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-3 text-sm">
                                <div className="flex justify-between">
                                    <span className="text-slate-300">Total Investment:</span>
                                    <span className="text-white font-mono">
                                        ${parseFloat(formData.principal_amount || 0).toLocaleString()}
                                    </span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-slate-300">Total Allocated:</span>
                                    <span className={`font-mono ${validation.isValid ? 'text-green-400' : 'text-red-400'}`}>
                                        ${validation.totalAllocated.toLocaleString()}
                                    </span>
                                </div>
                                <div className="flex justify-between border-t border-slate-600 pt-2">
                                    <span className="text-slate-300">Difference:</span>
                                    <span className={`font-mono font-bold ${validation.isValid ? 'text-green-400' : 'text-red-400'}`}>
                                        ${Math.abs(validation.totalAllocated - parseFloat(formData.principal_amount || 0)).toFixed(2)}
                                    </span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-slate-300">Status:</span>
                                    <Badge className={validation.isValid ? 'bg-green-600' : 'bg-red-600'}>
                                        {validation.isValid ? '✓ Valid' : '✗ Invalid'}
                                    </Badge>
                                </div>
                            </div>

                            {/* MT5 Account Breakdown */}
                            {formData.mt5_accounts.length > 0 && (
                                <div className="mt-4 pt-4 border-t border-slate-600">
                                    <h4 className="text-slate-300 font-medium mb-2">Account Breakdown:</h4>
                                    {formData.mt5_accounts.map((account, index) => (
                                        <div key={index} className="flex justify-between text-xs mb-1">
                                            <span className="text-slate-400">
                                                {account.mt5_account_number || `Account ${index + 1}`}:
                                            </span>
                                            <span className="text-white font-mono">
                                                ${parseFloat(account.allocated_amount || 0).toLocaleString()}
                                            </span>
                                        </div>
                                    ))}
                                </div>
                            )}

                            {/* Validation Errors */}
                            {validation.errors.length > 0 && (
                                <div className="mt-4 pt-4 border-t border-slate-600">
                                    <h4 className="text-red-400 font-medium mb-2">Issues to fix:</h4>
                                    {validation.errors.map((error, index) => (
                                        <p key={index} className="text-red-300 text-xs mb-1">
                                            • {error}
                                        </p>
                                    ))}
                                </div>
                            )}
                        </CardContent>
                    </Card>

                    {/* Submit Button */}
                    <Button
                        onClick={submitInvestment}
                        disabled={!validation.isValid || isSubmitting || !formData.client_id}
                        className={`w-full py-3 ${validation.isValid && formData.client_id 
                            ? 'bg-green-600 hover:bg-green-700' 
                            : 'bg-slate-600 cursor-not-allowed'
                        } text-white font-semibold`}
                    >
                        {isSubmitting ? (
                            <>
                                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                                Creating Investment...
                            </>
                        ) : (
                            <>
                                <CheckCircle className="h-4 w-4 mr-2" />
                                Create Investment with MT5 Accounts
                            </>
                        )}
                    </Button>

                    {validation.isValid && (
                        <p className="text-xs text-green-300 text-center">
                            ✓ Ready to create investment with {formData.mt5_accounts.length} MT5 account(s)
                        </p>
                    )}
                </div>
            </div>
        </div>
    );
};

export default InvestmentCreationWithMT5;