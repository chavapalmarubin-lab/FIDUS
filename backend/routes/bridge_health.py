"""
Bridge Health Monitoring API
Created: November 2025

Provides comprehensive health monitoring for the 3-bridge architecture:
- MEXAtlantic MT5 Bridge (13 accounts)
- Lucrum MT5 Bridge (1 account)  
- MEXAtlantic MT4 Bridge (1 account)

Total: 15 accounts
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone, timedelta
import os
import logging
import sys

sys.path.append('/app/backend')
from services.bridge_monitoring_service import get_monitoring_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/bridges", tags=["Bridge Health"])


async def get_database():
    """Dependency to get MongoDB database"""
    mongo_url = os.getenv('MONGO_URL')
    client = AsyncIOMotorClient(mongo_url)
    return client['fidus_production']


@router.get("/health")
async def get_bridge_health():
    """
    Get comprehensive health status for all 3 bridges.
    
    Returns health checks for:
    - MEXAtlantic MT5 Bridge (13 accounts)
    - Lucrum MT5 Bridge (1 account)
    - MEXAtlantic MT4 Bridge (1 account)
    
    **Public endpoint** - No authentication required for monitoring
    
    Response:
    ```json
    {
      "status": "healthy",
      "bridges": {
        "mexatlantic_mt5": {
          "status": "running",
          "accounts": 13,
          "last_sync": "2025-11-24T18:56:21Z",
          "healthy": true
        },
        "lucrum_mt5": {
          "status": "running",
          "accounts": 1,
          "last_sync": "2025-11-24T18:56:25Z",
          "healthy": true
        },
        "mexatlantic_mt4": {
          "status": "running",
          "accounts": 1,
          "last_sync": "2025-11-24T18:56:21Z",
          "healthy": true
        }
      },
      "total_accounts": 15,
      "timestamp": "2025-11-24T18:56:30Z"
    }
    ```
    """
    try:
        db = await get_database()
        
        # Define the 3 bridges configuration based on active allocation accounts
        # FIDUS Allocation Summary (Jan 28, 2026)
        bridges_config = {
            "mexatlantic_mt5": {
                "name": "MEXAtlantic MT5",
                "broker": "MEXAtlantic",
                "platform": "MT5",
                "expected_accounts": 3,
                "account_numbers": [891215, 917105, 917106]  # MEXAtlantic MT5 accounts in allocation
            },
            "lucrum_mt5": {
                "name": "Lucrum MT5",
                "broker": "Lucrum Capital",
                "platform": "MT5",
                "expected_accounts": 4,
                "account_numbers": [20043, 2209, 2205, 2206]  # Lucrum accounts in allocation
            },
            "mexatlantic_mt4": {
                "name": "MEXAtlantic MT4",
                "broker": "MEXAtlantic",
                "platform": "MT4",
                "expected_accounts": 0,
                "account_numbers": []  # No MT4 accounts in current allocation
            }
        }
        
        # Check each bridge
        bridge_status = {}
        total_accounts = 0
        all_healthy = True
        
        for bridge_id, config in bridges_config.items():
            status = await check_bridge_health(db, bridge_id, config)
            bridge_status[bridge_id] = status
            total_accounts += status["accounts"]
            if not status["healthy"]:
                all_healthy = False
        
        overall_status = "healthy" if all_healthy else "degraded"
        
        return {
            "status": overall_status,
            "bridges": bridge_status,
            "total_accounts": total_accounts,
            "expected_total": 15,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Bridge health check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def check_bridge_health(
    db: AsyncIOMotorClient,
    bridge_id: str,
    config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Check health of a specific bridge.
    
    Args:
        db: MongoDB database instance
        bridge_id: Bridge identifier (mexatlantic_mt5, lucrum_mt5, mexatlantic_mt4)
        config: Bridge configuration
        
    Returns:
        Bridge health status with account count and last sync time
    """
    try:
        # Use account numbers directly for all bridges
        account_numbers = config.get("account_numbers", [])
        
        if account_numbers:
            query = {"account": {"$in": account_numbers}}
        else:
            # No accounts for this bridge
            return {
                "name": config["name"],
                "status": "no_accounts",
                "accounts": 0,
                "expected": config.get("expected_accounts", 0),
                "last_sync": None,
                "healthy": True,  # No accounts expected means healthy
                "message": "No accounts in allocation"
            }
        
        # Get accounts for this bridge
        accounts = await db.mt5_accounts.find(query, {"_id": 0}).to_list(length=100)
        
        # Check last sync time
        last_sync = None
        healthy = True
        status_message = "running"
        
        if accounts:
            # Get most recent sync timestamp
            sync_times = []
            for account in accounts:
                if "last_sync_timestamp" in account:
                    sync_times.append(account["last_sync_timestamp"])
                elif "timestamp" in account:
                    sync_times.append(account["timestamp"])
            
            if sync_times:
                last_sync = max(sync_times)
                
                # Check if sync is recent (within 5 minutes)
                if isinstance(last_sync, str):
                    last_sync_dt = datetime.fromisoformat(last_sync.replace('Z', '+00:00'))
                else:
                    last_sync_dt = last_sync
                
                age_minutes = (datetime.now(timezone.utc) - last_sync_dt.replace(tzinfo=timezone.utc)).total_seconds() / 60
                
                if age_minutes > 5:
                    healthy = False
                    status_message = "stale_data"
        else:
            healthy = False
            status_message = "no_accounts"
        
        # Format last sync
        last_sync_str = None
        if last_sync:
            if isinstance(last_sync, str):
                last_sync_str = last_sync
            else:
                last_sync_str = last_sync.isoformat()
        
        return {
            "status": status_message,
            "accounts": len(accounts),
            "expected_accounts": config["expected_accounts"],
            "last_sync": last_sync_str,
            "healthy": healthy and len(accounts) == config["expected_accounts"],
            "broker": config["broker"],
            "platform": config["platform"],
            "server": config["server"]
        }
        
    except Exception as e:
        logger.error(f"❌ Error checking {bridge_id}: {e}")
        return {
            "status": "error",
            "accounts": 0,
            "expected_accounts": config["expected_accounts"],
            "last_sync": None,
            "healthy": False,
            "error": str(e)
        }


@router.get("/accounts")
async def get_all_bridge_accounts():
    """
    Get all 15 accounts with bridge and platform information.
    
    Returns detailed account list with:
    - Account number, broker, platform (MT4/MT5)
    - Balance, equity, positions
    - Bridge assignment
    - Last sync status
    
    Response:
    ```json
    {
      "success": true,
      "accounts": [
        {
          "account": 886557,
          "broker": "MEXAtlantic",
          "platform": "MT5",
          "bridge": "mexatlantic_mt5",
          "server": "MEXAtlantic-Real",
          "balance": 50000.00,
          "equity": 51500.00,
          "last_sync": "2025-11-24T18:56:21Z"
        },
        ...
      ],
      "total_accounts": 15,
      "by_bridge": {
        "mexatlantic_mt5": 13,
        "lucrum_mt5": 1,
        "mexatlantic_mt4": 1
      }
    }
    ```
    """
    try:
        db = await get_database()
        
        # Get all accounts
        accounts = await db.mt5_accounts.find({}, {"_id": 0}).to_list(length=100)
        
        # Classify accounts by bridge
        classified_accounts = []
        bridge_counts = {
            "mexatlantic_mt5": 0,
            "lucrum_mt5": 0,
            "mexatlantic_mt4": 0
        }
        
        for account in accounts:
            account_num = account.get("account")
            platform = account.get("platform", "MT5")  # Default to MT5 for legacy accounts
            server = account.get("server", "")
            data_source = account.get("data_source", "")
            
            # Determine bridge
            bridge = None
            if account_num == 2198:
                bridge = "lucrum_mt5"
            elif account_num == 33200931 or platform == "MT4" or data_source == "MT4_FILE_BRIDGE":
                bridge = "mexatlantic_mt4"
            elif platform == "MT5" and "MEXAtlantic" in server:
                bridge = "mexatlantic_mt5"
            else:
                bridge = "mexatlantic_mt5"  # Default
            
            bridge_counts[bridge] += 1
            
            # Get last sync time
            last_sync = account.get("last_sync_timestamp") or account.get("timestamp")
            if last_sync and not isinstance(last_sync, str):
                last_sync = last_sync.isoformat()
            
            classified_accounts.append({
                "account": account_num,
                "broker": "Lucrum Capital" if bridge == "lucrum_mt5" else "MEXAtlantic",
                "platform": platform,
                "bridge": bridge,
                "server": server,
                "balance": account.get("balance", 0),
                "equity": account.get("equity", 0),
                "positions_count": len(account.get("positions", [])),
                "last_sync": last_sync,
                "description": account.get("description", "")
            })
        
        # Sort by account number
        classified_accounts.sort(key=lambda x: x["account"])
        
        return {
            "success": True,
            "accounts": classified_accounts,
            "total_accounts": len(classified_accounts),
            "by_bridge": bridge_counts,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting bridge accounts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts")
async def get_bridge_alerts():
    """
    Get current alerts for bridges with issues.
    
    Checks for:
    - Stale data (no sync in >5 minutes)
    - Missing accounts
    - Connection failures
    
    Response:
    ```json
    {
      "alerts": [
        {
          "bridge": "mexatlantic_mt5",
          "severity": "warning",
          "message": "Last sync 7 minutes ago",
          "timestamp": "2025-11-24T18:56:30Z"
        }
      ],
      "total_alerts": 1
    }
    ```
    """
    try:
        db = await get_database()
        
        # Get bridge health
        health = await get_bridge_health()
        
        alerts = []
        
        for bridge_id, status in health["bridges"].items():
            # Check if unhealthy
            if not status["healthy"]:
                severity = "critical" if status["status"] == "no_accounts" else "warning"
                
                if status["status"] == "no_accounts":
                    message = f"No accounts found for {bridge_id}"
                elif status["status"] == "stale_data":
                    message = f"Data not synced in >5 minutes for {bridge_id}"
                elif status["accounts"] != status["expected_accounts"]:
                    message = f"Expected {status['expected_accounts']} accounts, found {status['accounts']}"
                else:
                    message = f"Bridge {bridge_id} is unhealthy"
                
                alerts.append({
                    "bridge": bridge_id,
                    "severity": severity,
                    "message": message,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "details": status
                })
        
        return {
            "alerts": alerts,
            "total_alerts": len(alerts),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting bridge alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts/history")
async def get_alert_history(
    hours: int = Query(24, description="Number of hours to look back"),
    bridge_id: Optional[str] = Query(None, description="Filter by specific bridge")
):
    """
    Get historical alerts from the database.
    
    Parameters:
    - hours: Number of hours to look back (default: 24)
    - bridge_id: Optional filter for specific bridge
    
    Response:
    ```json
    {
      "alerts": [
        {
          "bridge_id": "lucrum_mt5",
          "bridge_name": "Lucrum MT5",
          "severity": "warning",
          "status": "stale_data",
          "issues": ["Data not synced in 12 minutes"],
          "timestamp": "2025-11-24T18:56:30Z",
          "acknowledged": false
        }
      ],
      "total_alerts": 1,
      "period_hours": 24
    }
    ```
    """
    try:
        db = await get_database()
        service = await get_monitoring_service(db)
        
        alerts = await service.get_recent_alerts(hours=hours, bridge_id=bridge_id)
        
        # Convert datetime objects to ISO strings
        for alert in alerts:
            if "timestamp" in alert and not isinstance(alert["timestamp"], str):
                alert["timestamp"] = alert["timestamp"].isoformat()
            if "last_sync" in alert and alert["last_sync"] and not isinstance(alert["last_sync"], str):
                alert["last_sync"] = alert["last_sync"].isoformat()
        
        return {
            "alerts": alerts,
            "total_alerts": len(alerts),
            "period_hours": hours,
            "bridge_filter": bridge_id
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting alert history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/monitoring/status")
async def get_monitoring_status():
    """
    Get the status of the monitoring service.
    
    Response:
    ```json
    {
      "service_running": true,
      "check_interval_seconds": 60,
      "alert_threshold_minutes": 5,
      "bridges_monitored": 3,
      "last_check": "2025-11-24T19:00:00Z"
    }
    ```
    """
    try:
        db = await get_database()
        service = await get_monitoring_service(db)
        
        return {
            "service_running": service.is_running,
            "check_interval_seconds": service.check_interval_seconds,
            "alert_threshold_minutes": service.alert_threshold_minutes,
            "bridges_monitored": len(service.bridges_config),
            "bridge_list": list(service.bridges_config.keys())
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting monitoring status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
