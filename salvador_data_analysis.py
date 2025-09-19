#!/usr/bin/env python3
"""
SALVADOR PALMA DATA ANALYSIS - FOCUSED ON VT MARKETS CORRECTION
==============================================================

Based on the test results, Salvador has:
- 1 CORE fund investment: $5,000 (could be VT Markets that should be $4,000)
- Multiple BALANCE fund investments: $1,263,485.40 each (DooTechnology)

This script analyzes the specific data correction needed.
"""

import requests
import json

def analyze_salvador_data():
    base_url = "https://wealth-portal-17.preview.emergentagent.com"
    
    # Login as admin
    login_response = requests.post(f"{base_url}/api/auth/login", json={
        "username": "admin", 
        "password": "password123",
        "user_type": "admin"
    })
    
    if login_response.status_code != 200:
        print("❌ Admin login failed")
        return
    
    admin_data = login_response.json()
    token = admin_data.get('token')
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    
    print("🎯 SALVADOR PALMA DATA ANALYSIS")
    print("="*60)
    
    # Get Salvador's investments
    investments_response = requests.get(
        f"{base_url}/api/investments/client/client_003", 
        headers=headers
    )
    
    if investments_response.status_code != 200:
        print("❌ Failed to get Salvador's investments")
        return
    
    investments_data = investments_response.json()
    investments = investments_data.get('investments', [])
    
    print(f"📊 Salvador has {len(investments)} investments:")
    print()
    
    core_investments = []
    balance_investments = []
    
    for i, investment in enumerate(investments, 1):
        fund_code = investment.get('fund_code', 'Unknown')
        principal = investment.get('principal_amount', 0)
        current_value = investment.get('current_value', 0)
        investment_id = investment.get('investment_id', 'Unknown')
        deposit_date = investment.get('deposit_date', 'Unknown')
        
        print(f"Investment {i}:")
        print(f"  - ID: {investment_id}")
        print(f"  - Fund: {fund_code}")
        print(f"  - Principal: ${principal:,.2f}")
        print(f"  - Current Value: ${current_value:,.2f}")
        print(f"  - Deposit Date: {deposit_date}")
        
        if fund_code == 'CORE':
            core_investments.append(investment)
            if principal == 5000.00:
                print(f"  🎯 POTENTIAL VT MARKETS: This CORE investment shows $5,000")
                print(f"      USER REPORT: Should be $4,000 (difference: ${principal - 4000:.2f})")
            elif principal == 4000.00:
                print(f"  ✅ CORRECT VT MARKETS: This CORE investment shows correct $4,000")
        elif fund_code == 'BALANCE':
            balance_investments.append(investment)
            if principal == 1263485.40:
                print(f"  ✅ DOOTECHNOLOGY: This BALANCE investment shows correct $1,263,485.40")
        
        print()
    
    print("📋 SUMMARY:")
    print(f"  - CORE fund investments: {len(core_investments)}")
    print(f"  - BALANCE fund investments: {len(balance_investments)}")
    print()
    
    # Analyze the specific issue
    if len(core_investments) == 1:
        core_inv = core_investments[0]
        core_principal = core_inv.get('principal_amount', 0)
        
        if core_principal == 5000.00:
            print("🚨 ISSUE CONFIRMED:")
            print(f"  - Salvador's CORE fund investment shows ${core_principal:,.2f}")
            print(f"  - User reports it should be $4,000.00")
            print(f"  - Difference: ${core_principal - 4000:.2f} (needs correction)")
            print()
            print("💡 RECOMMENDED ACTION:")
            print(f"  - Update investment ID {core_inv.get('investment_id')} principal from ${core_principal:,.2f} to $4,000.00")
        elif core_principal == 4000.00:
            print("✅ ISSUE RESOLVED:")
            print(f"  - Salvador's CORE fund investment correctly shows $4,000.00")
        else:
            print("❓ UNEXPECTED VALUE:")
            print(f"  - Salvador's CORE fund investment shows ${core_principal:,.2f}")
            print(f"  - Expected either $5,000 (incorrect) or $4,000 (correct)")
    elif len(core_investments) == 0:
        print("❌ NO CORE INVESTMENTS FOUND:")
        print("  - Salvador should have 1 CORE fund investment (VT Markets)")
        print("  - This investment is missing entirely")
    else:
        print(f"❓ MULTIPLE CORE INVESTMENTS FOUND: {len(core_investments)}")
        print("  - Expected only 1 CORE fund investment (VT Markets)")
    
    # Check BALANCE investments
    balance_count_1263485 = sum(1 for inv in balance_investments if inv.get('principal_amount') == 1263485.40)
    
    if balance_count_1263485 > 0:
        print()
        print("✅ DOOTECHNOLOGY INVESTMENTS CONFIRMED:")
        print(f"  - Found {balance_count_1263485} BALANCE fund investment(s) with correct $1,263,485.40 amount")
    
    print()
    print("🔍 NEXT STEPS FOR TESTING AGENT:")
    if len(core_investments) == 1 and core_investments[0].get('principal_amount') == 5000.00:
        print("  1. ❌ CRITICAL: VT Markets investment shows $5,000 instead of $4,000")
        print("  2. 🔧 MAIN AGENT ACTION REQUIRED: Correct the principal amount in database")
        print("  3. 🧪 RE-TEST: Verify correction appears in all systems")
    elif len(core_investments) == 1 and core_investments[0].get('principal_amount') == 4000.00:
        print("  1. ✅ VT Markets investment amount is correct ($4,000)")
        print("  2. 🔍 INVESTIGATE: Why MT5 integration is failing (async/await errors)")
        print("  3. 🔍 INVESTIGATE: Why Fund Performance Dashboard shows 0 records")
    else:
        print("  1. ❓ INVESTIGATE: Unexpected CORE investment structure")
        print("  2. 🔍 VERIFY: Expected investment structure for Salvador")

if __name__ == "__main__":
    analyze_salvador_data()