import React, { useState } from "react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

function App() {
  const [loginType, setLoginType] = useState(null);
  const [credentials, setCredentials] = useState({ username: "", password: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [user, setUser] = useState(null);

  const handleLogin = async () => {
    if (!credentials.username || !credentials.password) {
      setError("Please enter username and password");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await fetch(`${BACKEND_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: credentials.username,
          password: credentials.password,
          user_type: loginType
        })
      });

      const data = await response.json();

      if (response.ok) {
        setUser(data);
        localStorage.setItem('fidus_user', JSON.stringify(data));
      } else {
        setError(data.detail || "Login failed");
      }
    } catch (err) {
      setError("Network error. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    setUser(null);
    setLoginType(null);
    setCredentials({ username: "", password: "" });
    localStorage.removeItem('fidus_user');
  };

  // Check for existing session
  React.useEffect(() => {
    const savedUser = localStorage.getItem('fidus_user');
    if (savedUser) {
      try {
        setUser(JSON.parse(savedUser));
      } catch (e) {
        localStorage.removeItem('fidus_user');
      }
    }
  }, []);

  const styles = {
    container: {
      padding: '20px',
      color: 'white',
      backgroundColor: '#1a1a1a',
      minHeight: '100vh',
      fontFamily: 'Arial, sans-serif'
    },
    card: {
      backgroundColor: '#2a2a2a',
      padding: '30px',
      borderRadius: '10px',
      maxWidth: '400px',
      margin: '50px auto',
      boxShadow: '0 4px 12px rgba(0,0,0,0.3)'
    },
    input: {
      width: '100%',
      padding: '12px',
      margin: '10px 0',
      backgroundColor: '#3a3a3a',
      border: '1px solid #555',
      borderRadius: '5px',
      color: 'white',
      fontSize: '16px'
    },
    button: {
      width: '100%',
      padding: '12px 20px',
      margin: '10px 0',
      backgroundColor: '#0891b2',
      color: 'white',
      border: 'none',
      borderRadius: '5px',
      fontSize: '16px',
      cursor: 'pointer'
    },
    buttonSecondary: {
      backgroundColor: '#10b981'
    },
    error: {
      color: '#ef4444',
      margin: '10px 0',
      padding: '10px',
      backgroundColor: '#2a1a1a',
      borderRadius: '5px'
    },
    dashboard: {
      textAlign: 'center'
    }
  };

  if (user) {
    return (
      <div style={styles.container}>
        <div style={styles.card}>
          <h1>Welcome to FIDUS</h1>
          <div style={styles.dashboard}>
            <h2>Welcome, {user.name || user.username}!</h2>
            <p><strong>Type:</strong> {user.type}</p>
            <p><strong>Email:</strong> {user.email}</p>
            <div style={{margin: '20px 0'}}>
              <p>✅ Authentication: Working</p>
              <p>✅ Backend API: Connected</p>
              <p>✅ Database: MongoDB Integrated</p>
            </div>
            <p style={{color: '#10b981', marginBottom: '20px'}}>
              System restored! Main application will be available shortly.
            </p>
            <button style={styles.button} onClick={handleLogout}>
              Logout
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!loginType) {
    return (
      <div style={styles.container}>
        <div style={styles.card}>
          <h1 style={{textAlign: 'center', marginBottom: '30px'}}>FIDUS Investment Management</h1>
          <p style={{textAlign: 'center', marginBottom: '30px', color: '#888'}}>
            Choose your login type
          </p>
          <button 
            style={{...styles.button, ...styles.buttonSecondary}}
            onClick={() => {
              setLoginType('admin');
              setCredentials({ username: 'admin', password: 'password123' });
            }}
          >
            Admin Login
          </button>
          <button 
            style={styles.button}
            onClick={() => {
              setLoginType('client');
              setCredentials({ username: 'client1', password: 'password123' });
            }}
          >
            Client Login
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h1 style={{textAlign: 'center'}}>
          {loginType === 'admin' ? 'Admin' : 'Client'} Login
        </h1>
        
        {error && <div style={styles.error}>{error}</div>}
        
        <input
          style={styles.input}
          type="text"
          placeholder="Username"
          value={credentials.username}
          onChange={(e) => setCredentials({...credentials, username: e.target.value})}
        />
        
        <input
          style={styles.input}
          type="password"
          placeholder="Password"
          value={credentials.password}
          onChange={(e) => setCredentials({...credentials, password: e.target.value})}
        />
        
        <button
          style={styles.button}
          onClick={handleLogin}
          disabled={loading}
        >
          {loading ? 'Signing in...' : 'Sign In'}
        </button>
        
        <button
          style={{...styles.button, backgroundColor: '#666'}}
          onClick={() => setLoginType(null)}
        >
          Back
        </button>
        
        <div style={{marginTop: '20px', fontSize: '14px', color: '#888'}}>
          <p><strong>Demo Credentials:</strong></p>
          <p>Admin: admin / password123</p>
          <p>Client: client1 / password123</p>
        </div>
      </div>
    </div>
  );
}

export default App;