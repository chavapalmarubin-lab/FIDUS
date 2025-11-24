"""
Bridge Monitoring and Alerting Service
Created: November 2025

Monitors the 3-bridge architecture and triggers alerts for:
- Stale data (no sync in >5 minutes)
- Missing accounts
- Connection failures
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
from motor.motor_asyncio import AsyncIOMotorClient
import os

logger = logging.getLogger(__name__)


class BridgeMonitoringService:
    """
    Service to monitor bridge health and send alerts.
    """
    
    def __init__(self, db: AsyncIOMotorClient):
        self.db = db
        self.alert_threshold_minutes = 5
        self.check_interval_seconds = 60  # Check every minute
        self.is_running = False
        
        # Bridge configurations
        self.bridges_config = {
            "mexatlantic_mt5": {
                "name": "MEXAtlantic MT5",
                "broker": "MEXAtlantic",
                "platform": "MT5",
                "expected_accounts": 13,
                "server": "MEXAtlantic-Real"
            },
            "lucrum_mt5": {
                "name": "Lucrum MT5",
                "broker": "Lucrum Capital",
                "platform": "MT5",
                "expected_accounts": 1,
                "server": "LucrumCapital-Trade",
                "account_numbers": [2198]
            },
            "mexatlantic_mt4": {
                "name": "MEXAtlantic MT4",
                "broker": "MEXAtlantic",
                "platform": "MT4",
                "expected_accounts": 1,
                "server": "MEXAtlantic-Real",
                "account_numbers": [33200931]
            }
        }
    
    async def start_monitoring(self):
        """
        Start the monitoring service.
        Runs in background and checks bridge health periodically.
        """
        if self.is_running:
            logger.warning("⚠️ Monitoring service already running")
            return
        
        self.is_running = True
        logger.info("🚀 Bridge Monitoring Service started")
        
        while self.is_running:
            try:
                await self.check_all_bridges()
                await asyncio.sleep(self.check_interval_seconds)
            except Exception as e:
                logger.error(f"❌ Error in monitoring loop: {e}")
                await asyncio.sleep(self.check_interval_seconds)
    
    async def stop_monitoring(self):
        """Stop the monitoring service."""
        self.is_running = False
        logger.info("🛑 Bridge Monitoring Service stopped")
    
    async def check_all_bridges(self):
        """
        Check health of all bridges and trigger alerts if needed.
        """
        try:
            alerts = []
            
            for bridge_id, config in self.bridges_config.items():
                status = await self.check_bridge_health(bridge_id, config)
                
                if not status["healthy"]:
                    alert = await self.create_alert(bridge_id, status, config)
                    alerts.append(alert)
            
            if alerts:
                await self.handle_alerts(alerts)
            
        except Exception as e:
            logger.error(f"❌ Error checking bridges: {e}")
    
    async def check_bridge_health(
        self,
        bridge_id: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Check health of a specific bridge.
        """
        try:
            # Build query based on bridge type
            if bridge_id == "mexatlantic_mt5":
                query = {
                    "$or": [
                        {"platform": {"$exists": False}},
                        {"platform": "MT5"}
                    ],
                    "server": config["server"]
                }
            elif bridge_id == "lucrum_mt5":
                query = {
                    "account": {"$in": config["account_numbers"]}
                }
            elif bridge_id == "mexatlantic_mt4":
                query = {
                    "account": {"$in": config["account_numbers"]},
                    "$or": [
                        {"platform": "MT4"},
                        {"data_source": "MT4_FILE_BRIDGE"}
                    ]
                }
            else:
                query = {}
            
            # Get accounts for this bridge
            accounts = await self.db.mt5_accounts.find(query).to_list(length=100)
            
            # Check last sync time
            last_sync = None
            healthy = True
            status_message = "running"
            issues = []
            
            if not accounts:
                healthy = False
                status_message = "no_accounts"
                issues.append(f"No accounts found for {config['name']}")
            else:
                # Check account count
                if len(accounts) != config["expected_accounts"]:
                    healthy = False
                    issues.append(
                        f"Expected {config['expected_accounts']} accounts, "
                        f"found {len(accounts)}"
                    )
                
                # Get most recent sync timestamp
                sync_times = []
                for account in accounts:
                    if "last_sync_timestamp" in account:
                        sync_times.append(account["last_sync_timestamp"])
                    elif "timestamp" in account:
                        sync_times.append(account["timestamp"])
                
                if sync_times:
                    last_sync = max(sync_times)
                    
                    # Check if sync is recent
                    if isinstance(last_sync, str):
                        last_sync_dt = datetime.fromisoformat(
                            last_sync.replace('Z', '+00:00')
                        )
                    else:
                        last_sync_dt = last_sync
                    
                    age_minutes = (
                        datetime.now(timezone.utc) - 
                        last_sync_dt.replace(tzinfo=timezone.utc)
                    ).total_seconds() / 60
                    
                    if age_minutes > self.alert_threshold_minutes:
                        healthy = False
                        status_message = "stale_data"
                        issues.append(
                            f"Data not synced in {int(age_minutes)} minutes "
                            f"(threshold: {self.alert_threshold_minutes} minutes)"
                        )
            
            return {
                "healthy": healthy,
                "status": status_message,
                "accounts": len(accounts),
                "expected_accounts": config["expected_accounts"],
                "last_sync": last_sync,
                "issues": issues
            }
            
        except Exception as e:
            logger.error(f"❌ Error checking {bridge_id}: {e}")
            return {
                "healthy": False,
                "status": "error",
                "accounts": 0,
                "expected_accounts": config["expected_accounts"],
                "last_sync": None,
                "issues": [str(e)]
            }
    
    async def create_alert(
        self,
        bridge_id: str,
        status: Dict[str, Any],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create an alert for an unhealthy bridge.
        """
        severity = "critical" if status["status"] == "no_accounts" else "warning"
        
        alert = {
            "bridge_id": bridge_id,
            "bridge_name": config["name"],
            "severity": severity,
            "status": status["status"],
            "issues": status["issues"],
            "accounts_found": status["accounts"],
            "accounts_expected": status["expected_accounts"],
            "last_sync": status["last_sync"],
            "timestamp": datetime.now(timezone.utc),
            "acknowledged": False
        }
        
        return alert
    
    async def handle_alerts(self, alerts: List[Dict[str, Any]]):
        """
        Handle alerts by logging and optionally storing in database.
        """
        for alert in alerts:
            logger.warning(
                f"⚠️ ALERT [{alert['severity'].upper()}]: "
                f"{alert['bridge_name']} - {', '.join(alert['issues'])}"
            )
            
            # Store alert in database for history
            try:
                await self.db.bridge_alerts.insert_one(alert)
            except Exception as e:
                logger.error(f"❌ Error storing alert: {e}")
    
    async def get_recent_alerts(
        self,
        hours: int = 24,
        bridge_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get recent alerts from the database.
        """
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
            
            query = {"timestamp": {"$gte": cutoff_time}}
            if bridge_id:
                query["bridge_id"] = bridge_id
            
            alerts = await self.db.bridge_alerts.find(
                query,
                {"_id": 0}
            ).sort("timestamp", -1).to_list(length=100)
            
            return alerts
            
        except Exception as e:
            logger.error(f"❌ Error getting recent alerts: {e}")
            return []
    
    async def acknowledge_alert(self, alert_timestamp: datetime):
        """
        Acknowledge an alert.
        """
        try:
            result = await self.db.bridge_alerts.update_one(
                {"timestamp": alert_timestamp},
                {"$set": {"acknowledged": True, "acknowledged_at": datetime.now(timezone.utc)}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"❌ Error acknowledging alert: {e}")
            return False
    
    async def get_bridge_status_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all bridge statuses.
        """
        try:
            summary = {
                "timestamp": datetime.now(timezone.utc),
                "bridges": {},
                "overall_healthy": True,
                "total_accounts": 0,
                "active_alerts": 0
            }
            
            for bridge_id, config in self.bridges_config.items():
                status = await self.check_bridge_health(bridge_id, config)
                summary["bridges"][bridge_id] = status
                summary["total_accounts"] += status["accounts"]
                
                if not status["healthy"]:
                    summary["overall_healthy"] = False
                    summary["active_alerts"] += 1
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Error getting status summary: {e}")
            return {
                "timestamp": datetime.now(timezone.utc),
                "bridges": {},
                "overall_healthy": False,
                "total_accounts": 0,
                "active_alerts": 0,
                "error": str(e)
            }


# Global instance
_monitoring_service: Optional[BridgeMonitoringService] = None


async def get_monitoring_service(db: AsyncIOMotorClient) -> BridgeMonitoringService:
    """
    Get or create the global monitoring service instance.
    """
    global _monitoring_service
    
    if _monitoring_service is None:
        _monitoring_service = BridgeMonitoringService(db)
    
    return _monitoring_service


async def start_monitoring_service(db: AsyncIOMotorClient):
    """
    Start the monitoring service in the background.
    """
    service = await get_monitoring_service(db)
    asyncio.create_task(service.start_monitoring())
    logger.info("✅ Bridge monitoring service task created")
