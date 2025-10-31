#!/usr/bin/env python3
"""
OAuth Connection Debug Test - Exact User Experience Simulation
Testing the exact Google OAuth connection failure that the user is experiencing.

This test simulates the exact flow:
1. User clicks "Connect Google Workspace" 
2. Frontend calls OAuth URL endpoint
3. User sees "Connection Failed" and "Google services disconnected"
"""

import requests
import json
import time
from datetime import datetime, timezone

# Backend URL from frontend/.env
BACKEND_URL = "https://fidus-invest.emergent.host/api"

def test_oauth_connection_failure():
    """Test the exact OAuth connection failure scenario"""
    print("🚀 OAuth Connection Failure Debug Test")
    print("=" * 60)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Started: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 60)
    
    # Step 1: Authenticate as admin (user credentials)
    print("\n🔐 Step 1: Admin Authentication")
    login_data = {
        "username": "admin",
        "password": "password123",
        "user_type": "admin"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data, timeout=30)
        print(f"Login Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Authentication failed: {response.text}")
            return
            
        data = response.json()
        admin_token = data.get("token")
        print(f"✅ Admin authenticated: {data.get('name')}")
        
    except Exception as e:
        print(f"❌ Authentication error: {str(e)}")
        return
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Step 2: Test the exact OAuth URL endpoint that frontend calls
    print("\n🔍 Step 2: Testing OAuth URL Generation (/api/auth/google/url)")
    try:
        response = requests.get(f"{BACKEND_URL}/auth/google/url", headers=headers, timeout=30)
        print(f"OAuth URL Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            auth_url = data.get("auth_url", "")
            print(f"✅ OAuth URL generated successfully")
            print(f"   URL: {auth_url[:100]}...")
            
            # Verify URL parameters
            required_params = ["client_id=", "redirect_uri=", "scope=", "response_type="]
            missing_params = [param for param in required_params if param not in auth_url]
            
            if not missing_params:
                print("✅ All required OAuth parameters present")
            else:
                print(f"❌ Missing OAuth parameters: {missing_params}")
                
        else:
            print(f"❌ OAuth URL generation failed: {response.text}")
            
    except Exception as e:
        print(f"❌ OAuth URL error: {str(e)}")
    
    # Step 3: Test connection status endpoint (shows "Connection Failed")
    print("\n🔍 Step 3: Testing Connection Status (/api/google/connection/test-all)")
    try:
        response = requests.get(f"{BACKEND_URL}/google/connection/test-all", headers=headers, timeout=30)
        print(f"Connection Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            overall_status = data.get("overall_status", "unknown")
            services = data.get("services", {})
            
            print(f"Overall Status: {overall_status}")
            print("Service Status:")
            
            for service_name, service_data in services.items():
                status = service_data.get("status", "unknown")
                print(f"  {service_name}: {status}")
                
                if status in ["no_auth", "disconnected"]:
                    print(f"    ⚠️  This explains 'Google services disconnected'")
                    
        else:
            print(f"❌ Connection status failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Connection status error: {str(e)}")
    
    # Step 4: Test individual OAuth status
    print("\n🔍 Step 4: Testing Individual OAuth Status")
    try:
        response = requests.get(f"{BACKEND_URL}/admin/google/individual-status", headers=headers, timeout=30)
        print(f"Individual Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            connected = data.get("connected", False)
            google_email = data.get("google_email", "N/A")
            
            print(f"Connected: {connected}")
            print(f"Google Email: {google_email}")
            
            if not connected:
                print("⚠️  This explains 'Connection Failed' status")
                
        else:
            print(f"❌ Individual status failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Individual status error: {str(e)}")
    
    # Step 5: Test Gmail API to check authentication requirement
    print("\n🔍 Step 5: Testing Gmail API Authentication")
    try:
        response = requests.get(f"{BACKEND_URL}/google/gmail/real-messages", headers=headers, timeout=30)
        print(f"Gmail API Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            auth_required = data.get("auth_required", False)
            messages = data.get("messages", [])
            
            if auth_required:
                print("⚠️  Gmail API requires authentication - OAuth not completed")
            elif messages:
                print(f"✅ Gmail API working - {len(messages)} messages retrieved")
            else:
                print("❓ Gmail API response unclear")
                
        else:
            print(f"❌ Gmail API failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Gmail API error: {str(e)}")
    
    # Step 6: Test OAuth callback endpoint accessibility
    print("\n🔍 Step 6: Testing OAuth Callback Endpoint")
    try:
        # Test without parameters (should return error but not 404)
        response = requests.get(f"{BACKEND_URL}/admin/google-callback", timeout=30)
        print(f"OAuth Callback Status: {response.status_code}")
        
        if response.status_code == 404:
            print("❌ OAuth callback endpoint not found - this could block OAuth flow")
        elif response.status_code in [400, 401, 403]:
            print("✅ OAuth callback endpoint exists (returns expected error without params)")
        else:
            print(f"✅ OAuth callback endpoint accessible")
            
    except Exception as e:
        print(f"❌ OAuth callback error: {str(e)}")
    
    # Step 7: Check backend environment configuration
    print("\n🔍 Step 7: Testing Backend Environment")
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=30)
        print(f"Backend Health: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend healthy: {data.get('service', 'N/A')}")
        else:
            print(f"❌ Backend unhealthy: {response.text}")
            
    except Exception as e:
        print(f"❌ Backend health error: {str(e)}")
    
    # Summary and Root Cause Analysis
    print("\n" + "=" * 60)
    print("🎯 ROOT CAUSE ANALYSIS")
    print("=" * 60)
    
    print("\n🔍 FINDINGS:")
    print("1. OAuth URL generation: Testing above")
    print("2. Connection status: Testing above") 
    print("3. Individual OAuth status: Testing above")
    print("4. Gmail API authentication: Testing above")
    print("5. OAuth callback accessibility: Testing above")
    print("6. Backend health: Testing above")
    
    print("\n💡 LIKELY ROOT CAUSES:")
    print("- OAuth flow has never been completed by user")
    print("- OAuth tokens are missing or expired")
    print("- OAuth callback is not processing correctly")
    print("- Frontend is calling wrong OAuth endpoints")
    
    print("\n🔧 RECOMMENDED FIXES:")
    print("1. Complete OAuth flow by visiting the generated OAuth URL")
    print("2. Check OAuth callback processing")
    print("3. Verify frontend is calling correct endpoints")
    print("4. Check for OAuth token storage issues")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_oauth_connection_failure()