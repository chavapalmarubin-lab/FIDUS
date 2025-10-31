import React, { useState, useRef, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Alert, AlertDescription } from "./ui/alert";
import { Badge } from "./ui/badge";
import { Progress } from "./ui/progress";
import { 
  Camera, 
  Upload, 
  FileText, 
  User, 
  Calendar, 
  MapPin, 
  Phone, 
  Mail,
  Shield,
  CheckCircle,
  AlertCircle,
  Loader2,
  ArrowRight,
  ArrowLeft,
  Eye,
  EyeOff,
  Scan
} from "lucide-react";
import axios from "axios";

const ClientOnboarding = ({ onBack, onComplete }) => {
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  
  // Document capture state
  const [documentImage, setDocumentImage] = useState(null);
  const [documentPreview, setDocumentPreview] = useState(null);
  const [documentProcessing, setDocumentProcessing] = useState(false);
  const [ocrResult, setOcrResult] = useState(null);
  
  // Extracted data state
  const [extractedData, setExtractedData] = useState({
    full_name: "",
    first_name: "",
    last_name: "",
    date_of_birth: "",
    document_number: "",
    nationality: "",
    document_type: "",
    place_of_birth: "",
    sex: ""
  });
  
  // Client registration data
  const [clientData, setClientData] = useState({
    email: "",
    phone: "",
    address: "",
    password: "",
    confirmPassword: "",
    terms_accepted: false,
    privacy_accepted: false
  });
  
  // KYC/AML status
  const [kycStatus, setKycStatus] = useState({
    document_verified: false,
    identity_verified: false,
    ofac_cleared: false,
    aml_status: "pending",
    overall_status: "incomplete"
  });
  
  const fileInputRef = useRef(null);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [showCamera, setShowCamera] = useState(false);
  const [stream, setStream] = useState(null);
  
  const backendUrl = process.env.REACT_APP_BACKEND_URL;
  
  // Step navigation
  const steps = [
    { number: 1, title: "Document Upload", description: "Capture or upload your ID document" },
    { number: 2, title: "Verify Information", description: "Review and confirm extracted data" },
    { number: 3, title: "Personal Details", description: "Complete your profile information" },
    { number: 4, title: "Account Setup", description: "Create your login credentials" },
    { number: 5, title: "KYC Verification", description: "Complete compliance verification" }
  ];
  
  const currentStepInfo = steps.find(step => step.number === currentStep);
  const progress = (currentStep / steps.length) * 100;
  
  // Camera functions
  const startCamera = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({ 
        video: { facingMode: 'environment' } // Use back camera if available
      });
      setStream(mediaStream);
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
      }
      setShowCamera(true);
      setError("");
    } catch (err) {
      setError("Unable to access camera. Please use file upload instead.");
    }
  };
  
  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
    setShowCamera(false);
  };
  
  const capturePhoto = () => {
    if (videoRef.current && canvasRef.current) {
      const canvas = canvasRef.current;
      const video = videoRef.current;
      
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      
      const ctx = canvas.getContext('2d');
      ctx.drawImage(video, 0, 0);
      
      canvas.toBlob((blob) => {
        const file = new File([blob], 'captured-document.jpg', { type: 'image/jpeg' });
        handleDocumentCapture(file);
        stopCamera();
      }, 'image/jpeg', 0.8);
    }
  };
  
  // File handling
  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      handleDocumentCapture(file);
    }
  };
  
  const handleDocumentCapture = async (file) => {
    if (!file) return;
    
    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/tiff'];
    if (!allowedTypes.includes(file.type)) {
      setError("Please upload a valid image file (JPEG, PNG, or TIFF)");
      return;
    }
    
    // Validate file size (10MB max)
    if (file.size > 10 * 1024 * 1024) {
      setError("File size must be less than 10MB");
      return;
    }
    
    setDocumentImage(file);
    
    // Create preview
    const reader = new FileReader();
    reader.onload = (e) => {
      setDocumentPreview(e.target.result);
    };
    reader.readAsDataURL(file);
    
    // Process document with OCR
    await processDocument(file);
  };
  
  const processDocument = async (file) => {
    setDocumentProcessing(true);
    setError("");
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('document_type', 'auto_detect');
      
      const response = await axios.post(`${backendUrl}/api/ocr/extract/sync`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 30000
      });
      
      if (response.data) {
        setOcrResult(response.data);
        
        // Extract key fields from parsed document
        const parsedDoc = response.data.parsed_document;
        if (parsedDoc && parsedDoc.fields) {
          const fields = parsedDoc.fields;
          
          setExtractedData({
            full_name: fields.full_name || fields.surname || "",
            first_name: fields.given_names || fields.first_name || "",
            last_name: fields.surname || fields.last_name || "",
            date_of_birth: fields.date_of_birth || "",
            document_number: fields.document_number || fields.passport_number || fields.license_number || fields.id_number || "",
            nationality: fields.nationality || "",
            document_type: parsedDoc.document_type || "unknown",
            place_of_birth: fields.place_of_birth || "",
            sex: fields.sex || ""
          });
          
          setKycStatus(prev => ({
            ...prev,
            document_verified: true
          }));
          
          setSuccess("Document processed successfully! Please review the extracted information.");
        } else {
          setError("Could not extract data from document. Please ensure the image is clear and try again.");
        }
      }
    } catch (err) {
      console.error("OCR processing error:", err);
      setError("Failed to process document. Please try again or use a different image.");
    } finally {
      setDocumentProcessing(false);
    }
  };
  
  // Handle extracted data updates
  const handleExtractedDataChange = (field, value) => {
    setExtractedData(prev => ({
      ...prev,
      [field]: value
    }));
  };
  
  // Handle client data updates
  const handleClientDataChange = (field, value) => {
    setClientData(prev => ({
      ...prev,
      [field]: value
    }));
  };
  
  // Step validation
  const validateCurrentStep = () => {
    switch (currentStep) {
      case 1:
        return documentImage && ocrResult;
      case 2:
        return extractedData.full_name && extractedData.date_of_birth;
      case 3:
        return clientData.email && clientData.phone && clientData.address;
      case 4:
        return clientData.password && clientData.confirmPassword && 
               clientData.password === clientData.confirmPassword &&
               clientData.terms_accepted && clientData.privacy_accepted;
      case 5:
        return kycStatus.overall_status === "approved";
      default:
        return true;
    }
  };
  
  // Navigation
  const nextStep = () => {
    if (validateCurrentStep() && currentStep < steps.length) {
      setCurrentStep(currentStep + 1);
      setError("");
      
      // Trigger KYC verification when moving to step 5
      if (currentStep === 4) {
        performKYCVerification();
      }
    } else {
      setError("Please complete all required fields before continuing.");
    }
  };
  
  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
      setError("");
    }
  };
  
  // KYC/AML verification
  const performKYCVerification = async () => {
    setLoading(true);
    setError("");
    
    try {
      // Step 1: Identity verification with extracted document data
      const identityResponse = await axios.post(`${backendUrl}/api/identity/verify/document`, {
        document_data: {
          ...extractedData,
          document_type: extractedData.document_type
        },
        verification_level: "comprehensive"
      });
      
      if (identityResponse.data.identity_verification.overall_status === "verified") {
        setKycStatus(prev => ({
          ...prev,
          identity_verified: true
        }));
      }
      
      // Step 2: OFAC screening
      const ofacResponse = await axios.post(`${backendUrl}/api/compliance/screen`, {
        customer_info: {
          full_name: extractedData.full_name,
          first_name: extractedData.first_name,
          last_name: extractedData.last_name,
          date_of_birth: extractedData.date_of_birth,
          nationality: extractedData.nationality,
          document_number: extractedData.document_number
        },
        screening_sources: ["sdn", "nonsdn", "eu", "un"]
      });
      
      if (ofacResponse.data.screening_status === "clear") {
        setKycStatus(prev => ({
          ...prev,
          ofac_cleared: true
        }));
      }
      
      // Step 3: Overall AML assessment
      const overall_approved = kycStatus.document_verified && 
                              identityResponse.data.identity_verification.overall_status === "verified" &&
                              ofacResponse.data.screening_status === "clear";
      
      setKycStatus(prev => ({
        ...prev,
        aml_status: overall_approved ? "approved" : "review_required",
        overall_status: overall_approved ? "approved" : "review_required"
      }));
      
      if (overall_approved) {
        setSuccess("KYC/AML verification completed successfully!");
      } else {
        setError("Your application requires manual review. Our compliance team will contact you within 24 hours.");
      }
      
    } catch (err) {
      console.error("KYC verification error:", err);
      setError("KYC verification failed. Please contact support.");
      setKycStatus(prev => ({
        ...prev,
        aml_status: "failed",
        overall_status: "failed"
      }));
    } finally {
      setLoading(false);
    }
  };
  
  // Complete registration
  const completeRegistration = async () => {
    setLoading(true);
    setError("");
    
    try {
      const registrationData = {
        // Extracted document data
        ...extractedData,
        // Client provided data
        ...clientData,
        // KYC status
        kyc_status: kycStatus,
        // OCR result
        document_processing_result: ocrResult,
        // Registration metadata
        registration_method: "document_upload",
        onboarding_completed: true
      };
      
      const response = await axios.post(`${backendUrl}/api/auth/register`, registrationData);
      
      if (response.data.success) {
        setSuccess("Account created successfully! Welcome to FIDUS.");
        
        // Complete onboarding
        setTimeout(() => {
          onComplete({
            user_id: response.data.user_id,
            username: response.data.username,
            name: extractedData.full_name,
            type: "client",
            kyc_status: kycStatus.overall_status
          });
        }, 2000);
      }
    } catch (err) {
      console.error("Registration error:", err);
      setError(err.response?.data?.detail || "Registration failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };
  
  // Render current step content
  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="space-y-6">
            <div className="text-center">
              <Scan className="mx-auto h-12 w-12 text-cyan-400 mb-4" />
              <h3 className="text-xl font-semibold text-white mb-2">Upload Your ID Document</h3>
              <p className="text-slate-400">
                Take a photo or upload an image of your passport, driver's license, or national ID
              </p>
            </div>
            
            {!documentPreview ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Button
                  onClick={startCamera}
                  className="h-32 bg-slate-700 hover:bg-slate-600 border-2 border-dashed border-slate-500 text-slate-300"
                  disabled={documentProcessing}
                >
                  <div className="text-center">
                    <Camera className="mx-auto h-8 w-8 mb-2" />
                    <div>Take Photo</div>
                    <div className="text-sm opacity-75">Use camera</div>
                  </div>
                </Button>
                
                <Button
                  onClick={() => fileInputRef.current?.click()}
                  className="h-32 bg-slate-700 hover:bg-slate-600 border-2 border-dashed border-slate-500 text-slate-300"
                  disabled={documentProcessing}
                >
                  <div className="text-center">
                    <Upload className="mx-auto h-8 w-8 mb-2" />
                    <div>Upload File</div>
                    <div className="text-sm opacity-75">Choose from device</div>
                  </div>
                </Button>
                
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleFileUpload}
                  className="hidden"
                />
              </div>
            ) : (
              <div className="space-y-4">
                <div className="relative">
                  <img
                    src={documentPreview}
                    alt="Document preview"
                    className="w-full max-w-md mx-auto rounded-lg border border-slate-600"
                  />
                  {documentProcessing && (
                    <div className="absolute inset-0 bg-black bg-opacity-75 flex items-center justify-center rounded-lg">
                      <div className="text-center text-white">
                        <Loader2 className="mx-auto h-8 w-8 animate-spin mb-2" />
                        <div>Processing document...</div>
                        <div className="text-sm opacity-75">Extracting information</div>
                      </div>
                    </div>
                  )}
                </div>
                
                {ocrResult && (
                  <div className="bg-green-900/20 border border-green-600/30 rounded-lg p-4">
                    <div className="flex items-center text-green-400 mb-2">
                      <CheckCircle className="h-5 w-5 mr-2" />
                      Document Processed Successfully
                    </div>
                    <div className="text-sm text-slate-300">
                      <div>Document Type: <span className="text-cyan-400">{ocrResult.parsed_document?.document_type || "Auto-detected"}</span></div>
                      <div>Confidence: <span className="text-cyan-400">{Math.round(ocrResult.ocr_results?.confidence || 0)}%</span></div>
                      <div>Processing Time: <span className="text-cyan-400">{(ocrResult.ocr_results?.processing_time || 0).toFixed(2)}s</span></div>
                    </div>
                  </div>
                )}
                
                <Button
                  onClick={() => {
                    setDocumentImage(null);
                    setDocumentPreview(null);
                    setOcrResult(null);
                    setExtractedData({
                      full_name: "",
                      first_name: "",
                      last_name: "",
                      date_of_birth: "",
                      document_number: "",
                      nationality: "",
                      document_type: "",
                      place_of_birth: "",
                      sex: ""
                    });
                  }}
                  variant="outline"
                  className="w-full"
                >
                  Upload Different Document
                </Button>
              </div>
            )}
            
            {/* Camera Modal */}
            <AnimatePresence>
              {showCamera && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="fixed inset-0 bg-black bg-opacity-90 flex items-center justify-center z-50"
                >
                  <div className="bg-slate-800 rounded-lg p-6 max-w-lg w-full mx-4">
                    <div className="text-center mb-4">
                      <h3 className="text-lg font-semibold text-white mb-2">Capture Document</h3>
                      <p className="text-slate-400 text-sm">
                        Position your document within the frame and ensure it's well-lit
                      </p>
                    </div>
                    
                    <div className="relative mb-4">
                      <video
                        ref={videoRef}
                        autoPlay
                        playsInline
                        className="w-full rounded-lg"
                      />
                      <div className="absolute inset-4 border-2 border-cyan-400 border-dashed rounded-lg pointer-events-none"></div>
                    </div>
                    
                    <div className="flex gap-3">
                      <Button onClick={capturePhoto} className="flex-1">
                        <Camera className="h-4 w-4 mr-2" />
                        Capture
                      </Button>
                      <Button onClick={stopCamera} variant="outline" className="flex-1">
                        Cancel
                      </Button>
                    </div>
                  </div>
                  
                  <canvas ref={canvasRef} className="hidden" />
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        );
        
      case 2:
        return (
          <div className="space-y-6">
            <div className="text-center">
              <FileText className="mx-auto h-12 w-12 text-cyan-400 mb-4" />
              <h3 className="text-xl font-semibold text-white mb-2">Verify Extracted Information</h3>
              <p className="text-slate-400">
                Review and correct the information extracted from your document
              </p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="full_name" className="text-slate-300">Full Name *</Label>
                <Input
                  id="full_name"
                  value={extractedData.full_name}
                  onChange={(e) => handleExtractedDataChange("full_name", e.target.value)}
                  className="bg-slate-700 border-slate-600 text-white"
                  placeholder="Enter your full name"
                />
              </div>
              
              <div>
                <Label htmlFor="date_of_birth" className="text-slate-300">Date of Birth *</Label>
                <Input
                  id="date_of_birth"
                  type="date"
                  value={extractedData.date_of_birth}
                  onChange={(e) => handleExtractedDataChange("date_of_birth", e.target.value)}
                  className="bg-slate-700 border-slate-600 text-white"
                />
              </div>
              
              <div>
                <Label htmlFor="document_number" className="text-slate-300">Document Number</Label>
                <Input
                  id="document_number"
                  value={extractedData.document_number}
                  onChange={(e) => handleExtractedDataChange("document_number", e.target.value)}
                  className="bg-slate-700 border-slate-600 text-white"
                  placeholder="Document number"
                />
              </div>
              
              <div>
                <Label htmlFor="nationality" className="text-slate-300">Nationality</Label>
                <Input
                  id="nationality"
                  value={extractedData.nationality}
                  onChange={(e) => handleExtractedDataChange("nationality", e.target.value)}
                  className="bg-slate-700 border-slate-600 text-white"
                  placeholder="Your nationality"
                />
              </div>
              
              <div>
                <Label htmlFor="place_of_birth" className="text-slate-300">Place of Birth</Label>
                <Input
                  id="place_of_birth"
                  value={extractedData.place_of_birth}
                  onChange={(e) => handleExtractedDataChange("place_of_birth", e.target.value)}
                  className="bg-slate-700 border-slate-600 text-white"
                  placeholder="Place of birth"
                />
              </div>
              
              <div>
                <Label htmlFor="sex" className="text-slate-300">Gender</Label>
                <select
                  id="sex"
                  value={extractedData.sex}
                  onChange={(e) => handleExtractedDataChange("sex", e.target.value)}
                  className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-white"
                >
                  <option value="">Select gender</option>
                  <option value="M">Male</option>
                  <option value="F">Female</option>
                  <option value="Other">Other</option>
                </select>
              </div>
            </div>
            
            {ocrResult && (
              <div className="bg-slate-800 border border-slate-600 rounded-lg p-4">
                <div className="text-sm text-slate-400 mb-2">Document Processing Details:</div>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>Document Type: <span className="text-cyan-400">{ocrResult.parsed_document?.document_type}</span></div>
                  <div>OCR Confidence: <span className="text-cyan-400">{Math.round(ocrResult.ocr_results?.confidence || 0)}%</span></div>
                  <div>Engine Used: <span className="text-cyan-400">{ocrResult.ocr_results?.engine_used}</span></div>
                  <div>Processing Time: <span className="text-cyan-400">{(ocrResult.ocr_results?.processing_time || 0).toFixed(2)}s</span></div>
                </div>
              </div>
            )}
          </div>
        );
        
      case 3:
        return (
          <div className="space-y-6">
            <div className="text-center">
              <User className="mx-auto h-12 w-12 text-cyan-400 mb-4" />
              <h3 className="text-xl font-semibold text-white mb-2">Personal Contact Information</h3>
              <p className="text-slate-400">
                Provide your contact details for account verification
              </p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="md:col-span-2">
                <Label htmlFor="email" className="text-slate-300">Email Address *</Label>
                <Input
                  id="email"
                  type="email"
                  value={clientData.email}
                  onChange={(e) => handleClientDataChange("email", e.target.value)}
                  className="bg-slate-700 border-slate-600 text-white"
                  placeholder="your.email@example.com"
                />
              </div>
              
              <div>
                <Label htmlFor="phone" className="text-slate-300">Phone Number *</Label>
                <Input
                  id="phone"
                  type="tel"
                  value={clientData.phone}
                  onChange={(e) => handleClientDataChange("phone", e.target.value)}
                  className="bg-slate-700 border-slate-600 text-white"
                  placeholder="+1 (555) 123-4567"
                />
              </div>
              
              <div>
                <Label htmlFor="address" className="text-slate-300">Address *</Label>
                <Input
                  id="address"
                  value={clientData.address}
                  onChange={(e) => handleClientDataChange("address", e.target.value)}
                  className="bg-slate-700 border-slate-600 text-white"
                  placeholder="Your current address"
                />
              </div>
            </div>
          </div>
        );
        
      case 4:
        return (
          <div className="space-y-6">
            <div className="text-center">
              <Shield className="mx-auto h-12 w-12 text-cyan-400 mb-4" />
              <h3 className="text-xl font-semibold text-white mb-2">Create Your Account</h3>
              <p className="text-slate-400">
                Set up your login credentials and review terms
              </p>
            </div>
            
            <div className="space-y-4">
              <div>
                <Label htmlFor="password" className="text-slate-300">Password *</Label>
                <Input
                  id="password"
                  type="password"
                  value={clientData.password}
                  onChange={(e) => handleClientDataChange("password", e.target.value)}
                  className="bg-slate-700 border-slate-600 text-white"
                  placeholder="Create a strong password"
                />
              </div>
              
              <div>
                <Label htmlFor="confirmPassword" className="text-slate-300">Confirm Password *</Label>
                <Input
                  id="confirmPassword"
                  type="password"
                  value={clientData.confirmPassword}
                  onChange={(e) => handleClientDataChange("confirmPassword", e.target.value)}
                  className="bg-slate-700 border-slate-600 text-white"
                  placeholder="Confirm your password"
                />
                {clientData.password && clientData.confirmPassword && clientData.password !== clientData.confirmPassword && (
                  <div className="text-red-400 text-sm mt-1">Passwords do not match</div>
                )}
              </div>
              
              <div className="space-y-3">
                <div className="flex items-start space-x-3">
                  <input
                    type="checkbox"
                    id="terms"
                    checked={clientData.terms_accepted}
                    onChange={(e) => handleClientDataChange("terms_accepted", e.target.checked)}
                    className="mt-1"
                  />
                  <Label htmlFor="terms" className="text-slate-300 text-sm leading-relaxed">
                    I agree to the <a href="#" className="text-cyan-400 hover:underline">Terms of Service</a> and understand the risks associated with financial investments *
                  </Label>
                </div>
                
                <div className="flex items-start space-x-3">
                  <input
                    type="checkbox"
                    id="privacy"
                    checked={clientData.privacy_accepted}
                    onChange={(e) => handleClientDataChange("privacy_accepted", e.target.checked)}
                    className="mt-1"
                  />
                  <Label htmlFor="privacy" className="text-slate-300 text-sm leading-relaxed">
                    I consent to the processing of my personal data in accordance with the <a href="#" className="text-cyan-400 hover:underline">Privacy Policy</a> *
                  </Label>
                </div>
              </div>
            </div>
          </div>
        );
        
      case 5:
        return (
          <div className="space-y-6">
            <div className="text-center">
              <Shield className="mx-auto h-12 w-12 text-cyan-400 mb-4" />
              <h3 className="text-xl font-semibold text-white mb-2">KYC/AML Verification</h3>
              <p className="text-slate-400">
                Completing compliance verification and OFAC screening
              </p>
            </div>
            
            <div className="space-y-4">
              <div className="bg-slate-800 border border-slate-600 rounded-lg p-4">
                <h4 className="text-white font-medium mb-3">Verification Checklist</h4>
                
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-slate-300">Document Verification</span>
                    {kycStatus.document_verified ? (
                      <CheckCircle className="h-5 w-5 text-green-400" />
                    ) : (
                      <div className="h-5 w-5 rounded-full border-2 border-slate-500"></div>
                    )}
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-slate-300">Identity Verification</span>
                    {kycStatus.identity_verified ? (
                      <CheckCircle className="h-5 w-5 text-green-400" />
                    ) : loading ? (
                      <Loader2 className="h-5 w-5 animate-spin text-cyan-400" />
                    ) : (
                      <div className="h-5 w-5 rounded-full border-2 border-slate-500"></div>
                    )}
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-slate-300">OFAC Screening</span>
                    {kycStatus.ofac_cleared ? (
                      <CheckCircle className="h-5 w-5 text-green-400" />
                    ) : loading ? (
                      <Loader2 className="h-5 w-5 animate-spin text-cyan-400" />
                    ) : (
                      <div className="h-5 w-5 rounded-full border-2 border-slate-500"></div>
                    )}
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-slate-300">AML Assessment</span>
                    {kycStatus.aml_status === "approved" ? (
                      <CheckCircle className="h-5 w-5 text-green-400" />
                    ) : kycStatus.aml_status === "review_required" ? (
                      <AlertCircle className="h-5 w-5 text-yellow-400" />
                    ) : loading ? (
                      <Loader2 className="h-5 w-5 animate-spin text-cyan-400" />
                    ) : (
                      <div className="h-5 w-5 rounded-full border-2 border-slate-500"></div>
                    )}
                  </div>
                </div>
              </div>
              
              <div className="bg-slate-800 border border-slate-600 rounded-lg p-4">
                <h4 className="text-white font-medium mb-2">Overall Status</h4>
                <div className="flex items-center gap-2">
                  <Badge 
                    className={`
                      ${kycStatus.overall_status === "approved" ? "bg-green-600 text-white" : ""}
                      ${kycStatus.overall_status === "review_required" ? "bg-yellow-600 text-white" : ""}
                      ${kycStatus.overall_status === "incomplete" ? "bg-slate-600 text-white" : ""}
                      ${kycStatus.overall_status === "failed" ? "bg-red-600 text-white" : ""}
                    `}
                  >
                    {kycStatus.overall_status === "approved" && "✓ Approved"}
                    {kycStatus.overall_status === "review_required" && "⚠ Review Required"}
                    {kycStatus.overall_status === "incomplete" && "○ In Progress"}
                    {kycStatus.overall_status === "failed" && "✗ Failed"}
                  </Badge>
                </div>
              </div>
              
              {kycStatus.overall_status === "approved" && (
                <Button
                  onClick={completeRegistration}
                  className="w-full bg-green-600 hover:bg-green-700"
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Creating Account...
                    </>
                  ) : (
                    "Complete Registration"
                  )}
                </Button>
              )}
            </div>
          </div>
        );
        
      default:
        return null;
    }
  };
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center p-4">
      <div className="w-full max-w-4xl">
        {/* Header */}
        <div className="text-center mb-8">
          <motion.div
            className="mb-6 logo-integrated"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.3, duration: 0.8 }}
          >
            <img 
              src="/fidus-logo.png"
              alt="FIDUS Logo"
              style={{
                width: "200px",
                height: "auto",
                margin: "0 auto",
                display: "block",
                filter: `
                  drop-shadow(0 0 15px rgba(255, 167, 38, 0.4))
                  drop-shadow(0 0 30px rgba(59, 130, 246, 0.2))
                  brightness(1.03)
                  contrast(1.01)
                `,
                transition: "all 0.3s ease"
              }}
            />
          </motion.div>
          
          <h1 className="text-3xl font-bold text-white mb-2">Welcome to FIDUS</h1>
          <p className="text-slate-400">Complete your client onboarding with advanced document verification</p>
        </div>
        
        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm text-slate-400">Step {currentStep} of {steps.length}</span>
            <span className="text-sm text-slate-400">{Math.round(progress)}% Complete</span>
          </div>
          <Progress value={progress} className="h-2" />
          
          <div className="mt-4">
            <h2 className="text-xl font-semibold text-white">{currentStepInfo?.title}</h2>
            <p className="text-slate-400">{currentStepInfo?.description}</p>
          </div>
        </div>
        
        {/* Alert Messages */}
        {error && (
          <Alert className="mb-6 border-red-600 bg-red-900/20">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription className="text-red-300">{error}</AlertDescription>
          </Alert>
        )}
        
        {success && (
          <Alert className="mb-6 border-green-600 bg-green-900/20">
            <CheckCircle className="h-4 w-4" />
            <AlertDescription className="text-green-300">{success}</AlertDescription>
          </Alert>
        )}
        
        {/* Main Content */}
        <Card className="bg-slate-800/50 border-slate-700 backdrop-blur-sm">
          <CardContent className="p-8">
            <AnimatePresence mode="wait">
              <motion.div
                key={currentStep}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.3 }}
              >
                {renderStepContent()}
              </motion.div>
            </AnimatePresence>
          </CardContent>
        </Card>
        
        {/* Navigation */}
        <div className="flex justify-between mt-8">
          <Button
            onClick={currentStep === 1 ? onBack : prevStep}
            variant="outline"
            className="border-slate-600 text-slate-300 hover:bg-slate-700"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            {currentStep === 1 ? "Back to Login" : "Previous"}
          </Button>
          
          {currentStep < steps.length ? (
            <Button
              onClick={nextStep}
              disabled={!validateCurrentStep() || loading}
              className="bg-cyan-600 hover:bg-cyan-700"
            >
              Next Step
              <ArrowRight className="h-4 w-4 ml-2" />
            </Button>
          ) : null}
        </div>
      </div>
    </div>
  );
};

export default ClientOnboarding;