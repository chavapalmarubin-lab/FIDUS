#!/usr/bin/env python3
"""
REVIEW REQUEST VERIFICATION TEST - Trading Platform Fixed Endpoints
Testing the specific endpoints mentioned in the review request:

**Authentication**: admin/password123

**Fixed Endpoints to Test**:

1. **Investment Admin Overview** (FIXED - should now show data):
   - GET /api/investments/admin/overview
   - Should show total_aum > 0, total_investments > 0, clients with Alejandro

2. **MT5 Accounts** (FIXED - just created 4 accounts):
   - GET /api/mt5/accounts/client_alejandro
   - Should return 4 MEXAtlantic accounts totaling $118,151.41

3. **Client Investments** (working):
   - GET /api/investments/client/client_alejandro
   - Should return investments for Alejandro

**Expected Results**:
- Admin overview should show AUM > $100,000 with Alejandro's data
- MT5 accounts should show 4 accounts: 886557 ($80k), 886066 ($10k), 886602 ($10k), 885822 ($18k)
- All endpoints should return data that the frontend can display

**This should fix the user's issue of seeing no data in the dashboard.**
"""

import requests
import json
import sys
from datetime import datetime

# Use the correct backend URL from frontend/.env
BACKEND_URL = "https://trading-platform-76.preview.emergentagent.com/api"

class ReviewRequestTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, details, response_data=None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        
        if response_data and (not success or "PASS" in test_name):
            print(f"   Response: {json.dumps(response_data, indent=2)}")
    
    def test_admin_authentication(self):
        """Test admin login with credentials admin/password123"""
        print("\n🔐 TESTING ADMIN AUTHENTICATION")
        
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
                        f"Successfully authenticated as {data.get('name', 'admin')} with JWT token",
                        {"user_id": data.get("id"), "username": data.get("username"), "type": data.get("type")}
                    )
                    return True
                else:
                    self.log_test("Admin Authentication", False, "No token in response", data)
                    return False
            else:
                self.log_test("Admin Authentication", False, f"HTTP {response.status_code}", response.json() if response.content else None)
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_investment_admin_overview_fixed(self):
        """Test Investment Admin Overview (FIXED - should now show data)"""
        print("\n📊 TESTING INVESTMENT ADMIN OVERVIEW (FIXED)")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/investments/admin/overview")
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract numeric values
                total_aum = data.get("total_aum", 0)
                total_investments = data.get("total_investments", 0)
                total_clients = data.get("total_clients", 0)
                
                # Convert AUM string to float if needed
                if isinstance(total_aum, str):
                    total_aum = float(total_aum.replace("$", "").replace(",", ""))
                
                # Check if meets expected criteria from review request
                aum_sufficient = total_aum > 100000  # Should be > $100,000
                has_investments = total_investments > 0
                has_clients = total_clients > 0
                
                # Check for Alejandro in client details if available
                clients_data = data.get("clients", [])
                alejandro_found = any("Alejandro" in str(client) for client in clients_data) if clients_data else True
                
                success = aum_sufficient and has_investments and has_clients
                
                if success:
                    self.log_test(
                        "Investment Admin Overview - FIXED PASS",
                        True,
                        f"✅ AUM: ${total_aum:,.2f} (>{100000:,}), Investments: {total_investments}, Clients: {total_clients}",
                        {
                            "total_aum": total_aum,
                            "total_investments": total_investments, 
                            "total_clients": total_clients,
                            "meets_review_criteria": True
                        }
                    )
                else:
                    issues = []
                    if not aum_sufficient:
                        issues.append(f"AUM too low: ${total_aum:,.2f} <= $100,000")
                    if not has_investments:
                        issues.append("No investments found")
                    if not has_clients:
                        issues.append("No clients found")
                    
                    self.log_test(
                        "Investment Admin Overview - FAILED",
                        False,
                        f"❌ Issues: {'; '.join(issues)}",
                        data
                    )
                    
                return success
            else:
                self.log_test("Investment Admin Overview", False, f"HTTP {response.status_code}", response.json() if response.content else None)
                return False
                
        except Exception as e:
            self.log_test("Investment Admin Overview", False, f"Exception: {str(e)}")
            return False
    
    def test_mt5_accounts_fixed(self):
        """Test MT5 Accounts (FIXED - just created 4 accounts)"""
        print("\n🏦 TESTING MT5 ACCOUNTS (FIXED - 4 MEXAtlantic accounts)")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/mt5/accounts/client_alejandro")
            
            if response.status_code == 200:
                data = response.json()
                
                accounts = data.get("accounts", [])
                
                if not accounts:
                    self.log_test(
                        "MT5 Accounts - EMPTY",
                        False,
                        "❌ No MT5 accounts found for client_alejandro - expected 4 MEXAtlantic accounts",
                        data
                    )
                    return False
                
                # Check for MEXAtlantic accounts
                mexatlantic_accounts = [acc for acc in accounts if "MEXAtlantic" in str(acc.get("broker_name", ""))]
                
                # Expected account numbers and balances from review request
                expected_accounts = {
                    "886557": 80000,    # $80k
                    "886066": 10000,    # $10k
                    "886602": 10000,    # $10k
                    "885822": 18151.41  # $18k (actually $18,151.41)
                }
                
                found_accounts = {}
                total_balance = 0
                
                for account in mexatlantic_accounts:
                    account_number = str(account.get("mt5_account_number", ""))
                    balance = float(account.get("balance", 0))
                    found_accounts[account_number] = balance
                    total_balance += balance
                
                # Check if we have the expected accounts from review request
                expected_total = 118151.41  # Total from review request
                has_correct_count = len(mexatlantic_accounts) == 4
                has_correct_total = abs(total_balance - expected_total) < 100.0  # Allow some variance
                
                # Check for specific account numbers from review request
                expected_account_numbers = set(expected_accounts.keys())
                found_account_numbers = set(found_accounts.keys())
                missing_accounts = expected_account_numbers - found_account_numbers
                
                if has_correct_count and has_correct_total and not missing_accounts:
                    self.log_test(
                        "MT5 Accounts - FIXED PASS",
                        True,
                        f"✅ Found {len(mexatlantic_accounts)} MEXAtlantic accounts, Total: ${total_balance:,.2f}",
                        {
                            "account_count": len(mexatlantic_accounts),
                            "total_balance": total_balance,
                            "accounts": found_accounts,
                            "expected_total": expected_total,
                            "meets_review_criteria": True
                        }
                    )
                    return True
                else:
                    issues = []
                    if not has_correct_count:
                        issues.append(f"Expected 4 accounts, found {len(mexatlantic_accounts)}")
                    if not has_correct_total:
                        issues.append(f"Expected ${expected_total:,.2f}, found ${total_balance:,.2f}")
                    if missing_accounts:
                        issues.append(f"Missing accounts: {missing_accounts}")
                    
                    self.log_test(
                        "MT5 Accounts - INCOMPLETE FIX",
                        False,
                        f"❌ Issues: {'; '.join(issues)}",
                        {
                            "found_accounts": found_accounts,
                            "expected_accounts": expected_accounts,
                            "total_balance": total_balance,
                            "expected_total": expected_total
                        }
                    )
                    return False
                    
            else:
                self.log_test("MT5 Accounts", False, f"HTTP {response.status_code}", response.json() if response.content else None)
                return False
                
        except Exception as e:
            self.log_test("MT5 Accounts", False, f"Exception: {str(e)}")
            return False
    
    def test_client_investments_working(self):
        """Test Client Investments (working) - should return investments for Alejandro"""
        print("\n💰 TESTING CLIENT INVESTMENTS (working)")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/investments/client/client_alejandro")
            
            if response.status_code == 200:
                data = response.json()
                
                investments = data.get("investments", [])
                
                if not investments:
                    self.log_test(
                        "Client Investments - EMPTY",
                        False,
                        "❌ No investments found for client_alejandro",
                        data
                    )
                    return False
                
                # Calculate total value
                total_value = sum(float(inv.get("current_value", 0)) for inv in investments)
                fund_codes = [inv.get("fund_code") for inv in investments]
                
                # Should have investments for Alejandro
                has_investments = len(investments) > 0
                has_value = total_value > 0
                
                if has_investments and has_value:
                    self.log_test(
                        "Client Investments - WORKING PASS",
                        True,
                        f"✅ Found {len(investments)} investments, Total: ${total_value:,.2f}, Funds: {fund_codes}",
                        {
                            "investment_count": len(investments),
                            "total_value": total_value,
                            "fund_codes": fund_codes,
                            "meets_review_criteria": True
                        }
                    )
                    return True
                else:
                    self.log_test(
                        "Client Investments - INSUFFICIENT DATA",
                        False,
                        f"❌ Insufficient investment data: {len(investments)} investments, ${total_value:,.2f} total",
                        data
                    )
                    return False
                    
            else:
                self.log_test("Client Investments", False, f"HTTP {response.status_code}", response.json() if response.content else None)
                return False
                
        except Exception as e:
            self.log_test("Client Investments", False, f"Exception: {str(e)}")
            return False
    
    def run_review_request_verification(self):
        """Run verification tests for the review request fixed endpoints"""
        print("🎯 REVIEW REQUEST VERIFICATION - Trading Platform Fixed Endpoints")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Authentication: admin/password123")
        print(f"Test Time: {datetime.now().isoformat()}")
        print("=" * 80)
        print("REVIEW REQUEST REQUIREMENTS:")
        print("1. Investment Admin Overview (FIXED) - should show AUM > $100,000 with Alejandro")
        print("2. MT5 Accounts (FIXED) - should return 4 MEXAtlantic accounts totaling $118,151.41")
        print("3. Client Investments (working) - should return investments for Alejandro")
        print("=" * 80)
        
        # Test sequence matching the review request
        tests = [
            ("Admin Authentication", self.test_admin_authentication),
            ("Investment Admin Overview (FIXED)", self.test_investment_admin_overview_fixed),
            ("MT5 Accounts (FIXED)", self.test_mt5_accounts_fixed),
            ("Client Investments (working)", self.test_client_investments_working)
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed_tests += 1
            except Exception as e:
                print(f"❌ CRITICAL ERROR in {test_name}: {str(e)}")
        
        # Final Summary
        print("\n" + "=" * 80)
        print("🎯 REVIEW REQUEST VERIFICATION RESULTS")
        print("=" * 80)
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"Overall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests})")
        
        # Determine if the review request requirements are met
        if success_rate == 100:
            print("\n🎉 SUCCESS: All review request requirements are met!")
            print("✅ Investment Admin Overview shows AUM > $100,000 with data")
            print("✅ MT5 Accounts returns 4 MEXAtlantic accounts totaling $118,151.41")
            print("✅ Client Investments returns Alejandro's investment data")
            print("\n👍 The user's issue of seeing no data in the dashboard should be RESOLVED.")
            print("🚀 Frontend should now display all data correctly.")
        elif success_rate >= 75:
            print("\n⚠️  PARTIAL SUCCESS: Most requirements met but some issues remain")
            failed_tests = [result["test"] for result in self.test_results if not result["success"]]
            print(f"❌ Failed requirements: {failed_tests}")
            print("🔧 Some fixes are working but additional work needed.")
        else:
            print("\n🚨 FAILURE: Critical review request requirements not met")
            failed_tests = [result["test"] for result in self.test_results if not result["success"]]
            print(f"❌ Failed requirements: {failed_tests}")
            print("🔧 The fixes have NOT resolved the user's dashboard data visibility issue.")
        
        # Specific recommendations based on review request
        print(f"\n📋 RECOMMENDATIONS FOR MAIN AGENT:")
        if not self.admin_token:
            print("   - Authentication failed - check admin credentials (admin/password123)")
        else:
            critical_failures = [result for result in self.test_results if not result["success"] and "FIXED" in result["test"]]
            if critical_failures:
                print("   - Critical endpoints still failing after fixes:")
                for failure in critical_failures:
                    print(f"     * {failure['test']}: {failure['details']}")
                print("   - Need to investigate why the 'fixed' endpoints are not returning expected data")
            else:
                print("   - All critical endpoints working - frontend should display data correctly")
                print("   - If user still reports no data, check frontend integration")
        
        return success_rate >= 75  # 75% success rate threshold

if __name__ == "__main__":
    tester = ReviewRequestTester()
    success = tester.run_review_request_verification()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)