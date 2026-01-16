import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import "./i18n/config"; // Initialize i18n

// =============================================================================
// CRITICAL: ROUTE DETECTION - MUST RUN BEFORE ANY COMPONENT IMPORTS
// This ensures VIKING and FIDUS are completely isolated
// =============================================================================
const pathname = window.location.pathname.toLowerCase();
const IS_VIKING = pathname.startsWith('/viking') || pathname === '/vikin' || pathname.startsWith('/vikin/');
const IS_PUBLIC = pathname.startsWith('/prospects');

// Debug logging
console.log('='.repeat(60));
console.log('🚀 INDEX.JS INITIALIZATION');
console.log('📍 Pathname:', window.location.pathname);
console.log('🟣 IS_VIKING:', IS_VIKING);
console.log('🟢 IS_PUBLIC:', IS_PUBLIC);
console.log('='.repeat(60));

// Handle /vikin typo redirect
if (pathname === '/vikin' || pathname.startsWith('/vikin/')) {
  console.log('🔄 Redirecting /vikin to /viking');
  window.location.replace(window.location.href.replace('/vikin', '/viking'));
}

const root = ReactDOM.createRoot(document.getElementById("root"));

// =============================================================================
// CONDITIONAL IMPORTS - Only load what's needed for each route
// This prevents FIDUS code from ever loading on VIKING routes
// =============================================================================
if (IS_VIKING) {
  // VIKING ROUTE - Import ONLY VikingApp
  console.log('🟣 Loading VIKING Application...');
  import('./components/VikingApp').then(({ default: VikingApp }) => {
    console.log('🟣 VIKING App loaded, rendering...');
    root.render(
      <React.StrictMode>
        <VikingApp />
      </React.StrictMode>
    );
  }).catch(err => {
    console.error('Failed to load VikingApp:', err);
    root.render(<div style={{color: 'white', padding: '20px'}}>Error loading VIKING App. Please refresh.</div>);
  });
} else if (IS_PUBLIC) {
  // PUBLIC ROUTE - Import PublicApp
  console.log('🟢 Loading Public Application...');
  import('./PublicApp').then(({ default: PublicApp }) => {
    root.render(
      <React.StrictMode>
        <PublicApp />
      </React.StrictMode>
    );
  });
} else {
  // FIDUS ROUTE - Import main App (which contains FidusApp)
  console.log('🔵 Loading FIDUS Application...');
  import('./App').then(({ default: App }) => {
    root.render(
      <React.StrictMode>
        <App />
      </React.StrictMode>
    );
  });
}
