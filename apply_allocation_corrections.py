#!/usr/bin/env python3
"""
Apply Allocation Corrections
1. Account 2198: $20,000 → $10,000 (already done)
2. Account 886602: $16,000 → $21,000
3. Account 33200931: Manager "Money Manager" → "Spaniard Stock CFDs"
4. Update Spaniard Stock CFDs profile URL
Date: November 25, 2025
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')
mongo_url = os.environ['MONGO_URL']

async def apply_corrections():
    client = AsyncIOMotorClient(mongo_url)
    db = client['fidus_production']
    
    print("=" * 80)
    print("APPLYING ALLOCATION CORRECTIONS")
    print("=" * 80)
    
    # Update 1: Account 2198 (already done, verify)
    print("\n1️⃣ Account 2198:")
    acc_2198 = await db.mt5_accounts.find_one({'account': 2198}, {'_id': 0, 'initial_allocation': 1, 'balance': 1})
    current_alloc = acc_2198.get('initial_allocation', 0)
    if current_alloc == 10000:
        print(f"   ✅ Already corrected: ${current_alloc:,.2f}")
    else:
        print(f"   ⚠️  Current: ${current_alloc:,.2f}, updating to $10,000")
        await db.mt5_accounts.update_one(
            {'account': 2198},
            {'$set': {'initial_allocation': 10000}}
        )
        print(f"   ✅ Updated to $10,000")
    
    # Update 2: Account 886602
    print("\n2️⃣ Account 886602:")
    acc_886602_before = await db.mt5_accounts.find_one({'account': 886602}, {'_id': 0, 'initial_allocation': 1, 'balance': 1})
    old_alloc = acc_886602_before.get('initial_allocation', 0)
    balance = acc_886602_before.get('balance', 0)
    
    print(f"   Before: Allocation ${old_alloc:,.2f}, Balance ${balance:,.2f}, P&L ${balance - old_alloc:,.2f}")
    
    result = await db.mt5_accounts.update_one(
        {'account': 886602},
        {'$set': {
            'initial_allocation': 21000,
            'calculated_pnl': balance - 21000
        }}
    )
    
    acc_886602_after = await db.mt5_accounts.find_one({'account': 886602}, {'_id': 0, 'initial_allocation': 1, 'balance': 1})
    new_alloc = acc_886602_after.get('initial_allocation', 0)
    
    print(f"   After:  Allocation ${new_alloc:,.2f}, Balance ${balance:,.2f}, P&L ${balance - new_alloc:,.2f}")
    print(f"   ✅ Updated: {result.modified_count} document(s)")
    
    # Update 3: Account 33200931 manager
    print("\n3️⃣ Account 33200931 Manager:")
    acc_33200931_before = await db.mt5_accounts.find_one({'account': 33200931}, {'_id': 0, 'manager_name': 1})
    old_manager = acc_33200931_before.get('manager_name', 'Unknown')
    
    print(f"   Before: {old_manager}")
    
    result = await db.mt5_accounts.update_one(
        {'account': 33200931},
        {'$set': {'manager_name': 'Spaniard Stock CFDs'}}
    )
    
    print(f"   After:  Spaniard Stock CFDs")
    print(f"   ✅ Updated: {result.modified_count} document(s)")
    
    # Update 4: Spaniard Stock CFDs profile URL
    print("\n4️⃣ Spaniard Stock CFDs Profile URL:")
    manager_before = await db.money_managers.find_one({'name': 'Spaniard Stock CFDs'}, {'_id': 0, 'profile_url': 1})
    
    if manager_before:
        old_url = manager_before.get('profile_url', 'None')
        print(f"   Before: {old_url}")
    else:
        print(f"   Manager not found in money_managers collection")
    
    result = await db.money_managers.update_one(
        {'name': 'Spaniard Stock CFDs'},
        {'$set': {
            'profile_url': 'https://ratings.mexatlantic.com/widgets/ratings/6260?widgetKey=social_platform_ratings',
            'rating_url': 'https://ratings.mexatlantic.com/widgets/ratings/6260?widgetKey=social_platform_ratings'
        }},
        upsert=True
    )
    
    print(f"   After:  https://ratings.mexatlantic.com/widgets/ratings/6260?widgetKey=social_platform_ratings")
    print(f"   ✅ Updated: {result.modified_count} document(s)")
    
    # Summary
    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    
    # Verify all changes
    acc_2198 = await db.mt5_accounts.find_one({'account': 2198}, {'_id': 0, 'initial_allocation': 1, 'balance': 1})
    acc_886602 = await db.mt5_accounts.find_one({'account': 886602}, {'_id': 0, 'initial_allocation': 1, 'balance': 1})
    acc_33200931 = await db.mt5_accounts.find_one({'account': 33200931}, {'_id': 0, 'manager_name': 1, 'initial_allocation': 1, 'balance': 1})
    
    print(f"\nAccount 2198:")
    print(f"  Allocation: ${acc_2198.get('initial_allocation', 0):,.2f} (expected: $10,000)")
    print(f"  Balance: ${acc_2198.get('balance', 0):,.2f}")
    print(f"  P&L: ${acc_2198.get('balance', 0) - acc_2198.get('initial_allocation', 0):,.2f}")
    
    print(f"\nAccount 886602:")
    print(f"  Allocation: ${acc_886602.get('initial_allocation', 0):,.2f} (expected: $21,000)")
    print(f"  Balance: ${acc_886602.get('balance', 0):,.2f}")
    print(f"  P&L: ${acc_886602.get('balance', 0) - acc_886602.get('initial_allocation', 0):,.2f}")
    
    print(f"\nAccount 33200931:")
    print(f"  Manager: {acc_33200931.get('manager_name', 'Unknown')} (expected: Spaniard Stock CFDs)")
    print(f"  Allocation: ${acc_33200931.get('initial_allocation', 0):,.2f}")
    print(f"  Balance: ${acc_33200931.get('balance', 0):,.2f}")
    
    # Calculate new totals
    pipeline = [
        {"$match": {"status": "active"}},
        {"$group": {
            "_id": None,
            "total_allocation": {"$sum": "$initial_allocation"},
            "total_balance": {"$sum": "$balance"}
        }}
    ]
    
    totals = await db.mt5_accounts.aggregate(pipeline).to_list(1)
    if totals:
        total_allocation = totals[0].get('total_allocation', 0)
        total_balance = totals[0].get('total_balance', 0)
        total_pnl = total_balance - total_allocation
        
        print("\n" + "=" * 80)
        print("NEW PORTFOLIO TOTALS")
        print("=" * 80)
        print(f"Total Allocation: ${total_allocation:,.2f} (expected: $129,657.41)")
        print(f"Total Balance: ${total_balance:,.2f}")
        print(f"Total P&L: ${total_pnl:,.2f}")
        print("=" * 80)
    
    print("\n✅ ALL CORRECTIONS APPLIED SUCCESSFULLY")
    
    client.close()

if __name__ == '__main__':
    asyncio.run(apply_corrections())
