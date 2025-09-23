import React, { useState, useEffect, Suspense } from "react";
import { BrowserRouter } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import LoginSelection from "./components/LoginSelection";
import ClientDashboard from "./components/ClientDashboard";
import AdminDashboard from "./components/AdminDashboard";
import GoogleCallback from "./components/GoogleCallback";
import { ToastProvider } from "./components/ui/toast";
import { isAuthenticated, getCurrentUser } from "./utils/auth";
import "./App.css";

function App() {
  const [currentView, setCurrentView] = useState("login"); // DEMO FIX: Skip animation
  const [user, setUser] = useState(null);

  useEffect(() => {
    console.log('App initializing...');
    
    // Check for session_id immediately
    const urlParams = new URLSearchParams(window.location.search);
    const sessionId = urlParams.get('session_id');
    
    if (sessionId) {
      console.log('🔄 Found session_id, processing immediately...');
      
      // Process Google OAuth session immediately
      const processGoogleSession = async () => {
        try {
          const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/google/process-session`, {
            method: 'POST',
            headers: {
              'X-Session-ID': sessionId,
              'Content-Type': 'application/json'
            }
          });

          const data = await response.json();
          
          if (data.success) {
            console.log('✅ Google OAuth processed successfully');
            
            // Store Google authentication
            localStorage.setItem('google_session_token', sessionId);
            localStorage.setItem('google_api_authenticated', 'true');
            
            // Remove session_id from URL
            const newUrl = window.location.pathname;
            window.history.replaceState({}, '', newUrl);
            
            // Redirect to admin dashboard
            setCurrentView("admin");
            const adminUser = { username: 'admin', type: 'admin', isAdmin: true };
            setUser(adminUser);
            return;
          }
        } catch (error) {
          console.error('❌ Session processing failed:', error);
        }
        
        // Fallback to login
        setCurrentView("login");
      };
      
      processGoogleSession();
      return;
    }
    
    // Regular authentication check
    const token = localStorage.getItem('fidus_token');
    const storedUser = localStorage.getItem('fidus_user');
    
    if (token && storedUser && storedUser !== 'null') {
      try {
        const user = JSON.parse(storedUser);
        setUser(user);
        
        if (user.isAdmin || user.type === 'admin') {
          setCurrentView("admin");
        } else {
          setCurrentView("client");
        }
      } catch {
        setCurrentView("login");
      }
    } else {
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