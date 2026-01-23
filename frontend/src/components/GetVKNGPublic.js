/**
 * VKNG AI Trading Operations - Public Dashboard (No Login Required)
 * 
 * Publicly accessible version of VIKING dashboard
 * Access at: /getvkng
 * 
 * This is for sharing with investors and prospects - no authentication required
 */

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import VikingDashboard from './VikingDashboard';
import { TrendingUp, ExternalLink } from 'lucide-react';

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

const GetVKNGPublic = () => {
  // Track active account info from dashboard
  const [activeAccount, setActiveAccount] = useState({
    account: '885822',
    broker: 'MEXAtlantic',
    strategy: 'CORE'
  });

  return (
    <div 
      className="min-h-screen"
      style={{ backgroundColor: VKNG_COLORS.dark }}
    >
      {/* VKNG AI Header - Public Version */}
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
                  Trading Analytics
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
                <TrendingUp className="w-4 h-4" style={{ color: activeAccount.strategy === 'PRO' ? VKNG_COLORS.purple : '#3B82F6' }} />
                <span className="text-xs" style={{ color: VKNG_COLORS.textSecondary }}>
                  {activeAccount.strategy} • {activeAccount.account}
                </span>
              </div>
            </div>

            {/* Right side - Link to main site */}
            <div className="flex items-center gap-3">
              <a
                href="https://getvkng.com"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 px-4 py-2 rounded-lg transition-all hover:opacity-80"
                style={{ 
                  backgroundColor: VKNG_COLORS.purple,
                  color: VKNG_COLORS.textPrimary
                }}
              >
                <span className="text-sm font-medium">Learn More</span>
                <ExternalLink className="w-4 h-4" />
              </a>
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
          <VikingDashboard onAccountChange={setActiveAccount} isPublic={true} />
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
                VKNG AI Trading Analytics
              </p>
            </div>
            <div className="flex items-center gap-4">
              <a 
                href="https://getvkng.com" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-xs hover:underline"
                style={{ color: VKNG_COLORS.purple }}
              >
                getvkng.com
              </a>
              <p 
                className="text-xs"
                style={{ color: `${VKNG_COLORS.textSecondary}40` }}
              >
                Elite Traders + AI Execution
              </p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default GetVKNGPublic;
