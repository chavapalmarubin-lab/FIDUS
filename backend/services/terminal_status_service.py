"""
Terminal Status Service
Handles MT5 terminal connection health and sync monitoring

Phase 4B: Optional Enhancements
"""

from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class TerminalStatusService:
    def __init__(self, db):
        self.db = db
    
    async def get_latest_status(self) -> Dict:
        """
        Get the most recent terminal status
        
        Returns:
            {
                "timestamp": "2025-01-15T14:30:00Z",
                "connected": true,
                "trade_allowed": true,
                "terminal_initialized": true,
                "active_accounts": 7,
                "total_errors_today": 2,
                "last_error_time": "2025-01-15T10:00:00Z",
                "build": 3850,
                "ping_last": 45,
                "health_status": "healthy"  // "healthy", "warning", "critical"
            }
        """
        try:
            # Get latest status
            cursor = self.db.mt5_terminal_status.find().sort("timestamp", -1).limit(1)
            statuses = await cursor.to_list(length=1)
            
            if not statuses:
                return {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "connected": False,
                    "health_status": "unknown",
                    "message": "No terminal status data available"
                }
            
            status = statuses[0]
            
            # Convert ObjectId and datetime
            if "_id" in status:
                status["_id"] = str(status["_id"])
            if "timestamp" in status:
                status["timestamp"] = status["timestamp"].isoformat()
            if "last_error_time" in status and status["last_error_time"]:
                status["last_error_time"] = status["last_error_time"].isoformat()
            
            # Determine health status
            health_status = "healthy"
            
            if not status.get("connected", False):
                health_status = "critical"
            elif not status.get("terminal_initialized", False):
                health_status = "critical"
            elif not status.get("trade_allowed", False):
                health_status = "warning"
            elif status.get("total_errors_today", 0) > 10:
                health_status = "warning"
            elif status.get("ping_last", 0) > 1000:  # High ping
                health_status = "warning"
            
            status["health_status"] = health_status
            
            logger.info(f"Retrieved terminal status: {health_status}")
            return status
            
        except Exception as e:
            logger.error(f"Error retrieving terminal status: {e}")
            raise
    
    async def get_status_history(
        self,
        hours: int = 24
    ) -> List[Dict]:
        """
        Get terminal status history for the past N hours
        
        Args:
            hours: Number of hours to retrieve
        
        Returns:
            List of status documents
        """
        try:
            # Calculate time range
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(hours=hours)
            
            # Query
            query = {
                "timestamp": {"$gte": start_date, "$lte": end_date}
            }
            
            cursor = self.db.mt5_terminal_status.find(query).sort("timestamp", -1)
            statuses = await cursor.to_list(length=None)
            
            # Convert ObjectId and datetime
            for status in statuses:
                if "_id" in status:
                    status["_id"] = str(status["_id"])
                if "timestamp" in status:
                    status["timestamp"] = status["timestamp"].isoformat()
                if "last_error_time" in status and status["last_error_time"]:
                    status["last_error_time"] = status["last_error_time"].isoformat()
            
            logger.info(f"Retrieved {len(statuses)} status records for past {hours} hours")
            return statuses
            
        except Exception as e:
            logger.error(f"Error retrieving status history: {e}")
            raise
    
    async def get_error_logs(
        self,
        hours: int = 24,
        error_type: Optional[str] = None,
        account_number: Optional[int] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Get error logs for monitoring
        
        Args:
            hours: Number of hours to retrieve
            error_type: Filter by error type
            account_number: Filter by account
            limit: Maximum errors to return
        
        Returns:
            List of error documents
        """
        try:
            # Calculate time range
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(hours=hours)
            
            # Build query
            query = {
                "timestamp": {"$gte": start_date, "$lte": end_date}
            }
            
            if error_type:
                query["error_type"] = error_type
            
            if account_number:
                query["account_number"] = account_number
            
            # Query errors
            cursor = self.db.mt5_error_logs.find(query).sort("timestamp", -1).limit(limit)
            errors = await cursor.to_list(length=limit)
            
            # Convert ObjectId and datetime
            for error in errors:
                if "_id" in error:
                    error["_id"] = str(error["_id"])
                if "timestamp" in error:
                    error["timestamp"] = error["timestamp"].isoformat()
            
            logger.info(f"Retrieved {len(errors)} error logs")
            return errors
            
        except Exception as e:
            logger.error(f"Error retrieving error logs: {e}")
            raise
    
    async def get_error_summary(
        self,
        hours: int = 24
    ) -> Dict:
        """
        Get error summary for the period
        
        Returns:
            {
                "total_errors": 15,
                "by_type": [
                    {"error_type": "account_sync_login", "count": 8},
                    {"error_type": "deal_collection", "count": 5},
                    ...
                ],
                "by_account": [
                    {"account_number": 886557, "count": 6},
                    ...
                ],
                "period_hours": 24
            }
        """
        try:
            # Calculate time range
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(hours=hours)
            
            # Query
            query = {
                "timestamp": {"$gte": start_date, "$lte": end_date}
            }
            
            # Total count
            total_errors = await self.db.mt5_error_logs.count_documents(query)
            
            # By type
            by_type_pipeline = [
                {"$match": query},
                {
                    "$group": {
                        "_id": "$error_type",
                        "count": {"$sum": 1}
                    }
                },
                {"$sort": {"count": -1}}
            ]
            
            by_type = await self.db.mt5_error_logs.aggregate(by_type_pipeline).to_list(length=None)
            
            for item in by_type:
                item["error_type"] = item.pop("_id")
            
            # By account
            by_account_pipeline = [
                {"$match": {**query, "account_number": {"$ne": None}}},
                {
                    "$group": {
                        "_id": "$account_number",
                        "count": {"$sum": 1}
                    }
                },
                {"$sort": {"count": -1}}
            ]
            
            by_account = await self.db.mt5_error_logs.aggregate(by_account_pipeline).to_list(length=None)
            
            for item in by_account:
                item["account_number"] = item.pop("_id")
            
            summary = {
                "total_errors": total_errors,
                "by_type": by_type,
                "by_account": by_account,
                "period_hours": hours
            }
            
            logger.info(f"Generated error summary: {total_errors} errors in past {hours} hours")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating error summary: {e}")
            raise
    
    async def get_sync_status(self) -> Dict:
        """
        Get overall sync status for all MT5 accounts
        
        Returns:
            {
                "last_account_sync": "2025-01-15T14:30:00Z",
                "last_deal_sync": "2025-01-15T12:00:00Z",
                "last_equity_snapshot": "2025-01-15T14:00:00Z",
                "accounts_synced": 7,
                "deals_synced_today": 345,
                "snapshots_today": 168,
                "sync_health": "healthy",
                "data_freshness_minutes": 5
            }
        """
        try:
            # Get latest terminal status for sync times
            latest_status = await self.get_latest_status()
            
            # Get latest account sync time
            cursor = self.db.mt5_accounts.find().sort("last_sync", -1).limit(1)
            accounts = await cursor.to_list(length=1)
            last_account_sync = accounts[0]["last_sync"] if accounts else None
            
            # Count deals synced today
            today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            deals_today = await self.db.mt5_deals_history.count_documents({
                "synced_at": {"$gte": today_start}
            })
            
            # Count snapshots today
            snapshots_today = await self.db.mt5_equity_snapshots.count_documents({
                "timestamp": {"$gte": today_start}
            })
            
            # Calculate data freshness
            data_freshness_minutes = 0
            if last_account_sync:
                time_diff = datetime.now(timezone.utc) - last_account_sync
                data_freshness_minutes = int(time_diff.total_seconds() / 60)
            
            # Determine sync health
            sync_health = "healthy"
            if data_freshness_minutes > 30:
                sync_health = "warning"
            if data_freshness_minutes > 60:
                sync_health = "critical"
            
            sync_status = {
                "last_account_sync": last_account_sync.isoformat() if last_account_sync else None,
                "accounts_synced": latest_status.get("active_accounts", 0),
                "deals_synced_today": deals_today,
                "snapshots_today": snapshots_today,
                "sync_health": sync_health,
                "data_freshness_minutes": data_freshness_minutes
            }
            
            logger.info(f"Generated sync status: {sync_health}")
            return sync_status
            
        except Exception as e:
            logger.error(f"Error generating sync status: {e}")
            raise
