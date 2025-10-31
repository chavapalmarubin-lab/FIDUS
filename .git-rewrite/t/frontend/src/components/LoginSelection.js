import React, { useState } from "react";
import { motion } from "framer-motion";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { User, Shield, Loader2 } from "lucide-react";
import ClientOnboarding from "./ClientOnboarding";
import LeadRegistrationForm from "./LeadRegistrationForm";
import PasswordReset from "./PasswordReset";
import PasswordChangeModal from "./PasswordChangeModal";
import GoogleSocialLogin from "./GoogleSocialLogin";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const LoginSelection = ({ onLogin }) => {
  const [selectedType, setSelectedType] = useState(null);
  const [credentials, setCredentials] = useState({ username: "", password: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [passwordResetType, setPasswordResetType] = useState(null);
  const [showPasswordChange, setShowPasswordChange] = useState(false);
  const [userRequiringPasswordChange, setUserRequiringPasswordChange] = useState(null);
  const [success, setSuccess] = useState("");

  const handleTypeSelect = (type) => {
    setSelectedType(type);
    setError("");
    // Clear credentials for security
    setCredentials({ username: "", password: "" });
  };

  const handleLogin = async () => {
    // Validate input
    if (!credentials.username || !credentials.password) {
      setError("Please enter both username and password");
      return;
    }

    // Trim whitespace from credentials
    const trimmedCredentials = {
      username: credentials.username.trim(),
      password: credentials.password.trim()
    };

    // Validate trimmed credentials
    if (!trimmedCredentials.username || !trimmedCredentials.password) {
      setError("Please enter valid username and password");
      return;
    }

    setLoading(true);
    setError("");

    // Small delay to ensure UI updates
    await new Promise(resolve => setTimeout(resolve, 100));

    try {
      console.log('Attempting login with:', {
        username: trimmedCredentials.username,
        user_type: selectedType,
        api_url: API
      });

      const response = await axios.post(`${API}/auth/login`, {
        username: trimmedCredentials.username,
        password: trimmedCredentials.password,
        user_type: selectedType
      });

      console.log('Login response:', response.status, response.data);

      console.log('Login response:', response.status, response.data);

      // Check if password change is required
      if (response.data.must_change_password) {
        setUserRequiringPasswordChange(response.data);
        setShowPasswordChange(true);
        setLoading(false);
        return;
      }

      onLogin(response.data);
    } catch (err) {
      console.error('Login error:', err);
      console.error('Error response:', err.response);
      
      let errorMessage = "Login failed";
      
      if (err.response) {
        // Server responded with error
        if (err.response.status === 401) {
          errorMessage = "Invalid username or password";
        } else if (err.response.status === 500) {
          errorMessage = "Server error. Please try again.";
        } else if (err.response.data?.detail) {
          errorMessage = err.response.data.detail;
        } else if (err.response.data?.message) {
          errorMessage = err.response.data.message;
        }
      } else if (err.request) {
        // Network error
        errorMessage = "Network error. Please check your connection.";
      } else {
        // Other error
        errorMessage = err.message || "An unexpected error occurred";
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordChanged = () => {
    setShowPasswordChange(false);
    setUserRequiringPasswordChange(null);
    setCredentials({ username: "", password: "" });
    setError("");
    // User will need to login again with new password
  };

  const handleBack = () => {
    setSelectedType(null);
    setCredentials({ username: "", password: "" });
    setError("");
  };

  return (
    <div className="login-selection">
      <motion.div
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
      >
        <Card className="login-card">
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
                  width: "280px",
                  height: "auto",
                  margin: "0 auto",
                  display: "block",
                  filter: `
                    drop-shadow(0 0 20px rgba(255, 167, 38, 0.4))
                    drop-shadow(0 0 35px rgba(59, 130, 246, 0.25))
                    brightness(1.04)
                    contrast(1.02)
                  `,
                  transition: "all 0.3s ease"
                }}
              />
            </motion.div>
            <h1 className="text-2xl text-white font-bold">
              {selectedType ? `${selectedType.charAt(0).toUpperCase() + selectedType.slice(1)} Login` : "Welcome to FIDUS"}
            </h1>
            <h2 className="text-slate-400 mt-2 text-lg">
              {selectedType 
                ? `Professional Investment Management Platform` 
                : "Professional Investment Management Platform"
              }
            </h2>
            <p className="text-slate-500 mt-1 text-sm">
              {selectedType 
                ? `Sign in to access your ${selectedType} dashboard` 
                : "Please select your account type to continue"
              }
            </p>
          </CardHeader>

          <CardContent>
            {!selectedType ? (
              <div className="space-y-4">
                {/* Google Social Login */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 }}
                  className="mb-6"
                >
                  <div className="relative mb-4">
                    <div className="absolute inset-0 flex items-center">
                      <div className="w-full border-t border-slate-600" />
                    </div>
                    <div className="relative flex justify-center text-sm">
                      <span className="px-3 bg-slate-900 text-slate-400">Quick Access</span>
                    </div>
                  </div>
                  
                  <div className="google-social-login-wrapper">
                    <GoogleSocialLogin 
                      onLoginSuccess={(user, token) => {
                        console.log('Google login successful:', user);
                        onLogin({ ...user, type: user.user_type || 'client', isGoogleAuth: true });
                      }}
                      redirectTo="/dashboard"
                    />
                  </div>
                </motion.div>

                {/* Divider */}
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.3 }}
                  className="relative my-6"
                >
                  <div className="absolute inset-0 flex items-center">
                    <div className="w-full border-t border-slate-600" />
                  </div>
                  <div className="relative flex justify-center text-sm">
                    <span className="px-3 bg-slate-900 text-slate-400">Or continue with FIDUS account</span>
                  </div>
                </motion.div>

                <motion.button
                  className="login-option"
                  onClick={() => handleTypeSelect("client")}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4 }}
                >
                  <User className="inline mr-3" size={20} />
                  Client Login
                </motion.button>

                <motion.button
                  className="login-option admin"
                  onClick={() => handleTypeSelect("admin")}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.6 }}
                >
                  <Shield className="inline mr-3" size={20} />
                  Admin Login
                </motion.button>

                <motion.div
                  className="mt-8 pt-6 border-t border-slate-600"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.8 }}
                >
                  <button
                    className="w-full py-3 px-4 text-slate-300 text-sm border border-slate-600 rounded-lg hover:border-cyan-400 hover:text-cyan-400 transition-all duration-300"
                    onClick={() => setSelectedType("register")}
                  >
                    First Time Users - Create Account
                  </button>
                </motion.div>
              </div>
            ) : selectedType === "register" ? (
              <LeadRegistrationForm 
                onBack={() => setSelectedType(null)}
                onComplete={(userData) => {
                  // After successful lead registration, show success message
                  setSuccess(`Thank you for your interest, ${userData.name}! We will contact you within 24 hours to discuss your investment opportunities.`);
                  setTimeout(() => {
                    setSelectedType(null);
                  }, 5000);
                }}
              />
            ) : selectedType === "forgot_password" ? (
              <PasswordReset 
                userType={passwordResetType || "client"}
                onBack={() => {
                  setSelectedType(null);
                  setPasswordResetType(null);
                }}
                onComplete={() => {
                  setSelectedType(null);
                  setPasswordResetType(null);
                }}
              />
            ) : (
              <motion.div
                initial={{ opacity: 0, x: 50 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5 }}
                className="space-y-4"
              >
                <div className="space-y-2">
                  <Label htmlFor="username" className="text-slate-300">Username</Label>
                  <Input
                    id="username"
                    type="text"
                    value={credentials.username}
                    onChange={(e) => setCredentials({ ...credentials, username: e.target.value })}
                    className="bg-slate-800 border-slate-600 text-white"
                    placeholder="Enter username"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="password" className="text-slate-300">Password</Label>
                  <Input
                    id="password"
                    type="password"
                    value={credentials.password}
                    onChange={(e) => setCredentials({ ...credentials, password: e.target.value })}
                    className="bg-slate-800 border-slate-600 text-white"
                    placeholder="Enter password"
                    onKeyPress={(e) => e.key === 'Enter' && handleLogin()}
                  />
                </div>

                {error && (
                  <div className="text-red-400 text-sm text-center">
                    {error}
                  </div>
                )}

                <div className="text-xs text-slate-500 text-center bg-slate-800 p-3 rounded">
                  <strong>Secure Login:</strong><br />
                  Enter your credentials to access the FIDUS Investment Management platform
                </div>

                <div className="flex gap-3">
                  <Button
                    variant="outline"
                    onClick={handleBack}
                    className="flex-1"
                    disabled={loading}
                  >
                    Back
                  </Button>
                  <Button
                    onClick={handleLogin}
                    disabled={loading}
                    className="flex-1 bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600"
                  >
                    {loading ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Signing in...
                      </>
                    ) : (
                      "Sign In"
                    )}
                  </Button>
                </div>

                <div className="text-center mt-4 pt-4 border-t border-slate-600">
                  <button
                    onClick={() => {
                      setPasswordResetType(selectedType);
                      setSelectedType("forgot_password");
                    }}
                    className="text-cyan-400 text-sm hover:text-cyan-300 underline"
                    disabled={loading}
                  >
                    Forgot your password?
                  </button>
                </div>
              </motion.div>
            )}
          </CardContent>
        </Card>
      </motion.div>
      
      {/* Password Change Modal */}
      {showPasswordChange && userRequiringPasswordChange && (
        <PasswordChangeModal
          user={userRequiringPasswordChange}
          onPasswordChanged={handlePasswordChanged}
          onClose={() => setShowPasswordChange(false)}
        />
      )}
    </div>
  );
};

export default LoginSelection;