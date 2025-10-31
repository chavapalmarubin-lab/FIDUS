#!/usr/bin/env python3
"""
FIDUS Investment Dropdown Routing Fix Verification Test
Testing the specific routing fix for investment dropdown endpoints.

Context: Fixed FastAPI routing by moving specific `/clients/ready-for-investment` routes 
BEFORE generic `/clients/{client_id}` routes to resolve routing conflicts.

Test Focus:
1. GET `/api/clients/ready-for-investment` - Should return hardcoded Alejandro response
2. GET `/api/clients/client_alejandro/readiness` - Confirm investment_ready=true from MongoDB
3. GET `/api/clients/ready-for-investment-test` and `/api/clients/ready-for-investment-debug` - Verify specific routes work
4. Verify routing conflicts resolved - specific routes work before parameterized routes intercept
"""

import requests
import json
import time
import sys
from datetime import datetime, timezone

# Backend URL Configuration
BACKEND_URL = "https://fidus-invest.emergent.host/api"

class RoutingFixTester:
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
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None

    def authenticate_admin(self):
        """Authenticate as admin to get JWT token"""
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
                    print(f"✅ Admin authenticated: {data.get('name')}")
                    return True
                else:
                    print("❌ Admin authentication failed: Missing token or incorrect type")
                    return False
            except json.JSONDecodeError:
                print("❌ Admin authentication failed: Invalid JSON response")
                return False
        else:
            status_code = response.status_code if response else "No response"
            print(f"❌ Admin authentication failed: HTTP {status_code}")
            return False

    def test_ready_clients_endpoint(self):
        """Test the main ready-for-investment endpoint that should return Alejandro"""
        print("🔍 Testing Ready Clients Endpoint...")
        
        if not self.admin_token:
            self.log_test("Ready Clients Endpoint", False, "No admin token available")
            return

        response = self.make_request("GET", "/clients/ready-for-investment", 
                                   auth_token=self.admin_token)
        
        if response and response.status_code == 200:
            try:
                data = response.json()
                ready_clients = data.get("ready_clients", [])
                total_ready = data.get("total_ready", 0)
                
                # Check if Alejandro is in the response
                alejandro_found = False
                for client in ready_clients:
                    if (client.get("client_id") == "client_alejandro" or 
                        "Alejandro" in client.get("name", "") or
                        "alejandro" in client.get("email", "").lower()):
                        alejandro_found = True
                        break
                
                if alejandro_found and total_ready > 0:
                    self.log_test("Ready Clients Endpoint", True, 
                                f"Alejandro found in ready clients list. Total ready: {total_ready}")
                elif total_ready > 0:
                    self.log_test("Ready Clients Endpoint", False, 
                                f"Ready clients found ({total_ready}) but Alejandro not included")
                else:
                    self.log_test("Ready Clients Endpoint", False, 
                                "Empty ready clients list - routing fix may not be working")
                    
            except json.JSONDecodeError:
                self.log_test("Ready Clients Endpoint", False, "Invalid JSON response")
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("Ready Clients Endpoint", False, f"HTTP {status_code}")

    def test_individual_readiness_endpoint(self):
        """Test Alejandro's individual readiness status"""
        print("🔍 Testing Individual Readiness Endpoint...")
        
        if not self.admin_token:
            self.log_test("Individual Readiness Endpoint", False, "No admin token available")
            return

        response = self.make_request("GET", "/clients/client_alejandro/readiness", 
                                   auth_token=self.admin_token)
        
        if response and response.status_code == 200:
            try:
                data = response.json()
                investment_ready = data.get("investment_ready", False)
                aml_kyc_completed = data.get("aml_kyc_completed", False)
                agreement_signed = data.get("agreement_signed", False)
                
                if investment_ready:
                    self.log_test("Individual Readiness Endpoint", True, 
                                f"Alejandro investment_ready=true, AML/KYC={aml_kyc_completed}, Agreement={agreement_signed}")
                else:
                    self.log_test("Individual Readiness Endpoint", False, 
                                f"Alejandro investment_ready=false - MongoDB update may not have worked")
                    
            except json.JSONDecodeError:
                self.log_test("Individual Readiness Endpoint", False, "Invalid JSON response")
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("Individual Readiness Endpoint", False, f"HTTP {status_code}")

    def test_debug_endpoints(self):
        """Test debug endpoints to verify specific routes work before parameterized routes"""
        print("🔍 Testing Debug Endpoints...")
        
        if not self.admin_token:
            self.log_test("Debug Endpoints", False, "No admin token available")
            return

        # Test ready-for-investment-test endpoint
        response = self.make_request("GET", "/clients/ready-for-investment-test", 
                                   auth_token=self.admin_token)
        
        if response and response.status_code == 200:
            try:
                data = response.json()
                if "test" in data or "message" in data:
                    self.log_test("Debug Test Endpoint", True, 
                                "ready-for-investment-test endpoint accessible")
                else:
                    self.log_test("Debug Test Endpoint", False, 
                                "Unexpected response format from test endpoint")
            except json.JSONDecodeError:
                self.log_test("Debug Test Endpoint", False, "Invalid JSON response")
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("Debug Test Endpoint", False, f"HTTP {status_code}")

        # Test ready-for-investment-debug endpoint
        response = self.make_request("GET", "/clients/ready-for-investment-debug", 
                                   auth_token=self.admin_token)
        
        if response and response.status_code == 200:
            try:
                data = response.json()
                if "debug" in data or "message" in data or "clients" in data:
                    self.log_test("Debug Debug Endpoint", True, 
                                "ready-for-investment-debug endpoint accessible")
                else:
                    self.log_test("Debug Debug Endpoint", False, 
                                "Unexpected response format from debug endpoint")
            except json.JSONDecodeError:
                self.log_test("Debug Debug Endpoint", False, "Invalid JSON response")
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("Debug Debug Endpoint", False, f"HTTP {status_code}")

    def test_routing_order_verification(self):
        """Verify that specific routes are not intercepted by parameterized routes"""
        print("🔍 Testing Routing Order Verification...")
        
        if not self.admin_token:
            self.log_test("Routing Order Verification", False, "No admin token available")
            return

        # Test that ready-for-investment is not intercepted by {client_id} route
        # This should NOT be treated as a client_id parameter
        response = self.make_request("GET", "/clients/ready-for-investment", 
                                   auth_token=self.admin_token)
        
        if response:
            try:
                data = response.json()
                # If this was intercepted by {client_id} route, we'd get a client-specific response
                # If routing is correct, we should get ready clients list
                if "ready_clients" in data or "total_ready" in data:
                    self.log_test("Routing Order Verification", True, 
                                "ready-for-investment route correctly handled (not intercepted by {client_id})")
                elif "client_id" in data or "name" in data:
                    self.log_test("Routing Order Verification", False, 
                                "ready-for-investment route intercepted by {client_id} route - routing fix failed")
                else:
                    self.log_test("Routing Order Verification", False, 
                                "Unexpected response format - cannot determine routing behavior")
            except json.JSONDecodeError:
                self.log_test("Routing Order Verification", False, "Invalid JSON response")
        else:
            self.log_test("Routing Order Verification", False, "No response from endpoint")

    def test_parameterized_route_still_works(self):
        """Verify that parameterized client routes still work after routing fix"""
        print("🔍 Testing Parameterized Route Still Works...")
        
        if not self.admin_token:
            self.log_test("Parameterized Route Test", False, "No admin token available")
            return

        # Test that actual client_id routes still work
        response = self.make_request("GET", "/clients/client_alejandro/readiness", 
                                   auth_token=self.admin_token)
        
        if response and response.status_code == 200:
            try:
                data = response.json()
                if "investment_ready" in data or "client_id" in data:
                    self.log_test("Parameterized Route Test", True, 
                                "Parameterized {client_id} routes still working correctly")
                else:
                    self.log_test("Parameterized Route Test", False, 
                                "Unexpected response format from parameterized route")
            except json.JSONDecodeError:
                self.log_test("Parameterized Route Test", False, "Invalid JSON response")
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("Parameterized Route Test", False, f"HTTP {status_code}")

    def run_routing_fix_verification(self):
        """Run all routing fix verification tests"""
        print("🚀 FIDUS Investment Dropdown Routing Fix Verification")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Started: {datetime.now(timezone.utc).isoformat()}")
        print("=" * 80)
        print()

        # Authenticate first
        if not self.authenticate_admin():
            print("❌ Cannot proceed without admin authentication")
            return 0

        print()

        # Run routing fix tests
        self.test_ready_clients_endpoint()
        self.test_individual_readiness_endpoint()
        self.test_debug_endpoints()
        self.test_routing_order_verification()
        self.test_parameterized_route_still_works()

        # Generate summary
        print("=" * 80)
        print("🎯 ROUTING FIX VERIFICATION SUMMARY")
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
        
        # Check if main endpoint works
        ready_clients_test = next((t for t in self.test_results if "Ready Clients Endpoint" in t["test"]), None)
        if ready_clients_test and ready_clients_test["success"]:
            print("   ✅ Ready clients endpoint returns Alejandro - routing fix successful")
        else:
            print("   ❌ Ready clients endpoint not working - routing fix failed")

        # Check if individual readiness works
        individual_test = next((t for t in self.test_results if "Individual Readiness" in t["test"]), None)
        if individual_test and individual_test["success"]:
            print("   ✅ Individual readiness shows investment_ready=true - MongoDB update successful")
        else:
            print("   ❌ Individual readiness not working - MongoDB update may have failed")

        # Check routing order
        routing_test = next((t for t in self.test_results if "Routing Order" in t["test"]), None)
        if routing_test and routing_test["success"]:
            print("   ✅ Routing conflicts resolved - specific routes work before parameterized routes")
        else:
            print("   ❌ Routing conflicts still exist - specific routes intercepted by parameterized routes")

        print()
        print("=" * 80)
        
        if success_rate >= 80:
            print("🎉 ROUTING FIX STATUS: SUCCESSFUL - Investment dropdown should work")
        elif success_rate >= 60:
            print("⚠️  ROUTING FIX STATUS: PARTIAL - Some issues remain")
        else:
            print("🚨 ROUTING FIX STATUS: FAILED - Investment dropdown still broken")
            
        print("=" * 80)
        
        return success_rate

if __name__ == "__main__":
    tester = RoutingFixTester()
    success_rate = tester.run_routing_fix_verification()
    
    # Exit with appropriate code
    sys.exit(0 if success_rate >= 80 else 1)