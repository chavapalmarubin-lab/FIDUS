#!/usr/bin/env python3
"""
Add Initial Allocation Field to MT5 Accounts
This field is used for TRUE P&L calculation: P&L = Balance - Initial Allocation
Date: November 24, 2025
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')
mongo_url = os.environ['MONGO_URL']

# Initial allocations from user's master table
INITIAL_ALLOCATIONS = {
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

async def add_initial_allocations():
    client = AsyncIOMotorClient(mongo_url)
    db = client['fidus_production']
    
    print("=" * 80)
    print("ADDING INITIAL ALLOCATION FIELD TO MT5 ACCOUNTS")
    print("=" * 80)
    
    updated_count = 0
    
    for account_number, allocation in INITIAL_ALLOCATIONS.items():
        # Get current account data
        account = await db.mt5_accounts.find_one({"account": account_number})
        
        if account:
            current_balance = account.get('balance', 0)
            pnl = current_balance - allocation
            
            result = await db.mt5_accounts.update_one(
                {"account": account_number},
                {"$set": {
                    "initial_allocation": allocation,
                    "calculated_pnl": pnl
                }}
            )
            
            if result.matched_count > 0:
                print(f"✅ Account {account_number}:")
                print(f"   Initial Allocation: ${allocation:>10,.2f}")
                print(f"   Current Balance:    ${current_balance:>10,.2f}")
                print(f"   P&L:                ${pnl:>10,.2f}")
                updated_count += 1
        else:
            print(f"⚠️  Account {account_number}: Not found in database")
    
    print("\n" + "=" * 80)
    print(f"SUMMARY: Added initial_allocation to {updated_count} out of {len(INITIAL_ALLOCATIONS)} accounts")
    print("=" * 80)
    
    # Verify totals by fund type
    print("\n📊 FUND ALLOCATION & P&L SUMMARY:")
    print("-" * 80)
    print(f"{'Fund Type':<15} {'Allocation':>15} {'Balance':>15} {'P&L':>15}")
    print("-" * 80)
    
    pipeline = [
        {"$match": {"status": "active"}},
        {"$group": {
            "_id": "$fund_type",
            "total_allocation": {"$sum": "$initial_allocation"},
            "total_balance": {"$sum": "$balance"},
            "account_count": {"$sum": 1}
        }},
        {"$sort": {"_id": 1}}
    ]
    
    funds = await db.mt5_accounts.aggregate(pipeline).to_list(None)
    
    total_allocation = 0
    total_balance = 0
    
    for fund in funds:
        fund_type = fund['_id']
        allocation = fund['total_allocation']
        balance = fund['total_balance']
        pnl = balance - allocation
        
        print(f"{fund_type:<15} ${allocation:>14,.2f} ${balance:>14,.2f} ${pnl:>14,.2f}")
        
        total_allocation += allocation
        total_balance += balance
    
    total_pnl = total_balance - total_allocation
    
    print("-" * 80)
    print(f"{'TOTAL':<15} ${total_allocation:>14,.2f} ${total_balance:>14,.2f} ${total_pnl:>14,.2f}")
    print("-" * 80)
    
    print("\n" + "=" * 80)
    print("✅ INITIAL ALLOCATION SETUP COMPLETE")
    print("=" * 80)
    print(f"Total Initial Allocation: ${total_allocation:,.2f}")
    print(f"Total Current Balance:    ${total_balance:,.2f}")
    print(f"Total P&L:                ${total_pnl:,.2f}")
    
    client.close()

if __name__ == '__main__':
    asyncio.run(add_initial_allocations())
