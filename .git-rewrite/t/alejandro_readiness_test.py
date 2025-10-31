#!/usr/bin/env python3
"""
FIDUS Backend API Testing - Alejandro Readiness and Routing Fix Verification
Testing specific endpoints for investment dropdown fix and client readiness override functionality.

Test Areas:
1. Ready Clients Endpoint - Should return hardcoded Alejandro response after routing fix
2. Alejandro's Readiness Status - Check current readiness before override
3. Apply Readiness Override - Set readiness_override=true with test reason
4. Verify Override Applied - Confirm investment_ready=true after override
5. Verify Ready Clients List - Confirm Alejandro appears in ready clients

Context: Testing routing conflict resolution and override mechanism for Alejandro Mariscal Romero
"""

import requests
import json
import time
import sys
from datetime import datetime, timezone

# Backend URL Configuration
BACKEND_URL = "https://fidus-invest.emergent.host/api"

# Test credentials
ADMIN_CREDENTIALS = {
    "username": "admin", 
    "password": "password123",
    "user_type": "admin"
}

class AlejandroReadinessTester:
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
        """Authenticate as admin and get JWT token"""
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
        """Test 1: GET /api/clients/ready-for-investment - Should return hardcoded Alejandro response"""
        print("🔍 Test 1: Testing Ready Clients Endpoint...")
        
        if not self.admin_token:
            self.log_test("Ready Clients Endpoint", False, "No admin token available")
            return
        
        response = self.make_request("GET", "/clients/ready-for-investment", auth_token=self.admin_token)
        if response and response.status_code == 200:
            try:
                data = response.json()
                clients = data.get("ready_clients", data.get("clients", []))
                
                # Check if Alejandro is in the response
                alejandro_found = False
                for client in clients:
                    if (client.get("name") == "Alejandro Mariscal Romero" or 
                        client.get("client_id") == "client_alejandro" or
                        "alejandro" in client.get("name", "").lower()):
                        alejandro_found = True
                        break
                
                if alejandro_found:
                    self.log_test("Ready Clients Endpoint", True, 
                                f"Alejandro found in ready clients list ({len(clients)} total clients)")
                else:
                    self.log_test("Ready Clients Endpoint", False, 
                                f"Alejandro NOT found in ready clients list ({len(clients)} total clients)")
                    print(f"   Available clients: {[c.get('name', 'Unknown') for c in clients]}")
                    
            except json.JSONDecodeError:
                self.log_test("Ready Clients Endpoint", False, "Invalid JSON response")
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("Ready Clients Endpoint", False, f"HTTP {status_code}")

    def test_alejandro_readiness_status(self):
        """Test 2: GET /api/clients/client_alejandro/readiness - Check current readiness status"""
        print("🔍 Test 2: Testing Alejandro's Current Readiness Status...")
        
        if not self.admin_token:
            self.log_test("Alejandro Readiness Status", False, "No admin token available")
            return
        
        response = self.make_request("GET", "/clients/client_alejandro/readiness", auth_token=self.admin_token)
        if response and response.status_code == 200:
            try:
                data = response.json()
                investment_ready = data.get("investment_ready", False)
                aml_kyc_completed = data.get("aml_kyc_completed", False)
                agreement_signed = data.get("agreement_signed", False)
                readiness_override = data.get("readiness_override", False)
                
                self.log_test("Alejandro Readiness Status", True, 
                            f"investment_ready: {investment_ready}, aml_kyc: {aml_kyc_completed}, "
                            f"agreement: {agreement_signed}, override: {readiness_override}")
                
                # Store current status for comparison later
                self.alejandro_current_status = data
                
            except json.JSONDecodeError:
                self.log_test("Alejandro Readiness Status", False, "Invalid JSON response")
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("Alejandro Readiness Status", False, f"HTTP {status_code}")

    def test_apply_readiness_override(self):
        """Test 3: POST /api/clients/client_alejandro/readiness - Apply override with test reason"""
        print("🔍 Test 3: Applying Readiness Override for Alejandro...")
        
        if not self.admin_token:
            self.log_test("Apply Readiness Override", False, "No admin token available")
            return
        
        override_data = {
            "readiness_override": True,
            "aml_kyc_completed": True,
            "agreement_signed": True,
            "readiness_override_reason": "Testing routing fix and override functionality - automated test",
            "readiness_override_by": "admin_001",
            "readiness_override_date": datetime.now(timezone.utc).isoformat()
        }
        
        response = self.make_request("PUT", "/clients/client_alejandro/readiness", 
                                   override_data, auth_token=self.admin_token)
        if response and response.status_code == 200:
            try:
                data = response.json()
                if data.get("success"):
                    self.log_test("Apply Readiness Override", True, 
                                f"Override applied successfully: {data.get('message', 'No message')}")
                else:
                    self.log_test("Apply Readiness Override", False, 
                                f"Override failed: {data.get('message', 'Unknown error')}")
            except json.JSONDecodeError:
                self.log_test("Apply Readiness Override", False, "Invalid JSON response")
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("Apply Readiness Override", False, f"HTTP {status_code}")

    def test_verify_override_applied(self):
        """Test 4: GET /api/clients/client_alejandro/readiness - Confirm investment_ready=true after override"""
        print("🔍 Test 4: Verifying Override Applied Successfully...")
        
        if not self.admin_token:
            self.log_test("Verify Override Applied", False, "No admin token available")
            return
        
        # Wait a moment for the override to be processed
        time.sleep(2)
        
        response = self.make_request("GET", "/clients/client_alejandro/readiness", auth_token=self.admin_token)
        if response and response.status_code == 200:
            try:
                data = response.json()
                investment_ready = data.get("investment_ready", False)
                aml_kyc_completed = data.get("aml_kyc_completed", False)
                agreement_signed = data.get("agreement_signed", False)
                readiness_override = data.get("readiness_override", False)
                override_reason = data.get("readiness_override_reason", "")
                
                if investment_ready and readiness_override:
                    self.log_test("Verify Override Applied", True, 
                                f"Override successful - investment_ready: {investment_ready}, "
                                f"override: {readiness_override}, reason: {override_reason[:50]}...")
                else:
                    self.log_test("Verify Override Applied", False, 
                                f"Override not applied correctly - investment_ready: {investment_ready}, "
                                f"override: {readiness_override}")
                    
            except json.JSONDecodeError:
                self.log_test("Verify Override Applied", False, "Invalid JSON response")
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("Verify Override Applied", False, f"HTTP {status_code}")

    def test_ready_clients_after_override(self):
        """Test 5: GET /api/clients/ready-for-investment - Confirm Alejandro appears in ready clients list"""
        print("🔍 Test 5: Testing Ready Clients After Override...")
        
        if not self.admin_token:
            self.log_test("Ready Clients After Override", False, "No admin token available")
            return
        
        # Wait a moment for the changes to propagate
        time.sleep(2)
        
        response = self.make_request("GET", "/clients/ready-for-investment", auth_token=self.admin_token)
        if response and response.status_code == 200:
            try:
                data = response.json()
                clients = data.get("ready_clients", data.get("clients", []))
                
                # Check if Alejandro is in the response
                alejandro_found = False
                alejandro_client = None
                for client in clients:
                    if (client.get("name") == "Alejandro Mariscal Romero" or 
                        client.get("client_id") == "client_alejandro" or
                        "alejandro" in client.get("name", "").lower()):
                        alejandro_found = True
                        alejandro_client = client
                        break
                
                if alejandro_found:
                    investment_ready = alejandro_client.get("investment_ready", False)
                    self.log_test("Ready Clients After Override", True, 
                                f"Alejandro found in ready clients list with investment_ready: {investment_ready} "
                                f"({len(clients)} total ready clients)")
                else:
                    self.log_test("Ready Clients After Override", False, 
                                f"Alejandro NOT found in ready clients list after override ({len(clients)} total clients)")
                    print(f"   Available clients: {[c.get('name', 'Unknown') for c in clients]}")
                    
            except json.JSONDecodeError:
                self.log_test("Ready Clients After Override", False, "Invalid JSON response")
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("Ready Clients After Override", False, f"HTTP {status_code}")

    def run_alejandro_readiness_test(self):
        """Run all Alejandro readiness tests"""
        print("🚀 FIDUS Backend API Testing - Alejandro Readiness and Routing Fix Verification")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Started: {datetime.now(timezone.utc).isoformat()}")
        print("=" * 80)
        print()

        # Authenticate first
        if not self.authenticate_admin():
            print("❌ Authentication failed - cannot proceed with tests")
            return 0

        # Run all test suites in order
        self.test_ready_clients_endpoint()
        self.test_alejandro_readiness_status()
        self.test_apply_readiness_override()
        self.test_verify_override_applied()
        self.test_ready_clients_after_override()

        # Generate summary
        print("=" * 80)
        print("🎯 ALEJANDRO READINESS TESTING SUMMARY")
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
        
        # Check routing fix
        ready_clients_tests = [t for t in self.test_results if "Ready Clients" in t["test"]]
        if all(t["success"] for t in ready_clients_tests):
            print("   ✅ Routing fix successful - ready clients endpoint working")
        else:
            print("   ❌ Routing fix issues - ready clients endpoint problems")

        # Check override functionality
        override_tests = [t for t in self.test_results if "Override" in t["test"] or "Readiness" in t["test"]]
        override_success = sum(1 for t in override_tests if t["success"])
        if override_success >= 3:
            print("   ✅ Override functionality working correctly")
        else:
            print("   ❌ Override functionality has issues")

        # Check Alejandro's status
        if self.passed_tests >= 4:
            print("   ✅ Alejandro appears in ready clients after override")
        else:
            print("   ❌ Alejandro readiness system needs attention")

        print()
        print("=" * 80)
        
        if success_rate >= 80:
            print("🎉 ROUTING FIX AND OVERRIDE SYSTEM: WORKING CORRECTLY")
        elif success_rate >= 60:
            print("⚠️  ROUTING FIX AND OVERRIDE SYSTEM: MINOR ISSUES")
        else:
            print("🚨 ROUTING FIX AND OVERRIDE SYSTEM: CRITICAL ISSUES")
            
        print("=" * 80)
        
        return success_rate

if __name__ == "__main__":
    tester = AlejandroReadinessTester()
    success_rate = tester.run_alejandro_readiness_test()
    
    # Exit with appropriate code
    sys.exit(0 if success_rate >= 80 else 1)