"""
VIKING MT4 JSON Sync Service
Reads JSON file written by MT4 EA and syncs to MongoDB

This service should run on the VPS alongside MT4.
It monitors the JSON file and updates MongoDB when changes are detected.

Usage:
    python viking_json_sync_service.py

Requirements:
    pip install pymongo watchdog python-dotenv
"""

import os
import json
import time
import logging
from datetime import datetime, timezone
from pathlib import Path
from pymongo import MongoClient
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('viking_sync.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb+srv://chavapalmarubin_db_user:2170TenochSecure@fidus.y1p9be2.mongodb.net/fidus_production?retryWrites=true&w=majority')
DB_NAME = 'fidus_production'

# MT4 JSON file path - UPDATE THIS FOR YOUR VPS
# Default MT4 Files folder location
MT4_FILES_PATH = os.environ.get('MT4_FILES_PATH', r'C:\Users\Administrator\AppData\Roaming\MetaQuotes\Terminal\4436C7899DD6783682A87A8056812DF7E\MQL4\Files')
JSON_FILENAME = 'viking_account_data.json'

class VikingJSONHandler(FileSystemEventHandler):
    """Handles file system events for the Viking JSON file"""
    
    def __init__(self, mongo_client, db_name):
        self.client = mongo_client
        self.db = self.client[db_name]
        self.last_sync = None
        
    def on_modified(self, event):
        if event.src_path.endswith(JSON_FILENAME):
            logger.info(f"Detected change in {JSON_FILENAME}")
            self.sync_to_mongodb()
    
    def on_created(self, event):
        if event.src_path.endswith(JSON_FILENAME):
            logger.info(f"Detected new {JSON_FILENAME}")
            self.sync_to_mongodb()
    
    def sync_to_mongodb(self):
        """Read JSON file and sync to MongoDB"""
        json_path = os.path.join(MT4_FILES_PATH, JSON_FILENAME)
        
        try:
            # Small delay to ensure file is fully written
            time.sleep(0.5)
            
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            account = data.get('account')
            if not account:
                logger.error("No account number in JSON file")
                return
            
            # Prepare document for MongoDB
            doc = {
                'account': account,
                'strategy': data.get('strategy', 'CORE'),
                'broker': data.get('broker', 'MEXAtlantic'),
                'server': data.get('server', ''),
                'platform': data.get('platform', 'MT4'),
                'currency': data.get('currency', 'USD'),
                'balance': float(data.get('balance', 0)),
                'equity': float(data.get('equity', 0)),
                'margin': float(data.get('margin', 0)),
                'free_margin': float(data.get('free_margin', 0)),
                'profit': float(data.get('profit', 0)),
                'floating_pl': float(data.get('floating_pl', 0)),
                'leverage': int(data.get('leverage', 0)),
                'margin_level': float(data.get('margin_level', 0)),
                'open_positions': int(data.get('open_positions', 0)),
                'status': 'active',
                'last_sync': datetime.now(timezone.utc),
                'updated_at': datetime.now(timezone.utc),
                'mt4_timestamp': data.get('timestamp'),
                'error_message': None
            }
            
            # Upsert to viking_accounts collection
            result = self.db.viking_accounts.update_one(
                {'_id': f'VIKING_{account}'},
                {'$set': doc, '$setOnInsert': {'created_at': datetime.now(timezone.utc)}},
                upsert=True
            )
            
            self.last_sync = datetime.now(timezone.utc)
            
            logger.info(f"✅ Synced account {account}: Balance=${doc['balance']:.2f}, Equity=${doc['equity']:.2f}")
            
            if result.modified_count > 0:
                logger.info(f"   Updated existing document")
            elif result.upserted_id:
                logger.info(f"   Created new document: {result.upserted_id}")
                
        except FileNotFoundError:
            logger.warning(f"JSON file not found: {json_path}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in file: {e}")
        except Exception as e:
            logger.error(f"Error syncing to MongoDB: {e}")


def poll_file(handler, interval=5):
    """Alternative to watchdog - poll the file periodically"""
    json_path = os.path.join(MT4_FILES_PATH, JSON_FILENAME)
    last_modified = 0
    
    logger.info(f"Starting poll mode - checking every {interval} seconds")
    logger.info(f"Watching: {json_path}")
    
    while True:
        try:
            if os.path.exists(json_path):
                current_modified = os.path.getmtime(json_path)
                if current_modified > last_modified:
                    last_modified = current_modified
                    handler.sync_to_mongodb()
            else:
                logger.debug(f"Waiting for file: {json_path}")
        except Exception as e:
            logger.error(f"Poll error: {e}")
        
        time.sleep(interval)


def main():
    """Main entry point"""
    logger.info("=" * 60)
    logger.info("VIKING MT4 JSON Sync Service Starting")
    logger.info("=" * 60)
    logger.info(f"MongoDB: {MONGO_URL[:50]}...")
    logger.info(f"Database: {DB_NAME}")
    logger.info(f"MT4 Files Path: {MT4_FILES_PATH}")
    logger.info(f"JSON File: {JSON_FILENAME}")
    
    # Connect to MongoDB
    try:
        client = MongoClient(MONGO_URL)
        # Test connection
        client.admin.command('ping')
        logger.info("✅ MongoDB connected successfully")
    except Exception as e:
        logger.error(f"❌ MongoDB connection failed: {e}")
        return
    
    # Create handler
    handler = VikingJSONHandler(client, DB_NAME)
    
    # Try watchdog first, fall back to polling
    try:
        observer = Observer()
        observer.schedule(handler, MT4_FILES_PATH, recursive=False)
        observer.start()
        logger.info("✅ File watcher started (watchdog mode)")
        
        # Also do an initial sync if file exists
        json_path = os.path.join(MT4_FILES_PATH, JSON_FILENAME)
        if os.path.exists(json_path):
            logger.info("Found existing JSON file - doing initial sync")
            handler.sync_to_mongodb()
        
        # Keep running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            logger.info("Service stopped by user")
        observer.join()
        
    except Exception as e:
        logger.warning(f"Watchdog failed ({e}), falling back to poll mode")
        poll_file(handler, interval=5)


if __name__ == '__main__':
    main()
