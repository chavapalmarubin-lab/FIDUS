import React, { useState, useEffect, Suspense, lazy } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import LogoAnimation from "./components/LogoAnimation";
import LoginSelection from "./components/LoginSelection";
import GoogleCallback from "./components/GoogleCallback";
import { ToastProvider } from "./components/ui/toast";
import { isAuthenticated, getCurrentUser } from "./utils/auth";
import "./App.css";

// Lazy load heavy components for better performance
const ClientDashboard = lazy(() => import("./components/ClientDashboard"));
const AdminDashboard = lazy(() => import("./components/AdminDashboard"));

// Loading spinner component for Suspense fallback
const LoadingSpinner = () => (
  <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center">
    <div className="text-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-400 mx-auto mb-4"></div>
      <h2 className="text-xl text-white font-semibold">Loading FIDUS Dashboard...</h2>
      <p className="text-slate-400 mt-2">Please wait while we prepare your workspace</p>
    </div>
  </div>
);

function App() {
  const [currentView, setCurrentView] = useState("logo"); // logo, login, client, admin
  const [user, setUser] = useState(null);

  useEffect(() => {
    console.log('=== APP.JS USEEFFECT DEBUGGING ===');
    console.log('Current URL:', window.location.href);
    console.log('Current localStorage:', {
      fidus_user: localStorage.getItem('fidus_user'),
      google_session_token: localStorage.getItem('google_session_token')
    });
    
    // Check for skip animation parameter (for production testing)
    const urlParams = new URLSearchParams(window.location.search);
    const skipAnimation = urlParams.get('skip_animation') === 'true';
    console.log('Skip animation:', skipAnimation);
    
    // Handle Google OAuth callback
    if (window.location.pathname === '/admin/google-callback') {
      console.log('Setting view to google-callback');
      setCurrentView('google-callback');
      return;
    }
    
    // Check if user is already authenticated FIRST
    const authenticated = isAuthenticated();
    console.log('Is authenticated:', authenticated);
    
    if (authenticated) {
      const userData = getCurrentUser();
      console.log('User data:', userData);
      if (userData) {
        console.log('Setting user and view to:', userData.type);
        setUser(userData);
        setCurrentView(userData.type === "admin" ? "admin" : "client");
        return; // CRITICAL: Return here to prevent further processing
      }
    }
    
    if (skipAnimation) {
      // Skip animation for testing/production - but only if not authenticated
      console.log('Setting view to login (skip animation)');
      setCurrentView("login");
    } else {
      // Clear any existing user session to always show logo animation
      // BUT only if not authenticated (to prevent clearing Google auth)
      if (!authenticated) {
        console.log('Clearing localStorage (not authenticated)');
        localStorage.removeItem("fidus_user");
      } else {
        console.log('NOT clearing localStorage (user is authenticated)');
      }
      
      // Always start with logo animation
      console.log('Setting view to logo');
      setCurrentView("logo");
    }
  }, []);

  // Update document title based on current view
  useEffect(() => {
    const titles = {
      logo: "FIDUS Investment Management | Loading...",
      login: "FIDUS Investment Management | Secure Login",
      "google-callback": "FIDUS Investment Management | Google Authentication",
      client: `FIDUS Investment Management | Client Portal${user ? ` - ${user.username}` : ''}`,
      admin: `FIDUS Investment Management | Admin Dashboard${user ? ` - ${user.username}` : ''}`
    };
    
    document.title = titles[currentView] || "FIDUS Investment Management";
  }, [currentView, user]);

  const handleLogin = (userData) => {
    setUser(userData);
    localStorage.setItem("fidus_user", JSON.stringify(userData));
    setCurrentView(userData.type === "admin" ? "admin" : "client");
  };

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem("fidus_user");
    setCurrentView("login");
  };

  const handleAnimationComplete = () => {
    setCurrentView("login");
  };

  return (
    <ToastProvider>
      <div className="App">
        <AnimatePresence mode="wait">
        {currentView === "logo" && (
          <motion.div
            key="logo"
            initial={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.5 }}
          >
            <LogoAnimation onComplete={handleAnimationComplete} />
          </motion.div>
        )}
        
        {currentView === "login" && (
          <motion.div
            key="login"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.5 }}
          >
            <LoginSelection onLogin={handleLogin} />
          </motion.div>
        )}
        
        {currentView === "google-callback" && (
          <motion.div
            key="google-callback"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.5 }}
          >
            <GoogleCallback />
          </motion.div>
        )}
        
        {currentView === "client" && user && (
          <motion.div
            key="client"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Suspense fallback={<LoadingSpinner />}>
              <ClientDashboard user={user} onLogout={handleLogout} />
            </Suspense>
          </motion.div>
        )}
        
        {currentView === "admin" && user && (
          <motion.div
            key="admin"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Suspense fallback={<LoadingSpinner />}>
              <AdminDashboard user={user} onLogout={handleLogout} />
            </Suspense>
          </motion.div>
        )}
        </AnimatePresence>
      </div>
    </ToastProvider>
  );
}

export default App;