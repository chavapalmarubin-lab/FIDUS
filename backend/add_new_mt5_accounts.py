"""
Add New MT5 Accounts 901351 and 901353
CRITICAL: These accounts must be added before building the Investment Committee UI
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import os

async def add_new_accounts():
    """Add accounts 901351 and 901353 to mt5_accounts collection"""
    
    print("=" * 70)
    print("🚨 ADDING NEW MT5 ACCOUNTS 901351 & 901353")
    print("=" * 70)
    
    # Read MONGO_URL from .env
    mongo_url = None
    with open('.env') as f:
        for line in f:
            if line.startswith('MONGO_URL='):
                mongo_url = line.split('=', 1)[1].strip().strip('"')
                break
    
    if not mongo_url:
        print("❌ ERROR: MONGO_URL not found in .env")
        return
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(mongo_url)
    db = client['fidus_production']
    
    print("\n🔍 Checking if accounts already exist...")
    
    # Check if accounts already exist
    existing = await db.mt5_accounts.find({
        "account": {"$in": [901351, 901353]}
    }).to_list(length=10)
    
    if len(existing) > 0:
        print(f"\n⚠️  WARNING: {len(existing)} account(s) already exist!")
        for acc in existing:
            print(f"   - Account {acc['account']} is already in the database")
        
        # Ask if we should update or skip
        print("\n✅ Accounts are already present. No action needed.")
        client.close()
        return
    
    print("✅ Accounts not found. Proceeding with insertion...")
    
    # Define new accounts
    new_accounts = [
        {
            "account": 901351,
            "password": ""[CLEANED_PASSWORD]"",
            "server": "MEXAtlantic-Real",
            "broker": "MEXAtlantic",
            "name": "Spaniard Stock CFDs - Master Account",
            "client_name": "FIDUS Investment Platform",
            "currency": "USD",
            "leverage": 100,
            
            # Assignments (initially null - committee will assign)
            "manager_assigned": None,
            "fund_type": None,
            "trading_platform": None,
            "allocated_capital": 0.0,
            
            # Balance info (VPS will populate)
            "balance": 10000.00,
            "equity": 10000.00,
            "margin": 0.0,
            "margin_free": 10000.00,
            "free_margin": 10000.00,
            "margin_level": 0.0,
            "profit": 0.0,
            
            # Metadata
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "last_sync": None,
            "sync_enabled": True,
            "status": "active",
            
            # No copy trading (this is master)
            "copy_trading_config": None,
            
            # Additional fields
            "last_allocation_update": None,
            "allocation_notes": "Master account for Spaniard Stock CFDs strategy"
        },
        {
            "account": 901353,
            "password": ""[CLEANED_PASSWORD]"",
            "server": "MEXAtlantic-Real",
            "broker": "MEXAtlantic",
            "name": "Spaniard Stock CFDs - Copy Account",
            "client_name": "FIDUS Investment Platform",
            "currency": "USD",
            "leverage": 100,
            
            # Assignments (initially null - committee will assign)
            "manager_assigned": None,
            "fund_type": None,
            "trading_platform": "Biking",
            "allocated_capital": 0.0,
            
            # Balance info (VPS will populate)
            "balance": 0.0,
            "equity": 0.0,
            "margin": 0.0,
            "margin_free": 0.0,
            "free_margin": 0.0,
            "margin_level": 0.0,
            "profit": 0.0,
            
            # Metadata
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "last_sync": None,
            "sync_enabled": True,
            "status": "active",
            
            # Copy trading config
            "copy_trading_config": {
                "is_copy_account": True,
                "copy_from_account": 901351,
                "copy_platform": "Biking",
                "copy_ratio": 1.0
            },
            
            # Additional fields
            "last_allocation_update": None,
            "allocation_notes": "Copy account via Biking platform, copying from account 901351"
        }
    ]
    
    print("\n📝 Inserting accounts into database...")
    
    # Insert accounts
    result = await db.mt5_accounts.insert_many(new_accounts)
    
    print(f"\n✅ Successfully added {len(result.inserted_ids)} accounts!")
    print(f"   - Account 901351: {result.inserted_ids[0]}")
    print(f"   - Account 901353: {result.inserted_ids[1]}")
    
    # Verify
    print("\n🔍 Verifying accounts were added...")
    count = await db.mt5_accounts.count_documents({
        "account": {"$in": [901351, 901353]}
    })
    print(f"✅ Verification: {count} accounts now in database")
    
    # Get total count of all 13 accounts
    total_count = await db.mt5_accounts.count_documents({
        "account": {"$in": [
            885822, 886066, 886528, 886557, 886602,
            891215, 891234, 897589, 897590, 897591,
            897599, 901351, 901353
        ]}
    })
    
    print(f"\n📊 TOTAL ACCOUNTS IN SYSTEM: {total_count}/13")
    
    if total_count == 13:
        print("✅ ALL 13 ACCOUNTS PRESENT - READY FOR UI IMPLEMENTATION!")
    else:
        print(f"⚠️  WARNING: Only {total_count}/13 accounts found")
    
    print("\n" + "=" * 70)
    print("✅ ACCOUNT ADDITION COMPLETE")
    print("=" * 70)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(add_new_accounts())
