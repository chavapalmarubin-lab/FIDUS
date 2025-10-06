#!/usr/bin/env python3
"""
Check In-Memory Storage
This script will call a custom endpoint to check what's in the in-memory client_readiness storage.
"""

import requests
import json

def get_admin_token():
    """Get admin JWT token"""
    login_data = {
        "username": "admin",
        "password": "password123", 
        "user_type": "admin"
    }
    
    response = requests.post("https://fidus-invest.emergent.host/api/auth/login", json=login_data, timeout=30)
    if response.status_code == 200:
        return response.json().get("token")
    return None

def main():
    print("🔍 Checking In-Memory Storage")
    print("=" * 40)
    
    # Get admin token
    token = get_admin_token()
    if not token:
        print("❌ Failed to get admin token")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Check debug endpoint (should show in-memory data)
    print("1. Checking debug endpoint...")
    try:
        response = requests.get("https://fidus-invest.emergent.host/api/clients/ready-for-investment-debug", 
                              headers=headers, timeout=30)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Debug response: {json.dumps(data, indent=2)}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")
    
    # Check regular endpoint
    print("\n2. Checking regular ready clients endpoint...")
    try:
        response = requests.get("https://fidus-invest.emergent.host/api/clients/ready-for-investment", 
                              headers=headers, timeout=30)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Ready clients response: {json.dumps(data, indent=2)}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")
    
    # Check individual readiness
    print("\n3. Checking individual readiness...")
    try:
        response = requests.get("https://fidus-invest.emergent.host/api/clients/client_alejandro/readiness", 
                              headers=headers, timeout=30)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Individual readiness: {json.dumps(data, indent=2)}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    main()