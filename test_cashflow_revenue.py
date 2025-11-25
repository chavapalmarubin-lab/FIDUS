#!/usr/bin/env python3
"""
Test Cash Flow Revenue Calculations
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os

with open('/app/backend/.env') as f:
    for line in f:
        if line.strip() and not line.startswith('#') and '=' in line:
            key, value = line.strip().split('=', 1)
            os.environ[key] = value

async def test_cashflow_revenue():
    mongo_url = os.environ.get('MONGO_URL')
    client = AsyncIOMotorClient(mongo_url)
    db = client['fidus_production']
    
    print("=" * 80)
    print("CASH FLOW REVENUE & OBLIGATIONS CALCULATIONS")
    print("=" * 80)
    
    # Get all accounts for total equity
    accounts = await db.mt5_accounts.find({}).to_list(100)
    total_equity = sum(float(acc.get('equity', 0)) for acc in accounts)
    
    print(f"\n📊 FUND ASSETS (Top Section)")
    print("-" * 80)
    print(f"  Total Equity (15 Accounts):      ${total_equity:>13,.2f}")
    print(f"  Broker Rebates:                   ${202:>13,.2f}")
    print(f"  " + "─" * 50)
    print(f"  Total Fund Assets:                ${total_equity + 202:>13,.2f}")
    
    # Calculate Fund Revenue
    client_money = 118151.41  # Fixed value
    fund_revenue = total_equity - client_money
    
    print(f"\n📊 FUND REVENUE (Bottom Section)")
    print("-" * 80)
    print(f"  Total Equity:                     ${total_equity:>13,.2f}")
    print(f"  Client Money (Investment):        ${client_money:>13,.2f}")
    print(f"  " + "─" * 50)
    print(f"  Fund Revenue:                     ${fund_revenue:>13,.2f}")
    
    # Get client interest obligations
    investments = await db.investments.find({'status': 'active'}).to_list(100)
    
    client_interest_obligations = 0
    
    print(f"\n📊 INVESTMENTS BREAKDOWN")
    print("-" * 80)
    print(f"  {'Client ID':<15} {'Fund Type':<12} {'Principal':<15} {'Rate':<8} {'Interest':<15}")
    print("-" * 80)
    
    for inv in investments:
        client_id = inv.get('client_id', 'N/A')
        principal = inv.get('principal_amount', 0)
        interest_rate = inv.get('interest_rate', 0)
        fund_type = inv.get('fund_type', '')
        
        # Calculate interest
        if 'CORE' in fund_type.upper():
            total_interest = principal * interest_rate * 12
        elif 'BALANCE' in fund_type.upper():
            total_interest = principal * interest_rate * 12
        else:
            total_interest = 0
        
        client_interest_obligations += total_interest
        
        print(f"  {client_id:<15} {fund_type:<12} ${principal:>13,.2f} {interest_rate*100:>6.2f}% ${total_interest:>13,.2f}")
    
    print("-" * 80)
    print(f"  {'TOTAL':<15} {'':<12} {'':<15} {'':<8} ${client_interest_obligations:>13,.2f}")
    
    # Fund Obligations
    fund_obligations = client_interest_obligations
    upcoming_redemptions = 0
    manager_fees = 0
    
    print(f"\n📊 FUND LIABILITIES (Obligations)")
    print("-" * 80)
    print(f"  Client Interest Obligations:      ${client_interest_obligations:>13,.2f}")
    print(f"  Upcoming Redemptions:             ${upcoming_redemptions:>13,.2f}")
    print(f"  Manager Performance Fees:         ${manager_fees:>13,.2f}")
    print(f"  " + "─" * 50)
    print(f"  Total Fund Obligations:           ${fund_obligations:>13,.2f}")
    
    # Net Profit
    net_profit = fund_revenue - fund_obligations
    
    print(f"\n📊 NET FUND PROFITABILITY")
    print("-" * 80)
    print(f"  Fund Revenue:                     ${fund_revenue:>13,.2f}")
    print(f"  Fund Obligations:                 ${fund_obligations:>13,.2f}")
    print(f"  " + "─" * 50)
    print(f"  Net Profit:                       ${net_profit:>13,.2f}")
    
    # Comparison with user's expected values
    print("\n" + "=" * 80)
    print("✅ VERIFICATION (User's Expected Values)")
    print("=" * 80)
    
    expected = {
        'fund_revenue': 12828.36,
        'fund_obligations': 33267,
        'net_profit': -20438.64
    }
    
    checks = [
        ("Fund Revenue", fund_revenue, expected['fund_revenue']),
        ("Fund Obligations", fund_obligations, expected['fund_obligations']),
        ("Net Profit", net_profit, expected['net_profit'])
    ]
    
    print()
    all_passed = True
    for name, actual, expected_val in checks:
        diff = abs(actual - expected_val)
        status = "✅" if diff < 100 else "⚠️"
        print(f"{status} {name}:")
        print(f"   Expected: ${expected_val:>13,.2f}")
        print(f"   Actual:   ${actual:>13,.2f}")
        print(f"   Diff:     ${diff:>13,.2f}")
        print()
        if diff >= 100:
            all_passed = False
    
    if all_passed:
        print("🎉 ALL CALCULATIONS MATCH EXPECTED VALUES!")
    else:
        print("⚠️  Some calculations differ from expected values")
    
    client.close()

asyncio.run(test_cashflow_revenue())
