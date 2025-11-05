#!/usr/bin/env python3
"""
Money Managers Service for FIDUS Platform

This service manages money manager profiles and performance tracking.
Tracks different trading strategies and managers across MT5 accounts.

Key Features:
- Manager profile management
- Performance aggregation across assigned accounts
- Strategy comparison and analysis
- Copy Trade vs MAM execution tracking
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
import os
from motor.motor_asyncio import AsyncIOMotorDatabase
import sys
sys.path.append('/app/backend')
from app.utils.field_transformers import transform_manager

from config.database import get_database

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MoneyManagersService:
    """
    Service for managing money manager profiles and performance tracking
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        
        # CORRECTED: 4 managers with 1:1 account mapping as specified by client
        self.initial_managers = [
            {
                "manager_id": "manager_cp_strategy",
                "name": "CP Strategy",
                "display_name": "CP Strategy Provider",
                "execution_type": "copy_trade",
                "broker": "MEXAtlantic",
                "profile_url": "https://ratings.mexatlantic.com/widgets/ratings/3157?widgetKey=social_platform_ratings",
                "assigned_accounts": [885822],  # CORRECTED: Only 885822 (CORE $18K)
                "strategy_name": "CP Strategy",
                "strategy_description": "Copy trading strategy from CP Strategy provider",
                "risk_profile": "medium",
                "start_date": datetime(2025, 10, 1, tzinfo=timezone.utc),
                "status": "active",
                "notes": "Copy trade strategy from CP provider",
                "contact_info": None
            },
            {
                "manager_id": "manager_tradinghub_gold",
                "name": "TradingHub Gold",
                "display_name": "TradingHub Gold Provider", 
                "execution_type": "copy_trade",
                "broker": "MEXAtlantic",
                "profile_url": None,  # TO BE ADDED LATER
                "assigned_accounts": [886557],  # CORRECTED: Only 886557 (BALANCE $80K)
                "strategy_name": "TradingHub Gold",
                "strategy_description": "Gold-focused trading strategy",
                "risk_profile": "medium",
                "start_date": datetime(2025, 10, 1, tzinfo=timezone.utc),
                "status": "active",
                "notes": "Profile link pending from client",
                "contact_info": None
            },
            {
                "manager_id": "manager_goldentrade",
                "name": "GoldenTrade",
                "display_name": "GoldenTrade Provider",
                "execution_type": "copy_trade",
                "broker": "MEXAtlantic",
                "profile_url": "https://ratings.mexatlantic.com/widgets/ratings/5843?widgetKey=social_platform_ratings",
                "assigned_accounts": [886066],  # CORRECTED: Only 886066 (BALANCE $10K)
                "strategy_name": "GoldenTrade",
                "strategy_description": "Copy trading strategy from GoldenTrade provider",
                "risk_profile": "high",
                "start_date": datetime(2025, 10, 1, tzinfo=timezone.utc),
                "status": "active",
                "notes": "Copy trade strategy from GoldenTrade provider",
                "contact_info": None
            },
            {
                "manager_id": "manager_uno14",
                "name": "UNO14",
                "display_name": "UNO14 MAM Manager",
                "execution_type": "mam",
                "broker": "MEXAtlantic", 
                "profile_url": None,  # TO BE ADDED LATER
                "assigned_accounts": [886602],  # CORRECTED: Only 886602 (BALANCE $10K)
                "strategy_name": "UNO14 MAM Strategy",
                "strategy_description": "Multi-Account Manager (MAM) execution strategy",
                "risk_profile": "medium",
                "start_date": datetime(2025, 10, 1, tzinfo=timezone.utc),
                "status": "active",
                "notes": "MAM execution type - profile link pending from client",
                "contact_info": None
            }
        ]
    
    async def ensure_indexes(self):
        """
        Create database indexes for optimal query performance
        """
        try:
            # Money Managers Collection Indexes
            await self.db.money_managers.create_index([("manager_id", 1)], unique=True)
            await self.db.money_managers.create_index([("status", 1)])
            await self.db.money_managers.create_index([("execution_type", 1)])
            await self.db.money_managers.create_index([("assigned_accounts", 1)])
            await self.db.money_managers.create_index([("start_date", -1)])
            
            logger.info("✅ Money managers database indexes created successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to create money managers indexes: {str(e)}")
            raise
    
    async def initialize_managers(self) -> Dict[str, Any]:
        """
        Initialize money managers collection with default manager configurations
        
        Returns:
            Dict with initialization results
        """
        try:
            await self.ensure_indexes()
            
            # Check if managers already exist
            existing_count = await self.db.money_managers.count_documents({})
            
            if existing_count > 0:
                logger.info(f"Money managers already initialized ({existing_count} managers exist)")
                return {
                    "success": True,
                    "action": "skip",
                    "message": f"Found {existing_count} existing managers",
                    "managers_created": 0
                }
            
            # Insert initial managers
            managers_to_insert = []
            for manager_config in self.initial_managers:
                manager_doc = {
                    **manager_config,
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                }
                managers_to_insert.append(manager_doc)
            
            if managers_to_insert:
                result = await self.db.money_managers.insert_many(managers_to_insert)
                created_count = len(result.inserted_ids)
                
                logger.info(f"✅ Created {created_count} money managers successfully")
                
                return {
                    "success": True,
                    "action": "created",
                    "message": f"Created {created_count} money managers",
                    "managers_created": created_count,
                    "manager_ids": [m["manager_id"] for m in managers_to_insert]
                }
            else:
                return {
                    "success": True,
                    "action": "skip",
                    "message": "No managers to create",
                    "managers_created": 0
                }
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize money managers: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "managers_created": 0
            }
    
    async def get_all_managers(self) -> List[Dict[str, Any]]:
        """
        Get all money managers with basic information and performance metrics
        
        Returns:
            List of manager documents with calculated performance
        """
        try:
            # FILTER: Get ONLY active managers (hides GoldenTrade and other inactive managers)
            managers_cursor = self.db.money_managers.find({"status": "active"})
            managers = await managers_cursor.to_list(length=None)
            
            # Calculate performance for each manager
            result_managers = []
            for manager in managers:
                try:
                    # Remove MongoDB ObjectId for JSON serialization
                    if "_id" in manager:
                        del manager["_id"]
                    
                    # Convert dates to ISO strings
                    if isinstance(manager.get("start_date"), datetime):
                        manager["start_date"] = manager["start_date"].isoformat()
                    if isinstance(manager.get("created_at"), datetime):
                        manager["created_at"] = manager["created_at"].isoformat()
                    if isinstance(manager.get("updated_at"), datetime):
                        manager["updated_at"] = manager["updated_at"].isoformat()
                    
                    # Calculate performance metrics (with error handling)
                    try:
                        performance = await self.calculate_manager_performance(manager["manager_id"])
                        manager["performance"] = performance
                    except Exception as perf_error:
                        logger.error(f"Performance calculation failed for {manager.get('name')}: {str(perf_error)}")
                        manager["performance"] = self.get_empty_performance()
                    
                    # Add account details (with error handling)
                    try:
                        account_details = await self.get_account_details(manager.get("assigned_accounts", []))
                        manager["account_details"] = account_details
                    except Exception as acc_error:
                        logger.error(f"Account details failed for {manager.get('name')}: {str(acc_error)}")
                        manager["account_details"] = []
                    
                    result_managers.append(manager)
                except Exception as mgr_error:
                    logger.error(f"Failed to process manager {manager.get('name', 'unknown')}: {str(mgr_error)}")
                    # Continue to next manager instead of failing completely
                    continue
            
            return result_managers
            
        except Exception as e:
            logger.error(f"Failed to get all managers: {str(e)}")
            return []
    
    async def get_manager_by_id(self, manager_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information for a specific money manager
        
        Args:
            manager_id: Manager identifier
            
        Returns:
            Manager document with detailed performance and trades
        """
        try:
            # Get manager document
            manager = await self.db.money_managers.find_one({"manager_id": manager_id})
            
            if not manager:
                return None
            
            # Remove MongoDB ObjectId
            if "_id" in manager:
                del manager["_id"]
            
            # Convert dates to ISO strings
            if isinstance(manager.get("start_date"), datetime):
                manager["start_date"] = manager["start_date"].isoformat()
            if isinstance(manager.get("created_at"), datetime):
                manager["created_at"] = manager["created_at"].isoformat()
            if isinstance(manager.get("updated_at"), datetime):
                manager["updated_at"] = manager["updated_at"].isoformat()
            
            # Calculate detailed performance metrics
            performance = await self.calculate_manager_performance(manager_id, detailed=True)
            manager["performance"] = performance
            
            # Get account details
            account_details = await self.get_account_details(manager["assigned_accounts"])
            manager["account_details"] = account_details
            
            # Get recent trades from all assigned accounts
            recent_trades = await self.get_manager_trades(manager["assigned_accounts"], limit=50)
            manager["recent_trades"] = recent_trades
            
            return manager
            
        except Exception as e:
            logger.error(f"Failed to get manager {manager_id}: {str(e)}")
            return None
    
    async def calculate_manager_performance(
        self, 
        manager_id: str, 
        detailed: bool = False
    ) -> Dict[str, Any]:
        """
        Calculate performance metrics for a money manager across all assigned accounts
        PHASE 3 FIX: Now uses TRUE P&L from corrected MT5 accounts data
        
        Args:
            manager_id: Manager identifier
            detailed: Whether to include detailed metrics
            
        Returns:
            Performance metrics dictionary with TRUE P&L
        """
        try:
            # Get manager document
            manager = await self.db.money_managers.find_one({"manager_id": manager_id})
            
            if not manager:
                return self.get_empty_performance()
            
            assigned_accounts = manager["assigned_accounts"]
            
            if not assigned_accounts:
                return self.get_empty_performance()
            
            # PHASE 3 FIX: Get corrected MT5 account data with TRUE P&L
            total_allocated = 0
            total_equity = 0
            total_withdrawals = 0
            total_true_pnl = 0
            
            for account_num in assigned_accounts:
                # Get corrected data from mt5_accounts collection
                account_data = await self.db.mt5_accounts.find_one({"account": account_num})
                
                if account_data:
                    balance = account_data.get("balance", 0)
                    equity = account_data.get("equity", 0)
                    
                    # CORRECT: Calculate net deposits from deal history
                    deals_cursor = self.db.mt5_deals_history.find({
                        "account_number": account_num,
                        "type": 2  # Balance operations only
                    })
                    deals = await deals_cursor.to_list(length=None)
                    
                    deposits_account = sum(d.get('profit', 0) for d in deals if d.get('profit', 0) > 0)
                    withdrawals_account = sum(d.get('profit', 0) for d in deals if d.get('profit', 0) < 0)
                    net_deposits_account = deposits_account + withdrawals_account
                    
                    # TRUE P&L for this account
                    pnl_account = balance - net_deposits_account
                    
                    total_allocated += net_deposits_account
                    total_equity += equity
                    total_true_pnl += pnl_account
                    
                    logger.info(f"Account {account_num}: NetDeposits=${net_deposits_account:,.2f}, Balance=${balance:,.2f}, TRUE P&L={pnl_account:,.2f}")
            
            # Get all trades from assigned accounts (last 30 days for trade statistics)
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=30)
            
            trades_cursor = self.db.mt5_trades.find({
                "account": {"$in": assigned_accounts},
                "close_time": {"$gte": start_date, "$lte": end_date}
            })
            trades = await trades_cursor.to_list(length=None)
            
            # Calculate trade statistics (win rate, profit factor, etc.)
            total_trades = len(trades)
            winning_trades = [t for t in trades if t["profit"] > 0]
            losing_trades = [t for t in trades if t["profit"] < 0]
            
            gross_profit = sum(t["profit"] for t in winning_trades)
            gross_loss = sum(t["profit"] for t in losing_trades)
            
            win_rate = (len(winning_trades) / total_trades * 100) if total_trades > 0 else 0
            profit_factor = abs(gross_profit / gross_loss) if gross_loss != 0 else 999.99
            avg_trade = sum(t["profit"] for t in trades) / total_trades if total_trades > 0 else 0
            
            logger.info(f"Manager {manager_id} Performance: "
                       f"TRUE P&L={total_true_pnl}, Allocated={total_allocated}, "
                       f"Equity={total_equity}, Withdrawals={total_withdrawals}")
            
            performance = {
                "total_allocated": round(total_allocated, 2),
                "current_equity": round(total_equity, 2),  # NEW: Current equity in accounts
                "total_withdrawals": round(total_withdrawals, 2),  # NEW: Profit withdrawals
                "total_pnl": round(total_true_pnl, 2),  # FIXED: Now uses TRUE P&L
                "total_trades": total_trades,
                "winning_trades": len(winning_trades),
                "losing_trades": len(losing_trades),
                "win_rate": round(win_rate, 2),
                "profit_factor": round(profit_factor, 2),
                "avg_trade": round(avg_trade, 2),
                "gross_profit": round(gross_profit, 2),
                "gross_loss": round(gross_loss, 2),
                "return_percentage": round((total_true_pnl / total_allocated * 100), 2) if total_allocated > 0 else 0
            }
            
            if detailed:
                # Add detailed metrics for detailed view
                largest_win = max((t["profit"] for t in winning_trades), default=0)
                largest_loss = min((t["profit"] for t in losing_trades), default=0)
                avg_win = gross_profit / len(winning_trades) if winning_trades else 0
                avg_loss = gross_loss / len(losing_trades) if losing_trades else 0
                
                performance.update({
                    "largest_win": round(largest_win, 2),
                    "largest_loss": round(largest_loss, 2),
                    "avg_win": round(avg_win, 2),
                    "avg_loss": round(avg_loss, 2),
                    "sharpe_ratio": 0,  # TODO: Calculate from daily returns
                    "max_drawdown": 0,  # TODO: Calculate from equity curve
                    "recovery_factor": 0  # TODO: Calculate
                })
            
            return performance
            
        except Exception as e:
            logger.error(f"Failed to calculate performance for manager {manager_id}: {str(e)}")
            return self.get_empty_performance()
    
    def get_empty_performance(self) -> Dict[str, Any]:
        """Return empty performance metrics"""
        return {
            "total_allocated": 0,
            "current_equity": 0,  # NEW
            "total_withdrawals": 0,  # NEW
            "total_pnl": 0,
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "win_rate": 0,
            "profit_factor": 0,
            "avg_trade": 0,
            "gross_profit": 0,
            "gross_loss": 0,
            "return_percentage": 0
        }
    
    async def get_account_details(self, account_numbers: List[int]) -> List[Dict[str, Any]]:
        """
        Get details for assigned accounts
        
        Args:
            account_numbers: List of MT5 account numbers
            
        Returns:
            List of account details with current status
        """
        account_details = []
        
        # Account allocation mapping
        account_info = {
            886557: {"name": "BALANCE Fund", "allocation": 80000},
            886066: {"name": "BALANCE Fund", "allocation": 10000},
            886602: {"name": "BALANCE Fund", "allocation": 10000},
            885822: {"name": "CORE Fund", "allocation": 18151.41}
        }
        
        for account_num in account_numbers:
            if account_num in account_info:
                # Get recent performance for this account
                recent_daily = await self.db.daily_performance.find_one(
                    {"account": account_num},
                    sort=[("date", -1)]
                )
                
                current_pnl = recent_daily["total_pnl"] if recent_daily else 0
                
                account_details.append({
                    "account": account_num,
                    "name": account_info[account_num]["name"],
                    "allocation": account_info[account_num]["allocation"],
                    "current_equity": account_info[account_num]["allocation"] + current_pnl,
                    "pnl": current_pnl,
                    "status": "active"
                })
        
        return account_details
    
    async def get_manager_trades(self, account_numbers: List[int], limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get recent trades from all assigned accounts for a manager
        
        Args:
            account_numbers: List of MT5 account numbers
            limit: Maximum number of trades to return
            
        Returns:
            List of recent trades
        """
        try:
            trades_cursor = self.db.mt5_trades.find({
                "account": {"$in": account_numbers}
            }).sort("close_time", -1).limit(limit)
            
            trades = await trades_cursor.to_list(length=None)
            
            # Convert dates to ISO strings and remove ObjectIds
            for trade in trades:
                if "_id" in trade:
                    del trade["_id"]
                if isinstance(trade.get("open_time"), datetime):
                    trade["open_time"] = trade["open_time"].isoformat()
                if isinstance(trade.get("close_time"), datetime):
                    trade["close_time"] = trade["close_time"].isoformat()
                if isinstance(trade.get("created_at"), datetime):
                    trade["created_at"] = trade["created_at"].isoformat()
            
            return trades
            
        except Exception as e:
            logger.error(f"Failed to get manager trades: {str(e)}")
            return []
    
    async def get_managers_comparison(self, manager_ids: List[str]) -> Dict[str, Any]:
        """
        Get comparison data for multiple managers
        
        Args:
            manager_ids: List of manager IDs to compare
            
        Returns:
            Comparison data structure
        """
        try:
            managers = []
            
            for manager_id in manager_ids:
                manager = await self.get_manager_by_id(manager_id)
                if manager:
                    managers.append(manager)
            
            # Calculate comparison metrics
            comparison_metrics = {
                "total_allocated": sum(m["performance"]["total_allocated"] for m in managers),
                "total_pnl": sum(m["performance"]["total_pnl"] for m in managers),
                "avg_win_rate": sum(m["performance"]["win_rate"] for m in managers) / len(managers) if managers else 0,
                "avg_profit_factor": sum(m["performance"]["profit_factor"] for m in managers) / len(managers) if managers else 0
            }
            
            return {
                "managers": managers,
                "comparison_metrics": comparison_metrics,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get managers comparison: {str(e)}")
            return {"managers": [], "comparison_metrics": {}}

# Initialization function
async def initialize_money_managers():
    """
    Initialize money managers service and setup initial data
    """
    try:
        db = await get_database()
        service = MoneyManagersService(db)
        
        result = await service.initialize_managers()
        
        if result["success"]:
            logger.info("🎉 Money managers service initialized successfully")
        else:
            logger.error("❌ Money managers service initialization failed")
            
        return result
        
    except Exception as e:
        logger.error(f"❌ Money managers initialization failed: {str(e)}")
        raise

if __name__ == "__main__":
    # For testing purposes
    asyncio.run(initialize_money_managers())