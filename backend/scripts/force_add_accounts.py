#!/usr/bin/env python3
"""
Force add accounts 901351 and 901353 to the database
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

MONGO_URL = "mongodb+srv://chavapalmarubin_db_user:"[CLEANED_PASSWORD]"@fidus.y1p9be2.mongodb.net/fidus_production?retryWrites=true&w=majority"

async def force_add():
    print("Connecting to MongoDB...")
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.get_database('fidus_production')
    
    print("\n1. Checking current state...")
    count_before = await db.mt5_accounts.count_documents({})
    print(f"   Total accounts before: {count_before}")
    
    acc1_exists = await db.mt5_accounts.find_one({"account": 901351})
    acc2_exists = await db.mt5_accounts.find_one({"account": 901353})
    
    print(f"   901351 exists: {acc1_exists is not None}")
    print(f"   901353 exists: {acc2_exists is not None}")
    
    # Delete if they exist (to start fresh)
    if acc1_exists or acc2_exists:
        print("\n2. Removing existing accounts...")
        result = await db.mt5_accounts.delete_many({"account": {"$in": [901351, 901353]}})
        print(f"   Deleted {result.deleted_count} document(s)")
    
    print("\n3. Inserting new accounts...")
    
    # Account 901351
    account_901351 = {
        "account": 901351,
        "password": ""[CLEANED_PASSWORD]"",
        "server": "MEXAtlantic-Real",
        "broker": "MEXAtlantic",
        "manager_assigned": None,
        "fund_type": None,
        "trading_platform": None,
        "allocated_capital": 0,
        "copy_trading_config": None,
        "balance": 0,
        "equity": 0,
        "margin": 0,
        "margin_free": 0,
        "margin_level": 0,
        "profit": 0,
        "created_at": datetime.utcnow(),
        "last_sync": None,
        "sync_enabled": False,
        "status": "active"
    }
    
    result1 = await db.mt5_accounts.insert_one(account_901351)
    print(f"   ✅ Inserted 901351 - ID: {result1.inserted_id}")
    
    # Account 901353
    account_901353 = {
        "account": 901353,
        "password": ""[CLEANED_PASSWORD]"",
        "server": "MEXAtlantic-Real",
        "broker": "MEXAtlantic",
        "manager_assigned": None,
        "fund_type": None,
        "trading_platform": None,
        "allocated_capital": 0,
        "copy_trading_config": {
            "is_copy_account": True,
            "copy_from_account": 901351,
            "copy_platform": "Biking",
            "copy_ratio": 1.0
        },
        "balance": 0,
        "equity": 0,
        "margin": 0,
        "margin_free": 0,
        "margin_level": 0,
        "profit": 0,
        "created_at": datetime.utcnow(),
        "last_sync": None,
        "sync_enabled": False,
        "status": "active"
    }
    
    result2 = await db.mt5_accounts.insert_one(account_901353)
    print(f"   ✅ Inserted 901353 - ID: {result2.inserted_id}")
    
    print("\n4. Verification...")
    count_after = await db.mt5_accounts.count_documents({})
    print(f"   Total accounts after: {count_after}")
    
    acc1_check = await db.mt5_accounts.find_one({"account": 901351})
    acc2_check = await db.mt5_accounts.find_one({"account": 901353})
    
    print(f"   901351 exists: {acc1_check is not None}")
    print(f"   901353 exists: {acc2_check is not None}")
    
    # List all accounts
    all_accounts = await db.mt5_accounts.find({}).to_list(length=20)
    account_numbers = sorted([a['account'] for a in all_accounts])
    print(f"\n5. All account numbers in database:")
    print(f"   {account_numbers}")
    print(f"   Total: {len(account_numbers)}")
    
    if len(account_numbers) == 13 and 901351 in account_numbers and 901353 in account_numbers:
        print("\n✅ SUCCESS! Both accounts added and verified!")
    else:
        print("\n❌ Something went wrong!")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(force_add())
