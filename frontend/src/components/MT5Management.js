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
    RefreshCw
} from 'lucide-react';

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
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/mt5/admin/accounts/by-broker`, {
                headers: {
                    'Authorization': `Bearer ${JSON.parse(localStorage.getItem('fidus_user')).token}`
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                setAccountsByBroker(data.accounts_by_broker || {});
                setTotalStats(data.total_stats || {});
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
            
            // Fetch account activity/details
            const activityResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/mt5/admin/account/${account.account_id}/activity`, {
                headers: {
                    'Authorization': `Bearer ${JSON.parse(localStorage.getItem('fidus_user')).token}`
                }
            });
            
            if (activityResponse.ok) {
                const activityData = await activityResponse.json();
                setAccountActivity(activityData.activity || []);
            } else {
                // Generate mock activity data if endpoint doesn't exist yet
                setAccountActivity(generateMockActivity(account));
            }
        } catch (err) {
            console.error('Failed to fetch account details:', err);
            // Generate mock activity data
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
                    <h2 className="text-2xl font-bold text-white mb-2">Multi-Broker MT5 Management</h2>
                    <p className="text-slate-400">Manage MT5 accounts across multiple brokers</p>
                </div>
                <Button 
                    onClick={() => setShowAddAccountModal(true)}
                    className="bg-cyan-600 hover:bg-cyan-700"
                >
                    <Plus size={16} className="mr-2" />
                    Add MT5 Account
                </Button>
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
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {brokerData.accounts.map((account) => (
                                                <tr 
                                                    key={account.account_id} 
                                                    className="border-b border-slate-700 hover:bg-slate-750 cursor-pointer transition-colors"
                                                    onClick={() => handleAccountClick(account)}
                                                    title="Click to view account details"
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

            {/* Add Account Modal */}
            {showAddAccountModal && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-slate-800 rounded-lg p-6 w-full max-w-md mx-4">
                        <h3 className="text-lg font-semibold text-white mb-4">Add MT5 Account</h3>
                        
                        <div className="space-y-4">
                            <div>
                                <Label className="text-slate-300">Client ID *</Label>
                                <Input
                                    value={newAccount.client_id}
                                    onChange={(e) => setNewAccount(prev => ({ ...prev, client_id: e.target.value }))}
                                    className="bg-slate-700 border-slate-600 text-white"
                                    placeholder="client_001"
                                />
                            </div>
                            
                            <div>
                                <Label className="text-slate-300">Fund Code</Label>
                                <select
                                    value={newAccount.fund_code}
                                    onChange={(e) => setNewAccount(prev => ({ ...prev, fund_code: e.target.value }))}
                                    className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-white"
                                >
                                    <option value="CORE">CORE</option>
                                    <option value="BALANCE">BALANCE</option>
                                    <option value="DYNAMIC">DYNAMIC</option>
                                    <option value="UNLIMITED">UNLIMITED</option>
                                </select>
                            </div>
                            
                            <div>
                                <Label className="text-slate-300">Broker *</Label>
                                <select
                                    value={selectedBroker}
                                    onChange={(e) => handleBrokerSelect(e.target.value)}
                                    className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-white"
                                >
                                    <option value="">Select Broker</option>
                                    {availableBrokers.map((broker) => (
                                        <option key={broker.code} value={broker.code}>
                                            {broker.name} - {broker.description}
                                        </option>
                                    ))}
                                </select>
                            </div>
                            
                            {brokerServers.length > 0 && (
                                <div>
                                    <Label className="text-slate-300">MT5 Server *</Label>
                                    <select
                                        value={newAccount.mt5_server}
                                        onChange={(e) => setNewAccount(prev => ({ ...prev, mt5_server: e.target.value }))}
                                        className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-white"
                                    >
                                        <option value="">Select Server</option>
                                        {brokerServers.map((server) => (
                                            <option key={server} value={server}>
                                                {server}
                                            </option>
                                        ))}
                                    </select>
                                </div>
                            )}
                            
                            <div>
                                <Label className="text-slate-300">MT5 Login *</Label>
                                <Input
                                    value={newAccount.mt5_login}
                                    onChange={(e) => setNewAccount(prev => ({ ...prev, mt5_login: e.target.value }))}
                                    className="bg-slate-700 border-slate-600 text-white"
                                    placeholder="9928326"
                                />
                            </div>
                            
                            <div>
                                <Label className="text-slate-300">MT5 Password *</Label>
                                <Input
                                    type="password"
                                    value={newAccount.mt5_password}
                                    onChange={(e) => setNewAccount(prev => ({ ...prev, mt5_password: e.target.value }))}
                                    className="bg-slate-700 border-slate-600 text-white"
                                    placeholder="R1d567j!"
                                />
                            </div>
                            
                            <div>
                                <Label className="text-slate-300">Allocated Amount</Label>
                                <Input
                                    type="number"
                                    value={newAccount.allocated_amount}
                                    onChange={(e) => setNewAccount(prev => ({ ...prev, allocated_amount: e.target.value }))}
                                    className="bg-slate-700 border-slate-600 text-white"
                                    placeholder="0.00"
                                />
                            </div>
                        </div>
                        
                        <div className="flex gap-3 mt-6">
                            <Button
                                variant="outline"
                                onClick={() => {
                                    setShowAddAccountModal(false);
                                    resetForm();
                                }}
                                className="flex-1"
                            >
                                Cancel
                            </Button>
                            <Button
                                onClick={handleAddAccount}
                                className="flex-1 bg-cyan-600 hover:bg-cyan-700"
                            >
                                Add Account
                            </Button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default MT5Management;