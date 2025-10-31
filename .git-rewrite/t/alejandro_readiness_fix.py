#!/usr/bin/env python3
"""
Alejandro Readiness Fix Script
This script will directly set Alejandro's investment readiness to true
and verify the endpoints are working correctly.
"""

import requests
import json
from datetime import datetime, timezone

# Backend URL Configuration
BACKEND_URL = "https://fidus-invest.emergent.host/api"

# Admin credentials
ADMIN_CREDENTIALS = {
    "username": "admin",
    "password": "password123", 
    "user_type": "admin"
}

def authenticate_admin():
    """Get admin JWT token"""
    response = requests.post(f"{BACKEND_URL}/auth/login", json=ADMIN_CREDENTIALS, timeout=30)
    if response.status_code == 200:
        data = response.json()
        return data.get("token")
    return None

def check_alejandro_readiness(token):
    """Check Alejandro's current readiness status"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BACKEND_URL}/clients/client_alejandro/readiness", 
                          headers=headers, timeout=30)
    if response.status_code == 200:
        return response.json()
    return None

def update_alejandro_readiness(token):
    """Update Alejandro's readiness to investment ready"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Set all readiness flags to True
    readiness_data = {
        "aml_kyc_completed": True,
        "agreement_signed": True,
        "account_creation_date": datetime.now(timezone.utc).isoformat(),
        "notes": "Set to investment ready for dropdown testing",
        "updated_by": "admin_001"
    }
    
    response = requests.post(f"{BACKEND_URL}/clients/client_alejandro/readiness", 
                           json=readiness_data, headers=headers, timeout=30)
    if response.status_code == 200:
        return response.json()
    return None

def check_ready_clients(token):
    """Check the ready clients endpoint"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BACKEND_URL}/clients/ready-for-investment", 
                          headers=headers, timeout=30)
    if response.status_code == 200:
        return response.json()
    return None

def check_debug_endpoint(token):
    """Check the debug endpoint"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BACKEND_URL}/clients/ready-for-investment-debug", 
                          headers=headers, timeout=30)
    if response.status_code == 200:
        return response.json()
    return None

def main():
    print("🔧 Alejandro Readiness Fix Script")
    print("=" * 50)
    
    # Step 1: Authenticate
    print("1. Authenticating as admin...")
    token = authenticate_admin()
    if not token:
        print("❌ Failed to authenticate")
        return
    print("✅ Admin authenticated")
    
    # Step 2: Check current readiness
    print("\n2. Checking Alejandro's current readiness...")
    current_readiness = check_alejandro_readiness(token)
    if current_readiness:
        print(f"   Current status: {json.dumps(current_readiness, indent=2)}")
        investment_ready = current_readiness.get("investment_ready", False)
        print(f"   Investment Ready: {investment_ready}")
    else:
        print("❌ Failed to get current readiness")
        return
    
    # Step 3: Update readiness if needed
    if not current_readiness.get("investment_ready", False):
        print("\n3. Updating Alejandro's readiness to investment ready...")
        update_result = update_alejandro_readiness(token)
        if update_result:
            print("✅ Readiness updated successfully")
            print(f"   Update result: {json.dumps(update_result, indent=2)}")
        else:
            print("❌ Failed to update readiness")
            return
    else:
        print("\n3. Alejandro is already investment ready")
    
    # Step 4: Re-check readiness
    print("\n4. Re-checking Alejandro's readiness...")
    updated_readiness = check_alejandro_readiness(token)
    if updated_readiness:
        print(f"   Updated status: {json.dumps(updated_readiness, indent=2)}")
        investment_ready = updated_readiness.get("investment_ready", False)
        print(f"   Investment Ready: {investment_ready}")
    else:
        print("❌ Failed to get updated readiness")
        return
    
    # Step 5: Check ready clients endpoint
    print("\n5. Checking ready clients endpoint...")
    ready_clients = check_ready_clients(token)
    if ready_clients:
        print(f"   Ready clients response: {json.dumps(ready_clients, indent=2)}")
        clients = ready_clients.get("ready_clients", [])
        alejandro_found = any("alejandro" in c.get("name", "").lower() for c in clients)
        print(f"   Alejandro found in ready clients: {alejandro_found}")
        print(f"   Total ready clients: {len(clients)}")
    else:
        print("❌ Failed to get ready clients")
        return
    
    # Step 6: Check debug endpoint
    print("\n6. Checking debug endpoint...")
    debug_info = check_debug_endpoint(token)
    if debug_info:
        print(f"   Debug response: {json.dumps(debug_info, indent=2)}")
    else:
        print("❌ Failed to get debug info")
    
    print("\n" + "=" * 50)
    if ready_clients and ready_clients.get("ready_clients"):
        print("🎉 SUCCESS: Alejandro should now appear in investment dropdown")
    else:
        print("❌ ISSUE: Alejandro still not appearing in ready clients")
    print("=" * 50)

if __name__ == "__main__":
    main()