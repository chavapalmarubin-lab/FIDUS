/**
 * Axios instance with JWT token auto-injection for FIDUS Investment Management Platform
 */

import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Create axios instance
const apiAxios = axios.create({
  baseURL: API,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to automatically add JWT token
apiAxios.interceptors.request.use(
  (config) => {
    // Get JWT token from localStorage
    try {
      const userDataStr = localStorage.getItem('fidus_user');
      if (userDataStr) {
        const userData = JSON.parse(userDataStr);
        if (userData.token) {
          config.headers['Authorization'] = `Bearer ${userData.token}`;
        }
      }
    } catch (error) {
      console.warn('Failed to parse user data from localStorage:', error);
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiAxios.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Handle 401 errors (token expired or invalid)
    if (error.response?.status === 401) {
      console.warn('Authentication failed - redirecting to login');
      // Clear invalid token
      localStorage.removeItem('fidus_user');
      // Optionally redirect to login page
      // window.location.href = '/';
    }
    
    return Promise.reject(error);
  }
);

export default apiAxios;