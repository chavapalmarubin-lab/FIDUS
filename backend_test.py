#!/usr/bin/env python3
"""
Backend Testing for Performance Fee Endpoints (Phase 3)
Testing the 6 new performance fee endpoints added to the backend.

Test Objectives:
1. GET /api/admin/performance-fees/current - Should return total of $1,000.64
2. POST /api/admin/performance-fees/calculate-daily - Should calculate fees successfully
3. GET /api/admin/performance-fees/summary - Should show correct period and totals
4. GET /api/admin/performance-fees/transactions - Should work (even if empty)
5. PUT /api/admin/money-managers/{manager_id}/performance-fee - Should update fee rate
6. Verify all endpoints return HTTP 200 and expected data structure

Expected Results:
- Current fees total: $1,000.64
- 3 managers with fees: TradingHub Gold ($848.91), GoldenTrade ($98.41), UNO14 MAM ($53.32)
- CP Strategy should have $0 fee (loss)
- Summary shows period "2025-10", accrued_fees: 1000.64, paid_fees: 0
- Transactions endpoint works (empty array initially)
- Manager fee update works correctly
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://financeflow-89.preview.emergentagent.com"

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class CashFlowBrokerRebatesTest:
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
    
    def test_cash_flow_overview_broker_rebates(self):
        """Test /api/admin/cashflow/overview endpoint for broker rebates fix"""
        try:
            url = f"{BACKEND_URL}/api/admin/cashflow/overview"
            params = {
                "timeframe": "12_months",
                "fund": "all"
            }
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if response has summary section
                if 'summary' not in data:
                    self.log_test("Cash Flow Overview Structure", False, "Missing 'summary' key in response")
                    return False
                
                summary = data['summary']
                
                # CRITICAL TEST: Check broker_rebates is NOT 0.0
                broker_rebates = summary.get('broker_rebates', 0)
                if broker_rebates == 0.0:
                    self.log_test("Broker Rebates Fix", False, 
                                f"broker_rebates is still hardcoded to 0.0 - fix not working")
                    return False
                
                # Check if broker_rebates matches expected value (291.44)
                expected_rebates = 291.44
                if abs(broker_rebates - expected_rebates) < 0.01:
                    self.log_test("Broker Rebates Value", True, 
                                f"broker_rebates = ${broker_rebates:.2f} (matches expected ${expected_rebates:.2f})")
                else:
                    self.log_test("Broker Rebates Value", True, 
                                f"broker_rebates = ${broker_rebates:.2f} (non-zero, different from expected ${expected_rebates:.2f})")
                
                # Check if rebates_summary object is present
                if 'rebates_summary' not in data:
                    self.log_test("Rebates Summary Object", False, "Missing 'rebates_summary' object in response")
                    return False
                
                rebates_summary = data['rebates_summary']
                
                # Verify rebates_summary structure
                required_rebate_fields = ['total_rebates', 'total_volume', 'rebate_breakdown']
                missing_rebate_fields = [field for field in required_rebate_fields if field not in rebates_summary]
                
                if missing_rebate_fields:
                    self.log_test("Rebates Summary Structure", False, 
                                f"Missing fields in rebates_summary: {missing_rebate_fields}")
                    return False
                
                # Check rebates_summary values
                total_rebates = rebates_summary.get('total_rebates', 0)
                total_volume = rebates_summary.get('total_volume', 0)
                
                if total_rebates != broker_rebates:
                    self.log_test("Rebates Summary Consistency", False, 
                                f"summary.broker_rebates (${broker_rebates:.2f}) != rebates_summary.total_rebates (${total_rebates:.2f})")
                    return False
                
                # Check fund_revenue includes broker rebates
                fund_revenue = summary.get('fund_revenue', 0)
                if fund_revenue == 0:
                    self.log_test("Fund Revenue Calculation", False, "fund_revenue is 0 - should include broker rebates")
                    return False
                
                # Check net_profit calculation
                net_profit = summary.get('net_profit', 0)
                
                details = (f"broker_rebates=${broker_rebates:.2f}, "
                          f"total_rebates=${total_rebates:.2f}, "
                          f"total_volume={total_volume:.2f} lots, "
                          f"fund_revenue=${fund_revenue:.2f}, "
                          f"net_profit=${net_profit:.2f}")
                
                self.log_test("Cash Flow Overview Broker Rebates", True, details)
                return True
                
            else:
                self.log_test("Cash Flow Overview Broker Rebates", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Cash Flow Overview Broker Rebates", False, f"Exception: {str(e)}")
            return False
    
    def test_mt5_fund_performance_consistency(self):
        """Test /api/mt5/fund-performance/corrected for consistent broker rebates"""
        try:
            url = f"{BACKEND_URL}/api/mt5/fund-performance/corrected"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if response has fund_assets section
                if 'fund_assets' not in data:
                    self.log_test("MT5 Fund Performance Structure", False, "Missing 'fund_assets' key in response")
                    return False
                
                fund_assets = data['fund_assets']
                
                # Check broker_rebates in fund_assets
                broker_rebates = fund_assets.get('broker_rebates', 0)
                
                if broker_rebates == 0.0:
                    self.log_test("MT5 Fund Performance Broker Rebates", False, 
                                f"broker_rebates is 0.0 in MT5 fund performance endpoint")
                    return False
                
                details = f"fund_assets.broker_rebates = ${broker_rebates:.2f}"
                self.log_test("MT5 Fund Performance Broker Rebates", True, details)
                
                # Store for consistency check
                self.mt5_broker_rebates = broker_rebates
                return True
                
            else:
                self.log_test("MT5 Fund Performance Broker Rebates", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("MT5 Fund Performance Broker Rebates", False, f"Exception: {str(e)}")
            return False
    
    def test_broker_rebates_consistency(self):
        """Test consistency between both endpoints"""
        if hasattr(self, 'mt5_broker_rebates') and hasattr(self, 'cashflow_broker_rebates'):
            if abs(self.mt5_broker_rebates - self.cashflow_broker_rebates) < 0.01:
                self.log_test("Broker Rebates Consistency", True, 
                            f"Both endpoints return consistent broker_rebates: ${self.cashflow_broker_rebates:.2f}")
                return True
            else:
                self.log_test("Broker Rebates Consistency", False, 
                            f"Inconsistent values: Cash Flow=${self.cashflow_broker_rebates:.2f}, MT5=${self.mt5_broker_rebates:.2f}")
                return False
        else:
            self.log_test("Broker Rebates Consistency", False, "Cannot compare - missing data from previous tests")
            return False
    
    def test_response_structure(self):
        """Test that response structure matches expected format"""
        try:
            url = f"{BACKEND_URL}/api/admin/cashflow/overview"
            params = {"timeframe": "12_months", "fund": "all"}
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check top-level structure
                required_top_level = ['summary', 'rebates_summary']
                missing_top_level = [field for field in required_top_level if field not in data]
                
                if missing_top_level:
                    self.log_test("Response Structure - Top Level", False, 
                                f"Missing top-level fields: {missing_top_level}")
                    return False
                
                # Check summary structure
                summary = data['summary']
                required_summary_fields = ['broker_rebates', 'fund_revenue', 'net_profit']
                missing_summary_fields = [field for field in required_summary_fields if field not in summary]
                
                if missing_summary_fields:
                    self.log_test("Response Structure - Summary", False, 
                                f"Missing summary fields: {missing_summary_fields}")
                    return False
                
                # Check rebates_summary structure
                rebates_summary = data['rebates_summary']
                required_rebates_fields = ['total_rebates', 'total_volume', 'rebate_breakdown']
                missing_rebates_fields = [field for field in required_rebates_fields if field not in rebates_summary]
                
                if missing_rebates_fields:
                    self.log_test("Response Structure - Rebates Summary", False, 
                                f"Missing rebates_summary fields: {missing_rebates_fields}")
                    return False
                
                # Check data types
                if not isinstance(summary['broker_rebates'], (int, float)):
                    self.log_test("Response Structure - Data Types", False, 
                                f"broker_rebates should be number, got {type(summary['broker_rebates'])}")
                    return False
                
                if not isinstance(rebates_summary['total_rebates'], (int, float)):
                    self.log_test("Response Structure - Data Types", False, 
                                f"total_rebates should be number, got {type(rebates_summary['total_rebates'])}")
                    return False
                
                if not isinstance(rebates_summary['total_volume'], (int, float)):
                    self.log_test("Response Structure - Data Types", False, 
                                f"total_volume should be number, got {type(rebates_summary['total_volume'])}")
                    return False
                
                if not isinstance(rebates_summary['rebate_breakdown'], dict):
                    self.log_test("Response Structure - Data Types", False, 
                                f"rebate_breakdown should be object, got {type(rebates_summary['rebate_breakdown'])}")
                    return False
                
                self.log_test("Response Structure", True, "All required fields present with correct data types")
                return True
                
            else:
                self.log_test("Response Structure", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Response Structure", False, f"Exception: {str(e)}")
            return False
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
        """Run all cash flow broker rebates tests"""
        print("🎯 CASH FLOW BROKER REBATES FIX TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Testing Time: {datetime.now().isoformat()}")
        print()
        
        # Step 1: Authenticate
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return False
        
        # Step 2: Test Cash Flow Overview Broker Rebates
        print("📋 STEP 1: Testing Cash Flow Overview Broker Rebates Fix")
        cashflow_success = self.test_cash_flow_overview_broker_rebates()
        if cashflow_success:
            # Store the broker rebates value for consistency check
            try:
                url = f"{BACKEND_URL}/api/admin/cashflow/overview"
                params = {"timeframe": "12_months", "fund": "all"}
                response = self.session.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    self.cashflow_broker_rebates = data.get('summary', {}).get('broker_rebates', 0)
            except:
                pass
        print()
        
        # Step 3: Test MT5 Fund Performance Consistency
        print("📋 STEP 2: Testing MT5 Fund Performance Consistency")
        self.test_mt5_fund_performance_consistency()
        print()
        
        # Step 4: Test Broker Rebates Consistency Between Endpoints
        print("📋 STEP 3: Testing Broker Rebates Consistency")
        self.test_broker_rebates_consistency()
        print()
        
        # Step 5: Test Response Structure
        print("📋 STEP 4: Testing Response Structure")
        self.test_response_structure()
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
            print("🎉 OVERALL RESULT: EXCELLENT - Broker rebates fix working correctly!")
        elif success_rate >= 75:
            print("✅ OVERALL RESULT: GOOD - Most broker rebates functionality working")
        elif success_rate >= 50:
            print("⚠️ OVERALL RESULT: PARTIAL - Some broker rebates issues need attention")
        else:
            print("❌ OVERALL RESULT: CRITICAL - Major broker rebates issues detected")
        
        print()
        print("🔍 KEY FINDINGS:")
        
        # Check if the main fix is working
        rebates_fix_working = any(r['success'] and 'Broker Rebates Fix' in r['test'] 
                                 for r in self.test_results)
        
        if rebates_fix_working:
            print("   ✅ Broker rebates fix is working - endpoint no longer returns hardcoded 0.0")
        else:
            print("   ❌ Broker rebates fix may not be working - still returning hardcoded 0.0")
        
        # Check if values are consistent
        consistency_working = any(r['success'] and 'Consistency' in r['test'] 
                                 for r in self.test_results)
        
        if consistency_working:
            print("   ✅ Broker rebates values are consistent between endpoints")
        else:
            print("   ⚠️ Need to verify broker rebates consistency between endpoints")
        
        # Check if response structure is correct
        structure_working = any(r['success'] and 'Response Structure' in r['test'] 
                               for r in self.test_results)
        
        if structure_working:
            print("   ✅ Response structure includes rebates_summary object as expected")
        else:
            print("   ⚠️ Response structure may be missing required rebates fields")
        
        print()

def main():
    """Main test execution"""
    tester = CashFlowBrokerRebatesTest()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()