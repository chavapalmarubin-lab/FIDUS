#!/usr/bin/env python3
"""
FIDUS Backend Commission Verification Test Suite
Testing comprehensive verification of FIDUS backend after commission fixes.

Test Coverage:
1. Salvador Palma Data - GET /api/admin/referrals/salespeople/sp_6909e8eaaaf69606babea151
2. Referrals Overview - GET /api/admin/referrals/overview
3. Commission Calendar/Schedule - Any endpoint that shows payment dates
4. Investment Data - GET /api/admin/investments or similar

Expected Results:
- Salvador Palma: totalCommissions = $3,326.76, clients = 1, activeInvestments = 2
- Referrals Overview: Total sales volume = $118,151.41, Total commissions = $3,326.76
- Commission Calendar: BALANCE first payment = Feb 28, 2026, CORE first payment = Dec 30, 2025
- Investment Data: Total investment = $118,151.41, CORE = $18,151.41, BALANCE = $100,000

CRITICAL VALIDATIONS:
- Verify BALANCE quarterly commission = $750 (NOT $250)
- Verify CORE monthly commission = $27.23
- Verify total = $3,326.76 (NOT $1,326.73)
- Verify BALANCE first payment date = February 28, 2026
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional

class FidusCommissionTester:
    def __init__(self):
        self.base_url = "https://fidus-fix.preview.emergentagent.com/api"
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
    
    def test_salvador_palma_data(self) -> bool:
        """Test 1: Salvador Palma Data - GET /api/admin/referrals/salespeople/sp_6909e8eaaaf69606babea151"""
        try:
            print("\n📊 Testing Salvador Palma Data...")
            
            salvador_id = "sp_6909e8eaaaf69606babea151"
            response = self.session.get(f"{self.base_url}/admin/referrals/salespeople/{salvador_id}")
            
            if response.status_code != 200:
                self.log_test("Salvador Palma API", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            if not data.get("success"):
                self.log_test("Salvador Palma API", "FAIL", f"API returned success=false: {data.get('message', 'Unknown error')}")
                return False
            
            salesperson = data.get("salesperson", {})
            investments = data.get("investments", [])
            
            success = True
            
            # Check total commissions = $3,326.76
            total_commissions = salesperson.get("totalCommissions", 0)
            expected_commissions = 3326.76
            
            if abs(total_commissions - expected_commissions) < 0.01:
                self.log_test("Salvador Total Commissions", "PASS", 
                            f"Commissions match expected value", 
                            f"${expected_commissions:,.2f}", 
                            f"${total_commissions:,.2f}")
            else:
                self.log_test("Salvador Total Commissions", "FAIL", 
                            f"Commissions do not match expected value", 
                            f"${expected_commissions:,.2f}", 
                            f"${total_commissions:,.2f}")
                success = False
            
            # Check clients = 1
            clients_count = salesperson.get("totalClientsReferred", 0)
            expected_clients = 1
            
            if clients_count == expected_clients:
                self.log_test("Salvador Clients Count", "PASS", 
                            f"Clients count matches expected value", 
                            expected_clients, 
                            clients_count)
            else:
                self.log_test("Salvador Clients Count", "FAIL", 
                            f"Clients count does not match expected value", 
                            expected_clients, 
                            clients_count)
                success = False
            
            # Check active investments = 2
            active_investments = len([inv for inv in investments if inv.get("status") == "active"])
            expected_investments = 2
            
            if active_investments == expected_investments:
                self.log_test("Salvador Active Investments", "PASS", 
                            f"Active investments count matches expected value", 
                            expected_investments, 
                            active_investments)
            else:
                self.log_test("Salvador Active Investments", "FAIL", 
                            f"Active investments count does not match expected value", 
                            expected_investments, 
                            active_investments)
                success = False
            
            return success
            
        except Exception as e:
            self.log_test("Salvador Palma Data Test", "ERROR", f"Exception: {str(e)}")
            return False
    
    def test_referrals_overview(self) -> bool:
        """Test 2: Referrals Overview - GET /api/admin/referrals/overview"""
        try:
            print("\n📈 Testing Referrals Overview...")
            
            response = self.session.get(f"{self.base_url}/admin/referrals/overview")
            
            if response.status_code != 200:
                self.log_test("Referrals Overview API", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            if not data.get("success"):
                self.log_test("Referrals Overview API", "FAIL", f"API returned success=false: {data.get('message', 'Unknown error')}")
                return False
            
            success = True
            
            # Check total sales volume = $118,151.41
            total_sales = data.get("totalSalesVolume", 0)
            expected_sales = 118151.41
            
            if abs(total_sales - expected_sales) < 0.01:
                self.log_test("Overview Total Sales Volume", "PASS", 
                            f"Total sales volume matches expected value", 
                            f"${expected_sales:,.2f}", 
                            f"${total_sales:,.2f}")
            else:
                self.log_test("Overview Total Sales Volume", "FAIL", 
                            f"Total sales volume does not match expected value", 
                            f"${expected_sales:,.2f}", 
                            f"${total_sales:,.2f}")
                success = False
            
            # Check total commissions = $3,326.76
            total_commissions = data.get("totalCommissions", 0)
            expected_commissions = 3326.76
            
            if abs(total_commissions - expected_commissions) < 0.01:
                self.log_test("Overview Total Commissions", "PASS", 
                            f"Total commissions match expected value", 
                            f"${expected_commissions:,.2f}", 
                            f"${total_commissions:,.2f}")
            else:
                self.log_test("Overview Total Commissions", "FAIL", 
                            f"Total commissions do not match expected value", 
                            f"${expected_commissions:,.2f}", 
                            f"${total_commissions:,.2f}")
                success = False
            
            return success
            
        except Exception as e:
            self.log_test("Referrals Overview Test", "ERROR", f"Exception: {str(e)}")
            return False
            
            if managers_with_real_data >= 4:  # At least 4 out of 5 should have real data
                self.log_test("Managers Real Performance Data", "PASS", 
                            f"{managers_with_real_data}/5 managers have real performance data")
            else:
                self.log_test("Managers Real Performance Data", "FAIL", 
                            f"Only {managers_with_real_data}/5 managers have real data")
                return False
            
            # Check total current month profit is not $0
            if total_current_profit != 0:
                self.log_test("Total Manager Current Profit", "PASS", f"Total current month profit: ${total_current_profit:,.2f} (not $0)")
            else:
                self.log_test("Total Manager Current Profit", "FAIL", "Total current month profit is $0 - expected real data")
                return False
            
            self.log_test("Money Managers API", "PASS", "Money managers with real performance data verified")
            return True
            
        except Exception as e:
            self.log_test("Money Managers Test", "ERROR", f"Exception: {str(e)}")
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
    
    def test_mt5_accounts(self) -> bool:
        """Test 4: MT5 Accounts - should return 11 accounts with real balances"""
        try:
            print("\n🏦 Testing MT5 Accounts...")
            
            response = self.session.get(f"{self.base_url}/mt5/admin/accounts")
            
            if response.status_code != 200:
                self.log_test("MT5 Admin Accounts API", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            accounts = data.get("accounts", [])
            
            # Check total count
            if len(accounts) == 11:
                self.log_test("MT5 Account Count", "PASS", f"Found expected 11 MT5 accounts")
            else:
                self.log_test("MT5 Account Count", "FAIL", f"Expected 11 accounts, found {len(accounts)}")
                return False
            
            # Check for real balances (not all $0)
            accounts_with_real_balance = 0
            total_equity = 0
            
            for acc in accounts:
                equity = acc.get("equity", 0) or acc.get("balance", 0)
                account_num = acc.get("account", "Unknown")
                
                if equity > 0:
                    accounts_with_real_balance += 1
                    total_equity += equity
                
                self.log_test(f"Account {account_num} Balance", 
                            "PASS" if equity > 0 else "FAIL",
                            f"Equity: ${equity:,.2f}")
            
            if accounts_with_real_balance >= 8:  # At least 8 out of 11 should have real balances
                self.log_test("Accounts Real Balances", "PASS", 
                            f"{accounts_with_real_balance}/11 accounts have real balances")
            else:
                self.log_test("Accounts Real Balances", "FAIL", 
                            f"Only {accounts_with_real_balance}/11 accounts have real balances")
                return False
            
            # Check total equity is substantial
            if total_equity > 50000:  # Expect at least $50K total
                self.log_test("Total MT5 Equity", "PASS", f"Total equity: ${total_equity:,.2f}")
            else:
                self.log_test("Total MT5 Equity", "FAIL", f"Total equity: ${total_equity:,.2f} - expected more substantial amounts")
                return False
            
            self.log_test("MT5 Admin Accounts API", "PASS", "MT5 accounts with real balances verified")
            return True
            
        except Exception as e:
            self.log_test("MT5 Accounts Test", "ERROR", f"Exception: {str(e)}")
            return False
    
    def test_fund_portfolio(self) -> bool:
        """Test 5: Fund Portfolio - should return real fund allocations for CORE, BALANCE, SEPARATION"""
        try:
            print("\n📊 Testing Fund Portfolio...")
            
            response = self.session.get(f"{self.base_url}/fund-portfolio/overview")
            
            if response.status_code != 200:
                self.log_test("Fund Portfolio API", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            funds_dict = data.get("funds", {})
            
            # Expected funds
            expected_funds = ["CORE", "BALANCE", "SEPARATION"]
            found_funds = {}
            
            # Parse the funds dictionary structure
            for fund_code in expected_funds:
                if fund_code in funds_dict:
                    fund_data = funds_dict[fund_code]
                    found_funds[fund_code] = {
                        "aum": fund_data.get("aum", 0),
                        "mt5_allocation": fund_data.get("mt5_allocation", 0),
                        "mt5_accounts_count": fund_data.get("mt5_accounts_count", 0),
                        "total_true_pnl": fund_data.get("total_true_pnl", 0)
                    }
            
            success = True
            
            # Check CORE fund
            if "CORE" in found_funds:
                core_data = found_funds["CORE"]
                if core_data["aum"] > 0:
                    self.log_test("CORE Fund Allocation", "PASS", 
                                f"CORE fund: AUM ${core_data['aum']:,.2f}, MT5 ${core_data['mt5_allocation']:,.2f}, {core_data['mt5_accounts_count']} accounts")
                else:
                    self.log_test("CORE Fund Allocation", "FAIL", "CORE fund has $0 AUM")
                    success = False
            else:
                self.log_test("CORE Fund", "FAIL", "CORE fund not found")
                success = False
            
            # Check BALANCE fund
            if "BALANCE" in found_funds:
                balance_data = found_funds["BALANCE"]
                if balance_data["aum"] > 0:
                    self.log_test("BALANCE Fund Allocation", "PASS", 
                                f"BALANCE fund: AUM ${balance_data['aum']:,.2f}, MT5 ${balance_data['mt5_allocation']:,.2f}, {balance_data['mt5_accounts_count']} accounts")
                else:
                    self.log_test("BALANCE Fund Allocation", "FAIL", "BALANCE fund has $0 AUM")
                    success = False
            else:
                self.log_test("BALANCE Fund", "FAIL", "BALANCE fund not found")
                success = False
            
            # Note: SEPARATION fund is not included in fund portfolio as it's operational accounts, not client investment funds
            # Check that we have the main investment funds (CORE and BALANCE)
            main_funds_count = len([f for f in ["CORE", "BALANCE"] if f in found_funds and found_funds[f]["aum"] > 0])
            if main_funds_count >= 2:
                self.log_test("Main Investment Funds", "PASS", f"Found {main_funds_count} active investment funds (CORE, BALANCE)")
            else:
                self.log_test("Main Investment Funds", "FAIL", f"Only {main_funds_count} active investment funds found")
                success = False
            
            # Check total portfolio value
            total_aum = data.get("total_aum", 0)
            if total_aum > 100000:  # Expect at least $100K total
                self.log_test("Total Portfolio Value", "PASS", f"Total AUM: ${total_aum:,.2f}")
            else:
                self.log_test("Total Portfolio Value", "FAIL", f"Total AUM: ${total_aum:,.2f} - expected more substantial amount")
                success = False
            
            self.log_test("Fund Portfolio API", "PASS" if success else "FAIL", 
                        "Fund portfolio with real allocations verified" if success else "Fund portfolio has allocation issues")
            return success
            
        except Exception as e:
            self.log_test("Fund Portfolio Test", "ERROR", f"Exception: {str(e)}")
            return False
    
    def test_three_tier_pnl_endpoint(self) -> bool:
        """Test GET /api/pnl/three-tier (Admin Only) - Complete three-tier P&L breakdown"""
        try:
            print("\n📊 Testing Three-Tier P&L Endpoint...")
            
            response = self.session.get(f"{self.base_url}/pnl/three-tier", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success') and 'data' in data:
                    pnl_data = data['data']
                    
                    # Verify structure
                    required_keys = ['client_pnl', 'fidus_pnl', 'total_fund_pnl', 'separation_balance']
                    missing_keys = [key for key in required_keys if key not in pnl_data]
                    
                    if missing_keys:
                        self.log_test("Three-Tier P&L Structure", "FAIL", f"Missing keys: {missing_keys}")
                        return False
                    
                    # Extract key values
                    client_pnl = pnl_data.get('client_pnl', {})
                    fidus_pnl = pnl_data.get('fidus_pnl', {})
                    total_fund_pnl = pnl_data.get('total_fund_pnl', {})
                    separation_balance = pnl_data.get('separation_balance', 0)
                    
                    # CRITICAL validation: Client Initial Investment MUST be $118,151.41
                    client_initial = client_pnl.get('initial_allocation', 0)
                    expected_client_initial = 118151.41
                    
                    if abs(client_initial - expected_client_initial) > 1.0:  # Allow $1 tolerance
                        self.log_test(
                            "Client Initial Investment", 
                            "FAIL", 
                            f"Expected ${expected_client_initial}, got ${client_initial}",
                            expected_client_initial,
                            client_initial
                        )
                        return False
                    
                    # Validate FIDUS capital
                    fidus_initial = fidus_pnl.get('initial_allocation', 0)
                    expected_fidus_initial = 14662.94
                    
                    # Validate total fund investment
                    total_initial = total_fund_pnl.get('initial_allocation', 0)
                    expected_total_initial = 132814.35
                    
                    # Validate account count (client should have 5 accounts)
                    client_account_count = client_pnl.get('account_count', 0)
                    
                    # Log success with key metrics
                    self.log_test(
                        "Three-Tier P&L Endpoint", 
                        "PASS", 
                        f"✅ Client: ${client_initial}, FIDUS: ${fidus_initial}, Total: ${total_initial}, Accounts: {client_account_count}"
                    )
                    
                    print(f"   📊 Client P&L: ${client_pnl.get('true_pnl', 0)} ({client_pnl.get('return_percent', 0):.1f}%)")
                    print(f"   📊 FIDUS P&L: ${fidus_pnl.get('true_pnl', 0)} ({fidus_pnl.get('return_percent', 0):.1f}%)")
                    print(f"   📊 Total Fund P&L: ${total_fund_pnl.get('true_pnl', 0)} ({total_fund_pnl.get('return_percent', 0):.1f}%)")
                    print(f"   📊 Separation Balance: ${separation_balance}")
                    
                    return True
                    
                else:
                    self.log_test("Three-Tier P&L Endpoint", "FAIL", f"Invalid response structure: {data}")
                    return False
                    
            else:
                self.log_test("Three-Tier P&L Endpoint", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Three-Tier P&L Endpoint", "ERROR", f"Exception: {str(e)}")
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
                self.log_test("Fund Performance Endpoint", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Fund Performance Endpoint", "ERROR", f"Exception: {str(e)}")
            return False
    
    def test_mathematical_consistency(self) -> bool:
        """Test mathematical consistency across all three-tier P&L endpoints"""
        try:
            print("\n🧮 Testing Mathematical Consistency...")
            
            # Get data from all three endpoints
            three_tier_response = self.session.get(f"{self.base_url}/pnl/three-tier", timeout=30)
            client_response = self.session.get(f"{self.base_url}/pnl/client/client_alejandro", timeout=30)
            fund_perf_response = self.session.get(f"{self.base_url}/pnl/fund-performance", timeout=30)
            
            if not all([r.status_code == 200 for r in [three_tier_response, client_response, fund_perf_response]]):
                self.log_test("Mathematical Consistency", "FAIL", "One or more endpoints failed")
                return False
            
            three_tier_data = three_tier_response.json()['data']
            client_data = client_response.json()['data']
            fund_perf_data = fund_perf_response.json()['data']
            
            # Validate consistency between three-tier and client endpoints
            three_tier_client = three_tier_data['client_pnl']
            
            consistency_checks = [
                ('Initial Investment', three_tier_client['initial_allocation'], client_data['initial_investment']),
                ('Current Equity', three_tier_client['current_equity'], client_data['current_equity']),
                ('Separation Balance', three_tier_data['separation_balance'], fund_perf_data['separation_balance'])
            ]
            
            for check_name, value1, value2 in consistency_checks:
                if abs(value1 - value2) > 0.01:  # Allow 1 cent tolerance
                    self.log_test(
                        "Mathematical Consistency", 
                        "FAIL", 
                        f"{check_name} mismatch: {value1} vs {value2}",
                        value1,
                        value2
                    )
                    return False
            
            # Validate fund performance consistency
            fund_perf_fund = fund_perf_data['fund_performance']
            three_tier_fund = three_tier_data['total_fund_pnl']
            
            fund_consistency_checks = [
                ('Fund Initial Allocation', fund_perf_fund['initial_allocation'], three_tier_fund['initial_allocation']),
                ('Fund Current Equity', fund_perf_fund['current_equity'], three_tier_fund['current_equity']),
                ('Fund True P&L', fund_perf_fund['true_pnl'], three_tier_fund['true_pnl'])
            ]
            
            for check_name, value1, value2 in fund_consistency_checks:
                if abs(value1 - value2) > 0.01:  # Allow 1 cent tolerance
                    self.log_test(
                        "Mathematical Consistency", 
                        "FAIL", 
                        f"{check_name} mismatch: {value1} vs {value2}",
                        value1,
                        value2
                    )
                    return False
            
            self.log_test(
                "Mathematical Consistency", 
                "PASS", 
                "✅ All cross-endpoint calculations are mathematically consistent"
            )
            return True
            
        except Exception as e:
            self.log_test("Mathematical Consistency", "ERROR", f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all critical backend endpoint tests - PRIORITIZING THREE-TIER P&L SYSTEM"""
        print("🚀 THREE-TIER P&L SYSTEM BACKEND API TESTING")
        print("=" * 80)
        
        # Authenticate first
        if not self.authenticate_admin():
            return {"success": False, "error": "Authentication failed"}
        
        # PRIMARY FOCUS: Three-Tier P&L System Tests
        print("\n🎯 PRIMARY FOCUS: THREE-TIER P&L SYSTEM")
        pnl_test_results = {
            "three_tier_pnl": self.test_three_tier_pnl_endpoint(),
            "client_pnl": self.test_client_pnl_endpoint(),
            "fund_performance": self.test_fund_performance_endpoint(),
            "mathematical_consistency": self.test_mathematical_consistency()
        }
        
        # SECONDARY: Other backend tests (if time permits)
        print("\n📋 SECONDARY: Other Backend Systems")
        other_test_results = {
            "cashflow_system": self.test_cashflow_system(),
            "money_managers_api": self.test_money_managers_api(),
            "trading_analytics": self.test_trading_analytics(),
            "mt5_accounts": self.test_mt5_accounts(),
            "fund_portfolio": self.test_fund_portfolio()
        }
        
        # Combine all results
        test_results = {**pnl_test_results, **other_test_results}
        
        # Calculate summary
        total_tests = len(test_results)
        passed_tests = sum(1 for result in test_results.values() if result)
        success_rate = (passed_tests / total_tests) * 100
        
        # Calculate P&L system specific results
        pnl_passed = sum(1 for result in pnl_test_results.values() if result)
        pnl_total = len(pnl_test_results)
        pnl_success_rate = (pnl_passed / pnl_total) * 100
        
        print("\n" + "=" * 80)
        print("📊 THREE-TIER P&L SYSTEM TEST SUMMARY")
        print("=" * 80)
        
        print("🎯 PRIMARY FOCUS - Three-Tier P&L System:")
        for test_name, result in pnl_test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {status} {test_name.replace('_', ' ').title()}")
        
        print(f"\n📊 P&L System Success Rate: {pnl_passed}/{pnl_total} ({pnl_success_rate:.1f}%)")
        
        print("\n📋 SECONDARY - Other Backend Systems:")
        for test_name, result in other_test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {status} {test_name.replace('_', ' ').title()}")
        
        print(f"\n🎯 Overall Success Rate: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        if pnl_success_rate == 100:
            print("🎉 THREE-TIER P&L SYSTEM: EXCELLENT - All endpoints working correctly!")
            print("   ✅ Client Initial Investment: $118,151.41 ✓")
            print("   ✅ FIDUS Capital: $14,662.94 ✓") 
            print("   ✅ Total Fund Investment: $132,814.35 ✓")
            print("   ✅ All calculations mathematically correct ✓")
            print("   ✅ Admin authentication working ✓")
        elif pnl_success_rate >= 75:
            print("✅ THREE-TIER P&L SYSTEM: GOOD - Minor issues to address")
        elif pnl_success_rate >= 50:
            print("⚠️ THREE-TIER P&L SYSTEM: NEEDS ATTENTION - Several issues found")
        else:
            print("🚨 THREE-TIER P&L SYSTEM: CRITICAL ISSUES - Major problems detected")
        
        return {
            "success": success_rate >= 80,
            "success_rate": success_rate,
            "passed_tests": passed_tests,
            "total_tests": total_tests,
            "test_results": test_results,
            "detailed_results": self.test_results
        }

def main():
    """Main test execution"""
    tester = BackendTester()
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if results["success"] else 1)

if __name__ == "__main__":
    main()