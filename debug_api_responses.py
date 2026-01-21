#!/usr/bin/env python3
"""
Debug API Responses - Check actual data structure from backend
"""

import requests
import json
from pprint import pprint

def authenticate():
    """Get admin token"""
    base_url = "https://viking-trade-dash.preview.emergentagent.com/api"
    
    login_data = {
        "username": "admin",
        "password": "password123",
        "user_type": "admin"
    }
    
    response = requests.post(f"{base_url}/auth/login", json=login_data, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        return data.get('token')
    else:
        print(f"Auth failed: {response.status_code} - {response.text}")
        return None

def debug_endpoint(endpoint, token, description):
    """Debug a specific endpoint"""
    base_url = "https://viking-trade-dash.preview.emergentagent.com/api"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"\n{'='*60}")
    print(f"🔍 DEBUGGING: {description}")
    print(f"Endpoint: {endpoint}")
    print(f"{'='*60}")
    
    try:
        response = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("Response Data:")
                pprint(data, width=100, depth=3)
            except:
                print("Response Text:")
                print(response.text[:1000])
        else:
            print("Error Response:")
            print(response.text)
            
    except Exception as e:
        print(f"Request Error: {str(e)}")

def main():
    print("🔐 Authenticating...")
    token = authenticate()
    
    if not token:
        print("❌ Authentication failed")
        return
    
    print("✅ Authentication successful")
    
    # Debug all the endpoints that failed
    endpoints = [
        ("/fund-portfolio/overview", "Fund Portfolio Overview"),
        ("/admin/cashflow/overview?timeframe=3months&fund=all", "Cash Flow Obligations"),
        ("/admin/fund-performance/dashboard", "Fund Performance Dashboard"),
        ("/admin/trading-analytics/managers", "Money Managers"),
        ("/mt5/admin/accounts", "MT5 Admin Accounts")
    ]
    
    for endpoint, description in endpoints:
        debug_endpoint(endpoint, token, description)

if __name__ == "__main__":
    main()