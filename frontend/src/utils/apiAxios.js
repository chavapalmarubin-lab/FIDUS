/**
 * Axios instance with JWT token auto-injection for FIDUS Investment Management Platform
 */

import axios from 'axios';
import { API_BASE_URL } from '../config/config';

// Create axios instance
const apiAxios = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to automatically add JWT token or Google session token
apiAxios.interceptors.request.use(
  (config) => {
    // Get actual JWT token from localStorage (fidus_token)
    const jwtToken = localStorage.getItem('fidus_token');
    if (jwtToken) {
      config.headers['Authorization'] = `Bearer ${jwtToken}`;
      return config;
    }
    
    // Fallback: Try the old fidus_user format
    try {
      const userDataStr = localStorage.getItem('fidus_user');
      if (userDataStr) {
        const userData = JSON.parse(userDataStr);
        if (userData.token) {
          config.headers['Authorization'] = `Bearer ${userData.token}`;
          return config;
        }
      }
    } catch (error) {
      console.warn('Failed to parse user data from localStorage:', error);
    }
    
    // Final fallback to Google session token
    const googleSessionToken = localStorage.getItem('google_session_token');
    if (googleSessionToken) {
      config.headers['Authorization'] = `Bearer ${googleSessionToken}`;
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