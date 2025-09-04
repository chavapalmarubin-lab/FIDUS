#!/usr/bin/env python3
"""
MongoDB Debug Test - Check if data exists and endpoints are working
"""

import requests
import sys
from datetime import datetime
import json

def test_mongodb_data():
    """Test MongoDB data directly"""
    base_url = "https://fidus-finance-1.preview.emergentagent.com"
    
    print("🔍 MONGODB DATA DEBUG TEST")
    print("=" * 50)
    
    # Test 1: Check if client investments exist in MongoDB
    print("\n1. Testing client investments endpoint...")
    try:
        response = requests.get(f"{base_url}/api/investments/client/client_001", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            investments = data.get('investments', [])
            print(f"   Investments found: {len(investments)}")
            for inv in investments:
                print(f"   - {inv.get('fund_code')}: ${inv.get('current_value', 0):,.2f}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Check admin investment overview
    print("\n2. Testing admin investment overview...")
    try:
        response = requests.get(f"{base_url}/api/investments/admin/overview", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Total AUM: ${data.get('total_aum', 0):,.2f}")
            print(f"   Total clients: {data.get('total_clients', 0)}")
            clients = data.get('clients', [])
            print(f"   Clients in array: {len(clients)}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: Check portfolio summary (the failing one)
    print("\n3. Testing portfolio summary (FAILING ENDPOINT)...")
    try:
        response = requests.get(f"{base_url}/api/admin/portfolio-summary", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Total AUM: ${data.get('total_aum', 0):,.2f}")
            print(f"   Client count: {data.get('client_count', 0)}")
            print(f"   Allocation: {data.get('allocation', {})}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 4: Check cashflow overview (the other failing one)
    print("\n4. Testing cashflow overview (FAILING ENDPOINT)...")
    try:
        response = requests.get(f"{base_url}/api/admin/cashflow/overview", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Total inflow: ${data.get('total_inflow', 0):,.2f}")
            print(f"   Total outflow: ${data.get('total_outflow', 0):,.2f}")
            print(f"   Cash flows count: {len(data.get('cash_flows', []))}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    test_mongodb_data()