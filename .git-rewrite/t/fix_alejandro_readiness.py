#!/usr/bin/env python3
"""
Fix Alejandro's Investment Readiness
This script will manually set Alejandro's readiness status to make him appear in the investment dropdown.
"""

import requests
import json
from datetime import datetime, timezone

# Backend URL Configuration
BACKEND_URL = "https://fidus-invest.emergent.host/api"

def get_admin_token():
    """Get admin JWT token"""
    login_data = {
        "username": "admin",
        "password": "password123", 
        "user_type": "admin"
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data, timeout=30)
    if response.status_code == 200:
        return response.json().get("token")
    return None

def set_alejandro_readiness(token):
    """Set Alejandro's readiness to investment ready"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Set all required flags to True
    readiness_data = {
        "aml_kyc_completed": True,
        "agreement_signed": True,
        "account_creation_date": datetime.now(timezone.utc).isoformat(),
        "notes": "Manually set to investment ready - has all required documents",
        "updated_by": "admin_001"
    }
    
    print(f"Setting readiness data: {json.dumps(readiness_data, indent=2)}")
    
    response = requests.put(f"{BACKEND_URL}/clients/client_alejandro/readiness", 
                          json=readiness_data, headers=headers, timeout=30)
    
    print(f"Response status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        return result
    else:
        print(f"Error response: {response.text}")
        return None

def check_ready_clients(token):
    """Check if Alejandro appears in ready clients"""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BACKEND_URL}/clients/ready-for-investment", 
                          headers=headers, timeout=30)
    
    if response.status_code == 200:
        return response.json()
    return None

def main():
    print("🔧 Fixing Alejandro's Investment Readiness")
    print("=" * 50)
    
    # Get admin token
    print("1. Getting admin token...")
    token = get_admin_token()
    if not token:
        print("❌ Failed to get admin token")
        return
    print("✅ Got admin token")
    
    # Set Alejandro's readiness
    print("\n2. Setting Alejandro's readiness...")
    result = set_alejandro_readiness(token)
    if not result:
        print("❌ Failed to set readiness")
        return
    print("✅ Readiness set successfully")
    
    # Check ready clients
    print("\n3. Checking ready clients endpoint...")
    ready_clients = check_ready_clients(token)
    if ready_clients:
        print(f"Ready clients response: {json.dumps(ready_clients, indent=2)}")
        
        clients = ready_clients.get("ready_clients", [])
        alejandro_found = any("alejandro" in c.get("name", "").lower() for c in clients)
        
        print(f"\nTotal ready clients: {len(clients)}")
        print(f"Alejandro found: {alejandro_found}")
        
        if alejandro_found:
            print("🎉 SUCCESS: Alejandro is now ready for investment!")
        else:
            print("❌ ISSUE: Alejandro still not appearing in ready clients")
    else:
        print("❌ Failed to get ready clients")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()