"""
Spread Analysis Service
Analyzes broker spreads and trading costs

Phase 4B: Optional Enhancements
"""

from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class SpreadAnalysisService:
    def __init__(self, db):
        self.db = db
    
    async def get_spread_statistics(
        self,
        symbol: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """
        Get spread statistics for symbols
        
        Returns:
            {
                "by_symbol": [
                    {
                        "symbol": "EURUSD",
                        "avg_spread": 1.8,
                        "min_spread": 0.5,
                        "max_spread": 3.5,
                        "total_deals": 234,
                        "total_volume": 45.5
                    },
                    ...
                ],
                "total_deals": 1234,
                "avg_spread_all": 2.1
            }
        """
        try:
            # Build query (only trading deals with spread data)
            query = {
                "type": {"$in": [0, 1]},  # Buy/Sell only
                "spread": {"$exists": True, "$ne": None, "$gt": 0}
            }
            
            if symbol:
                query["symbol"] = symbol
            
            if start_date:
                query.setdefault("time", {})["$gte"] = start_date
            
            if end_date:
                query.setdefault("time", {})["$lte"] = end_date
            
            # Aggregation by symbol
            pipeline = [
                {"$match": query},
                {
                    "$group": {
                        "_id": "$symbol",
                        "avg_spread": {"$avg": "$spread"},
                        "min_spread": {"$min": "$spread"},
                        "max_spread": {"$max": "$spread"},
                        "total_deals": {"$sum": 1},
                        "total_volume": {"$sum": "$volume"}
                    }
                },
                {"$sort": {"total_deals": -1}}
            ]
            
            results = await self.db.mt5_deals_history.aggregate(pipeline).to_list(length=None)
            
            # Format results
            by_symbol = []
            total_deals = 0
            total_spread = 0
            
            for item in results:
                by_symbol.append({
                    "symbol": item["_id"],
                    "avg_spread": round(item["avg_spread"], 2),
                    "min_spread": round(item["min_spread"], 2),
                    "max_spread": round(item["max_spread"], 2),
                    "total_deals": item["total_deals"],
                    "total_volume": round(item["total_volume"], 2)
                })
                total_deals += item["total_deals"]
                total_spread += item["avg_spread"] * item["total_deals"]
            
            avg_spread_all = round(total_spread / total_deals, 2) if total_deals > 0 else 0
            
            statistics = {
                "by_symbol": by_symbol,
                "total_deals": total_deals,
                "avg_spread_all": avg_spread_all
            }
            
            logger.info(f"Generated spread statistics for {len(by_symbol)} symbols")
            return statistics
            
        except Exception as e:
            logger.error(f"Error calculating spread statistics: {e}")
            raise
    
    async def calculate_spread_costs(
        self,
        account_number: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """
        Calculate spread costs (estimated cost from spreads)
        
        Returns:
            {
                "total_spread_cost": 1234.56,
                "by_symbol": [
                    {
                        "symbol": "EURUSD",
                        "spread_cost": 456.78,
                        "deals": 123,
                        "avg_spread": 1.8
                    },
                    ...
                ],
                "by_account": [...]
            }
        """
        try:
            # Build query
            query = {
                "type": {"$in": [0, 1]},
                "spread": {"$exists": True, "$ne": None, "$gt": 0}
            }
            
            if account_number:
                query["account_number"] = account_number
            
            if start_date:
                query.setdefault("time", {})["$gte"] = start_date
            
            if end_date:
                query.setdefault("time", {})["$lte"] = end_date
            
            # Note: Spread cost calculation is symbol-specific
            # For simplicity, we estimate: cost = spread * pip_value * volume
            # Pip values vary by symbol, but we'll use a simplified calculation
            
            # By symbol
            by_symbol_pipeline = [
                {"$match": query},
                {
                    "$group": {
                        "_id": "$symbol",
                        "total_spread": {"$sum": "$spread"},
                        "avg_spread": {"$avg": "$spread"},
                        "total_volume": {"$sum": "$volume"},
                        "deals": {"$sum": 1}
                    }
                },
                {"$sort": {"total_volume": -1}}
            ]
            
            by_symbol = await self.db.mt5_deals_history.aggregate(by_symbol_pipeline).to_list(length=None)
            
            # Estimate spread cost (simplified: assume $10 pip value)
            total_spread_cost = 0
            
            for item in by_symbol:
                # Simplified spread cost: spread_points * volume * $10
                spread_cost = item["total_spread"] * item["total_volume"] * 0.1  # Rough estimate
                item["spread_cost"] = round(spread_cost, 2)
                item["symbol"] = item.pop("_id")
                item["avg_spread"] = round(item["avg_spread"], 2)
                item["total_volume"] = round(item["total_volume"], 2)
                total_spread_cost += spread_cost
            
            # By account
            by_account_pipeline = [
                {"$match": query},
                {
                    "$group": {
                        "_id": "$account_number",
                        "account_name": {"$first": "$account_name"},
                        "total_spread": {"$sum": "$spread"},
                        "total_volume": {"$sum": "$volume"},
                        "deals": {"$sum": 1}
                    }
                },
                {"$sort": {"total_volume": -1}}
            ]
            
            by_account = await self.db.mt5_deals_history.aggregate(by_account_pipeline).to_list(length=None)
            
            for item in by_account:
                spread_cost = item["total_spread"] * item["total_volume"] * 0.1
                item["spread_cost"] = round(spread_cost, 2)
                item["account_number"] = item.pop("_id")
                item["total_volume"] = round(item["total_volume"], 2)
            
            result = {
                "total_spread_cost": round(total_spread_cost, 2),
                "by_symbol": by_symbol[:10],  # Top 10
                "by_account": by_account,
                "note": "Spread costs are estimates based on average pip values"
            }
            
            logger.info(f"Calculated spread costs: ${total_spread_cost:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Error calculating spread costs: {e}")
            raise
