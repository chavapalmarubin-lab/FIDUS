#!/usr/bin/env python3
"""
Simple test to debug readiness update issue
"""

import requests
import json

BACKEND_URL = "https://fidus-invest.emergent.host/api"

# Get admin token
login_data = {
    "username": "admin",
    "password": "password123",
    "user_type": "admin"
}

print("🔐 Logging in as admin...")
response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
if response.status_code == 200:
    token = response.json()["token"]
    print("✅ Admin login successful")
else:
    print(f"❌ Admin login failed: {response.status_code}")
    exit(1)

headers = {"Authorization": f"Bearer {token}"}

# Check current readiness
print("\n🔍 Checking current readiness...")
response = requests.get(f"{BACKEND_URL}/clients/client_alejandro/readiness", headers=headers)
if response.status_code == 200:
    current = response.json()
    print(f"Current readiness: {json.dumps(current, indent=2)}")
else:
    print(f"❌ Failed to get readiness: {response.status_code}")
    print(response.text)

# Update readiness
print("\n🔧 Updating readiness...")
update_data = {
    "aml_kyc_completed": True,
    "agreement_signed": True,
    "notes": "Test update",
    "updated_by": "admin"
}

response = requests.put(f"{BACKEND_URL}/clients/client_alejandro/readiness", 
                       json=update_data, headers=headers)
print(f"Update response status: {response.status_code}")
print(f"Update response: {response.text}")

# Check readiness after update
print("\n🔍 Checking readiness after update...")
response = requests.get(f"{BACKEND_URL}/clients/client_alejandro/readiness", headers=headers)
if response.status_code == 200:
    updated = response.json()
    print(f"Updated readiness: {json.dumps(updated, indent=2)}")
else:
    print(f"❌ Failed to get updated readiness: {response.status_code}")

# Check ready clients endpoint
print("\n🔍 Checking ready clients endpoint...")
response = requests.get(f"{BACKEND_URL}/clients/ready-for-investment", headers=headers)
print(f"Ready clients response status: {response.status_code}")
if response.status_code == 200:
    ready_data = response.json()
    print(f"Ready clients: {json.dumps(ready_data, indent=2)}")
else:
    print(f"Ready clients response: {response.text}")