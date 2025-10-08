#!/usr/bin/env python3
"""
ALEJANDRO MARISCAL CRITICAL PRODUCTION VERIFICATION TEST
Testing the critical endpoints for Alejandro Mariscal production setup.
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from frontend/.env
BACKEND_URL = "https://trading-platform-76.preview.emergentagent.com/api"

class AlejandroCriticalTest:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, details, response_data=None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        
        if response_data and not success:
            print(f"   Response: {json.dumps(response_data, indent=2)}")
    
    def test_admin_authentication(self):
        """Test 1: Admin Authentication Test"""
        try:
            login_data = {
                "username": "admin",
                "password": "password123",
                "user_type": "admin"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("token"):
                    self.admin_token = data["token"]
                    self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
                    self.log_test("Admin Authentication", True, f"Successfully authenticated as {data.get('name', 'admin')}")
                    return True
                else:
                    self.log_test("Admin Authentication", False, "No JWT token returned", data)
                    return False
            else:
                self.log_test("Admin Authentication", False, f"HTTP {response.status_code}: {response.text[:200]}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test("Admin Authentication", False, f"Connection error: {str(e)}")
            return False
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_ready_for_investment_endpoint(self):
        """Test 2: Ready for Investment Endpoint (FIXED)"""
        if not self.admin_token:
            self.log_test("Ready for Investment Endpoint", False, "No admin token available")
            return False
            
        try:
            response = self.session.get(f"{BACKEND_URL}/clients/ready-for-investment", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                ready_clients = data.get("ready_clients", [])
                
                # Check if Alejandro is in the list
                alejandro_found = False
                for client in ready_clients:
                    if ("alejandro" in client.get("name", "").lower() or 
                        "client_alejandro" in client.get("client_id", "") or
                        "alexmar7609@gmail.com" in client.get("email", "")):
                        alejandro_found = True
                        break
                
                if alejandro_found:
                    self.log_test("Ready for Investment Endpoint", True, f"Alejandro found in ready clients list (Total: {data.get('total_ready', 0)})")
                    return True
                else:
                    self.log_test("Ready for Investment Endpoint", False, f"Alejandro NOT found in ready clients list (Total: {data.get('total_ready', 0)})", data)
                    return False
            else:
                self.log_test("Ready for Investment Endpoint", False, f"HTTP {response.status_code}: {response.text[:200]}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test("Ready for Investment Endpoint", False, f"Connection error: {str(e)}")
            return False
        except Exception as e:
            self.log_test("Ready for Investment Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_individual_client_readiness(self):
        """Test 3: Individual Client Readiness"""
        if not self.admin_token:
            self.log_test("Individual Client Readiness", False, "No admin token available")
            return False
            
        try:
            response = self.session.get(f"{BACKEND_URL}/clients/client_alejandro_mariscal/readiness", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                investment_ready = data.get("investment_ready", False)
                
                if investment_ready:
                    self.log_test("Individual Client Readiness", True, "Alejandro shows investment_ready: true")
                    return True
                else:
                    self.log_test("Individual Client Readiness", False, "Alejandro shows investment_ready: false", data)
                    return False
            else:
                self.log_test("Individual Client Readiness", False, f"HTTP {response.status_code}: {response.text[:200]}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test("Individual Client Readiness", False, f"Connection error: {str(e)}")
            return False
        except Exception as e:
            self.log_test("Individual Client Readiness", False, f"Exception: {str(e)}")
            return False
    
    def test_client_record_lookup(self):
        """Test 4: Client Record Lookup"""
        if not self.admin_token:
            self.log_test("Client Record Lookup", False, "No admin token available")
            return False
            
        try:
            response = self.session.get(f"{BACKEND_URL}/clients/client_alejandro_mariscal", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                email = data.get("email", "")
                
                if email == "alexmar7609@gmail.com":
                    self.log_test("Client Record Lookup", True, f"Client exists with correct email: {email}")
                    return True
                else:
                    self.log_test("Client Record Lookup", False, f"Client email mismatch. Expected: alexmar7609@gmail.com, Got: {email}", data)
                    return False
            else:
                self.log_test("Client Record Lookup", False, f"HTTP {response.status_code}: {response.text[:200]}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test("Client Record Lookup", False, f"Connection error: {str(e)}")
            return False
        except Exception as e:
            self.log_test("Client Record Lookup", False, f"Exception: {str(e)}")
            return False
    
    def test_investment_records_check(self):
        """Test 5: Investment Records Check"""
        if not self.admin_token:
            self.log_test("Investment Records Check", False, "No admin token available")
            return False
            
        try:
            response = self.session.get(f"{BACKEND_URL}/clients/client_alejandro_mariscal/investments", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                investments = data.get("investments", [])
                
                # Look for BALANCE ($100,000) and CORE ($18,151.41) investments
                balance_found = False
                core_found = False
                total_amount = 0
                
                for investment in investments:
                    fund_code = investment.get("fund_code", "")
                    amount = investment.get("principal_amount", 0)
                    total_amount += amount
                    
                    if fund_code == "BALANCE" and abs(amount - 100000) < 1:
                        balance_found = True
                    elif fund_code == "CORE" and abs(amount - 18151.41) < 1:
                        core_found = True
                
                if balance_found and core_found:
                    self.log_test("Investment Records Check", True, f"Found BALANCE ($100,000) and CORE ($18,151.41) investments. Total: ${total_amount:,.2f}")
                    return True
                else:
                    missing = []
                    if not balance_found:
                        missing.append("BALANCE ($100,000)")
                    if not core_found:
                        missing.append("CORE ($18,151.41)")
                    self.log_test("Investment Records Check", False, f"Missing investments: {', '.join(missing)}. Found {len(investments)} investments", data)
                    return False
            else:
                self.log_test("Investment Records Check", False, f"HTTP {response.status_code}: {response.text[:200]}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test("Investment Records Check", False, f"Connection error: {str(e)}")
            return False
        except Exception as e:
            self.log_test("Investment Records Check", False, f"Exception: {str(e)}")
            return False
    
    def test_mt5_accounts_check(self):
        """Test 6: MT5 Accounts Check"""
        if not self.admin_token:
            self.log_test("MT5 Accounts Check", False, "No admin token available")
            return False
            
        try:
            response = self.session.get(f"{BACKEND_URL}/mt5/accounts/client_alejandro_mariscal", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                accounts = data.get("accounts", [])
                
                # Look for 4 MT5 accounts with MEXAtlantic broker
                mexatlantic_accounts = [acc for acc in accounts if acc.get("broker_name", "").lower() == "mexatlantic"]
                
                if len(mexatlantic_accounts) >= 4:
                    account_numbers = [acc.get("mt5_account_number") for acc in mexatlantic_accounts]
                    self.log_test("MT5 Accounts Check", True, f"Found {len(mexatlantic_accounts)} MEXAtlantic accounts: {account_numbers}")
                    return True
                else:
                    self.log_test("MT5 Accounts Check", False, f"Expected 4 MEXAtlantic accounts, found {len(mexatlantic_accounts)}. Total accounts: {len(accounts)}", data)
                    return False
            else:
                self.log_test("MT5 Accounts Check", False, f"HTTP {response.status_code}: {response.text[:200]}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test("MT5 Accounts Check", False, f"Connection error: {str(e)}")
            return False
        except Exception as e:
            self.log_test("MT5 Accounts Check", False, f"Exception: {str(e)}")
            return False
    
    def test_admin_investment_overview(self):
        """Test 7: Admin Investment Overview"""
        if not self.admin_token:
            self.log_test("Admin Investment Overview", False, "No admin token available")
            return False
            
        try:
            response = self.session.get(f"{BACKEND_URL}/investments/admin/overview", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                total_aum = data.get("total_aum", 0)
                
                # Expected total: $118,151.41
                expected_total = 118151.41
                
                if abs(total_aum - expected_total) < 1:
                    self.log_test("Admin Investment Overview", True, f"Total AUM matches expected: ${total_aum:,.2f}")
                    return True
                else:
                    self.log_test("Admin Investment Overview", False, f"Total AUM mismatch. Expected: ${expected_total:,.2f}, Got: ${total_aum:,.2f}", data)
                    return False
            else:
                self.log_test("Admin Investment Overview", False, f"HTTP {response.status_code}: {response.text[:200]}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test("Admin Investment Overview", False, f"Connection error: {str(e)}")
            return False
        except Exception as e:
            self.log_test("Admin Investment Overview", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all production verification tests"""
        print("🚀 ALEJANDRO MARISCAL CRITICAL PRODUCTION VERIFICATION")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 80)
        
        # Test 1: Admin Authentication (required for other tests)
        if not self.test_admin_authentication():
            print("\n❌ CRITICAL: Admin authentication failed. Cannot proceed with other tests.")
            print("🚨 ROOT CAUSE: MongoDB authentication failure - backend cannot connect to database")
            return False
        
        # Run all other tests
        tests = [
            ("Ready for Investment Endpoint", self.test_ready_for_investment_endpoint),
            ("Individual Client Readiness", self.test_individual_client_readiness),
            ("Client Record Lookup", self.test_client_record_lookup),
            ("Investment Records Check", self.test_investment_records_check),
            ("MT5 Accounts Check", self.test_mt5_accounts_check),
            ("Admin Investment Overview", self.test_admin_investment_overview)
        ]
        
        passed_tests = 1  # Admin auth already passed
        total_tests = len(tests) + 1
        
        for test_name, test_func in tests:
            if test_func():
                passed_tests += 1
        
        print("=" * 80)
        print(f"📊 FINAL RESULTS: {passed_tests}/{total_tests} tests passed ({(passed_tests/total_tests)*100:.1f}%)")
        
        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED - Production setup is ready for go-live!")
            return True
        else:
            print("🚨 SOME TESTS FAILED - Production setup requires fixes before go-live")
            return False
    
    def get_summary(self):
        """Get test summary for reporting"""
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        return {
            "total_tests": total,
            "passed_tests": passed,
            "failed_tests": total - passed,
            "success_rate": (passed / total * 100) if total > 0 else 0,
            "results": self.test_results
        }

def main():
    """Main test execution"""
    tester = AlejandroCriticalTest()
    success = tester.run_all_tests()
    
    # Print detailed summary
    summary = tester.get_summary()
    print(f"\n📋 DETAILED SUMMARY:")
    print(f"   Success Rate: {summary['success_rate']:.1f}%")
    print(f"   Passed: {summary['passed_tests']}")
    print(f"   Failed: {summary['failed_tests']}")
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()