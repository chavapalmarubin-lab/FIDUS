#!/usr/bin/env python3
"""
Google OAuth Flow Testing - Specific to User's "Connect Google Workspace" Issue

This test focuses on the exact OAuth flow that happens when user clicks "Connect Google Workspace" button.
Testing the specific issue: "Connection Failed" with "Google Auth Success: false" and "No emails returned from Gmail API, using fallback"

Test Flow:
1. OAuth URL generation (/api/auth/google/url)
2. OAuth URL validity check
3. Connection status check (/api/google/connection/test-all)
4. Gmail API call (/api/google/gmail/real-messages)
5. OAuth callback endpoint accessibility (/api/admin/google-callback)

Admin Credentials: admin/password123
Backend URL: https://fidus-invest.emergent.host/api
"""

import requests
import json
import time
import sys
from datetime import datetime, timezone
import urllib.parse

# Backend URL Configuration
BACKEND_URL = "https://fidus-invest.emergent.host/api"

class GoogleOAuthFlowTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
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

    def authenticate_admin(self):
        """Authenticate as admin user"""
        print("🔐 Authenticating as admin user...")
        
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
                    self.log_test("Admin Authentication", True, 
                                f"Admin: {data.get('name')}, ID: {data.get('id')}")
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

    def test_oauth_url_generation(self):
        """Test OAuth URL generation - the exact endpoint frontend calls"""
        print("🔍 Testing OAuth URL Generation (/api/auth/google/url)...")
        
        if not self.admin_token:
            self.log_test("OAuth URL Generation", False, "No admin token available")
            return None
            
        response = self.make_request("GET", "/auth/google/url", auth_token=self.admin_token)
        if response and response.status_code == 200:
            try:
                data = response.json()
                auth_url = data.get("auth_url")
                if auth_url and "accounts.google.com" in auth_url:
                    # Parse URL to check parameters
                    parsed_url = urllib.parse.urlparse(auth_url)
                    query_params = urllib.parse.parse_qs(parsed_url.query)
                    
                    required_params = ["client_id", "redirect_uri", "response_type", "scope", "state"]
                    missing_params = [param for param in required_params if param not in query_params]
                    
                    if not missing_params:
                        self.log_test("OAuth URL Generation", True, 
                                    f"Valid OAuth URL with all required parameters: {auth_url[:100]}...")
                        return auth_url
                    else:
                        self.log_test("OAuth URL Generation", False, 
                                    f"Missing required parameters: {missing_params}")
                        return None
                else:
                    self.log_test("OAuth URL Generation", False, 
                                "Invalid or missing OAuth URL")
                    return None
            except json.JSONDecodeError:
                self.log_test("OAuth URL Generation", False, "Invalid JSON response")
                return None
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("OAuth URL Generation", False, f"HTTP {status_code}")
            return None

    def test_oauth_url_validity(self, oauth_url):
        """Test if the generated OAuth URL is actually valid"""
        print("🔍 Testing OAuth URL Validity...")
        
        if not oauth_url:
            self.log_test("OAuth URL Validity", False, "No OAuth URL to test")
            return
            
        try:
            # Make a HEAD request to the OAuth URL to check if it's accessible
            response = requests.head(oauth_url, timeout=10, allow_redirects=True)
            if response.status_code in [200, 302]:
                self.log_test("OAuth URL Validity", True, 
                            f"OAuth URL accessible (HTTP {response.status_code})")
            else:
                self.log_test("OAuth URL Validity", False, 
                            f"OAuth URL returned HTTP {response.status_code}")
        except requests.exceptions.RequestException as e:
            self.log_test("OAuth URL Validity", False, f"OAuth URL request failed: {str(e)}")

    def test_connection_status_check(self):
        """Test connection status check endpoint"""
        print("🔍 Testing Connection Status Check (/api/google/connection/test-all)...")
        
        if not self.admin_token:
            self.log_test("Connection Status Check", False, "No admin token available")
            return
            
        response = self.make_request("GET", "/google/connection/test-all", auth_token=self.admin_token)
        if response and response.status_code == 200:
            try:
                data = response.json()
                overall_status = data.get("overall_status")
                services = data.get("services", {})
                
                expected_services = ["gmail", "calendar", "drive", "meet"]
                found_services = [svc for svc in expected_services if svc in services]
                
                if len(found_services) == 4:
                    service_statuses = {svc: services[svc].get("status", "unknown") for svc in found_services}
                    self.log_test("Connection Status Check", True, 
                                f"Overall status: {overall_status}, Services: {service_statuses}")
                else:
                    self.log_test("Connection Status Check", False, 
                                f"Expected 4 services, found {len(found_services)}: {found_services}")
            except json.JSONDecodeError:
                self.log_test("Connection Status Check", False, "Invalid JSON response")
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("Connection Status Check", False, f"HTTP {status_code}")

    def test_gmail_api_call(self):
        """Test Gmail API call that's returning 'No emails returned'"""
        print("🔍 Testing Gmail API Call (/api/google/gmail/real-messages)...")
        
        if not self.admin_token:
            self.log_test("Gmail API Call", False, "No admin token available")
            return
            
        response = self.make_request("GET", "/google/gmail/real-messages", auth_token=self.admin_token)
        if response:
            try:
                data = response.json()
                
                if response.status_code == 200:
                    messages = data.get("messages", [])
                    if messages:
                        self.log_test("Gmail API Call", True, 
                                    f"Gmail API returned {len(messages)} messages")
                    else:
                        # Check if it's an auth_required response
                        if data.get("auth_required"):
                            self.log_test("Gmail API Call", True, 
                                        f"Gmail API correctly indicates authentication required: {data.get('message', 'No message')}")
                        else:
                            self.log_test("Gmail API Call", False, 
                                        "Gmail API returned no messages and no auth_required flag")
                else:
                    # Non-200 status but valid JSON
                    if data.get("auth_required"):
                        self.log_test("Gmail API Call", True, 
                                    f"Gmail API correctly indicates authentication required (HTTP {response.status_code})")
                    else:
                        self.log_test("Gmail API Call", False, 
                                    f"Gmail API returned HTTP {response.status_code}: {data}")
                        
            except json.JSONDecodeError:
                self.log_test("Gmail API Call", False, 
                            f"Invalid JSON response (HTTP {response.status_code})")
        else:
            self.log_test("Gmail API Call", False, "No response from Gmail API")

    def test_oauth_callback_endpoint(self):
        """Test OAuth callback endpoint accessibility"""
        print("🔍 Testing OAuth Callback Endpoint (/api/admin/google-callback)...")
        
        # Test callback endpoint accessibility (should return some response, not 404)
        response = self.make_request("GET", "/admin/google-callback")
        if response:
            if response.status_code == 404:
                self.log_test("OAuth Callback Endpoint", False, 
                            "OAuth callback endpoint returns 404 - not accessible")
            elif response.status_code in [400, 401, 403]:
                # These are expected for GET requests without proper OAuth parameters
                self.log_test("OAuth Callback Endpoint", True, 
                            f"OAuth callback endpoint accessible (HTTP {response.status_code})")
            else:
                self.log_test("OAuth Callback Endpoint", True, 
                            f"OAuth callback endpoint accessible (HTTP {response.status_code})")
        else:
            self.log_test("OAuth Callback Endpoint", False, "No response from callback endpoint")

    def test_alternative_oauth_endpoints(self):
        """Test alternative OAuth endpoints that might be used"""
        print("🔍 Testing Alternative OAuth Endpoints...")
        
        if not self.admin_token:
            self.log_test("Alternative OAuth Endpoints", False, "No admin token available")
            return
            
        # Test Emergent OAuth endpoint
        response = self.make_request("GET", "/admin/google/auth-url", auth_token=self.admin_token)
        if response and response.status_code == 200:
            try:
                data = response.json()
                if data.get("auth_url"):
                    self.log_test("Alternative OAuth - Emergent", True, 
                                "Emergent OAuth endpoint working")
                else:
                    self.log_test("Alternative OAuth - Emergent", False, 
                                "Emergent OAuth endpoint missing auth_url")
            except json.JSONDecodeError:
                self.log_test("Alternative OAuth - Emergent", False, "Invalid JSON response")
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("Alternative OAuth - Emergent", False, f"HTTP {status_code}")

    def test_google_profile_endpoint(self):
        """Test Google profile endpoint"""
        print("🔍 Testing Google Profile Endpoint...")
        
        if not self.admin_token:
            self.log_test("Google Profile Endpoint", False, "No admin token available")
            return
            
        response = self.make_request("GET", "/admin/google/profile", auth_token=self.admin_token)
        if response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    self.log_test("Google Profile Endpoint", True, 
                                f"Google profile endpoint accessible: {data}")
                except json.JSONDecodeError:
                    self.log_test("Google Profile Endpoint", False, "Invalid JSON response")
            elif response.status_code == 404:
                self.log_test("Google Profile Endpoint", False, 
                            "Google profile endpoint returns 404")
            else:
                # Auth required or other expected responses
                self.log_test("Google Profile Endpoint", True, 
                            f"Google profile endpoint accessible (HTTP {response.status_code})")
        else:
            self.log_test("Google Profile Endpoint", False, "No response")

    def run_oauth_flow_test(self):
        """Run the complete OAuth flow test"""
        print("🚀 Google OAuth Flow Testing - Connect Google Workspace Issue")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Started: {datetime.now(timezone.utc).isoformat()}")
        print("Testing the exact flow when user clicks 'Connect Google Workspace' button")
        print("=" * 80)
        print()

        # Step 1: Authenticate as admin
        if not self.authenticate_admin():
            print("🚨 Cannot proceed without admin authentication")
            return 0

        # Step 2: Test OAuth URL generation (the exact endpoint frontend calls)
        oauth_url = self.test_oauth_url_generation()

        # Step 3: Test the actual OAuth URL validity
        self.test_oauth_url_validity(oauth_url)

        # Step 4: Test connection status check
        self.test_connection_status_check()

        # Step 5: Test Gmail API call (the one returning "No emails returned")
        self.test_gmail_api_call()

        # Step 6: Test OAuth callback endpoint
        self.test_oauth_callback_endpoint()

        # Step 7: Test alternative OAuth endpoints
        self.test_alternative_oauth_endpoints()

        # Step 8: Test Google profile endpoint
        self.test_google_profile_endpoint()

        # Generate summary
        print("=" * 80)
        print("🎯 GOOGLE OAUTH FLOW TEST SUMMARY")
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

        # Show critical findings
        print("🔍 CRITICAL FINDINGS FOR 'CONNECT GOOGLE WORKSPACE' ISSUE:")
        print()
        
        # OAuth URL Generation
        oauth_test = next((t for t in self.test_results if "OAuth URL Generation" in t["test"]), None)
        if oauth_test and oauth_test["success"]:
            print("   ✅ OAuth URL generation working - frontend can get OAuth URL")
        else:
            print("   ❌ OAuth URL generation failing - this is why 'Connect' button fails")

        # OAuth URL Validity
        validity_test = next((t for t in self.test_results if "OAuth URL Validity" in t["test"]), None)
        if validity_test and validity_test["success"]:
            print("   ✅ Generated OAuth URL is valid and points to Google")
        else:
            print("   ❌ Generated OAuth URL is invalid - users can't complete OAuth")

        # Connection Status
        connection_test = next((t for t in self.test_results if "Connection Status Check" in t["test"]), None)
        if connection_test and connection_test["success"]:
            print("   ✅ Connection status endpoint working - can check connection state")
        else:
            print("   ❌ Connection status endpoint failing - can't determine connection state")

        # Gmail API
        gmail_test = next((t for t in self.test_results if "Gmail API Call" in t["test"]), None)
        if gmail_test and gmail_test["success"]:
            print("   ✅ Gmail API endpoint working - 'No emails returned' is expected without OAuth")
        else:
            print("   ❌ Gmail API endpoint failing - this explains the fallback message")

        # OAuth Callback
        callback_test = next((t for t in self.test_results if "OAuth Callback Endpoint" in t["test"]), None)
        if callback_test and callback_test["success"]:
            print("   ✅ OAuth callback endpoint accessible - can handle OAuth return")
        else:
            print("   ❌ OAuth callback endpoint not accessible - OAuth flow can't complete")

        print()
        print("🎯 ROOT CAUSE ANALYSIS:")
        
        if success_rate >= 80:
            print("   • OAuth infrastructure is working correctly")
            print("   • 'Connection Failed' likely due to frontend integration issue")
            print("   • Check frontend OAuth button implementation")
        elif success_rate >= 60:
            print("   • OAuth infrastructure has minor issues")
            print("   • Some components working, others need attention")
            print("   • Focus on failed tests above")
        else:
            print("   • OAuth infrastructure has critical issues")
            print("   • Multiple components failing")
            print("   • Backend OAuth implementation needs immediate attention")

        print()
        print("=" * 80)
        
        if success_rate >= 80:
            print("🎉 OAUTH STATUS: BACKEND INFRASTRUCTURE READY")
        elif success_rate >= 60:
            print("⚠️  OAUTH STATUS: MINOR ISSUES - REVIEW REQUIRED")
        else:
            print("🚨 OAUTH STATUS: CRITICAL ISSUES - IMMEDIATE ATTENTION REQUIRED")
            
        print("=" * 80)
        
        return success_rate

if __name__ == "__main__":
    tester = GoogleOAuthFlowTester()
    success_rate = tester.run_oauth_flow_test()
    
    # Exit with appropriate code
    sys.exit(0 if success_rate >= 60 else 1)