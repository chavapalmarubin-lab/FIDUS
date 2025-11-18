"""
Investment Committee Allocation Recalculations Service

Handles all system-wide recalculations when MT5 account allocations are applied.
All functions support MongoDB transactions for atomic updates.
"""
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorClientSession

logger = logging.getLogger(__name__)


class AllocationRecalculationService:
    """Service for recalculating system data after allocation changes"""
    
    def __init__(self, db):
        self.db = db
    
    async def recalculate_cash_flow(self, session: Optional[AsyncIOMotorClientSession] = None) -> Dict[str, Any]:
        """
        Recalculate cash flow projections based on new account allocations
        
        Updates:
        - Monthly cash flow projections
        - Fund-level cash flows
        - Client-level cash flows
        - Manager-level cash flows
        """
        logger.info("🔄 Recalculating cash flow projections...")
        start_time = datetime.now(timezone.utc)
        
        try:
            # Get all active investments
            investments = await self.db.investments.find(
                {"status": "active"}
            ).to_list(length=None)
            
            updated_count = 0
            
            for investment in investments:
                # Calculate monthly cash flow based on fund type
                fund_code = investment.get("fund_code")
                principal = investment.get("principal_amount", 0)
                
                # Cash flow calculation logic
                monthly_rate = self._get_fund_monthly_rate(fund_code)
                monthly_interest = principal * (monthly_rate / 100)
                
                # Build 12-month projection
                cash_flow_projection = []
                for month in range(1, 13):
                    cash_flow_projection.append({
                        "month": month,
                        "interest_payment": monthly_interest,
                        "principal_payment": 0,  # Interest-only
                        "total_payment": monthly_interest,
                        "cumulative_interest": monthly_interest * month
                    })
                
                # Update investment
                await self.db.investments.update_one(
                    {"_id": investment["_id"]},
                    {
                        "$set": {
                            "cash_flow_projection": cash_flow_projection,
                            "monthly_interest": monthly_interest,
                            "annual_interest": monthly_interest * 12,
                            "recalculated_at": datetime.now(timezone.utc)
                        }
                    },
                    session=session
                )
                updated_count += 1
            
            duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            logger.info(f"✅ Cash flow recalculation complete: {updated_count} investments updated in {duration:.2f}s")
            
            return {
                "success": True,
                "investments_updated": updated_count,
                "duration_seconds": duration
            }
            
        except Exception as e:
            logger.error(f"❌ Cash flow recalculation failed: {e}")
            raise
    
    async def recalculate_commissions(self, session: Optional[AsyncIOMotorClientSession] = None) -> Dict[str, Any]:
        """
        Recalculate all commission structures
        
        Updates:
        - Referral agent commissions (10% of interest earned)
        - Manager performance fees (20% of profits)
        - Broker rebates (based on volume)
        """
        logger.info("🔄 Recalculating commissions...")
        start_time = datetime.now(timezone.utc)
        
        try:
            # Get all clients with active investments
            clients = await self.db.clients.find(
                {"has_active_investments": True}
            ).to_list(length=None)
            
            updated_count = 0
            total_referral_commissions = 0
            total_manager_fees = 0
            
            for client in clients:
                client_id = client["_id"]
                
                # Get client's investments
                investments = await self.db.investments.find(
                    {"client_id": str(client_id), "status": "active"}
                ).to_list(length=None)
                
                # Calculate total interest earned
                total_interest = sum(inv.get("annual_interest", 0) for inv in investments)
                
                # Referral commission: 10% of interest earned
                referral_commission = total_interest * 0.10
                total_referral_commissions += referral_commission
                
                # Manager performance fee: 20% of profits
                # Get client's MT5 accounts and calculate profit
                client_accounts = await self.db.mt5_accounts.find(
                    {"manager_assigned": {"$ne": None}}
                ).to_list(length=None)
                
                total_profit = sum(
                    acc.get("equity", 0) - acc.get("balance", 0) 
                    for acc in client_accounts 
                    if acc.get("equity", 0) > acc.get("balance", 0)
                )
                
                manager_fee = total_profit * 0.20
                total_manager_fees += manager_fee
                
                # Update client record
                await self.db.clients.update_one(
                    {"_id": client_id},
                    {
                        "$set": {
                            "referral_commission": referral_commission,
                            "manager_fee": manager_fee,
                            "total_fees": referral_commission + manager_fee,
                            "commissions_updated_at": datetime.now(timezone.utc)
                        }
                    },
                    session=session
                )
                updated_count += 1
            
            duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            logger.info(
                f"✅ Commission recalculation complete: {updated_count} clients updated in {duration:.2f}s"
            )
            
            return {
                "success": True,
                "clients_updated": updated_count,
                "total_referral_commissions": total_referral_commissions,
                "total_manager_fees": total_manager_fees,
                "duration_seconds": duration
            }
            
        except Exception as e:
            logger.error(f"❌ Commission recalculation failed: {e}")
            raise
    
    async def update_performance_metrics(self, session: Optional[AsyncIOMotorClientSession] = None) -> Dict[str, Any]:
        """
        Update all performance metrics
        
        Updates:
        - Manager performance (balance, equity, profit, ROI)
        - Fund performance
        - Account-level ROI
        - System-wide metrics
        """
        logger.info("🔄 Updating performance metrics...")
        start_time = datetime.now(timezone.utc)
        
        try:
            # Get all MT5 accounts with allocations
            accounts = await self.db.mt5_accounts.find(
                {"status": "assigned"}
            ).to_list(length=None)
            
            # Group by manager
            manager_stats = {}
            for account in accounts:
                manager = account.get("manager_assigned")
                if not manager:
                    continue
                
                if manager not in manager_stats:
                    manager_stats[manager] = {
                        "accounts": [],
                        "total_balance": 0,
                        "total_equity": 0,
                        "total_profit": 0,
                        "account_count": 0
                    }
                
                balance = account.get("balance", 0)
                equity = account.get("equity", 0)
                profit = equity - balance
                
                manager_stats[manager]["accounts"].append(account["account"])
                manager_stats[manager]["total_balance"] += balance
                manager_stats[manager]["total_equity"] += equity
                manager_stats[manager]["total_profit"] += profit
                manager_stats[manager]["account_count"] += 1
            
            # Update each manager's record
            managers_updated = 0
            for manager_name, stats in manager_stats.items():
                roi = (
                    (stats["total_profit"] / stats["total_balance"] * 100)
                    if stats["total_balance"] > 0 else 0
                )
                
                await self.db.money_managers.update_one(
                    {"name": manager_name},
                    {
                        "$set": {
                            "total_balance": stats["total_balance"],
                            "total_equity": stats["total_equity"],
                            "total_profit": stats["total_profit"],
                            "roi_percent": roi,
                            "account_count": stats["account_count"],
                            "assigned_accounts": stats["accounts"],
                            "updated_at": datetime.now(timezone.utc)
                        }
                    },
                    upsert=False,
                    session=session
                )
                managers_updated += 1
            
            duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            logger.info(
                f"✅ Performance metrics update complete: {managers_updated} managers updated in {duration:.2f}s"
            )
            
            return {
                "success": True,
                "managers_updated": managers_updated,
                "accounts_processed": len(accounts),
                "duration_seconds": duration
            }
            
        except Exception as e:
            logger.error(f"❌ Performance metrics update failed: {e}")
            raise
    
    async def recalculate_pl(self, session: Optional[AsyncIOMotorClientSession] = None) -> Dict[str, Any]:
        """
        Recalculate profit & loss for all entities
        
        Updates:
        - Account-level P&L
        - Fund-level P&L
        - Manager-level P&L
        - Client-level P&L
        """
        logger.info("🔄 Recalculating P&L...")
        start_time = datetime.now(timezone.utc)
        
        try:
            # Get all MT5 accounts
            accounts = await self.db.mt5_accounts.find({}).to_list(length=None)
            
            updated_count = 0
            total_pl = 0
            
            for account in accounts:
                # Calculate P&L
                balance = account.get("balance", 0)
                equity = account.get("equity", 0)
                pl = equity - balance
                
                # Calculate P&L percentage
                pl_percent = (pl / balance * 100) if balance > 0 else 0
                
                # Update account
                await self.db.mt5_accounts.update_one(
                    {"account": account["account"]},
                    {
                        "$set": {
                            "profit_loss": pl,
                            "profit_loss_percent": pl_percent,
                            "is_profitable": pl > 0,
                            "pl_updated_at": datetime.now(timezone.utc)
                        }
                    },
                    session=session
                )
                updated_count += 1
                total_pl += pl
            
            # Update system-wide P&L summary
            await self.db.system_metrics.update_one(
                {"metric_type": "total_pl"},
                {
                    "$set": {
                        "total_profit_loss": total_pl,
                        "accounts_count": updated_count,
                        "profitable_accounts": len([a for a in accounts if (a.get("equity", 0) - a.get("balance", 0)) > 0]),
                        "updated_at": datetime.now(timezone.utc)
                    }
                },
                upsert=True,
                session=session
            )
            
            duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            logger.info(
                f"✅ P&L recalculation complete: {updated_count} accounts updated in {duration:.2f}s"
            )
            
            return {
                "success": True,
                "accounts_updated": updated_count,
                "total_pl": total_pl,
                "duration_seconds": duration
            }
            
        except Exception as e:
            logger.error(f"❌ P&L recalculation failed: {e}")
            raise
    
    async def update_manager_allocations(self, session: Optional[AsyncIOMotorClientSession] = None) -> Dict[str, Any]:
        """
        Update manager allocation summaries
        
        Updates:
        - Allocated capital per manager
        - Account assignments per manager
        - Account count per manager
        """
        logger.info("🔄 Updating manager allocations...")
        start_time = datetime.now(timezone.utc)
        
        try:
            # Get all managers
            managers = await self.db.money_managers.find({}).to_list(length=None)
            
            managers_updated = 0
            
            for manager in managers:
                manager_name = manager.get("name") or manager.get("manager_name")
                
                # Get all accounts for this manager
                accounts = await self.db.mt5_accounts.find(
                    {"manager_assigned": manager_name, "status": "assigned"}
                ).to_list(length=None)
                
                # Calculate totals
                total_capital = sum(acc.get("balance", 0) for acc in accounts)
                account_numbers = [acc["account"] for acc in accounts]
                
                # Update manager record
                await self.db.money_managers.update_one(
                    {"_id": manager["_id"]},
                    {
                        "$set": {
                            "allocated_capital": total_capital,
                            "assigned_accounts": account_numbers,
                            "account_count": len(accounts),
                            "allocation_updated_at": datetime.now(timezone.utc)
                        }
                    },
                    session=session
                )
                managers_updated += 1
            
            duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            logger.info(
                f"✅ Manager allocations update complete: {managers_updated} managers updated in {duration:.2f}s"
            )
            
            return {
                "success": True,
                "managers_updated": managers_updated,
                "duration_seconds": duration
            }
            
        except Exception as e:
            logger.error(f"❌ Manager allocations update failed: {e}")
            raise
    
    async def update_fund_distributions(self, session: Optional[AsyncIOMotorClientSession] = None) -> Dict[str, Any]:
        """
        Update fund distribution summaries
        
        Updates:
        - Allocated capital per fund
        - Account assignments per fund
        - Account count per fund
        - Fund allocation percentages
        """
        logger.info("🔄 Updating fund distributions...")
        start_time = datetime.now(timezone.utc)
        
        try:
            # Get accounts grouped by fund
            pipeline = [
                {"$match": {"status": "assigned"}},
                {"$group": {
                    "_id": "$fund_type",
                    "total_capital": {"$sum": "$balance"},
                    "account_count": {"$sum": 1},
                    "accounts": {"$push": "$account"}
                }}
            ]
            
            fund_distributions = await self.db.mt5_accounts.aggregate(pipeline).to_list(length=None)
            
            # Calculate total capital for percentages
            total_capital = sum(dist["total_capital"] for dist in fund_distributions)
            
            # Update fund records
            funds_updated = 0
            for dist in fund_distributions:
                fund_code = dist["_id"]
                if not fund_code:
                    continue
                
                allocation_percent = (
                    (dist["total_capital"] / total_capital * 100)
                    if total_capital > 0 else 0
                )
                
                await self.db.fund_allocation_state.update_one(
                    {"fund_code": fund_code},
                    {
                        "$set": {
                            "allocated_capital": dist["total_capital"],
                            "assigned_accounts": dist["accounts"],
                            "account_count": dist["account_count"],
                            "allocation_percent": allocation_percent,
                            "updated_at": datetime.now(timezone.utc)
                        }
                    },
                    upsert=True,
                    session=session
                )
                funds_updated += 1
            
            duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            logger.info(
                f"✅ Fund distributions update complete: {funds_updated} funds updated in {duration:.2f}s"
            )
            
            return {
                "success": True,
                "funds_updated": funds_updated,
                "total_capital": total_capital,
                "duration_seconds": duration
            }
            
        except Exception as e:
            logger.error(f"❌ Fund distributions update failed: {e}")
            raise
    
    def _get_fund_monthly_rate(self, fund_code: str) -> float:
        """Get monthly interest rate for a fund"""
        rates = {
            "FIDUS CORE": 15.0 / 12,      # 15% annual = 1.25% monthly
            "FIDUS BALANCE": 30.0 / 12,   # 30% annual = 2.5% monthly
            "FIDUS DYNAMIC": 50.0 / 12,   # 50% annual = 4.17% monthly
            "SEPARATION INTEREST": 0.0,    # No interest
            "REBATES ACCOUNT": 0.0         # No interest
        }
        return rates.get(fund_code, 0.0)
    
    async def run_all_recalculations(
        self, 
        session: Optional[AsyncIOMotorClientSession] = None,
        progress_callback = None
    ) -> Dict[str, Any]:
        """
        Run all recalculation functions in sequence
        
        Args:
            session: MongoDB session for transaction support
            progress_callback: Optional function to call with progress updates
        
        Returns:
            Dict with results from all recalculations
        """
        logger.info("🚀 Starting comprehensive recalculation...")
        overall_start = datetime.now(timezone.utc)
        
        results = {
            "success": True,
            "recalculations": {},
            "errors": []
        }
        
        recalc_functions = [
            ("cash_flow", self.recalculate_cash_flow),
            ("commissions", self.recalculate_commissions),
            ("performance_metrics", self.update_performance_metrics),
            ("pl", self.recalculate_pl),
            ("manager_allocations", self.update_manager_allocations),
            ("fund_distributions", self.update_fund_distributions)
        ]
        
        for idx, (name, func) in enumerate(recalc_functions):
            try:
                if progress_callback:
                    progress_callback(name, (idx + 1) / len(recalc_functions) * 100)
                
                result = await func(session=session)
                results["recalculations"][name] = result
                
            except Exception as e:
                logger.error(f"❌ {name} recalculation failed: {e}")
                results["success"] = False
                results["errors"].append({
                    "recalculation": name,
                    "error": str(e)
                })
                raise  # Re-raise to trigger transaction rollback
        
        overall_duration = (datetime.now(timezone.utc) - overall_start).total_seconds()
        results["total_duration_seconds"] = overall_duration
        
        logger.info(f"🎉 All recalculations complete in {overall_duration:.2f}s")
        
        return results
