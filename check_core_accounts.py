#!/usr/bin/env python3
"""
Check CORE Fund Account Count Specifically
"""

import requests
import json

def authenticate():
    base_url = "https://fidus-restore.preview.emergentagent.com/api"
    
    login_data = {
        "username": "admin",
        "password": "password123",
        "user_type": "admin"
    }
    
    response = requests.post(f"{base_url}/auth/login", json=login_data, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        return data.get('token')
    return None

def check_core_accounts():
    base_url = "https://fidus-restore.preview.emergentagent.com/api"
    token = authenticate()
    
    if not token:
        print("❌ Authentication failed")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("🔍 Checking CORE Fund Account Count...")
    
    response = requests.get(f"{base_url}/admin/fund-performance/dashboard", headers=headers, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        
        by_fund = data['dashboard']['by_fund']
        
        if 'CORE' in by_fund:
            core_data = by_fund['CORE']
            account_count = core_data.get('account_count')
            
            print(f"CORE Fund Data:")
            for key, value in core_data.items():
                print(f"  {key}: {value}")
            
            print(f"\n🎯 CORE Fund Account Count: {account_count}")
            
            if account_count == 2:
                print("✅ PASS: CORE fund shows 2 accounts (expected: 885822 and 891234)")
            else:
                print(f"❌ FAIL: CORE fund shows {account_count} accounts (expected: 2)")
        else:
            print("❌ FAIL: No CORE fund data found")
    else:
        print(f"❌ FAIL: API error - HTTP {response.status_code}")

if __name__ == "__main__":
    check_core_accounts()