#!/usr/bin/env python3
"""
Test simplified Cash Flow API endpoint
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os

with open('/app/backend/.env') as f:
    for line in f:
        if line.strip() and not line.startswith('#') and '=' in line:
            key, value = line.strip().split('=', 1)
            os.environ[key] = value

async def test_simplified_cashflow():
    mongo_url = os.environ.get('MONGO_URL')
    client = AsyncIOMotorClient(mongo_url)
    db = client['fidus_production']
    
    print("=" * 80)
    print("SIMPLIFIED CASH FLOW CALCULATION")
    print("=" * 80)
    
    # Get all accounts
    accounts = await db.mt5_accounts.find({}).to_list(100)
    
    total_equity = 0
    total_balance = 0
    total_allocation = 0
    
    print(f"\n{'Account':<10} {'Status':<10} {'Equity':<15} {'Balance':<15} {'Allocation':<15}")
    print("-" * 70)
    
    for acc in sorted(accounts, key=lambda x: x.get('account')):
        account_num = acc.get('account')
        status = acc.get('status', 'N/A')
        equity = float(acc.get('equity', 0))
        balance = float(acc.get('balance', 0))
        allocation = float(acc.get('initial_allocation', 0))
        
        total_equity += equity
        total_balance += balance
        total_allocation += allocation
        
        print(f"{account_num:<10} {status:<10} ${equity:>13,.2f} ${balance:>13,.2f} ${allocation:>13,.2f}")
    
    print("-" * 70)
    print(f"{'TOTAL':<10} {len(accounts)} accts ${total_equity:>13,.2f} ${total_balance:>13,.2f} ${total_allocation:>13,.2f}")
    
    # Calculate simplified metrics
    broker_rebates = 202
    total_fund_assets = total_equity + broker_rebates
    
    print("\n" + "=" * 80)
    print("SIMPLIFIED FUND ASSETS")
    print("=" * 80)
    
    print(f"\n  Total Equity (15 Accounts):      ${total_equity:>13,.2f}")
    print(f"  (Real-time from all MT5/MT4 accounts)")
    print()
    print(f"  Broker Rebates:                   ${broker_rebates:>13,.2f}")
    print(f"  (Commission from trading volume)")
    print()
    print(f"  " + "─" * 50)
    print(f"  Total Fund Assets:                ${total_fund_assets:>13,.2f}")
    
    print("\n" + "=" * 80)
    print("✅ VERIFICATION")
    print("=" * 80)
    
    print(f"\n  Expected Total Equity: ~$129,948 (from user)")
    print(f"  Actual Total Equity:   ${total_equity:,.2f}")
    print(f"  Difference:            ${abs(total_equity - 129948):,.2f}")
    
    if abs(total_equity - 129948) < 500:
        print(f"\n  ✅ Total Equity is within acceptable range")
    else:
        print(f"\n  ⚠️  Total Equity differs from expected value")
    
    print(f"\n  Expected Total Fund Assets: ~$130,150")
    print(f"  Actual Total Fund Assets:   ${total_fund_assets:,.2f}")
    
    client.close()

asyncio.run(test_simplified_cashflow())
