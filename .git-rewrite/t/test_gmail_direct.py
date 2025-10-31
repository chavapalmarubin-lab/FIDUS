#!/usr/bin/env python3

import requests
import json

def test_gmail_endpoints_direct():
    """Test Gmail endpoints directly using localhost"""
    base_url = "http://localhost:8001"  # Direct backend access
    
    print("🚀 Testing Gmail OAuth Endpoints Directly...")
    print("=" * 50)
    
    # Test 1: Gmail Auth URL
    print("\n1. Testing Gmail Auth URL...")
    try:
        response = requests.get(f"{base_url}/api/gmail/auth-url", timeout=10)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Gmail Auth URL endpoint working!")
            print(f"   Success: {data.get('success')}")
            
            auth_url = data.get('authorization_url', '')
            if '909926639154-cjtnt3urluctt1q90gri3rtj37vbim6h.apps.googleusercontent.com' in auth_url:
                print("   ✅ Correct client ID found in OAuth URL")
            else:
                print("   ❌ Client ID not found in OAuth URL")
                
            print(f"   State: {data.get('state', 'N/A')}")
            print(f"   Instructions: {data.get('instructions', 'N/A')}")
            
        else:
            print(f"   ❌ Failed with status {response.status_code}")
            try:
                error = response.json()
                print(f"   Error: {error}")
            except:
                print(f"   Error text: {response.text}")
                
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
    
    # Test 2: Gmail Authentication
    print("\n2. Testing Gmail Authentication...")
    try:
        response = requests.post(f"{base_url}/api/gmail/authenticate", timeout=10)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Gmail Authentication endpoint working!")
            print(f"   Success: {data.get('success')}")
            print(f"   Message: {data.get('message')}")
            print(f"   Action: {data.get('action', 'N/A')}")
            
            if data.get('action') == 'redirect_to_oauth':
                print("   ✅ Properly detects missing credentials and provides OAuth flow")
            
        else:
            print(f"   ❌ Failed with status {response.status_code}")
            try:
                error = response.json()
                print(f"   Error: {error}")
            except:
                print(f"   Error text: {response.text}")
                
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
    
    # Test 3: Gmail OAuth Callback (structure test)
    print("\n3. Testing Gmail OAuth Callback Structure...")
    try:
        # Test with missing parameters
        response = requests.get(f"{base_url}/api/gmail/oauth-callback", timeout=10)
        print(f"   Status Code (missing params): {response.status_code}")
        
        if response.status_code in [400, 422]:
            print("   ✅ Missing parameters properly rejected")
        else:
            print("   ⚠️  Missing parameters handling may need improvement")
        
        # Test with invalid state
        response = requests.get(f"{base_url}/api/gmail/oauth-callback?code=test&state=invalid", timeout=10)
        print(f"   Status Code (invalid state): {response.status_code}")
        
        if response.status_code == 400:
            print("   ✅ Invalid state properly rejected")
        else:
            print("   ⚠️  Invalid state handling may need improvement")
            
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
    
    print("\n" + "=" * 50)
    print("Gmail OAuth endpoint testing completed!")

if __name__ == "__main__":
    test_gmail_endpoints_direct()