import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Badge } from "./ui/badge";
import { Alert, AlertDescription } from "./ui/alert";
import { 
  DollarSign, 
  Calendar, 
  Clock, 
  CheckCircle, 
  AlertCircle, 
  ArrowDownCircle,
  TrendingUp,
  FileText,
  Send
} from "lucide-react";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const RedemptionManagement = ({ user }) => {
  const [availableRedemptions, setAvailableRedemptions] = useState([]);
  const [redemptionRequests, setRedemptionRequests] = useState([]);
  const [activityLogs, setActivityLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [showRedemptionModal, setShowRedemptionModal] = useState(false);
  const [selectedInvestment, setSelectedInvestment] = useState(null);
  const [redemptionForm, setRedemptionForm] = useState({
    amount: "",
    reason: ""
  });

  useEffect(() => {
    fetchRedemptionData();
  }, [user.id]);

  const fetchRedemptionData = async () => {
    try {
      setLoading(true);
      
      // Fetch available redemptions
      const redemptionsResponse = await axios.get(`${API}/redemptions/client/${user.id}`);
      if (redemptionsResponse.data.success) {
        setAvailableRedemptions(redemptionsResponse.data.available_redemptions || []);
        setRedemptionRequests(redemptionsResponse.data.redemption_requests || []);
      }
      
      // Fetch activity logs
      const logsResponse = await axios.get(`${API}/activity-logs/client/${user.id}`);
      if (logsResponse.data.success) {
        setActivityLogs(logsResponse.data.activity_logs || []);
      }
      
    } catch (err) {
      setError("Failed to load redemption data");
      console.error('Redemption data fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRedemptionRequest = async () => {
    try {
      if (!redemptionForm.amount || !selectedInvestment) {
        setError("Please enter a valid amount");
        return;
      }

      const amount = parseFloat(redemptionForm.amount);
      if (isNaN(amount) || amount <= 0) {
        setError("Please enter a valid amount");
        return;
      }

      if (amount > selectedInvestment.current_value) {
        setError(`Amount cannot exceed current value of $${selectedInvestment.current_value.toLocaleString()}`);
        return;
      }

      const requestData = {
        investment_id: selectedInvestment.investment_id,
        requested_amount: amount,
        reason: redemptionForm.reason || ""
      };

      const response = await axios.post(`${API}/redemptions/request`, requestData);

      if (response.data.success) {
        setSuccess("Redemption request submitted successfully!");
        setShowRedemptionModal(false);
        setRedemptionForm({ amount: "", reason: "" });
        setSelectedInvestment(null);
        fetchRedemptionData(); // Refresh data
      }

    } catch (err) {
      setError(err.response?.data?.detail || "Failed to submit redemption request");
    }
  };

  const openRedemptionModal = (investment) => {
    setSelectedInvestment(investment);
    setRedemptionForm({ amount: investment.current_value.toString(), reason: "" });
    setShowRedemptionModal(true);
    setError("");
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      pending: { color: "bg-yellow-500", text: "Pending Review" },
      approved: { color: "bg-green-500", text: "Approved" },
      rejected: { color: "bg-red-500", text: "Rejected" },
      completed: { color: "bg-blue-500", text: "Completed" }
    };

    const config = statusConfig[status] || statusConfig.pending;
    return <Badge className={`${config.color} text-white`}>{config.text}</Badge>;
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
      month: 'long',
      day: 'numeric'
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-white text-xl">Loading redemption data...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white flex items-center">
          <ArrowDownCircle className="mr-3 h-8 w-8 text-cyan-400" />
          Redemption Management
        </h2>
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
              <AlertCircle className="h-4 w-4" />
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

      {/* Available Redemptions */}
      <Card className="dashboard-card">
        <CardHeader>
          <CardTitle className="text-white flex items-center">
            <DollarSign className="mr-2 h-6 w-6 text-green-400" />
            Available Redemptions
          </CardTitle>
        </CardHeader>
        <CardContent>
          {availableRedemptions.length === 0 ? (
            <div className="text-center py-8 text-slate-400">
              <ArrowDownCircle className="mx-auto h-12 w-12 mb-4 opacity-50" />
              <p>No investments available for redemption</p>
            </div>
          ) : (
            <div className="space-y-4">
              {availableRedemptions.map((investment, index) => (
                <motion.div
                  key={investment.investment_id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="bg-slate-800/50 rounded-lg p-4 border border-slate-700"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center mb-2">
                        <h4 className="text-lg font-medium text-white mr-3">
                          {investment.fund_name}
                        </h4>
                        <Badge className="bg-blue-500 text-white text-xs">
                          {investment.redemption_frequency}
                        </Badge>
                      </div>
                      
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="text-slate-400">Principal:</span>
                          <span className="text-white ml-2 font-medium">
                            {formatCurrency(investment.principal_amount)}
                          </span>
                        </div>
                        <div>
                          <span className="text-slate-400">Current Value:</span>
                          <span className="text-green-400 ml-2 font-medium">
                            {formatCurrency(investment.current_value)}
                          </span>
                        </div>
                        <div>
                          <span className="text-slate-400">Deposited:</span>
                          <span className="text-white ml-2">
                            {formatDate(investment.deposit_date)}
                          </span>
                        </div>
                        <div>
                          <span className="text-slate-400">Next Available:</span>
                          <span className="text-yellow-400 ml-2">
                            {formatDate(investment.next_redemption_date)}
                          </span>
                        </div>
                      </div>
                      
                      <div className="mt-2">
                        <div className="flex items-center">
                          {investment.can_redeem ? (
                            <CheckCircle className="h-4 w-4 text-green-400 mr-2" />
                          ) : (
                            <Clock className="h-4 w-4 text-yellow-400 mr-2" />
                          )}
                          <span className={`text-sm ${investment.can_redeem ? 'text-green-400' : 'text-yellow-400'}`}>
                            {investment.message}
                          </span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="ml-4">
                      <Button
                        onClick={() => openRedemptionModal(investment)}
                        disabled={!investment.can_redeem}
                        className={`${
                          investment.can_redeem 
                            ? 'bg-red-600 hover:bg-red-700' 
                            : 'bg-slate-600 cursor-not-allowed'
                        } text-white`}
                      >
                        <ArrowDownCircle className="mr-2 h-4 w-4" />
                        Request Redemption
                      </Button>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Redemption Requests Status */}
      <Card className="dashboard-card">
        <CardHeader>
          <CardTitle className="text-white flex items-center">
            <FileText className="mr-2 h-6 w-6 text-blue-400" />
            My Redemption Requests
          </CardTitle>
        </CardHeader>
        <CardContent>
          {redemptionRequests.length === 0 ? (
            <div className="text-center py-8 text-slate-400">
              <FileText className="mx-auto h-12 w-12 mb-4 opacity-50" />
              <p>No redemption requests submitted</p>
            </div>
          ) : (
            <div className="space-y-4">
              {redemptionRequests.map((request, index) => (
                <motion.div
                  key={request.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="bg-slate-800/50 rounded-lg p-4 border border-slate-700"
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center">
                      <h4 className="text-lg font-medium text-white mr-3">
                        {request.fund_name}
                      </h4>
                      {getStatusBadge(request.status)}
                    </div>
                    <div className="text-right">
                      <div className="text-lg font-bold text-white">
                        {formatCurrency(request.requested_amount)}
                      </div>
                      <div className="text-sm text-slate-400">
                        {formatDate(request.request_date)}
                      </div>
                    </div>
                  </div>
                  
                  {request.reason && (
                    <div className="text-sm text-slate-300 mb-2">
                      <span className="text-slate-400">Reason:</span> {request.reason}
                    </div>
                  )}
                  
                  {request.admin_notes && (
                    <div className="text-sm text-slate-300">
                      <span className="text-slate-400">Admin Notes:</span> {request.admin_notes}
                    </div>
                  )}
                </motion.div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Activity Logs */}
      <Card className="dashboard-card">
        <CardHeader>
          <CardTitle className="text-white flex items-center">
            <TrendingUp className="mr-2 h-6 w-6 text-purple-400" />
            Transaction History
          </CardTitle>
        </CardHeader>
        <CardContent>
          {activityLogs.length === 0 ? (
            <div className="text-center py-8 text-slate-400">
              <TrendingUp className="mx-auto h-12 w-12 mb-4 opacity-50" />
              <p>No transaction history available</p>
            </div>
          ) : (
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {activityLogs.slice(0, 10).map((log, index) => (
                <motion.div
                  key={log.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="flex items-center justify-between p-3 bg-slate-800/30 rounded-lg"
                >
                  <div className="flex items-center">
                    <div className={`w-2 h-2 rounded-full mr-3 ${
                      log.activity_type === 'deposit' ? 'bg-green-400' :
                      log.activity_type === 'redemption_request' ? 'bg-yellow-400' :
                      log.activity_type === 'redemption_approved' ? 'bg-blue-400' :
                      log.activity_type === 'redemption_rejected' ? 'bg-red-400' :
                      'bg-gray-400'
                    }`} />
                    <div>
                      <div className="text-white text-sm font-medium">
                        {log.description}
                      </div>
                      <div className="text-slate-400 text-xs">
                        {formatDate(log.timestamp)}
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className={`font-medium ${
                      log.activity_type === 'deposit' ? 'text-green-400' : 'text-red-400'
                    }`}>
                      {log.activity_type === 'deposit' ? '+' : '-'}{formatCurrency(log.amount)}
                    </div>
                    {log.fund_code && (
                      <div className="text-xs text-slate-400">{log.fund_code}</div>
                    )}
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Redemption Request Modal */}
      <AnimatePresence>
        {showRedemptionModal && selectedInvestment && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
            onClick={() => setShowRedemptionModal(false)}
          >
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.8, opacity: 0 }}
              className="bg-slate-800 rounded-lg p-6 max-w-md w-full mx-4"
              onClick={(e) => e.stopPropagation()}
            >
              <h3 className="text-xl font-semibold text-white mb-4 flex items-center">
                <ArrowDownCircle className="mr-2 h-6 w-6 text-red-400" />
                Request Redemption
              </h3>
              
              <div className="space-y-4">
                <div className="bg-slate-700/50 rounded-lg p-3">
                  <div className="text-sm text-slate-300">
                    <div className="flex justify-between mb-1">
                      <span>Investment:</span>
                      <span className="font-medium">{selectedInvestment.fund_name}</span>
                    </div>
                    <div className="flex justify-between mb-1">
                      <span>Current Value:</span>
                      <span className="font-medium text-green-400">
                        {formatCurrency(selectedInvestment.current_value)}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>Available:</span>
                      <span className="font-medium text-yellow-400">
                        {formatDate(selectedInvestment.next_redemption_date)}
                      </span>
                    </div>
                  </div>
                </div>

                <div>
                  <Label className="text-slate-300">Redemption Amount</Label>
                  <Input
                    type="number"
                    value={redemptionForm.amount}
                    onChange={(e) => setRedemptionForm({...redemptionForm, amount: e.target.value})}
                    placeholder="Enter amount to redeem"
                    className="mt-1 bg-slate-700 border-slate-600 text-white"
                    max={selectedInvestment.current_value}
                  />
                </div>

                <div>
                  <Label className="text-slate-300">Reason (Optional)</Label>
                  <textarea
                    value={redemptionForm.reason}
                    onChange={(e) => setRedemptionForm({...redemptionForm, reason: e.target.value})}
                    placeholder="Reason for redemption..."
                    className="mt-1 w-full min-h-20 px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-white resize-none"
                  />
                </div>

                <div className="bg-yellow-900/20 border border-yellow-600 rounded-lg p-3">
                  <div className="flex items-start">
                    <AlertCircle className="h-5 w-5 text-yellow-400 mr-2 mt-0.5" />
                    <div className="text-sm text-yellow-300">
                      <p className="font-medium mb-1">Important:</p>
                      <p>Redemption requests require admin approval. Processing may take 1-3 business days.</p>
                    </div>
                  </div>
                </div>
              </div>

              <div className="flex gap-3 mt-6">
                <Button
                  variant="outline"
                  onClick={() => setShowRedemptionModal(false)}
                  className="flex-1 border-slate-600 text-slate-300"
                >
                  Cancel
                </Button>
                <Button
                  onClick={handleRedemptionRequest}
                  className="flex-1 bg-red-600 hover:bg-red-700 text-white"
                >
                  <Send className="mr-2 h-4 w-4" />
                  Submit Request
                </Button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default RedemptionManagement;