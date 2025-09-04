import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import LogoAnimation from "./components/LogoAnimation";
import LoginSelection from "./components/LoginSelection";
import ClientDashboard from "./components/ClientDashboard";
import AdminDashboard from "./components/AdminDashboard";

function App() {
  const [currentView, setCurrentView] = useState("loading");
  const [user, setUser] = useState(null);

  useEffect(() => {
    // Initialize the app
    const urlParams = new URLSearchParams(window.location.search);
    const skipAnimation = urlParams.get('skip_animation') === 'true';
    
    if (skipAnimation) {
      // Check for existing session
      const savedUser = localStorage.getItem("fidus_user");
      if (savedUser) {
        try {
          const userData = JSON.parse(savedUser);
          setUser(userData);
          setCurrentView(userData.type === "admin" ? "admin" : "client");
          return;
        } catch (e) {
          localStorage.removeItem("fidus_user");
        }
      }
      setCurrentView("login");
    } else {
      // Start with logo animation
      setCurrentView("logo");
    }
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

  const handleAnimationComplete = () => {
    console.log("Animation completed, transitioning to login");
    setCurrentView("login");
  };

  // Show loading screen initially
  if (currentView === "loading") {
    return (
      <div className="App" style={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #1e3a8a 0%, #1e40af 50%, #3b82f6 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: 'white'
      }}>
        <div>Loading FIDUS...</div>
      </div>
    );
  }

  return (
    <div className="App">
      <AnimatePresence mode="wait">
        {currentView === "logo" && (
          <motion.div
            key="logo-animation"
            initial={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.5 }}
          >
            <LogoAnimation onComplete={handleAnimationComplete} />
          </motion.div>
        )}
        
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