#!/usr/bin/env python3
"""
Gmail API Debug Test - OAuth Connection Issue Investigation

Context: User completed OAuth flow successfully - UI shows "connected" and console shows 
"3/4 services connected" with 75% health status. However, Gmail API calls are still failing 
with "No emails returned from Gmail API, using fallback".

Debug Areas:
1. Test /api/admin/gmail/messages endpoint that should work since OAuth is connected
2. Check what specific error occurs when calling Gmail API
3. Look at backend logs for Gmail API errors
4. Test /admin/google/individual-status to see what tokens are actually stored
5. Verify if all required fields (access_token, client_id, client_secret, scopes) are present
6. Check if tokens have correct scopes for Gmail access
7. Test token usage in credentials

Admin Credentials: admin/password123
Backend URL: Use REACT_APP_BACKEND_URL from frontend/.env
"""

import requests
import json
import time
import sys
from datetime import datetime, timezone

# Backend URL from frontend/.env
BACKEND_URL = "https://trading-platform-76.preview.emergentagent.com/api"

# Admin credentials
ADMIN_CREDENTIALS = {
    "username": "admin",
    "password": "password123", 
    "user_type": "admin"
}

class GmailAPIDebugger:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.debug_results = []
        
    def log_debug(self, test_name, success, details="", error_msg="", response_data=None):
        """Log debug result with detailed information"""
        status = "✅ SUCCESS" if success else "❌ FAILED"
        
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "error": error_msg,
            "response_data": response_data,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        self.debug_results.append(result)
        
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if error_msg:
            print(f"   Error: {error_msg}")
        if response_data and isinstance(response_data, dict):
            print(f"   Response: {json.dumps(response_data, indent=2)[:500]}...")
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
                                 "Missing token or incorrect type", response_data=data)
                    return False
            except json.JSONDecodeError as e:
                self.log_debug("Admin Authentication", False, 
                             f"Invalid JSON response: {e}")
                return False
        else:
            status_code = response.status_code if response else "No response"
            self.log_debug("Admin Authentication", False, f"HTTP {status_code}")
            return False

    def test_gmail_api_endpoint(self):
        """Test the specific Gmail API endpoint that should work after OAuth"""
        print("📧 Testing Gmail API endpoint that should work after OAuth...")
        
        if not self.admin_token:
            self.log_debug("Gmail API Endpoint Test", False, "No admin token available")
            return
        
        # Test /api/admin/gmail/messages endpoint
        response = self.make_request("GET", "/admin/gmail/messages", auth_token=self.admin_token)
        
        if response:
            try:
                data = response.json()
                
                if response.status_code == 200:
                    if "messages" in data and len(data["messages"]) > 0:
                        self.log_debug("Gmail API - /admin/gmail/messages", True,
                                     f"Retrieved {len(data['messages'])} Gmail messages",
                                     response_data=data)
                    elif "auth_required" in data and data["auth_required"]:
                        self.log_debug("Gmail API - /admin/gmail/messages", False,
                                     "OAuth authentication required - tokens not working",
                                     f"Auth required: {data.get('message', 'No message')}",
                                     response_data=data)
                    else:
                        self.log_debug("Gmail API - /admin/gmail/messages", False,
                                     "Unexpected response format - no messages or auth_required",
                                     response_data=data)
                else:
                    self.log_debug("Gmail API - /admin/gmail/messages", False,
                                 f"HTTP {response.status_code}",
                                 f"Error response: {data.get('detail', 'No detail')}",
                                 response_data=data)
                    
            except json.JSONDecodeError as e:
                self.log_debug("Gmail API - /admin/gmail/messages", False,
                             f"Invalid JSON response: {e}",
                             f"Raw response: {response.text[:200]}")
        else:
            self.log_debug("Gmail API - /admin/gmail/messages", False, "No response received")

    def test_individual_oauth_status(self):
        """Test individual Google OAuth status to see stored tokens"""
        print("🔍 Testing individual Google OAuth status...")
        
        if not self.admin_token:
            self.log_debug("Individual OAuth Status Test", False, "No admin token available")
            return
        
        # Test /admin/google/individual-status endpoint
        response = self.make_request("GET", "/admin/google/individual-status", 
                                   auth_token=self.admin_token)
        
        if response:
            try:
                data = response.json()
                
                if response.status_code == 200:
                    if data.get("connected"):
                        # Check token details
                        tokens = data.get("tokens", {})
                        required_fields = ["access_token", "client_id", "client_secret", "scopes"]
                        missing_fields = [field for field in required_fields if not tokens.get(field)]
                        
                        if not missing_fields:
                            scopes = tokens.get("scopes", "").split() if isinstance(tokens.get("scopes"), str) else tokens.get("scopes", [])
                            gmail_scopes = [s for s in scopes if "gmail" in s.lower()]
                            
                            self.log_debug("Individual OAuth Status - Token Verification", True,
                                         f"All required fields present. Gmail scopes: {gmail_scopes}",
                                         response_data={
                                             "connected": data.get("connected"),
                                             "google_email": data.get("google_email"),
                                             "scopes": scopes,
                                             "token_fields": list(tokens.keys())
                                         })
                        else:
                            self.log_debug("Individual OAuth Status - Token Verification", False,
                                         f"Missing required token fields: {missing_fields}",
                                         response_data=data)
                    else:
                        self.log_debug("Individual OAuth Status - Connection Status", False,
                                     "OAuth not connected - no tokens stored",
                                     response_data=data)
                else:
                    self.log_debug("Individual OAuth Status - Endpoint Access", False,
                                 f"HTTP {response.status_code}",
                                 f"Error: {data.get('detail', 'No detail')}",
                                 response_data=data)
                    
            except json.JSONDecodeError as e:
                self.log_debug("Individual OAuth Status - Response Parsing", False,
                             f"Invalid JSON response: {e}",
                             f"Raw response: {response.text[:200]}")
        else:
            self.log_debug("Individual OAuth Status - Network", False, "No response received")

    def test_google_connection_monitor(self):
        """Test Google connection monitor to see overall status"""
        print("📊 Testing Google connection monitor...")
        
        if not self.admin_token:
            self.log_debug("Google Connection Monitor Test", False, "No admin token available")
            return
        
        # Test /google/connection/test-all endpoint
        response = self.make_request("GET", "/google/connection/test-all", 
                                   auth_token=self.admin_token)
        
        if response:
            try:
                data = response.json()
                
                if response.status_code == 200:
                    overall_status = data.get("overall_status")
                    services = data.get("services", {})
                    gmail_status = services.get("gmail", {})
                    
                    connected_services = sum(1 for svc in services.values() 
                                           if svc.get("status") == "connected")
                    total_services = len(services)
                    
                    self.log_debug("Google Connection Monitor - Overall Status", True,
                                 f"Overall: {overall_status}, Connected: {connected_services}/{total_services}",
                                 f"Gmail status: {gmail_status.get('status', 'unknown')}",
                                 response_data={
                                     "overall_status": overall_status,
                                     "gmail_service": gmail_status,
                                     "connected_count": connected_services,
                                     "total_services": total_services
                                 })
                else:
                    self.log_debug("Google Connection Monitor - Endpoint Access", False,
                                 f"HTTP {response.status_code}",
                                 f"Error: {data.get('detail', 'No detail')}",
                                 response_data=data)
                    
            except json.JSONDecodeError as e:
                self.log_debug("Google Connection Monitor - Response Parsing", False,
                             f"Invalid JSON response: {e}",
                             f"Raw response: {response.text[:200]}")
        else:
            self.log_debug("Google Connection Monitor - Network", False, "No response received")

    def test_gmail_real_messages_endpoint(self):
        """Test the real Gmail messages endpoint"""
        print("📨 Testing real Gmail messages endpoint...")
        
        if not self.admin_token:
            self.log_debug("Gmail Real Messages Test", False, "No admin token available")
            return
        
        # Test /google/gmail/real-messages endpoint
        response = self.make_request("GET", "/google/gmail/real-messages", 
                                   auth_token=self.admin_token)
        
        if response:
            try:
                data = response.json()
                
                if response.status_code == 200:
                    if "messages" in data and len(data["messages"]) > 0:
                        self.log_debug("Gmail Real Messages - Success", True,
                                     f"Retrieved {len(data['messages'])} real Gmail messages",
                                     response_data={
                                         "message_count": len(data["messages"]),
                                         "first_message": data["messages"][0] if data["messages"] else None
                                     })
                    elif "auth_required" in data and data["auth_required"]:
                        self.log_debug("Gmail Real Messages - Auth Required", False,
                                     "Google authentication required for real messages",
                                     f"Message: {data.get('message', 'No message')}",
                                     response_data=data)
                    else:
                        self.log_debug("Gmail Real Messages - Unexpected Format", False,
                                     "Unexpected response format",
                                     response_data=data)
                else:
                    self.log_debug("Gmail Real Messages - HTTP Error", False,
                                 f"HTTP {response.status_code}",
                                 f"Error: {data.get('detail', 'No detail')}",
                                 response_data=data)
                    
            except json.JSONDecodeError as e:
                self.log_debug("Gmail Real Messages - JSON Error", False,
                             f"Invalid JSON response: {e}",
                             f"Raw response: {response.text[:200]}")
        else:
            self.log_debug("Gmail Real Messages - Network Error", False, "No response received")

    def check_backend_logs(self):
        """Check backend logs for Gmail API errors"""
        print("📋 Checking backend logs for Gmail API errors...")
        
        try:
            # Try to get backend logs using supervisor
            import subprocess
            
            # Check supervisor backend logs
            result = subprocess.run(
                ["tail", "-n", "50", "/var/log/supervisor/backend.err.log"],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0 and result.stdout:
                gmail_errors = []
                for line in result.stdout.split('\n'):
                    if any(keyword in line.lower() for keyword in ['gmail', 'google', 'oauth', 'credential', 'token']):
                        gmail_errors.append(line.strip())
                
                if gmail_errors:
                    self.log_debug("Backend Logs - Gmail Errors", True,
                                 f"Found {len(gmail_errors)} Gmail-related log entries",
                                 response_data={"gmail_log_entries": gmail_errors[-10:]})  # Last 10 entries
                else:
                    self.log_debug("Backend Logs - No Gmail Errors", True,
                                 "No Gmail-related errors found in recent logs")
            else:
                self.log_debug("Backend Logs - Access Failed", False,
                             "Could not access backend error logs",
                             f"Return code: {result.returncode}")
                
        except subprocess.TimeoutExpired:
            self.log_debug("Backend Logs - Timeout", False, "Log check timed out")
        except Exception as e:
            self.log_debug("Backend Logs - Exception", False, f"Error checking logs: {e}")

    def test_oauth_url_generation(self):
        """Test OAuth URL generation to verify OAuth system is working"""
        print("🔗 Testing OAuth URL generation...")
        
        if not self.admin_token:
            self.log_debug("OAuth URL Generation Test", False, "No admin token available")
            return
        
        # Test /auth/google/url endpoint
        response = self.make_request("GET", "/auth/google/url", auth_token=self.admin_token)
        
        if response:
            try:
                data = response.json()
                
                if response.status_code == 200:
                    auth_url = data.get("auth_url", "")
                    if "accounts.google.com" in auth_url and "oauth2" in auth_url:
                        # Check if URL contains required parameters
                        required_params = ["client_id", "redirect_uri", "response_type", "scope"]
                        missing_params = [param for param in required_params if param not in auth_url]
                        
                        if not missing_params:
                            self.log_debug("OAuth URL Generation - Success", True,
                                         "Valid Google OAuth URL generated with all required parameters",
                                         response_data={"auth_url": auth_url[:100] + "..."})
                        else:
                            self.log_debug("OAuth URL Generation - Missing Parameters", False,
                                         f"OAuth URL missing parameters: {missing_params}",
                                         response_data=data)
                    else:
                        self.log_debug("OAuth URL Generation - Invalid URL", False,
                                     "Generated URL is not a valid Google OAuth URL",
                                     response_data=data)
                else:
                    self.log_debug("OAuth URL Generation - HTTP Error", False,
                                 f"HTTP {response.status_code}",
                                 f"Error: {data.get('detail', 'No detail')}",
                                 response_data=data)
                    
            except json.JSONDecodeError as e:
                self.log_debug("OAuth URL Generation - JSON Error", False,
                             f"Invalid JSON response: {e}",
                             f"Raw response: {response.text[:200]}")
        else:
            self.log_debug("OAuth URL Generation - Network Error", False, "No response received")

    def run_gmail_debug_investigation(self):
        """Run comprehensive Gmail API debugging investigation"""
        print("🚀 Gmail API Debug Investigation - OAuth Connection Issue")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Investigation Started: {datetime.now(timezone.utc).isoformat()}")
        print("=" * 80)
        print()

        # Step 1: Authenticate as admin
        if not self.authenticate_admin():
            print("🚨 CRITICAL: Cannot proceed without admin authentication")
            return False

        # Step 2: Test Gmail API endpoint that should work
        self.test_gmail_api_endpoint()

        # Step 3: Check individual OAuth status and stored tokens
        self.test_individual_oauth_status()

        # Step 4: Check Google connection monitor
        self.test_google_connection_monitor()

        # Step 5: Test real Gmail messages endpoint
        self.test_gmail_real_messages_endpoint()

        # Step 6: Test OAuth URL generation (verify OAuth system works)
        self.test_oauth_url_generation()

        # Step 7: Check backend logs for errors
        self.check_backend_logs()

        # Generate investigation summary
        print("=" * 80)
        print("🔍 GMAIL API DEBUG INVESTIGATION SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.debug_results)
        successful_tests = sum(1 for result in self.debug_results if result["success"])
        
        print(f"Total Debug Tests: {total_tests}")
        print(f"Successful: {successful_tests}")
        print(f"Failed: {total_tests - successful_tests}")
        print()

        # Analyze findings
        print("🎯 KEY FINDINGS:")
        
        # Check authentication
        auth_result = next((r for r in self.debug_results if "Authentication" in r["test"]), None)
        if auth_result and auth_result["success"]:
            print("   ✅ Admin authentication working")
        else:
            print("   ❌ Admin authentication failed")

        # Check OAuth status
        oauth_results = [r for r in self.debug_results if "OAuth" in r["test"]]
        oauth_working = any(r["success"] for r in oauth_results)
        if oauth_working:
            print("   ✅ OAuth system operational")
        else:
            print("   ❌ OAuth system issues detected")

        # Check Gmail API access
        gmail_results = [r for r in self.debug_results if "Gmail" in r["test"]]
        gmail_working = any(r["success"] for r in gmail_results)
        if gmail_working:
            print("   ✅ Gmail API accessible")
        else:
            print("   ❌ Gmail API access blocked")

        # Check token storage
        token_results = [r for r in self.debug_results if "Token" in r["test"] or "individual" in r["test"].lower()]
        tokens_valid = any(r["success"] for r in token_results)
        if tokens_valid:
            print("   ✅ OAuth tokens properly stored")
        else:
            print("   ❌ OAuth token storage issues")

        print()
        print("🚨 ROOT CAUSE ANALYSIS:")
        
        # Analyze the specific issue pattern
        failed_tests = [r for r in self.debug_results if not r["success"]]
        
        if any("auth_required" in str(r.get("response_data", {})) for r in failed_tests):
            print("   🎯 ISSUE IDENTIFIED: OAuth tokens not working despite connection status")
            print("   📋 LIKELY CAUSES:")
            print("      • Stored tokens missing required scopes for Gmail")
            print("      • Token format issues preventing Gmail API calls") 
            print("      • Google API credentials object creation failing")
            print("      • Token expiration or refresh issues")
        elif any("404" in str(r.get("error", "")) for r in failed_tests):
            print("   🎯 ISSUE IDENTIFIED: Missing Gmail API endpoints")
            print("   📋 LIKELY CAUSES:")
            print("      • /api/admin/gmail/messages endpoint not implemented")
            print("      • Routing configuration issues")
        elif not oauth_working:
            print("   🎯 ISSUE IDENTIFIED: OAuth system not functional")
            print("   📋 LIKELY CAUSES:")
            print("      • OAuth URL generation failing")
            print("      • OAuth callback processing broken")
        else:
            print("   🎯 ISSUE PATTERN: Mixed results - partial functionality")

        print()
        print("💡 RECOMMENDED NEXT STEPS:")
        print("   1. Check if OAuth tokens have correct Gmail scopes")
        print("   2. Verify _get_credentials method implementation")
        print("   3. Test token refresh mechanism")
        print("   4. Validate Google API credentials object creation")
        print("   5. Check backend logs for specific Gmail API errors")
        
        print("=" * 80)
        
        return successful_tests >= (total_tests * 0.5)  # 50% success threshold

if __name__ == "__main__":
    debugger = GmailAPIDebugger()
    success = debugger.run_gmail_debug_investigation()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)