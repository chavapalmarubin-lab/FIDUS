import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import LoginSelection from "./components/LoginSelection";
import ClientDashboard from "./components/ClientDashboard";
import AdminDashboard from "./components/AdminDashboard";

function App() {
  const [currentView, setCurrentView] = useState("login");
  const [user, setUser] = useState(null);
  const [showWelcome, setShowWelcome] = useState(true);

  useEffect(() => {
    // Check for existing session
    const savedUser = localStorage.getItem("fidus_user");
    if (savedUser) {
      try {
        const userData = JSON.parse(savedUser);
        setUser(userData);
        setCurrentView(userData.type === "admin" ? "admin" : "client");
        setShowWelcome(false);
        return;
      } catch (e) {
        localStorage.removeItem("fidus_user");
      }
    }

    // Show welcome message briefly, then login
    const timer = setTimeout(() => {
      setShowWelcome(false);
    }, 2000);

    return () => clearTimeout(timer);
  }, []);

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

  if (showWelcome) {
    return (
      <div className="App" style={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #1e3a8a 0%, #1e40af 50%, #3b82f6 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: 'white'
      }}>
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 1 }}
          style={{ textAlign: 'center' }}
        >
          <div style={{
            fontSize: '64px',
            fontWeight: 'bold',
            marginBottom: '20px',
            textShadow: '0 0 30px rgba(255,255,255,0.5)'
          }}>
            FIDUS
          </div>
          <div style={{
            fontSize: '20px',
            color: '#a1a1aa',
            letterSpacing: '2px'
          }}>
            Investment Management System
          </div>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="App">
      <AnimatePresence mode="wait">
        {currentView === "login" && (
          <motion.div
            key="login-selection"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.5 }}
          >
            <LoginSelection onLogin={handleLogin} />
          </motion.div>
        )}
        
        {currentView === "client" && user && (
          <motion.div
            key="client-dashboard"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.5 }}
          >
            <ClientDashboard user={user} onLogout={handleLogout} />
          </motion.div>
        )}
        
        {currentView === "admin" && user && (
          <motion.div
            key="admin-dashboard"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.5 }}
          >
            <AdminDashboard user={user} onLogout={handleLogout} />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default App;