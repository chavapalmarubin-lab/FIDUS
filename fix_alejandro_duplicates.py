#!/usr/bin/env python3
"""
FIX ALEJANDRO DUPLICATE INVESTMENTS
Remove duplicate investments and standardize client_id
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import json

# MongoDB connection
mongo_url = "mongodb+srv://chavapalmarubin_db_user:2170Tenoch!@fidus.y1p9be2.mongodb.net/fidus_production?retryWrites=true&w=majority"
client = AsyncIOMotorClient(mongo_url)
db = client["fidus_production"]

async def fix_alejandro_duplicates():
    """Fix duplicate Alejandro investments"""
    print("🔧 FIXING ALEJANDRO DUPLICATE INVESTMENTS")
    print("=" * 50)
    
    # Step 1: Check current state
    print("\n1. CURRENT STATE:")
    investments = await db.investments.find({
        "client_id": {"$in": ["client_alejandro", "client_alejandro_mariscal"]}
    }).to_list(length=10)
    
    print(f"Found {len(investments)} Alejandro investments:")
    for inv in investments:
        print(f"  - ID: {inv.get('_id')}, Client: {inv.get('client_id')}, Fund: {inv.get('fund_code')}, Amount: ${inv.get('principal_amount', 0):,.2f}")
    
    # Step 2: Delete client_alejandro_mariscal investments (duplicates)
    print("\n2. REMOVING DUPLICATE INVESTMENTS:")
    delete_result = await db.investments.delete_many({
        "client_id": "client_alejandro_mariscal"
    })
    
    print(f"Deleted {delete_result.deleted_count} duplicate investments for client_alejandro_mariscal")
    
    # Step 3: Update MT5 accounts to use client_alejandro
    print("\n3. UPDATING MT5 ACCOUNTS:")
    mt5_update_result = await db.mt5_accounts.update_many(
        {"client_id": None},
        {"$set": {"client_id": "client_alejandro"}}
    )
    
    print(f"Updated {mt5_update_result.modified_count} MT5 accounts to use client_alejandro")
    
    # Step 4: Verify final state
    print("\n4. FINAL STATE:")
    final_investments = await db.investments.find({
        "client_id": {"$in": ["client_alejandro", "client_alejandro_mariscal"]}
    }).to_list(length=10)
    
    print(f"Remaining Alejandro investments: {len(final_investments)}")
    total_aum = 0
    for inv in final_investments:
        amount = inv.get('principal_amount', 0)
        total_aum += amount
        print(f"  - Client: {inv.get('client_id')}, Fund: {inv.get('fund_code')}, Amount: ${amount:,.2f}")
    
    print(f"Total AUM: ${total_aum:,.2f}")
    
    # Check MT5 accounts
    mt5_accounts = await db.mt5_accounts.find({}).to_list(length=20)
    print(f"\nMT5 accounts: {len(mt5_accounts)}")
    for account in mt5_accounts:
        print(f"  - Account: {account.get('account')}, Client: {account.get('client_id')}, Fund: {account.get('fund_type')}")

async def main():
    try:
        await fix_alejandro_duplicates()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(main())