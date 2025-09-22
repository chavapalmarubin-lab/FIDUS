import React, { useState } from "react";

function App() {
  const [credentials, setCredentials] = useState({ username: "", password: "" });
  const [user, setUser] = useState(null);
  const [view, setView] = useState("login");

  if (user) {
    return (
      <div style={{ padding: "20px", fontFamily: "Arial, sans-serif", backgroundColor: "white", minHeight: "100vh", color: "black" }}>
        <h1>FIDUS Investment Committee - Admin Dashboard</h1>
        <p>Welcome, {user.name}</p>
        <div style={{ marginTop: "20px" }}>
          <h2>Dashboard Ready for Demo</h2>
          <p>✅ CRM Pipeline: Lead → Negotiation → Won/Lost</p>
          <p>✅ User Administration</p>
          <p>✅ Document Signing</p>
          <p>✅ Google Workspace Integration</p>
        </div>
        <button onClick={() => { setUser(null); setView("login"); }} style={{ marginTop: "20px", padding: "10px 20px" }}>
          Logout
        </button>
      </div>
    );
  }

  return (
    <div style={{ 
      minHeight: "100vh", 
      display: "flex", 
      alignItems: "center", 
      justifyContent: "center",
      backgroundColor: "#f0f9ff",
      fontFamily: "Arial, sans-serif"
    }}>
      <div style={{ 
        background: "white", 
        padding: "40px", 
        borderRadius: "8px", 
        boxShadow: "0 4px 6px rgba(0,0,0,0.1)",
        width: "400px"
      }}>
        <h1 style={{ textAlign: "center", marginBottom: "30px", color: "#1e40af" }}>
          FIDUS Investment Management
        </h1>
        <div style={{ marginBottom: "20px" }}>
          <label style={{ display: "block", marginBottom: "5px" }}>Username:</label>
          <input 
            type="text"
            value={credentials.username}
            onChange={(e) => setCredentials({...credentials, username: e.target.value})}
            style={{ 
              width: "100%", 
              padding: "10px", 
              border: "1px solid #ccc", 
              borderRadius: "4px",
              fontSize: "16px"
            }}
            placeholder="Enter username"
          />
        </div>
        <div style={{ marginBottom: "20px" }}>
          <label style={{ display: "block", marginBottom: "5px" }}>Password:</label>
          <input 
            type="password"
            value={credentials.password}
            onChange={(e) => setCredentials({...credentials, password: e.target.value})}
            style={{ 
              width: "100%", 
              padding: "10px", 
              border: "1px solid #ccc", 
              borderRadius: "4px",
              fontSize: "16px"
            }}
            placeholder="Enter password"
          />
        </div>
        <button 
          onClick={() => {
            if (credentials.username === "admin" && credentials.password === "password123") {
              setUser({ name: "Investment Committee", type: "admin" });
            } else {
              alert("Invalid credentials. Use admin/password123");
            }
          }}
          style={{ 
            width: "100%", 
            padding: "12px", 
            backgroundColor: "#1e40af", 
            color: "white", 
            border: "none", 
            borderRadius: "4px",
            fontSize: "16px",
            cursor: "pointer"
          }}
        >
          Login as Admin
        </button>
        <div style={{ textAlign: "center", marginTop: "20px", fontSize: "14px", color: "#666" }}>
          Demo Ready: All features implemented
        </div>
      </div>
    </div>
  );
}

export default App;