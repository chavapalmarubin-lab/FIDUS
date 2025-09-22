import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Badge } from './ui/badge';
import { Alert, AlertDescription } from './ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import {
  Users,
  Plus,
  Edit2,
  Trash2,
  UserCheck,
  Mail,
  Phone,
  Calendar,
  Search,
  Filter,
  Download,
  Upload,
  Settings,
  ShieldCheck,
  AlertCircle,
  Eye,
  EyeOff,
  Key,
  UserPlus,
  UserMinus,
  MoreVertical
} from 'lucide-react';
import apiAxios from '../utils/apiAxios';

const UserAdministration = () => {
  const [users, setUsers] = useState([]);
  const [filteredUsers, setFilteredUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [typeFilter, setTypeFilter] = useState('all');
  
  // Modal states
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  
  // Form data
  const [createFormData, setCreateFormData] = useState({
    name: '',
    email: '',
    phone: '',
    username: '',
    temporary_password: '',
    notes: ''
  });
  
  const [editFormData, setEditFormData] = useState({
    name: '',
    email: '',
    phone: '',
    notes: '',
    status: 'active'
  });
  
  const [passwordFormData, setPasswordFormData] = useState({
    new_password: '',
    confirm_password: '',
    must_change: true
  });

  useEffect(() => {
    fetchUsers();
  }, []);

  useEffect(() => {
    filterUsers();
  }, [users, searchTerm, statusFilter, typeFilter]);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      // Mock user data - in production this would be a real API call
      const mockUsers = [
        {
          id: 'admin_001',
          username: 'admin',
          name: 'Investment Committee',
          email: 'ic@fidus.com',
          phone: '+1-555-0100',
          type: 'admin',
          status: 'active',
          created_at: '2024-01-15T10:00:00Z',
          last_login: '2024-09-22T08:30:00Z',
          notes: 'Main admin account'
        },
        {
          id: 'client_003',
          username: 'client3',
          name: 'SALVADOR PALMA',
          email: 'chava@alyarglobal.com',
          phone: '+1-555-0200',
          type: 'client',
          status: 'active',
          created_at: '2024-02-01T14:30:00Z',
          last_login: '2024-09-21T16:45:00Z',
          notes: 'VIP client - BALANCE fund investor'
        },
        {
          id: 'client_001',
          username: 'client1',
          name: 'Gerardo Briones',
          email: 'g.b@fidus.com',
          phone: '+1-555-0300',
          type: 'client',
          status: 'active',
          created_at: '2024-03-15T09:20:00Z',
          last_login: '2024-09-20T11:15:00Z',
          notes: 'Regular client'
        },
        {
          id: 'client_002',
          username: 'client2',
          name: 'Maria Rodriguez',
          email: 'm.rodriguez@fidus.com',
          phone: '+1-555-0400',
          type: 'client',
          status: 'inactive',
          created_at: '2024-04-10T13:45:00Z',
          last_login: '2024-08-15T10:30:00Z',
          notes: 'Account suspended pending verification'
        }
      ];
      
      setUsers(mockUsers);
      setError('');
    } catch (err) {
      setError('Failed to fetch users');
      console.error('Error fetching users:', err);
    } finally {
      setLoading(false);
    }
  };

  const filterUsers = () => {
    let filtered = [...users];

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(user =>
        user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
        user.username.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Status filter
    if (statusFilter !== 'all') {
      filtered = filtered.filter(user => user.status === statusFilter);
    }

    // Type filter
    if (typeFilter !== 'all') {
      filtered = filtered.filter(user => user.type === typeFilter);
    }

    setFilteredUsers(filtered);
  };

  const handleCreateUser = async () => {
    try {
      if (!createFormData.name || !createFormData.email || !createFormData.username || !createFormData.temporary_password) {
        setError('Please fill in all required fields');
        return;
      }

      // Generate temporary password if not provided
      const tempPassword = createFormData.temporary_password || generateTempPassword();

      const response = await apiAxios.post('/admin/users/create', {
        ...createFormData,
        temporary_password: tempPassword
      });

      if (response.data.success) {
        setSuccess(`User created successfully! Username: ${createFormData.username}, Temporary password: ${tempPassword}`);
        setShowCreateModal(false);
        resetCreateForm();
        fetchUsers();
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create user');
    }
  };

  const handleEditUser = async () => {
    try {
      if (!selectedUser) return;

      // Mock update - in production this would be a real API call
      const updatedUsers = users.map(user =>
        user.id === selectedUser.id
          ? { ...user, ...editFormData, updated_at: new Date().toISOString() }
          : user
      );

      setUsers(updatedUsers);
      setSuccess('User updated successfully');
      setShowEditModal(false);
      setSelectedUser(null);
      resetEditForm();
    } catch (err) {
      setError('Failed to update user');
    }
  };

  const handlePasswordReset = async () => {
    try {
      if (!selectedUser) return;
      
      if (passwordFormData.new_password !== passwordFormData.confirm_password) {
        setError('Passwords do not match');
        return;
      }

      if (passwordFormData.new_password.length < 8) {
        setError('Password must be at least 8 characters long');
        return;
      }

      // Mock password reset - in production this would be a real API call
      setSuccess(`Password reset successfully for ${selectedUser.name}`);
      setShowPasswordModal(false);
      setSelectedUser(null);
      resetPasswordForm();
    } catch (err) {
      setError('Failed to reset password');
    }
  };

  const handleDeactivateUser = async (userId, userName) => {
    if (!window.confirm(`Are you sure you want to deactivate user "${userName}"?`)) {
      return;
    }

    try {
      // Mock deactivation - in production this would be a real API call
      const updatedUsers = users.map(user =>
        user.id === userId
          ? { ...user, status: 'inactive', updated_at: new Date().toISOString() }
          : user
      );

      setUsers(updatedUsers);
      setSuccess(`User "${userName}" deactivated successfully`);
    } catch (err) {
      setError('Failed to deactivate user');
    }
  };

  const generateTempPassword = () => {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%';
    let result = '';
    for (let i = 0; i < 12; i++) {
      result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
  };

  const resetCreateForm = () => {
    setCreateFormData({
      name: '',
      email: '',
      phone: '',
      username: '',
      temporary_password: '',
      notes: ''
    });
    setError('');
    setSuccess('');
  };

  const resetEditForm = () => {
    setEditFormData({
      name: '',
      email: '',
      phone: '',
      notes: '',
      status: 'active'
    });
  };

  const resetPasswordForm = () => {
    setPasswordFormData({
      new_password: '',
      confirm_password: '',
      must_change: true
    });
  };

  const openEditModal = (user) => {
    setSelectedUser(user);
    setEditFormData({
      name: user.name,
      email: user.email,
      phone: user.phone || '',
      notes: user.notes || '',
      status: user.status
    });
    setShowEditModal(true);
  };

  const openPasswordModal = (user) => {
    setSelectedUser(user);
    resetPasswordForm();
    setShowPasswordModal(true);
  };

  const getUserStats = () => {
    const active = users.filter(u => u.status === 'active').length;
    const inactive = users.filter(u => u.status === 'inactive').length;
    const admins = users.filter(u => u.type === 'admin').length;
    const clients = users.filter(u => u.type === 'client').length;
    
    return { active, inactive, admins, clients, total: users.length };
  };

  const stats = getUserStats();

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-slate-600">Loading users...</div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">User Administration</h1>
          <p className="text-slate-600">Manage user accounts, permissions, and access</p>
        </div>
        <Button
          onClick={() => setShowCreateModal(true)}
          className="bg-emerald-600 hover:bg-emerald-700"
        >
          <UserPlus className="h-4 w-4 mr-2" />
          Create User
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-600">Total Users</p>
                <p className="text-2xl font-bold text-slate-900">{stats.total}</p>
              </div>
              <Users className="h-8 w-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-600">Active</p>
                <p className="text-2xl font-bold text-green-600">{stats.active}</p>
              </div>
              <UserCheck className="h-8 w-8 text-green-500" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-600">Inactive</p>
                <p className="text-2xl font-bold text-red-600">{stats.inactive}</p>
              </div>
              <UserMinus className="h-8 w-8 text-red-500" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-600">Admins</p>
                <p className="text-2xl font-bold text-purple-600">{stats.admins}</p>
              </div>
              <ShieldCheck className="h-8 w-8 text-purple-500" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-600">Clients</p>
                <p className="text-2xl font-bold text-blue-600">{stats.clients}</p>
              </div>
              <Users className="h-8 w-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters and Search */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
                <Input
                  placeholder="Search users by name, email, or username..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            
            <div className="flex gap-2">
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="px-3 py-2 border border-slate-300 rounded-md text-sm"
              >
                <option value="all">All Status</option>
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
              </select>
              
              <select
                value={typeFilter}
                onChange={(e) => setTypeFilter(e.target.value)}
                className="px-3 py-2 border border-slate-300 rounded-md text-sm"
              >
                <option value="all">All Types</option>
                <option value="admin">Admin</option>
                <option value="client">Client</option>
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {error && (
        <Alert className="border-red-200 bg-red-50">
          <AlertCircle className="h-4 w-4 text-red-600" />
          <AlertDescription className="text-red-700">{error}</AlertDescription>
        </Alert>
      )}

      {success && (
        <Alert className="border-green-200 bg-green-50">
          <UserCheck className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-700">{success}</AlertDescription>
        </Alert>
      )}

      {/* Users Table */}
      <Card>
        <CardHeader>
          <CardTitle>Users ({filteredUsers.length})</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-200">
                  <th className="text-left py-3 px-4 font-medium text-slate-900">User</th>
                  <th className="text-left py-3 px-4 font-medium text-slate-900">Contact</th>
                  <th className="text-left py-3 px-4 font-medium text-slate-900">Type</th>
                  <th className="text-left py-3 px-4 font-medium text-slate-900">Status</th>
                  <th className="text-left py-3 px-4 font-medium text-slate-900">Last Login</th>
                  <th className="text-left py-3 px-4 font-medium text-slate-900">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredUsers.map((user) => (
                  <tr key={user.id} className="border-b border-slate-100 hover:bg-slate-50">
                    <td className="py-3 px-4">
                      <div>
                        <div className="font-medium text-slate-900">{user.name}</div>
                        <div className="text-sm text-slate-600">@{user.username}</div>
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <div className="space-y-1">
                        <div className="flex items-center text-sm text-slate-600">
                          <Mail className="h-3 w-3 mr-1" />
                          {user.email}
                        </div>
                        {user.phone && (
                          <div className="flex items-center text-sm text-slate-600">
                            <Phone className="h-3 w-3 mr-1" />
                            {user.phone}
                          </div>
                        )}
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <Badge
                        className={
                          user.type === 'admin'
                            ? 'bg-purple-100 text-purple-800'
                            : 'bg-blue-100 text-blue-800'
                        }
                      >
                        {user.type}
                      </Badge>
                    </td>
                    <td className="py-3 px-4">
                      <Badge
                        className={
                          user.status === 'active'
                            ? 'bg-green-100 text-green-800'
                            : 'bg-red-100 text-red-800'
                        }
                      >
                        {user.status}
                      </Badge>
                    </td>
                    <td className="py-3 px-4">
                      <div className="text-sm text-slate-600">
                        {user.last_login ? new Date(user.last_login).toLocaleDateString() : 'Never'}
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => openEditModal(user)}
                        >
                          <Edit2 className="h-3 w-3" />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => openPasswordModal(user)}
                        >
                          <Key className="h-3 w-3" />
                        </Button>
                        {user.status === 'active' && user.type !== 'admin' && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleDeactivateUser(user.id, user.name)}
                            className="text-red-600 hover:text-red-700"
                          >
                            <UserMinus className="h-3 w-3" />
                          </Button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Create User Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold mb-4">Create New User</h3>
            
            <div className="space-y-4">
              <div>
                <Label htmlFor="name">Full Name *</Label>
                <Input
                  id="name"
                  value={createFormData.name}
                  onChange={(e) => setCreateFormData({ ...createFormData, name: e.target.value })}
                  placeholder="Enter full name"
                />
              </div>
              
              <div>
                <Label htmlFor="email">Email *</Label>
                <Input
                  id="email"
                  type="email"
                  value={createFormData.email}
                  onChange={(e) => setCreateFormData({ ...createFormData, email: e.target.value })}
                  placeholder="Enter email address"
                />
              </div>
              
              <div>
                <Label htmlFor="username">Username *</Label>
                <Input
                  id="username"
                  value={createFormData.username}
                  onChange={(e) => setCreateFormData({ ...createFormData, username: e.target.value })}
                  placeholder="Enter username"
                />
              </div>
              
              <div>
                <Label htmlFor="phone">Phone</Label>
                <Input
                  id="phone"
                  value={createFormData.phone}
                  onChange={(e) => setCreateFormData({ ...createFormData, phone: e.target.value })}
                  placeholder="Enter phone number"
                />
              </div>
              
              <div>
                <Label htmlFor="temp_password">Temporary Password *</Label>
                <Input
                  id="temp_password"
                  type="password"
                  value={createFormData.temporary_password}
                  onChange={(e) => setCreateFormData({ ...createFormData, temporary_password: e.target.value })}
                  placeholder="Enter temporary password"
                />
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  className="mt-2"
                  onClick={() => setCreateFormData({ ...createFormData, temporary_password: generateTempPassword() })}
                >
                  Generate Password
                </Button>
              </div>
              
              <div>
                <Label htmlFor="notes">Notes</Label>
                <Input
                  id="notes"
                  value={createFormData.notes}
                  onChange={(e) => setCreateFormData({ ...createFormData, notes: e.target.value })}
                  placeholder="Optional notes"
                />
              </div>
            </div>
            
            <div className="flex gap-2 mt-6">
              <Button onClick={handleCreateUser} className="flex-1">
                Create User
              </Button>
              <Button
                variant="outline"
                onClick={() => {
                  setShowCreateModal(false);
                  resetCreateForm();
                }}
                className="flex-1"
              >
                Cancel
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Edit User Modal */}
      {showEditModal && selectedUser && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold mb-4">Edit User: {selectedUser.name}</h3>
            
            <div className="space-y-4">
              <div>
                <Label htmlFor="edit_name">Full Name</Label>
                <Input
                  id="edit_name"
                  value={editFormData.name}
                  onChange={(e) => setEditFormData({ ...editFormData, name: e.target.value })}
                />
              </div>
              
              <div>
                <Label htmlFor="edit_email">Email</Label>
                <Input
                  id="edit_email"
                  type="email"
                  value={editFormData.email}
                  onChange={(e) => setEditFormData({ ...editFormData, email: e.target.value })}
                />
              </div>
              
              <div>
                <Label htmlFor="edit_phone">Phone</Label>
                <Input
                  id="edit_phone"
                  value={editFormData.phone}
                  onChange={(e) => setEditFormData({ ...editFormData, phone: e.target.value })}
                />
              </div>
              
              <div>
                <Label htmlFor="edit_status">Status</Label>
                <select
                  id="edit_status"
                  value={editFormData.status}
                  onChange={(e) => setEditFormData({ ...editFormData, status: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-md"
                >
                  <option value="active">Active</option>
                  <option value="inactive">Inactive</option>
                </select>
              </div>
              
              <div>
                <Label htmlFor="edit_notes">Notes</Label>
                <Input
                  id="edit_notes"
                  value={editFormData.notes}
                  onChange={(e) => setEditFormData({ ...editFormData, notes: e.target.value })}
                />
              </div>
            </div>
            
            <div className="flex gap-2 mt-6">
              <Button onClick={handleEditUser} className="flex-1">
                Update User
              </Button>
              <Button
                variant="outline"
                onClick={() => {
                  setShowEditModal(false);
                  setSelectedUser(null);
                  resetEditForm();
                }}
                className="flex-1"
              >
                Cancel
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Password Reset Modal */}
      {showPasswordModal && selectedUser && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold mb-4">Reset Password: {selectedUser.name}</h3>
            
            <div className="space-y-4">
              <div>
                <Label htmlFor="new_password">New Password</Label>
                <Input
                  id="new_password"
                  type="password"
                  value={passwordFormData.new_password}
                  onChange={(e) => setPasswordFormData({ ...passwordFormData, new_password: e.target.value })}
                  placeholder="Enter new password"
                />
              </div>
              
              <div>
                <Label htmlFor="confirm_password">Confirm Password</Label>
                <Input
                  id="confirm_password"
                  type="password"
                  value={passwordFormData.confirm_password}
                  onChange={(e) => setPasswordFormData({ ...passwordFormData, confirm_password: e.target.value })}
                  placeholder="Confirm new password"
                />
              </div>
              
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="must_change"
                  checked={passwordFormData.must_change}
                  onChange={(e) => setPasswordFormData({ ...passwordFormData, must_change: e.target.checked })}
                />
                <Label htmlFor="must_change">User must change password on next login</Label>
              </div>
            </div>
            
            <div className="flex gap-2 mt-6">
              <Button onClick={handlePasswordReset} className="flex-1">
                Reset Password
              </Button>
              <Button
                variant="outline"
                onClick={() => {
                  setShowPasswordModal(false);
                  setSelectedUser(null);
                  resetPasswordForm();
                }}
                className="flex-1"
              >
                Cancel
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default UserAdministration;