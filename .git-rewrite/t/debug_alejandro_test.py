#!/usr/bin/env python3
"""
DEBUG ALEJANDRO READINESS - DETAILED INVESTIGATION
Investigating why the hardcoded response is not being returned to the test
"""

import requests
import json
import time
import sys
from datetime import datetime, timezone

# Backend URL Configuration
BACKEND_URL = "https://fidus-invest.emergent.host/api"

# Test credentials
ADMIN_CREDENTIALS = {
    "username": "admin",
    "password": "password123", 
    "user_type": "admin"
}

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
    if data:
        print(f"🔍 Data: {json.dumps(data, indent=2)}")
        
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=req_headers, timeout=30)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=req_headers, timeout=30)
        elif method.upper() == "PUT":
            response = requests.put(url, json=data, headers=req_headers, timeout=30)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
            
        print(f"🔍 Response Status: {response.status_code}")
        print(f"🔍 Response Headers: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print(f"🔍 Response Data: {json.dumps(response_data, indent=2)}")
        except:
            print(f"🔍 Response Text: {response.text}")
            
        return response
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None

def main():
    print("🚀 DEBUG ALEJANDRO READINESS - DETAILED INVESTIGATION")
    print("=" * 80)
    
    # Step 1: Authenticate
    print("\n🔐 Step 1: Authenticating as admin...")
    response = make_request("POST", "/auth/login", ADMIN_CREDENTIALS)
    
    if not response or response.status_code != 200:
        print("❌ Authentication failed")
        return
    
    data = response.json()
    admin_token = data.get("token")
    if not admin_token:
        print("❌ No token received")
        return
    
    print(f"✅ Admin authenticated successfully")
    
    # Step 2: Test ready-for-investment endpoint without auth
    print("\n📋 Step 2: Testing ready-for-investment endpoint WITHOUT auth...")
    response = make_request("GET", "/clients/ready-for-investment")
    
    # Step 3: Test ready-for-investment endpoint with auth
    print("\n📋 Step 3: Testing ready-for-investment endpoint WITH auth...")
    response = make_request("GET", "/clients/ready-for-investment", auth_token=admin_token)
    
    # Step 4: Test individual readiness endpoint
    print("\n🔍 Step 4: Testing individual readiness endpoint...")
    response = make_request("GET", "/clients/client_alejandro/readiness", auth_token=admin_token)
    
    # Step 5: Test alternative endpoints
    print("\n🔍 Step 5: Testing alternative endpoints...")
    
    # Try the test endpoint mentioned in logs
    response = make_request("GET", "/clients/ready-for-investment-test")
    
    # Try without the /api prefix (direct to backend)
    print("\n🔍 Step 6: Testing direct backend URL...")
    direct_url = "https://fidus-invest.emergent.host/clients/ready-for-investment"
    print(f"🔍 Making GET request to: {direct_url}")
    try:
        response = requests.get(direct_url, timeout=30)
        print(f"🔍 Response Status: {response.status_code}")
        try:
            response_data = response.json()
            print(f"🔍 Response Data: {json.dumps(response_data, indent=2)}")
        except:
            print(f"🔍 Response Text: {response.text}")
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    main()