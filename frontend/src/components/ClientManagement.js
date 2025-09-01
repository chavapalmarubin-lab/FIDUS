import React, { useState, useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Badge } from "./ui/badge";
import { Alert, AlertDescription } from "./ui/alert";
import { 
  Download, 
  Upload, 
  Search, 
  Filter,
  Users,
  DollarSign,
  TrendingUp,
  MoreHorizontal,
  Eye,
  Edit,
  Trash2,
  FileSpreadsheet,
  RefreshCw,
  CheckCircle,
  AlertCircle,
  UserPlus
} from "lucide-react";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ClientManagement = () => {
  const [clients, setClients] = useState([]);
  const [filteredClients, setFilteredClients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [sortBy, setSortBy] = useState("created_at");
  const [sortOrder, setSortOrder] = useState("desc");
  const [selectedClients, setSelectedClients] = useState([]);
  const [summary, setSummary] = useState({});
  const [uploadLoading, setUploadLoading] = useState(false);
  const [downloadLoading, setDownloadLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  
  const fileInputRef = useRef(null);

  useEffect(() => {
    fetchClients();
  }, []);

  useEffect(() => {
    applyFiltersAndSort();
  }, [clients, searchTerm, statusFilter, sortBy, sortOrder]);

  const fetchClients = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/admin/clients/detailed`);
      setClients(response.data.clients);
      setSummary({
        total: response.data.total_clients,
        active: response.data.active_clients,
        totalAUM: response.data.total_aum
      });
    } catch (err) {
      setError("Failed to fetch clients data");
      console.error("Error fetching clients:", err);
    } finally {
      setLoading(false);
    }
  };

  const applyFiltersAndSort = () => {
    let filtered = [...clients];

    // Apply search filter
    if (searchTerm) {
      filtered = filtered.filter(client => 
        client.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        client.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
        client.username.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Apply status filter
    if (statusFilter !== "all") {
      filtered = filtered.filter(client => client.status === statusFilter);
    }

    // Apply sorting
    filtered.sort((a, b) => {
      let aValue, bValue;
      
      switch (sortBy) {
        case "name":
          aValue = a.name.toLowerCase();
          bValue = b.name.toLowerCase();
          break;
        case "balance":
          aValue = a.balances.total;
          bValue = b.balances.total;
          break;
        case "created_at":
          aValue = new Date(a.created_at);
          bValue = new Date(b.created_at);
          break;
        case "last_activity":
          aValue = new Date(a.activity.last_activity);
          bValue = new Date(b.activity.last_activity);
          break;
        default:
          aValue = a[sortBy];
          bValue = b[sortBy];
      }

      if (aValue < bValue) return sortOrder === "asc" ? -1 : 1;
      if (aValue > bValue) return sortOrder === "asc" ? 1 : -1;
      return 0;
    });

    setFilteredClients(filtered);
  };

  const handleExportClients = async () => {
    try {
      setDownloadLoading(true);
      setError("");
      
      const response = await axios.get(`${API}/admin/clients/export`);
      
      if (response.data.success) {
        // Create and download file
        const blob = new Blob([response.data.data], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = response.data.filename;
        link.click();
        window.URL.revokeObjectURL(url);
        
        setSuccess(`Successfully exported ${response.data.total_clients} clients`);
      }
    } catch (err) {
      setError("Failed to export clients data");
      console.error("Export error:", err);
    } finally {
      setDownloadLoading(false);
    }
  };

  const handleImportClients = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Validate file type
    const allowedTypes = ['.xlsx', '.xls', '.csv'];
    const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
    
    if (!allowedTypes.includes(fileExtension)) {
      setError("Please upload an Excel (.xlsx, .xls) or CSV file");
      return;
    }

    try {
      setUploadLoading(true);
      setError("");
      
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await axios.post(`${API}/admin/clients/import`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      if (response.data.success) {
        setSuccess(`Successfully imported ${response.data.imported} new clients and updated ${response.data.updated} existing clients`);
        fetchClients(); // Refresh the data
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to import clients data");
      console.error("Import error:", err);
    } finally {
      setUploadLoading(false);
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleStatusUpdate = async (clientId, newStatus) => {
    try {
      const response = await axios.put(`${API}/admin/clients/${clientId}/status`, {
        status: newStatus
      });
      
      if (response.data.success) {
        setSuccess(`Client status updated to ${newStatus}`);
        fetchClients(); // Refresh data
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to update client status");
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(amount);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const getStatusBadgeVariant = (status) => {
    switch (status?.toLowerCase()) {
      case 'active': return 'default';
      case 'inactive': return 'secondary';
      case 'suspended': return 'destructive';
      default: return 'outline';
    }
  };

  const getRiskLevelColor = (risk) => {
    switch (risk?.toLowerCase()) {
      case 'low': return 'text-green-400';
      case 'medium': return 'text-yellow-400';
      case 'high': return 'text-red-400';
      default: return 'text-slate-400';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="text-white text-xl">Loading clients...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="dashboard-card">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">Total Clients</p>
                <p className="text-2xl font-bold text-white">{summary.total || 0}</p>
              </div>
              <Users className="h-8 w-8 text-cyan-400" />
            </div>
          </CardContent>
        </Card>

        <Card className="dashboard-card">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">Active Clients</p>
                <p className="text-2xl font-bold text-green-400">{summary.active || 0}</p>
              </div>
              <CheckCircle className="h-8 w-8 text-green-400" />
            </div>
          </CardContent>
        </Card>

        <Card className="dashboard-card">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">Total AUM</p>
                <p className="text-2xl font-bold text-cyan-400">{formatCurrency(summary.totalAUM || 0)}</p>
              </div>
              <DollarSign className="h-8 w-8 text-cyan-400" />
            </div>
          </CardContent>
        </Card>

        <Card className="dashboard-card">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">Growth Rate</p>
                <p className="text-2xl font-bold text-green-400">+12.5%</p>
              </div>
              <TrendingUp className="h-8 w-8 text-green-400" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Controls Section */}
      <Card className="dashboard-card">
        <CardHeader>
          <CardTitle className="text-white flex items-center justify-between">
            <span>Client Database Management</span>
            <div className="flex gap-2">
              <Button 
                onClick={() => fileInputRef.current?.click()}
                disabled={uploadLoading}
                variant="outline"
                size="sm"
                className="text-white border-slate-600"
              >
                {uploadLoading ? (
                  <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <Upload className="mr-2 h-4 w-4" />
                )}
                Import Excel
              </Button>
              <Button 
                onClick={handleExportClients}
                disabled={downloadLoading}
                variant="outline"
                size="sm"
                className="text-white border-slate-600"
              >
                {downloadLoading ? (
                  <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <Download className="mr-2 h-4 w-4" />
                )}
                Export Excel
              </Button>
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <input
            ref={fileInputRef}
            type="file"
            accept=".xlsx,.xls,.csv"
            onChange={handleImportClients}
            className="hidden"
          />
          
          {/* Filters and Search */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div>
              <Label className="text-slate-300">Search Clients</Label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400" size={16} />
                <Input
                  placeholder="Search by name, email, or username..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 bg-slate-800 border-slate-600 text-white"
                />
              </div>
            </div>

            <div>
              <Label className="text-slate-300">Status Filter</Label>
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger className="bg-slate-800 border-slate-600 text-white">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-slate-800 border-slate-600">
                  <SelectItem value="all" className="text-white">All Status</SelectItem>
                  <SelectItem value="active" className="text-white">Active</SelectItem>
                  <SelectItem value="inactive" className="text-white">Inactive</SelectItem>
                  <SelectItem value="suspended" className="text-white">Suspended</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label className="text-slate-300">Sort By</Label>
              <Select value={sortBy} onValueChange={setSortBy}>
                <SelectTrigger className="bg-slate-800 border-slate-600 text-white">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-slate-800 border-slate-600">
                  <SelectItem value="name" className="text-white">Name</SelectItem>
                  <SelectItem value="created_at" className="text-white">Registration Date</SelectItem>
                  <SelectItem value="balance" className="text-white">Total Balance</SelectItem>
                  <SelectItem value="last_activity" className="text-white">Last Activity</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label className="text-slate-300">Order</Label>
              <Select value={sortOrder} onValueChange={setSortOrder}>
                <SelectTrigger className="bg-slate-800 border-slate-600 text-white">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-slate-800 border-slate-600">
                  <SelectItem value="desc" className="text-white">Descending</SelectItem>
                  <SelectItem value="asc" className="text-white">Ascending</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Alerts */}
          {error && (
            <Alert className="mb-4 bg-red-900/20 border-red-600">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription className="text-red-400">{error}</AlertDescription>
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={() => setError("")}
                className="ml-auto text-red-400 hover:bg-red-900/30"
              >
                ×
              </Button>
            </Alert>
          )}

          {success && (
            <Alert className="mb-4 bg-green-900/20 border-green-600">
              <CheckCircle className="h-4 w-4" />
              <AlertDescription className="text-green-400">{success}</AlertDescription>
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={() => setSuccess("")}
                className="ml-auto text-green-400 hover:bg-green-900/30"
              >
                ×
              </Button>
            </Alert>
          )}

          {/* File Upload Instructions */}
          <Alert className="mb-6 bg-slate-800 border-slate-600">
            <FileSpreadsheet className="h-4 w-4" />
            <AlertDescription className="text-slate-300">
              <strong>Excel Import Format:</strong> Your Excel file should include columns: Full_Name, Email, Username, Status, Total_Balance, FIDUS_Funds, Core_Balance, Dynamic_Balance. 
              <Button variant="link" className="p-0 h-auto text-cyan-400" onClick={handleExportClients}>
                Download template
              </Button>
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>

      {/* Clients Table */}
      <Card className="dashboard-card">
        <CardHeader>
          <CardTitle className="text-white">
            Client Database ({filteredClients.length} of {clients.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-600">
                  <th className="text-left p-3 text-slate-300">Client</th>
                  <th className="text-left p-3 text-slate-300">Contact</th>
                  <th className="text-left p-3 text-slate-300">Balance</th>
                  <th className="text-left p-3 text-slate-300">Status</th>
                  <th className="text-left p-3 text-slate-300">Activity</th>
                  <th className="text-left p-3 text-slate-300">Compliance</th>
                  <th className="text-left p-3 text-slate-300">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredClients.map((client, index) => (
                  <motion.tr
                    key={client.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3, delay: index * 0.02 }}
                    className="border-b border-slate-700 hover:bg-slate-800/50"
                  >
                    <td className="p-3">
                      <div className="flex items-center gap-3">
                        <img 
                          src={client.profile_picture} 
                          alt={client.name}
                          className="w-10 h-10 rounded-full object-cover"
                        />
                        <div>
                          <div className="text-white font-medium">{client.name}</div>
                          <div className="text-slate-400 text-sm">ID: {client.id}</div>
                        </div>
                      </div>
                    </td>
                    <td className="p-3">
                      <div className="text-white">{client.email}</div>
                      <div className="text-slate-400 text-sm">{client.personal?.phone || "N/A"}</div>
                    </td>
                    <td className="p-3">
                      <div className="text-cyan-400 font-semibold">{formatCurrency(client.balances.total)}</div>
                      <div className="text-slate-400 text-sm">
                        F: {formatCurrency(client.balances.fidus)} | 
                        C: {formatCurrency(client.balances.core)} | 
                        D: {formatCurrency(client.balances.dynamic)}
                      </div>
                    </td>
                    <td className="p-3">
                      <Badge variant={getStatusBadgeVariant(client.status)}>
                        {client.status?.toUpperCase()}
                      </Badge>
                    </td>
                    <td className="p-3">
                      <div className="text-white text-sm">{client.activity.total_transactions} transactions</div>
                      <div className="text-slate-400 text-xs">{formatDate(client.activity.last_activity)}</div>
                    </td>
                    <td className="p-3">
                      <div className="space-y-1">
                        <div className="text-green-400 text-xs">✓ {client.compliance.kyc_status}</div>
                        <div className="text-green-400 text-xs">✓ {client.compliance.aml_status}</div>
                        <div className={`text-xs ${getRiskLevelColor(client.compliance.risk_level)}`}>
                          {client.compliance.risk_level} Risk
                        </div>
                      </div>
                    </td>
                    <td className="p-3">
                      <div className="flex gap-2">
                        <Button 
                          variant="ghost" 
                          size="sm"
                          className="text-slate-400 hover:text-white"
                        >
                          <Eye size={16} />
                        </Button>
                        <Select onValueChange={(value) => handleStatusUpdate(client.id, value)}>
                          <SelectTrigger className="w-24 h-8 bg-slate-800 border-slate-600">
                            <MoreHorizontal size={16} />
                          </SelectTrigger>
                          <SelectContent className="bg-slate-800 border-slate-600">
                            <SelectItem value="active" className="text-white">Set Active</SelectItem>
                            <SelectItem value="inactive" className="text-white">Set Inactive</SelectItem>
                            <SelectItem value="suspended" className="text-white">Suspend</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
            
            {filteredClients.length === 0 && (
              <div className="text-center py-12 text-slate-400">
                <Users size={48} className="mx-auto mb-4 opacity-50" />
                <p>No clients found matching your criteria</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ClientManagement;