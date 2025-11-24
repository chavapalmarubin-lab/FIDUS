"""
MT5 Bridge API Service - Multi-Terminal Support
Version: 2.0
Updated: November 24, 2025

Supports multiple MT5 terminals for different brokers:
- MEXAtlantic Terminal: 13 accounts
- LUCRUM Terminal: 1 account (2198)

Sync interval: 120 seconds
"""

import MetaTrader5 as mt5
from pymongo import MongoClient
from datetime import datetime, timezone
import time
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('C:\\mt5_bridge_service\\logs\\api_service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# MongoDB configuration
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb+srv://chavapalmarubin_db_user:"[CLEANED_PASSWORD]"@fidus.y1p9be2.mongodb.net/fidus_production')
DB_NAME = 'fidus_production'

# MT5 Terminal configurations
TERMINALS = {
    'MEXAtlantic-Real': {
        'path': r'C:\Program Files\MEXAtlantic MetaTrader 5\terminal64.exe',
        'broker': 'MEXAtlantic',
        'description': 'MEXAtlantic broker terminal'
    },
    'Lucrumcapital-Live': {
        'path': r'C:\Program Files\Lucrum Capital MetaTrader 5\terminal64.exe',
        'broker': 'Lucrum Capital',
        'description': 'LUCRUM Capital broker terminal'
    }
}

# Sync interval
SYNC_INTERVAL = 120  # seconds

class MT5BridgeMultiTerminal:
    def __init__(self):
        """Initialize the multi-terminal bridge"""
        self.db = None
        self.connect_mongodb()
        
    def connect_mongodb(self):
        """Connect to MongoDB"""
        try:
            client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)
            client.admin.command('ping')
            self.db = client[DB_NAME]
            logger.info("✅ MongoDB connection established")
            return True
        except Exception as e:
            logger.error(f"❌ MongoDB connection failed: {e}")
            return False
    
    def get_active_accounts(self):
        """Get all active accounts from MongoDB grouped by server"""
        try:
            accounts = list(self.db.mt5_account_config.find({'is_active': True}))
            logger.info(f"📋 Found {len(accounts)} active accounts in config")
            
            # Group accounts by server
            grouped = {}
            for account in accounts:
                server = account.get('server', '')
                if server not in grouped:
                    grouped[server] = []
                grouped[server].append(account)
            
            return grouped
        except Exception as e:
            logger.error(f"❌ Error fetching accounts: {e}")
            return {}
    
    def initialize_terminal(self, terminal_path, server_name):
        """Initialize connection to specific MT5 terminal"""
        try:
            # Shutdown any existing connection
            mt5.shutdown()
            
            # Initialize with specific terminal
            if not mt5.initialize(terminal_path):
                error = mt5.last_error()
                logger.error(f"❌ Failed to initialize terminal {terminal_path}: {error}")
                return False
            
            logger.info(f"✅ Terminal initialized: {server_name}")
            return True
        except Exception as e:
            logger.error(f"❌ Error initializing terminal: {e}")
            return False
    
    def sync_account(self, account_config, server_name):
        """Sync single account data"""
        account_number = account_config['account']
        password = account_config.get('password', '')
        
        try:
            # Login to the account
            authorized = mt5.login(account_number, password=password, server=server_name)
            
            if not authorized:
                error = mt5.last_error()
                logger.warning(f"⚠️  Login failed for account {account_number}: {error}")
                return False
            
            # Get account info
            account_info = mt5.account_info()
            if account_info is None:
                logger.warning(f"⚠️  Could not get account info for {account_number}")
                return False
            
            # Prepare update data
            update_data = {
                'balance': float(account_info.balance),
                'equity': float(account_info.equity),
                'margin': float(account_info.margin),
                'free_margin': float(account_info.margin_free),
                'margin_level': float(account_info.margin_level) if account_info.margin > 0 else 0,
                'profit': float(account_info.profit),
                'last_sync_timestamp': datetime.now(timezone.utc),
                'synced_from_vps': True,
                'connection_status': 'connected',
                'leverage': account_info.leverage,
                'currency': account_info.currency,
                'updated_at': datetime.now(timezone.utc).isoformat()
            }
            
            # Update MongoDB
            result = self.db.mt5_accounts.update_one(
                {'account': account_number},
                {'$set': update_data}
            )
            
            if result.modified_count > 0 or result.matched_count > 0:
                logger.info(f"✅ Synced account {account_number} ({account_config.get('name', 'N/A')}): Balance=${account_info.balance:,.2f}, Equity=${account_info.equity:,.2f}")
                return True
            else:
                logger.warning(f"⚠️  No document found for account {account_number} in mt5_accounts collection")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error syncing account {account_number}: {e}")
            return False
    
    def sync_server_accounts(self, server_name, accounts):
        """Sync all accounts for a specific server"""
        terminal_config = TERMINALS.get(server_name)
        
        if not terminal_config:
            logger.warning(f"⚠️  No terminal configuration found for server: {server_name}")
            return
        
        logger.info(f"\n{'='*60}")
        logger.info(f"🔄 Syncing {len(accounts)} accounts from {terminal_config['broker']} ({server_name})")
        logger.info(f"{'='*60}")
        
        # Initialize terminal for this broker
        if not self.initialize_terminal(terminal_config['path'], server_name):
            logger.error(f"❌ Could not initialize terminal for {server_name}")
            return
        
        # Sync each account
        success_count = 0
        for account in accounts:
            if self.sync_account(account, server_name):
                success_count += 1
            time.sleep(1)  # Small delay between accounts
        
        logger.info(f"✅ Server {server_name}: {success_count}/{len(accounts)} accounts synced successfully")
        
        # Shutdown terminal connection
        mt5.shutdown()
    
    def sync_all_accounts(self):
        """Main sync loop - sync all accounts from all servers"""
        try:
            logger.info(f"\n{'#'*60}")
            logger.info(f"🚀 Starting sync cycle at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info(f"{'#'*60}")
            
            # Get accounts grouped by server
            grouped_accounts = self.get_active_accounts()
            
            if not grouped_accounts:
                logger.warning("⚠️  No active accounts found")
                return
            
            total_accounts = sum(len(accounts) for accounts in grouped_accounts.values())
            logger.info(f"📊 Total active accounts: {total_accounts} across {len(grouped_accounts)} servers")
            
            # Sync each server's accounts
            for server_name, accounts in grouped_accounts.items():
                self.sync_server_accounts(server_name, accounts)
            
            logger.info(f"\n{'#'*60}")
            logger.info(f"✅ Sync cycle completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info(f"{'#'*60}\n")
            
        except Exception as e:
            logger.error(f"❌ Error in sync cycle: {e}")
    
    def run(self):
        """Run the bridge service continuously"""
        logger.info("\n" + "="*60)
        logger.info("🚀 MT5 Bridge Multi-Terminal Service Started")
        logger.info("="*60)
        logger.info(f"Version: 2.0")
        logger.info(f"Sync Interval: {SYNC_INTERVAL} seconds")
        logger.info(f"Configured Terminals:")
        for server, config in TERMINALS.items():
            logger.info(f"  - {server}: {config['broker']}")
        logger.info(f"MongoDB: Connected to {DB_NAME}")
        logger.info("="*60 + "\n")
        
        while True:
            try:
                self.sync_all_accounts()
                logger.info(f"⏳ Waiting {SYNC_INTERVAL} seconds until next sync...\n")
                time.sleep(SYNC_INTERVAL)
            except KeyboardInterrupt:
                logger.info("\n⛔ Bridge service stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Unexpected error in main loop: {e}")
                logger.info(f"⏳ Retrying in {SYNC_INTERVAL} seconds...")
                time.sleep(SYNC_INTERVAL)
        
        # Cleanup
        mt5.shutdown()
        logger.info("👋 Bridge service shutdown complete")


if __name__ == "__main__":
    # Create and run the bridge
    bridge = MT5BridgeMultiTerminal()
    bridge.run()
