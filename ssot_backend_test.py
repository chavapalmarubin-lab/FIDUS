#!/usr/bin/env python3
"""
COMPREHENSIVE SSOT ARCHITECTURE TESTING
December 19, 2025

Testing all new SSOT (Single Source of Truth) endpoints for the comprehensive architecture.
All endpoints query the single mt5_accounts collection (master source).

Test Coverage:
1. Health Check: GET /api/v2/health/ssot
2. Accounts Management: GET /api/v2/accounts/all  
3. Fund Portfolio: GET /api/v2/derived/fund-portfolio
4. Money Managers: GET /api/v2/derived/money-managers
5. Cash Flow: GET /api/v2/derived/cash-flow
6. Trading Analytics: GET /api/v2/derived/trading-analytics
7. Update Account Assignment: PATCH /api/v2/accounts/885822/assign

Expected Results:
- 15 total accounts with required fields
- Platforms: MT4, MT5
- Brokers: MEXAtlantic, LUCRUM Capital
- Funds: CORE, BALANCE, SEPARATION
- SSOT violation check: money_managers should NOT have assigned_accounts field
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any

# Configuration
BASE_URL = "https://data-integrity-13.preview.emergentagent.com"
TIMEOUT = 30

class SSotArchitectureTest:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.session.timeout = TIMEOUT
        self.results = []
        self.start_time = time.time()
        
    def log_result(self, test_name: str, success: bool, details: str, response_time: float = 0):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "response_time_ms": round(response_time * 1000, 2),
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        print(f"{status} {test_name}: {details}")
        if response_time > 0:
            print(f"   Response time: {response_time * 1000:.2f}ms")
        
    def test_health_check(self):
        """Test SSOT Health Check endpoint"""
        print("\n🔍 Testing SSOT Health Check...")
        
        try:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/api/v2/health/ssot")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Check expected structure
                expected_keys = ['success', 'ssot_architecture_status', 'validation']
                missing_keys = [key for key in expected_keys if key not in data]
                
                if missing_keys:
                    self.log_result("Health Check Structure", False, 
                                  f"Missing keys: {missing_keys}", response_time)
                    return False
                
                # Check total accounts
                total_accounts = data['validation']['total_accounts']
                accounts_valid = data['validation']['accounts_valid']
                
                if total_accounts == 15 and accounts_valid:
                    self.log_result("Health Check - Account Count", True, 
                                  f"Total accounts: {total_accounts} ✓", response_time)
                else:
                    self.log_result("Health Check - Account Count", False, 
                                  f"Expected 15 accounts, got {total_accounts}", response_time)
                
                # Check SSOT violation
                ssot_violation = data['validation']['ssot_violation']
                if not ssot_violation['violated']:
                    self.log_result("Health Check - SSOT Compliance", True, 
                                  "No SSOT violations detected ✓", response_time)
                else:
                    self.log_result("Health Check - SSOT Compliance", False, 
                                  f"SSOT violation: {ssot_violation['message']}", response_time)
                
                # Check data completeness
                completeness = data['validation']['data_completeness']
                platforms = completeness['platforms']
                brokers = completeness['brokers']
                
                expected_platforms = ['MT4', 'MT5']
                expected_brokers = ['MEXAtlantic', 'LUCRUM Capital']
                
                platforms_ok = all(p in platforms for p in expected_platforms)
                brokers_ok = all(b in brokers for b in expected_brokers)
                
                if platforms_ok and brokers_ok:
                    self.log_result("Health Check - Data Completeness", True, 
                                  f"Platforms: {platforms}, Brokers: {brokers} ✓", response_time)
                else:
                    self.log_result("Health Check - Data Completeness", False, 
                                  f"Missing platforms/brokers. Got: {platforms}, {brokers}", response_time)
                
                return True
                
            else:
                self.log_result("Health Check", False, 
                              f"HTTP {response.status_code}: {response.text}", response_time)
                return False
                
        except Exception as e:
            self.log_result("Health Check", False, f"Exception: {str(e)}")
            return False
    
    def test_accounts_all(self):
        """Test Accounts Management endpoint"""
        print("\n🔍 Testing Accounts Management...")
        
        try:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/api/v2/accounts/all")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Check structure
                if not all(key in data for key in ['success', 'accounts', 'summary']):
                    self.log_result("Accounts All - Structure", False, 
                                  "Missing required keys", response_time)
                    return False
                
                accounts = data['accounts']
                summary = data['summary']
                
                # Check account count
                if len(accounts) == 15:
                    self.log_result("Accounts All - Count", True, 
                                  f"15 accounts returned ✓", response_time)
                else:
                    self.log_result("Accounts All - Count", False, 
                                  f"Expected 15 accounts, got {len(accounts)}", response_time)
                
                # Check required fields in accounts
                required_fields = ['account', 'platform', 'broker', 'fund_type', 'manager_name', 'status']
                accounts_with_all_fields = 0
                
                for acc in accounts:
                    if all(field in acc and acc[field] for field in required_fields):
                        accounts_with_all_fields += 1
                
                if accounts_with_all_fields == len(accounts):
                    self.log_result("Accounts All - Required Fields", True, 
                                  f"All {len(accounts)} accounts have required fields ✓", response_time)
                else:
                    self.log_result("Accounts All - Required Fields", False, 
                                  f"Only {accounts_with_all_fields}/{len(accounts)} accounts have all required fields", response_time)
                
                # Check summary data
                expected_summary_keys = ['total_accounts', 'active_accounts', 'platforms', 'brokers']
                summary_ok = all(key in summary for key in expected_summary_keys)
                
                if summary_ok and summary['total_accounts'] == 15:
                    active_count = summary['active_accounts']
                    self.log_result("Accounts All - Summary", True, 
                                  f"Summary complete: {summary['total_accounts']} total, {active_count} active ✓", response_time)
                else:
                    self.log_result("Accounts All - Summary", False, 
                                  f"Summary incomplete or wrong total count", response_time)
                
                return True
                
            else:
                self.log_result("Accounts All", False, 
                              f"HTTP {response.status_code}: {response.text}", response_time)
                return False
                
        except Exception as e:
            self.log_result("Accounts All", False, f"Exception: {str(e)}")
            return False
    
    def test_fund_portfolio(self):
        """Test Fund Portfolio endpoint"""
        print("\n🔍 Testing Fund Portfolio...")
        
        try:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/api/v2/derived/fund-portfolio")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Check structure
                if not all(key in data for key in ['success', 'funds', 'summary']):
                    self.log_result("Fund Portfolio - Structure", False, 
                                  "Missing required keys", response_time)
                    return False
                
                funds = data['funds']
                summary = data['summary']
                
                # Check expected funds
                expected_funds = ['CORE', 'BALANCE', 'SEPARATION']
                found_funds = list(funds.keys())
                
                core_found = 'CORE' in found_funds
                balance_found = 'BALANCE' in found_funds
                separation_found = 'SEPARATION' in found_funds
                
                if core_found and balance_found:
                    self.log_result("Fund Portfolio - Fund Types", True, 
                                  f"Found expected funds: {found_funds} ✓", response_time)
                else:
                    self.log_result("Fund Portfolio - Fund Types", False, 
                                  f"Missing expected funds. Found: {found_funds}", response_time)
                
                # Check CORE fund details (should have 2 accounts: 885822, 897590)
                if 'CORE' in funds:
                    core_fund = funds['CORE']
                    core_accounts = [acc['account'] for acc in core_fund.get('accounts', [])]
                    
                    if 885822 in core_accounts and 897590 in core_accounts:
                        self.log_result("Fund Portfolio - CORE Fund", True, 
                                      f"CORE fund has expected accounts: {core_accounts} ✓", response_time)
                    else:
                        self.log_result("Fund Portfolio - CORE Fund", False, 
                                      f"CORE fund missing expected accounts. Found: {core_accounts}", response_time)
                
                # Check BALANCE fund details (should have 7 accounts)
                if 'BALANCE' in funds:
                    balance_fund = funds['BALANCE']
                    balance_account_count = balance_fund.get('account_count', 0)
                    
                    if balance_account_count == 7:
                        self.log_result("Fund Portfolio - BALANCE Fund", True, 
                                      f"BALANCE fund has 7 accounts ✓", response_time)
                    else:
                        self.log_result("Fund Portfolio - BALANCE Fund", False, 
                                      f"BALANCE fund expected 7 accounts, got {balance_account_count}", response_time)
                
                # Check SEPARATION fund details (should have 4 accounts)
                if 'SEPARATION' in funds:
                    separation_fund = funds['SEPARATION']
                    separation_account_count = separation_fund.get('account_count', 0)
                    
                    if separation_account_count == 4:
                        self.log_result("Fund Portfolio - SEPARATION Fund", True, 
                                      f"SEPARATION fund has 4 accounts ✓", response_time)
                    else:
                        self.log_result("Fund Portfolio - SEPARATION Fund", False, 
                                      f"SEPARATION fund expected 4 accounts, got {separation_account_count}", response_time)
                
                return True
                
            else:
                self.log_result("Fund Portfolio", False, 
                              f"HTTP {response.status_code}: {response.text}", response_time)
                return False
                
        except Exception as e:
            self.log_result("Fund Portfolio", False, f"Exception: {str(e)}")
            return False
    
    def test_money_managers(self):
        """Test Money Managers endpoint"""
        print("\n🔍 Testing Money Managers...")
        
        try:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/api/v2/derived/money-managers")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Check structure
                if not all(key in data for key in ['success', 'managers', 'summary']):
                    self.log_result("Money Managers - Structure", False, 
                                  "Missing required keys", response_time)
                    return False
                
                managers = data['managers']
                summary = data['summary']
                
                # Check manager count (should be 9 managers total)
                if summary.get('total_managers') == 9:
                    self.log_result("Money Managers - Count", True, 
                                  f"9 managers found ✓", response_time)
                else:
                    self.log_result("Money Managers - Count", False, 
                                  f"Expected 9 managers, got {summary.get('total_managers')}", response_time)
                
                # Check expected manager names
                expected_managers = ['CP Strategy', 'TradingHub Gold', 'UNO14 Manager']
                found_managers = list(managers.keys())
                
                expected_found = [mgr for mgr in expected_managers if mgr in found_managers]
                
                if len(expected_found) >= 2:  # At least 2 of the expected managers
                    self.log_result("Money Managers - Expected Names", True, 
                                  f"Found expected managers: {expected_found} ✓", response_time)
                else:
                    self.log_result("Money Managers - Expected Names", False, 
                                  f"Missing expected managers. Found: {found_managers}", response_time)
                
                # Check manager data structure
                manager_data_ok = True
                for mgr_name, mgr_data in managers.items():
                    required_fields = ['manager_name', 'account_count', 'total_balance', 'execution_method']
                    if not all(field in mgr_data for field in required_fields):
                        manager_data_ok = False
                        break
                
                if manager_data_ok:
                    self.log_result("Money Managers - Data Structure", True, 
                                  "All managers have required fields ✓", response_time)
                else:
                    self.log_result("Money Managers - Data Structure", False, 
                                  "Some managers missing required fields", response_time)
                
                return True
                
            else:
                self.log_result("Money Managers", False, 
                              f"HTTP {response.status_code}: {response.text}", response_time)
                return False
                
        except Exception as e:
            self.log_result("Money Managers", False, f"Exception: {str(e)}")
            return False
    
    def test_cash_flow(self):
        """Test Cash Flow endpoint"""
        print("\n🔍 Testing Cash Flow...")
        
        try:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/api/v2/derived/cash-flow")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Check structure
                if not all(key in data for key in ['success', 'accounts', 'summary']):
                    self.log_result("Cash Flow - Structure", False, 
                                  "Missing required keys", response_time)
                    return False
                
                accounts = data['accounts']
                summary = data['summary']
                
                # Check active accounts (should be 13)
                if summary.get('total_accounts') == 13:
                    self.log_result("Cash Flow - Active Accounts", True, 
                                  f"13 active accounts found ✓", response_time)
                else:
                    self.log_result("Cash Flow - Active Accounts", False, 
                                  f"Expected 13 active accounts, got {summary.get('total_accounts')}", response_time)
                
                # Check summary has financial data
                required_summary_fields = ['total_balance', 'total_equity', 'total_pnl']
                summary_complete = all(field in summary for field in required_summary_fields)
                
                if summary_complete:
                    total_balance = summary['total_balance']
                    total_equity = summary['total_equity']
                    total_pnl = summary['total_pnl']
                    
                    self.log_result("Cash Flow - Summary Data", True, 
                                  f"Balance: ${total_balance:,.2f}, Equity: ${total_equity:,.2f}, P&L: ${total_pnl:,.2f} ✓", response_time)
                else:
                    self.log_result("Cash Flow - Summary Data", False, 
                                  "Summary missing required financial fields", response_time)
                
                return True
                
            else:
                self.log_result("Cash Flow", False, 
                              f"HTTP {response.status_code}: {response.text}", response_time)
                return False
                
        except Exception as e:
            self.log_result("Cash Flow", False, f"Exception: {str(e)}")
            return False
    
    def test_trading_analytics(self):
        """Test Trading Analytics endpoint"""
        print("\n🔍 Testing Trading Analytics...")
        
        try:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/api/v2/derived/trading-analytics")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Check structure
                if not all(key in data for key in ['success', 'analytics']):
                    self.log_result("Trading Analytics - Structure", False, 
                                  "Missing required keys", response_time)
                    return False
                
                analytics = data['analytics']
                
                # Check analytics structure
                required_sections = ['overview', 'by_fund', 'by_manager']
                sections_ok = all(section in analytics for section in required_sections)
                
                if sections_ok:
                    self.log_result("Trading Analytics - Structure", True, 
                                  "All required analytics sections present ✓", response_time)
                else:
                    self.log_result("Trading Analytics - Structure", False, 
                                  f"Missing analytics sections. Found: {list(analytics.keys())}", response_time)
                
                # Check overview data
                overview = analytics.get('overview', {})
                overview_fields = ['total_accounts', 'total_balance', 'total_equity', 'overall_pnl']
                overview_complete = all(field in overview for field in overview_fields)
                
                if overview_complete:
                    total_accounts = overview['total_accounts']
                    overall_pnl = overview['overall_pnl']
                    
                    self.log_result("Trading Analytics - Overview", True, 
                                  f"Overview complete: {total_accounts} accounts, P&L: ${overall_pnl:,.2f} ✓", response_time)
                else:
                    self.log_result("Trading Analytics - Overview", False, 
                                  "Overview missing required fields", response_time)
                
                # Check fund and manager breakdowns
                by_fund = analytics.get('by_fund', {})
                by_manager = analytics.get('by_manager', {})
                
                if len(by_fund) > 0 and len(by_manager) > 0:
                    self.log_result("Trading Analytics - Breakdowns", True, 
                                  f"Fund breakdown: {len(by_fund)} funds, Manager breakdown: {len(by_manager)} managers ✓", response_time)
                else:
                    self.log_result("Trading Analytics - Breakdowns", False, 
                                  "Missing fund or manager breakdowns", response_time)
                
                return True
                
            else:
                self.log_result("Trading Analytics", False, 
                              f"HTTP {response.status_code}: {response.text}", response_time)
                return False
                
        except Exception as e:
            self.log_result("Trading Analytics", False, f"Exception: {str(e)}")
            return False
    
    def test_account_assignment_update(self):
        """Test Account Assignment Update endpoint"""
        print("\n🔍 Testing Account Assignment Update...")
        
        try:
            # Test updating account 885822
            account_number = 885822
            update_data = {
                "fund_type": "BALANCE",
                "manager_name": "UNO14 Manager", 
                "status": "active"
            }
            
            start_time = time.time()
            response = self.session.patch(
                f"{self.base_url}/api/v2/accounts/{account_number}/assign",
                json=update_data
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                if not all(key in data for key in ['success', 'message', 'account', 'updated_fields']):
                    self.log_result("Account Assignment - Structure", False, 
                                  "Missing required response keys", response_time)
                    return False
                
                # Check if update was successful
                if data['success']:
                    updated_account = data['account']
                    updated_fields = data['updated_fields']
                    
                    # Verify the updates were applied
                    updates_applied = all(
                        updated_account.get(field) == update_data[field] 
                        for field in update_data.keys()
                    )
                    
                    if updates_applied:
                        self.log_result("Account Assignment - Update Applied", True, 
                                      f"Account {account_number} updated successfully: {updated_fields} ✓", response_time)
                    else:
                        self.log_result("Account Assignment - Update Applied", False, 
                                      f"Updates not properly applied to account {account_number}", response_time)
                    
                    # Verify changes appear in accounts/all endpoint
                    time.sleep(1)  # Brief pause to ensure consistency
                    verify_response = self.session.get(f"{self.base_url}/api/v2/accounts/all")
                    
                    if verify_response.status_code == 200:
                        verify_data = verify_response.json()
                        accounts = verify_data.get('accounts', [])
                        
                        updated_account_in_list = None
                        for acc in accounts:
                            if acc.get('account') == account_number:
                                updated_account_in_list = acc
                                break
                        
                        if updated_account_in_list:
                            verification_ok = all(
                                updated_account_in_list.get(field) == update_data[field]
                                for field in update_data.keys()
                            )
                            
                            if verification_ok:
                                self.log_result("Account Assignment - Verification", True, 
                                              f"Changes verified in accounts/all endpoint ✓", response_time)
                            else:
                                self.log_result("Account Assignment - Verification", False, 
                                              f"Changes not reflected in accounts/all endpoint", response_time)
                        else:
                            self.log_result("Account Assignment - Verification", False, 
                                          f"Account {account_number} not found in accounts/all", response_time)
                    
                    return True
                else:
                    self.log_result("Account Assignment", False, 
                                  f"Update failed: {data.get('message', 'Unknown error')}", response_time)
                    return False
                
            else:
                self.log_result("Account Assignment", False, 
                              f"HTTP {response.status_code}: {response.text}", response_time)
                return False
                
        except Exception as e:
            self.log_result("Account Assignment", False, f"Exception: {str(e)}")
            return False
    
    def test_error_handling(self):
        """Test error handling scenarios"""
        print("\n🔍 Testing Error Handling...")
        
        # Test invalid account number
        try:
            start_time = time.time()
            response = self.session.patch(
                f"{self.base_url}/api/v2/accounts/999999/assign",
                json={"fund_type": "CORE"}
            )
            response_time = time.time() - start_time
            
            if response.status_code == 404:
                self.log_result("Error Handling - Invalid Account", True, 
                              "404 returned for invalid account number ✓", response_time)
            else:
                self.log_result("Error Handling - Invalid Account", False, 
                              f"Expected 404, got {response.status_code}", response_time)
        except Exception as e:
            self.log_result("Error Handling - Invalid Account", False, f"Exception: {str(e)}")
        
        # Test invalid fund type
        try:
            start_time = time.time()
            response = self.session.patch(
                f"{self.base_url}/api/v2/accounts/885822/assign",
                json={"fund_type": "INVALID"}
            )
            response_time = time.time() - start_time
            
            if response.status_code in [400, 422]:  # Bad request or validation error
                self.log_result("Error Handling - Invalid Fund Type", True, 
                              f"Error returned for invalid fund type ✓", response_time)
            else:
                self.log_result("Error Handling - Invalid Fund Type", False, 
                              f"Expected 400/422, got {response.status_code}", response_time)
        except Exception as e:
            self.log_result("Error Handling - Invalid Fund Type", False, f"Exception: {str(e)}")
        
        # Test missing required fields
        try:
            start_time = time.time()
            response = self.session.patch(
                f"{self.base_url}/api/v2/accounts/885822/assign",
                json={}
            )
            response_time = time.time() - start_time
            
            if response.status_code == 400:
                self.log_result("Error Handling - Missing Fields", True, 
                              "400 returned for missing fields ✓", response_time)
            else:
                self.log_result("Error Handling - Missing Fields", False, 
                              f"Expected 400, got {response.status_code}", response_time)
        except Exception as e:
            self.log_result("Error Handling - Missing Fields", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all SSOT architecture tests"""
        print("🚀 COMPREHENSIVE SSOT ARCHITECTURE TESTING")
        print("=" * 60)
        print(f"Base URL: {self.base_url}")
        print(f"Timeout: {TIMEOUT}s")
        print(f"Start time: {datetime.now().isoformat()}")
        print("=" * 60)
        
        # Run all tests
        tests = [
            self.test_health_check,
            self.test_accounts_all,
            self.test_fund_portfolio,
            self.test_money_managers,
            self.test_cash_flow,
            self.test_trading_analytics,
            self.test_account_assignment_update,
            self.test_error_handling
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                test_name = test.__name__.replace('test_', '').replace('_', ' ').title()
                self.log_result(test_name, False, f"Test execution failed: {str(e)}")
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        total_time = time.time() - self.start_time
        
        print("\n" + "=" * 60)
        print("📊 SSOT ARCHITECTURE TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Total Time: {total_time:.2f}s")
        print(f"End time: {datetime.now().isoformat()}")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.results:
                if not result['success']:
                    print(f"  • {result['test']}: {result['details']}")
        
        print("\n✅ PASSED TESTS:")
        for result in self.results:
            if result['success']:
                print(f"  • {result['test']}: {result['details']}")
        
        # Response time analysis
        response_times = [r['response_time_ms'] for r in self.results if r['response_time_ms'] > 0]
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            print(f"\n⏱️  PERFORMANCE:")
            print(f"  Average Response Time: {avg_response_time:.2f}ms")
            print(f"  Max Response Time: {max_response_time:.2f}ms")
        
        print("=" * 60)
        
        # Save detailed results to file
        with open('/app/ssot_test_results.json', 'w') as f:
            json.dump({
                'summary': {
                    'total_tests': total_tests,
                    'passed': passed_tests,
                    'failed': failed_tests,
                    'success_rate': success_rate,
                    'total_time': total_time,
                    'timestamp': datetime.now().isoformat()
                },
                'results': self.results
            }, f, indent=2)
        
        print(f"📄 Detailed results saved to: /app/ssot_test_results.json")


if __name__ == "__main__":
    tester = SSotArchitectureTest()
    tester.run_all_tests()