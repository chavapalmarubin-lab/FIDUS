#!/usr/bin/env python3
"""
Google Workspace API Detailed Response Analysis

This script will make detailed calls to each endpoint to see the actual responses
and understand what's happening with the Google OAuth integration.
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://fidus-finance-4.preview.emergentagent.com"

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

def authenticate():
    """Authenticate as admin and get JWT token"""
    session = requests.Session()
    
    try:
        auth_url = f"{BACKEND_URL}/api/auth/login"
        payload = {
            "username": ADMIN_USERNAME,
            "password": ADMIN_PASSWORD,
            "user_type": "admin"
        }
        
        response = session.post(auth_url, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            if token:
                session.headers.update({'Authorization': f'Bearer {token}'})
                print(f"✅ Successfully authenticated as {ADMIN_USERNAME}")
                return session
            else:
                print("❌ No token in response")
                return None
        else:
            print(f"❌ Authentication failed: HTTP {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Authentication exception: {str(e)}")
        return None

def test_endpoint_detailed(session, endpoint_name, endpoint_path):
    """Test an endpoint and show detailed response"""
    print(f"\n🔍 TESTING {endpoint_name}")
    print("=" * 60)
    
    try:
        url = f"{BACKEND_URL}{endpoint_path}"
        print(f"URL: {url}")
        
        response = session.get(url)
        print(f"HTTP Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        try:
            data = response.json()
            print(f"Response JSON:")
            print(json.dumps(data, indent=2))
            
            # Analyze the response
            if response.status_code == 200:
                if data.get('success'):
                    print("✅ SUCCESS: Endpoint returned success=True")
                    if 'data' in data:
                        print(f"📊 Data returned: {len(data.get('data', []))} items")
                else:
                    print("⚠️  SUCCESS with success=False - likely OAuth not connected")
            elif response.status_code == 401:
                print("🔐 AUTH ERROR: Authentication required")
            elif response.status_code == 500:
                print("🚨 SERVER ERROR: Internal server error")
            else:
                print(f"❓ UNEXPECTED STATUS: {response.status_code}")
                
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON response:")
            print(response.text[:500])
            
    except Exception as e:
        print(f"❌ Exception testing {endpoint_name}: {str(e)}")

def main():
    """Main detailed analysis"""
    print("🔍 GOOGLE WORKSPACE API DETAILED RESPONSE ANALYSIS")
    print("=" * 80)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Analysis Time: {datetime.now().isoformat()}")
    
    # Authenticate
    session = authenticate()
    if not session:
        print("❌ Cannot proceed without authentication")
        sys.exit(1)
    
    # Test each endpoint in detail
    endpoints = [
        ("Google Calendar", "/api/admin/google/calendar/events"),
        ("Google Drive", "/api/admin/google/drive/files"),
        ("Google Sheets", "/api/admin/google/sheets/spreadsheets")
    ]
    
    for endpoint_name, endpoint_path in endpoints:
        test_endpoint_detailed(session, endpoint_name, endpoint_path)
    
    print("\n" + "=" * 80)
    print("📋 ANALYSIS COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()