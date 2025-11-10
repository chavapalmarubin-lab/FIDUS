"""
MT5 Deals History Sync Service
Fetches trade/deals history from MT5 Bridge and syncs to MongoDB for rebates calculation

UPDATED: Nov 3, 2025 - MT5 Field Standardization Compliance
- Changed collection from mt5_deals_history to mt5_deals
- Using exact MT5 Python API field names (snake_case)
- Removed FIDUS-specific fields from core MT5 data
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
import aiohttp
import os

logger = logging.getLogger(__name__)

class MT5DealsSyncService:
    """Service to sync MT5 deals/trades history from bridge to MongoDB"""
    
    def __init__(self):
        self.bridge_url = os.environ.get('MT5_BRIDGE_URL', 'http://92.118.45.135:8000')
        self.session = None
        self.db = None
        
        # All 11 managed accounts (updated for new month allocation)
        self.managed_accounts = [885822, 886066, 886528, 886557, 886602, 891215, 891234, 897590, 897589, 897591, 897599]
        
    async def initialize(self, db):
        """Initialize with database connection"""
        self.db = db
        
        # Setup HTTP session
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        )
        
        logger.info("✅ MT5 Deals Sync Service initialized")
        
    async def fetch_account_trades(self, account_number: int, days: int = 30) -> List[Dict]:
        """Fetch trade history for an account from MT5 Bridge"""
        try:
            url = f"{self.bridge_url}/api/mt5/account/{account_number}/trades?limit=10000"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('success'):
                        trades = data.get('trades', [])
                        logger.info(f"✅ Fetched {len(trades)} trades for account {account_number}")
                        return trades
                    else:
                        logger.warning(f"⚠️ Failed to get trades for {account_number}: {data}")
                        return []
                else:
                    logger.error(f"❌ HTTP {response.status} for account {account_number}")
                    return []
                    
        except Exception as e:
            logger.error(f"❌ Error fetching trades for {account_number}: {e}")
            return []
    
    async def sync_account_deals(self, account_number: int) -> Dict:
        """
        Sync deals for a single account
        UPDATED: Nov 3, 2025 - MT5 Field Standardization Compliance
        """
        try:
            logger.info(f"🔄 Syncing deals for account {account_number}...")
            logger.info(f"📝 Target collection: mt5_deals")
            
            # Fetch trades from bridge
            trades = await self.fetch_account_trades(account_number, days=90)
            
            if not trades:
                return {
                    "account": account_number,
                    "success": False,
                    "message": "No trades fetched",
                    "deals_synced": 0
                }
            
            # Get account info for FIDUS metadata
            account_info = await self.db.mt5_account_config.find_one({"account_number": account_number})
            
            account_name = "Unknown"
            fund_type = "Unknown"
            
            if account_info:
                account_name = account_info.get('name', 'Unknown')
                fund_type = account_info.get('fund_type', 'Unknown')
            
            deals_synced = 0
            deals_updated = 0
            
            # Process each trade
            for trade in trades:
                # Parse time from Unix timestamp or ISO string
                time_value = trade.get('time')
                if isinstance(time_value, int):
                    # Unix timestamp
                    trade_time = datetime.fromtimestamp(time_value, tz=timezone.utc)
                elif isinstance(time_value, str):
                    try:
                        trade_time = datetime.fromisoformat(time_value.replace('Z', '+00:00'))
                    except:
                        trade_time = datetime.now(timezone.utc)
                else:
                    trade_time = datetime.now(timezone.utc)
                
                # Prepare deal document with EXACT MT5 Python API field names
                # Following MT5 Field Standardization Mandate
                deal_doc = {
                    # Core MT5 deal fields (from VPS API)
                    "ticket": trade.get('ticket'),
                    "order": trade.get('order'),
                    "time": trade_time,
                    "type": trade.get('type'),  # 0=buy, 1=sell, 2=balance
                    "entry": trade.get('entry'),  # 0=in, 1=out
                    "symbol": trade.get('symbol'),
                    "volume": float(trade.get('volume', 0)),  # Volume in lots
                    "price": float(trade.get('price', 0)),
                    "profit": float(trade.get('profit', 0)),
                    "comment": trade.get('comment', ''),
                    
                    # MT5 fields not provided by VPS API (set to None for honesty)
                    "time_msc": None,      # VPS doesn't provide milliseconds
                    "commission": None,    # VPS doesn't provide commission
                    "swap": None,          # VPS doesn't provide swap
                    "fee": None,           # VPS doesn't provide fee
                    "external_id": None,   # VPS doesn't provide external_id
                    "position_id": None,   # VPS doesn't provide position_id
                    "magic": None,         # VPS doesn't provide magic number
                    "reason": None,        # VPS doesn't provide reason
                    
                    # FIDUS-specific metadata (added AFTER MT5 fields)
                    "account": account_number,           # MT5 account login number
                    "account_name": account_name,        # Human-readable name
                    "fund_type": fund_type,              # CORE/BALANCE/DYNAMIC/UNLIMITED
                    "synced_at": datetime.now(timezone.utc),  # When synced
                    "synced_by": "mt5_deals_sync_service"   # Service identifier
                }
                
                # Upsert to database (update if exists, insert if new)
                # CORRECTED: Using mt5_deals collection (not mt5_deals_history)
                result = await self.db.mt5_deals.update_one(
                    {"ticket": deal_doc["ticket"], "account": account_number},
                    {"$set": deal_doc},
                    upsert=True
                )
                
                if result.upserted_id:
                    deals_synced += 1
                elif result.modified_count > 0:
                    deals_updated += 1
            
            logger.info(f"✅ Account {account_number}: {deals_synced} new, {deals_updated} updated in mt5_deals collection")
            
            return {
                "account": account_number,
                "success": True,
                "deals_synced": deals_synced,
                "deals_updated": deals_updated,
                "total_processed": len(trades)
            }
            
        except Exception as e:
            logger.error(f"❌ Error syncing account {account_number}: {e}")
            return {
                "account": account_number,
                "success": False,
                "error": str(e),
                "deals_synced": 0
            }
    
    async def sync_all_accounts(self) -> Dict:
        """Sync deals for all managed accounts"""
        logger.info("=" * 60)
        logger.info("🚀 STARTING MT5 DEALS HISTORY SYNC FOR ALL ACCOUNTS")
        logger.info("📝 Target collection: mt5_deals")
        logger.info("=" * 60)
        
        start_time = datetime.now()
        results = []
        
        for account_number in self.managed_accounts:
            result = await self.sync_account_deals(account_number)
            results.append(result)
            
            # Small delay between accounts
            await asyncio.sleep(1)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        total_synced = sum(r.get('deals_synced', 0) for r in results)
        total_updated = sum(r.get('deals_updated', 0) for r in results)
        successful = sum(1 for r in results if r.get('success'))
        
        summary = {
            "success": True,
            "accounts_processed": len(results),
            "accounts_successful": successful,
            "total_deals_synced": total_synced,
            "total_deals_updated": total_updated,
            "duration_seconds": round(duration, 2),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "results": results
        }
        
        logger.info("=" * 60)
        logger.info(f"✅ SYNC COMPLETE: {total_synced} new, {total_updated} updated in {duration:.2f}s")
        logger.info("=" * 60)
        
        return summary
    
    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()

# Global instance
mt5_deals_sync = MT5DealsSyncService()
