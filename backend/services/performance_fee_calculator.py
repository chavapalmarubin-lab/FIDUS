"""
Performance Fee Calculator Service

Calculates and tracks performance fees owed to money managers based on profitable trading.
Integrates with Cash Flow system to display fees as Fund Liabilities.

Business Rules:
- Performance fees apply ONLY to profits (positive TRUE P&L)
- NO fees charged on losses (negative TRUE P&L)
- Calculated daily based on current TRUE P&L
- Charged monthly - fees accumulate and are paid at month-end
- Simple monthly reset (no high water mark for MVP)
"""

from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)


class PerformanceFeeCalculator:
    """
    Service for calculating money manager performance fees.
    
    Integrates with:
    - money_managers collection: Manager configuration and fee rates
    - mt5_accounts collection: Source of TRUE P&L data
    - performance_fee_transactions collection: Historical fee records
    - daily_performance_fee_snapshots collection: Daily tracking
    """
    
    def __init__(self, db):
        self.db = db
        self.money_managers = db.money_managers
        self.mt5_accounts = db.mt5_accounts
        self.performance_fee_transactions = db.performance_fee_transactions
        self.daily_snapshots = db.daily_performance_fee_snapshots
    
    async def calculate_current_performance_fees(self) -> Dict:
        """
        Calculate current accrued performance fees for all active managers.
        
        Returns:
            Dict containing:
            - calculation_date: ISO timestamp
            - managers: List of manager fee calculations
            - totals: Aggregate statistics
        
        Example:
            {
                "calculation_date": "2025-10-13T15:00:00Z",
                "managers": [
                    {
                        "manager_id": "...",
                        "manager_name": "TradingHub Gold Provider",
                        "mt5_account_id": "886557",
                        "true_pnl": 2829.69,
                        "performance_fee_rate": 0.30,
                        "profit_for_fee": 2829.69,
                        "performance_fee_amount": 848.91,
                        "net_profit_after_fee": 1980.78,
                        "status": "PROFITABLE"
                    }
                ],
                "totals": {
                    "total_true_pnl": 2238.42,
                    "total_performance_fees": 902.23,
                    "net_profit_after_fees": 1336.19,
                    "managers_with_fees": 2
                }
            }
        """
        try:
            # Get all active managers
            managers = await self.money_managers.find({"status": "active"}).to_list(None)
            
            if not managers:
                logger.warning("No active managers found")
                return self._empty_result()
            
            results = []
            total_true_pnl = 0
            total_fees = 0
            total_net_profit = 0
            managers_with_fees = 0
            
            for manager in managers:
                # Get assigned MT5 account (first account in array)
                assigned_accounts = manager.get("assigned_accounts", [])
                if not assigned_accounts:
                    logger.warning(f"Manager {manager.get('manager_id')} has no assigned accounts")
                    continue
                
                mt5_account_id = str(assigned_accounts[0])
                
                # Get current TRUE P&L from MT5 account
                true_pnl = await self._get_true_pnl_for_account(mt5_account_id)
                
                # Calculate performance fee (only on profits)
                profit_for_fee = max(0, true_pnl)  # Only positive P&L
                fee_rate = manager.get("performance_fee_rate", 0)
                fee_amount = profit_for_fee * fee_rate
                net_profit = true_pnl - fee_amount
                
                if fee_amount > 0:
                    managers_with_fees += 1
                
                # Update manager document with current accruals
                await self.money_managers.update_one(
                    {"_id": manager["_id"]},
                    {
                        "$set": {
                            "current_month_profit": true_pnl,
                            "current_month_fee_accrued": fee_amount,
                            "updated_at": datetime.now(timezone.utc)
                        }
                    }
                )
                
                # Create daily snapshot
                await self._create_daily_snapshot(
                    manager=manager,
                    mt5_account_id=mt5_account_id,
                    true_pnl=true_pnl,
                    accrued_fee=fee_amount
                )
                
                results.append({
                    "manager_id": str(manager["_id"]),
                    "manager_name": manager.get("display_name") or manager.get("name", "Unknown"),
                    "mt5_account_id": mt5_account_id,
                    "true_pnl": round(true_pnl, 2),
                    "performance_fee_rate": fee_rate,
                    "profit_for_fee": round(profit_for_fee, 2),
                    "performance_fee_amount": round(fee_amount, 2),
                    "net_profit_after_fee": round(net_profit, 2),
                    "status": "PROFITABLE" if true_pnl > 0 else "LOSS"
                })
                
                total_true_pnl += true_pnl
                total_fees += fee_amount
                total_net_profit += net_profit
            
            logger.info(f"✅ Calculated performance fees: ${total_fees:.2f} from {len(results)} managers")
            
            return {
                "calculation_date": datetime.now(timezone.utc).isoformat(),
                "managers": results,
                "totals": {
                    "total_true_pnl": round(total_true_pnl, 2),
                    "total_performance_fees": round(total_fees, 2),
                    "net_profit_after_fees": round(total_net_profit, 2),
                    "managers_with_fees": managers_with_fees,
                    "fee_impact_percentage": round((total_fees / total_true_pnl * 100), 2) if total_true_pnl > 0 else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating performance fees: {str(e)}")
            raise
    
    async def _get_true_pnl_for_account(self, account_id: str) -> float:
        """
        Get current TRUE P&L for an MT5 account.
        Uses pre-calculated true_pnl from mt5_accounts collection.
        
        Args:
            account_id: MT5 account number as string
            
        Returns:
            TRUE P&L as float (0.0 if account not found)
        """
        try:
            # Convert to int for query
            account_num = int(account_id)
            
            account = await self.mt5_accounts.find_one({"account": account_num})
            
            if not account:
                logger.warning(f"MT5 account {account_id} not found")
                return 0.0
            
            # Use pre-calculated true_pnl field
            true_pnl = account.get("true_pnl", 0)
            return float(true_pnl)
            
        except ValueError:
            logger.error(f"Invalid account_id format: {account_id}")
            return 0.0
        except Exception as e:
            logger.error(f"Error getting TRUE P&L for account {account_id}: {str(e)}")
            return 0.0
    
    async def _create_daily_snapshot(
        self, 
        manager: Dict, 
        mt5_account_id: str,
        true_pnl: float, 
        accrued_fee: float
    ):
        """
        Create daily snapshot of performance fee accrual.
        Upserts to ensure only one snapshot per manager per day.
        
        Args:
            manager: Manager document
            mt5_account_id: MT5 account number
            true_pnl: Current TRUE P&L
            accrued_fee: Calculated performance fee
        """
        try:
            snapshot_date = datetime.now(timezone.utc).date().isoformat()
            
            # Get yesterday's snapshot for comparison
            yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).date().isoformat()
            yesterday_snapshot = await self.daily_snapshots.find_one({
                "snapshot_date": yesterday,
                "mt5_account_id": mt5_account_id
            })
            
            accrued_fee_yesterday = 0
            if yesterday_snapshot:
                accrued_fee_yesterday = yesterday_snapshot.get("accrued_fee_today", 0)
            
            snapshot = {
                "snapshot_date": snapshot_date,
                "manager_id": manager["_id"],
                "manager_name": manager.get("display_name") or manager.get("name", "Unknown"),
                "mt5_account_id": mt5_account_id,
                "true_pnl_mtd": true_pnl,
                "performance_fee_rate": manager.get("performance_fee_rate", 0),
                "accrued_fee_today": accrued_fee,
                "accrued_fee_yesterday": accrued_fee_yesterday,
                "fee_change": accrued_fee - accrued_fee_yesterday,
                "created_at": datetime.now(timezone.utc)
            }
            
            # Upsert (update if exists for today, insert if not)
            await self.daily_snapshots.update_one(
                {
                    "snapshot_date": snapshot_date,
                    "mt5_account_id": mt5_account_id
                },
                {"$set": snapshot},
                upsert=True
            )
            
        except Exception as e:
            logger.error(f"Error creating daily snapshot: {str(e)}")
            # Don't raise - snapshot failure shouldn't stop fee calculation
    
    async def get_performance_fees_for_cash_flow(self) -> Dict:
        """
        Get performance fee data for cash flow calculations.
        Used by /api/admin/cashflow/overview endpoint.
        
        Returns:
            Dict containing:
            - total_accrued: Total fees owed
            - breakdown: List of managers with fees > 0
            - managers_count: Number of managers with fees
        
        Example:
            {
                "total_accrued": 902.23,
                "breakdown": [
                    {
                        "manager": "TradingHub Gold Provider",
                        "fee": 848.91,
                        "status": "accrued"
                    }
                ],
                "managers_count": 2
            }
        """
        try:
            fees = await self.calculate_current_performance_fees()
            
            # Filter only managers with fees > 0
            breakdown = [
                {
                    "manager": m["manager_name"],
                    "mt5_account_id": m["mt5_account_id"],
                    "fee": m["performance_fee_amount"],
                    "status": "accrued"
                }
                for m in fees["managers"]
                if m["performance_fee_amount"] > 0
            ]
            
            return {
                "total_accrued": fees["totals"]["total_performance_fees"],
                "breakdown": breakdown,
                "managers_count": len(breakdown)
            }
            
        except Exception as e:
            logger.error(f"Error getting performance fees for cash flow: {str(e)}")
            return {
                "total_accrued": 0.0,
                "breakdown": [],
                "managers_count": 0
            }
    
    async def get_performance_fees_summary(
        self,
        month: Optional[int] = None,
        year: Optional[int] = None
    ) -> Dict:
        """
        Get performance fee summary for specified period.
        If month/year not provided, returns current month.
        
        Args:
            month: Month number (1-12), optional
            year: Year (e.g., 2025), optional
            
        Returns:
            Dict with period summary and manager breakdowns
        """
        try:
            if not month or not year:
                now = datetime.now(timezone.utc)
                month = now.month
                year = now.year
            
            # Get current fees
            current_fees = await self.calculate_current_performance_fees()
            
            # Get historical transactions for the period
            period_start = datetime(year, month, 1, tzinfo=timezone.utc)
            if month == 12:
                period_end = datetime(year + 1, 1, 1, tzinfo=timezone.utc) - timedelta(seconds=1)
            else:
                period_end = datetime(year, month + 1, 1, tzinfo=timezone.utc) - timedelta(seconds=1)
            
            paid_transactions = await self.performance_fee_transactions.find({
                "period_start": {"$gte": period_start, "$lte": period_end},
                "fee_status": "paid"
            }).to_list(None)
            
            total_paid = sum(t.get("performance_fee_calculated", 0) for t in paid_transactions)
            
            return {
                "period": f"{year}-{month:02d}",
                "period_start": period_start.isoformat(),
                "period_end": period_end.isoformat(),
                "accrued_fees": current_fees["totals"]["total_performance_fees"],
                "paid_fees": round(total_paid, 2),
                "pending_payment": round(
                    current_fees["totals"]["total_performance_fees"] - total_paid, 2
                ),
                "managers_breakdown": current_fees["managers"],
                "statistics": {
                    "total_managers": len(current_fees["managers"]),
                    "profitable_managers": current_fees["totals"]["managers_with_fees"],
                    "average_fee_rate": round(
                        sum(m["performance_fee_rate"] for m in current_fees["managers"]) / len(current_fees["managers"]),
                        4
                    ) if current_fees["managers"] else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting performance fees summary: {str(e)}")
            raise
    
    async def finalize_monthly_fees(
        self,
        year: int,
        month: int
    ) -> Dict:
        """
        Finalize performance fees for a completed month.
        Creates performance_fee_transactions for payment processing.
        
        Args:
            year: Year of the month to finalize
            month: Month number (1-12) to finalize
            
        Returns:
            Dict with finalization results and created transactions
        """
        try:
            period_start = datetime(year, month, 1, tzinfo=timezone.utc)
            if month == 12:
                period_end = datetime(year + 1, 1, 1, tzinfo=timezone.utc) - timedelta(seconds=1)
            else:
                period_end = datetime(year, month + 1, 1, tzinfo=timezone.utc) - timedelta(seconds=1)
            
            # Get current fees
            current_fees = await self.calculate_current_performance_fees()
            
            transactions = []
            total_fees = 0
            
            for manager_data in current_fees["managers"]:
                if manager_data["performance_fee_amount"] <= 0:
                    continue  # Skip if no fee owed
                
                # Find manager
                manager = await self.money_managers.find_one({
                    "assigned_accounts": int(manager_data["mt5_account_id"])
                })
                
                if not manager:
                    logger.warning(f"Manager not found for account {manager_data['mt5_account_id']}")
                    continue
                
                # Create transaction record
                transaction = {
                    "manager_id": manager["_id"],
                    "manager_name": manager.get("display_name") or manager.get("name", "Unknown"),
                    "mt5_account_id": manager_data["mt5_account_id"],
                    "period_start": period_start,
                    "period_end": period_end,
                    "period_type": "monthly",
                    "total_profit": manager_data["true_pnl"],
                    "performance_fee_rate": manager_data["performance_fee_rate"],
                    "profit_subject_to_fee": manager_data["profit_for_fee"],
                    "performance_fee_calculated": manager_data["performance_fee_amount"],
                    "fee_status": "accrued",
                    "verification_status": "pending",
                    "payment_status": "unpaid",
                    "calculated_at": datetime.now(timezone.utc),
                    "calculated_by": "system",
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                }
                
                result = await self.performance_fee_transactions.insert_one(transaction)
                transaction["_id"] = result.inserted_id
                transactions.append(transaction)
                
                total_fees += manager_data["performance_fee_amount"]
                
                # Update manager's YTD fees
                await self.money_managers.update_one(
                    {"_id": manager["_id"]},
                    {
                        "$inc": {"ytd_fees_accrued": manager_data["performance_fee_amount"]},
                        "$set": {
                            "last_fee_calculation_date": datetime.now(timezone.utc),
                            "current_month_profit": 0,  # Reset for new month
                            "current_month_fee_accrued": 0
                        }
                    }
                )
            
            logger.info(f"✅ Finalized {len(transactions)} fee transactions for {year}-{month:02d}, total: ${total_fees:.2f}")
            
            return {
                "period": f"{year}-{month:02d}",
                "period_start": period_start.isoformat(),
                "period_end": period_end.isoformat(),
                "transactions_created": len(transactions),
                "total_fees_accrued": round(total_fees, 2),
                "transactions": [
                    {
                        "transaction_id": str(t["_id"]),
                        "manager": t["manager_name"],
                        "mt5_account_id": t["mt5_account_id"],
                        "fee": t["performance_fee_calculated"]
                    }
                    for t in transactions
                ]
            }
            
        except Exception as e:
            logger.error(f"Error finalizing monthly fees: {str(e)}")
            raise
    
    def _empty_result(self) -> Dict:
        """Return empty result structure when no managers found"""
        return {
            "calculation_date": datetime.now(timezone.utc).isoformat(),
            "managers": [],
            "totals": {
                "total_true_pnl": 0.0,
                "total_performance_fees": 0.0,
                "net_profit_after_fees": 0.0,
                "managers_with_fees": 0,
                "fee_impact_percentage": 0.0
            }
        }
