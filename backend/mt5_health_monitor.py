"""
MT5 Bridge Service Health Monitor
Checks if MT5 data is syncing properly from VPS to MongoDB
"""
from datetime import datetime, timezone, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
import os

class MT5HealthMonitor:
    """Monitor MT5 Bridge Service health"""
    
    def __init__(self, db):
        self.db = db
        self.stale_threshold_minutes = 10  # Alert if no sync in 10 minutes
    
    async def check_health(self):
        """
        Comprehensive health check for MT5 Bridge Service
        Returns detailed status including:
        - Service status (running/stale/stopped)
        - Account sync status
        - Data freshness
        - Sync errors
        """
        try:
            # Check if mt5_accounts collection exists
            collections = await self.db.list_collection_names()
            
            if 'mt5_accounts' not in collections:
                return {
                    "status": "error",
                    "message": "mt5_accounts collection not found",
                    "service_running": False,
                    "accounts_synced": 0,
                    "expected_accounts": 7
                }
            
            # Get all MT5 accounts
            accounts = await self.db.mt5_accounts.find({}).to_list(length=None)
            
            if len(accounts) == 0:
                return {
                    "status": "error",
                    "message": "No MT5 accounts in database",
                    "service_running": False,
                    "accounts_synced": 0,
                    "expected_accounts": 7
                }
            
            # Check data freshness
            now = datetime.now(timezone.utc)
            stale_accounts = []
            fresh_accounts = []
            never_synced = []
            
            for account in accounts:
                account_num = account.get('account')
                last_sync = account.get('last_sync')
                
                if last_sync is None:
                    never_synced.append(account_num)
                else:
                    # Handle both datetime objects and ISO strings
                    if isinstance(last_sync, str):
                        last_sync = datetime.fromisoformat(last_sync.replace('Z', '+00:00'))
                    elif last_sync.tzinfo is None:
                        last_sync = last_sync.replace(tzinfo=timezone.utc)
                    
                    minutes_since_sync = (now - last_sync).total_seconds() / 60
                    
                    if minutes_since_sync > self.stale_threshold_minutes:
                        stale_accounts.append({
                            "account": account_num,
                            "minutes_since_sync": round(minutes_since_sync, 1),
                            "last_sync": last_sync.isoformat()
                        })
                    else:
                        fresh_accounts.append({
                            "account": account_num,
                            "minutes_since_sync": round(minutes_since_sync, 1),
                            "last_sync": last_sync.isoformat(),
                            "equity": account.get('equity', 0),
                            "profit": account.get('profit', 0)
                        })
            
            # Determine overall status
            if len(fresh_accounts) == len(accounts):
                status = "healthy"
                message = f"All {len(accounts)} accounts syncing properly"
            elif len(fresh_accounts) > 0:
                status = "degraded"
                message = f"{len(fresh_accounts)}/{len(accounts)} accounts syncing"
            else:
                status = "critical"
                message = "No accounts syncing - service may be down"
            
            # Check if expected accounts are present
            expected_accounts = [886557, 886066, 886602, 885822, 886528, 891215, 891234]
            present_accounts = [acc.get('account') for acc in accounts]
            missing_accounts = [acc for acc in expected_accounts if acc not in present_accounts]
            
            return {
                "status": status,
                "message": message,
                "service_running": len(fresh_accounts) > 0,
                "timestamp": now.isoformat(),
                "accounts": {
                    "total": len(accounts),
                    "expected": len(expected_accounts),
                    "fresh": len(fresh_accounts),
                    "stale": len(stale_accounts),
                    "never_synced": len(never_synced)
                },
                "fresh_accounts": fresh_accounts,
                "stale_accounts": stale_accounts if stale_accounts else None,
                "never_synced_accounts": never_synced if never_synced else None,
                "missing_accounts": missing_accounts if missing_accounts else None,
                "sync_threshold_minutes": self.stale_threshold_minutes
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Health check failed: {str(e)}",
                "service_running": False,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def get_sync_history(self, hours=24):
        """Get sync history for the last N hours"""
        try:
            # This would require a sync_history collection
            # For now, just check current state
            accounts = await self.db.mt5_accounts.find({}).to_list(length=None)
            
            history = []
            for account in accounts:
                history.append({
                    "account": account.get('account'),
                    "last_sync": account.get('last_sync'),
                    "equity": account.get('equity'),
                    "profit": account.get('profit'),
                    "connection_status": account.get('connection_status')
                })
            
            return {
                "period_hours": hours,
                "accounts": history
            }
            
        except Exception as e:
            return {
                "error": str(e)
            }

# Export for use in FastAPI
def get_mt5_health_monitor(db):
    return MT5HealthMonitor(db)
