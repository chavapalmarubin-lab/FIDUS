import React, { useState, useEffect, Suspense } from "react";
import { BrowserRouter } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import LoginSelection from "./components/LoginSelection";
import ClientDashboard from "./components/ClientDashboard";
import AdminDashboard from "./components/AdminDashboard";
// Clean Google integration - removed unused imports
import { ToastProvider } from "./components/ui/toast";
import { isAuthenticated, getCurrentUser } from "./utils/auth";
import "./App.css";

function App() {
  const [currentView, setCurrentView] = useState("login"); // DEMO FIX: Skip animation
  const [user, setUser] = useState(null);

  useEffect(() => {
    console.log('🔍 App initializing - checking for OAuth callback...');
    
    // CRITICAL: Check for session_id from Google OAuth callback FIRST
    const urlParams = new URLSearchParams(window.location.search);
    const sessionId = urlParams.get('session_id');
    
    console.log('URL params:', window.location.search);
    console.log('Session ID detected:', sessionId);
    
    if (sessionId) {
      console.log('🔄 GOOGLE OAUTH CALLBACK DETECTED - Processing session_id:', sessionId);
      
      // Process the Google OAuth session immediately
      const processOAuthCallback = async () => {
        try {
          console.log('📡 Calling process-session endpoint...');
          
          const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/google/process-session`, {
            method: 'POST',
            headers: {
              'X-Session-ID': sessionId,
              'Content-Type': 'application/json'
            }
          });

          console.log('🔍 Process-session response status:', response.status);
          const data = await response.json();
          console.log('🔍 Process-session response data:', data);
          
          if (data.success) {
            console.log('✅ GOOGLE OAUTH SUCCESS - Session processed');
            
            // Store all authentication data
            localStorage.setItem('google_session_token', data.session_token);
            localStorage.setItem('google_api_authenticated', 'true');
            localStorage.setItem('emergent_session_token', data.emergent_session_token);
            
            // Store user data for admin session
            const adminUser = {
              id: 'user_admin_001', // Add proper user ID
              email: data.email,
              name: data.name,
              picture: data.picture,
              isAdmin: true,
              type: 'admin',
              loginType: 'emergent_oauth',
              isGoogleAuth: true, // Required for isAuthenticated() check
              googleApiAccess: true // Required for isAuthenticated() check
            };
            
            localStorage.setItem('fidus_user', JSON.stringify(adminUser));
            localStorage.setItem('fidus_token', data.session_token);
            
            // Clean URL immediately to prevent loops
            const newUrl = window.location.protocol + '//' + window.location.host + window.location.pathname;
            window.history.replaceState({}, '', newUrl);
            
            // Set user and admin view
            setUser(adminUser);
            setCurrentView("admin");
            
            console.log('SESSION COMPLETE - Redirecting to admin dashboard');
            return;
          } else {
            console.error('❌ Session processing failed:', data.detail);
            alert('Google authentication failed: ' + (data.detail || 'Unknown error'));
          }
        } catch (error) {
          console.error('❌ OAuth callback processing error:', error);
          alert('Google authentication error: ' + error.message);
        }
        
        // If we get here, something failed - go to login
        setCurrentView("login");
      };
      
      processOAuthCallback();
      return; // CRITICAL: Return here to prevent normal auth check
    }
    
    // Normal authentication check (no OAuth callback)
    console.log('📋 No OAuth callback - checking normal authentication...');
    
    const token = localStorage.getItem('fidus_token');
    const storedUser = localStorage.getItem('fidus_user');
    const googleAuth = localStorage.getItem('google_api_authenticated');
    
    console.log('Auth check:', { token: !!token, user: !!storedUser, googleAuth });
    
    if (token && storedUser && storedUser !== 'null') {
      try {
        const user = JSON.parse(storedUser);
        console.log('✅ User authenticated:', user.email || user.username);
        setUser(user);
        
        if (user.isAdmin || user.type === 'admin') {
          setCurrentView("admin");
        } else {
          setCurrentView("client");
        }
      } catch (error) {
        console.error('❌ Error parsing stored user:', error);
        setCurrentView("login");
      }
    } else {
      console.log('👤 No authentication found - showing login');
      setCurrentView("login");
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
            {/* EMERGENCY: Only show login and dashboard - no logo animation */}
            {currentView === "login" && (
              <motion.div
                key="login"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.3 }}
              >
                <LoginSelection onLogin={handleLogin} />
              </motion.div>
            )}
            
            {/* GoogleCallback component removed - clean Google integration */}
            
            {currentView === "client" && user && (
              <motion.div
                key="client"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.5 }}
              >
                <Suspense fallback={<div>Loading...</div>}>
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
                <Suspense fallback={<div>Loading...</div>}>
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