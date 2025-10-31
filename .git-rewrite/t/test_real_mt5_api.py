#!/usr/bin/env python3
"""
Test REAL MT5 API connectivity using the correct endpoints
Critical for Alejandro's business flow validation
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

def test_mt5_system_status(token):
    """Test overall MT5 system status"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("🔍 Testing MT5 System Status...")
    try:
        response = requests.get(f"{BASE_URL}/api/mt5/admin/system-status", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ MT5 System Status: {data}")
            return True
        else:
            print(f"❌ MT5 System Status Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ MT5 System Status Exception: {e}")
        return False

def test_mt5_realtime_data(token):
    """Test MT5 real-time data endpoint"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n📊 Testing MT5 Real-time Data...")
    try:
        response = requests.get(f"{BASE_URL}/api/mt5/admin/realtime-data", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Real-time Data Available: {len(data) if isinstance(data, list) else 'Connected'}")
            if isinstance(data, list) and data:
                print(f"   Sample data: {data[0] if data else 'No data'}")
            return True
        else:
            print(f"❌ Real-time Data Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Real-time Data Exception: {e}")
        return False

def test_mt5_accounts(token):
    """Test MT5 accounts endpoint"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n🏦 Testing MT5 Admin Accounts...")
    try:
        response = requests.get(f"{BASE_URL}/api/mt5/admin/accounts", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ MT5 Accounts Found: {len(data.get('accounts', [])) if isinstance(data, dict) else 'Connected'}")
            
            # Look for Alejandro's accounts
            if isinstance(data, dict) and 'accounts' in data:
                alejandro_accounts = []
                for account in data['accounts']:
                    login_id = str(account.get('login', ''))
                    if login_id in ['886557', '886602', '886066', '885822']:
                        alejandro_accounts.append(account)
                        print(f"   🎯 Found Alejandro Account: {login_id} - {account.get('status', 'Unknown')}")
                
                print(f"\n📋 Alejandro's Accounts Found: {len(alejandro_accounts)}/4")
                return alejandro_accounts
            return True
        else:
            print(f"❌ MT5 Accounts Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ MT5 Accounts Exception: {e}")
        return False

def test_specific_account_data(token, account_id):
    """Test specific account data retrieval"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n🔍 Testing Account {account_id} Data...")
    
    # Test account activity
    try:
        response = requests.get(f"{BASE_URL}/api/mt5/admin/account/{account_id}/activity", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Account Activity: Available")
        else:
            print(f"   ❌ Account Activity: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Account Activity Exception: {e}")
    
    # Test account positions
    try:
        response = requests.get(f"{BASE_URL}/api/mt5/admin/account/{account_id}/positions", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Account Positions: Available")
            return True
        else:
            print(f"   ❌ Account Positions: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Account Positions Exception: {e}")
        return False

def main():
    print("⚡ REAL MT5 API CONNECTIVITY TEST - BUSINESS CRITICAL")
    print("=" * 60)
    print("Testing actual MT5 endpoints for Alejandro's investment accounts")
    
    token = get_admin_token()
    if not token:
        print("❌ Authentication failed - cannot test MT5 API")
        return
    
    print("✅ Authentication successful")
    
    # Test core MT5 system
    system_working = test_mt5_system_status(token)
    realtime_working = test_mt5_realtime_data(token)
    accounts_data = test_mt5_accounts(token)
    
    # Test Alejandro's specific accounts
    alejandro_accounts = ['886557', '886602', '886066', '885822']
    working_accounts = 0
    
    print(f"\n🎯 Testing Alejandro's 4 Investment Accounts:")
    for i, account_id in enumerate(alejandro_accounts, 1):
        investment_info = [
            "Investment 1: $80,000 BALANCE",
            "Investment 2: $10,000 BALANCE", 
            "Investment 3: $10,000 BALANCE",
            "Investment 4: $18,151.41 CORE"
        ][i-1]
        
        print(f"\n--- {investment_info} → MT5: {account_id} ---")
        if test_specific_account_data(token, account_id):
            working_accounts += 1
    
    # Final assessment
    print(f"\n🏆 MT5 API CONNECTIVITY ASSESSMENT:")
    print("=" * 50)
    print(f"System Status: {'✅ Working' if system_working else '❌ Issues'}")
    print(f"Real-time Data: {'✅ Available' if realtime_working else '❌ Unavailable'}")
    print(f"Account Access: {'✅ Connected' if accounts_data else '❌ Failed'}")
    print(f"Alejandro's Accounts Working: {working_accounts}/4")
    
    # Business flow assessment
    if working_accounts >= 3 and system_working and realtime_working:
        print(f"\n🎉 MT5 API: BUSINESS FLOW OPERATIONAL")
        print("✅ Real-time data retrieval: WORKING")
        print("✅ Account monitoring: FUNCTIONAL") 
        print("✅ Investment tracking: ACTIVE")
    elif working_accounts >= 2:
        print(f"\n⚠️ MT5 API: PARTIAL FUNCTIONALITY")
        print("✅ Core business operations: WORKING")
        print("🔧 Some accounts need attention")
    else:
        print(f"\n🚨 MT5 API: CRITICAL ISSUES")
        print("❌ Business flow: SEVERELY IMPACTED")
        print("🔧 IMMEDIATE MT5 API INTEGRATION REQUIRED")
    
    print(f"\n📊 Investment Summary:")
    print(f"   Total Investments: 4 ({working_accounts} MT5 accounts working)")
    print(f"   Total Value: $118,151.41")
    print(f"   MT5 Server: MEXAtlantic-Real")
    print(f"   Business Criticality: HIGH (Real-time trading data required)")

if __name__ == "__main__":
    main()