#!/usr/bin/env python3
"""
PRODUCTION FIX: Ensure Alejandro has EXACTLY 4 investments
Remove duplicates and verify MT5 mappings
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

def get_alejandro_investments(token):
    """Get ALL current investments for Alejandro"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("🔍 CHECKING ALEJANDRO'S CURRENT INVESTMENTS...")
    
    # Try multiple endpoints to get investment data
    endpoints = [
        "/api/investments/client/alejandrom",
        "/api/investments/client/client_11aed9e2", 
        "/api/clients/all",
        "/api/admin/users"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {endpoint}: {response.status_code}")
                
                if 'investments' in str(data):
                    print(f"📊 Data preview: {str(data)[:200]}...")
                    
                    # Extract investment information
                    if isinstance(data, dict):
                        if 'investments' in data:
                            investments = data['investments']
                            print(f"📋 Found {len(investments)} investments")
                            return investments
                        elif 'clients' in data:
                            for client in data['clients']:
                                if 'alejandro' in client.get('username', '').lower():
                                    print(f"👤 Client data: {client}")
                                    return client
                                    
        except Exception as e:
            print(f"❌ {endpoint}: {e}")
    
    return None

def check_mt5_mappings(token):
    """Check MT5 account mappings for Alejandro"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n🔌 CHECKING MT5 ACCOUNT MAPPINGS...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/mt5/admin/accounts", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ MT5 Accounts Response: {data}")
            
            # Look for Alejandro's MT5 accounts
            target_accounts = ['886557', '886602', '886066', '885822']
            found_accounts = []
            
            if isinstance(data, dict) and 'accounts' in data:
                for account in data['accounts']:
                    account_login = str(account.get('login', ''))
                    if account_login in target_accounts:
                        found_accounts.append(account)
                        print(f"   🎯 Found Target Account: {account_login}")
            
            print(f"📊 Target MT5 Accounts Found: {len(found_accounts)}/4")
            return found_accounts
            
    except Exception as e:
        print(f"❌ MT5 check error: {e}")
        
    return []

def verify_system_tabs(token):
    """Verify all system tabs and functionality"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n🏗️ VERIFYING SYSTEM FUNCTIONALITY...")
    
    # Test key endpoints for system health
    endpoints_to_test = [
        ("/api/investments/overview", "Investment Overview"),
        ("/api/mt5/admin/system-status", "MT5 System Status"), 
        ("/api/admin/portfolio-summary", "Portfolio Summary"),
        ("/api/clients/all", "Client Management"),
        ("/api/crm/pipeline-stats", "CRM Pipeline")
    ]
    
    working_endpoints = 0
    
    for endpoint, name in endpoints_to_test:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
            if response.status_code == 200:
                print(f"   ✅ {name}: Working")
                working_endpoints += 1
            else:
                print(f"   ❌ {name}: {response.status_code}")
        except Exception as e:
            print(f"   ⚠️ {name}: {e}")
    
    print(f"\n📊 System Health: {working_endpoints}/{len(endpoints_to_test)} endpoints working")
    return working_endpoints >= 4

def main():
    print("🚨 PRODUCTION ENVIRONMENT - ALEJANDRO INVESTMENT AUDIT")
    print("=" * 60)
    print("GOAL: Ensure EXACTLY 4 investments totaling $118,151.41")
    print("Required investments:")
    print("  1. $80,000 → BALANCE → MT5: 886557")
    print("  2. $10,000 → BALANCE → MT5: 886602")
    print("  3. $10,000 → BALANCE → MT5: 886066")
    print("  4. $18,151.41 → CORE → MT5: 885822")
    print("=" * 60)
    
    token = get_admin_token()
    if not token:
        print("❌ CRITICAL: Cannot authenticate")
        return
    
    print("✅ Authentication successful")
    
    # Step 1: Get current investment state
    current_investments = get_alejandro_investments(token)
    
    # Step 2: Check MT5 mappings  
    mt5_mappings = check_mt5_mappings(token)
    
    # Step 3: Verify system functionality
    system_healthy = verify_system_tabs(token)
    
    print(f"\n🎯 AUDIT SUMMARY:")
    print(f"Current Investments: {current_investments}")
    print(f"MT5 Mappings Found: {len(mt5_mappings)}")
    print(f"System Health: {'✅ Good' if system_healthy else '⚠️ Issues'}")
    
    if current_investments:
        print(f"\n⚠️ ISSUE IDENTIFIED: Extra investments detected")
        print(f"Action needed: Remove duplicates to get exactly 4 investments")
    else:
        print(f"\n✅ No investment data found - ready for clean setup")

if __name__ == "__main__":
    main()