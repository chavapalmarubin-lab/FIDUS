import React, { useState, useEffect } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "../components/ui/table";
import { Button } from "../components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "../components/ui/dialog";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "../components/ui/alert-dialog";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../components/ui/select";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Plus, Edit, Trash2, CheckCircle, XCircle, RefreshCw, Loader2 } from "lucide-react";
import axios from 'axios';
import { useToast } from "../components/ui/use-toast";

const MT5AccountManagement = () => {
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [editingAccount, setEditingAccount] = useState(null);
  const [accountToDelete, setAccountToDelete] = useState(null);
  const { toast } = useToast();

  // Form state
  const [formData, setFormData] = useState({
    account: '',
    password: '',
    name: '',
    fund_type: 'BALANCE',
    target_amount: '',
    is_active: true
  });

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'https://cashflow-manager-35.preview.emergentagent.com';

  // ============================================
  // LOAD ACCOUNTS - NO MOCK DATA
  // ============================================
  const loadAccounts = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      
      const response = await axios.get(
        `${BACKEND_URL}/api/admin/mt5/config/accounts`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );
      
      if (response.data.success) {
        setAccounts(response.data.accounts);
        console.log('✅ Loaded accounts from backend:', response.data.count);
      } else {
        toast({
          title: "Error",
          description: "Failed to load accounts",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('Error loading accounts:', error);
      toast({
        title: "Error",
        description: error.response?.data?.detail || error.message,
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAccounts();
  }, []);

  // ============================================
  // HANDLE FORM CHANGE
  // ============================================
  const handleFormChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // ============================================
  // ADD NEW ACCOUNT
  // ============================================
  const handleAddAccount = () => {
    setEditingAccount(null);
    setFormData({
      account: '',
      password: '',
      name: '',
      fund_type: 'BALANCE',
      target_amount: '',
      is_active: true
    });
    setModalOpen(true);
  };

  // ============================================
  // EDIT EXISTING ACCOUNT
  // ============================================
  const handleEditAccount = (account) => {
    setEditingAccount(account);
    setFormData({
      account: account.account,
      password: '',
      name: account.name,
      fund_type: account.fund_type,
      target_amount: account.target_amount,
      is_active: account.is_active
    });
    setModalOpen(true);
  };

  // ============================================
  // SAVE ACCOUNT
  // ============================================
  const handleSaveAccount = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      };

      if (editingAccount) {
        // UPDATE
        const updateData = {
          name: formData.name,
          fund_type: formData.fund_type,
          target_amount: parseFloat(formData.target_amount),
          is_active: formData.is_active
        };
        
        if (formData.password) {
          updateData.password = formData.password;
        }

        await axios.put(
          `${BACKEND_URL}/api/admin/mt5/config/accounts/${editingAccount.account}`,
          updateData,
          { headers }
        );
        
        toast({
          title: "Success",
          description: "Account updated successfully! Changes will sync within 50 minutes.",
        });
      } else {
        // ADD
        const newAccount = {
          account: parseInt(formData.account),
          password: formData.password,
          name: formData.name,
          fund_type: formData.fund_type,
          target_amount: parseFloat(formData.target_amount),
          is_active: formData.is_active
        };

        await axios.post(
          `${BACKEND_URL}/api/admin/mt5/config/accounts`,
          newAccount,
          { headers }
        );
        
        toast({
          title: "Success",
          description: "Account added successfully! Will be synced within 50 minutes.",
        });
      }
      
      setModalOpen(false);
      loadAccounts();
      
    } catch (error) {
      console.error('Error saving account:', error);
      toast({
        title: "Error",
        description: error.response?.data?.detail || error.message,
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  // ============================================
  // DEACTIVATE ACCOUNT
  // ============================================
  const handleDeactivateClick = (account) => {
    setAccountToDelete(account);
    setDeleteDialogOpen(true);
  };

  const confirmDeactivate = async () => {
    if (!accountToDelete) return;
    
    try {
      const token = localStorage.getItem('token');
      
      await axios.delete(
        `${BACKEND_URL}/api/admin/mt5/config/accounts/${accountToDelete.account}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );
      
      toast({
        title: "Success",
        description: "Account deactivated successfully",
      });
      
      setDeleteDialogOpen(false);
      loadAccounts();
    } catch (error) {
      console.error('Error deactivating account:', error);
      toast({
        title: "Error",
        description: error.response?.data?.detail || error.message,
        variant: "destructive",
      });
    }
  };

  // ============================================
  // ACTIVATE ACCOUNT
  // ============================================
  const handleActivateAccount = async (accountNumber) => {
    try {
      const token = localStorage.getItem('token');
      
      await axios.post(
        `${BACKEND_URL}/api/admin/mt5/config/accounts/${accountNumber}/activate`,
        {},
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );
      
      toast({
        title: "Success",
        description: "Account activated successfully! Will resume syncing within 50 minutes.",
      });
      
      loadAccounts();
    } catch (error) {
      console.error('Error activating account:', error);
      toast({
        title: "Error",
        description: error.response?.data?.detail || error.message,
        variant: "destructive",
      });
    }
  };

  // Fund type colors
  const getFundTypeColor = (fundType) => {
    switch (fundType) {
      case 'BALANCE':
        return 'bg-blue-500';
      case 'CORE':
        return 'bg-green-500';
      case 'SEPARATION':
        return 'bg-orange-500';
      default:
        return 'bg-gray-500';
    }
  };

  // ============================================
  // RENDER
  // ============================================
  return (
    <div className="p-6 space-y-6">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-2xl font-bold flex items-center gap-2">
                MT5 Account Management
                <Badge variant="secondary">{accounts.length} Accounts</Badge>
              </CardTitle>
              <CardDescription className="mt-2">
                Manage MT5 trading account configurations. Changes take effect within 50 minutes.
              </CardDescription>
            </div>
            <div className="flex gap-2">
              <Button
                variant="outline"
                onClick={loadAccounts}
                disabled={loading}
              >
                {loading ? (
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                ) : (
                  <RefreshCw className="h-4 w-4 mr-2" />
                )}
                Refresh
              </Button>
              <Button onClick={handleAddAccount}>
                <Plus className="h-4 w-4 mr-2" />
                Add Account
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {loading && accounts.length === 0 ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin" />
            </div>
          ) : (
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Account</TableHead>
                    <TableHead>Name</TableHead>
                    <TableHead>Fund Type</TableHead>
                    <TableHead>Target Amount</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Last Updated</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {accounts.map((account) => (
                    <TableRow key={account.account}>
                      <TableCell className="font-mono font-semibold">
                        #{account.account}
                      </TableCell>
                      <TableCell>{account.name}</TableCell>
                      <TableCell>
                        <Badge className={getFundTypeColor(account.fund_type)}>
                          {account.fund_type}
                        </Badge>
                      </TableCell>
                      <TableCell className="font-semibold">
                        ${account.target_amount?.toLocaleString(undefined, {
                          minimumFractionDigits: 2,
                          maximumFractionDigits: 2
                        }) || '0.00'}
                      </TableCell>
                      <TableCell>
                        <Badge variant={account.is_active ? "default" : "secondary"}>
                          {account.is_active ? (
                            <>
                              <CheckCircle className="h-3 w-3 mr-1" />
                              Active
                            </>
                          ) : (
                            <>
                              <XCircle className="h-3 w-3 mr-1" />
                              Inactive
                            </>
                          )}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-sm text-gray-500">
                        {new Date(account.updated_at).toLocaleDateString()} {new Date(account.updated_at).toLocaleTimeString()}
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleEditAccount(account)}
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          {account.is_active ? (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleDeactivateClick(account)}
                            >
                              <XCircle className="h-4 w-4 text-red-500" />
                            </Button>
                          ) : (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleActivateAccount(account.account)}
                            >
                              <CheckCircle className="h-4 w-4 text-green-500" />
                            </Button>
                          )}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* ADD/EDIT DIALOG */}
      <Dialog open={modalOpen} onOpenChange={setModalOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>
              {editingAccount ? '✏️ Edit MT5 Account' : '➕ Add New MT5 Account'}
            </DialogTitle>
            <DialogDescription>
              {editingAccount 
                ? 'Update account configuration. Changes sync within 50 minutes.'
                : 'Add a new MT5 account. It will be synced within 50 minutes.'}
            </DialogDescription>
          </DialogHeader>

          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="account">Account Number *</Label>
              <Input
                id="account"
                type="number"
                value={formData.account}
                onChange={(e) => handleFormChange('account', e.target.value)}
                disabled={!!editingAccount}
                placeholder="e.g., 886557"
              />
            </div>

            <div className="grid gap-2">
              <Label htmlFor="password">
                Password {!editingAccount && '*'}
              </Label>
              <Input
                id="password"
                type="password"
                value={formData.password}
                onChange={(e) => handleFormChange('password', e.target.value)}
                placeholder={editingAccount ? "Leave blank to keep current" : "Enter password"}
              />
            </div>

            <div className="grid gap-2">
              <Label htmlFor="name">Account Name *</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => handleFormChange('name', e.target.value)}
                placeholder="e.g., Main Balance Account"
              />
            </div>

            <div className="grid gap-2">
              <Label htmlFor="fund_type">Fund Type *</Label>
              <Select
                value={formData.fund_type}
                onValueChange={(value) => handleFormChange('fund_type', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select fund type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="BALANCE">BALANCE - Balanced Fund</SelectItem>
                  <SelectItem value="CORE">CORE - Core Fund</SelectItem>
                  <SelectItem value="SEPARATION">SEPARATION - Separation Fund</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="grid gap-2">
              <Label htmlFor="target_amount">Target Amount *</Label>
              <Input
                id="target_amount"
                type="number"
                value={formData.target_amount}
                onChange={(e) => handleFormChange('target_amount', e.target.value)}
                placeholder="e.g., 100000"
              />
            </div>

            {editingAccount && (
              <div className="grid gap-2">
                <Label htmlFor="is_active">Status</Label>
                <Select
                  value={formData.is_active.toString()}
                  onValueChange={(value) => handleFormChange('is_active', value === 'true')}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="true">Active - Will be synced</SelectItem>
                    <SelectItem value="false">Inactive - Will not be synced</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            )}
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setModalOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleSaveAccount} disabled={loading}>
              {loading && <Loader2 className="h-4 w-4 animate-spin mr-2" />}
              {editingAccount ? 'Update Account' : 'Add Account'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* DELETE CONFIRMATION DIALOG */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Deactivate Account</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to deactivate account #{accountToDelete?.account}? 
              The VPS bridge will stop syncing this account within 50 minutes.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={confirmDeactivate}>
              Yes, Deactivate
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};

export default MT5AccountManagement;

const { Option } = Select;

const MT5AccountManagement = () => {
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingAccount, setEditingAccount] = useState(null);
  const [form] = Form.useForm();

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'https://cashflow-manager-35.preview.emergentagent.com';

  // ============================================
  // LOAD ACCOUNTS - NO MOCK DATA
  // ============================================
  const loadAccounts = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      
      const response = await axios.get(
        `${BACKEND_URL}/api/admin/mt5/config/accounts`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );
      
      if (response.data.success) {
        // ALL DATA FROM BACKEND - NO MOCKS
        setAccounts(response.data.accounts);
        console.log('✅ Loaded accounts from backend:', response.data.count);
      } else {
        message.error('Failed to load accounts');
      }
    } catch (error) {
      console.error('Error loading accounts:', error);
      message.error(`Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAccounts();
  }, []);

  // ============================================
  // ADD NEW ACCOUNT
  // ============================================
  const handleAddAccount = () => {
    setEditingAccount(null);
    form.resetFields();
    setModalVisible(true);
  };

  // ============================================
  // EDIT EXISTING ACCOUNT
  // ============================================
  const handleEditAccount = (account) => {
    setEditingAccount(account);
    form.setFieldsValue({
      account: account.account,
      name: account.name,
      fund_type: account.fund_type,
      target_amount: account.target_amount,
      is_active: account.is_active
    });
    setModalVisible(true);
  };

  // ============================================
  // SAVE ACCOUNT (ADD OR UPDATE)
  // ============================================
  const handleSaveAccount = async (values) => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      };

      if (editingAccount) {
        // UPDATE existing account
        const updateData = {
          name: values.name,
          fund_type: values.fund_type,
          target_amount: values.target_amount,
          is_active: values.is_active
        };
        
        // Only include password if provided
        if (values.password) {
          updateData.password = values.password;
        }

        await axios.put(
          `${BACKEND_URL}/api/admin/mt5/config/accounts/${editingAccount.account}`,
          updateData,
          { headers }
        );
        
        message.success('Account updated successfully! Changes will sync within 50 minutes.');
      } else {
        // ADD new account
        await axios.post(
          `${BACKEND_URL}/api/admin/mt5/config/accounts`,
          values,
          { headers }
        );
        
        message.success('Account added successfully! Will be synced within 50 minutes.');
      }
      
      setModalVisible(false);
      form.resetFields();
      loadAccounts(); // Reload to show updated data
      
    } catch (error) {
      console.error('Error saving account:', error);
      const errorMsg = error.response?.data?.detail || error.message;
      message.error(`Error: ${errorMsg}`);
    } finally {
      setLoading(false);
    }
  };

  // ============================================
  // DEACTIVATE ACCOUNT
  // ============================================
  const handleDeactivateAccount = async (accountNumber) => {
    Modal.confirm({
      title: 'Deactivate Account',
      content: `Are you sure you want to deactivate account ${accountNumber}? The VPS bridge will stop syncing this account within 50 minutes.`,
      okText: 'Yes, Deactivate',
      okType: 'danger',
      cancelText: 'Cancel',
      onOk: async () => {
        try {
          const token = localStorage.getItem('token');
          
          await axios.delete(
            `${BACKEND_URL}/api/admin/mt5/config/accounts/${accountNumber}`,
            {
              headers: {
                'Authorization': `Bearer ${token}`
              }
            }
          );
          
          message.success('Account deactivated successfully');
          loadAccounts();
        } catch (error) {
          console.error('Error deactivating account:', error);
          message.error(`Error: ${error.response?.data?.detail || error.message}`);
        }
      }
    });
  };

  // ============================================
  // ACTIVATE ACCOUNT
  // ============================================
  const handleActivateAccount = async (accountNumber) => {
    try {
      const token = localStorage.getItem('token');
      
      await axios.post(
        `${BACKEND_URL}/api/admin/mt5/config/accounts/${accountNumber}/activate`,
        {},
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );
      
      message.success('Account activated successfully! Will resume syncing within 50 minutes.');
      loadAccounts();
    } catch (error) {
      console.error('Error activating account:', error);
      message.error(`Error: ${error.response?.data?.detail || error.message}`);
    }
  };

  // ============================================
  // TABLE COLUMNS
  // ============================================
  const columns = [
    {
      title: 'Account',
      dataIndex: 'account',
      key: 'account',
      width: 120,
      sorter: (a, b) => a.account - b.account,
      render: (account) => <strong className="text-blue-600">#{account}</strong>
    },
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      ellipsis: true,
    },
    {
      title: 'Fund Type',
      dataIndex: 'fund_type',
      key: 'fund_type',
      width: 120,
      filters: [
        { text: 'BALANCE', value: 'BALANCE' },
        { text: 'CORE', value: 'CORE' },
        { text: 'SEPARATION', value: 'SEPARATION' },
      ],
      onFilter: (value, record) => record.fund_type === value,
      render: (fundType) => {
        const colors = {
          'BALANCE': 'blue',
          'CORE': 'green',
          'SEPARATION': 'orange'
        };
        return <Tag color={colors[fundType]}>{fundType}</Tag>;
      }
    },
    {
      title: 'Target Amount',
      dataIndex: 'target_amount',
      key: 'target_amount',
      width: 150,
      sorter: (a, b) => a.target_amount - b.target_amount,
      render: (amount) => (
        <span className="font-semibold">
          ${amount?.toLocaleString(undefined, {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
          }) || '0.00'}
        </span>
      )
    },
    {
      title: 'Status',
      dataIndex: 'is_active',
      key: 'is_active',
      width: 100,
      filters: [
        { text: 'Active', value: true },
        { text: 'Inactive', value: false },
      ],
      onFilter: (value, record) => record.is_active === value,
      render: (isActive) => (
        <Tag color={isActive ? 'success' : 'default'} icon={isActive ? <CheckCircleOutlined /> : <CloseCircleOutlined />}>
          {isActive ? 'Active' : 'Inactive'}
        </Tag>
      )
    },
    {
      title: 'Last Updated',
      dataIndex: 'updated_at',
      key: 'updated_at',
      width: 180,
      render: (date) => new Date(date).toLocaleString()
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 200,
      fixed: 'right',
      render: (_, record) => (
        <Space size="small">
          <Button
            icon={<EditOutlined />}
            size="small"
            onClick={() => handleEditAccount(record)}
            type="link"
          >
            Edit
          </Button>
          {record.is_active ? (
            <Button
              icon={<CloseCircleOutlined />}
              size="small"
              danger
              onClick={() => handleDeactivateAccount(record.account)}
              type="link"
            >
              Deactivate
            </Button>
          ) : (
            <Button
              icon={<CheckCircleOutlined />}
              size="small"
              type="link"
              style={{ color: '#52c41a' }}
              onClick={() => handleActivateAccount(record.account)}
            >
              Activate
            </Button>
          )}
        </Space>
      )
    }
  ];

  // ============================================
  // RENDER
  // ============================================
  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <Card
        title={
          <div className="flex items-center gap-2">
            <span className="text-2xl font-bold">MT5 Account Management</span>
            <Tag color="blue">{accounts.length} Accounts</Tag>
          </div>
        }
        extra={
          <Space>
            <Button
              icon={<ReloadOutlined />}
              onClick={loadAccounts}
              loading={loading}
            >
              Refresh
            </Button>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={handleAddAccount}
              size="large"
            >
              Add Account
            </Button>
          </Space>
        }
        className="shadow-lg"
      >
        <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-sm text-gray-700">
            <strong>ℹ️ Note:</strong> Changes to account configurations will take effect on the VPS bridge within 50 minutes.
            The bridge automatically reloads active accounts every 50 minutes.
          </p>
        </div>

        <Table
          columns={columns}
          dataSource={accounts}
          rowKey="account"
          loading={loading}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showTotal: (total) => `Total ${total} accounts`
          }}
          scroll={{ x: 1200 }}
          bordered
        />
      </Card>

      {/* ADD/EDIT MODAL */}
      <Modal
        title={
          <div className="flex items-center gap-2">
            <span className="text-xl font-semibold">
              {editingAccount ? '✏️ Edit MT5 Account' : '➕ Add New MT5 Account'}
            </span>
          </div>
        }
        open={modalVisible}
        onCancel={() => {
          setModalVisible(false);
          form.resetFields();
        }}
        onOk={() => form.submit()}
        confirmLoading={loading}
        width={600}
        okText={editingAccount ? 'Update Account' : 'Add Account'}
        cancelText="Cancel"
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSaveAccount}
          className="mt-4"
        >
          <Form.Item
            name="account"
            label="Account Number"
            rules={[
              { required: true, message: 'Please enter account number' },
              { type: 'number', min: 1, message: 'Must be a positive number' }
            ]}
          >
            <InputNumber
              style={{ width: '100%' }}
              disabled={!!editingAccount}
              placeholder="e.g., 886557"
              size="large"
            />
          </Form.Item>

          <Form.Item
            name="password"
            label="Password"
            rules={[
              { required: !editingAccount, message: 'Password is required for new accounts' }
            ]}
          >
            <Input.Password
              placeholder={editingAccount ? "Leave blank to keep current password" : "Enter account password"}
              size="large"
            />
          </Form.Item>

          <Form.Item
            name="name"
            label="Account Name"
            rules={[
              { required: true, message: 'Please enter account name' },
              { min: 3, message: 'Name must be at least 3 characters' }
            ]}
          >
            <Input 
              placeholder="e.g., Main Balance Account" 
              size="large"
            />
          </Form.Item>

          <Form.Item
            name="fund_type"
            label="Fund Type"
            rules={[{ required: true, message: 'Please select fund type' }]}
          >
            <Select placeholder="Select fund type" size="large">
              <Option value="BALANCE">
                <Tag color="blue">BALANCE</Tag> - Balanced Fund
              </Option>
              <Option value="CORE">
                <Tag color="green">CORE</Tag> - Core Fund
              </Option>
              <Option value="SEPARATION">
                <Tag color="orange">SEPARATION</Tag> - Separation Fund
              </Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="target_amount"
            label="Target Amount"
            rules={[
              { required: true, message: 'Please enter target amount' },
              { type: 'number', min: 0, message: 'Must be a positive number' }
            ]}
          >
            <InputNumber
              style={{ width: '100%' }}
              prefix="$"
              formatter={value => `${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
              parser={value => value.replace(/\$\s?|(,*)/g, '')}
              placeholder="Enter target amount"
              size="large"
            />
          </Form.Item>

          {editingAccount && (
            <Form.Item
              name="is_active"
              label="Status"
              initialValue={true}
            >
              <Select size="large">
                <Option value={true}>
                  <Tag color="success">Active</Tag> - Account will be synced
                </Option>
                <Option value={false}>
                  <Tag color="default">Inactive</Tag> - Account will not be synced
                </Option>
              </Select>
            </Form.Item>
          )}
        </Form>
      </Modal>
    </div>
  );
};

export default MT5AccountManagement;
