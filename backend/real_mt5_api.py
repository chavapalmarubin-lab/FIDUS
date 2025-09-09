#!/usr/bin/env python3
"""
Real MT5 API Integration for FIDUS Investment Management System
============================================================

CRITICAL PLATFORM ISSUE IDENTIFIED:
- Official MetaTrader5 Python library only works on Windows
- Current environment: Linux ARM64 (cloud deployment)
- PRODUCTION SOLUTION REQUIRED

This module provides MT5 connectivity solutions for Linux production environments.
"""

import asyncio
import logging
import platform
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
import os
import requests

# Check platform and MT5 library availability
SYSTEM_INFO = {
    'platform': platform.system(),
    'architecture': platform.machine(),
    'python_version': platform.python_version()
}

# Try to import MetaTrader5 library
MT5_LIBRARY_STATUS = 'not_available'
MT5_MODULE = None

try:
    import MetaTrader5 as mt5
    MT5_LIBRARY_STATUS = 'official_available'
    MT5_MODULE = mt5
except ImportError:
    try:
        import mt5
        MT5_LIBRARY_STATUS = 'alternative_available'
        MT5_MODULE = mt5
    except ImportError:
        MT5_LIBRARY_STATUS = 'not_available'
        MT5_MODULE = None

class RealMT5API:
    """Real MT5 API connection with platform-specific solutions"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.connected_accounts = {}
        self.platform_info = SYSTEM_INFO
        self.mt5_status = MT5_LIBRARY_STATUS
        
        self.logger.critical(f"MT5 Integration Status: {MT5_LIBRARY_STATUS}")
        self.logger.critical(f"Platform: {SYSTEM_INFO['platform']} {SYSTEM_INFO['architecture']}")
        
        if MT5_LIBRARY_STATUS == 'not_available':
            self.logger.critical("CRITICAL: No MT5 library available for this platform")
            self.logger.critical("Production MT5 application requires alternative solution")
    
    async def connect_and_get_real_data(self, mt5_login: int, password: str, server: str) -> Dict[str, Any]:
        """
        Connect to REAL MT5 account - Platform-aware implementation
        """
        
        # Platform compatibility check
        if self.platform_info['platform'] != 'Windows':
            return await self._linux_mt5_connection_attempt(mt5_login, password, server)
        else:
            return await self._windows_mt5_connection(mt5_login, password, server)
    
    async def _linux_mt5_connection_attempt(self, mt5_login: int, password: str, server: str) -> Dict[str, Any]:
        """
        Attempt MT5 connection on Linux - requires alternative solution
        """
        
        self.logger.error(f"CRITICAL: Attempting MT5 connection on {self.platform_info['platform']}")
        
        # Check if we can use broker-specific APIs instead
        broker_api_result = await self._try_broker_api_connection(mt5_login, password, server)
        if broker_api_result['status'] == 'connected':
            return broker_api_result
        
        # Check if there's a Windows bridge service available
        bridge_result = await self._try_windows_bridge_connection(mt5_login, password, server)
        if bridge_result['status'] == 'connected':
            return bridge_result
        
        # Return critical error - production deployment issue
        return {
            'status': 'critical_error',
            'error': 'MT5 connection impossible on Linux without alternative solution',
            'platform': self.platform_info['platform'],
            'architecture': self.platform_info['architecture'],
            'connected': False,
            'requires_solution': True,
            'suggested_solutions': [
                'Deploy Windows VM with MetaTrader5 terminal',
                'Use broker-specific APIs',
                'Implement MT5 Windows bridge service',
                'Use MT5 WebAPI if supported by broker'
            ]
        }
    
    async def _windows_mt5_connection(self, mt5_login: int, password: str, server: str) -> Dict[str, Any]:
        """
        Windows MT5 connection using official library
        """
        
        if MT5_MODULE is None:
            return {
                'status': 'error',
                'error': 'MetaTrader5 library not available even on Windows',
                'connected': False
            }
        
        try:
            # Initialize MT5 connection
            if not MT5_MODULE.initialize():
                return {
                    'status': 'error', 
                    'error': 'Failed to initialize MT5 - MetaTrader5 terminal may not be installed',
                    'connected': False
                }
            
            # Connect to account
            if not MT5_MODULE.login(mt5_login, password=password, server=server):
                return {
                    'status': 'error',
                    'error': f'Failed to connect to MT5 account {mt5_login}',
                    'connected': False
                }
            
            # Get account info
            account_info = MT5_MODULE.account_info()
            if account_info is None:
                return {
                    'status': 'error',
                    'error': 'Failed to get account info',
                    'connected': False
                }
            
            # Get transaction history (last 365 days)
            from_date = datetime.now() - timedelta(days=365)
            to_date = datetime.now()
            
            deals = MT5_MODULE.history_deals_get(from_date, to_date)
            
            # Analyze deposit history
            deposits = []
            total_deposits = 0
            
            if deals:
                for deal in deals:
                    if deal.type == MT5_MODULE.DEAL_TYPE_BALANCE and deal.profit > 0:  # Deposit
                        deposits.append({
                            'date': datetime.fromtimestamp(deal.time, timezone.utc),
                            'amount': deal.profit,
                            'comment': deal.comment
                        })
                        total_deposits += deal.profit
            
            # Get current balance and equity
            current_balance = account_info.balance
            current_equity = account_info.equity
            profit_loss = current_equity - total_deposits if total_deposits > 0 else 0
            
            MT5_MODULE.shutdown()
            
            return {
                'status': 'connected',
                'connected': True,
                'account_login': mt5_login,
                'server': server,
                'current_balance': current_balance,
                'current_equity': current_equity,
                'total_deposits': total_deposits,
                'profit_loss': profit_loss,
                'deposit_history': deposits,
                'last_updated': datetime.now(timezone.utc).isoformat(),
                'connection_method': 'official_mt5_library'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'connected': False
            }
    
    async def _try_broker_api_connection(self, mt5_login: int, password: str, server: str) -> Dict[str, Any]:
        """Try connecting via broker-specific APIs"""
        
        self.logger.info(f"Attempting broker API connection for {server}")
        
        # DooTechnology API attempt
        if 'doo' in server.lower():
            return await self._doo_technology_api(mt5_login, password)
        
        # VT Markets API attempt  
        elif 'vt' in server.lower():
            return await self._vt_markets_api(mt5_login, password)
        
        return {
            'status': 'error',
            'error': f'No broker API available for {server}',
            'connected': False
        }
    
    async def _doo_technology_api(self, mt5_login: int, password: str) -> Dict[str, Any]:
        """Connect to DooTechnology API if available"""
        
        # This would need real DooTechnology API credentials and endpoints
        self.logger.info("Attempting DooTechnology API connection")
        
        return {
            'status': 'error',
            'error': 'DooTechnology API not implemented - need API credentials and endpoints',
            'connected': False,
            'requires_implementation': True
        }
    
    async def _vt_markets_api(self, mt5_login: int, password: str) -> Dict[str, Any]:
        """Connect to VT Markets API if available"""
        
        # This would need real VT Markets API credentials and endpoints
        self.logger.info("Attempting VT Markets API connection")
        
        return {
            'status': 'error',
            'error': 'VT Markets API not implemented - need API credentials and endpoints',
            'connected': False,
            'requires_implementation': True
        }
    
    async def _try_windows_bridge_connection(self, mt5_login: int, password: str, server: str) -> Dict[str, Any]:
        """Try connecting via Windows bridge service"""
        
        # This would connect to a Windows service that has MetaTrader5 installed
        bridge_url = os.environ.get('MT5_BRIDGE_URL')
        
        if not bridge_url:
            return {
                'status': 'error',
                'error': 'No MT5 Windows bridge service configured',
                'connected': False
            }
        
        try:
            # Would make API call to Windows bridge service
            self.logger.info(f"Attempting Windows bridge connection to {bridge_url}")
            
            return {
                'status': 'error',
                'error': 'Windows bridge service not implemented',
                'connected': False,
                'requires_implementation': True
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': f'Bridge connection failed: {str(e)}',
                'connected': False
            }
    
    def get_platform_status(self) -> Dict[str, Any]:
        """Get current platform and MT5 library status"""
        
        return {
            'platform': self.platform_info,
            'mt5_library_status': self.mt5_status,
            'mt5_module_available': MT5_MODULE is not None,
            'production_ready': self.mt5_status == 'official_available' and self.platform_info['platform'] == 'Windows',
            'requires_alternative_solution': self.platform_info['platform'] != 'Windows'
        }

# Global instance
real_mt5_api = RealMT5API()