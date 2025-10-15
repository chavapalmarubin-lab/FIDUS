/**
 * useMT5Data Hook - Phase 3
 * React hook for accessing MT5 data across components
 * Single source of truth with automatic refresh
 */

import { useState, useEffect, useCallback } from 'react';
import mt5Service from '../services/mt5Service';

/**
 * Main hook for MT5 data
 * @param {Object} options - Configuration options
 * @param {boolean} options.autoRefresh - Enable auto-refresh every 2 minutes
 * @param {number} options.refreshInterval - Refresh interval in milliseconds (default: 120000 = 2 min)
 * @param {boolean} options.skipInitialFetch - Skip initial fetch (default: false)
 */
export function useMT5Data(options = {}) {
  const {
    autoRefresh = true,
    refreshInterval = 120000, // 2 minutes
    skipInitialFetch = false
  } = options;

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(!skipInitialFetch);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  const fetchData = useCallback(async (skipCache = false) => {
    try {
      setLoading(true);
      setError(null);

      const result = await mt5Service.getAllAccounts(skipCache);
      
      setData(result);
      setLastUpdated(new Date());
      
      return result;
    } catch (err) {
      console.error('[useMT5Data] Fetch error:', err);
      setError(err.message || 'Failed to fetch MT5 data');
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial fetch
  useEffect(() => {
    if (!skipInitialFetch) {
      fetchData();
    }
  }, [skipInitialFetch, fetchData]);

  // Auto-refresh
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      console.log('[useMT5Data] Auto-refreshing data...');
      fetchData(true); // Skip cache on auto-refresh
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, fetchData]);

  const refresh = useCallback(() => {
    return fetchData(true); // Force fresh data
  }, [fetchData]);

  return {
    data,
    accounts: data?.accounts || [],
    summary: data?.summary || {},
    loading,
    error,
    lastUpdated,
    refresh,
    dataSource: data?.dataSource,
    isFresh: data?.summary?.fresh_accounts === data?.summary?.total_accounts
  };
}

/**
 * Hook for accounts grouped by fund type
 */
export function useMT5AccountsByFund() {
  const [grouped, setGrouped] = useState({
    BALANCE: [],
    CORE: [],
    SEPARATION: []
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchGrouped = async () => {
      try {
        setLoading(true);
        const result = await mt5Service.getAccountsByFundType();
        setGrouped(result);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchGrouped();
  }, []);

  return { grouped, loading, error };
}

/**
 * Hook for fund totals
 */
export function useMT5FundTotals() {
  const [totals, setTotals] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchTotals = useCallback(async () => {
    try {
      setLoading(true);
      const result = await mt5Service.getFundTotals();
      setTotals(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchTotals();
  }, [fetchTotals]);

  return { totals, loading, error, refresh: fetchTotals };
}

/**
 * Hook for single account by login number
 */
export function useMT5Account(mt5Login) {
  const [account, setAccount] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!mt5Login) {
      setLoading(false);
      return;
    }

    const fetchAccount = async () => {
      try {
        setLoading(true);
        const result = await mt5Service.getAccountByLogin(mt5Login);
        setAccount(result);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchAccount();
  }, [mt5Login]);

  return { account, loading, error };
}

/**
 * Hook for system health check
 */
export function useMT5Health() {
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);

  const checkHealth = useCallback(async () => {
    try {
      setLoading(true);
      const result = await mt5Service.checkHealth();
      setHealth(result);
    } catch (err) {
      setHealth({
        status: 'error',
        healthy: false,
        message: err.message
      });
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    checkHealth();
    
    // Check health every minute
    const interval = setInterval(checkHealth, 60000);
    return () => clearInterval(interval);
  }, [checkHealth]);

  return { health, loading, refresh: checkHealth };
}

export default useMT5Data;
