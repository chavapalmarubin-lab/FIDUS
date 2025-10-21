"""
MT5 Watchdog and Auto-Healing Service
Monitors MT5 Bridge health and attempts automatic recovery before alerting
"""

import asyncio
import logging
import os
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
import httpx

logger = logging.getLogger(__name__)


class MT5Watchdog:
    """
    MT5 Health Monitoring and Auto-Healing System
    
    Features:
    - Monitors MT5 data freshness every minute
    - Tracks consecutive failures
    - Attempts auto-healing after 3 consecutive failures
    - Sends alerts only if auto-healing fails
    """
    
    def __init__(self, db, alert_service):
        self.db = db
        self.alert_service = alert_service
        
        # Configuration
        self.check_interval = 60  # Check every 60 seconds
        self.data_freshness_threshold = 15  # Alert if no data in 15 minutes
        self.failure_threshold = 3  # Attempt healing after 3 failures
        self.healing_cooldown = 300  # 5 minutes between healing attempts
        
        # State tracking
        self.consecutive_failures = 0
        self.last_healing_attempt = None
        self.last_check_time = None
        self.last_alert_time = None
        self.is_healthy = True
        self.auto_healing_in_progress = False
        
        # GitHub configuration for auto-healing
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.github_repo = 'chavapalmarubin-lab/FIDUS'  # Updated repo name
        self.vps_bridge_url = 'http://92.118.45.135:8000'
    
    async def check_mt5_health(self) -> Dict[str, Any]:
        """
        Check MT5 Bridge health
        Returns health status and details
        """
        try:
            # Check 1: VPS Bridge API availability
            bridge_healthy = await self._check_bridge_api()
            
            # Check 2: Data freshness in MongoDB
            data_fresh = await self._check_data_freshness()
            
            # Check 3: Account sync status
            accounts_syncing = await self._check_accounts_syncing()
            
            # Determine overall health
            is_healthy = bridge_healthy and data_fresh and accounts_syncing
            
            return {
                'healthy': is_healthy,
                'bridge_api_available': bridge_healthy,
                'data_fresh': data_fresh,
                'accounts_syncing': accounts_syncing,
                'consecutive_failures': self.consecutive_failures,
                'auto_healing_in_progress': self.auto_healing_in_progress,
                'last_check': datetime.now(timezone.utc).isoformat(),
                'last_healing_attempt': self.last_healing_attempt.isoformat() if self.last_healing_attempt else None
            }
            
        except Exception as e:
            logger.error(f"[MT5 WATCHDOG] Error checking health: {str(e)}")
            return {
                'healthy': False,
                'error': str(e),
                'consecutive_failures': self.consecutive_failures
            }
    
    async def _check_bridge_api(self) -> bool:
        """Check if MT5 Bridge API is responding"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.vps_bridge_url}/api/mt5/bridge/health",
                    timeout=5.0
                )
                return response.status_code == 200
        except Exception as e:
            logger.warning(f"[MT5 WATCHDOG] Bridge API check failed: {str(e)}")
            return False
    
    async def _check_data_freshness(self) -> bool:
        """Check if MT5 data in MongoDB is fresh"""
        try:
            # Get most recent MT5 account update
            accounts = await self.db.mt5_accounts.find().sort('updated_at', -1).limit(1).to_list(length=1)
            
            if not accounts:
                logger.warning("[MT5 WATCHDOG] No MT5 accounts found in database")
                return False
            
            last_update = accounts[0].get('updated_at')
            if not last_update:
                return False
            
            # Ensure timezone aware
            if last_update.tzinfo is None:
                last_update = last_update.replace(tzinfo=timezone.utc)
            
            # Check if data is within threshold
            now = datetime.now(timezone.utc)
            minutes_since_update = (now - last_update).total_seconds() / 60
            
            is_fresh = minutes_since_update <= self.data_freshness_threshold
            
            if not is_fresh:
                logger.warning(f"[MT5 WATCHDOG] Data stale: {minutes_since_update:.1f} minutes since last update")
            
            return is_fresh
            
        except Exception as e:
            logger.error(f"[MT5 WATCHDOG] Data freshness check failed: {str(e)}")
            return False
    
    async def _check_accounts_syncing(self) -> bool:
        """Check if accounts are actively syncing"""
        try:
            # Count total accounts
            total_accounts = await self.db.mt5_accounts.count_documents({})
            
            # Count recently updated accounts (within last 15 minutes)
            cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=15)
            recent_updates = await self.db.mt5_accounts.count_documents({
                'updated_at': {'$gte': cutoff_time}
            })
            
            # Consider healthy if at least 50% of accounts synced recently
            if total_accounts == 0:
                return False
            
            sync_percentage = (recent_updates / total_accounts) * 100
            is_syncing = sync_percentage >= 50
            
            if not is_syncing:
                logger.warning(f"[MT5 WATCHDOG] Low sync rate: {recent_updates}/{total_accounts} accounts ({sync_percentage:.1f}%)")
            
            return is_syncing
            
        except Exception as e:
            logger.error(f"[MT5 WATCHDOG] Account sync check failed: {str(e)}")
            return False
    
    async def attempt_auto_healing(self) -> bool:
        """
        Attempt to automatically heal MT5 Bridge
        Returns True if healing was successful, False otherwise
        """
        if not self.github_token:
            logger.error("[MT5 WATCHDOG] Cannot auto-heal: GITHUB_TOKEN not configured")
            return False
        
        # Check cooldown
        if self.last_healing_attempt:
            time_since_last_attempt = (datetime.now(timezone.utc) - self.last_healing_attempt).total_seconds()
            if time_since_last_attempt < self.healing_cooldown:
                logger.info(f"[MT5 WATCHDOG] Healing cooldown active: {self.healing_cooldown - time_since_last_attempt:.0f}s remaining")
                return False
        
        try:
            self.auto_healing_in_progress = True
            self.last_healing_attempt = datetime.now(timezone.utc)
            
            logger.info("[MT5 WATCHDOG] 🔧 Attempting auto-healing: Triggering MT5 Bridge restart via GitHub Actions")
            
            # Trigger GitHub Actions workflow to restart MT5 Bridge
            success = await self._trigger_github_workflow()
            
            if success:
                logger.info("[MT5 WATCHDOG] ✅ Auto-healing workflow triggered successfully")
                
                # Wait for service to restart (30 seconds)
                logger.info("[MT5 WATCHDOG] ⏳ Waiting 30 seconds for service restart...")
                await asyncio.sleep(30)
                
                # Verify healing worked
                health = await self.check_mt5_health()
                
                if health['healthy']:
                    logger.info("[MT5 WATCHDOG] ✅ AUTO-HEALING SUCCESSFUL! MT5 Bridge recovered")
                    
                    # Send recovery notification
                    await self.alert_service.trigger_alert(
                        component="mt5_bridge",
                        component_name="MT5 Bridge Service",
                        severity="info",
                        status="RECOVERED",
                        message="MT5 Bridge automatically recovered via auto-healing",
                        details={
                            'healing_method': 'GitHub Actions workflow restart',
                            'downtime_duration': f'{self.consecutive_failures} minutes',
                            'recovery_time': datetime.now(timezone.utc).isoformat(),
                            'consecutive_failures_before_healing': self.consecutive_failures
                        }
                    )
                    
                    # Reset failure counter
                    self.consecutive_failures = 0
                    self.is_healthy = True
                    return True
                else:
                    logger.error("[MT5 WATCHDOG] ❌ Auto-healing failed: Service still unhealthy after restart")
                    return False
            else:
                logger.error("[MT5 WATCHDOG] ❌ Failed to trigger auto-healing workflow")
                return False
                
        except Exception as e:
            logger.error(f"[MT5 WATCHDOG] ❌ Auto-healing error: {str(e)}")
            return False
        finally:
            self.auto_healing_in_progress = False
    
    async def _trigger_github_workflow(self) -> bool:
        """Trigger GitHub Actions workflow to restart MT5 Bridge"""
        try:
            url = f"https://api.github.com/repos/{self.github_repo}/actions/workflows/deploy-mt5-bridge-emergency-ps.yml/dispatches"  # Use PowerShell version for better Windows compatibility
            
            headers = {
                'Authorization': f'Bearer {self.github_token}',
                'Accept': 'application/vnd.github.v3+json',
                'Content-Type': 'application/json'
            }
            
            data = {
                'ref': 'main'
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=data, headers=headers, timeout=10.0)
            
            if response.status_code == 204:
                logger.info("[MT5 WATCHDOG] ✅ GitHub Actions workflow dispatch successful")
                return True
            else:
                logger.error(f"[MT5 WATCHDOG] ❌ GitHub Actions dispatch failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"[MT5 WATCHDOG] ❌ Error triggering GitHub workflow: {str(e)}")
            return False
    
    async def monitor_loop(self):
        """
        Main monitoring loop
        Runs continuously and checks MT5 health
        """
        logger.info("[MT5 WATCHDOG] 🚀 Starting MT5 Watchdog monitoring loop")
        logger.info(f"[MT5 WATCHDOG] Check interval: {self.check_interval}s")
        logger.info(f"[MT5 WATCHDOG] Data freshness threshold: {self.data_freshness_threshold} minutes")
        logger.info(f"[MT5 WATCHDOG] Failure threshold for auto-healing: {self.failure_threshold} failures")
        
        while True:
            try:
                # Check MT5 health
                health = await self.check_mt5_health()
                self.last_check_time = datetime.now(timezone.utc)
                
                if health['healthy']:
                    # System is healthy
                    if not self.is_healthy:
                        # Just recovered
                        logger.info("[MT5 WATCHDOG] ✅ MT5 Bridge recovered (naturally or via auto-healing)")
                    
                    self.consecutive_failures = 0
                    self.is_healthy = True
                    
                else:
                    # System is unhealthy
                    self.consecutive_failures += 1
                    self.is_healthy = False
                    
                    logger.warning(f"[MT5 WATCHDOG] ⚠️ MT5 Bridge unhealthy - Consecutive failures: {self.consecutive_failures}/{self.failure_threshold}")
                    
                    # Attempt auto-healing if threshold reached
                    if self.consecutive_failures >= self.failure_threshold:
                        logger.warning(f"[MT5 WATCHDOG] 🔧 Failure threshold reached ({self.failure_threshold}), attempting auto-healing...")
                        
                        healing_successful = await self.attempt_auto_healing()
                        
                        if not healing_successful:
                            # Auto-healing failed - send critical alert
                            logger.error("[MT5 WATCHDOG] 🚨 AUTO-HEALING FAILED - Sending critical alert to admin")
                            
                            # Only send alert if we haven't sent one in the last 30 minutes
                            should_alert = True
                            if self.last_alert_time:
                                time_since_alert = (datetime.now(timezone.utc) - self.last_alert_time).total_seconds()
                                should_alert = time_since_alert >= 1800  # 30 minutes
                            
                            if should_alert:
                                await self.alert_service.trigger_alert(
                                    component="mt5_bridge",
                                    component_name="MT5 Bridge Service",
                                    severity="critical",
                                    status="OFFLINE - AUTO-HEALING FAILED",
                                    message="MT5 Bridge is offline and automatic recovery failed. Manual intervention required!",
                                    details={
                                        'consecutive_failures': self.consecutive_failures,
                                        'auto_healing_attempted': True,
                                        'auto_healing_result': 'FAILED',
                                        'last_healing_attempt': self.last_healing_attempt.isoformat() if self.last_healing_attempt else None,
                                        'action_required': 'Manual VPS access required to diagnose and fix the issue',
                                        'vps_ip': '92.118.45.135',
                                        'health_details': health
                                    }
                                )
                                self.last_alert_time = datetime.now(timezone.utc)
                
                # Store watchdog status in database
                await self._store_watchdog_status(health)
                
            except Exception as e:
                logger.error(f"[MT5 WATCHDOG] Error in monitoring loop: {str(e)}")
            
            # Wait before next check
            await asyncio.sleep(self.check_interval)
    
    async def _store_watchdog_status(self, health: Dict[str, Any]):
        """Store watchdog status in MongoDB for dashboard display"""
        try:
            status = {
                'timestamp': datetime.now(timezone.utc),
                'healthy': health['healthy'],
                'consecutive_failures': self.consecutive_failures,
                'auto_healing_in_progress': self.auto_healing_in_progress,
                'last_healing_attempt': self.last_healing_attempt,
                'health_details': health,
                'updated_at': datetime.now(timezone.utc)
            }
            
            # Upsert watchdog status
            await self.db.mt5_watchdog_status.replace_one(
                {'_id': 'current'},
                {**status, '_id': 'current'},
                upsert=True
            )
            
        except Exception as e:
            logger.error(f"[MT5 WATCHDOG] Error storing status: {str(e)}")
    
    async def force_sync_now(self) -> Dict[str, Any]:
        """Force an immediate MT5 sync"""
        try:
            logger.info("[MT5 WATCHDOG] 🔄 Force sync requested")
            
            # Trigger GitHub workflow
            success = await self._trigger_github_workflow()
            
            if success:
                return {
                    'success': True,
                    'message': 'MT5 sync triggered successfully',
                    'triggered_at': datetime.now(timezone.utc).isoformat()
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to trigger MT5 sync workflow'
                }
                
        except Exception as e:
            logger.error(f"[MT5 WATCHDOG] Error forcing sync: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


# Global watchdog instance (initialized in server.py startup)
watchdog_instance: Optional[MT5Watchdog] = None


async def initialize_watchdog(db, alert_service):
    """Initialize and start the MT5 Watchdog"""
    global watchdog_instance
    
    try:
        logger.info("[MT5 WATCHDOG] Initializing MT5 Watchdog and Auto-Healing System...")
        
        watchdog_instance = MT5Watchdog(db, alert_service)
        
        # Start monitoring loop in background
        asyncio.create_task(watchdog_instance.monitor_loop())
        
        logger.info("[MT5 WATCHDOG] ✅ MT5 Watchdog initialized and monitoring started")
        
        return watchdog_instance
        
    except Exception as e:
        logger.error(f"[MT5 WATCHDOG] ❌ Failed to initialize watchdog: {str(e)}")
        raise


def get_watchdog() -> Optional[MT5Watchdog]:
    """Get the global watchdog instance"""
    return watchdog_instance
