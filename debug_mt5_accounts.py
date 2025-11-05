#!/usr/bin/env python3
"""
Debug MT5 Accounts - Check what accounts actually exist
"""

import requests
import json

# Backend URL from environment
BACKEND_URL = "https://referral-rescue.preview.emergentagent.com"

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

def authenticate():
    """Authenticate as admin and get JWT token"""
    session = requests.Session()
    
    auth_url = f"{BACKEND_URL}/api/auth/login"
    payload = {
        "username": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD,
        "user_type": "admin"
    }
    
    response = session.post(auth_url, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        token = data.get('token')
        if token:
            session.headers.update({'Authorization': f'Bearer {token}'})
            print("✅ Authentication successful")
            return session
    
    print("❌ Authentication failed")
    return None

def debug_mt5_accounts():
    """Debug MT5 accounts to see what actually exists"""
    session = authenticate()
    if not session:
        return
    
    print("\n🔍 DEBUGGING MT5 ACCOUNTS")
    print("=" * 50)
    
    # Test MT5 admin accounts endpoint
    url = f"{BACKEND_URL}/api/mt5/admin/accounts"
    response = session.get(url)
    
    print(f"GET {url}")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Response Keys: {list(data.keys())}")
        
        if 'accounts' in data:
            accounts = data['accounts']
            print(f"Number of accounts: {len(accounts)}")
            print()
            
            if accounts:
                print("📋 FOUND ACCOUNTS:")
                for i, account in enumerate(accounts):
                    login = account.get('login', 'N/A')
                    fund_type = account.get('fund_type', 'N/A')
                    fund_code = account.get('fund_code', 'N/A')
                    balance = account.get('balance', 0)
                    broker = account.get('broker_name', 'N/A')
                    
                    print(f"  {i+1}. Login: {login}")
                    print(f"     Fund Type: {fund_type}")
                    print(f"     Fund Code: {fund_code}")
                    print(f"     Balance: ${balance:,.2f}")
                    print(f"     Broker: {broker}")
                    print()
            else:
                print("❌ No accounts found in response")
        else:
            print("❌ No 'accounts' key in response")
            print(f"Response: {json.dumps(data, indent=2)}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"Response: {response.text}")

def test_fund_portfolio_overview():
    """Test the fund portfolio overview endpoint"""
    session = authenticate()
    if not session:
        return
    
    print("\n🔍 TESTING FUND PORTFOLIO OVERVIEW")
    print("=" * 50)
    
    url = f"{BACKEND_URL}/api/fund-portfolio/overview"
    response = session.get(url)
    
    print(f"GET {url}")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data.get('success', 'N/A')}")
        
        if 'funds' in data:
            funds = data['funds']
            print(f"Number of funds: {len(funds)}")
            print()
            
            for fund_code, fund_data in funds.items():
                mt5_count = fund_data.get('mt5_accounts_count', 'N/A')
                mt5_allocation = fund_data.get('mt5_allocation', 'N/A')
                performance_ytd = fund_data.get('performance_ytd', 'N/A')
                
                print(f"📊 {fund_code} Fund:")
                print(f"   MT5 Accounts Count: {mt5_count}")
                print(f"   MT5 Allocation: ${mt5_allocation}")
                print(f"   Performance YTD: {performance_ytd}%")
                print()
        else:
            print("❌ No 'funds' key in response")
            print(f"Response: {json.dumps(data, indent=2)}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"Response: {response.text}")

if __name__ == "__main__":
    debug_mt5_accounts()
    test_fund_portfolio_overview()