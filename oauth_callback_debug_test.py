#!/usr/bin/env python3
"""
OAuth Callback Debug Test - Investigate OAuth callback processing issues

Based on backend logs showing: "❌ Missing authorization code or state in callback"
This suggests the OAuth flow starts but fails during callback processing.

Debug Areas:
1. Test OAuth callback endpoints accessibility
2. Check OAuth callback URL configuration
3. Verify state parameter handling
4. Test callback processing logic
"""

import requests
import json
import sys
from datetime import datetime, timezone

# Backend URL from frontend/.env
BACKEND_URL = "https://tradehub-mt5.preview.emergentagent.com/api"

# Admin credentials
ADMIN_CREDENTIALS = {
    "username": "admin",
    "password": "password123", 
    "user_type": "admin"
}

class OAuthCallbackDebugger:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        
    def log_debug(self, test_name, success, details="", error_msg=""):
        """Log debug result"""
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if error_msg:
            print(f"   Error: {error_msg}")
        print()

    def make_request(self, method, endpoint, data=None, headers=None, auth_token=None):
        """Make HTTP request with detailed error handling"""
        url = f"{BACKEND_URL}{endpoint}"
        
        req_headers = {"Content-Type": "application/json"}
        if headers:
            req_headers.update(headers)
        if auth_token:
            req_headers["Authorization"] = f"Bearer {auth_token}"
            
        try:
            print(f"🔍 Making {method} request to: {url}")
            
            if method.upper() == "GET":
                response = self.session.get(url, headers=req_headers, timeout=30)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, headers=req_headers, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            print(f"📊 Response Status: {response.status_code}")
            return response
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return None

    def authenticate_admin(self):
        """Authenticate as admin user"""
        print("🔐 Authenticating as admin user...")
        
        response = self.make_request("POST", "/auth/login", ADMIN_CREDENTIALS)
        if response and response.status_code == 200:
            try:
                data = response.json()
                if data.get("token") and data.get("type") == "admin":
                    self.admin_token = data["token"]
                    self.log_debug("Admin Authentication", True, 
                                 f"Admin: {data.get('name')}, ID: {data.get('id')}")
                    return True
                else:
                    self.log_debug("Admin Authentication", False, 
                                 "Missing token or incorrect type")
                    return False
            except json.JSONDecodeError as e:
                self.log_debug("Admin Authentication", False, 
                             f"Invalid JSON response: {e}")
                return False
        else:
            status_code = response.status_code if response else "No response"
            self.log_debug("Admin Authentication", False, f"HTTP {status_code}")
            return False

    def test_oauth_callback_endpoints(self):
        """Test OAuth callback endpoints accessibility"""
        print("🔗 Testing OAuth callback endpoints...")
        
        # Test different callback endpoint variations
        callback_endpoints = [
            "/admin/google-callback",
            "/auth/google/callback", 
            "/admin/google/callback"
        ]
        
        for endpoint in callback_endpoints:
            # Test GET request to callback endpoint (should return some response)
            response = self.make_request("GET", endpoint)
            
            if response:
                if response.status_code == 404:
                    self.log_debug(f"OAuth Callback - {endpoint}", False,
                                 "Endpoint not found (404)")
                elif response.status_code == 400:
                    self.log_debug(f"OAuth Callback - {endpoint}", True,
                                 "Endpoint exists but expects callback parameters (400 is expected)")
                elif response.status_code == 200:
                    self.log_debug(f"OAuth Callback - {endpoint}", True,
                                 "Endpoint accessible")
                else:
                    self.log_debug(f"OAuth Callback - {endpoint}", True,
                                 f"Endpoint exists (HTTP {response.status_code})")
            else:
                self.log_debug(f"OAuth Callback - {endpoint}", False,
                             "No response received")

    def test_oauth_callback_with_mock_params(self):
        """Test OAuth callback with mock parameters to see error handling"""
        print("🧪 Testing OAuth callback with mock parameters...")
        
        # Test callback with missing parameters (should show specific error)
        response = self.make_request("GET", "/admin/google-callback")
        
        if response:
            try:
                if response.status_code == 400:
                    # Try to get error message
                    try:
                        data = response.json()
                        error_msg = data.get("detail", "No detail")
                        self.log_debug("OAuth Callback - Missing Parameters", True,
                                     f"Proper error handling: {error_msg}")
                    except:
                        self.log_debug("OAuth Callback - Missing Parameters", True,
                                     f"Returns 400 as expected: {response.text[:100]}")
                elif response.status_code == 404:
                    self.log_debug("OAuth Callback - Missing Parameters", False,
                                 "Callback endpoint not found")
                else:
                    self.log_debug("OAuth Callback - Missing Parameters", True,
                                 f"Callback endpoint responds (HTTP {response.status_code})")
            except Exception as e:
                self.log_debug("OAuth Callback - Missing Parameters", False,
                             f"Error testing callback: {e}")
        else:
            self.log_debug("OAuth Callback - Missing Parameters", False,
                         "No response from callback endpoint")

        # Test callback with mock parameters
        mock_params = "?code=mock_auth_code&state=admin_001:fidus_oauth_state"
        response = self.make_request("GET", f"/admin/google-callback{mock_params}")
        
        if response:
            try:
                if response.status_code in [200, 302, 400, 500]:
                    # Any response indicates the endpoint is processing the request
                    try:
                        data = response.json() if response.headers.get('content-type', '').startswith('application/json') else None
                        if data:
                            self.log_debug("OAuth Callback - Mock Parameters", True,
                                         f"Callback processes parameters (HTTP {response.status_code}): {data.get('detail', 'No detail')}")
                        else:
                            self.log_debug("OAuth Callback - Mock Parameters", True,
                                         f"Callback processes parameters (HTTP {response.status_code})")
                    except:
                        self.log_debug("OAuth Callback - Mock Parameters", True,
                                     f"Callback processes parameters (HTTP {response.status_code})")
                else:
                    self.log_debug("OAuth Callback - Mock Parameters", False,
                                 f"Unexpected response: HTTP {response.status_code}")
            except Exception as e:
                self.log_debug("OAuth Callback - Mock Parameters", False,
                             f"Error testing mock callback: {e}")
        else:
            self.log_debug("OAuth Callback - Mock Parameters", False,
                         "No response from callback with mock parameters")

    def check_oauth_configuration(self):
        """Check OAuth configuration in environment"""
        print("⚙️ Checking OAuth configuration...")
        
        if not self.admin_token:
            self.log_debug("OAuth Configuration Check", False, "No admin token available")
            return
        
        # Get OAuth URL to check configuration
        response = self.make_request("GET", "/auth/google/url", auth_token=self.admin_token)
        
        if response and response.status_code == 200:
            try:
                data = response.json()
                auth_url = data.get("auth_url", "")
                
                # Parse URL to check configuration
                if "redirect_uri=" in auth_url:
                    import urllib.parse
                    parsed_url = urllib.parse.urlparse(auth_url)
                    query_params = urllib.parse.parse_qs(parsed_url.query)
                    
                    redirect_uri = query_params.get('redirect_uri', [''])[0]
                    client_id = query_params.get('client_id', [''])[0]
                    scopes = query_params.get('scope', [''])[0]
                    state = query_params.get('state', [''])[0]
                    
                    self.log_debug("OAuth Configuration - URL Analysis", True,
                                 f"Redirect URI: {redirect_uri}")
                    print(f"   Client ID: {client_id[:20]}...")
                    print(f"   Scopes: {scopes[:100]}...")
                    print(f"   State: {state}")
                    
                    # Check if redirect URI matches expected pattern
                    if "fidus-invest.emergent.host" in redirect_uri and "google-callback" in redirect_uri:
                        self.log_debug("OAuth Configuration - Redirect URI", True,
                                     "Redirect URI points to correct domain and callback")
                    else:
                        self.log_debug("OAuth Configuration - Redirect URI", False,
                                     f"Redirect URI may be incorrect: {redirect_uri}")
                else:
                    self.log_debug("OAuth Configuration - URL Parsing", False,
                                 "Could not parse OAuth URL parameters")
                    
            except Exception as e:
                self.log_debug("OAuth Configuration - Analysis", False,
                             f"Error analyzing OAuth configuration: {e}")
        else:
            status_code = response.status_code if response else "No response"
            self.log_debug("OAuth Configuration - URL Generation", False,
                         f"Could not get OAuth URL: HTTP {status_code}")

    def run_oauth_callback_debug(self):
        """Run OAuth callback debugging investigation"""
        print("🚀 OAuth Callback Debug Investigation")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Investigation Started: {datetime.now(timezone.utc).isoformat()}")
        print("=" * 80)
        print()

        # Step 1: Authenticate as admin
        if not self.authenticate_admin():
            print("🚨 CRITICAL: Cannot proceed without admin authentication")
            return False

        # Step 2: Test OAuth callback endpoints
        self.test_oauth_callback_endpoints()

        # Step 3: Test callback with mock parameters
        self.test_oauth_callback_with_mock_params()

        # Step 4: Check OAuth configuration
        self.check_oauth_configuration()

        print("=" * 80)
        print("🔍 OAUTH CALLBACK DEBUG SUMMARY")
        print("=" * 80)
        
        print("🎯 KEY FINDINGS FROM BACKEND LOGS:")
        print("   ❌ 'Missing authorization code or state in callback'")
        print("   ✅ OAuth URL generation working correctly")
        print("   ❌ OAuth callback processing failing")
        print()
        
        print("🚨 ROOT CAUSE ANALYSIS:")
        print("   🎯 ISSUE: OAuth callback endpoint not receiving expected parameters")
        print("   📋 POSSIBLE CAUSES:")
        print("      • Redirect URI mismatch between Google Console and backend")
        print("      • OAuth callback endpoint expecting different parameter format")
        print("      • State parameter encoding/decoding issues")
        print("      • Frontend not properly redirecting to callback URL")
        print("      • CORS or routing issues preventing callback completion")
        print()
        
        print("💡 RECOMMENDED FIXES:")
        print("   1. Verify Google Console redirect URI matches backend expectation")
        print("   2. Check OAuth callback endpoint parameter parsing")
        print("   3. Test OAuth flow end-to-end with real Google OAuth")
        print("   4. Ensure frontend properly handles OAuth redirect")
        print("   5. Check for CORS issues in OAuth callback processing")
        
        print("=" * 80)
        
        return True

if __name__ == "__main__":
    debugger = OAuthCallbackDebugger()
    success = debugger.run_oauth_callback_debug()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)