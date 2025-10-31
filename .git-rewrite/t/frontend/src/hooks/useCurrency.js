import { useState, useEffect, useCallback } from 'react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const useCurrency = () => {
  const [exchangeRates, setExchangeRates] = useState({});
  const [currencies, setCurrencies] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  const fetchExchangeRates = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`${API}/currency/rates`);
      const data = await response.json();
      
      if (data.success) {
        setExchangeRates(data.rates || {});
        setCurrencies(data.supported_currencies || []);
        setLastUpdated(new Date(data.last_updated));
      } else {
        throw new Error('Failed to fetch exchange rates');
      }
    } catch (err) {
      setError(err.message);
      // Set fallback data
      setExchangeRates({ USD: 1.0, MXN: 18.5, EUR: 0.85 });
      setCurrencies([
        { code: 'USD', name: 'US Dollar', symbol: '$' },
        { code: 'MXN', name: 'Mexican Peso', symbol: '$' },
        { code: 'EUR', name: 'Euro', symbol: '€' }
      ]);
    } finally {
      setLoading(false);
    }
  }, []);

  const convertAmount = useCallback((amount, fromCurrency = 'USD', toCurrency = 'USD') => {
    if (fromCurrency === toCurrency) return amount;
    
    const rates = exchangeRates;
    
    if (fromCurrency === 'USD') {
      return amount * (rates[toCurrency] || 1);
    } else if (toCurrency === 'USD') {
      const fromRate = rates[fromCurrency] || 1;
      return fromRate !== 0 ? amount / fromRate : amount;
    } else {
      // Convert via USD
      const usdAmount = convertAmount(amount, fromCurrency, 'USD');
      return convertAmount(usdAmount, 'USD', toCurrency);
    }
  }, [exchangeRates]);

  const formatCurrency = useCallback((amount, currency = 'USD') => {
    const currencyData = currencies.find(c => c.code === currency);
    const symbol = currencyData?.symbol || '$';
    
    const formattedAmount = amount.toLocaleString(undefined, { 
      minimumFractionDigits: 2, 
      maximumFractionDigits: 2 
    });
    
    if (currency === 'USD') {
      return `${symbol}${formattedAmount}`;
    } else if (currency === 'MXN') {
      return `${symbol}${formattedAmount} MXN`;
    } else if (currency === 'EUR') {
      return `${symbol}${formattedAmount} EUR`;
    } else {
      return `${symbol}${formattedAmount}`;
    }
  }, [currencies]);

  const getConvertedAmount = useCallback((amount, targetCurrency = 'USD') => {
    const converted = convertAmount(amount, 'USD', targetCurrency);
    return {
      amount: converted,
      formatted: formatCurrency(converted, targetCurrency),
      rate: exchangeRates[targetCurrency] || 1
    };
  }, [convertAmount, formatCurrency, exchangeRates]);

  const getAllConversions = useCallback((amount) => {
    const conversions = {};
    currencies.forEach(currency => {
      conversions[currency.code] = getConvertedAmount(amount, currency.code);
    });
    return conversions;
  }, [currencies, getConvertedAmount]);

  useEffect(() => {
    fetchExchangeRates();
    
    // Refresh rates every 30 minutes
    const interval = setInterval(fetchExchangeRates, 30 * 60 * 1000);
    
    return () => clearInterval(interval);
  }, [fetchExchangeRates]);

  return {
    exchangeRates,
    currencies,
    loading,
    error,
    lastUpdated,
    fetchExchangeRates,
    convertAmount,
    formatCurrency,
    getConvertedAmount,
    getAllConversions
  };
};

export default useCurrency;