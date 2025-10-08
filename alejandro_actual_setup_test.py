#!/usr/bin/env python3
"""
ALEJANDRO ACTUAL SETUP TEST: Testing with actual database configuration
Based on database investigation, testing both client IDs to find the correct setup:
- client_alejandro (found in ready-for-investment)
- client_alejandro_mariscal (has investments but not in ready list)

Expected Results from Review Request:
1. Ready for Investment: Should return Alejandro with email: alexmar7609@gmail.com
2. Client Investments: Should return 2 investments: BALANCE ($100,000) + CORE ($18,151.41)  
3. MT5 Accounts: Should return 4 MT5 accounts: 886557 ($80k), 886066 ($10k), 886602 ($10k), 885822 ($18,151.41)
"""

import requests
import json
import sys
from datetime import datetime, timezone

# Backend URL Configuration
BACKEND_URL = "https://trading-platform-76.preview.emergentagent.com/api"

class AlejandroActualSetupTester:
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

    def test_ready_for_investment_endpoint(self):
        """Test 1: Ready for Investment endpoint - check actual vs expected"""
        print("🔍 Testing Ready for Investment Endpoint...")
        
        if not self.admin_token:
            self.log_test("Ready for Investment Endpoint", False, "No admin token available")
            return

        response = self.make_request("GET", "/clients/ready-for-investment", auth_token=self.admin_token)
        if response and response.status_code == 200:
            try:
                data = response.json()
                ready_clients = data.get("ready_clients", [])
                
                # Look for any Alejandro
                alejandro_found = None
                for client in ready_clients:
                    if ("alejandro" in client.get("name", "").lower() or 
                        "alejandro" in client.get("client_id", "").lower()):
                        alejandro_found = client
                        break
                
                if alejandro_found:
                    # Check what we actually have vs what's expected
                    actual_client_id = alejandro_found.get("client_id", "")
                    actual_email = alejandro_found.get("email", "")
                    actual_name = alejandro_found.get("name", "")
                    
                    expected_client_id = "client_alejandro_mariscal"
                    expected_email = "alexmar7609@gmail.com"
                    
                    # Determine if this matches expectations
                    client_id_match = actual_client_id == expected_client_id
                    email_match = actual_email == expected_email
                    
                    if client_id_match and email_match:
                        self.log_test("Ready for Investment - Perfect Match", True, 
                                    f"✅ PERFECT: Client ID: {actual_client_id}, Email: {actual_email}")
                    else:
                        details = f"ACTUAL: Client ID: {actual_client_id}, Email: {actual_email}, Name: {actual_name}\n"
                        details += f"   EXPECTED: Client ID: {expected_client_id}, Email: {expected_email}"
                        if not client_id_match:
                            details += f"\n   ❌ Client ID mismatch"
                        if not email_match:
                            details += f"\n   ❌ Email mismatch"
                        
                        self.log_test("Ready for Investment - Data Mismatch", False, details)
                else:
                    client_list = [f"{c.get('client_id', 'N/A')} ({c.get('name', 'N/A')})" for c in ready_clients]
                    self.log_test("Ready for Investment - Alejandro Not Found", False, 
                                f"No Alejandro found. Available clients: {client_list}")
                    
            except json.JSONDecodeError:
                self.log_test("Ready for Investment - JSON Error", False, "Invalid JSON response")
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("Ready for Investment - Request Failed", False, f"HTTP {status_code}")

    def test_client_investments_both_ids(self):
        """Test 2: Client Investments endpoint - test both possible client IDs"""
        print("🔍 Testing Client Investments Endpoints...")
        
        if not self.admin_token:
            self.log_test("Client Investments Test", False, "No admin token available")
            return

        # Test both possible client IDs
        client_ids_to_test = [
            ("client_alejandro", "Original Client ID"),
            ("client_alejandro_mariscal", "Corrected Client ID")
        ]
        
        for client_id, description in client_ids_to_test:
            print(f"   Testing {description}: {client_id}")
            
            # Test the investments endpoint
            endpoint = f"/investments/client/{client_id}"
            response = self.make_request("GET", endpoint, auth_token=self.admin_token)
            
            if response and response.status_code == 200:
                try:
                    data = response.json()
                    investments = data.get("investments", [])
                    
                    # Look for the expected investments: BALANCE ($100,000) + CORE ($18,151.41)
                    balance_investment = None
                    core_investment = None
                    
                    for inv in investments:
                        if inv.get("fund_code") == "BALANCE" and abs(inv.get("principal_amount", 0) - 100000) < 0.01:
                            balance_investment = inv
                        elif inv.get("fund_code") == "CORE" and abs(inv.get("principal_amount", 0) - 18151.41) < 0.01:
                            core_investment = inv
                    
                    # Check if we have the expected investments
                    has_expected_balance = balance_investment is not None
                    has_expected_core = core_investment is not None
                    
                    if has_expected_balance and has_expected_core:
                        total_expected = 100000 + 18151.41
                        self.log_test(f"Client Investments - {description} ✅", True, 
                                    f"Found expected investments: BALANCE ($100,000) + CORE ($18,151.41) = ${total_expected:,.2f}")
                    else:
                        # Show what we actually found
                        investment_details = []
                        for inv in investments:
                            investment_details.append(f"{inv.get('fund_code')}: ${inv.get('principal_amount', 0):,.2f}")
                        
                        details = f"Found {len(investments)} investments: {', '.join(investment_details)}\n"
                        details += f"   Expected: BALANCE ($100,000) + CORE ($18,151.41)"
                        if not has_expected_balance:
                            details += f"\n   ❌ Missing BALANCE $100,000"
                        if not has_expected_core:
                            details += f"\n   ❌ Missing CORE $18,151.41"
                        
                        self.log_test(f"Client Investments - {description} ⚠️", False, details)
                        
                except json.JSONDecodeError:
                    self.log_test(f"Client Investments - {description} JSON Error", False, "Invalid JSON response")
            else:
                status_code = response.status_code if response else "No response"
                self.log_test(f"Client Investments - {description} Failed", False, f"HTTP {status_code}")

    def test_mt5_accounts_both_ids(self):
        """Test 3: MT5 Accounts endpoint - test both possible client IDs"""
        print("🔍 Testing MT5 Accounts Endpoints...")
        
        if not self.admin_token:
            self.log_test("MT5 Accounts Test", False, "No admin token available")
            return

        # Test both possible client IDs
        client_ids_to_test = [
            ("client_alejandro", "Original Client ID"),
            ("client_alejandro_mariscal", "Corrected Client ID")
        ]
        
        # Expected MT5 accounts: 886557 ($80k), 886066 ($10k), 886602 ($10k), 885822 ($18,151.41)
        expected_accounts = {
            "886557": 80000.0,
            "886066": 10000.0, 
            "886602": 10000.0,
            "885822": 18151.41
        }
        
        for client_id, description in client_ids_to_test:
            print(f"   Testing {description}: {client_id}")
            
            endpoint = f"/mt5/accounts/{client_id}"
            response = self.make_request("GET", endpoint, auth_token=self.admin_token)
            
            if response and response.status_code == 200:
                try:
                    data = response.json()
                    accounts = data.get("accounts", [])
                    
                    if len(accounts) == 4:
                        # Check if we have the expected accounts
                        found_accounts = {}
                        for acc in accounts:
                            account_number = str(acc.get("mt5_account_number", ""))
                            balance = acc.get("balance", 0)
                            found_accounts[account_number] = balance
                        
                        # Verify all expected accounts are present with correct balances
                        all_correct = True
                        account_details = []
                        
                        for expected_acc, expected_balance in expected_accounts.items():
                            if expected_acc in found_accounts:
                                actual_balance = found_accounts[expected_acc]
                                if abs(actual_balance - expected_balance) < 0.01:
                                    account_details.append(f"{expected_acc}: ${actual_balance:,.2f} ✓")
                                else:
                                    account_details.append(f"{expected_acc}: ${actual_balance:,.2f} (expected ${expected_balance:,.2f}) ✗")
                                    all_correct = False
                            else:
                                account_details.append(f"{expected_acc}: MISSING ✗")
                                all_correct = False
                        
                        if all_correct:
                            total_balance = sum(found_accounts.values())
                            self.log_test(f"MT5 Accounts - {description} ✅", True, 
                                        f"Found 4 MT5 accounts with correct balances: {', '.join(account_details)}, Total: ${total_balance:,.2f}")
                        else:
                            self.log_test(f"MT5 Accounts - {description} ⚠️", False, 
                                        f"Account balances incorrect: {', '.join(account_details)}")
                    else:
                        if len(accounts) == 0:
                            self.log_test(f"MT5 Accounts - {description} Empty", False, 
                                        f"No MT5 accounts found (expected 4)")
                        else:
                            found_account_details = [(acc.get("mt5_account_number"), acc.get("balance", 0)) for acc in accounts]
                            self.log_test(f"MT5 Accounts - {description} Count Mismatch", False, 
                                        f"Expected 4 MT5 accounts, found {len(accounts)}: {found_account_details}")
                        
                except json.JSONDecodeError:
                    self.log_test(f"MT5 Accounts - {description} JSON Error", False, "Invalid JSON response")
            else:
                status_code = response.status_code if response else "No response"
                self.log_test(f"MT5 Accounts - {description} Failed", False, f"HTTP {status_code}")

    def run_actual_setup_test(self):
        """Run all tests with actual database setup"""
        print("🚀 ALEJANDRO ACTUAL SETUP TEST: Database Reality Check")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Started: {datetime.now(timezone.utc).isoformat()}")
        print("=" * 80)
        print()

        # Authenticate first
        if not self.authenticate_admin():
            print("🚨 CRITICAL: Admin authentication failed. Cannot proceed with tests.")
            return 0.0

        # Run the tests
        self.test_ready_for_investment_endpoint()
        self.test_client_investments_both_ids()
        self.test_mt5_accounts_both_ids()

        # Generate summary
        print("=" * 80)
        print("🎯 ALEJANDRO ACTUAL SETUP TEST SUMMARY")
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
                print(f"   • {test['test']}")
                if test['details']:
                    print(f"     {test['details']}")
            print()

        # Show critical findings
        print("🔍 CRITICAL FINDINGS:")
        
        # Check ready for investment
        ready_tests = [t for t in self.test_results if "Ready for Investment" in t["test"]]
        ready_success = any(t["success"] for t in ready_tests)
        if ready_success:
            print("   ✅ Alejandro found in ready-for-investment endpoint")
        else:
            print("   ❌ Alejandro data mismatch in ready-for-investment endpoint")
            
        # Check investments
        investment_tests = [t for t in self.test_results if "Client Investments" in t["test"] and t["success"]]
        if investment_tests:
            print(f"   ✅ Found expected investments in {len(investment_tests)} client ID(s)")
        else:
            print("   ❌ Expected investments not found in any client ID")

        # Check MT5 accounts
        mt5_tests = [t for t in self.test_results if "MT5 Accounts" in t["test"] and t["success"]]
        if mt5_tests:
            print(f"   ✅ Found expected MT5 accounts in {len(mt5_tests)} client ID(s)")
        else:
            print("   ❌ Expected MT5 accounts not found in any client ID")

        print()
        print("🎯 RECOMMENDATIONS:")
        
        # Analyze which client ID works better
        original_id_tests = [t for t in self.test_results if "Original Client ID" in t["test"]]
        corrected_id_tests = [t for t in self.test_results if "Corrected Client ID" in t["test"]]
        
        original_success = sum(1 for t in original_id_tests if t["success"])
        corrected_success = sum(1 for t in corrected_id_tests if t["success"])
        
        if original_success > corrected_success:
            print("   📋 Use 'client_alejandro' - has more working endpoints")
        elif corrected_success > original_success:
            print("   📋 Use 'client_alejandro_mariscal' - has more working endpoints")
        else:
            print("   📋 Both client IDs have similar issues - data setup needed")

        # Check what needs to be fixed
        if not ready_success:
            print("   🔧 Fix: Update email to 'alexmar7609@gmail.com' or client ID to 'client_alejandro_mariscal'")
        
        if not investment_tests:
            print("   🔧 Fix: Ensure BALANCE ($100,000) + CORE ($18,151.41) investments exist")
            
        if not mt5_tests:
            print("   🔧 Fix: Create 4 MT5 accounts: 886557 ($80k), 886066 ($10k), 886602 ($10k), 885822 ($18,151.41)")

        print()
        print("=" * 80)
        
        if success_rate == 100:
            print("🎉 ALEJANDRO SETUP: PERFECT MATCH - PRODUCTION READY")
        elif success_rate >= 50:
            print("⚠️  ALEJANDRO SETUP: PARTIAL MATCH - MINOR FIXES NEEDED")
        else:
            print("🚨 ALEJANDRO SETUP: MAJOR ISSUES - SIGNIFICANT DATA SETUP REQUIRED")
            
        print("=" * 80)
        
        return success_rate

if __name__ == "__main__":
    tester = AlejandroActualSetupTester()
    success_rate = tester.run_actual_setup_test()
    
    # Exit with appropriate code
    sys.exit(0 if success_rate >= 75 else 1)