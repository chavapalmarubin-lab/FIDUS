#!/usr/bin/env python3
"""
URGENT VERIFICATION: Alejandro Mariscal Production Setup Test
Testing specific endpoints for Alejandro Mariscal's corrected production setup.

Expected Results:
1. Ready for Investment: Alejandro with email alexmar7609@gmail.com
2. Client Investments: Exactly 2 investments (BALANCE $100,000 + CORE $18,151.41)
3. MT5 Accounts: Exactly 4 MT5 accounts with MEXAtlantic broker
4. Investment Admin Overview: Total AUM of $118,151.41

Authentication: admin/password123 for JWT
"""

import requests
import json
import sys
from datetime import datetime, timezone

# Backend URL Configuration
BACKEND_URL = "https://trading-platform-76.preview.emergentagent.com/api"

class AlejandroProductionVerifier:
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
        """Test Ready for Investment Endpoint"""
        print("🔍 Testing Ready for Investment Endpoint...")
        
        if not self.admin_token:
            self.log_test("Ready for Investment Endpoint", False, "No admin token available")
            return
        
        response = self.make_request("GET", "/clients/ready-for-investment", auth_token=self.admin_token)
        if response and response.status_code == 200:
            try:
                data = response.json()
                ready_clients = data.get("ready_clients", [])
                
                # Look for Alejandro with correct email
                alejandro_found = None
                for client in ready_clients:
                    if (client.get("name") == "Alejandro Mariscal Romero" or 
                        client.get("client_id") == "client_alejandro"):
                        alejandro_found = client
                        break
                
                if alejandro_found:
                    email = alejandro_found.get("email", "")
                    if email == "alexmar7609@gmail.com":
                        self.log_test("Ready for Investment Endpoint", True, 
                                    f"✅ Alejandro found with correct email: {email}")
                    else:
                        self.log_test("Ready for Investment Endpoint", False, 
                                    f"❌ Email mismatch. Expected: alexmar7609@gmail.com, Got: {email}")
                else:
                    self.log_test("Ready for Investment Endpoint", False, 
                                f"❌ Alejandro not found in ready clients list ({len(ready_clients)} clients total)")
                    
            except json.JSONDecodeError:
                self.log_test("Ready for Investment Endpoint", False, "Invalid JSON response")
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("Ready for Investment Endpoint", False, f"HTTP {status_code}")

    def test_client_investments_endpoint(self):
        """Test Client Investments Endpoint"""
        print("🔍 Testing Client Investments Endpoint...")
        
        if not self.admin_token:
            self.log_test("Client Investments Endpoint", False, "No admin token available")
            return
        
        response = self.make_request("GET", "/clients/client_alejandro_mariscal/investments", auth_token=self.admin_token)
        if response and response.status_code == 200:
            try:
                data = response.json()
                investments = data.get("investments", [])
                
                if len(investments) == 2:
                    # Check for BALANCE ($100,000) and CORE ($18,151.41)
                    balance_investment = None
                    core_investment = None
                    
                    for inv in investments:
                        if inv.get("fund_code") == "BALANCE":
                            balance_investment = inv
                        elif inv.get("fund_code") == "CORE":
                            core_investment = inv
                    
                    balance_amount = balance_investment.get("principal_amount", 0) if balance_investment else 0
                    core_amount = core_investment.get("principal_amount", 0) if core_investment else 0
                    
                    if (balance_investment and abs(balance_amount - 100000) < 0.01 and
                        core_investment and abs(core_amount - 18151.41) < 0.01):
                        total_amount = balance_amount + core_amount
                        self.log_test("Client Investments Endpoint", True, 
                                    f"✅ Found 2 investments: BALANCE (${balance_amount:,.2f}) + CORE (${core_amount:,.2f}) = ${total_amount:,.2f}")
                    else:
                        self.log_test("Client Investments Endpoint", False, 
                                    f"❌ Investment amounts incorrect. Expected: BALANCE $100,000 + CORE $18,151.41. Got: BALANCE ${balance_amount:,.2f} + CORE ${core_amount:,.2f}")
                else:
                    self.log_test("Client Investments Endpoint", False, 
                                f"❌ Expected exactly 2 investments, found {len(investments)}")
                    
            except json.JSONDecodeError:
                self.log_test("Client Investments Endpoint", False, "Invalid JSON response")
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("Client Investments Endpoint", False, f"HTTP {status_code}")

    def test_mt5_accounts_endpoint(self):
        """Test MT5 Accounts Endpoint"""
        print("🔍 Testing MT5 Accounts Endpoint...")
        
        if not self.admin_token:
            self.log_test("MT5 Accounts Endpoint", False, "No admin token available")
            return
        
        response = self.make_request("GET", "/mt5/accounts/client_alejandro_mariscal", auth_token=self.admin_token)
        if response and response.status_code == 200:
            try:
                data = response.json()
                accounts = data.get("accounts", [])
                
                if len(accounts) == 4:
                    # Check for expected MT5 accounts: 886557 ($80k), 886066 ($10k), 886602 ($10k), 885822 ($18,151.41)
                    expected_accounts = {
                        "886557": 80000,
                        "886066": 10000, 
                        "886602": 10000,
                        "885822": 18151.41
                    }
                    
                    found_accounts = {}
                    mexatlantic_count = 0
                    total_balance = 0
                    
                    for acc in accounts:
                        account_number = acc.get("mt5_account_number", "")
                        balance = acc.get("balance", 0)
                        broker = acc.get("broker_name", "")
                        
                        if account_number in expected_accounts:
                            found_accounts[account_number] = balance
                        
                        if broker == "MEXAtlantic":
                            mexatlantic_count += 1
                            
                        total_balance += balance
                    
                    # Check if all expected accounts found with correct balances
                    all_correct = True
                    for acc_num, expected_balance in expected_accounts.items():
                        if acc_num not in found_accounts:
                            all_correct = False
                            break
                        if abs(found_accounts[acc_num] - expected_balance) > 0.01:
                            all_correct = False
                            break
                    
                    if all_correct and mexatlantic_count == 4 and abs(total_balance - 118151.41) < 0.01:
                        self.log_test("MT5 Accounts Endpoint", True, 
                                    f"✅ Found 4 MT5 accounts with MEXAtlantic broker, Total: ${total_balance:,.2f}")
                    else:
                        self.log_test("MT5 Accounts Endpoint", False, 
                                    f"❌ Account verification failed. Expected 4 MEXAtlantic accounts totaling $118,151.41. Got {mexatlantic_count} MEXAtlantic accounts totaling ${total_balance:,.2f}")
                else:
                    self.log_test("MT5 Accounts Endpoint", False, 
                                f"❌ Expected exactly 4 MT5 accounts, found {len(accounts)}")
                    
            except json.JSONDecodeError:
                self.log_test("MT5 Accounts Endpoint", False, "Invalid JSON response")
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("MT5 Accounts Endpoint", False, f"HTTP {status_code}")

    def test_investment_admin_overview(self):
        """Test Investment Admin Overview"""
        print("🔍 Testing Investment Admin Overview...")
        
        if not self.admin_token:
            self.log_test("Investment Admin Overview", False, "No admin token available")
            return
        
        response = self.make_request("GET", "/investments/admin/overview", auth_token=self.admin_token)
        if response and response.status_code == 200:
            try:
                data = response.json()
                total_aum = data.get("total_aum", 0)
                total_investments = data.get("total_investments", 0)
                expected_aum = 118151.41
                
                if abs(total_aum - expected_aum) < 0.01 and total_investments > 0:
                    self.log_test("Investment Admin Overview", True, 
                                f"✅ Total AUM: ${total_aum:,.2f}, Total Investments: {total_investments}")
                else:
                    self.log_test("Investment Admin Overview", False, 
                                f"❌ AUM/Investment count mismatch. Expected AUM: ${expected_aum:,.2f} with >0 investments. Got AUM: ${total_aum:,.2f}, Investments: {total_investments}")
                    
            except json.JSONDecodeError:
                self.log_test("Investment Admin Overview", False, "Invalid JSON response")
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("Investment Admin Overview", False, f"HTTP {status_code}")

    def run_verification(self):
        """Run complete Alejandro production setup verification"""
        print("🚀 URGENT VERIFICATION: Alejandro Mariscal Production Setup")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Started: {datetime.now(timezone.utc).isoformat()}")
        print("=" * 80)
        print()

        # Authenticate first
        if not self.authenticate_admin():
            print("🚨 CRITICAL: Admin authentication failed - cannot proceed with verification")
            return 0.0

        # Run all verification tests
        self.test_ready_for_investment_endpoint()
        self.test_client_investments_endpoint()
        self.test_mt5_accounts_endpoint()
        self.test_investment_admin_overview()

        # Generate summary
        print("=" * 80)
        print("🎯 ALEJANDRO MARISCAL PRODUCTION VERIFICATION SUMMARY")
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
        print("🔍 VERIFICATION RESULTS:")
        
        ready_test = next((t for t in self.test_results if "Ready for Investment" in t["test"]), None)
        if ready_test and ready_test["success"]:
            print("   ✅ Ready for Investment: Alejandro appears with correct email")
        else:
            print("   ❌ Ready for Investment: FAILED - Alejandro not found or wrong email")
            
        investments_test = next((t for t in self.test_results if "Client Investments" in t["test"]), None)
        if investments_test and investments_test["success"]:
            print("   ✅ Client Investments: 2 investments totaling $118,151.41")
        else:
            print("   ❌ Client Investments: FAILED - Wrong number or amounts")
            
        mt5_test = next((t for t in self.test_results if "MT5 Accounts" in t["test"]), None)
        if mt5_test and mt5_test["success"]:
            print("   ✅ MT5 Accounts: 4 accounts with MEXAtlantic broker")
        else:
            print("   ❌ MT5 Accounts: FAILED - Wrong number or broker")
            
        overview_test = next((t for t in self.test_results if "Investment Admin Overview" in t["test"]), None)
        if overview_test and overview_test["success"]:
            print("   ✅ Admin Overview: Total AUM $118,151.41")
        else:
            print("   ❌ Admin Overview: FAILED - Wrong AUM amount")

        print()
        print("=" * 80)
        
        if success_rate == 100:
            print("🎉 PRODUCTION SETUP STATUS: READY FOR GO-LIVE")
            print("✅ All endpoints working correctly - first real client setup complete")
        elif success_rate >= 75:
            print("⚠️  PRODUCTION SETUP STATUS: MOSTLY READY - MINOR ISSUES")
            print("🔧 Some endpoints need attention before go-live")
        else:
            print("🚨 PRODUCTION SETUP STATUS: NOT READY - CRITICAL ISSUES")
            print("❌ Major problems detected - immediate intervention required")
            
        print("=" * 80)
        
        return success_rate

if __name__ == "__main__":
    verifier = AlejandroProductionVerifier()
    success_rate = verifier.run_verification()
    
    # Exit with appropriate code
    sys.exit(0 if success_rate == 100 else 1)