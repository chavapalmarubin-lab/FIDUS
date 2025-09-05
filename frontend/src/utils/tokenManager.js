/**
 * JWT Token Management System
 * Handles automatic token refresh, validation, and secure storage
 */

import { getCurrentUser } from './auth';

class TokenManager {
  constructor() {
    this.refreshTimer = null;
    this.isRefreshing = false;
    this.refreshSubscribers = [];
    
    // Start monitoring tokens when initialized
    this.startTokenMonitoring();
  }

  /**
   * Start monitoring token expiration and auto-refresh
   */
  startTokenMonitoring() {
    // Check token every minute
    this.refreshTimer = setInterval(() => {
      this.checkTokenExpiration();
    }, 60000); // 1 minute
  }

  /**
   * Stop token monitoring (on logout)
   */
  stopTokenMonitoring() {
    if (this.refreshTimer) {
      clearInterval(this.refreshTimer);
      this.refreshTimer = null;
    }
  }

  /**
   * Check if token needs refresh (refresh 5 minutes before expiry)
   */
  checkTokenExpiration() {
    const user = getCurrentUser();
    if (!user || !user.token) return;

    try {
      const payload = JSON.parse(atob(user.token.split('.')[1]));
      const currentTime = Math.floor(Date.now() / 1000);
      const expiryTime = payload.exp;
      const refreshThreshold = 5 * 60; // 5 minutes in seconds

      // If token expires in less than 5 minutes, refresh it
      if (expiryTime - currentTime < refreshThreshold) {
        console.log('Token expires soon, refreshing...');
        this.refreshToken();
      }
    } catch (error) {
      console.warn('Error checking token expiration:', error);
    }
  }

  /**
   * Refresh JWT token
   */
  async refreshToken() {
    if (this.isRefreshing) {
      return new Promise((resolve) => {
        this.refreshSubscribers.push(resolve);
      });
    }

    this.isRefreshing = true;

    try {
      const user = getCurrentUser();
      if (!user || !user.token) {
        throw new Error('No valid token to refresh');
      }

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/auth/refresh-token`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${user.token}`
        }
      });

      if (!response.ok) {
        throw new Error('Token refresh failed');
      }

      const data = await response.json();
      
      // Update user data with new token
      const updatedUser = { ...user, token: data.token };
      localStorage.setItem('fidus_user', JSON.stringify(updatedUser));

      // Notify all subscribers
      this.refreshSubscribers.forEach(callback => callback(data.token));
      this.refreshSubscribers = [];

      console.log('Token refreshed successfully');
      return data.token;

    } catch (error) {
      console.error('Token refresh failed:', error);
      
      // Clear invalid token and redirect to login
      localStorage.removeItem('fidus_user');
      
      // Notify subscribers of failure
      this.refreshSubscribers.forEach(callback => callback(null));
      this.refreshSubscribers = [];

      // Redirect to login page
      window.location.href = '/';
      
      throw error;
    } finally {
      this.isRefreshing = false;
    }
  }

  /**
   * Get valid token (refresh if needed)
   */
  async getValidToken() {
    const user = getCurrentUser();
    if (!user || !user.token) return null;

    try {
      const payload = JSON.parse(atob(user.token.split('.')[1]));
      const currentTime = Math.floor(Date.now() / 1000);
      const expiryTime = payload.exp;

      // If token is expired or expires in next minute, refresh it
      if (expiryTime <= currentTime + 60) {
        return await this.refreshToken();
      }

      return user.token;
    } catch (error) {
      console.warn('Error validating token:', error);
      return null;
    }
  }

  /**
   * Clear token and stop monitoring
   */
  clearToken() {
    localStorage.removeItem('fidus_user');
    this.stopTokenMonitoring();
  }
}

// Global token manager instance
export const tokenManager = new TokenManager();

// Utility functions
export const getValidToken = () => tokenManager.getValidToken();
export const refreshToken = () => tokenManager.refreshToken();
export const clearToken = () => tokenManager.clearToken();