import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Table, 
  Button, 
  Modal, 
  Form, 
  Input, 
  Select, 
  InputNumber,
  Tag,
  Space,
  message,
  Spin
} from 'antd';
import { 
  PlusOutlined, 
  EditOutlined, 
  DeleteOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ReloadOutlined
} from '@ant-design/icons';
import axios from 'axios';

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
