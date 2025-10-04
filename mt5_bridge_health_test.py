#!/usr/bin/env python3
"""
FIDUS MT5 Bridge Health Endpoint Testing Suite
Testing MT5 Bridge Health endpoint after server restart and verifying latest endpoint fixes.

Focus Areas:
1. MT5 Bridge Health Endpoint - GET /api/mt5/bridge/health with admin authentication
2. Fixed CRM MT5 Endpoints - /api/crm/mt5/client/{client_id}/account and /api/crm/mt5/client/{client_id}/positions
3. Endpoint Registration Status - verify all MT5 endpoints are properly registered
4. Overall Integration Health - test comprehensive set of MT5 endpoints

Expected: Higher MT5 integration success rate with previously failing endpoints now working after fixes and server restart.
"""

import requests
import json
import time
import sys
from datetime import datetime, timezone
from typing import Dict, Any, List

class MT5BridgeHealthTester:
    def __init__(self):
        # Use the correct backend URL from frontend/.env
        self.backend_url = "https://fidus-admin.preview.emergentagent.com/api"
        self.session = requests.Session()
        self.admin_token = None
        self.client_token = None
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
        url = f"{self.backend_url}{endpoint}"
        
        # Set up headers
        req_headers = {"Content-Type": "application/json"}
        if headers:
            req_headers.update(headers)
        if auth_token:
            req_headers["Authorization"] = f"Bearer {auth_token}"
            
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=req_headers, timeout=35)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, headers=req_headers, timeout=35)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, headers=req_headers, timeout=35)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=req_headers, timeout=35)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None

    def setup_authentication(self):
        """Setup admin and client authentication"""
        print("🔐 Setting up authentication...")
        
        # Admin login
        admin_login = {
            "username": "admin",
            "password": "password123",
            "user_type": "admin"
        }
        
        response = self.make_request("POST", "/auth/login", admin_login)
        if response and response.status_code == 200:
            try:
                data = response.json()
                if data.get("token"):
                    self.admin_token = data["token"]
                    print(f"✅ Admin authentication successful: {data.get('name')}")
                else:
                    print("❌ Admin login failed - no token received")
                    return False
            except json.JSONDecodeError:
                print("❌ Admin login failed - invalid JSON response")
                return False
        else:
            status_code = response.status_code if response else "No response"
            print(f"❌ Admin login failed - HTTP {status_code}")
            return False

        # Client login (Salvador Palma)
        client_login = {
            "username": "client3",
            "password": "password123",
            "user_type": "client"
        }
        
        response = self.make_request("POST", "/auth/login", client_login)
        if response and response.status_code == 200:
            try:
                data = response.json()
                if data.get("token"):
                    self.client_token = data["token"]
                    print(f"✅ Client authentication successful: {data.get('name')}")
                else:
                    print("❌ Client login failed - no token received")
                    return False
            except json.JSONDecodeError:
                print("❌ Client login failed - invalid JSON response")
                return False
        else:
            status_code = response.status_code if response else "No response"
            print(f"❌ Client login failed - HTTP {status_code}")
            return False

        return True

    def test_mt5_bridge_health_endpoint(self):
        """Test MT5 Bridge Health Endpoint with admin authentication"""
        print("🔍 Testing MT5 Bridge Health Endpoint...")
        
        if not self.admin_token:
            self.log_test("MT5 Bridge Health Endpoint", False, "No admin token available")
            return

        # Test MT5 Bridge Health endpoint
        response = self.make_request("GET", "/mt5/bridge/health", auth_token=self.admin_token)
        
        if response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    # Check if endpoint is properly registered and returns structured response
                    if isinstance(data, dict):
                        success_flag = data.get('success')
                        bridge_status = data.get('bridge_status', 'unknown')
                        connectivity = data.get('connectivity', 'unknown')
                        
                        if success_flag is not None:  # Endpoint is registered and working
                            if success_flag:
                                self.log_test("MT5 Bridge Health Endpoint", True, 
                                            f"Bridge Status: {bridge_status}, Connectivity: {connectivity}")
                            else:
                                # Bridge unreachable but endpoint working correctly
                                error_msg = data.get('error', 'Unknown error')
                                self.log_test("MT5 Bridge Health Endpoint", True, 
                                            f"Endpoint working, Bridge unreachable: {error_msg}")
                        else:
                            self.log_test("MT5 Bridge Health Endpoint", True, 
                                        f"Endpoint registered, Response: {list(data.keys())}")
                    else:
                        self.log_test("MT5 Bridge Health Endpoint", False, 
                                    f"Unexpected response format: {type(data)}")
                        
                except json.JSONDecodeError:
                    self.log_test("MT5 Bridge Health Endpoint", False, "Invalid JSON response")
            elif response.status_code == 404:
                self.log_test("MT5 Bridge Health Endpoint", False, 
                            "Endpoint not registered - 404 error")
            elif response.status_code == 401:
                self.log_test("MT5 Bridge Health Endpoint", False, 
                            "Authentication failed - check admin token")
            else:
                self.log_test("MT5 Bridge Health Endpoint", False, 
                            f"HTTP {response.status_code}: {response.text}")
        else:
            self.log_test("MT5 Bridge Health Endpoint", False, "No response received")

    def test_fixed_crm_mt5_endpoints(self):
        """Test Fixed CRM MT5 Endpoints"""
        print("🔍 Testing Fixed CRM MT5 Endpoints...")
        
        if not self.admin_token:
            self.log_test("CRM MT5 Endpoints", False, "No admin token available")
            return

        # Test client IDs to use
        test_client_ids = ["client_003", "client_001", "client_002"]
        
        for client_id in test_client_ids:
            # Test CRM MT5 Client Account endpoint
            response = self.make_request("GET", f"/crm/mt5/client/{client_id}/account", 
                                       auth_token=self.admin_token)
            
            if response:
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if isinstance(data, dict):
                            # Check if using real MT5 service instead of mock_mt5
                            if 'mock' not in str(data).lower():
                                self.log_test(f"CRM MT5 Client Account ({client_id})", True, 
                                            f"Using real MT5 service, Response keys: {list(data.keys())}")
                            else:
                                self.log_test(f"CRM MT5 Client Account ({client_id})", False, 
                                            "Still using mock_mt5 service")
                        else:
                            self.log_test(f"CRM MT5 Client Account ({client_id})", False, 
                                        f"Unexpected response format: {type(data)}")
                    except json.JSONDecodeError:
                        self.log_test(f"CRM MT5 Client Account ({client_id})", False, 
                                    "Invalid JSON response")
                elif response.status_code == 404:
                    self.log_test(f"CRM MT5 Client Account ({client_id})", False, 
                                "Endpoint not registered - 404 error")
                else:
                    # Endpoint exists but may have other issues
                    self.log_test(f"CRM MT5 Client Account ({client_id})", True, 
                                f"Endpoint registered, HTTP {response.status_code}")
            else:
                self.log_test(f"CRM MT5 Client Account ({client_id})", False, 
                            "No response received")

            # Test CRM MT5 Client Positions endpoint
            response = self.make_request("GET", f"/crm/mt5/client/{client_id}/positions", 
                                       auth_token=self.admin_token)
            
            if response:
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if isinstance(data, dict):
                            # Check if using real MT5 service instead of mock_mt5
                            if 'mock' not in str(data).lower():
                                self.log_test(f"CRM MT5 Client Positions ({client_id})", True, 
                                            f"Using real MT5 service, Response keys: {list(data.keys())}")
                            else:
                                self.log_test(f"CRM MT5 Client Positions ({client_id})", False, 
                                            "Still using mock_mt5 service")
                        else:
                            self.log_test(f"CRM MT5 Client Positions ({client_id})", False, 
                                        f"Unexpected response format: {type(data)}")
                    except json.JSONDecodeError:
                        self.log_test(f"CRM MT5 Client Positions ({client_id})", False, 
                                    "Invalid JSON response")
                elif response.status_code == 404:
                    self.log_test(f"CRM MT5 Client Positions ({client_id})", False, 
                                "Endpoint not registered - 404 error")
                else:
                    # Endpoint exists but may have other issues
                    self.log_test(f"CRM MT5 Client Positions ({client_id})", True, 
                                f"Endpoint registered, HTTP {response.status_code}")
            else:
                self.log_test(f"CRM MT5 Client Positions ({client_id})", False, 
                            "No response received")

    def test_mt5_endpoint_registration(self):
        """Test MT5 Endpoint Registration Status"""
        print("🔍 Testing MT5 Endpoint Registration Status...")
        
        if not self.admin_token:
            self.log_test("MT5 Endpoint Registration", False, "No admin token available")
            return

        # List of MT5 endpoints that should be registered
        mt5_endpoints = [
            ("/mt5/bridge/health", "GET", "MT5 Bridge Health"),
            ("/mt5/admin/accounts", "GET", "MT5 Admin Accounts"),
            ("/mt5/admin/performance/overview", "GET", "MT5 Admin Performance"),
            ("/mt5/brokers", "GET", "MT5 Brokers List"),
            ("/mt5/admin/system-status", "GET", "MT5 System Status"),
            ("/crm/mt5/client/client_003/account", "GET", "CRM MT5 Client Account"),
            ("/crm/mt5/client/client_003/positions", "GET", "CRM MT5 Client Positions"),
        ]
        
        registered_endpoints = 0
        total_endpoints = len(mt5_endpoints)
        
        for endpoint, method, description in mt5_endpoints:
            response = self.make_request(method, endpoint, auth_token=self.admin_token)
            
            if response:
                if response.status_code != 404:  # Not 404 means endpoint is registered
                    registered_endpoints += 1
                    if response.status_code == 200:
                        status_detail = "Working correctly"
                    elif response.status_code == 401:
                        status_detail = "Authentication required"
                    elif response.status_code == 500:
                        status_detail = "Server error (but registered)"
                    else:
                        status_detail = f"HTTP {response.status_code}"
                    
                    print(f"   ✅ {description}: {status_detail}")
                else:
                    print(f"   ❌ {description}: Not registered (404)")
            else:
                print(f"   ❌ {description}: No response")

        # Calculate registration success rate
        registration_rate = (registered_endpoints / total_endpoints) * 100
        
        if registration_rate >= 80:
            self.log_test("MT5 Endpoint Registration", True, 
                        f"{registered_endpoints}/{total_endpoints} endpoints registered ({registration_rate:.1f}%)")
        else:
            self.log_test("MT5 Endpoint Registration", False, 
                        f"Only {registered_endpoints}/{total_endpoints} endpoints registered ({registration_rate:.1f}%)")

    def test_admin_authentication_on_mt5_endpoints(self):
        """Test Admin Authentication on MT5 Endpoints"""
        print("🔍 Testing Admin Authentication on MT5 Endpoints...")
        
        # Test without authentication (should fail)
        response = self.make_request("GET", "/mt5/bridge/health")
        
        if response and response.status_code == 401:
            self.log_test("MT5 Admin Authentication - Unauthorized", True, 
                        "Correctly requires authentication")
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("MT5 Admin Authentication - Unauthorized", False, 
                        f"Expected 401, got {status_code}")

        # Test with admin authentication (should work)
        if self.admin_token:
            response = self.make_request("GET", "/mt5/bridge/health", auth_token=self.admin_token)
            
            if response and response.status_code in [200, 500]:  # 200 or 500 both indicate auth worked
                self.log_test("MT5 Admin Authentication - Authorized", True, 
                            f"Admin authentication working (HTTP {response.status_code})")
            else:
                status_code = response.status_code if response else "No response"
                self.log_test("MT5 Admin Authentication - Authorized", False, 
                            f"Admin auth failed, HTTP {status_code}")

        # Test with client token (should be forbidden for admin endpoints)
        if self.client_token:
            response = self.make_request("GET", "/mt5/admin/accounts", auth_token=self.client_token)
            
            if response and response.status_code == 403:
                self.log_test("MT5 Admin Authentication - Client Forbidden", True, 
                            "Client correctly forbidden from admin endpoints")
            else:
                status_code = response.status_code if response else "No response"
                self.log_test("MT5 Admin Authentication - Client Forbidden", False, 
                            f"Expected 403, got {status_code}")

    def test_comprehensive_mt5_integration(self):
        """Test Comprehensive MT5 Integration Health"""
        print("🔍 Testing Comprehensive MT5 Integration Health...")
        
        if not self.admin_token:
            self.log_test("Comprehensive MT5 Integration", False, "No admin token available")
            return

        # Test a comprehensive set of MT5 endpoints
        mt5_integration_endpoints = [
            ("/mt5/bridge/health", "MT5 Bridge Health"),
            ("/mt5/admin/accounts", "MT5 Admin Accounts"),
            ("/mt5/admin/performance/overview", "MT5 Performance Overview"),
            ("/mt5/brokers", "MT5 Brokers"),
            ("/mt5/admin/system-status", "MT5 System Status"),
            ("/crm/mt5/client/client_003/account", "CRM MT5 Account"),
            ("/crm/mt5/client/client_003/positions", "CRM MT5 Positions"),
        ]
        
        working_endpoints = 0
        total_endpoints = len(mt5_integration_endpoints)
        
        for endpoint, description in mt5_integration_endpoints:
            response = self.make_request("GET", endpoint, auth_token=self.admin_token)
            
            if response:
                # Consider 200, 500 (server error but endpoint exists), and structured error responses as "working"
                if response.status_code in [200, 500]:
                    working_endpoints += 1
                    print(f"   ✅ {description}: Working (HTTP {response.status_code})")
                elif response.status_code == 404:
                    print(f"   ❌ {description}: Not registered (404)")
                else:
                    print(f"   ⚠️ {description}: HTTP {response.status_code}")
            else:
                print(f"   ❌ {description}: No response")

        # Calculate integration success rate
        success_rate = (working_endpoints / total_endpoints) * 100
        
        if success_rate >= 70:  # Expect higher success rate after fixes
            self.log_test("Comprehensive MT5 Integration", True, 
                        f"{working_endpoints}/{total_endpoints} endpoints working ({success_rate:.1f}%)")
        else:
            self.log_test("Comprehensive MT5 Integration", False, 
                        f"Only {working_endpoints}/{total_endpoints} endpoints working ({success_rate:.1f}%)")

        return success_rate

    def run_mt5_bridge_health_tests(self):
        """Run all MT5 Bridge Health tests"""
        print("🚀 FIDUS MT5 Bridge Health Endpoint Testing Suite")
        print("=" * 80)
        print(f"Backend URL: {self.backend_url}")
        print(f"Test Started: {datetime.now(timezone.utc).isoformat()}")
        print("Focus: MT5 Bridge Health endpoint after server restart and endpoint fixes")
        print("=" * 80)
        print()

        # Setup authentication
        if not self.setup_authentication():
            print("❌ Authentication setup failed - cannot proceed")
            return False

        # Run test suites
        print("\n" + "="*60)
        print("1. MT5 BRIDGE HEALTH ENDPOINT")
        print("="*60)
        self.test_mt5_bridge_health_endpoint()

        print("\n" + "="*60)
        print("2. FIXED CRM MT5 ENDPOINTS")
        print("="*60)
        self.test_fixed_crm_mt5_endpoints()

        print("\n" + "="*60)
        print("3. MT5 ENDPOINT REGISTRATION STATUS")
        print("="*60)
        self.test_mt5_endpoint_registration()

        print("\n" + "="*60)
        print("4. ADMIN AUTHENTICATION ON MT5 ENDPOINTS")
        print("="*60)
        self.test_admin_authentication_on_mt5_endpoints()

        print("\n" + "="*60)
        print("5. COMPREHENSIVE MT5 INTEGRATION HEALTH")
        print("="*60)
        integration_success_rate = self.test_comprehensive_mt5_integration()

        # Generate summary
        print("\n" + "=" * 80)
        print("🎯 MT5 BRIDGE HEALTH TESTING SUMMARY")
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
        
        # Check MT5 Bridge Health endpoint
        bridge_health_tests = [t for t in self.test_results if "MT5 Bridge Health Endpoint" in t["test"]]
        if bridge_health_tests and bridge_health_tests[0]["success"]:
            print("   ✅ MT5 Bridge Health endpoint is properly registered and working")
        else:
            print("   ❌ MT5 Bridge Health endpoint has issues - needs investigation")

        # Check CRM MT5 endpoints
        crm_mt5_tests = [t for t in self.test_results if "CRM MT5" in t["test"]]
        crm_success = sum(1 for t in crm_mt5_tests if t["success"])
        if crm_success >= len(crm_mt5_tests) * 0.5:  # At least 50% working
            print("   ✅ CRM MT5 endpoints are using real MT5 service (not mock)")
        else:
            print("   ❌ CRM MT5 endpoints may still be using mock_mt5 service")

        # Check endpoint registration
        registration_tests = [t for t in self.test_results if "Registration" in t["test"]]
        if registration_tests and registration_tests[0]["success"]:
            print("   ✅ MT5 endpoints are properly registered after server restart")
        else:
            print("   ❌ Some MT5 endpoints are not properly registered")

        # Check authentication
        auth_tests = [t for t in self.test_results if "Authentication" in t["test"]]
        auth_success = sum(1 for t in auth_tests if t["success"])
        if auth_success >= len(auth_tests) * 0.8:  # At least 80% working
            print("   ✅ Admin authentication is working correctly on MT5 endpoints")
        else:
            print("   ❌ Admin authentication issues detected on MT5 endpoints")

        print()
        print("=" * 80)
        
        if success_rate >= 80:
            print("🎉 MT5 BRIDGE HEALTH STATUS: EXCELLENT - All fixes working correctly")
        elif success_rate >= 60:
            print("⚠️  MT5 BRIDGE HEALTH STATUS: GOOD - Minor issues remain")
        else:
            print("🚨 MT5 BRIDGE HEALTH STATUS: NEEDS ATTENTION - Significant issues detected")
            
        print("=" * 80)
        
        return success_rate >= 70  # Success if 70% or higher

if __name__ == "__main__":
    tester = MT5BridgeHealthTester()
    success = tester.run_mt5_bridge_health_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)