import React, { useState, useEffect } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import LogoAnimation from "./components/LogoAnimation";
import LoginSelection from "./components/LoginSelection";
import ClientDashboard from "./components/ClientDashboard";
import AdminDashboard from "./components/AdminDashboard";
import "./App.css";

function App() {
  const [currentView, setCurrentView] = useState("logo"); // logo, login, client, admin
  const [user, setUser] = useState(null);

  useEffect(() => {
    // Check for skip animation parameter (for production testing)
    const urlParams = new URLSearchParams(window.location.search);
    const skipAnimation = urlParams.get('skip_animation') === 'true';
    
    if (skipAnimation) {
      // Check if user is already logged in
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
      // Skip animation for testing/production
      setCurrentView("login");
    } else {
      // Clear any existing user session to always show logo animation
      localStorage.removeItem("fidus_user");
      
      // Always start with logo animation
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
    setCurrentView("login");
  };

  return (
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
        
        {currentView === "client" && user && (
          <motion.div
            key="client"
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
            key="admin"
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