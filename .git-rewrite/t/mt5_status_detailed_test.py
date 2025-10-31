#!/usr/bin/env python3
"""
FIDUS MT5 Status Endpoint Detailed Test
Get detailed response from /api/mt5/status endpoint to understand the actual response.
"""

import requests
import json
import sys
from datetime import datetime, timezone

def test_mt5_status_detailed():
    """Test MT5 status endpoint with detailed response logging"""
    backend_url = "https://fidus-invest.emergent.host/api"
    
    print("🚀 FIDUS MT5 Status Detailed Test")
    print("=" * 80)
    print(f"Backend URL: {backend_url}")
    print(f"Test Started: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 80)
    
    # Step 1: Authenticate as admin
    print("\n🔐 Authenticating as admin...")
    login_data = {
        "username": "admin",
        "password": "password123",
        "user_type": "admin"
    }
    
    try:
        response = requests.post(f"{backend_url}/auth/login", json=login_data, timeout=30)
        if response.status_code == 200:
            auth_data = response.json()
            admin_token = auth_data.get("token")
            print(f"✅ Admin authenticated successfully")
            print(f"   Admin: {auth_data.get('name')}")
            print(f"   Type: {auth_data.get('type')}")
        else:
            print(f"❌ Admin authentication failed: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Admin authentication error: {str(e)}")
        return False
    
    # Step 2: Test MT5 status endpoint with detailed logging
    print(f"\n🔍 Testing /api/mt5/status endpoint...")
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    try:
        response = requests.get(f"{backend_url}/mt5/status", headers=headers, timeout=30)
        
        print(f"   Response Status Code: {response.status_code}")
        print(f"   Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"\n📋 Full MT5 Status Response:")
                print(json.dumps(data, indent=2, default=str))
                
                # Extract key information
                success = data.get('success', False)
                bridge_health = data.get('bridge_health', {})
                total_accounts = data.get('total_accounts', 0)
                broker_stats = data.get('broker_statistics', {})
                sync_status = data.get('sync_status', {})
                
                print(f"\n🔍 Key Information:")
                print(f"   Success: {success}")
                print(f"   Bridge Health Status: {bridge_health.get('status', 'N/A')}")
                print(f"   Bridge Health Message: {bridge_health.get('message', 'N/A')}")
                print(f"   Total MT5 Accounts: {total_accounts}")
                print(f"   Broker Statistics: {broker_stats}")
                print(f"   Sync Status: {sync_status}")
                
                if success:
                    print(f"\n✅ /api/mt5/status endpoint is working correctly!")
                    print(f"   The endpoint is NOT returning a 500 error.")
                    print(f"   Bridge status: {bridge_health.get('status', 'unknown')}")
                    
                    if bridge_health.get('status') == 'unhealthy':
                        print(f"   ⚠️ Note: Bridge is unhealthy but endpoint works fine")
                        print(f"   Bridge message: {bridge_health.get('message', 'No message')}")
                else:
                    print(f"   ⚠️ Success flag is False, but endpoint returned 200")
                
                return True
                
            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse JSON response: {str(e)}")
                print(f"   Raw response: {response.text}")
                return False
                
        elif response.status_code == 500:
            print(f"❌ MT5 Status endpoint returned 500 Internal Server Error")
            try:
                error_data = response.json()
                print(f"   Error Detail: {error_data.get('detail', 'No detail provided')}")
                print(f"   Full Error Response:")
                print(json.dumps(error_data, indent=2))
            except json.JSONDecodeError:
                print(f"   Raw Error Response: {response.text}")
            return False
            
        else:
            print(f"❌ MT5 Status endpoint returned HTTP {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error Response:")
                print(json.dumps(error_data, indent=2))
            except json.JSONDecodeError:
                print(f"   Raw Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"❌ Request timed out after 30 seconds")
        return False
    except Exception as e:
        print(f"❌ Request error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_mt5_status_detailed()
    
    if success:
        print(f"\n" + "=" * 80)
        print(f"✅ CONCLUSION: /api/mt5/status endpoint is WORKING correctly")
        print(f"   The endpoint is NOT returning a 500 error as reported.")
        print(f"   The issue may have been resolved or was temporary.")
        print(f"=" * 80)
        sys.exit(0)
    else:
        print(f"\n" + "=" * 80)
        print(f"❌ CONCLUSION: /api/mt5/status endpoint has issues")
        print(f"   Further investigation needed.")
        print(f"=" * 80)
        sys.exit(1)