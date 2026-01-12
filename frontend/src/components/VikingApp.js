/**
 * VIKING Trading Operations - Standalone Application
 * 
 * This is a completely separate application from FIDUS
 * Access at: /viking
 * 
 * Features:
 * - Separate login (viking_admin / viking2026)
 * - VIKING-only dashboard with all tabs
 * - No access to FIDUS features
 */

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import VikingLogin from './VikingLogin';
import VikingDashboard from './VikingDashboard';
import { Button } from './ui/button';
import { LogOut, User, Bell, Settings } from 'lucide-react';

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
  };

  // Show login if not authenticated
  if (!authenticated) {
    return <VikingLogin onLogin={handleLogin} />;
  }

  // Show VIKING dashboard when authenticated
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950">
      {/* VIKING Header */}
      <header className="bg-gray-900/80 border-b border-gray-800 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo & Title */}
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center shadow-lg shadow-amber-500/20">
                <span className="text-xl">⚔️</span>
              </div>
              <div>
                <h1 className="text-lg font-bold text-white">VIKING Trading</h1>
                <p className="text-xs text-gray-500">Operations Portal</p>
              </div>
            </div>

            {/* Right side */}
            <div className="flex items-center gap-4">
              {/* Status indicator */}
              <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 bg-green-500/10 border border-green-500/30 rounded-full">
                <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                <span className="text-xs text-green-400">Live</span>
              </div>

              {/* User info */}
              <div className="flex items-center gap-2 px-3 py-1.5 bg-gray-800/50 rounded-lg">
                <User className="w-4 h-4 text-amber-500" />
                <span className="text-sm text-gray-300 hidden sm:inline">{user}</span>
              </div>

              {/* Logout button */}
              <Button
                onClick={handleLogout}
                variant="ghost"
                size="sm"
                className="text-gray-400 hover:text-white hover:bg-gray-800"
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
      <footer className="border-t border-gray-800 mt-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between text-xs text-gray-600">
            <p>VIKING Trading Operations • Account 33627673</p>
            <p>Separate from FIDUS • Real-time MT4 Analytics</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default VikingApp;
