#!/usr/bin/env python3
"""
Debug CRM endpoint issues
"""

import requests
import json

BACKEND_URL = "https://fidus-invest.emergent.host/api"

def get_admin_token():
    """Get admin token"""
    response = requests.post(f"{BACKEND_URL}/auth/login", json={
        "username": "admin",
        "password": "password123",
        "user_type": "admin"
    })
    
    if response.status_code == 200:
        return response.json().get("token")
    else:
        print(f"Login failed: {response.status_code} - {response.text}")
        return None

def test_get_prospects():
    """Test GET prospects"""
    token = get_admin_token()
    if not token:
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BACKEND_URL}/crm/prospects", headers=headers)
    
    print(f"GET /crm/prospects: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response type: {type(data)}")
        print(f"Response keys: {data.keys() if isinstance(data, dict) else 'Not a dict'}")
        if isinstance(data, dict) and 'prospects' in data:
            print(f"Prospects count: {len(data['prospects'])}")
    else:
        print(f"Error: {response.text}")

def test_create_prospect():
    """Test POST create prospect"""
    token = get_admin_token()
    if not token:
        return
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    prospect_data = {
        "name": "Debug Test Prospect",
        "email": "debug@test.com",
        "phone": "+1-555-DEBUG",
        "notes": "Debug test prospect"
    }
    
    response = requests.post(f"{BACKEND_URL}/crm/prospects", headers=headers, json=prospect_data)
    
    print(f"POST /crm/prospects: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data}")
    else:
        print(f"Error: {response.text}")

def test_pipeline():
    """Test GET pipeline"""
    token = get_admin_token()
    if not token:
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BACKEND_URL}/crm/prospects/pipeline", headers=headers)
    
    print(f"GET /crm/prospects/pipeline: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Pipeline data type: {type(data)}")
        if isinstance(data, dict):
            print(f"Pipeline keys: {data.keys()}")
            if 'pipeline' in data:
                pipeline = data['pipeline']
                print(f"Pipeline stages: {list(pipeline.keys())}")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    print("=== DEBUG CRM ENDPOINTS ===")
    test_get_prospects()
    print()
    test_create_prospect()
    print()
    test_pipeline()