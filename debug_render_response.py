#!/usr/bin/env python3
"""Debug exact JSON response from Render API"""
import requests
import json

BACKEND_URL = "https://fidus-api.onrender.com"

# Login
print("Logging in...")
login_response = requests.post(
    f"{BACKEND_URL}/api/auth/login",
    json={"username": "admin", "password": "password123", "user_type": "admin"},
    timeout=15
)

token = login_response.json().get('token')
print(f"✅ Got token\n")

# Get managers
print("Getting Money Managers data...")
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(f"{BACKEND_URL}/api/admin/money-managers", headers=headers, timeout=30)

print(f"Status: {response.status_code}\n")

data = response.json()

# Show exact structure
print("="*80)
print("EXACT JSON RESPONSE STRUCTURE:")
print("="*80)
print(json.dumps(data, indent=2, default=str)[:3000])
print("\n...")

# Extract manager data and show field names
if isinstance(data, dict):
    managers = data.get('managers', [])
else:
    managers = data

print("\n" + "="*80)
print(f"MANAGER FIELD NAMES (First Manager):")
print("="*80)
if managers and len(managers) > 0:
    first_manager = managers[0]
    for key, value in first_manager.items():
        print(f"  {key}: {type(value).__name__} = {value}")

