#!/usr/bin/env python3
"""
FIDUS Investment Creation Dropdown Issue Debug Test
Testing the specific issue where investment dropdown is empty after client cleanup.

Focus Areas:
1. Ready Clients Endpoint: GET /api/clients/ready-for-investment
2. Alejandro's Readiness Status: GET /api/clients/{alejandro_id}/readiness  
3. Update Alejandro's Readiness: POST /api/clients/{alejandro_id}/readiness
4. Frontend API Call verification

Expected Result: Alejandro Mariscal should appear in investment dropdown
"""

import requests
import json
import time
import sys
from datetime import datetime, timezone

# Backend URL Configuration - Use URL from frontend .env
BACKEND_URL = "https://mt5-integration.preview.emergentagent.com/api"

# Admin credentials for testing
ADMIN_CREDENTIALS = {
    "username": "admin",
    "password": "password123", 
    "user_type": "admin"
}

class InvestmentDropdownTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.alejandro_client_id = None
        
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

    def find_alejandro_client_id(self):
        """Find Alejandro's client ID from the users list"""
        print("🔍 Finding Alejandro's client ID...")
        
        if not self.admin_token:
            self.log_test("Find Alejandro Client ID", False, "No admin token available")
            return False

        # Get all clients
        response = self.make_request("GET", "/admin/clients", auth_token=self.admin_token)
        if response and response.status_code == 200:
            try:
                data = response.json()
                clients = data.get("clients", [])
                
                # Look for Alejandro Mariscal
                alejandro_variations = [
                    "alejandro mariscal romero",
                    "alejandro mariscal", 
                    "alejandro",
                    "alexmar7609@gmail.com"
                ]
                
                for client in clients:
                    client_name = client.get("name", "").lower()
                    client_email = client.get("email", "").lower()
                    
                    for variation in alejandro_variations:
                        if variation in client_name or variation in client_email:
                            self.alejandro_client_id = client.get("id")
                            self.log_test("Find Alejandro Client ID", True,
                                        f"Found Alejandro: ID={self.alejandro_client_id}, Name={client.get('name')}, Email={client.get('email')}")
                            return True
                
                # If not found, list all clients for debugging
                client_list = [f"{c.get('name')} ({c.get('email')})" for c in clients]
                self.log_test("Find Alejandro Client ID", False, 
                            f"Alejandro not found. Available clients: {client_list}")
                return False
                
            except json.JSONDecodeError:
                self.log_test("Find Alejandro Client ID", False, "Invalid JSON response")
                return False
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("Find Alejandro Client ID", False, f"HTTP {status_code}")
            return False

    def test_ready_clients_endpoint(self):
        """Test the ready clients endpoint that feeds the investment dropdown"""
        print("🔍 Testing Ready Clients Endpoint...")
        
        if not self.admin_token:
            self.log_test("Ready Clients Endpoint", False, "No admin token available")
            return False

        response = self.make_request("GET", "/clients/ready-for-investment", auth_token=self.admin_token)
        if response and response.status_code == 200:
            try:
                data = response.json()
                ready_clients = data.get("ready_clients", []) if isinstance(data, dict) else data
                
                if isinstance(ready_clients, list):
                    # Check if Alejandro is in the ready clients list
                    alejandro_found = False
                    for client in ready_clients:
                        client_name = client.get("name", "").lower()
                        client_email = client.get("email", "").lower()
                        if ("alejandro" in client_name or "alexmar7609@gmail.com" in client_email):
                            alejandro_found = True
                            break
                    
                    if alejandro_found:
                        self.log_test("Ready Clients Endpoint", True,
                                    f"Alejandro found in ready clients list. Total ready clients: {len(ready_clients)}")
                    else:
                        client_list = [f"{c.get('name')} ({c.get('email')})" for c in ready_clients]
                        self.log_test("Ready Clients Endpoint", False,
                                    f"Alejandro NOT found in ready clients. Ready clients: {client_list}")
                    return alejandro_found
                else:
                    self.log_test("Ready Clients Endpoint", False, 
                                f"Unexpected response format: {type(ready_clients)}")
                    return False
                    
            except json.JSONDecodeError:
                self.log_test("Ready Clients Endpoint", False, "Invalid JSON response")
                return False
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("Ready Clients Endpoint", False, f"HTTP {status_code}")
            return False

    def test_alejandro_readiness_status(self):
        """Test Alejandro's specific readiness status"""
        print("🔍 Testing Alejandro's Readiness Status...")
        
        if not self.admin_token:
            self.log_test("Alejandro Readiness Status", False, "No admin token available")
            return None
            
        if not self.alejandro_client_id:
            self.log_test("Alejandro Readiness Status", False, "Alejandro client ID not found")
            return None

        response = self.make_request("GET", f"/clients/{self.alejandro_client_id}/readiness", 
                                   auth_token=self.admin_token)
        if response and response.status_code == 200:
            try:
                data = response.json()
                aml_kyc = data.get("aml_kyc_completed", False)
                agreement = data.get("agreement_signed", False)
                investment_ready = data.get("investment_ready", False)
                
                self.log_test("Alejandro Readiness Status", True,
                            f"AML/KYC: {aml_kyc}, Agreement: {agreement}, Investment Ready: {investment_ready}")
                return data
                
            except json.JSONDecodeError:
                self.log_test("Alejandro Readiness Status", False, "Invalid JSON response")
                return None
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("Alejandro Readiness Status", False, f"HTTP {status_code}")
            return None

    def update_alejandro_readiness(self):
        """Update Alejandro's readiness status to make him investment ready"""
        print("🔧 Updating Alejandro's Readiness Status...")
        
        if not self.admin_token:
            self.log_test("Update Alejandro Readiness", False, "No admin token available")
            return False
            
        if not self.alejandro_client_id:
            self.log_test("Update Alejandro Readiness", False, "Alejandro client ID not found")
            return False

        # Update readiness data
        readiness_data = {
            "aml_kyc_completed": True,
            "agreement_signed": True,
            "notes": "Updated for investment dropdown testing",
            "updated_by": "admin"
        }

        response = self.make_request("PUT", f"/clients/{self.alejandro_client_id}/readiness", 
                                   readiness_data, auth_token=self.admin_token)
        if response and response.status_code == 200:
            try:
                data = response.json()
                if data.get("success"):
                    self.log_test("Update Alejandro Readiness", True,
                                "Alejandro's readiness status updated successfully")
                    return True
                else:
                    self.log_test("Update Alejandro Readiness", False,
                                f"Update failed: {data.get('message', 'Unknown error')}")
                    return False
                    
            except json.JSONDecodeError:
                self.log_test("Update Alejandro Readiness", False, "Invalid JSON response")
                return False
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("Update Alejandro Readiness", False, f"HTTP {status_code}")
            return False

    def verify_frontend_api_call(self):
        """Verify the frontend API call format matches backend response"""
        print("🔍 Verifying Frontend API Call Format...")
        
        if not self.admin_token:
            self.log_test("Frontend API Call Verification", False, "No admin token available")
            return False

        response = self.make_request("GET", "/clients/ready-for-investment", auth_token=self.admin_token)
        if response and response.status_code == 200:
            try:
                data = response.json()
                
                # Check if response format matches what frontend expects
                # Frontend expects: [{"client_id": "id", "name": "Name", "email": "email"}]
                ready_clients = data.get("ready_clients", []) if isinstance(data, dict) else data
                
                if isinstance(ready_clients, list) and len(ready_clients) > 0:
                    sample_client = ready_clients[0]
                    required_fields = ["client_id", "name", "email"]
                    missing_fields = [field for field in required_fields if field not in sample_client]
                    
                    if not missing_fields:
                        self.log_test("Frontend API Call Verification", True,
                                    f"Response format correct. Sample: {sample_client}")
                        return True
                    else:
                        # Check alternative field names
                        alt_fields = {"client_id": "id", "name": "name", "email": "email"}
                        alt_missing = []
                        for field in required_fields:
                            alt_field = alt_fields.get(field, field)
                            if alt_field not in sample_client:
                                alt_missing.append(f"{field} (or {alt_field})")
                        
                        self.log_test("Frontend API Call Verification", False,
                                    f"Missing fields: {alt_missing}. Available fields: {list(sample_client.keys())}")
                        return False
                else:
                    self.log_test("Frontend API Call Verification", False,
                                "No ready clients found or invalid format")
                    return False
                    
            except json.JSONDecodeError:
                self.log_test("Frontend API Call Verification", False, "Invalid JSON response")
                return False
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("Frontend API Call Verification", False, f"HTTP {status_code}")
            return False

    def run_investment_dropdown_debug(self):
        """Run the complete investment dropdown debug test"""
        print("🚀 FIDUS Investment Creation Dropdown Issue Debug")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Started: {datetime.now(timezone.utc).isoformat()}")
        print("=" * 80)
        print()

        # Step 1: Authenticate as admin
        if not self.authenticate_admin():
            print("❌ Cannot proceed without admin authentication")
            return False

        # Step 2: Find Alejandro's client ID
        if not self.find_alejandro_client_id():
            print("❌ Cannot proceed without Alejandro's client ID")
            return False

        # Step 3: Check current ready clients endpoint
        print("📋 STEP 1: Check Ready Clients Endpoint")
        alejandro_ready_initially = self.test_ready_clients_endpoint()

        # Step 4: Check Alejandro's readiness status
        print("📋 STEP 2: Check Alejandro's Readiness Status")
        readiness_status = self.test_alejandro_readiness_status()

        # Step 5: Update Alejandro's readiness if needed
        if readiness_status and not readiness_status.get("investment_ready", False):
            print("📋 STEP 3: Update Alejandro's Readiness")
            self.update_alejandro_readiness()
            
            # Wait a moment for database update
            time.sleep(2)
            
            # Re-check readiness status
            print("📋 STEP 4: Re-check Alejandro's Readiness Status")
            self.test_alejandro_readiness_status()

        # Step 6: Re-test ready clients endpoint
        print("📋 STEP 5: Re-test Ready Clients Endpoint")
        alejandro_ready_finally = self.test_ready_clients_endpoint()

        # Step 7: Verify frontend API call format
        print("📋 STEP 6: Verify Frontend API Call Format")
        self.verify_frontend_api_call()

        # Generate summary
        print("=" * 80)
        print("🎯 INVESTMENT DROPDOWN DEBUG SUMMARY")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()

        # Show critical findings
        print("🔍 CRITICAL FINDINGS:")
        
        if self.alejandro_client_id:
            print(f"   ✅ Alejandro found: ID={self.alejandro_client_id}")
        else:
            print("   ❌ Alejandro not found in client list")
            
        if alejandro_ready_finally:
            print("   ✅ Alejandro appears in ready clients endpoint")
        else:
            print("   ❌ Alejandro does NOT appear in ready clients endpoint")

        # Show failed tests
        failed_tests = [t for t in self.test_results if not t["success"]]
        if failed_tests:
            print()
            print("❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"   • {test['test']}: {test['error']}")

        print()
        print("=" * 80)
        
        if alejandro_ready_finally:
            print("🎉 ISSUE RESOLVED: Alejandro should now appear in investment dropdown")
        else:
            print("🚨 ISSUE PERSISTS: Alejandro still not appearing in investment dropdown")
            
        print("=" * 80)
        
        return alejandro_ready_finally

if __name__ == "__main__":
    tester = InvestmentDropdownTester()
    success = tester.run_investment_dropdown_debug()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)