#!/usr/bin/env python3
"""
Create Salvador's Expected Investments
Based on the review request requirements
"""

import requests
import json

def create_salvador_investments():
    base_url = "https://fidus-workspace-1.preview.emergentagent.com"
    
    # Authenticate as admin
    auth_response = requests.post(f"{base_url}/api/auth/login", json={
        "username": "admin",
        "password": "password123",
        "user_type": "admin"
    })
    
    if auth_response.status_code != 200:
        print("❌ Failed to authenticate as admin")
        return False
    
    token = auth_response.json().get('token')
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    
    print("🔍 CREATING SALVADOR'S EXPECTED INVESTMENTS")
    print("=" * 60)
    
    salvador_client_id = "client_003"
    
    # Investment 1: BALANCE Fund
    balance_investment = {
        "client_id": salvador_client_id,
        "fund_code": "BALANCE",
        "amount": 1263485.40,
        "deposit_date": "2025-04-01",
        "create_mt5_account": True,
        "mt5_login": "9928326",
        "mt5_password": "secure_password_123",
        "mt5_server": "DooTechnology-Live",
        "broker_name": "DooTechnology MT5",
        "mt5_initial_balance": 1263485.40
    }
    
    print("\n💰 Creating BALANCE Fund Investment...")
    print(f"   Amount: ${balance_investment['amount']:,.2f}")
    print(f"   Deposit Date: {balance_investment['deposit_date']}")
    print(f"   MT5 Login: {balance_investment['mt5_login']}")
    
    balance_response = requests.post(
        f"{base_url}/api/investments/create",
        json=balance_investment,
        headers=headers
    )
    
    if balance_response.status_code == 200:
        balance_result = balance_response.json()
        print(f"   ✅ BALANCE investment created: {balance_result.get('investment_id')}")
        print(f"   MT5 Mapping: {balance_result.get('mt5_mapping_success', False)}")
    else:
        print(f"   ❌ Failed to create BALANCE investment: {balance_response.status_code}")
        try:
            error = balance_response.json()
            print(f"   Error: {error}")
        except:
            print(f"   Error text: {balance_response.text}")
    
    # Investment 2: CORE Fund
    core_investment = {
        "client_id": salvador_client_id,
        "fund_code": "CORE",
        "amount": 5000.00,
        "deposit_date": "2025-09-04",
        "create_mt5_account": True,
        "mt5_login": "15759667",
        "mt5_password": "secure_password_456",
        "mt5_server": "VTMarkets-Live",
        "broker_name": "VT Markets PAMM",
        "mt5_initial_balance": 5000.00
    }
    
    print("\n💰 Creating CORE Fund Investment...")
    print(f"   Amount: ${core_investment['amount']:,.2f}")
    print(f"   Deposit Date: {core_investment['deposit_date']}")
    print(f"   MT5 Login: {core_investment['mt5_login']}")
    
    core_response = requests.post(
        f"{base_url}/api/investments/create",
        json=core_investment,
        headers=headers
    )
    
    if core_response.status_code == 200:
        core_result = core_response.json()
        print(f"   ✅ CORE investment created: {core_result.get('investment_id')}")
        print(f"   MT5 Mapping: {core_result.get('mt5_mapping_success', False)}")
    else:
        print(f"   ❌ Failed to create CORE investment: {core_response.status_code}")
        try:
            error = core_response.json()
            print(f"   Error: {error}")
        except:
            print(f"   Error text: {core_response.text}")
    
    # Verify creation
    print("\n🔍 VERIFYING CREATED INVESTMENTS...")
    
    # Check Salvador's investments
    verify_response = requests.get(
        f"{base_url}/api/investments/client/{salvador_client_id}",
        headers=headers
    )
    
    if verify_response.status_code == 200:
        verify_data = verify_response.json()
        investments = verify_data.get('investments', [])
        print(f"   Salvador now has {len(investments)} investments:")
        for inv in investments:
            print(f"     - {inv.get('fund_code')}: ${inv.get('principal_amount', 0):,.2f}")
    else:
        print(f"   ❌ Failed to verify investments: {verify_response.status_code}")
    
    # Check MT5 accounts
    mt5_response = requests.get(f"{base_url}/api/mt5/admin/accounts", headers=headers)
    if mt5_response.status_code == 200:
        mt5_data = mt5_response.json()
        accounts = mt5_data.get('accounts', [])
        salvador_accounts = [acc for acc in accounts if acc.get('client_id') == salvador_client_id]
        print(f"   Salvador now has {len(salvador_accounts)} MT5 accounts:")
        for acc in salvador_accounts:
            print(f"     - Login: {acc.get('mt5_login')} ({acc.get('broker_name')})")
    else:
        print(f"   ❌ Failed to verify MT5 accounts: {mt5_response.status_code}")
    
    return True

if __name__ == "__main__":
    create_salvador_investments()