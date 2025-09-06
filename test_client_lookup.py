#!/usr/bin/env python3
import requests
import json

# Get admin token
login_response = requests.post(
    "https://fund-performance.preview.emergentagent.com/api/auth/login",
    json={
        "username": "admin", 
        "password": "password123",
        "user_type": "admin"
    }
)

if login_response.status_code == 200:
    token = login_response.json().get('token')
    print(f"Admin token obtained")
    
    # Test the manual account creation with minimal data to see the exact error
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    test_account = {
        "client_id": "client_001",
        "fund_code": "CORE", 
        "broker_code": "dootechnology",
        "mt5_login": 9928326,
        "mt5_password": "R1d567j!",
        "mt5_server": "DooTechnology-Live",
        "allocated_amount": 100000.00
    }
    
    print(f"\nTesting manual account creation...")
    response = requests.post(
        "https://fund-performance.preview.emergentagent.com/api/mt5/admin/add-manual-account",
        json=test_account,
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
else:
    print(f"Failed to login: {login_response.status_code}")
    print(login_response.text)