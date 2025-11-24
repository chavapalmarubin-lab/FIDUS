"""
MT4 Bridge Service - MEXAtlantic Account 33200931
Version: 1.0
Created: November 24, 2025

File-based bridge for MT4 account (MT4 doesn't have simple Python API like MT5)
Reads data written by MT4 EA to JSON file and updates MongoDB

Platform: MT4
Account: 33200931
Server: MEXAtlantic-Real
"""

import json
import os
import time
import logging
from pymongo import MongoClient
from datetime import datetime, timezone
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('C:\\mt5_bridge_service\\logs\\mt4_mexatlantic.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb+srv://chavapalmarubin_db_user:"[CLEANED_PASSWORD]"@fidus.y1p9be2.mongodb.net/fidus_production')
DB_NAME = 'fidus_production'

# MT4 data file path (written by MT4 EA)
MT4_DATA_FILE = Path('C:/Users/Administrator/AppData/Roaming/MetaQuotes/Terminal/Common/Files/account_33200931_data.json')

# Sync interval
SYNC_INTERVAL = 120  # seconds

# Account info
MT4_ACCOUNT = 33200931
MT4_SERVER = 'MEXAtlantic-Real'
MT4_BROKER = 'MEXAtlantic'

class MT4BridgeService:
    def __init__(self):
        """Initialize MT4 bridge service"""
        self.db = None
        self.connect_mongodb()
        self.last_file_modified = None
        
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
    
    def read_mt4_data_file(self):
        """Read data from MT4 data file"""
        try:
            if not MT4_DATA_FILE.exists():
                logger.warning(f"⚠️  MT4 data file not found: {MT4_DATA_FILE}")
                return None
            
            # Check if file was modified
            current_modified = MT4_DATA_FILE.stat().st_mtime
            if self.last_file_modified and current_modified == self.last_file_modified:
                logger.info("📄 MT4 data file unchanged, skipping")
                return None
            
            self.last_file_modified = current_modified
            
            # Read and parse JSON
            with open(MT4_DATA_FILE, 'r') as f:
                data = json.load(f)
            
            logger.info(f"📄 Read MT4 data file (modified: {datetime.fromtimestamp(current_modified)})")
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON in MT4 data file: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Error reading MT4 data file: {e}")
            return None
    
    def update_mongodb(self, data):
        """Update MongoDB with MT4 account data"""
        try:
            if not data:
                return False
            
            # Prepare update data
            update_data = {
                'account': MT4_ACCOUNT,
                'balance': float(data.get('balance', 0)),
                'equity': float(data.get('equity', 0)),
                'margin': float(data.get('margin', 0)),
                'free_margin': float(data.get('free_margin', 0)),
                'margin_level': float(data.get('margin_level', 0)),
                'profit': float(data.get('profit', 0)),
                'leverage': int(data.get('leverage', 100)),
                'currency': data.get('currency', 'USD'),
                'server': MT4_SERVER,
                'broker': MT4_BROKER,
                'platform': 'MT4',
                'last_sync_timestamp': datetime.now(timezone.utc),
                'synced_from_vps': True,
                'connection_status': 'connected',
                'data_source': 'MT4_FILE_BRIDGE',
                'updated_at': datetime.now(timezone.utc).isoformat()
            }
            
            # Add positions if available
            if 'positions' in data:
                update_data['positions'] = data['positions']
                update_data['positions_count'] = len(data['positions'])
            
            # Add orders if available
            if 'orders' in data:
                update_data['orders'] = data['orders']
                update_data['orders_count'] = len(data['orders'])
            
            # Update MongoDB
            result = self.db.mt5_accounts.update_one(
                {'account': MT4_ACCOUNT},
                {'$set': update_data},
                upsert=True
            )
            
            if result.modified_count > 0 or result.upserted_id:
                logger.info(f"✅ Updated MT4 account {MT4_ACCOUNT}: Balance=${update_data['balance']:,.2f}, Equity=${update_data['equity']:,.2f}")
                return True
            else:
                logger.info(f"📊 MT4 account {MT4_ACCOUNT} data unchanged")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error updating MongoDB: {e}")
            return False
    
    def sync_once(self):
        """Perform one sync cycle"""
        try:
            logger.info(f"\n{'='*60}")
            logger.info(f"🔄 MT4 Sync Cycle Started - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info(f"{'='*60}")
            
            # Read MT4 data file
            data = self.read_mt4_data_file()
            
            if data:
                # Update MongoDB
                if self.update_mongodb(data):
                    logger.info("✅ MT4 sync completed successfully")
                else:
                    logger.warning("⚠️  MT4 sync completed with warnings")
            else:
                logger.info("📄 No new MT4 data to sync")
            
            logger.info(f"{'='*60}\n")
            
        except Exception as e:
            logger.error(f"❌ Error in sync cycle: {e}")
    
    def run(self):
        """Run the bridge service continuously"""
        logger.info("\n" + "="*60)
        logger.info("🚀 MT4 Bridge Service Started")
        logger.info("="*60)
        logger.info(f"Version: 1.0")
        logger.info(f"Account: {MT4_ACCOUNT}")
        logger.info(f"Server: {MT4_SERVER}")
        logger.info(f"Broker: {MT4_BROKER}")
        logger.info(f"Data File: {MT4_DATA_FILE}")
        logger.info(f"Sync Interval: {SYNC_INTERVAL} seconds")
        logger.info(f"MongoDB: Connected to {DB_NAME}")
        logger.info("="*60 + "\n")
        
        # Check if data file exists
        if not MT4_DATA_FILE.exists():
            logger.warning("⚠️  MT4 data file does not exist yet")
            logger.warning("⚠️  Please install MT4 EA to generate data file")
            logger.warning(f"⚠️  Expected location: {MT4_DATA_FILE}")
        
        while True:
            try:
                self.sync_once()
                logger.info(f"⏳ Waiting {SYNC_INTERVAL} seconds until next sync...\n")
                time.sleep(SYNC_INTERVAL)
            except KeyboardInterrupt:
                logger.info("\n⛔ MT4 Bridge service stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Unexpected error in main loop: {e}")
                logger.info(f"⏳ Retrying in {SYNC_INTERVAL} seconds...")
                time.sleep(SYNC_INTERVAL)
        
        logger.info("👋 MT4 Bridge service shutdown complete")


if __name__ == "__main__":
    # Create and run the bridge
    bridge = MT4BridgeService()
    bridge.run()
