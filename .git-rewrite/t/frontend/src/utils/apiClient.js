/**
 * Enhanced API Client with Caching, Retry Logic, and Performance Optimization
 * Professional-grade API client for FIDUS Investment Management Platform
 */

import axios from 'axios';
import { apiCache, getCacheTTL } from './apiCache';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API_BASE = `${BACKEND_URL}/api`;

class APIClient {
  constructor() {
    this.client = axios.create({
      baseURL: API_BASE,
      timeout: 30000, // 30 seconds timeout
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
    this.requestQueue = new Map();
    this.retryAttempts = 3;
    this.retryDelay = 1000; // 1 second base delay
  }

  /**
   * Setup request and response interceptors
   */
  setupInterceptors() {
    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        // Add performance timing
        config.metadata = { startTime: Date.now() };
        
        // Add request ID for debugging
        config.requestId = Math.random().toString(36).substr(2, 9);
        
        // Add JWT token from localStorage if available
        const userDataStr = localStorage.getItem('fidus_user');
        if (userDataStr) {
          try {
            const userData = JSON.parse(userDataStr);
            if (userData.token) {
              config.headers['Authorization'] = `Bearer ${userData.token}`;
            }
          } catch (error) {
            console.warn('Failed to parse user data from localStorage:', error);
          }
        }
        
        console.log(`🚀 API Request [${config.requestId}]:`, config.method?.toUpperCase(), config.url);
        return config;
      },
      (error) => {
        console.error('❌ Request interceptor error:', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => {
        // Calculate response time
        const endTime = Date.now();
        const responseTime = endTime - response.config.metadata.startTime;
        
        console.log(
          `✅ API Response [${response.config.requestId}]:`, 
          response.status, 
          `(${responseTime}ms)`
        );

        // Cache successful GET responses
        if (response.config.method === 'get' && response.status === 200) {
          const cacheKey = apiCache.generateKey(response.config.url, response.config.params);
          const ttl = getCacheTTL(response.config.url);
          apiCache.set(cacheKey, response.data, ttl);
        }

        return response;
      },
      async (error) => {
        const config = error.config;
        
        console.error(
          `❌ API Error [${config?.requestId}]:`, 
          error.response?.status, 
          error.message
        );

        // Implement retry logic for certain errors
        if (this.shouldRetry(error) && (!config._retryCount || config._retryCount < this.retryAttempts)) {
          config._retryCount = config._retryCount || 0;
          config._retryCount += 1;

          const delay = this.calculateRetryDelay(config._retryCount);
          
          console.warn(
            `🔄 Retrying API call [${config.requestId}] (attempt ${config._retryCount}/${this.retryAttempts}) in ${delay}ms`
          );

          await this.sleep(delay);
          return this.client(config);
        }

        // Handle specific error types
        return this.handleAPIError(error);
      }
    );
  }

  /**
   * Enhanced GET method with caching
   */
  async get(url, params = {}, options = {}) {
    const cacheKey = apiCache.generateKey(url, params);
    
    // Check cache first (unless bypassed)
    if (!options.bypassCache) {
      const cachedData = apiCache.get(cacheKey);
      if (cachedData) {
        console.log(`💾 Cache hit for: ${url}`);
        return { data: cachedData, fromCache: true };
      }
    }

    // Prevent duplicate requests
    if (this.requestQueue.has(cacheKey)) {
      console.log(`⏳ Waiting for duplicate request: ${url}`);
      return await this.requestQueue.get(cacheKey);
    }

    // Make API request
    const requestPromise = this.client.get(url, { params, ...options })
      .finally(() => {
        this.requestQueue.delete(cacheKey);
      });

    this.requestQueue.set(cacheKey, requestPromise);
    return await requestPromise;
  }

  /**
   * POST method with cache invalidation
   */
  async post(url, data = {}, options = {}) {
    const response = await this.client.post(url, data, options);
    
    // Invalidate related cache entries
    this.invalidateRelatedCache(url);
    
    return response;
  }

  /**
   * PUT method with cache invalidation
   */
  async put(url, data = {}, options = {}) {
    const response = await this.client.put(url, data, options);
    
    // Invalidate related cache entries
    this.invalidateRelatedCache(url);
    
    return response;
  }

  /**
   * DELETE method with cache invalidation
   */
  async delete(url, options = {}) {
    const response = await this.client.delete(url, options);
    
    // Invalidate related cache entries
    this.invalidateRelatedCache(url);
    
    return response;
  }

  /**
   * Batch API requests with concurrency control
   */
  async batchRequests(requests, concurrency = 5) {
    const results = [];
    const executing = [];

    for (const request of requests) {
      const promise = this.executeRequest(request).then(result => {
        executing.splice(executing.indexOf(promise), 1);
        return result;
      });

      results.push(promise);
      executing.push(promise);

      if (executing.length >= concurrency) {
        await Promise.race(executing);
      }
    }

    return await Promise.allSettled(results);
  }

  /**
   * Execute individual request from batch
   */
  async executeRequest(request) {
    const { method = 'get', url, data, params, options } = request;
    
    switch (method.toLowerCase()) {
      case 'get':
        return await this.get(url, params, options);
      case 'post':
        return await this.post(url, data, options);
      case 'put':
        return await this.put(url, data, options);
      case 'delete':
        return await this.delete(url, options);
      default:
        throw new Error(`Unsupported method: ${method}`);
    }
  }

  /**
   * Preload critical application data
   */
  async preloadCriticalData(userId, userType) {
    const criticalRequests = [];

    // Common data for all users
    criticalRequests.push(
      { method: 'get', url: '/documents/categories' },
      { method: 'get', url: '/fund-configurations' }
    );

    // User-specific data
    if (userType === 'admin') {
      criticalRequests.push(
        { method: 'get', url: '/admin/overview' },
        { method: 'get', url: '/clients/all' },
        { method: 'get', url: '/mt5/admin/accounts' }
      );
    } else if (userType === 'client') {
      criticalRequests.push(
        { method: 'get', url: `/investments/client/${userId}` },
        { method: 'get', url: `/documents/client/${userId}` },
        { method: 'get', url: `/mt5/client/${userId}/accounts` }
      );
    }

    console.log(`🚀 Preloading ${criticalRequests.length} critical API endpoints...`);
    
    const results = await this.batchRequests(criticalRequests, 3);
    const successful = results.filter(r => r.status === 'fulfilled').length;
    
    console.log(`✅ Preloaded ${successful}/${criticalRequests.length} endpoints successfully`);
    return results;
  }

  /**
   * Determine if error should trigger retry
   */
  shouldRetry(error) {
    if (!error.response) return true; // Network errors
    
    const status = error.response.status;
    return status >= 500 || status === 429; // Server errors or rate limits
  }

  /**
   * Calculate exponential backoff delay
   */
  calculateRetryDelay(attempt) {
    return Math.min(this.retryDelay * Math.pow(2, attempt - 1), 10000); // Max 10 seconds
  }

  /**
   * Sleep utility for retry delays
   */
  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Invalidate cache entries related to the API endpoint
   */
  invalidateRelatedCache(url) {
    const patterns = [
      url.split('/')[1], // First path segment
      url.split('/').slice(0, 2).join('/'), // First two segments
    ];

    let invalidatedCount = 0;
    patterns.forEach(pattern => {
      invalidatedCount += apiCache.invalidatePattern(pattern);
    });

    if (invalidatedCount > 0) {
      console.log(`🗑️ Invalidated ${invalidatedCount} cache entries for: ${url}`);
    }
  }

  /**
   * Handle API errors with user-friendly messages
   */
  handleAPIError(error) {
    const errorInfo = {
      status: error.response?.status,
      message: error.response?.data?.message || error.message,
      url: error.config?.url,
      requestId: error.config?.requestId,
    };

    // Log structured error information
    console.error('🚨 API Error Details:', errorInfo);

    // Create user-friendly error message
    let userMessage = 'An unexpected error occurred. Please try again.';
    
    if (error.response?.status === 401) {
      userMessage = 'Authentication required. Please log in again.';
    } else if (error.response?.status === 403) {
      userMessage = 'Access denied. You don\'t have permission for this action.';
    } else if (error.response?.status === 404) {
      userMessage = 'The requested resource was not found.';
    } else if (error.response?.status >= 500) {
      userMessage = 'Server error. Our team has been notified. Please try again later.';
    } else if (!error.response) {
      userMessage = 'Network error. Please check your connection and try again.';
    }

    // Enhance error object
    error.userMessage = userMessage;
    error.errorInfo = errorInfo;

    return Promise.reject(error);
  }

  /**
   * Get API performance statistics
   */
  getPerformanceStats() {
    return {
      cache: apiCache.getStats(),
      queueSize: this.requestQueue.size,
      timestamp: new Date().toISOString(),
    };
  }

  /**
   * Clear all caches and reset client
   */
  reset() {
    apiCache.clear();
    this.requestQueue.clear();
    console.log('🧹 API Client reset - all caches cleared');
  }
}

// Global API client instance
export const apiClient = new APIClient();

// Convenience methods for common operations
export const api = {
  get: (url, params, options) => apiClient.get(url, params, options),
  post: (url, data, options) => apiClient.post(url, data, options),
  put: (url, data, options) => apiClient.put(url, data, options),
  delete: (url, options) => apiClient.delete(url, options),
  
  // Specialized methods
  preload: (userId, userType) => apiClient.preloadCriticalData(userId, userType),
  batch: (requests, concurrency) => apiClient.batchRequests(requests, concurrency),
  stats: () => apiClient.getPerformanceStats(),
  reset: () => apiClient.reset(),
};

export default apiClient;