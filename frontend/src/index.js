import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import App from "./App";
import PublicApp from "./PublicApp";
import "./i18n/config"; // Initialize i18n

// =============================================================================
// CRITICAL ROUTE DETECTION - Runs BEFORE any React component renders
// =============================================================================
const pathname = window.location.pathname.toLowerCase();
const isPublicRoute = pathname.startsWith('/prospects');
const isVikingRoute = pathname.startsWith('/viking') || pathname === '/vikin' || pathname.startsWith('/vikin/');

// Debug logging
console.log('🚀 INDEX.JS - pathname:', window.location.pathname);
console.log('🚀 INDEX.JS - isVikingRoute:', isVikingRoute);
console.log('🚀 INDEX.JS - isPublicRoute:', isPublicRoute);

// Handle /vikin typo redirect
if (pathname === '/vikin' || pathname.startsWith('/vikin/')) {
  console.log('🔄 Redirecting /vikin to /viking');
  window.location.href = window.location.href.replace('/vikin', '/viking');
}

const root = ReactDOM.createRoot(document.getElementById("root"));

// VIKING routes get the App component which will render VikingApp
// Public routes get PublicApp
// All other routes get App which will render FidusApp
if (isVikingRoute) {
  console.log('🟣 INDEX.JS: Rendering App for VIKING route');
} else if (isPublicRoute) {
  console.log('🟢 INDEX.JS: Rendering PublicApp for public route');
} else {
  console.log('🔵 INDEX.JS: Rendering App for FIDUS route');
}

root.render(
  <React.StrictMode>
    {isPublicRoute ? <PublicApp /> : <App />}
  </React.StrictMode>,
);
