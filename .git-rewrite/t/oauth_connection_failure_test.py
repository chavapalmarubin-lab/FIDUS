#!/usr/bin/env python3
"""
OAuth Connection Failure Specific Test
Debug the exact issue user is experiencing:
- "Connection Failed" when clicking "Connect Google Workspace"
- "Google Auth Success: false"
- "Individual Google OAuth Code: None"
- "No OAuth callback - checking normal authentication"

This test focuses on the specific OAuth flow that the user is trying to complete.
"""

import requests
import json
import time
import sys
from datetime import datetime, timezone
import urllib.parse

# Backend URL Configuration
BACKEND_URL = "https://fidus-invest.emergent.host/api"

class OAuthConnectionFailureTester:
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
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, headers=req_headers, timeout=30)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=req_headers, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None

    def authenticate_admin(self):
        """Authenticate as admin user"""
        print("🔐 Authenticating as admin...")
        
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

    def test_oauth_url_generation_updated_redirect(self):
        """Test OAuth URL generation with updated redirect URI"""
        print("🔍 Testing OAuth URL Generation (Updated Redirect URI)...")
        
        if not self.admin_token:
            self.log_test("OAuth URL Generation", False, "No admin token available")
            return

        # Test Direct Google OAuth URL generation
        response = self.make_request("GET", "/auth/google/url", auth_token=self.admin_token)
        if response and response.status_code == 200:
            try:
                data = response.json()
                auth_url = data.get("auth_url", "")
                
                if auth_url and "accounts.google.com" in auth_url:
                    # Parse URL to check redirect URI specifically
                    parsed_url = urllib.parse.urlparse(auth_url)
                    query_params = urllib.parse.parse_qs(parsed_url.query)
                    
                    redirect_uri = query_params.get("redirect_uri", [""])[0]
                    client_id = query_params.get("client_id", [""])[0]
                    scopes = query_params.get("scope", [""])[0]
                    state = query_params.get("state", [""])[0]
                    
                    # Check if redirect URI has been updated correctly
                    expected_redirect = "https://fidus-invest.emergent.host/admin/google-callback"
                    if redirect_uri == expected_redirect:
                        self.log_test("OAuth URL Generation - Redirect URI Fixed", True,
                                    f"Redirect URI correctly updated: {redirect_uri}")
                    else:
                        self.log_test("OAuth URL Generation - Redirect URI Fixed", False,
                                    f"Redirect URI not updated. Expected: {expected_redirect}, Got: {redirect_uri}")
                    
                    # Check client ID
                    expected_client_id = "909926639154-r3v0ka94cbu4uo0sn8g4jvtiulf4i9qs.apps.googleusercontent.com"
                    if client_id == expected_client_id:
                        self.log_test("OAuth URL Generation - Client ID", True,
                                    f"Client ID correct: {client_id}")
                    else:
                        self.log_test("OAuth URL Generation - Client ID", False,
                                    f"Client ID mismatch. Expected: {expected_client_id}, Got: {client_id}")
                    
                    # Check scopes
                    required_scopes = ["gmail.readonly", "gmail.send", "drive", "calendar"]
                    decoded_scopes = urllib.parse.unquote(scopes)
                    scope_list = decoded_scopes.split()
                    
                    missing_scopes = []
                    for required_scope in required_scopes:
                        if not any(required_scope in scope for scope in scope_list):
                            missing_scopes.append(required_scope)
                    
                    if not missing_scopes:
                        self.log_test("OAuth URL Generation - Scopes", True,
                                    f"All required scopes present: {len(scope_list)} scopes")
                    else:
                        self.log_test("OAuth URL Generation - Scopes", False,
                                    f"Missing scopes: {missing_scopes}")
                    
                    # Check state parameter
                    if state and "admin_001" in state:
                        self.log_test("OAuth URL Generation - State Parameter", True,
                                    f"State parameter includes admin ID: {state}")
                    else:
                        self.log_test("OAuth URL Generation - State Parameter", False,
                                    f"State parameter missing admin ID: {state}")
                        
                else:
                    self.log_test("OAuth URL Generation", False,
                                "Invalid or missing OAuth URL")
            except json.JSONDecodeError:
                self.log_test("OAuth URL Generation", False, 
                            "Invalid JSON response")
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("OAuth URL Generation", False, f"HTTP {status_code}")

    def test_connection_status_discrepancy(self):
        """Test why connection status shows disconnected"""
        print("🔍 Testing Connection Status Discrepancy...")
        
        if not self.admin_token:
            self.log_test("Connection Status Test", False, "No admin token available")
            return

        # Test main connection status endpoint
        response = self.make_request("GET", "/google/connection/test-all", 
                                   auth_token=self.admin_token)
        if response and response.status_code == 200:
            try:
                data = response.json()
                overall_status = data.get("overall_status", "unknown")
                services = data.get("services", {})
                
                # Count connected services
                connected_services = []
                disconnected_services = []
                
                for service_name, service_data in services.items():
                    if isinstance(service_data, dict):
                        status = service_data.get("status", "unknown")
                        connected = service_data.get("connected", False)
                        
                        if connected or status.lower() == "connected":
                            connected_services.append(service_name)
                        else:
                            disconnected_services.append(service_name)
                            
                self.log_test("Connection Status - Service Count", True,
                            f"Connected: {len(connected_services)}, Disconnected: {len(disconnected_services)}")
                
                # Check individual OAuth status
                response2 = self.make_request("GET", "/admin/google/individual-status", 
                                           auth_token=self.admin_token)
                if response2 and response2.status_code == 200:
                    try:
                        individual_data = response2.json()
                        individual_connected = individual_data.get("connected", False)
                        google_email = individual_data.get("google_email", "Not connected")
                        
                        # Compare connection monitor vs individual status
                        if len(connected_services) > 0 and individual_connected:
                            self.log_test("Connection Status - Consistency Check", True,
                                        f"Both monitor and individual show connected. Google email: {google_email}")
                        elif len(connected_services) > 0 and not individual_connected:
                            self.log_test("Connection Status - Consistency Check", False,
                                        f"Monitor shows {len(connected_services)} connected but individual shows disconnected")
                        elif len(connected_services) == 0 and individual_connected:
                            self.log_test("Connection Status - Consistency Check", False,
                                        f"Monitor shows disconnected but individual shows connected: {google_email}")
                        else:
                            self.log_test("Connection Status - Consistency Check", True,
                                        "Both monitor and individual show disconnected (consistent)")
                            
                    except json.JSONDecodeError:
                        self.log_test("Connection Status - Individual Status", False, 
                                    "Invalid JSON response from individual status")
                else:
                    status_code = response2.status_code if response2 else "No response"
                    self.log_test("Connection Status - Individual Status", False, f"HTTP {status_code}")
                    
            except json.JSONDecodeError:
                self.log_test("Connection Status - Service Count", False, 
                            "Invalid JSON response")
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("Connection Status - Service Count", False, f"HTTP {status_code}")

    def test_oauth_callback_endpoints(self):
        """Test OAuth callback endpoint accessibility"""
        print("🔍 Testing OAuth Callback Endpoints...")
        
        # Test all possible callback endpoints
        callback_endpoints = [
            "/admin/google-callback",
            "/api/admin/google-callback", 
            "/auth/google/callback"
        ]
        
        for endpoint in callback_endpoints:
            # Test GET request to callback (should return some response, not 404)
            response = self.make_request("GET", endpoint)
            if response:
                if response.status_code == 404:
                    self.log_test(f"OAuth Callback - {endpoint}", False,
                                f"Endpoint not found (HTTP 404)")
                elif response.status_code in [200, 400, 401, 405, 302]:
                    # These are acceptable responses (endpoint exists)
                    try:
                        # Try to get response content for more info
                        if response.headers.get('content-type', '').startswith('application/json'):
                            data = response.json()
                            self.log_test(f"OAuth Callback - {endpoint}", True,
                                        f"Endpoint accessible (HTTP {response.status_code}), Response: {str(data)[:100]}")
                        else:
                            self.log_test(f"OAuth Callback - {endpoint}", True,
                                        f"Endpoint accessible (HTTP {response.status_code})")
                    except:
                        self.log_test(f"OAuth Callback - {endpoint}", True,
                                    f"Endpoint accessible (HTTP {response.status_code})")
                else:
                    self.log_test(f"OAuth Callback - {endpoint}", True,
                                f"Endpoint exists (HTTP {response.status_code})")
            else:
                self.log_test(f"OAuth Callback - {endpoint}", False,
                            "No response from endpoint")

    def test_google_api_authentication_status(self):
        """Test Google API authentication status"""
        print("🔍 Testing Google API Authentication Status...")
        
        if not self.admin_token:
            self.log_test("Google API Auth Status", False, "No admin token available")
            return

        # Test Gmail API
        response = self.make_request("GET", "/google/gmail/real-messages", 
                                   auth_token=self.admin_token)
        if response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "messages" in data and len(data["messages"]) > 0:
                        self.log_test("Google API Auth - Gmail", True,
                                    f"Gmail API working, {len(data['messages'])} messages retrieved")
                    elif data.get("auth_required"):
                        self.log_test("Google API Auth - Gmail", False,
                                    "Gmail API requires authentication (OAuth not completed)")
                    else:
                        self.log_test("Google API Auth - Gmail", False,
                                    f"Gmail API response unexpected: {str(data)[:100]}")
                except json.JSONDecodeError:
                    self.log_test("Google API Auth - Gmail", False,
                                "Invalid JSON response from Gmail API")
            else:
                self.log_test("Google API Auth - Gmail", False,
                            f"Gmail API error: HTTP {response.status_code}")
        else:
            self.log_test("Google API Auth - Gmail", False,
                        "No response from Gmail API")

        # Test Calendar API
        response = self.make_request("GET", "/google/calendar/events", 
                                   auth_token=self.admin_token)
        if response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "events" in data:
                        self.log_test("Google API Auth - Calendar", True,
                                    f"Calendar API working, {len(data['events'])} events retrieved")
                    elif data.get("auth_required"):
                        self.log_test("Google API Auth - Calendar", False,
                                    "Calendar API requires authentication (OAuth not completed)")
                    else:
                        self.log_test("Google API Auth - Calendar", False,
                                    f"Calendar API response unexpected: {str(data)[:100]}")
                except json.JSONDecodeError:
                    self.log_test("Google API Auth - Calendar", False,
                                "Invalid JSON response from Calendar API")
            else:
                self.log_test("Google API Auth - Calendar", False,
                            f"Calendar API error: HTTP {response.status_code}")
        else:
            self.log_test("Google API Auth - Calendar", False,
                        "No response from Calendar API")

    def run_oauth_connection_failure_test(self):
        """Run OAuth connection failure specific test"""
        print("🚀 OAuth Connection Failure Debug Test")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Started: {datetime.now(timezone.utc).isoformat()}")
        print("=" * 80)
        print()

        # Authenticate first
        if not self.authenticate_admin():
            print("❌ Cannot proceed without admin authentication")
            return 0

        # Run OAuth connection failure tests
        self.test_oauth_url_generation_updated_redirect()
        self.test_connection_status_discrepancy()
        self.test_oauth_callback_endpoints()
        self.test_google_api_authentication_status()

        # Generate summary
        print("=" * 80)
        print("🎯 OAUTH CONNECTION FAILURE DEBUG SUMMARY")
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
        print("🔍 CRITICAL FINDINGS:")
        
        # OAuth URL Analysis
        oauth_tests = [t for t in self.test_results if "OAuth URL Generation" in t["test"]]
        oauth_success = sum(1 for t in oauth_tests if t["success"])
        if oauth_success >= 3:
            print("   ✅ OAuth URL generation working correctly after redirect URI fix")
        else:
            print("   ❌ OAuth URL generation still has issues")

        # Connection Status Analysis
        connection_tests = [t for t in self.test_results if "Connection Status" in t["test"]]
        connection_success = sum(1 for t in connection_tests if t["success"])
        if connection_success >= 1:
            print("   ✅ Connection status monitoring working")
        else:
            print("   ❌ Connection status monitoring has issues")

        # OAuth Callback Analysis
        callback_tests = [t for t in self.test_results if "OAuth Callback" in t["test"]]
        callback_success = sum(1 for t in callback_tests if t["success"])
        if callback_success >= 1:
            print("   ✅ OAuth callback endpoints accessible")
        else:
            print("   ❌ OAuth callback endpoints not accessible - OAuth flow will fail")

        # Google API Analysis
        api_tests = [t for t in self.test_results if "Google API Auth" in t["test"]]
        api_success = sum(1 for t in api_tests if t["success"])
        if api_success >= 1:
            print("   ✅ Some Google APIs working (OAuth may be partially complete)")
        else:
            print("   ❌ Google APIs require authentication (OAuth not completed)")

        print()
        print("=" * 80)
        
        # Provide specific recommendations
        print("🔧 SPECIFIC RECOMMENDATIONS FOR USER:")
        
        if success_rate >= 80:
            print("   • OAuth infrastructure is working correctly")
            print("   • User should try completing OAuth flow by:")
            print("     1. Click 'Connect Google Workspace' button")
            print("     2. Complete Google OAuth consent screen")
            print("     3. Allow all requested permissions")
            print("     4. Wait for redirect back to application")
        elif success_rate >= 60:
            print("   • OAuth infrastructure mostly working")
            print("   • Check failed tests above for specific issues")
            print("   • User may need to clear browser cache and try again")
        else:
            print("   • Critical OAuth infrastructure issues")
            print("   • Fix failed tests before user attempts OAuth flow")
            print("   • Backend configuration needs attention")

        print("=" * 80)
        
        return success_rate

if __name__ == "__main__":
    tester = OAuthConnectionFailureTester()
    success_rate = tester.run_oauth_connection_failure_test()
    
    # Exit with appropriate code
    sys.exit(0 if success_rate >= 70 else 1)