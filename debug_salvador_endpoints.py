#!/usr/bin/env python3
"""
DEBUG SALVADOR ENDPOINTS
========================
Debug the specific API endpoints to understand response formats
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://crm-workspace-1.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

def authenticate_admin():
    """Authenticate as admin user"""
    session = requests.Session()
    try:
        response = session.post(f"{BACKEND_URL}/auth/login", json={
            "username": ADMIN_USERNAME,
            "password": ADMIN_PASSWORD,
            "user_type": "admin"
        })
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("token")
            if token:
                session.headers.update({"Authorization": f"Bearer {token}"})
                print("✅ Admin authentication successful")
                return session
            else:
                print("❌ No token received")
                return None
        else:
            print(f"❌ Authentication failed: HTTP {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Authentication exception: {str(e)}")
        return None

def debug_endpoint(session, endpoint, description):
    """Debug a specific endpoint"""
    print(f"\n🔍 DEBUGGING: {description}")
    print(f"Endpoint: {endpoint}")
    print("-" * 50)
    
    try:
        response = session.get(f"{BACKEND_URL}{endpoint}")
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Response Type: {type(data)}")
                print(f"Response Content (first 1000 chars):")
                print(json.dumps(data, indent=2, default=str)[:1000])
                
                if isinstance(data, list) and len(data) > 0:
                    print(f"\nFirst item structure:")
                    print(json.dumps(data[0], indent=2, default=str))
                elif isinstance(data, dict):
                    print(f"\nKeys in response: {list(data.keys())}")
                    
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error: {e}")
                print(f"Raw response: {response.text[:500]}")
        else:
            print(f"❌ Error response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

def main():
    """Main debug execution"""
    print("🎯 SALVADOR ENDPOINTS DEBUG")
    print("=" * 50)
    
    session = authenticate_admin()
    if not session:
        print("❌ Cannot proceed without authentication")
        return
    
    # Debug critical endpoints
    endpoints = [
        ("/admin/clients", "Admin Clients List"),
        ("/investments/client/client_003", "Salvador's Investments"),
        ("/mt5/admin/accounts", "MT5 Accounts"),
        ("/fund-portfolio/overview", "Fund Portfolio Overview"),
        ("/admin/cashflow/overview", "Cash Flow Overview")
    ]
    
    for endpoint, description in endpoints:
        debug_endpoint(session, endpoint, description)
    
    print("\n" + "=" * 50)
    print("🎯 DEBUG COMPLETE")

if __name__ == "__main__":
    main()