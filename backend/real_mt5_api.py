#!/usr/bin/env python3
"""
Real MT5 API Integration for FIDUS Investment Management System
============================================================

PRODUCTION SYSTEM - NO MOCK DATA
This module connects to REAL MT5 accounts to get:
- Actual deposit history and dates
- Real current balances
- Transaction records
- Account connection status
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
import os

try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False

class RealMT5API:
    """Real MT5 API connection - NO MOCK DATA ALLOWED"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.connected_accounts = {}
        
        if not MT5_AVAILABLE:
            self.logger.critical("MetaTrader5 library not available - install: pip install MetaTrader5")
    
    async def connect_and_get_real_data(self, mt5_login: int, password: str, server: str) -> Dict[str, Any]:
        """
        Connect to REAL MT5 account and get ACTUAL historical data
        
        Returns:
            Dict with real account data or error status
        """
        if not MT5_AVAILABLE:
            return {
                'status': 'error',
                'error': 'MetaTrader5 library not installed',
                'connected': False
            }
        
        try:
            # Initialize MT5 connection
            if not mt5.initialize():
                return {
                    'status': 'error', 
                    'error': 'Failed to initialize MT5',
                    'connected': False
                }
            
            # Connect to account
            if not mt5.login(mt5_login, password=password, server=server):
                return {
                    'status': 'error',
                    'error': f'Failed to connect to MT5 account {mt5_login}',
                    'connected': False
                }
            
            # Get account info
            account_info = mt5.account_info()
            if account_info is None:
                return {
                    'status': 'error',
                    'error': 'Failed to get account info',
                    'connected': False
                }
            
            # Get transaction history (last 365 days)
            from_date = datetime.now() - timedelta(days=365)
            to_date = datetime.now()
            
            deals = mt5.history_deals_get(from_date, to_date)
            
            # Analyze deposit history
            deposits = []
            total_deposits = 0
            
            if deals:
                for deal in deals:
                    if deal.type == mt5.DEAL_TYPE_BALANCE and deal.profit > 0:  # Deposit
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
            
            mt5.shutdown()
            
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
                'last_updated': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'connected': False
            }
    
    def get_mock_status_for_disconnected_account(self, mt5_login: int) -> Dict[str, Any]:
        """
        Return disconnected status for accounts that can't connect to real MT5
        """
        return {
            'status': 'disconnected',
            'connected': False,
            'account_login': mt5_login,
            'error': 'MT5 credentials not provided or MetaTrader5 library not available',
            'current_balance': 0,
            'current_equity': 0,
            'total_deposits': 0,
            'profit_loss': 0,
            'deposit_history': [],
            'requires_real_connection': True
        }

# Global instance
real_mt5_api = RealMT5API()