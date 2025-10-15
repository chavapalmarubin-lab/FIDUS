"""
Pending Orders Service
Handles pending MT5 orders (limit, stop, stop-limit orders)

Phase 4B: Optional Enhancements
"""

from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class PendingOrdersService:
    def __init__(self, db):
        self.db = db
    
    async def get_pending_orders(
        self,
        account_number: Optional[int] = None,
        symbol: Optional[str] = None
    ) -> List[Dict]:
        """
        Get pending orders with optional filters
        
        Args:
            account_number: Filter by MT5 account
            symbol: Filter by symbol (e.g., 'EURUSD')
        
        Returns:
            List of pending order documents
        """
        try:
            # Build query
            query = {}
            
            if account_number:
                query["account_number"] = account_number
            
            if symbol:
                query["symbol"] = symbol
            
            # Query orders
            cursor = self.db.mt5_pending_orders.find(query).sort("time_setup", -1)
            orders = await cursor.to_list(length=None)
            
            # Convert ObjectId and datetime to strings
            for order in orders:
                if "_id" in order:
                    order["_id"] = str(order["_id"])
                if "time_setup" in order:
                    order["time_setup"] = order["time_setup"].isoformat()
                if "time_expiration" in order and order["time_expiration"]:
                    order["time_expiration"] = order["time_expiration"].isoformat()
                if "synced_at" in order:
                    order["synced_at"] = order["synced_at"].isoformat()
            
            logger.info(f"Retrieved {len(orders)} pending orders")
            return orders
            
        except Exception as e:
            logger.error(f"Error retrieving pending orders: {e}")
            raise
    
    async def get_pending_orders_summary(
        self,
        account_number: Optional[int] = None
    ) -> Dict:
        """
        Get summary of pending orders
        
        Returns:
            {
                "total_orders": 12,
                "buy_orders": 7,
                "sell_orders": 5,
                "total_volume": 15.5,
                "by_type": [
                    {"type_name": "BUY_LIMIT", "count": 5, "volume": 7.5},
                    {"type_name": "SELL_STOP", "count": 4, "volume": 6.0},
                    ...
                ],
                "by_symbol": [
                    {"symbol": "EURUSD", "count": 6, "volume": 9.0},
                    ...
                ]
            }
        """
        try:
            # Build query
            query = {}
            
            if account_number:
                query["account_number"] = account_number
            
            # Total counts pipeline
            count_pipeline = [
                {"$match": query},
                {
                    "$group": {
                        "_id": None,
                        "total_orders": {"$sum": 1},
                        "total_volume": {"$sum": "$volume_current"},
                        "buy_orders": {
                            "$sum": {"$cond": [{"$in": ["$type", [0, 2, 4, 6]]}, 1, 0]}
                        },
                        "sell_orders": {
                            "$sum": {"$cond": [{"$in": ["$type", [1, 3, 5, 7]]}, 1, 0]}
                        }
                    }
                }
            ]
            
            count_result = await self.db.mt5_pending_orders.aggregate(count_pipeline).to_list(length=1)
            
            if not count_result:
                return {
                    "total_orders": 0,
                    "buy_orders": 0,
                    "sell_orders": 0,
                    "total_volume": 0,
                    "by_type": [],
                    "by_symbol": []
                }
            
            summary = count_result[0]
            summary.pop("_id", None)
            
            # By type breakdown
            by_type_pipeline = [
                {"$match": query},
                {
                    "$group": {
                        "_id": "$type_name",
                        "count": {"$sum": 1},
                        "volume": {"$sum": "$volume_current"}
                    }
                },
                {"$sort": {"count": -1}}
            ]
            
            by_type = await self.db.mt5_pending_orders.aggregate(by_type_pipeline).to_list(length=None)
            
            for item in by_type:
                item["type_name"] = item.pop("_id")
                item["volume"] = round(item["volume"], 2)
            
            summary["by_type"] = by_type
            
            # By symbol breakdown
            by_symbol_pipeline = [
                {"$match": query},
                {
                    "$group": {
                        "_id": "$symbol",
                        "count": {"$sum": 1},
                        "volume": {"$sum": "$volume_current"}
                    }
                },
                {"$sort": {"count": -1}}
            ]
            
            by_symbol = await self.db.mt5_pending_orders.aggregate(by_symbol_pipeline).to_list(length=None)
            
            for item in by_symbol:
                item["symbol"] = item.pop("_id")
                item["volume"] = round(item["volume"], 2)
            
            summary["by_symbol"] = by_symbol
            
            # Round values
            summary["total_volume"] = round(summary["total_volume"], 2)
            
            logger.info(f"Generated pending orders summary: {summary['total_orders']} orders")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating pending orders summary: {e}")
            raise
