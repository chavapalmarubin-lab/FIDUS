"""
Enhanced MT5 Bridge Client for FIDUS Investment Management System
Production-grade client for Windows VPS MT5 Bridge Service with comprehensive error handling
"""

import asyncio
import aiohttp
import logging
import os
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timezone, timedelta
import json
from decimal import Decimal
import time

class MT5BridgeClient:
    """Production-grade client to communicate with MT5 Bridge Service on Windows VPS"""
    
    def __init__(self):
        self.bridge_url = os.environ.get('MT5_BRIDGE_URL', 'http://217.197.163.11:8000')
        self.api_key = os.environ.get('MT5_BRIDGE_API_KEY', 'fidus-mt5-bridge-key-2025-secure')
        self.timeout = int(os.environ.get('MT5_BRIDGE_TIMEOUT', '30'))
        self.session = None
        self.logger = logging.getLogger(__name__)
        self.last_health_check = None
        self.is_healthy = False
        self.retry_attempts = 3
        self.retry_delay = 1  # seconds
        
    async def _ensure_session(self):
        """Ensure aiohttp session is available"""
        if self.session is None or self.session.closed:
            connector = aiohttp.TCPConnector(
                ssl=False,  # For development - use True in production with proper SSL
                limit_per_host=10,
                ttl_dns_cache=300
            )
            
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=aiohttp.ClientTimeout(total=self.timeout),
                headers={
                    'Content-Type': 'application/json',
                    'X-API-Key': self.api_key
                }
            )
    
    async def _make_request(self, method: str, endpoint: str, data: dict = None) -> dict:
        """Make HTTP request to MT5 Bridge Service"""
        await self._ensure_session()
        
        url = f"{self.bridge_url}{endpoint}"
        
        try:
            return await self._make_request_with_retry(method, url, json=data)
        
    async def _make_request_with_retry(self, method: str, url: str, **kwargs) -> dict:
        """Make HTTP request with retry logic"""
        last_error = None
        
        for attempt in range(self.retry_attempts):
            try:
                await self._ensure_session()
                
                async with self.session.request(method, url, **kwargs) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 401:
                        return {'success': False, 'error': 'Invalid API key'}
                    elif response.status == 503:
                        # Service temporarily unavailable - retry
                        if attempt < self.retry_attempts - 1:
                            await asyncio.sleep(self.retry_delay * (2 ** attempt))
                            continue
                        return {'success': False, 'error': 'MT5 Bridge service unavailable'}
                    else:
                        error_text = await response.text()
                        self.logger.error(f"MT5 Bridge API error {response.status}: {error_text}")
                        return {
                            'success': False, 
                            'error': f"HTTP {response.status}: {error_text}"
                        }
                        
            except asyncio.TimeoutError as e:
                last_error = f"Connection timeout: {e}"
                self.logger.warning(f"MT5 Bridge timeout attempt {attempt + 1}/{self.retry_attempts}")
                if attempt < self.retry_attempts - 1:
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))
                    continue
                    
            except Exception as e:
                last_error = f"Connection error: {e}"
                self.logger.warning(f"MT5 Bridge error attempt {attempt + 1}/{self.retry_attempts}: {e}")
                if attempt < self.retry_attempts - 1:
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))
                    continue
                    
        # All retry attempts failed
        self.logger.error(f"MT5 Bridge failed after {self.retry_attempts} attempts: {last_error}")
        return {'success': False, 'error': last_error or 'Unknown error'}
    
    async def health_check(self) -> Dict[str, Any]:
        """Check if MT5 Bridge Service is healthy"""
        return await self._make_request('GET', '/health')
    
    async def mt5_initialize(self) -> Dict[str, Any]:
        """Initialize MT5 connection on bridge service"""
        return await self._make_request('POST', '/api/mt5/initialize')
    
    async def mt5_login(self, login: int, password: str, server: str) -> Dict[str, Any]:
        """Login to MT5 account via bridge service"""
        return await self._make_request('POST', '/api/mt5/login', {
            'login': login,
            'password': password,
            'server': server
        })
    
    async def get_account_info(self, login: int) -> Dict[str, Any]:
        """Get MT5 account information"""
        return await self._make_request('GET', f'/api/mt5/account/{login}/info')
    
    async def get_account_history(self, login: int, from_date: str = None, to_date: str = None) -> Dict[str, Any]:
        """Get MT5 account trading history"""
        params = {'login': login}
        if from_date:
            params['from_date'] = from_date
        if to_date:
            params['to_date'] = to_date
            
        return await self._make_request('POST', '/api/mt5/history', params)
    
    async def get_positions(self, login: int) -> Dict[str, Any]:
        """Get current open positions"""
        return await self._make_request('GET', f'/api/mt5/account/{login}/positions')
    
    async def get_deals(self, login: int, from_date: str = None, to_date: str = None) -> Dict[str, Any]:
        """Get deals history for finding deposits/withdrawals"""
        params = {'login': login}
        if from_date:
            params['from_date'] = from_date
        if to_date:
            params['to_date'] = to_date
            
        return await self._make_request('POST', '/api/mt5/deals', params)
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test full MT5 connection through bridge"""
        try:
            # Test bridge health
            health = await self.health_check()
            if not health.get('success'):
                return health
            
            # Test MT5 initialization
            init_result = await self.mt5_initialize()
            
            return {
                'success': True,
                'bridge_health': health,
                'mt5_init': init_result,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    async def close(self):
        """Close aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()

# Global instance
mt5_bridge = MT5BridgeClient()

# For testing
async def test_bridge_connectivity():
    """Test connectivity to MT5 Bridge Service"""
    print("🔗 Testing MT5 Bridge Service Connectivity...")
    
    try:
        result = await mt5_bridge.test_connection()
        
        if result['success']:
            print("✅ MT5 Bridge Service connection successful!")
            print(f"   Bridge Health: {result['bridge_health']}")
            print(f"   MT5 Init: {result['mt5_init']}")
        else:
            print("❌ MT5 Bridge Service connection failed:")
            print(f"   Error: {result['error']}")
            
    except Exception as e:
        print(f"❌ Bridge test failed: {e}")
    
    finally:
        await mt5_bridge.close()

if __name__ == "__main__":
    asyncio.run(test_bridge_connectivity())