import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import "./i18n/config"; // Initialize i18n

// =============================================================================
// CRITICAL: ROUTE DETECTION - Uses flag set by index.html script
// This runs AFTER the HTML script has already determined the app type
// =============================================================================
const hostname = window.location.hostname.toLowerCase();
const pathname = window.location.pathname.toLowerCase();

// Check both the pre-set flag AND do our own check for redundancy
const hostnameHasViking = hostname.includes('viking') || hostname.includes('vkng');
const pathHasViking = pathname.startsWith('/viking') || pathname === '/vikin' || pathname.startsWith('/vikin/');
const IS_VIKING = window.__IS_VIKING_APP__ === true || hostnameHasViking || pathHasViking;
const IS_PUBLIC = pathname.startsWith('/prospects');

// Debug logging
console.log('='.repeat(60));
console.log('🚀 INDEX.JS INITIALIZATION');
console.log('🌐 Hostname:', hostname);
console.log('📍 Pathname:', pathname);
console.log('🔍 window.__IS_VIKING_APP__:', window.__IS_VIKING_APP__);
console.log('🔍 Hostname has viking/vkng:', hostnameHasViking);
console.log('🔍 Path has viking:', pathHasViking);
console.log('🟣 IS_VIKING (final):', IS_VIKING);
console.log('🟢 IS_PUBLIC:', IS_PUBLIC);
console.log('='.repeat(60));

// Handle /vikin typo redirect
if (pathname === '/vikin' || pathname.startsWith('/vikin/')) {
  console.log('🔄 Redirecting /vikin to /viking');
  window.location.replace(window.location.href.replace('/vikin', '/viking'));
}

const root = ReactDOM.createRoot(document.getElementById("root"));

// =============================================================================
// CONDITIONAL IMPORTS - Only load what's needed
// VIKING app loads FIRST if detected - FIDUS code never executes
// =============================================================================
if (IS_VIKING) {
  // VIKING - Load VikingApp directly, FIDUS code never runs
  console.log('🟣 Loading VIKING Application (FIDUS will NOT load)...');
  import('./components/VikingApp').then(({ default: VikingApp }) => {
    console.log('🟣 VIKING App loaded, rendering...');
    root.render(
      <React.StrictMode>
        <VikingApp />
      </React.StrictMode>
    );
  }).catch(err => {
    console.error('Failed to load VikingApp:', err);
    root.render(
      <div style={{
        color: 'white', 
        padding: '40px', 
        background: '#0A112B', 
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        fontFamily: 'system-ui, sans-serif'
      }}>
        <h1 style={{color: '#9B27FF', marginBottom: '20px'}}>VKNG AI</h1>
        <p>Error loading application. Please refresh the page.</p>
        <button 
          onClick={() => window.location.reload()} 
          style={{
            marginTop: '20px',
            padding: '10px 24px',
            background: '#9B27FF',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: 'pointer',
            fontSize: '16px'
          }}
        >
          Refresh Page
        </button>
      </div>
    );
  });
} else if (IS_PUBLIC) {
  // PUBLIC ROUTE
  console.log('🟢 Loading Public Application...');
  import('./PublicApp').then(({ default: PublicApp }) => {
    root.render(
      <React.StrictMode>
        <PublicApp />
      </React.StrictMode>
    );
  });
} else {
  // FIDUS ROUTE - Only loads if NOT on VIKING domain
  console.log('🔵 Loading FIDUS Application...');
  import('./App').then(({ default: App }) => {
    root.render(
      <React.StrictMode>
        <App />
      </React.StrictMode>
    );
  });
}
