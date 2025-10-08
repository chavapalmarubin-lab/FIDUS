#!/usr/bin/env python3
"""
ALEJANDRO MARISCAL PRODUCTION SETUP VERIFICATION TEST
Testing that the first real client (Alejandro Mariscal) has been successfully set up in production database.

CRITICAL TESTS TO PERFORM:
1. Client Record Verification - GET /api/clients/client_alejandro_mariscal
2. Client Readiness Verification - GET /api/clients/client_alejandro_mariscal/readiness  
3. Ready for Investment Endpoint - GET /api/clients/ready-for-investment
4. Investment Records Verification - GET /api/clients/client_alejandro_mariscal/investments
5. MT5 Accounts Verification - GET /api/mt5/accounts/client_alejandro_mariscal
6. Investment Admin Overview - GET /api/investments/admin/overview

EXPECTED RESULTS:
- Client exists and is ready for investment
- 2 investment records created with correct amounts and dates
- 4 MT5 accounts created with real MEXAtlantic credentials
- Total amounts match exactly: $118,151.41
- All dates set to October 1, 2025
- Incubation ends December 1, 2025
- Minimum hold ends December 1, 2026
"""

import requests
import json
import time
import sys
from datetime import datetime, timezone
from typing import Dict, List, Optional

# Backend URL Configuration - Use production URL
BACKEND_URL = "https://fidus-invest.emergent.host/api"

# Expected Alejandro Data
EXPECTED_ALEJANDRO = {
    "client_id": "client_alejandro_mariscal",
    "email": "alexmar7609@gmail.com",
    "username": "alejandrom", 
    "status": "active",
    "total_investment": 118151.41,
    "investment_count": 2,
    "mt5_account_count": 4,
    "deposit_date": "2025-10-01",
    "incubation_end": "2025-12-01",
    "minimum_hold_end": "2026-12-01"
}

# Expected Investment Records
EXPECTED_INVESTMENTS = [
    {
        "fund_code": "BALANCE",
        "amount": 100000.00,
        "deposit_date": "2025-10-01"
    },
    {
        "fund_code": "CORE", 
        "amount": 18151.41,
        "deposit_date": "2025-10-01"
    }
]

# Expected MT5 Accounts
EXPECTED_MT5_ACCOUNTS = [
    {"login": "886557", "balance": 80000.00, "fund": "BALANCE"},
    {"login": "886066", "balance": 10000.00, "fund": "BALANCE"},
    {"login": "886602", "balance": 10000.00, "fund": "BALANCE"},
    {"login": "885822", "balance": 18151.41, "fund": "CORE"}
]

class AlejandroProductionTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.critical_failures = []
        
    def log_test(self, test_name: str, success: bool, details: str = "", error_msg: str = "", critical: bool = False):
        """Log test result with critical failure tracking"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
            if critical:
                self.critical_failures.append(test_name)
                status = "🚨 CRITICAL FAIL"
            
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "error": error_msg,
            "critical": critical,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if error_msg:
            print(f"   Error: {error_msg}")
        print()

    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                    headers: Optional[Dict] = None, auth_token: Optional[str] = None) -> Optional[requests.Response]:
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

    def authenticate_admin(self) -> bool:
        """Authenticate as admin and get JWT token"""
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
                    self.log_test("Admin Authentication", False, 
                                "Missing token or incorrect type", critical=True)
                    return False
            except json.JSONDecodeError:
                self.log_test("Admin Authentication", False, 
                            "Invalid JSON response", critical=True)
                return False
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("Admin Authentication", False, 
                        f"HTTP {status_code}", critical=True)
            return False

    def test_client_record_verification(self):
        """Test 1: Client Record Verification"""
        print("🔍 Test 1: Client Record Verification...")
        
        if not self.admin_token:
            self.log_test("Client Record Verification", False, 
                        "No admin token available", critical=True)
            return
        
        # Test GET /api/clients/client_alejandro_mariscal
        response = self.make_request("GET", "/clients/client_alejandro_mariscal", 
                                   auth_token=self.admin_token)
        
        if response and response.status_code == 200:
            try:
                data = response.json()
                client = data.get("client", {})
                
                # Verify client details
                checks = []
                if client.get("email") == EXPECTED_ALEJANDRO["email"]:
                    checks.append("✅ Email correct")
                else:
                    checks.append(f"❌ Email mismatch: expected {EXPECTED_ALEJANDRO['email']}, got {client.get('email')}")
                
                if client.get("username") == EXPECTED_ALEJANDRO["username"]:
                    checks.append("✅ Username correct")
                else:
                    checks.append(f"❌ Username mismatch: expected {EXPECTED_ALEJANDRO['username']}, got {client.get('username')}")
                
                if client.get("status") == EXPECTED_ALEJANDRO["status"]:
                    checks.append("✅ Status active")
                else:
                    checks.append(f"❌ Status mismatch: expected {EXPECTED_ALEJANDRO['status']}, got {client.get('status')}")
                
                all_correct = all("✅" in check for check in checks)
                details = "; ".join(checks)
                
                self.log_test("Client Record Verification", all_correct, details, 
                            critical=not all_correct)
                
            except json.JSONDecodeError:
                self.log_test("Client Record Verification", False, 
                            "Invalid JSON response", critical=True)
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("Client Record Verification", False, 
                        f"HTTP {status_code}", critical=True)

    def test_client_readiness_verification(self):
        """Test 2: Client Readiness Verification"""
        print("🔍 Test 2: Client Readiness Verification...")
        
        if not self.admin_token:
            self.log_test("Client Readiness Verification", False, 
                        "No admin token available", critical=True)
            return
        
        # Test GET /api/clients/client_alejandro_mariscal/readiness
        response = self.make_request("GET", "/clients/client_alejandro_mariscal/readiness", 
                                   auth_token=self.admin_token)
        
        if response and response.status_code == 200:
            try:
                data = response.json()
                readiness = data.get("readiness", {})
                
                # Verify readiness flags
                checks = []
                if readiness.get("investment_ready") is True:
                    checks.append("✅ Investment ready")
                else:
                    checks.append(f"❌ Not investment ready: {readiness.get('investment_ready')}")
                
                if readiness.get("aml_kyc_completed") is True:
                    checks.append("✅ AML/KYC completed")
                else:
                    checks.append(f"❌ AML/KYC not completed: {readiness.get('aml_kyc_completed')}")
                
                if readiness.get("agreement_signed") is True:
                    checks.append("✅ Agreement signed")
                else:
                    checks.append(f"❌ Agreement not signed: {readiness.get('agreement_signed')}")
                
                all_ready = all("✅" in check for check in checks)
                details = "; ".join(checks)
                
                self.log_test("Client Readiness Verification", all_ready, details, 
                            critical=not all_ready)
                
            except json.JSONDecodeError:
                self.log_test("Client Readiness Verification", False, 
                            "Invalid JSON response", critical=True)
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("Client Readiness Verification", False, 
                        f"HTTP {status_code}", critical=True)

    def test_ready_for_investment_endpoint(self):
        """Test 3: Ready for Investment Endpoint"""
        print("🔍 Test 3: Ready for Investment Endpoint...")
        
        if not self.admin_token:
            self.log_test("Ready for Investment Endpoint", False, 
                        "No admin token available", critical=True)
            return
        
        # Test GET /api/clients/ready-for-investment
        response = self.make_request("GET", "/clients/ready-for-investment", 
                                   auth_token=self.admin_token)
        
        if response and response.status_code == 200:
            try:
                data = response.json()
                ready_clients = data.get("ready_clients", [])
                total_ready = data.get("total_ready", 0)
                
                # Check if Alejandro is in the list
                alejandro_found = False
                alejandro_data = None
                
                for client in ready_clients:
                    if (client.get("client_id") == EXPECTED_ALEJANDRO["client_id"] or 
                        client.get("email") == EXPECTED_ALEJANDRO["email"]):
                        alejandro_found = True
                        alejandro_data = client
                        break
                
                if alejandro_found:
                    checks = [f"✅ Alejandro found in ready clients list"]
                    if total_ready >= 1:
                        checks.append(f"✅ Total ready clients: {total_ready}")
                    else:
                        checks.append(f"❌ Total ready clients should be ≥1, got {total_ready}")
                    
                    details = "; ".join(checks)
                    success = total_ready >= 1
                    self.log_test("Ready for Investment Endpoint", success, details, 
                                critical=not success)
                else:
                    self.log_test("Ready for Investment Endpoint", False, 
                                f"Alejandro not found in ready clients list. Found {len(ready_clients)} clients", 
                                critical=True)
                
            except json.JSONDecodeError:
                self.log_test("Ready for Investment Endpoint", False, 
                            "Invalid JSON response", critical=True)
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("Ready for Investment Endpoint", False, 
                        f"HTTP {status_code}", critical=True)

    def test_investment_records_verification(self):
        """Test 4: Investment Records Verification"""
        print("🔍 Test 4: Investment Records Verification...")
        
        if not self.admin_token:
            self.log_test("Investment Records Verification", False, 
                        "No admin token available", critical=True)
            return
        
        # Test GET /api/clients/client_alejandro_mariscal/investments
        response = self.make_request("GET", "/clients/client_alejandro_mariscal/investments", 
                                   auth_token=self.admin_token)
        
        if response and response.status_code == 200:
            try:
                data = response.json()
                investments = data.get("investments", [])
                
                # Verify investment count
                if len(investments) == EXPECTED_ALEJANDRO["investment_count"]:
                    count_check = f"✅ Investment count: {len(investments)}"
                else:
                    count_check = f"❌ Expected {EXPECTED_ALEJANDRO['investment_count']} investments, got {len(investments)}"
                
                # Verify total investment amount
                total_amount = sum(inv.get("principal_amount", 0) for inv in investments)
                if abs(total_amount - EXPECTED_ALEJANDRO["total_investment"]) < 0.01:
                    amount_check = f"✅ Total investment: ${total_amount:,.2f}"
                else:
                    amount_check = f"❌ Expected ${EXPECTED_ALEJANDRO['total_investment']:,.2f}, got ${total_amount:,.2f}"
                
                # Verify fund types and amounts
                fund_checks = []
                for expected_inv in EXPECTED_INVESTMENTS:
                    found_inv = next((inv for inv in investments 
                                    if inv.get("fund_code") == expected_inv["fund_code"]), None)
                    if found_inv:
                        if abs(found_inv.get("principal_amount", 0) - expected_inv["amount"]) < 0.01:
                            fund_checks.append(f"✅ {expected_inv['fund_code']}: ${expected_inv['amount']:,.2f}")
                        else:
                            fund_checks.append(f"❌ {expected_inv['fund_code']}: expected ${expected_inv['amount']:,.2f}, got ${found_inv.get('principal_amount', 0):,.2f}")
                    else:
                        fund_checks.append(f"❌ {expected_inv['fund_code']} investment not found")
                
                all_checks = [count_check, amount_check] + fund_checks
                all_correct = all("✅" in check for check in all_checks)
                details = "; ".join(all_checks)
                
                self.log_test("Investment Records Verification", all_correct, details, 
                            critical=not all_correct)
                
            except json.JSONDecodeError:
                self.log_test("Investment Records Verification", False, 
                            "Invalid JSON response", critical=True)
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("Investment Records Verification", False, 
                        f"HTTP {status_code}", critical=True)

    def test_mt5_accounts_verification(self):
        """Test 5: MT5 Accounts Verification"""
        print("🔍 Test 5: MT5 Accounts Verification...")
        
        if not self.admin_token:
            self.log_test("MT5 Accounts Verification", False, 
                        "No admin token available", critical=True)
            return
        
        # Test GET /api/mt5/accounts/client_alejandro_mariscal
        response = self.make_request("GET", "/mt5/accounts/client_alejandro_mariscal", 
                                   auth_token=self.admin_token)
        
        if response and response.status_code == 200:
            try:
                data = response.json()
                mt5_accounts = data.get("accounts", [])
                
                # Verify MT5 account count
                if len(mt5_accounts) == EXPECTED_ALEJANDRO["mt5_account_count"]:
                    count_check = f"✅ MT5 account count: {len(mt5_accounts)}"
                else:
                    count_check = f"❌ Expected {EXPECTED_ALEJANDRO['mt5_account_count']} MT5 accounts, got {len(mt5_accounts)}"
                
                # Verify individual MT5 accounts
                account_checks = []
                total_mt5_balance = 0
                
                for expected_acc in EXPECTED_MT5_ACCOUNTS:
                    found_acc = next((acc for acc in mt5_accounts 
                                    if str(acc.get("login")) == str(expected_acc["login"])), None)
                    if found_acc:
                        balance = found_acc.get("balance", 0)
                        total_mt5_balance += balance
                        
                        if abs(balance - expected_acc["balance"]) < 0.01:
                            account_checks.append(f"✅ Login {expected_acc['login']}: ${balance:,.2f}")
                        else:
                            account_checks.append(f"❌ Login {expected_acc['login']}: expected ${expected_acc['balance']:,.2f}, got ${balance:,.2f}")
                        
                        # Check broker
                        if found_acc.get("broker") == "MEXAtlantic":
                            account_checks.append(f"✅ Login {expected_acc['login']} broker: MEXAtlantic")
                        else:
                            account_checks.append(f"❌ Login {expected_acc['login']} broker: expected MEXAtlantic, got {found_acc.get('broker')}")
                        
                        # Check server
                        if found_acc.get("server") == "MEXAtlantic-Real":
                            account_checks.append(f"✅ Login {expected_acc['login']} server: MEXAtlantic-Real")
                        else:
                            account_checks.append(f"❌ Login {expected_acc['login']} server: expected MEXAtlantic-Real, got {found_acc.get('server')}")
                    else:
                        account_checks.append(f"❌ MT5 account {expected_acc['login']} not found")
                
                # Verify total MT5 balance matches investment total
                if abs(total_mt5_balance - EXPECTED_ALEJANDRO["total_investment"]) < 0.01:
                    balance_check = f"✅ Total MT5 balance: ${total_mt5_balance:,.2f}"
                else:
                    balance_check = f"❌ Total MT5 balance ${total_mt5_balance:,.2f} doesn't match investment total ${EXPECTED_ALEJANDRO['total_investment']:,.2f}"
                
                all_checks = [count_check, balance_check] + account_checks
                all_correct = all("✅" in check for check in all_checks)
                details = "; ".join(all_checks)
                
                self.log_test("MT5 Accounts Verification", all_correct, details, 
                            critical=not all_correct)
                
            except json.JSONDecodeError:
                self.log_test("MT5 Accounts Verification", False, 
                            "Invalid JSON response", critical=True)
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("MT5 Accounts Verification", False, 
                        f"HTTP {status_code}", critical=True)

    def test_investment_admin_overview(self):
        """Test 6: Investment Admin Overview"""
        print("🔍 Test 6: Investment Admin Overview...")
        
        if not self.admin_token:
            self.log_test("Investment Admin Overview", False, 
                        "No admin token available", critical=True)
            return
        
        # Test GET /api/investments/admin/overview
        response = self.make_request("GET", "/investments/admin/overview", 
                                   auth_token=self.admin_token)
        
        if response and response.status_code == 200:
            try:
                data = response.json()
                
                # Verify overview includes Alejandro's investments
                checks = []
                
                total_aum = data.get("total_aum", 0)
                if total_aum >= EXPECTED_ALEJANDRO["total_investment"]:
                    checks.append(f"✅ Total AUM includes Alejandro: ${total_aum:,.2f}")
                else:
                    checks.append(f"❌ Total AUM ${total_aum:,.2f} should include Alejandro's ${EXPECTED_ALEJANDRO['total_investment']:,.2f}")
                
                total_investments = data.get("total_investments", 0)
                if total_investments >= EXPECTED_ALEJANDRO["investment_count"]:
                    checks.append(f"✅ Total investments: {total_investments}")
                else:
                    checks.append(f"❌ Total investments {total_investments} should include Alejandro's {EXPECTED_ALEJANDRO['investment_count']}")
                
                total_clients = data.get("total_clients", 0)
                if total_clients >= 1:
                    checks.append(f"✅ Total clients: {total_clients}")
                else:
                    checks.append(f"❌ Total clients {total_clients} should include Alejandro")
                
                all_correct = all("✅" in check for check in checks)
                details = "; ".join(checks)
                
                self.log_test("Investment Admin Overview", all_correct, details, 
                            critical=not all_correct)
                
            except json.JSONDecodeError:
                self.log_test("Investment Admin Overview", False, 
                            "Invalid JSON response", critical=True)
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("Investment Admin Overview", False, 
                        f"HTTP {status_code}", critical=True)

    def run_alejandro_production_test(self):
        """Run all Alejandro production setup tests"""
        print("🚀 ALEJANDRO MARISCAL PRODUCTION SETUP VERIFICATION")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Started: {datetime.now(timezone.utc).isoformat()}")
        print(f"Expected Client ID: {EXPECTED_ALEJANDRO['client_id']}")
        print(f"Expected Email: {EXPECTED_ALEJANDRO['email']}")
        print(f"Expected Total Investment: ${EXPECTED_ALEJANDRO['total_investment']:,.2f}")
        print("=" * 80)
        print()

        # Authenticate first
        if not self.authenticate_admin():
            print("🚨 CRITICAL: Admin authentication failed - cannot proceed with tests")
            return 0.0

        # Run all verification tests
        self.test_client_record_verification()
        self.test_client_readiness_verification()
        self.test_ready_for_investment_endpoint()
        self.test_investment_records_verification()
        self.test_mt5_accounts_verification()
        self.test_investment_admin_overview()

        # Generate summary
        print("=" * 80)
        print("🎯 ALEJANDRO PRODUCTION SETUP TEST SUMMARY")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()

        # Show critical failures
        if self.critical_failures:
            print("🚨 CRITICAL FAILURES:")
            for failure in self.critical_failures:
                print(f"   • {failure}")
            print()

        # Show failed tests
        failed_tests = [t for t in self.test_results if not t["success"]]
        if failed_tests:
            print("❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"   • {test['test']}: {test['error']}")
            print()

        # Production readiness assessment
        print("🔍 PRODUCTION READINESS ASSESSMENT:")
        
        if success_rate == 100:
            print("   🎉 PERFECT: Alejandro's production setup is 100% complete and ready for go-live")
        elif success_rate >= 80:
            print("   ✅ READY: Alejandro's production setup is ready with minor issues")
        elif success_rate >= 60:
            print("   ⚠️  CAUTION: Alejandro's production setup has significant issues")
        else:
            print("   🚨 CRITICAL: Alejandro's production setup is NOT ready for go-live")

        # Critical system checks
        critical_systems = [
            "Client Record Verification",
            "Client Readiness Verification", 
            "Ready for Investment Endpoint",
            "Investment Records Verification"
        ]
        
        critical_passed = sum(1 for test in self.test_results 
                            if test["test"] in critical_systems and test["success"])
        
        if critical_passed == len(critical_systems):
            print("   ✅ All critical systems operational")
        else:
            print(f"   ❌ {len(critical_systems) - critical_passed} critical systems failing")

        print()
        print("=" * 80)
        
        if success_rate >= 90 and not self.critical_failures:
            print("🎉 ALEJANDRO PRODUCTION STATUS: READY FOR GO-LIVE")
        elif success_rate >= 70:
            print("⚠️  ALEJANDRO PRODUCTION STATUS: REVIEW REQUIRED BEFORE GO-LIVE")
        else:
            print("🚨 ALEJANDRO PRODUCTION STATUS: NOT READY - IMMEDIATE FIXES REQUIRED")
            
        print("=" * 80)
        
        return success_rate

if __name__ == "__main__":
    tester = AlejandroProductionTester()
    success_rate = tester.run_alejandro_production_test()
    
    # Exit with appropriate code
    sys.exit(0 if success_rate >= 90 else 1)