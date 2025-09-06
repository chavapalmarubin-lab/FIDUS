#!/usr/bin/env python3
"""
Detailed endpoint test to understand the inconsistency
"""

import requests
import json

def test_endpoints():
    base_url = "https://fund-tracker-11.preview.emergentagent.com"
    
    print("🔍 DETAILED ENDPOINT ANALYSIS")
    print("=" * 60)
    
    # Test portfolio summary multiple times
    print("\n1. Portfolio Summary - Multiple calls:")
    for i in range(3):
        try:
            response = requests.get(f"{base_url}/api/admin/portfolio-summary", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"   Call {i+1}: AUM=${data.get('total_aum', 0):,.2f}, Clients={data.get('client_count', 0)}")
                print(f"           Response: {json.dumps(data, indent=2)}")
            else:
                print(f"   Call {i+1}: Error {response.status_code}")
        except Exception as e:
            print(f"   Call {i+1}: Exception {e}")
    
    # Test cashflow overview multiple times  
    print("\n2. Cashflow Overview - Multiple calls:")
    for i in range(3):
        try:
            response = requests.get(f"{base_url}/api/admin/cashflow/overview", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"   Call {i+1}: Inflow=${data.get('total_inflow', 0):,.2f}, Outflow=${data.get('total_outflow', 0):,.2f}")
                print(f"           Response keys: {list(data.keys())}")
            else:
                print(f"   Call {i+1}: Error {response.status_code}")
        except Exception as e:
            print(f"   Call {i+1}: Exception {e}")

if __name__ == "__main__":
    test_endpoints()