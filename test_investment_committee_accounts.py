#!/usr/bin/env python3
"""
Test that Investment Committee returns all 15 accounts
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os

with open('/app/backend/.env') as f:
    for line in f:
        if line.strip() and not line.startswith('#') and '=' in line:
            key, value = line.strip().split('=', 1)
            os.environ[key] = value

ALL_MT5_ACCOUNTS = [
    885822, 886066, 886528, 886557, 886602,
    891215, 891234, 897589, 897590, 897591,
    897599, 901351, 901353, 2198
]

ALL_MT4_ACCOUNTS = [
    33200931
]

ALL_ACCOUNTS = ALL_MT5_ACCOUNTS + ALL_MT4_ACCOUNTS

async def test_accounts():
    mongo_url = os.environ.get('MONGO_URL')
    client = AsyncIOMotorClient(mongo_url)
    db = client['fidus_production']
    
    print("=" * 80)
    print("INVESTMENT COMMITTEE ACCOUNTS TEST")
    print("=" * 80)
    
    print(f"\n📋 Expected Accounts: {len(ALL_ACCOUNTS)}")
    print(f"   MT5: {len(ALL_MT5_ACCOUNTS)}")
    print(f"   MT4: {len(ALL_MT4_ACCOUNTS)}")
    
    # Fetch accounts using the same query as the API
    accounts = await db.mt5_accounts.find({
        "account": {"$in": ALL_ACCOUNTS}
    }, {"_id": 0}).to_list(length=50)
    
    print(f"\n✅ Found in Database: {len(accounts)}")
    
    # Sort by platform and account number
    def sort_key(acc):
        platform_order = {"MT5": 0, "MT4": 1}
        platform = acc.get("platform", "MT5")
        return (platform_order.get(platform, 2), acc["account"])
    
    accounts_sorted = sorted(accounts, key=sort_key)
    
    print(f"\n{'Account':<12} {'Platform':<10} {'Fund':<15} {'Manager':<25} {'Balance':<15}")
    print("-" * 85)
    
    for acc in accounts_sorted:
        account_num = acc.get('account', 'N/A')
        platform = acc.get('platform', 'MT5')
        fund_type = acc.get('fund_type', 'Unassigned')
        manager = acc.get('manager_name', 'Unassigned')
        balance = acc.get('balance', 0)
        
        print(f"{account_num:<12} {platform:<10} {fund_type:<15} {manager:<25} ${balance:>13,.2f}")
    
    print("-" * 85)
    
    # Check for missing accounts
    found_accounts = [acc['account'] for acc in accounts]
    missing = [acc for acc in ALL_ACCOUNTS if acc not in found_accounts]
    
    if missing:
        print(f"\n❌ MISSING ACCOUNTS: {missing}")
    else:
        print(f"\n✅ ALL {len(ALL_ACCOUNTS)} ACCOUNTS FOUND!")
    
    # Group by platform
    mt5_found = [acc for acc in accounts if acc.get('platform', 'MT5') == 'MT5']
    mt4_found = [acc for acc in accounts if acc.get('platform') == 'MT4']
    
    print(f"\n📊 Platform Breakdown:")
    print(f"   MT5: {len(mt5_found)}/{len(ALL_MT5_ACCOUNTS)}")
    print(f"   MT4: {len(mt4_found)}/{len(ALL_MT4_ACCOUNTS)}")
    
    client.close()

asyncio.run(test_accounts())
