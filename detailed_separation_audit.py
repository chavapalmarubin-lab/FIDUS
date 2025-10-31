#!/usr/bin/env python3
"""
DETAILED SEPARATION ACCOUNTS AUDIT
Check MT5 accounts database for accounts 891215 and 886528
"""

import requests
import json
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://bridge-guardian.preview.emergentagent.com')

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

def check_mt5_accounts(token):
    """Check all MT5 accounts for separation accounts"""
    mt5_url = f"{BACKEND_URL}/api/mt5/admin/accounts"
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n📊 Checking MT5 Accounts: {mt5_url}")
    response = requests.get(mt5_url, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        accounts = data.get('accounts', [])
        
        print(f"\n🔍 Found {len(accounts)} MT5 accounts:")
        
        account_891215 = None
        account_886528 = None
        separation_accounts = []
        
        for account in accounts:
            account_num = str(account.get('account', ''))
            fund_type = account.get('fund_type', '')
            name = account.get('name', '')
            equity = account.get('equity', 0)
            balance = account.get('balance', 0)
            
            print(f"  Account {account_num}: {name} ({fund_type}) - Equity: ${equity}, Balance: ${balance}")
            
            # Check for specific accounts
            if account_num == '891215':
                account_891215 = account
                print(f"    ⭐ FOUND ACCOUNT 891215!")
            elif account_num == '886528':
                account_886528 = account
                print(f"    ⭐ FOUND ACCOUNT 886528!")
            
            # Check for separation accounts
            if 'SEPARATION' in fund_type.upper() or 'INTEREST' in fund_type.upper():
                separation_accounts.append(account)
                print(f"    💰 SEPARATION ACCOUNT DETECTED")
        
        print(f"\n" + "="*60)
        print("SEPARATION ACCOUNTS SUMMARY")
        print("="*60)
        
        print(f"Total separation accounts found: {len(separation_accounts)}")
        
        if account_891215:
            print(f"\n📋 ACCOUNT 891215 DETAILS:")
            print(json.dumps(account_891215, indent=2, default=str))
        else:
            print(f"\n❌ Account 891215 NOT FOUND in MT5 accounts")
        
        if account_886528:
            print(f"\n📋 ACCOUNT 886528 DETAILS:")
            print(json.dumps(account_886528, indent=2, default=str))
        else:
            print(f"\n❌ Account 886528 NOT FOUND in MT5 accounts")
        
        print(f"\n📋 ALL SEPARATION ACCOUNTS:")
        for sep_acc in separation_accounts:
            print(f"  Account {sep_acc.get('account')}: {sep_acc.get('name')} - ${sep_acc.get('equity', 0)}")
        
        return {
            'account_891215': account_891215,
            'account_886528': account_886528,
            'separation_accounts': separation_accounts,
            'all_accounts': accounts
        }
    else:
        print(f"❌ MT5 Accounts request failed")
        print(f"Response: {response.text}")
        return None

def check_mt5_config_accounts(token):
    """Check MT5 configuration accounts"""
    config_url = f"{BACKEND_URL}/api/admin/mt5/config/accounts"
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n📊 Checking MT5 Config Accounts: {config_url}")
    response = requests.get(config_url, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        accounts = data.get('accounts', [])
        
        print(f"\n🔍 Found {len(accounts)} MT5 config accounts:")
        
        for account in accounts:
            account_num = str(account.get('account', ''))
            name = account.get('name', '')
            fund_type = account.get('fund_type', '')
            
            print(f"  Config Account {account_num}: {name} ({fund_type})")
            
            if account_num in ['891215', '886528']:
                print(f"    ⭐ TARGET ACCOUNT FOUND IN CONFIG!")
                print(f"    Details: {json.dumps(account, indent=4, default=str)}")
        
        return accounts
    else:
        print(f"❌ MT5 Config Accounts request failed")
        print(f"Response: {response.text}")
        return None

def main():
    """Main audit function"""
    print("DETAILED SEPARATION ACCOUNTS AUDIT")
    print("="*50)
    
    # Step 1: Login as Admin
    token = login_as_admin()
    if not token:
        print("❌ Cannot proceed without admin token")
        return
    
    # Step 2: Check MT5 Accounts
    mt5_data = check_mt5_accounts(token)
    
    # Step 3: Check MT5 Config Accounts
    config_data = check_mt5_config_accounts(token)
    
    print(f"\n" + "="*60)
    print("FINAL AUDIT SUMMARY")
    print("="*60)
    
    if mt5_data:
        print(f"✅ MT5 Accounts API accessible")
        print(f"   - Account 891215: {'FOUND' if mt5_data['account_891215'] else 'NOT FOUND'}")
        print(f"   - Account 886528: {'FOUND' if mt5_data['account_886528'] else 'NOT FOUND'}")
        print(f"   - Separation accounts: {len(mt5_data['separation_accounts'])}")
    else:
        print(f"❌ MT5 Accounts API failed")
    
    if config_data:
        print(f"✅ MT5 Config API accessible")
        config_891215 = any(str(acc.get('account')) == '891215' for acc in config_data)
        config_886528 = any(str(acc.get('account')) == '886528' for acc in config_data)
        print(f"   - Config Account 891215: {'FOUND' if config_891215 else 'NOT FOUND'}")
        print(f"   - Config Account 886528: {'FOUND' if config_886528 else 'NOT FOUND'}")
    else:
        print(f"❌ MT5 Config API failed")

if __name__ == "__main__":
    main()