/**
 * Advanced API Caching System for FIDUS Investment Platform
 * Implements intelligent caching with TTL, invalidation, and performance optimization
 */

class APICache {
  constructor() {
    this.cache = new Map();
    this.timeouts = new Map();
    this.defaultTTL = 5 * 60 * 1000; // 5 minutes default
    this.maxCacheSize = 100; // Maximum cache entries
  }

  /**
   * Generate cache key from URL and parameters
   */
  generateKey(url, params = {}) {
    const paramString = Object.keys(params)
      .sort()
      .map(key => `${key}=${JSON.stringify(params[key])}`)
      .join('&');
    return `${url}${paramString ? '?' + paramString : ''}`;
  }

  /**
   * Get cached data if valid
   */
  get(key) {
    const entry = this.cache.get(key);
    
    if (!entry) {
      return null;
    }

    // Check if expired
    if (Date.now() > entry.expiry) {
      this.delete(key);
      return null;
    }

    // Update access time for LRU
    entry.lastAccessed = Date.now();
    return entry.data;
  }

  /**
   * Set cache entry with TTL
   */
  set(key, data, ttl = this.defaultTTL) {
    // Implement LRU eviction if cache is full
    if (this.cache.size >= this.maxCacheSize) {
      this.evictLRU();
    }

    const expiry = Date.now() + ttl;
    
    // Clear existing timeout if any
    if (this.timeouts.has(key)) {
      clearTimeout(this.timeouts.get(key));
    }

    // Set cache entry
    this.cache.set(key, {
      data: JSON.parse(JSON.stringify(data)), // Deep copy
      expiry,
      lastAccessed: Date.now(),
      createdAt: Date.now()
    });

    // Set cleanup timeout
    const timeout = setTimeout(() => {
      this.delete(key);
    }, ttl);
    
    this.timeouts.set(key, timeout);
  }

  /**
   * Delete cache entry
   */
  delete(key) {
    this.cache.delete(key);
    
    if (this.timeouts.has(key)) {
      clearTimeout(this.timeouts.get(key));
      this.timeouts.delete(key);
    }
  }

  /**
   * Clear all cache entries
   */
  clear() {
    // Clear all timeouts
    this.timeouts.forEach(timeout => clearTimeout(timeout));
    this.timeouts.clear();
    this.cache.clear();
  }

  /**
   * Evict least recently used entry
   */
  evictLRU() {
    let oldestKey = null;
    let oldestTime = Date.now();

    for (const [key, entry] of this.cache.entries()) {
      if (entry.lastAccessed < oldestTime) {
        oldestTime = entry.lastAccessed;
        oldestKey = key;
      }
    }

    if (oldestKey) {
      this.delete(oldestKey);
    }
  }

  /**
   * Invalidate cache entries by pattern
   */
  invalidatePattern(pattern) {
    const regex = new RegExp(pattern);
    const keysToDelete = [];

    for (const key of this.cache.keys()) {
      if (regex.test(key)) {
        keysToDelete.push(key);
      }
    }

    keysToDelete.forEach(key => this.delete(key));
    return keysToDelete.length;
  }

  /**
   * Get cache statistics
   */
  getStats() {
    const entries = Array.from(this.cache.entries());
    const now = Date.now();
    
    return {
      size: this.cache.size,
      maxSize: this.maxCacheSize,
      entries: entries.map(([key, entry]) => ({
        key,
        age: now - entry.createdAt,
        timeToExpiry: entry.expiry - now,
        lastAccessed: now - entry.lastAccessed,
        dataSize: JSON.stringify(entry.data).length
      }))
    };
  }

  /**
   * Preload cache with common API calls
   */
  async preloadCommonData(apiClient) {
    const commonEndpoints = [
      { url: '/api/documents/categories', ttl: 30 * 60 * 1000 }, // 30 minutes
      { url: '/api/fund-configurations', ttl: 15 * 60 * 1000 }, // 15 minutes
    ];

    const preloadPromises = commonEndpoints.map(async ({ url, ttl }) => {
      try {
        const response = await apiClient.get(url);
        const key = this.generateKey(url);
        this.set(key, response.data, ttl);
        console.log(`✅ Preloaded cache for ${url}`);
      } catch (error) {
        console.warn(`⚠️ Failed to preload ${url}:`, error.message);
      }
    });

    await Promise.allSettled(preloadPromises);
  }
}

/**
 * Cache configuration for different API endpoints
 */
export const CACHE_CONFIG = {
  // User data - short cache due to frequent updates
  '/api/auth/': { ttl: 2 * 60 * 1000 }, // 2 minutes
  '/api/clients/': { ttl: 5 * 60 * 1000 }, // 5 minutes
  
  // Investment data - moderate cache
  '/api/investments/': { ttl: 3 * 60 * 1000 }, // 3 minutes
  '/api/mt5/': { ttl: 1 * 60 * 1000 }, // 1 minute (real-time data)
  
  // Configuration data - long cache
  '/api/documents/categories': { ttl: 30 * 60 * 1000 }, // 30 minutes
  '/api/fund-configurations': { ttl: 15 * 60 * 1000 }, // 15 minutes
  
  // Static data - very long cache
  '/api/database/': { ttl: 60 * 60 * 1000 }, // 1 hour
};

/**
 * Get cache TTL for specific endpoint
 */
export const getCacheTTL = (url) => {
  for (const [pattern, config] of Object.entries(CACHE_CONFIG)) {
    if (url.includes(pattern)) {
      return config.ttl;
    }
  }
  return 5 * 60 * 1000; // Default 5 minutes
};

// Global cache instance
export const apiCache = new APICache();

// Cache performance monitoring
export const cacheStats = () => {
  const stats = apiCache.getStats();
  console.group('📊 API Cache Statistics');
  console.log(`Cache size: ${stats.size}/${stats.maxSize}`);
  console.log(`Cache entries:`, stats.entries);
  console.groupEnd();
  return stats;
};