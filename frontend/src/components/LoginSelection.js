import React, { useState } from "react";
import { motion } from "framer-motion";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { User, Shield } from "lucide-react";
import UserRegistration from "./UserRegistration";
import PasswordReset from "./PasswordReset";
import PasswordChangeModal from "./PasswordChangeModal";
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

  const handleTypeSelect = (type) => {
    setSelectedType(type);
    setError("");
    // Set default credentials for demo
    if (type === "client") {
      setCredentials({ username: "client1", password: "password123" });
    } else {
      setCredentials({ username: "admin", password: "password123" });
    }
  };

  const handleLogin = async () => {
    if (!credentials.username || !credentials.password) {
      setError("Please enter username and password");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await axios.post(`${API}/auth/login`, {
        username: credentials.username,
        password: credentials.password,
        user_type: selectedType
      });

      // Check if password change is required
      if (response.data.must_change_password) {
        setUserRequiringPasswordChange(response.data);
        setShowPasswordChange(true);
        setLoading(false);
        return;
      }

      onLogin(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Login failed");
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
              className="mb-4"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.3, duration: 0.8 }}
            >
              <img 
                src="https://customer-assets.emergentagent.com/job_fidus-portal/artifacts/hxt31ed0_FIDUS%20LOGO%20SMALL.jpg"
                alt="FIDUS Logo"
                style={{
                  width: "250px",
                  height: "auto",
                  margin: "0 auto",
                  display: "block",
                  filter: "drop-shadow(0 0 15px rgba(255, 167, 38, 0.3))"
                }}
              />
            </motion.div>
            <CardTitle className="text-2xl text-white">
              {selectedType ? "Login" : "Welcome to FIDUS"}
            </CardTitle>
            <p className="text-slate-400 mt-2">
              {selectedType 
                ? `Sign in to your ${selectedType} account` 
                : "Please select your account type"
              }
            </p>
          </CardHeader>

          <CardContent>
            {!selectedType ? (
              <div className="space-y-4">
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
              <UserRegistration 
                onBack={() => setSelectedType(null)}
                onComplete={(userData) => {
                  // After successful registration, automatically log them in
                  onLogin(userData);
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
                  <strong>Demo Credentials:</strong><br />
                  Client: client1 / password123<br />
                  Admin: admin / password123
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
                    {loading ? "Signing in..." : "Sign In"}
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