"""
System Testing API Endpoints
Provides manual testing triggers for the MT5 auto-healing system
"""

from fastapi import APIRouter, HTTPException
import logging
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/api/system/test/auto-healing")
async def test_auto_healing():
    """
    Manually trigger auto-healing for testing purposes
    Returns detailed status about the healing attempt
    """
    try:
        logger.info("[TEST] Manual auto-healing trigger requested")
        
        # Import here to avoid circular dependency
        from server import watchdog_instance
        
        if not watchdog_instance:
            raise HTTPException(
                status_code=503, 
                detail="Watchdog not initialized - check server startup"
            )
        
        # Attempt healing
        success = await watchdog_instance.attempt_auto_healing()
        
        result = {
            "status": "success" if success else "failed",
            "message": "Auto-healing test completed",
            "healing_triggered": success,
            "timestamp": datetime.utcnow().isoformat(),
            "consecutive_failures": watchdog_instance.consecutive_failures,
            "healing_in_progress": watchdog_instance.healing_in_progress
        }
        
        logger.info(f"[TEST] Auto-healing test result: {result}")
        return result
        
    except Exception as e:
        logger.error(f"[TEST] Auto-healing test failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/system/test/status")
async def get_test_status():
    """
    Get current system status for testing and monitoring
    Returns watchdog state and system health
    """
    try:
        from server import watchdog_instance
        
        if not watchdog_instance:
            return {
                "watchdog_running": False,
                "message": "Watchdog not initialized",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        return {
            "watchdog_running": True,
            "consecutive_failures": watchdog_instance.consecutive_failures,
            "last_check_time": watchdog_instance.last_check_time.isoformat() if watchdog_instance.last_check_time else None,
            "healing_in_progress": watchdog_instance.healing_in_progress,
            "last_healing_time": watchdog_instance.last_healing_time.isoformat() if watchdog_instance.last_healing_time else None,
            "failure_threshold": watchdog_instance.failure_threshold,
            "check_interval": watchdog_instance.check_interval,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"[TEST] Failed to get test status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/system/test/reset-failures")
async def reset_failure_count():
    """
    Reset the consecutive failure counter for testing
    Useful after manual interventions
    """
    try:
        from server import watchdog_instance
        
        if not watchdog_instance:
            raise HTTPException(status_code=503, detail="Watchdog not initialized")
        
        old_count = watchdog_instance.consecutive_failures
        watchdog_instance.consecutive_failures = 0
        
        logger.info(f"[TEST] Failure counter reset from {old_count} to 0")
        
        return {
            "status": "success",
            "message": "Failure counter reset",
            "old_count": old_count,
            "new_count": 0,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"[TEST] Failed to reset failures: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/system/test/health-check")
async def manual_health_check():
    """
    Manually trigger a health check without waiting for scheduled check
    Returns the current health status
    """
    try:
        from server import watchdog_instance
        
        if not watchdog_instance:
            raise HTTPException(status_code=503, detail="Watchdog not initialized")
        
        logger.info("[TEST] Manual health check triggered")
        
        # Perform immediate health check
        is_healthy = await watchdog_instance.check_mt5_bridge_health()
        
        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "message": "Manual health check completed",
            "mt5_bridge_healthy": is_healthy,
            "consecutive_failures": watchdog_instance.consecutive_failures,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"[TEST] Manual health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
