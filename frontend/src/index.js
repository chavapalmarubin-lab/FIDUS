import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import App from "./App";
import PublicApp from "./PublicApp";
import "./i18n/config"; // Initialize i18n

// Check if we're on a public route
const isPublicRoute = window.location.pathname.startsWith('/prospects');

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    {isPublicRoute ? <PublicApp /> : <App />}
  </React.StrictMode>,
);
