#!/usr/bin/env python3
"""
Database Check for Alejandro Mariscal Production Setup
"""

import requests
import json

BACKEND_URL = "https://trading-platform-76.preview.emergentagent.com/api"

def authenticate():
    """Get admin token"""
    response = requests.post(f"{BACKEND_URL}/auth/login", json={
        "username": "admin",
        "password": "password123",
        "user_type": "admin"
    })
    
    if response.status_code == 200:
        return response.json().get('token')
    return None

def check_database():
    """Check current database state"""
    token = authenticate()
    if not token:
        print("❌ Authentication failed")
        return
    
    headers = {'Authorization': f'Bearer {token}'}
    
    print("🔍 CURRENT DATABASE STATE CHECK")
    print("=" * 50)
    
    # Check ready clients
    print("\n1. Ready for Investment Clients:")
    response = requests.get(f"{BACKEND_URL}/clients/ready-for-investment", headers=headers)
    if response.status_code == 200:
        data = response.json()
        clients = data.get('ready_clients', [])
        print(f"   Found {len(clients)} ready clients:")
        for client in clients:
            print(f"   - ID: {client.get('client_id')}")
            print(f"     Name: {client.get('name')}")
            print(f"     Email: {client.get('email')}")
            print(f"     Investments: {client.get('total_investments', 0)}")
    else:
        print(f"   ❌ Error: {response.status_code}")
    
    # Check client_alejandro investments
    print("\n2. client_alejandro Investments:")
    response = requests.get(f"{BACKEND_URL}/clients/client_alejandro/investments", headers=headers)
    if response.status_code == 200:
        data = response.json()
        investments = data.get('investments', [])
        print(f"   Found {len(investments)} investments:")
        for inv in investments:
            print(f"   - Fund: {inv.get('fund_code')}")
            print(f"     Amount: ${inv.get('current_value', 0):,.2f}")
            print(f"     Date: {inv.get('deposit_date')}")
    else:
        print(f"   ❌ Error: {response.status_code} - {response.text}")
    
    # Check MT5 accounts
    print("\n3. client_alejandro MT5 Accounts:")
    response = requests.get(f"{BACKEND_URL}/mt5/accounts/client_alejandro", headers=headers)
    if response.status_code == 200:
        data = response.json()
        accounts = data.get('accounts', [])
        print(f"   Found {len(accounts)} MT5 accounts:")
        for acc in accounts:
            print(f"   - Account: {acc.get('mt5_account_number')}")
            print(f"     Broker: {acc.get('broker_name')}")
            print(f"     Balance: ${acc.get('balance', 0):,.2f}")
    else:
        print(f"   ❌ Error: {response.status_code} - {response.text}")
    
    # Check admin overview
    print("\n4. Admin Overview:")
    response = requests.get(f"{BACKEND_URL}/investments/admin/overview", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"   Total AUM: {data.get('total_aum', '$0.00')}")
        print(f"   Total Investments: {data.get('total_investments', 0)}")
        print(f"   Total Clients: {data.get('total_clients', 0)}")
    else:
        print(f"   ❌ Error: {response.status_code}")

if __name__ == "__main__":
    check_database()