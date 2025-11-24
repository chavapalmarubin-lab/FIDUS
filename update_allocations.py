#!/usr/bin/env python3
"""
Update MT5 Account Allocations
Based on Master Account Table provided by user
Date: November 24, 2025
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')
mongo_url = os.environ['MONGO_URL']

# Master allocation data from user's table
ALLOCATIONS = {
    885822: 2151.41,
    886066: 0,
    886528: 0,
    886557: 0,
    886602: 16000,
    891215: 20000,
    891234: 0,
    897589: 20000,
    897590: 16000,
    897591: 0,
    897599: 15506,
    901351: 15000,
    901353: 0,
    2198: 20000,
    33200931: 10000
}

async def update_allocations():
    client = AsyncIOMotorClient(mongo_url)
    db = client['fidus_production']
    
    print("=" * 80)
    print("UPDATING MT5 ACCOUNT ALLOCATIONS")
    print("=" * 80)
    
    updated_count = 0
    
    for account_number, allocation in ALLOCATIONS.items():
        result = await db.mt5_accounts.update_one(
            {"account": account_number},
            {"$set": {"balance": allocation}}
        )
        
        if result.matched_count > 0:
            print(f"✅ Account {account_number}: Updated balance to ${allocation:,.2f}")
            updated_count += 1
        else:
            print(f"⚠️  Account {account_number}: Not found in database")
    
    print("\n" + "=" * 80)
    print(f"SUMMARY: Updated {updated_count} out of {len(ALLOCATIONS)} accounts")
    print("=" * 80)
    
    # Verify totals by fund type
    print("\n📊 FUND ALLOCATION VERIFICATION:")
    print("-" * 80)
    
    pipeline = [
        {"$match": {"status": "active"}},
        {"$group": {
            "_id": "$fund_type",
            "total_balance": {"$sum": "$balance"},
            "account_count": {"$sum": 1}
        }},
        {"$sort": {"_id": 1}}
    ]
    
    funds = await db.mt5_accounts.aggregate(pipeline).to_list(None)
    
    total_all_funds = 0
    for fund in funds:
        fund_type = fund['_id']
        total = fund['total_balance']
        count = fund['account_count']
        print(f"{fund_type:12} ${total:>12,.2f} ({count} accounts)")
        total_all_funds += total
    
    print("-" * 80)
    print(f"{'TOTAL':12} ${total_all_funds:>12,.2f}")
    print("-" * 80)
    
    # Expected totals
    print("\n📋 EXPECTED vs ACTUAL:")
    print("-" * 80)
    expected = {
        'CORE': 18151.41,
        'BALANCE': 81000.00,
        'SEPARATION': 35506.00
    }
    
    for fund_type, expected_total in expected.items():
        actual_fund = next((f for f in funds if f['_id'] == fund_type), None)
        actual_total = actual_fund['total_balance'] if actual_fund else 0
        match = "✅" if abs(actual_total - expected_total) < 0.01 else "❌"
        print(f"{match} {fund_type:12} Expected: ${expected_total:>10,.2f}  Actual: ${actual_total:>10,.2f}")
    
    expected_grand_total = sum(expected.values())
    match = "✅" if abs(total_all_funds - expected_grand_total) < 0.01 else "❌"
    print(f"{match} {'TOTAL':12} Expected: ${expected_grand_total:>10,.2f}  Actual: ${total_all_funds:>10,.2f}")
    
    print("\n" + "=" * 80)
    print("✅ ALLOCATION UPDATE COMPLETE")
    print("=" * 80)
    
    client.close()

if __name__ == '__main__':
    asyncio.run(update_allocations())
