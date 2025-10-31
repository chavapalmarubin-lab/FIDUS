"""
True P&L Calculator Service
Calculates accurate Profit & Loss accounting for deposits and withdrawals.

CRITICAL FORMULA:
TRUE P&L = (Current Equity + Total Withdrawals) - (Initial Allocation + Total Deposits)

Author: FIDUS Investment Management
Date: October 31, 2025
"""

from datetime import datetime
from typing import Dict, List, Optional
from pymongo.database import Database


class PnLCalculator:
    """
    Calculates TRUE Profit & Loss for MT5 trading accounts.
    
    This accounts for:
    - Profit withdrawals to separation accounts
    - Additional capital deposits during the period
    - Inter-account transfers
    - Management fee withdrawals
    """
    
    def __init__(self, db: Database):
        """Initialize the P&L Calculator with MongoDB database."""
        self.db = db
    
    def calculate_account_pnl(
        self, 
        account_number: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """
        Calculate TRUE P&L for a single MT5 account.
        
        Args:
            account_number: MT5 account number
            start_date: Start of calculation period (default: inception)
            end_date: End of calculation period (default: now)
            
        Returns:
            Dict with P&L breakdown including withdrawals and deposits
        """
        
        # Get account configuration - check for initial_allocation field
        config = self.db.mt5_account_config.find_one({"account": account_number})
        if not config:
            # Try to get from mt5_accounts collection
            mt5_acc = self.db.mt5_accounts.find_one({"account": account_number})
            if not mt5_acc:
                raise ValueError(f"Account {account_number} not found")
            
            # Use target_amount or balance as initial allocation if config doesn't exist
            initial_allocation = float(mt5_acc.get("target_amount") or mt5_acc.get("balance", 0))
        else:
            initial_allocation = float(config.get("initial_allocation") or config.get("target_amount", 0))
        
        # Get current equity
        current = self.db.mt5_accounts.find_one({"account": account_number})
        if not current:
            raise ValueError(f"Account {account_number} not found in mt5_accounts")
        
        current_equity = float(current.get("equity", 0))
        
        # Calculate withdrawals (type=2, profit<0) - EXCLUDING internal transfers AND P/L shares
        withdrawal_pipeline = [
            {
                "$match": {
                    "account_number": account_number,
                    "type": 2,
                    "profit": {"$lt": 0},
                    # EXCLUDE all types of internal operations
                    "comment": {
                        "$not": {
                            "$regex": "(Transfer|TRF|transfer|P/L Share) (from|to|From|To|:|#)"
                        }
                    }
                }
            },
            {
                "$group": {
                    "_id": "$account_number",
                    "total_withdrawals": {"$sum": {"$abs": "$profit"}},
                    "count": {"$sum": 1}
                }
            }
        ]
        
        if start_date or end_date:
            date_filter = {}
            if start_date:
                date_filter["$gte"] = start_date
            if end_date:
                date_filter["$lte"] = end_date
            withdrawal_pipeline[0]["$match"]["time"] = date_filter
        
        w_result = list(self.db.mt5_deals_history.aggregate(withdrawal_pipeline))
        total_withdrawals = float(w_result[0]["total_withdrawals"]) if w_result else 0.0
        withdrawal_count = int(w_result[0]["count"]) if w_result else 0
        
        # Calculate deposits (type=2, profit>0) - EXCLUDING internal transfers AND P/L shares
        deposit_pipeline = [
            {
                "$match": {
                    "account_number": account_number,
                    "type": 2,
                    "profit": {"$gt": 0},
                    # EXCLUDE all types of internal operations
                    "comment": {
                        "$not": {
                            "$regex": "(Transfer|TRF|transfer|P/L Share) (from|to|From|To|:|#)"
                        }
                    }
                }
            },
            {
                "$group": {
                    "_id": "$account_number",
                    "total_deposits": {"$sum": "$profit"},
                    "count": {"$sum": 1}
                }
            }
        ]
        
        if start_date or end_date:
            date_filter = {}
            if start_date:
                date_filter["$gte"] = start_date
            if end_date:
                date_filter["$lte"] = end_date
            deposit_pipeline[0]["$match"]["time"] = date_filter
        
        d_result = list(self.db.mt5_deals_history.aggregate(deposit_pipeline))
        total_deposits = float(d_result[0]["total_deposits"]) if d_result else 0.0
        deposit_count = int(d_result[0]["count"]) if d_result else 0
        
        # Calculate TRUE P&L
        total_capital_in = initial_allocation + total_deposits
        total_capital_out = current_equity + total_withdrawals
        true_pnl = total_capital_out - total_capital_in
        
        # Calculate return percentage
        return_percentage = (true_pnl / total_capital_in * 100) if total_capital_in > 0 else 0.0
        
        return {
            "account_number": account_number,
            "calculation_date": datetime.utcnow().isoformat(),
            
            # Capital In
            "initial_allocation": initial_allocation,
            "total_deposits": total_deposits,
            "deposit_count": deposit_count,
            "total_capital_in": total_capital_in,
            
            # Capital Out
            "current_equity": current_equity,
            "total_withdrawals": total_withdrawals,
            "withdrawal_count": withdrawal_count,
            "total_capital_out": total_capital_out,
            
            # P&L
            "true_pnl": true_pnl,
            "return_percentage": return_percentage,
            "is_profitable": true_pnl > 0,
            "status": "profit" if true_pnl > 0 else "loss" if true_pnl < 0 else "breakeven"
        }
    
    def calculate_fund_pnl(
        self, 
        fund_type: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """
        Calculate aggregate TRUE P&L for all accounts in a fund.
        
        Args:
            fund_type: CORE, BALANCE, DYNAMIC, SEPARATION, or UNLIMITED
            
        Returns:
            Fund-level P&L with account breakdown
        """
        
        # Get all accounts for this fund from mt5_accounts (since config might not have all)
        accounts = list(self.db.mt5_accounts.find({"fund_type": fund_type}))
        
        if not accounts:
            raise ValueError(f"No accounts found for fund type '{fund_type}'")
        
        # Calculate P&L for each account
        account_pnls = []
        for account in accounts:
            try:
                pnl = self.calculate_account_pnl(account["account"], start_date, end_date)
                account_pnls.append(pnl)
            except ValueError as e:
                print(f"Warning: Could not calculate P&L for account {account['account']}: {e}")
                continue
        
        if not account_pnls:
            raise ValueError(f"Could not calculate P&L for any accounts in {fund_type} fund")
        
        # Aggregate metrics
        total_capital_in = sum(a["total_capital_in"] for a in account_pnls)
        total_capital_out = sum(a["total_capital_out"] for a in account_pnls)
        fund_pnl = total_capital_out - total_capital_in
        fund_return = (fund_pnl / total_capital_in * 100) if total_capital_in > 0 else 0.0
        
        return {
            "fund_type": fund_type,
            "total_accounts": len(account_pnls),
            "calculation_date": datetime.utcnow().isoformat(),
            
            "total_initial_allocation": sum(a["initial_allocation"] for a in account_pnls),
            "total_deposits": sum(a["total_deposits"] for a in account_pnls),
            "total_capital_in": total_capital_in,
            
            "total_current_equity": sum(a["current_equity"] for a in account_pnls),
            "total_withdrawals": sum(a["total_withdrawals"] for a in account_pnls),
            "total_capital_out": total_capital_out,
            
            "fund_true_pnl": fund_pnl,
            "fund_return_percentage": fund_return,
            "is_profitable": fund_pnl > 0,
            
            "accounts": account_pnls
        }
    
    def calculate_manager_pnl(
        self, 
        manager_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """
        Calculate TRUE P&L for all accounts managed by a specific manager.
        
        Args:
            manager_id: Money manager identifier
            
        Returns:
            Manager-level P&L with account breakdown
        """
        
        # Get all accounts for this manager from mt5_accounts
        accounts = list(self.db.mt5_accounts.find({"manager_name": manager_id}))
        
        if not accounts:
            # Try alternative field names
            accounts = list(self.db.mt5_accounts.find({"money_manager": manager_id}))
        
        if not accounts:
            raise ValueError(f"No accounts found for manager '{manager_id}'")
        
        # Calculate P&L for each account
        account_pnls = []
        for account in accounts:
            try:
                pnl = self.calculate_account_pnl(account["account"], start_date, end_date)
                account_pnls.append(pnl)
            except ValueError as e:
                print(f"Warning: Could not calculate P&L for account {account['account']}: {e}")
                continue
        
        if not account_pnls:
            raise ValueError(f"Could not calculate P&L for any accounts managed by {manager_id}")
        
        # Aggregate metrics
        total_capital_in = sum(a["total_capital_in"] for a in account_pnls)
        total_capital_out = sum(a["total_capital_out"] for a in account_pnls)
        manager_pnl = total_capital_out - total_capital_in
        manager_return = (manager_pnl / total_capital_in * 100) if total_capital_in > 0 else 0.0
        
        return {
            "manager_id": manager_id,
            "total_accounts": len(account_pnls),
            "calculation_date": datetime.utcnow().isoformat(),
            
            "manager_true_pnl": manager_pnl,
            "manager_return_percentage": manager_return,
            "is_profitable": manager_pnl > 0,
            
            "total_capital_in": total_capital_in,
            "total_capital_out": total_capital_out,
            
            "accounts": account_pnls
        }
    
    def get_all_accounts_pnl(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict]:
        """Calculate TRUE P&L for ALL configured accounts."""
        
        accounts = list(self.db.mt5_accounts.find())
        
        account_pnls = []
        for account in accounts:
            try:
                pnl = self.calculate_account_pnl(account["account"], start_date, end_date)
                account_pnls.append(pnl)
            except ValueError as e:
                print(f"Warning: Could not calculate P&L for account {account['account']}: {e}")
                continue
        
        return account_pnls
