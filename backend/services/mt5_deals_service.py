"""
MT5 Deals Service
Handles deal history queries, analytics, rebate calculations, and manager performance

Phase 4A: Deal History Collection
"""

from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class MT5DealsService:
    def __init__(self, db):
        self.db = db
    
    async def get_deals(
        self,
        account_number: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        symbol: Optional[str] = None,
        deal_type: Optional[int] = None,
        limit: int = 1000
    ) -> List[Dict]:
        """
        Get deal history with optional filters
        
        Args:
            account_number: Filter by MT5 account
            start_date: Filter deals from this date
            end_date: Filter deals until this date
            symbol: Filter by trading symbol (e.g., 'EURUSD')
            deal_type: Filter by type (0=buy, 1=sell, 2=balance operation)
            limit: Maximum number of deals to return
        
        Returns:
            List of deal documents
        """
        try:
            # Build query filter
            query = {}
            
            if account_number:
                query["account_number"] = account_number
            
            if start_date:
                query.setdefault("time", {})["$gte"] = start_date
            
            if end_date:
                query.setdefault("time", {})["$lte"] = end_date
            
            if symbol:
                query["symbol"] = symbol
            
            if deal_type is not None:
                query["type"] = deal_type
            
            # Query deals
            cursor = self.db.mt5_deals_history.find(query).sort("time", -1).limit(limit)
            deals = await cursor.to_list(length=limit)
            
            # Convert ObjectId to string for JSON serialization
            for deal in deals:
                if "_id" in deal:
                    deal["_id"] = str(deal["_id"])
                # Convert datetime to ISO string
                if "time" in deal:
                    deal["time"] = deal["time"].isoformat()
                if "synced_at" in deal:
                    deal["synced_at"] = deal["synced_at"].isoformat()
            
            logger.info(f"Retrieved {len(deals)} deals (filters: account={account_number}, symbol={symbol}, type={deal_type})")
            return deals
            
        except Exception as e:
            logger.error(f"Error retrieving deals: {e}")
            raise
    
    async def get_deals_summary(
        self,
        account_number: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """
        Get aggregated deal statistics
        
        Returns:
            {
                "total_deals": 1234,
                "total_volume": 156.5,  # Total lots traded
                "total_profit": 5432.10,
                "total_commission": -234.50,
                "buy_deals": 567,
                "sell_deals": 645,
                "balance_operations": 22,
                "symbols_traded": ["EURUSD", "GBPUSD", ...],
                "date_range": {"start": "2024-10-15", "end": "2025-01-15"}
            }
        """
        try:
            # Build query filter
            query = {}
            
            if account_number:
                query["account_number"] = account_number
            
            if start_date:
                query.setdefault("time", {})["$gte"] = start_date
            
            if end_date:
                query.setdefault("time", {})["$lte"] = end_date
            
            # Aggregation pipeline
            pipeline = [
                {"$match": query},
                {
                    "$group": {
                        "_id": None,
                        "total_deals": {"$sum": 1},
                        "total_volume": {"$sum": "$volume"},
                        "total_profit": {"$sum": "$profit"},
                        "total_commission": {"$sum": "$commission"},
                        "total_swap": {"$sum": "$swap"},
                        "buy_deals": {
                            "$sum": {"$cond": [{"$eq": ["$type", 0]}, 1, 0]}
                        },
                        "sell_deals": {
                            "$sum": {"$cond": [{"$eq": ["$type", 1]}, 1, 0]}
                        },
                        "balance_operations": {
                            "$sum": {"$cond": [{"$eq": ["$type", 2]}, 1, 0]}
                        },
                        "symbols_traded": {"$addToSet": "$symbol"},
                        "earliest_deal": {"$min": "$time"},
                        "latest_deal": {"$max": "$time"}
                    }
                }
            ]
            
            result = await self.db.mt5_deals_history.aggregate(pipeline).to_list(length=1)
            
            if not result:
                return {
                    "total_deals": 0,
                    "total_volume": 0,
                    "total_profit": 0,
                    "total_commission": 0,
                    "total_swap": 0,
                    "buy_deals": 0,
                    "sell_deals": 0,
                    "balance_operations": 0,
                    "symbols_traded": [],
                    "date_range": None
                }
            
            summary = result[0]
            summary.pop("_id", None)
            
            # Convert datetime to ISO string
            if "earliest_deal" in summary and summary["earliest_deal"]:
                summary["earliest_deal"] = summary["earliest_deal"].isoformat()
            if "latest_deal" in summary and summary["latest_deal"]:
                summary["latest_deal"] = summary["latest_deal"].isoformat()
            
            # Add date range info
            summary["date_range"] = {
                "start": summary.get("earliest_deal"),
                "end": summary.get("latest_deal")
            }
            
            logger.info(f"Generated deals summary: {summary['total_deals']} deals, {summary['total_volume']:.2f} lots")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating deals summary: {e}")
            raise
    
    async def calculate_rebates(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        account_number: Optional[int] = None,
        rebate_per_lot: float = 5.05
    ) -> Dict:
        """
        Calculate broker rebates based on trading volume
        
        Formula: total_volume (lots) × rebate_per_lot ($5.05)
        
        Returns:
            {
                "total_volume": 156.5,
                "rebate_per_lot": 5.05,
                "total_rebates": 790.825,
                "by_account": [
                    {"account": 886557, "volume": 50.5, "rebates": 255.025},
                    ...
                ],
                "by_symbol": [
                    {"symbol": "EURUSD", "volume": 80.0, "rebates": 404.00},
                    ...
                ],
                "date_range": {"start": "2024-10-15", "end": "2025-01-15"}
            }
        """
        try:
            # Build query filter (only trading deals, not balance operations)
            query = {"type": {"$in": [0, 1]}}  # 0=buy, 1=sell (exclude 2=balance)
            
            if account_number:
                query["account_number"] = account_number
            
            if start_date:
                query.setdefault("time", {})["$gte"] = start_date
            
            if end_date:
                query.setdefault("time", {})["$lte"] = end_date
            
            # Total volume and rebates
            total_pipeline = [
                {"$match": query},
                {
                    "$group": {
                        "_id": None,
                        "total_volume": {"$sum": "$volume"},
                        "total_commission": {"$sum": "$commission"}
                    }
                }
            ]
            
            total_result = await self.db.mt5_deals_history.aggregate(total_pipeline).to_list(length=1)
            total_volume = total_result[0]["total_volume"] if total_result else 0
            total_commission = total_result[0]["total_commission"] if total_result else 0
            total_rebates = total_volume * rebate_per_lot
            
            # Rebates by account
            by_account_pipeline = [
                {"$match": query},
                {
                    "$group": {
                        "_id": "$account_number",
                        "account_name": {"$first": "$account_name"},
                        "fund_type": {"$first": "$fund_type"},
                        "volume": {"$sum": "$volume"},
                        "commission": {"$sum": "$commission"}
                    }
                },
                {"$sort": {"volume": -1}}
            ]
            
            by_account = await self.db.mt5_deals_history.aggregate(by_account_pipeline).to_list(length=None)
            
            for item in by_account:
                item["account"] = item.pop("_id")
                item["rebates"] = item["volume"] * rebate_per_lot
            
            # Rebates by symbol
            by_symbol_pipeline = [
                {"$match": query},
                {
                    "$group": {
                        "_id": "$symbol",
                        "volume": {"$sum": "$volume"},
                        "deals": {"$sum": 1}
                    }
                },
                {"$sort": {"volume": -1}}
            ]
            
            by_symbol = await self.db.mt5_deals_history.aggregate(by_symbol_pipeline).to_list(length=None)
            
            for item in by_symbol:
                item["symbol"] = item.pop("_id")
                item["rebates"] = item["volume"] * rebate_per_lot
            
            result = {
                "total_volume": round(total_volume, 2),
                "total_commission": round(total_commission, 2),
                "rebate_per_lot": rebate_per_lot,
                "total_rebates": round(total_rebates, 2),
                "by_account": by_account,
                "by_symbol": by_symbol[:10],  # Top 10 symbols
                "date_range": {
                    "start": start_date.isoformat() if start_date else None,
                    "end": end_date.isoformat() if end_date else None
                }
            }
            
            logger.info(f"Calculated rebates: {total_volume:.2f} lots = ${total_rebates:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Error calculating rebates: {e}")
            raise
    
    async def get_manager_performance(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Get performance attribution by money manager (using magic number)
        
        Returns:
            [
                {
                    "magic": 100234,
                    "manager_name": "TradingHub Gold",
                    "total_deals": 234,
                    "total_volume": 45.5,
                    "total_profit": 2345.67,
                    "win_deals": 156,
                    "loss_deals": 78,
                    "win_rate": 66.67,
                    "avg_profit_per_deal": 10.02
                },
                ...
            ]
        """
        try:
            # Build query filter (only trading deals)
            query = {"type": {"$in": [0, 1]}}  # 0=buy, 1=sell
            
            if start_date:
                query.setdefault("time", {})["$gte"] = start_date
            
            if end_date:
                query.setdefault("time", {})["$lte"] = end_date
            
            # Aggregation by magic number
            pipeline = [
                {"$match": query},
                {
                    "$group": {
                        "_id": "$magic",
                        "total_deals": {"$sum": 1},
                        "total_volume": {"$sum": "$volume"},
                        "total_profit": {"$sum": "$profit"},
                        "total_commission": {"$sum": "$commission"},
                        "win_deals": {
                            "$sum": {"$cond": [{"$gt": ["$profit", 0]}, 1, 0]}
                        },
                        "loss_deals": {
                            "$sum": {"$cond": [{"$lt": ["$profit", 0]}, 1, 0]}
                        },
                        "accounts_used": {"$addToSet": "$account_number"}
                    }
                },
                {"$sort": {"total_profit": -1}}
            ]
            
            results = await self.db.mt5_deals_history.aggregate(pipeline).to_list(length=None)
            
            # Calculate derived metrics and add manager names
            manager_map = {
                0: "Manual Trading",
                100234: "TradingHub Gold",
                100235: "GoldenTrade",
                100236: "UNO14 MAM",
                100237: "CP Strategy"
            }
            
            for item in results:
                magic = item.pop("_id")
                item["magic"] = magic
                item["manager_name"] = manager_map.get(magic, f"Manager {magic}")
                
                # Calculate win rate
                total_trades = item["win_deals"] + item["loss_deals"]
                item["win_rate"] = round((item["win_deals"] / total_trades * 100) if total_trades > 0 else 0, 2)
                
                # Average profit per deal
                item["avg_profit_per_deal"] = round(item["total_profit"] / item["total_deals"], 2) if item["total_deals"] > 0 else 0
                
                # Round values
                item["total_volume"] = round(item["total_volume"], 2)
                item["total_profit"] = round(item["total_profit"], 2)
                item["total_commission"] = round(item["total_commission"], 2)
            
            logger.info(f"Generated manager performance for {len(results)} managers")
            return results
            
        except Exception as e:
            logger.error(f"Error getting manager performance: {e}")
            raise
    
    async def get_balance_operations(
        self,
        account_number: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Get balance operations (type=2) for cash flow tracking
        
        Identifies:
        - Profit withdrawals
        - Deposits
        - Inter-account transfers
        - Interest payments
        
        Returns:
            [
                {
                    "ticket": 12345678,
                    "time": "2025-01-15T14:30:00Z",
                    "account_number": 886557,
                    "profit": 5000.00,
                    "comment": "Profit withdrawal",
                    "operation_type": "withdrawal"
                },
                ...
            ]
        """
        try:
            # Query for balance operations only
            query = {"type": 2}  # 2 = balance operation
            
            if account_number:
                query["account_number"] = account_number
            
            if start_date:
                query.setdefault("time", {})["$gte"] = start_date
            
            if end_date:
                query.setdefault("time", {})["$lte"] = end_date
            
            cursor = self.db.mt5_deals_history.find(query).sort("time", -1)
            operations = await cursor.to_list(length=None)
            
            # Classify operations based on comment
            for op in operations:
                if "_id" in op:
                    op["_id"] = str(op["_id"])
                if "time" in op:
                    op["time"] = op["time"].isoformat()
                if "synced_at" in op:
                    op["synced_at"] = op["synced_at"].isoformat()
                
                # Classify operation type
                comment = op.get("comment", "").lower()
                profit = op.get("profit", 0)
                
                if "withdrawal" in comment or "profit" in comment:
                    op["operation_type"] = "withdrawal"
                elif "deposit" in comment:
                    op["operation_type"] = "deposit"
                elif "transfer" in comment:
                    op["operation_type"] = "transfer"
                elif "interest" in comment or "separation" in comment:
                    op["operation_type"] = "interest"
                elif profit > 0:
                    op["operation_type"] = "credit"
                elif profit < 0:
                    op["operation_type"] = "debit"
                else:
                    op["operation_type"] = "other"
            
            logger.info(f"Retrieved {len(operations)} balance operations")
            return operations
            
        except Exception as e:
            logger.error(f"Error retrieving balance operations: {e}")
            raise
    
    async def get_daily_pnl(
        self,
        account_number: Optional[int] = None,
        days: int = 30
    ) -> List[Dict]:
        """
        Get daily P&L for equity curve charting
        
        Returns:
            [
                {"date": "2025-01-15", "pnl": 234.56, "volume": 5.5, "deals": 12},
                {"date": "2025-01-14", "pnl": -45.32, "volume": 3.2, "deals": 8},
                ...
            ]
        """
        try:
            # Calculate date range
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=days)
            
            # Build query
            query = {
                "type": {"$in": [0, 1]},  # Trading deals only
                "time": {"$gte": start_date, "$lte": end_date}
            }
            
            if account_number:
                query["account_number"] = account_number
            
            # Aggregation by date
            pipeline = [
                {"$match": query},
                {
                    "$group": {
                        "_id": {
                            "$dateToString": {"format": "%Y-%m-%d", "date": "$time"}
                        },
                        "pnl": {"$sum": "$profit"},
                        "volume": {"$sum": "$volume"},
                        "deals": {"$sum": 1},
                        "commission": {"$sum": "$commission"},
                        "swap": {"$sum": "$swap"}
                    }
                },
                {"$sort": {"_id": 1}}
            ]
            
            results = await self.db.mt5_deals_history.aggregate(pipeline).to_list(length=None)
            
            # Format results
            daily_pnl = []
            for item in results:
                daily_pnl.append({
                    "date": item["_id"],
                    "pnl": round(item["pnl"], 2),
                    "volume": round(item["volume"], 2),
                    "deals": item["deals"],
                    "commission": round(item["commission"], 2),
                    "swap": round(item["swap"], 2)
                })
            
            logger.info(f"Generated daily P&L for {len(daily_pnl)} days")
            return daily_pnl
            
        except Exception as e:
            logger.error(f"Error calculating daily P&L: {e}")
            raise
