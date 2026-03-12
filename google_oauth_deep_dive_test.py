#!/usr/bin/env python3
"""
Google OAuth Flow Deep Dive Testing
Testing the specific OAuth flow issues identified in the live system
"""

import requests
import json
from urllib.parse import urlparse, parse_qs
import re

def test_google_oauth_flow():
    """Test the complete Google OAuth flow"""
    print("🔍 DEEP DIVE: Google OAuth Flow Testing")
    print("="*60)
    
    # Test both backend URLs
    backend_urls = [
        "https://fidus-trading.preview.emergentagent.com/api",
        "https://fidus-invest.emergent.host/api"
    ]
    
    for backend_url in backend_urls:
        print(f"\n🌐 Testing Backend: {backend_url}")
        print("-" * 50)
        
        # Authenticate first
        try:
            login_data = {
                "username": "admin",
                "password": "password123", 
                "user_type": "admin"
            }
            
            response = requests.post(f"{backend_url}/auth/login", json=login_data, timeout=10)
            
            if response.status_code != 200:
                print(f"❌ Authentication failed: {response.status_code}")
                continue
                
            token = response.json().get('token')
            headers = {"Authorization": f"Bearer {token}"}
            
            print(f"✅ Authenticated successfully")
            
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            continue
        
        # Test Direct Google OAuth URL
        try:
            response = requests.get(f"{backend_url}/auth/google/url", headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                auth_url = data.get('auth_url', '')
                
                print(f"✅ Direct OAuth URL: {auth_url[:100]}...")
                
                # Parse the OAuth URL
                parsed_url = urlparse(auth_url)
                query_params = parse_qs(parsed_url.query)
                
                print(f"   Client ID: {query_params.get('client_id', ['N/A'])[0]}")
                print(f"   Redirect URI: {query_params.get('redirect_uri', ['N/A'])[0]}")
                print(f"   Response Type: {query_params.get('response_type', ['N/A'])[0]}")
                print(f"   Scope: {query_params.get('scope', ['N/A'])[0]}")
                
                # Check if this is a valid Google OAuth URL
                if 'accounts.google.com/o/oauth2/auth' in auth_url:
                    print(f"✅ Valid Google OAuth URL structure")
                else:
                    print(f"❌ Invalid Google OAuth URL structure")
                    
            else:
                print(f"❌ Direct OAuth URL failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Direct OAuth URL error: {str(e)}")
        
        # Test Emergent OAuth URL
        try:
            response = requests.get(f"{backend_url}/admin/google/auth-url", headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                auth_url = data.get('auth_url', '')
                
                print(f"✅ Emergent OAuth URL: {auth_url}")
                
                # Check if this is pointing to Emergent OAuth service
                if 'auth.emergentagent.com' in auth_url:
                    print(f"✅ Using Emergent OAuth service")
                    
                    # Check if the redirect parameter is properly encoded
                    if 'redirect=' in auth_url:
                        redirect_param = auth_url.split('redirect=')[1]
                        print(f"   Redirect parameter: {redirect_param[:100]}...")
                        
                        # Check if session_id placeholder is present
                        if '{session_id}' in redirect_param:
                            print(f"❌ Session ID placeholder not replaced!")
                        else:
                            print(f"✅ Session ID properly handled")
                    else:
                        print(f"❌ No redirect parameter found")
                else:
                    print(f"❌ Not using Emergent OAuth service")
                    
            else:
                print(f"❌ Emergent OAuth URL failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Emergent OAuth URL error: {str(e)}")
        
        # Test Google Profile endpoint (to check if OAuth tokens exist)
        try:
            response = requests.get(f"{backend_url}/admin/google/profile", headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ Google Profile accessible - OAuth tokens exist")
                    print(f"   Profile: {data.get('profile', {}).get('name', 'N/A')}")
                else:
                    print(f"❌ Google Profile not accessible: {data.get('error', 'Unknown error')}")
            else:
                print(f"❌ Google Profile endpoint failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Google Profile error: {str(e)}")

def test_google_console_configuration():
    """Test Google Console configuration by making a test OAuth request"""
    print("\n🔍 TESTING GOOGLE CONSOLE CONFIGURATION")
    print("="*60)
    
    # Extract OAuth configuration from backend
    try:
        with open('/app/backend/.env', 'r') as f:
            env_content = f.read()
        
        client_id = None
        client_secret = None
        redirect_uri = None
        
        for line in env_content.split('\n'):
            if line.startswith('GOOGLE_CLIENT_ID='):
                client_id = line.split('=', 1)[1].strip('"')
            elif line.startswith('GOOGLE_CLIENT_SECRET='):
                client_secret = line.split('=', 1)[1].strip('"')
            elif line.startswith('GOOGLE_OAUTH_REDIRECT_URI='):
                redirect_uri = line.split('=', 1)[1].strip('"')
        
        print(f"Client ID: {client_id}")
        print(f"Client Secret: {'*' * 20 if client_secret else 'Not found'}")
        print(f"Redirect URI: {redirect_uri}")
        
        if not all([client_id, client_secret, redirect_uri]):
            print("❌ Missing OAuth configuration in backend .env")
            return
        
        # Test OAuth URL construction
        oauth_url = f"https://accounts.google.com/o/oauth2/auth?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope=openid%20email%20profile%20https://www.googleapis.com/auth/gmail.readonly%20https://www.googleapis.com/auth/calendar.readonly%20https://www.googleapis.com/auth/drive.readonly"
        
        print(f"\n✅ Constructed OAuth URL:")
        print(f"   {oauth_url[:100]}...")
        
        # Test if the OAuth URL is accessible (should return HTML page, not error)
        try:
            response = requests.get(oauth_url, timeout=10, allow_redirects=False)
            
            if response.status_code in [200, 302]:
                print(f"✅ Google OAuth URL accessible (Status: {response.status_code})")
                
                if response.status_code == 302:
                    location = response.headers.get('Location', '')
                    if 'error=' in location:
                        error_match = re.search(r'error=([^&]+)', location)
                        if error_match:
                            error = error_match.group(1)
                            print(f"❌ OAuth Error: {error}")
                            
                            if error == 'redirect_uri_mismatch':
                                print(f"🚨 CRITICAL: redirect_uri_mismatch error!")
                                print(f"   The redirect URI '{redirect_uri}' is not configured in Google Console")
                                print(f"   Go to Google Console > APIs & Services > Credentials")
                                print(f"   Add '{redirect_uri}' to Authorized redirect URIs")
                            elif error == 'invalid_client':
                                print(f"🚨 CRITICAL: invalid_client error!")
                                print(f"   The client ID '{client_id}' is invalid or not found")
                                print(f"   Check Google Console OAuth 2.0 Client IDs configuration")
                        else:
                            print(f"❌ OAuth redirect with unknown error")
                    else:
                        print(f"✅ OAuth redirect successful (likely to consent screen)")
                else:
                    # Check if response contains Google OAuth consent screen
                    if 'accounts.google.com' in response.text and 'oauth' in response.text.lower():
                        print(f"✅ Google OAuth consent screen accessible")
                    else:
                        print(f"❌ Unexpected response from Google OAuth URL")
            else:
                print(f"❌ Google OAuth URL not accessible: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error testing Google OAuth URL: {str(e)}")
            
    except Exception as e:
        print(f"❌ Error reading backend configuration: {str(e)}")

def test_oauth_callback_endpoint():
    """Test OAuth callback endpoint"""
    print("\n🔍 TESTING OAUTH CALLBACK ENDPOINT")
    print("="*60)
    
    backend_urls = [
        "https://fidus-trading.preview.emergentagent.com/api",
        "https://fidus-invest.emergent.host/api"
    ]
    
    for backend_url in backend_urls:
        print(f"\n🌐 Testing Backend: {backend_url}")
        print("-" * 30)
        
        # Test if callback endpoint exists
        try:
            # Test with a dummy code (should return error but endpoint should exist)
            callback_url = f"{backend_url}/admin/google-callback?code=dummy_code&state=dummy_state"
            response = requests.get(callback_url, timeout=10, allow_redirects=False)
            
            if response.status_code in [200, 302, 400, 401]:
                print(f"✅ OAuth callback endpoint exists (Status: {response.status_code})")
                
                if response.status_code == 302:
                    location = response.headers.get('Location', '')
                    print(f"   Redirects to: {location}")
                elif response.status_code == 400:
                    print(f"   Returns 400 for invalid code (expected behavior)")
                    
            else:
                print(f"❌ OAuth callback endpoint issue: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error testing callback endpoint: {str(e)}")

if __name__ == "__main__":
    test_google_oauth_flow()
    test_google_console_configuration()
    test_oauth_callback_endpoint()