import requests
import logging
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional, List
import json

logger = logging.getLogger(__name__)

class CurrencyService:
    """Service for handling currency conversion with live exchange rates"""
    
    def __init__(self):
        # Use free exchangerate-api.com (no API key required)
        self.base_url = "https://api.exchangerate-api.com/v4/latest/USD"
        self.supported_currencies = ['USD', 'MXN', 'EUR']
        self.cache = {}
        self.cache_expiry = None
        self.cache_duration = timedelta(hours=1)  # Cache for 1 hour
        
    def _is_cache_valid(self) -> bool:
        """Check if current cache is still valid"""
        if not self.cache_expiry:
            return False
        return datetime.now(timezone.utc) < self.cache_expiry
    
    def _fetch_exchange_rates(self) -> Dict[str, float]:
        """Fetch latest exchange rates from free API"""
        try:
            response = requests.get(self.base_url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'rates' in data:
                rates = {
                    'USD': 1.0,
                    'MXN': data['rates'].get('MXN', 18.50),
                    'EUR': data['rates'].get('EUR', 0.85)
                }
                
                # Update cache
                self.cache = rates
                self.cache_expiry = datetime.now(timezone.utc) + self.cache_duration
                
                logger.info(f"✅ Successfully fetched LIVE exchange rates: USD/MXN={rates['MXN']:.4f}, USD/EUR={rates['EUR']:.4f}")
                return rates
            else:
                raise ValueError("Invalid API response format")
                
        except requests.RequestException as e:
            logger.error(f"Failed to fetch exchange rates: {str(e)}")
            return self._get_fallback_rates()
        except Exception as e:
            logger.error(f"Unexpected error fetching exchange rates: {str(e)}")
            return self._get_fallback_rates()
    
    def _get_fallback_rates(self) -> Dict[str, float]:
        """Fallback rates if API is unavailable (updated to recent approximate rates)"""
        logger.warning("Using fallback exchange rates")
        return {
            'USD': 1.0,
            'MXN': 17.20,  # Approximate USD/MXN rate as of Feb 2026
            'EUR': 0.85    # Approximate USD/EUR rate
        }
    
    def get_exchange_rates(self) -> Dict[str, float]:
        """Get current exchange rates (cached or fresh)"""
        if self._is_cache_valid():
            return self.cache
        
        return self._fetch_exchange_rates()
    
    def convert_amount(self, amount: float, from_currency: str = 'USD', to_currency: str = 'USD') -> float:
        """Convert amount from one currency to another"""
        if from_currency == to_currency:
            return amount
        
        if from_currency not in self.supported_currencies or to_currency not in self.supported_currencies:
            raise ValueError(f"Unsupported currency. Supported: {self.supported_currencies}")
        
        rates = self.get_exchange_rates()
        
        if from_currency == 'USD':
            # Direct conversion from USD
            return amount * rates.get(to_currency, 1.0)
        elif to_currency == 'USD':
            # Convert to USD
            from_rate = rates.get(from_currency, 1.0)
            return amount / from_rate if from_rate != 0 else amount
        else:
            # Convert via USD (from_currency -> USD -> to_currency)
            usd_amount = self.convert_amount(amount, from_currency, 'USD')
            return self.convert_amount(usd_amount, 'USD', to_currency)
    
    def get_currency_info(self) -> List[Dict[str, str]]:
        """Get supported currency information"""
        return [
            {'code': 'USD', 'name': 'US Dollar', 'symbol': '$'},
            {'code': 'MXN', 'name': 'Mexican Peso', 'symbol': '$'},
            {'code': 'EUR', 'name': 'Euro', 'symbol': '€'}
        ]
    
    def format_currency(self, amount: float, currency: str = 'USD') -> str:
        """Format amount with appropriate currency symbol"""
        currency_symbols = {
            'USD': '$',
            'MXN': '$',
            'EUR': '€'
        }
        
        symbol = currency_symbols.get(currency, '$')
        
        if currency == 'USD':
            return f"{symbol}{amount:,.2f}"
        elif currency == 'MXN':
            return f"{symbol}{amount:,.2f} MXN"
        elif currency == 'EUR':
            return f"{symbol}{amount:,.2f} EUR"
        else:
            return f"{symbol}{amount:,.2f}"
    
    def get_conversion_summary(self, base_amount: float, currency: str = 'USD') -> Dict[str, Dict[str, any]]:
        """Get conversion summary for all supported currencies"""
        rates = self.get_exchange_rates()
        summary = {}
        
        for curr in self.supported_currencies:
            converted_amount = self.convert_amount(base_amount, 'USD', curr)
            summary[curr] = {
                'amount': converted_amount,
                'formatted': self.format_currency(converted_amount, curr),
                'rate': rates.get(curr, 1.0),
                'name': next(c['name'] for c in self.get_currency_info() if c['code'] == curr),
                'symbol': next(c['symbol'] for c in self.get_currency_info() if c['code'] == curr)
            }
        
        return summary

# Global currency service instance
currency_service = CurrencyService()