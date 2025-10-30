#!/usr/bin/env python3
"""
Fix MT5 Deals History Index - Remove single ticket index, add compound index
This fixes the duplicate key errors when syncing trades
"""

import asyncio
import sys
from motor.motor_asyncio import AsyncIOMotorClient
import os

async def fix_index():
    """Fix the mt5_deals_history collection index"""
    
    # Get MongoDB URL from environment
    mongo_url = os.getenv('MONGO_URL')
    if not mongo_url:
        # Try reading from .env file
        try:
            with open('/app/backend/.env', 'r') as f:
                for line in f:
                    if line.startswith('MONGO_URL='):
                        mongo_url = line.split('=', 1)[1].strip()
                        break
        except:
            pass
    
    if not mongo_url:
        print("❌ MONGO_URL not found in environment or .env file")
        return False
    
    try:
        print("🔗 Connecting to MongoDB Atlas...")
        client = AsyncIOMotorClient(mongo_url)
        db = client['fidus_production']
        collection = db.mt5_deals_history
        
        # Get existing indexes
        print("📊 Checking existing indexes...")
        indexes = await collection.index_information()
        print(f"Current indexes: {list(indexes.keys())}")
        
        # Drop the problematic single-field ticket index if it exists
        if 'ticket_1' in indexes:
            print("🗑️  Dropping old single-field 'ticket' index...")
            await collection.drop_index('ticket_1')
            print("✅ Old index dropped")
        else:
            print("ℹ️  Single-field 'ticket' index not found")
        
        # Create new compound index on (ticket, account_number)
        print("🔧 Creating new compound index on (ticket, account_number)...")
        await collection.create_index(
            [("ticket", 1), ("account_number", 1)],
            unique=True,
            name="ticket_account_unique"
        )
        print("✅ New compound index created: ticket_account_unique")
        
        # Verify new indexes
        print("\n📊 Final indexes:")
        indexes = await collection.index_information()
        for idx_name, idx_info in indexes.items():
            print(f"  - {idx_name}: {idx_info.get('key', [])}")
        
        # Get collection stats
        count = await collection.count_documents({})
        print(f"\n📈 Collection has {count:,} documents")
        
        client.close()
        print("\n✅ Index migration complete!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(fix_index())
    sys.exit(0 if success else 1)
