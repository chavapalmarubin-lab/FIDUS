"""
VIKING MT5 CORE Account Monitor v1.0
- Monitors viking_mt5_account_885822_data.json
- Updates viking_accounts collection with account data
- Updates viking_deals_history collection with closed deals
- Supports MT5 data format
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
ACCOUNT_NUMBER = 885822
STRATEGY = "CORE"
PLATFORM = "MT5"
POLL_INTERVAL = 30  # Check every 30 seconds

def find_account_data_file():
    """Search for viking_mt5_account_885822_data.json in common MT5 locations"""
    search_paths = [
        # Common Files directory (shared across terminals)
        r"C:\Users\Administrator\AppData\Roaming\MetaQuotes\Terminal\Common\Files",
        # MT5 specific directories
        r"C:\Program Files\MetaTrader 5\MQL5\Files",
        r"C:\Program Files (x86)\MetaTrader 5\MQL5\Files",
        # User-specific terminal directories
        r"C:\Users\Administrator\AppData\Roaming\MetaQuotes\Terminal",
    ]
    
    filename = f"viking_mt5_account_{ACCOUNT_NUMBER}_data.json"
    print(f"🔍 Searching for {filename}...")
    
    for base_path in search_paths:
        if not os.path.exists(base_path):
            continue
        
        print(f"   Checking: {base_path}")
        
        # Search recursively
        for root, dirs, files in os.walk(base_path):
            if filename in files:
                file_path = os.path.join(root, filename)
                print(f"✅ Found: {file_path}")
                return file_path
    
    print(f"❌ {filename} not found in any common location")
    return None


def parse_mt5_datetime(dt_str):
    """Parse MT5 datetime string to Python datetime"""
    if not dt_str:
        return None
    
    try:
        if isinstance(dt_str, datetime):
            return dt_str
        
        # Handle various formats
        formats = [
            "%Y.%m.%d %H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y.%m.%d %H:%M",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%SZ",
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(str(dt_str)[:19], fmt).replace(tzinfo=timezone.utc)
            except:
                continue
        
        return None
    except:
        return None


def get_database():
    """Connect to MongoDB"""
    try:
        client = MongoClient(MONGO_URL)
        db = client['fidus_production']
        # Test connection
        db.command('ping')
        return db
    except Exception as e:
        print(f"❌ MongoDB connection error: {e}")
        return None


def upload_account_data(db, account_data):
    """Upload account data to MongoDB viking_accounts collection"""
    try:
        doc = {
            "account": ACCOUNT_NUMBER,
            "strategy": STRATEGY,
            "platform": PLATFORM,
            "status": "active",
            "account_label": "CORE (MT5 - Active)",
            "server": account_data.get("server", "Unknown"),
            "balance": float(account_data.get("balance", 0)),
            "equity": float(account_data.get("equity", 0)),
            "margin": float(account_data.get("margin", 0)),
            "free_margin": float(account_data.get("free_margin", 0)),
            "margin_level": float(account_data.get("margin_level", 0)),
            "profit": float(account_data.get("profit", 0)),
            "leverage": account_data.get("leverage", 0),
            "currency": account_data.get("currency", "USD"),
            "positions_count": account_data.get("positions_count", 0),
            "orders_count": account_data.get("orders_count", 0),
            "deals_count": account_data.get("closed_deals_count", 0),
            "last_sync": datetime.now(timezone.utc),
            "data_timestamp": account_data.get("timestamp", "")
        }
        
        db.viking_accounts.update_one(
            {"account": ACCOUNT_NUMBER},
            {"$set": doc},
            upsert=True
        )
        return True
    except Exception as e:
        print(f"❌ Account data upload error: {e}")
        return False


def upload_balance_snapshot(db, account_data):
    """Save balance snapshot for historical tracking"""
    try:
        doc = {
            "account": ACCOUNT_NUMBER,
            "strategy": STRATEGY,
            "balance": float(account_data.get("balance", 0)),
            "equity": float(account_data.get("equity", 0)),
            "margin": float(account_data.get("margin", 0)),
            "free_margin": float(account_data.get("free_margin", 0)),
            "profit": float(account_data.get("profit", 0)),
            "timestamp": datetime.now(timezone.utc)
        }
        db.viking_balance_history.insert_one(doc)
        return True
    except Exception as e:
        print(f"⚠️ Balance snapshot error: {e}")
        return False


def upload_closed_deals(db, closed_deals):
    """Upload closed deals to MongoDB viking_deals_history collection"""
    if not closed_deals:
        return 0
    
    try:
        operations = []
        
        for deal in closed_deals:
            ticket = deal.get("ticket")
            if not ticket:
                continue
            
            doc = {
                "ticket": ticket,
                "account": ACCOUNT_NUMBER,
                "strategy": STRATEGY,
                "platform": PLATFORM,
                "symbol": deal.get("symbol"),
                "type": deal.get("type"),
                "volume": float(deal.get("volume", 0)),
                "open_price": float(deal.get("open_price", 0)),
                "close_price": float(deal.get("close_price", 0)),
                "open_time": parse_mt5_datetime(deal.get("open_time")),
                "close_time": parse_mt5_datetime(deal.get("close_time")),
                "profit": float(deal.get("profit", 0)),
                "swap": float(deal.get("swap", 0)),
                "commission": float(deal.get("commission", 0)),
                "magic": deal.get("magic", 0),
                "comment": deal.get("comment", ""),
                "is_balance_operation": False,
                "updated_at": datetime.now(timezone.utc)
            }
            
            # Use upsert to avoid duplicates
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
        print(f"❌ Closed deals upload error: {e}")
        return 0


def upload_balance_operations(db, balance_operations):
    """Upload balance operations (deposits/withdrawals) to MongoDB viking_deals_history collection"""
    if not balance_operations:
        return 0
    
    try:
        operations = []
        
        for op in balance_operations:
            ticket = op.get("ticket")
            if not ticket:
                continue
            
            amount = float(op.get("amount", 0))
            op_type = op.get("type", "DEPOSIT" if amount >= 0 else "WITHDRAWAL")
            
            doc = {
                "ticket": ticket,
                "account": ACCOUNT_NUMBER,
                "strategy": STRATEGY,
                "platform": PLATFORM,
                "symbol": None,
                "type": op_type,
                "volume": 0,
                "open_price": 0,
                "close_price": 0,
                "open_time": parse_mt5_datetime(op.get("time")),
                "close_time": parse_mt5_datetime(op.get("time")),
                "profit": amount,
                "swap": 0,
                "commission": 0,
                "is_balance_operation": True,
                "comment": op.get("comment", ""),
                "updated_at": datetime.now(timezone.utc)
            }
            
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
        print(f"❌ Balance operations upload error: {e}")
        return 0


def main():
    print("=" * 60)
    print(f"VIKING MT5 CORE File Monitor v1.0")
    print(f"Account: {ACCOUNT_NUMBER} | Strategy: {STRATEGY}")
    print("=" * 60)
    
    # Find the JSON file
    json_file = find_account_data_file()
    if not json_file:
        print(f"\n⚠️ No JSON file found. Creating one at default location...")
        json_file = rf"C:\Users\Administrator\AppData\Roaming\MetaQuotes\Terminal\Common\Files\viking_mt5_account_{ACCOUNT_NUMBER}_data.json"
        print(f"   Expected file: {json_file}")
        print(f"\n   Please ensure the MT5 EA is running and writing to this file.")
    
    # Connect to MongoDB
    db = get_database()
    if not db:
        print("❌ Cannot connect to MongoDB. Exiting.")
        sys.exit(1)
    
    print(f"✅ Connected to MongoDB")
    print(f"📁 Monitoring: {json_file}")
    print(f"⏰ Poll interval: {POLL_INTERVAL} seconds")
    print("-" * 60)
    
    last_modified = 0
    error_count = 0
    
    while True:
        try:
            # Check if file exists and has been modified
            if os.path.exists(json_file):
                current_modified = os.path.getmtime(json_file)
                
                if current_modified != last_modified:
                    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] File changed, processing...")
                    
                    # Read and parse JSON
                    with open(json_file, 'r') as f:
                        account_data = json.load(f)
                    
                    if account_data:
                        # Upload account data
                        if upload_account_data(db, account_data):
                            print(f"✅ Account: Balance=${account_data.get('balance', 0):,.2f}, Equity=${account_data.get('equity', 0):,.2f}")
                        
                        # Save balance snapshot (every hour)
                        upload_balance_snapshot(db, account_data)
                        
                        # Upload closed deals
                        closed_deals = account_data.get("closed_deals", [])
                        if closed_deals:
                            deals_synced = upload_closed_deals(db, closed_deals)
                            print(f"✅ Closed deals synced: {deals_synced} (from {len(closed_deals)} in file)")
                        else:
                            print("ℹ️  No closed deals in file")
                        
                        # Upload balance operations (deposits/withdrawals)
                        balance_ops = account_data.get("balance_operations", [])
                        if balance_ops:
                            ops_synced = upload_balance_operations(db, balance_ops)
                            print(f"✅ Balance operations synced: {ops_synced} (from {len(balance_ops)} in file)")
                        else:
                            print("ℹ️  No balance operations in file")
                        
                        last_modified = current_modified
                        error_count = 0
            else:
                if error_count % 10 == 0:  # Print every 10th attempt
                    print(f"⏳ Waiting for file: {json_file}")
                error_count += 1
            
            time.sleep(POLL_INTERVAL)
            
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON parse error: {e}")
            time.sleep(POLL_INTERVAL)
        except Exception as e:
            print(f"❌ Error: {e}")
            error_count += 1
            if error_count > 10:
                print("Too many errors, waiting 60 seconds...")
                time.sleep(60)
                error_count = 0
            else:
                time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
