import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';

const MT5Management = () => {
    const [mt5Accounts, setMt5Accounts] = useState([]);
    const [performanceOverview, setPerformanceOverview] = useState(null);
    const [loading, setLoading] = useState(true);
    const [selectedAccount, setSelectedAccount] = useState(null);
    const [credentialsModal, setCredentialsModal] = useState(false);
    const [newCredentials, setNewCredentials] = useState({
        mt5_login: '',
        mt5_password: '',
        mt5_server: ''
    });

    useEffect(() => {
        fetchMT5Data();
        // Set up auto-refresh for real-time data
        const interval = setInterval(fetchMT5Data, 30000); // Refresh every 30 seconds
        return () => clearInterval(interval);
    }, []);

    const fetchMT5Data = async () => {
        try {
            // Fetch all MT5 accounts
            const accountsResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/mt5/admin/accounts`);
            const accountsData = await accountsResponse.json();

            // Fetch performance overview
            const performanceResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/mt5/admin/performance/overview`);
            const performanceData = await performanceResponse.json();

            if (accountsData.success) {
                setMt5Accounts(accountsData.accounts);
            }

            if (performanceData.success) {
                setPerformanceOverview(performanceData.overview);
            }

            setLoading(false);
        } catch (error) {
            console.error('Error fetching MT5 data:', error);
            setLoading(false);
        }
    };

    const handleUpdateCredentials = async () => {
        if (!selectedAccount) return;

        try {
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/mt5/admin/credentials/update`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    client_id: selectedAccount.client_id,
                    fund_code: selectedAccount.fund_code,
                    mt5_login: parseInt(newCredentials.mt5_login),
                    mt5_password: newCredentials.mt5_password,
                    mt5_server: newCredentials.mt5_server
                }),
            });

            const data = await response.json();

            if (data.success) {
                alert('MT5 credentials updated successfully');
                setCredentialsModal(false);
                setNewCredentials({ mt5_login: '', mt5_password: '', mt5_server: '' });
                fetchMT5Data(); // Refresh data
            } else {
                alert('Failed to update credentials');
            }
        } catch (error) {
            console.error('Error updating credentials:', error);
            alert('Error updating credentials');
        }
    };

    const handleDisconnectAccount = async (accountId) => {
        if (window.confirm('Are you sure you want to disconnect this MT5 account?')) {
            try {
                const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/mt5/admin/account/${accountId}/disconnect`, {
                    method: 'POST',
                });

                const data = await response.json();

                if (data.success) {
                    alert('Account disconnected successfully');
                    fetchMT5Data(); // Refresh data
                } else {
                    alert('Failed to disconnect account');
                }
            } catch (error) {
                console.error('Error disconnecting account:', error);
                alert('Error disconnecting account');
            }
        }
    };

    const openCredentialsModal = (account) => {
        setSelectedAccount(account);
        setNewCredentials({
            mt5_login: account.mt5_login.toString(),
            mt5_password: '',
            mt5_server: account.mt5_server
        });
        setCredentialsModal(true);
    };

    const getConnectionStatusColor = (status) => {
        switch (status) {
            case 'connected': return 'text-green-600';
            case 'disconnected': return 'text-red-600';
            case 'connecting': return 'text-yellow-600';
            default: return 'text-gray-600';
        }
    };

    const formatCurrency = (amount) => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 2,
        }).format(amount);
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center h-64">
                <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-indigo-600"></div>
            </div>
        );
    }

    return (
        <div className="p-6 max-w-7xl mx-auto">
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-gray-900 mb-2">MT5 Account Management</h1>
                <p className="text-gray-600">Manage client MT5 accounts and monitor real-time performance</p>
            </div>

            {/* Performance Overview */}
            {performanceOverview && (
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                    <Card>
                        <CardContent className="p-6">
                            <div className="text-2xl font-bold text-indigo-600">
                                {performanceOverview.total_accounts}
                            </div>
                            <div className="text-sm text-gray-600">Total MT5 Accounts</div>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardContent className="p-6">
                            <div className="text-2xl font-bold text-blue-600">
                                {formatCurrency(performanceOverview.total_allocated)}
                            </div>
                            <div className="text-sm text-gray-600">Total Allocated</div>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardContent className="p-6">
                            <div className="text-2xl font-bold text-green-600">
                                {formatCurrency(performanceOverview.total_equity)}
                            </div>
                            <div className="text-sm text-gray-600">Total Equity</div>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardContent className="p-6">
                            <div className={`text-2xl font-bold ${performanceOverview.overall_performance_percentage >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                {performanceOverview.overall_performance_percentage.toFixed(2)}%
                            </div>
                            <div className="text-sm text-gray-600">Overall Performance</div>
                        </CardContent>
                    </Card>
                </div>
            )}

            {/* Fund Performance Breakdown */}
            {performanceOverview && performanceOverview.fund_breakdown && (
                <Card className="mb-8">
                    <CardHeader>
                        <CardTitle>Fund Performance Breakdown</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                            {performanceOverview.fund_breakdown.map((fund) => (
                                <div key={fund.fund_code} className="bg-gray-50 p-4 rounded-lg">
                                    <div className="font-semibold text-lg">{fund.fund_code}</div>
                                    <div className="text-sm text-gray-600 mb-2">{fund.accounts_count} accounts</div>
                                    <div className="space-y-1">
                                        <div className="flex justify-between">
                                            <span className="text-sm">Allocated:</span>
                                            <span className="text-sm font-medium">{formatCurrency(fund.total_allocated)}</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="text-sm">Equity:</span>
                                            <span className="text-sm font-medium">{formatCurrency(fund.total_equity)}</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="text-sm">Performance:</span>
                                            <span className={`text-sm font-medium ${fund.performance_percentage >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                                {fund.performance_percentage.toFixed(2)}%
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </CardContent>
                </Card>
            )}

            {/* MT5 Accounts Table */}
            <Card>
                <CardHeader>
                    <CardTitle>MT5 Accounts</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="overflow-x-auto">
                        <table className="w-full border-collapse">
                            <thead>
                                <tr className="border-b bg-gray-50">
                                    <th className="text-left p-3 font-semibold">Client</th>
                                    <th className="text-left p-3 font-semibold">Fund</th>
                                    <th className="text-left p-3 font-semibold">MT5 Login</th>
                                    <th className="text-left p-3 font-semibold">Server</th>
                                    <th className="text-left p-3 font-semibold">Allocated</th>
                                    <th className="text-left p-3 font-semibold">Current Equity</th>
                                    <th className="text-left p-3 font-semibold">P&L</th>
                                    <th className="text-left p-3 font-semibold">Status</th>
                                    <th className="text-left p-3 font-semibold">Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {mt5Accounts.map((account) => (
                                    <tr key={account.account_id} className="border-b hover:bg-gray-50">
                                        <td className="p-3">
                                            <div>
                                                <div className="font-medium">{account.client_name}</div>
                                                <div className="text-sm text-gray-600">{account.client_id}</div>
                                            </div>
                                        </td>
                                        <td className="p-3">
                                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                                {account.fund_code}
                                            </span>
                                        </td>
                                        <td className="p-3 font-mono">{account.mt5_login}</td>
                                        <td className="p-3 text-sm">{account.mt5_server}</td>
                                        <td className="p-3">{formatCurrency(account.total_allocated)}</td>
                                        <td className="p-3">{formatCurrency(account.current_equity)}</td>
                                        <td className="p-3">
                                            <div className={account.profit_loss >= 0 ? 'text-green-600' : 'text-red-600'}>
                                                {formatCurrency(account.profit_loss)}
                                                <div className="text-xs">
                                                    ({account.profit_loss_percentage.toFixed(2)}%)
                                                </div>
                                            </div>
                                        </td>
                                        <td className="p-3">
                                            <span className={`capitalize ${getConnectionStatusColor(account.connection_status)}`}>
                                                {account.connection_status}
                                            </span>
                                            {account.positions_count > 0 && (
                                                <div className="text-xs text-gray-600">
                                                    {account.positions_count} positions
                                                </div>
                                            )}
                                        </td>
                                        <td className="p-3">
                                            <div className="flex space-x-2">
                                                <button
                                                    onClick={() => openCredentialsModal(account)}
                                                    className="text-blue-600 hover:text-blue-800 text-sm"
                                                >
                                                    Edit
                                                </button>
                                                <button
                                                    onClick={() => handleDisconnectAccount(account.account_id)}
                                                    className="text-red-600 hover:text-red-800 text-sm"
                                                >
                                                    Disconnect
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>

                        {mt5Accounts.length === 0 && (
                            <div className="text-center py-8 text-gray-500">
                                No MT5 accounts found
                            </div>
                        )}
                    </div>
                </CardContent>
            </Card>

            {/* Credentials Modal */}
            {credentialsModal && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white rounded-lg p-6 w-96 max-w-90vw">
                        <h3 className="text-lg font-semibold mb-4">Update MT5 Credentials</h3>
                        
                        {selectedAccount && (
                            <div className="mb-4 p-3 bg-gray-100 rounded">
                                <div className="text-sm">
                                    <strong>Client:</strong> {selectedAccount.client_name}
                                </div>
                                <div className="text-sm">
                                    <strong>Fund:</strong> {selectedAccount.fund_code}
                                </div>
                            </div>
                        )}

                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    MT5 Login
                                </label>
                                <input
                                    type="number"
                                    value={newCredentials.mt5_login}
                                    onChange={(e) => setNewCredentials({
                                        ...newCredentials,
                                        mt5_login: e.target.value
                                    })}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    MT5 Password
                                </label>
                                <input
                                    type="password"
                                    value={newCredentials.mt5_password}
                                    onChange={(e) => setNewCredentials({
                                        ...newCredentials,
                                        mt5_password: e.target.value
                                    })}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    placeholder="Enter new password"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    MT5 Server
                                </label>
                                <input
                                    type="text"
                                    value={newCredentials.mt5_server}
                                    onChange={(e) => setNewCredentials({
                                        ...newCredentials,
                                        mt5_server: e.target.value
                                    })}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                />
                            </div>
                        </div>

                        <div className="flex justify-end space-x-3 mt-6">
                            <button
                                onClick={() => {
                                    setCredentialsModal(false);
                                    setNewCredentials({ mt5_login: '', mt5_password: '', mt5_server: '' });
                                }}
                                className="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={handleUpdateCredentials}
                                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                            >
                                Update Credentials
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default MT5Management;