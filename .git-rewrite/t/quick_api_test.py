#!/usr/bin/env python3
"""
Quick API test after backend restart
"""

import requests
import json

def test_api_endpoints():
    base_url = "https://fidus-invest.emergent.host"
    
    # Authenticate
    print("🔍 Authenticating...")
    auth_response = requests.post(
        f"{base_url}/api/auth/login",
        json={
            "username": "admin",
            "password": "password123",
            "user_type": "admin"
        },
        timeout=10
    )
    
    if auth_response.status_code != 200:
        print(f"❌ Authentication failed: {auth_response.status_code}")
        return
    
    token = auth_response.json().get('token')
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    
    print("✅ Authenticated successfully")
    
    # Test endpoints
    endpoints = [
        ("Salvador Investments", "api/investments/client/client_003"),
        ("MT5 Admin Accounts", "api/mt5/admin/accounts"),
        ("Admin Clients", "api/admin/clients"),
    ]
    
    for name, endpoint in endpoints:
        print(f"\n🔍 Testing {name}...")
        try:
            response = requests.get(f"{base_url}/{endpoint}", headers=headers, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Response keys: {list(data.keys())}")
                
                if 'investments' in data:
                    investments = data['investments']
                    print(f"   Investments: {len(investments)}")
                    for inv in investments:
                        print(f"     - {inv.get('fund_code')} ${inv.get('principal_amount')}")
                
                if 'accounts' in data:
                    accounts = data['accounts']
                    print(f"   MT5 Accounts: {len(accounts)}")
                    for acc in accounts:
                        print(f"     - {acc.get('broker')} Login: {acc.get('login')}")
                
                if 'clients' in data:
                    clients = data['clients']
                    print(f"   Clients: {len(clients)}")
                    for client in clients:
                        print(f"     - {client.get('name')} (ID: {client.get('id')})")
            else:
                print(f"   ❌ Failed: {response.text[:200]}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_api_endpoints()