#!/usr/bin/env python3
"""
CASH FLOW API RESPONSE STRUCTURE AUDIT
Test /api/admin/cashflow/overview?timeframe=3_months and report COMPLETE response structure
"""

import requests
import json
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://mt5-data-integrity.preview.emergentagent.com')

def login_as_admin():
    """Login as admin and get JWT token"""
    login_url = f"{BACKEND_URL}/api/auth/login"
    login_data = {
        "username": "admin",
        "password": "password123",
        "user_type": "admin"
    }
    
    print(f"🔐 Logging in as admin at: {login_url}")
    response = requests.post(login_url, json=login_data)
    
    if response.status_code == 200:
        token = response.json().get('token')
        print(f"✅ Admin login successful - Token received")
        return token
    else:
        print(f"❌ Admin login failed - Status: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def audit_cashflow_api(token):
    """Audit the cash flow API response structure"""
    cashflow_url = f"{BACKEND_URL}/api/admin/cashflow/overview?timeframe=3_months"
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n📊 Auditing Cash Flow API: {cashflow_url}")
    response = requests.get(cashflow_url, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        print("\n" + "="*80)
        print("COMPLETE CASH FLOW API RESPONSE STRUCTURE")
        print("="*80)
        
        # Pretty print the entire response
        print(json.dumps(data, indent=2, default=str))
        
        print("\n" + "="*80)
        print("SPECIFIC AUDIT FINDINGS")
        print("="*80)
        
        # 1. Check summary.broker_rebates value
        summary = data.get('summary', {})
        broker_rebates = summary.get('broker_rebates')
        print(f"1. summary.broker_rebates: {broker_rebates}")
        
        # 2. Check summary.separation_accounts - does this key exist?
        separation_accounts_in_summary = summary.get('separation_accounts')
        print(f"2. summary.separation_accounts exists: {separation_accounts_in_summary is not None}")
        if separation_accounts_in_summary is not None:
            print(f"   Value: {separation_accounts_in_summary}")
        
        # 3. Search for ANY separation_accounts data anywhere in response
        print(f"3. Searching for 'separation_accounts' anywhere in response:")
        def find_separation_accounts(obj, path=""):
            """Recursively search for separation_accounts keys"""
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    if 'separation' in key.lower():
                        print(f"   Found at {current_path}: {value}")
                    find_separation_accounts(value, current_path)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    find_separation_accounts(item, f"{path}[{i}]")
        
        find_separation_accounts(data)
        
        # 4. Search for Account 891215 data
        print(f"4. Searching for Account 891215 data:")
        def find_account_data(obj, account_id, path=""):
            """Recursively search for specific account data"""
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    if str(value) == str(account_id) or (isinstance(value, str) and account_id in value):
                        print(f"   Found {account_id} at {current_path}: {value}")
                    find_account_data(value, account_id, current_path)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    find_account_data(item, account_id, f"{path}[{i}]")
        
        find_account_data(data, "891215")
        
        # 5. Search for Account 886528 data
        print(f"5. Searching for Account 886528 data:")
        find_account_data(data, "886528")
        
        # 6. Show all top-level keys
        print(f"\n6. All top-level response keys:")
        for key in data.keys():
            print(f"   - {key}: {type(data[key])}")
        
        # 7. Show summary structure in detail
        print(f"\n7. Summary object structure:")
        if 'summary' in data:
            for key, value in summary.items():
                print(f"   summary.{key}: {value} ({type(value).__name__})")
        
        return data
    else:
        print(f"❌ Cash Flow API request failed")
        print(f"Response: {response.text}")
        return None

def main():
    """Main audit function"""
    print("CASH FLOW API RESPONSE STRUCTURE AUDIT")
    print("="*50)
    
    # Step 1: Login as Admin
    token = login_as_admin()
    if not token:
        print("❌ Cannot proceed without admin token")
        return
    
    # Step 2: Audit Cash Flow API
    audit_data = audit_cashflow_api(token)
    
    if audit_data:
        print("\n✅ Cash Flow API audit completed successfully")
    else:
        print("\n❌ Cash Flow API audit failed")

if __name__ == "__main__":
    main()