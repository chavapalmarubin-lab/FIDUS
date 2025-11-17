#!/usr/bin/env python3
"""
Update accounts 901351 and 901353 with complete schema including password
and new assignment fields for the drag-and-drop feature
"""

import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def update_accounts():
    """Update accounts 901351 and 901353 with complete schema"""
    
    mongo_url = os.environ.get('MONGO_URL', 'mongodb+srv://emergent-ops:BpzaxqxDCjz1yWY4@fidus.y1p9be2.mongodb.net/fidus_production')
    
    print(f"Connecting to MongoDB...")
    client = AsyncIOMotorClient(mongo_url)
    db = client.get_database('fidus_production')
    
    print("\n" + "="*60)
    print("UPDATING ACCOUNTS 901351 AND 901353")
    print("="*60)
    
    # Update 901351
    print("\n📋 Updating Account 901351...")
    result1 = await db.mt5_accounts.update_one(
        {"account": 901351},
        {"$set": {
            "password": "Fidus13!",
            "server": "MEXAtlantic-Real",
            "broker": "MEXAtlantic",
            "manager_assigned": None,
            "fund_type": None,
            "trading_platform": None,
            "allocated_capital": 0,
            "copy_trading_config": None,
            "status": "active"
        }}
    )
    print(f"✅ Updated account 901351 - Modified: {result1.modified_count} document(s)")
    
    # Update 901353 with copy config
    print("\n📋 Updating Account 901353 (Copy Account)...")
    result2 = await db.mt5_accounts.update_one(
        {"account": 901353},
        {"$set": {
            "password": "Fidus13!",
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
            "status": "active"
        }}
    )
    print(f"✅ Updated account 901353 - Modified: {result2.modified_count} document(s)")
    
    # Verify updates
    print("\n" + "="*60)
    print("VERIFICATION")
    print("="*60)
    
    acc_901351 = await db.mt5_accounts.find_one({"account": 901351})
    acc_901353 = await db.mt5_accounts.find_one({"account": 901353})
    
    print("\n📊 Account 901351:")
    print(f"  Password: {acc_901351.get('password', 'NOT SET')}")
    print(f"  Broker: {acc_901351.get('broker', 'NOT SET')}")
    print(f"  Server: {acc_901351.get('server', 'NOT SET')}")
    print(f"  Manager Assigned: {acc_901351.get('manager_assigned', 'None')}")
    print(f"  Fund Type: {acc_901351.get('fund_type', 'None')}")
    print(f"  Trading Platform: {acc_901351.get('trading_platform', 'None')}")
    print(f"  Copy Config: {acc_901351.get('copy_trading_config', 'None')}")
    
    print("\n📊 Account 901353:")
    print(f"  Password: {acc_901353.get('password', 'NOT SET')}")
    print(f"  Broker: {acc_901353.get('broker', 'NOT SET')}")
    print(f"  Server: {acc_901353.get('server', 'NOT SET')}")
    print(f"  Manager Assigned: {acc_901353.get('manager_assigned', 'None')}")
    print(f"  Fund Type: {acc_901353.get('fund_type', 'None')}")
    print(f"  Trading Platform: {acc_901353.get('trading_platform', 'None')}")
    print(f"  Copy Config: {acc_901353.get('copy_trading_config', 'None')}")
    
    print("\n" + "="*60)
    print("✅ PHASE 0 COMPLETE!")
    print("="*60)
    print("Both accounts updated with:")
    print("  ✅ Password: Fidus13!")
    print("  ✅ New assignment fields (manager, fund, platform)")
    print("  ✅ Account 901353 configured as copy account")
    print("\nReady for Phase 1: Backend API Development! 🚀")
    print("="*60)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(update_accounts())
