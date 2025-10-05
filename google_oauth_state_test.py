#!/usr/bin/env python3
"""
Google OAuth State Parameter Fix Testing
Testing the specific fix where state parameter now includes admin_user_id format: {admin_user_id}:fidus_oauth_state

Test Focus:
1. Admin authentication (admin/password123)
2. Test /api/auth/google/url endpoint with admin authentication
3. Verify OAuth URL contains correct state parameter with user ID
4. Test OAuth callback processing readiness
5. Check backend logs for OAuth-related errors

Context: The fix ensures state parameter includes admin user ID for proper callback processing
"""

import requests
import json
import time
import sys
import re
from datetime import datetime, timezone
from urllib.parse import urlparse, parse_qs

# Backend URL Configuration
BACKEND_URL = "https://fidus-finance-api.preview.emergentagent.com/api"

class GoogleOAuthStateTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.admin_user_id = None
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_test(self, test_name, success, details="", error_msg=""):
        """Log test result"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
            
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "error": error_msg,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if error_msg:
            print(f"   Error: {error_msg}")
        print()

    def make_request(self, method, endpoint, data=None, headers=None, auth_token=None):
        """Make HTTP request with proper error handling"""
        url = f"{BACKEND_URL}{endpoint}"
        
        # Set up headers
        req_headers = {"Content-Type": "application/json"}
        if headers:
            req_headers.update(headers)
        if auth_token:
            req_headers["Authorization"] = f"Bearer {auth_token}"
            
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=req_headers, timeout=30)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, headers=req_headers, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None

    def test_admin_authentication(self):
        """Test admin authentication and extract user ID"""
        print("🔍 Testing Admin Authentication...")
        
        login_payload = {
            "username": "admin",
            "password": "password123",
            "user_type": "admin"
        }
        
        response = self.make_request("POST", "/auth/login", login_payload)
        if response and response.status_code == 200:
            try:
                data = response.json()
                if data.get("token") and data.get("type") == "admin":
                    self.admin_token = data["token"]
                    self.admin_user_id = data.get("id")  # Extract admin user ID
                    self.log_test("Admin Authentication", True, 
                                f"Admin: {data.get('name')}, ID: {self.admin_user_id}, Type: {data.get('type')}")
                    return True
                else:
                    self.log_test("Admin Authentication", False, "Missing token or incorrect type")
                    return False
            except json.JSONDecodeError:
                self.log_test("Admin Authentication", False, "Invalid JSON response")
                return False
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("Admin Authentication", False, f"HTTP {status_code}")
            return False

    def test_google_oauth_url_generation(self):
        """Test Google OAuth URL generation with admin authentication"""
        print("🔍 Testing Google OAuth URL Generation...")
        
        if not self.admin_token:
            self.log_test("Google OAuth URL Generation", False, "No admin token available")
            return False

        response = self.make_request("GET", "/auth/google/url", auth_token=self.admin_token)
        if response and response.status_code == 200:
            try:
                data = response.json()
                auth_url = data.get("auth_url")
                
                if auth_url and "accounts.google.com" in auth_url:
                    self.log_test("Google OAuth URL Generation", True, 
                                f"Valid Google OAuth URL generated: {auth_url[:100]}...")
                    return auth_url
                else:
                    self.log_test("Google OAuth URL Generation", False, 
                                "Invalid or missing OAuth URL")
                    return False
            except json.JSONDecodeError:
                self.log_test("Google OAuth URL Generation", False, "Invalid JSON response")
                return False
        else:
            status_code = response.status_code if response else "No response"
            error_msg = ""
            if response:
                try:
                    error_data = response.json()
                    error_msg = error_data.get("detail", "")
                except:
                    error_msg = response.text[:200] if response.text else ""
            
            self.log_test("Google OAuth URL Generation", False, 
                        f"HTTP {status_code}: {error_msg}")
            return False

    def test_oauth_state_parameter(self, auth_url):
        """Test that OAuth URL contains correct state parameter with admin user ID"""
        print("🔍 Testing OAuth State Parameter Format...")
        
        if not auth_url:
            self.log_test("OAuth State Parameter", False, "No OAuth URL to analyze")
            return False

        try:
            # Parse the OAuth URL
            parsed_url = urlparse(auth_url)
            query_params = parse_qs(parsed_url.query)
            
            # Extract state parameter
            state_param = query_params.get('state', [None])[0]
            
            if not state_param:
                self.log_test("OAuth State Parameter", False, "No state parameter found in OAuth URL")
                return False

            # Check if state parameter contains admin user ID
            expected_pattern = f"{self.admin_user_id}:fidus_oauth_state"
            
            if state_param == expected_pattern:
                self.log_test("OAuth State Parameter", True, 
                            f"State parameter correct: '{state_param}' matches expected format")
                return True
            elif "fidus_oauth_state" in state_param:
                # Check if it contains user ID in some format
                if self.admin_user_id and self.admin_user_id in state_param:
                    self.log_test("OAuth State Parameter", True, 
                                f"State parameter contains user ID: '{state_param}'")
                    return True
                else:
                    self.log_test("OAuth State Parameter", False, 
                                f"State parameter missing user ID: '{state_param}' (expected to contain '{self.admin_user_id}')")
                    return False
            else:
                self.log_test("OAuth State Parameter", False, 
                            f"State parameter invalid format: '{state_param}' (expected format: '{expected_pattern}')")
                return False
                
        except Exception as e:
            self.log_test("OAuth State Parameter", False, f"Error parsing OAuth URL: {str(e)}")
            return False

    def test_oauth_url_parameters(self, auth_url):
        """Test that OAuth URL contains all required parameters"""
        print("🔍 Testing OAuth URL Parameters...")
        
        if not auth_url:
            self.log_test("OAuth URL Parameters", False, "No OAuth URL to analyze")
            return False

        try:
            parsed_url = urlparse(auth_url)
            query_params = parse_qs(parsed_url.query)
            
            # Required OAuth parameters
            required_params = {
                'client_id': 'Google Client ID',
                'redirect_uri': 'Redirect URI',
                'response_type': 'Response Type (should be code)',
                'scope': 'OAuth Scopes',
                'state': 'State Parameter'
            }
            
            missing_params = []
            param_details = []
            
            for param, description in required_params.items():
                if param in query_params:
                    value = query_params[param][0]
                    param_details.append(f"{description}: {value[:50]}{'...' if len(value) > 50 else ''}")
                else:
                    missing_params.append(param)
            
            if not missing_params:
                self.log_test("OAuth URL Parameters", True, 
                            f"All required parameters present: {', '.join(required_params.keys())}")
                
                # Log parameter details
                for detail in param_details:
                    print(f"   {detail}")
                print()
                return True
            else:
                self.log_test("OAuth URL Parameters", False, 
                            f"Missing parameters: {', '.join(missing_params)}")
                return False
                
        except Exception as e:
            self.log_test("OAuth URL Parameters", False, f"Error parsing OAuth URL: {str(e)}")
            return False

    def test_oauth_callback_readiness(self):
        """Test OAuth callback endpoint accessibility"""
        print("🔍 Testing OAuth Callback Readiness...")
        
        # Test callback endpoint accessibility (should return method not allowed or similar)
        callback_endpoints = [
            "/auth/google/callback",
            "/admin/google-callback"
        ]
        
        callback_accessible = False
        
        for endpoint in callback_endpoints:
            response = self.make_request("GET", endpoint)
            if response:
                if response.status_code in [200, 405, 400]:  # 405 = Method Not Allowed is expected for GET on callback
                    callback_accessible = True
                    self.log_test("OAuth Callback Readiness", True, 
                                f"Callback endpoint {endpoint} accessible (HTTP {response.status_code})")
                    break
        
        if not callback_accessible:
            self.log_test("OAuth Callback Readiness", False, 
                        "No OAuth callback endpoints accessible")
            return False
        
        return True

    def test_google_profile_endpoint(self):
        """Test Google profile endpoint (should require OAuth completion)"""
        print("🔍 Testing Google Profile Endpoint...")
        
        if not self.admin_token:
            self.log_test("Google Profile Endpoint", False, "No admin token available")
            return False

        response = self.make_request("GET", "/admin/google/profile", auth_token=self.admin_token)
        if response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get("connected"):
                        self.log_test("Google Profile Endpoint", True, 
                                    "Google profile connected and accessible")
                    else:
                        self.log_test("Google Profile Endpoint", True, 
                                    "Google profile endpoint working (not connected yet)")
                except json.JSONDecodeError:
                    self.log_test("Google Profile Endpoint", False, "Invalid JSON response")
            elif response.status_code == 401:
                self.log_test("Google Profile Endpoint", True, 
                            "Google profile endpoint requires OAuth (expected)")
            elif response.status_code == 404:
                self.log_test("Google Profile Endpoint", False, 
                            "Google profile endpoint not found")
            else:
                try:
                    data = response.json()
                    if "auth_required" in data or "google_authentication_required" in str(data):
                        self.log_test("Google Profile Endpoint", True, 
                                    "Google profile endpoint properly indicates auth required")
                    else:
                        self.log_test("Google Profile Endpoint", False, 
                                    f"Unexpected response: HTTP {response.status_code}")
                except:
                    self.log_test("Google Profile Endpoint", False, 
                                f"Unexpected response: HTTP {response.status_code}")
        else:
            self.log_test("Google Profile Endpoint", False, "No response from endpoint")

    def run_oauth_state_test(self):
        """Run focused Google OAuth state parameter testing"""
        print("🚀 Google OAuth State Parameter Fix Testing")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Started: {datetime.now(timezone.utc).isoformat()}")
        print("Testing the fix: state parameter format {admin_user_id}:fidus_oauth_state")
        print("=" * 80)
        print()

        # Step 1: Admin Authentication
        auth_success = self.test_admin_authentication()
        if not auth_success:
            print("🚨 CRITICAL: Admin authentication failed - cannot proceed with OAuth testing")
            return False

        # Step 2: Google OAuth URL Generation
        auth_url = self.test_google_oauth_url_generation()
        if not auth_url:
            print("🚨 CRITICAL: OAuth URL generation failed - state parameter cannot be tested")
            return False

        # Step 3: OAuth State Parameter Testing (MAIN FOCUS)
        state_success = self.test_oauth_state_parameter(auth_url)
        
        # Step 4: OAuth URL Parameters Validation
        params_success = self.test_oauth_url_parameters(auth_url)
        
        # Step 5: OAuth Callback Readiness
        callback_success = self.test_oauth_callback_readiness()
        
        # Step 6: Google Profile Endpoint
        self.test_google_profile_endpoint()

        # Generate summary
        print("=" * 80)
        print("🎯 GOOGLE OAUTH STATE PARAMETER FIX TEST SUMMARY")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()

        # Show failed tests
        failed_tests = [t for t in self.test_results if not t["success"]]
        if failed_tests:
            print("❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"   • {test['test']}: {test['error']}")
            print()

        # Critical findings
        print("🔍 CRITICAL FINDINGS:")
        
        if auth_success:
            print(f"   ✅ Admin authentication working (User ID: {self.admin_user_id})")
        else:
            print("   ❌ Admin authentication failed - OAuth testing blocked")
            
        if auth_url:
            print("   ✅ OAuth URL generation working")
        else:
            print("   ❌ OAuth URL generation failed - state parameter fix cannot be verified")

        if state_success:
            print("   ✅ STATE PARAMETER FIX WORKING - Contains admin user ID")
        else:
            print("   ❌ STATE PARAMETER FIX FAILED - Missing or incorrect admin user ID")

        if params_success:
            print("   ✅ OAuth URL parameters complete")
        else:
            print("   ❌ OAuth URL missing required parameters")

        if callback_success:
            print("   ✅ OAuth callback endpoints accessible")
        else:
            print("   ❌ OAuth callback endpoints not accessible")

        print()
        print("=" * 80)
        
        # Final verdict on the state parameter fix
        if state_success and auth_success:
            print("🎉 STATE PARAMETER FIX VERIFIED: OAuth flow ready for callback processing")
            print("✅ The fix ensures admin_user_id is included in state for proper callback handling")
        elif auth_success and auth_url:
            print("⚠️  STATE PARAMETER FIX NEEDS REVIEW: OAuth URL generated but state format incorrect")
            print("❌ The state parameter may not include admin_user_id as required")
        else:
            print("🚨 STATE PARAMETER FIX CANNOT BE VERIFIED: OAuth URL generation failed")
            print("❌ Need to fix OAuth URL generation before testing state parameter")
            
        print("=" * 80)
        
        return state_success and auth_success

if __name__ == "__main__":
    tester = GoogleOAuthStateTester()
    success = tester.run_oauth_state_test()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)