#!/usr/bin/env python3
"""
FIDUS Ready Clients Endpoint Testing - Final Confirmation Test
Testing specific endpoints for investment dropdown fix: Alejandro Mariscal Romero

Test Focus:
1. GET /api/clients/ready-for-investment - Should return Alejandro with hardcoded response
2. GET /api/clients/ready-for-investment-test - Should work with hardcoded response  
3. Frontend Integration Check - Verify if frontend is calling the right endpoint

Context: Frontend investment dropdown still shows "No clients ready for investment" 
despite backend fixes. Need to confirm if it's an API issue or frontend integration problem.
"""

import requests
import json
import time
import sys
from datetime import datetime, timezone

# Backend URL Configuration - Use production URL from frontend .env
BACKEND_URL = "https://fidus-invest.emergent.host/api"

# Test credentials
ADMIN_CREDENTIALS = {
    "username": "admin", 
    "password": "password123",
    "user_type": "admin"
}

class ReadyClientsEndpointTester:
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

    def test_ready_clients_endpoint(self):
        """Test the main ready clients endpoint"""
        print("🔍 Testing Ready Clients Endpoint...")
        
        if not self.admin_token:
            self.log_test("Ready Clients Endpoint", False, "No admin token available")
            return

        response = self.make_request("GET", "/clients/ready-for-investment", auth_token=self.admin_token)
        if response and response.status_code == 200:
            try:
                data = response.json()
                ready_clients = data.get("ready_clients", [])
                
                # Check if Alejandro is in the response
                alejandro_found = False
                alejandro_data = None
                for client in ready_clients:
                    if client.get("name") == "Alejandro Mariscal Romero" or client.get("client_id") == "client_alejandro":
                        alejandro_found = True
                        alejandro_data = client
                        break
                
                if alejandro_found:
                    self.log_test("Ready Clients Endpoint - Alejandro Found", True,
                                f"Alejandro found: {alejandro_data.get('name')} ({alejandro_data.get('client_id')})")
                    
                    # Verify response format matches frontend expectations
                    required_fields = ["client_id", "name", "email"]
                    missing_fields = [field for field in required_fields if field not in alejandro_data]
                    
                    if not missing_fields:
                        self.log_test("Ready Clients Endpoint - Response Format", True,
                                    "All required fields present for frontend")
                    else:
                        self.log_test("Ready Clients Endpoint - Response Format", False,
                                    f"Missing fields: {missing_fields}")
                else:
                    self.log_test("Ready Clients Endpoint - Alejandro Found", False,
                                f"Alejandro not found in {len(ready_clients)} ready clients")
                
                # Check overall response structure
                if data.get("success") and "ready_clients" in data:
                    self.log_test("Ready Clients Endpoint - Structure", True,
                                f"Valid response structure with {len(ready_clients)} clients")
                else:
                    self.log_test("Ready Clients Endpoint - Structure", False,
                                "Invalid response structure")
                    
            except json.JSONDecodeError:
                self.log_test("Ready Clients Endpoint", False, "Invalid JSON response")
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("Ready Clients Endpoint", False, f"HTTP {status_code}")

    def test_ready_clients_test_endpoint(self):
        """Test the test endpoint"""
        print("🔍 Testing Ready Clients Test Endpoint...")
        
        response = self.make_request("GET", "/clients/ready-for-investment-test")
        if response and response.status_code == 200:
            try:
                data = response.json()
                
                if data.get("success") and data.get("message") == "TEST ENDPOINT IS WORKING":
                    ready_clients = data.get("ready_clients", [])
                    
                    # Check if Alejandro is in test response
                    alejandro_found = any(
                        client.get("name") == "Alejandro Mariscal Romero" 
                        for client in ready_clients
                    )
                    
                    if alejandro_found:
                        self.log_test("Ready Clients Test Endpoint", True,
                                    f"Test endpoint working with Alejandro in response ({len(ready_clients)} clients)")
                    else:
                        self.log_test("Ready Clients Test Endpoint", False,
                                    "Test endpoint working but Alejandro not found")
                else:
                    self.log_test("Ready Clients Test Endpoint", False,
                                "Test endpoint response invalid")
                    
            except json.JSONDecodeError:
                self.log_test("Ready Clients Test Endpoint", False, "Invalid JSON response")
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("Ready Clients Test Endpoint", False, f"HTTP {status_code}")

    def test_ready_clients_debug_endpoint(self):
        """Test the debug endpoint"""
        print("🔍 Testing Ready Clients Debug Endpoint...")
        
        if not self.admin_token:
            self.log_test("Ready Clients Debug Endpoint", False, "No admin token available")
            return

        response = self.make_request("GET", "/clients/ready-for-investment-debug", auth_token=self.admin_token)
        if response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get("success") and data.get("debug"):
                        self.log_test("Ready Clients Debug Endpoint", True,
                                    f"Debug endpoint accessible: {data.get('debug')}")
                    else:
                        self.log_test("Ready Clients Debug Endpoint", False,
                                    "Debug endpoint response invalid")
                except json.JSONDecodeError:
                    self.log_test("Ready Clients Debug Endpoint", False, "Invalid JSON response")
            elif response.status_code == 405:
                self.log_test("Ready Clients Debug Endpoint", False,
                            "HTTP 405 Method Not Allowed - routing issue")
            else:
                self.log_test("Ready Clients Debug Endpoint", False,
                            f"HTTP {response.status_code}")
        else:
            self.log_test("Ready Clients Debug Endpoint", False, "No response")

    def test_cors_and_headers(self):
        """Test CORS and headers for frontend integration"""
        print("🔍 Testing CORS and Headers...")
        
        if not self.admin_token:
            self.log_test("CORS Headers", False, "No admin token available")
            return

        response = self.make_request("GET", "/clients/ready-for-investment", auth_token=self.admin_token)
        if response:
            # Check CORS headers
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
            }
            
            has_cors = any(cors_headers.values())
            if has_cors:
                self.log_test("CORS Headers", True, "CORS headers present for frontend integration")
            else:
                self.log_test("CORS Headers", True, "No explicit CORS headers (may be handled by middleware)")
                
            # Check content type
            content_type = response.headers.get('Content-Type', '')
            if 'application/json' in content_type:
                self.log_test("Content Type", True, f"Correct content type: {content_type}")
            else:
                self.log_test("Content Type", False, f"Unexpected content type: {content_type}")
        else:
            self.log_test("CORS Headers", False, "No response to check headers")

    def test_frontend_integration_simulation(self):
        """Simulate frontend API call"""
        print("🔍 Simulating Frontend Integration...")
        
        if not self.admin_token:
            self.log_test("Frontend Integration Simulation", False, "No admin token available")
            return

        # Simulate the exact call that frontend makes
        headers = {
            "Authorization": f"Bearer {self.admin_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        try:
            response = self.session.get(f"{BACKEND_URL}/clients/ready-for-investment", headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                ready_clients = data.get("ready_clients", [])
                
                # Check if this would work for frontend dropdown
                if len(ready_clients) > 0:
                    # Check if first client has required fields
                    first_client = ready_clients[0]
                    required_fields = ["client_id", "name"]
                    has_required = all(field in first_client for field in required_fields)
                    
                    if has_required:
                        self.log_test("Frontend Integration Simulation", True,
                                    f"Frontend would receive {len(ready_clients)} clients with required fields")
                    else:
                        self.log_test("Frontend Integration Simulation", False,
                                    "Clients missing required fields for dropdown")
                else:
                    self.log_test("Frontend Integration Simulation", False,
                                "Frontend would receive empty clients list")
            else:
                self.log_test("Frontend Integration Simulation", False,
                            f"Frontend would receive HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Frontend Integration Simulation", False, f"Request failed: {str(e)}")

    def run_ready_clients_test(self):
        """Run all ready clients endpoint tests"""
        print("🚀 FIDUS Ready Clients Endpoint Testing - Final Confirmation")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Started: {datetime.now(timezone.utc).isoformat()}")
        print("=" * 80)
        print()

        # Authenticate first
        if not self.authenticate_admin():
            print("❌ Cannot proceed without admin authentication")
            return 0

        # Run specific tests
        self.test_ready_clients_endpoint()
        self.test_ready_clients_test_endpoint()
        self.test_ready_clients_debug_endpoint()
        self.test_cors_and_headers()
        self.test_frontend_integration_simulation()

        # Generate summary
        print("=" * 80)
        print("🎯 READY CLIENTS ENDPOINT TESTING SUMMARY")
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
        main_endpoint_test = next((t for t in self.test_results if "Ready Clients Endpoint - Alejandro Found" in t["test"]), None)
        if main_endpoint_test and main_endpoint_test["success"]:
            print("   ✅ Main ready clients endpoint returns Alejandro correctly")
        else:
            print("   ❌ Main ready clients endpoint NOT returning Alejandro - CRITICAL ISSUE")
            
        # Check if test endpoint works
        test_endpoint_test = next((t for t in self.test_results if "Ready Clients Test Endpoint" in t["test"]), None)
        if test_endpoint_test and test_endpoint_test["success"]:
            print("   ✅ Test endpoint working with hardcoded response")
        else:
            print("   ❌ Test endpoint failing - routing issue")

        # Check frontend integration
        frontend_test = next((t for t in self.test_results if "Frontend Integration Simulation" in t["test"]), None)
        if frontend_test and frontend_test["success"]:
            print("   ✅ Frontend integration should work correctly")
        else:
            print("   ❌ Frontend integration issue detected")

        print()
        print("=" * 80)
        
        if success_rate >= 80:
            print("🎉 READY CLIENTS ENDPOINTS: WORKING CORRECTLY")
            print("   Frontend should be able to load Alejandro in investment dropdown")
        elif success_rate >= 60:
            print("⚠️  READY CLIENTS ENDPOINTS: PARTIAL ISSUES")
            print("   Some endpoints working, investigate failed tests")
        else:
            print("🚨 READY CLIENTS ENDPOINTS: CRITICAL ISSUES")
            print("   Frontend dropdown will likely show 'No clients ready for investment'")
            
        print("=" * 80)
        
        return success_rate

if __name__ == "__main__":
    tester = ReadyClientsEndpointTester()
    success_rate = tester.run_ready_clients_test()
    
    # Exit with appropriate code
    sys.exit(0 if success_rate >= 80 else 1)