#!/usr/bin/env python3
"""
MOCK_USERS DEPENDENCY CRITICAL TEST
===================================

This test specifically checks the endpoints that reference MOCK_USERS
to determine if they will fail when MOCK_USERS is removed.
"""

import requests
import json
import sys
from datetime import datetime

BACKEND_URL = "https://fidus-invest.emergent.host/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class MockUsersDependencyTest:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name} - {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "username": ADMIN_USERNAME,
                "password": ADMIN_PASSWORD,
                "user_type": "admin"
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                if self.admin_token:
                    self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
                    return True
            return False
        except Exception as e:
            return False
    
    def test_client_data_endpoint(self):
        """Test /client/{client_id}/data endpoint that references MOCK_USERS"""
        try:
            response = self.session.get(f"{BACKEND_URL}/client/client_003/data")
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("Client Data Endpoint (MOCK_USERS ref)", True, 
                              "Endpoint working despite MOCK_USERS reference", 
                              {"response_keys": list(data.keys())})
            elif response.status_code == 500:
                self.log_result("Client Data Endpoint (MOCK_USERS ref)", False, 
                              "Endpoint failing due to MOCK_USERS dependency", 
                              {"status_code": response.status_code, "response": response.text[:200]})
            else:
                self.log_result("Client Data Endpoint (MOCK_USERS ref)", False, 
                              f"Unexpected status code: {response.status_code}", 
                              {"response": response.text[:200]})
                
        except Exception as e:
            self.log_result("Client Data Endpoint (MOCK_USERS ref)", False, 
                          f"Exception: {str(e)}")
    
    def test_mt5_accounts_endpoint(self):
        """Test MT5 accounts endpoint that references MOCK_USERS"""
        try:
            response = self.session.get(f"{BACKEND_URL}/mt5/accounts")
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("MT5 Accounts Endpoint (MOCK_USERS ref)", True, 
                              "MT5 endpoint working despite MOCK_USERS reference", 
                              {"account_count": len(data.get("accounts", []))})
            elif response.status_code == 500:
                self.log_result("MT5 Accounts Endpoint (MOCK_USERS ref)", False, 
                              "MT5 endpoint failing due to MOCK_USERS dependency", 
                              {"status_code": response.status_code, "response": response.text[:200]})
            else:
                self.log_result("MT5 Accounts Endpoint (MOCK_USERS ref)", False, 
                              f"Unexpected status code: {response.status_code}", 
                              {"response": response.text[:200]})
                
        except Exception as e:
            self.log_result("MT5 Accounts Endpoint (MOCK_USERS ref)", False, 
                          f"Exception: {str(e)}")
    
    def test_fund_allocations_endpoint(self):
        """Test fund allocations endpoint that references MOCK_USERS"""
        try:
            response = self.session.get(f"{BACKEND_URL}/fund-portfolio/overview")
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("Fund Allocations Endpoint (MOCK_USERS ref)", True, 
                              "Fund allocations endpoint working despite MOCK_USERS reference", 
                              {"data_keys": list(data.keys())})
            elif response.status_code == 500:
                self.log_result("Fund Allocations Endpoint (MOCK_USERS ref)", False, 
                              "Fund allocations endpoint failing due to MOCK_USERS dependency", 
                              {"status_code": response.status_code, "response": response.text[:200]})
            else:
                self.log_result("Fund Allocations Endpoint (MOCK_USERS ref)", False, 
                              f"Unexpected status code: {response.status_code}", 
                              {"response": response.text[:200]})
                
        except Exception as e:
            self.log_result("Fund Allocations Endpoint (MOCK_USERS ref)", False, 
                          f"Exception: {str(e)}")
    
    def test_all_clients_details_endpoint(self):
        """Test all clients details endpoint that references MOCK_USERS"""
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/clients/details")
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("All Clients Details Endpoint (MOCK_USERS ref)", True, 
                              "Clients details endpoint working despite MOCK_USERS reference", 
                              {"client_count": len(data.get("clients", []))})
            elif response.status_code == 500:
                self.log_result("All Clients Details Endpoint (MOCK_USERS ref)", False, 
                              "Clients details endpoint failing due to MOCK_USERS dependency", 
                              {"status_code": response.status_code, "response": response.text[:200]})
            else:
                self.log_result("All Clients Details Endpoint (MOCK_USERS ref)", False, 
                              f"Unexpected status code: {response.status_code}", 
                              {"response": response.text[:200]})
                
        except Exception as e:
            self.log_result("All Clients Details Endpoint (MOCK_USERS ref)", False, 
                          f"Exception: {str(e)}")
    
    def run_dependency_tests(self):
        """Run all MOCK_USERS dependency tests"""
        print("🚨 MOCK_USERS DEPENDENCY CRITICAL TEST")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed.")
            return False
        
        print("🔍 Testing endpoints with MOCK_USERS references...")
        print("-" * 50)
        
        self.test_client_data_endpoint()
        self.test_mt5_accounts_endpoint()
        self.test_fund_allocations_endpoint()
        self.test_all_clients_details_endpoint()
        
        self.generate_dependency_summary()
        
        return True
    
    def generate_dependency_summary(self):
        """Generate dependency test summary"""
        print("\n" + "=" * 60)
        print("🚨 MOCK_USERS DEPENDENCY TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Endpoints Tested: {total_tests}")
        print(f"Working Despite MOCK_USERS References: {passed_tests}")
        print(f"Failing Due to MOCK_USERS Dependencies: {failed_tests}")
        print()
        
        if failed_tests > 0:
            print("❌ CRITICAL DEPENDENCIES FOUND:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['message']}")
            print()
            print("🚨 DEPLOYMENT RISK: These endpoints will fail when MOCK_USERS is removed!")
        else:
            print("✅ NO CRITICAL DEPENDENCIES DETECTED:")
            for result in self.test_results:
                if result['success']:
                    print(f"   • {result['test']}: {result['message']}")
            print()
            print("✅ SAFE TO REMOVE: Endpoints working without MOCK_USERS data")
        
        print("=" * 60)

def main():
    """Main test execution"""
    test_runner = MockUsersDependencyTest()
    success = test_runner.run_dependency_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()