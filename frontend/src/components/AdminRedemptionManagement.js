import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Badge } from "./ui/badge";
import { Alert, AlertDescription } from "./ui/alert";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { 
  CheckCircle, 
  XCircle, 
  Clock, 
  DollarSign, 
  User, 
  Calendar,
  FileCheck,
  AlertTriangle,
  TrendingDown,
  Activity,
  Search
} from "lucide-react";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AdminRedemptionManagement = () => {
  const [pendingRedemptions, setPendingRedemptions] = useState([]);
  const [allActivityLogs, setAllActivityLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [showApprovalModal, setShowApprovalModal] = useState(false);
  const [selectedRedemption, setSelectedRedemption] = useState(null);
  const [approvalForm, setApprovalForm] = useState({
    action: "",
    admin_notes: "",
    // Payment confirmation fields for approvals
    payment_method: "fiat",
    wire_confirmation_number: "",
    bank_reference: "",
    transaction_hash: "",
    blockchain_network: "",
    wallet_address: "",
    payment_notes: ""
  });
  const [searchTerm, setSearchTerm] = useState("");
  const [filterType, setFilterType] = useState("all");

  useEffect(() => {
    fetchRedemptionData();
  }, []);

  const fetchRedemptionData = async () => {
    try {
      setLoading(true);
      
      // Fetch pending redemptions
      const pendingResponse = await axios.get(`${API}/redemptions/admin/pending`);
      if (pendingResponse.data.success) {
        setPendingRedemptions(pendingResponse.data.pending_redemptions || []);
      }
      
      // Fetch all activity logs
      const logsResponse = await axios.get(`${API}/activity-logs/admin/all`);
      if (logsResponse.data.success) {
        setAllActivityLogs(logsResponse.data.activity_logs || []);
      }
      
    } catch (err) {
      setError("Failed to load redemption data");
      console.error('Admin redemption data fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleApprovalAction = async () => {
    try {
      if (!approvalForm.action || !selectedRedemption) {
        setError("Please select an action");
        return;
      }

      const approvalData = {
        redemption_id: selectedRedemption.id,
        action: approvalForm.action,
        admin_notes: approvalForm.admin_notes,
        admin_id: "admin_001" // In real app, get from auth context
      };

      const response = await axios.post(`${API}/redemptions/admin/approve`, approvalData);

      if (response.data.success) {
        setSuccess(`Redemption ${approvalForm.action === 'approve' ? 'approved' : 'rejected'} successfully!`);
        setShowApprovalModal(false);
        setApprovalForm({ action: "", admin_notes: "" });
        setSelectedRedemption(null);
        fetchRedemptionData(); // Refresh data
        
        // Clear success message after 5 seconds
        setTimeout(() => setSuccess(""), 5000);
      }

    } catch (err) {
      setError(err.response?.data?.detail || "Failed to process redemption approval");
    }
  };

  const openApprovalModal = (redemption, action) => {
    setSelectedRedemption(redemption);
    setApprovalForm({ action, admin_notes: "" });
    setShowApprovalModal(true);
    setError("");
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
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getActivityTypeIcon = (type) => {
    switch (type) {
      case 'deposit':
        return <TrendingDown className="h-4 w-4 text-green-400 rotate-180" />;
      case 'redemption_request':
        return <Clock className="h-4 w-4 text-yellow-400" />;
      case 'redemption_approved':
        return <CheckCircle className="h-4 w-4 text-green-400" />;
      case 'redemption_rejected':
        return <XCircle className="h-4 w-4 text-red-400" />;
      default:
        return <Activity className="h-4 w-4 text-blue-400" />;
    }
  };

  const getActivityTypeColor = (type) => {
    switch (type) {
      case 'deposit':
        return 'text-green-400';
      case 'redemption_request':
        return 'text-yellow-400';
      case 'redemption_approved':
        return 'text-green-400';
      case 'redemption_rejected':
        return 'text-red-400';
      default:
        return 'text-blue-400';
    }
  };

  const filteredActivityLogs = allActivityLogs.filter(log => {
    const matchesSearch = !searchTerm || 
      log.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.client_info.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (log.fund_code && log.fund_code.toLowerCase().includes(searchTerm.toLowerCase()));
    
    const matchesFilter = filterType === 'all' || log.activity_type === filterType;
    
    return matchesSearch && matchesFilter;
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-white text-xl">Loading redemption management...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white flex items-center">
          <FileCheck className="mr-3 h-8 w-8 text-purple-400" />
          Redemption Management
        </h2>
        <div className="flex items-center space-x-4">
          <Badge className="bg-yellow-500 text-white text-sm px-3 py-1">
            {pendingRedemptions.length} Pending Requests
          </Badge>
        </div>
      </div>

      {/* Error/Success Messages */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <Alert className="bg-red-900/20 border-red-600">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription className="text-red-400">{error}</AlertDescription>
            </Alert>
          </motion.div>
        )}

        {success && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <Alert className="bg-green-900/20 border-green-600">
              <CheckCircle className="h-4 w-4" />
              <AlertDescription className="text-green-400">{success}</AlertDescription>
            </Alert>
          </motion.div>
        )}
      </AnimatePresence>

      <Tabs defaultValue="pending" className="w-full">
        <TabsList className="grid w-full grid-cols-2 bg-slate-800">
          <TabsTrigger value="pending" className="text-white">
            Pending Requests ({pendingRedemptions.length})
          </TabsTrigger>
          <TabsTrigger value="activity" className="text-white">
            Activity Logs ({allActivityLogs.length})
          </TabsTrigger>
        </TabsList>

        {/* Pending Redemptions Tab */}
        <TabsContent value="pending">
          <Card className="dashboard-card">
            <CardHeader>
              <CardTitle className="text-white flex items-center">
                <Clock className="mr-2 h-6 w-6 text-yellow-400" />
                Pending Redemption Requests
              </CardTitle>
            </CardHeader>
            <CardContent>
              {pendingRedemptions.length === 0 ? (
                <div className="text-center py-12 text-slate-400">
                  <CheckCircle className="mx-auto h-16 w-16 mb-4 opacity-50" />
                  <h3 className="text-xl font-medium mb-2">No Pending Requests</h3>
                  <p>All redemption requests have been processed.</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {(pendingRedemptions || []).map((redemption, index) => (
                    <motion.div
                      key={redemption.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="bg-slate-800/50 rounded-lg p-6 border border-slate-700"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center mb-3">
                            <User className="h-5 w-5 text-blue-400 mr-2" />
                            <h4 className="text-lg font-medium text-white">
                              {redemption.client_info.name}
                            </h4>
                            <Badge className="ml-3 bg-yellow-500 text-white">
                              {redemption.status.toUpperCase()}
                            </Badge>
                          </div>
                          
                          <div className="grid grid-cols-2 gap-4 mb-4">
                            <div>
                              <span className="text-slate-400 text-sm">Fund:</span>
                              <div className="text-white font-medium">{redemption.fund_name}</div>
                            </div>
                            <div>
                              <span className="text-slate-400 text-sm">Amount Requested:</span>
                              <div className="text-red-400 font-bold text-lg">
                                {formatCurrency(redemption.requested_amount)}
                              </div>
                            </div>
                            <div>
                              <span className="text-slate-400 text-sm">Current Value:</span>
                              <div className="text-green-400 font-medium">
                                {formatCurrency(redemption.current_value)}
                              </div>
                            </div>
                            <div>
                              <span className="text-slate-400 text-sm">Request Date:</span>
                              <div className="text-white">{formatDate(redemption.request_date)}</div>
                            </div>
                          </div>

                          {redemption.reason && (
                            <div className="mb-4">
                              <span className="text-slate-400 text-sm">Client Reason:</span>
                              <div className="text-slate-300 bg-slate-700/50 rounded p-2 mt-1">
                                {redemption.reason}
                              </div>
                            </div>
                          )}

                          <div className="text-sm text-slate-400">
                            <span>Email:</span> {redemption.client_info.email}
                          </div>
                        </div>
                        
                        <div className="flex flex-col space-y-2 ml-6">
                          <Button
                            onClick={() => openApprovalModal(redemption, 'approve')}
                            className="bg-green-600 hover:bg-green-700 text-white"
                          >
                            <CheckCircle className="mr-2 h-4 w-4" />
                            Approve
                          </Button>
                          <Button
                            onClick={() => openApprovalModal(redemption, 'reject')}
                            variant="outline"
                            className="border-red-600 text-red-400 hover:bg-red-600 hover:text-white"
                          >
                            <XCircle className="mr-2 h-4 w-4" />
                            Reject
                          </Button>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Activity Logs Tab */}
        <TabsContent value="activity">
          <Card className="dashboard-card">
            <CardHeader>
              <CardTitle className="text-white flex items-center justify-between">
                <div className="flex items-center">
                  <Activity className="mr-2 h-6 w-6 text-purple-400" />
                  All Activity Logs
                </div>
                <div className="flex items-center space-x-4">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
                    <Input
                      placeholder="Search activities..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-10 bg-slate-700 border-slate-600 text-white w-64"
                    />
                  </div>
                  <select
                    value={filterType}
                    onChange={(e) => setFilterType(e.target.value)}
                    className="bg-slate-700 border border-slate-600 text-white rounded px-3 py-2"
                  >
                    <option value="all">All Activities</option>
                    <option value="deposit">Deposits</option>
                    <option value="redemption_request">Redemption Requests</option>
                    <option value="redemption_approved">Approved</option>
                    <option value="redemption_rejected">Rejected</option>
                  </select>
                </div>
              </CardTitle>
            </CardHeader>
            <CardContent>
              {filteredActivityLogs.length === 0 ? (
                <div className="text-center py-12 text-slate-400">
                  <Activity className="mx-auto h-16 w-16 mb-4 opacity-50" />
                  <h3 className="text-xl font-medium mb-2">No Activity Found</h3>
                  <p>No activities match your current filters.</p>
                </div>
              ) : (
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {(filteredActivityLogs || []).slice(0, 50).map((log, index) => (
                    <motion.div
                      key={log.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.02 }}
                      className="flex items-center justify-between p-4 bg-slate-800/30 rounded-lg hover:bg-slate-800/50 transition-colors"
                    >
                      <div className="flex items-center">
                        {getActivityTypeIcon(log.activity_type)}
                        <div className="ml-3">
                          <div className="flex items-center space-x-2">
                            <span className="text-white font-medium">
                              {log.client_info.name}
                            </span>
                            <span className="text-slate-400">•</span>
                            <span className={`text-sm ${getActivityTypeColor(log.activity_type)}`}>
                              {log.description}
                            </span>
                          </div>
                          <div className="flex items-center space-x-4 text-xs text-slate-400 mt-1">
                            <span>{formatDate(log.timestamp)}</span>
                            {log.fund_code && (
                              <>
                                <span>•</span>
                                <span>{log.fund_code} Fund</span>
                              </>
                            )}
                            {log.reference_id && (
                              <>
                                <span>•</span>
                                <span>Ref: {log.reference_id.slice(0, 8)}...</span>
                              </>
                            )}
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className={`font-bold ${
                          log.activity_type === 'deposit' ? 'text-green-400' : 'text-red-400'
                        }`}>
                          {log.activity_type === 'deposit' ? '+' : '-'}{formatCurrency(log.amount)}
                        </div>
                        <div className="text-xs text-slate-400">
                          {log.client_info.email}
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Approval Modal */}
      <AnimatePresence>
        {showApprovalModal && selectedRedemption && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
            onClick={() => setShowApprovalModal(false)}
          >
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.8, opacity: 0 }}
              className="bg-slate-800 rounded-lg p-6 max-w-md w-full mx-4"
              onClick={(e) => e.stopPropagation()}
            >
              <h3 className="text-xl font-semibold text-white mb-4 flex items-center">
                {approvalForm.action === 'approve' ? (
                  <CheckCircle className="mr-2 h-6 w-6 text-green-400" />
                ) : (
                  <XCircle className="mr-2 h-6 w-6 text-red-400" />
                )}
                {approvalForm.action === 'approve' ? 'Approve' : 'Reject'} Redemption
              </h3>
              
              <div className="space-y-4">
                <div className="bg-slate-700/50 rounded-lg p-3">
                  <div className="text-sm text-slate-300">
                    <div className="flex justify-between mb-1">
                      <span>Client:</span>
                      <span className="font-medium">{selectedRedemption.client_info.name}</span>
                    </div>
                    <div className="flex justify-between mb-1">
                      <span>Fund:</span>
                      <span className="font-medium">{selectedRedemption.fund_name}</span>
                    </div>
                    <div className="flex justify-between mb-1">
                      <span>Amount:</span>
                      <span className="font-medium text-red-400">
                        {formatCurrency(selectedRedemption.requested_amount)}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>Current Value:</span>
                      <span className="font-medium text-green-400">
                        {formatCurrency(selectedRedemption.current_value)}
                      </span>
                    </div>
                  </div>
                </div>

                <div>
                  <Label className="text-slate-300">Admin Notes</Label>
                  <textarea
                    value={approvalForm.admin_notes}
                    onChange={(e) => setApprovalForm({...approvalForm, admin_notes: e.target.value})}
                    placeholder={`Add notes for this ${approvalForm.action}...`}
                    className="mt-1 w-full min-h-20 px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-white resize-none"
                  />
                </div>

                {approvalForm.action === 'approve' && (
                  <div className="bg-green-900/20 border border-green-600 rounded-lg p-3">
                    <div className="flex items-start">
                      <CheckCircle className="h-5 w-5 text-green-400 mr-2 mt-0.5" />
                      <div className="text-sm text-green-300">
                        <p className="font-medium mb-1">Approval Confirmation:</p>
                        <p>This redemption will be approved and marked for processing.</p>
                      </div>
                    </div>
                  </div>
                )}

                {approvalForm.action === 'reject' && (
                  <div className="bg-red-900/20 border border-red-600 rounded-lg p-3">
                    <div className="flex items-start">
                      <XCircle className="h-5 w-5 text-red-400 mr-2 mt-0.5" />
                      <div className="text-sm text-red-300">
                        <p className="font-medium mb-1">Rejection Notice:</p>
                        <p>This redemption will be rejected and the client will be notified.</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              <div className="flex gap-3 mt-6">
                <Button
                  variant="outline"
                  onClick={() => setShowApprovalModal(false)}
                  className="flex-1 border-slate-600 text-slate-300"
                >
                  Cancel
                </Button>
                <Button
                  onClick={handleApprovalAction}
                  className={`flex-1 ${
                    approvalForm.action === 'approve' 
                      ? 'bg-green-600 hover:bg-green-700' 
                      : 'bg-red-600 hover:bg-red-700'
                  } text-white`}
                >
                  {approvalForm.action === 'approve' ? (
                    <CheckCircle className="mr-2 h-4 w-4" />
                  ) : (
                    <XCircle className="mr-2 h-4 w-4" />
                  )}
                  Confirm {approvalForm.action === 'approve' ? 'Approval' : 'Rejection'}
                </Button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default AdminRedemptionManagement;