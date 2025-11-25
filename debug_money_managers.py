#!/usr/bin/env python3
"""
DEBUG MONEY MANAGERS ENDPOINTS
Examine the actual API responses to understand data structure
"""

import requests
import json
from pprint import pprint

def debug_endpoints():
    base_url = "https://truth-fincore.preview.emergentagent.com/api"
    session = requests.Session()
    
    # Authenticate
    login_data = {
        "username": "admin",
        "password": "password123",
        "user_type": "admin"
    }
    
    response = session.post(f"{base_url}/auth/login", json=login_data)
    if response.status_code == 200:
        token = response.json().get('token')
        session.headers.update({'Authorization': f'Bearer {token}'})
        print("✅ Authenticated successfully")
    else:
        print("❌ Authentication failed")
        return
    
    print("\n" + "="*80)
    print("OVERVIEW TAB ENDPOINT: /api/admin/money-managers")
    print("="*80)
    
    response = session.get(f"{base_url}/admin/money-managers")
    if response.status_code == 200:
        data = response.json()
        print("Response structure:")
        pprint(data, width=120, depth=3)
        
        if 'managers' in data:
            print(f"\nFound {len(data['managers'])} managers:")
            for i, manager in enumerate(data['managers']):
                print(f"\nManager {i+1}:")
                pprint(manager, width=120, depth=2)
    else:
        print(f"❌ Failed: HTTP {response.status_code}")
        print(response.text)
    
    print("\n" + "="*80)
    print("COMPARE TAB ENDPOINT: /api/admin/trading-analytics/managers")
    print("="*80)
    
    response = session.get(f"{base_url}/admin/trading-analytics/managers")
    if response.status_code == 200:
        data = response.json()
        print("Response structure:")
        pprint(data, width=120, depth=3)
        
        if 'managers' in data:
            print(f"\nFound {len(data['managers'])} managers:")
            for i, manager in enumerate(data['managers']):
                print(f"\nManager {i+1}:")
                pprint(manager, width=120, depth=2)
    else:
        print(f"❌ Failed: HTTP {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    debug_endpoints()