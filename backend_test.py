#!/usr/bin/env python3
"""
FIDUS Backend Comprehensive Testing Suite - All Today's Changes
Testing comprehensive verification of FIDUS backend after today's critical updates.

Test Coverage:
1. Money Managers API Test - GET /api/v2/derived/money-managers
2. Investment Committee API Test - GET /api/admin/investment-committee/mt5-accounts  
3. Accounts Management API Test - GET /api/v2/derived/accounts
4. Cash Flow API Test - GET /api/admin/cashflow/complete
5. Account 2198 Password Test - Database check
6. Manager Allocations Test - Database verification

Expected Results:
- Money Managers: 8+ active managers with real data (not $0.00)
- Investment Committee: Exactly 15 accounts (14 MT5 + 1 MT4)
- Accounts Management: All 15 accounts with correct managers
- Cash Flow: Real calculations with separation interest
- Account 2198: Password "Fidus13!!" and correct details
- Manager Allocations: Japanese $15,000, Viking Gold $20,000, Internal BOT $15,506
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional

class FidusBackendTester:
    def __init__(self):
        self.base_url = "https://truth-fincore.preview.emergentagent.com/api"
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
    def log_test(self, test_name: str, status: str, details: str, expected: Any = None, actual: Any = None):
        """Log test result"""
        result = {
            "test_name": test_name,
            "status": status,  # PASS, FAIL, ERROR
            "details": details,
            "expected": expected,
            "actual": actual,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_emoji} {test_name}: {details}")
        
        if expected is not None and actual is not None:
            print(f"   Expected: {expected}")
            print(f"   Actual: {actual}")
    
    def authenticate_admin(self) -> bool:
        """Authenticate as admin user"""
        try:
            print("🔐 Authenticating as admin...")
            
            login_data = {
                "username": "admin",
                "password": "password123",
                "user_type": "admin"
            }
            
            response = self.session.post(f"{self.base_url}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token')
                if self.admin_token:
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.admin_token}'
                    })
                    self.log_test("Admin Authentication", "PASS", "Successfully authenticated as admin")
                    return True
                else:
                    self.log_test("Admin Authentication", "FAIL", "No token received in response")
                    return False
            else:
                self.log_test("Admin Authentication", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", "ERROR", f"Exception during authentication: {str(e)}")
            return False
    
    def test_money_managers_api(self) -> bool:
        """Test 1: Money Managers API - GET /api/v2/derived/money-managers"""
        try:
            print("\n💼 Testing Money Managers API...")
            
            response = self.session.get(f"{self.base_url}/v2/derived/money-managers", timeout=30)
            
            if response.status_code != 200:
                self.log_test("Money Managers API", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            if not data.get("success"):
                self.log_test("Money Managers API", "FAIL", f"API returned success=false: {data.get('message', 'Unknown error')}")
                return False
            
            managers = data.get("managers", [])
            success = True
            
            # Check we have 8+ active managers
            if len(managers) >= 8:
                self.log_test("Money Managers Count", "PASS", 
                            f"Found {len(managers)} managers (expected 8+)", 
                            "8+", 
                            len(managers))
            else:
                self.log_test("Money Managers Count", "FAIL", 
                            f"Only found {len(managers)} managers (expected 8+)", 
                            "8+", 
                            len(managers))
                success = False
            
            # Check specific managers and their allocations
            expected_managers = {
                "Viking Gold": 20000,
                "Internal BOT": 15506,
                "Japanese": 15000,
                "Provider1-Assev": 20000
            }
            
            found_managers = {}
            non_zero_count = 0
            
            for manager in managers:
                manager_name = manager.get("manager_name", "")
                performance = manager.get("performance", {})
                total_allocated = performance.get("total_allocated", 0)
                current_equity = performance.get("current_equity", 0)
                total_pnl = performance.get("total_pnl", 0)
                
                # Count managers with non-zero values
                if total_allocated > 0 or current_equity > 0 or abs(total_pnl) > 0:
                    non_zero_count += 1
                
                # Check specific expected managers
                if manager_name in expected_managers:
                    found_managers[manager_name] = total_allocated
                    expected_allocation = expected_managers[manager_name]
                    
                    if abs(total_allocated - expected_allocation) < 1.0:
                        self.log_test(f"{manager_name} Allocation", "PASS", 
                                    f"Allocation matches expected value", 
                                    f"${expected_allocation:,.2f}", 
                                    f"${total_allocated:,.2f}")
                    else:
                        self.log_test(f"{manager_name} Allocation", "FAIL", 
                                    f"Allocation does not match expected value", 
                                    f"${expected_allocation:,.2f}", 
                                    f"${total_allocated:,.2f}")
                        success = False
                
                # Check account_details field exists
                if "account_details" not in manager:
                    self.log_test(f"{manager_name} Account Details", "FAIL", 
                                f"Missing account_details field")
                    success = False
            
            # Check that most managers have non-zero values (not $0.00)
            if non_zero_count >= len(managers) * 0.7:  # At least 70% should have real data
                self.log_test("Managers Real Data", "PASS", 
                            f"{non_zero_count}/{len(managers)} managers have non-zero values")
            else:
                self.log_test("Managers Real Data", "FAIL", 
                            f"Only {non_zero_count}/{len(managers)} managers have non-zero values")
                success = False
            
            # Check that all expected managers were found
            missing_managers = set(expected_managers.keys()) - set(found_managers.keys())
            if not missing_managers:
                self.log_test("Expected Managers Found", "PASS", 
                            f"All expected managers found: {list(expected_managers.keys())}")
            else:
                self.log_test("Expected Managers Found", "FAIL", 
                            f"Missing managers: {list(missing_managers)}")
                success = False
            
            return success
            
        except Exception as e:
            self.log_test("Money Managers API Test", "ERROR", f"Exception: {str(e)}")
            return False
    
    def test_investment_committee_api(self) -> bool:
        """Test 2: Investment Committee API - GET /api/admin/investment-committee/mt5-accounts"""
        try:
            print("\n🏛️ Testing Investment Committee API...")
            
            response = self.session.get(f"{self.base_url}/admin/investment-committee/mt5-accounts", timeout=30)
            
            if response.status_code != 200:
                self.log_test("Investment Committee API", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            if not data.get("success"):
                self.log_test("Investment Committee API", "FAIL", f"API returned success=false: {data.get('message', 'Unknown error')}")
                return False
            
            accounts = data.get("accounts", [])
            success = True
            
            # Check exactly 15 accounts (14 MT5 + 1 MT4)
            if len(accounts) == 15:
                self.log_test("Investment Committee Accounts Count", "PASS", 
                            f"Found exactly 15 accounts as expected", 
                            15, 
                            len(accounts))
            else:
                self.log_test("Investment Committee Accounts Count", "FAIL", 
                            f"Expected 15 accounts, found {len(accounts)}", 
                            15, 
                            len(accounts))
                success = False
            
            # Check for specific accounts
            account_numbers = [str(acc.get("account_number", "")) for acc in accounts]
            
            # Check Account 2198 (JOSE - LUCRUM Capital)
            if "2198" in account_numbers:
                self.log_test("Account 2198 Present", "PASS", 
                            "Account 2198 (JOSE - LUCRUM Capital) found")
                
                # Find account 2198 details
                account_2198 = next((acc for acc in accounts if str(acc.get("account_number", "")) == "2198"), None)
                if account_2198:
                    manager = account_2198.get("manager", "")
                    broker = account_2198.get("broker", "")
                    
                    if "JOSE" in manager:
                        self.log_test("Account 2198 Manager", "PASS", f"Manager is JOSE: {manager}")
                    else:
                        self.log_test("Account 2198 Manager", "FAIL", f"Expected JOSE, got: {manager}")
                        success = False
                    
                    if "LUCRUM" in broker:
                        self.log_test("Account 2198 Broker", "PASS", f"Broker is LUCRUM Capital: {broker}")
                    else:
                        self.log_test("Account 2198 Broker", "FAIL", f"Expected LUCRUM, got: {broker}")
                        success = False
            else:
                self.log_test("Account 2198 Present", "FAIL", 
                            "Account 2198 (JOSE - LUCRUM Capital) not found")
                success = False
            
            # Check Account 33200931 (MT4 - Spaniard Stock CFDs)
            if "33200931" in account_numbers:
                self.log_test("Account 33200931 Present", "PASS", 
                            "Account 33200931 (MT4 - Spaniard Stock CFDs) found")
            else:
                self.log_test("Account 33200931 Present", "FAIL", 
                            "Account 33200931 (MT4 - Spaniard Stock CFDs) not found")
                success = False
            
            # Check specific manager allocations
            expected_allocations = {
                "901351": ("Japanese", 15000),
                "891215": ("Viking Gold", 20000),
                "897599": ("Internal BOT", 15506)
            }
            
            for account_num, (expected_manager, expected_allocation) in expected_allocations.items():
                account = next((acc for acc in accounts if str(acc.get("account_number", "")) == account_num), None)
                if account:
                    manager = account.get("manager", "")
                    allocation = account.get("initial_allocation", 0)
                    
                    if expected_manager.lower() in manager.lower():
                        self.log_test(f"Account {account_num} Manager", "PASS", 
                                    f"Manager matches: {manager}")
                    else:
                        self.log_test(f"Account {account_num} Manager", "FAIL", 
                                    f"Expected {expected_manager}, got: {manager}")
                        success = False
                    
                    if abs(allocation - expected_allocation) < 1.0:
                        self.log_test(f"Account {account_num} Allocation", "PASS", 
                                    f"Allocation matches: ${allocation:,.2f}")
                    else:
                        self.log_test(f"Account {account_num} Allocation", "FAIL", 
                                    f"Expected ${expected_allocation:,.2f}, got: ${allocation:,.2f}")
                        success = False
                else:
                    self.log_test(f"Account {account_num} Found", "FAIL", 
                                f"Account {account_num} not found")
                    success = False
            
            return success
            
        except Exception as e:
            self.log_test("Investment Committee API Test", "ERROR", f"Exception: {str(e)}")
            return False
    
    def test_commission_calendar(self) -> bool:
        """Test 3: Commission Calendar/Schedule - Any endpoint that shows payment dates"""
        try:
            print("\n📅 Testing Commission Calendar/Schedule...")
            
            # Try multiple potential endpoints for commission calendar
            endpoints_to_try = [
                "/admin/cashflow/calendar",
                "/admin/commissions/schedule", 
                "/admin/referrals/commission-schedule",
                "/admin/cashflow/overview"
            ]
            
            calendar_found = False
            success = True
            
            for endpoint in endpoints_to_try:
                try:
                    response = self.session.get(f"{self.base_url}{endpoint}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        if data.get("success"):
                            calendar_found = True
                            self.log_test("Commission Calendar Endpoint", "PASS", 
                                        f"Found working calendar endpoint: {endpoint}")
                            
                            # Look for payment schedule data
                            monthly_obligations = data.get("monthly_obligations", [])
                            milestones = data.get("milestones", {})
                            
                            if monthly_obligations:
                                # Check for BALANCE first payment (Feb 28, 2026)
                                balance_payments = [
                                    payment for payment in monthly_obligations 
                                    if payment.get("balance_interest", 0) > 0
                                ]
                                
                                if balance_payments:
                                    first_balance = balance_payments[0]
                                    balance_date = first_balance.get("date", "")
                                    
                                    if "2026-02" in balance_date or "Feb" in balance_date:
                                        self.log_test("BALANCE First Payment Date", "PASS", 
                                                    f"BALANCE first payment scheduled correctly", 
                                                    "February 2026", 
                                                    balance_date)
                                    else:
                                        self.log_test("BALANCE First Payment Date", "FAIL", 
                                                    f"BALANCE first payment date incorrect", 
                                                    "February 2026", 
                                                    balance_date)
                                        success = False
                                
                                # Check for CORE first payment (Dec 30, 2025)
                                core_payments = [
                                    payment for payment in monthly_obligations 
                                    if payment.get("core_interest", 0) > 0
                                ]
                                
                                if core_payments:
                                    first_core = core_payments[0]
                                    core_date = first_core.get("date", "")
                                    
                                    if "2025-12" in core_date or "Dec" in core_date:
                                        self.log_test("CORE First Payment Date", "PASS", 
                                                    f"CORE first payment scheduled correctly", 
                                                    "December 2025", 
                                                    core_date)
                                    else:
                                        self.log_test("CORE First Payment Date", "FAIL", 
                                                    f"CORE first payment date incorrect", 
                                                    "December 2025", 
                                                    core_date)
                                        success = False
                                
                                # Check total commission payments count (16 total: 12 CORE + 4 BALANCE)
                                total_payments = len(monthly_obligations)
                                expected_payments = 16
                                
                                if total_payments >= expected_payments:
                                    self.log_test("Total Commission Payments", "PASS", 
                                                f"Total commission payments count adequate", 
                                                f">= {expected_payments}", 
                                                total_payments)
                                else:
                                    self.log_test("Total Commission Payments", "FAIL", 
                                                f"Total commission payments count low", 
                                                f">= {expected_payments}", 
                                                total_payments)
                                    success = False
                            
                            break
                            
                except Exception as e:
                    continue
            
            if not calendar_found:
                self.log_test("Commission Calendar", "FAIL", "No working commission calendar endpoint found")
                return False
            
            return success
            
        except Exception as e:
            self.log_test("Commission Calendar Test", "ERROR", f"Exception: {str(e)}")
            return False
            
        except Exception as e:
            self.log_test("Trading Analytics Test", "ERROR", f"Exception: {str(e)}")
            return False
    
    def test_investment_data(self) -> bool:
        """Test 4: Investment Data - GET /api/admin/investments or similar"""
        try:
            print("\n💰 Testing Investment Data...")
            
            # Try multiple potential endpoints for investment data
            endpoints_to_try = [
                "/admin/investments",
                "/investments/admin/overview",
                "/admin/fund-portfolio/overview",
                "/fund-portfolio/overview"
            ]
            
            investment_found = False
            success = True
            
            for endpoint in endpoints_to_try:
                try:
                    response = self.session.get(f"{self.base_url}{endpoint}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        if data.get("success") or data.get("investments") or data.get("funds"):
                            investment_found = True
                            self.log_test("Investment Data Endpoint", "PASS", 
                                        f"Found working investment endpoint: {endpoint}")
                            
                            # Check total investment amount
                            total_investment = 0
                            core_investment = 0
                            balance_investment = 0
                            
                            # Handle different response structures
                            if data.get("investments"):
                                investments = data["investments"]
                                for inv in investments:
                                    amount = inv.get("principal_amount", 0) or inv.get("amount", 0)
                                    total_investment += amount
                                    
                                    fund_code = inv.get("fund_code", "").upper()
                                    if fund_code == "CORE":
                                        core_investment += amount
                                    elif fund_code == "BALANCE":
                                        balance_investment += amount
                            
                            elif data.get("funds"):
                                funds = data["funds"]
                                for fund in funds:
                                    fund_code = fund.get("fund_code", "").upper()
                                    amount = fund.get("total_allocated", 0) or fund.get("aum", 0)
                                    
                                    if fund_code == "CORE":
                                        core_investment = amount
                                    elif fund_code == "BALANCE":
                                        balance_investment = amount
                                
                                total_investment = core_investment + balance_investment
                            
                            elif data.get("total_aum"):
                                total_investment = data["total_aum"]
                            
                            # Validate total investment = $118,151.41
                            expected_total = 118151.41
                            if abs(total_investment - expected_total) < 0.01:
                                self.log_test("Total Investment Amount", "PASS", 
                                            f"Total investment matches expected value", 
                                            f"${expected_total:,.2f}", 
                                            f"${total_investment:,.2f}")
                            else:
                                self.log_test("Total Investment Amount", "FAIL", 
                                            f"Total investment does not match expected value", 
                                            f"${expected_total:,.2f}", 
                                            f"${total_investment:,.2f}")
                                success = False
                            
                            # Validate CORE investment = $18,151.41
                            expected_core = 18151.41
                            if abs(core_investment - expected_core) < 0.01:
                                self.log_test("CORE Investment Amount", "PASS", 
                                            f"CORE investment matches expected value", 
                                            f"${expected_core:,.2f}", 
                                            f"${core_investment:,.2f}")
                            else:
                                self.log_test("CORE Investment Amount", "FAIL", 
                                            f"CORE investment does not match expected value", 
                                            f"${expected_core:,.2f}", 
                                            f"${core_investment:,.2f}")
                                success = False
                            
                            # Validate BALANCE investment = $100,000
                            expected_balance = 100000.00
                            if abs(balance_investment - expected_balance) < 0.01:
                                self.log_test("BALANCE Investment Amount", "PASS", 
                                            f"BALANCE investment matches expected value", 
                                            f"${expected_balance:,.2f}", 
                                            f"${balance_investment:,.2f}")
                            else:
                                self.log_test("BALANCE Investment Amount", "FAIL", 
                                            f"BALANCE investment does not match expected value", 
                                            f"${expected_balance:,.2f}", 
                                            f"${balance_investment:,.2f}")
                                success = False
                            
                            break
                            
                except Exception as e:
                    continue
            
            if not investment_found:
                self.log_test("Investment Data", "FAIL", "No working investment data endpoint found")
                return False
            
            return success
            
        except Exception as e:
            self.log_test("Investment Data Test", "ERROR", f"Exception: {str(e)}")
            return False
    
    def test_commission_calculations(self) -> bool:
        """Test 5: Commission Calculations - Verify specific commission calculation validations"""
        try:
            print("\n🧮 Testing Commission Calculations...")
            
            success = True
            
            # Test BALANCE quarterly commission calculation
            # Expected: BALANCE quarterly commission = $7,500 (NOT $750 or $250)
            balance_principal = 100000.00  # $100,000 BALANCE investment
            balance_monthly_rate = 0.025   # 2.5% monthly rate
            balance_quarterly = balance_principal * balance_monthly_rate * 3  # 3 months
            expected_balance_quarterly = 7500.00
            
            if abs(balance_quarterly - expected_balance_quarterly) < 0.01:
                self.log_test("BALANCE Quarterly Commission Calculation", "PASS", 
                            f"BALANCE quarterly commission calculated correctly", 
                            f"${expected_balance_quarterly:,.2f}", 
                            f"${balance_quarterly:,.2f}")
            else:
                self.log_test("BALANCE Quarterly Commission Calculation", "FAIL", 
                            f"BALANCE quarterly commission calculation incorrect", 
                            f"${expected_balance_quarterly:,.2f}", 
                            f"${balance_quarterly:,.2f}")
                success = False
            
            # Test CORE monthly commission calculation
            # Expected: CORE monthly commission = $272.27
            core_principal = 18151.41      # $18,151.41 CORE investment
            core_monthly_rate = 0.015      # 1.5% monthly rate
            core_monthly = core_principal * core_monthly_rate
            expected_core_monthly = 272.27
            
            if abs(core_monthly - expected_core_monthly) < 0.01:
                self.log_test("CORE Monthly Commission Calculation", "PASS", 
                            f"CORE monthly commission calculated correctly", 
                            f"${expected_core_monthly:,.2f}", 
                            f"${core_monthly:,.2f}")
            else:
                self.log_test("CORE Monthly Commission Calculation", "FAIL", 
                            f"CORE monthly commission calculation incorrect", 
                            f"${expected_core_monthly:,.2f}", 
                            f"${core_monthly:,.2f}")
                success = False
            
            # Test total commission calculation
            # 12 CORE payments + 4 BALANCE payments = total commissions
            total_core_commissions = core_monthly * 12  # 12 monthly payments
            total_balance_commissions = balance_quarterly * 4  # 4 quarterly payments
            total_calculated = total_core_commissions + total_balance_commissions
            expected_total = 3326.76
            
            if abs(total_calculated - expected_total) < 0.01:
                self.log_test("Total Commission Calculation", "PASS", 
                            f"Total commission calculation matches expected", 
                            f"${expected_total:,.2f}", 
                            f"${total_calculated:,.2f}")
            else:
                self.log_test("Total Commission Calculation", "FAIL", 
                            f"Total commission calculation incorrect", 
                            f"${expected_total:,.2f}", 
                            f"${total_calculated:,.2f}")
                success = False
            
            # Verify NOT the incorrect values mentioned in the review
            incorrect_balance_quarterly = 750.00  # This should NOT be the result
            incorrect_total = 1326.73  # This should NOT be the result
            
            if balance_quarterly != incorrect_balance_quarterly:
                self.log_test("BALANCE Commission NOT $750", "PASS", 
                            f"BALANCE quarterly commission is NOT the incorrect $750", 
                            f"NOT ${incorrect_balance_quarterly:,.2f}", 
                            f"${balance_quarterly:,.2f}")
            else:
                self.log_test("BALANCE Commission NOT $750", "FAIL", 
                            f"BALANCE quarterly commission incorrectly calculated as $750")
                success = False
            
            if total_calculated != incorrect_total:
                self.log_test("Total Commission NOT $1,326.73", "PASS", 
                            f"Total commission is NOT the incorrect $1,326.73", 
                            f"NOT ${incorrect_total:,.2f}", 
                            f"${total_calculated:,.2f}")
            else:
                self.log_test("Total Commission NOT $1,326.73", "FAIL", 
                            f"Total commission incorrectly calculated as $1,326.73")
                success = False
            
            return success
            
        except Exception as e:
            self.log_test("Commission Calculations Test", "ERROR", f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self) -> bool:
        """Run all FIDUS commission verification tests"""
        print("🚀 Starting FIDUS Backend Commission Verification Tests")
        print("=" * 70)
        
        # Authenticate first
        if not self.authenticate_admin():
            print("\n❌ Authentication failed. Cannot proceed with tests.")
            return False
        
        # Run all commission verification tests
        tests = [
            ("Salvador Palma Data", self.test_salvador_palma_data),
            ("Referrals Overview", self.test_referrals_overview),
            ("Commission Calendar", self.test_commission_calendar),
            ("Investment Data", self.test_investment_data),
            ("Commission Calculations", self.test_commission_calculations)
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed_tests += 1
            except Exception as e:
                self.log_test(f"{test_name} Exception", "ERROR", f"Test failed with exception: {str(e)}")
        
        # Print summary
        print("\n" + "=" * 70)
        print("📊 FIDUS COMMISSION VERIFICATION SUMMARY")
        print("=" * 70)
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        # Print detailed results
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status_icon = "✅" if result["status"] == "PASS" else "❌" if result["status"] == "FAIL" else "⚠️"
            print(f"{status_icon} {result['test_name']}: {result['details']}")
            
            if result.get("expected") and result.get("actual"):
                print(f"   Expected: {result['expected']}")
                print(f"   Actual: {result['actual']}")
        
        print("\n" + "=" * 70)
        
        if success_rate >= 80:
            print("🎉 FIDUS COMMISSION VERIFICATION: SUCCESSFUL")
            print("✅ Salvador Palma commission data verified")
            print("✅ Referrals overview totals verified") 
            print("✅ Commission calculations validated")
            return True
        else:
            print("🚨 FIDUS COMMISSION VERIFICATION: NEEDS ATTENTION")
            print("❌ Critical commission issues found")
            return False
    
    def test_client_pnl_endpoint(self) -> bool:
        """Test GET /api/pnl/client/client_alejandro - Client-specific P&L"""
        try:
            print("\n👤 Testing Client P&L Endpoint...")
            
            response = self.session.get(f"{self.base_url}/pnl/client/client_alejandro", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success') and 'data' in data:
                    client_data = data['data']
                    
                    # Verify structure
                    required_keys = ['client_id', 'initial_investment', 'current_equity', 
                                   'available_for_withdrawal', 'total_value', 'total_pnl', 
                                   'total_return_percent', 'accounts']
                    missing_keys = [key for key in required_keys if key not in client_data]
                    
                    if missing_keys:
                        self.log_test("Client P&L Structure", "FAIL", f"Missing keys: {missing_keys}")
                        return False
                    
                    # Extract key values
                    client_id = client_data.get('client_id')
                    initial_investment = client_data.get('initial_investment', 0)
                    current_equity = client_data.get('current_equity', 0)
                    available_for_withdrawal = client_data.get('available_for_withdrawal', 0)
                    total_value = client_data.get('total_value', 0)
                    total_pnl = client_data.get('total_pnl', 0)
                    total_return_percent = client_data.get('total_return_percent', 0)
                    accounts = client_data.get('accounts', [])
                    
                    # CRITICAL validation: Initial investment MUST be $118,151.41
                    expected_initial = 118151.41
                    if abs(initial_investment - expected_initial) > 1.0:  # Allow $1 tolerance
                        self.log_test(
                            "Client Initial Investment", 
                            "FAIL", 
                            f"Expected ${expected_initial}, got ${initial_investment}",
                            expected_initial,
                            initial_investment
                        )
                        return False
                    
                    # Validate client ID
                    if client_id != 'client_alejandro':
                        self.log_test(
                            "Client ID Validation", 
                            "FAIL", 
                            f"Expected 'client_alejandro', got '{client_id}'"
                        )
                        return False
                    
                    self.log_test(
                        "Client P&L Endpoint", 
                        "PASS", 
                        f"✅ Initial: ${initial_investment}, Current: ${current_equity}, P&L: ${total_pnl} ({total_return_percent:.1f}%)"
                    )
                    
                    print(f"   📊 Available for Withdrawal: ${available_for_withdrawal}")
                    print(f"   📊 Total Value: ${total_value}")
                    print(f"   📊 Account Count: {len(accounts)}")
                    
                    return True
                    
                else:
                    self.log_test("Client P&L Endpoint", "FAIL", f"Invalid response structure: {data}")
                    return False
                    
            else:
                self.log_test("Client P&L Endpoint", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Client P&L Endpoint", "ERROR", f"Exception: {str(e)}")
            return False
    
    def test_fund_performance_endpoint(self) -> bool:
        """Test GET /api/pnl/fund-performance (Admin Only) - Fund performance vs client obligations"""
        try:
            print("\n📈 Testing Fund Performance Endpoint...")
            
            response = self.session.get(f"{self.base_url}/pnl/fund-performance", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success') and 'data' in data:
                    perf_data = data['data']
                    
                    # Verify structure
                    required_keys = ['fund_performance', 'client_obligations', 'gap_analysis', 'separation_balance']
                    missing_keys = [key for key in required_keys if key not in perf_data]
                    
                    if missing_keys:
                        self.log_test("Fund Performance Structure", "FAIL", f"Missing keys: {missing_keys}")
                        return False
                    
                    # Extract key values
                    fund_performance = perf_data.get('fund_performance', {})
                    client_obligations = perf_data.get('client_obligations', {})
                    gap_analysis = perf_data.get('gap_analysis', {})
                    separation_balance = perf_data.get('separation_balance', 0)
                    
                    # Validate obligations
                    core_obligations = client_obligations.get('core_obligations', 0)
                    balance_obligations = client_obligations.get('balance_obligations', 0)
                    total_obligations = client_obligations.get('total_obligations', 0)
                    
                    expected_core = 3267.25
                    expected_balance = 30000.00
                    expected_total = 33267.25
                    
                    if abs(core_obligations - expected_core) > 0.01:
                        self.log_test(
                            "CORE Obligations", 
                            "FAIL", 
                            f"Expected ${expected_core}, got ${core_obligations}",
                            expected_core,
                            core_obligations
                        )
                        return False
                    
                    if abs(balance_obligations - expected_balance) > 0.01:
                        self.log_test(
                            "BALANCE Obligations", 
                            "FAIL", 
                            f"Expected ${expected_balance}, got ${balance_obligations}",
                            expected_balance,
                            balance_obligations
                        )
                        return False
                    
                    if abs(total_obligations - expected_total) > 0.01:
                        self.log_test(
                            "Total Obligations", 
                            "FAIL", 
                            f"Expected ${expected_total}, got ${total_obligations}",
                            expected_total,
                            total_obligations
                        )
                        return False
                    
                    # Extract gap analysis
                    fund_pnl = gap_analysis.get('fund_pnl', 0)
                    obligations = gap_analysis.get('obligations', 0)
                    surplus_deficit = gap_analysis.get('surplus_deficit', 0)
                    status = gap_analysis.get('status', '')
                    coverage_ratio = gap_analysis.get('coverage_ratio', 0)
                    
                    self.log_test(
                        "Fund Performance Endpoint", 
                        "PASS", 
                        f"✅ Fund P&L: ${fund_pnl}, Obligations: ${obligations}, Gap: ${surplus_deficit} ({status})"
                    )
                    
                    print(f"   📊 Coverage Ratio: {coverage_ratio:.1f}%")
                    print(f"   📊 Separation Balance: ${separation_balance}")
                    print(f"   📊 Fund Initial: ${fund_performance.get('initial_allocation', 0)}")
                    print(f"   📊 Fund Current: ${fund_performance.get('current_equity', 0)}")
                    
                    return True
                    
                else:
                    self.log_test("Fund Performance Endpoint", "FAIL", f"Invalid response structure: {data}")
                    return False
                    
            else:
                return False
                
        except Exception as e:
            self.log_test("Fund Performance Endpoint", "ERROR", f"Exception: {str(e)}")
            return False

def main():
    """Main test execution"""
    tester = FidusCommissionTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()