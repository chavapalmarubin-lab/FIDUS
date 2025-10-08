#!/usr/bin/env python3
"""
ALEJANDRO MARISCAL FINAL VERIFICATION TEST
Testing specific endpoints for Alejandro's data after backend restart as requested in review.

Expected Results:
1. Ready for Investment: Should return Alejandro with email alexmar7609@gmail.com
2. Client Investments: Should return exactly 2 investments totaling $118,151.41
3. MT5 Accounts: Should return 4 MEXAtlantic accounts totaling $118,151.41
4. Admin Overview: Should show correct AUM

Backend URL: https://trading-platform-76.preview.emergentagent.com/api
Auth: admin/password123
"""

import requests
import json
import sys
from datetime import datetime, timezone

# Backend URL Configuration
BACKEND_URL = "https://trading-platform-76.preview.emergentagent.com/api"

class AlejandroFinalVerificationTester:
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

    def test_ready_for_investment(self):
        """Test Ready for Investment endpoint - should return Alejandro with email alexmar7609@gmail.com"""
        print("🔍 Testing Ready for Investment Endpoint...")
        
        response = self.make_request("GET", "/clients/ready-for-investment", auth_token=self.admin_token)
        if response and response.status_code == 200:
            try:
                data = response.json()
                ready_clients = data.get("ready_clients", [])
                
                # Look for Alejandro Mariscal Romero
                alejandro_found = None
                for client in ready_clients:
                    if client.get("name") == "Alejandro Mariscal Romero":
                        alejandro_found = client
                        break
                
                if alejandro_found:
                    email = alejandro_found.get("email", "")
                    if email == "alexmar7609@gmail.com":
                        self.log_test("Ready for Investment - Alejandro Found", True, 
                                    f"Alejandro found with correct email: {email}")
                    else:
                        self.log_test("Ready for Investment - Alejandro Found", False, 
                                    f"Email mismatch. Expected: alexmar7609@gmail.com, Got: {email}")
                else:
                    self.log_test("Ready for Investment - Alejandro Found", False, 
                                f"Alejandro not found in ready clients list ({len(ready_clients)} clients total)")
                    
            except json.JSONDecodeError:
                self.log_test("Ready for Investment - Alejandro Found", False, "Invalid JSON response")
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("Ready for Investment - Alejandro Found", False, f"HTTP {status_code}")

    def test_client_investments(self):
        """Test Client Investments - should return exactly 2 investments totaling $118,151.41"""
        print("🔍 Testing Client Investments Endpoint...")
        
        response = self.make_request("GET", "/clients/client_alejandro/investments", auth_token=self.admin_token)
        if response and response.status_code == 200:
            try:
                data = response.json()
                investments = data.get("investments", [])
                
                if len(investments) == 2:
                    # Calculate total amount
                    total_amount = sum(inv.get("principal_amount", 0) for inv in investments)
                    expected_total = 118151.41
                    
                    if abs(total_amount - expected_total) < 0.01:  # Allow for small floating point differences
                        # Check for specific investments
                        balance_found = any(inv.get("fund_code") == "BALANCE" and inv.get("principal_amount") == 100000 for inv in investments)
                        core_found = any(inv.get("fund_code") == "CORE" and inv.get("principal_amount") == 18151.41 for inv in investments)
                        
                        if balance_found and core_found:
                            self.log_test("Client Investments - Correct Data", True, 
                                        f"Found 2 investments: BALANCE ($100,000) + CORE ($18,151.41) = ${total_amount:,.2f}")
                        else:
                            self.log_test("Client Investments - Correct Data", False, 
                                        f"Investment types incorrect. Expected: BALANCE $100,000 + CORE $18,151.41")
                    else:
                        self.log_test("Client Investments - Correct Data", False, 
                                    f"Total amount mismatch. Expected: ${expected_total:,.2f}, Got: ${total_amount:,.2f}")
                else:
                    self.log_test("Client Investments - Correct Data", False, 
                                f"Expected 2 investments, found {len(investments)}")
                    
            except json.JSONDecodeError:
                self.log_test("Client Investments - Correct Data", False, "Invalid JSON response")
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("Client Investments - Correct Data", False, f"HTTP {status_code}")

    def test_mt5_accounts(self):
        """Test MT5 Accounts - should return 4 MEXAtlantic accounts totaling $118,151.41"""
        print("🔍 Testing MT5 Accounts Endpoint...")
        
        response = self.make_request("GET", "/mt5/accounts/client_alejandro", auth_token=self.admin_token)
        if response and response.status_code == 200:
            try:
                data = response.json()
                accounts = data.get("accounts", [])
                
                if len(accounts) == 4:
                    # Check for MEXAtlantic broker
                    mexatlantic_accounts = [acc for acc in accounts if acc.get("broker_name") == "MEXAtlantic"]
                    
                    if len(mexatlantic_accounts) == 4:
                        # Calculate total balance
                        total_balance = sum(acc.get("balance", 0) for acc in accounts)
                        expected_total = 118151.41
                        
                        if abs(total_balance - expected_total) < 0.01:  # Allow for small floating point differences
                            # Check for expected account numbers
                            expected_accounts = ["886557", "886066", "886602", "885822"]
                            found_accounts = [acc.get("mt5_account_number") for acc in accounts]
                            
                            all_found = all(acc in found_accounts for acc in expected_accounts)
                            
                            if all_found:
                                self.log_test("MT5 Accounts - Correct Data", True, 
                                            f"Found 4 MEXAtlantic accounts ({', '.join(found_accounts)}), Total: ${total_balance:,.2f}")
                            else:
                                self.log_test("MT5 Accounts - Correct Data", False, 
                                            f"Account numbers mismatch. Expected: {expected_accounts}, Got: {found_accounts}")
                        else:
                            self.log_test("MT5 Accounts - Correct Data", False, 
                                        f"Total balance mismatch. Expected: ${expected_total:,.2f}, Got: ${total_balance:,.2f}")
                    else:
                        self.log_test("MT5 Accounts - Correct Data", False, 
                                    f"Expected 4 MEXAtlantic accounts, found {len(mexatlantic_accounts)} MEXAtlantic accounts")
                else:
                    self.log_test("MT5 Accounts - Correct Data", False, 
                                f"Expected 4 MT5 accounts, found {len(accounts)}")
                    
            except json.JSONDecodeError:
                self.log_test("MT5 Accounts - Correct Data", False, "Invalid JSON response")
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("MT5 Accounts - Correct Data", False, f"HTTP {status_code}")

    def test_admin_overview(self):
        """Test Admin Overview - should show correct AUM"""
        print("🔍 Testing Admin Overview Endpoint...")
        
        response = self.make_request("GET", "/investments/admin/overview", auth_token=self.admin_token)
        if response and response.status_code == 200:
            try:
                data = response.json()
                total_aum = data.get("total_aum", 0)
                expected_aum = 118151.41
                
                if abs(total_aum - expected_aum) < 0.01:  # Allow for small floating point differences
                    total_investments = data.get("total_investments", 0)
                    total_clients = data.get("total_clients", 0)
                    
                    self.log_test("Admin Overview - Correct AUM", True, 
                                f"Total AUM: ${total_aum:,.2f}, Investments: {total_investments}, Clients: {total_clients}")
                else:
                    self.log_test("Admin Overview - Correct AUM", False, 
                                f"AUM mismatch. Expected: ${expected_aum:,.2f}, Got: ${total_aum:,.2f}")
                    
            except json.JSONDecodeError:
                self.log_test("Admin Overview - Correct AUM", False, "Invalid JSON response")
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("Admin Overview - Correct AUM", False, f"HTTP {status_code}")

    def run_final_verification(self):
        """Run final verification tests for Alejandro's data"""
        print("🚀 ALEJANDRO MARISCAL FINAL VERIFICATION TEST")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Started: {datetime.now(timezone.utc).isoformat()}")
        print("Expected Results:")
        print("1. Ready for Investment: Alejandro with email alexmar7609@gmail.com")
        print("2. Client Investments: 2 investments totaling $118,151.41")
        print("3. MT5 Accounts: 4 MEXAtlantic accounts totaling $118,151.41")
        print("4. Admin Overview: Correct AUM display")
        print("=" * 80)
        print()

        # Authenticate first
        if not self.authenticate_admin():
            print("🚨 CRITICAL: Admin authentication failed. Cannot proceed with tests.")
            return 0.0

        # Run specific verification tests
        self.test_ready_for_investment()
        self.test_client_investments()
        self.test_mt5_accounts()
        self.test_admin_overview()

        # Generate summary
        print("=" * 80)
        print("🎯 ALEJANDRO FINAL VERIFICATION SUMMARY")
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

        # Show detailed results
        print("🔍 DETAILED RESULTS:")
        for test in self.test_results:
            if test["success"]:
                print(f"   ✅ {test['test']}: {test['details']}")
            else:
                print(f"   ❌ {test['test']}: {test['error']}")
        print()

        print("=" * 80)
        
        if success_rate == 100:
            print("🎉 PRODUCTION READY: All Alejandro endpoints returning correct data")
        elif success_rate >= 75:
            print("⚠️  MOSTLY READY: Minor issues detected, review required")
        else:
            print("🚨 NOT READY: Critical issues found, immediate attention required")
            
        print("=" * 80)
        
        return success_rate

if __name__ == "__main__":
    tester = AlejandroFinalVerificationTester()
    success_rate = tester.run_final_verification()
    
    # Exit with appropriate code
    sys.exit(0 if success_rate == 100 else 1)