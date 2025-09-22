#!/usr/bin/env python3
"""
Simple CRM test to isolate the issue
"""

import requests
import json

BACKEND_URL = "https://fidus-invest.emergent.host/api"

def test_without_auth():
    """Test without authentication"""
    prospect_data = {
        "name": "Simple Test",
        "email": "simple@test.com", 
        "phone": "+1-555-SIMPLE",
        "notes": "Simple test"
    }
    
    response = requests.post(f"{BACKEND_URL}/crm/prospects", json=prospect_data)
    print(f"Without auth: {response.status_code} - {response.text}")

def test_with_auth():
    """Test with authentication"""
    # Get token
    login_response = requests.post(f"{BACKEND_URL}/auth/login", json={
        "username": "admin",
        "password": "password123", 
        "user_type": "admin"
    })
    
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.status_code}")
        return
        
    token = login_response.json().get("token")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    prospect_data = {
        "name": "Auth Test",
        "email": "auth@test.com",
        "phone": "+1-555-AUTH", 
        "notes": "Auth test"
    }
    
    response = requests.post(f"{BACKEND_URL}/crm/prospects", json=prospect_data, headers=headers)
    print(f"With auth: {response.status_code} - {response.text}")

def test_health():
    """Test health endpoint"""
    response = requests.get(f"{BACKEND_URL}/health")
    print(f"Health: {response.status_code} - {response.text}")

if __name__ == "__main__":
    print("=== SIMPLE CRM TEST ===")
    test_health()
    test_without_auth()
    test_with_auth()