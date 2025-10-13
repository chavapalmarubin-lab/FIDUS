#!/usr/bin/env python3
"""
Broker Rebates Calculator Service
Calculates IB rebates based on MT5 trading volume
"""

from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class RebateCalculator:
    """
    Service for calculating broker rebates based on trading volume.
    
    FIDUS operates as an Introducing Broker (IB) and earns rebates
    from brokers based on client trading volume.
    """
    
    def __init__(self, db):
        self.db = db
        self.mt5_trades = db.mt5_trades
        self.mt5_accounts = db.mt5_accounts
        self.rebate_config = db.broker_rebate_config
        self.rebate_transactions = db.rebate_transactions
    
    async def calculate_rebates_for_period(
        self,
        start_date: datetime,
        end_date: datetime,
        account_ids: Optional[List[str]] = None,
        auto_approve: bool = False
    ) -> Dict:
        """
        Calculate rebates based on trading volume for specified period.
        
        Args:
            start_date: Start of period
            end_date: End of period
            account_ids: Specific accounts to process (None = all accounts)
            auto_approve: Automatically approve calculated rebates
        
        Returns:
            Dictionary with calculation results
        
        Process:
        1. Get all MT5 accounts (or specific ones) with rebate tracking enabled
        2. For each account, get broker rebate configuration
        3. Calculate volume traded in period from mt5_trades
        4. Calculate rebate = volume × rebate_per_lot
        5. Create rebate_transaction record
        """
        
        logger.info(f"🔄 Starting rebate calculation for period {start_date} to {end_date}")
        
        # 1. Get accounts to process
        query = {"track_rebates": True}
        if account_ids:
            query["account"] = {"$in": [int(aid) for aid in account_ids]}
        
        accounts_cursor = self.mt5_accounts.find(query)
        accounts = await accounts_cursor.to_list(length=None)
        
        if not accounts:
            logger.warning("⚠️ No accounts found for rebate calculation")
            return {
                "success": False,
                "message": "No accounts with rebate tracking enabled",
                "accounts_processed": 0
            }
        
        logger.info(f"📊 Processing {len(accounts)} accounts for rebate calculation")
        
        results = []
        total_volume = 0
        total_rebates = 0
        
        for account in accounts:
            account_id = account.get('account')
            broker_code = account.get('broker_code', 'MEX')
            
            # 2. Get broker rebate config
            broker_config_cursor = self.rebate_config.find({
                "broker_code": broker_code,
                "is_active": True
            }).sort("effective_date", -1).limit(1)
            
            broker_config_list = await broker_config_cursor.to_list(length=1)
            
            if not broker_config_list:
                logger.warning(f"⚠️ No rebate config found for broker {broker_code}")
                continue
            
            broker_config = broker_config_list[0]
            rebate_per_lot = broker_config.get('rebate_per_lot', 0)
            
            # 3. Calculate volume from mt5_trades
            # Query trades in the period
            trades_cursor = self.mt5_trades.find({
                "account": account_id,
                "close_time": {
                    "$gte": start_date,
                    "$lte": end_date
                }
            })
            
            trades = await trades_cursor.to_list(length=None)
            
            # Calculate total volume in lots
            # MT5 stores volume in different ways depending on the data source
            # Typically it's in hundreds (100 = 0.01 lot, 10000 = 1.00 lot)
            total_volume_raw = 0
            for trade in trades:
                volume = trade.get('volume', 0)
                # If volume is already in decimal format (e.g., 0.5 for 0.5 lots)
                if isinstance(volume, (int, float)):
                    total_volume_raw += volume
            
            # Convert to standard lots
            # If the volume looks like it's already in lots (< 100), use as-is
            # Otherwise divide by 10000 to get lots
            if total_volume_raw < 100:
                volume_standard_lots = total_volume_raw
            else:
                volume_standard_lots = total_volume_raw / 10000
            
            # 4. Calculate rebate
            rebate_earned = volume_standard_lots * rebate_per_lot
            
            if rebate_earned <= 0:
                logger.info(f"⚠️ Account {account_id}: No volume traded in period, skipping")
                continue
            
            # 5. Create transaction record
            transaction = {
                "account_id": str(account_id),
                "account_name": f"{account_id} - {account.get('name', 'Unknown')}",
                "broker_name": broker_config.get('broker_name'),
                "broker_code": broker_config.get('broker_code'),
                "volume_lots": round(volume_standard_lots, 2),
                "rebate_per_lot": rebate_per_lot,
                "rebate_earned": round(rebate_earned, 2),
                "currency": "USD",
                "period_start": start_date,
                "period_end": end_date,
                "calculation_date": datetime.now(timezone.utc),
                "status": "calculated",
                "verification_status": "approved" if auto_approve else "pending",
                "payment_status": "unpaid",
                "payment_date": None,
                "calculated_by": "system",
                "notes": f"Automated calculation from {len(trades)} trades",
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            
            # Check if transaction already exists for this period
            existing = await self.rebate_transactions.find_one({
                "account_id": str(account_id),
                "period_start": start_date,
                "period_end": end_date
            })
            
            if existing:
                # Update existing transaction
                await self.rebate_transactions.update_one(
                    {"_id": existing["_id"]},
                    {"$set": transaction}
                )
                logger.info(f"✅ Updated rebate for account {account_id}: ${rebate_earned:.2f}")
            else:
                # Insert new transaction
                await self.rebate_transactions.insert_one(transaction)
                logger.info(f"✅ Created rebate for account {account_id}: ${rebate_earned:.2f}")
            
            results.append({
                "account_id": str(account_id),
                "account_name": transaction["account_name"],
                "volume_lots": round(volume_standard_lots, 2),
                "rebate_earned": round(rebate_earned, 2),
                "status": transaction["status"],
                "verification_status": transaction["verification_status"]
            })
            
            total_volume += volume_standard_lots
            total_rebates += rebate_earned
        
        calculation_id = f"calc_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        
        logger.info(f"✅ Rebate calculation complete: {len(results)} accounts, ${total_rebates:.2f} total")
        
        return {
            "success": True,
            "calculation_id": calculation_id,
            "accounts_processed": len(results),
            "total_volume": round(total_volume, 2),
            "total_rebates": round(total_rebates, 2),
            "rebate_transactions": results,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    
    async def get_rebates_for_cash_flow(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """
        Get total verified/approved rebates for cash flow calculations.
        
        Args:
            start_date: Start of period
            end_date: End of period
        
        Returns:
            Dictionary with total rebates and breakdown
        """
        
        pipeline = [
            {
                "$match": {
                    "period_start": {"$gte": start_date},
                    "period_end": {"$lte": end_date},
                    "verification_status": {"$in": ["approved", "verified"]},
                    "status": {"$in": ["calculated", "verified", "paid"]}
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total_rebates": {"$sum": "$rebate_earned"},
                    "total_volume": {"$sum": "$volume_lots"},
                    "count": {"$sum": 1}
                }
            }
        ]
        
        result_cursor = self.rebate_transactions.aggregate(pipeline)
        result_list = await result_cursor.to_list(length=1)
        
        if result_list:
            result = result_list[0]
            return {
                "total_rebates": round(result.get("total_rebates", 0), 2),
                "total_volume": round(result.get("total_volume", 0), 2),
                "transaction_count": result.get("count", 0),
                "status": "approved"
            }
        else:
            return {
                "total_rebates": 0.0,
                "total_volume": 0.0,
                "transaction_count": 0,
                "status": "no_data"
            }
    
    async def get_rebate_summary(
        self,
        period: str = "monthly",
        year: int = None,
        month: int = None
    ) -> Dict:
        """
        Get rebate summary statistics for a period.
        
        Args:
            period: 'monthly', 'quarterly', 'yearly'
            year: Year (default: current year)
            month: Month for monthly period
        
        Returns:
            Dictionary with summary statistics
        """
        
        if year is None:
            year = datetime.now(timezone.utc).year
        
        if month is None:
            month = datetime.now(timezone.utc).month
        
        # Calculate date range based on period
        if period == "monthly":
            start_date = datetime(year, month, 1, tzinfo=timezone.utc)
            if month == 12:
                end_date = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
            else:
                end_date = datetime(year, month + 1, 1, tzinfo=timezone.utc)
        else:
            # Default to current month
            start_date = datetime(year, month, 1, tzinfo=timezone.utc)
            end_date = datetime.now(timezone.utc)
        
        # Aggregate rebates by status
        pipeline = [
            {
                "$match": {
                    "period_start": {"$gte": start_date},
                    "period_end": {"$lt": end_date}
                }
            },
            {
                "$facet": {
                    "by_status": [
                        {
                            "$group": {
                                "_id": "$verification_status",
                                "total": {"$sum": "$rebate_earned"},
                                "count": {"$sum": 1}
                            }
                        }
                    ],
                    "by_broker": [
                        {
                            "$group": {
                                "_id": "$broker_code",
                                "broker_name": {"$first": "$broker_name"},
                                "volume_lots": {"$sum": "$volume_lots"},
                                "rebates_earned": {"$sum": "$rebate_earned"}
                            }
                        }
                    ],
                    "totals": [
                        {
                            "$group": {
                                "_id": None,
                                "total_volume": {"$sum": "$volume_lots"},
                                "total_rebates": {"$sum": "$rebate_earned"},
                                "accounts_count": {"$addToSet": "$account_id"}
                            }
                        }
                    ]
                }
            }
        ]
        
        result_cursor = self.rebate_transactions.aggregate(pipeline)
        result_list = await result_cursor.to_list(length=1)
        
        if not result_list:
            return {
                "period": f"{year}-{month:02d}",
                "total_volume_lots": 0,
                "total_rebates_earned": 0,
                "total_rebates_paid": 0,
                "total_rebates_pending": 0,
                "accounts_with_rebates": 0
            }
        
        data = result_list[0]
        
        # Process by status
        by_status = {item["_id"]: item["total"] for item in data.get("by_status", [])}
        
        # Process totals
        totals = data.get("totals", [{}])[0]
        
        return {
            "period": f"{year}-{month:02d}",
            "total_volume_lots": round(totals.get("total_volume", 0), 2),
            "total_rebates_earned": round(totals.get("total_rebates", 0), 2),
            "total_rebates_paid": round(by_status.get("paid", 0), 2),
            "total_rebates_pending": round(by_status.get("pending", 0), 2),
            "accounts_with_rebates": len(totals.get("accounts_count", [])),
            "average_rebate_per_account": round(
                totals.get("total_rebates", 0) / max(len(totals.get("accounts_count", [])), 1),
                2
            ),
            "by_broker": data.get("by_broker", []),
            "by_status": by_status
        }
