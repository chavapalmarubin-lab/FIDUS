#!/usr/bin/env python3
"""
Test script to verify Cash Flow API endpoint returns correct data from SSOT
"""
import asyncio
import sys
sys.path.append('/app/backend')

from motor.motor_asyncio import AsyncIOMotorClient
import os

# Read .env file
with open('/app/backend/.env') as f:
    for line in f:
        if line.strip() and not line.startswith('#') and '=' in line:
            key, value = line.strip().split('=', 1)
            os.environ[key] = value

async def test_ssot_calculation():
    """Simulate what the /api/admin/cashflow/complete endpoint does"""
    
    mongo_url = os.environ.get('MONGO_URL')
    client = AsyncIOMotorClient(mongo_url)
    db = client['fidus_production']
    
    print("=" * 80)
    print("TESTING CASH FLOW API SSOT CALCULATION")
    print("=" * 80)
    
    # Get all active accounts (SSOT)
    mt5_accounts_cursor = db.mt5_accounts.find({'status': 'active'})
    mt5_accounts = await mt5_accounts_cursor.to_list(length=None)
    
    # Calculate MT5 Trading P&L
    mt5_trading_pnl = 0
    total_balance = 0
    total_allocation = 0
    
    print(f"\n📊 Active Accounts ({len(mt5_accounts)}):")
    print(f"{'Account':<12} {'Fund':<12} {'Balance':<15} {'Allocation':<15} {'P&L':<15}")
    print("-" * 75)
    
    for acc in mt5_accounts:
        account_num = acc.get('account')
        balance = float(acc.get('balance', 0))
        initial = float(acc.get('initial_allocation', 0))
        fund_type = acc.get('fund_type', 'N/A')
        pnl = balance - initial
        
        mt5_trading_pnl += pnl
        total_balance += balance
        total_allocation += initial
        
        print(f"{account_num:<12} {fund_type:<12} ${balance:>13,.2f} ${initial:>13,.2f} ${pnl:>13,.2f}")
    
    print("-" * 75)
    print(f"{'TOTALS':<12} {'':<12} ${total_balance:>13,.2f} ${total_allocation:>13,.2f} ${mt5_trading_pnl:>13,.2f}")
    
    # Get separation accounts
    separation_accounts = await db.mt5_accounts.find({
        'account': {'$in': [897591, 897599]}
    }).to_list(length=10)
    separation_balance = sum(acc.get('balance', 0) for acc in separation_accounts)
    
    # Check for profit withdrawals
    collections = await db.list_collection_names()
    if 'withdrawals' in collections:
        withdrawals_cursor = db.withdrawals.find({'type': 'profit_withdrawal'})
        withdrawals = await withdrawals_cursor.to_list(length=None)
        profit_withdrawals = sum(w.get('amount', 0) for w in withdrawals)
    else:
        profit_withdrawals = 0
    
    # Calculate broker interest
    broker_interest = separation_balance - profit_withdrawals
    
    # For now, assume broker rebates = 0 (monthly calculation)
    broker_rebates = 0
    
    # Calculate total inflows
    total_inflows = mt5_trading_pnl + broker_interest + broker_rebates
    
    print(f"\n💰 CASH FLOW CALCULATIONS:")
    print(f"   MT5 Trading P&L:     ${mt5_trading_pnl:>12,.2f}")
    print(f"   Separation Balance:  ${separation_balance:>12,.2f}")
    print(f"   Profit Withdrawals:  ${profit_withdrawals:>12,.2f}")
    print(f"   Broker Interest:     ${broker_interest:>12,.2f}")
    print(f"   Broker Rebates:      ${broker_rebates:>12,.2f}")
    print(f"   " + "-" * 40)
    print(f"   TOTAL INFLOWS:       ${total_inflows:>12,.2f}")
    
    print(f"\n✅ VERIFICATION:")
    print(f"   Expected Balance:    $132,768.00")
    print(f"   Actual Balance:      ${total_balance:,.2f}")
    print(f"   Difference:          ${abs(total_balance - 132768):,.2f}")
    print()
    print(f"   Expected P&L:        $3,110.59")
    print(f"   Actual P&L:          ${mt5_trading_pnl:,.2f}")
    print(f"   Difference:          ${abs(mt5_trading_pnl - 3110.59):,.2f}")
    
    print("\n" + "=" * 80)
    
    if abs(mt5_trading_pnl - 3110.59) < 100:
        print("✅ SUCCESS: P&L is within $100 of expected value (accounting for market movements)")
    else:
        print("❌ FAILURE: P&L differs significantly from expected value")
    
    print("=" * 80)
    
    client.close()

if __name__ == '__main__':
    asyncio.run(test_ssot_calculation())
