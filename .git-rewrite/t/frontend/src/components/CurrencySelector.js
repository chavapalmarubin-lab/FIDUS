import React, { useState, useEffect } from 'react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { Card, CardContent } from "./ui/card";
import { 
  Globe, 
  DollarSign, 
  TrendingUp, 
  RefreshCw,
  AlertCircle 
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const CURRENCY_FLAGS = {
  'USD': '🇺🇸',
  'MXN': '🇲🇽', 
  'EUR': '🇪🇺'
};

const CurrencySelector = ({ 
  selectedCurrency = 'USD', 
  onCurrencyChange, 
  showRates = true,
  showSummary = false,
  baseAmount = null,
  className = "",
  size = "default" // "sm", "default", "lg"
}) => {
  const [currencies, setCurrencies] = useState([]);
  const [exchangeRates, setExchangeRates] = useState({});
  const [currencySummary, setCurrencySummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [lastUpdated, setLastUpdated] = useState(null);

  useEffect(() => {
    fetchExchangeRates();
  }, []);

  useEffect(() => {
    if (showSummary && baseAmount && baseAmount > 0) {
      fetchCurrencySummary(baseAmount);
    }
  }, [baseAmount, showSummary]);

  const fetchExchangeRates = async () => {
    try {
      setLoading(true);
      setError("");
      
      const response = await fetch(`${API}/currency/rates`);
      const data = await response.json();
      
      if (data.success) {
        setCurrencies(data.supported_currencies || []);
        setExchangeRates(data.rates || {});
        setLastUpdated(new Date(data.last_updated));
      } else {
        throw new Error("Failed to fetch exchange rates");
      }
    } catch (err) {
      setError("Failed to load exchange rates");
      console.error("Currency fetch error:", err);
      
      // Fallback currencies if API fails
      setCurrencies([
        { code: 'USD', name: 'US Dollar', symbol: '$' },
        { code: 'MXN', name: 'Mexican Peso', symbol: '$' },
        { code: 'EUR', name: 'Euro', symbol: '€' }
      ]);
      setExchangeRates({ USD: 1.0, MXN: 18.5, EUR: 0.85 });
    } finally {
      setLoading(false);
    }
  };

  const fetchCurrencySummary = async (amount) => {
    try {
      const response = await fetch(`${API}/currency/summary/${amount}`);
      const data = await response.json();
      
      if (data.success) {
        setCurrencySummary(data.conversions);
      }
    } catch (err) {
      console.error("Currency summary error:", err);
    }
  };

  const formatCurrency = (amount, currency) => {
    const currencyData = currencies.find(c => c.code === currency);
    const symbol = currencyData?.symbol || '$';
    
    if (currency === 'USD') {
      return `${symbol}${amount.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    } else if (currency === 'MXN') {
      return `${symbol}${amount.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })} MXN`;
    } else if (currency === 'EUR') {
      return `${symbol}${amount.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })} EUR`;
    } else {
      return `${symbol}${amount.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    }
  };

  const getExchangeRateDisplay = (currency) => {
    if (currency === 'USD') return null;
    const rate = exchangeRates[currency];
    if (!rate) return null;
    
    return `1 USD = ${rate.toFixed(4)} ${currency}`;
  };

  const sizeClasses = {
    sm: "h-8 text-sm",
    default: "h-10",
    lg: "h-12 text-lg"
  };

  return (
    <div className={`space-y-3 ${className}`}>
      {/* Currency Selector */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2">
          <Globe className={`${size === 'sm' ? 'w-4 h-4' : size === 'lg' ? 'w-6 h-6' : 'w-5 h-5'} text-blue-600`} />
          <span className={`${size === 'sm' ? 'text-sm' : size === 'lg' ? 'text-lg' : ''} font-medium text-gray-700`}>
            Currency:
          </span>
        </div>
        
        <Select value={selectedCurrency} onValueChange={onCurrencyChange}>
          <SelectTrigger className={`w-40 ${sizeClasses[size]} ${error ? 'border-red-300' : ''}`}>
            <SelectValue>
              <div className="flex items-center gap-2">
                <span>{CURRENCY_FLAGS[selectedCurrency] || '💱'}</span>
                <span>{selectedCurrency}</span>
              </div>
            </SelectValue>
          </SelectTrigger>
          <SelectContent>
            {currencies.map((currency) => (
              <SelectItem key={currency.code} value={currency.code}>
                <div className="flex items-center gap-2">
                  <span>{CURRENCY_FLAGS[currency.code] || '💱'}</span>
                  <span className="font-medium">{currency.code}</span>
                  <span className="text-gray-500">- {currency.name}</span>
                </div>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Button
          variant="outline"
          size={size === 'sm' ? 'sm' : 'default'}
          onClick={fetchExchangeRates}
          disabled={loading}
          className="flex items-center gap-2"
        >
          <RefreshCw className={`${loading ? 'animate-spin' : ''} ${size === 'sm' ? 'w-3 h-3' : 'w-4 h-4'}`} />
          {size !== 'sm' && 'Refresh'}
        </Button>
      </div>

      {/* Error Display */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="flex items-center gap-2 text-red-600 text-sm"
          >
            <AlertCircle className="w-4 h-4" />
            {error}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Exchange Rates Display */}
      {showRates && !error && (
        <div className="flex flex-wrap gap-2">
          {currencies.map((currency) => {
            const rateDisplay = getExchangeRateDisplay(currency.code);
            if (!rateDisplay) return null;
            
            return (
              <Badge
                key={currency.code}
                variant="outline"
                className={`${
                  selectedCurrency === currency.code 
                    ? 'bg-blue-50 border-blue-300 text-blue-700' 
                    : 'bg-gray-50 border-gray-300'
                } ${size === 'sm' ? 'text-xs px-2 py-1' : ''}`}
              >
                <span className="mr-1">{CURRENCY_FLAGS[currency.code]}</span>
                {rateDisplay}
              </Badge>
            );
          })}
          
          {lastUpdated && (
            <Badge variant="secondary" className={`${size === 'sm' ? 'text-xs px-2 py-1' : ''}`}>
              Updated: {lastUpdated.toLocaleTimeString()}
            </Badge>
          )}
        </div>
      )}

      {/* Currency Summary Card */}
      {showSummary && currencySummary && baseAmount && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          className="mt-4"
        >
          <Card className="bg-gradient-to-r from-blue-50 to-green-50 border-blue-200">
            <CardContent className="p-4">
              <div className="flex items-center gap-2 mb-3">
                <TrendingUp className="w-5 h-5 text-blue-600" />
                <h4 className="font-medium text-gray-900">
                  Currency Conversion Summary
                </h4>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {Object.entries(currencySummary).map(([currCode, data]) => (
                  <div
                    key={currCode}
                    className={`p-3 rounded-lg border ${
                      selectedCurrency === currCode
                        ? 'bg-blue-100 border-blue-300'
                        : 'bg-white border-gray-200'
                    }`}
                  >
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-lg">{CURRENCY_FLAGS[currCode]}</span>
                      <span className="font-medium text-gray-900">{currCode}</span>
                      {selectedCurrency === currCode && (
                        <Badge variant="secondary" className="text-xs">Selected</Badge>
                      )}
                    </div>
                    <div className="text-lg font-bold text-gray-900">
                      {data.formatted}
                    </div>
                    <div className="text-sm text-gray-600">
                      {currCode !== 'USD' && `Rate: ${data.rate.toFixed(4)}`}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}
    </div>
  );
};

export default CurrencySelector;