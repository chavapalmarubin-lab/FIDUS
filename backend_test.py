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
        self.base_url = "https://viking-trade-dash.preview.emergentagent.com/api"
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
                client_name = client.get("client_name", "")
                client_total = client.get("total_invested", 0)
                investment_count = client.get("investment_count", 0)
                
                # Check for expected clients (exact name matching from API response)
                found_clients[client_name] = client_total
                
                # Map to expected names for validation
                for expected_name, expected_amount in expected_clients.items():
                    if client_name == expected_name:
                        
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
    
    def test_client_money_api(self) -> bool:
        """Test 2: Client Money API - GET /api/admin/client-money/total"""
        try:
            print("\n💰 Testing Client Money API...")
            
            response = self.session.get(f"{self.base_url}/admin/client-money/total", timeout=30)
            
            if response.status_code != 200:
                self.log_test("Client Money API", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            success = True
            
            # Check Total Client Money: $380,536.05
            total_client_money = data.get("total_client_money", 0)
            expected_total = 380536.05
            
            if abs(total_client_money - expected_total) < 1.0:
                self.log_test("Total Client Money", "PASS", 
                            f"Total Client Money matches expected value", 
                            f"${expected_total:,.2f}", 
                            f"${total_client_money:,.2f}")
            else:
                self.log_test("Total Client Money", "FAIL", 
                            f"Total Client Money does not match expected value", 
                            f"${expected_total:,.2f}", 
                            f"${total_client_money:,.2f}")
                success = False
            
            # Check response structure
            if "total_client_money" in data:
                self.log_test("Client Money Response Structure", "PASS", 
                            "Response contains total_client_money field")
            else:
                self.log_test("Client Money Response Structure", "FAIL", 
                            "Response missing total_client_money field")
                success = False
            
            return success
            
        except Exception as e:
            self.log_test("Client Money API Test", "ERROR", f"Exception: {str(e)}")
            return False
    
    def test_salespeople_api(self) -> bool:
        """Test 3: Salespeople API - GET /api/admin/referrals/salespeople?active_only=true"""
        try:
            print("\n👥 Testing Salespeople API...")
            
            response = self.session.get(f"{self.base_url}/admin/referrals/salespeople?active_only=true", timeout=30)
            
            if response.status_code != 200:
                self.log_test("Salespeople API", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            success = True
            
            # Get salespeople list
            salespeople = data.get("salespeople", [])
            
            # Expected salespeople data
            expected_salespeople = {
                "Javier Gonzalez": {
                    "clients": 2,
                    "sales": 262384.64,
                    "commissions": 8911.56
                },
                "Salvador Palma": {
                    "clients": 1,
                    "sales": 118151.41,
                    "commissions": 3272.27
                }
            }
            
            found_salespeople = {}
            
            for salesperson in salespeople:
                name = salesperson.get("name", "")
                clients = salesperson.get("totalClientsReferred", 0)
                sales = salesperson.get("totalSalesVolume", 0)
                commissions = salesperson.get("totalCommissionsEarned", 0)
                
                # Check for expected salespeople (exact name matching)
                for expected_name, expected_data in expected_salespeople.items():
                    if name == expected_name:
                        found_salespeople[expected_name] = {
                            "clients": clients,
                            "sales": sales,
                            "commissions": commissions
                        }
                        
                        # Check clients count
                        if clients == expected_data["clients"]:
                            self.log_test(f"{expected_name} Clients", "PASS", 
                                        f"Client count matches expected", 
                                        expected_data["clients"], 
                                        clients)
                        else:
                            self.log_test(f"{expected_name} Clients", "FAIL", 
                                        f"Client count does not match expected", 
                                        expected_data["clients"], 
                                        clients)
                            success = False
                        
                        # Check sales amount (allow small tolerance)
                        if abs(sales - expected_data["sales"]) < 1.0:
                            self.log_test(f"{expected_name} Sales", "PASS", 
                                        f"Sales amount matches expected", 
                                        f"${expected_data['sales']:,.2f}", 
                                        f"${sales:,.2f}")
                        else:
                            self.log_test(f"{expected_name} Sales", "FAIL", 
                                        f"Sales amount does not match expected", 
                                        f"${expected_data['sales']:,.2f}", 
                                        f"${sales:,.2f}")
                            success = False
                        
                        # Check commissions amount (allow small tolerance)
                        if abs(commissions - expected_data["commissions"]) < 1.0:
                            self.log_test(f"{expected_name} Commissions", "PASS", 
                                        f"Commissions amount matches expected", 
                                        f"${expected_data['commissions']:,.2f}", 
                                        f"${commissions:,.2f}")
                        else:
                            self.log_test(f"{expected_name} Commissions", "FAIL", 
                                        f"Commissions amount does not match expected", 
                                        f"${expected_data['commissions']:,.2f}", 
                                        f"${commissions:,.2f}")
                            success = False
                        break
            
            # Check all expected salespeople were found
            missing_salespeople = set(expected_salespeople.keys()) - set(found_salespeople.keys())
            if not missing_salespeople:
                self.log_test("Expected Salespeople Found", "PASS", 
                            f"All expected salespeople found: {list(expected_salespeople.keys())}")
            else:
                self.log_test("Expected Salespeople Found", "FAIL", 
                            f"Missing salespeople: {list(missing_salespeople)}")
                success = False
            
            return success
            
        except Exception as e:
            self.log_test("Salespeople API Test", "ERROR", f"Exception: {str(e)}")
            return False
    
    def test_mt5_accounts_guillermo_garcia(self) -> bool:
        """Test 4: MT5 Accounts for Guillermo Garcia - verify accounts 2205 and 2209"""
        try:
            print("\n🏦 Testing MT5 Accounts for Guillermo Garcia...")
            
            # First, try to get all accounts to find Guillermo Garcia's accounts
            response = self.session.get(f"{self.base_url}/v2/accounts/all", timeout=30)
            
            if response.status_code != 200:
                self.log_test("MT5 Accounts API", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            if not data.get("success"):
                self.log_test("MT5 Accounts API", "FAIL", f"API returned success=false: {data.get('message', 'Unknown error')}")
                return False
            
            accounts = data.get("accounts", [])
            success = True
            
            # Expected accounts for Guillermo Garcia
            expected_accounts = {
                "2205": {
                    "balance": 8612,
                    "manager": "Viking Gold - Jared"
                },
                "2209": {
                    "balance": 22261,
                    "manager": "Japones"
                }
            }
            
            found_accounts = {}
            
            for account in accounts:
                account_number = str(account.get("account", "") or account.get("account_number", ""))
                
                if account_number in expected_accounts:
                    balance = account.get("balance", 0)
                    equity = account.get("equity", 0)
                    manager = account.get("manager_name", "") or account.get("manager", "")
                    
                    found_accounts[account_number] = {
                        "balance": balance,
                        "equity": equity,
                        "manager": manager
                    }
                    
                    expected_data = expected_accounts[account_number]
                    
                    # Check balance (allow some tolerance)
                    if abs(balance - expected_data["balance"]) < 200:  # Allow $200 tolerance
                        self.log_test(f"Account {account_number} Balance", "PASS", 
                                    f"Balance close to expected value", 
                                    f"${expected_data['balance']:,.0f}", 
                                    f"${balance:,.2f}")
                    else:
                        self.log_test(f"Account {account_number} Balance", "FAIL", 
                                    f"Balance differs significantly from expected", 
                                    f"${expected_data['balance']:,.0f}", 
                                    f"${balance:,.2f}")
                        success = False
                    
                    # Check manager (partial matching)
                    expected_manager = expected_data["manager"]
                    if any(part.lower() in manager.lower() for part in expected_manager.split()):
                        self.log_test(f"Account {account_number} Manager", "PASS", 
                                    f"Manager matches expected", 
                                    expected_manager, 
                                    manager)
                    else:
                        self.log_test(f"Account {account_number} Manager", "FAIL", 
                                    f"Manager does not match expected", 
                                    expected_manager, 
                                    manager)
                        success = False
            
            # Check both accounts were found
            missing_accounts = set(expected_accounts.keys()) - set(found_accounts.keys())
            if not missing_accounts:
                self.log_test("Guillermo Garcia Accounts Found", "PASS", 
                            f"Both accounts 2205 and 2209 found")
            else:
                self.log_test("Guillermo Garcia Accounts Found", "FAIL", 
                            f"Missing accounts: {list(missing_accounts)}")
                success = False
            
            # Verify total for Guillermo Garcia accounts
            if len(found_accounts) == 2:
                total_balance = sum(acc["balance"] for acc in found_accounts.values())
                expected_total = 8612 + 22261  # $30,873
                
                if abs(total_balance - expected_total) < 200:  # Allow $200 tolerance
                    self.log_test("Guillermo Garcia Total Balance", "PASS", 
                                f"Total balance close to expected", 
                                f"${expected_total:,.0f}", 
                                f"${total_balance:,.2f}")
                else:
                    self.log_test("Guillermo Garcia Total Balance", "FAIL", 
                                f"Total balance differs from expected", 
                                f"${expected_total:,.0f}", 
                                f"${total_balance:,.2f}")
                    success = False
            
            return success
            
        except Exception as e:
            self.log_test("MT5 Accounts Guillermo Garcia Test", "ERROR", f"Exception: {str(e)}")
            return False
    
    # Additional test methods can be added here as needed
    
    def run_all_tests(self) -> bool:
        """Run all FIDUS platform data integrity tests"""
        print("🚀 Starting FIDUS Platform Data Integrity Verification")
        print("=" * 80)
        
        # Authenticate first
        if not self.authenticate_admin():
            print("\n❌ Authentication failed. Cannot proceed with tests.")
            return False
        
        # Run all FIDUS data integrity tests
        tests = [
            ("Investments Overview API", self.test_investments_overview_api),
            ("Client Money API", self.test_client_money_api),
            ("Salespeople API", self.test_salespeople_api),
            ("MT5 Accounts Guillermo Garcia", self.test_mt5_accounts_guillermo_garcia)
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
        print("📊 FIDUS PLATFORM DATA INTEGRITY VERIFICATION SUMMARY")
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
            print("🎉 FIDUS PLATFORM DATA INTEGRITY VERIFICATION: SUCCESSFUL")
            print("✅ Total AUM: $380,536.05 verified")
            print("✅ 3 clients with correct investment amounts verified")
            print("✅ Total Client Money: $380,536.05 verified")
            print("✅ Salespeople data (Javier Gonzalez & Salvador Palma) verified")
            print("✅ Guillermo Garcia MT5 accounts (2205 & 2209) verified")
            return True
        else:
            print("🚨 FIDUS PLATFORM DATA INTEGRITY VERIFICATION: NEEDS ATTENTION")
            print("❌ Critical data integrity issues found")
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