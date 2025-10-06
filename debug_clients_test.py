#!/usr/bin/env python3
"""
Debug test to check what get_all_clients returns
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

# Check all clients endpoint
print("\n🔍 Checking all clients endpoint...")
response = requests.get(f"{BACKEND_URL}/admin/clients", headers=headers)
print(f"All clients response status: {response.status_code}")
if response.status_code == 200:
    clients_data = response.json()
    print(f"All clients response: {json.dumps(clients_data, indent=2)}")
    
    # Look for Alejandro specifically
    clients = clients_data.get("clients", [])
    for client in clients:
        if "alejandro" in client.get("name", "").lower():
            print(f"\n🎯 Found Alejandro: {json.dumps(client, indent=2)}")
else:
    print(f"All clients response: {response.text}")