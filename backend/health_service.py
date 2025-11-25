"""
System Health Monitoring Service
Phase 5: Real-time System Health Dashboard
Provides health check endpoints for all system components
"""

import time
import httpx
import os
from datetime import datetime, timezone
from typing import Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorClient

# Component health check functions

async def check_frontend_health() -> Dict[str, Any]:
    """Check frontend availability and response time"""
    start = time.time()
    frontend_url = os.environ.get('REACT_APP_BACKEND_URL', 'https://dashboard-unify.preview.emergentagent.com').replace('/api', '')
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                frontend_url,
                timeout=5.0,
                follow_redirects=True
            )
        response_time = (time.time() - start) * 1000  # Convert to ms
        
        # Determine status based on response time
        if response_time < 1000:
            status = "healthy"
        elif response_time < 3000:
            status = "degraded"
        else:
            status = "slow"
        
        return {
            "component": "frontend",
            "name": "FIDUS Frontend",
            "status": status,
            "response_time": round(response_time, 2),
            "status_code": response.status_code,
            "url": frontend_url,
            "last_check": datetime.now(timezone.utc).isoformat(),
            "message": "Frontend is responding" if status == "healthy" else f"Response time: {round(response_time)}ms"
        }
    except httpx.TimeoutException:
        return {
            "component": "frontend",
            "name": "FIDUS Frontend",
            "status": "timeout",
            "error": "Request timed out after 5 seconds",
            "last_check": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "component": "frontend",
            "name": "FIDUS Frontend",
            "status": "offline",
            "error": str(e),
            "last_check": datetime.now(timezone.utc).isoformat()
        }


async def check_backend_health(db) -> Dict[str, Any]:
    """Check backend API internal health"""
    start = time.time()
    try:
        # Check database connection
        await db.command('ping')
        db_connected = True
        
        response_time = (time.time() - start) * 1000
        
        # Get active connections count
        try:
            stats = await db.command('serverStatus')
            active_connections = stats.get('connections', {}).get('current', 0)
        except:
            active_connections = 0
        
        backend_url = os.environ.get('REACT_APP_BACKEND_URL', 'https://dashboard-unify.preview.emergentagent.com/api')
        
        return {
            "component": "backend",
            "name": "FIDUS Backend API",
            "status": "healthy",
            "response_time": round(response_time, 2),
            "database_connected": db_connected,
            "active_connections": active_connections,
            "url": backend_url,
            "last_check": datetime.now(timezone.utc).isoformat(),
            "message": "All systems operational"
        }
    except Exception as e:
        return {
            "component": "backend",
            "name": "FIDUS Backend API",
            "status": "error",
            "error": str(e),
            "database_connected": False,
            "last_check": datetime.now(timezone.utc).isoformat()
        }


async def check_database_health(db) -> Dict[str, Any]:
    """Check MongoDB connection and performance"""
    start = time.time()
    try:
        # Ping database
        await db.command('ping')
        latency = (time.time() - start) * 1000
        
        # Get database stats
        stats = await db.command('dbStats')
        
        # Count collections
        collections = await db.list_collection_names()
        
        return {
            "component": "database",
            "name": "MongoDB Atlas",
            "status": "healthy" if latency < 100 else "degraded",
            "connection": "established",
            "latency": round(latency, 2),
            "database": db.name,
            "collections_count": len(collections),
            "data_size": stats.get('dataSize', 0),
            "storage_size": stats.get('storageSize', 0),
            "last_check": datetime.now(timezone.utc).isoformat(),
            "message": f"Connected to {db.name}"
        }
    except Exception as e:
        return {
            "component": "database",
            "name": "MongoDB Atlas",
            "status": "offline",
            "connection": "failed",
            "error": str(e),
            "last_check": datetime.now(timezone.utc).isoformat()
        }


async def check_mt5_bridge_health() -> Dict[str, Any]:
    """Check MT5 Bridge VPS service availability"""
    start = time.time()
    vps_url = "http://92.118.45.135:8000"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{vps_url}/api/mt5/bridge/health",  # Correct endpoint
                timeout=5.0
            )
        response_time = (time.time() - start) * 1000
        data = response.json()
        
        return {
            "component": "mt5_bridge",
            "name": "MT5 Bridge Service",
            "status": "healthy" if response.status_code == 200 else "degraded",
            "response_time": round(response_time, 2),
            "vps_ip": "92.118.45.135",
            "accounts_connected": data.get('accounts_connected', 0),
            "last_sync": data.get('last_sync', 'Unknown'),
            "last_check": datetime.now(timezone.utc).isoformat(),
            "message": "VPS bridge operational"
        }
    except httpx.TimeoutException:
        return {
            "component": "mt5_bridge",
            "name": "MT5 Bridge Service",
            "status": "timeout",
            "error": "VPS not responding",
            "vps_ip": "92.118.45.135",
            "last_check": datetime.now(timezone.utc).isoformat(),
            "message": "Unable to reach VPS"
        }
    except Exception as e:
        return {
            "component": "mt5_bridge",
            "name": "MT5 Bridge Service",
            "status": "offline",
            "error": str(e),
            "vps_ip": "92.118.45.135",
            "last_check": datetime.now(timezone.utc).isoformat(),
            "message": "VPS bridge unavailable"
        }


async def check_google_apis_health(db) -> Dict[str, Any]:
    """Check Google Workspace API connection status"""
    try:
        # Check if we have any OAuth tokens
        tokens = await db.google_tokens.find_one({})
        
        if not tokens:
            return {
                "component": "google_apis",
                "name": "Google Workspace APIs",
                "status": "not_configured",
                "connected": False,
                "services": {
                    "gmail": {"status": "not_connected"},
                    "calendar": {"status": "not_connected"},
                    "drive": {"status": "not_connected"}
                },
                "last_check": datetime.now(timezone.utc).isoformat(),
                "message": "Google OAuth not configured"
            }
        
        # Parse expiry time
        expiry_str = tokens.get('expiry')
        token_valid = True
        expires_in_days = None
        
        if expiry_str:
            try:
                if expiry_str.endswith('Z'):
                    expiry_time = datetime.fromisoformat(expiry_str.replace('Z', '+00:00'))
                else:
                    expiry_time = datetime.fromisoformat(expiry_str)
                
                now = datetime.now(timezone.utc)
                if expiry_time.tzinfo is None:
                    expiry_time = expiry_time.replace(tzinfo=timezone.utc)
                
                time_until_expiry = expiry_time - now
                expires_in_days = time_until_expiry.days
                token_valid = expires_in_days > 0
            except:
                pass
        
        status = "healthy" if token_valid else "token_expired"
        
        return {
            "component": "google_apis",
            "name": "Google Workspace APIs",
            "status": status,
            "connected": token_valid,
            "services": {
                "gmail": {"status": "connected" if token_valid else "expired"},
                "calendar": {"status": "connected" if token_valid else "expired"},
                "drive": {"status": "connected" if token_valid else "expired"}
            },
            "token_expires_in_days": expires_in_days,
            "last_check": datetime.now(timezone.utc).isoformat(),
            "message": f"Token valid for {expires_in_days} days" if token_valid and expires_in_days else "OAuth token needs renewal"
        }
    except Exception as e:
        return {
            "component": "google_apis",
            "name": "Google Workspace APIs",
            "status": "error",
            "error": str(e),
            "connected": False,
            "last_check": datetime.now(timezone.utc).isoformat()
        }


async def check_github_health() -> Dict[str, Any]:
    """
    Check GitHub repository status
    Phase 7: Adjusted thresholds for external service (more lenient)
    """
    start = time.time()
    repo_url = "https://api.github.com/repos/chavapalmarubin-lab/FIDUS"
    github_token = os.getenv('GITHUB_TOKEN')
    
    try:
        headers = {'Accept': 'application/vnd.github.v3+json'}
        
        # Add authentication if token available (increases rate limit from 60 to 5000/hour)
        if github_token:
            headers['Authorization'] = f'Bearer {github_token}'
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                repo_url,
                timeout=10.0,  # Increased from 5.0 for external API
                headers=headers
            )
        response_time = (time.time() - start) * 1000
        
        # More lenient thresholds for external service (Phase 7 fix)
        # GitHub is external and naturally slower than internal services
        if response_time < 2000:  # < 2s
            status = "healthy"
        elif response_time < 5000:  # 2-5s
            status = "degraded"
        else:  # > 5s
            status = "slow"
        
        if response.status_code == 200:
            data = response.json()
            rate_limit_remaining = response.headers.get('X-RateLimit-Remaining', 'Unknown')
            rate_limit = response.headers.get('X-RateLimit-Limit', 'Unknown')
            
            return {
                "component": "github",
                "name": "GitHub Repository",
                "status": status,  # Use calculated status based on response time
                "response_time": round(response_time, 2),
                "default_branch": data.get('default_branch', 'main'),
                "last_commit": data.get('pushed_at', 'Unknown'),
                "open_issues": data.get('open_issues_count', 0),
                "repo_size": data.get('size', 0),
                "url": "https://github.com/chavapalmarubin-lab/FIDUS",
                "rate_limit": f"{rate_limit_remaining}/{rate_limit}",
                "last_check": datetime.now(timezone.utc).isoformat(),
                "message": f"Repository accessible ({round(response_time)}ms)" if status == "healthy" else f"Slow response: {round(response_time)}ms"
            }
        elif response.status_code == 403:
            # Rate limit exceeded
            return {
                "component": "github",
                "name": "GitHub Repository",
                "status": "degraded",  # Not critical, just rate limited
                "status_code": response.status_code,
                "last_check": datetime.now(timezone.utc).isoformat(),
                "message": "GitHub API rate limit exceeded (add GITHUB_TOKEN to .env for higher limit)"
            }
        else:
            return {
                "component": "github",
                "name": "GitHub Repository",
                "status": "degraded",  # Not offline, just HTTP error
                "status_code": response.status_code,
                "last_check": datetime.now(timezone.utc).isoformat(),
                "message": f"API returned {response.status_code}"
            }
    except httpx.TimeoutException:
        # GitHub timeout is degraded, not offline (external service)
        return {
            "component": "github",
            "name": "GitHub Repository",
            "status": "degraded",
            "error": "Request timeout",
            "last_check": datetime.now(timezone.utc).isoformat(),
            "message": "GitHub API timeout (external service experiencing delays)"
        }
    except Exception as e:
        # GitHub being unreachable is degraded, not critical (external dependency)
        return {
            "component": "github",
            "name": "GitHub Repository",
            "status": "degraded",
            "error": str(e),
            "last_check": datetime.now(timezone.utc).isoformat(),
            "message": "Unable to reach GitHub API (external service issue)"
        }


async def check_render_platform_health() -> Dict[str, Any]:
    """Check Render platform services status"""
    results = {
        "frontend": "unknown",
        "backend": "unknown"
    }
    
    # Check frontend
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://fidus-investment-platform.onrender.com",
                timeout=5.0,
                follow_redirects=True
            )
        results["frontend"] = "healthy" if response.status_code == 200 else "degraded"
    except:
        results["frontend"] = "offline"
    
    # Check backend
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://fidus-api.onrender.com/api/health",
                timeout=5.0
            )
        results["backend"] = "healthy" if response.status_code == 200 else "degraded"
    except:
        results["backend"] = "offline"
    
    # Determine overall status
    if all(s == "healthy" for s in results.values()):
        overall_status = "healthy"
        message = "All Render services operational"
    elif any(s == "offline" for s in results.values()):
        overall_status = "degraded"
        message = "Some services experiencing issues"
    else:
        overall_status = "degraded"
        message = "Services running with degraded performance"
    
    return {
        "component": "render_platform",
        "name": "Render Hosting Platform",
        "status": overall_status,
        "services": {
            "frontend": results["frontend"],
            "backend": results["backend"]
        },
        "last_check": datetime.now(timezone.utc).isoformat(),
        "message": message,
        "dashboard_url": "https://dashboard.render.com"
    }


async def check_all_components(db, trigger_alerts: bool = True) -> Dict[str, Any]:
    """Run health checks on all components and return aggregated status"""
    
    # Import AlertService
    from alert_service import AlertService
    alert_service = AlertService(db) if trigger_alerts else None
    
    # Run all health checks concurrently
    frontend_health = await check_frontend_health()
    backend_health = await check_backend_health(db)
    database_health = await check_database_health(db)
    mt5_bridge_health = await check_mt5_bridge_health()
    google_apis_health = await check_google_apis_health(db)
    github_health = await check_github_health()
    render_platform_health = await check_render_platform_health()
    
    # Check for alerts if enabled
    if alert_service:
        await alert_service.check_and_alert("frontend", "FIDUS Frontend", frontend_health["status"], frontend_health)
        await alert_service.check_and_alert("backend", "FIDUS Backend API", backend_health["status"], backend_health)
        await alert_service.check_and_alert("database", "MongoDB Atlas", database_health["status"], database_health)
        await alert_service.check_and_alert("mt5_bridge", "MT5 Bridge Service", mt5_bridge_health["status"], mt5_bridge_health)
        await alert_service.check_and_alert("google_apis", "Google Workspace APIs", google_apis_health["status"], google_apis_health)
        await alert_service.check_and_alert("github", "GitHub Repository", github_health["status"], github_health)
        await alert_service.check_and_alert("render_platform", "Render Hosting Platform", render_platform_health["status"], render_platform_health)
    
    components = [
        frontend_health,
        backend_health,
        database_health,
        mt5_bridge_health,
        google_apis_health,
        github_health,
        render_platform_health
    ]
    
    # Calculate overall system status
    statuses = [c['status'] for c in components]
    
    if all(s == "healthy" for s in statuses):
        overall_status = "healthy"
        overall_message = "All systems operational"
    elif any(s in ["offline", "error", "timeout"] for s in statuses):
        overall_status = "critical"
        offline_count = sum(1 for s in statuses if s in ["offline", "error", "timeout"])
        overall_message = f"{offline_count} component(s) offline or in error state"
    elif any(s in ["degraded", "slow"] for s in statuses):
        overall_status = "degraded"
        degraded_count = sum(1 for s in statuses if s in ["degraded", "slow"])
        overall_message = f"{degraded_count} component(s) experiencing degraded performance"
    elif any(s == "not_configured" for s in statuses):
        # Some components not configured but others working - still operational
        configured_count = sum(1 for s in statuses if s != "not_configured")
        if configured_count > 0:
            overall_status = "healthy"  # System works with configured components
            overall_message = f"{configured_count} component(s) operational (some not configured)"
        else:
            overall_status = "unknown"
            overall_message = "No components configured"
    else:
        overall_status = "unknown"
        overall_message = f"System status unknown - unexpected statuses: {set(statuses)}"
    
    # Calculate statistics
    healthy_count = sum(1 for s in statuses if s == "healthy")
    total_count = len(components)
    health_percentage = round((healthy_count / total_count) * 100, 1)
    
    return {
        "overall_status": overall_status,
        "overall_message": overall_message,
        "health_percentage": health_percentage,
        "healthy_count": healthy_count,
        "total_count": total_count,
        "components": components,
        "last_check": datetime.now(timezone.utc).isoformat(),
        "timestamp": datetime.now(timezone.utc).timestamp()
    }


async def store_health_history(db, health_data: Dict[str, Any]) -> None:
    """Store health check results in MongoDB for historical tracking"""
    try:
        await db.system_health_history.insert_one({
            "timestamp": datetime.now(timezone.utc),
            "overall_status": health_data["overall_status"],
            "health_percentage": health_data["health_percentage"],
            "components": health_data["components"],
            "created_at": datetime.now(timezone.utc)
        })
        
        # Keep only last 24 hours of history (clean up old records)
        twenty_four_hours_ago = datetime.now(timezone.utc).timestamp() - (24 * 60 * 60)
        await db.system_health_history.delete_many({
            "timestamp": {"$lt": datetime.fromtimestamp(twenty_four_hours_ago, tz=timezone.utc)}
        })
    except Exception as e:
        print(f"Error storing health history: {str(e)}")


async def calculate_uptime_percentage(db, component: str, hours: int = 24) -> float:
    """Calculate uptime percentage for a component over specified hours"""
    try:
        cutoff_time = datetime.now(timezone.utc).timestamp() - (hours * 60 * 60)
        
        # Get all health checks for this component in the time period
        history = await db.system_health_history.find({
            "timestamp": {"$gte": datetime.fromtimestamp(cutoff_time, tz=timezone.utc)}
        }).to_list(length=None)
        
        if not history:
            return 0.0
        
        # Count healthy checks
        healthy_count = 0
        total_count = len(history)
        
        for record in history:
            for comp in record.get('components', []):
                if comp['component'] == component and comp['status'] == 'healthy':
                    healthy_count += 1
                    break
        
        return round((healthy_count / total_count) * 100, 1) if total_count > 0 else 0.0
    except Exception as e:
        print(f"Error calculating uptime: {str(e)}")
        return 0.0
