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
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://fidus-investment-platform.onrender.com",
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
            "url": "https://fidus-investment-platform.onrender.com",
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
        
        return {
            "component": "backend",
            "name": "FIDUS Backend API",
            "status": "healthy",
            "response_time": round(response_time, 2),
            "database_connected": db_connected,
            "active_connections": active_connections,
            "url": "https://fidus-api.onrender.com",
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
    vps_url = "http://217.197.163.11:8000"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{vps_url}/health",
                timeout=5.0
            )
        response_time = (time.time() - start) * 1000
        data = response.json()
        
        return {
            "component": "mt5_bridge",
            "name": "MT5 Bridge Service",
            "status": "healthy" if response.status_code == 200 else "degraded",
            "response_time": round(response_time, 2),
            "vps_ip": "217.197.163.11",
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
            "vps_ip": "217.197.163.11",
            "last_check": datetime.now(timezone.utc).isoformat(),
            "message": "Unable to reach VPS"
        }
    except Exception as e:
        return {
            "component": "mt5_bridge",
            "name": "MT5 Bridge Service",
            "status": "offline",
            "error": str(e),
            "vps_ip": "217.197.163.11",
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
    """Check GitHub repository status"""
    start = time.time()
    repo_url = "https://api.github.com/repos/chavapalmarubin/fidus-platform"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                repo_url,
                timeout=5.0,
                headers={'Accept': 'application/vnd.github.v3+json'}
            )
        response_time = (time.time() - start) * 1000
        
        if response.status_code == 200:
            data = response.json()
            
            return {
                "component": "github",
                "name": "GitHub Repository",
                "status": "healthy",
                "response_time": round(response_time, 2),
                "default_branch": data.get('default_branch', 'main'),
                "last_commit": data.get('pushed_at', 'Unknown'),
                "open_issues": data.get('open_issues_count', 0),
                "repo_size": data.get('size', 0),
                "url": "https://github.com/chavapalmarubin/fidus-platform",
                "last_check": datetime.now(timezone.utc).isoformat(),
                "message": "Repository accessible"
            }
        else:
            return {
                "component": "github",
                "name": "GitHub Repository",
                "status": "degraded",
                "status_code": response.status_code,
                "last_check": datetime.now(timezone.utc).isoformat(),
                "message": f"API returned {response.status_code}"
            }
    except Exception as e:
        return {
            "component": "github",
            "name": "GitHub Repository",
            "status": "error",
            "error": str(e),
            "last_check": datetime.now(timezone.utc).isoformat()
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


async def check_all_components(db) -> Dict[str, Any]:
    """Run health checks on all components and return aggregated status"""
    
    # Run all health checks concurrently
    frontend_health = await check_frontend_health()
    backend_health = await check_backend_health(db)
    database_health = await check_database_health(db)
    mt5_bridge_health = await check_mt5_bridge_health()
    google_apis_health = await check_google_apis_health(db)
    github_health = await check_github_health()
    render_platform_health = await check_render_platform_health()
    
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
    else:
        overall_status = "unknown"
        overall_message = "System status unknown"
    
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
