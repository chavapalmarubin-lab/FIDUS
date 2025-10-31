import React from "react";

function App() {
  return (
    <div className="App" style={{padding: '20px', color: 'white', backgroundColor: '#1a1a1a', minHeight: '100vh'}}>
      <h1>FIDUS Investment Management</h1>
      <p>System is being restored...</p>
      <div style={{marginTop: '20px'}}>
        <button 
          style={{padding: '10px 20px', marginRight: '10px', backgroundColor: '#0891b2', color: 'white', border: 'none', borderRadius: '5px'}}
          onClick={() => window.location.href = '/admin'}
        >
          Admin Login
        </button>
        <button 
          style={{padding: '10px 20px', backgroundColor: '#10b981', color: 'white', border: 'none', borderRadius: '5px'}}
          onClick={() => window.location.href = '/client'}
        >
          Client Login
        </button>
      </div>
    </div>
  );
}

export default App;