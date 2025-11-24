#!/usr/bin/env python3
"""
CHECK MT5 ACCOUNT CONFIG
Check what's in the mt5_account_config collection
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import json

# MongoDB connection
mongo_url = "mongodb+srv://chavapalmarubin_db_user:"[CLEANED_PASSWORD]"@fidus.y1p9be2.mongodb.net/fidus_production?retryWrites=true&w=majority"
client = AsyncIOMotorClient(mongo_url)
db = client["fidus_production"]

async def check_mt5_config():
    """Check MT5 account config collection"""
    print("🔍 CHECKING MT5 ACCOUNT CONFIG")
    print("=" * 40)
    
    # Check mt5_account_config collection
    print("\n1. MT5_ACCOUNT_CONFIG COLLECTION:")
    config_accounts = await db.mt5_account_config.find({}).to_list(length=20)
    print(f"Total accounts in mt5_account_config: {len(config_accounts)}")
    
    for account in config_accounts:
        print(f"  - Account: {account.get('account')}, Name: {account.get('name')}, Active: {account.get('is_active')}, Fund: {account.get('fund_type')}")
    
    # Check active accounts specifically
    print("\n2. ACTIVE ACCOUNTS:")
    active_accounts = await db.mt5_account_config.find({"is_active": True}).to_list(length=20)
    print(f"Active accounts: {len(active_accounts)}")
    
    for account in active_accounts:
        print(f"  - Account: {account.get('account')}, Name: {account.get('name')}, Fund: {account.get('fund_type')}")
    
    # Check mt5_accounts collection for comparison
    print("\n3. MT5_ACCOUNTS COLLECTION:")
    mt5_accounts = await db.mt5_accounts.find({}).to_list(length=20)
    print(f"Total accounts in mt5_accounts: {len(mt5_accounts)}")
    
    for account in mt5_accounts:
        print(f"  - Account: {account.get('account')}, Client: {account.get('client_id')}, Fund: {account.get('fund_type')}, Balance: ${account.get('balance', 0):,.2f}")

async def main():
    try:
        await check_mt5_config()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(main())