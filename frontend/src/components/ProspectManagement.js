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
  Users, 
  Plus, 
  Edit2, 
  Edit,
  Trash2, 
  UserCheck, 
  Send,
  Eye,
  ArrowRight,
  TrendingUp,
  Calendar,
  Phone,
  Mail,
  FileText,
  CheckCircle,
  XCircle,
  Clock,
  Target,
  DollarSign,
  Upload,
  Download,
  File,
  Image,
  Shield,
  ShieldCheck,
  AlertCircle,
  AlertTriangle,
  X,
  Home,
  CreditCard,
  Building,
  Briefcase,
  Calculator,
  MessageSquare,
  Video,
  Share2
} from "lucide-react";
import axios from "axios";
import apiAxios from "../utils/apiAxios";
import InvestmentSimulator from './InvestmentSimulator';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// AML/KYC Document Types Configuration
const KYC_DOCUMENT_TYPES = {
  identity: {
    label: "Identity Document",
    description: "Passport, Driver's License, National ID",
    icon: Shield,
    required: true,
    status: "completed" // Usually completed during onboarding
  },
  proof_of_residence: {
    label: "Proof of Residence",
    description: "Utility bill, Bank statement, Lease agreement (max 3 months old)",
    icon: Home,
    required: true,
    status: "pending"
  },
  bank_statement: {
    label: "Bank Statement",
    description: "Recent bank statement (max 3 months old)",
    icon: CreditCard,
    required: true,
    status: "pending"
  },
  source_of_funds: {
    label: "Source of Funds",
    description: "Salary slip, Business registration, Investment statement",
    icon: Building,
    required: true,
    status: "pending"
  },
  employment_verification: {
    label: "Employment Verification",
    description: "Employment letter, Contract, Business license",
    icon: Briefcase,
    required: false,
    status: "optional"
  }
};

const STAGE_CONFIG = {
  lead: { 
    label: "Lead", 
    color: "bg-blue-500", 
    textColor: "text-blue-700", 
    bgColor: "bg-blue-50",
    icon: Target 
  },
  negotiation: { 
    label: "Negotiation/Proposal", 
    color: "bg-orange-500", 
    textColor: "text-orange-700", 
    bgColor: "bg-orange-50",
    icon: TrendingUp 
  },
  won: { 
    label: "Won", 
    color: "bg-emerald-600", 
    textColor: "text-emerald-700", 
    bgColor: "bg-emerald-50",
    icon: UserCheck 
  },
  lost: { 
    label: "Lost", 
    color: "bg-red-500", 
    textColor: "text-red-700", 
    bgColor: "bg-red-50",
    icon: XCircle 
  }
};

const ProspectManagement = () => {
  const [prospects, setProspects] = useState([]);
  const [pipeline, setPipeline] = useState({});
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [showMeetingModal, setShowMeetingModal] = useState(false);
  const [showEmailModal, setShowEmailModal] = useState(false);
  const [selectedProspect, setSelectedProspect] = useState(null);
  const [meetingData, setMeetingData] = useState({
    type: 'consultation',
    date: '',
    time: '',
    duration: 60,
    notes: ''
  });
  const [emailData, setEmailData] = useState({
    type: 'general',
    subject: '',
    body: '',
    recipient: null
  });
  const [activeTab, setActiveTab] = useState("overview");
  
  // Document management states
  const [showDocumentModal, setShowDocumentModal] = useState(false);
  const [selectedProspectForDocs, setSelectedProspectForDocs] = useState(null);
  const [prospectDocuments, setProspectDocuments] = useState({});
  const [uploadingDocument, setUploadingDocument] = useState(false);
  const [documentToUpload, setDocumentToUpload] = useState({
    type: "",
    file: null,
    notes: ""
  });

  // Form states
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    phone: "",
    notes: ""
  });

  useEffect(() => {
    fetchProspects();
    fetchPipeline();
  }, []);

  // ===== GOOGLE API INTEGRATION FUNCTIONS =====
  
  // Email prospect via Gmail API with modal
  const openEmailModal = (prospect, emailType = 'general') => {
    setSelectedProspect(prospect);
    setEmailData({
      type: emailType,
      subject: emailType === 'document_request' 
        ? `Document Request - ${prospect.name}` 
        : `Investment Opportunity - ${prospect.name}`,
      body: emailType === 'document_request' 
        ? `Dear ${prospect.name},\n\nWe need the following documents to proceed with your investment application:\n\n- Government-issued photo ID\n- Proof of residence\n- Bank statement\n- Source of funds documentation\n\nBest regards,\nFIDUS Investment Management Team`
        : `Dear ${prospect.name},\n\nThank you for your interest in FIDUS Investment Management. We would like to discuss investment opportunities with you.\n\nBest regards,\nFIDUS Investment Management Team`,
      recipient: prospect
    });
    setShowEmailModal(true);
  };

  // Schedule meeting via Calendar API with modal
  const openMeetingModal = (prospect, meetingType = 'consultation') => {
    setSelectedProspect(prospect);
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    
    setMeetingData({
      type: meetingType,
      date: tomorrow.toISOString().split('T')[0],
      time: '14:00',
      duration: meetingType === 'consultation' ? 60 : 30,
      notes: `${meetingType === 'consultation' ? 'Investment consultation' : 'Follow-up meeting'} with ${prospect.name}`
    });
    setShowMeetingModal(true);
  };

  // Send email function
  const sendProspectEmail = async () => {
    if (!emailData.recipient || !emailData.subject || !emailData.body) {
      setError('Please fill in all email fields');
      return;
    }

    try {
      const response = await apiAxios.post('/google/gmail/send', {
        to: emailData.recipient.email,
        subject: emailData.subject,
        body: emailData.body,
        html_body: emailData.body.replace(/\n/g, '<br>')
      });

      if (response.data.success) {
        setSuccess(`Email sent successfully to ${emailData.recipient.name}!`);
        setShowEmailModal(false);
      } else {
        setError(`Failed to send email: ${response.data.error}`);
      }
    } catch (error) {
      console.error('Email sending error:', error);
      setError('Failed to send email. Please ensure Google authentication is active.');
    }
  };

  // Schedule meeting function
  const scheduleProspectMeeting = async () => {
    if (!meetingData.date || !meetingData.time || !selectedProspect) {
      setError('Please fill in all meeting details');
      return;
    }

    try {
      const startDateTime = new Date(`${meetingData.date}T${meetingData.time}:00`);
      const endDateTime = new Date(startDateTime.getTime() + meetingData.duration * 60000);

      const eventData = {
        summary: `${meetingData.type === 'consultation' ? 'Investment Consultation' : 'Follow-up Meeting'} - ${selectedProspect.name}`,
        description: `${meetingData.notes}\n\nContact: ${selectedProspect.email}\nPhone: ${selectedProspect.phone || 'N/A'}`,
        start: {
          dateTime: startDateTime.toISOString(),
          timeZone: 'UTC'
        },
        end: {
          dateTime: endDateTime.toISOString(),
          timeZone: 'UTC'
        },
        attendees: [{ email: selectedProspect.email }],
        conferenceData: {
          createRequest: {
            requestId: `prospect-meeting-${Date.now()}`,
            conferenceSolutionKey: { type: 'hangoutsMeet' }
          }
        }
      };

      const response = await apiAxios.post('/google/calendar/create-event', eventData);
      
      if (response.data.success) {
        setSuccess(`Meeting scheduled successfully with ${selectedProspect.name}! Calendar invite sent.`);
        setShowMeetingModal(false);
      } else {
        setError(`Failed to schedule meeting: ${response.data.error}`);
      }
    } catch (error) {
      console.error('Meeting scheduling error:', error);
      setError('Failed to schedule meeting. Please ensure Google authentication is active.');
    }
  };

  // Email prospect with different types
  const emailProspectWithType = async (prospect, emailType = 'general') => {
    try {
      let subject, body, htmlBody;
      
      switch (emailType) {
        case 'document_request':
          subject = 'Document Request - FIDUS Investment Management';
          body = `Dear ${prospect.name},

Thank you for your interest in FIDUS Investment Management. To proceed with your investment application, we need the following documents:

Required Documents:
- Government-issued photo ID (passport, driver's license, or national ID)
- Proof of residence (utility bill, bank statement, or lease agreement - max 3 months old)
- Bank statement (recent statement from your primary bank account)
- Source of funds documentation (salary slip, business registration, or investment statements)

You can upload these documents securely through our client portal or respond to this email with the attachments.

If you have any questions, please don't hesitate to contact us.

Best regards,
FIDUS Investment Management Team`;
          
          htmlBody = `<html><body>
<h2>Document Request - FIDUS Investment Management</h2>
<p>Dear ${prospect.name},</p>
<p>Thank you for your interest in FIDUS Investment Management. To proceed with your investment application, we need the following documents:</p>
<h3>Required Documents:</h3>
<ul>
<li>Government-issued photo ID (passport, driver's license, or national ID)</li>
<li>Proof of residence (utility bill, bank statement, or lease agreement - max 3 months old)</li>
<li>Bank statement (recent statement from your primary bank account)</li>
<li>Source of funds documentation (salary slip, business registration, or investment statements)</li>
</ul>
<p>You can upload these documents securely through our client portal or respond to this email with the attachments.</p>
<p>If you have any questions, please don't hesitate to contact us.</p>
<p>Best regards,<br><strong>FIDUS Investment Management Team</strong></p>
</body></html>`;
          break;
          
        case 'meeting_followup':
          subject = 'Follow-up - Investment Consultation';
          body = `Dear ${prospect.name},

Thank you for your time during our recent discussion about investment opportunities with FIDUS Investment Management.

As discussed, we believe our investment solutions can help you achieve your financial goals. Here's a summary of what we can offer:

- Personalized portfolio management
- Risk assessment and mitigation strategies
- Regular performance reviews and updates
- Access to institutional-grade investment products

Next steps:
1. Review the investment proposal we'll send separately
2. Complete the necessary documentation
3. Schedule a follow-up meeting if you have questions

We're here to support you every step of the way. Please don't hesitate to reach out with any questions.

Best regards,
FIDUS Investment Management Team`;

          htmlBody = `<html><body>
<h2>Follow-up - Investment Consultation</h2>
<p>Dear ${prospect.name},</p>
<p>Thank you for your time during our recent discussion about investment opportunities with FIDUS Investment Management.</p>
<p>As discussed, we believe our investment solutions can help you achieve your financial goals. Here's what we can offer:</p>
<ul>
<li>Personalized portfolio management</li>
<li>Risk assessment and mitigation strategies</li>
<li>Regular performance reviews and updates</li>
<li>Access to institutional-grade investment products</li>
</ul>
<h3>Next steps:</h3>
<ol>
<li>Review the investment proposal we'll send separately</li>
<li>Complete the necessary documentation</li>
<li>Schedule a follow-up meeting if you have questions</li>
</ol>
<p>We're here to support you every step of the way. Please don't hesitate to reach out with any questions.</p>
<p>Best regards,<br><strong>FIDUS Investment Management Team</strong></p>
</body></html>`;
          break;
          
        default:
          subject = 'Investment Opportunity - FIDUS Investment Management';
          body = `Dear ${prospect.name},

Thank you for your interest in FIDUS Investment Management. We specialize in creating customized investment solutions that align with your financial goals.

Our experienced team would love to discuss how we can help you achieve your investment objectives. We offer comprehensive portfolio management, risk assessment, and personalized investment strategies.

Would you be available for a brief consultation this week? We can arrange a call at your convenience.

Best regards,
FIDUS Investment Management Team`;

          htmlBody = `<html><body>
<h2>Investment Opportunity - FIDUS Investment Management</h2>
<p>Dear ${prospect.name},</p>
<p>Thank you for your interest in FIDUS Investment Management. We specialize in creating customized investment solutions that align with your financial goals.</p>
<p>Our experienced team would love to discuss how we can help you achieve your investment objectives. We offer:</p>
<ul>
<li>Comprehensive portfolio management</li>
<li>Risk assessment and mitigation</li>
<li>Personalized investment strategies</li>
</ul>
<p>Would you be available for a brief consultation this week? We can arrange a call at your convenience.</p>
<p>Best regards,<br><strong>FIDUS Investment Management Team</strong></p>
</body></html>`;
          break;
      }

      const response = await apiAxios.post('/google/gmail/send', {
        to: prospect.email,
        subject: subject,
        body: body,
        html_body: htmlBody
      });

      if (response.data.success) {
        setSuccess(`Email sent successfully to ${prospect.name}!`);
      } else {
        setError(`Failed to send email: ${response.data.error}`);
      }
    } catch (error) {
      console.error('Email sending error:', error);
      setError('Failed to send email. Please ensure Google authentication is active.');
    }
  };

  // Share investment report with prospect
  const shareInvestmentReport = async (prospect) => {
    try {
      // Generate personalized investment report data
      const reportData = {
        prospect_name: prospect.name,
        initial_investment: prospect.initial_investment || 'To be determined',
        risk_tolerance: prospect.risk_tolerance || 'Conservative',
        investment_timeline: prospect.investment_timeline || '5+ years',
        recommended_allocation: {
          conservative: '60% Bonds, 40% Stocks',
          moderate: '50% Bonds, 50% Stocks', 
          aggressive: '30% Bonds, 70% Stocks'
        }
      };

      // Send personalized investment report via email
      const subject = `Personalized Investment Report - ${prospect.name}`;
      const body = `Dear ${prospect.name},

Based on our discussions, we've prepared a personalized investment report for your review.

Investment Profile:
- Initial Investment: ${reportData.initial_investment}
- Risk Tolerance: ${reportData.risk_tolerance}
- Investment Timeline: ${reportData.investment_timeline}

Recommended Portfolio Allocation:
${reportData.recommended_allocation[prospect.risk_tolerance?.toLowerCase()] || reportData.recommended_allocation.conservative}

Key Benefits of Working with FIDUS:
- Professional portfolio management
- Regular performance monitoring
- Risk management strategies
- Transparent fee structure

Next Steps:
1. Review this personalized report
2. Schedule a detailed consultation
3. Begin your investment journey with FIDUS

Please don't hesitate to contact us with any questions.

Best regards,
FIDUS Investment Management Team`;

      const htmlBody = `<html><body>
<h2>Personalized Investment Report - ${prospect.name}</h2>
<p>Dear ${prospect.name},</p>
<p>Based on our discussions, we've prepared a personalized investment report for your review.</p>

<h3>Investment Profile:</h3>
<ul>
<li><strong>Initial Investment:</strong> ${reportData.initial_investment}</li>
<li><strong>Risk Tolerance:</strong> ${reportData.risk_tolerance}</li>
<li><strong>Investment Timeline:</strong> ${reportData.investment_timeline}</li>
</ul>

<h3>Recommended Portfolio Allocation:</h3>
<p><strong>${reportData.recommended_allocation[prospect.risk_tolerance?.toLowerCase()] || reportData.recommended_allocation.conservative}</strong></p>

<h3>Key Benefits of Working with FIDUS:</h3>
<ul>
<li>Professional portfolio management</li>
<li>Regular performance monitoring</li>
<li>Risk management strategies</li>
<li>Transparent fee structure</li>
</ul>

<h3>Next Steps:</h3>
<ol>
<li>Review this personalized report</li>
<li>Schedule a detailed consultation</li>
<li>Begin your investment journey with FIDUS</li>
</ol>

<p>Please don't hesitate to contact us with any questions.</p>
<p>Best regards,<br><strong>FIDUS Investment Management Team</strong></p>
</body></html>`;

      const response = await apiAxios.post('/google/gmail/send', {
        to: prospect.email,
        subject: subject,
        body: body,
        html_body: htmlBody
      });

      if (response.data.success) {
        setSuccess(`Investment report shared successfully with ${prospect.name}!`);
      } else {
        setError(`Failed to share report: ${response.data.error}`);
      }
    } catch (error) {
      console.error('Report sharing error:', error);
      setError('Failed to share report. Please ensure Google authentication is active.');
    }
  };

  // Show prospect detail modal with Google actions
  const showProspectDetail = (prospect) => {
    setSelectedProspect(prospect);
    setShowDetailModal(true);
  };

  const fetchProspects = async () => {
    try {
      setLoading(true);
      const response = await apiAxios.get(`/crm/prospects`);
      setProspects(response.data.prospects);
      setStats(response.data);
    } catch (err) {
      setError("Failed to fetch prospects");
      console.error("Error fetching prospects:", err);
    } finally {
      setLoading(false);
    }
  };

  const fetchPipeline = async () => {
    try {
      const response = await apiAxios.get(`/crm/prospects/pipeline`);
      setPipeline(response.data.pipeline);
      setStats(prev => ({ ...prev, ...response.data.stats }));
    } catch (err) {
      console.error("Error fetching pipeline:", err);
    }
  };

  const handleAddProspect = async () => {
    try {
      if (!formData.name || !formData.email || !formData.phone) {
        setError("Please fill in all required fields");
        return;
      }

      const response = await apiAxios.post(`/crm/prospects`, formData);
      
      if (response.data.success) {
        setSuccess("Prospect added successfully");
        setShowAddModal(false);
        resetForm();
        fetchProspects();
        fetchPipeline();
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to add prospect");
    }
  };

  const handleUpdateProspect = async () => {
    try {
      if (!selectedProspect) return;

      const response = await apiAxios.put(`/crm/prospects/${selectedProspect.id}`, formData);
      
      if (response.data.success) {
        setSuccess("Prospect updated successfully");
        setShowEditModal(false);
        setSelectedProspect(null);
        resetForm();
        fetchProspects();
        fetchPipeline();
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to update prospect");
    }
  };

  const handleStageChange = async (prospectId, newStage) => {
    try {
      setLoading(true);
      console.log(`Updating prospect ${prospectId} to stage: ${newStage}`);
      
      const response = await apiAxios.put(`/crm/prospects/${prospectId}`, {
        stage: newStage,
        notes: `Moved to ${newStage} stage on ${new Date().toLocaleDateString()}`
      });
      
      console.log('Stage update response:', response.data);
      
      if (response.data.success) {
        setSuccess(`✅ Prospect moved to ${STAGE_CONFIG[newStage].label} stage successfully!`);
        await fetchProspects();
        await fetchPipeline();
      } else {
        setError(`Failed to update prospect stage: ${response.data.message || 'Unknown error'}`);
      }
    } catch (err) {
      console.error('Stage change error:', err);
      const errorMessage = err.response?.data?.detail || err.response?.data?.message || err.message || "Failed to update prospect stage";
      setError(`❌ Error: ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteProspect = async (prospectId, prospectName) => {
    if (!window.confirm(`Are you sure you want to delete prospect "${prospectName}"?`)) {
      return;
    }

    try {
      const response = await apiAxios.delete(`/crm/prospects/${prospectId}`);
      
      if (response.data.success) {
        setSuccess("Prospect deleted successfully");
        fetchProspects();
        fetchPipeline();
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to delete prospect");
    }
  };

  const handleAMLKYCCheck = async (prospectId) => {
    try {
      setLoading(true);
      const response = await apiAxios.post(`/crm/prospects/${prospectId}/aml-kyc`);
      
      if (response.data.success) {
        const amlResult = response.data.aml_result;
        setSuccess(`AML/KYC check completed: ${amlResult.overall_status.toUpperCase()}`);
        
        // Show detailed results
        if (amlResult.ofac_matches > 0) {
          setError(`⚠️ OFAC Alert: ${amlResult.ofac_matches} potential match(es) found. Status: ${amlResult.ofac_status}`);
        }
        
        fetchProspects();
        fetchPipeline();
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to run AML/KYC check");
    } finally {
      setLoading(false);
    }
  };

  const handleManualAMLApproval = async (prospectId) => {
    try {
      setLoading(true);
      const response = await apiAxios.post(`/crm/prospects/${prospectId}/aml-approve`, {
        prospect_id: prospectId,
        approved: true,
        admin_notes: "Manual AML/KYC review completed and approved by admin"
      });
      
      if (response.data.success) {
        setSuccess("AML/KYC status approved manually. Prospect can now be converted to client.");
        fetchProspects();
        fetchPipeline();
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to approve AML/KYC manually");
    } finally {
      setLoading(false);
    }
  };

  const handleConvertProspect = async (prospectId) => {
    try {
      setLoading(true);
      const response = await apiAxios.post(`/crm/prospects/${prospectId}/convert`, {
        prospect_id: prospectId,
        send_agreement: true
      });
      
      if (response.data.success) {
        setSuccess(`Prospect converted to client successfully! Username: ${response.data.username}. ${response.data.message}`);
        fetchProspects();
        fetchPipeline();
      }
    } catch (err) {
      if (err.response?.data?.detail?.includes('AML/KYC compliance required')) {
        setError(`${err.response.data.detail} Please run AML/KYC check first.`);
      } else {
        setError(err.response?.data?.detail || "Failed to convert prospect");
      }
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFormData({
      name: "",
      email: "",
      phone: "",
      notes: ""
    });
    setError("");
    setSuccess("");
  };
  
  // Document Management Functions
  const fetchProspectDocuments = async (prospectId) => {
    try {
      const response = await apiAxios.get(`/crm/prospects/${prospectId}/documents`);
      setProspectDocuments(prev => ({
        ...prev,
        [prospectId]: response.data.documents || []
      }));
    } catch (err) {
      console.error("Error fetching prospect documents:", err);
    }
  };
  
  const handleDocumentUpload = async () => {
    try {
      if (!documentToUpload.type || !documentToUpload.file) {
        setError("Please select document type and file");
        return;
      }
      
      setUploadingDocument(true);
      
      const formData = new FormData();
      formData.append('file', documentToUpload.file);
      formData.append('document_type', documentToUpload.type);
      formData.append('notes', documentToUpload.notes);
      
      const response = await apiAxios.post(
        `/crm/prospects/${selectedProspectForDocs.id}/documents`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      
      if (response.data.success) {
        setSuccess("Document uploaded successfully");
        setDocumentToUpload({ type: "", file: null, notes: "" });
        fetchProspectDocuments(selectedProspectForDocs.id);
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to upload document");
    } finally {
      setUploadingDocument(false);
    }
  };
  
  const handleRequestDocument = async (prospectId, documentType) => {
    try {
      const response = await apiAxios.post(`/crm/prospects/${prospectId}/documents/request`, {
        document_type: documentType,
        message: `Please upload your ${KYC_DOCUMENT_TYPES[documentType].label} to complete your KYC verification.`
      });
      
      if (response.data.success) {
        setSuccess(`Document request sent to ${prospects.find(p => p.id === prospectId)?.name}`);
        fetchProspectDocuments(prospectId);
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to request document");
    }
  };
  
  const handleVerifyDocument = async (prospectId, documentId, status) => {
    try {
      const response = await apiAxios.patch(`/crm/prospects/${prospectId}/documents/${documentId}`, {
        verification_status: status,
        verified_at: new Date().toISOString(),
        verified_by: "admin"
      });
      
      if (response.data.success) {
        setSuccess(`Document ${status === 'approved' ? 'approved' : 'rejected'} successfully`);
        fetchProspectDocuments(prospectId);
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to verify document");
    }
  };
  
  const openDocumentModal = (prospect) => {
    setSelectedProspectForDocs(prospect);
    setShowDocumentModal(true);
    fetchProspectDocuments(prospect.id);
  };
  
  const getDocumentStatus = (prospectId, documentType) => {
    const documents = prospectDocuments[prospectId] || [];
    const doc = documents.find(d => d.document_type === documentType);
    
    if (!doc) return 'missing';
    if (doc.verification_status === 'approved') return 'approved';
    if (doc.verification_status === 'rejected') return 'rejected';
    if (doc.verification_status === 'pending') return 'pending';
    return 'uploaded';
  };
  
  const getKYCCompletionStatus = (prospectId) => {
    const requiredDocs = Object.keys(KYC_DOCUMENT_TYPES).filter(
      key => KYC_DOCUMENT_TYPES[key].required
    );
    
    const approvedDocs = requiredDocs.filter(
      docType => getDocumentStatus(prospectId, docType) === 'approved'
    );
    
    return {
      completed: approvedDocs.length,
      total: requiredDocs.length,
      percentage: Math.round((approvedDocs.length / requiredDocs.length) * 100),
      isComplete: approvedDocs.length === requiredDocs.length
    };
  };

  const openEditModal = (prospect) => {
    setSelectedProspect(prospect);
    setFormData({
      name: prospect.name,
      email: prospect.email,
      phone: prospect.phone,
      notes: prospect.notes || ""
    });
    setShowEditModal(true);
  };

  const renderProspectCard = (prospect) => {
    const stageConfig = STAGE_CONFIG[prospect.stage] || STAGE_CONFIG.lead; // Fallback to lead
    const IconComponent = stageConfig?.icon || Target; // Fallback to Target icon

    return (
      <motion.div
        key={prospect.id}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-lg border border-slate-200 p-4 hover:shadow-md transition-shadow"
      >
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-full ${stageConfig.bgColor}`}>
              <IconComponent className={`h-4 w-4 ${stageConfig.textColor}`} />
            </div>
            <div>
              <h3 className="font-medium text-slate-900">{prospect.name}</h3>
              <p className="text-sm text-slate-600">{prospect.email}</p>
            </div>
          </div>
          <Badge className={`${stageConfig.color} text-white text-xs`}>
            {stageConfig.label}
          </Badge>
        </div>

        <div className="space-y-2 text-sm text-slate-600 mb-4">
          <div className="flex items-center gap-2">
            <Phone className="h-3 w-3" />
            <span>{prospect.phone}</span>
          </div>
          <div className="flex items-center gap-2">
            <Calendar className="h-3 w-3" />
            <span>Created: {new Date(prospect.created_at).toLocaleDateString()}</span>
          </div>
          
          {/* AML/KYC Status */}
          {prospect.aml_kyc_status && (
            <div className="flex items-center gap-2">
              <ShieldCheck className="h-3 w-3" />
              <span className={`text-xs font-medium ${
                prospect.aml_kyc_status === 'clear' || prospect.aml_kyc_status === 'approved' 
                  ? 'text-green-600' 
                  : prospect.aml_kyc_status === 'manual_review' 
                  ? 'text-yellow-600' 
                  : prospect.aml_kyc_status === 'hit' || prospect.aml_kyc_status === 'rejected'
                  ? 'text-red-600'
                  : 'text-gray-600'
              }`}>
                AML/KYC: {prospect.aml_kyc_status.toUpperCase()}
              </span>
            </div>
          )}
          
          {prospect.notes && (
            <div className="flex items-start gap-2">
              <FileText className="h-3 w-3 mt-0.5" />
              <span className="text-xs">{prospect.notes.substring(0, 100)}...</span>
            </div>
          )}
        </div>

        <div className="flex gap-1 flex-wrap">
          {/* Google API Action Buttons */}
          <div className="w-full grid grid-cols-2 gap-2 mb-2">
            <Button
              size="sm"
              variant="outline"
              onClick={() => openEmailModal(prospect, 'general')}
              className="text-xs bg-blue-50 hover:bg-blue-100 border-blue-200"
            >
              <MessageSquare size={12} className="mr-1" />
              Email
            </Button>
            
            <Button
              size="sm"
              variant="outline"
              onClick={() => openMeetingModal(prospect, 'consultation')}
              className="text-xs bg-green-50 hover:bg-green-100 border-green-200"
            >
              <Video size={12} className="mr-1" />
              Meet
            </Button>
            
            <Button
              size="sm"
              variant="outline"
              onClick={() => openEmailModal(prospect, 'document_request')}
              className="text-xs bg-orange-50 hover:bg-orange-100 border-orange-200"
            >
              <FileText size={12} className="mr-1" />
              Docs
            </Button>
            
            <Button
              size="sm"
              variant="outline"
              onClick={() => shareInvestmentReport(prospect)}
              className="text-xs bg-purple-50 hover:bg-purple-100 border-purple-200"
            >
              <Share2 size={12} className="mr-1" />
              Report
            </Button>
          </div>
          
          {/* Regular Action Buttons */}
          <Button
            size="sm"
            variant="outline"
            onClick={() => showProspectDetail(prospect)}
            className="flex-1 min-w-0"
          >
            <Edit2 size={14} className="mr-1" />
            Details
          </Button>
          
          <Button
            size="sm"
            variant="outline"
            onClick={() => openEditModal(prospect)}
            className="flex-1 min-w-0"
          >
            <Edit size={14} className="mr-1" />
            Edit
          </Button>
          
          {/* AML/KYC Check Button - Show for won prospects without AML/KYC status */}
          {prospect.stage === 'won' && !prospect.aml_kyc_status && (
            <Button
              size="sm"
              onClick={() => handleAMLKYCCheck(prospect.id)}
              disabled={loading}
              className="flex-1 bg-blue-600 hover:bg-blue-700 min-w-0"
            >
              <ShieldCheck size={14} className="mr-1" />
              AML/KYC
            </Button>
          )}
          
          {/* Convert Button - Show only if AML/KYC is clear/approved - MADE BIGGER AND BOLDER */}
          {prospect.stage === 'won' && 
           (prospect.aml_kyc_status === 'clear' || prospect.aml_kyc_status === 'approved') && 
           !prospect.converted_to_client && (
            <Button
              size="lg"
              onClick={() => handleConvertProspect(prospect.id)}
              disabled={loading}
              className="flex-1 bg-green-600 hover:bg-green-700 min-w-0 h-10 px-6 font-bold text-base shadow-lg border-2 border-green-500 hover:border-green-400"
            >
              <UserCheck size={18} className="mr-2" />
              CONVERT TO CLIENT
            </Button>
          )}
          
          {/* Show AML/KYC status for manual review cases */}
          {prospect.stage === 'won' && prospect.aml_kyc_status === 'manual_review' && (
            <div className="flex gap-2 w-full">
              <Button
                size="sm"
                variant="outline"
                className="flex-1 bg-yellow-50 border-yellow-300 text-yellow-800 min-w-0"
                disabled
              >
                <AlertTriangle size={14} className="mr-1" />
                Manual Review Required
              </Button>
              <Button
                size="sm"
                onClick={() => handleManualAMLApproval(prospect.id)}
                disabled={loading}
                className="bg-green-600 hover:bg-green-700 text-white font-semibold px-4"
              >
                <ShieldCheck size={14} className="mr-1" />
                Approve AML/KYC
              </Button>
            </div>
          )}
          
          {/* Show rejected status */}
          {prospect.stage === 'won' && (prospect.aml_kyc_status === 'hit' || prospect.aml_kyc_status === 'rejected') && (
            <Button
              size="sm"
              variant="outline"
              className="flex-1 bg-red-50 border-red-300 text-red-800 min-w-0"
              disabled
            >
              <X size={14} className="mr-1" />
              Rejected
            </Button>
          )}
          
          <Button
            size="sm"
            variant="outline"
            onClick={() => handleDeleteProspect(prospect.id, prospect.name)}
            className="text-red-500 hover:text-red-700"
          >
            <Trash2 size={14} />
          </Button>
        </div>
      </motion.div>
    );
  };

  const renderStageColumn = (stage, prospects) => {
    const stageConfig = STAGE_CONFIG[stage] || STAGE_CONFIG.lead; // Fallback to lead if stage not found
    const IconComponent = stageConfig?.icon || Target; // Fallback to Target icon

    return (
      <div key={stage} className="min-w-80 bg-slate-50 rounded-lg p-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <IconComponent className={`h-5 w-5 ${stageConfig.textColor}`} />
            <h3 className="font-medium text-slate-900">{stageConfig.label}</h3>
            <Badge variant="outline" className="text-xs">
              {(prospects || []).length}
            </Badge>
          </div>
        </div>

        <div className="space-y-3 max-h-96 overflow-y-auto">
          {(prospects || []).map(prospect => (
            <div key={prospect.id} className="bg-white rounded-lg border p-3 shadow-sm">
              <div className="flex items-start justify-between mb-2">
                <div>
                  <h4 className="font-medium text-sm text-slate-900">{prospect.name}</h4>
                  <p className="text-xs text-slate-600">{prospect.email}</p>
                  {/* KYC Completion Status */}
                  {(() => {
                    const kycStatus = getKYCCompletionStatus(prospect.id);
                    return (
                      <div className="flex items-center gap-1 mt-1">
                        <Shield className="h-3 w-3 text-slate-400" />
                        <span className="text-xs text-slate-500">
                          KYC: {kycStatus.completed}/{kycStatus.total} ({kycStatus.percentage}%)
                        </span>
                        {kycStatus.isComplete && <CheckCircle className="h-3 w-3 text-green-500" />}
                      </div>
                    );
                  })()}
                </div>
                <div className="flex gap-1">
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => openDocumentModal(prospect)}
                    className="h-6 w-6 p-0 text-blue-600 hover:text-blue-700"
                    title="Manage Documents"
                  >
                    <FileText size={12} />
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => openEditModal(prospect)}
                    className="h-6 w-6 p-0"
                  >
                    <Edit2 size={12} />
                  </Button>
                </div>
              </div>
              
              <div className="flex items-center gap-2 text-xs text-slate-500 mb-3">
                <Phone className="h-3 w-3" />
                <span>{prospect.phone}</span>
              </div>

              {/* Stage progression buttons - IMPROVED VISIBILITY */}
              <div className="flex gap-2 flex-wrap mt-3 pt-2 border-t border-slate-100">
                <p className="text-xs text-slate-500 w-full mb-1">Move to stage:</p>
                {Object.keys(STAGE_CONFIG).map(nextStage => {
                  if (nextStage === stage) return null;
                  const nextConfig = STAGE_CONFIG[nextStage];
                  
                  return (
                    <Button
                      key={nextStage}
                      size="sm"
                      variant="default"
                      onClick={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        console.log(`Moving prospect ${prospect.id} to ${nextStage}`);
                        handleStageChange(prospect.id, nextStage);
                      }}
                      disabled={loading}
                      className="text-xs h-8 px-3 font-medium bg-slate-600 text-white hover:bg-slate-700 border border-slate-600 hover:border-slate-700 transition-all hover:scale-105 hover:shadow-md"
                    >
                      {nextConfig.label}
                    </Button>
                  );
                })}
              </div>
            </div>
          ))}
          
          {(prospects || []).length === 0 && (
            <div className="text-center py-8 text-slate-500">
              <Users className="h-8 w-8 mx-auto mb-2 opacity-50" />
              <p className="text-sm">No prospects in this stage</p>
            </div>
          )}
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="text-slate-600 text-xl">Loading prospects...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">Prospect Management</h2>
          <p className="text-slate-600">Manage leads and track conversion pipeline</p>
        </div>
        
        <Button
          onClick={() => setShowAddModal(true)}
          className="bg-cyan-600 hover:bg-cyan-700"
        >
          <Plus size={16} className="mr-2" />
          Add Prospect
        </Button>
      </div>

      {/* Success/Error Messages */}
      {error && (
        <Alert className="bg-red-50 border-red-200">
          <AlertDescription className="text-red-800">{error}</AlertDescription>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setError("")}
            className="ml-auto text-red-600"
          >
            ×
          </Button>
        </Alert>
      )}

      {success && (
        <Alert className="bg-green-50 border-green-200">
          <AlertDescription className="text-green-800">{success}</AlertDescription>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setSuccess("")}
            className="ml-auto text-green-600"
          >
            ×
          </Button>
        </Alert>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-50 rounded-full">
                <Users className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-slate-600">Total Prospects</p>
                <p className="text-xl font-semibold text-slate-900">{stats.total_prospects || 0}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-50 rounded-full">
                <Target className="h-5 w-5 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-slate-600">Active Prospects</p>
                <p className="text-xl font-semibold text-slate-900">{stats.active_prospects || 0}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-emerald-50 rounded-full">
                <UserCheck className="h-5 w-5 text-emerald-600" />
              </div>
              <div>
                <p className="text-sm text-slate-600">Won Prospects</p>
                <p className="text-xl font-semibold text-slate-900">{stats.won_prospects || 0}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-purple-50 rounded-full">
                <TrendingUp className="h-5 w-5 text-purple-600" />
              </div>
              <div>
                <p className="text-sm text-slate-600">Conversion Rate</p>
                <p className="text-xl font-semibold text-slate-900">{stats.conversion_rate || 0}%</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="pipeline">Pipeline</TabsTrigger>
          <TabsTrigger value="simulator">
            <Calculator className="w-4 h-4 mr-2" />
            Investment Simulator
          </TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {(prospects || []).map(renderProspectCard)}
          </div>
          
          {(prospects || []).length === 0 && (
            <Card>
              <CardContent className="p-12 text-center">
                <Users size={48} className="mx-auto mb-4 text-slate-400" />
                <h3 className="text-lg font-medium text-slate-900 mb-2">No Prospects Yet</h3>
                <p className="text-slate-600 mb-4">Start building your sales pipeline by adding prospects</p>
                <Button
                  onClick={() => setShowAddModal(true)}
                  className="bg-cyan-600 hover:bg-cyan-700"
                >
                  <Plus size={16} className="mr-2" />
                  Add First Prospect
                </Button>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="pipeline" className="space-y-4">
          <div className="overflow-x-auto">
            <div className="flex gap-4 pb-4" style={{ minWidth: 'fit-content' }}>
              {Object.entries(pipeline).map(([stage, prospects]) => 
                renderStageColumn(stage, prospects)
              )}
            </div>
          </div>
        </TabsContent>

        <TabsContent value="simulator" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calculator className="w-5 h-5" />
                Investment Portfolio Simulator
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <div className="flex items-start gap-3">
                  <TrendingUp className="w-5 h-5 text-blue-600 mt-0.5" />
                  <div>
                    <h3 className="font-medium text-blue-900 mb-1">Sales Tool - Investment Simulator</h3>
                    <p className="text-blue-700 text-sm">
                      Use this powerful tool during prospect calls to show real-time projections across FIDUS fund combinations. 
                      Demonstrate potential returns, incubation periods, and redemption schedules to convert leads effectively.
                    </p>
                  </div>
                </div>
              </div>

              <InvestmentSimulator isPublic={false} />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Add Prospect Modal */}
      <AnimatePresence>
        {showAddModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
            onClick={() => setShowAddModal(false)}
          >
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.8, opacity: 0 }}
              className="bg-white rounded-lg p-6 max-w-md w-full mx-4"
              onClick={(e) => e.stopPropagation()}
            >
              <h3 className="text-xl font-semibold text-slate-900 mb-4">Add New Prospect</h3>
              
              <div className="space-y-4">
                <div>
                  <Label htmlFor="name" className="text-slate-700">Name *</Label>
                  <Input
                    id="name"
                    value={formData.name}
                    onChange={(e) => setFormData({...formData, name: e.target.value})}
                    placeholder="Full name"
                    className="mt-1"
                  />
                </div>
                
                <div>
                  <Label htmlFor="email" className="text-slate-700">Email *</Label>
                  <Input
                    id="email"
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                    placeholder="email@example.com"
                    className="mt-1"
                  />
                </div>
                
                <div>
                  <Label htmlFor="phone" className="text-slate-700">Phone *</Label>
                  <Input
                    id="phone"
                    value={formData.phone}
                    onChange={(e) => setFormData({...formData, phone: e.target.value})}
                    placeholder="+1 (555) 123-4567"
                    className="mt-1"
                  />
                </div>
                
                <div>
                  <Label htmlFor="notes" className="text-slate-700">Notes</Label>
                  <textarea
                    id="notes"
                    value={formData.notes}
                    onChange={(e) => setFormData({...formData, notes: e.target.value})}
                    placeholder="Additional notes about this prospect..."
                    className="mt-1 w-full min-h-20 px-3 py-2 border border-slate-300 rounded-md resize-none"
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
                  onClick={handleAddProspect}
                  className="flex-1 bg-cyan-600 hover:bg-cyan-700"
                >
                  Add Prospect
                </Button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Edit Prospect Modal */}
      <AnimatePresence>
        {showEditModal && selectedProspect && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
            onClick={() => setShowEditModal(false)}
          >
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.8, opacity: 0 }}
              className="bg-white rounded-lg p-6 max-w-md w-full mx-4"
              onClick={(e) => e.stopPropagation()}
            >
              <h3 className="text-xl font-semibold text-slate-900 mb-4">Edit Prospect</h3>
              
              <div className="space-y-4">
                <div>
                  <Label htmlFor="edit-name" className="text-slate-700">Name *</Label>
                  <Input
                    id="edit-name"
                    value={formData.name}
                    onChange={(e) => setFormData({...formData, name: e.target.value})}
                    placeholder="Full name"
                    className="mt-1"
                  />
                </div>
                
                <div>
                  <Label htmlFor="edit-email" className="text-slate-700">Email *</Label>
                  <Input
                    id="edit-email"
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                    placeholder="email@example.com"
                    className="mt-1"
                  />
                </div>
                
                <div>
                  <Label htmlFor="edit-phone" className="text-slate-700">Phone *</Label>
                  <Input
                    id="edit-phone"
                    value={formData.phone}
                    onChange={(e) => setFormData({...formData, phone: e.target.value})}
                    placeholder="+1 (555) 123-4567"
                    className="mt-1"
                  />
                </div>
                
                <div>
                  <Label htmlFor="edit-notes" className="text-slate-700">Notes</Label>
                  <textarea
                    id="edit-notes"
                    value={formData.notes}
                    onChange={(e) => setFormData({...formData, notes: e.target.value})}
                    placeholder="Additional notes about this prospect..."
                    className="mt-1 w-full min-h-20 px-3 py-2 border border-slate-300 rounded-md resize-none"
                  />
                </div>
              </div>

              <div className="flex gap-3 mt-6">
                <Button
                  variant="outline"
                  onClick={() => {
                    setShowEditModal(false);
                    setSelectedProspect(null);
                    resetForm();
                  }}
                  className="flex-1"
                >
                  Cancel
                </Button>
                <Button
                  onClick={handleUpdateProspect}
                  className="flex-1 bg-cyan-600 hover:bg-cyan-700"
                >
                  Update Prospect
                </Button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Document Management Modal */}
      <AnimatePresence>
        {showDocumentModal && selectedProspectForDocs && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="bg-white rounded-lg p-6 max-w-4xl w-full max-h-[90vh] overflow-y-auto"
            >
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-xl font-bold text-slate-900">Document Management</h2>
                  <p className="text-slate-600">
                    {selectedProspectForDocs.name} - KYC/AML Documentation
                  </p>
                </div>
                <Button
                  variant="ghost"
                  onClick={() => {
                    setShowDocumentModal(false);
                    setSelectedProspectForDocs(null);
                  }}
                  className="p-2 hover:bg-slate-100 rounded-full"
                  title="Close Modal"
                >
                  <XCircle size={24} className="text-slate-500 hover:text-slate-700" />
                </Button>
              </div>

              {/* Document Types Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
                {Object.entries(KYC_DOCUMENT_TYPES).map(([docType, config]) => {
                  const IconComponent = config.icon;
                  const status = getDocumentStatus(selectedProspectForDocs.id, docType);
                  const isRequired = config.required;
                  
                  return (
                    <Card key={docType} className="relative">
                      <CardContent className="p-4">
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex items-center gap-2">
                            <IconComponent className="h-5 w-5 text-slate-600" />
                            <div>
                              <h3 className="font-medium text-sm text-slate-900">
                                {config.label}
                                {isRequired && <span className="text-red-500 ml-1">*</span>}
                              </h3>
                            </div>
                          </div>
                          
                          {/* Status Badge */}
                          <Badge 
                            className={`text-xs ${
                              status === 'approved' ? 'bg-green-100 text-green-800' :
                              status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                              status === 'rejected' ? 'bg-red-100 text-red-800' :
                              status === 'uploaded' ? 'bg-blue-100 text-blue-800' :
                              'bg-slate-100 text-slate-600'
                            }`}
                          >
                            {status === 'approved' && '✓ Approved'}
                            {status === 'pending' && '⏳ Pending'}
                            {status === 'rejected' && '✗ Rejected'}
                            {status === 'uploaded' && '📄 Uploaded'}
                            {status === 'missing' && '○ Missing'}
                          </Badge>
                        </div>
                        
                        <p className="text-xs text-slate-600 mb-3">{config.description}</p>
                        
                        <div className="flex gap-1">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleRequestDocument(selectedProspectForDocs.id, docType)}
                            className="text-xs flex-1"
                          >
                            <Send size={12} className="mr-1" />
                            Request
                          </Button>
                          
                          {status === 'uploaded' || status === 'pending' ? (
                            <div className="flex gap-1">
                              <Button
                                size="sm"
                                onClick={() => handleVerifyDocument(selectedProspectForDocs.id, docType, 'approved')}
                                className="text-xs bg-green-600 hover:bg-green-700 text-white px-2"
                              >
                                ✓
                              </Button>
                              <Button
                                size="sm"
                                onClick={() => handleVerifyDocument(selectedProspectForDocs.id, docType, 'rejected')}
                                className="text-xs bg-red-600 hover:bg-red-700 text-white px-2"
                              >
                                ✗
                              </Button>
                            </div>
                          ) : null}
                        </div>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>

              {/* Upload New Document */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Upload Document</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="document-type">Document Type</Label>
                      <select
                        id="document-type"
                        value={documentToUpload.type}
                        onChange={(e) => setDocumentToUpload(prev => ({ ...prev, type: e.target.value }))}
                        className="w-full px-3 py-2 border border-slate-300 rounded-md text-sm"
                      >
                        <option value="">Select document type...</option>
                        {Object.entries(KYC_DOCUMENT_TYPES).map(([key, config]) => (
                          <option key={key} value={key}>
                            {config.label} {config.required ? '*' : ''}
                          </option>
                        ))}
                      </select>
                    </div>
                    
                    <div>
                      <Label htmlFor="document-file">Select File</Label>
                      <input
                        id="document-file"
                        type="file"
                        accept=".jpg,.jpeg,.png,.pdf,.doc,.docx,.tiff"
                        onChange={(e) => setDocumentToUpload(prev => ({ ...prev, file: e.target.files[0] }))}
                        className="w-full px-3 py-2 border border-slate-300 rounded-md text-sm"
                      />
                    </div>
                  </div>
                  
                  <div>
                    <Label htmlFor="document-notes">Notes (Optional)</Label>
                    <Input
                      id="document-notes"
                      value={documentToUpload.notes}
                      onChange={(e) => setDocumentToUpload(prev => ({ ...prev, notes: e.target.value }))}
                      placeholder="Additional notes about this document..."
                      className="text-sm"
                    />
                  </div>
                  
                  <Button
                    onClick={handleDocumentUpload}
                    disabled={!documentToUpload.type || !documentToUpload.file || uploadingDocument}
                    className="bg-blue-600 hover:bg-blue-700"
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
                </CardContent>
              </Card>

              {/* Existing Documents List */}
              {prospectDocuments[selectedProspectForDocs.id] && prospectDocuments[selectedProspectForDocs.id].length > 0 && (
                <Card className="mt-6">
                  <CardHeader>
                    <CardTitle className="text-lg">Uploaded Documents</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {(prospectDocuments[selectedProspectForDocs.id] || []).map((doc) => (
                        <div key={doc.id} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                          <div className="flex items-center gap-3">
                            <File className="h-5 w-5 text-slate-600" />
                            <div>
                              <p className="font-medium text-sm text-slate-900">{doc.filename}</p>
                              <p className="text-xs text-slate-600">
                                {KYC_DOCUMENT_TYPES[doc.document_type]?.label || doc.document_type} • 
                                Uploaded {new Date(doc.upload_date).toLocaleDateString()}
                              </p>
                            </div>
                          </div>
                          
                          <div className="flex items-center gap-2">
                            <Badge 
                              className={`text-xs ${
                                doc.verification_status === 'approved' ? 'bg-green-100 text-green-800' :
                                doc.verification_status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                                doc.verification_status === 'rejected' ? 'bg-red-100 text-red-800' :
                                'bg-slate-100 text-slate-600'
                              }`}
                            >
                              {doc.verification_status}
                            </Badge>
                            
                            {doc.verification_status === 'pending' && (
                              <div className="flex gap-1">
                                <Button
                                  size="sm"
                                  onClick={() => handleVerifyDocument(selectedProspectForDocs.id, doc.id, 'approved')}
                                  className="text-xs bg-green-600 hover:bg-green-700 text-white px-2 py-1"
                                >
                                  ✓ Approve
                                </Button>
                                <Button
                                  size="sm"
                                  onClick={() => handleVerifyDocument(selectedProspectForDocs.id, doc.id, 'rejected')}
                                  className="text-xs bg-red-600 hover:bg-red-700 text-white px-2 py-1"
                                >
                                  ✗ Reject
                                </Button>
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
              
              {/* KYC Completion Action - Show when all required documents are approved */}
              {(() => {
                const requiredDocs = Object.entries(KYC_DOCUMENT_TYPES).filter(([key, config]) => config.required);
                const allRequiredApproved = requiredDocs.every(([docType]) => 
                  getDocumentStatus(selectedProspectForDocs.id, docType) === 'approved'
                );
                
                if (allRequiredApproved && requiredDocs.length > 0) {
                  return (
                    <Card className="mt-6 bg-green-50 border-green-200">
                      <CardContent className="p-6">
                        <div className="text-center">
                          <div className="flex items-center justify-center mb-4">
                            <div className="bg-green-100 p-3 rounded-full">
                              <CheckCircle className="h-8 w-8 text-green-600" />
                            </div>
                          </div>
                          <h3 className="text-lg font-semibold text-green-800 mb-2">
                            KYC Documentation Complete!
                          </h3>
                          <p className="text-sm text-green-700 mb-4">
                            All required documents have been approved. You can now proceed with the client conversion process.
                          </p>
                          <div className="flex gap-2 justify-center">
                            <Button
                              onClick={() => {
                                setShowDocumentModal(false);
                                setSelectedProspectForDocs(null);
                                setSuccess("KYC documentation completed successfully! You can now run AML/KYC check and convert to client.");
                              }}
                              className="bg-green-600 hover:bg-green-700"
                            >
                              <CheckCircle size={16} className="mr-2" />
                              Complete KYC Process
                            </Button>
                            <Button
                              variant="outline"
                              onClick={() => {
                                setShowDocumentModal(false);
                                setSelectedProspectForDocs(null);
                              }}
                              className="border-green-300 text-green-700 hover:bg-green-50"
                            >
                              Close
                            </Button>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  );
                }
                return null;
              })()}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Prospect Detail Modal with Google Integration */}
      <AnimatePresence>
        {showDetailModal && selectedProspect && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
            onClick={() => setShowDetailModal(false)}
          >
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.8, opacity: 0 }}
              className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-semibold text-slate-900">
                  {selectedProspect.name} - Prospect Details
                </h3>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowDetailModal(false)}
                  className="text-slate-600 hover:text-slate-900"
                >
                  ✕
                </Button>
              </div>

              {/* Prospect Information */}
              <div className="grid md:grid-cols-2 gap-6 mb-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Contact Information</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex items-center gap-2">
                      <Mail className="h-4 w-4 text-slate-600" />
                      <span className="text-sm">{selectedProspect.email}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Phone className="h-4 w-4 text-slate-600" />
                      <span className="text-sm">{selectedProspect.phone}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <MapPin className="h-4 w-4 text-slate-600" />
                      <span className="text-sm">{selectedProspect.country}</span>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Investment Profile</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div>
                      <span className="text-sm font-medium text-slate-600">Initial Investment:</span>
                      <span className="text-sm ml-2">{selectedProspect.initial_investment || 'Not specified'}</span>
                    </div>
                    <div>
                      <span className="text-sm font-medium text-slate-600">Risk Tolerance:</span>
                      <span className="text-sm ml-2">{selectedProspect.risk_tolerance || 'Not assessed'}</span>
                    </div>
                    <div>
                      <span className="text-sm font-medium text-slate-600">Timeline:</span>
                      <span className="text-sm ml-2">{selectedProspect.investment_timeline || 'Not specified'}</span>
                    </div>
                    <div>
                      <span className="text-sm font-medium text-slate-600">Stage:</span>
                      <Badge className={`ml-2 ${STAGE_CONFIG[selectedProspect.stage]?.color || 'bg-slate-500'} text-white`}>
                        {STAGE_CONFIG[selectedProspect.stage]?.label || selectedProspect.stage}
                      </Badge>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Google API Actions */}
              <Card className="mb-6">
                <CardHeader>
                  <CardTitle className="text-lg">Google API Actions</CardTitle>
                  <p className="text-sm text-slate-600">Integrated Gmail, Calendar, and Drive actions for this prospect</p>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    <Button
                      onClick={() => emailProspectWithType(selectedProspect, 'general')}
                      className="bg-blue-600 hover:bg-blue-700"
                    >
                      <MessageSquare className="h-4 w-4 mr-2" />
                      Send Email
                    </Button>
                    
                    <Button
                      onClick={() => scheduleProspectMeeting(selectedProspect, 'consultation')}
                      className="bg-green-600 hover:bg-green-700"
                    >
                      <Video className="h-4 w-4 mr-2" />
                      Schedule Meet
                    </Button>
                    
                    <Button
                      onClick={() => emailProspectWithType(selectedProspect, 'document_request')}
                      className="bg-orange-600 hover:bg-orange-700"
                    >
                      <FileText className="h-4 w-4 mr-2" />
                      Request Docs
                    </Button>
                    
                    <Button
                      onClick={() => shareInvestmentReport(selectedProspect)}
                      className="bg-purple-600 hover:bg-purple-700"
                    >
                      <Share2 className="h-4 w-4 mr-2" />
                      Share Report
                    </Button>
                  </div>

                  {/* Email Templates */}
                  <div className="mt-4 pt-4 border-t">
                    <h4 className="font-medium text-slate-900 mb-3">Quick Email Templates</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => emailProspectWithType(selectedProspect, 'meeting_followup')}
                        className="text-xs"
                      >
                        Meeting Follow-up
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => scheduleProspectMeeting(selectedProspect, 'followup')}
                        className="text-xs"
                      >
                        Schedule Follow-up
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Notes Section */}
              {selectedProspect.notes && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Notes</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-slate-700">{selectedProspect.notes}</p>
                  </CardContent>
                </Card>
              )}

              {/* Close Button */}
              <div className="flex justify-end mt-6">
                <Button
                  onClick={() => setShowDetailModal(false)}
                  variant="outline"
                  className="px-6"
                >
                  Close
                </Button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Meeting Scheduling Modal */}
      <AnimatePresence>
        {showMeetingModal && selectedProspect && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
            onClick={() => setShowMeetingModal(false)}
          >
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.8, opacity: 0 }}
              className="bg-white rounded-lg p-6 max-w-lg w-full mx-4"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-semibold text-slate-900">
                  Schedule Meeting - {selectedProspect.name}
                </h3>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowMeetingModal(false)}
                  className="text-slate-600 hover:text-slate-900"
                >
                  ✕
                </Button>
              </div>

              <div className="space-y-4">
                {/* Meeting Type */}
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Meeting Type
                  </label>
                  <select
                    value={meetingData.type}
                    onChange={(e) => setMeetingData({ ...meetingData, type: e.target.value })}
                    className="w-full p-2 border border-slate-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="consultation">Initial Consultation</option>
                    <option value="followup">Follow-up Meeting</option>
                    <option value="review">Portfolio Review</option>
                    <option value="onboarding">Client Onboarding</option>
                  </select>
                </div>

                {/* Date and Time */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">
                      Date
                    </label>
                    <input
                      type="date"
                      value={meetingData.date}
                      onChange={(e) => setMeetingData({ ...meetingData, date: e.target.value })}
                      className="w-full p-2 border border-slate-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      min={new Date().toISOString().split('T')[0]}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">
                      Time
                    </label>
                    <input
                      type="time"
                      value={meetingData.time}
                      onChange={(e) => setMeetingData({ ...meetingData, time: e.target.value })}
                      className="w-full p-2 border border-slate-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                </div>

                {/* Duration */}
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Duration (minutes)
                  </label>
                  <select
                    value={meetingData.duration}
                    onChange={(e) => setMeetingData({ ...meetingData, duration: parseInt(e.target.value) })}
                    className="w-full p-2 border border-slate-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value={30}>30 minutes</option>
                    <option value={45}>45 minutes</option>
                    <option value={60}>1 hour</option>
                    <option value={90}>1.5 hours</option>
                    <option value={120}>2 hours</option>
                  </select>
                </div>

                {/* Notes */}
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Meeting Notes
                  </label>
                  <textarea
                    value={meetingData.notes}
                    onChange={(e) => setMeetingData({ ...meetingData, notes: e.target.value })}
                    className="w-full p-2 border border-slate-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    rows="3"
                    placeholder="Add any specific agenda items or notes for this meeting..."
                  />
                </div>

                {/* Prospect Info */}
                <div className="bg-slate-50 p-3 rounded-md">
                  <h4 className="font-medium text-slate-900 mb-2">Meeting with:</h4>
                  <div className="text-sm text-slate-600 space-y-1">
                    <div><strong>Name:</strong> {selectedProspect.name}</div>
                    <div><strong>Email:</strong> {selectedProspect.email}</div>
                    <div><strong>Phone:</strong> {selectedProspect.phone || 'N/A'}</div>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex gap-3 pt-4">
                  <Button
                    onClick={scheduleProspectMeeting}
                    className="flex-1 bg-green-600 hover:bg-green-700"
                    disabled={!meetingData.date || !meetingData.time}
                  >
                    <Calendar className="h-4 w-4 mr-2" />
                    Schedule Meeting
                  </Button>
                  <Button
                    onClick={() => setShowMeetingModal(false)}
                    variant="outline"
                    className="px-6"
                  >
                    Cancel
                  </Button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Email Sending Modal */}
      <AnimatePresence>
        {showEmailModal && selectedProspect && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
            onClick={() => setShowEmailModal(false)}
          >
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.8, opacity: 0 }}
              className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-semibold text-slate-900">
                  Send Email - {selectedProspect.name}
                </h3>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowEmailModal(false)}
                  className="text-slate-600 hover:text-slate-900"
                >
                  ✕
                </Button>
              </div>

              <div className="space-y-4">
                {/* Email Type */}
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Email Type
                  </label>
                  <select
                    value={emailData.type}
                    onChange={(e) => {
                      const newType = e.target.value;
                      setEmailData({ 
                        ...emailData, 
                        type: newType,
                        subject: newType === 'document_request' 
                          ? `Document Request - ${selectedProspect.name}` 
                          : `Investment Opportunity - ${selectedProspect.name}`
                      });
                    }}
                    className="w-full p-2 border border-slate-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="general">General Investment Inquiry</option>
                    <option value="document_request">Document Request</option>
                    <option value="meeting_followup">Meeting Follow-up</option>
                    <option value="portfolio_update">Portfolio Update</option>
                  </select>
                </div>

                {/* Subject */}
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Subject
                  </label>
                  <input
                    type="text"
                    value={emailData.subject}
                    onChange={(e) => setEmailData({ ...emailData, subject: e.target.value })}
                    className="w-full p-2 border border-slate-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Enter email subject"
                  />
                </div>

                {/* Body */}
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Message
                  </label>
                  <textarea
                    value={emailData.body}
                    onChange={(e) => setEmailData({ ...emailData, body: e.target.value })}
                    className="w-full p-2 border border-slate-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    rows="8"
                    placeholder="Enter your message here..."
                  />
                </div>

                {/* Recipient Info */}
                <div className="bg-slate-50 p-3 rounded-md">
                  <h4 className="font-medium text-slate-900 mb-2">Sending to:</h4>
                  <div className="text-sm text-slate-600">
                    <div><strong>Name:</strong> {selectedProspect.name}</div>
                    <div><strong>Email:</strong> {selectedProspect.email}</div>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex gap-3 pt-4">
                  <Button
                    onClick={sendProspectEmail}
                    className="flex-1 bg-blue-600 hover:bg-blue-700"
                    disabled={!emailData.subject || !emailData.body}
                  >
                    <Send className="h-4 w-4 mr-2" />
                    Send Email
                  </Button>
                  <Button
                    onClick={() => setShowEmailModal(false)}
                    variant="outline"
                    className="px-6"
                  >
                    Cancel
                  </Button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default ProspectManagement;