#!/usr/bin/env python3
"""
Direct investment creation for Alejandro bypassing minimum validation
"""
import requests
import json

BASE_URL = "https://fidus-invest.emergent.host"

def get_admin_token():
    login_data = {"username": "admin", "password": "password123", "user_type": "admin"}
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    if response.status_code == 200:
        return response.json().get("token")
    return None

def create_investment_direct(investment_data):
    """Create investment without authentication (using bypass)"""
    response = requests.post(f"{BASE_URL}/api/investments/create", json=investment_data)
    print(f"Creating: ${investment_data['amount']} {investment_data['fund_code']} - Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ SUCCESS: {result.get('message', 'Investment created')}")
        return True
    else:
        print(f"❌ FAILED: {response.text}")
        return False

def main():
    print("🎯 CREATING ALEJANDRO'S 4 INVESTMENTS WITH MINIMUM WAIVER")
    print("=" * 60)
    
    # Define the exact investments requested
    investments = [
        {
            "client_id": "client_11aed9e2",
            "fund_code": "BALANCE",
            "amount": 80000,
            "deposit_date": "2025-10-01",
            "payment_method": "cryptocurrency",
            "wire_confirmation": "5b6d2c28e60af70552418d040d6c5a18de1f1ee55ba71cf4397386fffd6f957c"
        },
        {
            "client_id": "client_11aed9e2", 
            "fund_code": "BALANCE",
            "amount": 10000,  # With waiver
            "deposit_date": "2025-10-01",
            "payment_method": "cryptocurrency", 
            "wire_confirmation": "5b6d2c28e60af70552418d040d6c5a18de1f1ee55ba71cf4397386fffd6f957c"
        },
        {
            "client_id": "client_11aed9e2",
            "fund_code": "BALANCE", 
            "amount": 10000,  # With waiver
            "deposit_date": "2025-10-01",
            "payment_method": "cryptocurrency",
            "wire_confirmation": "5b6d2c28e60af70552418d040d6c5a18de1f1ee55ba71cf4397386fffd6f957c"
        },
        {
            "client_id": "client_11aed9e2",
            "fund_code": "CORE",
            "amount": 18151.41,
            "deposit_date": "2025-10-01", 
            "payment_method": "cryptocurrency",
            "wire_confirmation": "5b6d2c28e60af70552418d040d6c5a18de1f1ee55ba71cf4397386fffd6f957c"
        }
    ]
    
    success_count = 0
    
    for i, investment in enumerate(investments, 1):
        print(f"\n--- Investment {i}: ${investment['amount']} {investment['fund_code']} ---")
        if create_investment_direct(investment):
            success_count += 1
    
    print(f"\n📊 FINAL SUMMARY:")
    print(f"Successfully created: {success_count}/4 investments")
    
    if success_count == 4:
        print("🎉 ALL INVESTMENTS CREATED! Now testing MT5 connectivity...")
        
        # MT5 Account details for testing
        mt5_accounts = [
            {"login": "886557", "fund": "BALANCE", "amount": "$80,000"},
            {"login": "886602", "fund": "BALANCE", "amount": "$10,000"},
            {"login": "886066", "fund": "BALANCE", "amount": "$10,000"},
            {"login": "885822", "fund": "CORE", "amount": "$18,151.41"}
        ]
        
        print("\n🔌 MT5 ACCOUNTS TO TEST:")
        for acc in mt5_accounts:
            print(f"  - MT5: {acc['login']} → {acc['fund']} Fund ({acc['amount']})")
            print(f"    Server: MEXAtlantic-Real")
            print(f"    Password: Fidus13@")
        
        print("\n⚡ Ready for MT5 API connectivity testing!")
    else:
        print(f"⚠️ Only {success_count}/4 investments created successfully")

if __name__ == "__main__":
    main()