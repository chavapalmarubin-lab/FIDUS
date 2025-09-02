import React, { useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Alert, AlertDescription } from "./ui/alert";
import { Progress } from "./ui/progress";
import { Badge } from "./ui/badge";
import { 
  Upload, 
  FileText, 
  CheckCircle, 
  AlertCircle, 
  Loader2, 
  Eye, 
  EyeOff,
  ArrowLeft,
  User,
  CreditCard,
  Shield,
  Mail,
  Phone,
  Camera
} from "lucide-react";
import axios from "axios";
import CameraCapture from "./CameraCapture";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const REGISTRATION_STEPS = {
  PERSONAL_INFO: "personal_info",
  DOCUMENT_UPLOAD: "document_upload",
  DOCUMENT_PROCESSING: "document_processing", 
  AML_KYC_CHECK: "aml_kyc_check",
  REVIEW: "review",
  COMPLETE: "complete"
};

const UserRegistration = ({ onBack, onComplete }) => {
  const [currentStep, setCurrentStep] = useState(REGISTRATION_STEPS.PERSONAL_INFO);
  const [registrationData, setRegistrationData] = useState({
    firstName: "",
    lastName: "",
    email: "",
    phone: "",
    dateOfBirth: "",
    nationality: "",
    address: "",
    city: "",
    postalCode: "",
    country: ""
  });
  const [documentFile, setDocumentFile] = useState(null);
  const [documentType, setDocumentType] = useState("");
  const [documentPreview, setDocumentPreview] = useState(null);
  const [extractedData, setExtractedData] = useState(null);
  const [amlKycResults, setAmlKycResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [progress, setProgress] = useState(0);
  const [applicationId, setApplicationId] = useState(null);
  
  const fileInputRef = useRef(null);

  const handlePersonalInfoSubmit = () => {
    // Validate required fields
    const requiredFields = ["firstName", "lastName", "email", "phone", "dateOfBirth"];
    const missingFields = requiredFields.filter(field => !registrationData[field]);
    
    if (missingFields.length > 0) {
      setError(`Please fill in all required fields: ${missingFields.join(", ")}`);
      return;
    }

    setError("");
    setCurrentStep(REGISTRATION_STEPS.DOCUMENT_UPLOAD);
  };

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Validate file type
    const allowedTypes = ["image/jpeg", "image/jpg", "image/png", "image/webp"];
    if (!allowedTypes.includes(file.type)) {
      setError("Please upload a valid image file (JPEG, PNG, or WebP)");
      return;
    }

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      setError("File size must be less than 10MB");
      return;
    }

    setDocumentFile(file);
    setError("");

    // Create preview
    const reader = new FileReader();
    reader.onload = (e) => {
      setDocumentPreview(e.target.result);
    };
    reader.readAsDataURL(file);
  };

  const handleDocumentSubmit = async () => {
    if (!documentFile || !documentType) {
      setError("Please select a document type and upload your ID document");
      return;
    }

    setLoading(true);
    setError("");
    setCurrentStep(REGISTRATION_STEPS.DOCUMENT_PROCESSING);
    setProgress(20);

    try {
      // Create application
      const applicationResponse = await axios.post(`${API}/registration/create-application`, {
        personalInfo: registrationData,
        documentType: documentType
      });
      
      setApplicationId(applicationResponse.data.applicationId);
      setProgress(40);

      // Upload and process document
      const formData = new FormData();
      formData.append("document", documentFile);
      formData.append("documentType", documentType);
      formData.append("applicationId", applicationResponse.data.applicationId);

      const uploadResponse = await axios.post(`${API}/registration/process-document`, formData, {
        headers: {
          "Content-Type": "multipart/form-data"
        }
      });

      setExtractedData(uploadResponse.data.extractedData);
      setProgress(60);

      // Proceed to AML/KYC check
      setCurrentStep(REGISTRATION_STEPS.AML_KYC_CHECK);
      await performAmlKycCheck(applicationResponse.data.applicationId);

    } catch (err) {
      setError(err.response?.data?.detail || "Document processing failed. Please try again.");
      setCurrentStep(REGISTRATION_STEPS.DOCUMENT_UPLOAD);
    } finally {
      setLoading(false);
    }
  };

  const performAmlKycCheck = async (appId) => {
    setProgress(70);
    
    try {
      const amlResponse = await axios.post(`${API}/registration/aml-kyc-check`, {
        applicationId: appId,
        personalInfo: registrationData,
        extractedData: extractedData
      });

      setAmlKycResults(amlResponse.data);
      setProgress(90);

      // Move to review step
      setTimeout(() => {
        setCurrentStep(REGISTRATION_STEPS.REVIEW);
        setProgress(100);
      }, 2000);

    } catch (err) {
      setError(err.response?.data?.detail || "AML/KYC verification failed. Please contact support.");
      setCurrentStep(REGISTRATION_STEPS.REVIEW);
    }
  };

  const handleFinalSubmit = async () => {
    setLoading(true);
    
    try {
      const response = await axios.post(`${API}/registration/finalize`, {
        applicationId: applicationId,
        approved: true
      });

      setCurrentStep(REGISTRATION_STEPS.COMPLETE);
      
      // Auto-complete after showing success message
      setTimeout(() => {
        onComplete(response.data);
      }, 3000);

    } catch (err) {
      setError(err.response?.data?.detail || "Application finalization failed");
    } finally {
      setLoading(false);
    }
  };

  const getStepProgress = () => {
    const steps = Object.values(REGISTRATION_STEPS);
    const currentIndex = steps.indexOf(currentStep);
    return Math.round(((currentIndex + 1) / steps.length) * 100);
  };

  const renderPersonalInfoStep = () => (
    <motion.div
      initial={{ opacity: 0, x: 50 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-4"
    >
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <Label htmlFor="firstName" className="text-slate-300">First Name *</Label>
          <Input
            id="firstName"
            value={registrationData.firstName}
            onChange={(e) => setRegistrationData({...registrationData, firstName: e.target.value})}
            className="bg-slate-800 border-slate-600 text-white"
            placeholder="Enter your first name"
          />
        </div>
        <div>
          <Label htmlFor="lastName" className="text-slate-300">Last Name *</Label>
          <Input
            id="lastName"
            value={registrationData.lastName}
            onChange={(e) => setRegistrationData({...registrationData, lastName: e.target.value})}
            className="bg-slate-800 border-slate-600 text-white"
            placeholder="Enter your last name"
          />
        </div>
      </div>

      <div>
        <Label htmlFor="email" className="text-slate-300">Email Address *</Label>
        <Input
          id="email"
          type="email"
          value={registrationData.email}
          onChange={(e) => setRegistrationData({...registrationData, email: e.target.value})}
          className="bg-slate-800 border-slate-600 text-white"
          placeholder="Enter your email address"
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <Label htmlFor="phone" className="text-slate-300">Phone Number *</Label>
          <Input
            id="phone"
            value={registrationData.phone}
            onChange={(e) => setRegistrationData({...registrationData, phone: e.target.value})}
            className="bg-slate-800 border-slate-600 text-white"
            placeholder="+1 (555) 123-4567"
          />
        </div>
        <div>
          <Label htmlFor="dateOfBirth" className="text-slate-300">Date of Birth *</Label>
          <Input
            id="dateOfBirth"
            type="date"
            value={registrationData.dateOfBirth}
            onChange={(e) => setRegistrationData({...registrationData, dateOfBirth: e.target.value})}
            className="bg-slate-800 border-slate-600 text-white"
          />
        </div>
      </div>

      <div>
        <Label htmlFor="address" className="text-slate-300">Address</Label>
        <Input
          id="address"
          value={registrationData.address}
          onChange={(e) => setRegistrationData({...registrationData, address: e.target.value})}
          className="bg-slate-800 border-slate-600 text-white"
          placeholder="Enter your full address"
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <Label htmlFor="city" className="text-slate-300">City</Label>
          <Input
            id="city"
            value={registrationData.city}
            onChange={(e) => setRegistrationData({...registrationData, city: e.target.value})}
            className="bg-slate-800 border-slate-600 text-white"
            placeholder="City"
          />
        </div>
        <div>
          <Label htmlFor="postalCode" className="text-slate-300">Postal Code</Label>
          <Input
            id="postalCode"
            value={registrationData.postalCode}
            onChange={(e) => setRegistrationData({...registrationData, postalCode: e.target.value})}
            className="bg-slate-800 border-slate-600 text-white"
            placeholder="12345"
          />
        </div>
        <div>
          <Label htmlFor="country" className="text-slate-300">Country</Label>
          <Input
            id="country"
            value={registrationData.country}
            onChange={(e) => setRegistrationData({...registrationData, country: e.target.value})}
            className="bg-slate-800 border-slate-600 text-white"
            placeholder="United States"
          />
        </div>
      </div>

      <div className="flex gap-3 mt-6">
        <Button variant="outline" onClick={onBack} className="flex-1">
          <ArrowLeft size={16} className="mr-2" />
          Back
        </Button>
        <Button onClick={handlePersonalInfoSubmit} className="flex-1 bg-cyan-600 hover:bg-cyan-700">
          Continue
        </Button>
      </div>
    </motion.div>
  );

  const renderDocumentUploadStep = () => (
    <motion.div
      initial={{ opacity: 0, x: 50 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-6"
    >
      <div>
        <Label className="text-slate-300 mb-3 block">Document Type *</Label>
        <Select value={documentType} onValueChange={setDocumentType}>
          <SelectTrigger className="bg-slate-800 border-slate-600 text-white">
            <SelectValue placeholder="Select your ID document type" />
          </SelectTrigger>
          <SelectContent className="bg-slate-800 border-slate-600">
            <SelectItem value="passport" className="text-white">Passport</SelectItem>
            <SelectItem value="drivers_license" className="text-white">Driver's License</SelectItem>
            <SelectItem value="national_id" className="text-white">National ID Card</SelectItem>
            <SelectItem value="state_id" className="text-white">State ID Card</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div>
        <Label className="text-slate-300 mb-3 block">Upload ID Document *</Label>
        <div 
          className="border-2 border-dashed border-slate-600 rounded-lg p-8 text-center hover:border-cyan-400 transition-colors cursor-pointer"
          onClick={() => fileInputRef.current?.click()}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleFileUpload}
            className="hidden"
          />
          
          {documentPreview ? (
            <div className="space-y-4">
              <img 
                src={documentPreview} 
                alt="Document preview" 
                className="max-h-64 mx-auto rounded-lg shadow-lg"
              />
              <div className="text-slate-300">
                <CheckCircle className="inline mr-2" size={20} />
                Document uploaded successfully
              </div>
              <Button variant="outline" size="sm" onClick={() => fileInputRef.current?.click()}>
                Choose Different File
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              <Upload className="mx-auto text-slate-400" size={48} />
              <div>
                <div className="text-slate-300 text-lg">Click to upload your ID document</div>
                <div className="text-slate-500 text-sm mt-2">
                  Supported formats: JPEG, PNG, WebP (max 10MB)
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      <Alert className="bg-slate-800 border-slate-600">
        <Shield className="h-4 w-4" />
        <AlertDescription className="text-slate-300">
          Your document will be securely processed using advanced OCR and verified through our AML/KYC system. 
          All data is encrypted and handled in compliance with financial regulations.
        </AlertDescription>
      </Alert>

      <div className="flex gap-3">
        <Button 
          variant="outline" 
          onClick={() => setCurrentStep(REGISTRATION_STEPS.PERSONAL_INFO)} 
          className="flex-1"
        >
          <ArrowLeft size={16} className="mr-2" />
          Back
        </Button>
        <Button 
          onClick={handleDocumentSubmit} 
          disabled={!documentFile || !documentType}
          className="flex-1 bg-cyan-600 hover:bg-cyan-700"
        >
          Process Document
        </Button>
      </div>
    </motion.div>
  );

  const renderProcessingStep = () => (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="text-center space-y-6 py-8"
    >
      <div className="relative">
        <div className="w-24 h-24 mx-auto rounded-full bg-slate-800 flex items-center justify-center mb-6">
          <Loader2 className="w-12 h-12 text-cyan-400 animate-spin" />
        </div>
      </div>
      
      <div>
        <h3 className="text-xl font-semibold text-white mb-2">Processing Your Application</h3>
        <p className="text-slate-400">
          {currentStep === REGISTRATION_STEPS.DOCUMENT_PROCESSING && 
            "Using advanced OCR technology to extract data from your document..."
          }
          {currentStep === REGISTRATION_STEPS.AML_KYC_CHECK && 
            "Performing comprehensive AML/KYC verification including sanctions screening..."
          }
        </p>
      </div>

      <div className="space-y-3">
        <Progress value={progress} className="w-full" />
        <div className="text-sm text-slate-400">
          {progress < 40 && "Creating secure application..."}
          {progress >= 40 && progress < 60 && "Real-time OCR document analysis..."}
          {progress >= 60 && progress < 80 && "AML sanctions screening in progress..."}
          {progress >= 80 && progress < 90 && "Identity verification checks..."}
          {progress >= 90 && "Finalizing compliance verification..."}
        </div>
      </div>

      {/* Processing Details */}
      <div className="bg-slate-800/50 rounded-lg p-4 text-left text-xs text-slate-400">
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${progress >= 40 ? 'bg-green-400' : 'bg-slate-600'}`} />
            <span>Document Processing: {progress >= 60 ? 'Complete' : 'In Progress'}</span>
          </div>
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${progress >= 80 ? 'bg-green-400' : progress >= 60 ? 'bg-yellow-400' : 'bg-slate-600'}`} />
            <span>AML/KYC Verification: {progress >= 90 ? 'Complete' : progress >= 60 ? 'In Progress' : 'Pending'}</span>
          </div>
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${progress >= 90 ? 'bg-green-400' : 'bg-slate-600'}`} />
            <span>Identity Verification: {progress >= 95 ? 'Complete' : progress >= 80 ? 'In Progress' : 'Pending'}</span>
          </div>
        </div>
      </div>

      <div className="text-xs text-slate-500">
        {currentStep === REGISTRATION_STEPS.DOCUMENT_PROCESSING && 
          "Using Tesseract OCR and Google Cloud Vision for maximum accuracy"
        }
        {currentStep === REGISTRATION_STEPS.AML_KYC_CHECK && 
          "Screening against OFAC, UN, and EU sanctions lists"
        }
      </div>
    </motion.div>
  );

  const renderReviewStep = () => (
    <motion.div
      initial={{ opacity: 0, x: 50 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-6"
    >
      <div className="text-center mb-6">
        <CheckCircle className="w-16 h-16 text-green-400 mx-auto mb-4" />
        <h3 className="text-xl font-semibold text-white">Verification Complete</h3>
        <p className="text-slate-400">Please review your information before finalizing</p>
      </div>

      {extractedData && (
        <Card className="bg-slate-800 border-slate-600">
          <CardHeader>
            <CardTitle className="text-white text-lg flex items-center gap-2">
              <FileText size={20} />
              Document Analysis Results
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* OCR Quality Metrics */}
            <div className="bg-slate-700/50 rounded-lg p-3">
              <div className="text-sm text-slate-300 mb-2">Processing Quality</div>
              <div className="grid grid-cols-2 gap-4 text-xs">
                <div>
                  <span className="text-slate-400">OCR Method:</span>
                  <span className="text-cyan-400 ml-2 font-medium">
                    {extractedData.ocrMethod === 'google_vision' ? 'Google Cloud Vision' : 'Tesseract OCR'}
                  </span>
                </div>
                <div>
                  <span className="text-slate-400">Confidence:</span>
                  <span className={`ml-2 font-medium ${
                    extractedData.confidenceScore >= 0.8 ? 'text-green-400' : 
                    extractedData.confidenceScore >= 0.6 ? 'text-yellow-400' : 'text-red-400'
                  }`}>
                    {Math.round((extractedData.confidenceScore || 0) * 100)}%
                  </span>
                </div>
                <div>
                  <span className="text-slate-400">Fields Extracted:</span>
                  <span className="text-white ml-2 font-medium">{extractedData.fieldsExtracted || 0}</span>
                </div>
                <div>
                  <span className="text-slate-400">Document Type:</span>
                  <span className="text-white ml-2 font-medium capitalize">{documentType.replace('_', ' ')}</span>
                </div>
              </div>
            </div>

            {/* Extracted Data */}
            {extractedData.structured_data && Object.keys(extractedData.structured_data).length > 0 && (
              <div>
                <div className="text-sm text-slate-300 mb-3">Extracted Information</div>
                <div className="space-y-2">
                  {Object.entries(extractedData.structured_data).map(([key, value]) => (
                    <div key={key} className="flex justify-between items-center py-1">
                      <span className="text-slate-400 capitalize text-sm">{key.replace(/_/g, ' ')}:</span>
                      <span className="text-white font-medium text-sm">{value || 'Not detected'}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {amlKycResults && (
        <Card className="bg-slate-800 border-slate-600">
          <CardHeader>
            <CardTitle className="text-white text-lg flex items-center gap-2">
              <Shield size={20} />
              AML/KYC Compliance Verification
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Overall Status */}
            <div className="bg-slate-700/50 rounded-lg p-3">
              <div className="flex justify-between items-center mb-3">
                <span className="text-slate-300 font-medium">Overall Status:</span>
                <Badge variant={
                  amlKycResults.overall_status === 'approved' ? 'default' : 
                  amlKycResults.overall_status === 'enhanced_monitoring' ? 'secondary' :
                  amlKycResults.overall_status === 'manual_review_required' ? 'outline' : 'destructive'
                }>
                  {amlKycResults.overall_status?.toUpperCase().replace('_', ' ')}
                </Badge>
              </div>
              
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-slate-400">Risk Level:</span>
                  <span className={`ml-2 font-medium ${
                    amlKycResults.risk_level === 'LOW' ? 'text-green-400' :
                    amlKycResults.risk_level === 'MEDIUM' ? 'text-yellow-400' : 'text-red-400'
                  }`}>
                    {amlKycResults.risk_level}
                  </span>
                </div>
                <div>
                  <span className="text-slate-400">Risk Score:</span>
                  <span className="text-white ml-2 font-medium">{amlKycResults.total_score || 0}/100</span>
                </div>
              </div>
            </div>

            {/* Verification Checks */}
            <div>
              <div className="text-sm text-slate-300 mb-3">Compliance Checks Completed</div>
              <div className="space-y-2">
                {amlKycResults.checks_completed?.map((check, index) => (
                  <div key={index} className="flex items-center gap-2 text-sm">
                    <CheckCircle size={16} className="text-green-400" />
                    <span className="text-slate-300 capitalize">{check.replace('_', ' ')}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Sanctions Screening */}
            {amlKycResults.sanctions_screening && (
              <div>
                <div className="text-sm text-slate-300 mb-2">Sanctions Screening</div>
                <div className="bg-slate-700/30 rounded p-2 text-xs">
                  <div className="flex justify-between mb-1">
                    <span className="text-slate-400">Provider:</span>
                    <span className="text-cyan-400">{amlKycResults.sanctions_screening.provider}</span>
                  </div>
                  <div className="flex justify-between mb-1">
                    <span className="text-slate-400">Total Hits:</span>
                    <span className="text-white">{amlKycResults.sanctions_screening.total_hits || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Status:</span>
                    <span className={`${
                      amlKycResults.sanctions_screening.total_hits === 0 ? 'text-green-400' : 'text-yellow-400'
                    }`}>
                      {amlKycResults.sanctions_screening.total_hits === 0 ? '✓ Clear' : '⚠ Matches Found'}
                    </span>
                  </div>
                </div>
              </div>
            )}

            {/* Identity Verification */}
            {amlKycResults.identity_verification && (
              <div>
                <div className="text-sm text-slate-300 mb-2">Identity Verification</div>
                <div className="bg-slate-700/30 rounded p-2 text-xs">
                  <div className="flex justify-between mb-1">
                    <span className="text-slate-400">Status:</span>
                    <span className={`${
                      amlKycResults.identity_verification.identity_verified ? 'text-green-400' : 'text-red-400'
                    }`}>
                      {amlKycResults.identity_verification.identity_verified ? '✓ Verified' : '✗ Failed'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Verification Score:</span>
                    <span className="text-white">
                      {Math.round((amlKycResults.identity_verification.verification_score || 0) * 100)}%
                    </span>
                  </div>
                </div>
              </div>
            )}

            {/* Next Steps */}
            {amlKycResults.next_steps && amlKycResults.next_steps.length > 0 && (
              <div>
                <div className="text-sm text-slate-300 mb-2">Next Steps</div>
                <div className="space-y-1">
                  {amlKycResults.next_steps.map((step, index) => (
                    <div key={index} className="flex items-start gap-2 text-xs text-slate-400">
                      <div className="w-1 h-1 rounded-full bg-cyan-400 mt-2 flex-shrink-0" />
                      <span>{step}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      <div className="flex gap-3">
        <Button variant="outline" className="flex-1" disabled={loading}>
          Contact Support
        </Button>
        <Button 
          onClick={handleFinalSubmit} 
          disabled={loading}
          className="flex-1 bg-green-600 hover:bg-green-700"
        >
          {loading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Finalizing...
            </>
          ) : (
            "Complete Registration"
          )}
        </Button>
      </div>
    </motion.div>
  );

  const renderCompleteStep = () => (
    <motion.div
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
      className="text-center space-y-6 py-8"
    >
      <div className="w-24 h-24 mx-auto rounded-full bg-green-600 flex items-center justify-center mb-6">
        <CheckCircle className="w-12 h-12 text-white" />
      </div>
      
      <div>
        <h3 className="text-2xl font-bold text-white mb-2">Registration Complete!</h3>
        <p className="text-slate-400 mb-4">
          Your account has been successfully created and verified.
        </p>
        <div className="bg-slate-800 rounded-lg p-4 text-left">
          <p className="text-slate-300 text-sm">
            <Mail className="inline mr-2" size={16} />
            Login credentials have been sent to: <strong className="text-cyan-400">{registrationData.email}</strong>
          </p>
        </div>
      </div>

      <div className="text-slate-400 text-sm">
        Redirecting to login page in a few seconds...
      </div>
    </motion.div>
  );

  return (
    <div className="login-selection">
      <motion.div
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
      >
        <Card className="login-card max-w-2xl">
          <CardHeader className="text-center">
            <motion.div
              className="mb-4"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.3, duration: 0.8 }}
            >
              <img 
                src="https://customer-assets.emergentagent.com/job_fidus-portal/artifacts/hxt31ed0_FIDUS%20LOGO%20SMALL.jpg"
                alt="FIDUS Logo"
                style={{
                  width: "150px",
                  height: "auto",
                  margin: "0 auto",
                  display: "block",
                  filter: "drop-shadow(0 0 15px rgba(255, 167, 38, 0.3))"
                }}
              />
            </motion.div>
            <CardTitle className="text-2xl text-white">
              Create Your FIDUS Account
            </CardTitle>
            <p className="text-slate-400 mt-2">
              Complete registration with secure document verification
            </p>
            
            {/* Progress Indicator */}
            {currentStep !== REGISTRATION_STEPS.COMPLETE && (
              <div className="mt-4">
                <Progress value={getStepProgress()} className="w-full" />
                <div className="text-xs text-slate-500 mt-2">
                  Step {Object.values(REGISTRATION_STEPS).indexOf(currentStep) + 1} of {Object.values(REGISTRATION_STEPS).length}
                </div>
              </div>
            )}
          </CardHeader>

          <CardContent>
            {error && (
              <Alert className="mb-4 bg-red-900/20 border-red-600">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription className="text-red-400">
                  {error}
                </AlertDescription>
              </Alert>
            )}

            <AnimatePresence mode="wait">
              {currentStep === REGISTRATION_STEPS.PERSONAL_INFO && renderPersonalInfoStep()}
              {currentStep === REGISTRATION_STEPS.DOCUMENT_UPLOAD && renderDocumentUploadStep()}
              {(currentStep === REGISTRATION_STEPS.DOCUMENT_PROCESSING || currentStep === REGISTRATION_STEPS.AML_KYC_CHECK) && renderProcessingStep()}
              {currentStep === REGISTRATION_STEPS.REVIEW && renderReviewStep()}
              {currentStep === REGISTRATION_STEPS.COMPLETE && renderCompleteStep()}
            </AnimatePresence>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
};

export default UserRegistration;