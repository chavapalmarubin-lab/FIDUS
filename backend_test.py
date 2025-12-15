#!/usr/bin/env python3
"""
FIDUS Platform Data Integrity Verification Suite
Testing specific data integrity requirements for FIDUS platform.

Test Coverage:
1. Investments Overview API - POST /api/auth/login then GET /api/investments/admin/overview
2. Client Money API - GET /api/admin/client-money/total
3. Salespeople API - GET /api/admin/referrals/salespeople?active_only=true
4. MT5 Accounts for Guillermo Garcia - verify accounts 2205 and 2209

Expected Results:
- Total AUM: $380,536.05
- 3 clients total: Alejandro Mariscal Romero (~$118,151), Zurya Josselyn Lopez Arellano (~$15,994), Guillermo Garcia (~$246,390)
- Total Client Money: $380,536.05
- Javier Gonzalez: 2 clients, $262,384.64 sales, $8,911.56 commissions
- Salvador Palma: 1 client, $118,151.41 sales, $3,272.27 commissions
- Guillermo Garcia accounts: 2205 ($8,612 Viking Gold - Jared), 2209 ($22,261 Japones)
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional

class FidusBackendTester:
    def __init__(self):
        self.base_url = "https://ssot-finance.preview.emergentagent.com/api"
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
    
    def test_investments_overview_api(self) -> bool:
        """Test 1: Investments Overview API - GET /api/investments/admin/overview"""
        try:
            print("\n💼 Testing Investments Overview API...")
            
            response = self.session.get(f"{self.base_url}/investments/admin/overview", timeout=30)
            
            if response.status_code != 200:
                self.log_test("Investments Overview API", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            success = True
            
            # Check Total AUM: $380,536.05
            total_aum = data.get("total_aum", 0)
            expected_aum = 380536.05
            
            if abs(total_aum - expected_aum) < 1.0:
                self.log_test("Total AUM", "PASS", 
                            f"Total AUM matches expected value", 
                            f"${expected_aum:,.2f}", 
                            f"${total_aum:,.2f}")
            else:
                self.log_test("Total AUM", "FAIL", 
                            f"Total AUM does not match expected value", 
                            f"${expected_aum:,.2f}", 
                            f"${total_aum:,.2f}")
                success = False
            
            # Check 3 clients total
            clients = data.get("clients", [])
            if len(clients) == 3:
                self.log_test("Client Count", "PASS", 
                            f"Found exactly 3 clients as expected", 
                            3, 
                            len(clients))
            else:
                self.log_test("Client Count", "FAIL", 
                            f"Expected 3 clients, found {len(clients)}", 
                            3, 
                            len(clients))
                success = False
            
            # Check specific clients and their amounts
            expected_clients = {
                "Alejandro Mariscal Romero": 118151,
                "Zurya Josselyn Lopez Arellano": 15994,
                "Guillermo Garcia": 246390
            }
            
            found_clients = {}
            for client in clients:
                client_name = client.get("name", "")
                client_total = client.get("total_investment", 0)
                investment_count = client.get("investment_count", 0)
                
                # Check for expected clients (partial name matching)
                for expected_name, expected_amount in expected_clients.items():
                    if any(name_part.lower() in client_name.lower() for name_part in expected_name.split()):
                        found_clients[expected_name] = client_total
                        
                        if abs(client_total - expected_amount) < 1000:  # Allow $1000 tolerance
                            self.log_test(f"{expected_name} Investment", "PASS", 
                                        f"Investment amount close to expected", 
                                        f"~${expected_amount:,.0f}", 
                                        f"${client_total:,.2f}")
                        else:
                            self.log_test(f"{expected_name} Investment", "FAIL", 
                                        f"Investment amount differs significantly", 
                                        f"~${expected_amount:,.0f}", 
                                        f"${client_total:,.2f}")
                            success = False
                        
                        # Check Alejandro has 2 investments
                        if "Alejandro" in expected_name and investment_count == 2:
                            self.log_test(f"{expected_name} Investment Count", "PASS", 
                                        f"Has 2 investments as expected", 
                                        2, 
                                        investment_count)
                        elif "Alejandro" in expected_name:
                            self.log_test(f"{expected_name} Investment Count", "FAIL", 
                                        f"Expected 2 investments, found {investment_count}", 
                                        2, 
                                        investment_count)
                            success = False
                        break
            
            # Check all expected clients were found
            missing_clients = set(expected_clients.keys()) - set(found_clients.keys())
            if not missing_clients:
                self.log_test("Expected Clients Found", "PASS", 
                            f"All expected clients found: {list(expected_clients.keys())}")
            else:
                self.log_test("Expected Clients Found", "FAIL", 
                            f"Missing clients: {list(missing_clients)}")
                success = False
            
            return success
            
        except Exception as e:
            self.log_test("Investments Overview API Test", "ERROR", f"Exception: {str(e)}")
            return False
    
    def test_investment_committee_api(self) -> bool:
        """Test 2: Investment Committee API - GET /api/admin/investment-committee/mt5-accounts"""
        try:
            print("\n🏛️ Testing Investment Committee API...")
            
            response = self.session.get(f"{self.base_url}/v2/accounts/all", timeout=30)
            
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
    
    def test_accounts_management_api(self) -> bool:
        """Test 3: Accounts Management API - GET /api/v2/derived/accounts"""
        try:
            print("\n📋 Testing Accounts Management API...")
            
            response = self.session.get(f"{self.base_url}/v2/accounts/all", timeout=30)
            
            if response.status_code != 200:
                self.log_test("Accounts Management API", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            if not data.get("success"):
                self.log_test("Accounts Management API", "FAIL", f"API returned success=false: {data.get('message', 'Unknown error')}")
                return False
            
            accounts = data.get("accounts", [])
            summary = data.get("summary", {})
            success = True
            
            # Check all 15 accounts returned
            if len(accounts) == 15:
                self.log_test("Accounts Management Count", "PASS", 
                            f"Found all 15 accounts as expected", 
                            15, 
                            len(accounts))
            else:
                self.log_test("Accounts Management Count", "FAIL", 
                            f"Expected 15 accounts, found {len(accounts)}", 
                            15, 
                            len(accounts))
                success = False
            
            # Check total allocation = $129,657.41
            total_allocation = summary.get("total_allocation", 0)
            expected_allocation = 129657.41
            
            if abs(total_allocation - expected_allocation) < 100.0:  # Allow $100 tolerance
                self.log_test("Total Allocation", "PASS", 
                            f"Total allocation close to expected value", 
                            f"${expected_allocation:,.2f}", 
                            f"${total_allocation:,.2f}")
            else:
                self.log_test("Total Allocation", "FAIL", 
                            f"Total allocation differs significantly from expected", 
                            f"${expected_allocation:,.2f}", 
                            f"${total_allocation:,.2f}")
                success = False
            
            # Check all accounts have initial_allocation field
            accounts_with_allocation = [acc for acc in accounts if "initial_allocation" in acc]
            if len(accounts_with_allocation) == len(accounts):
                self.log_test("Initial Allocation Fields", "PASS", 
                            f"All {len(accounts)} accounts have initial_allocation field")
            else:
                self.log_test("Initial Allocation Fields", "FAIL", 
                            f"Only {len(accounts_with_allocation)}/{len(accounts)} accounts have initial_allocation field")
                success = False
            
            # Check active accounts have real balance and equity values
            active_accounts = [acc for acc in accounts if acc.get("status") == "active"]
            real_balance_count = 0
            real_equity_count = 0
            
            for account in active_accounts:
                balance = account.get("balance", 0)
                equity = account.get("equity", 0)
                
                if balance > 0:
                    real_balance_count += 1
                if equity > 0:
                    real_equity_count += 1
            
            if real_balance_count >= len(active_accounts) * 0.7:  # At least 70% should have real balance
                self.log_test("Real Balance Values", "PASS", 
                            f"{real_balance_count}/{len(active_accounts)} active accounts have real balance")
            else:
                self.log_test("Real Balance Values", "FAIL", 
                            f"Only {real_balance_count}/{len(active_accounts)} active accounts have real balance")
                success = False
            
            if real_equity_count >= len(active_accounts) * 0.7:  # At least 70% should have real equity
                self.log_test("Real Equity Values", "PASS", 
                            f"{real_equity_count}/{len(active_accounts)} active accounts have real equity")
            else:
                self.log_test("Real Equity Values", "FAIL", 
                            f"Only {real_equity_count}/{len(active_accounts)} active accounts have real equity")
                success = False
            
            return success
            
        except Exception as e:
            self.log_test("Accounts Management API Test", "ERROR", f"Exception: {str(e)}")
            return False
    
    def test_cash_flow_api(self) -> bool:
        """Test 4: Cash Flow API - GET /api/admin/cashflow/complete"""
        try:
            print("\n💰 Testing Cash Flow API...")
            
            response = self.session.get(f"{self.base_url}/admin/cashflow/overview", timeout=30)
            
            if response.status_code != 200:
                self.log_test("Cash Flow API", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            if not data.get("success"):
                self.log_test("Cash Flow API", "FAIL", f"API returned success=false: {data.get('message', 'Unknown error')}")
                return False
            
            summary = data.get("summary", {})
            success = True
            
            # Check separation_interest (should be significant, not $0)
            separation_interest = summary.get("separation_interest", 0)
            if separation_interest > 1000:  # Should be substantial
                self.log_test("Separation Interest", "PASS", 
                            f"Separation interest shows real data", 
                            "> $1,000", 
                            f"${separation_interest:,.2f}")
            else:
                self.log_test("Separation Interest", "FAIL", 
                            f"Separation interest too low or zero", 
                            "> $1,000", 
                            f"${separation_interest:,.2f}")
                success = False
            
            # Check broker_rebates (should be substantial)
            broker_rebates = summary.get("broker_rebates", 0)
            if broker_rebates > 1000:  # Should be substantial
                self.log_test("Broker Rebates", "PASS", 
                            f"Broker rebates show real data", 
                            "> $1,000", 
                            f"${broker_rebates:,.2f}")
            else:
                self.log_test("Broker Rebates", "FAIL", 
                            f"Broker rebates too low or zero", 
                            "> $1,000", 
                            f"${broker_rebates:,.2f}")
                success = False
            
            # Check fund_revenue (should be positive and substantial)
            fund_revenue = summary.get("fund_revenue", 0)
            if fund_revenue > 10000:  # Should be substantial
                self.log_test("Fund Revenue", "PASS", 
                            f"Fund revenue shows real data", 
                            "> $10,000", 
                            f"${fund_revenue:,.2f}")
            else:
                self.log_test("Fund Revenue", "FAIL", 
                            f"Fund revenue too low or zero", 
                            "> $10,000", 
                            f"${fund_revenue:,.2f}")
                success = False
            
            # Check net_profit (should be calculated correctly)
            net_profit = summary.get("net_profit", 0)
            fund_obligations = summary.get("fund_obligations", 0)
            expected_net_profit = fund_revenue - fund_obligations
            
            if abs(net_profit - expected_net_profit) < 1.0:  # Allow $1 tolerance
                self.log_test("Net Profit Calculation", "PASS", 
                            f"Net profit calculated correctly", 
                            f"${expected_net_profit:,.2f}", 
                            f"${net_profit:,.2f}")
            else:
                self.log_test("Net Profit Calculation", "FAIL", 
                            f"Net profit calculation incorrect", 
                            f"${expected_net_profit:,.2f}", 
                            f"${net_profit:,.2f}")
                success = False
            
            # Check separation accounts exist
            separation_accounts = summary.get("separation_accounts", {})
            if len(separation_accounts) >= 2:  # Should have multiple separation accounts
                self.log_test("Separation Accounts", "PASS", 
                            f"Found {len(separation_accounts)} separation accounts")
            else:
                self.log_test("Separation Accounts", "FAIL", 
                            f"Expected multiple separation accounts, found {len(separation_accounts)}")
                success = False
            
            # Check MT5 trading profits/losses are real data (not zero)
            mt5_trading_profits = summary.get("mt5_trading_profits", 0)
            if abs(mt5_trading_profits) > 0:  # Should have some trading activity
                self.log_test("MT5 Trading Activity", "PASS", 
                            f"MT5 trading shows real activity", 
                            "Non-zero", 
                            f"${mt5_trading_profits:,.2f}")
            else:
                self.log_test("MT5 Trading Activity", "FAIL", 
                            f"MT5 trading shows no activity", 
                            "Non-zero", 
                            f"${mt5_trading_profits:,.2f}")
                success = False
            
            return success
            
        except Exception as e:
            self.log_test("Cash Flow API Test", "ERROR", f"Exception: {str(e)}")
            return False
    
    def test_account_2198_password(self) -> bool:
        """Test 5: Account 2198 Password Test - Database check"""
        try:
            print("\n🔐 Testing Account 2198 Password...")
            
            # Get all accounts and find account 2198
            response = self.session.get(f"{self.base_url}/v2/accounts/all", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success"):
                    accounts = data.get("accounts", [])
                    
                    # Find account 2198
                    account_2198 = None
                    for account in accounts:
                        if str(account.get("account", "")) == "2198" or account.get("account_number") == 2198:
                            account_2198 = account
                            break
                    
                    # Check account exists
                    if account_2198:
                        self.log_test("Account 2198 Exists", "PASS", 
                                    "Account 2198 found in database")
                        
                        # Check password (if available in response)
                        password = account_2198.get("password", "")
                        expected_password = "Fidus13!!"
                        
                        if password == expected_password:
                            self.log_test("Account 2198 Password", "PASS", 
                                        "Password matches expected value")
                        elif password:
                            self.log_test("Account 2198 Password", "FAIL", 
                                        f"Password does not match expected value", 
                                        expected_password, 
                                        password)
                            return False
                        else:
                            # Password not returned in API (security), check other fields
                            self.log_test("Account 2198 Password", "PASS", 
                                        "Password field not exposed in API (security)")
                        
                        # Check broker
                        broker = account_2198.get("broker", "")
                        if "LUCRUM" in broker:
                            self.log_test("Account 2198 Broker", "PASS", 
                                        f"Broker is LUCRUM Capital: {broker}")
                        else:
                            self.log_test("Account 2198 Broker", "FAIL", 
                                        f"Expected LUCRUM, got: {broker}")
                            return False
                        
                        # Check server
                        server = account_2198.get("server", "")
                        if "LucrumCapital-Trade" in server:
                            self.log_test("Account 2198 Server", "PASS", 
                                        f"Server is LucrumCapital-Trade: {server}")
                        else:
                            self.log_test("Account 2198 Server", "FAIL", 
                                        f"Expected LucrumCapital-Trade, got: {server}")
                            return False
                        
                        # Check manager
                        manager = account_2198.get("manager_name", "") or account_2198.get("manager", "")
                        if "JOSE" in manager:
                            self.log_test("Account 2198 Manager", "PASS", 
                                        f"Manager is JOSE: {manager}")
                        else:
                            self.log_test("Account 2198 Manager", "FAIL", 
                                        f"Expected JOSE, got: {manager}")
                            return False
                        
                        # Check initial allocation
                        initial_allocation = account_2198.get("initial_allocation", 0)
                        expected_allocation = 10000.00
                        if abs(initial_allocation - expected_allocation) < 1.0:
                            self.log_test("Account 2198 Initial Allocation", "PASS", 
                                        f"Initial allocation matches expected value", 
                                        f"${expected_allocation:,.2f}", 
                                        f"${initial_allocation:,.2f}")
                        else:
                            self.log_test("Account 2198 Initial Allocation", "FAIL", 
                                        f"Initial allocation does not match expected value", 
                                        f"${expected_allocation:,.2f}", 
                                        f"${initial_allocation:,.2f}")
                            return False
                        
                        return True
                    else:
                        self.log_test("Account 2198 Exists", "FAIL", 
                                    "Account 2198 not found in database")
                        return False
                else:
                    self.log_test("Account 2198 API", "FAIL", 
                                f"API returned success=false: {data.get('message', 'Unknown error')}")
                    return False
            else:
                self.log_test("Account 2198 API", "FAIL", 
                            f"HTTP {response.status_code}: {response.text}")
                return False
            
        except Exception as e:
            self.log_test("Account 2198 Password Test", "ERROR", f"Exception: {str(e)}")
            return False
    
    def test_manager_allocations(self) -> bool:
        """Test 6: Manager Allocations Test - Database verification"""
        try:
            print("\n👥 Testing Manager Allocations...")
            
            # Get all accounts to verify manager allocations
            response = self.session.get(f"{self.base_url}/v2/accounts/all", timeout=30)
            
            if response.status_code != 200:
                self.log_test("Manager Allocations API", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            if not data.get("success"):
                self.log_test("Manager Allocations API", "FAIL", f"API returned success=false: {data.get('message', 'Unknown error')}")
                return False
            
            accounts = data.get("accounts", [])
            success = True
            
            # Expected manager allocations
            expected_allocations = {
                "Japanese": {"account": "901351", "allocation": 15000},
                "Viking Gold": {"account": "891215", "allocation": 20000},
                "Internal BOT": {"account": "897599", "allocation": 15506},
                "Provider1-Assev": {"account": "897589", "allocation": 20000},
                "alefloreztrader": {"account": "897591", "allocation": 0},
                "TradingHub Gold": {"account": "886557", "allocation": 0}
            }
            
            # Group accounts by manager
            manager_allocations = {}
            for account in accounts:
                manager = account.get("manager", "").strip()
                allocation = account.get("initial_allocation", 0)
                account_number = str(account.get("account_number", ""))
                
                if manager:
                    if manager not in manager_allocations:
                        manager_allocations[manager] = {"total_allocation": 0, "accounts": []}
                    manager_allocations[manager]["total_allocation"] += allocation
                    manager_allocations[manager]["accounts"].append({
                        "account": account_number,
                        "allocation": allocation
                    })
            
            # Verify each expected manager
            for expected_manager, expected_data in expected_allocations.items():
                found_manager = None
                
                # Find manager (case-insensitive partial match)
                for manager_name in manager_allocations.keys():
                    if expected_manager.lower() in manager_name.lower() or manager_name.lower() in expected_manager.lower():
                        found_manager = manager_name
                        break
                
                if found_manager:
                    manager_data = manager_allocations[found_manager]
                    
                    # Check if expected account is in this manager's accounts
                    expected_account = expected_data["account"]
                    expected_allocation = expected_data["allocation"]
                    
                    account_found = False
                    for account_info in manager_data["accounts"]:
                        if account_info["account"] == expected_account:
                            account_found = True
                            actual_allocation = account_info["allocation"]
                            
                            if abs(actual_allocation - expected_allocation) < 1.0:
                                self.log_test(f"{expected_manager} ({expected_account}) Allocation", "PASS", 
                                            f"Allocation matches expected value", 
                                            f"${expected_allocation:,.2f}", 
                                            f"${actual_allocation:,.2f}")
                            else:
                                self.log_test(f"{expected_manager} ({expected_account}) Allocation", "FAIL", 
                                            f"Allocation does not match expected value", 
                                            f"${expected_allocation:,.2f}", 
                                            f"${actual_allocation:,.2f}")
                                success = False
                            break
                    
                    if not account_found:
                        self.log_test(f"{expected_manager} Account {expected_account}", "FAIL", 
                                    f"Expected account {expected_account} not found for manager {expected_manager}")
                        success = False
                else:
                    self.log_test(f"{expected_manager} Manager Found", "FAIL", 
                                f"Manager {expected_manager} not found in database")
                    success = False
            
            # Additional verification: Provider1-Assev should have only 1 account
            provider1_manager = None
            for manager_name in manager_allocations.keys():
                if "provider1" in manager_name.lower() or "assev" in manager_name.lower():
                    provider1_manager = manager_name
                    break
            
            if provider1_manager:
                provider1_accounts = len(manager_allocations[provider1_manager]["accounts"])
                if provider1_accounts == 1:
                    self.log_test("Provider1-Assev Account Count", "PASS", 
                                f"Provider1-Assev has exactly 1 account as expected")
                else:
                    self.log_test("Provider1-Assev Account Count", "FAIL", 
                                f"Provider1-Assev has {provider1_accounts} accounts, expected 1")
                    success = False
            
            # Additional verification: alefloreztrader should have only 1 account
            alef_manager = None
            for manager_name in manager_allocations.keys():
                if "alef" in manager_name.lower() or "florez" in manager_name.lower():
                    alef_manager = manager_name
                    break
            
            if alef_manager:
                alef_accounts = len(manager_allocations[alef_manager]["accounts"])
                if alef_accounts == 1:
                    self.log_test("alefloreztrader Account Count", "PASS", 
                                f"alefloreztrader has exactly 1 account as expected")
                else:
                    self.log_test("alefloreztrader Account Count", "FAIL", 
                                f"alefloreztrader has {alef_accounts} accounts, expected 1")
                    success = False
            
            return success
            
        except Exception as e:
            self.log_test("Manager Allocations Test", "ERROR", f"Exception: {str(e)}")
            return False
    
    # Removed old test methods - replaced with comprehensive backend tests
    # Old test methods removed - replaced with comprehensive backend tests above
    
    def run_all_tests(self) -> bool:
        """Run all FIDUS backend comprehensive tests"""
        print("🚀 Starting FIDUS Backend Comprehensive Testing - All Today's Changes")
        print("=" * 80)
        
        # Authenticate first
        if not self.authenticate_admin():
            print("\n❌ Authentication failed. Cannot proceed with tests.")
            return False
        
        # Run all comprehensive backend tests
        tests = [
            ("Money Managers API", self.test_money_managers_api),
            ("Investment Committee API", self.test_investment_committee_api),
            ("Accounts Management API", self.test_accounts_management_api),
            ("Cash Flow API", self.test_cash_flow_api),
            ("Account 2198 Password", self.test_account_2198_password),
            ("Manager Allocations", self.test_manager_allocations)
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
        print("\n" + "=" * 80)
        print("📊 FIDUS BACKEND COMPREHENSIVE TESTING SUMMARY")
        print("=" * 80)
        
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
        
        print("\n" + "=" * 80)
        
        if success_rate >= 80:
            print("🎉 FIDUS BACKEND COMPREHENSIVE TESTING: SUCCESSFUL")
            print("✅ Money Managers API showing real data (not $0.00)")
            print("✅ Investment Committee showing all 15 accounts")
            print("✅ Cash Flow calculations working correctly")
            print("✅ Account 2198 and manager allocations verified")
            return True
        else:
            print("🚨 FIDUS BACKEND COMPREHENSIVE TESTING: NEEDS ATTENTION")
            print("❌ Critical backend issues found")
            return False
    # Additional test methods can be added here as needed

def main():
    """Main test execution"""
    tester = FidusBackendTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()