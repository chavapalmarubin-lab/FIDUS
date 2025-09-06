import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Alert, AlertDescription } from "./ui/alert";
import { Progress } from "./ui/progress";
import { 
  ArrowLeft, 
  Mail, 
  Key, 
  Eye, 
  EyeOff,
  CheckCircle, 
  AlertCircle,
  Shield,
  Loader2
} from "lucide-react";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const RESET_STEPS = {
  EMAIL_INPUT: "email_input",
  EMAIL_SENT: "email_sent", 
  RESET_CODE: "reset_code",
  NEW_PASSWORD: "new_password",
  SUCCESS: "success"
};

const PasswordReset = ({ userType, onBack, onComplete }) => {
  const [currentStep, setCurrentStep] = useState(RESET_STEPS.EMAIL_INPUT);
  const [email, setEmail] = useState("");
  const [resetCode, setResetCode] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [resetToken, setResetToken] = useState("");
  const [passwordStrength, setPasswordStrength] = useState(0);

  const handleEmailSubmit = async () => {
    if (!email || !email.includes('@')) {
      setError("Please enter a valid email address");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await axios.post(`${API}/auth/forgot-password`, {
        email: email,
        userType: userType
      });

      if (response.data.success) {
        setResetToken(response.data.resetToken);
        setCurrentStep(RESET_STEPS.EMAIL_SENT);
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to send reset email. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleCodeSubmit = async () => {
    if (!resetCode || resetCode.length !== 6) {
      setError("Please enter the 6-digit verification code");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await axios.post(`${API}/auth/verify-reset-code`, {
        email: email,
        resetCode: resetCode,
        resetToken: resetToken
      });

      if (response.data.success) {
        setCurrentStep(RESET_STEPS.NEW_PASSWORD);
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Invalid verification code. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordReset = async () => {
    if (!newPassword || newPassword.length < 8) {
      setError("Password must be at least 8 characters long");
      return;
    }

    if (newPassword !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    if (passwordStrength < 3) {
      setError("Password is not strong enough. Please include uppercase, lowercase, numbers, and symbols.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await axios.post(`${API}/auth/reset-password`, {
        email: email,
        resetCode: resetCode,
        resetToken: resetToken,
        newPassword: newPassword
      });

      if (response.data.success) {
        setCurrentStep(RESET_STEPS.SUCCESS);
        setTimeout(() => {
          onComplete();
        }, 3000);
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to reset password. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const calculatePasswordStrength = (password) => {
    let strength = 0;
    if (password.length >= 8) strength++;
    if (/[a-z]/.test(password)) strength++;
    if (/[A-Z]/.test(password)) strength++;
    if (/[0-9]/.test(password)) strength++;
    if (/[^A-Za-z0-9]/.test(password)) strength++;
    return strength;
  };

  const handlePasswordChange = (value) => {
    setNewPassword(value);
    setPasswordStrength(calculatePasswordStrength(value));
  };

  const getPasswordStrengthColor = () => {
    if (passwordStrength <= 2) return "bg-red-500";
    if (passwordStrength === 3) return "bg-yellow-500";
    if (passwordStrength === 4) return "bg-blue-500";
    return "bg-green-500";
  };

  const getPasswordStrengthText = () => {
    if (passwordStrength <= 2) return "Weak";
    if (passwordStrength === 3) return "Fair";
    if (passwordStrength === 4) return "Good";
    return "Strong";
  };

  const renderEmailInputStep = () => (
    <motion.div
      initial={{ opacity: 0, x: 50 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-4"
    >
      <div className="text-center mb-6">
        <Mail className="w-16 h-16 text-cyan-400 mx-auto mb-4" />
        <h3 className="text-xl font-semibold text-white mb-2">Reset Your Password</h3>
        <p className="text-slate-400">
          Enter your email address and we'll send you a verification code to reset your password.
        </p>
      </div>

      <div className="space-y-2">
        <Label htmlFor="email" className="text-slate-300">Email Address</Label>
        <Input
          id="email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="bg-slate-800 border-slate-600 text-white"
          placeholder="Enter your email address"
          onKeyPress={(e) => e.key === 'Enter' && handleEmailSubmit()}
        />
      </div>

      <div className="flex gap-3 pt-4">
        <Button variant="outline" onClick={onBack} className="flex-1">
          <ArrowLeft size={16} className="mr-2" />
          Back to Login
        </Button>
        <Button 
          onClick={handleEmailSubmit} 
          disabled={loading || !email}
          className="flex-1 bg-cyan-600 hover:bg-cyan-700"
        >
          {loading ? (
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          ) : (
            <Mail className="mr-2 h-4 w-4" />
          )}
          Send Reset Code
        </Button>
      </div>
    </motion.div>
  );

  const renderEmailSentStep = () => (
    <motion.div
      initial={{ opacity: 0, x: 50 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-4"
    >
      <div className="text-center mb-6">
        <div className="w-16 h-16 bg-green-600 rounded-full flex items-center justify-center mx-auto mb-4">
          <CheckCircle className="w-8 h-8 text-white" />
        </div>
        <h3 className="text-xl font-semibold text-white mb-2">Check Your Email</h3>
        <p className="text-slate-400">
          We've sent a 6-digit verification code to:
        </p>
        <p className="text-cyan-400 font-medium">{email}</p>
      </div>

      <div className="bg-slate-800 rounded-lg p-4 text-center">
        <p className="text-slate-300 text-sm mb-2">Didn't receive the email?</p>
        <Button 
          variant="ghost" 
          size="sm"
          onClick={() => setCurrentStep(RESET_STEPS.EMAIL_INPUT)}
          className="text-cyan-400 hover:bg-cyan-900/20"
        >
          Try a different email
        </Button>
      </div>

      <Button 
        onClick={() => setCurrentStep(RESET_STEPS.RESET_CODE)}
        className="w-full bg-cyan-600 hover:bg-cyan-700"
      >
        I Have the Code
      </Button>
    </motion.div>
  );

  const renderResetCodeStep = () => (
    <motion.div
      initial={{ opacity: 0, x: 50 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-4"
    >
      <div className="text-center mb-6">
        <Key className="w-16 h-16 text-cyan-400 mx-auto mb-4" />
        <h3 className="text-xl font-semibold text-white mb-2">Enter Verification Code</h3>
        <p className="text-slate-400">
          Enter the 6-digit code sent to {email}
        </p>
      </div>

      <div className="space-y-2">
        <Label htmlFor="resetCode" className="text-slate-300">Verification Code</Label>
        <Input
          id="resetCode"
          type="text"
          value={resetCode}
          onChange={(e) => setResetCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
          className="bg-slate-800 border-slate-600 text-white text-center text-2xl tracking-widest"
          placeholder="000000"
          maxLength={6}
          onKeyPress={(e) => e.key === 'Enter' && handleCodeSubmit()}
        />
      </div>

      <Alert className="bg-slate-800 border-slate-600">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription className="text-slate-300">
          <strong>Demo Mode:</strong> Use any 6-digit code (e.g., 123456) to proceed.
        </AlertDescription>
      </Alert>

      <div className="flex gap-3 pt-4">
        <Button 
          variant="outline" 
          onClick={() => setCurrentStep(RESET_STEPS.EMAIL_SENT)} 
          className="flex-1"
        >
          <ArrowLeft size={16} className="mr-2" />
          Back
        </Button>
        <Button 
          onClick={handleCodeSubmit} 
          disabled={loading || resetCode.length !== 6}
          className="flex-1 bg-cyan-600 hover:bg-cyan-700"
        >
          {loading ? (
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          ) : null}
          Verify Code
        </Button>
      </div>
    </motion.div>
  );

  const renderNewPasswordStep = () => (
    <motion.div
      initial={{ opacity: 0, x: 50 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-4"
    >
      <div className="text-center mb-6">
        <Shield className="w-16 h-16 text-cyan-400 mx-auto mb-4" />
        <h3 className="text-xl font-semibold text-white mb-2">Create New Password</h3>
        <p className="text-slate-400">
          Choose a strong password for your account
        </p>
      </div>

      <div className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="newPassword" className="text-slate-300">New Password</Label>
          <div className="relative">
            <Input
              id="newPassword"
              type={showPassword ? "text" : "password"}
              value={newPassword}
              onChange={(e) => handlePasswordChange(e.target.value)}
              className="bg-slate-800 border-slate-600 text-white pr-10"
              placeholder="Enter new password"
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-1/2 transform -translate-y-1/2 text-slate-400 hover:text-white"
            >
              {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
            </button>
          </div>
          
          {/* Password Strength Indicator */}
          {newPassword && (
            <div className="space-y-2">
              <div className="flex justify-between text-xs">
                <span className="text-slate-400">Password Strength</span>
                <span className={`font-medium ${
                  passwordStrength <= 2 ? 'text-red-400' :
                  passwordStrength === 3 ? 'text-yellow-400' :
                  passwordStrength === 4 ? 'text-blue-400' : 'text-green-400'
                }`}>
                  {getPasswordStrengthText()}
                </span>
              </div>
              <Progress 
                value={(passwordStrength / 5) * 100} 
                className="h-2"
              />
            </div>
          )}
        </div>

        <div className="space-y-2">
          <Label htmlFor="confirmPassword" className="text-slate-300">Confirm Password</Label>
          <div className="relative">
            <Input
              id="confirmPassword"
              type={showConfirmPassword ? "text" : "password"}
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className="bg-slate-800 border-slate-600 text-white pr-10"
              placeholder="Confirm new password"
            />
            <button
              type="button"
              onClick={() => setShowConfirmPassword(!showConfirmPassword)}
              className="absolute right-3 top-1/2 transform -translate-y-1/2 text-slate-400 hover:text-white"
            >
              {showConfirmPassword ? <EyeOff size={16} /> : <Eye size={16} />}
            </button>
          </div>
          
          {/* Password Match Indicator */}
          {confirmPassword && (
            <div className="text-xs">
              {newPassword === confirmPassword ? (
                <span className="text-green-400">✓ Passwords match</span>
              ) : (
                <span className="text-red-400">✗ Passwords do not match</span>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Password Requirements */}
      <div className="bg-slate-800/50 rounded-lg p-3 text-xs text-slate-400">
        <div className="font-medium mb-2">Password Requirements:</div>
        <div className="space-y-1">
          <div className={newPassword.length >= 8 ? 'text-green-400' : 'text-slate-400'}>
            ✓ At least 8 characters
          </div>
          <div className={/[a-z]/.test(newPassword) ? 'text-green-400' : 'text-slate-400'}>
            ✓ Lowercase letter
          </div>
          <div className={/[A-Z]/.test(newPassword) ? 'text-green-400' : 'text-slate-400'}>
            ✓ Uppercase letter
          </div>
          <div className={/[0-9]/.test(newPassword) ? 'text-green-400' : 'text-slate-400'}>
            ✓ Number
          </div>
          <div className={/[^A-Za-z0-9]/.test(newPassword) ? 'text-green-400' : 'text-slate-400'}>
            ✓ Special character
          </div>
        </div>
      </div>

      <div className="flex gap-3 pt-4">
        <Button 
          variant="outline" 
          onClick={() => setCurrentStep(RESET_STEPS.RESET_CODE)} 
          className="flex-1"
        >
          <ArrowLeft size={16} className="mr-2" />
          Back
        </Button>
        <Button 
          onClick={handlePasswordReset} 
          disabled={loading || passwordStrength < 3 || newPassword !== confirmPassword}
          className="flex-1 bg-green-600 hover:bg-green-700"
        >
          {loading ? (
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          ) : (
            <Shield className="mr-2 h-4 w-4" />
          )}
          Reset Password
        </Button>
      </div>
    </motion.div>
  );

  const renderSuccessStep = () => (
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
        <h3 className="text-2xl font-bold text-white mb-2">Password Reset Successful!</h3>
        <p className="text-slate-400 mb-4">
          Your password has been successfully updated.
        </p>
        <div className="bg-slate-800 rounded-lg p-4">
          <p className="text-slate-300 text-sm">
            You can now log in with your new password.
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
        <Card className="login-card max-w-lg">
          <CardHeader className="text-center">
            <motion.div
              className="mb-4 logo-integrated"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.3, duration: 0.8 }}
            >
              <img 
                src="/fidus-logo.png"
                alt="FIDUS Logo"
                style={{
                  width: "180px",
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
            <CardTitle className="text-2xl text-white">
              {userType === 'admin' ? 'Admin' : 'Client'} Password Reset
            </CardTitle>
            <p className="text-slate-400 mt-2">
              Secure password recovery for your FIDUS account
            </p>
            
            {/* Progress Indicator */}
            {currentStep !== RESET_STEPS.SUCCESS && (
              <div className="mt-4">
                <div className="flex justify-between text-xs text-slate-500 mb-2">
                  <span className={currentStep === RESET_STEPS.EMAIL_INPUT ? 'text-cyan-400' : ''}>Email</span>
                  <span className={currentStep === RESET_STEPS.RESET_CODE ? 'text-cyan-400' : ''}>Verify</span>
                  <span className={currentStep === RESET_STEPS.NEW_PASSWORD ? 'text-cyan-400' : ''}>Reset</span>
                </div>
                <Progress 
                  value={
                    currentStep === RESET_STEPS.EMAIL_INPUT ? 25 :
                    currentStep === RESET_STEPS.EMAIL_SENT ? 50 :
                    currentStep === RESET_STEPS.RESET_CODE ? 75 :
                    currentStep === RESET_STEPS.NEW_PASSWORD ? 100 : 25
                  } 
                  className="w-full" 
                />
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
              {currentStep === RESET_STEPS.EMAIL_INPUT && renderEmailInputStep()}
              {currentStep === RESET_STEPS.EMAIL_SENT && renderEmailSentStep()}
              {currentStep === RESET_STEPS.RESET_CODE && renderResetCodeStep()}
              {currentStep === RESET_STEPS.NEW_PASSWORD && renderNewPasswordStep()}
              {currentStep === RESET_STEPS.SUCCESS && renderSuccessStep()}
            </AnimatePresence>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
};

export default PasswordReset;