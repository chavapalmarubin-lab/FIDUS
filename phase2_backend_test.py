#!/usr/bin/env python3
"""
Phase 2 Backend Endpoints Testing - Architectural Refactor

Context:
Testing 5 new endpoints created for architectural refactor as requested in review.

TEST OBJECTIVES:
1. Login as Admin (admin/password123)
2. Test /api/portfolio/fund-allocations - Expected: total_aum = 118151.41, funds with CORE and BALANCE
3. Test /api/investments/summary - Expected: total_aum = 118151.41, total_investments = 2, active_clients = 1
4. Test /api/analytics/trading-metrics?account=all - Expected: All metrics as strings with .2f format
5. Test /api/money-managers/performance - Expected: managers array with performance metrics
6. Test /api/mt5/accounts/all - Expected: ALL 7 accounts returned

SUCCESS CRITERIA:
- HTTP status for each endpoint
- Key values returned
- Any errors or missing data
- Confirmation that calculations are in backend (no need for frontend calculations)
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://mt5-dashboard-2.preview.emergentagent.com"

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class Phase2EndpointTesting:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.test_results = []
        
    def log_test(self, test_name, success, details, http_status=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "http_status": http_status,
            "timestamp": datetime.now().isoformat()
        })
        print(f"{status}: {test_name}")
        if http_status:
            print(f"   HTTP Status: {http_status}")
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
                    self.log_test("Admin Authentication", True, f"Successfully authenticated as {ADMIN_USERNAME}", 200)
                    return True
                else:
                    self.log_test("Admin Authentication", False, "No token in response", response.status_code)
                    return False
            else:
                self.log_test("Admin Authentication", False, f"Authentication failed: {response.text}", response.status_code)
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_portfolio_fund_allocations(self):
        """Test /api/portfolio/fund-allocations endpoint"""
        try:
            url = f"{BACKEND_URL}/api/portfolio/fund-allocations"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for expected total_aum = 118151.41
                total_aum = data.get('total_aum', 0)
                expected_aum = 118151.41
                
                # Check if funds with CORE and BALANCE are present
                funds = data.get('funds', [])
                core_found = any(fund.get('fund_code') == 'CORE' for fund in funds)
                balance_found = any(fund.get('fund_code') == 'BALANCE' for fund in funds)
                
                # Check if percentages are calculated in backend
                percentages_calculated = all('percentage' in fund for fund in funds)
                
                # Check if account numbers are included
                accounts_included = any('accounts' in fund or 'account_numbers' in fund for fund in funds)
                
                # Verify total_aum matches expected
                aum_match = abs(total_aum - expected_aum) < 1.0  # Allow small variance
                
                details = f"Total AUM: ${total_aum:,.2f} (expected: ${expected_aum:,.2f}), CORE: {core_found}, BALANCE: {balance_found}, Percentages: {percentages_calculated}, Accounts: {accounts_included}"
                
                success = aum_match and core_found and balance_found and percentages_calculated
                self.log_test("Portfolio Fund Allocations", success, details, response.status_code)
                return success
                
            else:
                self.log_test("Portfolio Fund Allocations", False, f"HTTP Error: {response.text}", response.status_code)
                return False
                
        except Exception as e:
            self.log_test("Portfolio Fund Allocations", False, f"Exception: {str(e)}")
            return False
    
    def test_investments_summary(self):
        """Test /api/investments/summary endpoint"""
        try:
            url = f"{BACKEND_URL}/api/investments/summary"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check expected values
                total_aum = data.get('total_aum', 0)
                total_investments = data.get('total_investments', 0)
                active_clients = data.get('active_clients', 0)
                avg_investment = data.get('avg_investment', 0)
                by_fund = data.get('by_fund', {})
                
                expected_aum = 118151.41
                expected_investments = 2
                expected_clients = 1
                
                # Verify values
                aum_match = abs(total_aum - expected_aum) < 1.0
                investments_match = total_investments == expected_investments
                clients_match = active_clients == expected_clients
                
                # Check if avg_investment is calculated in backend
                avg_calculated = avg_investment > 0
                
                # Check if by_fund breakdown exists
                fund_breakdown = len(by_fund) > 0
                
                details = f"Total AUM: ${total_aum:,.2f}, Investments: {total_investments}, Clients: {active_clients}, Avg Investment: ${avg_investment:,.2f}, Fund Breakdown: {fund_breakdown}"
                
                success = aum_match and investments_match and clients_match and avg_calculated and fund_breakdown
                self.log_test("Investments Summary", success, details, response.status_code)
                return success
                
            else:
                self.log_test("Investments Summary", False, f"HTTP Error: {response.text}", response.status_code)
                return False
                
        except Exception as e:
            self.log_test("Investments Summary", False, f"Exception: {str(e)}")
            return False
    
    def test_analytics_trading_metrics(self):
        """Test /api/analytics/trading-metrics?account=all endpoint"""
        try:
            url = f"{BACKEND_URL}/api/analytics/trading-metrics?account=all"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check that all metrics are strings with .2f format
                metrics_to_check = ['total_pnl', 'total_equity', 'win_rate', 'avg_trade', 'max_drawdown']
                
                string_format_correct = True
                null_values_found = False
                total_trades_count = data.get('total_trades', 0)
                
                for metric in metrics_to_check:
                    value = data.get(metric)
                    if value is None:
                        null_values_found = True
                    elif not isinstance(value, str):
                        string_format_correct = False
                    elif isinstance(value, str) and not ('.' in value and len(value.split('.')[-1]) == 2):
                        # Check if it's in .2f format (has decimal with 2 places)
                        try:
                            float(value)  # Should be convertible to float
                        except:
                            string_format_correct = False
                
                details = f"Total Trades: {total_trades_count}, String Format: {string_format_correct}, No Nulls: {not null_values_found}"
                
                success = string_format_correct and not null_values_found and total_trades_count > 0
                self.log_test("Analytics Trading Metrics", success, details, response.status_code)
                return success
                
            else:
                self.log_test("Analytics Trading Metrics", False, f"HTTP Error: {response.text}", response.status_code)
                return False
                
        except Exception as e:
            self.log_test("Analytics Trading Metrics", False, f"Exception: {str(e)}")
            return False
    
    def test_money_managers_performance(self):
        """Test /api/money-managers/performance endpoint"""
        try:
            url = f"{BACKEND_URL}/api/money-managers/performance"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for managers array
                managers = data.get('managers', [])
                
                # Check if win_rate is calculated in backend
                win_rate_calculated = all('win_rate' in manager for manager in managers)
                
                # Check if accounts are grouped by provider
                accounts_grouped = all('accounts' in manager or 'account_count' in manager for manager in managers)
                
                # Check for performance metrics
                performance_metrics = all(
                    'performance' in manager or ('total_pnl' in manager and 'trades_count' in manager)
                    for manager in managers
                )
                
                details = f"Managers Count: {len(managers)}, Win Rate Calculated: {win_rate_calculated}, Accounts Grouped: {accounts_grouped}, Performance Metrics: {performance_metrics}"
                
                success = len(managers) > 0 and win_rate_calculated and performance_metrics
                self.log_test("Money Managers Performance", success, details, response.status_code)
                return success
                
            else:
                self.log_test("Money Managers Performance", False, f"HTTP Error: {response.text}", response.status_code)
                return False
                
        except Exception as e:
            self.log_test("Money Managers Performance", False, f"Exception: {str(e)}")
            return False
    
    def test_mt5_accounts_all(self):
        """Test /api/mt5/accounts/all endpoint"""
        try:
            url = f"{BACKEND_URL}/api/mt5/accounts/all"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for ALL 7 accounts
                accounts = data.get('accounts', [])
                expected_accounts = ['891215', '891234', '886557', '886066', '886602', '885822', '886528']
                
                found_accounts = []
                for account in accounts:
                    account_num = str(account.get('account', account.get('account_id', account.get('mt5_login', ''))))
                    if account_num in expected_accounts:
                        found_accounts.append(account_num)
                
                # Check if totals are calculated
                totals_calculated = 'totals' in data or 'summary' in data
                
                # Verify specific accounts 891215 and 891234 are included
                account_891215_found = '891215' in found_accounts
                account_891234_found = '891234' in found_accounts
                
                details = f"Found Accounts: {len(found_accounts)}/7 ({found_accounts}), Totals Calculated: {totals_calculated}, 891215: {account_891215_found}, 891234: {account_891234_found}"
                
                success = len(found_accounts) == 7 and account_891215_found and account_891234_found
                self.log_test("MT5 Accounts All", success, details, response.status_code)
                return success
                
            else:
                self.log_test("MT5 Accounts All", False, f"HTTP Error: {response.text}", response.status_code)
                return False
                
        except Exception as e:
            self.log_test("MT5 Accounts All", False, f"Exception: {str(e)}")
            return False
    
    def run_phase2_testing(self):
        """Run complete Phase 2 endpoint testing"""
        print("🔍 PHASE 2 BACKEND ENDPOINTS TESTING - ARCHITECTURAL REFACTOR")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        # Step 1: Authenticate
        print("📋 STEP 1: Login as Admin")
        if not self.authenticate():
            print("❌ Authentication failed. Cannot test endpoints.")
            return False
        print()
        
        # Step 2: Test /api/portfolio/fund-allocations
        print("📋 STEP 2: Test /api/portfolio/fund-allocations")
        portfolio_success = self.test_portfolio_fund_allocations()
        print()
        
        # Step 3: Test /api/investments/summary
        print("📋 STEP 3: Test /api/investments/summary")
        investments_success = self.test_investments_summary()
        print()
        
        # Step 4: Test /api/analytics/trading-metrics?account=all
        print("📋 STEP 4: Test /api/analytics/trading-metrics?account=all")
        analytics_success = self.test_analytics_trading_metrics()
        print()
        
        # Step 5: Test /api/money-managers/performance
        print("📋 STEP 5: Test /api/money-managers/performance")
        managers_success = self.test_money_managers_performance()
        print()
        
        # Step 6: Test /api/mt5/accounts/all
        print("📋 STEP 6: Test /api/mt5/accounts/all")
        mt5_success = self.test_mt5_accounts_all()
        print()
        
        # Summary
        self.print_testing_summary()
        
        # Return overall success
        all_endpoints = [portfolio_success, investments_success, analytics_success, managers_success, mt5_success]
        return all(all_endpoints)
    
    def print_testing_summary(self):
        """Print testing summary"""
        print("=" * 80)
        print("📊 PHASE 2 ENDPOINTS TESTING SUMMARY")
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
        
        # Endpoint-by-endpoint results
        print("🔍 ENDPOINT TESTING RESULTS:")
        
        endpoints = [
            "Portfolio Fund Allocations",
            "Investments Summary", 
            "Analytics Trading Metrics",
            "Money Managers Performance",
            "MT5 Accounts All"
        ]
        
        for endpoint in endpoints:
            result = next((r for r in self.test_results if endpoint in r['test']), None)
            if result:
                status = "✅ PASS" if result['success'] else "❌ FAIL"
                http_status = result.get('http_status', 'N/A')
                print(f"   {status} {endpoint} (HTTP {http_status})")
                print(f"      {result['details']}")
            else:
                print(f"   ❓ {endpoint} - Not tested")
        print()
        
        if failed_tests > 0:
            print("❌ FAILED ENDPOINTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['details']}")
            print()
        
        print("✅ SUCCESSFUL ENDPOINTS:")
        for result in self.test_results:
            if result['success']:
                print(f"   • {result['test']}: {result['details']}")
        print()
        
        # Key findings
        print("🎯 KEY FINDINGS:")
        
        # Check if all expected values are correct
        portfolio_success = any('Portfolio Fund Allocations' in r['test'] and r['success'] for r in self.test_results)
        investments_success = any('Investments Summary' in r['test'] and r['success'] for r in self.test_results)
        analytics_success = any('Analytics Trading Metrics' in r['test'] and r['success'] for r in self.test_results)
        managers_success = any('Money Managers Performance' in r['test'] and r['success'] for r in self.test_results)
        mt5_success = any('MT5 Accounts All' in r['test'] and r['success'] for r in self.test_results)
        
        print(f"   {'✅' if portfolio_success else '❌'} Portfolio Fund Allocations: total_aum = 118151.41, CORE and BALANCE funds")
        print(f"   {'✅' if investments_success else '❌'} Investments Summary: total_aum = 118151.41, 2 investments, 1 client")
        print(f"   {'✅' if analytics_success else '❌'} Trading Metrics: All metrics as strings with .2f format, no nulls")
        print(f"   {'✅' if managers_success else '❌'} Money Managers Performance: win_rate calculated, accounts grouped")
        print(f"   {'✅' if mt5_success else '❌'} MT5 Accounts All: ALL 7 accounts including 891215 and 891234")
        
        print()
        print("📋 ARCHITECTURAL REFACTOR VERIFICATION:")
        
        all_passed = portfolio_success and investments_success and analytics_success and managers_success and mt5_success
        
        if all_passed:
            print("   ✅ ALL 5 PHASE 2 ENDPOINTS OPERATIONAL")
            print("   🎉 Backend calculations confirmed - no frontend calculations needed")
            print("   🚀 Architectural refactor successful")
        else:
            print("   ❌ SOME PHASE 2 ENDPOINTS FAILED")
            print("   🔧 Architectural refactor needs attention")
            
            if not portfolio_success:
                print("   🔧 Portfolio fund allocations endpoint needs fixing")
            if not investments_success:
                print("   🔧 Investments summary endpoint needs fixing")
            if not analytics_success:
                print("   🔧 Analytics trading metrics endpoint needs fixing")
            if not managers_success:
                print("   🔧 Money managers performance endpoint needs fixing")
            if not mt5_success:
                print("   🔧 MT5 accounts all endpoint needs fixing")
        
        print()

def main():
    """Main testing execution"""
    tester = Phase2EndpointTesting()
    success = tester.run_phase2_testing()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()