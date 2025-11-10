"""
Account Flow Calculator Service
Calculates TRUE P&L based on actual deposits/withdrawals from deal history
"""
import logging
from typing import Dict, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)

class AccountFlowCalculator:
    """Calculate true P&L by tracking actual money flow per account"""
    
    # TRUTH: One client invested this total amount
    CLIENT_TOTAL_INVESTMENT = 118151.41
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    async def calculate_account_net_deposits(self, account_number: int) -> Dict:
        """
        Calculate net deposits for a specific account from deal history
        
        Returns:
            {
                "account_number": int,
                "total_deposits": float,  # Sum of positive type 2 deals
                "total_withdrawals": float,  # Sum of negative type 2 deals
                "net_deposits": float,  # Net money deposited into account
                "current_balance": float,
                "true_pnl": float,  # balance - net_deposits
                "return_pct": float
            }
        """
        try:
            # Get all balance operations (type 2) for this account
            deals_cursor = self.db.mt5_deals_history.find({
                "account_number": account_number,
                "type": 2  # Balance operations (deposits/withdrawals)
            })
            deals = await deals_cursor.to_list(length=None)
            
            deposits = sum(d.get('profit', 0) for d in deals if d.get('profit', 0) > 0)
            withdrawals = sum(d.get('profit', 0) for d in deals if d.get('profit', 0) < 0)
            net_deposits = deposits + withdrawals  # withdrawals are negative
            
            # Get current balance
            account_data = await self.db.mt5_accounts.find_one({"account": account_number})
            current_balance = account_data.get('balance', 0) if account_data else 0
            
            # TRUE P&L = what you have now - what you put in
            true_pnl = current_balance - net_deposits
            return_pct = (true_pnl / net_deposits * 100) if net_deposits > 0 else 0
            
            return {
                "account_number": account_number,
                "total_deposits": round(deposits, 2),
                "total_withdrawals": round(withdrawals, 2),
                "net_deposits": round(net_deposits, 2),
                "current_balance": round(current_balance, 2),
                "true_pnl": round(true_pnl, 2),
                "return_pct": round(return_pct, 2)
            }
            
        except Exception as e:
            logger.error(f"Error calculating account flow for {account_number}: {e}")
            return {
                "account_number": account_number,
                "net_deposits": 0,
                "current_balance": 0,
                "true_pnl": 0,
                "return_pct": 0
            }
    
    async def calculate_platform_totals(self) -> Dict:
        """
        Calculate platform-wide totals
        
        Returns:
            {
                "client_investment": float,  # The one true constant
                "current_total_balance": float,
                "total_pnl": float,
                "return_pct": float
            }
        """
        try:
            # Get all MT5 accounts
            accounts_cursor = self.db.mt5_accounts.find({})
            accounts = await accounts_cursor.to_list(length=None)
            
            current_total = sum(acc.get('balance', 0) for acc in accounts)
            total_pnl = current_total - self.CLIENT_TOTAL_INVESTMENT
            return_pct = (total_pnl / self.CLIENT_TOTAL_INVESTMENT) * 100
            
            return {
                "client_investment": round(self.CLIENT_TOTAL_INVESTMENT, 2),
                "current_total_balance": round(current_total, 2),
                "total_pnl": round(total_pnl, 2),
                "return_pct": round(return_pct, 2)
            }
            
        except Exception as e:
            logger.error(f"Error calculating platform totals: {e}")
            return {
                "client_investment": self.CLIENT_TOTAL_INVESTMENT,
                "current_total_balance": 0,
                "total_pnl": 0,
                "return_pct": 0
            }
