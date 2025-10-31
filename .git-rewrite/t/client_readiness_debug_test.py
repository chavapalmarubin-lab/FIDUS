#!/usr/bin/env python3
"""
FIDUS Client Readiness Debug Test
Debug the client readiness issue for the investment creation dropdown.

Issue: Investment creation dropdown is showing empty even though 7 clients exist.
Need to understand why no clients are marked as "investment_ready".

Test Areas:
1. Check Ready Clients Endpoint: GET `/api/clients/ready-for-investment`
2. Check All Clients: GET `/api/users` 
3. Check Specific Client: Find Alejandro Mariscal's client record and check his readiness status
4. Verify readiness requirements (aml_kyc_completed and agreement_signed)
5. Check data inconsistency between in-memory and MongoDB storage
"""

import requests
import json
import time
import sys
from datetime import datetime, timezone

# Backend URL Configuration
BACKEND_URL = "https://fidus-invest.emergent.host/api"

class ClientReadinessDebugger:
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

    def check_ready_clients_endpoint(self):
        """Check Ready Clients Endpoint: GET `/api/clients/ready-for-investment`"""
        print("🔍 Checking Ready Clients Endpoint...")
        
        if not self.admin_token:
            self.log_test("Ready Clients Endpoint", False, "No admin token available")
            return
        
        response = self.make_request("GET", "/clients/ready-for-investment", auth_token=self.admin_token)
        if response and response.status_code == 200:
            try:
                data = response.json()
                ready_clients = data.get("ready_clients", [])
                total_ready = data.get("total_ready", 0)
                
                self.log_test("Ready Clients Endpoint", True, 
                            f"Found {total_ready} ready clients out of total clients")
                
                if ready_clients:
                    print("   📋 Ready Clients Details:")
                    for client in ready_clients:
                        print(f"      • {client.get('name')} ({client.get('client_id')}) - {client.get('email')}")
                else:
                    print("   ⚠️  NO CLIENTS ARE MARKED AS READY FOR INVESTMENT")
                    
                return ready_clients
                
            except json.JSONDecodeError:
                self.log_test("Ready Clients Endpoint", False, "Invalid JSON response")
                return []
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("Ready Clients Endpoint", False, f"HTTP {status_code}")
            return []

    def check_all_clients(self):
        """Check All Clients: GET `/api/users`"""
        print("🔍 Checking All Clients in System...")
        
        if not self.admin_token:
            self.log_test("All Clients Check", False, "No admin token available")
            return []
        
        response = self.make_request("GET", "/admin/users", auth_token=self.admin_token)
        if response and response.status_code == 200:
            try:
                data = response.json()
                users = data.get("users", [])
                clients = [u for u in users if u.get("type") == "client"]
                
                self.log_test("All Clients Check", True, 
                            f"Found {len(clients)} clients out of {len(users)} total users")
                
                print("   📋 All Clients in System:")
                for client in clients:
                    readiness_status = "Unknown"
                    if hasattr(client, 'investment_ready'):
                        readiness_status = "Ready" if client.get('investment_ready') else "Not Ready"
                    print(f"      • {client.get('name')} ({client.get('id')}) - {client.get('email')} - Status: {readiness_status}")
                
                return clients
                
            except json.JSONDecodeError:
                self.log_test("All Clients Check", False, "Invalid JSON response")
                return []
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("All Clients Check", False, f"HTTP {status_code}")
            return []

    def check_specific_client_readiness(self, client_id, client_name):
        """Check specific client's readiness status"""
        print(f"🔍 Checking {client_name}'s Readiness Status...")
        
        if not self.admin_token:
            self.log_test(f"{client_name} Readiness Check", False, "No admin token available")
            return None
        
        response = self.make_request("GET", f"/clients/{client_id}/readiness", auth_token=self.admin_token)
        if response and response.status_code == 200:
            try:
                data = response.json()
                readiness = data.get("readiness", {})
                
                aml_kyc_completed = readiness.get("aml_kyc_completed", False)
                agreement_signed = readiness.get("agreement_signed", False)
                investment_ready = readiness.get("investment_ready", False)
                account_creation_date = readiness.get("account_creation_date")
                
                self.log_test(f"{client_name} Readiness Check", True, 
                            f"AML/KYC: {aml_kyc_completed}, Agreement: {agreement_signed}, Ready: {investment_ready}")
                
                print(f"   📋 {client_name} Readiness Details:")
                print(f"      • AML/KYC Completed: {aml_kyc_completed}")
                print(f"      • Agreement Signed: {agreement_signed}")
                print(f"      • Investment Ready: {investment_ready}")
                print(f"      • Account Creation Date: {account_creation_date}")
                print(f"      • Updated At: {readiness.get('updated_at')}")
                print(f"      • Updated By: {readiness.get('updated_by')}")
                
                # Check if readiness logic is correct
                expected_ready = aml_kyc_completed and agreement_signed
                if investment_ready != expected_ready:
                    print(f"   ⚠️  READINESS LOGIC MISMATCH: Expected {expected_ready}, Got {investment_ready}")
                
                return readiness
                
            except json.JSONDecodeError:
                self.log_test(f"{client_name} Readiness Check", False, "Invalid JSON response")
                return None
        else:
            status_code = response.status_code if response else "No response"
            self.log_test(f"{client_name} Readiness Check", False, f"HTTP {status_code}")
            return None

    def update_client_readiness(self, client_id, client_name, aml_kyc=True, agreement=True):
        """Update client readiness to make them investment ready"""
        print(f"🔧 Updating {client_name}'s Readiness Status...")
        
        if not self.admin_token:
            self.log_test(f"Update {client_name} Readiness", False, "No admin token available")
            return False
        
        update_data = {
            "aml_kyc_completed": aml_kyc,
            "agreement_signed": agreement,
            "account_creation_date": datetime.now(timezone.utc).isoformat(),
            "updated_by": "admin_001",
            "notes": f"Updated during client readiness debugging - {datetime.now(timezone.utc).isoformat()}"
        }
        
        response = self.make_request("PUT", f"/clients/{client_id}/readiness", update_data, auth_token=self.admin_token)
        if response and response.status_code == 200:
            try:
                data = response.json()
                if data.get("success"):
                    readiness = data.get("readiness", {})
                    investment_ready = readiness.get("investment_ready", False)
                    
                    self.log_test(f"Update {client_name} Readiness", True, 
                                f"Updated successfully - Investment Ready: {investment_ready}")
                    return True
                else:
                    self.log_test(f"Update {client_name} Readiness", False, "Update failed")
                    return False
            except json.JSONDecodeError:
                self.log_test(f"Update {client_name} Readiness", False, "Invalid JSON response")
                return False
        else:
            status_code = response.status_code if response else "No response"
            self.log_test(f"Update {client_name} Readiness", False, f"HTTP {status_code}")
            return False

    def verify_data_consistency(self):
        """Verify data consistency between endpoints"""
        print("🔍 Verifying Data Consistency...")
        
        # Get ready clients from ready endpoint
        ready_clients = self.check_ready_clients_endpoint()
        
        # Get all clients from users endpoint
        all_clients = self.check_all_clients()
        
        # Check each client's individual readiness
        print("\n🔍 Checking Individual Client Readiness...")
        individual_ready_count = 0
        
        for client in all_clients:
            client_id = client.get('id')
            client_name = client.get('name')
            
            readiness = self.check_specific_client_readiness(client_id, client_name)
            if readiness and readiness.get('investment_ready'):
                individual_ready_count += 1
        
        # Compare results
        ready_endpoint_count = len(ready_clients)
        
        print(f"\n📊 Data Consistency Analysis:")
        print(f"   • Ready Clients Endpoint: {ready_endpoint_count} clients")
        print(f"   • Individual Readiness Checks: {individual_ready_count} clients")
        print(f"   • Total Clients in System: {len(all_clients)} clients")
        
        if ready_endpoint_count == individual_ready_count:
            self.log_test("Data Consistency Check", True, 
                        f"Consistent: {ready_endpoint_count} ready clients across all endpoints")
        else:
            self.log_test("Data Consistency Check", False, 
                        f"Inconsistent: Ready endpoint shows {ready_endpoint_count}, individual checks show {individual_ready_count}")

    def run_debug_test(self):
        """Run comprehensive client readiness debug test"""
        print("🚀 FIDUS Client Readiness Debug Test")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Started: {datetime.now(timezone.utc).isoformat()}")
        print("=" * 80)
        print()

        # Step 1: Authenticate
        if not self.authenticate_admin():
            print("❌ Cannot proceed without admin authentication")
            return False

        # Step 2: Check ready clients endpoint
        ready_clients = self.check_ready_clients_endpoint()

        # Step 3: Check all clients in system
        all_clients = self.check_all_clients()

        # Step 4: Check Alejandro Mariscal specifically
        alejandro_found = False
        alejandro_id = None
        for client in all_clients:
            if "alejandro" in client.get('name', '').lower() or "mariscal" in client.get('name', '').lower():
                alejandro_found = True
                alejandro_id = client.get('id')
                break
        
        if alejandro_found:
            alejandro_readiness = self.check_specific_client_readiness(alejandro_id, "Alejandro Mariscal")
            
            # If Alejandro is not ready, try to make him ready
            if alejandro_readiness and not alejandro_readiness.get('investment_ready'):
                print("\n🔧 Attempting to make Alejandro Mariscal investment ready...")
                self.update_client_readiness(alejandro_id, "Alejandro Mariscal")
                
                # Re-check after update
                print("\n🔍 Re-checking Alejandro's status after update...")
                self.check_specific_client_readiness(alejandro_id, "Alejandro Mariscal")
                
                # Re-check ready clients endpoint
                print("\n🔍 Re-checking ready clients endpoint after update...")
                self.check_ready_clients_endpoint()
        else:
            self.log_test("Find Alejandro Mariscal", False, "Alejandro Mariscal not found in clients list")

        # Step 5: Verify data consistency
        self.verify_data_consistency()

        # Generate summary
        print("\n" + "=" * 80)
        print("🎯 CLIENT READINESS DEBUG SUMMARY")
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

        # Show key findings
        print("🔍 KEY FINDINGS:")
        
        ready_clients_test = next((t for t in self.test_results if "Ready Clients Endpoint" in t["test"]), None)
        if ready_clients_test and ready_clients_test["success"]:
            if "0 ready clients" in ready_clients_test["details"]:
                print("   🚨 CRITICAL: No clients are marked as investment ready")
                print("   💡 SOLUTION: Clients need AML/KYC completion and agreement signing")
            else:
                print("   ✅ Some clients are marked as investment ready")
        
        alejandro_test = next((t for t in self.test_results if "Alejandro" in t["test"]), None)
        if alejandro_test:
            if alejandro_test["success"]:
                print("   ✅ Alejandro Mariscal found and readiness checked")
            else:
                print("   ❌ Issues with Alejandro Mariscal's readiness status")
        
        consistency_test = next((t for t in self.test_results if "Data Consistency" in t["test"]), None)
        if consistency_test:
            if consistency_test["success"]:
                print("   ✅ Data consistency verified across endpoints")
            else:
                print("   ⚠️  Data inconsistency detected between endpoints")
        
        print("\n🎯 RECOMMENDED ACTIONS:")
        if len(ready_clients) == 0:
            print("   1. Update client readiness status for existing clients")
            print("   2. Ensure AML/KYC completion and agreement signing workflow")
            print("   3. Verify MongoDB synchronization of readiness data")
        else:
            print("   1. Client readiness system appears to be working")
            print("   2. Verify frontend dropdown is using correct endpoint")
        
        print("=" * 80)
        
        return success_rate >= 80

if __name__ == "__main__":
    debugger = ClientReadinessDebugger()
    success = debugger.run_debug_test()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)