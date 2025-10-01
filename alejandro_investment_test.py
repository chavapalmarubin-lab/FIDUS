#!/usr/bin/env python3
"""
ALEJANDRO MARISCAL INVESTMENT CREATION CRITICAL TEST
==================================================

CRITICAL PRODUCTION ISSUE: Investment creation failing for Alejandro Mariscal with $18,151.41 investment.

This test focuses on debugging the specific investment creation failure:
- Client ID: alejandrom (alejandro.mariscal@email.com)
- Amount: 18151.41
- Fund: FIDUS Core Fund
- Payment Method: Crypto Currency
- Transaction Hash: 5b6d2c28e60af70552418d040d6c5a18de1f1ee55ba71cf4397386ffd6f957c
- Date: 2025-10-01

Test Objectives:
1. Verify POST /api/investments endpoint exists and is accessible
2. Test authentication requirements
3. Verify client exists in database
4. Test investment creation with Alejandro's exact data
5. Check MongoDB Atlas connectivity for investments collection
6. Verify fund configuration exists
7. Test MT5 account mapping functionality

Expected Results:
- Investment creation should succeed
- Return investment ID and confirmation
- Update client's investment records
- Create MT5 account mapping
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration - Use production backend URL
BACKEND_URL = "https://fidus-invest.emergent.host/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

# Alejandro's investment data from the critical issue
ALEJANDRO_INVESTMENT_DATA = {
    "client_id": "alejandrom",  # This might need to be mapped to actual client ID
    "fund_code": "CORE",  # FIDUS Core Fund
    "amount": 18151.41,
    "deposit_date": "2025-10-01",
    "broker_code": "multibank",
    "create_mt5_account": True,
    "mt5_login": None,
    "mt5_password": None,
    "mt5_server": None,
    "broker_name": "Multibank",
    "mt5_initial_balance": 18151.41,
    "banking_fees": 0.0,
    "fee_notes": "Crypto Currency Payment - Transaction Hash: 5b6d2c28e60af70552418d040d6c5a18de1f1ee55ba71cf4397386ffd6f957c"
}

class AlejandroInvestmentTest:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        self.alejandro_client_id = None
        
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
            print(f"   Details: {json.dumps(details, indent=2)}")
    
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
                    self.log_result("Admin Authentication", True, "Successfully authenticated as admin")
                    return True
                else:
                    self.log_result("Admin Authentication", False, "No token received", {"response": data})
                    return False
            else:
                self.log_result("Admin Authentication", False, f"HTTP {response.status_code}", {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_backend_connectivity(self):
        """Test basic backend connectivity"""
        try:
            response = self.session.get(f"{BACKEND_URL}/health")
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("Backend Connectivity", True, "Backend is healthy and accessible", {"health_data": data})
                return True
            else:
                self.log_result("Backend Connectivity", False, f"Backend health check failed: HTTP {response.status_code}", {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Backend Connectivity", False, f"Cannot connect to backend: {str(e)}")
            return False
    
    def find_alejandro_client(self):
        """Find Alejandro's client record in the database"""
        try:
            # Try to get all users/clients to find Alejandro
            response = self.session.get(f"{BACKEND_URL}/admin/users")
            
            if response.status_code == 200:
                data = response.json()
                users = data.get("users", [])
                
                # Look for Alejandro by email or name
                alejandro_candidates = []
                for user in users:
                    if ("alejandro" in user.get("name", "").lower() or 
                        "alejandro.mariscal@email.com" in user.get("email", "") or
                        "alexmar7609@gmail.com" in user.get("email", "") or
                        "alejandrom" in user.get("username", "")):
                        alejandro_candidates.append(user)
                
                if alejandro_candidates:
                    # Use the first match
                    alejandro = alejandro_candidates[0]
                    self.alejandro_client_id = alejandro.get("id")
                    self.log_result("Find Alejandro Client", True, 
                                  f"Found Alejandro client: {alejandro.get('name')} ({alejandro.get('email')})",
                                  {"client_id": self.alejandro_client_id, "client_data": alejandro})
                    return True
                else:
                    self.log_result("Find Alejandro Client", False, 
                                  "Alejandro client not found in database",
                                  {"total_users": len(users), "searched_for": ["alejandro", "alejandro.mariscal@email.com", "alexmar7609@gmail.com"]})
                    return False
            else:
                self.log_result("Find Alejandro Client", False, f"Failed to get users list: HTTP {response.status_code}", {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Find Alejandro Client", False, f"Exception: {str(e)}")
            return False
    
    def test_investments_endpoint_exists(self):
        """Test if POST /api/investments/create endpoint exists"""
        try:
            # Test with invalid data to see if endpoint exists
            response = self.session.post(f"{BACKEND_URL}/investments/create", json={})
            
            if response.status_code == 422:  # Validation error means endpoint exists
                self.log_result("Investments Endpoint Exists", True, "POST /api/investments/create endpoint exists (validation error expected)")
                return True
            elif response.status_code == 404:
                self.log_result("Investments Endpoint Exists", False, "POST /api/investments/create endpoint not found")
                return False
            elif response.status_code == 401:
                self.log_result("Investments Endpoint Exists", True, "POST /api/investments/create endpoint exists (authentication required)")
                return True
            else:
                self.log_result("Investments Endpoint Exists", True, f"POST /api/investments/create endpoint exists (HTTP {response.status_code})")
                return True
                
        except Exception as e:
            self.log_result("Investments Endpoint Exists", False, f"Exception: {str(e)}")
            return False
    
    def test_fund_configuration(self):
        """Test if FIDUS Core Fund configuration exists"""
        try:
            # Try to get fund configurations or information
            response = self.session.get(f"{BACKEND_URL}/funds")
            
            if response.status_code == 200:
                data = response.json()
                funds = data.get("funds", [])
                
                # Look for CORE fund
                core_fund = None
                for fund in funds:
                    if fund.get("fund_code") == "CORE" or "Core" in fund.get("name", ""):
                        core_fund = fund
                        break
                
                if core_fund:
                    self.log_result("Fund Configuration", True, 
                                  f"FIDUS Core Fund configuration found: {core_fund.get('name')}",
                                  {"fund_config": core_fund})
                    return True
                else:
                    self.log_result("Fund Configuration", False, 
                                  "FIDUS Core Fund configuration not found",
                                  {"available_funds": [f.get("fund_code") for f in funds]})
                    return False
            elif response.status_code == 404:
                # Try alternative endpoint
                self.log_result("Fund Configuration", False, "Funds endpoint not found - will test with investment creation")
                return True  # Continue with test
            else:
                self.log_result("Fund Configuration", False, f"Failed to get fund configurations: HTTP {response.status_code}")
                return True  # Continue with test
                
        except Exception as e:
            self.log_result("Fund Configuration", False, f"Exception: {str(e)}")
            return True  # Continue with test
    
    def test_mongodb_connectivity(self):
        """Test MongoDB Atlas connectivity"""
        try:
            # Test database connectivity through a simple endpoint
            response = self.session.get(f"{BACKEND_URL}/admin/users")
            
            if response.status_code == 200:
                data = response.json()
                users = data.get("users", [])
                self.log_result("MongoDB Connectivity", True, 
                              f"MongoDB Atlas connection working - found {len(users)} users",
                              {"user_count": len(users)})
                return True
            else:
                self.log_result("MongoDB Connectivity", False, f"Database connectivity issue: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("MongoDB Connectivity", False, f"Exception: {str(e)}")
            return False
    
    def test_investment_creation_with_alejandro_data(self):
        """Test investment creation with Alejandro's exact data"""
        if not self.alejandro_client_id:
            self.log_result("Investment Creation", False, "Cannot test - Alejandro client ID not found")
            return False
        
        try:
            # Prepare investment data with correct client ID
            investment_data = ALEJANDRO_INVESTMENT_DATA.copy()
            investment_data["client_id"] = self.alejandro_client_id
            
            print(f"🎯 Testing investment creation with data: {json.dumps(investment_data, indent=2)}")
            
            response = self.session.post(f"{BACKEND_URL}/investments/create", json=investment_data)
            
            if response.status_code == 200 or response.status_code == 201:
                data = response.json()
                investment_id = data.get("investment_id") or data.get("id")
                
                if investment_id:
                    self.log_result("Investment Creation", True, 
                                  f"Investment created successfully: {investment_id}",
                                  {"investment_data": data, "original_request": investment_data})
                    return True
                else:
                    self.log_result("Investment Creation", False, 
                                  "Investment creation response missing investment ID",
                                  {"response": data, "original_request": investment_data})
                    return False
            else:
                try:
                    error_data = response.json()
                except:
                    error_data = {"raw_response": response.text}
                
                self.log_result("Investment Creation", False, 
                              f"Investment creation failed: HTTP {response.status_code}",
                              {"error_response": error_data, "original_request": investment_data})
                return False
                
        except Exception as e:
            self.log_result("Investment Creation", False, f"Exception during investment creation: {str(e)}")
            return False
    
    def test_mt5_account_mapping(self):
        """Test MT5 account mapping functionality"""
        try:
            # Try to get MT5 accounts for the client
            if not self.alejandro_client_id:
                self.log_result("MT5 Account Mapping", False, "Cannot test - Alejandro client ID not found")
                return False
            
            response = self.session.get(f"{BACKEND_URL}/clients/{self.alejandro_client_id}/mt5-accounts")
            
            if response.status_code == 200:
                data = response.json()
                mt5_accounts = data.get("mt5_accounts", [])
                self.log_result("MT5 Account Mapping", True, 
                              f"MT5 accounts endpoint accessible - found {len(mt5_accounts)} accounts",
                              {"mt5_accounts": mt5_accounts})
                return True
            elif response.status_code == 404:
                self.log_result("MT5 Account Mapping", False, "MT5 accounts endpoint not found")
                return False
            else:
                self.log_result("MT5 Account Mapping", False, f"MT5 accounts endpoint error: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("MT5 Account Mapping", False, f"Exception: {str(e)}")
            return False
    
    def test_client_investments_retrieval(self):
        """Test retrieving client investments after creation"""
        if not self.alejandro_client_id:
            self.log_result("Client Investments Retrieval", False, "Cannot test - Alejandro client ID not found")
            return False
        
        try:
            response = self.session.get(f"{BACKEND_URL}/clients/{self.alejandro_client_id}/investments")
            
            if response.status_code == 200:
                data = response.json()
                investments = data.get("investments", [])
                
                # Look for the investment we just created
                core_investments = [inv for inv in investments if inv.get("fund_code") == "CORE"]
                
                self.log_result("Client Investments Retrieval", True, 
                              f"Client investments accessible - found {len(investments)} total, {len(core_investments)} CORE fund",
                              {"total_investments": len(investments), "core_investments": len(core_investments)})
                return True
            else:
                self.log_result("Client Investments Retrieval", False, f"Failed to get client investments: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Client Investments Retrieval", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all investment creation tests for Alejandro"""
        print("🚨 ALEJANDRO MARISCAL INVESTMENT CREATION CRITICAL TEST")
        print("=" * 70)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print(f"Investment Amount: ${ALEJANDRO_INVESTMENT_DATA['amount']}")
        print(f"Fund: FIDUS Core Fund")
        print(f"Payment Method: Crypto Currency")
        print()
        
        # Test basic connectivity first
        print("🔍 Testing Backend Connectivity...")
        print("-" * 50)
        if not self.test_backend_connectivity():
            print("❌ CRITICAL: Backend connectivity failed. Cannot proceed.")
            return False
        
        # Authenticate
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed.")
            return False
        
        print("\n🔍 Running Investment Creation Tests...")
        print("-" * 50)
        
        # Run all tests
        self.test_mongodb_connectivity()
        self.find_alejandro_client()
        self.test_investments_endpoint_exists()
        self.test_fund_configuration()
        self.test_investment_creation_with_alejandro_data()
        self.test_mt5_account_mapping()
        self.test_client_investments_retrieval()
        
        # Generate summary
        self.generate_test_summary()
        
        return True
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 70)
        print("🚨 ALEJANDRO INVESTMENT CREATION TEST SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Show failed tests first (critical issues)
        if failed_tests > 0:
            print("❌ CRITICAL ISSUES FOUND:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['message']}")
                    if result.get('details'):
                        # Show key error details
                        details = result['details']
                        if 'error_response' in details:
                            print(f"     Error: {details['error_response']}")
                        elif 'response' in details:
                            print(f"     Response: {details['response']}")
            print()
        
        # Show passed tests
        if passed_tests > 0:
            print("✅ WORKING COMPONENTS:")
            for result in self.test_results:
                if result['success']:
                    print(f"   • {result['test']}: {result['message']}")
            print()
        
        # Critical assessment
        critical_tests = [
            "Backend Connectivity",
            "Admin Authentication", 
            "Find Alejandro Client",
            "Investments Endpoint Exists",
            "Investment Creation"
        ]
        
        critical_passed = sum(1 for result in self.test_results 
                            if result['success'] and any(critical in result['test'] for critical in critical_tests))
        
        print("🚨 CRITICAL ASSESSMENT:")
        if critical_passed >= 4 and any(r['test'] == 'Investment Creation' and r['success'] for r in self.test_results):
            print("✅ INVESTMENT CREATION: WORKING")
            print("   Alejandro's investment creation is functional.")
            print("   The reported issue may be resolved or was a temporary problem.")
        elif any(r['test'] == 'Investment Creation' and not r['success'] for r in self.test_results):
            print("❌ INVESTMENT CREATION: FAILING")
            print("   Alejandro's investment creation is broken.")
            print("   URGENT: Main agent action required to fix investment endpoint.")
            
            # Find the investment creation failure details
            for result in self.test_results:
                if result['test'] == 'Investment Creation' and not result['success']:
                    print(f"   Root Cause: {result['message']}")
                    if result.get('details', {}).get('error_response'):
                        print(f"   Error Details: {result['details']['error_response']}")
        else:
            print("❌ INVESTMENT CREATION: CANNOT TEST")
            print("   Prerequisites failed - cannot test investment creation.")
            print("   Fix backend connectivity, authentication, or client lookup first.")
        
        print("\n" + "=" * 70)

def main():
    """Main test execution"""
    test_runner = AlejandroInvestmentTest()
    success = test_runner.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()