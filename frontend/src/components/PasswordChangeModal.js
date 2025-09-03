import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Alert, AlertDescription } from "./ui/alert";
import { Eye, EyeOff, Lock, AlertCircle, CheckCircle } from "lucide-react";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const PasswordChangeModal = ({ user, onPasswordChanged, onClose }) => {
  const [formData, setFormData] = useState({
    current_password: "",
    new_password: "",
    confirm_password: ""
  });
  const [showPasswords, setShowPasswords] = useState({
    current: false,
    new: false,
    confirm: false
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.current_password || !formData.new_password || !formData.confirm_password) {
      setError("Please fill in all fields");
      return;
    }

    if (formData.new_password !== formData.confirm_password) {
      setError("New passwords do not match");
      return;
    }

    if (formData.new_password.length < 6) {
      setError("New password must be at least 6 characters long");
      return;
    }

    try {
      setLoading(true);
      setError("");

      const response = await axios.post(`${API}/auth/change-password`, {
        username: user.username,
        current_password: formData.current_password,
        new_password: formData.new_password
      });

      if (response.data.success) {
        setSuccess("Password changed successfully! You can now login with your new password.");
        setTimeout(() => {
          onPasswordChanged();
        }, 2000);
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to change password");
    } finally {
      setLoading(false);
    }
  };

  const togglePasswordVisibility = (field) => {
    setShowPasswords(prev => ({
      ...prev,
      [field]: !prev[field]
    }));
  };

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      >
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.8, opacity: 0 }}
          className="bg-slate-800 rounded-lg p-6 max-w-md w-full mx-4"
        >
          <CardHeader className="text-center pb-4">
            <div className="flex justify-center mb-4">
              <div className="p-3 bg-yellow-500/20 rounded-full">
                <Lock className="h-8 w-8 text-yellow-400" />
              </div>
            </div>
            <CardTitle className="text-white text-xl">Password Change Required</CardTitle>
            <p className="text-slate-400 text-sm">
              You are using a temporary password. Please create a new secure password to continue.
            </p>
          </CardHeader>

          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Current Password */}
              <div>
                <Label className="text-slate-300">Current Temporary Password *</Label>
                <div className="relative">
                  <Input
                    type={showPasswords.current ? "text" : "password"}
                    value={formData.current_password}
                    onChange={(e) => setFormData({...formData, current_password: e.target.value})}
                    placeholder="Enter your temporary password"
                    className="mt-1 bg-slate-700 border-slate-600 text-white pr-10"
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="absolute right-0 top-1 h-8 w-8 text-slate-400 hover:text-white"
                    onClick={() => togglePasswordVisibility('current')}
                  >
                    {showPasswords.current ? <EyeOff size={16} /> : <Eye size={16} />}
                  </Button>
                </div>
              </div>

              {/* New Password */}
              <div>
                <Label className="text-slate-300">New Password *</Label>
                <div className="relative">
                  <Input
                    type={showPasswords.new ? "text" : "password"}
                    value={formData.new_password}
                    onChange={(e) => setFormData({...formData, new_password: e.target.value})}
                    placeholder="Create a secure password"
                    className="mt-1 bg-slate-700 border-slate-600 text-white pr-10"
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="absolute right-0 top-1 h-8 w-8 text-slate-400 hover:text-white"
                    onClick={() => togglePasswordVisibility('new')}
                  >
                    {showPasswords.new ? <EyeOff size={16} /> : <Eye size={16} />}
                  </Button>
                </div>
                <p className="text-xs text-slate-400 mt-1">
                  Minimum 6 characters
                </p>
              </div>

              {/* Confirm Password */}
              <div>
                <Label className="text-slate-300">Confirm New Password *</Label>
                <div className="relative">
                  <Input
                    type={showPasswords.confirm ? "text" : "password"}
                    value={formData.confirm_password}
                    onChange={(e) => setFormData({...formData, confirm_password: e.target.value})}
                    placeholder="Confirm your new password"
                    className="mt-1 bg-slate-700 border-slate-600 text-white pr-10"
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="absolute right-0 top-1 h-8 w-8 text-slate-400 hover:text-white"
                    onClick={() => togglePasswordVisibility('confirm')}
                  >
                    {showPasswords.confirm ? <EyeOff size={16} /> : <Eye size={16} />}
                  </Button>
                </div>
              </div>

              {/* Error Alert */}
              {error && (
                <Alert className="bg-red-900/20 border-red-600">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription className="text-red-400">{error}</AlertDescription>
                </Alert>
              )}

              {/* Success Alert */}
              {success && (
                <Alert className="bg-green-900/20 border-green-600">
                  <CheckCircle className="h-4 w-4" />
                  <AlertDescription className="text-green-400">{success}</AlertDescription>
                </Alert>
              )}

              {/* Submit Button */}
              <Button
                type="submit"
                disabled={loading}
                className="w-full bg-yellow-600 hover:bg-yellow-700 text-white"
              >
                {loading ? "Changing Password..." : "Change Password"}
              </Button>
            </form>

            <div className="mt-4 p-3 bg-slate-700/50 rounded">
              <p className="text-xs text-slate-400">
                <strong>Password Requirements:</strong> Minimum 6 characters. 
                Choose a secure password that you haven't used before.
              </p>
            </div>
          </CardContent>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default PasswordChangeModal;