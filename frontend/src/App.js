import React, { useState, useEffect, Suspense, lazy } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import GoogleCallback from "./components/GoogleCallback";
import LoginPage from "./components/LoginPage";
import SignupPage from "./components/SignupPage";
import { ToastProvider } from "./components/ui/toast";
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
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Check authentication status on app load
  useEffect(() => {
    const checkAuth = async () => {
      try {
        // Check for existing session
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/auth/me`, {
          credentials: 'include'
        });

        if (response.ok) {
          const data = await response.json();
          if (data.success && data.user) {
            setUser(data.user);
          }
        }
      } catch (error) {
        console.log('No existing authentication found');
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  const handleLogout = async () => {
    try {
      // Call logout endpoint
      await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/auth/google/logout`, {
        method: 'POST',
        credentials: 'include'
      });
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear local storage and state
      localStorage.removeItem('fidus_user');
      localStorage.removeItem('fidus_token');
      localStorage.removeItem('google_session_token');
      setUser(null);
    }
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <BrowserRouter>
      <ToastProvider>
        <div className="App">
          <Routes>
            {/* Public Routes */}
            <Route 
              path="/login" 
              element={!user ? <LoginPage /> : <Navigate to="/dashboard" replace />} 
            />
            <Route 
              path="/signup" 
              element={!user ? <SignupPage /> : <Navigate to="/dashboard" replace />} 
            />
            
            {/* Legacy Routes */}
            <Route 
              path="/admin/google-callback" 
              element={<GoogleCallback onSuccess={(userData) => setUser(userData)} />} 
            />
            
            {/* Protected Routes */}
            <Route 
              path="/dashboard" 
              element={
                user ? (
                  <Suspense fallback={<LoadingSpinner />}>
                    <ClientDashboard user={user} onLogout={handleLogout} />
                  </Suspense>
                ) : (
                  <Navigate to="/login" replace />
                )
              } 
            />
            
            <Route 
              path="/admin/dashboard" 
              element={
                user && user.user_type === 'admin' ? (
                  <Suspense fallback={<LoadingSpinner />}>
                    <AdminDashboard user={user} onLogout={handleLogout} />
                  </Suspense>
                ) : user ? (
                  <Navigate to="/dashboard" replace />
                ) : (
                  <Navigate to="/login" replace />
                )
              } 
            />
            
            {/* Legacy admin route - redirect to new login */}
            <Route 
              path="/admin" 
              element={<Navigate to="/login" replace />} 
            />
            
            {/* Default route */}
            <Route 
              path="/" 
              element={
                user ? (
                  user.user_type === 'admin' ? 
                    <Navigate to="/admin/dashboard" replace /> : 
                    <Navigate to="/dashboard" replace />
                ) : (
                  <Navigate to="/login" replace />
                )
              } 
            />
            
            {/* Catch all route */}
            <Route 
              path="*" 
              element={<Navigate to="/" replace />} 
            />
          </Routes>
        </div>
      </ToastProvider>
    </BrowserRouter>
  );
}

export default App;