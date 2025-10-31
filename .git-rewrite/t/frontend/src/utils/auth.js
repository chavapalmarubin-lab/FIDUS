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
  const token = getAuthToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
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
  const token = getAuthToken();
  if (!token) return false;
  
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
    return false;
  }
};

/**
 * Clear authentication data (logout)
 */
export const clearAuth = () => {
  localStorage.removeItem('fidus_user');
};