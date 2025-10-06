#!/usr/bin/env python3
"""
Debug test to see exactly what's being returned from the routing fix endpoints
"""

import requests
import json
from datetime import datetime, timezone

# Backend URL Configuration
BACKEND_URL = "https://fidus-invest.emergent.host/api"

def make_request(method, endpoint, data=None, headers=None, auth_token=None):
    """Make HTTP request with detailed logging"""
    url = f"{BACKEND_URL}{endpoint}"
    
    # Set up headers
    req_headers = {"Content-Type": "application/json"}
    if headers:
        req_headers.update(headers)
    if auth_token:
        req_headers["Authorization"] = f"Bearer {auth_token}"
        
    print(f"🔍 Making {method} request to: {url}")
    print(f"🔍 Headers: {req_headers}")
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=req_headers, timeout=30)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=req_headers, timeout=30)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
            
        print(f"🔍 Response Status: {response.status_code}")
        print(f"🔍 Response Headers: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print(f"🔍 Response Data: {json.dumps(response_data, indent=2)}")
        except json.JSONDecodeError:
            print(f"🔍 Response Text: {response.text}")
            
        return response
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None

def main():
    print("🚀 Debug Routing Test")
    print("=" * 50)
    
    # First authenticate
    print("\n1. Authenticating as admin...")
    login_payload = {
        "username": "admin",
        "password": "password123",
        "user_type": "admin"
    }
    
    response = make_request("POST", "/auth/login", login_payload)
    if not response or response.status_code != 200:
        print("❌ Authentication failed")
        return
    
    data = response.json()
    admin_token = data.get("token")
    print(f"✅ Admin token obtained: {admin_token[:50]}...")
    
    print("\n2. Testing ready-for-investment endpoint...")
    response = make_request("GET", "/clients/ready-for-investment", auth_token=admin_token)
    
    print("\n3. Testing individual readiness endpoint...")
    response = make_request("GET", "/clients/client_alejandro/readiness", auth_token=admin_token)
    
    print("\n4. Testing debug endpoints...")
    response = make_request("GET", "/clients/ready-for-investment-test", auth_token=admin_token)
    response = make_request("GET", "/clients/ready-for-investment-debug", auth_token=admin_token)

if __name__ == "__main__":
    main()