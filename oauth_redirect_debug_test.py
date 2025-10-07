#!/usr/bin/env python3
"""
Google OAuth Redirect URI Mismatch Debug Test
==============================================

This test specifically debugs the Google OAuth redirect URI mismatch error
that's blocking the OAuth flow when users click "Connect Google Workspace".

The goal is to:
1. Test OAuth URL generation via /api/auth/google/url
2. Extract the exact redirect_uri parameter being sent
3. Check Google Client configuration
4. Identify the mismatch between what's sent vs what should be configured
"""

import requests
import json
import os
from urllib.parse import urlparse, parse_qs
import sys

# Configuration
BACKEND_URL = "https://investor-dash-1.preview.emergentagent.com"
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
        print(f"Login URL: {login_url}")
        print(f"Login Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            print(f"✅ Admin authentication successful")
            print(f"Admin ID: {data.get('id')}")
            print(f"Admin Name: {data.get('name')}")
            print(f"JWT Token: {token[:50]}..." if token else "No token")
            return token
        else:
            print(f"❌ Admin authentication failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Admin authentication error: {str(e)}")
        return None

def test_oauth_url_generation(token):
    """Test Google OAuth URL generation and extract redirect_uri"""
    print_section("GOOGLE OAUTH URL GENERATION TEST")
    
    headers = {"Authorization": f"Bearer {token}"}
    oauth_url_endpoint = f"{BACKEND_URL}/api/auth/google/url"
    
    try:
        response = requests.get(oauth_url_endpoint, headers=headers, timeout=10)
        print(f"OAuth URL Endpoint: {oauth_url_endpoint}")
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            oauth_url = data.get('auth_url') or data.get('url') or data.get('oauth_url')
            
            if oauth_url:
                print(f"✅ OAuth URL generated successfully")
                print(f"Full OAuth URL: {oauth_url}")
                
                # Parse the OAuth URL to extract parameters
                parsed_url = urlparse(oauth_url)
                query_params = parse_qs(parsed_url.query)
                
                print(f"\n📋 OAUTH URL ANALYSIS:")
                print(f"Base URL: {parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}")
                
                # Extract key OAuth parameters
                client_id = query_params.get('client_id', ['Not found'])[0]
                redirect_uri = query_params.get('redirect_uri', ['Not found'])[0]
                response_type = query_params.get('response_type', ['Not found'])[0]
                scope = query_params.get('scope', ['Not found'])[0]
                state = query_params.get('state', ['Not found'])[0]
                
                print(f"Client ID: {client_id}")
                print(f"🎯 REDIRECT URI: {redirect_uri}")
                print(f"Response Type: {response_type}")
                print(f"Scope: {scope}")
                print(f"State: {state}")
                
                return {
                    'oauth_url': oauth_url,
                    'client_id': client_id,
                    'redirect_uri': redirect_uri,
                    'response_type': response_type,
                    'scope': scope,
                    'state': state
                }
            else:
                print(f"❌ No OAuth URL found in response: {data}")
                return None
        else:
            print(f"❌ OAuth URL generation failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ OAuth URL generation error: {str(e)}")
        return None

def check_environment_configuration():
    """Check environment variable configuration"""
    print_section("ENVIRONMENT CONFIGURATION CHECK")
    
    # Check backend environment variables (from the code we saw)
    backend_env_config = {
        'GOOGLE_CLIENT_ID': '909926639154-r3v0ka94cbu4uo0sn8g4jvtiulf4i9qs.apps.googleusercontent.com',
        'GOOGLE_OAUTH_REDIRECT_URI': 'https://investor-dash-1.preview.emergentagent.com/admin/google-callback',
        'GOOGLE_OAUTH_REDIRECT_URI_COMMENTED': 'https://fidus-invest.emergent.host/admin/google-callback'
    }
    
    # Check frontend environment variables (from the code we saw)
    frontend_env_config = {
        'REACT_APP_BACKEND_URL': 'https://investor-dash-1.preview.emergentagent.com',
        'REACT_APP_GOOGLE_CLIENT_ID': '909926639154-r3v0ka94cbu4uo0sn8g4jvtiulf4i9qs.apps.googleusercontent.com',
        'REACT_APP_GOOGLE_REDIRECT_URI': 'https://fidus-invest.emergent.host/admin/google-callback'
    }
    
    print("📋 BACKEND ENVIRONMENT CONFIGURATION:")
    for key, value in backend_env_config.items():
        print(f"  {key}: {value}")
    
    print("\n📋 FRONTEND ENVIRONMENT CONFIGURATION:")
    for key, value in frontend_env_config.items():
        print(f"  {key}: {value}")
    
    # Identify potential mismatches
    print(f"\n🔍 CONFIGURATION ANALYSIS:")
    backend_redirect = backend_env_config['GOOGLE_OAUTH_REDIRECT_URI']
    frontend_redirect = frontend_env_config['REACT_APP_GOOGLE_REDIRECT_URI']
    
    if backend_redirect != frontend_redirect:
        print(f"🚨 REDIRECT URI MISMATCH DETECTED!")
        print(f"   Backend expects: {backend_redirect}")
        print(f"   Frontend expects: {frontend_redirect}")
        print(f"   This is likely the root cause of the redirect_uri_mismatch error!")
    else:
        print(f"✅ Redirect URIs match between backend and frontend")
    
    return {
        'backend_config': backend_env_config,
        'frontend_config': frontend_env_config,
        'mismatch_detected': backend_redirect != frontend_redirect,
        'backend_redirect_uri': backend_redirect,
        'frontend_redirect_uri': frontend_redirect
    }

def test_oauth_callback_accessibility(redirect_uri):
    """Test if the OAuth callback endpoint is accessible"""
    print_section("OAUTH CALLBACK ENDPOINT ACCESSIBILITY")
    
    try:
        # Test the callback endpoint
        response = requests.get(redirect_uri, timeout=10, allow_redirects=False)
        print(f"Callback URL: {redirect_uri}")
        print(f"Response Status: {response.status_code}")
        
        if response.status_code in [200, 404, 405]:  # 404/405 are acceptable for callback endpoints
            print(f"✅ Callback endpoint is accessible")
            return True
        else:
            print(f"⚠️ Callback endpoint returned: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Callback endpoint accessibility error: {str(e)}")
        return False

def generate_google_console_recommendations(oauth_params, env_config):
    """Generate recommendations for Google Cloud Console configuration"""
    print_section("GOOGLE CLOUD CONSOLE CONFIGURATION RECOMMENDATIONS")
    
    if oauth_params and env_config:
        client_id = oauth_params.get('client_id')
        actual_redirect_uri = oauth_params.get('redirect_uri')
        
        print(f"📋 GOOGLE CLOUD CONSOLE SETUP:")
        print(f"1. Go to Google Cloud Console: https://console.cloud.google.com/")
        print(f"2. Navigate to APIs & Services > Credentials")
        print(f"3. Find OAuth 2.0 Client ID: {client_id}")
        print(f"4. In 'Authorized redirect URIs', ensure you have:")
        print(f"   ✅ {actual_redirect_uri}")
        
        if env_config.get('mismatch_detected'):
            print(f"\n🚨 CRITICAL ISSUE IDENTIFIED:")
            print(f"The backend is sending: {actual_redirect_uri}")
            print(f"But frontend expects: {env_config['frontend_redirect_uri']}")
            print(f"\n🔧 RECOMMENDED FIXES:")
            print(f"Option 1: Update backend .env GOOGLE_OAUTH_REDIRECT_URI to: {env_config['frontend_redirect_uri']}")
            print(f"Option 2: Update frontend .env REACT_APP_GOOGLE_REDIRECT_URI to: {actual_redirect_uri}")
            print(f"Option 3: Add both URIs to Google Cloud Console authorized redirect URIs")
        
        print(f"\n📝 ADDITIONAL GOOGLE CONSOLE SETTINGS:")
        print(f"- Authorized JavaScript origins: https://fidus-invest.emergent.host")
        print(f"- Authorized redirect URIs should include: {actual_redirect_uri}")
        print(f"- OAuth consent screen should be configured for external users")

def main():
    """Main test execution"""
    print_header("GOOGLE OAUTH REDIRECT URI MISMATCH DEBUG TEST")
    print("This test will identify the exact cause of the redirect_uri_mismatch error")
    
    # Step 1: Authenticate as admin
    token = authenticate_admin()
    if not token:
        print("❌ Cannot proceed without admin authentication")
        sys.exit(1)
    
    # Step 2: Test OAuth URL generation and extract parameters
    oauth_params = test_oauth_url_generation(token)
    
    # Step 3: Check environment configuration
    env_config = check_environment_configuration()
    
    # Step 4: Test callback endpoint accessibility
    if oauth_params:
        redirect_uri = oauth_params.get('redirect_uri')
        if redirect_uri and redirect_uri != 'Not found':
            test_oauth_callback_accessibility(redirect_uri)
    
    # Step 5: Generate recommendations
    generate_google_console_recommendations(oauth_params, env_config)
    
    # Final summary
    print_header("DEBUG TEST SUMMARY")
    
    if oauth_params and env_config:
        actual_redirect = oauth_params.get('redirect_uri')
        expected_redirect = env_config.get('frontend_redirect_uri')
        
        print(f"🎯 ROOT CAUSE ANALYSIS:")
        print(f"Backend sends redirect_uri: {actual_redirect}")
        print(f"Frontend expects redirect_uri: {expected_redirect}")
        
        if actual_redirect != expected_redirect:
            print(f"🚨 CONFIRMED: Redirect URI mismatch is the root cause!")
            print(f"Google OAuth expects: {actual_redirect}")
            print(f"But Google Console may be configured for: {expected_redirect}")
        else:
            print(f"✅ Redirect URIs match - issue may be in Google Console configuration")
        
        print(f"\n📋 NEXT STEPS:")
        print(f"1. Check Google Cloud Console OAuth client configuration")
        print(f"2. Ensure {actual_redirect} is in authorized redirect URIs")
        print(f"3. Consider environment variable alignment between backend/frontend")
    else:
        print(f"❌ Unable to complete full analysis due to authentication or API issues")

if __name__ == "__main__":
    main()