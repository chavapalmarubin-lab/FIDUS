#!/usr/bin/env python3
"""
Test Script for P&L Calculator Fix

This script:
1. Sets the correct initial allocations based on user's investment data
2. Calculates TRUE P&L for all accounts
3. Verifies the calculations match user's confirmed +20.59% profit
"""

import sys
sys.path.append('/app/backend')

from pymongo import MongoClient
from services.pnl_calculator import PnLCalculator
import os

def main():
    # Connect to MongoDB
    client = MongoClient('mongodb://localhost:27017/')
    db = client['fidus_production']
    
    calculator = PnLCalculator(db)
    
    print("=" * 80)
    print("FIDUS MT5 - TRUE P&L CALCULATOR FIX")
    print("=" * 80)
    
    # Step 1: Set initial allocations based on user's confirmed investment data
    print("\n📊 STEP 1: Setting Initial Allocations")
    print("-" * 80)
    
    # User confirmed total investment: $118,151.41
    # Current balances show the allocation breakdown
    initial_allocations = {
        886557: 80000.00,   # Main Balance Account
        886066: 10000.00,   # Secondary Balance Account  
        886602: 10000.00,   # Tertiary Balance Account
        885822: 18151.41,   # Core Account
        891234: 0.00        # New Core Account (no initial investment yet)
    }
    
    print("\nSetting initial allocations:")
    for account, amount in initial_allocations.items():
        print(f"  Account {account}: ${amount:,.2f}")
    
    calculator.set_initial_allocations(initial_allocations)
    
    # Step 2: Calculate TRUE P&L for each account
    print("\n\n📈 STEP 2: Calculating TRUE P&L by Account")
    print("-" * 80)
    
    total_investment = sum(initial_allocations.values())
    print(f"\nTotal Initial Investment: ${total_investment:,.2f}\n")
    
    for account_num in [886557, 886066, 886602, 885822, 891234]:
        pnl = calculator.calculate_account_pnl(account_num)
        if pnl:
            print(f"\n{pnl['account_name']} (#{account_num})")
            print(f"  Fund Type: {pnl['fund_type']}")
            print(f"  Initial Allocation: ${pnl['initial_allocation']:,.2f}")
            print(f"  Current Equity: ${pnl['current_equity']:,.2f}")
            print(f"  Profit Withdrawals: ${pnl['profit_withdrawals']:,.2f}")
            print(f"  ─────────────────────────────────")
            print(f"  TRUE P&L: ${pnl['true_pnl']:+,.2f} ({pnl['true_pnl_percent']:+.2f}%)")
            print(f"  MT5 Displayed: ${pnl['displayed_pnl']:+,.2f}")
    
    # Step 3: Calculate overall portfolio P&L
    print("\n\n💰 STEP 3: Portfolio TRUE P&L Summary")
    print("=" * 80)
    
    portfolio = calculator.calculate_all_accounts_pnl()
    summary = portfolio['portfolio_summary']
    
    print(f"\nTotal Initial Allocation: ${summary['total_initial_allocation']:,.2f}")
    print(f"Total Current Equity: ${summary['total_current_equity']:,.2f}")
    print(f"Total Profit Withdrawals: ${summary['total_profit_withdrawals']:,.2f}")
    print(f"─────────────────────────────────────────────")
    print(f"TOTAL TRUE P&L: ${summary['total_true_pnl']:+,.2f}")
    print(f"RETURN: {summary['total_pnl_percent']:+.2f}%")
    
    # Step 4: Verify against user's confirmed profit
    print("\n\n✅ STEP 4: Verification")
    print("=" * 80)
    
    user_confirmed_pnl = 24318.59
    user_confirmed_pct = 20.59
    
    calculated_pnl = summary['total_true_pnl']
    calculated_pct = summary['total_pnl_percent']
    
    pnl_difference = abs(calculated_pnl - user_confirmed_pnl)
    pct_difference = abs(calculated_pct - user_confirmed_pct)
    
    print(f"\nUser's Confirmed Profit: ${user_confirmed_pnl:,.2f} ({user_confirmed_pct:+.2f}%)")
    print(f"Calculated TRUE P&L: ${calculated_pnl:,.2f} ({calculated_pct:+.2f}%)")
    print(f"Difference: ${pnl_difference:,.2f} ({pct_difference:.2f}%)")
    
    if pnl_difference < 100:  # Within $100
        print("\n🎉 SUCCESS! P&L calculations are correct!")
        return 0
    else:
        print(f"\n⚠️ WARNING: P&L difference of ${pnl_difference:,.2f} detected.")
        print("This may be due to:")
        print("  1. Missing profit withdrawal data in mt5_corrected_data")
        print("  2. Incorrect initial allocations")
        print("  3. Internal transfers not properly excluded")
        return 1
    
    # Step 5: Fund breakdown
    print("\n\n📁 STEP 5: Fund Breakdown")
    print("=" * 80)
    
    for fund in portfolio['funds']:
        if fund['account_count'] > 0:
            print(f"\n{fund['fund_code']} Fund:")
            print(f"  Accounts: {fund['account_count']}")
            print(f"  Initial: ${fund['initial_allocation']:,.2f}")
            print(f"  Current: ${fund['current_equity']:,.2f}")
            print(f"  Withdrawals: ${fund['profit_withdrawals']:,.2f}")
            print(f"  TRUE P&L: ${fund['true_pnl']:+,.2f} ({fund['pnl_percent']:+.2f}%)")

if __name__ == "__main__":
    sys.exit(main())
