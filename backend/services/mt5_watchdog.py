"""
MT5 Auto-Healing Watchdog Service
Updated: November 10, 2025

Monitors MT5 data pipeline health and triggers auto-healing when issues detected.
Compliant with MT5 Field Standardization Mandate (November 2025).
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
import httpx
import os

logger = logging.getLogger(__name__)

class MT5Watchdog:
    """
    Monitors MT5 system health and triggers auto-healing.
    
    Updated November 2025 to monitor:
    - mt5_deals collection (not mt5_deals_history)
    - Initial allocation integrity
    - Money manager data quality
    - VPS sync freshness
    """
    
    def __init__(self, db, github_token: str = None, repo: str = None):
        self.db = db
        self.github_token = github_token or os.getenv('GITHUB_TOKEN')
        self.repo = repo or os.getenv('GITHUB_REPO', 'chavapalmarubin-lab/FIDUS')
        self.check_interval = 900  # 15 minutes
        
        # Health thresholds
        self.min_deals_count = 1000
        self.expected_accounts = 11
        self.expected_active_accounts = 8
        self.max_sync_age_minutes = 10
        self.expected_total_allocation = 138805.17
        
    async def start_monitoring(self):
        """Start continuous health monitoring"""
        logger.info("🔍 MT5 Watchdog started - Monitoring every 15 minutes")
        
        while True:
            try:
                await self.check_system_health()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"❌ Watchdog error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    async def check_system_health(self) -> Dict:
        """
        Comprehensive system health check.
        Updated to check mt5_deals collection and initial allocations.
        """
        logger.info("🔍 Running system health check...")
        
        health_status = {
            "timestamp": datetime.now(timezone.utc),
            "overall_healthy": True,
            "components": {}
        }
        
        # Check 1: MT5 Deals Collection
        deals_health = await self.check_deals_collection()
        health_status["components"]["mt5_deals"] = deals_health
        if not deals_health["healthy"]:
            health_status["overall_healthy"] = False
        
        # Check 2: MT5 Accounts Collection
        accounts_health = await self.check_accounts_collection()
        health_status["components"]["mt5_accounts"] = accounts_health
        if not accounts_health["healthy"]:
            health_status["overall_healthy"] = False
        
        # Check 3: Initial Allocations
        allocations_health = await self.check_initial_allocations()
        health_status["components"]["initial_allocations"] = allocations_health
        if not allocations_health["healthy"]:
            health_status["overall_healthy"] = False
        
        # Check 4: VPS Sync Status
        sync_health = await self.check_vps_sync_status()
        health_status["components"]["vps_sync"] = sync_health
        if not sync_health["healthy"]:
            health_status["overall_healthy"] = False
        
        # Check 5: Money Manager Data
        managers_health = await self.check_money_managers()
        health_status["components"]["money_managers"] = managers_health
        if not managers_health["healthy"]:
            health_status["overall_healthy"] = False
        
        # Log results
        if health_status["overall_healthy"]:
            logger.info("✅ System health check PASSED - All components healthy")
        else:
            logger.warning(f"⚠️ System health check FAILED - Issues detected")
            logger.warning(f"Health status: {health_status}")
            
            # Trigger auto-healing
            await self.trigger_auto_healing(health_status)
        
        return health_status
    
    async def check_deals_collection(self) -> Dict:
        """Check mt5_deals collection health"""
        try:
            # Count documents
            count = await self.db.mt5_deals.count_documents({})
            
            # Check if collection has substantial data
            healthy = count >= self.min_deals_count
            
            # Get sample document to verify field names
            sample = await self.db.mt5_deals.find_one({})
            has_correct_field = 'account' in sample if sample else False
            has_wrong_field = 'account_number' in sample if sample else False
            
            field_healthy = has_correct_field and not has_wrong_field
            healthy = healthy and field_healthy
            
            status = {
                "healthy": healthy,
                "count": count,
                "threshold": self.min_deals_count,
                "correct_field_names": field_healthy,
                "message": f"mt5_deals has {count} documents"
            }
            
            if not healthy:
                issues = []
                if count < self.min_deals_count:
                    issues.append(f"Deal count ({count}) below threshold ({self.min_deals_count})")
                if not field_healthy:
                    issues.append(f"Incorrect field names detected")
                status["issues"] = issues
                logger.error(f"🚨 mt5_deals issues: {issues}")
            
            return status
            
        except Exception as e:
            logger.error(f"❌ Error checking mt5_deals: {e}")
            return {
                "healthy": False,
                "error": str(e),
                "message": "Failed to check mt5_deals collection"
            }
    
    async def check_accounts_collection(self) -> Dict:
        """Check mt5_accounts collection health"""
        try:
            # Count total accounts
            total_count = await self.db.mt5_account_config.count_documents({})
            
            # Count active accounts
            active_count = await self.db.mt5_account_config.count_documents({
                "is_active": True
            })
            
            # Check expectations
            total_healthy = total_count == self.expected_accounts
            active_healthy = active_count == self.expected_active_accounts
            healthy = total_healthy and active_healthy
            
            status = {
                "healthy": healthy,
                "total_accounts": total_count,
                "active_accounts": active_count,
                "expected_total": self.expected_accounts,
                "expected_active": self.expected_active_accounts,
                "message": f"{active_count}/{total_count} accounts active"
            }
            
            if not healthy:
                issues = []
                if not total_healthy:
                    issues.append(f"Expected {self.expected_accounts} total accounts, found {total_count}")
                if not active_healthy:
                    issues.append(f"Expected {self.expected_active_accounts} active accounts, found {active_count}")
                status["issues"] = issues
                logger.warning(f"⚠️ Account health issues: {issues}")
            
            return status
            
        except Exception as e:
            logger.error(f"❌ Error checking mt5_accounts: {e}")
            return {
                "healthy": False,
                "error": str(e),
                "message": "Failed to check mt5_accounts collection"
            }
    
    async def check_initial_allocations(self) -> Dict:
        """Check that all active accounts have initial allocations set"""
        try:
            # Get active accounts without initial allocation
            missing = await self.db.mt5_account_config.count_documents({
                "is_active": True,
                "initial_allocation": {"$exists": False}
            })
            
            # Get active accounts with zero allocation
            zero_allocation = await self.db.mt5_account_config.count_documents({
                "is_active": True,
                "initial_allocation": 0
            })
            
            # Calculate total allocation
            pipeline = [
                {"$match": {"is_active": True}},
                {"$group": {
                    "_id": None,
                    "total": {"$sum": "$initial_allocation"}
                }}
            ]
            result = await self.db.mt5_account_config.aggregate(pipeline).to_list(1)
            total_allocation = result[0]["total"] if result else 0
            
            # Check against expected total
            allocation_accurate = abs(total_allocation - self.expected_total_allocation) < 10  # Allow $10 variance
            
            healthy = missing == 0 and zero_allocation == 0 and total_allocation > 0 and allocation_accurate
            
            status = {
                "healthy": healthy,
                "missing_allocation": missing,
                "zero_allocation": zero_allocation,
                "total_allocation": total_allocation,
                "expected_total": self.expected_total_allocation,
                "message": f"Total allocation: ${total_allocation:.2f}"
            }
            
            if not healthy:
                issues = []
                if missing > 0:
                    issues.append(f"{missing} active accounts missing initial_allocation")
                if zero_allocation > 0:
                    issues.append(f"{zero_allocation} active accounts have zero allocation")
                if total_allocation == 0:
                    issues.append("Total allocation is zero")
                if not allocation_accurate:
                    issues.append(f"Total allocation (${total_allocation:.2f}) doesn't match expected (${self.expected_total_allocation:.2f})")
                status["issues"] = issues
                logger.error(f"🚨 Initial allocation issues: {issues}")
            
            return status
            
        except Exception as e:
            logger.error(f"❌ Error checking initial allocations: {e}")
            return {
                "healthy": False,
                "error": str(e),
                "message": "Failed to check initial allocations"
            }
    
    async def check_vps_sync_status(self) -> Dict:
        """Check VPS sync recency"""
        try:
            # Get most recently synced deal (more reliable than accounts)
            recent = await self.db.mt5_deals.find_one(
                sort=[("synced_at", -1)]
            )
            
            if not recent:
                return {
                    "healthy": False,
                    "message": "No accounts found in database"
                }
            
            last_sync = recent.get("updated_at")
            if not last_sync:
                return {
                    "healthy": False,
                    "message": "No sync timestamp found"
                }
            
            # Calculate age
            age = datetime.now(timezone.utc) - last_sync
            age_minutes = age.total_seconds() / 60
            
            healthy = age_minutes < self.max_sync_age_minutes
            
            status = {
                "healthy": healthy,
                "last_sync": last_sync,
                "age_minutes": age_minutes,
                "threshold_minutes": self.max_sync_age_minutes,
                "message": f"Last sync {age_minutes:.1f} minutes ago"
            }
            
            if not healthy:
                status["issue"] = f"Sync age ({age_minutes:.1f} min) exceeds threshold ({self.max_sync_age_minutes} min)"
                logger.error(f"🚨 {status['issue']}")
            
            return status
            
        except Exception as e:
            logger.error(f"❌ Error checking VPS sync: {e}")
            return {
                "healthy": False,
                "error": str(e),
                "message": "Failed to check VPS sync status"
            }
    
    async def check_money_managers(self) -> Dict:
        """Check money manager data quality"""
        try:
            # Get active accounts
            active_accounts = await self.db.mt5_account_config.find({
                "is_active": True
            }).to_list(None)
            
            # Check each has manager_name
            missing_manager = [
                acc["account"] for acc in active_accounts 
                if not acc.get("money_manager_name")
            ]
            
            # Check each has manager_profile
            missing_profile = [
                acc["account"] for acc in active_accounts 
                if not acc.get("money_manager_url")
            ]
            
            # Count unique managers
            managers = set(
                acc.get("money_manager_name") 
                for acc in active_accounts 
                if acc.get("money_manager_name")
            )
            
            healthy = len(missing_manager) == 0 and len(managers) >= 5
            
            status = {
                "healthy": healthy,
                "total_managers": len(managers),
                "expected_managers": 5,
                "missing_manager_name": len(missing_manager),
                "missing_manager_profile": len(missing_profile),
                "message": f"{len(managers)} managers configured"
            }
            
            if not healthy:
                issues = []
                if missing_manager:
                    issues.append(f"Accounts missing manager_name: {missing_manager}")
                if len(managers) < 5:
                    issues.append(f"Only {len(managers)} managers found, expected 5")
                status["issues"] = issues
                logger.warning(f"⚠️ Money manager issues: {issues}")
            
            return status
            
        except Exception as e:
            logger.error(f"❌ Error checking money managers: {e}")
            return {
                "healthy": False,
                "error": str(e),
                "message": "Failed to check money managers"
            }
    
    async def trigger_auto_healing(self, health_status: Dict):
        """
        Trigger auto-healing via GitHub Actions.
        Updated to use correct workflow and parameters.
        """
        logger.warning("🔧 Triggering auto-healing...")
        
        # Determine healing action based on issues
        failing_components = [
            name for name, status in health_status["components"].items()
            if not status["healthy"]
        ]
        
        reason = f"Auto-healing triggered: {', '.join(failing_components)}"
        
        try:
            # Trigger GitHub Actions workflow
            url = f"https://api.github.com/repos/{self.repo}/actions/workflows/deploy-complete-bridge.yml/dispatches"
            
            headers = {
                "Authorization": f"Bearer {self.github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            data = {
                "ref": "main",
                "inputs": {
                    "reason": reason
                }
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=data)
                
                if response.status_code == 204:
                    logger.info("✅ Auto-healing triggered successfully")
                    
                    # Send notification (optional)
                    await self.send_healing_notification(reason, True)
                    
                    return True
                else:
                    logger.error(f"❌ Failed to trigger auto-healing: {response.status_code}")
                    logger.error(f"Response: {response.text}")
                    
                    # Send failure notification
                    await self.send_healing_notification(reason, False)
                    
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Error triggering auto-healing: {e}")
            await self.send_healing_notification(reason, False)
            return False
    
    async def send_healing_notification(self, reason: str, success: bool):
        """Send notification about healing attempt"""
        # TODO: Implement email/Slack notification
        if success:
            logger.info(f"📧 Notification: Auto-healing triggered - {reason}")
        else:
            logger.error(f"📧 Notification: Auto-healing FAILED - {reason}")


# Singleton instance
_watchdog_instance = None

async def get_watchdog(db) -> MT5Watchdog:
    """Get or create MT5 watchdog singleton"""
    global _watchdog_instance
    if _watchdog_instance is None:
        _watchdog_instance = MT5Watchdog(db)
    return _watchdog_instance
