#!/usr/bin/env python3
"""
MT5 Broker Migration Script
Updates existing MT5 accounts to include broker information for multi-broker support
"""

import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from datetime import datetime, timezone

# Add the project root to the Python path
sys.path.append('/app')

async def migrate_mt5_accounts():
    """Update existing MT5 accounts to include broker information"""
    
    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/fidus_investment')
    db_name = os.environ.get('DB_NAME', 'fidus_investment')
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print("🔄 Starting MT5 Broker Migration...")
    print(f"Database URL: {mongo_url}")
    print(f"Database Name: {db_name}")
    
    try:
        # Get all existing MT5 accounts
        mt5_accounts = []
        async for account in db.mt5_accounts.find({}):
            mt5_accounts.append(account)
        
        print(f"Found {len(mt5_accounts)} existing MT5 accounts")
        
        updated_count = 0
        
        for account in mt5_accounts:
            account_id = account.get('account_id')
            
            # Check if account already has broker information
            if account.get('broker_code') and account.get('broker_name'):
                print(f"  ✅ Account {account_id} already has broker info")
                continue
            
            # Determine broker based on server name or default to multibank
            broker_code = 'multibank'  # Default
            broker_name = 'Multibank'
            
            server = account.get('mt5_server', '')
            if 'dootechnology' in server.lower():
                broker_code = 'dootechnology'
                broker_name = 'DooTechnology'
            elif 'multibank' in server.lower():
                broker_code = 'multibank'
                broker_name = 'Multibank'
            
            # Update the account with broker information
            update_result = await db.mt5_accounts.update_one(
                {'account_id': account_id},
                {
                    '$set': {
                        'broker_code': broker_code,
                        'broker_name': broker_name,
                        'updated_at': datetime.now(timezone.utc).isoformat()
                    }
                }
            )
            
            if update_result.modified_count > 0:
                print(f"  ✅ Updated account {account_id} with {broker_name} broker info")
                updated_count += 1
            else:
                print(f"  ❌ Failed to update account {account_id}")
        
        print(f"\n🎉 Migration completed successfully!")
        print(f"Updated {updated_count} MT5 accounts with broker information")
        
        # Verify the migration
        print("\n🔍 Verifying migration...")
        accounts_by_broker = {}
        async for account in db.mt5_accounts.find({}):
            broker_code = account.get('broker_code', 'unknown')
            if broker_code not in accounts_by_broker:
                accounts_by_broker[broker_code] = 0
            accounts_by_broker[broker_code] += 1
        
        print("Accounts by broker after migration:")
        for broker, count in accounts_by_broker.items():
            print(f"  - {broker}: {count} accounts")
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        return False
    
    finally:
        client.close()
    
    return True

if __name__ == "__main__":
    asyncio.run(migrate_mt5_accounts())