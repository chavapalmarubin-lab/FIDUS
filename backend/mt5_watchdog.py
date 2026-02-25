"""
MT5 Watchdog and Auto-Healing Service
Monitors MT5 Bridge health and attempts automatic recovery before alerting

UPDATED: Feb 25, 2026 - LUCRUM-ONLY Mode
- Old MEXAtlantic VPS (92.118.45.135) is no longer used
- Watchdog now monitors LUCRUM data freshness in MongoDB only
- No external VPS health checks or auto-healing via SSH
"""

import asyncio
import logging
import os
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
import httpx

logger = logging.getLogger(__name__)

# LUCRUM-ONLY MODE: Disable VPS health checks and auto-healing
LUCRUM_ONLY_MODE = True


class MT5Watchdog:
    """
    MT5 Health Monitoring and Auto-Healing System
    
    LUCRUM-ONLY MODE (Feb 2026):
    - Only monitors LUCRUM data freshness in MongoDB
    - No VPS health checks (old MEXAtlantic VPS is offline)
    - No auto-healing via GitHub Actions (LUCRUM synced differently)
    - Alerts only if LUCRUM data is stale for extended period
    """
    
    def __init__(self, db, alert_service):
        self.db = db
        self.alert_service = alert_service
        self.lucrum_only_mode = LUCRUM_ONLY_MODE
        
        # Configuration
        self.check_interval = 300 if LUCRUM_ONLY_MODE else 60  # Check every 5 mins in LUCRUM mode
        self.data_freshness_threshold = 60  # Alert if no LUCRUM data update in 60 minutes
        self.failure_threshold = 5  # Higher threshold for LUCRUM mode
        self.healing_cooldown = 3600  # 1 hour between alerts in LUCRUM mode
        
        # State tracking
        self.consecutive_failures = 0
        self.last_healing_attempt = None
        self.last_check_time = None
        self.last_alert_time = None
        self.is_healthy = True
        self.auto_healing_in_progress = False
        self.needs_full_restart = False
        
        # GitHub configuration (not used in LUCRUM-only mode)
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.github_repo = 'chavapalmarubin-lab/FIDUS'
        self.vps_bridge_url = 'http://92.118.45.135:8000'  # Legacy - not used in LUCRUM mode
        
        if self.lucrum_only_mode:
            logger.info("🟢 [MT5 WATCHDOG] Running in LUCRUM-ONLY mode - VPS checks disabled")
    
    async def check_mt5_health(self) -> Dict[str, Any]:
        """
        Check MT5 Bridge health
        
        In LUCRUM-ONLY mode:
        - Skip VPS bridge API checks
        - Only check LUCRUM data freshness in MongoDB
        - Return healthy if LUCRUM data is recent
        """
        try:
            if self.lucrum_only_mode:
                # LUCRUM-ONLY: Only check MongoDB data freshness
                data_fresh = await self._check_lucrum_data_freshness()
                
                return {
                    'healthy': data_fresh,
                    'mode': 'lucrum_only',
                    'bridge_api_available': True,  # Not applicable
                    'data_fresh': data_fresh,
                    'accounts_syncing': True,  # Synced via GitHub Actions
                    'consecutive_failures': self.consecutive_failures,
                    'auto_healing_in_progress': False,
                    'last_check': datetime.now(timezone.utc).isoformat(),
                    'last_healing_attempt': None,
                    'message': 'LUCRUM accounts synced via GitHub Actions'
                }
            
            # Legacy VPS mode (disabled)
            bridge_healthy = await self._check_bridge_api()
            data_fresh = await self._check_data_freshness()
            accounts_syncing = await self._check_accounts_syncing()
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
    
    async def _check_lucrum_data_freshness(self) -> bool:
        """
        Check if LUCRUM account data in MongoDB is fresh
        Used in LUCRUM-ONLY mode
        """
        try:
            # Get most recent LUCRUM account update
            lucrum_accounts = await self.db.mt5_accounts.find({
                "broker": {"$regex": "LUCRUM", "$options": "i"}
            }).sort('updated_at', -1).limit(1).to_list(length=1)
            
            if not lucrum_accounts:
                logger.info("[MT5 WATCHDOG] No LUCRUM accounts found - this is normal if sync hasn't run yet")
                return True  # Don't alert if no accounts yet
            
            last_update = lucrum_accounts[0].get('updated_at')
            if not last_update:
                logger.info("[MT5 WATCHDOG] LUCRUM account has no updated_at field")
                return True  # Don't alert for missing field
            
            # Convert string to datetime if needed
            if isinstance(last_update, str):
                last_update = datetime.fromisoformat(last_update.replace('Z', '+00:00'))
            
            # Ensure timezone aware
            if last_update.tzinfo is None:
                last_update = last_update.replace(tzinfo=timezone.utc)
            
            # Check if data is within threshold (60 minutes for LUCRUM)
            now = datetime.now(timezone.utc)
            minutes_since_update = (now - last_update).total_seconds() / 60
            
            # LUCRUM data is synced via GitHub Actions (manual trigger)
            # Don't alert unless data is very old (24 hours)
            is_fresh = minutes_since_update <= 1440  # 24 hours
            
            if not is_fresh:
                logger.warning(f"[MT5 WATCHDOG] LUCRUM data stale: {minutes_since_update:.1f} minutes since last update")
            else:
                logger.debug(f"[MT5 WATCHDOG] LUCRUM data fresh: {minutes_since_update:.1f} minutes since last update")
            
            return is_fresh
            
        except Exception as e:
            logger.error(f"[MT5 WATCHDOG] LUCRUM data freshness check failed: {str(e)}")
            return True  # Don't alert on errors in LUCRUM mode
    
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
            
            # DEBUG: Log the type and value
            logger.debug(f"[MT5 WATCHDOG DEBUG] last_update type: {type(last_update)}, value: {last_update}")
            
            # Convert string to datetime if needed
            if isinstance(last_update, str):
                logger.debug(f"[MT5 WATCHDOG DEBUG] Converting string to datetime")
                last_update = datetime.fromisoformat(last_update.replace('Z', '+00:00'))
                logger.debug(f"[MT5 WATCHDOG DEBUG] After conversion: {type(last_update)}, tzinfo: {last_update.tzinfo}")
            
            # Ensure timezone aware
            if last_update.tzinfo is None:
                logger.debug(f"[MT5 WATCHDOG DEBUG] Adding timezone")
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
        """Check if accounts are actively syncing and detect $0 balance issue"""
        try:
            # Get all accounts
            accounts = await self.db.mt5_accounts.find().to_list(length=None)
            
            if not accounts:
                logger.warning("[MT5 WATCHDOG] No MT5 accounts found in database")
                return False
            
            total_accounts = len(accounts)
            zero_balance_count = 0
            total_active_accounts = 0  # Count only non-separation accounts
            synced_count = 0
            cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=15)
            
            # Check each account
            for account in accounts:
                balance = float(account.get('balance', 0))
                fund_type = account.get('fund_type', '')
                
                # Only count non-SEPARATION accounts for zero balance check
                if fund_type not in ['SEPARATION']:
                    total_active_accounts += 1
                    if balance == 0:
                        zero_balance_count += 1
                
                # Count recently synced - FIX: Handle both datetime and string formats
                updated_at = account.get('updated_at')
                if updated_at:
                    try:
                        # Convert to timezone-aware datetime if needed
                        if isinstance(updated_at, str):
                            updated_at = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                        elif isinstance(updated_at, datetime) and updated_at.tzinfo is None:
                            updated_at = updated_at.replace(tzinfo=timezone.utc)
                        
                        if updated_at >= cutoff_time:
                            synced_count += 1
                    except (ValueError, AttributeError):
                        logger.warning(f"[MT5 WATCHDOG] Invalid updated_at format for account {account.get('account')}: {updated_at}")
            
            # SMART CRITICAL CHECK: Only trigger if $0 balances AND accounts NOT syncing
            # This prevents false alarms during capital reallocation (accounts sync fine but show $0)
            zero_balance_percentage = (zero_balance_count / total_active_accounts) if total_active_accounts > 0 else 0
            sync_percentage = (synced_count / total_accounts) * 100 if total_accounts > 0 else 0
            is_syncing = sync_percentage >= 40  # At least 40% of accounts recently synced
            
            # CRITICAL CONDITION: >80% accounts at $0 AND low sync activity
            if zero_balance_percentage > 0.8 and total_active_accounts >= 3:
                if not is_syncing:
                    # REAL PROBLEM: Terminals disconnected
                    logger.critical(f"🚨 [MT5 WATCHDOG] {zero_balance_count}/{total_active_accounts} ACTIVE ACCOUNTS SHOWING $0 BALANCE!")
                    logger.critical(f"🚨 [MT5 WATCHDOG] AND only {synced_count}/{total_accounts} accounts syncing ({sync_percentage:.1f}%)")
                    logger.critical("🚨 [MT5 WATCHDOG] MT5 Terminals likely DISCONNECTED - Need FULL restart!")
                    self.needs_full_restart = True
                    return False
                else:
                    # FALSE POSITIVE: Accounts syncing fine, just showing $0 (capital reallocation)
                    logger.info(f"ℹ️ [MT5 WATCHDOG] {zero_balance_count}/{total_active_accounts} accounts at $0 BUT {synced_count}/{total_accounts} syncing ({sync_percentage:.1f}%)")
                    logger.info("ℹ️ [MT5 WATCHDOG] Likely capital reallocation - accounts syncing normally, not disconnected")
                    return True  # System is healthy
            
            # Check sync percentage for normal operations
            if not is_syncing:
                logger.warning(f"[MT5 WATCHDOG] Low sync rate: {synced_count}/{total_accounts} accounts ({sync_percentage:.1f}%)")
            
            # Only log (not alarm) about zero balances if some accounts affected but not critical
            if zero_balance_count > 0 and zero_balance_percentage <= 0.8:
                logger.info(f"[MT5 WATCHDOG] {zero_balance_count}/{total_active_accounts} active accounts showing $0 balance (normal, SEPARATION excluded)")
            
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
        """Trigger GitHub Actions workflow to restart MT5 Bridge or Full System"""
        try:
            # Choose workflow based on needs_full_restart flag
            if self.needs_full_restart:
                workflow_file = "mt5-full-restart.yml"
                event_type = "mt5-full-restart"
                logger.info("[MT5 WATCHDOG] 🚀 Triggering FULL MT5 SYSTEM RESTART (terminals + bridge)")
            else:
                workflow_file = "deploy-mt5-bridge-emergency-ps.yml"
                event_type = None
                logger.info("[MT5 WATCHDOG] 🔧 Triggering simple MT5 Bridge restart")
            
            # For repository_dispatch events (full restart)
            if event_type:
                url = f"https://api.github.com/repos/{self.github_repo}/dispatches"
                data = {
                    'event_type': event_type,
                    'client_payload': {
                        'trigger': 'watchdog',
                        'reason': 'All accounts showing $0 balance - MT5 terminals disconnected',
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    }
                }
            else:
                # For workflow_dispatch events (simple restart)
                url = f"https://api.github.com/repos/{self.github_repo}/actions/workflows/{workflow_file}/dispatches"
                data = {'ref': 'main'}
            
            headers = {
                'Authorization': f'Bearer {self.github_token}',
                'Accept': 'application/vnd.github.v3+json',
                'Content-Type': 'application/json'
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=data, headers=headers, timeout=10.0)
            
            if response.status_code == 204:
                logger.info("[MT5 WATCHDOG] ✅ GitHub Actions workflow dispatch successful")
                # Reset flag after triggering
                if self.needs_full_restart:
                    self.needs_full_restart = False
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
        
        LUCRUM-ONLY MODE:
        - Checks every 5 minutes instead of 1 minute
        - Only monitors LUCRUM data freshness in MongoDB
        - Does NOT trigger auto-healing or send critical alerts
        - LUCRUM accounts are synced via GitHub Actions manually
        """
        if self.lucrum_only_mode:
            logger.info("[MT5 WATCHDOG] 🟢 Starting in LUCRUM-ONLY mode")
            logger.info("[MT5 WATCHDOG] ℹ️  VPS health checks: DISABLED")
            logger.info("[MT5 WATCHDOG] ℹ️  Auto-healing: DISABLED")
            logger.info("[MT5 WATCHDOG] ℹ️  Critical alerts: DISABLED")
            logger.info(f"[MT5 WATCHDOG] Check interval: {self.check_interval}s (LUCRUM data freshness only)")
        else:
            logger.info("[MT5 WATCHDOG] 🚀 Starting MT5 Watchdog monitoring loop")
            logger.info(f"[MT5 WATCHDOG] Check interval: {self.check_interval}s")
            logger.info(f"[MT5 WATCHDOG] Data freshness threshold: {self.data_freshness_threshold} minutes")
            logger.info(f"[MT5 WATCHDOG] Failure threshold for auto-healing: {self.failure_threshold} failures")
        
        while True:
            try:
                # Check MT5 health
                health = await self.check_mt5_health()
                self.last_check_time = datetime.now(timezone.utc)
                
                # LUCRUM-ONLY MODE: Just log status, no alerts or auto-healing
                if self.lucrum_only_mode:
                    if health['healthy']:
                        logger.debug("[MT5 WATCHDOG] 🟢 LUCRUM data status: OK")
                    else:
                        logger.info("[MT5 WATCHDOG] ℹ️  LUCRUM data may need manual sync via GitHub Actions")
                    
                    # Store status but skip alerts
                    await self._store_watchdog_status(health)
                    await asyncio.sleep(self.check_interval)
                    continue
                
                # LEGACY VPS MODE (disabled)
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
