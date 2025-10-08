#!/usr/bin/env python3
"""
MT5 Accounts Test - Quick test for client_alejandro MT5 accounts endpoint
Testing: GET /api/mt5/accounts/client_alejandro
Expected: Should return 4 MEXAtlantic accounts or show logs explaining why empty
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from frontend .env
BACKEND_URL = "https://trading-platform-76.preview.emergentagent.com"

def test_mt5_accounts_endpoint():
    """Test the MT5 accounts endpoint for client_alejandro"""
    print("=" * 80)
    print("MT5 ACCOUNTS TEST - CLIENT ALEJANDRO")
    print("=" * 80)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Time: {datetime.now()}")
    print()
    
    # Step 1: Admin Authentication
    print("🔐 STEP 1: Admin Authentication")
    print("-" * 40)
    
    login_data = {
        "username": "admin",
        "password": "password123", 
        "user_type": "admin"
    }
    
    try:
        login_response = requests.post(
            f"{BACKEND_URL}/api/auth/login",
            json=login_data,
            timeout=10
        )
        
        print(f"Login Status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            jwt_token = login_result.get('token')
            admin_name = login_result.get('name', 'Unknown')
            print(f"✅ Admin authenticated successfully: {admin_name}")
            print(f"JWT Token: {jwt_token[:50]}..." if jwt_token else "❌ No JWT token received")
        else:
            print(f"❌ Admin authentication failed: {login_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Admin authentication error: {str(e)}")
        return False
    
    if not jwt_token:
        print("❌ Cannot proceed without JWT token")
        return False
    
    print()
    
    # Step 2: Test MT5 Accounts Endpoint
    print("🏦 STEP 2: MT5 Accounts Endpoint Test")
    print("-" * 40)
    
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }
    
    mt5_endpoint = f"{BACKEND_URL}/api/mt5/accounts/client_alejandro"
    print(f"Testing endpoint: {mt5_endpoint}")
    
    try:
        mt5_response = requests.get(
            mt5_endpoint,
            headers=headers,
            timeout=15
        )
        
        print(f"MT5 Response Status: {mt5_response.status_code}")
        print(f"Response Headers: {dict(mt5_response.headers)}")
        
        if mt5_response.status_code == 200:
            mt5_data = mt5_response.json()
            print("✅ MT5 endpoint accessible")
            print(f"Response structure: {json.dumps(mt5_data, indent=2)}")
            
            # Check for accounts
            accounts = mt5_data.get('accounts', [])
            print(f"\n📊 MT5 ACCOUNTS ANALYSIS:")
            print(f"Total accounts returned: {len(accounts)}")
            
            if len(accounts) == 0:
                print("⚠️  EMPTY ACCOUNTS - This is the issue we're investigating")
                print("Expected: 4 MEXAtlantic accounts")
                print("Actual: 0 accounts")
            else:
                print("✅ Accounts found:")
                for i, account in enumerate(accounts, 1):
                    broker = account.get('broker_name', 'Unknown')
                    account_num = account.get('mt5_account_number', 'Unknown')
                    print(f"  {i}. Account: {account_num}, Broker: {broker}")
            
            return True
            
        else:
            print(f"❌ MT5 endpoint failed: {mt5_response.status_code}")
            print(f"Error response: {mt5_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ MT5 endpoint error: {str(e)}")
        return False

def main():
    """Main test execution"""
    print("Starting MT5 Accounts Test for client_alejandro...")
    print()
    
    success = test_mt5_accounts_endpoint()
    
    print()
    print("=" * 80)
    if success:
        print("✅ TEST COMPLETED - Check backend logs for MT5 search messages")
        print("Expected log messages:")
        print("  - 'Searching MT5 accounts for client_id: client_alejandro'")
        print("  - 'Found X MT5 accounts for client_id: client_alejandro'")
    else:
        print("❌ TEST FAILED - Unable to complete MT5 accounts test")
    print("=" * 80)
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)