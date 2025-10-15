"""
Equity Snapshots Service
Handles equity progression data for trend analysis and equity curve visualization

Phase 4B: Optional Enhancements
"""

from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class EquitySnapshotsService:
    def __init__(self, db):
        self.db = db
    
    async def get_equity_snapshots(
        self,
        account_number: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 1000
    ) -> List[Dict]:
        """
        Get equity snapshots with optional filters
        
        Args:
            account_number: Filter by MT5 account
            start_date: Filter from this date
            end_date: Filter until this date
            limit: Maximum snapshots to return
        
        Returns:
            List of equity snapshot documents
        """
        try:
            # Build query
            query = {}
            
            if account_number:
                query["account_number"] = account_number
            
            if start_date:
                query.setdefault("timestamp", {})["$gte"] = start_date
            
            if end_date:
                query.setdefault("timestamp", {})["$lte"] = end_date
            
            # Query snapshots
            cursor = self.db.mt5_equity_snapshots.find(query).sort("timestamp", -1).limit(limit)
            snapshots = await cursor.to_list(length=limit)
            
            # Convert ObjectId and datetime to strings
            for snapshot in snapshots:
                if "_id" in snapshot:
                    snapshot["_id"] = str(snapshot["_id"])
                if "timestamp" in snapshot:
                    snapshot["timestamp"] = snapshot["timestamp"].isoformat()
            
            logger.info(f"Retrieved {len(snapshots)} equity snapshots")
            return snapshots
            
        except Exception as e:
            logger.error(f"Error retrieving equity snapshots: {e}")
            raise
    
    async def get_equity_curve(
        self,
        account_number: Optional[int] = None,
        days: int = 30,
        resolution: str = "daily"
    ) -> List[Dict]:
        """
        Get equity curve data for charting
        
        Args:
            account_number: Filter by account (None for all accounts)
            days: Number of days to include
            resolution: "hourly", "daily", or "weekly"
        
        Returns:
            [
                {"timestamp": "2025-01-15T10:00:00Z", "equity": 125000.50, "balance": 124500.00},
                ...
            ]
        """
        try:
            # Calculate date range
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=days)
            
            # Build query
            query = {
                "timestamp": {"$gte": start_date, "$lte": end_date}
            }
            
            if account_number:
                query["account_number"] = account_number
            
            # Determine date format based on resolution
            if resolution == "hourly":
                date_format = "%Y-%m-%d %H:00:00"
            elif resolution == "weekly":
                date_format = "%Y-W%U"  # Year-Week
            else:  # daily
                date_format = "%Y-%m-%d"
            
            # Aggregation pipeline
            pipeline = [
                {"$match": query},
                {
                    "$group": {
                        "_id": {
                            "$dateToString": {"format": date_format, "date": "$timestamp"}
                        },
                        "equity": {"$avg": "$equity"},
                        "balance": {"$avg": "$balance"},
                        "profit": {"$avg": "$profit"},
                        "count": {"$sum": 1}
                    }
                },
                {"$sort": {"_id": 1}}
            ]
            
            results = await self.db.mt5_equity_snapshots.aggregate(pipeline).to_list(length=None)
            
            # Format results
            equity_curve = []
            for item in results:
                equity_curve.append({
                    "timestamp": item["_id"],
                    "equity": round(item["equity"], 2),
                    "balance": round(item["balance"], 2),
                    "profit": round(item["profit"], 2),
                    "snapshots_count": item["count"]
                })
            
            logger.info(f"Generated equity curve: {len(equity_curve)} data points")
            return equity_curve
            
        except Exception as e:
            logger.error(f"Error generating equity curve: {e}")
            raise
    
    async def get_equity_stats(
        self,
        account_number: Optional[int] = None,
        days: int = 30
    ) -> Dict:
        """
        Get equity statistics for the period
        
        Returns:
            {
                "current_equity": 125000.50,
                "starting_equity": 120000.00,
                "highest_equity": 126500.75,
                "lowest_equity": 119500.25,
                "equity_growth": 5000.50,
                "equity_growth_pct": 4.17,
                "max_drawdown": -1000.50,
                "max_drawdown_pct": -0.83,
                "period_days": 30
            }
        """
        try:
            # Calculate date range
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=days)
            
            # Build query
            query = {
                "timestamp": {"$gte": start_date, "$lte": end_date}
            }
            
            if account_number:
                query["account_number"] = account_number
            
            # Get snapshots
            cursor = self.db.mt5_equity_snapshots.find(query).sort("timestamp", 1)
            snapshots = await cursor.to_list(length=None)
            
            if not snapshots:
                return {
                    "current_equity": 0,
                    "starting_equity": 0,
                    "highest_equity": 0,
                    "lowest_equity": 0,
                    "equity_growth": 0,
                    "equity_growth_pct": 0,
                    "max_drawdown": 0,
                    "max_drawdown_pct": 0,
                    "period_days": days
                }
            
            # Calculate statistics
            equities = [s["equity"] for s in snapshots]
            starting_equity = equities[0]
            current_equity = equities[-1]
            highest_equity = max(equities)
            lowest_equity = min(equities)
            
            equity_growth = current_equity - starting_equity
            equity_growth_pct = (equity_growth / starting_equity * 100) if starting_equity > 0 else 0
            
            # Calculate max drawdown
            max_drawdown = 0
            max_drawdown_pct = 0
            peak_equity = equities[0]
            
            for equity in equities:
                if equity > peak_equity:
                    peak_equity = equity
                
                drawdown = equity - peak_equity
                if drawdown < max_drawdown:
                    max_drawdown = drawdown
                    max_drawdown_pct = (drawdown / peak_equity * 100) if peak_equity > 0 else 0
            
            stats = {
                "current_equity": round(current_equity, 2),
                "starting_equity": round(starting_equity, 2),
                "highest_equity": round(highest_equity, 2),
                "lowest_equity": round(lowest_equity, 2),
                "equity_growth": round(equity_growth, 2),
                "equity_growth_pct": round(equity_growth_pct, 2),
                "max_drawdown": round(max_drawdown, 2),
                "max_drawdown_pct": round(max_drawdown_pct, 2),
                "period_days": days,
                "snapshots_count": len(snapshots)
            }
            
            logger.info(f"Calculated equity stats: growth={equity_growth:.2f}, drawdown={max_drawdown:.2f}")
            return stats
            
        except Exception as e:
            logger.error(f"Error calculating equity stats: {e}")
            raise
