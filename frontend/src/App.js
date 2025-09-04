import React, { useState, useEffect } from "react";
import LoginSelection from "./components/LoginSelection";
import ClientDashboard from "./components/ClientDashboard";  
import AdminDashboard from "./components/AdminDashboard";

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for existing session
    const savedUser = localStorage.getItem("fidus_user");
    if (savedUser) {
      try {
        const userData = JSON.parse(savedUser);
        setUser(userData);
      } catch (e) {
        localStorage.removeItem("fidus_user");
      }
    }
    setLoading(false);
  }, []);

  const handleLogin = (userData) => {
    setUser(userData);
    localStorage.setItem("fidus_user", JSON.stringify(userData));
  };

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem("fidus_user");
  };

  if (loading) {
    return (
      <div style={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #1e3a8a 0%, #1e40af 50%, #3b82f6 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: 'white',
        fontSize: '64px',
        fontWeight: 'bold',
        textShadow: '0 0 30px rgba(255,255,255,0.5)'
      }}>
        FIDUS
      </div>
    );
  }

  // Show appropriate dashboard based on user
  if (user) {
    if (user.type === "admin") {
      return <AdminDashboard user={user} onLogout={handleLogout} />;
    } else {
      return <ClientDashboard user={user} onLogout={handleLogout} />;
    }
  }

  // Show login selection
  return <LoginSelection onLogin={handleLogin} />;
}

export default App;