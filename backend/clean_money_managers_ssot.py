"""
Clean money_managers collection to enforce Single Source of Truth architecture.
Removes assigned_accounts field which violates SSOT pattern.
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
import json

load_dotenv('.env')
mongo_url = os.environ['MONGO_URL']

async def clean_money_managers():
    client = AsyncIOMotorClient(mongo_url)
    db = client['fidus_production']
    
    print("=" * 80)
    print("CLEANING MONEY_MANAGERS COLLECTION - SSOT ARCHITECTURE")
    print("=" * 80)
    
    # Check current state
    managers_with_accounts = await db.money_managers.count_documents({'assigned_accounts': {'$exists': True}})
    print(f'\n📊 Managers with assigned_accounts field: {managers_with_accounts}')
    
    if managers_with_accounts > 0:
        # Show what will be removed
        managers = await db.money_managers.find({'assigned_accounts': {'$exists': True}}, {'name': 1, 'assigned_accounts': 1}).to_list(None)
        print('\n🔍 Managers with account lists (will be removed):')
        for mgr in managers:
            name = mgr.get('name', 'Unknown')
            accounts = mgr.get('assigned_accounts', [])
            print(f'  - {name}: {accounts}')
        
        # Remove the assigned_accounts field from all money_managers documents
        result = await db.money_managers.update_many(
            {},
            {'$unset': {'assigned_accounts': ''}}
        )
        print(f'\n✅ Removed assigned_accounts field from {result.modified_count} managers')
    else:
        print('\n✅ No assigned_accounts fields found - collection already clean')
    
    # Verify cleanup
    print('\n📋 Sample money_managers document after cleanup:')
    sample = await db.money_managers.find_one({})
    if sample:
        if '_id' in sample:
            del sample['_id']
        print(json.dumps(sample, indent=2, default=str))
    
    # Final verification
    remaining = await db.money_managers.count_documents({'assigned_accounts': {'$exists': True}})
    print(f'\n✅ Verification: {remaining} managers still have assigned_accounts field')
    
    if remaining == 0:
        print('\n🎉 SSOT CLEANUP COMPLETE - money_managers collection is now clean!')
        print('   - Collection contains ONLY manager metadata')
        print('   - NO account data stored')
        print('   - Links to mt5_accounts via manager_name field')
    
    client.close()

if __name__ == '__main__':
    asyncio.run(clean_money_managers())
