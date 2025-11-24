"""
MT5 Bridge Service - Dynamic Configuration Version
Syncs MT5 account data to MongoDB with dynamic account loading from mt5_account_config collection

DEPLOYMENT LOCATION: C:\mt5_bridge_service\mt5_bridge_service_dynamic.py
Python Version: 3.12
Pymongo Version: 4.x compatible

KEY FEATURES:
- Loads MT5 accounts dynamically from MongoDB mt5_account_config collection
- Falls back to hardcoded accounts if MongoDB query fails
- Proper pymongo 4.x error handling (no truth value testing on database objects)
- Syncs every 5 minutes (300 seconds)
- Comprehensive error logging
"""

import MetaTrader5 as mt5
from pymongo import MongoClient, UpdateOne
from datetime import datetime, timezone
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
        logging.FileHandler('C:\\mt5_bridge_service\\mt5_bridge_dynamic.log'),
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

# Hardcoded fallback accounts (if MongoDB query fails)
FALLBACK_ACCOUNTS = [
    {"account": 886557, "password": ""[CLEANED_PASSWORD]"", "name": "Main Balance Account", "fund_type": "BALANCE", "target_amount": 100000.0},
    {"account": 886066, "password": ""[CLEANED_PASSWORD]"", "name": "Secondary Balance Account", "fund_type": "BALANCE", "target_amount": 210000.0},
    {"account": 886602, "password": ""[CLEANED_PASSWORD]"", "name": "Tertiary Balance Account", "fund_type": "BALANCE", "target_amount": 50000.0},
    {"account": 885822, "password": ""[CLEANED_PASSWORD]"", "name": "Core Account", "fund_type": "CORE", "target_amount": 128151.41},
    {"account": 886528, "password": ""[CLEANED_PASSWORD]"", "name": "Separation Account", "fund_type": "SEPARATION", "target_amount": 10000.0},
    {"account": 888520, "password": ""[CLEANED_PASSWORD]"", "name": "Profit Share Account", "fund_type": "BALANCE", "target_amount": 1.0},
    {"account": 888521, "password": ""[CLEANED_PASSWORD]"", "name": "Growth Balance Account", "fund_type": "BALANCE", "target_amount": 7000.0}
]

class MT5BridgeDynamic:
    def __init__(self):
        self.db = None
        self.mt5_accounts = []
        
    def connect_mongodb(self):
        """Connect to MongoDB with pymongo 4.x compatibility"""
        try:
            logger.info("🔌 Connecting to MongoDB...")
            client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
            
            # Test connection
            client.admin.command('ping')
            
            # Get database
            self.db = client.get_database()
            
            # CRITICAL: Don't use truth value testing on db object (pymongo 4.x)
            # Instead, verify connection by testing a simple operation
            try:
                list(self.db.list_collection_names())
                logger.info("✅ MongoDB connected successfully")
                return True
            except Exception as e:
                logger.error(f"❌ MongoDB connection test failed: {e}")
                return False
                
        except Exception as e:
            logger.error(f"❌ MongoDB connection error: {e}")
            self.db = None
            return False
    
    def load_mt5_accounts_from_mongodb(self):
        """
        Load MT5 accounts from mt5_account_config collection
        Falls back to hardcoded accounts if query fails
        """
        try:
            # CRITICAL: Check if db exists using 'is not None' instead of truth value
            if self.db is None:
                logger.warning("⚠️ MongoDB not connected, using fallback accounts")
                self.mt5_accounts = FALLBACK_ACCOUNTS
                return
            
            logger.info("📥 Loading MT5 accounts from mt5_account_config collection...")
            
            # Query for active accounts only
            cursor = self.db.mt5_account_config.find(
                {"is_active": True},
                {"account": 1, "password": 1, "name": 1, "fund_type": 1, "target_amount": 1, "_id": 0}
            )
            
            # Convert cursor to list
            accounts = list(cursor)
            
            if len(accounts) > 0:
                self.mt5_accounts = accounts
                logger.info(f"✅ Loaded {len(accounts)} active accounts from MongoDB:")
                for acc in accounts:
                    logger.info(f"   - {acc['account']}: {acc['name']} ({acc['fund_type']})")
            else:
                logger.warning("⚠️ No active accounts found in mt5_account_config, using fallback")
                self.mt5_accounts = FALLBACK_ACCOUNTS
                
        except Exception as e:
            logger.error(f"❌ Error loading accounts from MongoDB: {e}")
            logger.info("📋 Using fallback hardcoded accounts")
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
    
    def sync_account(self, account_config):
        """Sync a single MT5 account to MongoDB"""
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
        """Sync all configured MT5 accounts"""
        logger.info("=" * 80)
        logger.info(f"🔄 Starting sync cycle at {datetime.now()}")
        logger.info(f"📊 Accounts to sync: {len(self.mt5_accounts)}")
        
        success_count = 0
        fail_count = 0
        
        for account_config in self.mt5_accounts:
            if self.sync_account(account_config):
                success_count += 1
            else:
                fail_count += 1
            
            # Small delay between accounts
            time.sleep(1)
        
        logger.info(f"✅ Sync complete: {success_count} successful, {fail_count} failed")
        logger.info("=" * 80)
    
    def run(self):
        """Main service loop"""
        logger.info("🚀 MT5 Bridge Service - Dynamic Configuration Mode Starting...")
        logger.info(f"⏱️  Update interval: {UPDATE_INTERVAL} seconds ({UPDATE_INTERVAL/60:.1f} minutes)")
        
        # Connect to MongoDB
        if not self.connect_mongodb():
            logger.error("❌ Failed to connect to MongoDB - will use fallback accounts")
        
        # Load accounts from MongoDB (or fallback)
        self.load_mt5_accounts_from_mongodb()
        
        # Initialize MT5
        if not self.initialize_mt5():
            logger.error("❌ Failed to initialize MT5 - exiting")
            sys.exit(1)
        
        logger.info("✅ Service initialized successfully - starting sync loop")
        
        # Main sync loop
        cycle_count = 0
        while True:
            try:
                cycle_count += 1
                logger.info(f"\n{'='*80}")
                logger.info(f"📊 SYNC CYCLE #{cycle_count}")
                
                # Reload accounts from MongoDB every cycle (in case config changed)
                self.load_mt5_accounts_from_mongodb()
                
                # Sync all accounts
                self.sync_all_accounts()
                
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
        bridge = MT5BridgeDynamic()
        bridge.run()
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)
