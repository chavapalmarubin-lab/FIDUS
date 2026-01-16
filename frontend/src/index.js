import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import "./i18n/config"; // Initialize i18n

// =============================================================================
// CRITICAL: ROUTE DETECTION - Check HOSTNAME and PATH
// If hostname contains "viking" OR path starts with "/viking" -> Show VIKING
// =============================================================================
const hostname = window.location.hostname.toLowerCase();
const pathname = window.location.pathname.toLowerCase();

// VIKING if: hostname contains "viking" OR path starts with "/viking"
const IS_VIKING = hostname.includes('viking') || pathname.startsWith('/viking') || pathname === '/vikin' || pathname.startsWith('/vikin/');
const IS_PUBLIC = pathname.startsWith('/prospects');

// Debug logging
console.log('='.repeat(60));
console.log('🚀 INDEX.JS INITIALIZATION');
console.log('🌐 Hostname:', hostname);
console.log('📍 Pathname:', pathname);
console.log('🟣 IS_VIKING:', IS_VIKING, `(hostname has viking: ${hostname.includes('viking')}, path: ${pathname.startsWith('/viking')})`);
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
// =============================================================================
if (IS_VIKING) {
  // VIKING - Load VikingApp directly, bypass everything else
  console.log('🟣 Loading VIKING Application (hostname or path match)...');
  import('./components/VikingApp').then(({ default: VikingApp }) => {
    console.log('🟣 VIKING App loaded, rendering...');
    root.render(
      <React.StrictMode>
        <VikingApp />
      </React.StrictMode>
    );
  }).catch(err => {
    console.error('Failed to load VikingApp:', err);
    root.render(<div style={{color: 'white', padding: '20px', background: '#0A112B', minHeight: '100vh'}}>Error loading VIKING App. Please refresh.</div>);
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
  // FIDUS ROUTE
  console.log('🔵 Loading FIDUS Application...');
  import('./App').then(({ default: App }) => {
    root.render(
      <React.StrictMode>
        <App />
      </React.StrictMode>
    );
  });
}
