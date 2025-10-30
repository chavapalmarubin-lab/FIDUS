"""
MT5 Deals History Sync Service
Fetches trade/deals history from MT5 Bridge and syncs to MongoDB for rebates calculation
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
        
        # All 7 managed accounts
        self.managed_accounts = [885822, 886066, 886528, 886557, 886602, 891215, 891234]
        
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
        """Sync deals for a single account"""
        try:
            logger.info(f"🔄 Syncing deals for account {account_number}...")
            
            # Fetch trades from bridge
            trades = await self.fetch_account_trades(account_number, days=90)
            
            if not trades:
                return {
                    "account": account_number,
                    "success": False,
                    "message": "No trades fetched",
                    "deals_synced": 0
                }
            
            # Get account info for metadata
            account_info = self.db.mt5_account_config.find_one({"account_number": account_number})
            
            account_name = "Unknown"
            fund_type = "Unknown"
            
            if account_info:
                account_name = account_info.get('name', 'Unknown')
                fund_type = account_info.get('fund_type', 'Unknown')
            
            deals_synced = 0
            deals_updated = 0
            
            # Process each trade
            for trade in trades:
                # Parse time
                time_str = trade.get('time')
                if isinstance(time_str, str):
                    try:
                        trade_time = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                    except:
                        trade_time = datetime.now(timezone.utc)
                else:
                    trade_time = datetime.now(timezone.utc)
                
                # Prepare deal document
                deal_doc = {
                    "ticket": trade.get('ticket'),
                    "order": trade.get('order'),
                    "time": trade_time,
                    "type": trade.get('type'),  # 0=buy, 1=sell
                    "entry": trade.get('entry'),  # 0=in, 1=out
                    "volume": float(trade.get('volume', 0)),  # Already in lots
                    "price": float(trade.get('price', 0)),
                    "commission": float(trade.get('commission', 0)),
                    "swap": float(trade.get('swap', 0)),
                    "profit": float(trade.get('profit', 0)),
                    "symbol": trade.get('symbol'),
                    "comment": trade.get('comment', ''),
                    "account_number": account_number,
                    "account_name": account_name,
                    "fund_type": fund_type,
                    "synced_at": datetime.now(timezone.utc)
                }
                
                # Upsert to database (update if exists, insert if new)
                self.db.mt5_deals_history.update_one(
                    {"ticket": deal_doc["ticket"], "account_number": account_number},
                    {"$set": deal_doc},
                    upsert=True
                )
                
                deals_synced += 1
            
            logger.info(f"✅ Account {account_number}: {deals_synced} new, {deals_updated} updated")
            
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
