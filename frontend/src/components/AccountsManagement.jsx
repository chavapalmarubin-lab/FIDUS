import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Input } from './ui/input';
import { Alert, AlertDescription } from './ui/alert';
import { 
    Edit3, 
    Save, 
    X, 
    RefreshCw, 
    Database,
    Settings,
    CheckCircle,
    AlertCircle,
    Search
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

// Available options for dropdowns
const FUND_TYPES = ['CORE', 'BALANCE', 'SEPARATION', 'DYNAMIC', 'UNLIMITED'];
const MANAGER_OPTIONS = [
    'CP Strategy', 'TradingHub Gold', 'UNO14 Manager', 'Provider1-Assev', 
    'alefloreztrader', 'Spaniard Stock CFDs', 'JOSE', 'Money Manager',
    'GoldenTrade', 'Reserve Account'
];
const STATUS_OPTIONS = ['active', 'inactive'];

export default function AccountsManagement() {
    const [accounts, setAccounts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [editingAccount, setEditingAccount] = useState(null);
    const [searchTerm, setSearchTerm] = useState('');
    const [filterPlatform, setFilterPlatform] = useState('all');
    const [filterFund, setFilterFund] = useState('all');
    const [filterStatus, setFilterStatus] = useState('all');
    
    // Summary stats
    const [summary, setSummary] = useState({});
    
    // Bridge health data (merged from BridgeHealthMonitor)
    const [bridgeHealth, setBridgeHealth] = useState(null);

    useEffect(() => {
        fetchAccounts();
        fetchBridgeHealth();
        // Auto-refresh every 30 seconds for balance updates
        const interval = setInterval(() => {
            fetchAccounts();
            fetchBridgeHealth();
        }, 30000);
        return () => clearInterval(interval);
    }, []);
    
    const fetchBridgeHealth = async () => {
        try {
            const healthRes = await fetch(`${BACKEND_URL}/api/bridges/health`);
            const healthJson = await healthRes.json();
            setBridgeHealth(healthJson);
        } catch (err) {
            console.error('Error fetching bridge health:', err);
        }
    };

    const fetchAccounts = async () => {
        try {
            setLoading(true);
            const response = await fetch(`${BACKEND_URL}/api/v2/accounts/all`);
            const data = await response.json();
            
            if (data.success) {
                setAccounts(data.accounts);
                setSummary(data.summary);
                setError('');
            } else {
                setError(data.message || 'Failed to fetch accounts');
            }
        } catch (err) {
            console.error('Error fetching accounts:', err);
            setError('Failed to connect to server');
        } finally {
            setLoading(false);
        }
    };

    const startEditing = (account) => {
        setEditingAccount({
            ...account,
            // Store original values for cancel
            _original: {
                fund_type: account.fund_type,
                manager_name: account.manager_name,
                status: account.status,
                description: account.description || ''
            }
        });
    };

    const cancelEditing = () => {
        setEditingAccount(null);
        setError('');
        setSuccess('');
    };

    const saveAccountAssignment = async () => {
        if (!editingAccount) return;
        
        try {
            const updateData = {
                fund_type: editingAccount.fund_type,
                manager_name: editingAccount.manager_name,
                status: editingAccount.status,
                description: editingAccount.description || ''
            };

            const response = await fetch(`${BACKEND_URL}/api/v2/accounts/${editingAccount.account}/assign`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(updateData)
            });

            const data = await response.json();

            if (data.success) {
                setSuccess(`Account ${editingAccount.account} updated successfully`);
                setEditingAccount(null);
                fetchAccounts(); // Refresh to show changes
                
                // Clear success message after 3 seconds
                setTimeout(() => setSuccess(''), 3000);
            } else {
                setError(data.message || 'Failed to update account');
            }
        } catch (err) {
            console.error('Error saving account:', err);
            setError('Failed to save changes');
        }
    };

    const updateEditingField = (field, value) => {
        setEditingAccount(prev => ({
            ...prev,
            [field]: value
        }));
    };

    // Filter accounts based on search and filters
    const filteredAccounts = accounts.filter(account => {
        const matchesSearch = searchTerm === '' || 
            account.account.toString().includes(searchTerm) ||
            account.manager_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
            account.broker?.toLowerCase().includes(searchTerm.toLowerCase());
        
        const matchesPlatform = filterPlatform === 'all' || account.platform === filterPlatform;
        const matchesFund = filterFund === 'all' || account.fund_type === filterFund;
        const matchesStatus = filterStatus === 'all' || account.status === filterStatus;
        
        return matchesSearch && matchesPlatform && matchesFund && matchesStatus;
    });

    const getPlatformBadgeVariant = (platform) => {
        return platform === 'MT4' ? 'secondary' : 'default';
    };

    const getFundBadgeVariant = (fund) => {
        const variants = {
            'CORE': 'destructive',
            'BALANCE': 'default', 
            'SEPARATION': 'warning'
        };
        return variants[fund] || 'secondary';
    };

    const getStatusBadgeVariant = (status) => {
        return status === 'active' ? 'success' : 'secondary';
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center p-8">
                <RefreshCw className="h-8 w-8 animate-spin text-gray-400" />
                <span className="ml-2 text-gray-600">Loading accounts...</span>
            </div>
        );
    }

    return (
        <div className="space-y-6 p-4">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold flex items-center gap-2">
                        <Database className="h-6 w-6" />
                        Accounts Management
                        <Badge variant="outline" className="ml-2">Single Source of Truth</Badge>
                    </h2>
                    <p className="text-sm text-gray-500 mt-1">
                        Edit fund and manager assignments here. All other tabs update automatically.
                    </p>
                </div>
                <Button onClick={fetchAccounts} variant="outline" size="sm">
                    <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                    Refresh
                </Button>
            </div>

            {/* Alerts */}
            {success && (
                <Alert className="border-green-500 bg-green-50">
                    <CheckCircle className="h-4 w-4 text-green-600" />
                    <AlertDescription className="text-green-800">{success}</AlertDescription>
                </Alert>
            )}

            {error && (
                <Alert className="border-red-500 bg-red-50">
                    <AlertCircle className="h-4 w-4 text-red-600" />
                    <AlertDescription className="text-red-800">{error}</AlertDescription>
                </Alert>
            )}

            {/* Summary Cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <Card>
                    <CardContent className="p-4">
                        <div className="text-2xl font-bold text-blue-600">{summary.total_accounts || 0}</div>
                        <div className="text-sm text-gray-500">Total Accounts</div>
                    </CardContent>
                </Card>
                <Card>
                    <CardContent className="p-4">
                        <div className="text-2xl font-bold text-green-600">{summary.active_accounts || 0}</div>
                        <div className="text-sm text-gray-500">Active Accounts</div>
                    </CardContent>
                </Card>
                <Card>
                    <CardContent className="p-4">
                        <div className="text-2xl font-bold text-purple-600">
                            ${(summary.total_balance || 0).toLocaleString('en-US', { maximumFractionDigits: 0 })}
                        </div>
                        <div className="text-sm text-gray-500">Total Balance</div>
                    </CardContent>
                </Card>
                <Card>
                    <CardContent className="p-4">
                        <div className="text-2xl font-bold text-orange-600">
                            ${(summary.total_equity || 0).toLocaleString('en-US', { maximumFractionDigits: 0 })}
                        </div>
                        <div className="text-sm text-gray-500">Total Equity</div>
                    </CardContent>
                </Card>
            </div>

            {/* Filters */}
            <Card>
                <CardContent className="p-4">
                    <div className="flex flex-wrap gap-4 items-center">
                        <div className="flex items-center gap-2">
                            <Search className="h-4 w-4 text-gray-400" />
                            <Input
                                placeholder="Search accounts..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                className="w-64"
                            />
                        </div>
                        
                        <select 
                            value={filterPlatform} 
                            onChange={(e) => setFilterPlatform(e.target.value)}
                            className="px-3 py-2 border rounded-md"
                        >
                            <option value="all">All Platforms</option>
                            <option value="MT5">MT5</option>
                            <option value="MT4">MT4</option>
                        </select>
                        
                        <select 
                            value={filterFund} 
                            onChange={(e) => setFilterFund(e.target.value)}
                            className="px-3 py-2 border rounded-md"
                        >
                            <option value="all">All Funds</option>
                            {FUND_TYPES.map(fund => (
                                <option key={fund} value={fund}>{fund}</option>
                            ))}
                        </select>
                        
                        <select 
                            value={filterStatus} 
                            onChange={(e) => setFilterStatus(e.target.value)}
                            className="px-3 py-2 border rounded-md"
                        >
                            <option value="all">All Status</option>
                            <option value="active">Active</option>
                            <option value="inactive">Inactive</option>
                        </select>

                        <div className="text-sm text-gray-500">
                            Showing {filteredAccounts.length} of {accounts.length} accounts
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* Accounts Table */}
            <Card>
                <CardHeader>
                    <CardTitle>Master Accounts Table</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                            <thead>
                                <tr className="border-b">
                                    <th className="text-left p-2">Account</th>
                                    <th className="text-left p-2">Platform</th>
                                    <th className="text-left p-2">Broker</th>
                                    <th className="text-left p-2">Fund Type</th>
                                    <th className="text-left p-2">Manager</th>
                                    <th className="text-right p-2">Allocation</th>
                                    <th className="text-right p-2">Balance</th>
                                    <th className="text-right p-2">P&L</th>
                                    <th className="text-center p-2">Status</th>
                                    <th className="text-center p-2">Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filteredAccounts.map((account) => {
                                    const isEditing = editingAccount && editingAccount.account === account.account;
                                    
                                    return (
                                        <tr key={account.account} className={`border-b hover:bg-gray-50 ${isEditing ? 'bg-blue-50' : ''}`}>
                                            <td className="p-2 font-mono font-bold">{account.account}</td>
                                            <td className="p-2">
                                                <Badge variant={getPlatformBadgeVariant(account.platform)}>
                                                    {account.platform}
                                                </Badge>
                                            </td>
                                            <td className="p-2 text-xs">
                                                {account.broker === 'LUCRUM Capital' ? 'LUCRUM' : account.broker}
                                            </td>
                                            <td className="p-2">
                                                {isEditing ? (
                                                    <select 
                                                        value={editingAccount.fund_type}
                                                        onChange={(e) => updateEditingField('fund_type', e.target.value)}
                                                        className="px-2 py-1 border rounded text-xs"
                                                    >
                                                        {FUND_TYPES.map(fund => (
                                                            <option key={fund} value={fund}>{fund}</option>
                                                        ))}
                                                    </select>
                                                ) : (
                                                    <Badge variant={getFundBadgeVariant(account.fund_type)}>
                                                        {account.fund_type}
                                                    </Badge>
                                                )}
                                            </td>
                                            <td className="p-2">
                                                {isEditing ? (
                                                    <select 
                                                        value={editingAccount.manager_name}
                                                        onChange={(e) => updateEditingField('manager_name', e.target.value)}
                                                        className="px-2 py-1 border rounded text-xs w-full"
                                                    >
                                                        {MANAGER_OPTIONS.map(manager => (
                                                            <option key={manager} value={manager}>{manager}</option>
                                                        ))}
                                                    </select>
                                                ) : (
                                                    <span className="text-xs">{account.manager_name}</span>
                                                )}
                                            </td>
                                            <td className="p-2 text-right font-medium text-gray-600">
                                                ${(account.initial_allocation || 0).toLocaleString('en-US', {
                                                    minimumFractionDigits: 2,
                                                    maximumFractionDigits: 2
                                                })}
                                            </td>
                                            <td className="p-2 text-right font-medium">
                                                ${(account.balance || 0).toLocaleString('en-US', {
                                                    minimumFractionDigits: 2,
                                                    maximumFractionDigits: 2
                                                })}
                                            </td>
                                            <td className={`p-2 text-right font-medium ${(account.pnl || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                                ${(account.pnl || 0).toLocaleString('en-US', {
                                                    minimumFractionDigits: 2,
                                                    maximumFractionDigits: 2
                                                })}
                                            </td>
                                            <td className="p-2 text-center">
                                                {isEditing ? (
                                                    <select 
                                                        value={editingAccount.status}
                                                        onChange={(e) => updateEditingField('status', e.target.value)}
                                                        className="px-2 py-1 border rounded text-xs"
                                                    >
                                                        {STATUS_OPTIONS.map(status => (
                                                            <option key={status} value={status}>
                                                                {status.charAt(0).toUpperCase() + status.slice(1)}
                                                            </option>
                                                        ))}
                                                    </select>
                                                ) : (
                                                    <Badge variant={getStatusBadgeVariant(account.status)}>
                                                        {account.status}
                                                    </Badge>
                                                )}
                                            </td>
                                            <td className="p-2 text-center">
                                                {isEditing ? (
                                                    <div className="flex gap-1 justify-center">
                                                        <Button 
                                                            size="sm" 
                                                            onClick={saveAccountAssignment}
                                                            className="h-6 w-6 p-0"
                                                        >
                                                            <Save className="h-3 w-3" />
                                                        </Button>
                                                        <Button 
                                                            size="sm" 
                                                            variant="outline"
                                                            onClick={cancelEditing}
                                                            className="h-6 w-6 p-0"
                                                        >
                                                            <X className="h-3 w-3" />
                                                        </Button>
                                                    </div>
                                                ) : (
                                                    <Button 
                                                        size="sm" 
                                                        variant="ghost"
                                                        onClick={() => startEditing(account)}
                                                        className="h-6 w-6 p-0"
                                                    >
                                                        <Edit3 className="h-3 w-3" />
                                                    </Button>
                                                )}
                                            </td>
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    </div>
                </CardContent>
            </Card>

            {/* Instructions */}
            <Card className="bg-blue-50 border-blue-200">
                <CardContent className="p-4">
                    <div className="flex items-start gap-3">
                        <Settings className="h-5 w-5 text-blue-600 mt-0.5" />
                        <div>
                            <h3 className="font-semibold text-blue-800 mb-2">Single Source of Truth</h3>
                            <div className="text-sm text-blue-700 space-y-1">
                                <p>• <strong>Edit here:</strong> Change fund type, manager, or status using the edit buttons</p>
                                <p>• <strong>Updates everywhere:</strong> Changes automatically appear in Fund Portfolio, Money Managers, and Analytics tabs</p>
                                <p>• <strong>Real-time data:</strong> Account balances and equity are updated every 30 seconds from VPS bridges</p>
                                <p>• <strong>No duplicates:</strong> This is the only place where account assignments are managed</p>
                            </div>
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}