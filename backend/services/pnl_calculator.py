"""
TRUE P&L Calculator Service

Calculates accurate Profit & Loss for MT5 accounts by:
1. Using correct initial allocations (from user investments)
2. Including profit withdrawals to separation accounts
3. Excluding internal transfers and P/L Share operations

Formula: TRUE P&L = (Current Equity + Profit Withdrawals) - Initial Allocation
"""

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
import os
import logging
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class PnLCalculator:
    def __init__(self, db):
        """
        Initialize PnLCalculator with async motor database
        
        Args:
            db: AsyncIOMotorDatabase instance
        """
        self.db = db
        self.is_async = hasattr(db, 'command')  # Motor has command, sync doesn't
        
    async def calculate_account_pnl(self, account_number: int) -> Dict:
        """
        Calculate TRUE P&L for a single account
        
        Returns:
        {
            'account_number': int,
            'initial_allocation': float,
            'current_equity': float,
            'profit_withdrawals': float,
            'true_pnl': float,
            'true_pnl_percent': float,
            'displayed_pnl': float  # MT5's reported profit (may be wrong)
        }
        """
        # Get account data
        account = await self.db.mt5_accounts.find_one({'account': account_number})
        if not account:
            logger.warning(f"Account {account_number} not found in mt5_accounts")
            return None
            
        # Get initial allocation from config
        config = await self.db.mt5_account_config.find_one({'account': account_number})
        initial_allocation = config.get('initial_allocation', 0) if config else 0
        
        # Get current state
        current_equity = account.get('equity', 0)
        displayed_pnl = account.get('profit', 0)
        
        # Get profit withdrawals from corrected data
        corrected = await self.db.mt5_corrected_data.find_one({'account_number': account_number})
        profit_withdrawals = corrected.get('profit_withdrawals', 0) if corrected else 0
        
        # Get inter-account transfers (money moved to/from separation accounts)
        # Transfers OUT are stored as POSITIVE (profit taken to separation accounts)
        inter_account_transfers = float(account.get('inter_account_transfers', 0))
        
        # Calculate TRUE P&L
        # Formula: Current Equity + Profit Withdrawals + Inter-Account Transfers - Initial Allocation
        # Why we ADD transfers: When $100k is moved to separation accounts, it's PROFIT that was taken
        # Must add it back to show true performance (not count it as a loss)
        true_pnl = (current_equity + profit_withdrawals + inter_account_transfers) - initial_allocation
        true_pnl_percent = (true_pnl / initial_allocation * 100) if initial_allocation > 0 else 0
        
        return {
            'account_number': account_number,
            'account_name': account.get('name', f'Account {account_number}'),
            'fund_type': config.get('fund_type') if config else account.get('fund_code'),
            'initial_allocation': round(initial_allocation, 2),
            'current_equity': round(current_equity, 2),
            'profit_withdrawals': round(profit_withdrawals, 2),
            'inter_account_transfers': round(inter_account_transfers, 2),  # NEW: Include in response
            'true_pnl': round(true_pnl, 2),
            'true_pnl_percent': round(true_pnl_percent, 2),
            'displayed_pnl': round(displayed_pnl, 2),
            'last_updated': datetime.utcnow()
        }
    
    async def calculate_fund_pnl(self, fund_code: str) -> Dict:
        """
        Calculate TRUE P&L for all accounts in a fund
        
        Returns aggregated P&L for the fund
        """
        # Get all accounts for this fund
        configs = await self.db.mt5_account_config.find({'fund_type': fund_code, 'is_active': True}).to_list(length=100)
        
        total_initial = 0
        total_equity = 0
        total_withdrawals = 0
        total_true_pnl = 0
        accounts_data = []
        
        for config in configs:
            account_pnl = await self.calculate_account_pnl(config['account'])
            if account_pnl:
                accounts_data.append(account_pnl)
                total_initial += account_pnl['initial_allocation']
                total_equity += account_pnl['current_equity']
                total_withdrawals += account_pnl['profit_withdrawals']
                total_true_pnl += account_pnl['true_pnl']
        
        total_pnl_percent = (total_true_pnl / total_initial * 100) if total_initial > 0 else 0
        
        return {
            'fund_code': fund_code,
            'total_initial_allocation': round(total_initial, 2),
            'total_current_equity': round(total_equity, 2),
            'total_profit_withdrawals': round(total_withdrawals, 2),
            'total_true_pnl': round(total_true_pnl, 2),
            'total_pnl_percent': round(total_pnl_percent, 2),
            'account_count': len(accounts_data),
            'accounts': accounts_data,
            'last_updated': datetime.utcnow()
        }
    
    async def calculate_all_accounts_pnl(self) -> Dict:
        """
        Calculate TRUE P&L for ALL active accounts across all funds
        
        Returns comprehensive portfolio P&L
        """
        # Get all active TRADING accounts (exclude SEPARATION accounts)
        configs = await self.db.mt5_account_config.find({
            'is_active': True,
            'fund_type': {'$nin': ['SEPARATION']}  # Exclude separation accounts
        }).to_list(length=100)
        
        total_initial = 0
        total_equity = 0
        total_withdrawals = 0
        total_true_pnl = 0
        
        accounts_data = []
        funds_summary = {}
        
        for config in configs:
            account_pnl = await self.calculate_account_pnl(config['account'])
            if account_pnl:
                accounts_data.append(account_pnl)
                
                # Aggregate by fund
                fund = account_pnl.get('fund_type', 'UNKNOWN')
                if fund not in funds_summary:
                    funds_summary[fund] = {
                        'fund_code': fund,
                        'initial_allocation': 0,
                        'current_equity': 0,
                        'profit_withdrawals': 0,
                        'true_pnl': 0,
                        'account_count': 0
                    }
                
                funds_summary[fund]['initial_allocation'] += account_pnl['initial_allocation']
                funds_summary[fund]['current_equity'] += account_pnl['current_equity']
                funds_summary[fund]['profit_withdrawals'] += account_pnl['profit_withdrawals']
                funds_summary[fund]['true_pnl'] += account_pnl['true_pnl']
                funds_summary[fund]['account_count'] += 1
                
                # Portfolio totals
                total_initial += account_pnl['initial_allocation']
                total_equity += account_pnl['current_equity']
                total_withdrawals += account_pnl['profit_withdrawals']
                total_true_pnl += account_pnl['true_pnl']
        
        # Calculate fund percentages
        for fund_data in funds_summary.values():
            if fund_data['initial_allocation'] > 0:
                fund_data['pnl_percent'] = round(
                    fund_data['true_pnl'] / fund_data['initial_allocation'] * 100, 
                    2
                )
            else:
                fund_data['pnl_percent'] = 0
        
        total_pnl_percent = (total_true_pnl / total_initial * 100) if total_initial > 0 else 0
        
        return {
            'portfolio_summary': {
                'total_initial_allocation': round(total_initial, 2),
                'total_current_equity': round(total_equity, 2),
                'total_profit_withdrawals': round(total_withdrawals, 2),
                'total_true_pnl': round(total_true_pnl, 2),
                'total_pnl_percent': round(total_pnl_percent, 2),
                'total_accounts': len(accounts_data)
            },
            'funds': list(funds_summary.values()),
            'accounts': accounts_data,
            'last_updated': datetime.utcnow()
        }

    async def set_initial_allocations(self, allocations: Dict[int, float]):
        """
        Update initial allocations for accounts
        
        Args:
            allocations: Dict mapping account_number -> initial_allocation amount
        
        Example:
            {
                886557: 80000.00,
                886066: 10000.00,
                886602: 10000.00,
                885822: 18151.41
            }
        """
        logger.info(f"Updating initial allocations for {len(allocations)} accounts")
        
        for account_number, amount in allocations.items():
            result = await self.db.mt5_account_config.update_one(
                {'account': account_number},
                {'$set': {
                    'initial_allocation': amount,
                    'updated_at': datetime.utcnow()
                }},
                upsert=False
            )
            
            if result.modified_count > 0:
                logger.info(f"  ✅ Account {account_number}: ${amount:,.2f}")
            else:
                logger.warning(f"  ⚠️ Account {account_number}: Not found in config")
        
        logger.info("Initial allocations update complete")
