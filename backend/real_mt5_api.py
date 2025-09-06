#!/usr/bin/env python3
"""
Real MT5 API Integration for FIDUS Investment Management System
============================================================

This module provides real MT5 API connections to get actual account data,
transaction history, and deposit dates - NO MOCK DATA.
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import os

# Note: In production, install MetaTrader5 package
# pip install MetaTrader5

try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False
    print("⚠️  MetaTrader5 package not installed. Install with: pip install MetaTrader5")

class RealMT5API:
    """Real MT5 API connection for getting actual account data"""
    
    def __init__(self):
        self.setup_logging()
        self.connected_accounts = {}
        
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    async def connect_to_real_mt5_account(self, login: int, password: str, server: str) -> bool:
        """
        Connect to real MT5 account and get actual data
        
        Args:
            login: MT5 account login number (e.g., 9928326)
            password: MT5 account password
            server: MT5 server name
            
        Returns:
            bool: True if connection successful
        """
        if not MT5_AVAILABLE:
            self.logger.error("MetaTrader5 package not available. Cannot connect to real MT5.")
            return False
            
        try:
            # Initialize MT5 connection
            if not mt5.initialize():
                self.logger.error("Failed to initialize MT5")
                return False
            
            # Login to account
            if not mt5.login(login, password=password, server=server):
                self.logger.error(f"Failed to login to MT5 account {login}")
                mt5.shutdown()
                return False
            
            self.logger.info(f"✅ Successfully connected to real MT5 account {login}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error connecting to MT5 account {login}: {str(e)}")
            return False
    
    async def get_real_account_history(self, login: int, password: str, server: str) -> Optional[Dict[str, Any]]:
        """
        Get complete account history from real MT5 API
        
        Returns:
            Dict containing:
            - first_deposit_date: When account was first funded
            - deposit_history: All deposits
            - withdrawal_history: All withdrawals
            - account_creation_date: When account was created
            - current_balance: Current account balance
            - current_equity: Current equity
            - total_profit: Total profit/loss
        """
        if not await self.connect_to_real_mt5_account(login, password, server):
            return None
            
        try:
            # Get account info
            account_info = mt5.account_info()
            if not account_info:
                self.logger.error("Failed to get account info")
                return None
            
            # Get complete deal history from account creation to now
            # This gets ALL transactions since account creation
            from_date = datetime(2020, 1, 1)  # Start from 2020 to ensure we get everything
            to_date = datetime.now()
            
            deals = mt5.history_deals_get(from_date, to_date)
            if not deals:
                self.logger.warning("No deal history found")
                return None
            
            # Process deals to find deposits, withdrawals, and first deposit date
            deposits = []
            withdrawals = []
            first_deposit_date = None
            total_deposits = 0
            total_withdrawals = 0
            
            for deal in deals:
                deal_dict = deal._asdict()
                deal_time = datetime.fromtimestamp(deal.time, tz=timezone.utc)
                
                # Check for balance operations (deposits/withdrawals)
                if deal.type == mt5.DEAL_TYPE_BALANCE:
                    if deal.profit > 0:  # Deposit
                        deposit_record = {
                            "date": deal_time,
                            "amount": deal.profit,
                            "comment": deal.comment,
                            "ticket": deal.ticket
                        }
                        deposits.append(deposit_record)
                        total_deposits += deal.profit
                        
                        # Track first deposit
                        if first_deposit_date is None or deal_time < first_deposit_date:
                            first_deposit_date = deal_time
                    
                    elif deal.profit < 0:  # Withdrawal
                        withdrawal_record = {
                            "date": deal_time,
                            "amount": abs(deal.profit),
                            "comment": deal.comment,
                            "ticket": deal.ticket
                        }
                        withdrawals.append(withdrawal_record)
                        total_withdrawals += abs(deal.profit)
            
            # Sort by date
            deposits.sort(key=lambda x: x["date"])
            withdrawals.sort(key=lambda x: x["date"])
            
            result = {
                "login": login,
                "server": server,
                "account_creation_date": datetime.fromtimestamp(account_info.creation_time, tz=timezone.utc) if hasattr(account_info, 'creation_time') else None,
                "first_deposit_date": first_deposit_date,
                "deposits": deposits,
                "withdrawals": withdrawals,
                "total_deposits": total_deposits,
                "total_withdrawals": total_withdrawals,
                "current_balance": account_info.balance,
                "current_equity": account_info.equity,
                "current_profit": account_info.profit,
                "leverage": account_info.leverage,
                "currency": account_info.currency,
                "data_retrieved_at": datetime.now(timezone.utc)
            }
            
            self.logger.info(f"✅ Retrieved complete account history for {login}")
            self.logger.info(f"   First deposit: {first_deposit_date}")
            self.logger.info(f"   Total deposits: ${total_deposits:,.2f}")
            self.logger.info(f"   Total withdrawals: ${total_withdrawals:,.2f}")
            self.logger.info(f"   Current balance: ${account_info.balance:,.2f}")
            self.logger.info(f"   Current equity: ${account_info.equity:,.2f}")
            
            # Shutdown MT5 connection
            mt5.shutdown()
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error getting account history: {str(e)}")
            mt5.shutdown()
            return None
    
    async def get_salvador_real_data(self) -> Optional[Dict[str, Any]]:
        """
        Get Salvador's real MT5 account data (login 9928326)
        
        Using REAL MT5 credentials provided by user
        """
        # Salvador's REAL account details
        login = 9928326
        password = "R1d567j!"  # Real trading password provided
        server = "DooTechnology-Live"  # Real server provided
        
        self.logger.info(f"🔗 Connecting to REAL MT5 account {login} on {server}")
        
        # Connect to real MT5 account and get actual transaction history
        return await self.get_real_account_history(login, password, server)

# Example usage
async def main():
    """Example of how to use RealMT5API"""
    api = RealMT5API()
    
    print("🔍 Real MT5 API - Getting Salvador's Account History")
    print("=" * 60)
    
    # This would get real data if credentials are available
    real_data = await api.get_salvador_real_data()
    
    if real_data:
        print("✅ Real MT5 data retrieved successfully!")
        print(f"First deposit date: {real_data['first_deposit_date']}")
        print(f"Total deposits: ${real_data['total_deposits']:,.2f}")
    else:
        print("❌ Could not retrieve real MT5 data")
        print("   Reason: Real MT5 credentials required")

if __name__ == "__main__":
    asyncio.run(main())