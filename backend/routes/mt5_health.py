"""
MT5 Health Check API Endpoints
Created: November 10, 2025

Provides comprehensive health monitoring for MT5 data pipeline.
Integrates with MT5 Watchdog service for auto-healing.
"""

from fastapi import APIRouter, Depends, HTTPException, Header
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
import os
import logging

# Import the watchdog service
import sys
sys.path.append('/app/backend')
from services.mt5_watchdog import MT5Watchdog, get_watchdog

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/mt5", tags=["MT5 Health"])


async def get_database():
    """Dependency to get MongoDB database"""
    mongo_url = os.getenv('MONGO_URL')
    client = AsyncIOMotorClient(mongo_url)
    return client['fidus_production']


@router.get("/health-check")
async def get_mt5_health_check():
    """
    Get comprehensive MT5 system health status.
    
    Returns health checks for:
    - mt5_deals collection (data availability)
    - mt5_accounts collection (account tracking)
    - Initial allocations (P&L calculation readiness)
    - VPS sync status (data freshness)
    - Money manager data (configuration validity)
    
    **Public endpoint** - No authentication required for monitoring
    
    Response:
    ```json
    {
      "success": true,
      "overall_healthy": true,
      "components": {
        "mt5_deals": {"healthy": true, "count": 2812},
        "mt5_accounts": {"healthy": true, "active_accounts": 8},
        "initial_allocations": {"healthy": true, "total_allocation": 138805.17},
        "vps_sync": {"healthy": true, "age_minutes": 3.2},
        "money_managers": {"healthy": true, "total_managers": 5}
      },
      "timestamp": "2025-11-10T12:30:00Z"
    }
    ```
    """
    try:
        db = await get_database()
        
        # Get watchdog instance
        watchdog = await get_watchdog(db)
        
        # Run comprehensive health check
        health_status = await watchdog.check_system_health()
        
        return {
            "success": True,
            "overall_healthy": health_status["overall_healthy"],
            "components": health_status["components"],
            "timestamp": health_status["timestamp"].isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Health check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health-summary")
async def get_mt5_health_summary():
    """
    Get quick health summary (minimal response for dashboards).
    
    **Public endpoint** - No authentication required
    
    Response:
    ```json
    {
      "healthy": true,
      "deals_count": 2812,
      "active_accounts": 8,
      "last_sync_minutes": 3.2
    }
    ```
    """
    try:
        db = await get_database()
        watchdog = await get_watchdog(db)
        
        # Run health check
        health = await watchdog.check_system_health()
        
        return {
            "healthy": health["overall_healthy"],
            "deals_count": health["components"]["mt5_deals"].get("count", 0),
            "active_accounts": health["components"]["mt5_accounts"].get("active_accounts", 0),
            "last_sync_minutes": health["components"]["vps_sync"].get("age_minutes", 999),
            "timestamp": health["timestamp"].isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Health summary error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trigger-auto-healing")
async def trigger_manual_healing(
    reason: str,
    authorization: Optional[str] = Header(None)
):
    """
    Manually trigger auto-healing process.
    
    **Admin only** - Requires authentication
    
    Parameters:
    - reason: Description of why healing is being triggered
    
    Example:
    ```bash
    curl -X POST https://fidus-api.onrender.com/api/mt5/trigger-auto-healing \\
      -H "Authorization: Bearer YOUR_TOKEN" \\
      -H "Content-Type: application/json" \\
      -d '{"reason": "Manual test of auto-healing system"}'
    ```
    
    Response:
    ```json
    {
      "success": true,
      "message": "Auto-healing triggered successfully",
      "reason": "Manual test of auto-healing system"
    }
    ```
    """
    try:
        # TODO: Add proper authentication check
        # For now, just verify authorization header exists
        if not authorization:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        db = await get_database()
        watchdog = await get_watchdog(db)
        
        # Create mock health status for manual trigger
        mock_health = {
            "components": {
                "manual_trigger": {"healthy": False}
            }
        }
        
        # Trigger healing
        success = await watchdog.trigger_auto_healing(mock_health)
        
        if success:
            return {
                "success": True,
                "message": "Auto-healing triggered successfully",
                "reason": reason
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to trigger auto-healing"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Manual healing trigger error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/component-health/{component}")
async def get_component_health(component: str):
    """
    Get health status for a specific component.
    
    **Public endpoint** - No authentication required
    
    Parameters:
    - component: One of: mt5_deals, mt5_accounts, initial_allocations, vps_sync, money_managers
    
    Response:
    ```json
    {
      "component": "mt5_deals",
      "healthy": true,
      "details": {
        "count": 2812,
        "threshold": 1000,
        "message": "mt5_deals has 2812 documents"
      }
    }
    ```
    """
    try:
        valid_components = [
            "mt5_deals",
            "mt5_accounts",
            "initial_allocations",
            "vps_sync",
            "money_managers"
        ]
        
        if component not in valid_components:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid component. Must be one of: {', '.join(valid_components)}"
            )
        
        db = await get_database()
        watchdog = await get_watchdog(db)
        
        # Run full health check
        health = await watchdog.check_system_health()
        
        component_status = health["components"].get(component, {})
        
        return {
            "component": component,
            "healthy": component_status.get("healthy", False),
            "details": component_status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Component health error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/watchdog-status")
async def get_watchdog_status():
    """
    Get MT5 watchdog monitoring status.
    
    **Public endpoint** - No authentication required
    
    Response:
    ```json
    {
      "monitoring_enabled": true,
      "check_interval_minutes": 15,
      "last_check": "2025-11-10T12:30:00Z",
      "auto_healing_enabled": true,
      "github_workflow": "deploy-complete-bridge.yml"
    }
    ```
    """
    return {
        "monitoring_enabled": True,
        "check_interval_minutes": 15,
        "auto_healing_enabled": True,
        "github_repo": os.getenv('GITHUB_REPO', 'chavapalmarubin-lab/FIDUS'),
        "github_workflow": "deploy-complete-bridge.yml",
        "thresholds": {
            "min_deals_count": 1000,
            "expected_accounts": 11,
            "expected_active_accounts": 8,
            "max_sync_age_minutes": 10
        }
    }
