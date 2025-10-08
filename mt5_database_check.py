#!/usr/bin/env python3
"""
MT5 Database Check - Investigate what MT5 accounts exist in MongoDB
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from frontend .env
BACKEND_URL = "https://trading-platform-76.preview.emergentagent.com"

def check_mt5_database():
    """Check what MT5 accounts exist in the database"""
    print("=" * 80)
    print("MT5 DATABASE INVESTIGATION")
    print("=" * 80)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Investigation Time: {datetime.now()}")
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
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            jwt_token = login_result.get('token')
            print(f"✅ Admin authenticated successfully")
        else:
            print(f"❌ Admin authentication failed: {login_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Admin authentication error: {str(e)}")
        return False
    
    if not jwt_token:
        return False
    
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }
    
    print()
    
    # Step 2: Check MT5 Pool Statistics
    print("📊 STEP 2: MT5 Pool Statistics")
    print("-" * 40)
    
    try:
        pool_stats_response = requests.get(
            f"{BACKEND_URL}/api/mt5/pool/statistics",
            headers=headers,
            timeout=10
        )
        
        if pool_stats_response.status_code == 200:
            stats_data = pool_stats_response.json()
            print("✅ MT5 Pool Statistics:")
            print(f"  Total accounts: {stats_data.get('total_accounts', 0)}")
            print(f"  Available accounts: {stats_data.get('available_accounts', 0)}")
            print(f"  Allocated accounts: {stats_data.get('allocated_accounts', 0)}")
            print(f"  Utilization: {stats_data.get('utilization_percentage', 0)}%")
        else:
            print(f"❌ Pool statistics failed: {pool_stats_response.status_code}")
            
    except Exception as e:
        print(f"❌ Pool statistics error: {str(e)}")
    
    print()
    
    # Step 3: Check Available MT5 Accounts
    print("🏦 STEP 3: Available MT5 Accounts")
    print("-" * 40)
    
    try:
        available_accounts_response = requests.get(
            f"{BACKEND_URL}/api/mt5/pool/accounts",
            headers=headers,
            timeout=10
        )
        
        if available_accounts_response.status_code == 200:
            accounts_data = available_accounts_response.json()
            accounts = accounts_data.get('accounts', [])
            print(f"✅ Available MT5 accounts: {len(accounts)}")
            
            for i, account in enumerate(accounts, 1):
                account_num = account.get('mt5_account_number', 'Unknown')
                broker = account.get('broker_name', 'Unknown')
                status = account.get('status', 'Unknown')
                print(f"  {i}. Account: {account_num}, Broker: {broker}, Status: {status}")
                
        else:
            print(f"❌ Available accounts failed: {available_accounts_response.status_code}")
            
    except Exception as e:
        print(f"❌ Available accounts error: {str(e)}")
    
    print()
    
    # Step 4: Check Client Investments
    print("💰 STEP 4: Client Alejandro Investments")
    print("-" * 40)
    
    try:
        investments_response = requests.get(
            f"{BACKEND_URL}/api/investments/client/client_alejandro",
            headers=headers,
            timeout=10
        )
        
        if investments_response.status_code == 200:
            investments_data = investments_response.json()
            investments = investments_data.get('investments', [])
            print(f"✅ Client investments: {len(investments)}")
            
            for i, investment in enumerate(investments, 1):
                fund_code = investment.get('fund_code', 'Unknown')
                amount = investment.get('principal_amount', 0)
                status = investment.get('status', 'Unknown')
                print(f"  {i}. Fund: {fund_code}, Amount: ${amount:,.2f}, Status: {status}")
                
        else:
            print(f"❌ Client investments failed: {investments_response.status_code}")
            
    except Exception as e:
        print(f"❌ Client investments error: {str(e)}")
    
    print()
    
    # Step 5: Test Other Clients' MT5 Accounts
    print("🔍 STEP 5: Other Clients' MT5 Accounts")
    print("-" * 40)
    
    test_clients = ["client_003", "client_001", "client_002"]
    
    for client_id in test_clients:
        try:
            mt5_response = requests.get(
                f"{BACKEND_URL}/api/mt5/accounts/{client_id}",
                headers=headers,
                timeout=10
            )
            
            if mt5_response.status_code == 200:
                mt5_data = mt5_response.json()
                account_count = len(mt5_data.get('accounts', []))
                print(f"  {client_id}: {account_count} MT5 accounts")
            else:
                print(f"  {client_id}: Error {mt5_response.status_code}")
                
        except Exception as e:
            print(f"  {client_id}: Exception - {str(e)}")
    
    return True

def main():
    """Main investigation execution"""
    print("Starting MT5 Database Investigation...")
    print()
    
    success = check_mt5_database()
    
    print()
    print("=" * 80)
    if success:
        print("✅ INVESTIGATION COMPLETED")
        print("Key findings will help identify why client_alejandro has 0 MT5 accounts")
    else:
        print("❌ INVESTIGATION FAILED")
    print("=" * 80)
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)