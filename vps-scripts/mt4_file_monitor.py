"""
MT4 File Monitor Service - Auto-discovers and monitors account_data.json
"""
import os
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from pymongo import MongoClient
import sys

# Configuration
MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
ACCOUNT_ID = "MT4_33200931"
POLL_INTERVAL = 30  # Check every 30 seconds

def find_account_data_file():
    """Search for account_data.json in common MT4 locations"""
    search_paths = [
        # Common Files directory (shared across terminals)
        r"C:\Users\Administrator\AppData\Roaming\MetaQuotes\Terminal\Common\Files",
        # User-specific terminal directories
        r"C:\Users\Administrator\AppData\Roaming\MetaQuotes\Terminal",
        # MT4 installation directories
        r"C:\Program Files\MEX Atlantic MT4 Terminal\MQL4\Files",
        r"C:\Program Files (x86)\MEX Atlantic MT4 Terminal\MQL4\Files",
    ]
    
    print("🔍 Searching for account_data.json...")
    
    for base_path in search_paths:
        if not os.path.exists(base_path):
            continue
        
        print(f"   Checking: {base_path}")
        
        # Search recursively
        for root, dirs, files in os.walk(base_path):
            if "account_data.json" in files:
                file_path = os.path.join(root, "account_data.json")
                print(f"✅ Found: {file_path}")
                return file_path
    
    print("❌ account_data.json not found in any common location")
    return None

def connect_mongodb():
    """Connect to MongoDB"""
    try:
        client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        db = client.get_database()
        print(f"✅ Connected to MongoDB")
        return db
    except Exception as e:
        print(f"❌ MongoDB connection error: {e}")
        return None

def read_account_data(file_path):
    """Read and parse account data JSON"""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return data
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        return None
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return None

def upload_to_mongodb(db, account_data):
    """Upload account data to MongoDB"""
    try:
        doc = {
            "_id": ACCOUNT_ID,
            "account_number": account_data.get("account"),
            "account_name": account_data.get("name"),
            "server": account_data.get("server"),
            "balance": float(account_data.get("balance", 0)),
            "equity": float(account_data.get("equity", 0)),
            "margin": float(account_data.get("margin", 0)),
            "free_margin": float(account_data.get("free_margin", 0)),
            "profit": float(account_data.get("profit", 0)),
            "currency": account_data.get("currency"),
            "leverage": account_data.get("leverage"),
            "credit": float(account_data.get("credit", 0)),
            "platform": "MT4",
            "fund_type": "MONEY_MANAGER",
            "updated_at": datetime.now(timezone.utc),
            "mt4_timestamp": account_data.get("timestamp")
        }
        
        result = db.mt5_accounts.update_one(
            {"_id": ACCOUNT_ID},
            {"$set": doc},
            upsert=True
        )
        
        if result.upserted_id:
            print(f"✅ Created account: {ACCOUNT_ID}")
        else:
            print(f"✅ Updated: Balance=${doc['balance']:.2f}, Equity=${doc['equity']:.2f}")
        
        return True
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return False

def main():
    """Main service loop"""
    print("=" * 70)
    print("MT4 FILE MONITOR SERVICE")
    print("=" * 70)
    print(f"Account: {ACCOUNT_ID}")
    print(f"MongoDB: {MONGO_URL[:50]}...")
    print("=" * 70)
    
    # Find account data file
    file_path = find_account_data_file()
    if not file_path:
        print("\n⚠️  Cannot start: account_data.json not found")
        print("\nPossible reasons:")
        print("1. MT4 EA is not running")
        print("2. EA has not written data yet (wait 5 minutes)")
        print("3. File is in a different location")
        print("\nRetrying in 60 seconds...")
        time.sleep(60)
        return main()  # Retry
    
    # Connect to MongoDB
    db = connect_mongodb()
    if not db:
        print("❌ Cannot start without MongoDB connection")
        sys.exit(1)
    
    print(f"\n🚀 Service started. Monitoring: {file_path}")
    print(f"📊 Poll interval: {POLL_INTERVAL} seconds\n")
    
    last_modified = None
    error_count = 0
    
    while True:
        try:
            if not os.path.exists(file_path):
                print(f"⚠️  File removed: {file_path}")
                time.sleep(POLL_INTERVAL)
                continue
            
            current_modified = os.path.getmtime(file_path)
            
            if last_modified is None or current_modified > last_modified:
                timestamp = datetime.fromtimestamp(current_modified).strftime('%Y-%m-%d %H:%M:%S')
                print(f"\n📄 File updated: {timestamp}")
                
                account_data = read_account_data(file_path)
                
                if account_data:
                    if upload_to_mongodb(db, account_data):
                        last_modified = current_modified
                        error_count = 0
                else:
                    error_count += 1
                    if error_count > 5:
                        print("❌ Too many errors. Restarting search...")
                        return main()
            
            time.sleep(POLL_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n⏹️  Service stopped by user")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            error_count += 1
            if error_count > 10:
                print("❌ Too many errors. Exiting...")
                sys.exit(1)
            time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()
