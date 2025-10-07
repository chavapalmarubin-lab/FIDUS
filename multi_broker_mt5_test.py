#!/usr/bin/env python3
"""
Multi-Broker MT5 Integration Testing Suite
Tests the new multi-broker MT5 system implementation for FIDUS Investment Management

Test Coverage:
- Priority 1: Broker Management APIs
- Priority 2: Multi-Broker Account Management  
- Priority 3: Existing MT5 APIs (regression testing)
"""

import requests
import json
import sys
import time
from datetime import datetime
from typing import Dict, Any, List

# Backend URL from environment
BACKEND_URL = "https://investor-dash-1.preview.emergentagent.com/api"

class MT5MultibrokerTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
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
            "timestamp": datetime.now().isoformat()
        }
        
        if response_data:
            result["response_data"] = response_data
            
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"    Details: {details}")
        if not success and response_data:
            print(f"    Response: {json.dumps(response_data, indent=2)}")
        print()

    def authenticate_admin(self) -> bool:
        """Authenticate as admin to get JWT token"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "username": "admin",
                "password": "password123", 
                "user_type": "admin"
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                if self.admin_token:
                    # Set authorization header for all future requests
                    self.session.headers.update({
                        "Authorization": f"Bearer {self.admin_token}"
                    })
                    self.log_test("Admin Authentication", True, f"Successfully authenticated as admin")
                    return True
                else:
                    self.log_test("Admin Authentication", False, "No token received in response", data)
                    return False
            else:
                self.log_test("Admin Authentication", False, f"HTTP {response.status_code}", response.json())
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False

    def test_priority_1_broker_management(self):
        """Priority 1: Test Broker Management APIs"""
        print("🎯 PRIORITY 1: BROKER MANAGEMENT APIs")
        print("=" * 60)
        
        # Test 1.1: GET /api/mt5/brokers - Get list of available brokers
        try:
            response = self.session.get(f"{BACKEND_URL}/mt5/brokers")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success") and "brokers" in data:
                    brokers = data["brokers"]
                    broker_codes = [broker.get("code") for broker in brokers]
                    
                    # Check if required brokers are present
                    has_multibank = "multibank" in broker_codes
                    has_dootechnology = "dootechnology" in broker_codes
                    
                    if has_multibank and has_dootechnology:
                        self.log_test("Get Available Brokers", True, 
                                    f"Found {len(brokers)} brokers including Multibank and DooTechnology", data)
                    else:
                        missing = []
                        if not has_multibank:
                            missing.append("Multibank")
                        if not has_dootechnology:
                            missing.append("DooTechnology")
                        self.log_test("Get Available Brokers", False, 
                                    f"Missing required brokers: {', '.join(missing)}", data)
                else:
                    self.log_test("Get Available Brokers", False, "Invalid response structure", data)
            else:
                self.log_test("Get Available Brokers", False, f"HTTP {response.status_code}", response.json())
                
        except Exception as e:
            self.log_test("Get Available Brokers", False, f"Exception: {str(e)}")

        # Test 1.2: GET /api/mt5/brokers/dootechnology/servers - Get DooTechnology servers
        try:
            response = self.session.get(f"{BACKEND_URL}/mt5/brokers/dootechnology/servers")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success") and "servers" in data:
                    servers = data["servers"]
                    has_live_server = "DooTechnology-Live" in servers
                    
                    if has_live_server:
                        self.log_test("Get DooTechnology Servers", True, 
                                    f"Found {len(servers)} servers including DooTechnology-Live", data)
                    else:
                        self.log_test("Get DooTechnology Servers", False, 
                                    "DooTechnology-Live server not found in server list", data)
                else:
                    self.log_test("Get DooTechnology Servers", False, "Invalid response structure", data)
            else:
                self.log_test("Get DooTechnology Servers", False, f"HTTP {response.status_code}", response.json())
                
        except Exception as e:
            self.log_test("Get DooTechnology Servers", False, f"Exception: {str(e)}")

        # Test 1.3: GET /api/mt5/brokers/multibank/servers - Get Multibank servers
        try:
            response = self.session.get(f"{BACKEND_URL}/mt5/brokers/multibank/servers")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success") and "servers" in data:
                    servers = data["servers"]
                    self.log_test("Get Multibank Servers", True, 
                                f"Found {len(servers)} Multibank servers", data)
                else:
                    self.log_test("Get Multibank Servers", False, "Invalid response structure", data)
            else:
                self.log_test("Get Multibank Servers", False, f"HTTP {response.status_code}", response.json())
                
        except Exception as e:
            self.log_test("Get Multibank Servers", False, f"Exception: {str(e)}")

    def test_priority_2_account_management(self):
        """Priority 2: Test Multi-Broker Account Management"""
        print("🎯 PRIORITY 2: MULTI-BROKER ACCOUNT MANAGEMENT")
        print("=" * 60)
        
        # Test 2.1: POST /api/mt5/admin/add-manual-account - Add DooTechnology client
        try:
            # Test data as specified in the review request
            account_data = {
                "client_id": "client_001",  # Using existing client (Gerardo Briones)
                "fund_code": "CORE",
                "broker_code": "dootechnology",
                "mt5_login": 9928326,
                "mt5_password": "R1d567j!",
                "mt5_server": "DooTechnology-Live",
                "allocated_amount": 100000.00
            }
            
            response = self.session.post(f"{BACKEND_URL}/mt5/admin/add-manual-account", json=account_data)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success") and "account_id" in data:
                    account_id = data["account_id"]
                    self.log_test("Add DooTechnology Manual Account", True, 
                                f"Successfully created MT5 account {account_id} for client_001", data)
                    
                    # Store account_id for later tests
                    self.created_account_id = account_id
                else:
                    self.log_test("Add DooTechnology Manual Account", False, "Invalid response structure", data)
            else:
                self.log_test("Add DooTechnology Manual Account", False, f"HTTP {response.status_code}", response.json())
                
        except Exception as e:
            self.log_test("Add DooTechnology Manual Account", False, f"Exception: {str(e)}")

        # Test 2.2: GET /api/mt5/admin/accounts/by-broker - Get accounts grouped by broker
        try:
            response = self.session.get(f"{BACKEND_URL}/mt5/admin/accounts/by-broker")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success") and "accounts_by_broker" in data:
                    accounts_by_broker = data["accounts_by_broker"]
                    
                    # Check if we have both brokers represented
                    has_multibank = "multibank" in accounts_by_broker
                    has_dootechnology = "dootechnology" in accounts_by_broker
                    
                    broker_count = len(accounts_by_broker)
                    total_accounts = sum(len(broker_data.get("accounts", [])) for broker_data in accounts_by_broker.values())
                    
                    if has_dootechnology:
                        doo_accounts = len(accounts_by_broker["dootechnology"].get("accounts", []))
                        self.log_test("Get Accounts by Broker", True, 
                                    f"Found {broker_count} brokers with {total_accounts} total accounts. DooTechnology: {doo_accounts} accounts", data)
                    else:
                        self.log_test("Get Accounts by Broker", False, 
                                    f"DooTechnology broker not found in grouped accounts", data)
                else:
                    self.log_test("Get Accounts by Broker", False, "Invalid response structure", data)
            else:
                self.log_test("Get Accounts by Broker", False, f"HTTP {response.status_code}", response.json())
                
        except Exception as e:
            self.log_test("Get Accounts by Broker", False, f"Exception: {str(e)}")

    def test_priority_3_regression_testing(self):
        """Priority 3: Test Existing MT5 APIs (ensure no regression)"""
        print("🎯 PRIORITY 3: EXISTING MT5 APIs (REGRESSION TESTING)")
        print("=" * 60)
        
        # Test 3.1: GET /api/mt5/admin/accounts - Test getting all MT5 accounts still works
        try:
            response = self.session.get(f"{BACKEND_URL}/mt5/admin/accounts")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success") and "accounts" in data and "summary" in data:
                    accounts = data["accounts"]
                    summary = data["summary"]
                    
                    account_count = len(accounts)
                    total_allocated = summary.get("total_allocated", 0)
                    total_equity = summary.get("total_equity", 0)
                    
                    self.log_test("Get All MT5 Accounts", True, 
                                f"Found {account_count} accounts with ${total_allocated:,.2f} allocated, ${total_equity:,.2f} equity", data)
                else:
                    self.log_test("Get All MT5 Accounts", False, "Invalid response structure", data)
            else:
                self.log_test("Get All MT5 Accounts", False, f"HTTP {response.status_code}", response.json())
                
        except Exception as e:
            self.log_test("Get All MT5 Accounts", False, f"Exception: {str(e)}")

        # Test 3.2: GET /api/mt5/admin/performance/overview - Test performance overview still works
        try:
            response = self.session.get(f"{BACKEND_URL}/mt5/admin/performance/overview")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success"):
                    # Check for expected performance data structure
                    has_performance_data = any(key in data for key in ["total_accounts", "total_equity", "total_profit", "fund_performance"])
                    
                    if has_performance_data:
                        total_accounts = data.get("total_accounts", 0)
                        total_equity = data.get("total_equity", 0)
                        total_profit = data.get("total_profit", 0)
                        
                        self.log_test("Get MT5 Performance Overview", True, 
                                    f"Performance overview working: {total_accounts} accounts, ${total_equity:,.2f} equity, ${total_profit:,.2f} profit", data)
                    else:
                        self.log_test("Get MT5 Performance Overview", False, "Missing expected performance data fields", data)
                else:
                    self.log_test("Get MT5 Performance Overview", False, "Response indicates failure", data)
            else:
                self.log_test("Get MT5 Performance Overview", False, f"HTTP {response.status_code}", response.json())
                
        except Exception as e:
            self.log_test("Get MT5 Performance Overview", False, f"Exception: {str(e)}")

    def test_database_integration(self):
        """Test database integration and data consistency"""
        print("🎯 ADDITIONAL: DATABASE INTEGRATION VERIFICATION")
        print("=" * 60)
        
        # Test: Verify no database errors or connection issues
        try:
            # Test health endpoint to verify database connectivity
            response = self.session.get(f"{BACKEND_URL}/health/ready")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("status") == "ready" and data.get("checks", {}).get("database"):
                    self.log_test("Database Connection Health", True, "Database connectivity verified", data)
                else:
                    self.log_test("Database Connection Health", False, "Database not ready", data)
            else:
                self.log_test("Database Connection Health", False, f"Health check failed: HTTP {response.status_code}", response.json())
                
        except Exception as e:
            self.log_test("Database Connection Health", False, f"Exception: {str(e)}")

    def run_comprehensive_test(self):
        """Run all multi-broker MT5 integration tests"""
        print("🚀 MULTI-BROKER MT5 INTEGRATION COMPREHENSIVE TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Start Time: {datetime.now().isoformat()}")
        print("=" * 80)
        print()
        
        # Step 1: Authenticate
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with MT5 tests.")
            return False
        
        # Step 2: Run Priority Tests
        self.test_priority_1_broker_management()
        self.test_priority_2_account_management()
        self.test_priority_3_regression_testing()
        self.test_database_integration()
        
        # Step 3: Generate Summary
        self.generate_test_summary()
        
        return self.passed_tests == self.total_tests

    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("=" * 80)
        print("🎯 MULTI-BROKER MT5 INTEGRATION TEST SUMMARY")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Group results by priority
        priority_1_tests = [r for r in self.test_results if any(keyword in r["test"] for keyword in ["Brokers", "Servers"])]
        priority_2_tests = [r for r in self.test_results if any(keyword in r["test"] for keyword in ["Manual Account", "by Broker"])]
        priority_3_tests = [r for r in self.test_results if any(keyword in r["test"] for keyword in ["All MT5", "Performance Overview"])]
        
        print("📊 RESULTS BY PRIORITY:")
        print()
        
        print("Priority 1 - Broker Management APIs:")
        for test in priority_1_tests:
            print(f"  {test['status']}: {test['test']}")
        print()
        
        print("Priority 2 - Multi-Broker Account Management:")
        for test in priority_2_tests:
            print(f"  {test['status']}: {test['test']}")
        print()
        
        print("Priority 3 - Existing MT5 APIs (Regression):")
        for test in priority_3_tests:
            print(f"  {test['status']}: {test['test']}")
        print()
        
        # Show failed tests with details
        failed_tests = [r for r in self.test_results if not r["success"]]
        if failed_tests:
            print("❌ FAILED TESTS DETAILS:")
            print("-" * 40)
            for test in failed_tests:
                print(f"Test: {test['test']}")
                print(f"Details: {test['details']}")
                print()
        
        # Overall assessment
        if success_rate >= 90:
            print("🎉 OVERALL ASSESSMENT: EXCELLENT - Multi-broker MT5 system is working correctly!")
        elif success_rate >= 75:
            print("✅ OVERALL ASSESSMENT: GOOD - Multi-broker MT5 system is mostly functional with minor issues")
        elif success_rate >= 50:
            print("⚠️  OVERALL ASSESSMENT: NEEDS ATTENTION - Multi-broker MT5 system has significant issues")
        else:
            print("❌ OVERALL ASSESSMENT: CRITICAL - Multi-broker MT5 system requires immediate fixes")
        
        print("=" * 80)

def main():
    """Main test execution"""
    tester = MT5MultibrokerTester()
    
    try:
        success = tester.run_comprehensive_test()
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️ Test execution interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Critical error during test execution: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()