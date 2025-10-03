#!/usr/bin/env python3
"""
Create the correct 4 investments for Alejandro with exact amounts
"""
import requests
import json

BASE_URL = "https://fidus-invest.emergent.host"

def get_admin_token():
    login_data = {
        "username": "admin",
        "password": "password123", 
        "user_type": "admin"
    }
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    if response.status_code == 200:
        return response.json().get("token")
    return None

def create_investment(token, investment_data):
    """Create a single investment"""
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    response = requests.post(f"{BASE_URL}/api/investments/create", 
                           json=investment_data, headers=headers)
    
    print(f"Creating investment: {investment_data['amount']} {investment_data['fund_code']}")
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Response: {response.text}")
    else:
        print("✅ Investment created successfully")
    
    return response.status_code == 200

def main():
    print("🚀 CREATING CORRECT INVESTMENTS FOR ALEJANDRO")
    print("=" * 50)
    
    token = get_admin_token()
    if not token:
        print("❌ Could not get admin token")
        return
    
    # The 4 CORRECT investments as specified
    investments = [
        {
            "client_id": "alejandrom",
            "fund_code": "BALANCE",
            "amount": 80000,
            "deposit_date": "2025-10-01",
            "payment_method": "cryptocurrency",
            "wire_confirmation": "5b6d2c28e60af70552418d040d6c5a18de1f1ee55ba71cf4397386fffd6f957c",
            "bank_reference": "ALEJANDRO-INV1-80K-BALANCE-MT5-886557"
        },
        {
            "client_id": "client_11aed9e2", 
            "fund_code": "BALANCE",
            "amount": 10000,  # CORRECT amount for Investment 2
            "deposit_date": "2025-10-01",
            "payment_method": "cryptocurrency", 
            "wire_confirmation": "5b6d2c28e60af70552418d040d6c5a18de1f1ee55ba71cf4397386fffd6f957c",
            "bank_reference": "ALEJANDRO-INV2-10K-BALANCE-MT5-886602"
        },
        {
            "client_id": "alejandrom",
            "fund_code": "BALANCE", 
            "amount": 10000,  # CORRECT amount for Investment 3
            "deposit_date": "2025-10-01",
            "payment_method": "cryptocurrency",
            "wire_confirmation": "5b6d2c28e60af70552418d040d6c5a18de1f1ee55ba71cf4397386fffd6f957c",
            "bank_reference": "ALEJANDRO-INV3-10K-BALANCE-MT5-886066"
        },
        {
            "client_id": "alejandrom",
            "fund_code": "CORE",  # CORE fund for Investment 4
            "amount": 18151.41,  # CORRECT amount for Investment 4
            "deposit_date": "2025-10-01", 
            "payment_method": "cryptocurrency",
            "wire_confirmation": "5b6d2c28e60af70552418d040d6c5a18de1f1ee55ba71cf4397386fffd6f957c",
            "bank_reference": "ALEJANDRO-INV4-18151-CORE-MT5-885822"
        }
    ]
    
    print(f"📋 Creating {len(investments)} investments...")
    success_count = 0
    
    for i, investment in enumerate(investments, 1):
        print(f"\n--- Investment {i} ---")
        if create_investment(token, investment):
            success_count += 1
        else:
            print(f"❌ Failed to create Investment {i}")
    
    print(f"\n📊 SUMMARY:")
    print(f"Created: {success_count}/{len(investments)} investments")
    print(f"Expected total: $118,151.41")
    print(f"Individual amounts: $80,000 + $10,000 + $10,000 + $18,151.41")

if __name__ == "__main__":
    main()