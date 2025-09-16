import React, { useState } from "react";
import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Alert, AlertDescription } from "./ui/alert";
import { Textarea } from "./ui/textarea";
import { 
  User, 
  Phone, 
  Mail,
  MapPin,
  Calendar,
  FileText,
  CheckCircle,
  AlertCircle,
  Loader2,
  ArrowLeft,
  ArrowRight,
  Upload,
  DollarSign
} from "lucide-react";
import axios from "axios";

const LeadRegistrationForm = ({ onBack, onComplete }) => {
  const [formData, setFormData] = useState({
    firstName: "",
    lastName: "",
    email: "",
    phone: "",
    dateOfBirth: "",
    address: "",
    city: "",
    country: "",
    investmentInterest: "",
    investmentAmount: "",
    notes: ""
  });
  
  const [documents, setDocuments] = useState({
    governmentId: null,
    proofOfAddress: null
  });
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [step, setStep] = useState(1);
  
  const backendUrl = process.env.REACT_APP_BACKEND_URL;
  
  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    setError(""); // Clear error when user starts typing
  };
  
  const handleFileUpload = (documentType, file) => {
    if (file) {
      setDocuments(prev => ({ ...prev, [documentType]: file }));
    }
  };
  
  const validateStep1 = () => {
    const { firstName, lastName, email, phone } = formData;
    if (!firstName || !lastName || !email || !phone) {
      setError("Please fill in all required fields");
      return false;
    }
    
    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      setError("Please enter a valid email address");
      return false;
    }
    
    return true;
  };
  
  const validateStep2 = () => {
    const { dateOfBirth, address, country } = formData;
    if (!dateOfBirth || !address || !country) {
      setError("Please complete all required fields");
      return false;
    }
    
    // Validate date of birth (must be at least 18 years old)
    const birthDate = new Date(dateOfBirth);
    const today = new Date();
    const age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    
    if (age < 18 || (age === 18 && monthDiff < 0) || 
        (age === 18 && monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      setError("You must be at least 18 years old to register");
      return false;
    }
    
    return true;
  };
  
  const validateStep3 = () => {
    const { investmentInterest, investmentAmount } = formData;
    if (!investmentInterest || !investmentAmount) {
      setError("Please specify your investment interests");
      return false;
    }
    
    const amount = parseFloat(investmentAmount);
    if (isNaN(amount) || amount < 1000) {
      setError("Minimum investment interest is $1,000");
      return false;
    }
    
    return true;
  };
  
  const nextStep = () => {
    let isValid = false;
    
    if (step === 1) {
      isValid = validateStep1();
    } else if (step === 2) {
      isValid = validateStep2();
    } else if (step === 3) {
      isValid = validateStep3();
    }
    
    if (isValid) {
      setStep(prev => prev + 1);
      setError("");
    }
  };
  
  const prevStep = () => {
    setStep(prev => prev - 1);
    setError("");
  };
  
  const handleSubmit = async () => {
    if (!documents.governmentId || !documents.proofOfAddress) {
      setError("Please upload both required documents");
      return;
    }
    
    setLoading(true);
    setError("");
    
    try {
      // Create FormData for file uploads
      const submitData = new FormData();
      
      // Add prospect data
      const prospectData = {
        name: `${formData.firstName} ${formData.lastName}`,
        email: formData.email,
        phone: formData.phone,
        notes: `Investment Interest: ${formData.investmentInterest} | Amount: $${formData.investmentAmount} | Address: ${formData.address}, ${formData.city}, ${formData.country} | DOB: ${formData.dateOfBirth} | Additional Notes: ${formData.notes || 'None'}`
      };
      
      // Submit prospect to CRM system
      const response = await axios.post(`${backendUrl}/api/crm/prospects`, prospectData);
      
      if (response.data.success) {
        const prospectId = response.data.prospect_id;
        
        // Upload documents
        const documentFormData = new FormData();
        documentFormData.append('file', documents.governmentId);
        documentFormData.append('document_type', 'identity');
        documentFormData.append('notes', 'Government ID uploaded during registration');
        
        await axios.post(`${backendUrl}/api/crm/prospects/${prospectId}/documents`, documentFormData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        
        const addressFormData = new FormData();
        addressFormData.append('file', documents.proofOfAddress);
        addressFormData.append('document_type', 'proof_of_residence');
        addressFormData.append('notes', 'Proof of address uploaded during registration');
        
        await axios.post(`${backendUrl}/api/crm/prospects/${prospectId}/documents`, addressFormData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        
        setSuccess("Registration successful! Our team will review your application and contact you within 24 hours.");
        
        // Complete registration after 3 seconds
        setTimeout(() => {
          onComplete({
            type: "lead",
            prospectId: prospectId,
            name: prospectData.name,
            email: prospectData.email
          });
        }, 3000);
        
      } else {
        throw new Error(response.data.message || "Registration failed");
      }
      
    } catch (err) {
      console.error('Registration error:', err);
      setError(err.response?.data?.detail || err.message || "Registration failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };
  
  if (success) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center py-8"
      >
        <CheckCircle className="h-16 w-16 mx-auto text-green-500 mb-4" />
        <h3 className="text-xl font-bold text-white mb-2">Registration Successful!</h3>
        <p className="text-slate-300 mb-4">{success}</p>
        <p className="text-sm text-slate-400">You will be redirected shortly...</p>
      </motion.div>
    );
  }
  
  return (
    <div className="space-y-6">
      {/* Progress Indicator */}
      <div className="flex items-center justify-between mb-6">
        {[1, 2, 3, 4].map((stepNum) => (
          <div key={stepNum} className="flex items-center">
            <div className={`
              w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium
              ${step >= stepNum 
                ? 'bg-cyan-600 text-white' 
                : 'bg-slate-600 text-slate-300'
              }
            `}>
              {step > stepNum ? <CheckCircle size={16} /> : stepNum}
            </div>
            {stepNum < 4 && (
              <div className={`
                h-1 w-12 mx-2
                ${step > stepNum ? 'bg-cyan-600' : 'bg-slate-600'}
              `} />
            )}
          </div>
        ))}
      </div>
      
      {/* Step Content */}
      <Card className="bg-slate-800 border-slate-600">
        <CardHeader>
          <CardTitle className="text-white">
            {step === 1 && "Personal Information"}
            {step === 2 && "Address & Verification"}
            {step === 3 && "Investment Interest"}
            {step === 4 && "Document Upload"}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {error && (
            <Alert className="bg-red-50 border-red-200">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription className="text-red-800">{error}</AlertDescription>
            </Alert>
          )}
          
          {/* Step 1: Personal Information */}
          {step === 1 && (
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="grid grid-cols-1 md:grid-cols-2 gap-4"
            >
              <div>
                <Label htmlFor="firstName" className="text-slate-300">First Name *</Label>
                <Input
                  id="firstName"
                  value={formData.firstName}
                  onChange={(e) => handleInputChange('firstName', e.target.value)}
                  className="bg-slate-700 border-slate-600 text-white"
                  placeholder="Enter your first name"
                />
              </div>
              <div>
                <Label htmlFor="lastName" className="text-slate-300">Last Name *</Label>
                <Input
                  id="lastName"
                  value={formData.lastName}
                  onChange={(e) => handleInputChange('lastName', e.target.value)}
                  className="bg-slate-700 border-slate-600 text-white"
                  placeholder="Enter your last name"
                />
              </div>
              <div>
                <Label htmlFor="email" className="text-slate-300">Email Address *</Label>
                <Input
                  id="email"
                  type="email"
                  value={formData.email}
                  onChange={(e) => handleInputChange('email', e.target.value)}
                  className="bg-slate-700 border-slate-600 text-white"
                  placeholder="Enter your email"
                />
              </div>
              <div>
                <Label htmlFor="phone" className="text-slate-300">Phone Number *</Label>
                <Input
                  id="phone"
                  value={formData.phone}
                  onChange={(e) => handleInputChange('phone', e.target.value)}
                  className="bg-slate-700 border-slate-600 text-white"
                  placeholder="Enter your phone number"
                />
              </div>
            </motion.div>
          )}
          
          {/* Step 2: Address & Verification */}
          {step === 2 && (
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="space-y-4"
            >
              <div>
                <Label htmlFor="dateOfBirth" className="text-slate-300">Date of Birth *</Label>
                <Input
                  id="dateOfBirth"
                  type="date"
                  value={formData.dateOfBirth}
                  onChange={(e) => handleInputChange('dateOfBirth', e.target.value)}
                  className="bg-slate-700 border-slate-600 text-white"
                />
              </div>
              <div>
                <Label htmlFor="address" className="text-slate-300">Address *</Label>
                <Input
                  id="address"
                  value={formData.address}
                  onChange={(e) => handleInputChange('address', e.target.value)}
                  className="bg-slate-700 border-slate-600 text-white"
                  placeholder="Enter your full address"
                />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="city" className="text-slate-300">City</Label>
                  <Input
                    id="city"
                    value={formData.city}
                    onChange={(e) => handleInputChange('city', e.target.value)}
                    className="bg-slate-700 border-slate-600 text-white"
                    placeholder="Enter your city"
                  />
                </div>
                <div>
                  <Label htmlFor="country" className="text-slate-300">Country *</Label>
                  <Input
                    id="country"
                    value={formData.country}
                    onChange={(e) => handleInputChange('country', e.target.value)}
                    className="bg-slate-700 border-slate-600 text-white"
                    placeholder="Enter your country"
                  />
                </div>
              </div>
            </motion.div>
          )}
          
          {/* Step 3: Investment Interest */}
          {step === 3 && (
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="space-y-4"
            >
              <div>
                <Label htmlFor="investmentInterest" className="text-slate-300">Investment Interest *</Label>
                <select
                  id="investmentInterest"
                  value={formData.investmentInterest}
                  onChange={(e) => handleInputChange('investmentInterest', e.target.value)}
                  className="w-full px-3 py-2 bg-slate-700 border-slate-600 text-white rounded-md"
                >
                  <option value="">Select fund interest</option>
                  <option value="CORE">FIDUS Core Fund (1.5% monthly)</option>
                  <option value="BALANCE">FIDUS Balance Fund (2.5% monthly)</option>
                  <option value="DYNAMIC">FIDUS Dynamic Fund (3.5% monthly)</option>
                  <option value="UNLIMITED">FIDUS Unlimited Fund (Performance sharing)</option>
                  <option value="MULTIPLE">Multiple funds</option>
                  <option value="CONSULTATION">Need consultation</option>
                </select>
              </div>
              <div>
                <Label htmlFor="investmentAmount" className="text-slate-300">Approximate Investment Amount *</Label>
                <Input
                  id="investmentAmount"
                  type="number"
                  value={formData.investmentAmount}
                  onChange={(e) => handleInputChange('investmentAmount', e.target.value)}
                  className="bg-slate-700 border-slate-600 text-white"
                  placeholder="Enter amount in USD"
                  min="1000"
                />
              </div>
              <div>
                <Label htmlFor="notes" className="text-slate-300">Additional Notes</Label>
                <Textarea
                  id="notes"
                  value={formData.notes}
                  onChange={(e) => handleInputChange('notes', e.target.value)}
                  className="bg-slate-700 border-slate-600 text-white"
                  placeholder="Any additional information or questions"
                  rows={3}
                />
              </div>
            </motion.div>
          )}
          
          {/* Step 4: Document Upload */}
          {step === 4 && (
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="space-y-6"
            >
              <div className="text-center mb-6">
                <p className="text-slate-300 mb-2">Please upload the following documents to complete your registration:</p>
                <p className="text-sm text-slate-400">Accepted formats: JPG, PNG, PDF (max 5MB each)</p>
              </div>
              
              {/* Government ID Upload */}
              <div className="border border-slate-600 rounded-lg p-4">
                <Label className="text-slate-300 mb-2 block">Government ID (Required)</Label>
                <p className="text-sm text-slate-400 mb-3">Passport, Driver's License, or National ID</p>
                <input
                  type="file"
                  accept=".jpg,.jpeg,.png,.pdf"
                  onChange={(e) => handleFileUpload('governmentId', e.target.files[0])}
                  className="hidden"
                  id="governmentId"
                />
                <label
                  htmlFor="governmentId"
                  className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-slate-600 rounded-lg cursor-pointer hover:border-cyan-500 transition-colors"
                >
                  {documents.governmentId ? (
                    <div className="text-center">
                      <CheckCircle className="h-8 w-8 text-green-500 mx-auto mb-2" />
                      <p className="text-sm text-green-400">{documents.governmentId.name}</p>
                    </div>
                  ) : (
                    <div className="text-center">
                      <Upload className="h-8 w-8 text-slate-400 mx-auto mb-2" />
                      <p className="text-sm text-slate-400">Click to upload Government ID</p>
                    </div>
                  )}
                </label>
              </div>
              
              {/* Proof of Address Upload */}
              <div className="border border-slate-600 rounded-lg p-4">
                <Label className="text-slate-300 mb-2 block">Proof of Address (Required)</Label>
                <p className="text-sm text-slate-400 mb-3">Utility bill, Bank statement, or Lease agreement (max 3 months old)</p>
                <input
                  type="file"
                  accept=".jpg,.jpeg,.png,.pdf"
                  onChange={(e) => handleFileUpload('proofOfAddress', e.target.files[0])}
                  className="hidden"
                  id="proofOfAddress"
                />
                <label
                  htmlFor="proofOfAddress"
                  className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-slate-600 rounded-lg cursor-pointer hover:border-cyan-500 transition-colors"
                >
                  {documents.proofOfAddress ? (
                    <div className="text-center">
                      <CheckCircle className="h-8 w-8 text-green-500 mx-auto mb-2" />
                      <p className="text-sm text-green-400">{documents.proofOfAddress.name}</p>
                    </div>
                  ) : (
                    <div className="text-center">
                      <Upload className="h-8 w-8 text-slate-400 mx-auto mb-2" />
                      <p className="text-sm text-slate-400">Click to upload Proof of Address</p>
                    </div>
                  )}
                </label>
              </div>
            </motion.div>
          )}
          
          {/* Navigation Buttons */}
          <div className="flex justify-between pt-6">
            <Button
              variant="outline"
              onClick={step === 1 ? onBack : prevStep}
              disabled={loading}
              className="border-slate-600 text-slate-300 hover:bg-slate-700"
            >
              <ArrowLeft size={16} className="mr-2" />
              {step === 1 ? "Back to Login" : "Previous"}
            </Button>
            
            {step < 4 ? (
              <Button
                onClick={nextStep}
                disabled={loading}
                className="bg-cyan-600 hover:bg-cyan-700"
              >
                Next
                <ArrowRight size={16} className="ml-2" />
              </Button>
            ) : (
              <Button
                onClick={handleSubmit}
                disabled={loading}
                className="bg-green-600 hover:bg-green-700"
              >
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Submitting...
                  </>
                ) : (
                  <>
                    Complete Registration
                    <CheckCircle size={16} className="ml-2" />
                  </>
                )}
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default LeadRegistrationForm;