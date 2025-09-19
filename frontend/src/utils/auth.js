/**
 * Authentication utilities for FIDUS Investment Management Platform
 */

/**
 * Get the JWT token from localStorage
 * @returns {string|null} JWT token or null if not found
 */
export const getAuthToken = () => {
  try {
    const userDataStr = localStorage.getItem('fidus_user');
    if (userDataStr) {
      const userData = JSON.parse(userDataStr);
      return userData.token || null;
    }
  } catch (error) {
    console.warn('Failed to parse user data from localStorage:', error);
  }
  return null;
};

/**
 * Get authorization headers for API calls
 * @returns {object} Headers object with Authorization header if token exists
 */
export const getAuthHeaders = () => {
  // First try to get JWT token for regular admin authentication
  const jwtToken = getAuthToken();
  if (jwtToken) {
    return { Authorization: `Bearer ${jwtToken}` };
  }
  
  // Fallback to Google session token for Google OAuth authenticated requests
  const googleSessionToken = localStorage.getItem('google_session_token');
  if (googleSessionToken) {
    return { Authorization: `Bearer ${googleSessionToken}` };
  }
  
  return {};
};

/**
 * Get the current user data from localStorage
 * @returns {object|null} User data or null if not found
 */
export const getCurrentUser = () => {
  try {
    const userDataStr = localStorage.getItem('fidus_user');
    if (userDataStr) {
      return JSON.parse(userDataStr);
    }
  } catch (error) {
    console.warn('Failed to parse user data from localStorage:', error);
  }
  return null;
};

/**
 * Check if user is authenticated
 * @returns {boolean} True if user has valid token
 */
export const isAuthenticated = () => {
  // Check for JWT token first
  const token = getAuthToken();
  if (token) {
    try {
      // Basic JWT structure check
      const parts = token.split('.');
      if (parts.length !== 3) return false;
      
      // Decode payload to check expiration
      const payload = JSON.parse(atob(parts[1]));
      const currentTime = Math.floor(Date.now() / 1000);
      
      return payload.exp > currentTime;
    } catch (error) {
      console.warn('Invalid JWT token format:', error);
    }
  }
  
  // Check for Google session token
  const googleSessionToken = localStorage.getItem('google_session_token');
  if (googleSessionToken) {
    // If we have a Google session token and user data, consider authenticated
    const userData = getCurrentUser();
    return userData && userData.isGoogleAuth;
  }
  
  return false;
};

/**
 * Clear authentication data (logout)
 */
export const clearAuth = () => {
  localStorage.removeItem('fidus_user');
};