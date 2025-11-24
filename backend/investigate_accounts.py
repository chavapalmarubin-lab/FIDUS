#!/usr/bin/env python3
"""
MT5 Account Investigation Script
Run this to diagnose why accounts 901351 and 901353 aren't loading
"""

from pymongo import MongoClient
import os

# Get MongoDB connection from environment or use provided one
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb+srv://chavapalmarubin_db_user:"[CLEANED_PASSWORD]"@fidus.y1p9be2.mongodb.net/fidus_production?retryWrites=true&w=majority')

print("Connecting to MongoDB...")
client = MongoClient(MONGO_URL)
db = client.fidus_production

print("=" * 60)
print("MT5 ACCOUNT INVESTIGATION")
print("=" * 60)

# Check which collection is used
collections = db.list_collection_names()
mt5_collections = [c for c in collections if 'mt5' in c.lower() or 'account' in c.lower()]
print(f"\nMT5-related collections: {mt5_collections}")

# Try both possible collection names
for collection_name in ['mt5_account_config', 'mt5_accounts']:
    if collection_name in collections:
        print(f"\n{'=' * 60}")
        print(f"CHECKING COLLECTION: {collection_name}")
        print(f"{'=' * 60}")
        
        collection = db[collection_name]
        
        # Total accounts
        total = collection.count_documents({})
        print(f"\nTotal documents: {total}")
        
        # Active accounts
        active = collection.count_documents({'is_active': True})
        print(f"Active accounts (is_active=True): {active}")
        
        # By status
        try:
            assigned = collection.count_documents({'status': 'assigned'})
            unassigned = collection.count_documents({'status': 'unassigned'})
            no_status = collection.count_documents({'status': None})
            print(f"Status breakdown:")
            print(f"  - Assigned: {assigned}")
            print(f"  - Unassigned: {unassigned}")
            print(f"  - No status: {no_status}")
        except:
            print("  - Status field not available")
        
        # List ALL accounts
        print(f"\n{'=' * 60}")
        print(f"ALL ACCOUNTS IN {collection_name}:")
        print(f"{'=' * 60}")
        
        accounts = list(collection.find({}, {
            'account': 1, 
            'is_active': 1, 
            'status': 1,
            'fund_type': 1,
            'broker': 1,
            '_id': 0
        }).sort('account', 1))
        
        if accounts:
            print(f"\nFound {len(accounts)} accounts:")
            for acc in accounts:
                account_num = acc.get('account', 'NO_ACCOUNT_NUM')
                is_active = acc.get('is_active', 'NOT_SET')
                status = acc.get('status', 'None')
                fund_type = acc.get('fund_type', 'None')
                broker = acc.get('broker', 'NOT_SET')
                print(f"  {account_num}: active={is_active}, status={status}, fund={fund_type}, broker={broker}")
        else:
            print("  No accounts found!")
        
        # Check the two new accounts specifically
        print(f"\n{'=' * 60}")
        print("CHECKING NEW ACCOUNTS 901351 and 901353:")
        print(f"{'=' * 60}")
        
        for acc_num in [901351, 901353]:
            acc = collection.find_one({'account': acc_num})
            if acc:
                print(f"\n✅ Account {acc_num} EXISTS in {collection_name}:")
                print(f"   is_active: {acc.get('is_active', 'NOT_SET')}")
                print(f"   status: {acc.get('status', 'NOT_SET')}")
                print(f"   fund_type: {acc.get('fund_type', 'NOT_SET')}")
                print(f"   broker: {acc.get('broker', 'NOT_SET')}")
                print(f"   server: {acc.get('server', 'NOT_SET')}")
                print(f"   password: {'***' if acc.get('password') else 'NOT_SET'}")
            else:
                print(f"\n❌ Account {acc_num} NOT FOUND in {collection_name}")

print(f"\n{'=' * 60}")
print("INVESTIGATION COMPLETE")
print(f"{'=' * 60}")

client.close()
