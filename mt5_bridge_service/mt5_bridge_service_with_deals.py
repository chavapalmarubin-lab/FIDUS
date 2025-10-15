"""
MT5 Bridge Service - Deal History Collection (Phase 4A)
Syncs MT5 account data + deal history to MongoDB

DEPLOYMENT LOCATION: C:\mt5_bridge_service\mt5_bridge_service_with_deals.py
Python Version: 3.12
Pymongo Version: 4.x compatible

PHASE 4A ENHANCEMENTS:
- Collects deal history using mt5.history_deals_get()
- 90-day initial backfill on first run
- Daily incremental sync (last 24 hours)
- Stores in mt5_deals_history collection
- Unlocks: Trading Analytics, Cash Flow, Rebates, Manager Performance
"""

import MetaTrader5 as mt5
from pymongo import MongoClient, UpdateOne, ASCENDING, DESCENDING
from datetime import datetime, timezone, timedelta
import time
import os
from dotenv import load_dotenv
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('C:\\mt5_bridge_service\\mt5_bridge_with_deals.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# MongoDB Configuration
MONGODB_URI = os.getenv('MONGODB_URI')
if not MONGODB_URI:
    logger.error("❌ MONGODB_URI not found in .env file")
    sys.exit(1)

# MT5 Configuration
MT5_PATH = os.getenv('MT5_PATH', 'C:\\Program Files\\MEX Atlantic MT5 Terminal\\terminal64.exe')
UPDATE_INTERVAL = int(os.getenv('UPDATE_INTERVAL', '300'))  # 5 minutes
DEAL_SYNC_INTERVAL = int(os.getenv('DEAL_SYNC_INTERVAL', '86400'))  # 24 hours (daily)
INITIAL_BACKFILL_DAYS = int(os.getenv('INITIAL_BACKFILL_DAYS', '90'))  # 90 days

# Hardcoded fallback accounts (if MongoDB query fails)
FALLBACK_ACCOUNTS = [
    {"account": 886557, "password": "Fidus13@", "name": "Main Balance Account", "fund_type": "BALANCE", "target_amount": 100000.0},
    {"account": 886066, "password": "Fidus13@", "name": "Secondary Balance Account", "fund_type": "BALANCE", "target_amount": 210000.0},
    {"account": 886602, "password": "Fidus13@", "name": "Tertiary Balance Account", "fund_type": "BALANCE", "target_amount": 50000.0},
    {"account": 885822, "password": "Fidus13@", "name": "Core Account", "fund_type": "CORE", "target_amount": 128151.41},
    {"account": 886528, "password": "Fidus13@", "name": "Separation Account", "fund_type": "SEPARATION", "target_amount": 10000.0},
    {"account": 891215, "password": "Fidus13@", "name": "Interest Earnings Trading", "fund_type": "SEPARATION", "target_amount": 10000.0},
    {"account": 891234, "password": "Fidus13@", "name": "CORE Fund", "fund_type": "CORE", "target_amount": 10000.0}
]

class MT5BridgeWithDeals:
    def __init__(self):
        self.db = None
        self.mt5_accounts = []
        self.last_deal_sync = None
        
    def connect_mongodb(self):
        """Connect to MongoDB with pymongo 4.x compatibility"""
        try:
            logger.info("🔌 Connecting to MongoDB...")
            client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
            
            # Test connection
            client.admin.command('ping')
            
            # Get database
            self.db = client.get_database()
            
            # Verify connection
            try:
                list(self.db.list_collection_names())
                logger.info("✅ MongoDB connected successfully")
                self.ensure_deal_indexes()
                return True
            except Exception as e:
                logger.error(f"❌ MongoDB connection test failed: {e}")
                return False
                
        except Exception as e:
            logger.error(f"❌ MongoDB connection error: {e}")
            self.db = None
            return False
    
    def ensure_deal_indexes(self):
        """Create indexes for mt5_deals_history collection for optimal query performance"""
        try:
            if self.db is None:
                return
            
            collection = self.db.mt5_deals_history
            
            # Create indexes
            collection.create_index([("account_number", ASCENDING)])
            collection.create_index([("time", DESCENDING)])
            collection.create_index([("type", ASCENDING)])
            collection.create_index([("symbol", ASCENDING)])
            collection.create_index([("account_number", ASCENDING), ("time", DESCENDING)])
            collection.create_index([("ticket", ASCENDING)], unique=True)
            
            logger.info("✅ Deal history indexes created/verified")
            
        except Exception as e:
            logger.warning(f"⚠️ Error creating indexes: {e}")
    
    def load_mt5_accounts_from_mongodb(self):
        """Load MT5 accounts from mt5_account_config collection"""
        try:
            if self.db is None:
                logger.warning("⚠️ MongoDB not connected, using fallback accounts")
                self.mt5_accounts = FALLBACK_ACCOUNTS
                return
            
            logger.info("📥 Loading MT5 accounts from mt5_account_config collection...")
            
            cursor = self.db.mt5_account_config.find(
                {"is_active": True},
                {"account": 1, "password": 1, "name": 1, "fund_type": 1, "target_amount": 1, "_id": 0}
            )
            
            accounts = list(cursor)
            
            if len(accounts) > 0:
                self.mt5_accounts = accounts
                logger.info(f"✅ Loaded {len(accounts)} active accounts from MongoDB")
            else:
                logger.warning("⚠️ No active accounts found, using fallback")
                self.mt5_accounts = FALLBACK_ACCOUNTS
                
        except Exception as e:
            logger.error(f"❌ Error loading accounts from MongoDB: {e}")
            self.mt5_accounts = FALLBACK_ACCOUNTS
    
    def initialize_mt5(self):
        """Initialize MT5 terminal"""
        try:
            if not mt5.initialize(path=MT5_PATH):
                logger.error(f"❌ MT5 initialize() failed, error code: {mt5.last_error()}")
                return False
            
            version = mt5.version()
            logger.info(f"✅ MT5 Terminal initialized: v{version}")
            return True
            
        except Exception as e:
            logger.error(f"❌ MT5 initialization error: {e}")
            return False
    
    def check_if_backfill_needed(self, account_number):
        """Check if initial 90-day backfill is needed for this account"""
        try:
            if self.db is None:
                return True
            
            # Check if we have any deals for this account
            deal_count = self.db.mt5_deals_history.count_documents({"account_number": account_number})
            
            if deal_count == 0:
                logger.info(f"📦 Account {account_number} needs initial backfill (no deals found)")
                return True
            
            # Check if we have recent deals (within last 7 days)
            recent_date = datetime.now(timezone.utc) - timedelta(days=7)
            recent_count = self.db.mt5_deals_history.count_documents({
                "account_number": account_number,
                "time": {"$gte": recent_date}
            })
            
            if recent_count == 0:
                logger.info(f"📦 Account {account_number} needs backfill (no recent deals)")
                return True
            
            logger.info(f"✅ Account {account_number} has {deal_count} deals, skipping backfill")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error checking backfill status: {e}")
            return True
    
    def collect_deals(self, account_config, start_date, end_date):
        """
        Collect deal history for an account within date range
        
        Returns list of deals with structure:
        - ticket (int): Unique deal ID
        - order (int): Order ticket
        - time (datetime): Deal execution time
        - type (int): Deal type (0=buy, 1=sell, 2=balance operation)
        - entry (int): Entry type (0=in, 1=out)
        - symbol (str): Trading symbol
        - volume (float): Volume in lots (CRITICAL for rebates)
        - price (float): Deal price
        - profit (float): Profit/loss (CRITICAL for analytics)
        - commission (float): Commission (CRITICAL for rebates)
        - swap (float): Swap/overnight fee
        - position_id (int): Related position
        - magic (int): Magic number (for manager attribution)
        - comment (str): Comment (for transfer classification)
        - external_id (str): External ID
        """
        account_number = account_config["account"]
        password = account_config["password"]
        server = "MEXAtlantic-Real"
        
        try:
            # Login to MT5 account
            authorized = mt5.login(account_number, password=password, server=server)
            
            if not authorized:
                error = mt5.last_error()
                logger.error(f"❌ Login failed for {account_number}: {error}")
                return []
            
            # Get deal history
            deals = mt5.history_deals_get(start_date, end_date)
            
            if deals is None:
                logger.warning(f"⚠️ No deals found for {account_number} ({start_date.date()} to {end_date.date()})")
                return []
            
            if len(deals) == 0:
                logger.info(f"📊 Account {account_number}: No deals in range")
                return []
            
            # Convert MT5 deals to dict format for MongoDB
            deal_list = []
            for deal in deals:
                deal_dict = {
                    "ticket": deal.ticket,
                    "order": deal.order,
                    "time": datetime.fromtimestamp(deal.time, tz=timezone.utc),
                    "type": deal.type,
                    "entry": deal.entry,
                    "symbol": deal.symbol,
                    "volume": deal.volume,
                    "price": deal.price,
                    "profit": deal.profit,
                    "commission": deal.commission,
                    "swap": deal.swap,
                    "position_id": deal.position_id,
                    "magic": deal.magic,
                    "comment": deal.comment,
                    "external_id": deal.external_id,
                    "account_number": account_number,
                    "account_name": account_config["name"],
                    "fund_type": account_config["fund_type"],
                    "synced_at": datetime.now(timezone.utc)
                }
                deal_list.append(deal_dict)
            
            logger.info(f"✅ Collected {len(deal_list)} deals for {account_number}")
            return deal_list
            
        except Exception as e:
            logger.error(f"❌ Error collecting deals for {account_number}: {e}")
            return []
    
    def sync_deals_to_mongodb(self, deals):
        """Store deals in MongoDB using bulk upsert"""
        if self.db is None or len(deals) == 0:
            return 0
        
        try:
            operations = []
            for deal in deals:
                operations.append(
                    UpdateOne(
                        {"ticket": deal["ticket"]},
                        {"$set": deal},
                        upsert=True
                    )
                )
            
            result = self.db.mt5_deals_history.bulk_write(operations)
            
            inserted = result.upserted_count
            modified = result.modified_count
            
            logger.info(f"💾 Stored {inserted} new deals, updated {modified} existing deals")
            return inserted + modified
            
        except Exception as e:
            logger.error(f"❌ Error storing deals to MongoDB: {e}")
            return 0
    
    def backfill_deal_history(self, account_config):
        """Perform initial 90-day backfill for an account"""
        account_number = account_config["account"]
        
        # Check if backfill is needed
        if not self.check_if_backfill_needed(account_number):
            return 0
        
        logger.info(f"📦 Starting {INITIAL_BACKFILL_DAYS}-day backfill for account {account_number}")
        
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=INITIAL_BACKFILL_DAYS)
        
        deals = self.collect_deals(account_config, start_date, end_date)
        
        if len(deals) > 0:
            synced = self.sync_deals_to_mongodb(deals)
            logger.info(f"✅ Backfill complete for {account_number}: {synced} deals")
            return synced
        else:
            logger.info(f"📊 No deals to backfill for {account_number}")
            return 0
    
    def sync_daily_deals(self, account_config):
        """Sync deals from last 24 hours (daily incremental)"""
        account_number = account_config["account"]
        
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=1)
        
        logger.info(f"🔄 Syncing daily deals for {account_number} ({start_date.date()} to {end_date.date()})")
        
        deals = self.collect_deals(account_config, start_date, end_date)
        
        if len(deals) > 0:
            synced = self.sync_deals_to_mongodb(deals)
            return synced
        else:
            logger.info(f"📊 No new deals for {account_number}")
            return 0
    
    def sync_account(self, account_config):
        """Sync a single MT5 account (basic account data)"""
        account_number = account_config["account"]
        password = account_config["password"]
        server = "MEXAtlantic-Real"
        
        try:
            # Login to MT5 account
            authorized = mt5.login(account_number, password=password, server=server)
            
            if not authorized:
                error = mt5.last_error()
                logger.error(f"❌ Login failed for {account_number}: {error}")
                return False
            
            # Get account info
            account_info = mt5.account_info()
            if account_info is None:
                logger.error(f"❌ Failed to get account info for {account_number}")
                return False
            
            # Get positions
            positions = mt5.positions_get()
            if positions is None:
                positions = []
            
            # Calculate metrics
            balance = account_info.balance
            equity = account_info.equity
            profit = account_info.profit
            margin = account_info.margin
            free_margin = account_info.margin_free
            margin_level = account_info.margin_level if account_info.margin_level else 0
            
            # Prepare update data
            update_data = {
                "account": account_number,
                "name": account_config["name"],
                "fund_type": account_config["fund_type"],
                "target_amount": account_config["target_amount"],
                "server": server,
                "broker": "MEXAtlantic",
                "balance": balance,
                "equity": equity,
                "margin": margin,
                "free_margin": free_margin,
                "margin_level": margin_level,
                "profit": profit,
                "num_positions": len(positions),
                "updated_at": datetime.now(timezone.utc),
                "connection_status": "active",
                "last_sync": datetime.now(timezone.utc)
            }
            
            # Update in MongoDB (upsert)
            if self.db is not None:
                self.db.mt5_accounts.update_one(
                    {"account": account_number},
                    {"$set": update_data},
                    upsert=True
                )
            
            logger.info(f"✅ Synced {account_number}: Balance=${balance:.2f}, Equity=${equity:.2f}, P&L=${profit:.2f}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error syncing account {account_number}: {e}")
            return False
    
    def sync_all_accounts(self):
        """Sync all configured MT5 accounts (basic data)"""
        logger.info("=" * 80)
        logger.info(f"🔄 Starting account sync cycle at {datetime.now()}")
        
        success_count = 0
        fail_count = 0
        
        for account_config in self.mt5_accounts:
            if self.sync_account(account_config):
                success_count += 1
            else:
                fail_count += 1
            time.sleep(1)
        
        logger.info(f"✅ Account sync complete: {success_count} successful, {fail_count} failed")
        logger.info("=" * 80)
    
    def sync_all_deals(self):
        """Sync deal history for all accounts (backfill + daily)"""
        logger.info("=" * 80)
        logger.info(f"💼 Starting deal history sync at {datetime.now()}")
        
        total_deals = 0
        
        for account_config in self.mt5_accounts:
            # Backfill if needed
            backfill_count = self.backfill_deal_history(account_config)
            total_deals += backfill_count
            
            # Daily incremental sync
            daily_count = self.sync_daily_deals(account_config)
            total_deals += daily_count
            
            time.sleep(2)  # Delay between accounts
        
        self.last_deal_sync = datetime.now(timezone.utc)
        logger.info(f"✅ Deal sync complete: {total_deals} deals processed")
        logger.info("=" * 80)
    
    def should_sync_deals(self):
        """Check if it's time to sync deals (daily)"""
        if self.last_deal_sync is None:
            return True
        
        time_since_last = datetime.now(timezone.utc) - self.last_deal_sync
        return time_since_last.total_seconds() >= DEAL_SYNC_INTERVAL
    
    def run(self):
        """Main service loop"""
        logger.info("🚀 MT5 Bridge Service - Deal History Collection (Phase 4A) Starting...")
        logger.info(f"⏱️  Account sync interval: {UPDATE_INTERVAL} seconds ({UPDATE_INTERVAL/60:.1f} minutes)")
        logger.info(f"💼 Deal sync interval: {DEAL_SYNC_INTERVAL} seconds ({DEAL_SYNC_INTERVAL/3600:.1f} hours)")
        logger.info(f"📦 Initial backfill: {INITIAL_BACKFILL_DAYS} days")
        
        # Connect to MongoDB
        if not self.connect_mongodb():
            logger.error("❌ Failed to connect to MongoDB - exiting")
            sys.exit(1)
        
        # Load accounts
        self.load_mt5_accounts_from_mongodb()
        
        # Initialize MT5
        if not self.initialize_mt5():
            logger.error("❌ Failed to initialize MT5 - exiting")
            sys.exit(1)
        
        # Perform initial deal sync
        logger.info("🎯 Performing initial deal history sync...")
        self.sync_all_deals()
        
        logger.info("✅ Service initialized successfully - starting sync loop")
        
        # Main sync loop
        cycle_count = 0
        while True:
            try:
                cycle_count += 1
                logger.info(f"\n{'='*80}")
                logger.info(f"📊 SYNC CYCLE #{cycle_count}")
                
                # Reload accounts from MongoDB (in case config changed)
                self.load_mt5_accounts_from_mongodb()
                
                # Sync account data (every cycle)
                self.sync_all_accounts()
                
                # Sync deals (daily check)
                if self.should_sync_deals():
                    logger.info("💼 Daily deal sync triggered")
                    self.sync_all_deals()
                
                # Wait for next cycle
                logger.info(f"⏳ Next sync in {UPDATE_INTERVAL} seconds...")
                time.sleep(UPDATE_INTERVAL)
                
            except KeyboardInterrupt:
                logger.info("\n⚠️ Service stopped by user (Ctrl+C)")
                break
            except Exception as e:
                logger.error(f"❌ Unexpected error in main loop: {e}")
                logger.info(f"⏳ Retrying in {UPDATE_INTERVAL} seconds...")
                time.sleep(UPDATE_INTERVAL)
        
        # Cleanup
        mt5.shutdown()
        logger.info("✅ MT5 Bridge Service stopped")

if __name__ == "__main__":
    try:
        bridge = MT5BridgeWithDeals()
        bridge.run()
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)
