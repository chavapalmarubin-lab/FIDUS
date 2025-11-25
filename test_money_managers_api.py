#!/usr/bin/env python3
"""
Test the Money Managers API endpoint
"""
import requests
import json
import os

# Get backend URL
backend_url = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')

print("=" * 80)
print("TESTING MONEY MANAGERS API ENDPOINT")
print("=" * 80)
print(f"\nBackend URL: {backend_url}")
print(f"Endpoint: {backend_url}/api/v2/derived/money-managers\n")

try:
    response = requests.get(f"{backend_url}/api/v2/derived/money-managers", timeout=10)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}\n")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ SUCCESS - API returned 200 OK\n")
        print(json.dumps(data, indent=2))
        
        if data.get('success'):
            managers = data.get('managers', {})
            print(f"\n✅ Found {len(managers)} managers in response")
            
            for mgr_name, mgr_data in managers.items():
                print(f"\n{mgr_name}:")
                print(f"  Accounts: {mgr_data.get('account_count', 0)}")
                print(f"  Allocation: ${mgr_data.get('total_allocation', 0):,.2f}")
                print(f"  Balance: ${mgr_data.get('total_balance', 0):,.2f}")
                print(f"  P&L: ${mgr_data.get('total_pnl', 0):,.2f}")
        else:
            print(f"\n❌ API returned success=False: {data.get('message')}")
    else:
        print(f"❌ ERROR - Status {response.status_code}")
        print(f"Response: {response.text}")
        
except requests.exceptions.Timeout:
    print("❌ ERROR - Request timed out")
except requests.exceptions.ConnectionError as e:
    print(f"❌ ERROR - Connection failed: {e}")
except Exception as e:
    print(f"❌ ERROR - {type(e).__name__}: {e}")

print("\n" + "=" * 80)
