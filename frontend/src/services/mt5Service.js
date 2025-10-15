/**
 * MT5 Data Service - Phase 3
 * Single source of truth for all MT5 account data
 * Connects to backend API which syncs with VPS MT5 Bridge
 */

import apiAxios from '../utils/apiAxios';

const MT5_SERVICE_VERSION = 'Phase3-Production';

class MT5Service {
  constructor() {
    this.cache = null;
    this.cacheTimestamp = null;
    this.cacheDuration = 60000; // 1 minute cache
  }

  /**
   * Get all MT5 accounts from backend
   * SINGLE SOURCE OF TRUTH - no mock data
   */
  async getAllAccounts(skipCache = false) {
    try {
      // Check cache first
      if (!skipCache && this.cache && this.cacheTimestamp) {
        const age = Date.now() - this.cacheTimestamp;
        if (age < this.cacheDuration) {
          console.log(`[MT5Service] Using cached data (${Math.round(age / 1000)}s old)`);
          return this.cache;
        }
      }

      console.log('[MT5Service] Fetching fresh data from backend...');
      
      // Fetch from backend (which gets from MongoDB via VPS Bridge)
      const response = await apiAxios.get('/mt5/admin/accounts');
      
      if (!response.data || !response.data.success) {
        throw new Error('Invalid response from MT5 API');
      }

      const data = {
        accounts: response.data.accounts || [],
        summary: response.data.summary || {},
        timestamp: response.data.timestamp,
        dataSource: response.data.data_source || 'MongoDB (VPS Bridge)',
        version: MT5_SERVICE_VERSION
      };

      // Update cache
      this.cache = data;
      this.cacheTimestamp = Date.now();

      console.log(`[MT5Service] ✅ Fetched ${data.accounts.length} accounts`);
      console.log(`[MT5Service] Fresh: ${data.summary.fresh_accounts || 0}, Stale: ${data.summary.stale_accounts || 0}`);

      return data;
    } catch (error) {
      console.error('[MT5Service] Error fetching MT5 accounts:', error);
      
      // DO NOT return mock data - throw error instead
      throw new Error(`Failed to fetch MT5 data: ${error.message}`);
    }
  }

  /**
   * Get accounts grouped by fund type
   */
  async getAccountsByFundType() {
    try {
      const data = await this.getAllAccounts();
      const accounts = data.accounts || [];

      const grouped = {
        BALANCE: accounts.filter(acc => acc.fund_code === 'BALANCE'),
        CORE: accounts.filter(acc => acc.fund_code === 'CORE'),
        SEPARATION: accounts.filter(acc => acc.fund_code === 'SEPARATION')
      };

      return grouped;
    } catch (error) {
      console.error('[MT5Service] Error grouping accounts:', error);
      throw error;
    }
  }

  /**
   * Get single account by MT5 login number
   */
  async getAccountByLogin(mt5Login) {
    try {
      const data = await this.getAllAccounts();
      const accounts = data.accounts || [];
      
      const account = accounts.find(acc => acc.mt5_login === parseInt(mt5Login));
      
      if (!account) {
        throw new Error(`Account ${mt5Login} not found`);
      }

      return account;
    } catch (error) {
      console.error(`[MT5Service] Error fetching account ${mt5Login}:`, error);
      throw error;
    }
  }

  /**
   * Calculate fund totals by type
   */
  async getFundTotals() {
    try {
      const grouped = await this.getAccountsByFundType();

      const totals = {
        BALANCE: this._calculateFundTotal(grouped.BALANCE),
        CORE: this._calculateFundTotal(grouped.CORE),
        SEPARATION: this._calculateFundTotal(grouped.SEPARATION),
        ALL: this._calculateFundTotal([
          ...grouped.BALANCE,
          ...grouped.CORE,
          ...grouped.SEPARATION
        ])
      };

      return totals;
    } catch (error) {
      console.error('[MT5Service] Error calculating fund totals:', error);
      throw error;
    }
  }

  /**
   * Helper: Calculate totals for a group of accounts
   */
  _calculateFundTotal(accounts) {
    return accounts.reduce((total, acc) => ({
      accounts: total.accounts + 1,
      equity: total.equity + (acc.current_equity || 0),
      profit: total.profit + (acc.profit_loss || 0),
      balance: total.balance + (acc.balance || 0)
    }), { accounts: 0, equity: 0, profit: 0, balance: 0 });
  }

  /**
   * Check if MT5 data is fresh (< 10 minutes old)
   */
  async checkDataFreshness() {
    try {
      const data = await this.getAllAccounts();
      const summary = data.summary || {};

      const totalAccounts = summary.total_accounts || 0;
      const freshAccounts = summary.fresh_accounts || 0;
      const staleAccounts = summary.stale_accounts || 0;

      return {
        isFresh: freshAccounts === totalAccounts && totalAccounts > 0,
        totalAccounts,
        freshAccounts,
        staleAccounts,
        message: freshAccounts === totalAccounts 
          ? 'All accounts have fresh data'
          : `${staleAccounts} accounts have stale data (>10 min old)`
      };
    } catch (error) {
      console.error('[MT5Service] Error checking data freshness:', error);
      return {
        isFresh: false,
        totalAccounts: 0,
        freshAccounts: 0,
        staleAccounts: 0,
        message: `Error: ${error.message}`
      };
    }
  }

  /**
   * Check system health
   */
  async checkHealth() {
    try {
      const response = await apiAxios.get('/mt5/health/public');
      return response.data;
    } catch (error) {
      console.error('[MT5Service] Error checking health:', error);
      return {
        status: 'error',
        healthy: false,
        message: error.message
      };
    }
  }

  /**
   * Clear cache (force fresh data on next request)
   */
  clearCache() {
    this.cache = null;
    this.cacheTimestamp = null;
    console.log('[MT5Service] Cache cleared');
  }

  /**
   * Get cache age in seconds
   */
  getCacheAge() {
    if (!this.cacheTimestamp) return null;
    return Math.round((Date.now() - this.cacheTimestamp) / 1000);
  }
}

// Export singleton instance
const mt5Service = new MT5Service();
export default mt5Service;

// Also export the class for testing
export { MT5Service };
