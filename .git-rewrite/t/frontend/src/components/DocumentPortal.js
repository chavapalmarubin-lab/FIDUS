import React, { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Badge } from "./ui/badge";
import { Alert, AlertDescription } from "./ui/alert";
import { Progress } from "./ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { 
  FileText, 
  Upload, 
  Download, 
  Send, 
  Eye,
  Trash2,
  Search,
  Filter,
  Calendar,
  User,
  CheckCircle,
  Clock,
  XCircle,
  FileX,
  Signature,
  Mail,
  AlertCircle,
  Folder,
  Archive,
  Plus,
  MoreHorizontal,
  Camera
} from "lucide-react";
import { format } from "date-fns";
import axios from "axios";
import CameraCapture from "./CameraCapture";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const DOCUMENT_STATUSES = {
  'draft': { icon: Clock, color: 'text-gray-400', bg: 'bg-gray-100' },
  'sent': { icon: Mail, color: 'text-blue-400', bg: 'bg-blue-100' },
  'delivered': { icon: Eye, color: 'text-cyan-400', bg: 'bg-cyan-100' },
  'completed': { icon: CheckCircle, color: 'text-green-400', bg: 'bg-green-100' },
  'declined': { icon: XCircle, color: 'text-red-400', bg: 'bg-red-100' },
  'voided': { icon: FileX, color: 'text-gray-500', bg: 'bg-gray-100' }
};

const DOCUMENT_CATEGORIES = [
  'loan_agreements',
  'account_opening',
  'compliance_forms',
  'investment_documents',
  'insurance_forms',
  'amendments',
  'other'
];

const DocumentPortal = ({ user, userType }) => {
  const [documents, setDocuments] = useState([]);
  const [filteredDocuments, setFilteredDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [showCameraModal, setShowCameraModal] = useState(false);
  const [showSendModal, setShowSendModal] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [categoryFilter, setCategoryFilter] = useState("all");
  const [dateFilter, setDateFilter] = useState("all");
  const [sortBy, setSortBy] = useState("created_at");
  const [sortOrder, setSortOrder] = useState("desc");
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [uploadCategory, setUploadCategory] = useState('other');
  const [availableCategories, setAvailableCategories] = useState({ shared_categories: [], admin_only_categories: [] });
  const fileInputRef = useRef(null);

  useEffect(() => {
    fetchDocuments();
    fetchCategories();
  }, [user]);

  const fetchCategories = async () => {
    try {
      const response = await axios.get(`${API}/documents/categories`);
      if (response.data) {
        setAvailableCategories(response.data);
      }
    } catch (err) {
      console.error("Error fetching document categories:", err);
    }
  };

  useEffect(() => {
    applyFiltersAndSort();
  }, [documents, searchTerm, statusFilter, categoryFilter, dateFilter, sortBy, sortOrder]);

  const fetchDocuments = async () => {
    try {
      setLoading(true);
      const endpoint = userType === 'admin' ? 
        `${API}/documents/admin/all` : 
        `${API}/documents/client/${user.id}`;
      
      const response = await axios.get(endpoint);
      setDocuments(response.data.documents || []);
    } catch (err) {
      setError("Failed to fetch documents");
      console.error("Error fetching documents:", err);
    } finally {
      setLoading(false);
    }
  };

  const applyFiltersAndSort = () => {
    let filtered = [...documents];

    // Apply search filter
    if (searchTerm) {
      filtered = filtered.filter(doc => 
        doc.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        doc.sender_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        doc.recipient_emails?.some(email => 
          email.toLowerCase().includes(searchTerm.toLowerCase())
        )
      );
    }

    // Apply status filter
    if (statusFilter !== "all") {
      filtered = filtered.filter(doc => doc.status === statusFilter);
    }

    // Apply category filter
    if (categoryFilter !== "all") {
      filtered = filtered.filter(doc => doc.category === categoryFilter);
    }

    // Apply date filter
    if (dateFilter !== "all") {
      const now = new Date();
      const filterDate = new Date();
      
      switch (dateFilter) {
        case "today":
          filterDate.setHours(0, 0, 0, 0);
          break;
        case "week":
          filterDate.setDate(now.getDate() - 7);
          break;
        case "month":
          filterDate.setMonth(now.getMonth() - 1);
          break;
        case "year":
          filterDate.setFullYear(now.getFullYear() - 1);
          break;
      }
      
      if (dateFilter !== "all") {
        filtered = filtered.filter(doc => 
          new Date(doc.created_at) >= filterDate
        );
      }
    }

    // Apply sorting
    filtered.sort((a, b) => {
      let aValue, bValue;
      
      switch (sortBy) {
        case "name":
          aValue = a.name.toLowerCase();
          bValue = b.name.toLowerCase();
          break;
        case "status":
          aValue = a.status;
          bValue = b.status;
          break;
        case "created_at":
          aValue = new Date(a.created_at);
          bValue = new Date(b.created_at);
          break;
        case "updated_at":
          aValue = new Date(a.updated_at);
          bValue = new Date(b.updated_at);
          break;
        default:
          aValue = a[sortBy];
          bValue = b[sortBy];
      }

      if (aValue < bValue) return sortOrder === "asc" ? -1 : 1;
      if (aValue > bValue) return sortOrder === "asc" ? 1 : -1;
      return 0;
    });

    setFilteredDocuments(filtered);
  };

  const handleFileUpload = async (files) => {
    if (!files || files.length === 0) return;
    
    const file = files[0];
    await uploadFile(file);
  };

  const handleCameraCapture = async (file) => {
    if (!file) return;
    await uploadFile(file);
  };

  const uploadFile = async (file) => {
    setError("");
    setSuccess("");

    // Validate file type - now includes images from camera
    const allowedTypes = [
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'text/plain',
      'text/html',
      'image/jpeg',
      'image/png',
      'image/webp'
    ];
    
    if (!allowedTypes.includes(file.type)) {
      setError("Only PDF, Word, Text, HTML, and Image files are supported");
      return;
    }

    // Validate file size (10MB limit)
    if (file.size > 10 * 1024 * 1024) {
      setError("File size must be less than 10MB");
      return;
    }

    try {
      setUploadProgress(0);
      const formData = new FormData();
      formData.append('document', file);
      formData.append('category', uploadCategory);
      formData.append('uploader_id', user.id);
      formData.append('uploader_type', userType);
      if (userType === 'client') {
        formData.append('client_id', user.id);
      }

      const response = await axios.post(`${API}/documents/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        onUploadProgress: (progressEvent) => {
          const progress = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          setUploadProgress(progress);
        }
      });

      if (response.data.success) {
        const uploadMethod = file.name.includes('document-') && file.type.startsWith('image/') ? 'camera' : 'file';
        setSuccess(`Document uploaded successfully via ${uploadMethod}`);
        setShowUploadModal(false);
        setShowCameraModal(false);
        fetchDocuments();
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Upload failed");
    } finally {
      setUploadProgress(0);
    }
  };

  const handleSendForSignature = async (documentId, requestData) => {
    try {
      setLoading(true);
      
      const response = await axios.post(`${API}/documents/${documentId}/send-for-signature`, {
        recipients: requestData.recipients,
        email_subject: requestData.email_subject,
        email_message: requestData.email_message,
        sender_id: user.id
      });

      if (response.data.success) {
        setSuccess(`Document sent successfully via Gmail to ${response.data.successful_sends?.length || 0} recipients`);
        setShowSendModal(false);
        fetchDocuments();
      } else {
        setError(response.data.message || "Failed to send document");
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to send document via Gmail");
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadDocument = async (documentId, documentName) => {
    try {
      const response = await axios.get(`${API}/documents/${documentId}/download`, {
        responseType: 'blob'
      });

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.download = documentName;
      link.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError("Failed to download document");
    }
  };

  const handleDeleteDocument = async (documentId) => {
    if (!window.confirm("Are you sure you want to delete this document?")) {
      return;
    }

    try {
      await axios.delete(`${API}/documents/${documentId}`);
      setSuccess("Document deleted successfully");
      fetchDocuments();
    } catch (err) {
      setError("Failed to delete document");
    }
  };

  const getStatusIcon = (status) => {
    const statusConfig = DOCUMENT_STATUSES[status] || DOCUMENT_STATUSES['draft'];
    const IconComponent = statusConfig.icon;
    return <IconComponent className={`w-4 h-4 ${statusConfig.color}`} />;
  };

  const formatDate = (dateString) => {
    return format(new Date(dateString), 'MMM dd, yyyy HH:mm');
  };

  const renderDocumentCard = (document) => (
    <motion.div
      key={document.id}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="bg-slate-800 border border-slate-600 rounded-lg p-4 hover:border-cyan-400 transition-colors"
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <FileText className="w-8 h-8 text-cyan-400" />
          <div>
            <h3 className="text-white font-medium truncate max-w-xs">
              {document.name}
            </h3>
            <p className="text-slate-400 text-sm">
              {document.category?.replace('_', ' ').toUpperCase()}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {getStatusIcon(document.status)}
          <Badge variant="outline" className="text-xs">
            {document.status.toUpperCase()}
          </Badge>
        </div>
      </div>

      <div className="space-y-2 text-sm text-slate-400">
        <div className="flex justify-between">
          <span>Created:</span>
          <span>{formatDate(document.created_at)}</span>
        </div>
        {document.sender_name && (
          <div className="flex justify-between">
            <span>Sender:</span>
            <span className="text-white">{document.sender_name}</span>
          </div>
        )}
        {document.recipient_emails && document.recipient_emails.length > 0 && (
          <div className="flex justify-between">
            <span>Recipients:</span>
            <span className="text-white">{document.recipient_emails.length}</span>
          </div>
        )}
      </div>

      <div className="flex gap-2 mt-4">
        <Button
          size="sm"
          variant="outline"
          onClick={() => handleDownloadDocument(document.id, document.name)}
          className="flex-1 text-white border-slate-600 hover:bg-slate-700"
        >
          <Download size={14} className="mr-1" />
          Download
        </Button>
        
        {userType === 'admin' && document.status === 'draft' && (
          <Button
            size="sm"
            variant="outline"
            onClick={() => {
              setSelectedDocument(document);
              setShowSendModal(true);
            }}
            className="flex-1 text-white border-slate-600 hover:bg-slate-700"
          >
            <Send size={14} className="mr-1" />
            Send
          </Button>
        )}
        
        {userType === 'admin' && (
          <Button
            size="sm"
            variant="outline"
            onClick={() => handleDeleteDocument(document.id)}
            className="text-red-400 border-red-600 hover:bg-red-900/20"
          >
            <Trash2 size={14} />
          </Button>
        )}
      </div>
    </motion.div>
  );

  const renderUploadModal = () => (
    <AnimatePresence>
      {showUploadModal && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
          onClick={() => setShowUploadModal(false)}
        >
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.8, opacity: 0 }}
            className="bg-slate-800 rounded-lg p-6 max-w-md w-full mx-4"
            onClick={(e) => e.stopPropagation()}
          >
            <h3 className="text-xl font-semibold text-white mb-4">Upload Document</h3>
            
            {/* Category Selection */}
            <div className="mb-4">
              <Label className="text-slate-300 mb-2 block">Document Category</Label>
              <Select value={uploadCategory} onValueChange={setUploadCategory}>
                <SelectTrigger className="bg-slate-700 border-slate-600 text-white">
                  <SelectValue placeholder="Select category" />
                </SelectTrigger>
                <SelectContent className="bg-slate-700 border-slate-600">
                  {/* Shared categories - visible to both admin and client */}
                  <SelectItem value="other" className="text-white">Other</SelectItem>
                  {availableCategories.shared_categories.map((category) => (
                    <SelectItem key={category} value={category} className="text-white">
                      {category.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </SelectItem>
                  ))}
                  
                  {/* Admin-only categories - only visible to admin */}
                  {userType === 'admin' && (
                    <>
                      <SelectItem disabled className="text-slate-500 font-semibold">
                        — Internal Documents —
                      </SelectItem>
                      {availableCategories.admin_only_categories.map((category) => (
                        <SelectItem key={category} value={category} className="text-white">
                          {category.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        </SelectItem>
                      ))}
                    </>
                  )}
                </SelectContent>
              </Select>
              <div className="text-xs text-slate-400 mt-1">
                {userType === 'admin' 
                  ? "Choose category for document (internal categories visible only to admin)"
                  : "Choose category for document (shared with admin)"
                }
              </div>
            </div>
            
            {/* Upload Options */}
            <div className="space-y-4">
              {/* File Upload Option */}
              <div
                className="border-2 border-dashed border-slate-600 rounded-lg p-6 text-center hover:border-cyan-400 transition-colors cursor-pointer"
                onClick={() => fileInputRef.current?.click()}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf,.doc,.docx,.txt,.html,.jpg,.jpeg,.png"
                  onChange={(e) => handleFileUpload(e.target.files)}
                  className="hidden"
                />
                
                <Upload className="mx-auto text-slate-400 mb-3" size={40} />
                <div className="text-slate-300 font-medium">Upload from Device</div>
                <div className="text-slate-500 text-sm mt-2">
                  PDF, Word, Text, HTML, Images (max 10MB)
                </div>
              </div>

              {/* Camera Capture Option */}
              <div className="text-center">
                <div className="text-slate-400 text-sm mb-2">OR</div>
                <Button
                  onClick={() => {
                    setShowUploadModal(false);
                    setShowCameraModal(true);
                  }}
                  className="w-full bg-cyan-600 hover:bg-cyan-700"
                >
                  <Camera size={16} className="mr-2" />
                  Take Photo with Camera
                </Button>
                <div className="text-slate-500 text-xs mt-2">
                  Capture documents directly with your camera
                </div>
              </div>
            </div>

            {/* Upload Progress */}
            {uploadProgress > 0 && (
              <div className="mt-4">
                <Progress value={uploadProgress} className="w-full" />
                <div className="text-sm text-slate-400 mt-2 text-center">
                  Uploading... {uploadProgress}%
                </div>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex gap-3 mt-6">
              <Button
                variant="outline"
                onClick={() => setShowUploadModal(false)}
                className="flex-1"
              >
                Cancel
              </Button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );

  const renderSendModal = () => (
    <AnimatePresence>
      {showSendModal && selectedDocument && (
        <SendForSignatureModal
          document={selectedDocument}
          onClose={() => {
            setShowSendModal(false);
            setSelectedDocument(null);
          }}
          onSend={handleSendForSignature}
        />
      )}
    </AnimatePresence>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="text-white text-xl">Loading documents...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">Document Portal</h2>
          <p className="text-slate-400">
            Manage and track your documents and signatures
          </p>
        </div>
        
        <Button
          onClick={() => setShowUploadModal(true)}
          className="bg-cyan-600 hover:bg-cyan-700"
        >
          <Plus size={16} className="mr-2" />
          Upload Document
        </Button>
      </div>

      {/* Filters */}
      <Card className="bg-slate-800 border-slate-600">
        <CardContent className="p-4">
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            {/* Search */}
            <div className="md:col-span-2">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400" size={16} />
                <Input
                  placeholder="Search documents..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 bg-slate-700 border-slate-600 text-white"
                />
              </div>
            </div>

            {/* Status Filter */}
            <div>
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger className="bg-slate-700 border-slate-600 text-white">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-slate-700 border-slate-600">
                  <SelectItem value="all" className="text-white">All Status</SelectItem>
                  <SelectItem value="draft" className="text-white">Draft</SelectItem>
                  <SelectItem value="sent" className="text-white">Sent</SelectItem>
                  <SelectItem value="completed" className="text-white">Completed</SelectItem>
                  <SelectItem value="declined" className="text-white">Declined</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Category Filter */}
            <div>
              <Select value={categoryFilter} onValueChange={setCategoryFilter}>
                <SelectTrigger className="bg-slate-700 border-slate-600 text-white">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-slate-700 border-slate-600">
                  <SelectItem value="all" className="text-white">All Categories</SelectItem>
                  {DOCUMENT_CATEGORIES.map(category => (
                    <SelectItem key={category} value={category} className="text-white">
                      {category.replace('_', ' ').toUpperCase()}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Sort */}
            <div>
              <Select value={`${sortBy}_${sortOrder}`} onValueChange={(value) => {
                const [field, order] = value.split('_');
                setSortBy(field);
                setSortOrder(order);
              }}>
                <SelectTrigger className="bg-slate-700 border-slate-600 text-white">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-slate-700 border-slate-600">
                  <SelectItem value="created_at_desc" className="text-white">Newest First</SelectItem>
                  <SelectItem value="created_at_asc" className="text-white">Oldest First</SelectItem>
                  <SelectItem value="name_asc" className="text-white">Name A-Z</SelectItem>
                  <SelectItem value="name_desc" className="text-white">Name Z-A</SelectItem>
                  <SelectItem value="status_asc" className="text-white">Status</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Alerts */}
      {error && (
        <Alert className="bg-red-900/20 border-red-600">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription className="text-red-400">
            {error}
          </AlertDescription>
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
        <Alert className="bg-green-900/20 border-green-600">
          <CheckCircle className="h-4 w-4" />
          <AlertDescription className="text-green-400">
            {success}
          </AlertDescription>
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

      {/* Documents Grid */}
      <div>
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-white">
            Documents ({filteredDocuments.length})
          </h3>
        </div>

        {filteredDocuments.length === 0 ? (
          <Card className="bg-slate-800 border-slate-600">
            <CardContent className="p-12 text-center">
              <FileText size={48} className="mx-auto mb-4 text-slate-400" />
              <h3 className="text-lg font-medium text-white mb-2">No Documents Found</h3>
              <p className="text-slate-400 mb-4">
                {searchTerm || statusFilter !== "all" || categoryFilter !== "all" 
                  ? "No documents match your current filters."
                  : "Upload your first document to get started."
                }
              </p>
              <Button
                onClick={() => setShowUploadModal(true)}
                className="bg-cyan-600 hover:bg-cyan-700"
              >
                <Plus size={16} className="mr-2" />
                Upload Document
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {(filteredDocuments || []).map(renderDocumentCard)}
          </div>
        )}
      </div>

      {/* Modals */}
      {renderUploadModal()}
      <CameraCapture
        isOpen={showCameraModal}
        onCapture={handleCameraCapture}
        onClose={() => setShowCameraModal(false)}
      />
      {renderSendModal()}
    </div>
  );
};

// Send For Signature Modal Component
const SendForSignatureModal = ({ document, onClose, onSend }) => {
  const [recipients, setRecipients] = useState([{ email: "", name: "", role: "signer" }]);
  const [emailSubject, setEmailSubject] = useState(`Please sign: ${document.name}`);
  const [emailMessage, setEmailMessage] = useState("Please review and sign the attached document.");
  const [loading, setLoading] = useState(false);

  const addRecipient = () => {
    setRecipients([...recipients, { email: "", name: "", role: "signer" }]);
  };

  const removeRecipient = (index) => {
    setRecipients(recipients.filter((_, i) => i !== index));
  };

  const updateRecipient = (index, field, value) => {
    const updated = [...recipients];
    updated[index] = { ...updated[index], [field]: value };
    setRecipients(updated);
  };

  const handleSend = async () => {
    // Validate recipients
    const validRecipients = recipients.filter(r => r.email && r.name);
    
    if (validRecipients.length === 0) {
      alert("Please add at least one valid recipient with both name and email");
      return;
    }

    setLoading(true);
    try {
      await onSend(document.id, {
        recipients: validRecipients,
        email_subject: emailSubject,
        email_message: emailMessage
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.8, opacity: 0 }}
        className="bg-slate-800 rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <h3 className="text-xl font-semibold text-white mb-4">Send for Signature</h3>
        
        <div className="space-y-4">
          {/* Document Info */}
          <div className="bg-slate-700 rounded-lg p-3">
            <div className="flex items-center gap-3">
              <FileText className="w-8 h-8 text-cyan-400" />
              <div>
                <h4 className="text-white font-medium">{document.name}</h4>
                <p className="text-slate-400 text-sm">
                  {document.category?.replace('_', ' ').toUpperCase()}
                </p>
              </div>
            </div>
          </div>

          {/* Recipients */}
          <div>
            <div className="flex justify-between items-center mb-3">
              <Label className="text-slate-300">Recipients</Label>
              <Button
                size="sm"
                variant="outline"
                onClick={addRecipient}
                className="text-white border-slate-600"
              >
                <Plus size={14} className="mr-1" />
                Add Recipient
              </Button>
            </div>
            
            <div className="space-y-3">
              {(recipients || []).map((recipient, index) => (
                <div key={`recipient-${index}-${recipient.email || index}`} className="flex gap-3 items-end">
                  <div className="flex-1">
                    <Input
                      placeholder="Recipient Name"
                      value={recipient.name}
                      onChange={(e) => updateRecipient(index, 'name', e.target.value)}
                      className="bg-slate-700 border-slate-600 text-white mb-2"
                    />
                    <Input
                      placeholder="email@example.com"
                      type="email"
                      value={recipient.email}
                      onChange={(e) => updateRecipient(index, 'email', e.target.value)}
                      className="bg-slate-700 border-slate-600 text-white"
                    />
                  </div>
                  <div className="w-24">
                    <Select 
                      value={recipient.role} 
                      onValueChange={(value) => updateRecipient(index, 'role', value)}
                    >
                      <SelectTrigger className="bg-slate-700 border-slate-600 text-white">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent className="bg-slate-700 border-slate-600">
                        <SelectItem value="signer" className="text-white">Signer</SelectItem>
                        <SelectItem value="cc" className="text-white">CC</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  {recipients.length > 1 && (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => removeRecipient(index)}
                      className="text-red-400 border-red-600 hover:bg-red-900/20"
                    >
                      <Trash2 size={14} />
                    </Button>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Email Subject */}
          <div>
            <Label className="text-slate-300">Email Subject</Label>
            <Input
              value={emailSubject}
              onChange={(e) => setEmailSubject(e.target.value)}
              className="bg-slate-700 border-slate-600 text-white"
            />
          </div>

          {/* Email Message */}
          <div>
            <Label className="text-slate-300">Email Message</Label>
            <textarea
              value={emailMessage}
              onChange={(e) => setEmailMessage(e.target.value)}
              rows={4}
              className="w-full bg-slate-700 border border-slate-600 rounded-md p-3 text-white resize-none"
              placeholder="Message to recipients..."
            />
          </div>
        </div>

        <div className="flex gap-3 mt-6">
          <Button
            variant="outline"
            onClick={onClose}
            className="flex-1"
            disabled={loading}
          >
            Cancel
          </Button>
          <Button
            onClick={handleSend}
            disabled={loading}
            className="flex-1 bg-cyan-600 hover:bg-cyan-700"
          >
            {loading ? (
              <>
                <Clock className="mr-2 h-4 w-4 animate-spin" />
                Sending...
              </>
            ) : (
              <>
                <Send className="mr-2 h-4 w-4" />
                Send for Signature
              </>
            )}
          </Button>
        </div>
      </motion.div>
    </motion.div>
  );
};

export default DocumentPortal;