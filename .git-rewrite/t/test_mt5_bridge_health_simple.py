#!/usr/bin/env python3
"""
Simple test to isolate MT5 Bridge Health endpoint issue
"""

import requests
import json

def test_mt5_bridge_health():
    """Test MT5 Bridge Health endpoint specifically"""
    
    # Step 1: Login as admin
    print("🔐 Step 1: Admin Login")
    login_response = requests.post(
        'https://fidus-invest.emergent.host/api/auth/login',
        json={
            'username': 'admin',
            'password': 'password123',
            'user_type': 'admin'
        }
    )
    
    if login_response.status_code != 200:
        print(f"❌ Admin login failed: {login_response.status_code}")
        print(f"Response: {login_response.text}")
        return False
    
    token = login_response.json().get('token')
    print(f"✅ Admin login successful, token: {token[:20]}...")
    
    # Step 2: Test MT5 Bridge Health endpoint
    print("\n🏥 Step 2: MT5 Bridge Health Endpoint Test")
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Test the endpoint
    health_response = requests.get(
        'https://fidus-invest.emergent.host/api/mt5/bridge/health',
        headers=headers
    )
    
    print(f"Status Code: {health_response.status_code}")
    print(f"Response Headers: {dict(health_response.headers)}")
    print(f"Response Text: {health_response.text}")
    
    if health_response.status_code == 404:
        print("❌ CRITICAL: MT5 Bridge Health endpoint returns 404 - NOT REGISTERED")
        return False
    elif health_response.status_code == 200:
        print("✅ SUCCESS: MT5 Bridge Health endpoint returns 200 OK")
        try:
            response_data = health_response.json()
            print(f"Response JSON: {json.dumps(response_data, indent=2)}")
        except:
            print("Response is not JSON")
        return True
    else:
        print(f"⚠️ UNEXPECTED: MT5 Bridge Health endpoint returns {health_response.status_code}")
        return False

def test_other_mt5_endpoints():
    """Test other MT5 endpoints to see if they work"""
    
    # Login as admin
    login_response = requests.post(
        'https://fidus-invest.emergent.host/api/auth/login',
        json={
            'username': 'admin',
            'password': 'password123',
            'user_type': 'admin'
        }
    )
    
    if login_response.status_code != 200:
        print(f"❌ Admin login failed for other tests")
        return
    
    token = login_response.json().get('token')
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Test other MT5 endpoints
    mt5_endpoints = [
        '/api/mt5/admin/accounts',
        '/api/mt5/brokers',
        '/api/mt5/admin/system-status',
        '/api/mt5/status'  # This is defined with @app.get
    ]
    
    print("\n🔍 Testing other MT5 endpoints:")
    for endpoint in mt5_endpoints:
        response = requests.get(f'https://fidus-invest.emergent.host{endpoint}', headers=headers)
        print(f"   {endpoint}: {response.status_code}")

if __name__ == "__main__":
    print("🧪 MT5 Bridge Health Endpoint Isolation Test")
    print("=" * 60)
    
    success = test_mt5_bridge_health()
    test_other_mt5_endpoints()
    
    if success:
        print("\n✅ MT5 Bridge Health endpoint is working!")
    else:
        print("\n❌ MT5 Bridge Health endpoint has issues!")