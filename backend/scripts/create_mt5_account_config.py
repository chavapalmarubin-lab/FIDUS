"""
Create MT5 Account Config Collection
This collection is the SOURCE OF TRUTH for the MT5 Bridge Service
"""
import os
import sys
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def create_mt5_account_config():
    """Create mt5_account_config collection with all 7 accounts"""
    
    # Connect to MongoDB
    mongo_url = os.getenv('MONGO_URL')
    client = AsyncIOMotorClient(mongo_url)
    db = client.fidus_production
    
    print("=" * 80)
    print("CREATING MT5 ACCOUNT CONFIG COLLECTION")
    print("=" * 80)
    
    # Define all 7 MT5 accounts with their credentials
    # CRITICAL: These will be read by the VPS MT5 Bridge Service
    mt5_account_configs = [
        {
            "account": 886557,
            "password": "Fidus13@",  # Real password from VPS
            "name": "Main Balance Account",
            "fund_type": "BALANCE",
            "server": "MEXAtlantic-Real",
            "broker_name": "MEXAtlantic",
            "target_amount": 100000.0,
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "account": 886066,
            "password": "Fidus13@",
            "name": "Secondary Balance Account",
            "fund_type": "BALANCE",
            "server": "MEXAtlantic-Real",
            "broker_name": "MEXAtlantic",
            "target_amount": 210000.0,
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "account": 886602,
            "password": "Fidus13@",
            "name": "Tertiary Balance Account",
            "fund_type": "BALANCE",
            "server": "MEXAtlantic-Real",
            "broker_name": "MEXAtlantic",
            "target_amount": 50000.0,
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "account": 885822,
            "password": "Fidus13@",
            "name": "Core Account",
            "fund_type": "CORE",
            "server": "MEXAtlantic-Real",
            "broker_name": "MEXAtlantic",
            "target_amount": 128151.41,
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "account": 886528,
            "password": "Fidus13@",
            "name": "Separation Account",
            "fund_type": "SEPARATION",
            "server": "MEXAtlantic-Real",
            "broker_name": "MEXAtlantic",
            "target_amount": 10000.0,
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "account": 891215,
            "password": "Fidus13@",  # Need to verify this password on VPS
            "name": "Account 891215 - Interest Earnings Trading",
            "fund_type": "SEPARATION",
            "server": "MEXAtlantic-Real",
            "broker_name": "MEXAtlantic",
            "target_amount": 0.0,
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "account": 891234,
            "password": "Fidus13@",  # Need to verify this password on VPS
            "name": "Account 891234 - CORE Fund",
            "fund_type": "CORE",
            "server": "MEXAtlantic-Real",
            "broker_name": "MEXAtlantic",
            "target_amount": 0.0,
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
    ]
    
    print(f"\n[1/2] Creating mt5_account_config collection with {len(mt5_account_configs)} accounts...")
    
    # Drop existing collection if it exists
    await db.mt5_account_config.drop()
    print("  ✓ Dropped existing collection (if any)")
    
    # Insert all configs
    result = await db.mt5_account_config.insert_many(mt5_account_configs)
    print(f"  ✓ Inserted {len(result.inserted_ids)} account configurations")
    
    # Create index on account number for fast lookups
    await db.mt5_account_config.create_index("account", unique=True)
    print("  ✓ Created unique index on 'account' field")
    
    # Verification
    print("\n[2/2] Verification...")
    count = await db.mt5_account_config.count_documents({})
    active_count = await db.mt5_account_config.count_documents({"is_active": True})
    
    print(f"  ✓ Total configs: {count}")
    print(f"  ✓ Active configs: {active_count}")
    
    # Show all configs
    print("\n  Account Configurations:")
    async for cfg in db.mt5_account_config.find({}):
        status = "🟢 ACTIVE" if cfg.get('is_active') else "🔴 INACTIVE"
        print(f"    {cfg['account']}: {cfg['name']} ({cfg['fund_type']}) {status}")
    
    print("\n" + "=" * 80)
    print("✅ MT5 ACCOUNT CONFIG COLLECTION CREATED SUCCESSFULLY")
    print("=" * 80)
    print("\n📋 NEXT STEPS:")
    print("1. Deploy this collection info to VPS")
    print("2. Ensure VPS .env has correct MONGODB_URI")
    print("3. Run mt5_bridge_service_dynamic.py on VPS")
    print("4. Service will automatically sync every 5 minutes")
    print("5. Check mt5_accounts collection for live data")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(create_mt5_account_config())
