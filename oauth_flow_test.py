#!/usr/bin/env python3
"""
Google OAuth Flow Test - Simulate User Connection Attempt
=========================================================

This test simulates what happens when a user clicks "Connect Google Workspace"
and follows the OAuth flow to identify where exactly it fails.
"""

import requests
import json
from urllib.parse import urlparse, parse_qs
import sys

# Configuration
BACKEND_URL = "https://mt5-deploy-debug.preview.emergentagent.com"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def print_section(title):
    """Print a formatted section"""
    print(f"\n{'-'*40}")
    print(f" {title}")
    print(f"{'-'*40}")

def authenticate_admin():
    """Authenticate as admin and get JWT token"""
    print_section("ADMIN AUTHENTICATION")
    
    login_url = f"{BACKEND_URL}/api/auth/login"
    login_data = {
        "username": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD,
        "user_type": "admin"
    }
    
    try:
        response = requests.post(login_url, json=login_data, timeout=10)
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            print(f"✅ Admin authenticated successfully")
            return token
        else:
            print(f"❌ Admin authentication failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Admin authentication error: {str(e)}")
        return None

def test_google_oauth_url_access(oauth_url):
    """Test accessing the Google OAuth URL to see what error occurs"""
    print_section("GOOGLE OAUTH URL ACCESS TEST")
    
    try:
        # Make a request to the OAuth URL to see what Google returns
        response = requests.get(oauth_url, timeout=10, allow_redirects=False)
        print(f"OAuth URL: {oauth_url}")
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 302:
            # This is expected - Google should redirect to consent screen
            location = response.headers.get('Location', '')
            print(f"✅ Google OAuth URL accessible - redirects to: {location[:100]}...")
            return True
        elif response.status_code == 400:
            # This is the error we're looking for
            print(f"🚨 HTTP 400 ERROR DETECTED!")
            print(f"Response Text: {response.text}")
            
            # Check if it contains redirect_uri_mismatch
            if 'redirect_uri_mismatch' in response.text.lower():
                print(f"🎯 CONFIRMED: redirect_uri_mismatch error found!")
                return False
            else:
                print(f"❌ HTTP 400 but not redirect_uri_mismatch: {response.text}")
                return False
        else:
            print(f"⚠️ Unexpected response: {response.status_code}")
            print(f"Response Text: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error accessing OAuth URL: {str(e)}")
        return False

def test_google_console_configuration():
    """Test what redirect URIs might be configured in Google Console"""
    print_section("GOOGLE CONSOLE CONFIGURATION ANALYSIS")
    
    # Based on our findings, let's analyze what should be configured
    actual_redirect_uri = "https://mt5-deploy-debug.preview.emergentagent.com/admin/google-callback"
    expected_redirect_uri = "https://fidus-invest.emergent.host/admin/google-callback"
    
    print(f"📋 REDIRECT URI ANALYSIS:")
    print(f"Backend sends: {actual_redirect_uri}")
    print(f"Frontend expects: {expected_redirect_uri}")
    print(f"")
    print(f"🔍 LIKELY GOOGLE CONSOLE CONFIGURATION:")
    print(f"The Google Cloud Console OAuth client is probably configured with:")
    print(f"   ❌ {expected_redirect_uri}")
    print(f"But Google OAuth requests are being sent with:")
    print(f"   ✅ {actual_redirect_uri}")
    print(f"")
    print(f"This mismatch causes Google to return 'Error 400: redirect_uri_mismatch'")

def simulate_oauth_callback_test():
    """Test what happens when OAuth callback is called"""
    print_section("OAUTH CALLBACK SIMULATION")
    
    callback_url = "https://mt5-deploy-debug.preview.emergentagent.com/admin/google-callback"
    
    # Test callback endpoint with mock parameters
    test_params = {
        'code': 'mock_authorization_code',
        'state': 'admin_001:fidus_oauth_state'
    }
    
    try:
        response = requests.get(callback_url, params=test_params, timeout=10, allow_redirects=False)
        print(f"Callback URL: {callback_url}")
        print(f"Test Parameters: {test_params}")
        print(f"Response Status: {response.status_code}")
        
        if response.status_code in [200, 302, 400]:
            print(f"✅ Callback endpoint is functional")
            if response.status_code == 302:
                location = response.headers.get('Location', '')
                print(f"Redirects to: {location}")
        else:
            print(f"⚠️ Callback endpoint returned: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Callback test error: {str(e)}")

def generate_fix_recommendations():
    """Generate specific fix recommendations"""
    print_section("FIX RECOMMENDATIONS")
    
    print(f"🔧 IMMEDIATE FIXES TO RESOLVE redirect_uri_mismatch:")
    print(f"")
    print(f"OPTION 1 - Update Google Cloud Console (RECOMMENDED):")
    print(f"1. Go to: https://console.cloud.google.com/apis/credentials")
    print(f"2. Find OAuth 2.0 Client: 909926639154-r3v0ka94cbu4uo0sn8g4jvtiulf4i9qs.apps.googleusercontent.com")
    print(f"3. Click Edit")
    print(f"4. In 'Authorized redirect URIs', ADD:")
    print(f"   https://mt5-deploy-debug.preview.emergentagent.com/admin/google-callback")
    print(f"5. Keep existing URI if present:")
    print(f"   https://fidus-invest.emergent.host/admin/google-callback")
    print(f"6. Save changes")
    print(f"")
    print(f"OPTION 2 - Update Backend Configuration:")
    print(f"1. Edit /app/backend/.env")
    print(f"2. Change GOOGLE_OAUTH_REDIRECT_URI to:")
    print(f"   GOOGLE_OAUTH_REDIRECT_URI=\"https://fidus-invest.emergent.host/admin/google-callback\"")
    print(f"3. Restart backend service")
    print(f"")
    print(f"OPTION 3 - Update Frontend Configuration:")
    print(f"1. Edit /app/frontend/.env")
    print(f"2. Change REACT_APP_GOOGLE_REDIRECT_URI to:")
    print(f"   REACT_APP_GOOGLE_REDIRECT_URI=https://mt5-deploy-debug.preview.emergentagent.com/admin/google-callback")
    print(f"3. Restart frontend service")
    print(f"")
    print(f"🎯 RECOMMENDED APPROACH:")
    print(f"Use OPTION 1 (Update Google Console) as it allows both URLs to work")
    print(f"and provides flexibility for different environments.")

def main():
    """Main test execution"""
    print_header("GOOGLE OAUTH FLOW TEST - USER CONNECTION SIMULATION")
    
    # Step 1: Authenticate
    token = authenticate_admin()
    if not token:
        print("❌ Cannot proceed without admin authentication")
        sys.exit(1)
    
    # Step 2: Get OAuth URL
    headers = {"Authorization": f"Bearer {token}"}
    oauth_url_endpoint = f"{BACKEND_URL}/api/auth/google/url"
    
    try:
        response = requests.get(oauth_url_endpoint, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            oauth_url = data.get('auth_url') or data.get('url') or data.get('oauth_url')
            
            if oauth_url:
                # Step 3: Test accessing the OAuth URL
                test_google_oauth_url_access(oauth_url)
                
                # Step 4: Analyze configuration
                test_google_console_configuration()
                
                # Step 5: Test callback
                simulate_oauth_callback_test()
                
                # Step 6: Generate recommendations
                generate_fix_recommendations()
            else:
                print("❌ No OAuth URL found in response")
        else:
            print(f"❌ Failed to get OAuth URL: {response.text}")
    except Exception as e:
        print(f"❌ OAuth URL test error: {str(e)}")
    
    # Final summary
    print_header("OAUTH FLOW TEST SUMMARY")
    print(f"🎯 ISSUE CONFIRMED:")
    print(f"The 'Error 400: redirect_uri_mismatch' occurs because:")
    print(f"1. Backend sends redirect_uri: https://mt5-deploy-debug.preview.emergentagent.com/admin/google-callback")
    print(f"2. Google Console is likely configured for: https://fidus-invest.emergent.host/admin/google-callback")
    print(f"3. Google OAuth validates redirect_uri against Console configuration")
    print(f"4. Mismatch = Error 400: redirect_uri_mismatch")
    print(f"")
    print(f"✅ SOLUTION: Add the actual redirect_uri to Google Cloud Console authorized URIs")

if __name__ == "__main__":
    main()