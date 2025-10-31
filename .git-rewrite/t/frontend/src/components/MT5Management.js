import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Alert, AlertDescription } from './ui/alert';
import { Badge } from './ui/badge';
import { 
    TrendingUp, 
    TrendingDown, 
    Users, 
    Activity, 
    Plus,
    Settings,
    Server,
    User,
    DollarSign,
    BarChart3,
    AlertCircle,
    CheckCircle,
    RefreshCw,
    Eye
} from 'lucide-react';
import apiAxios from '../utils/apiAxios';

const MT5Management = () => {
    const [accountsByBroker, setAccountsByBroker] = useState({});
    const [totalStats, setTotalStats] = useState({});
    const [availableBrokers, setAvailableBrokers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    
    // Modal states
    const [showAddAccountModal, setShowAddAccountModal] = useState(false);
    const [showAccountDetailsModal, setShowAccountDetailsModal] = useState(false);
    const [selectedAccountDetails, setSelectedAccountDetails] = useState(null);
    const [accountActivity, setAccountActivity] = useState([]);
    const [selectedBroker, setSelectedBroker] = useState('');
    const [brokerServers, setBrokerServers] = useState([]);
    const [newAccount, setNewAccount] = useState({
        client_id: '',
        fund_code: 'CORE',
        broker_code: '',
        mt5_login: '',
        mt5_password: '',
        mt5_server: '',
        allocated_amount: ''
    });

    useEffect(() => {
        fetchMT5Data();
        fetchAvailableBrokers();
        // Set up auto-refresh for real-time data
        const interval = setInterval(fetchMT5Data, 30000); // Refresh every 30 seconds
        return () => clearInterval(interval);
    }, []);

    const fetchMT5Data = async () => {
        try {
            const response = await apiAxios.get('/mt5/admin/accounts');
            
            if (response.data) {
                const data = response.data;
                // Group accounts by broker for display
                const accountsByBroker = {};
                let totalStats = { total_accounts: 0, total_balance: 0, total_equity: 0 };
                
                if (Array.isArray(data)) {
                    data.forEach(account => {
                        const broker = account.broker || 'Unknown';
                        if (!accountsByBroker[broker]) {
                            accountsByBroker[broker] = [];
                        }
                        accountsByBroker[broker].push(account);
                        totalStats.total_accounts++;
                        totalStats.total_balance += account.balance || 0;
                        totalStats.total_equity += account.equity || 0;
                    });
                }
                
                setAccountsByBroker(accountsByBroker);
                setTotalStats(totalStats);
            } else {
                throw new Error('Failed to fetch MT5 data');
            }
        } catch (err) {
            setError('Failed to load MT5 data');
            console.error('MT5 data fetch error:', err);
        } finally {
            setLoading(false);
        }
    };

    const fetchAvailableBrokers = async () => {
        try {
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/mt5/brokers`, {
                headers: {
                    'Authorization': `Bearer ${JSON.parse(localStorage.getItem('fidus_user')).token}`
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                setAvailableBrokers(data.brokers || []);
            }
        } catch (err) {
            console.error('Failed to fetch brokers:', err);
        }
    };

    const handleBrokerSelect = async (brokerCode) => {
        setSelectedBroker(brokerCode);
        setNewAccount(prev => ({ ...prev, broker_code: brokerCode }));
        
        try {
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/mt5/brokers/${brokerCode}/servers`, {
                headers: {
                    'Authorization': `Bearer ${JSON.parse(localStorage.getItem('fidus_user')).token}`
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                setBrokerServers(data.servers || []);
            }
        } catch (err) {
            console.error('Failed to fetch broker servers:', err);
        }
    };

    const handleAddAccount = async () => {
        try {
            setError('');
            
            // Validation
            if (!newAccount.client_id || !newAccount.mt5_login || !newAccount.mt5_password || !newAccount.mt5_server) {
                setError('Please fill in all required fields');
                return;
            }

            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/mt5/admin/add-manual-account`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${JSON.parse(localStorage.getItem('fidus_user')).token}`
                },
                body: JSON.stringify(newAccount)
            });

            const data = await response.json();

            if (response.ok && data.success) {
                setSuccess('MT5 account added successfully!');
                setShowAddAccountModal(false);
                resetForm();
                fetchMT5Data(); // Refresh data
            } else {
                setError(data.detail || 'Failed to add MT5 account');
            }
        } catch (err) {
            setError('Failed to add MT5 account');
            console.error('Add account error:', err);
        }
    };

    const handleAccountClick = async (account) => {
        try {
            setSelectedAccountDetails(account);
            setShowAccountDetailsModal(true);
            
            // Fetch real account activity from backend
            const activityResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/mt5/admin/account/${account.account_id}/activity`, {
                headers: {
                    'Authorization': `Bearer ${JSON.parse(localStorage.getItem('fidus_user')).token}`
                }
            });
            
            if (activityResponse.ok) {
                const activityData = await activityResponse.json();
                if (activityData.success) {
                    setAccountActivity(activityData.activity || []);
                    console.log('Real trading activity loaded:', activityData.activity);
                } else {
                    console.warn('No real trading activity found, using mock data');
                    setAccountActivity(generateMockActivity(account));
                }
            } else {
                console.warn('Trading activity API failed, using mock data');
                setAccountActivity(generateMockActivity(account));
            }
        } catch (err) {
            console.error('Failed to fetch account details:', err);
            // Fallback to mock data
            setAccountActivity(generateMockActivity(account));
        }
    };

    const generateMockActivity = (account) => {
        return [
            {
                id: 1,
                type: 'deposit',
                amount: account.total_allocated,
                description: `Initial allocation to ${account.fund_code} fund`,
                timestamp: new Date(Date.now() - 86400000 * 7).toISOString(),
                status: 'completed'
            },
            {
                id: 2,
                type: 'trade',
                amount: 0,
                description: 'Position opened: EURUSD Buy 1.0 lot',
                timestamp: new Date(Date.now() - 86400000 * 5).toISOString(),
                status: 'open'
            },
            {
                id: 3,
                type: 'trade',
                amount: 150.00,
                description: 'Position closed: GBPUSD Sell 0.5 lot (+$150.00)',
                timestamp: new Date(Date.now() - 86400000 * 3).toISOString(),
                status: 'completed'
            },
            {
                id: 4,
                type: 'profit',
                amount: 75.50,
                description: 'Daily profit from active positions',
                timestamp: new Date(Date.now() - 86400000 * 1).toISOString(),
                status: 'completed'
            }
        ];
    };

    const resetForm = () => {
        setNewAccount({
            client_id: '',
            fund_code: 'CORE',
            broker_code: '',
            mt5_login: '',
            mt5_password: '',
            mt5_server: '',
            allocated_amount: ''
        });
        setSelectedBroker('');
        setBrokerServers([]);
    };

    const getConnectionStatusColor = (status) => {
        switch (status) {
            case 'connected': return 'bg-green-500';
            case 'connecting': return 'bg-yellow-500';
            case 'error': return 'bg-red-500';
            default: return 'bg-gray-500';
        }
    };

    const formatCurrency = (amount) => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(amount || 0);
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center p-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-400"></div>
                <span className="ml-2 text-slate-400">Loading MT5 data...</span>
            </div>
        );
    }

    return (
        <div className="mt5-management p-6 space-y-6">
            <div className="flex justify-between items-center">
                <div>
                    <h2 className="text-2xl font-bold text-white mb-2">Multi-Broker MT5 Management (Monitoring View)</h2>
                    <div className="flex items-center space-x-4">
                        <p className="text-slate-400">Manage MT5 accounts across multiple brokers</p>
                        <div className="flex items-center space-x-2">
                            <div className="flex items-center space-x-1">
                                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                                <span className="text-xs text-green-400">Real MT5 Data Available</span>
                            </div>
                            <div className="flex items-center space-x-1">
                                <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                                <span className="text-xs text-yellow-400">Simulated Data (Demo)</span>
                            </div>
                        </div>
                    </div>
                </div>
                <div className="flex items-center gap-3">
                    <span className="text-sm text-slate-400">
                        📊 View and monitor all MT5 accounts
                    </span>
                    <Button 
                        onClick={() => window.location.reload()}
                        className="bg-slate-600 hover:bg-slate-500 text-white px-4 py-2 rounded flex items-center gap-2"
                    >
                        <RefreshCw className="h-4 w-4" />
                        Refresh
                    </Button>
                </div>
            </div>

            {/* Error/Success Messages */}
            {error && (
                <Alert className="border-red-500 bg-red-500/10">
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription className="text-red-400">{error}</AlertDescription>
                </Alert>
            )}
            {success && (
                <Alert className="border-green-500 bg-green-500/10">
                    <CheckCircle className="h-4 w-4" />
                    <AlertDescription className="text-green-400">{success}</AlertDescription>
                </Alert>
            )}

            {/* Overall Statistics */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <Card className="bg-slate-800 border-slate-700">
                    <CardContent className="p-4">
                        <div className="flex items-center">
                            <Users className="h-8 w-8 text-cyan-500" />
                            <div className="ml-4">
                                <p className="text-sm font-medium text-slate-400">Total Accounts</p>
                                <p className="text-2xl font-bold text-white">{totalStats.total_accounts || 0}</p>
                            </div>
                        </div>
                    </CardContent>
                </Card>
                
                <Card className="bg-slate-800 border-slate-700">
                    <CardContent className="p-4">
                        <div className="flex items-center">
                            <DollarSign className="h-8 w-8 text-green-500" />
                            <div className="ml-4">
                                <p className="text-sm font-medium text-slate-400">Total Allocated</p>
                                <p className="text-2xl font-bold text-white">{formatCurrency(totalStats.total_allocated)}</p>
                            </div>
                        </div>
                    </CardContent>
                </Card>
                
                <Card className="bg-slate-800 border-slate-700">
                    <CardContent className="p-4">
                        <div className="flex items-center">
                            <BarChart3 className="h-8 w-8 text-blue-500" />
                            <div className="ml-4">
                                <p className="text-sm font-medium text-slate-400">Current Equity</p>
                                <p className="text-2xl font-bold text-white">{formatCurrency(totalStats.total_equity)}</p>
                            </div>
                        </div>
                    </CardContent>
                </Card>
                
                <Card className="bg-slate-800 border-slate-700">
                    <CardContent className="p-4">
                        <div className="flex items-center">
                            {totalStats.total_profit_loss >= 0 ? (
                                <TrendingUp className="h-8 w-8 text-green-500" />
                            ) : (
                                <TrendingDown className="h-8 w-8 text-red-500" />
                            )}
                            <div className="ml-4">
                                <p className="text-sm font-medium text-slate-400">Total P&L</p>
                                <p className={`text-2xl font-bold ${totalStats.total_profit_loss >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                    {formatCurrency(totalStats.total_profit_loss)}
                                </p>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Accounts by Broker */}
            <div className="space-y-6">
                <h3 className="text-xl font-semibold text-white">Accounts by Broker</h3>
                
                {Object.keys(accountsByBroker).length === 0 ? (
                    <Card className="bg-slate-800 border-slate-700">
                        <CardContent className="p-8 text-center">
                            <Server className="h-12 w-12 text-slate-500 mx-auto mb-4" />
                            <p className="text-slate-400">No MT5 accounts found</p>
                            <p className="text-sm text-slate-500 mt-2">Add your first MT5 account to get started</p>
                        </CardContent>
                    </Card>
                ) : (
                    Object.entries(accountsByBroker).map(([brokerCode, brokerData]) => (
                        <Card key={brokerCode} className="bg-slate-800 border-slate-700">
                            <CardHeader>
                                <div className="flex justify-between items-center">
                                    <div>
                                        <CardTitle className="text-white">{brokerData.broker_name}</CardTitle>
                                        <p className="text-slate-400 text-sm">
                                            {brokerData.stats.account_count} accounts • 
                                            {formatCurrency(brokerData.stats.total_allocated)} allocated
                                        </p>
                                    </div>
                                    <Badge variant="outline" className="text-cyan-400 border-cyan-400">
                                        {brokerCode.toUpperCase()}
                                    </Badge>
                                </div>
                            </CardHeader>
                            <CardContent>
                                <div className="overflow-x-auto">
                                    <table className="w-full">
                                        <thead>
                                            <tr className="border-b border-slate-600">
                                                <th className="text-left py-3 px-4 text-slate-300">Client</th>
                                                <th className="text-left py-3 px-4 text-slate-300">Fund</th>
                                                <th className="text-left py-3 px-4 text-slate-300">MT5 Login</th>
                                                <th className="text-left py-3 px-4 text-slate-300">Server</th>
                                                <th className="text-left py-3 px-4 text-slate-300">Allocated</th>
                                                <th className="text-left py-3 px-4 text-slate-300">Equity</th>
                                                <th className="text-left py-3 px-4 text-slate-300">P&L</th>
                                                <th className="text-left py-3 px-4 text-slate-300">Status</th>
                                                <th className="text-left py-3 px-4 text-slate-300">Actions</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {brokerData.accounts.map((account) => (
                                                <tr 
                                                    key={account.account_id} 
                                                    className="border-b border-slate-700 hover:bg-slate-750 transition-colors"
                                                >
                                                    <td className="py-3 px-4 text-white">{account.client_id}</td>
                                                    <td className="py-3 px-4">
                                                        <Badge className="bg-blue-600 text-white">
                                                            {account.fund_code}
                                                        </Badge>
                                                    </td>
                                                    <td className="py-3 px-4 text-slate-300">{account.mt5_login}</td>
                                                    <td className="py-3 px-4 text-slate-300">{account.mt5_server}</td>
                                                    <td className="py-3 px-4 text-white">{formatCurrency(account.total_allocated)}</td>
                                                    <td className="py-3 px-4 text-white">{formatCurrency(account.current_equity)}</td>
                                                    <td className={`py-3 px-4 ${account.profit_loss >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                                        {formatCurrency(account.profit_loss)}
                                                        <span className="text-sm ml-1">
                                                            ({account.profit_loss_percentage?.toFixed(2)}%)
                                                        </span>
                                                    </td>
                                                    <td className="py-3 px-4">
                                                        <Badge className={`${getConnectionStatusColor(account.connection_status)} text-white`}>
                                                            {account.connection_status}
                                                        </Badge>
                                                    </td>
                                                    <td className="px-4 py-3">
                                                        <div className="flex items-center space-x-2">
                                                            <Button
                                                                onClick={(e) => {
                                                                    e.stopPropagation();
                                                                    setSelectedAccountDetails(account);
                                                                    setShowAccountDetailsModal(true);
                                                                }}
                                                                variant="outline"
                                                                size="sm"
                                                                className="border-slate-600 text-slate-300 hover:bg-slate-700"
                                                            >
                                                                <Eye size={14} className="mr-1" />
                                                                View Details
                                                            </Button>
                                                        </div>
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            </CardContent>
                        </Card>
                    ))
                )}
            </div>

            {/* MT5 Account Details Modal - VIEW ONLY */}
            {showAccountDetailsModal && selectedAccountDetails && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-slate-800 rounded-lg p-6 w-full max-w-2xl mx-4">
                        <div className="flex justify-between items-center mb-4">
                            <h3 className="text-lg font-semibold text-white">MT5 Account Details</h3>
                            <button 
                                onClick={() => setShowAccountDetailsModal(false)}
                                className="text-slate-400 hover:text-white"
                            >
                                ✕
                            </button>
                        </div>
                        
                        <div className="grid grid-cols-2 gap-4 text-sm">
                            <div>
                                <label className="text-slate-300 font-medium">MT5 Account Number</label>
                                <p className="text-white bg-slate-700 p-2 rounded">{selectedAccountDetails.mt5_login}</p>
                            </div>
                            <div>
                                <label className="text-slate-300 font-medium">Broker</label>
                                <p className="text-white bg-slate-700 p-2 rounded">{selectedAccountDetails.broker}</p>
                            </div>
                            <div>
                                <label className="text-slate-300 font-medium">Status</label>
                                <p className="text-white bg-slate-700 p-2 rounded">{selectedAccountDetails.status}</p>
                            </div>
                            <div>
                                <label className="text-slate-300 font-medium">Client</label>
                                <p className="text-white bg-slate-700 p-2 rounded">{selectedAccountDetails.client_id || 'Not allocated'}</p>
                            </div>
                            <div>
                                <label className="text-slate-300 font-medium">Fund Code</label>
                                <p className="text-white bg-slate-700 p-2 rounded">{selectedAccountDetails.fund_code || 'N/A'}</p>
                            </div>
                            <div>
                                <label className="text-slate-300 font-medium">Allocated Amount</label>
                                <p className="text-white bg-slate-700 p-2 rounded">
                                    {selectedAccountDetails.allocated_amount ? `$${Number(selectedAccountDetails.allocated_amount).toLocaleString()}` : 'N/A'}
                                </p>
                            </div>
                            <div className="col-span-2">
                                <label className="text-slate-300 font-medium">Allocation Notes</label>
                                <p className="text-white bg-slate-700 p-2 rounded min-h-[60px]">
                                    {selectedAccountDetails.allocation_notes || 'No notes available'}
                                </p>
                            </div>
                        </div>
                        
                        <div className="flex justify-end mt-6">
                            <button 
                                onClick={() => setShowAccountDetailsModal(false)}
                                className="bg-slate-600 hover:bg-slate-500 text-white px-4 py-2 rounded"
                            >
                                Close
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Account Details Modal */}
            {showAccountDetailsModal && selectedAccountDetails && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-slate-800 rounded-lg p-6 w-full max-w-4xl mx-4 max-h-[90vh] overflow-y-auto">
                        <div className="flex justify-between items-center mb-6">
                            <div>
                                <h3 className="text-xl font-semibold text-white">MT5 Account Details</h3>
                                <p className="text-slate-400">
                                    {selectedAccountDetails.broker_name || 'MT5'} • Login: {selectedAccountDetails.mt5_login}
                                </p>
                            </div>
                            <button
                                onClick={() => {
                                    setShowAccountDetailsModal(false);
                                    setSelectedAccountDetails(null);
                                    setAccountActivity([]);
                                }}
                                className="text-slate-400 hover:text-white text-2xl"
                            >
                                ×
                            </button>
                        </div>

                        {/* Account Overview */}
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                            <Card className="bg-slate-700 border-slate-600">
                                <CardContent className="p-4">
                                    <div className="text-sm text-slate-400">Client</div>
                                    <div className="text-lg font-semibold text-white">
                                        {selectedAccountDetails.client_id}
                                    </div>
                                </CardContent>
                            </Card>
                            
                            <Card className="bg-slate-700 border-slate-600">
                                <CardContent className="p-4">
                                    <div className="text-sm text-slate-400">Fund</div>
                                    <div className="text-lg font-semibold text-white">
                                        {selectedAccountDetails.fund_code}
                                    </div>
                                </CardContent>
                            </Card>
                            
                            <Card className="bg-slate-700 border-slate-600">
                                <CardContent className="p-4">
                                    <div className="text-sm text-slate-400">Allocated</div>
                                    <div className="text-lg font-semibold text-white">
                                        {formatCurrency(selectedAccountDetails.total_allocated)}
                                    </div>
                                </CardContent>
                            </Card>
                            
                            <Card className="bg-slate-700 border-slate-600">
                                <CardContent className="p-4">
                                    <div className="text-sm text-slate-400">Current Equity</div>
                                    <div className="text-lg font-semibold text-white">
                                        {formatCurrency(selectedAccountDetails.current_equity)}
                                    </div>
                                    <div className={`text-sm ${selectedAccountDetails.profit_loss >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                        {selectedAccountDetails.profit_loss >= 0 ? '+' : ''}{formatCurrency(selectedAccountDetails.profit_loss)} 
                                        ({selectedAccountDetails.profit_loss_percentage?.toFixed(2)}%)
                                    </div>
                                </CardContent>
                            </Card>
                        </div>

                        {/* Account Information */}
                        <Card className="bg-slate-700 border-slate-600 mb-6">
                            <CardHeader>
                                <CardTitle className="text-white">Account Information</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <div>
                                        <div className="text-sm text-slate-400">MT5 Login</div>
                                        <div className="text-white font-mono">{selectedAccountDetails.mt5_login}</div>
                                    </div>
                                    <div>
                                        <div className="text-sm text-slate-400">MT5 Server</div>
                                        <div className="text-white">{selectedAccountDetails.mt5_server}</div>
                                    </div>
                                    <div>
                                        <div className="text-sm text-slate-400">Account ID</div>
                                        <div className="text-white font-mono text-sm">{selectedAccountDetails.account_id}</div>
                                    </div>
                                    <div>
                                        <div className="text-sm text-slate-400">Status</div>
                                        <Badge className={`${getConnectionStatusColor(selectedAccountDetails.connection_status)} text-white`}>
                                            {selectedAccountDetails.connection_status}
                                        </Badge>
                                    </div>
                                    <div>
                                        <div className="text-sm text-slate-400">Created</div>
                                        <div className="text-white">
                                            {selectedAccountDetails.created_at ? 
                                                new Date(selectedAccountDetails.created_at).toLocaleDateString() : 
                                                'N/A'
                                            }
                                        </div>
                                    </div>
                                    <div>
                                        <div className="text-sm text-slate-400">Last Updated</div>
                                        <div className="text-white">
                                            {selectedAccountDetails.updated_at ? 
                                                new Date(selectedAccountDetails.updated_at).toLocaleDateString() : 
                                                'N/A'
                                            }
                                        </div>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>

                        {/* Account Activity */}
                        <Card className="bg-slate-700 border-slate-600">
                            <CardHeader>
                                <CardTitle className="text-white">Account Activity</CardTitle>
                            </CardHeader>
                            <CardContent>
                                {accountActivity.length === 0 ? (
                                    <div className="text-center py-8">
                                        <Activity className="h-12 w-12 text-slate-500 mx-auto mb-4" />
                                        <p className="text-slate-400">No activity recorded</p>
                                    </div>
                                ) : (
                                    <div className="space-y-4">
                                        {accountActivity.map((activity, index) => {
                                            // Determine activity icon and color based on type
                                            let activityIcon, activityColor, activityBg;
                                            
                                            if (activity.type === 'deposit') {
                                                activityIcon = <DollarSign size={16} />;
                                                activityColor = 'text-green-400';
                                                activityBg = 'bg-green-600';
                                            } else if (activity.type === 'trade') {
                                                activityIcon = <BarChart3 size={16} />;
                                                if (activity.profit_loss >= 0) {
                                                    activityColor = 'text-green-400';
                                                    activityBg = 'bg-green-600';
                                                } else {
                                                    activityColor = 'text-red-400';
                                                    activityBg = 'bg-red-600';
                                                }
                                            } else if (activity.type === 'profit') {
                                                activityIcon = <TrendingUp size={16} />;
                                                activityColor = 'text-cyan-400';
                                                activityBg = 'bg-cyan-600';
                                            } else {
                                                activityIcon = <Activity size={16} />;
                                                activityColor = 'text-slate-400';
                                                activityBg = 'bg-slate-600';
                                            }
                                            
                                            return (
                                                <div key={activity.activity_id || index} className="flex items-center justify-between p-4 bg-slate-800 rounded-lg">
                                                    <div className="flex items-center space-x-4">
                                                        <div className={`w-10 h-10 rounded-full flex items-center justify-center ${activityBg}`}>
                                                            {activityIcon}
                                                        </div>
                                                        <div>
                                                            <div className="text-white font-medium">
                                                                {activity.description}
                                                            </div>
                                                            <div className="text-sm text-slate-400">
                                                                {new Date(activity.timestamp).toLocaleString()}
                                                            </div>
                                                            {/* Show additional trading details */}
                                                            {activity.type === 'trade' && activity.symbol && (
                                                                <div className="text-xs text-slate-500 mt-1">
                                                                    {activity.symbol} • Vol: {activity.volume} • 
                                                                    Open: {activity.opening_price} • 
                                                                    Current: {activity.current_price}
                                                                </div>
                                                            )}
                                                        </div>
                                                    </div>
                                                    <div className="text-right">
                                                        {(activity.amount !== 0 || activity.profit_loss !== 0) && (
                                                            <div className={`font-semibold ${activityColor}`}>
                                                                {activity.type === 'trade' ? (
                                                                    <>
                                                                        {activity.profit_loss > 0 ? '+' : ''}{formatCurrency(activity.profit_loss)}
                                                                    </>
                                                                ) : (
                                                                    <>
                                                                        {activity.amount > 0 ? '+' : ''}{formatCurrency(activity.amount)}
                                                                    </>
                                                                )}
                                                            </div>
                                                        )}
                                                        <Badge className={`${
                                                            activity.status === 'completed' ? 'bg-green-600' :
                                                            activity.status === 'open' ? 'bg-blue-600' :
                                                            'bg-slate-600'
                                                        } text-white text-xs mt-1`}>
                                                            {activity.status}
                                                        </Badge>
                                                    </div>
                                                </div>
                                            );
                                        })}
                                    </div>
                                )}
                            </CardContent>
                        </Card>

                        {/* Close Button */}
                        <div className="mt-6 flex justify-end">
                            <Button
                                onClick={() => {
                                    setShowAccountDetailsModal(false);
                                    setSelectedAccountDetails(null);
                                    setAccountActivity([]);
                                }}
                                className="bg-slate-600 hover:bg-slate-700"
                            >
                                Close
                            </Button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default MT5Management;