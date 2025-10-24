"""
VPS MT5 Bridge Sync Service
Fetches live MT5 data from VPS Bridge and updates MongoDB
Critical fix for stale data issue (Oct 24, 2025)
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any
import httpx
import os

logger = logging.getLogger(__name__)

class VPSSyncService:
    """Service to sync MT5 data from VPS Bridge to MongoDB"""
    
    def __init__(self, db):
        self.db = db
        self.bridge_url = os.getenv('MT5_BRIDGE_URL', 'http://92.118.45.135:8000')
        self.timeout = int(os.getenv('MT5_BRIDGE_TIMEOUT', '30'))
        logger.info(f"🔗 VPS Sync Service initialized with URL: {self.bridge_url}")
    
    async def fetch_from_vps(self, endpoint: str) -> Dict[str, Any]:
        """
        Fetch data from VPS MT5 Bridge API
        
        Args:
            endpoint: API endpoint (e.g., '/api/mt5/accounts/summary')
        
        Returns:
            Response data as dict
        """
        url = f"{self.bridge_url}{endpoint}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"❌ VPS API error {response.status_code}: {response.text}")
                    return {"error": f"HTTP {response.status_code}"}
        
        except Exception as e:
            logger.error(f"❌ Error calling VPS Bridge: {str(e)}")
            return {"error": str(e)}
    
    async def sync_all_accounts(self) -> Dict[str, Any]:
        """
        Sync all MT5 accounts from VPS to MongoDB
        Uses individual account endpoints to get LIVE data (not cached MongoDB data)
        
        Returns:
            Sync results with statistics
        """
        try:
            logger.info("🔄 Starting VPS→MongoDB sync for all accounts")
            start_time = datetime.now(timezone.utc)
            
            # First, get the list of accounts from summary (just to know which accounts exist)
            summary_result = await self.fetch_from_vps('/api/mt5/accounts/summary')
            
            if 'error' in summary_result:
                logger.error(f"❌ Failed to fetch account list from VPS: {summary_result['error']}")
                return {
                    "success": False,
                    "error": summary_result['error'],
                    "accounts_synced": 0,
                    "timestamp": start_time.isoformat()
                }
            
            accounts_list = summary_result.get('accounts', [])
            
            if not accounts_list:
                logger.warning("⚠️  No accounts returned from VPS")
                return {
                    "success": False,
                    "error": "No accounts returned from VPS",
                    "accounts_synced": 0,
                    "timestamp": start_time.isoformat()
                }
            
            # Fetch LIVE data for each account individually
            accounts_synced = 0
            failed_accounts = []
            
            for account_info in accounts_list:
                account_id = account_info.get('account')
                
                if not account_id:
                    logger.warning(f"⚠️  Skipping account with no ID: {account_info}")
                    continue
                
                try:
                    # Fetch live data from VPS for this specific account
                    account_result = await self.fetch_from_vps(f'/api/mt5/account/{account_id}/info')
                    
                    if 'error' in account_result:
                        logger.error(f"❌ Failed to fetch account {account_id}: {account_result['error']}")
                        failed_accounts.append(account_id)
                        continue
                    
                    # Get live data (not cached MongoDB data)
                    live_data = account_result.get('live_data', {})
                    
                    if not live_data:
                        logger.warning(f"⚠️  No live data for account {account_id}, using stored data")
                        # Fallback to stored data if live data not available
                        stored_data = account_result.get('stored_data', {})
                        balance = stored_data.get('balance', account_info.get('balance', 0))
                        equity = stored_data.get('equity', account_info.get('equity', 0))
                        profit = stored_data.get('profit', account_info.get('profit', 0))
                    else:
                        # Use LIVE data from MT5
                        balance = live_data.get('balance', 0)
                        equity = live_data.get('equity', 0)
                        profit = live_data.get('profit', 0)
                    
                    # Update MongoDB with LIVE data
                    update_result = await self.db.mt5_accounts.update_one(
                        {'account': account_id},
                        {
                            '$set': {
                                'balance': balance,
                                'equity': equity,
                                'profit': profit,
                                'margin': live_data.get('margin'),
                                'margin_free': live_data.get('margin_free'),
                                'margin_level': live_data.get('margin_level'),
                                'leverage': live_data.get('leverage'),
                                'currency': live_data.get('currency', 'USD'),
                                'trade_allowed': live_data.get('trade_allowed'),
                                'updated_at': start_time,
                                'synced_from_vps': True,
                                'vps_sync_timestamp': start_time,
                                'data_source': 'VPS_LIVE_MT5' if live_data else 'VPS_STORED'
                            }
                        },
                        upsert=False  # Don't create new accounts, only update existing
                    )
                    
                    if update_result.modified_count > 0 or update_result.matched_count > 0:
                        accounts_synced += 1
                        logger.info(f"✅ Synced account {account_id}: ${balance:,.2f} (live: {bool(live_data)})")
                    else:
                        logger.warning(f"⚠️  Account {account_id} not found in database")
                        failed_accounts.append(account_id)
                
                except Exception as e:
                    logger.error(f"❌ Error syncing account {account_id}: {str(e)}")
                    failed_accounts.append(account_id)
            
            duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            logger.info(f"✅ VPS sync complete: {accounts_synced}/{len(accounts_list)} accounts synced in {duration:.2f}s")
            if failed_accounts:
                logger.warning(f"⚠️  Failed accounts: {failed_accounts}")
            
            return {
                "success": True,
                "accounts_synced": accounts_synced,
                "total_accounts": len(accounts_list),
                "failed_accounts": failed_accounts,
                "duration_seconds": duration,
                "timestamp": start_time.isoformat(),
                "vps_url": self.bridge_url
            }
        
        except Exception as e:
            logger.error(f"❌ VPS sync error: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "accounts_synced": 0,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def sync_single_account(self, account_id: int) -> Dict[str, Any]:
        """
        Sync a single MT5 account from VPS
        
        Args:
            account_id: MT5 account number
        
        Returns:
            Sync result
        """
        try:
            logger.info(f"🔄 Syncing single account {account_id} from VPS")
            
            # Fetch account info from VPS
            result = await self.fetch_from_vps(f'/api/mt5/account/{account_id}/info')
            
            if 'error' in result:
                logger.error(f"❌ Failed to fetch account {account_id}: {result['error']}")
                return {
                    "success": False,
                    "account_id": account_id,
                    "error": result['error']
                }
            
            # Extract live data
            live_data = result.get('live_data', {})
            
            if not live_data:
                logger.warning(f"⚠️  No live data for account {account_id}")
                return {
                    "success": False,
                    "account_id": account_id,
                    "error": "No live data available"
                }
            
            # Update MongoDB
            update_time = datetime.now(timezone.utc)
            update_result = await self.db.mt5_accounts.update_one(
                {'account': account_id},
                {
                    '$set': {
                        'balance': live_data.get('balance', 0),
                        'equity': live_data.get('equity', 0),
                        'profit': live_data.get('profit', 0),
                        'margin': live_data.get('margin'),
                        'margin_free': live_data.get('margin_free'),
                        'margin_level': live_data.get('margin_level'),
                        'leverage': live_data.get('leverage'),
                        'currency': live_data.get('currency', 'USD'),
                        'trade_allowed': live_data.get('trade_allowed'),
                        'updated_at': update_time,
                        'synced_from_vps': True,
                        'vps_sync_timestamp': update_time
                    }
                }
            )
            
            if update_result.modified_count > 0 or update_result.matched_count > 0:
                logger.info(f"✅ Synced account {account_id}: ${live_data.get('balance', 0):,.2f}")
                return {
                    "success": True,
                    "account_id": account_id,
                    "balance": live_data.get('balance', 0),
                    "equity": live_data.get('equity', 0),
                    "profit": live_data.get('profit', 0),
                    "updated_at": update_time.isoformat()
                }
            else:
                logger.warning(f"⚠️  Account {account_id} not found in database")
                return {
                    "success": False,
                    "account_id": account_id,
                    "error": "Account not found in database"
                }
        
        except Exception as e:
            logger.error(f"❌ Error syncing account {account_id}: {str(e)}", exc_info=True)
            return {
                "success": False,
                "account_id": account_id,
                "error": str(e)
            }
    
    async def check_vps_health(self) -> Dict[str, Any]:
        """
        Check if VPS MT5 Bridge is healthy
        
        Returns:
            Health check result
        """
        try:
            result = await self.fetch_from_vps('/api/mt5/bridge/health')
            
            if 'error' in result:
                return {
                    "healthy": False,
                    "error": result['error']
                }
            
            is_healthy = result.get('status') == 'healthy'
            
            return {
                "healthy": is_healthy,
                "status": result.get('status'),
                "mt5_available": result.get('mt5', {}).get('available'),
                "mongodb_connected": result.get('mongodb', {}).get('connected'),
                "timestamp": result.get('timestamp')
            }
        
        except Exception as e:
            logger.error(f"❌ Health check error: {str(e)}")
            return {
                "healthy": False,
                "error": str(e)
            }


# Singleton instance
_vps_sync_service = None

async def get_vps_sync_service(db):
    """Get or create VPS sync service singleton"""
    global _vps_sync_service
    if _vps_sync_service is None:
        _vps_sync_service = VPSSyncService(db)
    return _vps_sync_service
