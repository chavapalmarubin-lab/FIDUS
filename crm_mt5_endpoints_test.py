#!/usr/bin/env python3
"""
FIDUS CRM Client MT5 Endpoints Testing
Testing specific CRM client MT5 endpoints that are causing 500 errors.

Target Endpoints:
1. /api/crm/mt5/client/{client_id}/account 
2. /api/crm/mt5/client/{client_id}/positions
3. /api/crm/mt5/client/{client_id}/history

Test Client: Salvador Palma (client_003)
Admin Credentials: admin/password123
"""

import requests
import json
import time
import sys
from datetime import datetime, timezone

# Backend URL - Using the URL from frontend/.env
BACKEND_URL = "https://investor-dash-1.preview.emergentagent.com/api"

# Test Configuration
TEST_CLIENT_ID = "client_003"  # Salvador Palma
ADMIN_CREDENTIALS = {
    "username": "admin",
    "password": "password123",
    "user_type": "admin"
}

class CRMClientMT5Tester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_test(self, test_name, success, details="", error_msg="", response_data=None):
        """Log test result with detailed information"""
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
            "response_data": response_data,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if error_msg:
            print(f"   Error: {error_msg}")
        if response_data and not success:
            print(f"   Response: {json.dumps(response_data, indent=2)}")
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
        print("🔐 Authenticating as admin...")
        
        response = self.make_request("POST", "/auth/login", ADMIN_CREDENTIALS)
        if response and response.status_code == 200:
            try:
                data = response.json()
                if data.get("token") and data.get("type") == "admin":
                    self.admin_token = data["token"]
                    self.log_test("Admin Authentication", True, 
                                f"Admin: {data.get('name')}, Type: {data.get('type')}")
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

    def test_crm_mt5_client_account(self):
        """Test /api/crm/mt5/client/{client_id}/account endpoint"""
        print(f"🔍 Testing CRM MT5 Client Account endpoint for {TEST_CLIENT_ID}...")
        
        if not self.admin_token:
            self.log_test("CRM MT5 Client Account", False, "No admin token available")
            return

        endpoint = f"/crm/mt5/client/{TEST_CLIENT_ID}/account"
        response = self.make_request("GET", endpoint, auth_token=self.admin_token)
        
        if response:
            try:
                data = response.json()
                
                if response.status_code == 200:
                    if data.get("success") and data.get("account"):
                        account = data["account"]
                        self.log_test("CRM MT5 Client Account", True, 
                                    f"Account found - Login: {account.get('mt5_login')}, "
                                    f"Broker: {account.get('broker_name')}, "
                                    f"Server: {account.get('mt5_server')}")
                    else:
                        self.log_test("CRM MT5 Client Account", False, 
                                    "Missing success flag or account data", 
                                    response_data=data)
                elif response.status_code == 404:
                    self.log_test("CRM MT5 Client Account", True, 
                                "No MT5 accounts found for client (expected for some clients)", 
                                response_data=data)
                elif response.status_code == 500:
                    self.log_test("CRM MT5 Client Account", False, 
                                "500 Internal Server Error - This is the reported issue!", 
                                error_msg=data.get("detail", "Unknown server error"),
                                response_data=data)
                else:
                    self.log_test("CRM MT5 Client Account", False, 
                                f"Unexpected status code: {response.status_code}",
                                response_data=data)
            except json.JSONDecodeError:
                self.log_test("CRM MT5 Client Account", False, 
                            f"Invalid JSON response (HTTP {response.status_code})",
                            error_msg=response.text[:200])
        else:
            self.log_test("CRM MT5 Client Account", False, "No response from server")

    def test_crm_mt5_client_positions(self):
        """Test /api/crm/mt5/client/{client_id}/positions endpoint"""
        print(f"🔍 Testing CRM MT5 Client Positions endpoint for {TEST_CLIENT_ID}...")
        
        if not self.admin_token:
            self.log_test("CRM MT5 Client Positions", False, "No admin token available")
            return

        endpoint = f"/crm/mt5/client/{TEST_CLIENT_ID}/positions"
        response = self.make_request("GET", endpoint, auth_token=self.admin_token)
        
        if response:
            try:
                data = response.json()
                
                if response.status_code == 200:
                    if data.get("success") and "positions" in data and "summary" in data:
                        summary = data["summary"]
                        self.log_test("CRM MT5 Client Positions", True, 
                                    f"Positions retrieved - Total: {summary.get('total_positions')}, "
                                    f"Profit: ${summary.get('total_profit')}, "
                                    f"Volume: {summary.get('total_volume')}")
                    else:
                        self.log_test("CRM MT5 Client Positions", False, 
                                    "Missing success flag or positions/summary data", 
                                    response_data=data)
                elif response.status_code == 500:
                    self.log_test("CRM MT5 Client Positions", False, 
                                "500 Internal Server Error - This is the reported issue!", 
                                error_msg=data.get("detail", "Unknown server error"),
                                response_data=data)
                else:
                    self.log_test("CRM MT5 Client Positions", False, 
                                f"Unexpected status code: {response.status_code}",
                                response_data=data)
            except json.JSONDecodeError:
                self.log_test("CRM MT5 Client Positions", False, 
                            f"Invalid JSON response (HTTP {response.status_code})",
                            error_msg=response.text[:200])
        else:
            self.log_test("CRM MT5 Client Positions", False, "No response from server")

    def test_crm_mt5_client_history(self):
        """Test /api/crm/mt5/client/{client_id}/history endpoint"""
        print(f"🔍 Testing CRM MT5 Client History endpoint for {TEST_CLIENT_ID}...")
        
        if not self.admin_token:
            self.log_test("CRM MT5 Client History", False, "No admin token available")
            return

        endpoint = f"/crm/mt5/client/{TEST_CLIENT_ID}/history"
        response = self.make_request("GET", endpoint, auth_token=self.admin_token)
        
        if response:
            try:
                data = response.json()
                
                if response.status_code == 200:
                    if "trades" in data and "summary" in data:
                        summary = data["summary"]
                        self.log_test("CRM MT5 Client History", True, 
                                    f"History retrieved - Total trades: {summary.get('total_trades')}, "
                                    f"Total profit: ${summary.get('total_profit')}, "
                                    f"Win rate: {summary.get('win_rate')}%")
                    else:
                        self.log_test("CRM MT5 Client History", False, 
                                    "Missing trades or summary data", 
                                    response_data=data)
                elif response.status_code == 500:
                    self.log_test("CRM MT5 Client History", False, 
                                "500 Internal Server Error - This is the reported issue!", 
                                error_msg=data.get("detail", "Unknown server error"),
                                response_data=data)
                else:
                    self.log_test("CRM MT5 Client History", False, 
                                f"Unexpected status code: {response.status_code}",
                                response_data=data)
            except json.JSONDecodeError:
                self.log_test("CRM MT5 Client History", False, 
                            f"Invalid JSON response (HTTP {response.status_code})",
                            error_msg=response.text[:200])
        else:
            self.log_test("CRM MT5 Client History", False, "No response from server")

    def check_backend_logs(self):
        """Check backend logs for MT5 service initialization issues"""
        print("🔍 Checking for MT5 service initialization issues...")
        
        # Test MT5 status endpoint to see if service is initialized
        response = self.make_request("GET", "/mt5/status", auth_token=self.admin_token)
        
        if response:
            try:
                data = response.json()
                if response.status_code == 200:
                    self.log_test("MT5 Service Status", True, 
                                f"MT5 service status: {data.get('status', 'unknown')}")
                else:
                    self.log_test("MT5 Service Status", False, 
                                f"MT5 status endpoint error (HTTP {response.status_code})",
                                response_data=data)
            except json.JSONDecodeError:
                self.log_test("MT5 Service Status", False, 
                            f"Invalid JSON from MT5 status (HTTP {response.status_code})")
        else:
            self.log_test("MT5 Service Status", False, "No response from MT5 status endpoint")

    def test_authentication_requirements(self):
        """Test authentication requirements for CRM MT5 endpoints"""
        print("🔍 Testing authentication requirements...")
        
        # Test without authentication
        endpoint = f"/crm/mt5/client/{TEST_CLIENT_ID}/account"
        response = self.make_request("GET", endpoint)
        
        if response and response.status_code == 401:
            self.log_test("Authentication Required", True, 
                        "Endpoints correctly require authentication")
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("Authentication Required", False, 
                        f"Expected 401, got HTTP {status_code}")

    def run_comprehensive_test(self):
        """Run all CRM client MT5 endpoint tests"""
        print("🚀 FIDUS CRM Client MT5 Endpoints Testing")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Client: Salvador Palma ({TEST_CLIENT_ID})")
        print(f"Test Started: {datetime.now(timezone.utc).isoformat()}")
        print("=" * 60)
        print()

        # Authenticate first
        if not self.authenticate_admin():
            print("❌ Cannot proceed without admin authentication")
            return 0

        # Run authentication tests
        self.test_authentication_requirements()
        
        # Check MT5 service status
        self.check_backend_logs()
        
        # Test the three CRM client MT5 endpoints
        self.test_crm_mt5_client_account()
        self.test_crm_mt5_client_positions()
        self.test_crm_mt5_client_history()

        # Generate summary
        print("=" * 60)
        print("🎯 CRM CLIENT MT5 ENDPOINTS TEST SUMMARY")
        print("=" * 60)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()

        # Show failed tests with details
        failed_tests = [t for t in self.test_results if not t["success"]]
        if failed_tests:
            print("❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"   • {test['test']}: {test['error']}")
                if test.get('response_data'):
                    print(f"     Response: {json.dumps(test['response_data'], indent=6)}")
            print()

        # Show critical findings
        print("🔍 CRITICAL FINDINGS:")
        
        # Check for 500 errors specifically
        server_errors = [t for t in self.test_results if "500 Internal Server Error" in t.get('error', '')]
        if server_errors:
            print(f"   🚨 Found {len(server_errors)} endpoints with 500 errors:")
            for test in server_errors:
                print(f"      - {test['test']}")
        else:
            print("   ✅ No 500 errors detected in CRM client MT5 endpoints")

        # Check MT5 service initialization
        mt5_status_test = next((t for t in self.test_results if "MT5 Service Status" in t['test']), None)
        if mt5_status_test and mt5_status_test['success']:
            print("   ✅ MT5 service appears to be initialized")
        else:
            print("   ⚠️  MT5 service initialization may have issues")

        # Check authentication
        auth_test = next((t for t in self.test_results if "Authentication Required" in t['test']), None)
        if auth_test and auth_test['success']:
            print("   ✅ Authentication requirements working correctly")
        else:
            print("   ⚠️  Authentication requirements may have issues")

        print()
        print("=" * 60)
        
        if success_rate >= 80:
            print("🎉 STATUS: CRM CLIENT MT5 ENDPOINTS WORKING CORRECTLY")
        elif success_rate >= 60:
            print("⚠️  STATUS: SOME ISSUES DETECTED - REVIEW REQUIRED")
        else:
            print("🚨 STATUS: CRITICAL ISSUES - IMMEDIATE ATTENTION REQUIRED")
            
        print("=" * 60)
        
        return success_rate

if __name__ == "__main__":
    tester = CRMClientMT5Tester()
    success_rate = tester.run_comprehensive_test()
    
    # Exit with appropriate code
    sys.exit(0 if success_rate >= 80 else 1)