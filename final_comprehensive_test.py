#!/usr/bin/env python3
"""
FINAL COMPREHENSIVE TEST: Alejandro Mariscal Production Setup Verification

Testing the exact requirements from the review request:
1. Authentication: admin/password123
2. Backend URL: https://trading-platform-76.preview.emergentagent.com/api
3. Investment Admin Overview: Should show AUM > $100,000 and total_investments > 0
4. MT5 Accounts (CRITICAL): GET /mt5/accounts/client_alejandro
   - Should return exactly 4 MEXAtlantic accounts: 886557 ($80k), 886066 ($10k), 886602 ($10k), 885822 ($18,151.41)
5. Ready for Investment: GET /clients/ready-for-investment - Should return Alejandro as available
6. Client Investments: GET /investments/client/client_alejandro - Should return investment data

CRITICAL SUCCESS CRITERIA: MT5 accounts endpoint MUST return 4 accounts totaling $118,151.41.
"""

import requests
import json
import sys
from datetime import datetime

# Use the exact backend URL from the review request
BACKEND_URL = "https://trading-platform-76.preview.emergentagent.com/api"

class FinalComprehensiveTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        self.critical_failures = []
        
    def log_test(self, test_name, success, details, response_data=None, is_critical=False):
        """Log test results with critical failure tracking"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data,
            "is_critical": is_critical
        }
        self.test_results.append(result)
        
        if not success and is_critical:
            self.critical_failures.append(test_name)
        
        status = "✅ PASS" if success else "❌ FAIL"
        critical_marker = " [CRITICAL]" if is_critical else ""
        print(f"{status} {test_name}{critical_marker}: {details}")
        
        if response_data and not success:
            print(f"   Response: {json.dumps(response_data, indent=2)}")
    
    def test_admin_authentication(self):
        """Test admin login with exact credentials from review request"""
        print("\n🔐 TESTING ADMIN AUTHENTICATION")
        print("   Credentials: admin/password123")
        
        try:
            login_data = {
                "username": "admin",
                "password": "password123", 
                "user_type": "admin"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("token"):
                    self.admin_token = data["token"]
                    self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
                    
                    self.log_test(
                        "Admin Authentication",
                        True,
                        f"Successfully authenticated as {data.get('name', 'admin')}",
                        {"user_id": data.get("id"), "username": data.get("username")},
                        is_critical=True
                    )
                    return True
                else:
                    self.log_test("Admin Authentication", False, "No token in response", data, is_critical=True)
                    return False
            else:
                self.log_test("Admin Authentication", False, f"HTTP {response.status_code}", response.json() if response.content else None, is_critical=True)
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}", is_critical=True)
            return False
    
    def test_investment_admin_overview(self):
        """Test investment admin overview - should show AUM > $100,000 and total_investments > 0"""
        print("\n📊 TESTING INVESTMENT ADMIN OVERVIEW")
        print("   Expected: AUM > $100,000 and total_investments > 0")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/investments/admin/overview")
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract numeric values
                total_aum = data.get("total_aum", 0)
                total_investments = data.get("total_investments", 0)
                total_clients = data.get("total_clients", 0)
                
                # Convert AUM to float if it's a string
                if isinstance(total_aum, str):
                    total_aum = float(total_aum.replace("$", "").replace(",", ""))
                
                # Check requirements
                aum_meets_requirement = total_aum > 100000
                investments_meets_requirement = total_investments > 0
                
                success = aum_meets_requirement and investments_meets_requirement
                
                self.log_test(
                    "Investment Admin Overview", 
                    success,
                    f"AUM: ${total_aum:,.2f} ({'✓' if aum_meets_requirement else '✗'} >$100k), Investments: {total_investments} ({'✓' if investments_meets_requirement else '✗'} >0), Clients: {total_clients}",
                    data,
                    is_critical=True
                )
                    
                return success
            else:
                self.log_test("Investment Admin Overview", False, f"HTTP {response.status_code}", response.json() if response.content else None, is_critical=True)
                return False
                
        except Exception as e:
            self.log_test("Investment Admin Overview", False, f"Exception: {str(e)}", is_critical=True)
            return False
    
    def test_mt5_accounts_critical(self):
        """CRITICAL TEST: MT5 accounts for client_alejandro - MUST return exactly 4 MEXAtlantic accounts totaling $118,151.41"""
        print("\n🏦 TESTING MT5 ACCOUNTS (CRITICAL)")
        print("   Expected: Exactly 4 MEXAtlantic accounts: 886557 ($80k), 886066 ($10k), 886602 ($10k), 885822 ($18,151.41)")
        print("   Total Expected: $118,151.41")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/mt5/accounts/client_alejandro")
            
            if response.status_code == 200:
                data = response.json()
                accounts = data.get("accounts", [])
                
                if not accounts:
                    self.log_test(
                        "MT5 Accounts - CRITICAL FAILURE",
                        False,
                        "NO MT5 accounts found for client_alejandro - Expected 4 MEXAtlantic accounts",
                        data,
                        is_critical=True
                    )
                    return False
                
                # Check for MEXAtlantic accounts
                mexatlantic_accounts = [acc for acc in accounts if "MEXAtlantic" in acc.get("broker_name", "")]
                
                # Expected account numbers and balances
                expected_accounts = {
                    "886557": 80000.00,
                    "886066": 10000.00, 
                    "886602": 10000.00,
                    "885822": 18151.41
                }
                
                found_accounts = {}
                total_balance = 0
                
                for account in mexatlantic_accounts:
                    account_number = str(account.get("mt5_account_number", ""))
                    balance = float(account.get("balance", 0))
                    found_accounts[account_number] = balance
                    total_balance += balance
                
                # Check if we have exactly the expected accounts
                expected_total = 118151.41
                accounts_match = len(mexatlantic_accounts) == 4
                balance_matches = abs(total_balance - expected_total) < 0.01
                
                if accounts_match and balance_matches:
                    self.log_test(
                        "MT5 Accounts - CRITICAL SUCCESS",
                        True,
                        f"Found {len(mexatlantic_accounts)} MEXAtlantic accounts totaling ${total_balance:,.2f}",
                        {"found_accounts": found_accounts, "total_balance": total_balance},
                        is_critical=True
                    )
                    return True
                else:
                    missing_details = []
                    if not accounts_match:
                        missing_details.append(f"Expected 4 accounts, found {len(mexatlantic_accounts)}")
                    if not balance_matches:
                        missing_details.append(f"Expected ${expected_total:,.2f}, found ${total_balance:,.2f}")
                    
                    self.log_test(
                        "MT5 Accounts - CRITICAL FAILURE",
                        False,
                        f"Account mismatch: {'; '.join(missing_details)}",
                        {"expected": expected_accounts, "found": found_accounts, "total_found": total_balance},
                        is_critical=True
                    )
                    return False
                
            else:
                self.log_test("MT5 Accounts - CRITICAL FAILURE", False, f"HTTP {response.status_code}", response.json() if response.content else None, is_critical=True)
                return False
                
        except Exception as e:
            self.log_test("MT5 Accounts - CRITICAL FAILURE", False, f"Exception: {str(e)}", is_critical=True)
            return False
    
    def test_ready_for_investment(self):
        """Test ready for investment - should return Alejandro as available"""
        print("\n👥 TESTING READY FOR INVESTMENT")
        print("   Expected: Alejandro Mariscal Romero should be available for investment")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/clients/ready-for-investment")
            
            if response.status_code == 200:
                data = response.json()
                ready_clients = data.get("ready_clients", [])
                
                # Look for Alejandro
                alejandro_found = None
                for client in ready_clients:
                    if (client.get("client_id") == "client_alejandro" or 
                        "Alejandro" in client.get("name", "")):
                        alejandro_found = client
                        break
                
                if alejandro_found:
                    self.log_test(
                        "Ready for Investment",
                        True,
                        f"Alejandro found: {alejandro_found.get('name')} ({alejandro_found.get('client_id')})",
                        alejandro_found,
                        is_critical=True
                    )
                    return True
                else:
                    self.log_test(
                        "Ready for Investment",
                        False,
                        f"Alejandro NOT found in {len(ready_clients)} ready clients",
                        data,
                        is_critical=True
                    )
                    return False
                
            else:
                self.log_test("Ready for Investment", False, f"HTTP {response.status_code}", response.json() if response.content else None, is_critical=True)
                return False
                
        except Exception as e:
            self.log_test("Ready for Investment", False, f"Exception: {str(e)}", is_critical=True)
            return False
    
    def test_client_investments(self):
        """Test client investments for Alejandro - should return investment data"""
        print("\n💰 TESTING CLIENT INVESTMENTS")
        print("   Expected: Investment data for client_alejandro")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/investments/client/client_alejandro")
            
            if response.status_code == 200:
                data = response.json()
                investments = data.get("investments", [])
                
                if investments:
                    total_value = sum(inv.get("current_value", 0) for inv in investments)
                    fund_codes = [inv.get("fund_code") for inv in investments]
                    
                    self.log_test(
                        "Client Investments",
                        True,
                        f"Found {len(investments)} investments totaling ${total_value:,.2f}, Funds: {fund_codes}",
                        {"investment_count": len(investments), "total_value": total_value, "funds": fund_codes},
                        is_critical=True
                    )
                    return True
                else:
                    self.log_test(
                        "Client Investments",
                        False,
                        "No investments found for client_alejandro",
                        data,
                        is_critical=True
                    )
                    return False
                
            else:
                self.log_test("Client Investments", False, f"HTTP {response.status_code}", response.json() if response.content else None, is_critical=True)
                return False
                
        except Exception as e:
            self.log_test("Client Investments", False, f"Exception: {str(e)}", is_critical=True)
            return False
    
    def run_final_comprehensive_test(self):
        """Run the final comprehensive test as specified in the review request"""
        print("🎯 FINAL COMPREHENSIVE TEST: Alejandro Mariscal Production Setup")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Authentication: admin/password123")
        print(f"Test Time: {datetime.now().isoformat()}")
        print("=" * 80)
        
        # Test sequence exactly as specified in review request
        tests = [
            ("Authentication", self.test_admin_authentication),
            ("Investment Admin Overview", self.test_investment_admin_overview),
            ("MT5 Accounts (CRITICAL)", self.test_mt5_accounts_critical),
            ("Ready for Investment", self.test_ready_for_investment),
            ("Client Investments", self.test_client_investments)
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed_tests += 1
            except Exception as e:
                print(f"❌ CRITICAL ERROR in {test_name}: {str(e)}")
                self.critical_failures.append(test_name)
        
        # Final Summary
        print("\n" + "=" * 80)
        print("🎯 FINAL COMPREHENSIVE TEST RESULTS")
        print("=" * 80)
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"Overall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests})")
        
        # Critical Success Criteria Check
        mt5_test_passed = not any("MT5" in failure for failure in self.critical_failures)
        
        print(f"\n🎯 CRITICAL SUCCESS CRITERIA:")
        print(f"   MT5 Accounts (4 MEXAtlantic accounts totaling $118,151.41): {'✅ PASS' if mt5_test_passed else '❌ FAIL'}")
        
        if self.critical_failures:
            print(f"\n🚨 CRITICAL FAILURES:")
            for failure in self.critical_failures:
                print(f"   - {failure}")
        
        # Final Verdict
        print(f"\n🏁 FINAL VERDICT:")
        if success_rate == 100 and mt5_test_passed:
            print("   ✅ PRODUCTION READY - All endpoints working correctly")
            print("   ✅ User complaint resolved - MT5 accounts and investments visible")
        elif mt5_test_passed:
            print("   ⚠️  MOSTLY READY - MT5 accounts working but some minor issues")
        else:
            print("   ❌ NOT PRODUCTION READY - Critical MT5 accounts issue unresolved")
            print("   ❌ User complaint VALID - MT5 accounts not properly configured")
        
        return success_rate >= 80 and mt5_test_passed

if __name__ == "__main__":
    tester = FinalComprehensiveTester()
    success = tester.run_final_comprehensive_test()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)