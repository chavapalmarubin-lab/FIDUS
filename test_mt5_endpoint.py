#!/usr/bin/env python3
"""
TEST MT5 ENDPOINT DIRECTLY
Debug the MT5 accounts endpoint
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from frontend .env
BACKEND_URL = "https://trader-hub-27.preview.emergentagent.com"

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

def test_mt5_endpoint_detailed(token):
    """Test MT5 endpoint with detailed debugging"""
    print("\n🏦 Testing /api/mt5/accounts/all with detailed debugging...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/mt5/accounts/all", headers=headers, timeout=30)
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Full response: {json.dumps(data, indent=2)}")
            
            # Check if it's the old format or new format
            if 'data' in data:
                print("Using new data structure format")
                accounts = data['data'].get('accounts', [])
            else:
                print("Using direct format")
                accounts = data.get('accounts', [])
            
            print(f"Number of accounts: {len(accounts)}")
            
            if len(accounts) > 0:
                print("Account details:")
                for i, account in enumerate(accounts):
                    print(f"  {i+1}. Account: {account}")
            else:
                print("No accounts found in response")
                
        else:
            print(f"❌ API call failed: {response.status_code}")
            print(f"Response text: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing MT5 endpoint: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    """Main test function"""
    print("🚀 MT5 ENDPOINT DETAILED TEST")
    print("=" * 40)
    
    # Login as admin
    token = login_admin()
    if not token:
        print("❌ Cannot proceed without admin token")
        sys.exit(1)
    
    # Test MT5 endpoint
    test_mt5_endpoint_detailed(token)

if __name__ == "__main__":
    main()