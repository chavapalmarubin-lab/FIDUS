import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Badge } from "./ui/badge";
import { Alert, AlertDescription } from "./ui/alert";
import { 
  Users, 
  Plus, 
  Edit2, 
  Trash2, 
  Search, 
  Filter,
  UserPlus,
  UserCheck,
  CheckCircle,
  XCircle,
  AlertCircle,
  FileText,
  Mail,
  Phone,
  Calendar,
  DollarSign,
  TrendingUp,
  Eye
} from "lucide-react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import apiAxios from "../utils/apiAxios";

const ClientManagement = () => {
  const [clients, setClients] = useState([]);
  const [filteredClients, setFilteredClients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const [filterStatus, setFilterStatus] = useState("all");
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedClient, setSelectedClient] = useState(null);
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    phone: "",
    type: "individual",
    status: "active",
    notes: ""
  });

  useEffect(() => {
    fetchClients();
  }, []);

  useEffect(() => {
    filterClients();
  }, [clients, searchTerm, filterStatus]);

  const fetchClients = async () => {
    try {
      setLoading(true);
      const response = await apiAxios.get('/clients/all');
      setClients(response.data.clients || []);
    } catch (err) {
      setError("Failed to fetch clients");
      console.error("Error fetching clients:", err);
    } finally {
      setLoading(false);
    }
  };

  const filterClients = () => {
    let filtered = clients;

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(client =>
        client.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        client.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
        client.phone.includes(searchTerm)
      );
    }

    // Filter by status
    if (filterStatus !== "all") {
      filtered = filtered.filter(client => client.status === filterStatus);
    }

    setFilteredClients(filtered);
  };

  const handleAddClient = async () => {
    try {
      if (!formData.name || !formData.email || !formData.phone) {
        setError("Please fill in all required fields");
        return;
      }

      const response = await apiAxios.post('/clients/create', formData);
      
      if (response.data.success) {
        setSuccess("Client added successfully");
        setShowAddModal(false);
        resetForm();
        fetchClients();
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to add client");
    }
  };

  const handleUpdateClient = async () => {
    try {
      if (!selectedClient) return;

      const response = await apiAxios.put(`/clients/${selectedClient.id}`, formData);
      
      if (response.data.success) {
        setSuccess("Client updated successfully");
        setShowEditModal(false);
        setSelectedClient(null);
        resetForm();
        fetchClients();
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to update client");
    }
  };

  const handleDeleteClient = async (clientId) => {
    if (!confirm("Are you sure you want to delete this client?")) return;

    try {
      const response = await apiAxios.delete(`/clients/${clientId}`);
      
      if (response.data.success) {
        setSuccess("Client deleted successfully");
        fetchClients();
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to delete client");
    }
  };

  const handleUpdateReadiness = async (clientId, readinessData) => {
    try {
      const response = await apiAxios.put(`/clients/${clientId}/readiness`, readinessData);
      
      if (response.data.success) {
        setSuccess("Client readiness updated successfully");
        fetchClients();
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to update readiness");
    }
  };

  const resetForm = () => {
    setFormData({
      name: "",
      email: "",
      phone: "",
      type: "individual",
      status: "active",
      notes: ""
    });
  };

  const handleEditClient = (client) => {
    setSelectedClient(client);
    setFormData({
      name: client.name,
      email: client.email,
      phone: client.phone,
      type: client.type || "individual",
      status: client.status || "active",
      notes: client.notes || ""
    });
    setShowEditModal(true);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'bg-green-500';
      case 'inactive': return 'bg-gray-500';
      case 'pending': return 'bg-yellow-500';
      default: return 'bg-gray-500';
    }
  };

  const getReadinessStatus = (client) => {
    if (client.investment_ready) {
      return { status: 'Ready', color: 'text-green-500', icon: CheckCircle };
    } else if (client.readiness_status) {
      return { status: 'In Progress', color: 'text-yellow-500', icon: AlertCircle };
    }
    return { status: 'Not Started', color: 'text-red-500', icon: XCircle };
  };

  return (
    <div className="client-management p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-white mb-2">Client Management</h2>
          <p className="text-slate-400">Manage client accounts and investment readiness</p>
        </div>
        <Button onClick={() => setShowAddModal(true)} className="bg-cyan-600 hover:bg-cyan-700">
          <Plus size={16} className="mr-2" />
          Add Client
        </Button>
      </div>

      {/* Alerts */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="mb-4"
          >
            <Alert className="border-red-500 bg-red-500/10">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription className="text-red-400">{error}</AlertDescription>
            </Alert>
          </motion.div>
        )}
        {success && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="mb-4"
          >
            <Alert className="border-green-500 bg-green-500/10">
              <CheckCircle className="h-4 w-4" />
              <AlertDescription className="text-green-400">{success}</AlertDescription>
            </Alert>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Search and Filter */}
      <div className="flex gap-4 mb-6">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-3 h-4 w-4 text-slate-400" />
          <Input
            placeholder="Search clients by name, email, or phone..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10 bg-slate-800 border-slate-600 text-white"
          />
        </div>
        <select
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
          className="px-4 py-2 bg-slate-800 border border-slate-600 rounded-md text-white"
        >
          <option value="all">All Status</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
          <option value="pending">Pending</option>
        </select>
      </div>

      {/* Client Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <Card className="bg-slate-800 border-slate-700">
          <CardContent className="p-4">
            <div className="flex items-center">
              <Users className="h-8 w-8 text-cyan-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-slate-400">Total Clients</p>
                <p className="text-2xl font-bold text-white">{clients.length}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="bg-slate-800 border-slate-700">
          <CardContent className="p-4">
            <div className="flex items-center">
              <UserCheck className="h-8 w-8 text-green-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-slate-400">Ready for Investment</p>
                <p className="text-2xl font-bold text-white">
                  {clients.filter(c => c.investment_ready).length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="bg-slate-800 border-slate-700">
          <CardContent className="p-4">
            <div className="flex items-center">
              <AlertCircle className="h-8 w-8 text-yellow-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-slate-400">In Progress</p>
                <p className="text-2xl font-bold text-white">
                  {clients.filter(c => c.readiness_status && !c.investment_ready).length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="bg-slate-800 border-slate-700">
          <CardContent className="p-4">
            <div className="flex items-center">
              <TrendingUp className="h-8 w-8 text-blue-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-slate-400">Active Clients</p>
                <p className="text-2xl font-bold text-white">
                  {clients.filter(c => c.status === 'active').length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Client List */}
      <Card className="bg-slate-800 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white">Client Directory</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-400 mx-auto mb-4"></div>
              <p className="text-slate-400">Loading clients...</p>
            </div>
          ) : filteredClients.length === 0 ? (
            <div className="text-center py-8">
              <Users className="h-12 w-12 text-slate-500 mx-auto mb-4" />
              <p className="text-slate-400">No clients found</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-slate-600">
                    <th className="text-left py-3 px-4 text-slate-300">Name</th>
                    <th className="text-left py-3 px-4 text-slate-300">Email</th>
                    <th className="text-left py-3 px-4 text-slate-300">Phone</th>
                    <th className="text-left py-3 px-4 text-slate-300">Status</th>
                    <th className="text-left py-3 px-4 text-slate-300">Readiness</th>
                    <th className="text-left py-3 px-4 text-slate-300">Investments</th>
                    <th className="text-left py-3 px-4 text-slate-300">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredClients.map((client) => {
                    const readiness = getReadinessStatus(client);
                    const ReadinessIcon = readiness.icon;
                    
                    return (
                      <tr key={client.id} className="border-b border-slate-700 hover:bg-slate-750">
                        <td className="py-3 px-4">
                          <div className="font-medium text-white">{client.name}</div>
                          <div className="text-sm text-slate-400">{client.type || 'Individual'}</div>
                        </td>
                        <td className="py-3 px-4 text-slate-300">{client.email}</td>
                        <td className="py-3 px-4 text-slate-300">{client.phone}</td>
                        <td className="py-3 px-4">
                          <Badge className={`${getStatusColor(client.status)} text-white`}>
                            {client.status || 'Active'}
                          </Badge>
                        </td>
                        <td className="py-3 px-4">
                          <div className={`flex items-center ${readiness.color}`}>
                            <ReadinessIcon size={16} className="mr-2" />
                            {readiness.status}
                          </div>
                        </td>
                        <td className="py-3 px-4 text-slate-300">
                          {client.total_investments || 0}
                        </td>
                        <td className="py-3 px-4">
                          <div className="flex gap-2">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleEditClient(client)}
                              className="text-cyan-400 border-cyan-400 hover:bg-cyan-400 hover:text-black"
                            >
                              <Edit2 size={14} />
                            </Button>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleDeleteClient(client.id)}
                              className="text-red-400 border-red-400 hover:bg-red-400 hover:text-white"
                            >
                              <Trash2 size={14} />
                            </Button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Add Client Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="bg-slate-800 rounded-lg p-6 w-full max-w-md mx-4"
          >
            <h3 className="text-lg font-semibold text-white mb-4">Add New Client</h3>
            
            <div className="space-y-4">
              <div>
                <Label htmlFor="name" className="text-slate-300">Name *</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="bg-slate-700 border-slate-600 text-white"
                  placeholder="Client name"
                />
              </div>
              
              <div>
                <Label htmlFor="email" className="text-slate-300">Email *</Label>
                <Input
                  id="email"
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="bg-slate-700 border-slate-600 text-white"
                  placeholder="client@example.com"
                />
              </div>
              
              <div>
                <Label htmlFor="phone" className="text-slate-300">Phone *</Label>
                <Input
                  id="phone"
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  className="bg-slate-700 border-slate-600 text-white"
                  placeholder="+1 (555) 123-4567"
                />
              </div>
              
              <div>
                <Label htmlFor="type" className="text-slate-300">Client Type</Label>
                <select
                  id="type"
                  value={formData.type}
                  onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-white"
                >
                  <option value="individual">Individual</option>
                  <option value="corporate">Corporate</option>
                  <option value="trust">Trust</option>
                </select>
              </div>
              
              <div>
                <Label htmlFor="notes" className="text-slate-300">Notes</Label>
                <Input
                  id="notes"
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  className="bg-slate-700 border-slate-600 text-white"
                  placeholder="Additional notes..."
                />
              </div>
            </div>
            
            <div className="flex gap-3 mt-6">
              <Button
                variant="outline"
                onClick={() => {
                  setShowAddModal(false);
                  resetForm();
                }}
                className="flex-1"
              >
                Cancel
              </Button>
              <Button
                onClick={handleAddClient}
                className="flex-1 bg-cyan-600 hover:bg-cyan-700"
              >
                Add Client
              </Button>
            </div>
          </motion.div>
        </div>
      )}

      {/* Edit Client Modal */}
      {showEditModal && selectedClient && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="bg-slate-800 rounded-lg p-6 w-full max-w-md mx-4"
          >
            <h3 className="text-lg font-semibold text-white mb-4">Edit Client</h3>
            
            <div className="space-y-4">
              <div>
                <Label htmlFor="edit-name" className="text-slate-300">Name *</Label>
                <Input
                  id="edit-name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="bg-slate-700 border-slate-600 text-white"
                />
              </div>
              
              <div>
                <Label htmlFor="edit-email" className="text-slate-300">Email *</Label>
                <Input
                  id="edit-email"
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="bg-slate-700 border-slate-600 text-white"
                />
              </div>
              
              <div>
                <Label htmlFor="edit-phone" className="text-slate-300">Phone *</Label>
                <Input
                  id="edit-phone"
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  className="bg-slate-700 border-slate-600 text-white"
                />
              </div>
              
              <div>
                <Label htmlFor="edit-status" className="text-slate-300">Status</Label>
                <select
                  id="edit-status"
                  value={formData.status}
                  onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-white"
                >
                  <option value="active">Active</option>
                  <option value="inactive">Inactive</option>
                  <option value="pending">Pending</option>
                </select>
              </div>
              
              <div>
                <Label htmlFor="edit-notes" className="text-slate-300">Notes</Label>
                <Input
                  id="edit-notes"
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  className="bg-slate-700 border-slate-600 text-white"
                />
              </div>
            </div>
            
            <div className="flex gap-3 mt-6">
              <Button
                variant="outline"
                onClick={() => {
                  setShowEditModal(false);
                  setSelectedClient(null);
                  resetForm();
                }}
                className="flex-1"
              >
                Cancel
              </Button>
              <Button
                onClick={handleUpdateClient}
                className="flex-1 bg-cyan-600 hover:bg-cyan-700"
              >
                Update Client
              </Button>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
};

export default ClientManagement;