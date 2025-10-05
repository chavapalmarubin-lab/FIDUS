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
    
    // Check for OAuth callback parameters
    const urlParams = new URLSearchParams(window.location.search);
    const googleAuthSuccess = urlParams.get('google_auth') === 'success';  // Direct Google OAuth (legacy)
    const googleAuthTab = urlParams.get('tab');
    
    // NEW: Emergent Auth session_id from URL fragment (format: #session_id=xxx)
    const urlFragment = window.location.hash.substring(1);
    const fragmentParams = new URLSearchParams(urlFragment);
    const emergentSessionId = fragmentParams.get('session_id');
    
    // NEW: Individual Google OAuth callback parameters
    const googleOAuthCode = urlParams.get('code');  // Individual Google OAuth authorization code
    const googleOAuthState = urlParams.get('state');  // Individual Google OAuth state
    const googleOAuthError = urlParams.get('error');  // Individual Google OAuth error
    
    console.log('URL params:', window.location.search);
    console.log('Session ID detected:', emergentSessionId);
    console.log('Google Auth Success:', googleAuthSuccess);
    console.log('Individual Google OAuth Code:', googleOAuthCode ? 'Present' : 'None');
    console.log('Individual Google OAuth State:', googleOAuthState);
    console.log('Individual Google OAuth Error:', googleOAuthError);
    
    // Handle Individual Google OAuth callback (NEW)
    if (googleOAuthCode && googleOAuthState) {
      console.log('✅ INDIVIDUAL GOOGLE OAUTH CALLBACK DETECTED - Processing...');
      
      // Process individual Google OAuth callback
      const processIndividualOAuthCallback = async () => {
        try {
          console.log('📡 Processing individual Google OAuth callback...');
          
          const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/google/individual-callback`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('fidus_token')}`,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              code: googleOAuthCode,
              state: googleOAuthState
            })
          });

          console.log('🔍 Individual OAuth callback response status:', response.status);
          const data = await response.json();
          console.log('🔍 Individual OAuth callback response data:', data);
          
          if (data.success) {
            console.log('✅ INDIVIDUAL GOOGLE OAUTH SUCCESS - Connection established');
            
            // Store authentication success for this admin
            localStorage.setItem('individual_google_authenticated', 'true');
            localStorage.setItem('individual_google_completed', new Date().toISOString());
            
            // Clean URL and redirect to Google Workspace tab
            const baseUrl = window.location.origin + window.location.pathname;
            const newUrl = `${baseUrl}?skip_animation=true&tab=google-workspace`;
            window.history.replaceState({}, '', newUrl);
            
            // Show success message and redirect
            console.log('🚀 Individual Google authentication successful - redirecting to Google Workspace');
            
            setTimeout(() => {
              window.location.reload();
            }, 1000);
          } else {
            console.error('❌ Individual Google OAuth failed:', data.message);
            // Clean URL and redirect back
            const baseUrl = window.location.origin + window.location.pathname;
            const newUrl = `${baseUrl}?skip_animation=true&tab=google-workspace&oauth_error=${encodeURIComponent(data.message)}`;
            window.history.replaceState({}, '', newUrl);
            
            setTimeout(() => {
              window.location.reload();
            }, 1000);
          }
          
        } catch (error) {
          console.error('❌ Individual Google OAuth processing failed:', error);
          // Clean URL and redirect back with error
          const baseUrl = window.location.origin + window.location.pathname;
          const newUrl = `${baseUrl}?skip_animation=true&tab=google-workspace&oauth_error=${encodeURIComponent(error.message)}`;
          window.history.replaceState({}, '', newUrl);
          
          setTimeout(() => {
            window.location.reload();
          }, 1000);
        }
      };
      
      processIndividualOAuthCallback();
      return;
    }
    
    // Handle Individual Google OAuth error (NEW)
    if (googleOAuthError) {
      console.error('❌ INDIVIDUAL GOOGLE OAUTH ERROR:', googleOAuthError);
      
      // Clean URL and redirect back with error
      const baseUrl = window.location.origin + window.location.pathname;
      const newUrl = `${baseUrl}?skip_animation=true&tab=google-workspace&oauth_error=${encodeURIComponent(googleOAuthError)}`;
      window.history.replaceState({}, '', newUrl);
      
      setTimeout(() => {
        window.location.reload();
      }, 1000);
      
      return;
    }
    
    // Handle Direct Google OAuth success
    if (googleAuthSuccess) {
      console.log('✅ DIRECT GOOGLE OAUTH SUCCESS - Authentication completed');
      
      // Store authentication success
      localStorage.setItem('google_api_authenticated', 'true');
      localStorage.setItem('google_auth_completed', new Date().toISOString());
      
      // CRITICAL: Preserve admin login state during OAuth callback
      const existingToken = localStorage.getItem('token');
      const existingUser = localStorage.getItem('currentUser');
      
      if (!existingToken || !existingUser) {
        console.log('⚠️ Admin session not found, restoring admin login state');
        // Set default admin state for OAuth callback
        const adminUser = {
          username: 'admin',
          type: 'admin',
          isAdmin: true,
          name: 'Admin User'
        };
        localStorage.setItem('currentUser', JSON.stringify(adminUser));
        localStorage.setItem('isAuthenticated', 'true');
      }
      
      // Clean URL and redirect to admin dashboard with Connection Monitor tab
      const baseUrl = window.location.origin + window.location.pathname;
      const newUrl = `${baseUrl}?skip_animation=true&tab=connection-monitor`;
      window.history.replaceState({}, '', newUrl);
      
      // Show success message
      console.log('🚀 Google authentication successful - redirecting to Connection Monitor');
      
      // Force page refresh to show Connection Monitor with connected status
      setTimeout(() => {
        window.location.reload();
      }, 1000);
      
      return;
    }
    
    // Handle Emergent OAuth (existing logic)
    if (emergentSessionId) {
      console.log('🔄 GOOGLE OAUTH CALLBACK DETECTED - Processing session_id:', emergentSessionId);
      
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