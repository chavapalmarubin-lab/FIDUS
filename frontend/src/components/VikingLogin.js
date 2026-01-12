/**
 * VKNG AI Trading Operations - Login Page
 * 
 * Branded with official VKNG AI colors and logo
 * Access at: /viking
 */

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { 
  Eye, 
  EyeOff, 
  Loader2,
  AlertCircle,
  ChevronRight
} from 'lucide-react';

// VKNG AI Brand Colors (from getvkng.com)
const VKNG_COLORS = {
  gold: '#D4AF37',
  goldLight: '#F4D03F',
  goldDark: '#B8860B',
  dark: '#0A0A0A',
  darkGray: '#141414',
  mediumGray: '#1A1A1A',
  textPrimary: '#FFFFFF',
  textSecondary: '#9CA3AF',
  success: '#22C55E',
  danger: '#EF4444'
};

// VKNG AI credentials
const VKNG_CREDENTIALS = {
  username: 'viking_admin',
  password: 'viking2026'
};

const VikingLogin = ({ onLogin }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 800));

    if (username === VKNG_CREDENTIALS.username && password === VKNG_CREDENTIALS.password) {
      localStorage.setItem('viking_authenticated', 'true');
      localStorage.setItem('viking_user', username);
      onLogin(true);
    } else {
      setError('Invalid credentials. Please contact your account manager.');
    }
    
    setLoading(false);
  };

  return (
    <div 
      className="min-h-screen flex items-center justify-center p-4 relative overflow-hidden"
      style={{ backgroundColor: VKNG_COLORS.dark }}
    >
      {/* Animated background gradient */}
      <div className="absolute inset-0">
        <div 
          className="absolute inset-0 opacity-30"
          style={{
            background: `radial-gradient(ellipse at 50% 0%, ${VKNG_COLORS.gold}20 0%, transparent 50%)`
          }}
        />
        <div 
          className="absolute inset-0 opacity-20"
          style={{
            background: `radial-gradient(ellipse at 80% 80%, ${VKNG_COLORS.gold}10 0%, transparent 40%)`
          }}
        />
      </div>

      {/* Grid pattern overlay */}
      <div 
        className="absolute inset-0 opacity-5"
        style={{
          backgroundImage: `linear-gradient(${VKNG_COLORS.gold}20 1px, transparent 1px), linear-gradient(90deg, ${VKNG_COLORS.gold}20 1px, transparent 1px)`,
          backgroundSize: '50px 50px'
        }}
      />
      
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
        className="relative z-10 w-full max-w-md"
      >
        <Card 
          className="border-0 shadow-2xl backdrop-blur-xl"
          style={{ 
            backgroundColor: `${VKNG_COLORS.darkGray}F0`,
            boxShadow: `0 25px 50px -12px ${VKNG_COLORS.gold}20`
          }}
        >
          <CardHeader className="text-center pb-4 pt-8">
            {/* VKNG AI Logo */}
            <motion.div 
              className="mx-auto mb-6"
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: 0.2, duration: 0.5 }}
            >
              <img 
                src="/vkng-logo.png" 
                alt="VKNG AI" 
                className="h-20 w-auto mx-auto"
                style={{ filter: 'drop-shadow(0 0 30px rgba(212, 175, 55, 0.5))' }}
              />
            </motion.div>
            
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.4 }}
            >
              <h1 
                className="text-3xl font-bold tracking-tight"
                style={{ color: VKNG_COLORS.textPrimary }}
              >
                VKNG AI
              </h1>
              <p 
                className="text-sm mt-2"
                style={{ color: VKNG_COLORS.textSecondary }}
              >
                Trading Operations Portal
              </p>
              <div 
                className="mt-3 inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs"
                style={{ 
                  backgroundColor: `${VKNG_COLORS.gold}15`,
                  color: VKNG_COLORS.gold,
                  border: `1px solid ${VKNG_COLORS.gold}30`
                }}
              >
                <span className="w-2 h-2 rounded-full animate-pulse" style={{ backgroundColor: VKNG_COLORS.success }}></span>
                Account 33627673 • MEXAtlantic
              </div>
            </motion.div>
          </CardHeader>
          
          <CardContent className="pt-2 pb-8 px-8">
            <form onSubmit={handleLogin} className="space-y-5">
              {error && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="rounded-lg p-3 flex items-center gap-2"
                  style={{ 
                    backgroundColor: `${VKNG_COLORS.danger}15`,
                    border: `1px solid ${VKNG_COLORS.danger}30`
                  }}
                >
                  <AlertCircle className="w-4 h-4" style={{ color: VKNG_COLORS.danger }} />
                  <span className="text-sm" style={{ color: VKNG_COLORS.danger }}>{error}</span>
                </motion.div>
              )}
              
              <div className="space-y-2">
                <Label 
                  htmlFor="username" 
                  className="text-sm font-medium"
                  style={{ color: VKNG_COLORS.textSecondary }}
                >
                  Username
                </Label>
                <Input
                  id="username"
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="h-12 border-0 text-white placeholder:text-gray-500"
                  style={{ 
                    backgroundColor: VKNG_COLORS.mediumGray,
                    boxShadow: 'inset 0 2px 4px rgba(0,0,0,0.3)'
                  }}
                  placeholder="Enter your username"
                  required
                  data-testid="viking-username-input"
                />
              </div>
              
              <div className="space-y-2">
                <Label 
                  htmlFor="password"
                  className="text-sm font-medium"
                  style={{ color: VKNG_COLORS.textSecondary }}
                >
                  Password
                </Label>
                <div className="relative">
                  <Input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="h-12 border-0 text-white pr-12 placeholder:text-gray-500"
                    style={{ 
                      backgroundColor: VKNG_COLORS.mediumGray,
                      boxShadow: 'inset 0 2px 4px rgba(0,0,0,0.3)'
                    }}
                    placeholder="Enter your password"
                    required
                    data-testid="viking-password-input"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-4 top-1/2 -translate-y-1/2 transition-colors"
                    style={{ color: VKNG_COLORS.textSecondary }}
                  >
                    {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                </div>
              </div>
              
              <Button
                type="submit"
                disabled={loading}
                className="w-full h-12 text-base font-semibold border-0 mt-2 transition-all duration-300"
                style={{ 
                  background: `linear-gradient(135deg, ${VKNG_COLORS.gold} 0%, ${VKNG_COLORS.goldDark} 100%)`,
                  color: VKNG_COLORS.dark,
                  boxShadow: `0 4px 20px ${VKNG_COLORS.gold}40`
                }}
                data-testid="viking-login-btn"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                    Authenticating...
                  </>
                ) : (
                  <>
                    Access Portal
                    <ChevronRight className="w-5 h-5 ml-2" />
                  </>
                )}
              </Button>
            </form>
            
            <div className="mt-8 pt-6" style={{ borderTop: `1px solid ${VKNG_COLORS.mediumGray}` }}>
              <p className="text-center text-xs" style={{ color: VKNG_COLORS.textSecondary }}>
                Real-time MT4 Performance Analytics
              </p>
              <p className="text-center text-xs mt-1" style={{ color: `${VKNG_COLORS.textSecondary}80` }}>
                Elite Traders + AI Execution
              </p>
            </div>
          </CardContent>
        </Card>
        
        {/* Demo credentials */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1 }}
          className="mt-6 text-center"
        >
          <p className="text-xs" style={{ color: `${VKNG_COLORS.textSecondary}60` }}>
            Demo: viking_admin / viking2026
          </p>
        </motion.div>
      </motion.div>
    </div>
  );
};

export default VikingLogin;
