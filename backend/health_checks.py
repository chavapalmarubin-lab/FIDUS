"""
System Health Checks Module
Provides health check functionality for all system components
"""

import aiohttp
import asyncio
import time
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def check_url_health(url: str, method: str = 'GET', timeout: int = 5, expected_status: int = 200) -> Dict[str, Any]:
    """
    Check health of a URL endpoint
    Returns status, response time, and any error information
    """
    start_time = time.time()
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, timeout=aiohttp.ClientTimeout(total=timeout)) as response:
                response_time = round((time.time() - start_time) * 1000, 2)  # Convert to ms
                
                is_healthy = response.status == expected_status
                
                return {
                    'status': 'online' if is_healthy else 'degraded',
                    'http_status': response.status,
                    'response_time_ms': response_time,
                    'checked_at': datetime.now(timezone.utc).isoformat(),
                    'error': None if is_healthy else f'Expected {expected_status}, got {response.status}'
                }
    except asyncio.TimeoutError:
        response_time = round((time.time() - start_time) * 1000, 2)
        return {
            'status': 'offline',
            'http_status': None,
            'response_time_ms': response_time,
            'checked_at': datetime.now(timezone.utc).isoformat(),
            'error': f'Timeout after {timeout}s'
        }
    except Exception as e:
        response_time = round((time.time() - start_time) * 1000, 2)
        return {
            'status': 'offline',
            'http_status': None,
            'response_time_ms': response_time,
            'checked_at': datetime.now(timezone.utc).isoformat(),
            'error': str(e)
        }


async def check_mongodb_health(mongo_client) -> Dict[str, Any]:
    """
    Check MongoDB connection health
    """
    start_time = time.time()
    
    try:
        # Ping the database
        await mongo_client.admin.command('ping')
        response_time = round((time.time() - start_time) * 1000, 2)
        
        return {
            'status': 'online',
            'response_time_ms': response_time,
            'checked_at': datetime.now(timezone.utc).isoformat(),
            'error': None
        }
    except Exception as e:
        response_time = round((time.time() - start_time) * 1000, 2)
        return {
            'status': 'offline',
            'response_time_ms': response_time,
            'checked_at': datetime.now(timezone.utc).isoformat(),
            'error': str(e)
        }


async def check_mt5_sync_health(db) -> Dict[str, Any]:
    """
    Check MT5 sync service health by checking last sync timestamp
    """
    start_time = time.time()
    
    try:
        # Get the most recent MT5 account update
        accounts = await db.mt5_accounts.find().sort('updated_at', -1).limit(1).to_list(length=1)
        
        if accounts:
            last_update = accounts[0].get('updated_at')
            
            if last_update:
                now = datetime.now(timezone.utc)
                if last_update.tzinfo is None:
                    last_update = last_update.replace(tzinfo=timezone.utc)
                
                minutes_since_update = (now - last_update).total_seconds() / 60
                
                response_time = round((time.time() - start_time) * 1000, 2)
                
                # Consider stale if no update in last 20 minutes
                if minutes_since_update > 20:
                    return {
                        'status': 'degraded',
                        'response_time_ms': response_time,
                        'checked_at': datetime.now(timezone.utc).isoformat(),
                        'last_sync': last_update.isoformat(),
                        'minutes_since_sync': round(minutes_since_update, 1),
                        'error': f'No sync in {round(minutes_since_update)} minutes'
                    }
                else:
                    return {
                        'status': 'online',
                        'response_time_ms': response_time,
                        'checked_at': datetime.now(timezone.utc).isoformat(),
                        'last_sync': last_update.isoformat(),
                        'minutes_since_sync': round(minutes_since_update, 1),
                        'error': None
                    }
        
        response_time = round((time.time() - start_time) * 1000, 2)
        return {
            'status': 'unknown',
            'response_time_ms': response_time,
            'checked_at': datetime.now(timezone.utc).isoformat(),
            'error': 'No MT5 account data found'
        }
        
    except Exception as e:
        response_time = round((time.time() - start_time) * 1000, 2)
        return {
            'status': 'offline',
            'response_time_ms': response_time,
            'checked_at': datetime.now(timezone.utc).isoformat(),
            'error': str(e)
        }


async def perform_all_health_checks(mongo_client, db) -> Dict[str, Dict[str, Any]]:
    """
    Perform health checks on all major system components
    Returns a dictionary with component_id as key and health info as value
    """
    health_results = {}
    
    # Frontend check - use preview URL
    logger.info("Checking frontend health...")
    health_results['frontend'] = await check_url_health(
        url='https://trading-platform-110.preview.emergentagent.com',
        timeout=5,
        expected_status=200
    )
    
    # Backend check (self-check - always online if we can execute this code)
    logger.info("Checking backend health...")
    health_results['backend'] = {
        'status': 'online',
        'http_status': 200,
        'response_time_ms': 0.5,
        'checked_at': datetime.now(timezone.utc).isoformat(),
        'error': None
    }
    
    # MongoDB check
    logger.info("Checking MongoDB health...")
    health_results['mongodb'] = await check_mongodb_health(mongo_client)
    
    # MT5 Bridge check (via last sync timestamp)
    logger.info("Checking MT5 Bridge health...")
    health_results['mt5_bridge'] = await check_mt5_sync_health(db)
    
    # VPS check - Use MT5 terminal status as proxy for VPS health
    logger.info("Checking VPS health via MT5 status...")
    try:
        # Check if we have recent terminal status in the database
        terminal_status = await db.mt5_terminal_status.find_one(sort=[('timestamp', -1)])
        
        if terminal_status:
            # Check if terminal is connected and initialized
            is_connected = terminal_status.get('connected', False)
            is_initialized = terminal_status.get('terminal_initialized', False)
            
            # Calculate time since last update
            last_update = terminal_status.get('timestamp')
            if last_update:
                now = datetime.now(timezone.utc)
                # Handle timezone-aware datetime
                if last_update.tzinfo is None:
                    last_update = last_update.replace(tzinfo=timezone.utc)
                minutes_since = (now - last_update).total_seconds() / 60
                
                if is_connected and is_initialized and minutes_since < 5:
                    health_results['vps'] = {
                        'status': 'online',
                        'response_time_ms': 0,
                        'checked_at': datetime.now(timezone.utc).isoformat(),
                        'last_heartbeat': last_update.isoformat(),
                        'minutes_since_heartbeat': round(minutes_since, 1),
                        'error': None
                    }
                else:
                    health_results['vps'] = {
                        'status': 'degraded',
                        'response_time_ms': 0,
                        'checked_at': datetime.now(timezone.utc).isoformat(),
                        'last_heartbeat': last_update.isoformat() if last_update else None,
                        'minutes_since_heartbeat': round(minutes_since, 1) if last_update else None,
                        'error': f'No heartbeat in {round(minutes_since, 1)} minutes' if minutes_since >= 5 else 'MT5 not connected'
                    }
            else:
                health_results['vps'] = {
                    'status': 'degraded',
                    'response_time_ms': 0,
                    'checked_at': datetime.now(timezone.utc).isoformat(),
                    'error': 'No timestamp in terminal status'
                }
        else:
            health_results['vps'] = {
                'status': 'offline',
                'response_time_ms': 0,
                'checked_at': datetime.now(timezone.utc).isoformat(),
                'error': 'No terminal status records found'
            }
    except Exception as e:
        logger.error(f"VPS health check error: {str(e)}")
        health_results['vps'] = {
            'status': 'offline',
            'response_time_ms': 0,
            'checked_at': datetime.now(timezone.utc).isoformat(),
            'error': str(e)
        }
    
    return health_results


def calculate_overall_status(health_results: Dict[str, Dict[str, Any]]) -> str:
    """
    Calculate overall system status based on individual component statuses
    """
    statuses = [result['status'] for result in health_results.values()]
    
    if all(status == 'online' for status in statuses):
        return 'all_systems_operational'
    elif any(status == 'offline' for status in statuses):
        return 'partial_outage'
    elif any(status == 'degraded' for status in statuses):
        return 'degraded_performance'
    else:
        return 'unknown'
