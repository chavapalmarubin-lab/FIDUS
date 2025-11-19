"""
MT4 File-Based Bridge Service
Reads account data from JSON file and uploads to MongoDB
"""
import os
import json
import time
from datetime import datetime, timezone
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
MONGO_URL = os.getenv('MONGO_URL')
MT4_DATA_FILE = r"C:\mt4_bridge\account_data.json"
POLL_INTERVAL = 60  # Check file every 60 seconds
ACCOUNT_ID = "MT4_33200931"

def connect_to_mongodb():
    """Connect to MongoDB"""
    try:
        client = MongoClient(MONGO_URL)
        db = client.get_database()
        print(f"✅ Connected to MongoDB")
        return db
    except Exception as e:
        print(f"❌ MongoDB connection error: {e}")
        return None

def read_account_data():
    """Read account data from JSON file"""
    try:
        if not os.path.exists(MT4_DATA_FILE):
            print(f"⚠️  File not found: {MT4_DATA_FILE}")
            return None
            
        with open(MT4_DATA_FILE, 'r') as f:
            data = json.load(f)
        
        print(f"📄 Read data from file: Balance=${data.get('balance', 0)}")
        return data
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in file: {e}")
        return None
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return None

def upload_to_mongodb(db, account_data):
    """Upload account data to MongoDB"""
    try:
        # Prepare document
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
            "last_update": datetime.now(timezone.utc).isoformat(),
            "mt4_timestamp": account_data.get("timestamp")
        }
        
        # Upsert to database
        result = db.mt5_accounts.update_one(
            {"_id": ACCOUNT_ID},
            {"$set": doc},
            upsert=True
        )
        
        if result.upserted_id:
            print(f"✅ Created new account document: {ACCOUNT_ID}")
        else:
            print(f"✅ Updated account: Balance=${doc['balance']}, Equity=${doc['equity']}")
        
        return True
    except Exception as e:
        print(f"❌ MongoDB upload error: {e}")
        return False

def ensure_directory():
    """Ensure the MT4 bridge directory exists"""
    bridge_dir = os.path.dirname(MT4_DATA_FILE)
    if not os.path.exists(bridge_dir):
        os.makedirs(bridge_dir)
        print(f"✅ Created directory: {bridge_dir}")

def main():
    """Main service loop"""
    print("=" * 60)
    print("MT4 FILE-BASED BRIDGE SERVICE")
    print("=" * 60)
    print(f"Account: {ACCOUNT_ID}")
    print(f"Data file: {MT4_DATA_FILE}")
    print(f"Poll interval: {POLL_INTERVAL} seconds")
    print("=" * 60)
    
    # Ensure directory exists
    ensure_directory()
    
    # Connect to MongoDB
    db = connect_to_mongodb()
    if not db:
        print("❌ Cannot start service without MongoDB connection")
        return
    
    print("🚀 Service started. Monitoring file for updates...")
    print()
    
    last_modified = None
    
    while True:
        try:
            # Check if file exists and has been modified
            if os.path.exists(MT4_DATA_FILE):
                current_modified = os.path.getmtime(MT4_DATA_FILE)
                
                # Process file if it's new or modified
                if last_modified is None or current_modified > last_modified:
                    print(f"📊 File updated at {datetime.fromtimestamp(current_modified)}")
                    
                    # Read account data
                    account_data = read_account_data()
                    
                    if account_data:
                        # Upload to MongoDB
                        if upload_to_mongodb(db, account_data):
                            last_modified = current_modified
                    
                    print()
            else:
                if last_modified is not None:
                    print(f"⚠️  File removed: {MT4_DATA_FILE}")
                    last_modified = None
            
            # Wait before next check
            time.sleep(POLL_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n⏹️  Service stopped by user")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()
