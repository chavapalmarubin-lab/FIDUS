#!/usr/bin/env python3
"""
Debug Production APIs - Investigate API response structures
"""

import requests
import json
from datetime import datetime

def authenticate():
    """Authenticate and get token"""
    base_url = "https://fidus-api.onrender.com/api"
    
    login_data = {
        "username": "admin",
        "password": "password123",
        "user_type": "admin"
    }
    
    response = requests.post(f"{base_url}/auth/login", json=login_data, timeout=30)
    
    if response.status_code == 200:
        data = response.json()
        token = data.get('token')
        return token, base_url
    else:
        print(f"Authentication failed: {response.status_code} - {response.text}")
        return None, None

def debug_api_endpoint(url, headers, endpoint_name):
    """Debug a specific API endpoint"""
    print(f"\n{'='*60}")
    print(f"🔍 DEBUGGING: {endpoint_name}")
    print(f"URL: {url}")
    print(f"{'='*60}")
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Response Type: {type(data)}")
                
                if isinstance(data, dict):
                    print(f"Keys: {list(data.keys())}")
                    
                    # Print first few items for inspection
                    for key, value in list(data.items())[:5]:
                        print(f"  {key}: {type(value)} - {str(value)[:100]}...")
                        
                elif isinstance(data, list):
                    print(f"List Length: {len(data)}")
                    if data:
                        print(f"First Item Type: {type(data[0])}")
                        if isinstance(data[0], dict):
                            print(f"First Item Keys: {list(data[0].keys())}")
                
                # Save full response for detailed inspection
                with open(f"/app/debug_{endpoint_name.lower().replace(' ', '_')}_response.json", "w") as f:
                    json.dump(data, f, indent=2, default=str)
                print(f"Full response saved to debug_{endpoint_name.lower().replace(' ', '_')}_response.json")
                
            except json.JSONDecodeError:
                print(f"Response is not JSON: {response.text[:200]}...")
        else:
            print(f"Error Response: {response.text}")
            
    except Exception as e:
        print(f"Exception: {str(e)}")

def main():
    """Debug main production APIs"""
    print("🔍 DEBUGGING PRODUCTION API RESPONSES")
    
    # Authenticate
    token, base_url = authenticate()
    if not token:
        return
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # Debug key endpoints
    endpoints = [
        (f"{base_url}/mt5/accounts/corrected", "MT5 Accounts Corrected"),
        (f"{base_url}/fund-portfolio/overview", "Fund Portfolio Overview"),
        (f"{base_url}/mt5/status", "MT5 Status"),
        (f"{base_url}/funds/BALANCE/performance", "BALANCE Fund Performance"),
        (f"{base_url}/mt5/admin/accounts", "MT5 Admin Accounts")
    ]
    
    for url, name in endpoints:
        debug_api_endpoint(url, headers, name)
    
    # Also test VPS Bridge directly
    print(f"\n{'='*60}")
    print(f"🔍 DEBUGGING: VPS Bridge Direct")
    print(f"URL: http://92.118.45.135:8000/api/mt5/accounts/summary")
    print(f"{'='*60}")
    
    try:
        response = requests.get("http://92.118.45.135:8000/api/mt5/accounts/summary", timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"VPS Response Type: {type(data)}")
            
            if isinstance(data, dict):
                print(f"VPS Keys: {list(data.keys())}")
                accounts = data.get("accounts", [])
                print(f"VPS Accounts Count: {len(accounts)}")
                
                if accounts:
                    print(f"First VPS Account: {accounts[0]}")
                    
                    # Look for account 886557
                    account_886557 = next((acc for acc in accounts if str(acc.get("account")) == "886557"), None)
                    if account_886557:
                        print(f"Account 886557 Data: {account_886557}")
            
            # Save VPS response
            with open(f"/app/debug_vps_bridge_response.json", "w") as f:
                json.dump(data, f, indent=2, default=str)
            print(f"VPS response saved to debug_vps_bridge_response.json")
            
    except Exception as e:
        print(f"VPS Exception: {str(e)}")

if __name__ == "__main__":
    main()