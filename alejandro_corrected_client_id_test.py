#!/usr/bin/env python3
"""
CORRECTED CLIENT ID TEST: Alejandro Mariscal Endpoints Testing
Testing Alejandro's endpoints using the CORRECTED client ID: client_alejandro_mariscal

CORRECTED CLIENT ID: client_alejandro_mariscal (not client_alejandro)

Test Endpoints:
1. Ready for Investment: GET /api/clients/ready-for-investment
   - Should return Alejandro (client_alejandro_mariscal) with email: alexmar7609@gmail.com

2. Client Investments: GET /api/clients/client_alejandro_mariscal/investments  
   - Should return 2 investments: BALANCE ($100,000) + CORE ($18,151.41)

3. MT5 Accounts: GET /api/mt5/accounts/client_alejandro_mariscal
   - Should return 4 MT5 accounts: 886557 ($80k), 886066 ($10k), 886602 ($10k), 885822 ($18,151.41)

Authentication: admin/password123
"""

import requests
import json
import sys
from datetime import datetime, timezone

# Backend URL Configuration
BACKEND_URL = "https://trading-platform-76.preview.emergentagent.com/api"

# CORRECTED CLIENT ID
CORRECTED_CLIENT_ID = "client_alejandro_mariscal"

class AlejandroClientIDTester:
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
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=req_headers, timeout=30)
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
        """Test 1: Ready for Investment endpoint with corrected client ID"""
        print("🔍 Testing Ready for Investment Endpoint...")
        
        if not self.admin_token:
            self.log_test("Ready for Investment Endpoint", False, "No admin token available")
            return

        response = self.make_request("GET", "/clients/ready-for-investment", auth_token=self.admin_token)
        if response and response.status_code == 200:
            try:
                data = response.json()
                ready_clients = data.get("ready_clients", [])
                
                # Look for Alejandro with corrected client ID
                alejandro_found = None
                for client in ready_clients:
                    if (client.get("client_id") == CORRECTED_CLIENT_ID or 
                        client.get("name") == "Alejandro Mariscal Romero" or
                        client.get("email") == "alexmar7609@gmail.com"):
                        alejandro_found = client
                        break
                
                if alejandro_found:
                    # Verify expected data
                    expected_email = "alexmar7609@gmail.com"
                    actual_email = alejandro_found.get("email", "")
                    
                    if actual_email == expected_email:
                        self.log_test("Ready for Investment - Alejandro Found", True, 
                                    f"Client ID: {alejandro_found.get('client_id')}, Name: {alejandro_found.get('name')}, Email: {actual_email}")
                    else:
                        self.log_test("Ready for Investment - Alejandro Found", False, 
                                    f"Email mismatch. Expected: {expected_email}, Got: {actual_email}")
                else:
                    client_list = [f"{c.get('client_id', 'N/A')} ({c.get('name', 'N/A')})" for c in ready_clients]
                    self.log_test("Ready for Investment - Alejandro Found", False, 
                                f"Alejandro not found. Available clients: {client_list}")
                    
            except json.JSONDecodeError:
                self.log_test("Ready for Investment - Alejandro Found", False, "Invalid JSON response")
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("Ready for Investment - Alejandro Found", False, f"HTTP {status_code}")

    def test_client_investments_endpoint(self):
        """Test 2: Client Investments endpoint with corrected client ID"""
        print("🔍 Testing Client Investments Endpoint...")
        
        if not self.admin_token:
            self.log_test("Client Investments Endpoint", False, "No admin token available")
            return

        # Test with corrected client ID
        endpoint = f"/clients/{CORRECTED_CLIENT_ID}/investments"
        response = self.make_request("GET", endpoint, auth_token=self.admin_token)
        
        if response and response.status_code == 200:
            try:
                data = response.json()
                investments = data.get("investments", [])
                
                if len(investments) == 2:
                    # Check for expected investments: BALANCE ($100,000) + CORE ($18,151.41)
                    balance_investment = None
                    core_investment = None
                    
                    for inv in investments:
                        if inv.get("fund_code") == "BALANCE":
                            balance_investment = inv
                        elif inv.get("fund_code") == "CORE":
                            core_investment = inv
                    
                    # Verify BALANCE investment
                    balance_correct = (balance_investment and 
                                     abs(balance_investment.get("principal_amount", 0) - 100000) < 0.01)
                    
                    # Verify CORE investment  
                    core_correct = (core_investment and 
                                   abs(core_investment.get("principal_amount", 0) - 18151.41) < 0.01)
                    
                    if balance_correct and core_correct:
                        total_amount = sum(inv.get("principal_amount", 0) for inv in investments)
                        self.log_test("Client Investments - Expected Investments", True, 
                                    f"Found 2 investments: BALANCE (${balance_investment.get('principal_amount', 0):,.2f}) + CORE (${core_investment.get('principal_amount', 0):,.2f}) = ${total_amount:,.2f}")
                    else:
                        investment_details = [(inv.get("fund_code"), inv.get("principal_amount", 0)) for inv in investments]
                        self.log_test("Client Investments - Expected Investments", False, 
                                    f"Investment amounts incorrect. Found: {investment_details}, Expected: BALANCE $100,000 + CORE $18,151.41")
                else:
                    investment_details = [(inv.get("fund_code"), inv.get("principal_amount", 0)) for inv in investments]
                    self.log_test("Client Investments - Expected Investments", False, 
                                f"Expected 2 investments, found {len(investments)}: {investment_details}")
                    
            except json.JSONDecodeError:
                self.log_test("Client Investments - Expected Investments", False, "Invalid JSON response")
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("Client Investments - Expected Investments", False, f"HTTP {status_code}")

    def test_mt5_accounts_endpoint(self):
        """Test 3: MT5 Accounts endpoint with corrected client ID"""
        print("🔍 Testing MT5 Accounts Endpoint...")
        
        if not self.admin_token:
            self.log_test("MT5 Accounts Endpoint", False, "No admin token available")
            return

        # Test with corrected client ID
        endpoint = f"/mt5/accounts/{CORRECTED_CLIENT_ID}"
        response = self.make_request("GET", endpoint, auth_token=self.admin_token)
        
        if response and response.status_code == 200:
            try:
                data = response.json()
                accounts = data.get("accounts", [])
                
                if len(accounts) == 4:
                    # Check for expected MT5 accounts: 886557 ($80k), 886066 ($10k), 886602 ($10k), 885822 ($18,151.41)
                    expected_accounts = {
                        "886557": 80000.0,
                        "886066": 10000.0, 
                        "886602": 10000.0,
                        "885822": 18151.41
                    }
                    
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
                        self.log_test("MT5 Accounts - Expected Accounts", True, 
                                    f"Found 4 MT5 accounts with correct balances: {', '.join(account_details)}, Total: ${total_balance:,.2f}")
                    else:
                        self.log_test("MT5 Accounts - Expected Accounts", False, 
                                    f"Account balances incorrect: {', '.join(account_details)}")
                else:
                    found_account_details = [(acc.get("mt5_account_number"), acc.get("balance", 0)) for acc in accounts]
                    self.log_test("MT5 Accounts - Expected Accounts", False, 
                                f"Expected 4 MT5 accounts, found {len(accounts)}: {found_account_details}")
                    
            except json.JSONDecodeError:
                self.log_test("MT5 Accounts - Expected Accounts", False, "Invalid JSON response")
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("MT5 Accounts - Expected Accounts", False, f"HTTP {status_code}")

    def run_corrected_client_id_test(self):
        """Run all corrected client ID tests"""
        print("🚀 CORRECTED CLIENT ID TEST: Alejandro Mariscal Endpoints")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"CORRECTED CLIENT ID: {CORRECTED_CLIENT_ID}")
        print(f"Test Started: {datetime.now(timezone.utc).isoformat()}")
        print("=" * 80)
        print()

        # Authenticate first
        if not self.authenticate_admin():
            print("🚨 CRITICAL: Admin authentication failed. Cannot proceed with tests.")
            return 0.0

        # Run the three specific tests
        self.test_ready_for_investment_endpoint()
        self.test_client_investments_endpoint()
        self.test_mt5_accounts_endpoint()

        # Generate summary
        print("=" * 80)
        print("🎯 CORRECTED CLIENT ID TEST SUMMARY")
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
        
        ready_test = next((t for t in self.test_results if "Ready for Investment" in t["test"]), None)
        if ready_test and ready_test["success"]:
            print("   ✅ Alejandro appears in ready-for-investment endpoint")
        else:
            print("   ❌ Alejandro NOT found in ready-for-investment endpoint")
            
        investments_test = next((t for t in self.test_results if "Client Investments" in t["test"]), None)
        if investments_test and investments_test["success"]:
            print("   ✅ Alejandro has expected 2 investments (BALANCE + CORE)")
        else:
            print("   ❌ Alejandro investments missing or incorrect")

        mt5_test = next((t for t in self.test_results if "MT5 Accounts" in t["test"]), None)
        if mt5_test and mt5_test["success"]:
            print("   ✅ Alejandro has expected 4 MT5 accounts")
        else:
            print("   ❌ Alejandro MT5 accounts missing or incorrect")

        print()
        print("=" * 80)
        
        if success_rate == 100:
            print("🎉 CORRECTED CLIENT ID TEST: ALL TESTS PASSED - PRODUCTION READY")
        elif success_rate >= 75:
            print("⚠️  CORRECTED CLIENT ID TEST: MOSTLY WORKING - MINOR ISSUES")
        else:
            print("🚨 CORRECTED CLIENT ID TEST: CRITICAL ISSUES - DATA SETUP REQUIRED")
            
        print("=" * 80)
        
        return success_rate

if __name__ == "__main__":
    tester = AlejandroClientIDTester()
    success_rate = tester.run_corrected_client_id_test()
    
    # Exit with appropriate code
    sys.exit(0 if success_rate >= 75 else 1)