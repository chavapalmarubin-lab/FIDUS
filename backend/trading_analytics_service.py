#!/usr/bin/env python3
"""
Trading Analytics Service for FIDUS Platform

This service implements end-of-day batch processing for MT5 trading analytics.
Phase 1A: Basic analytics with account 886557 (BALANCE Fund)
Phase 1B: Expand to all 4 MT5 accounts

Key Features:
- Daily sync job (runs at 11 PM UTC)
- Pre-calculated metrics stored in MongoDB
- Lightweight dashboard queries
- No real-time processing
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
import os
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import UpdateOne

from config.database import get_database
from mt5_bridge_client import MT5BridgeClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TradingAnalyticsService:
    """
    Service for managing trading analytics with end-of-day batch processing
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.mt5_client = MT5BridgeClient()
        
        # Phase 1B: All 4 MT5 accounts active
        self.mt5_accounts = [
            {"number": 886557, "name": "BALANCE Fund ($80K)", "fund_type": "BALANCE"},
            {"number": 886066, "name": "BALANCE Fund ($10K)", "fund_type": "BALANCE"},
            {"number": 886602, "name": "BALANCE Fund ($10K)", "fund_type": "BALANCE"},
            {"number": 885822, "name": "CORE Fund ($18K)", "fund_type": "CORE"}
        ]
    
    async def ensure_indexes(self):
        """
        Create database indexes for optimal query performance
        """
        try:
            # MT5 Trades Collection Indexes
            await self.db.mt5_trades.create_index([("account", 1), ("close_time", -1)])
            await self.db.mt5_trades.create_index([("ticket", 1), ("account", 1)], unique=True)
            await self.db.mt5_trades.create_index([("symbol", 1), ("close_time", -1)])
            await self.db.mt5_trades.create_index([("close_time", -1)])
            
            # Daily Performance Collection Indexes  
            await self.db.daily_performance.create_index([("date", -1), ("account", 1)], unique=True)
            await self.db.daily_performance.create_index([("account", 1), ("date", -1)])
            await self.db.daily_performance.create_index([("status", 1), ("date", -1)])
            
            # Period Performance Collection Indexes
            await self.db.period_performance.create_index([
                ("period_type", 1), ("period_start", -1), ("account", 1)
            ], unique=True)
            await self.db.period_performance.create_index([("account", 1), ("period_start", -1)])
            
            logger.info("✅ Trading analytics database indexes created successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to create indexes: {str(e)}")
            raise
    
    async def daily_sync_job(self, target_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Main daily sync job - runs at 11 PM UTC
        
        Args:
            target_date: Date to sync (defaults to yesterday)
            
        Returns:
            Dict with sync results and statistics
        """
        start_time = datetime.now(timezone.utc)
        
        if target_date is None:
            # Default to yesterday (after market close)
            target_date = (datetime.now(timezone.utc) - timedelta(days=1)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
        
        logger.info(f"🚀 Starting daily trading sync for {target_date.date()}")
        
        sync_results = {
            "sync_date": target_date.isoformat(),
            "started_at": start_time.isoformat(),
            "accounts_processed": 0,
            "total_trades_synced": 0,
            "daily_summaries_created": 0,
            "errors": [],
            "success": False
        }
        
        try:
            # Step 1: Ensure database indexes exist
            await self.ensure_indexes()
            
            # Step 2: Sync trades for each account
            for account in self.mt5_accounts:
                try:
                    account_trades = await self.sync_account_trades(
                        account["number"], 
                        target_date
                    )
                    
                    sync_results["total_trades_synced"] += len(account_trades)
                    sync_results["accounts_processed"] += 1
                    
                    logger.info(
                        f"✅ Account {account['number']}: {len(account_trades)} trades synced"
                    )
                    
                except Exception as e:
                    error_msg = f"Account {account['number']} sync failed: {str(e)}"
                    sync_results["errors"].append(error_msg)
                    logger.error(f"❌ {error_msg}")
                    continue
            
            # Step 3: Calculate daily performance summaries
            for account in self.mt5_accounts:
                try:
                    daily_stats = await self.calculate_daily_performance(
                        account["number"],
                        target_date
                    )
                    
                    if daily_stats:
                        await self.save_daily_performance(daily_stats)
                        sync_results["daily_summaries_created"] += 1
                        
                        logger.info(
                            f"✅ Daily summary for {account['number']}: "
                            f"{daily_stats.get('total_trades', 0)} trades, "
                            f"P&L: ${daily_stats.get('total_pnl', 0):.2f}"
                        )
                    
                except Exception as e:
                    error_msg = f"Daily calculation for account {account['number']} failed: {str(e)}"
                    sync_results["errors"].append(error_msg)
                    logger.error(f"❌ {error_msg}")
                    continue
            
            # Step 4: Update period summaries if needed
            await self.update_period_summaries(target_date)
            
            # Step 5: Mark sync as successful
            end_time = datetime.now(timezone.utc)
            sync_results["completed_at"] = end_time.isoformat()
            sync_results["duration_seconds"] = (end_time - start_time).total_seconds()
            sync_results["success"] = len(sync_results["errors"]) == 0
            
            # Log final results
            if sync_results["success"]:
                logger.info(
                    f"🎉 Daily sync completed successfully in {sync_results['duration_seconds']:.2f}s: "
                    f"{sync_results['total_trades_synced']} trades, "
                    f"{sync_results['daily_summaries_created']} summaries"
                )
            else:
                logger.warning(
                    f"⚠️ Daily sync completed with {len(sync_results['errors'])} errors"
                )
            
            return sync_results
            
        except Exception as e:
            error_msg = f"Daily sync job failed: {str(e)}"
            sync_results["errors"].append(error_msg)
            sync_results["success"] = False
            logger.error(f"❌ {error_msg}")
            raise
    
    async def sync_account_trades(self, account_number: int, target_date: datetime) -> List[Dict]:
        """
        Fetch and store trades for a specific account and date
        
        Args:
            account_number: MT5 account number
            target_date: Date to fetch trades for
            
        Returns:
            List of synced trades
        """
        try:
            # Phase 1B: Mock MT5 data for all 4 accounts
            # TODO: Replace with actual MT5 bridge call after testing
            
            # Simulate MT5 API call for real integration
            # trades = await self.mt5_client.get_closed_trades(
            #     account_number, 
            #     target_date, 
            #     target_date + timedelta(days=1)
            # )
            
            # Mock trades for Phase 1B testing (varies by account)
            trades = self.generate_mock_trades(account_number, target_date)
            
            if not trades:
                logger.info(f"No trades found for account {account_number} on {target_date.date()}")
                return []
            
            # Transform and store trades
            bulk_operations = []
            for trade in trades:
                trade_doc = self.transform_mt5_trade(trade, account_number)
                
                # Upsert operation to avoid duplicates
                bulk_operations.append(
                    UpdateOne(
                        filter={
                            "ticket": trade_doc["ticket"],
                            "account": trade_doc["account"]
                        },
                        update={"$set": trade_doc},
                        upsert=True
                    )
                )
            
            # Execute bulk write
            if bulk_operations:
                result = await self.db.mt5_trades.bulk_write(bulk_operations)
                logger.info(
                    f"Account {account_number}: {result.upserted_count} new trades, "
                    f"{result.modified_count} updated trades"
                )
            
            return trades
            
        except Exception as e:
            logger.error(f"Failed to sync trades for account {account_number}: {str(e)}")
            raise
    
    def generate_mock_trades(self, account_number: int, target_date: datetime) -> List[Dict]:
        """
        Generate mock trading data for Phase 1B testing (varies by account)
        
        Args:
            account_number: MT5 account number
            target_date: Date to generate trades for
            
        Returns:
            List of mock trades
        """
        import random
        
        # Account-specific trading patterns for Phase 1B
        account_profiles = {
            886557: {"activity": 0.8, "skill": 0.6, "volume_range": (0.5, 3.0), "symbols": ['EURUSD', 'GBPUSD', 'USDJPY']},
            886066: {"activity": 0.5, "skill": 0.4, "volume_range": (0.1, 1.0), "symbols": ['EURUSD', 'AUDUSD']},
            886602: {"activity": 0.6, "skill": 0.5, "volume_range": (0.2, 1.5), "symbols": ['GBPUSD', 'USDCHF']},
            885822: {"activity": 0.7, "skill": 0.7, "volume_range": (1.0, 5.0), "symbols": ['EURUSD', 'GBPUSD', 'USDJPY', 'GOLD']}
        }
        
        profile = account_profiles.get(account_number, account_profiles[886557])
        
        # Trading probability based on account activity level
        if random.random() > profile["activity"]:
            return []
        
        # Number of trades varies by account
        if account_number == 886557:  # BALANCE $80K - Most active
            num_trades = random.randint(2, 8)
        elif account_number in [886066, 886602]:  # BALANCE $10K - Moderate
            num_trades = random.randint(1, 4)
        elif account_number == 885822:  # CORE $18K - Strategic
            num_trades = random.randint(1, 5)
        else:
            num_trades = random.randint(1, 3)
        
        trades = []
        base_time = target_date.replace(hour=8, minute=0)  # Market open
        
        for i in range(num_trades):
            # Random trade timing during market hours
            open_time = base_time + timedelta(
                hours=random.randint(0, 10),
                minutes=random.randint(0, 59)
            )
            
            close_time = open_time + timedelta(
                minutes=random.randint(5, 300)  # 5 minutes to 5 hours
            )
            
            # Account-specific P&L simulation
            skill_factor = profile["skill"]
            base_range = 500
            
            if skill_factor > 0.6:  # Skilled accounts
                profit = round(random.uniform(-base_range * 0.6, base_range * 1.4), 2)
            elif skill_factor > 0.4:  # Average accounts  
                profit = round(random.uniform(-base_range * 0.8, base_range * 1.2), 2)
            else:  # Less skilled accounts
                profit = round(random.uniform(-base_range * 1.2, base_range * 0.8), 2)
            
            # Account size affects volume
            volume = round(random.uniform(*profile["volume_range"]), 2)
            
            trade = {
                "ticket": 123456000 + (account_number % 1000) * 1000 + i + int(target_date.timestamp() % 1000),
                "symbol": random.choice(profile["symbols"]),
                "type": random.choice([0, 1]),  # 0=BUY, 1=SELL
                "volume": volume,
                "price_open": round(random.uniform(1.0500, 1.0900), 5),
                "price_close": round(random.uniform(1.0500, 1.0900), 5),
                "time_open": int(open_time.timestamp()),
                "time_close": int(close_time.timestamp()),
                "profit": profit,
                "commission": round(random.uniform(-5, -1), 2),
                "swap": round(random.uniform(-2, 1), 2),
                "comment": f"Account {account_number} - Trade #{i+1}"
            }
            
            trades.append(trade)
        
        return trades
    
    def transform_mt5_trade(self, raw_trade: Dict, account_number: int) -> Dict:
        """
        Transform raw MT5 trade data to our schema
        
        Args:
            raw_trade: Raw trade data from MT5
            account_number: MT5 account number
            
        Returns:
            Transformed trade document
        """
        return {
            "ticket": int(raw_trade["ticket"]),
            "account": account_number,
            "symbol": raw_trade["symbol"],
            "type": "BUY" if raw_trade["type"] == 0 else "SELL",
            "volume": float(raw_trade["volume"]),
            "open_price": float(raw_trade["price_open"]),
            "close_price": float(raw_trade["price_close"]),
            "open_time": datetime.fromtimestamp(raw_trade["time_open"], timezone.utc),
            "close_time": datetime.fromtimestamp(raw_trade["time_close"], timezone.utc),
            "profit": float(raw_trade["profit"]),
            "commission": float(raw_trade["commission"]),
            "swap": float(raw_trade.get("swap", 0)),
            "comment": raw_trade.get("comment", ""),
            "created_at": datetime.now(timezone.utc)
        }
    
    async def calculate_daily_performance(
        self, 
        account_number: int, 
        target_date: datetime
    ) -> Optional[Dict]:
        """
        Calculate daily performance metrics for an account
        
        Args:
            account_number: MT5 account number
            target_date: Date to calculate performance for
            
        Returns:
            Daily performance summary or None if no trades
        """
        try:
            # Query trades for the target date
            start_date = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)
            
            trades_cursor = self.db.mt5_trades.find({
                "account": account_number,
                "close_time": {"$gte": start_date, "$lt": end_date}
            })
            
            trades = await trades_cursor.to_list(length=None)
            
            if not trades:
                # Return minimal record for no-trading days
                return {
                    "date": start_date,
                    "account": account_number,
                    "total_trades": 0,
                    "winning_trades": 0,
                    "losing_trades": 0,
                    "breakeven_trades": 0,
                    "total_pnl": 0.0,
                    "gross_profit": 0.0,
                    "gross_loss": 0.0,
                    "win_rate": 0.0,
                    "profit_factor": 0.0,
                    "largest_win": 0.0,
                    "largest_loss": 0.0,
                    "avg_win": 0.0,
                    "avg_loss": 0.0,
                    "instruments_traded": [],
                    "status": "no_trading",
                    "calculated_at": datetime.now(timezone.utc)
                }
            
            # Calculate metrics
            winning_trades = [t for t in trades if t["profit"] > 0]
            losing_trades = [t for t in trades if t["profit"] < 0]
            breakeven_trades = [t for t in trades if t["profit"] == 0]
            
            total_pnl = sum(t["profit"] for t in trades)
            gross_profit = sum(t["profit"] for t in winning_trades)
            gross_loss = sum(t["profit"] for t in losing_trades)
            
            win_rate = (len(winning_trades) / len(trades)) * 100 if trades else 0
            profit_factor = abs(gross_profit / gross_loss) if gross_loss != 0 else float('inf')
            
            largest_win = max((t["profit"] for t in winning_trades), default=0)
            largest_loss = min((t["profit"] for t in losing_trades), default=0)
            
            avg_win = gross_profit / len(winning_trades) if winning_trades else 0
            avg_loss = gross_loss / len(losing_trades) if losing_trades else 0
            
            instruments_traded = list(set(t["symbol"] for t in trades))
            
            # Determine status
            if total_pnl > 0:
                status = "profitable"
            elif total_pnl < 0:
                status = "loss"
            else:
                status = "breakeven"
            
            return {
                "date": start_date,
                "account": account_number,
                "total_trades": len(trades),
                "winning_trades": len(winning_trades),
                "losing_trades": len(losing_trades),
                "breakeven_trades": len(breakeven_trades),
                "total_pnl": round(total_pnl, 2),
                "gross_profit": round(gross_profit, 2),
                "gross_loss": round(gross_loss, 2),
                "win_rate": round(win_rate, 2),
                "profit_factor": round(profit_factor, 2) if profit_factor != float('inf') else 999.99,
                "largest_win": round(largest_win, 2),
                "largest_loss": round(largest_loss, 2),
                "avg_win": round(avg_win, 2),
                "avg_loss": round(avg_loss, 2),
                "instruments_traded": instruments_traded,
                "status": status,
                "calculated_at": datetime.now(timezone.utc)
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate daily performance for account {account_number}: {str(e)}")
            raise
    
    async def save_daily_performance(self, daily_stats: Dict) -> None:
        """
        Save daily performance summary to database
        
        Args:
            daily_stats: Daily performance metrics
        """
        try:
            await self.db.daily_performance.update_one(
                {
                    "account": daily_stats["account"],
                    "date": daily_stats["date"]
                },
                {"$set": daily_stats},
                upsert=True
            )
            
        except Exception as e:
            logger.error(f"Failed to save daily performance: {str(e)}")
            raise
    
    async def update_period_summaries(self, target_date: datetime) -> None:
        """
        Update weekly/monthly period summaries if needed
        
        Args:
            target_date: Date that was processed
        """
        try:
            # Check if we need to update weekly summary (end of week)
            if target_date.weekday() == 6:  # Sunday
                await self.calculate_weekly_summary(target_date)
            
            # Check if we need to update monthly summary (end of month)
            next_day = target_date + timedelta(days=1)
            if next_day.month != target_date.month:
                await self.calculate_monthly_summary(target_date)
            
        except Exception as e:
            logger.error(f"Failed to update period summaries: {str(e)}")
    
    async def calculate_weekly_summary(self, end_date: datetime) -> None:
        """Calculate and store weekly performance summary"""
        # TODO: Implement weekly aggregation
        pass
    
    async def calculate_monthly_summary(self, end_date: datetime) -> None:
        """Calculate and store monthly performance summary"""  
        # TODO: Implement monthly aggregation
        pass
    
    async def get_analytics_overview(
        self, 
        account_numbers: List[int], 
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get analytics overview for dashboard display
        
        Args:
            account_numbers: List of account numbers to include
            days: Number of days to analyze
            
        Returns:
            Analytics overview data
        """
        try:
            end_date = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            start_date = end_date - timedelta(days=days)
            
            # Query daily performance data
            query_filter = {
                "account": {"$in": account_numbers},
                "date": {"$gte": start_date, "$lt": end_date}
            }
            
            daily_data = await self.db.daily_performance.find(query_filter).to_list(length=None)
            
            if not daily_data:
                return self.get_empty_analytics_overview()
            
            # Aggregate metrics
            total_trades = sum(day["total_trades"] for day in daily_data)
            winning_trades = sum(day["winning_trades"] for day in daily_data)
            losing_trades = sum(day["losing_trades"] for day in daily_data)
            total_pnl = sum(day["total_pnl"] for day in daily_data)
            gross_profit = sum(day["gross_profit"] for day in daily_data)
            gross_loss = sum(day["gross_loss"] for day in daily_data)
            
            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
            profit_factor = abs(gross_profit / gross_loss) if gross_loss != 0 else 999.99
            avg_trade = total_pnl / total_trades if total_trades > 0 else 0
            
            # Find largest win/loss
            largest_win = max((day["largest_win"] for day in daily_data), default=0)
            largest_loss = min((day["largest_loss"] for day in daily_data), default=0)
            
            return {
                "overview": {
                    "total_pnl": round(total_pnl, 2),
                    "total_trades": total_trades,
                    "winning_trades": winning_trades,
                    "losing_trades": losing_trades,
                    "win_rate": round(win_rate, 2),
                    "profit_factor": round(profit_factor, 2),
                    "avg_trade": round(avg_trade, 2),
                    "gross_profit": round(gross_profit, 2),
                    "gross_loss": round(gross_loss, 2),
                    "largest_win": round(largest_win, 2),
                    "largest_loss": round(largest_loss, 2),
                    "avg_win": round(gross_profit / winning_trades, 2) if winning_trades > 0 else 0,
                    "avg_loss": round(gross_loss / losing_trades, 2) if losing_trades > 0 else 0,
                    "max_drawdown": 0,  # TODO: Calculate from daily equity curve
                    "recovery_factor": 0,  # TODO: Calculate
                    "sharpe_ratio": 0  # TODO: Calculate
                },
                "period_start": start_date.isoformat(),
                "period_end": end_date.isoformat(),
                "last_sync": max((day["calculated_at"] for day in daily_data), default=datetime.now(timezone.utc)).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get analytics overview: {str(e)}")
            return self.get_empty_analytics_overview()
    
    def get_empty_analytics_overview(self) -> Dict[str, Any]:
        """Return empty analytics overview for when no data exists"""
        return {
            "overview": {
                "total_pnl": 0.0,
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0.0,
                "profit_factor": 0.0,
                "avg_trade": 0.0,
                "gross_profit": 0.0,
                "gross_loss": 0.0,
                "largest_win": 0.0,
                "largest_loss": 0.0,
                "avg_win": 0.0,
                "avg_loss": 0.0,
                "max_drawdown": 0.0,
                "recovery_factor": 0.0,
                "sharpe_ratio": 0.0
            },
            "period_start": datetime.now(timezone.utc).isoformat(),
            "period_end": datetime.now(timezone.utc).isoformat(),
            "last_sync": datetime.now(timezone.utc).isoformat()
        }

# Scheduled task runner
async def run_daily_sync():
    """
    Entry point for scheduled daily sync job
    To be called by cron or task scheduler at 11 PM UTC
    """
    try:
        db = await get_database()
        service = TradingAnalyticsService(db)
        
        result = await service.daily_sync_job()
        
        if result["success"]:
            logger.info("🎉 Daily sync completed successfully")
        else:
            logger.error("❌ Daily sync completed with errors")
            
        return result
        
    except Exception as e:
        logger.error(f"❌ Daily sync job failed: {str(e)}")
        raise

if __name__ == "__main__":
    # For testing purposes
    asyncio.run(run_daily_sync())