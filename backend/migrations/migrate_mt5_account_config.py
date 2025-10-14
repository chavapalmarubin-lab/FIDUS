#!/usr/bin/env python3
"""
MT5 Account Configuration Migration Script
Creates mt5_account_config collection and migrates existing accounts
NO MOCK DATA - uses real production account numbers
"""

import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from datetime import datetime, timezone
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')
MONGO_URL = os.getenv('MONGO_URL')

# Existing 7 REAL production accounts
EXISTING_ACCOUNTS = [
    {
        "account": 886557,
        "password": "9qvMcIgO1El58W4",
        "name": "Main Balance Account",
        "server": "MEXAtlantic-Real",
        "fund_type": "BALANCE",
        "target_amount": 100000,
        "is_active": True
    },
    {
        "account": 886066,
        "password": "9qvMcIgO1El58W4",
        "name": "Secondary Balance Account",
        "server": "MEXAtlantic-Real",
        "fund_type": "BALANCE",
        "target_amount": 210000,
        "is_active": True
    },
    {
        "account": 886602,
        "password": "9qvMcIgO1El58W4",
        "name": "Tertiary Balance Account",
        "server": "MEXAtlantic-Real",
        "fund_type": "BALANCE",
        "target_amount": 50000,
        "is_active": True
    },
    {
        "account": 885822,
        "password": "9qvMcIgO1El58W4",
        "name": "Core Account",
        "server": "MEXAtlantic-Real",
        "fund_type": "CORE",
        "target_amount": 128151,
        "is_active": True
    },
    {
        "account": 886528,
        "password": "9qvMcIgO1El58W4",
        "name": "Separation Account",
        "server": "MEXAtlantic-Real",
        "fund_type": "SEPARATION",
        "target_amount": 10000,
        "is_active": True
    },
    {
        "account": 888520,
        "password": "9qvMcIgO1El58W4",
        "name": "Profit Share Account",
        "server": "MEXAtlantic-Real",
        "fund_type": "BALANCE",
        "target_amount": 1,
        "is_active": True
    },
    {
        "account": 888521,
        "password": "9qvMcIgO1El58W4",
        "name": "Growth Balance Account",
        "server": "MEXAtlantic-Real",
        "fund_type": "BALANCE",
        "target_amount": 7000,
        "is_active": True
    }
]

async def create_collection_and_indexes():
    """Create mt5_account_config collection with proper indexes"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.fidus_production
    
    print("=" * 60)
    print("MT5 ACCOUNT CONFIGURATION MIGRATION")
    print("=" * 60)
    print()
    
    # Check if collection exists
    collections = await db.list_collection_names()
    if 'mt5_account_config' in collections:
        print("⚠️  Collection 'mt5_account_config' already exists")
        response = input("Do you want to drop and recreate? (yes/no): ")
        if response.lower() == 'yes':
            await db.mt5_account_config.drop()
            print("✓ Dropped existing collection")
        else:
            print("❌ Migration cancelled")
            client.close()
            return False
    
    # Create collection (implicitly created on first insert)
    print("\n📦 Creating mt5_account_config collection...")
    
    # Create indexes
    print("🔧 Creating indexes...")
    await db.mt5_account_config.create_index("account", unique=True)
    await db.mt5_account_config.create_index("is_active")
    await db.mt5_account_config.create_index("fund_type")
    print("✓ Indexes created: account (unique), is_active, fund_type")
    
    # Migrate existing accounts
    print(f"\n📝 Migrating {len(EXISTING_ACCOUNTS)} existing accounts...")
    
    now = datetime.now(timezone.utc).isoformat()
    migrated_count = 0
    
    for account_data in EXISTING_ACCOUNTS:
        # Add metadata
        account_doc = {
            **account_data,
            "created_at": now,
            "updated_at": now,
            "created_by": "system_migration",
            "last_modified_by": "system_migration"
        }
        
        try:
            await db.mt5_account_config.insert_one(account_doc)
            print(f"  ✓ Migrated account {account_data['account']} - {account_data['name']}")
            migrated_count += 1
        except Exception as e:
            print(f"  ❌ Failed to migrate account {account_data['account']}: {str(e)}")
    
    print(f"\n✅ Migration complete: {migrated_count}/{len(EXISTING_ACCOUNTS)} accounts migrated")
    
    # Verify migration
    print("\n🔍 Verifying migration...")
    count = await db.mt5_account_config.count_documents({})
    active_count = await db.mt5_account_config.count_documents({"is_active": True})
    
    print(f"  Total accounts: {count}")
    print(f"  Active accounts: {active_count}")
    
    # Show summary by fund type
    print("\n📊 Summary by fund type:")
    pipeline = [
        {"$group": {
            "_id": "$fund_type",
            "count": {"$sum": 1},
            "total_target": {"$sum": "$target_amount"}
        }},
        {"$sort": {"_id": 1}}
    ]
    
    async for result in db.mt5_account_config.aggregate(pipeline):
        print(f"  {result['_id']}: {result['count']} accounts, "
              f"${result['total_target']:,.2f} total target")
    
    print("\n" + "=" * 60)
    print("✅ MIGRATION COMPLETED SUCCESSFULLY")
    print("=" * 60)
    
    client.close()
    return True

async def verify_indexes():
    """Verify that all indexes were created correctly"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.fidus_production
    
    print("\n🔍 Verifying indexes...")
    indexes = await db.mt5_account_config.list_indexes().to_list(length=None)
    
    print("Indexes found:")
    for idx in indexes:
        print(f"  - {idx['name']}: {idx.get('key', {})}")
        if idx.get('unique'):
            print(f"    (unique)")
    
    client.close()

async def show_sample_data():
    """Show sample data from the collection"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.fidus_production
    
    print("\n📋 Sample data from mt5_account_config:")
    print("-" * 60)
    
    async for account in db.mt5_account_config.find().limit(3):
        print(f"Account: {account['account']}")
        print(f"  Name: {account['name']}")
        print(f"  Fund Type: {account['fund_type']}")
        print(f"  Target: ${account['target_amount']:,.2f}")
        print(f"  Active: {account['is_active']}")
        print(f"  Created: {account['created_at']}")
        print("-" * 60)
    
    client.close()

async def main():
    """Main migration function"""
    try:
        success = await create_collection_and_indexes()
        
        if success:
            await verify_indexes()
            await show_sample_data()
            
            print("\n✅ Phase 1 (Database Layer) completed successfully!")
            print("\nNext steps:")
            print("1. Verify collection in MongoDB Atlas dashboard")
            print("2. Proceed to Phase 2 (Backend API implementation)")
            
            return 0
        else:
            return 1
            
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
