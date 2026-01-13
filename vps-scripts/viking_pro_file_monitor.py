"""
VIKING PRO File Monitor Service v2.0
- Monitors viking_account_1309411_data.json (Traders Trust PRO account)
- Updates viking_accounts collection with account data
- Updates viking_deals_history collection with closed trades
"""
import os
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from pymongo import MongoClient, UpdateOne
import sys

# Configuration
MONGO_URL = os.getenv('MONGO_URL', 'mongodb+srv://chavapalmarubin_db_user:2170TenochSecure@fidus.y1p9be2.mongodb.net/fidus_production?retryWrites=true&w=majority')
ACCOUNT_ID = "VIKING_1309411"
ACCOUNT_NUMBER = "1309411"
STRATEGY = "PRO"
BROKER = "Traders Trust"
POLL_INTERVAL = 30  # Check every 30 seconds

def find_account_data_file():
    """Search for viking_account_1309411_data.json in common MT4 locations"""
    search_paths = [
        # Common Files directory (shared across terminals)
        r"C:\Users\Administrator\AppData\Roaming\MetaQuotes\Terminal\Common\Files",
        # User-specific terminal directories
        r"C:\Users\Administrator\AppData\Roaming\MetaQuotes\Terminal",
        # MT4 installation directories
        r"C:\Program Files\Traders Trust MT4 Terminal\MQL4\Files",
        r"C:\Program Files (x86)\Traders Trust MT4 Terminal\MQL4\Files",
        r"C:\Program Files\TradersTrust-Live\MQL4\Files",
        r"C:\Program Files (x86)\TradersTrust-Live\MQL4\Files",
    ]
    
    print("🔍 Searching for viking_account_1309411_data.json...")
    
    for base_path in search_paths:
        if not os.path.exists(base_path):
            continue
        
        print(f"   Checking: {base_path}")
        
        # Search recursively
        for root, dirs, files in os.walk(base_path):
            if "viking_account_1309411_data.json" in files:
                file_path = os.path.join(root, "viking_account_1309411_data.json")
                print(f"✅ Found: {file_path}")
                return file_path
    
    print("❌ viking_account_1309411_data.json not found in any common location")
    return None

def connect_mongodb():
    """Connect to MongoDB"""
    try:
        client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        db = client['fidus_production']
        print(f"✅ Connected to MongoDB: fidus_production")
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

def parse_mt4_datetime(dt_str):
    """Parse MT4 datetime string to Python datetime"""
    if not dt_str:
        return None
    try:
        # MT4 format: "2025.01.12 15:30:45"
        return datetime.strptime(dt_str, "%Y.%m.%d %H:%M:%S")
    except:
        try:
            # Alternative format
            return datetime.strptime(dt_str, "%Y.%m.%d %H:%M")
        except:
            return None

def upload_account_data(db, account_data):
    """Upload account data to MongoDB viking_accounts collection"""
    try:
        doc = {
            "_id": ACCOUNT_ID,
            "account": ACCOUNT_NUMBER,
            "strategy": STRATEGY,
            "broker": account_data.get("broker", BROKER),
            "server": account_data.get("server"),
            "platform": "MT4",
            "balance": float(account_data.get("balance", 0)),
            "equity": float(account_data.get("equity", 0)),
            "margin": float(account_data.get("margin", 0)),
            "free_margin": float(account_data.get("free_margin", 0)),
            "margin_level": float(account_data.get("margin_level", 0)),
            "profit": float(account_data.get("profit", 0)),
            "currency": account_data.get("currency", "USD"),
            "leverage": account_data.get("leverage"),
            "positions_count": account_data.get("positions_count", 0),
            "orders_count": account_data.get("orders_count", 0),
            "closed_trades_count": account_data.get("closed_trades_count", 0),
            "history_total": account_data.get("history_total", 0),
            "status": "active",
            "last_sync": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "mt4_timestamp": account_data.get("timestamp"),
            "error_message": None
        }
        
        result = db.viking_accounts.update_one(
            {"_id": ACCOUNT_ID},
            {"$set": doc},
            upsert=True
        )
        
        return True
    except Exception as e:
        print(f"❌ Account upload error: {e}")
        return False

def upload_closed_trades(db, closed_trades):
    """Upload closed trades to MongoDB viking_deals_history collection"""
    if not closed_trades:
        return 0
    
    try:
        operations = []
        
        for trade in closed_trades:
            ticket = trade.get("ticket")
            if not ticket:
                continue
            
            doc = {
                "ticket": ticket,
                "account": ACCOUNT_NUMBER,
                "strategy": STRATEGY,
                "broker": BROKER,
                "symbol": trade.get("symbol"),
                "type": trade.get("type"),
                "volume": float(trade.get("volume", 0)),
                "open_price": float(trade.get("open_price", 0)),
                "close_price": float(trade.get("close_price", 0)),
                "open_time": parse_mt4_datetime(trade.get("open_time")),
                "close_time": parse_mt4_datetime(trade.get("close_time")),
                "profit": float(trade.get("profit", 0)),
                "swap": float(trade.get("swap", 0)),
                "commission": float(trade.get("commission", 0)),
                "updated_at": datetime.now(timezone.utc)
            }
            
            # Use upsert to avoid duplicates - use account+ticket as unique key
            operations.append(
                UpdateOne(
                    {"ticket": ticket, "account": ACCOUNT_NUMBER},
                    {"$set": doc, "$setOnInsert": {"created_at": datetime.now(timezone.utc)}},
                    upsert=True
                )
            )
        
        if operations:
            result = db.viking_deals_history.bulk_write(operations, ordered=False)
            return result.upserted_count + result.modified_count
        
        return 0
    except Exception as e:
        print(f"❌ Closed trades upload error: {e}")
        return 0

def main():
    """Main service loop"""
    print("=" * 70)
    print("VIKING PRO FILE MONITOR SERVICE v2.0")
    print("=" * 70)
    print(f"Account: {ACCOUNT_ID} ({STRATEGY})")
    print(f"Broker: {BROKER}")
    print(f"MongoDB: {MONGO_URL[:50]}...")
    print(f"Collections: viking_accounts, viking_deals_history")
    print("=" * 70)
    
    # Find account data file
    file_path = find_account_data_file()
    if not file_path:
        print("\n⚠️  Cannot start: viking_account_1309411_data.json not found")
        print("\nPossible reasons:")
        print("1. MT4 EA is not running on Traders Trust terminal")
        print("2. EA has not written data yet (wait 5 minutes)")
        print("3. File is in a different location")
        print("\nRetrying in 60 seconds...")
        time.sleep(60)
        return main()  # Retry
    
    # Connect to MongoDB
    db = connect_mongodb()
    if db is None:
        print("❌ Cannot start without MongoDB connection")
        sys.exit(1)
    
    # Create index for deals history
    try:
        db.viking_deals_history.create_index([("ticket", 1), ("account", 1)], unique=True)
        db.viking_deals_history.create_index([("close_time", -1)])
        db.viking_deals_history.create_index([("symbol", 1)])
        db.viking_deals_history.create_index([("strategy", 1)])
        print("✅ Indexes created for viking_deals_history")
    except Exception as e:
        print(f"⚠️  Index creation: {e}")
    
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
                    # Upload account data
                    if upload_account_data(db, account_data):
                        print(f"✅ PRO Account: Balance=${account_data.get('balance', 0):,.2f}, Equity=${account_data.get('equity', 0):,.2f}")
                    
                    # Upload closed trades
                    closed_trades = account_data.get("closed_trades", [])
                    if closed_trades:
                        trades_synced = upload_closed_trades(db, closed_trades)
                        print(f"✅ PRO Closed trades synced: {trades_synced} (from {len(closed_trades)} in file)")
                    else:
                        print("ℹ️  No closed trades in file")
                    
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
