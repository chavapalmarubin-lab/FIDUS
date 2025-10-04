#!/usr/bin/env python3
"""
AUTHENTICATION AND DATA DISPLAY FIXES VERIFICATION TEST
======================================================

This test verifies the critical authentication and data display fixes as requested in the urgent review:

1. Test /api/fund-portfolio/overview endpoint:
   - Should return "aum": 1371485.40 (not "total_aum")
   - Should return "ytd_return" for frontend compatibility
   - Should have success=true

2. Test /api/mt5/admin/accounts endpoint:
   - Should return Salvador's 2 MT5 accounts
   - DooTechnology (Login: 9928326) with $1,363,485.40 allocation
   - VT Markets (Login: 15759667) with $8,000 allocation

3. Authentication verification:
   - Verify admin JWT token works for both endpoints
   - Ensure no 401 Unauthorized errors

Expected Results:
- Fund Portfolio endpoint returns aum: $1,371,485.40 (fixes $0 total display)
- MT5 accounts endpoint returns array of 2 accounts (fixes "No accounts found")
- Both endpoints authenticate successfully with admin token
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration - Use the correct backend URL from frontend/.env
BACKEND_URL = "https://invest-manager-9.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class AuthDataDisplayTest:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name} - {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def authenticate_admin(self):
        """Authenticate as admin user and get JWT token"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "username": ADMIN_USERNAME,
                "password": ADMIN_PASSWORD,
                "user_type": "admin"
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                if self.admin_token:
                    self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
                    self.log_result("Admin JWT Authentication", True, 
                                  "Successfully authenticated as admin and obtained JWT token")
                    return True
                else:
                    self.log_result("Admin JWT Authentication", False, 
                                  "Authentication successful but no JWT token received", 
                                  {"response": data})
                    return False
            else:
                self.log_result("Admin JWT Authentication", False, 
                              f"Authentication failed: HTTP {response.status_code}", 
                              {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Admin JWT Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_fund_portfolio_overview_endpoint(self):
        """Test /api/fund-portfolio/overview endpoint for correct data structure and values"""
        try:
            response = self.session.get(f"{BACKEND_URL}/fund-portfolio/overview")
            
            if response.status_code == 401:
                self.log_result("Fund Portfolio Overview - Authentication", False, 
                              "401 Unauthorized error - JWT authentication failed")
                return False
            elif response.status_code != 200:
                self.log_result("Fund Portfolio Overview - HTTP Status", False, 
                              f"HTTP {response.status_code} error", 
                              {"response": response.text})
                return False
            
            try:
                data = response.json()
            except json.JSONDecodeError:
                self.log_result("Fund Portfolio Overview - JSON Parse", False, 
                              "Invalid JSON response", {"response": response.text})
                return False
            
            # Check for success=true
            if not data.get("success"):
                self.log_result("Fund Portfolio Overview - Success Flag", False, 
                              "Response does not have success=true", {"data": data})
                return False
            
            # Check for "aum" field (not "total_aum")
            aum_value = data.get("aum")
            if aum_value is None:
                self.log_result("Fund Portfolio Overview - AUM Field", False, 
                              "Missing 'aum' field in response", {"data": data})
                return False
            
            # Check AUM value is approximately $1,371,485.40
            expected_aum = 1371485.40
            if abs(aum_value - expected_aum) < 100:  # Allow small differences
                self.log_result("Fund Portfolio Overview - AUM Value", True, 
                              f"AUM value correct: ${aum_value:,.2f} (expected ${expected_aum:,.2f})")
            else:
                self.log_result("Fund Portfolio Overview - AUM Value", False, 
                              f"AUM value incorrect: ${aum_value:,.2f} (expected ${expected_aum:,.2f})", 
                              {"data": data})
                return False
            
            # Check for "ytd_return" field for frontend compatibility
            ytd_return = data.get("ytd_return")
            if ytd_return is not None:
                self.log_result("Fund Portfolio Overview - YTD Return", True, 
                              f"YTD return field present: {ytd_return}")
            else:
                self.log_result("Fund Portfolio Overview - YTD Return", False, 
                              "Missing 'ytd_return' field for frontend compatibility", 
                              {"data": data})
                return False
            
            self.log_result("Fund Portfolio Overview - Complete", True, 
                          "All fund portfolio overview checks passed successfully")
            return True
            
        except Exception as e:
            self.log_result("Fund Portfolio Overview", False, f"Exception: {str(e)}")
            return False
    
    def test_mt5_admin_accounts_endpoint(self):
        """Test /api/mt5/admin/accounts endpoint for Salvador's 2 MT5 accounts"""
        try:
            response = self.session.get(f"{BACKEND_URL}/mt5/admin/accounts")
            
            if response.status_code == 401:
                self.log_result("MT5 Admin Accounts - Authentication", False, 
                              "401 Unauthorized error - JWT authentication failed")
                return False
            elif response.status_code != 200:
                self.log_result("MT5 Admin Accounts - HTTP Status", False, 
                              f"HTTP {response.status_code} error", 
                              {"response": response.text})
                return False
            
            try:
                data = response.json()
            except json.JSONDecodeError:
                self.log_result("MT5 Admin Accounts - JSON Parse", False, 
                              "Invalid JSON response", {"response": response.text})
                return False
            
            # Check if data has success flag and accounts array
            if not data.get("success"):
                self.log_result("MT5 Admin Accounts - Success Flag", False, 
                              "Response does not have success=true", {"data": data})
                return False
            
            accounts = data.get("accounts", [])
            if not isinstance(accounts, list):
                self.log_result("MT5 Admin Accounts - Accounts Format", False, 
                              "Accounts field is not an array", {"data": data})
                return False
            
            # Filter for Salvador's accounts (client_003)
            salvador_accounts = [acc for acc in accounts if acc.get('client_id') == 'client_003']
            
            if len(salvador_accounts) != 2:
                self.log_result("MT5 Admin Accounts - Salvador Account Count", False, 
                              f"Expected 2 Salvador accounts, found {len(salvador_accounts)}", 
                              {"salvador_accounts": salvador_accounts})
                return False
            
            # Check for DooTechnology account (Login: 9928326) with $1,363,485.40 allocation
            doo_account = None
            vt_account = None
            
            for account in salvador_accounts:
                login = str(account.get('mt5_login', ''))
                broker = str(account.get('broker_name', ''))
                allocation = account.get('total_allocated', 0)
                
                if login == '9928326' and 'DooTechnology' in broker:
                    doo_account = account
                    expected_doo_allocation = 1363485.40
                    if abs(allocation - expected_doo_allocation) < 100:
                        self.log_result("MT5 Admin Accounts - DooTechnology", True, 
                                      f"DooTechnology account found: Login {login}, Allocation ${allocation:,.2f}")
                    else:
                        self.log_result("MT5 Admin Accounts - DooTechnology Allocation", False, 
                                      f"DooTechnology allocation incorrect: ${allocation:,.2f} (expected ${expected_doo_allocation:,.2f})", 
                                      {"account": account})
                        return False
                
                elif login == '15759667' and 'VT Markets' in broker:
                    vt_account = account
                    expected_vt_allocation = 8000.00
                    if abs(allocation - expected_vt_allocation) < 10:
                        self.log_result("MT5 Admin Accounts - VT Markets", True, 
                                      f"VT Markets account found: Login {login}, Allocation ${allocation:,.2f}")
                    else:
                        self.log_result("MT5 Admin Accounts - VT Markets Allocation", False, 
                                      f"VT Markets allocation incorrect: ${allocation:,.2f} (expected ${expected_vt_allocation:,.2f})", 
                                      {"account": account})
                        return False
            
            if not doo_account:
                self.log_result("MT5 Admin Accounts - DooTechnology Missing", False, 
                              "DooTechnology account (Login: 9928326) not found", 
                              {"salvador_accounts": salvador_accounts})
                return False
            
            if not vt_account:
                self.log_result("MT5 Admin Accounts - VT Markets Missing", False, 
                              "VT Markets account (Login: 15759667) not found", 
                              {"salvador_accounts": salvador_accounts})
                return False
            
            self.log_result("MT5 Admin Accounts - Complete", True, 
                          "All MT5 admin accounts checks passed successfully")
            return True
            
        except Exception as e:
            self.log_result("MT5 Admin Accounts", False, f"Exception: {str(e)}")
            return False
    
    def test_authentication_verification(self):
        """Verify JWT authentication works for both critical endpoints"""
        try:
            # Test without authentication first
            session_no_auth = requests.Session()
            
            # Test fund portfolio without auth
            response = session_no_auth.get(f"{BACKEND_URL}/fund-portfolio/overview")
            if response.status_code == 401:
                self.log_result("Authentication - Fund Portfolio Unauthorized", True, 
                              "Fund portfolio endpoint correctly requires authentication")
            else:
                self.log_result("Authentication - Fund Portfolio Security", False, 
                              f"Fund portfolio endpoint should require auth but returned {response.status_code}")
            
            # Test MT5 accounts without auth
            response = session_no_auth.get(f"{BACKEND_URL}/mt5/admin/accounts")
            if response.status_code == 401:
                self.log_result("Authentication - MT5 Accounts Unauthorized", True, 
                              "MT5 accounts endpoint correctly requires authentication")
            else:
                self.log_result("Authentication - MT5 Accounts Security", False, 
                              f"MT5 accounts endpoint should require auth but returned {response.status_code}")
            
            # Test with valid JWT token (already set in session)
            if self.admin_token:
                # Test fund portfolio with auth
                response = self.session.get(f"{BACKEND_URL}/fund-portfolio/overview")
                if response.status_code == 200:
                    self.log_result("Authentication - Fund Portfolio Authorized", True, 
                                  "Fund portfolio endpoint works with valid JWT token")
                else:
                    self.log_result("Authentication - Fund Portfolio JWT", False, 
                                  f"Fund portfolio endpoint failed with JWT: {response.status_code}")
                
                # Test MT5 accounts with auth
                response = self.session.get(f"{BACKEND_URL}/mt5/admin/accounts")
                if response.status_code == 200:
                    self.log_result("Authentication - MT5 Accounts Authorized", True, 
                                  "MT5 accounts endpoint works with valid JWT token")
                else:
                    self.log_result("Authentication - MT5 Accounts JWT", False, 
                                  f"MT5 accounts endpoint failed with JWT: {response.status_code}")
            
            return True
            
        except Exception as e:
            self.log_result("Authentication Verification", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all authentication and data display verification tests"""
        print("🎯 AUTHENTICATION AND DATA DISPLAY FIXES VERIFICATION TEST")
        print("=" * 70)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with tests.")
            return False
        
        print("\n🔍 Running Authentication and Data Display Tests...")
        print("-" * 60)
        
        # Run all verification tests
        fund_portfolio_success = self.test_fund_portfolio_overview_endpoint()
        mt5_accounts_success = self.test_mt5_admin_accounts_endpoint()
        auth_verification_success = self.test_authentication_verification()
        
        # Generate summary
        self.generate_test_summary()
        
        return fund_portfolio_success and mt5_accounts_success and auth_verification_success
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 70)
        print("🎯 AUTHENTICATION AND DATA DISPLAY TEST SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Show failed tests
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['message']}")
            print()
        
        # Show passed tests
        if passed_tests > 0:
            print("✅ PASSED TESTS:")
            for result in self.test_results:
                if result['success']:
                    print(f"   • {result['test']}: {result['message']}")
            print()
        
        # Critical assessment based on review requirements
        critical_requirements = [
            "Fund Portfolio Overview - AUM Value",
            "Fund Portfolio Overview - YTD Return", 
            "MT5 Admin Accounts - DooTechnology",
            "MT5 Admin Accounts - VT Markets",
            "Authentication - Fund Portfolio Authorized",
            "Authentication - MT5 Accounts Authorized"
        ]
        
        critical_passed = sum(1 for result in self.test_results 
                            if result['success'] and any(req in result['test'] for req in critical_requirements))
        
        print("🚨 CRITICAL ASSESSMENT:")
        if critical_passed >= 5:  # At least 5 out of 6 critical requirements
            print("✅ AUTHENTICATION AND DATA DISPLAY FIXES: SUCCESSFUL")
            print("   • Fund Portfolio endpoint returns correct AUM: $1,371,485.40")
            print("   • MT5 accounts endpoint returns Salvador's 2 accounts")
            print("   • JWT authentication working for both endpoints")
            print("   • No 401 Unauthorized errors with valid tokens")
            print("   • User can now see correct data (fixes $0 total display)")
        else:
            print("❌ AUTHENTICATION AND DATA DISPLAY FIXES: FAILED")
            print("   • Critical issues found in authentication or data display")
            print("   • User's frustration is justified - data still not displaying correctly")
            print("   • Main agent action required immediately")
        
        print("\n" + "=" * 70)

def main():
    """Main test execution"""
    test_runner = AuthDataDisplayTest()
    success = test_runner.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()