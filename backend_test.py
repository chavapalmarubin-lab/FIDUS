#!/usr/bin/env python3
"""
Backend Testing for Fund Portfolio Management - Weighted Performance Endpoint Fix
Testing the newly fixed weighted performance endpoint after bug fix in fund_performance_calculator.py
Changed query from 'fund_code' to 'fund_type' to match MT5 accounts database structure.

Test Objectives:
1. Test /api/funds/CORE/performance - Should return weighted performance for CORE fund
2. Test /api/funds/BALANCE/performance - Should return weighted performance for BALANCE fund  
3. Test /api/funds/DYNAMIC/performance - Should return empty (no accounts yet)
4. Test /api/funds/performance/all - Should return all funds performance
5. Test /api/fund-portfolio/overview - Should now show NON-ZERO weighted returns

Expected MT5 Accounts:
- Account 885822: CORE fund, balance=$18,151.41, true_pnl=$-112.94
- Account 886557: BALANCE fund, balance=$80,000, true_pnl=$2,829.69
- Account 886066: BALANCE fund, balance=$9,901.59, true_pnl=$656.07
- Account 886602: BALANCE fund, balance=$10,740.53, true_pnl=$177.74
- Account 886528: SEPARATION, balance=$3,927.41, true_pnl=$0
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://truepnl-tracker.preview.emergentagent.com"

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class FundPerformanceTest:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.test_results = []
        
    def log_test(self, test_name, success, details):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        print()
    
    def authenticate(self):
        """Authenticate as admin and get JWT token"""
        try:
            auth_url = f"{BACKEND_URL}/api/auth/login"
            payload = {
                "username": ADMIN_USERNAME,
                "password": ADMIN_PASSWORD,
                "user_type": "admin"
            }
            
            response = self.session.post(auth_url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('token')
                if self.token:
                    self.session.headers.update({'Authorization': f'Bearer {self.token}'})
                    self.log_test("Admin Authentication", True, f"Successfully authenticated as {ADMIN_USERNAME}")
                    return True
                else:
                    self.log_test("Admin Authentication", False, "No token in response")
                    return False
            else:
                self.log_test("Admin Authentication", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_fund_performance_endpoint(self, fund_type, expected_accounts=None, expected_non_zero=True):
        """Test individual fund performance endpoint"""
        try:
            url = f"{BACKEND_URL}/api/funds/{fund_type}/performance"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required fields
                required_fields = ['account_count', 'total_aum', 'weighted_return', 'total_true_pnl']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test(f"Fund {fund_type} Performance Structure", False, 
                                f"Missing fields: {missing_fields}")
                    return False
                
                # Check if we expect non-zero values
                if expected_non_zero and fund_type in ['CORE', 'BALANCE']:
                    if data['account_count'] == 0:
                        self.log_test(f"Fund {fund_type} Performance Data", False, 
                                    f"Expected accounts but got account_count=0")
                        return False
                    
                    if data['total_aum'] == 0:
                        self.log_test(f"Fund {fund_type} Performance Data", False, 
                                    f"Expected non-zero AUM but got total_aum=0")
                        return False
                
                # Log successful response
                details = f"account_count={data['account_count']}, total_aum=${data['total_aum']:,.2f}, weighted_return={data['weighted_return']:.2f}%, total_true_pnl=${data['total_true_pnl']:,.2f}"
                self.log_test(f"Fund {fund_type} Performance", True, details)
                
                # Validate expected values for specific funds
                if fund_type == 'CORE' and expected_accounts:
                    expected_count = 1
                    if data['account_count'] != expected_count:
                        self.log_test(f"Fund {fund_type} Account Count", False, 
                                    f"Expected {expected_count} accounts, got {data['account_count']}")
                        return False
                
                elif fund_type == 'BALANCE' and expected_accounts:
                    expected_count = 3
                    if data['account_count'] != expected_count:
                        self.log_test(f"Fund {fund_type} Account Count", False, 
                                    f"Expected {expected_count} accounts, got {data['account_count']}")
                        return False
                
                elif fund_type == 'DYNAMIC':
                    # DYNAMIC should have no accounts yet
                    if data['account_count'] != 0:
                        self.log_test(f"Fund {fund_type} Account Count", False, 
                                    f"Expected 0 accounts for DYNAMIC, got {data['account_count']}")
                        return False
                
                return True
                
            else:
                self.log_test(f"Fund {fund_type} Performance", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test(f"Fund {fund_type} Performance", False, f"Exception: {str(e)}")
            return False
    
    def test_all_funds_performance(self):
        """Test /api/funds/performance/all endpoint"""
        try:
            url = f"{BACKEND_URL}/api/funds/performance/all"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                # Should contain all 4 funds
                expected_funds = ['CORE', 'BALANCE', 'DYNAMIC', 'UNLIMITED']
                
                if 'funds' not in data:
                    self.log_test("All Funds Performance Structure", False, "Missing 'funds' key in response")
                    return False
                
                funds_data = data['funds']
                found_funds = list(funds_data.keys()) if isinstance(funds_data, dict) else []
                
                missing_funds = [fund for fund in expected_funds if fund not in found_funds]
                if missing_funds:
                    self.log_test("All Funds Performance Coverage", False, 
                                f"Missing funds: {missing_funds}. Found: {found_funds}")
                    return False
                
                # Check portfolio totals
                if 'portfolio_totals' in data:
                    totals = data['portfolio_totals']
                    details = f"Found {len(found_funds)} funds. Portfolio totals: total_accounts={totals.get('total_accounts', 'N/A')}, total_aum=${totals.get('total_aum', 0):,.2f}"
                else:
                    details = f"Found {len(found_funds)} funds: {found_funds}"
                
                self.log_test("All Funds Performance", True, details)
                return True
                
            else:
                self.log_test("All Funds Performance", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("All Funds Performance", False, f"Exception: {str(e)}")
            return False
    
    def test_fund_portfolio_overview(self):
        """Test /api/fund-portfolio/overview endpoint - should show NON-ZERO weighted returns"""
        try:
            url = f"{BACKEND_URL}/api/fund-portfolio/overview"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for funds data
                if 'funds' not in data:
                    self.log_test("Fund Portfolio Overview Structure", False, "Missing 'funds' key in response")
                    return False
                
                funds = data['funds']
                
                # Look for CORE and BALANCE funds with non-zero performance
                core_found = False
                balance_found = False
                
                for fund in funds:
                    if fund.get('fund_code') == 'CORE':
                        core_found = True
                        performance_ytd = fund.get('performance_ytd', 0)
                        if performance_ytd == 0:
                            self.log_test("CORE Fund Performance YTD", False, 
                                        f"Expected non-zero performance_ytd, got {performance_ytd}")
                        else:
                            self.log_test("CORE Fund Performance YTD", True, 
                                        f"performance_ytd={performance_ytd}% (non-zero)")
                    
                    elif fund.get('fund_code') == 'BALANCE':
                        balance_found = True
                        performance_ytd = fund.get('performance_ytd', 0)
                        if performance_ytd == 0:
                            self.log_test("BALANCE Fund Performance YTD", False, 
                                        f"Expected non-zero performance_ytd, got {performance_ytd}")
                        else:
                            self.log_test("BALANCE Fund Performance YTD", True, 
                                        f"performance_ytd={performance_ytd}% (non-zero)")
                
                if not core_found:
                    self.log_test("CORE Fund Presence", False, "CORE fund not found in portfolio overview")
                
                if not balance_found:
                    self.log_test("BALANCE Fund Presence", False, "BALANCE fund not found in portfolio overview")
                
                # Overall success if we found the funds
                details = f"Found {len(funds)} funds in portfolio overview"
                self.log_test("Fund Portfolio Overview", True, details)
                return True
                
            else:
                self.log_test("Fund Portfolio Overview", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Fund Portfolio Overview", False, f"Exception: {str(e)}")
            return False
    
    def test_mt5_accounts_verification(self):
        """Verify MT5 accounts exist with correct fund_type field"""
        try:
            url = f"{BACKEND_URL}/api/mt5/admin/accounts"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'accounts' not in data:
                    self.log_test("MT5 Accounts Structure", False, "Missing 'accounts' key in response")
                    return False
                
                accounts = data['accounts']
                
                # Expected accounts with fund_type
                expected_accounts = {
                    '885822': 'CORE',
                    '886557': 'BALANCE', 
                    '886066': 'BALANCE',
                    '886602': 'BALANCE',
                    '886528': 'SEPARATION'
                }
                
                found_accounts = {}
                for account in accounts:
                    login = str(account.get('login', ''))
                    fund_type = account.get('fund_type', account.get('fund_code', ''))
                    if login in expected_accounts:
                        found_accounts[login] = fund_type
                
                # Check if we found the expected accounts
                missing_accounts = []
                wrong_fund_type = []
                
                for login, expected_fund_type in expected_accounts.items():
                    if login not in found_accounts:
                        missing_accounts.append(f"{login} ({expected_fund_type})")
                    elif found_accounts[login] != expected_fund_type:
                        wrong_fund_type.append(f"{login}: expected {expected_fund_type}, got {found_accounts[login]}")
                
                if missing_accounts:
                    self.log_test("MT5 Accounts Presence", False, 
                                f"Missing accounts: {missing_accounts}")
                    return False
                
                if wrong_fund_type:
                    self.log_test("MT5 Accounts Fund Type", False, 
                                f"Wrong fund_type: {wrong_fund_type}")
                    return False
                
                details = f"Found {len(found_accounts)} expected accounts with correct fund_type: {found_accounts}"
                self.log_test("MT5 Accounts Verification", True, details)
                return True
                
            else:
                self.log_test("MT5 Accounts Verification", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("MT5 Accounts Verification", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all fund performance tests"""
        print("🎯 FUND PORTFOLIO MANAGEMENT - WEIGHTED PERFORMANCE ENDPOINT TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Testing Time: {datetime.now().isoformat()}")
        print()
        
        # Step 1: Authenticate
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return False
        
        # Step 2: Verify MT5 accounts have correct fund_type field
        print("📋 STEP 1: Verifying MT5 Accounts Structure")
        self.test_mt5_accounts_verification()
        print()
        
        # Step 3: Test individual fund performance endpoints
        print("📋 STEP 2: Testing Individual Fund Performance Endpoints")
        self.test_fund_performance_endpoint('CORE', expected_accounts=True)
        self.test_fund_performance_endpoint('BALANCE', expected_accounts=True)
        self.test_fund_performance_endpoint('DYNAMIC', expected_accounts=False)
        self.test_fund_performance_endpoint('UNLIMITED', expected_accounts=False)
        print()
        
        # Step 4: Test all funds performance endpoint
        print("📋 STEP 3: Testing All Funds Performance Endpoint")
        self.test_all_funds_performance()
        print()
        
        # Step 5: Test fund portfolio overview (frontend endpoint)
        print("📋 STEP 4: Testing Fund Portfolio Overview (Frontend Endpoint)")
        self.test_fund_portfolio_overview()
        print()
        
        # Summary
        self.print_summary()
        
        # Return overall success
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        return passed_tests == total_tests
    
    def print_summary(self):
        """Print test summary"""
        print("=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['details']}")
            print()
        
        print("✅ PASSED TESTS:")
        for result in self.test_results:
            if result['success']:
                print(f"   • {result['test']}: {result['details']}")
        print()
        
        # Overall assessment
        if success_rate >= 90:
            print("🎉 OVERALL RESULT: EXCELLENT - Fund performance endpoints working correctly!")
        elif success_rate >= 75:
            print("✅ OVERALL RESULT: GOOD - Most fund performance functionality working")
        elif success_rate >= 50:
            print("⚠️ OVERALL RESULT: PARTIAL - Some fund performance issues need attention")
        else:
            print("❌ OVERALL RESULT: CRITICAL - Major fund performance issues detected")
        
        print()
        print("🔍 KEY FINDINGS:")
        
        # Check if the main fix is working
        core_working = any(r['success'] and 'CORE' in r['test'] and 'Performance' in r['test'] 
                          for r in self.test_results)
        balance_working = any(r['success'] and 'BALANCE' in r['test'] and 'Performance' in r['test'] 
                             for r in self.test_results)
        
        if core_working and balance_working:
            print("   ✅ Fund performance calculation fix is working - CORE and BALANCE funds returning data")
        else:
            print("   ❌ Fund performance calculation fix may not be working - missing CORE/BALANCE data")
        
        # Check if weighted returns are non-zero
        non_zero_returns = any(r['success'] and 'Performance YTD' in r['test'] and 'non-zero' in r['details'] 
                              for r in self.test_results)
        
        if non_zero_returns:
            print("   ✅ Weighted returns are NON-ZERO - calculation fix successful")
        else:
            print("   ⚠️ Need to verify weighted returns are non-zero")
        
        print()

def main():
    """Main test execution"""
    tester = FundPerformanceTest()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()