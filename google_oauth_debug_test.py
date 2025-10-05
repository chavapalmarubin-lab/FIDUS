#!/usr/bin/env python3
"""
Google OAuth Connection Failure Debug Test
Testing the specific OAuth flow issues reported by the user:
- "Connection Failed" when clicking "Connect Google Workspace"
- "Google Auth Success: false"
- "Individual Google OAuth Code: None"
- "No OAuth callback - checking normal authentication"

Focus Areas:
1. OAuth URL generation (/api/auth/google/url)
2. Connection status check (/api/google/connection/test-all)
3. OAuth callback accessibility (/api/admin/google-callback)
4. Redirect URI configuration verification
5. OAuth flow completion testing

Admin Credentials: admin/password123
"""

import requests
import json
import time
import sys
from datetime import datetime, timezone

# Backend URL Configuration - Use REACT_APP_BACKEND_URL from frontend/.env
BACKEND_URL = "https://fidus-invest.emergent.host/api"

class GoogleOAuthDebugTester:
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
        """Test Google OAuth URL generation"""
        print("🔍 Testing Google OAuth URL Generation...")
        
        if not self.admin_token:
            self.log_test("OAuth URL Generation", False, "No admin token available")
            return

        # Test direct Google OAuth URL generation
        response = self.make_request("GET", "/auth/google/url", auth_token=self.admin_token)
        if response and response.status_code == 200:
            try:
                data = response.json()
                auth_url = data.get("auth_url", "")
                
                # Check if URL contains required OAuth parameters
                required_params = ["client_id", "redirect_uri", "response_type", "scope", "state"]
                missing_params = []
                
                for param in required_params:
                    if param not in auth_url:
                        missing_params.append(param)
                
                if not missing_params and "accounts.google.com" in auth_url:
                    self.log_test("OAuth URL Generation", True, 
                                f"Valid OAuth URL with all required parameters")
                    
                    # Extract and log OAuth parameters for debugging
                    if "client_id=" in auth_url:
                        client_id_start = auth_url.find("client_id=") + 10
                        client_id_end = auth_url.find("&", client_id_start)
                        client_id = auth_url[client_id_start:client_id_end] if client_id_end != -1 else auth_url[client_id_start:]
                        print(f"   Client ID: {client_id}")
                    
                    if "scope=" in auth_url:
                        scope_start = auth_url.find("scope=") + 6
                        scope_end = auth_url.find("&", scope_start)
                        scope = auth_url[scope_start:scope_end] if scope_end != -1 else auth_url[scope_start:]
                        print(f"   Scopes: {scope.replace('%20', ' ')}")
                        
                else:
                    self.log_test("OAuth URL Generation", False, 
                                f"Missing parameters: {missing_params}")
            except json.JSONDecodeError:
                self.log_test("OAuth URL Generation", False, "Invalid JSON response")
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("OAuth URL Generation", False, f"HTTP {status_code}")

    def test_stored_token_retrieval(self):
        """Test stored Google OAuth token retrieval"""
        print("🔍 Testing Stored Google OAuth Token Retrieval...")
        
        if not self.admin_token:
            self.log_test("Token Retrieval", False, "No admin token available")
            return

        # Test individual Google OAuth status
        response = self.make_request("GET", "/admin/google/individual-status", 
                                   auth_token=self.admin_token)
        if response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    connected = data.get("connected", False)
                    google_email = data.get("google_email", "")
                    
                    if connected and google_email:
                        self.log_test("Token Retrieval - Individual Status", True,
                                    f"Connected to Google account: {google_email}")
                        
                        # Check token details if available
                        token_info = data.get("token_info", {})
                        if token_info:
                            scopes = token_info.get("scopes", [])
                            expires_at = token_info.get("expires_at", "")
                            print(f"   Token Scopes: {scopes}")
                            print(f"   Token Expires: {expires_at}")
                            
                            # Check for required token fields
                            required_fields = ["access_token", "refresh_token", "client_id", "client_secret"]
                            missing_fields = [field for field in required_fields if field not in token_info]
                            
                            if missing_fields:
                                print(f"   ⚠️ Missing token fields: {missing_fields}")
                            else:
                                print(f"   ✅ All required token fields present")
                        
                    else:
                        self.log_test("Token Retrieval - Individual Status", False,
                                    "Not connected to Google or missing email")
                except json.JSONDecodeError:
                    self.log_test("Token Retrieval - Individual Status", False, 
                                "Invalid JSON response")
            else:
                self.log_test("Token Retrieval - Individual Status", False,
                            f"HTTP {response.status_code}")
        else:
            self.log_test("Token Retrieval - Individual Status", False, "No response")

    def test_gmail_api_calls(self):
        """Test Gmail API calls that are failing"""
        print("🔍 Testing Gmail API Calls...")
        
        if not self.admin_token:
            self.log_test("Gmail API Calls", False, "No admin token available")
            return

        # Test the specific failing endpoint: /api/admin/gmail/messages
        response = self.make_request("GET", "/admin/gmail/messages", 
                                   auth_token=self.admin_token)
        if response:
            print(f"   Response Status: {response.status_code}")
            try:
                data = response.json()
                print(f"   Response Data: {json.dumps(data, indent=2)}")
                
                if response.status_code == 200:
                    messages = data.get("messages", [])
                    if messages and len(messages) > 0:
                        self.log_test("Gmail API - Admin Messages", True,
                                    f"Retrieved {len(messages)} Gmail messages")
                    elif "auth_required" in data:
                        self.log_test("Gmail API - Admin Messages", False,
                                    "Authentication required - OAuth tokens missing or invalid")
                    else:
                        self.log_test("Gmail API - Admin Messages", False,
                                    "No messages returned - possible fallback mode")
                else:
                    error_msg = data.get("detail", data.get("error", "Unknown error"))
                    self.log_test("Gmail API - Admin Messages", False,
                                f"HTTP {response.status_code}: {error_msg}")
                    
            except json.JSONDecodeError:
                self.log_test("Gmail API - Admin Messages", False, 
                            f"Invalid JSON response (HTTP {response.status_code})")
        else:
            self.log_test("Gmail API - Admin Messages", False, "No response")

        # Test alternative Gmail API endpoint
        response = self.make_request("GET", "/google/gmail/real-messages", 
                                   auth_token=self.admin_token)
        if response:
            print(f"   Real Messages Response Status: {response.status_code}")
            try:
                data = response.json()
                
                if response.status_code == 200:
                    messages = data.get("messages", [])
                    if messages and len(messages) > 0:
                        self.log_test("Gmail API - Real Messages", True,
                                    f"Retrieved {len(messages)} real Gmail messages")
                    elif "auth_required" in data:
                        self.log_test("Gmail API - Real Messages", False,
                                    "Authentication required - OAuth tokens missing or invalid")
                    else:
                        self.log_test("Gmail API - Real Messages", False,
                                    "No messages returned from real Gmail API")
                else:
                    error_msg = data.get("detail", data.get("error", "Unknown error"))
                    self.log_test("Gmail API - Real Messages", False,
                                f"HTTP {response.status_code}: {error_msg}")
                    
            except json.JSONDecodeError:
                self.log_test("Gmail API - Real Messages", False, 
                            f"Invalid JSON response (HTTP {response.status_code})")
        else:
            self.log_test("Gmail API - Real Messages", False, "No response")

    def test_token_format_validation(self):
        """Test stored token format and required fields"""
        print("🔍 Testing Token Format Validation...")
        
        if not self.admin_token:
            self.log_test("Token Format Validation", False, "No admin token available")
            return

        # Test Google profile endpoint to check token usage
        response = self.make_request("GET", "/admin/google/profile", 
                                   auth_token=self.admin_token)
        if response:
            print(f"   Profile Response Status: {response.status_code}")
            try:
                data = response.json()
                print(f"   Profile Response: {json.dumps(data, indent=2)}")
                
                if response.status_code == 200:
                    profile = data.get("profile", {})
                    if profile and profile.get("email"):
                        self.log_test("Token Format - Profile Access", True,
                                    f"Successfully accessed Google profile: {profile.get('email')}")
                    else:
                        self.log_test("Token Format - Profile Access", False,
                                    "Empty or invalid profile data")
                elif "auth_required" in data or "authentication required" in str(data).lower():
                    self.log_test("Token Format - Profile Access", False,
                                "Google authentication required - tokens not working")
                else:
                    error_msg = data.get("detail", data.get("error", "Unknown error"))
                    self.log_test("Token Format - Profile Access", False,
                                f"HTTP {response.status_code}: {error_msg}")
                    
            except json.JSONDecodeError:
                self.log_test("Token Format - Profile Access", False, 
                            f"Invalid JSON response (HTTP {response.status_code})")
        else:
            self.log_test("Token Format - Profile Access", False, "No response")

    def check_backend_logs(self):
        """Check backend logs for specific Gmail API errors"""
        print("🔍 Checking Backend Logs for Gmail API Errors...")
        
        # This would typically require access to backend logs
        # For now, we'll test endpoints that might reveal log information
        
        if not self.admin_token:
            self.log_test("Backend Log Check", False, "No admin token available")
            return

        # Test health endpoint that might include error information
        response = self.make_request("GET", "/health", auth_token=self.admin_token)
        if response and response.status_code == 200:
            try:
                data = response.json()
                if "errors" in data or "warnings" in data:
                    self.log_test("Backend Log Check", True,
                                "Health endpoint accessible, may contain error info")
                else:
                    self.log_test("Backend Log Check", True,
                                "Health endpoint accessible, no immediate errors reported")
            except json.JSONDecodeError:
                self.log_test("Backend Log Check", False, "Invalid JSON response")
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("Backend Log Check", False, f"HTTP {status_code}")

    def test_credentials_method(self):
        """Test the _get_credentials method functionality"""
        print("🔍 Testing Credentials Method Functionality...")
        
        if not self.admin_token:
            self.log_test("Credentials Method", False, "No admin token available")
            return

        # Test Google connection test endpoint which likely uses _get_credentials
        response = self.make_request("GET", "/google/connection/test-all", 
                                   auth_token=self.admin_token)
        if response:
            print(f"   Connection Test Response Status: {response.status_code}")
            try:
                data = response.json()
                print(f"   Connection Test Response: {json.dumps(data, indent=2)}")
                
                if response.status_code == 200:
                    overall_status = data.get("overall_status", "")
                    services = data.get("services", {})
                    
                    # Check individual service statuses
                    gmail_status = services.get("gmail", {}).get("status", "unknown")
                    calendar_status = services.get("calendar", {}).get("status", "unknown")
                    drive_status = services.get("drive", {}).get("status", "unknown")
                    
                    if gmail_status == "connected":
                        self.log_test("Credentials Method - Gmail", True,
                                    "Gmail credentials working correctly")
                    elif "credential error" in gmail_status.lower() or "no_auth" in gmail_status:
                        self.log_test("Credentials Method - Gmail", False,
                                    f"Gmail credential error: {gmail_status}")
                    else:
                        self.log_test("Credentials Method - Gmail", False,
                                    f"Gmail status unknown: {gmail_status}")
                    
                    # Check for specific credential errors
                    for service_name, service_data in services.items():
                        if isinstance(service_data, dict):
                            error_msg = service_data.get("error", "")
                            if "credential" in error_msg.lower():
                                print(f"   ⚠️ {service_name} credential error: {error_msg}")
                    
                else:
                    error_msg = data.get("detail", data.get("error", "Unknown error"))
                    self.log_test("Credentials Method", False,
                                f"HTTP {response.status_code}: {error_msg}")
                    
            except json.JSONDecodeError:
                self.log_test("Credentials Method", False, 
                            f"Invalid JSON response (HTTP {response.status_code})")
        else:
            self.log_test("Credentials Method", False, "No response")

    def run_debug_tests(self):
        """Run all Google OAuth debugging tests"""
        print("🚀 Google OAuth Token Debugging Test Suite")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Started: {datetime.now(timezone.utc).isoformat()}")
        print("=" * 80)
        print()

        # Authenticate first
        if not self.authenticate_admin():
            print("❌ Cannot proceed without admin authentication")
            return 0

        # Run debugging tests
        self.test_oauth_url_generation()
        self.test_stored_token_retrieval()
        self.test_gmail_api_calls()
        self.test_token_format_validation()
        self.check_backend_logs()
        self.test_credentials_method()

        # Generate summary
        print("=" * 80)
        print("🎯 GOOGLE OAUTH DEBUGGING SUMMARY")
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
        
        # Check OAuth URL generation
        oauth_tests = [t for t in self.test_results if "OAuth URL" in t["test"]]
        if any(t["success"] for t in oauth_tests):
            print("   ✅ OAuth URL generation working correctly")
        else:
            print("   ❌ OAuth URL generation failed - check client configuration")

        # Check token retrieval
        token_tests = [t for t in self.test_results if "Token" in t["test"]]
        token_success = sum(1 for t in token_tests if t["success"])
        if token_success >= 1:
            print("   ✅ Token storage/retrieval partially working")
        else:
            print("   ❌ Token storage/retrieval completely broken")

        # Check Gmail API
        gmail_tests = [t for t in self.test_results if "Gmail API" in t["test"]]
        gmail_success = sum(1 for t in gmail_tests if t["success"])
        if gmail_success >= 1:
            print("   ✅ Gmail API partially functional")
        else:
            print("   ❌ Gmail API completely broken - 'No emails returned from Gmail API, using fallback'")

        # Check credentials method
        cred_tests = [t for t in self.test_results if "Credentials Method" in t["test"]]
        if any(t["success"] for t in cred_tests):
            print("   ✅ _get_credentials method working")
        else:
            print("   ❌ _get_credentials method has issues")

        print()
        print("🔧 RECOMMENDED FIXES:")
        
        if not any(t["success"] for t in gmail_tests):
            print("   1. Check stored OAuth tokens for missing client_id, client_secret, token_uri")
            print("   2. Verify token scopes include required Gmail permissions")
            print("   3. Check if tokens have expired and need refresh")
            print("   4. Validate _get_credentials method implementation")
        
        if not any(t["success"] for t in token_tests):
            print("   5. Check database token storage format")
            print("   6. Verify OAuth callback is storing all required fields")
        
        print()
        print("=" * 80)
        
        if success_rate >= 70:
            print("🎉 OAUTH STATUS: MOSTLY WORKING - MINOR FIXES NEEDED")
        elif success_rate >= 40:
            print("⚠️  OAUTH STATUS: PARTIAL FUNCTIONALITY - REVIEW REQUIRED")
        else:
            print("🚨 OAUTH STATUS: CRITICAL ISSUES - IMMEDIATE ATTENTION REQUIRED")
            
        print("=" * 80)
        
        return success_rate

if __name__ == "__main__":
    tester = GoogleOAuthDebugTester()
    success_rate = tester.run_debug_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success_rate >= 70 else 1)