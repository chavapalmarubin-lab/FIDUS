import React, { useState, useEffect } from "react";
import { BrowserRouter } from "react-router-dom";
import LoginSelection from "./components/LoginSelection";
import ClientDashboard from "./components/ClientDashboard";
import AdminDashboard from "./components/AdminDashboard";
import GoogleCallback from "./components/GoogleCallback";
import { ToastProvider } from "./components/ui/toast";
import "./App.css";

function App() {
  const [currentView, setCurrentView] = useState("login");
  const [user, setUser] = useState(null);

  useEffect(() => {
    console.log('Simple App initializing...');
    
    // Check if user is authenticated
    const storedUser = localStorage.getItem('fidus_user');
    const isAuthenticated = localStorage.getItem('fidus_token');
    
    if (isAuthenticated && storedUser && storedUser !== 'null') {
      try {
        const currentUser = JSON.parse(storedUser);
        setUser(currentUser);
        
        if (currentUser?.isAdmin || currentUser?.type === 'admin') {
          setCurrentView("admin");
        } else {
          setCurrentView("client");
        }
      } catch (err) {
        console.error('Error parsing stored user:', err);
        setCurrentView("login");
      }
    } else {
      setCurrentView("login");
    }
  }, []);

  const handleLogin = (userData) => {
    console.log('Login handler called with:', userData);
    setUser(userData);
    
    // Store user data and token in localStorage
    localStorage.setItem('fidus_user', JSON.stringify(userData));
    if (userData.token) {
      localStorage.setItem('fidus_token', userData.token);
    }
    
    // Set current view based on user type
    if (userData.isAdmin || userData.type === 'admin') {
      setCurrentView("admin");
    } else {
      setCurrentView("client");
    }
  };

  const handleLogout = () => {
    console.log('Logout handler called');
    
    // Clear all auth data
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
          {currentView === "login" && (
            <LoginSelection onLogin={handleLogin} />
          )}
          
          {currentView === "client" && user && (
            <ClientDashboard user={user} />
          )}
          
          {currentView === "admin" && user && (
            <AdminDashboard user={user} />
          )}
          
          {currentView === "google-callback" && (
            <GoogleCallback />
          )}
        </div>
      </ToastProvider>
    </BrowserRouter>
  );
}

export default App;