import React, { useState, useEffect, Suspense, lazy } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
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
    const initializeAuth = () => {
      console.log('=== APP.JS USEEFFECT DEBUGGING ===');
      console.log('Current URL:', window.location.href);
      console.log('Current localStorage:', {
        fidus_user: localStorage.getItem('fidus_user'),
        google_session_token: localStorage.getItem('google_session_token')
      });
      
      // Check for skip animation parameter (for production testing)
      const urlParams = new URLSearchParams(window.location.search);
      const skipAnimation = urlParams.get('skip_animation') === 'true';
      const googleAuthSuccess = urlParams.get('google_auth') === 'success';
      console.log('Skip animation:', skipAnimation, 'Google auth success:', googleAuthSuccess);
      
      // Handle Google OAuth callback
      if (window.location.pathname === '/admin/google-callback') {
        console.log('Setting view to google-callback');
        setCurrentView('google-callback');
        return;
      }
      
      // Custom authentication check that accounts for different token types
      if (isAuthenticated()) {
        console.log('User is authenticated');
        const currentUser = getCurrentUser();
        console.log('Current user:', currentUser);
        setUser(currentUser);
        
        // Ensure localStorage is available
        if (typeof window !== 'undefined' && window.localStorage) {
          // Determine view based on user type
          if (currentUser?.isAdmin || currentUser?.type === 'admin') {
            console.log('Setting view to admin');
            setCurrentView("admin");
          } else {
            console.log('Setting view to client');
            setCurrentView("client");
          }
        } else {
          console.log('Setting view to login (no localStorage)');
          setCurrentView("login");
        }
      } else {
        console.log('User is not authenticated');
        // PERMANENT FIX: Always skip animation to prevent dark screen issue
        console.log('Skipping animation for all users - going to login');
        setCurrentView("login");
      }
    };

    // Only run if window is available (client-side)
    if (typeof window !== 'undefined') {
      // Small delay to ensure localStorage is available
      setTimeout(initializeAuth, 100);
    } else {
      initializeAuth();
    }
  }, []);

  const handleLogin = (userData) => {
    console.log('App.js: handleLogin called with:', userData);
    setUser(userData);
    
    // Store JWT token if present
    if (userData?.token) {
      localStorage.setItem('fidus_token', userData.token);
      console.log('JWT token stored in localStorage');
    }
    
    // Store user data
    localStorage.setItem('fidus_user', JSON.stringify(userData));
    
    if (userData?.isAdmin || userData?.type === 'admin') {
      setCurrentView("admin");
    } else {
      setCurrentView("client");
    }
  };

  const handleLogout = async () => {
    console.log('App.js: handleLogout called');
    
    try {
      // Call logout endpoint for Google Social Login
      await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/auth/google/logout`, {
        method: 'POST',
        credentials: 'include'
      });
    } catch (error) {
      console.error('Logout error:', error);
    }
    
    // Clear all auth data including JWT token
    localStorage.removeItem("fidus_user");
    localStorage.removeItem("fidus_token");
    localStorage.removeItem("google_session_token");
    localStorage.removeItem("google_api_authenticated");
    setUser(null);
    setCurrentView("login");
  };

  return (
    <BrowserRouter>
      <ToastProvider>
        <div className="App">
          <AnimatePresence mode="wait">
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
                <GoogleCallback onSuccess={handleLogin} />
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
  </BrowserRouter>
  );
}

export default App;