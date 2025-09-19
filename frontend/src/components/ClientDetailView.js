import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { Alert, AlertDescription } from "./ui/alert";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { 
  X,
  User,
  FileText,
  Shield,
  DollarSign,
  Clock,
  Mail,
  Phone,
  Calendar,
  MapPin,
  Download,
  Eye,
  CheckCircle,
  AlertTriangle,
  XCircle,
  Activity,
  CreditCard,
  Briefcase,
  History,
  MessageSquare,
  Upload,
  ExternalLink
} from "lucide-react";
import apiAxios from "../utils/apiAxios";

// Document types for client uploads
const CLIENT_DOCUMENT_TYPES = {
  identity: "Government ID",
  proof_of_address: "Proof of Address", 
  proof_of_income: "Proof of Income",
  bank_statement: "Bank Statement",
  investment_agreement: "Investment Agreement",
  risk_assessment: "Risk Assessment",
  compliance_form: "Compliance Form",
  tax_document: "Tax Document",
  other: "Other Document"
};

const ClientDetailView = ({ client, onClose, onUpdate }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [clientDetails, setClientDetails] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [investments, setInvestments] = useState([]);
  const [activityLog, setActivityLog] = useState([]);
  const [amlKycData, setAmlKycData] = useState(null);
  
  // Document upload state
  const [uploadingDocument, setUploadingDocument] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [documentToUpload, setDocumentToUpload] = useState({
    type: "",
    file: null,
    notes: ""
  });

  useEffect(() => {
    if (client) {
      fetchClientDetails();
    }
  }, [client]);

  const fetchClientDetails = async () => {
    try {
      setLoading(true);
      
      // Fetch comprehensive client data
      const [
        detailsResponse,
        documentsResponse,  
        investmentsResponse,
        activityResponse
      ] = await Promise.allSettled([
        apiAxios.get(`/admin/clients/${client.id}/details`),
        apiAxios.get(`/admin/clients/${client.id}/documents`),
        apiAxios.get(`/investments/client/${client.id}`),
        apiAxios.get(`/admin/clients/${client.id}/activity`)
      ]);

      // Handle client details
      if (detailsResponse.status === 'fulfilled') {
        setClientDetails(detailsResponse.value.data);
      } else {
        setClientDetails(client); // Fallback to basic client data
      }

      // Handle documents
      if (documentsResponse.status === 'fulfilled') {
        setDocuments(documentsResponse.value.data.documents || []);
      }

      // Handle investments
      if (investmentsResponse.status === 'fulfilled') {
        setInvestments(investmentsResponse.value.data.investments || []);
      }

      // Handle activity log
      if (activityResponse.status === 'fulfilled') {
        setActivityLog(activityResponse.value.data.activities || []);
      } else {
        // Generate mock activity log based on available data
        generateMockActivityLog();
      }

      // Check for AML/KYC data
      if (client.aml_kyc_result_id) {
        try {
          const amlResponse = await apiAxios.get(`/admin/aml-kyc/${client.aml_kyc_result_id}`);
          setAmlKycData(amlResponse.data);
        } catch (amlError) {
          console.log('AML/KYC data not available');
        }
      }

    } catch (err) {
      setError("Failed to load client details");
      console.error('Client details error:', err);
    } finally {
      setLoading(false);
    }
  };

  const generateMockActivityLog = () => {
    const activities = [
      {
        id: 1,
        type: "registration",
        title: "Account Created",
        description: `Client account created${client.created_from_prospect ? ' from prospect conversion' : ''}`,
        timestamp: client.createdAt || new Date().toISOString(),
        icon: "user-plus",
        status: "completed"
      }
    ];

    if (client.created_from_prospect) {
      activities.unshift({
        id: 0,
        type: "prospect",
        title: "Lead Registration", 
        description: "Initial prospect registration and document submission",
        timestamp: client.createdAt || new Date().toISOString(),
        icon: "file-text",
        status: "completed"
      });
    }

    if (client.aml_kyc_status) {
      activities.push({
        id: 2,
        type: "compliance",
        title: "AML/KYC Check",
        description: `Compliance screening completed with status: ${client.aml_kyc_status.toUpperCase()}`,
        timestamp: client.createdAt || new Date().toISOString(),
        icon: "shield",
        status: client.aml_kyc_status === 'clear' ? 'completed' : 'pending'
      });
    }

    if (investments.length > 0) {
      investments.forEach((investment, index) => {
        activities.push({
          id: 10 + index,
          type: "investment",
          title: `${investment.fund_code} Investment`,
          description: `Investment of $${investment.principal_amount?.toLocaleString()} in ${investment.fund_code} fund`,
          timestamp: investment.deposit_date || investment.created_at,
          icon: "dollar-sign",
          status: "completed"
        });
      });
    }

    setActivityLog(activities.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp)));
  };

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'active': return 'bg-green-100 text-green-800 border-green-200';
      case 'inactive': return 'bg-gray-100 text-gray-800 border-gray-200';
      case 'suspended': return 'bg-red-100 text-red-800 border-red-200';
      case 'pending': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getDocumentStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'approved': return 'text-green-600';
      case 'pending': return 'text-yellow-600';
      case 'rejected': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getActivityIcon = (type) => {
    switch (type) {
      case 'registration': return <User className="h-4 w-4" />;
      case 'prospect': return <FileText className="h-4 w-4" />;
      case 'compliance': return <Shield className="h-4 w-4" />;
      case 'investment': return <DollarSign className="h-4 w-4" />;
      case 'document': return <FileText className="h-4 w-4" />;
      case 'communication': return <MessageSquare className="h-4 w-4" />;
      default: return <Activity className="h-4 w-4" />;
    }
  };

  const downloadDocument = async (documentId, fileName) => {
    try {
      const response = await apiAxios.get(`/admin/documents/${documentId}/download`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', fileName);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      setError("Failed to download document");
    }
  };

  const handleDocumentUpload = async () => {
    try {
      if (!documentToUpload.type || !documentToUpload.file) {
        setError("Please select document type and file");
        return;
      }
      
      setUploadingDocument(true);
      setError("");
      
      const formData = new FormData();
      formData.append('file', documentToUpload.file);
      formData.append('document_type', documentToUpload.type);
      formData.append('notes', documentToUpload.notes);
      
      const response = await apiAxios.post(
        `/admin/clients/${client.id}/documents`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      
      if (response.data.success) {
        setDocuments([...documents, response.data.document]);
        setDocumentToUpload({ type: "", file: null, notes: "" });
        setShowUploadModal(false);
        // Refresh documents
        const documentsResponse = await apiAxios.get(`/admin/clients/${client.id}/documents`);
        if (documentsResponse.data.documents) {
          setDocuments(documentsResponse.data.documents);
        }
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to upload document");
    } finally {
      setUploadingDocument(false);
    }
  };

  if (!client) return null;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.95, opacity: 0 }}
        className="bg-white rounded-lg shadow-xl max-w-6xl w-full max-h-[90vh] overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 bg-gradient-to-r from-blue-600 to-purple-600">
          <div className="flex items-center space-x-4">
            <div className="bg-white p-2 rounded-full">
              <User className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">
                {clientDetails?.name || client.name}
              </h2>
              <p className="text-blue-100">
                Client ID: {client.id} • {client.email}
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Badge className={getStatusColor(client.status)}>
              {client.status?.toUpperCase() || 'ACTIVE'}
            </Badge>
            <Button
              variant="ghost"
              onClick={onClose}
              className="p-2 text-white hover:bg-white hover:bg-opacity-20 rounded-full"
            >
              <X size={20} />
            </Button>
          </div>
        </div>

        {/* Content */}
        <div className="overflow-y-auto max-h-[calc(90vh-80px)]">
          {loading ? (
            <div className="flex items-center justify-center p-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <span className="ml-3 text-gray-600">Loading client details...</span>
            </div>
          ) : (
            <Tabs defaultValue="overview" className="w-full">
              <TabsList className="grid w-full grid-cols-5 bg-gray-50 m-0 rounded-none">
                <TabsTrigger value="overview" className="flex items-center space-x-2">
                  <User className="h-4 w-4" />
                  <span>Overview</span>
                </TabsTrigger>
                <TabsTrigger value="documents" className="flex items-center space-x-2">
                  <FileText className="h-4 w-4" />
                  <span>Documents</span>
                </TabsTrigger>
                <TabsTrigger value="investments" className="flex items-center space-x-2">
                  <DollarSign className="h-4 w-4" />
                  <span>Investments</span>
                </TabsTrigger>
                <TabsTrigger value="compliance" className="flex items-center space-x-2">
                  <Shield className="h-4 w-4" />
                  <span>Compliance</span>
                </TabsTrigger>
                <TabsTrigger value="activity" className="flex items-center space-x-2">
                  <History className="h-4 w-4" />
                  <span>Activity</span>
                </TabsTrigger>
              </TabsList>

              {/* Overview Tab */}
              <TabsContent value="overview" className="p-6 space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {/* Basic Information */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg flex items-center">
                        <User className="h-5 w-5 mr-2" />
                        Basic Information
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <div className="flex items-center space-x-2">
                        <Mail className="h-4 w-4 text-gray-500" />
                        <span className="text-sm">{client.email}</span>
                      </div>
                      {client.phone && (
                        <div className="flex items-center space-x-2">
                          <Phone className="h-4 w-4 text-gray-500" />
                          <span className="text-sm">{client.phone}</span>
                        </div>
                      )}
                      <div className="flex items-center space-x-2">
                        <Calendar className="h-4 w-4 text-gray-500" />
                        <span className="text-sm">
                          Created: {new Date(client.createdAt || Date.now()).toLocaleDateString()}
                        </span>
                      </div>
                      {client.created_from_prospect && (
                        <div className="flex items-center space-x-2">
                          <CheckCircle className="h-4 w-4 text-green-500" />
                          <span className="text-sm text-green-600">Converted from Prospect</span>
                        </div>
                      )}
                    </CardContent>
                  </Card>

                  {/* Investment Summary */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg flex items-center">
                        <DollarSign className="h-5 w-5 mr-2" />
                        Investment Summary
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <div className="text-2xl font-bold text-green-600">
                        ${(investments.reduce((sum, inv) => sum + (inv.principal_amount || 0), 0)).toLocaleString()}
                      </div>
                      <p className="text-sm text-gray-600">Total Invested</p>
                      <div className="text-lg font-semibold">
                        {investments.length} Active Investment{investments.length !== 1 ? 's' : ''}
                      </div>
                      {investments.length > 0 && (
                        <div className="space-y-1">
                          {investments.slice(0, 3).map((inv, index) => (
                            <div key={index} className="text-sm flex justify-between">
                              <span>{inv.fund_code}</span>
                              <span>${inv.principal_amount?.toLocaleString()}</span>
                            </div>
                          ))}
                        </div>
                      )}
                    </CardContent>
                  </Card>

                  {/* Compliance Status */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg flex items-center">
                        <Shield className="h-5 w-5 mr-2" />
                        Compliance Status
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <div className="flex items-center space-x-2">
                        {client.aml_kyc_status === 'clear' ? (
                          <CheckCircle className="h-5 w-5 text-green-500" />
                        ) : client.aml_kyc_status === 'pending' ? (
                          <AlertTriangle className="h-5 w-5 text-yellow-500" />
                        ) : (
                          <XCircle className="h-5 w-5 text-red-500" />
                        )}
                        <span className="font-medium">
                          AML/KYC: {client.aml_kyc_status?.toUpperCase() || 'PENDING'}
                        </span>
                      </div>
                      <div className="text-sm text-gray-600">
                        Documents: {documents.filter(d => d.verification_status === 'approved').length}/{documents.length} Approved
                      </div>
                      {client.aml_approval_document && (
                        <Button
                          size="sm"
                          variant="outline"
                          className="w-full"
                          onClick={() => window.open(client.aml_approval_document, '_blank')}
                        >
                          <Download className="h-4 w-4 mr-2" />
                          AML Approval Document
                        </Button>
                      )}
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>

              {/* Documents Tab */}
              <TabsContent value="documents" className="p-6">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-semibold">Client Documents</h3>
                    <div className="flex items-center gap-3">
                      <Badge variant="outline">{documents.length} Documents</Badge>
                      <Button
                        onClick={() => setShowUploadModal(true)}
                        size="sm"
                        className="bg-blue-600 hover:bg-blue-700 text-white"
                      >
                        <Upload className="h-4 w-4 mr-2" />
                        Upload Document
                      </Button>
                    </div>
                  </div>
                  
                  {documents.length === 0 ? (
                    <Card>
                      <CardContent className="p-8 text-center">
                        <FileText className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                        <h3 className="text-lg font-medium text-gray-900 mb-2">No Documents Found</h3>
                        <p className="text-gray-500">No documents have been uploaded for this client yet.</p>
                      </CardContent>
                    </Card>
                  ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {documents.map((doc, index) => (
                        <Card key={index} className="hover:shadow-md transition-shadow">
                          <CardContent className="p-4">
                            <div className="flex items-start justify-between mb-3">
                              <div className="flex items-center space-x-2">
                                <FileText className="h-5 w-5 text-blue-600" />
                                <div>
                                  <h4 className="font-medium text-sm">{doc.document_type?.replace('_', ' ').toUpperCase()}</h4>
                                  <p className="text-xs text-gray-500">{doc.file_name || 'Document'}</p>
                                </div>
                              </div>
                              <Badge 
                                variant="outline" 
                                className={getDocumentStatusColor(doc.verification_status)}
                              >
                                {doc.verification_status?.toUpperCase()}
                              </Badge>
                            </div>
                            
                            {doc.notes && (
                              <p className="text-sm text-gray-600 mb-3">{doc.notes}</p>
                            )}
                            
                            <div className="flex space-x-2">
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => downloadDocument(doc.document_id, doc.file_name)}
                                className="flex-1"
                              >
                                <Download className="h-4 w-4 mr-1" />
                                Download
                              </Button>
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => window.open(doc.file_path, '_blank')}
                              >
                                <Eye className="h-4 w-4" />
                              </Button>
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  )}
                </div>
              </TabsContent>

              {/* Investments Tab */}
              <TabsContent value="investments" className="p-6">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-semibold">Investment Portfolio</h3>
                    <Badge variant="outline">{investments.length} Investments</Badge>
                  </div>

                  {investments.length === 0 ? (
                    <Card>
                      <CardContent className="p-8 text-center">
                        <DollarSign className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                        <h3 className="text-lg font-medium text-gray-900 mb-2">No Investments</h3>
                        <p className="text-gray-500">This client has not made any investments yet.</p>
                      </CardContent>
                    </Card>
                  ) : (
                    <div className="space-y-4">
                      {investments.map((investment, index) => (
                        <Card key={index}>
                          <CardContent className="p-4">
                            <div className="flex items-center justify-between mb-4">
                              <div>
                                <h4 className="font-semibold text-lg">{investment.fund_code} Fund</h4>
                                <p className="text-sm text-gray-600">Investment ID: {investment.investment_id}</p>
                              </div>
                              <Badge 
                                className={
                                  investment.status === 'ACTIVE' ? 'bg-green-100 text-green-800' :
                                  investment.status === 'PENDING' ? 'bg-yellow-100 text-yellow-800' :
                                  'bg-gray-100 text-gray-800'
                                }
                              >
                                {investment.status}
                              </Badge>
                            </div>
                            
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                              <div>
                                <p className="text-sm text-gray-600">Principal Amount</p>
                                <p className="font-semibold">${investment.principal_amount?.toLocaleString()}</p>
                              </div>
                              <div>
                                <p className="text-sm text-gray-600">Current Value</p>
                                <p className="font-semibold">${investment.current_value?.toLocaleString()}</p>
                              </div>
                              <div>
                                <p className="text-sm text-gray-600">Deposit Date</p>
                                <p className="font-semibold">
                                  {investment.deposit_date ? new Date(investment.deposit_date).toLocaleDateString() : 'N/A'}
                                </p>
                              </div>
                              <div>
                                <p className="text-sm text-gray-600">Performance</p>
                                <p className={`font-semibold ${
                                  (investment.current_value || 0) >= (investment.principal_amount || 0) ? 'text-green-600' : 'text-red-600'
                                }`}>
                                  {investment.current_value && investment.principal_amount 
                                    ? `${((investment.current_value - investment.principal_amount) / investment.principal_amount * 100).toFixed(2)}%`
                                    : 'N/A'
                                  }
                                </p>
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  )}
                </div>
              </TabsContent>

              {/* Compliance Tab */}
              <TabsContent value="compliance" className="p-6">
                <div className="space-y-6">
                  <h3 className="text-lg font-semibold">Compliance & AML/KYC Information</h3>

                  {/* AML/KYC Status */}
                  <Card>
                    <CardHeader>
                      <CardTitle>AML/KYC Status</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="flex items-center space-x-3 mb-4">
                        {client.aml_kyc_status === 'clear' ? (
                          <>
                            <CheckCircle className="h-6 w-6 text-green-500" />
                            <div>
                              <p className="font-medium text-green-800">CLEARED</p>
                              <p className="text-sm text-gray-600">AML/KYC screening passed</p>
                            </div>
                          </>
                        ) : client.aml_kyc_status === 'pending' ? (
                          <>
                            <AlertTriangle className="h-6 w-6 text-yellow-500" />
                            <div>
                              <p className="font-medium text-yellow-800">PENDING</p>
                              <p className="text-sm text-gray-600">AML/KYC screening in progress</p>
                            </div>
                          </>
                        ) : (
                          <>
                            <XCircle className="h-6 w-6 text-red-500" />
                            <div>
                              <p className="font-medium text-red-800">REQUIRES REVIEW</p>
                              <p className="text-sm text-gray-600">Manual review required</p>
                            </div>
                          </>
                        )}
                      </div>

                      {amlKycData && (
                        <div className="bg-gray-50 p-4 rounded-lg">
                          <h4 className="font-medium mb-2">Compliance Details</h4>
                          <div className="grid grid-cols-2 gap-4 text-sm">
                            <div>
                              <p className="text-gray-600">OFAC Status</p>
                              <p className="font-medium">{amlKycData.ofac_status?.toUpperCase()}</p>
                            </div>
                            <div>
                              <p className="text-gray-600">Risk Level</p>
                              <p className="font-medium">{amlKycData.risk_level?.toUpperCase()}</p>
                            </div>
                          </div>
                        </div>
                      )}
                    </CardContent>
                  </Card>

                  {/* Document Verification Status */}
                  <Card>
                    <CardHeader>
                      <CardTitle>Document Verification</CardTitle>
                    </CardHeader>
                    <CardContent>
                      {documents.length === 0 ? (
                        <p className="text-gray-500">No documents submitted</p>
                      ) : (
                        <div className="space-y-3">
                          {documents.map((doc, index) => (
                            <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                              <div className="flex items-center space-x-3">
                                <FileText className="h-4 w-4 text-gray-600" />
                                <div>
                                  <p className="font-medium">{doc.document_type?.replace('_', ' ').toUpperCase()}</p>
                                  <p className="text-sm text-gray-600">{doc.file_name}</p>
                                </div>
                              </div>
                              <Badge 
                                className={
                                  doc.verification_status === 'approved' ? 'bg-green-100 text-green-800' :
                                  doc.verification_status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                                  'bg-red-100 text-red-800'
                                }
                              >
                                {doc.verification_status?.toUpperCase()}
                              </Badge>
                            </div>
                          ))}
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>

              {/* Activity Tab */}
              <TabsContent value="activity" className="p-6">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-semibold">Activity Timeline</h3>
                    <Badge variant="outline">{activityLog.length} Events</Badge>
                  </div>

                  <div className="space-y-4">
                    {activityLog.map((activity, index) => (
                      <div key={activity.id} className="flex items-start space-x-4">
                        <div className={`p-2 rounded-full ${
                          activity.status === 'completed' ? 'bg-green-100' : 
                          activity.status === 'pending' ? 'bg-yellow-100' : 'bg-gray-100'
                        }`}>
                          {getActivityIcon(activity.type)}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between">
                            <p className="text-sm font-medium text-gray-900">
                              {activity.title}
                            </p>
                            <p className="text-sm text-gray-500">
                              {new Date(activity.timestamp).toLocaleDateString()}
                            </p>
                          </div>
                          <p className="text-sm text-gray-600 mt-1">
                            {activity.description}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </TabsContent>
            </Tabs>
          )}
        </div>

        {error && (
          <Alert className="m-6 bg-red-50 border-red-200">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription className="text-red-800">{error}</AlertDescription>
          </Alert>
        )}
      </motion.div>

      {/* Document Upload Modal */}
      <AnimatePresence>
        {showUploadModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[60]"
            onClick={() => setShowUploadModal(false)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="p-6 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold">Upload Document</h3>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setShowUploadModal(false)}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              </div>

              <div className="p-6 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Document Type
                  </label>
                  <select
                    className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                    value={documentToUpload.type}
                    onChange={(e) => setDocumentToUpload(prev => ({ ...prev, type: e.target.value }))}
                  >
                    <option value="">Select document type</option>
                    {Object.entries(CLIENT_DOCUMENT_TYPES).map(([key, label]) => (
                      <option key={key} value={key}>{label}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    File
                  </label>
                  <input
                    type="file"
                    className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                    onChange={(e) => setDocumentToUpload(prev => ({ ...prev, file: e.target.files[0] }))}
                    accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Notes (Optional)
                  </label>
                  <textarea
                    className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                    rows={3}
                    placeholder="Add any notes about this document..."
                    value={documentToUpload.notes}
                    onChange={(e) => setDocumentToUpload(prev => ({ ...prev, notes: e.target.value }))}
                  />
                </div>
              </div>

              <div className="p-6 border-t border-gray-200 flex gap-3">
                <Button
                  variant="outline"
                  onClick={() => setShowUploadModal(false)}
                  className="flex-1"
                >
                  Cancel
                </Button>
                <Button
                  onClick={handleDocumentUpload}
                  disabled={!documentToUpload.type || !documentToUpload.file || uploadingDocument}
                  className="flex-1 bg-blue-600 hover:bg-blue-700"
                >
                  {uploadingDocument ? (
                    <>
                      <Upload className="h-4 w-4 mr-2 animate-spin" />
                      Uploading...
                    </>
                  ) : (
                    <>
                      <Upload className="h-4 w-4 mr-2" />
                      Upload Document
                    </>
                  )}
                </Button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

export default ClientDetailView;