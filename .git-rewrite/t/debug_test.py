#!/usr/bin/env python3
import requests
import json

# Get admin token
login_response = requests.post("https://fidus-invest.emergent.host/api/auth/login", 
                              json={"username":"admin","password":"password123","user_type":"admin"})
token = login_response.json()["token"]

# Test debug endpoint
headers = {"Authorization": f"Bearer {token}"}
debug_response = requests.get("https://fidus-invest.emergent.host/api/clients/ready-for-investment-debug", 
                             headers=headers)

print("Debug Response:")
print(json.dumps(debug_response.json(), indent=2))

# Test ready clients endpoint
ready_response = requests.get("https://fidus-invest.emergent.host/api/clients/ready-for-investment", 
                             headers=headers)

print("\nReady Clients Response:")
print(json.dumps(ready_response.json(), indent=2))