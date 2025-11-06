"""
THREE-TIER P&L Calculator Service

Calculates P&L separately for three capital sources:
1. CLIENT P&L - For client reporting (Alejandro Mariscal Romero)
2. FIDUS P&L - For house capital performance
3. TOTAL FUND P&L - For overall fund performance

Uses MT5 deal history as source of truth for:
- True client deposits (Deposit-CTFBP comments)
- Profit withdrawals (transfers to separation accounts)
- Excluding internal transfers between trading accounts

Formula: TRUE P&L = (Current Equity + Profit Withdrawals) - Initial Allocation
"""

from motor.motor_asyncio import AsyncIOMotorClient
import logging
from datetime import datetime
from typing import Dict, List, Optional
from decimal import Decimal

logger = logging.getLogger(__name__)


class ThreeTierPnLCalculator:
    def __init__(self, db):
        """
        Initialize ThreeTierPnLCalculator with async motor database
        
        Args:
            db: AsyncIOMotorDatabase instance
        """
        self.db = db
        
    def to_float(self, value):
        """Convert Decimal128 or any number to float"""
        if hasattr(value, 'to_decimal'):
            return float(value.to_decimal())
        return float(value) if value else 0.0
    
    async def calculate_tier_pnl(self, capital_source: str, client_id: Optional[str] = None) -> Dict:
        """
        Calculate P&L for a specific capital source tier
        
        Args:
            capital_source: 'client', 'fidus', or 'reinvested_profit'
            client_id: Optional client ID for filtering client accounts
        
        Returns:
            {
                'capital_source': str,
                'client_id': str or None,
                'initial_allocation': float,
                'current_equity': float,
                'profit_withdrawals': float,
                'true_pnl': float,
                'return_percent': float,
                'account_count': int,
                'accounts': List[Dict]
            }
        """
        # Build query
        query = {'capital_source': capital_source}
        if client_id:
            query['client_id'] = client_id
        
        # Get all accounts for this tier
        accounts = await self.db.mt5_accounts.find(query).to_list(None)
        
        total_allocation = 0
        total_equity = 0
        total_withdrawals = 0
        accounts_detail = []
        
        for account in accounts:
            account_number = account.get('account')
            fund_type = account.get('fund_type', 'Unknown')
            
            # Get values
            initial_alloc = self.to_float(account.get('initial_allocation', 0))
            current_equity = self.to_float(account.get('equity', 0))
            
            # Get profit withdrawals from deal history embedded in account
            profit_withdrawals = 0
            deal_history = account.get('deal_history', {})
            if deal_history:
                profit_withdrawals = self.to_float(deal_history.get('total_profit_withdrawals', 0))
            
            # Calculate account P&L
            account_pnl = current_equity + profit_withdrawals - initial_alloc
            account_return = (account_pnl / initial_alloc * 100) if initial_alloc > 0 else 0
            
            # Aggregate
            total_allocation += initial_alloc
            total_equity += current_equity
            total_withdrawals += profit_withdrawals
            
            # Add to detail
            accounts_detail.append({
                'account_number': account_number,
                'fund_type': fund_type,
                'initial_allocation': round(initial_alloc, 2),
                'current_equity': round(current_equity, 2),
                'profit_withdrawals': round(profit_withdrawals, 2),
                'pnl': round(account_pnl, 2),
                'return_percent': round(account_return, 2)
            })
        
        # Calculate tier totals
        total_pnl = total_equity + total_withdrawals - total_allocation
        total_return = (total_pnl / total_allocation * 100) if total_allocation > 0 else 0
        
        return {
            'capital_source': capital_source,
            'client_id': client_id,
            'initial_allocation': round(total_allocation, 2),
            'current_equity': round(total_equity, 2),
            'profit_withdrawals': round(total_withdrawals, 2),
            'true_pnl': round(total_pnl, 2),
            'return_percent': round(total_return, 2),
            'account_count': len(accounts_detail),
            'accounts': accounts_detail
        }
    
    async def calculate_all_tiers(self) -> Dict:
        """
        Calculate P&L for all three tiers
        
        Returns:
            {
                'client_pnl': {...},
                'fidus_pnl': {...},
                'reinvested_pnl': {...},
                'total_fund_pnl': {...},
                'separation_balance': float,
                'last_updated': datetime
            }
        """
        # Calculate each tier
        client_pnl = await self.calculate_tier_pnl('client', 'client_alejandro')
        fidus_pnl = await self.calculate_tier_pnl('fidus')
        reinvested_pnl = await self.calculate_tier_pnl('reinvested_profit')
        
        # Calculate separation balance
        separation_accounts = await self.db.mt5_accounts.find({'capital_source': 'separation'}).to_list(None)
        separation_balance = sum([self.to_float(acc.get('equity', 0)) for acc in separation_accounts])
        
        # Calculate total fund P&L
        total_allocation = client_pnl['initial_allocation'] + fidus_pnl['initial_allocation']
        total_equity = client_pnl['current_equity'] + fidus_pnl['current_equity'] + reinvested_pnl['current_equity']
        total_withdrawals = client_pnl['profit_withdrawals'] + fidus_pnl['profit_withdrawals']
        total_pnl = total_equity + total_withdrawals - total_allocation
        total_return = (total_pnl / total_allocation * 100) if total_allocation > 0 else 0
        
        total_fund_pnl = {
            'initial_allocation': round(total_allocation, 2),
            'current_equity': round(total_equity, 2),
            'profit_withdrawals': round(total_withdrawals, 2),
            'true_pnl': round(total_pnl, 2),
            'return_percent': round(total_return, 2),
            'account_count': (client_pnl['account_count'] + 
                            fidus_pnl['account_count'] + 
                            reinvested_pnl['account_count'])
        }
        
        return {
            'client_pnl': client_pnl,
            'fidus_pnl': fidus_pnl,
            'reinvested_pnl': reinvested_pnl,
            'total_fund_pnl': total_fund_pnl,
            'separation_balance': round(separation_balance, 2),
            'last_updated': datetime.utcnow().isoformat()
        }
    
    async def get_client_view(self, client_id: str) -> Dict:
        """
        Get P&L view for a specific client (what they see on their dashboard)
        
        Args:
            client_id: Client identifier (e.g., 'client_alejandro')
        
        Returns:
            Client-specific P&L with only their accounts
        """
        client_pnl = await self.calculate_tier_pnl('client', client_id)
        
        # Add separation balance (their share of extracted profits)
        separation_accounts = await self.db.mt5_accounts.find({'capital_source': 'separation'}).to_list(None)
        separation_balance = sum([self.to_float(acc.get('equity', 0)) for acc in separation_accounts])
        
        # Client total value = current equity + separation balance
        total_value = client_pnl['current_equity'] + separation_balance
        total_pnl_including_separation = total_value - client_pnl['initial_allocation']
        total_return_including_separation = (total_pnl_including_separation / client_pnl['initial_allocation'] * 100) if client_pnl['initial_allocation'] > 0 else 0
        
        return {
            'client_id': client_id,
            'initial_investment': client_pnl['initial_allocation'],
            'current_equity': client_pnl['current_equity'],
            'available_for_withdrawal': round(separation_balance, 2),
            'total_value': round(total_value, 2),
            'total_pnl': round(total_pnl_including_separation, 2),
            'total_return_percent': round(total_return_including_separation, 2),
            'accounts': client_pnl['accounts'],
            'last_updated': datetime.utcnow().isoformat()
        }
    
    async def get_admin_view(self) -> Dict:
        """
        Get comprehensive admin view with all three tiers
        
        Returns:
            Complete breakdown for FIDUS admin dashboard
        """
        return await self.calculate_all_tiers()
