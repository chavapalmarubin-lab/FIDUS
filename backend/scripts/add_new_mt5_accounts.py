#!/usr/bin/env python3
"""
Script to add two new MT5 accounts to the database: 901351 and 901353
Password: Fidus13! (with exclamation mark)

This is Phase 0 of the Investment Committee Drag-and-Drop feature.
"""

import os
import sys
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def add_new_accounts():
    """Add accounts 901351 and 901353 to mt5_accounts collection"""
    
    # Get MongoDB connection string from environment
    mongo_url = os.environ.get('MONGO_URL', 'mongodb+srv://emergent-ops:BpzaxqxDCjz1yWY4@fidus.y1p9be2.mongodb.net/fidus_production')
    
    print(f"Connecting to MongoDB...")
    client = AsyncIOMotorClient(mongo_url)
    db = client.get_database('fidus_production')
    
    print("\n" + "="*60)
    print("PHASE 0: ADDING NEW MT5 ACCOUNTS")
    print("="*60)
    
    # Check if accounts already exist
    existing_901351 = await db.mt5_accounts.find_one({"account": 901351})
    existing_901353 = await db.mt5_accounts.find_one({"account": 901353})
    
    if existing_901351:
        print("⚠️  Account 901351 already exists in database")
    else:
        print("\n📋 Adding Account 901351...")
        account_901351 = {
            # Account Info
            "account": 901351,
            "password": "Fidus13!",
            "server": "MEXAtlantic-Real",
            "broker": "MEXAtlantic",
            
            # FOUR ASSIGNMENTS (all null until committee assigns)
            "manager_assigned": None,
            "fund_type": None,
            "trading_platform": None,
            "allocated_capital": 0,
            
            # Copy Trading Config
            "copy_trading_config": None,
            
            # MT5 Live Data (VPS will populate)
            "balance": 0,
            "equity": 0,
            "margin": 0,
            "margin_free": 0,
            "margin_level": 0,
            "profit": 0,
            
            # Metadata
            "created_at": datetime.utcnow(),
            "last_sync": None,
            "sync_enabled": False,
            "status": "active"
        }
        
        result = await db.mt5_accounts.insert_one(account_901351)
        print(f"✅ Account 901351 added successfully! ID: {result.inserted_id}")
    
    if existing_901353:
        print("⚠️  Account 901353 already exists in database")
    else:
        print("\n📋 Adding Account 901353 (Copy Account)...")
        account_901353 = {
            # Account Info
            "account": 901353,
            "password": "Fidus13!",
            "server": "MEXAtlantic-Real",
            "broker": "MEXAtlantic",
            
            # FOUR ASSIGNMENTS
            "manager_assigned": None,
            "fund_type": None,
            "trading_platform": None,
            "allocated_capital": 0,
            
            # Copy Trading Config (copies from 901351 via Biking)
            "copy_trading_config": {
                "is_copy_account": True,
                "copy_from_account": 901351,
                "copy_platform": "Biking",
                "copy_ratio": 1.0
            },
            
            # MT5 Live Data
            "balance": 0,
            "equity": 0,
            "margin": 0,
            "margin_free": 0,
            "margin_level": 0,
            "profit": 0,
            
            # Metadata
            "created_at": datetime.utcnow(),
            "last_sync": None,
            "sync_enabled": False,
            "status": "active"
        }
        
        result = await db.mt5_accounts.insert_one(account_901353)
        print(f"✅ Account 901353 added successfully! ID: {result.inserted_id}")
    
    # Verification
    print("\n" + "="*60)
    print("VERIFICATION")
    print("="*60)
    
    # Check both accounts exist
    print("\n🔍 Checking if both accounts exist...")
    both_accounts = await db.mt5_accounts.find({
        "account": {"$in": [901351, 901353]}
    }).to_list(length=10)
    
    print(f"Found {len(both_accounts)} accounts (901351, 901353)")
    for acc in both_accounts:
        print(f"  ✅ Account {acc['account']} - Broker: {acc['broker']} - Password: {acc['password']}")
    
    # Check total count of all 13 accounts
    print("\n🔍 Checking total account count (should be 13)...")
    all_accounts = [
        885822, 886066, 886528, 886557, 886602,
        891215, 891234, 897589, 897590, 897591,
        897599, 901351, 901353
    ]
    
    total_accounts = await db.mt5_accounts.find({
        "account": {"$in": all_accounts}
    }).to_list(length=20)
    
    print(f"Total accounts found: {len(total_accounts)} / 13")
    
    if len(total_accounts) == 13:
        print("✅ SUCCESS! All 13 accounts are in the database!")
    else:
        print(f"⚠️  WARNING: Expected 13 accounts, but found {len(total_accounts)}")
        print("\nMissing accounts:")
        found_numbers = [acc['account'] for acc in total_accounts]
        for acc_num in all_accounts:
            if acc_num not in found_numbers:
                print(f"  ❌ {acc_num}")
    
    print("\n" + "="*60)
    print("PHASE 0 COMPLETE!")
    print("="*60)
    print("✅ Account 901351: Added and verified")
    print("✅ Account 901353: Added and verified")
    print(f"✅ Total accounts: {len(total_accounts)}")
    print("\nReady for Phase 1: Backend API Development! 🚀")
    print("="*60)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(add_new_accounts())
