#!/usr/bin/env python3
"""
TEST CORRECT MT5 ENDPOINT
Test the correct MT5 endpoint for Alejandro
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from frontend .env
BACKEND_URL = "https://prospect-portal.preview.emergentagent.com"

def login_admin():
    """Login as admin and get JWT token"""
    print("🔐 Logging in as admin...")
    
    login_data = {
        "username": "admin",
        "password": "password123",
        "user_type": "admin"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/auth/login", json=login_data, timeout=30)
        print(f"Login response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            if token:
                print("✅ Admin login successful")
                return token
            else:
                print("❌ No token in login response")
                return None
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        return None

def test_mt5_endpoint_alejandro(token):
    """Test MT5 endpoint for Alejandro specifically"""
    print("\n🏦 Testing /api/mt5/accounts/client_alejandro...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/mt5/accounts/client_alejandro", headers=headers, timeout=30)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response data: {json.dumps(data, indent=2)}")
            
            # Extract accounts
            accounts = data.get('accounts', [])
            account_count = len(accounts)
            
            print(f"Number of accounts returned: {account_count}")
            
            # Expected account numbers
            expected_accounts = [886557, 886066, 886602, 885822, 891234, 886528, 891215]
            
            if account_count == 7:
                print("✅ CORRECT: 7 accounts returned")
                
                # Check specific account numbers
                returned_account_numbers = []
                for account in accounts:
                    account_num = account.get('mt5_account_number') or account.get('account')
                    if account_num:
                        returned_account_numbers.append(int(account_num))
                
                print(f"Returned account numbers: {sorted(returned_account_numbers)}")
                print(f"Expected account numbers: {sorted(expected_accounts)}")
                
                missing_accounts = set(expected_accounts) - set(returned_account_numbers)
                extra_accounts = set(returned_account_numbers) - set(expected_accounts)
                
                if not missing_accounts and not extra_accounts:
                    print("✅ CORRECT: All expected accounts present")
                    return True
                else:
                    if missing_accounts:
                        print(f"❌ Missing accounts: {missing_accounts}")
                    if extra_accounts:
                        print(f"❌ Extra accounts: {extra_accounts}")
                    return False
            else:
                print(f"❌ WRONG: {account_count} accounts returned (expected 7)")
                return False
        else:
            print(f"❌ API call failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing MT5 endpoint: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 CORRECT MT5 ENDPOINT TEST")
    print("=" * 40)
    
    # Login as admin
    token = login_admin()
    if not token:
        print("❌ Cannot proceed without admin token")
        sys.exit(1)
    
    # Test correct MT5 endpoint
    success = test_mt5_endpoint_alejandro(token)
    
    if success:
        print("\n✅ MT5 endpoint test PASSED")
    else:
        print("\n❌ MT5 endpoint test FAILED")

if __name__ == "__main__":
    main()