/**
 * VKNG AI Trading Operations - Standalone Application
 * 
 * Branded with official VKNG AI colors and logo from getvkng.com
 * Access at: /viking
 */

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import VikingLogin from './VikingLogin';
import VikingDashboard from './VikingDashboard';
import { Button } from './ui/button';
import { LogOut, User, Bell, TrendingUp } from 'lucide-react';

// VKNG AI Brand Colors (from getvkng.com - Purple/Magenta theme)
const VKNG_COLORS = {
  purple: '#9B27FF',
  purpleLight: '#A239EA',
  magenta: '#CC00FF',
  pink: '#E621A4',
  dark: '#0A112B',
  darkGray: '#0D1629',
  mediumGray: '#1A2744',
  textPrimary: '#FFFFFF',
  textSecondary: '#9CA3AF',
  success: '#22C55E'
};

const VikingApp = () => {
  // Check for existing VIKING session on initial load
  const [authenticated, setAuthenticated] = useState(() => {
    return localStorage.getItem('viking_authenticated') === 'true';
  });
  const [user, setUser] = useState(() => {
    return localStorage.getItem('viking_user') || null;
  });

  const handleLogin = (success) => {
    if (success) {
      setAuthenticated(true);
      setUser(localStorage.getItem('viking_user'));
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('viking_authenticated');
    localStorage.removeItem('viking_user');
    setAuthenticated(false);
    setUser(null);
    // Ensure we stay on /viking route
    if (window.location.pathname !== '/viking') {
      window.location.href = '/viking';
    }
  };

  // Show login if not authenticated
  if (!authenticated) {
    return <VikingLogin onLogin={handleLogin} />;
  }

  // Show VKNG AI dashboard when authenticated
  return (
    <div 
      className="min-h-screen"
      style={{ backgroundColor: VKNG_COLORS.dark }}
    >
      {/* VKNG AI Header */}
      <header 
        className="sticky top-0 z-50 backdrop-blur-xl"
        style={{ 
          backgroundColor: `${VKNG_COLORS.darkGray}E0`,
          borderBottom: `1px solid ${VKNG_COLORS.mediumGray}`
        }}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo & Title */}
            <div className="flex items-center gap-4">
              <img 
                src="/vkng-logo.png" 
                alt="VKNG AI" 
                className="h-10 w-auto"
                style={{ filter: 'drop-shadow(0 0 15px rgba(155, 39, 255, 0.5))' }}
              />
              <div className="hidden sm:block">
                <h1 
                  className="text-lg font-bold"
                  style={{ color: VKNG_COLORS.textPrimary }}
                >
                  VKNG AI
                </h1>
                <p 
                  className="text-xs -mt-0.5"
                  style={{ color: VKNG_COLORS.textSecondary }}
                >
                  Trading Operations
                </p>
              </div>
            </div>

            {/* Center - Status */}
            <div className="hidden md:flex items-center gap-6">
              <div 
                className="flex items-center gap-2 px-4 py-1.5 rounded-full"
                style={{ 
                  backgroundColor: `${VKNG_COLORS.success}15`,
                  border: `1px solid ${VKNG_COLORS.success}30`
                }}
              >
                <div 
                  className="w-2 h-2 rounded-full animate-pulse"
                  style={{ backgroundColor: VKNG_COLORS.success }}
                />
                <span className="text-xs font-medium" style={{ color: VKNG_COLORS.success }}>
                  LIVE
                </span>
              </div>
              
              <div 
                className="flex items-center gap-2 px-3 py-1.5 rounded-lg"
                style={{ backgroundColor: VKNG_COLORS.mediumGray }}
              >
                <TrendingUp className="w-4 h-4" style={{ color: VKNG_COLORS.purple }} />
                <span className="text-xs" style={{ color: VKNG_COLORS.textSecondary }}>
                  Account 33627673
                </span>
              </div>
            </div>

            {/* Right side */}
            <div className="flex items-center gap-3">
              {/* User info */}
              <div 
                className="flex items-center gap-2 px-3 py-1.5 rounded-lg"
                style={{ backgroundColor: VKNG_COLORS.mediumGray }}
              >
                <User className="w-4 h-4" style={{ color: VKNG_COLORS.purple }} />
                <span 
                  className="text-sm hidden sm:inline"
                  style={{ color: VKNG_COLORS.textPrimary }}
                >
                  {user}
                </span>
              </div>

              {/* Logout button */}
              <Button
                onClick={handleLogout}
                variant="ghost"
                size="sm"
                className="border-0 transition-colors"
                style={{ 
                  color: VKNG_COLORS.textSecondary,
                  backgroundColor: 'transparent'
                }}
                data-testid="viking-logout-btn"
              >
                <LogOut className="w-4 h-4 mr-2" />
                <span className="hidden sm:inline">Logout</span>
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          <VikingDashboard />
        </motion.div>
      </main>

      {/* Footer */}
      <footer style={{ borderTop: `1px solid ${VKNG_COLORS.mediumGray}` }}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-2">
            <div className="flex items-center gap-3">
              <img 
                src="/vkng-logo.png" 
                alt="VKNG AI" 
                className="h-6 w-auto opacity-70"
              />
              <p 
                className="text-xs"
                style={{ color: `${VKNG_COLORS.textSecondary}60` }}
              >
                VKNG AI Trading Operations
              </p>
            </div>
            <p 
              className="text-xs"
              style={{ color: `${VKNG_COLORS.textSecondary}40` }}
            >
              Elite Traders + AI Execution • Real-time MT4 Analytics
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default VikingApp;
