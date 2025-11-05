#!/usr/bin/env python3
"""
RENDER DEPLOYMENT BACKEND TESTING - ALL 4 PRIORITY ISSUES + DEPLOYMENT
Test Suite for MT5 Bridge System Production Deployment

Backend URL: https://fidus-integration-1.preview.emergentagent.com/api
Auth: Admin token (username: admin, password: password123)

Test Coverage:
1. Fund Portfolio - FIDUS Monthly Profit (Rebates)
2. Cash Flow - Fund Obligations  
3. Trading Analytics - CORE Fund Account Count
4. Money Managers - Real Managers Only
5. Deployment Health Check
6. MongoDB Atlas Trade Data Verification
"""

import requests
import json
import sys
from datetime import datetime
import time

class RenderDeploymentTester:
    def __init__(self):
        self.base_url = "https://fidus-integration-1.preview.emergentagent.com/api"
        self.admin_token = None
        self.test_results = []
        self.success_count = 0
        self.total_tests = 0
        
    def log_test(self, test_name, success, details, expected=None, actual=None):
        """Log test result with detailed information"""
        self.total_tests += 1
        if success:
            self.success_count += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
            
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "expected": expected,
            "actual": actual,
            "timestamp": datetime.now().isoformat()
        }
        
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        print(f"   Details: {details}")
        if expected and actual:
            print(f"   Expected: {expected}")
            print(f"   Actual: {actual}")
        print()
        
    def authenticate_admin(self):
        """Authenticate as admin user and get JWT token"""
        try:
            print("🔐 AUTHENTICATING AS ADMIN...")
            
            login_data = {
                "username": "admin",
                "password": "password123",
                "user_type": "admin"
            }
            
            response = requests.post(
                f"{self.base_url}/auth/login",
                json=login_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token')
                
                if self.admin_token:
                    self.log_test(
                        "Admin Authentication",
                        True,
                        f"Successfully authenticated as admin, token received"
                    )
                    return True
                else:
                    self.log_test(
                        "Admin Authentication", 
                        False,
                        "Login successful but no token in response"
                    )
                    return False
            else:
                self.log_test(
                    "Admin Authentication",
                    False, 
                    f"Login failed with status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Admin Authentication",
                False,
                f"Authentication error: {str(e)}"
            )
            return False
    
    def get_headers(self):
        """Get headers with admin authorization"""
        return {
            "Authorization": f"Bearer {self.admin_token}",
            "Content-Type": "application/json"
        }
    
    def test_health_endpoint(self):
        """Test 5: Deployment Health Check"""
        try:
            print("🏥 TESTING DEPLOYMENT HEALTH CHECK...")
            
            response = requests.get(
                f"{self.base_url}/health",
                timeout=5
            )
            
            if response.status_code == 200:
                self.log_test(
                    "Deployment Health Check",
                    True,
                    f"Health endpoint responding correctly (HTTP 200)",
                    "HTTP 200 with server responding",
                    f"HTTP {response.status_code}"
                )
                return True
            else:
                self.log_test(
                    "Deployment Health Check",
                    False,
                    f"Health endpoint returned HTTP {response.status_code}",
                    "HTTP 200",
                    f"HTTP {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Deployment Health Check",
                False,
                f"Health endpoint error: {str(e)}"
            )
            return False
    
    def test_fund_portfolio_rebates(self):
        """Test 1: Fund Portfolio - FIDUS Monthly Profit (Rebates)"""
        try:
            print("💰 TESTING FUND PORTFOLIO REBATES...")
            
            response = requests.get(
                f"{self.base_url}/fund-portfolio/overview",
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for total_rebates field in CORE and BALANCE funds
                rebates_found = False
                core_rebates = None
                balance_rebates = None
                
                if isinstance(data, list):
                    for fund in data:
                        if fund.get('fund_code') == 'CORE':
                            core_rebates = fund.get('total_rebates')
                        elif fund.get('fund_code') == 'BALANCE':
                            balance_rebates = fund.get('total_rebates')
                
                # Check if rebates are showing actual values (not $0.00)
                if core_rebates is not None or balance_rebates is not None:
                    if (core_rebates and core_rebates != 0) or (balance_rebates and balance_rebates != 0):
                        rebates_found = True
                        self.log_test(
                            "Fund Portfolio Rebates",
                            True,
                            f"Rebates showing actual values - CORE: ${core_rebates}, BALANCE: ${balance_rebates}",
                            "Should show actual rebate values (NOT $0.00)",
                            f"CORE: ${core_rebates}, BALANCE: ${balance_rebates}"
                        )
                    else:
                        self.log_test(
                            "Fund Portfolio Rebates",
                            False,
                            f"Rebates showing zero values - CORE: ${core_rebates}, BALANCE: ${balance_rebates}",
                            "Should show actual rebate values (~$5,774.83 from 22,491 trades)",
                            f"CORE: ${core_rebates}, BALANCE: ${balance_rebates}"
                        )
                else:
                    self.log_test(
                        "Fund Portfolio Rebates",
                        False,
                        "No total_rebates field found in fund data",
                        "total_rebates field present with actual values",
                        "total_rebates field missing"
                    )
                
                return rebates_found
            else:
                self.log_test(
                    "Fund Portfolio Rebates",
                    False,
                    f"API returned HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Fund Portfolio Rebates",
                False,
                f"Fund portfolio API error: {str(e)}"
            )
            return False
    
    def test_cash_flow_obligations(self):
        """Test 2: Cash Flow - Fund Obligations"""
        try:
            print("💸 TESTING CASH FLOW OBLIGATIONS...")
            
            response = requests.get(
                f"{self.base_url}/admin/cashflow/overview?timeframe=3months&fund=all",
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for obligation fields
                client_obligations = data.get('total_client_obligations')
                fund_outflows = data.get('total_fund_outflows')
                
                obligations_working = False
                if client_obligations is not None and fund_outflows is not None:
                    obligations_working = True
                    self.log_test(
                        "Cash Flow Obligations",
                        True,
                        f"Obligation calculations working - Client: ${client_obligations}, Outflows: ${fund_outflows}",
                        "Should show proper obligation calculations",
                        f"Client Obligations: ${client_obligations}, Fund Outflows: ${fund_outflows}"
                    )
                else:
                    self.log_test(
                        "Cash Flow Obligations",
                        False,
                        "Missing obligation calculation fields",
                        "total_client_obligations and total_fund_outflows fields",
                        f"Client Obligations: {client_obligations}, Fund Outflows: {fund_outflows}"
                    )
                
                return obligations_working
            else:
                self.log_test(
                    "Cash Flow Obligations",
                    False,
                    f"Cash flow API returned HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Cash Flow Obligations",
                False,
                f"Cash flow API error: {str(e)}"
            )
            return False
    
    def test_trading_analytics_core_accounts(self):
        """Test 3: Trading Analytics - CORE Fund Account Count"""
        try:
            print("📊 TESTING TRADING ANALYTICS CORE FUND ACCOUNTS...")
            
            response = requests.get(
                f"{self.base_url}/admin/fund-performance/dashboard",
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for CORE fund account count
                core_account_count = None
                
                # Look for by_fund.CORE.account_count structure
                by_fund = data.get('by_fund', {})
                if 'CORE' in by_fund:
                    core_account_count = by_fund['CORE'].get('account_count')
                
                if core_account_count == 2:
                    self.log_test(
                        "Trading Analytics CORE Accounts",
                        True,
                        f"CORE fund shows correct account count: {core_account_count}",
                        "Should be 2 (accounts 885822 and 891234)",
                        f"{core_account_count} accounts"
                    )
                    return True
                else:
                    self.log_test(
                        "Trading Analytics CORE Accounts",
                        False,
                        f"CORE fund account count incorrect: {core_account_count}",
                        "Should be 2 (accounts 885822 and 891234)",
                        f"{core_account_count} accounts"
                    )
                    return False
            else:
                self.log_test(
                    "Trading Analytics CORE Accounts",
                    False,
                    f"Fund performance API returned HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Trading Analytics CORE Accounts",
                False,
                f"Trading analytics API error: {str(e)}"
            )
            return False
    
    def test_money_managers_real_only(self):
        """Test 4: Money Managers - Real Managers Only"""
        try:
            print("👥 TESTING MONEY MANAGERS (REAL MANAGERS ONLY)...")
            
            response = requests.get(
                f"{self.base_url}/admin/trading-analytics/managers",
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Expected managers: CP Strategy, TradingHub Gold, GoldenTrade, UNO14
                expected_managers = {"CP Strategy", "TradingHub Gold", "GoldenTrade", "UNO14"}
                excluded_managers = {"Manual Trading", "Manager None"}
                
                managers_found = set()
                excluded_found = set()
                
                if isinstance(data, list):
                    for manager in data:
                        manager_name = manager.get('manager_name', '')
                        managers_found.add(manager_name)
                        
                        if manager_name in excluded_managers:
                            excluded_found.add(manager_name)
                
                # Check if we have exactly 4 real managers and no excluded ones
                real_managers_count = len(managers_found & expected_managers)
                has_excluded = len(excluded_found) > 0
                
                if real_managers_count == 4 and not has_excluded:
                    self.log_test(
                        "Money Managers Real Only",
                        True,
                        f"Exactly 4 real managers found: {managers_found & expected_managers}",
                        "EXACTLY 4 managers (CP Strategy, TradingHub Gold, GoldenTrade, UNO14)",
                        f"{real_managers_count} real managers, no excluded managers"
                    )
                    return True
                else:
                    issues = []
                    if real_managers_count != 4:
                        issues.append(f"Found {real_managers_count}/4 expected managers")
                    if has_excluded:
                        issues.append(f"Found excluded managers: {excluded_found}")
                    
                    self.log_test(
                        "Money Managers Real Only",
                        False,
                        f"Manager list issues: {', '.join(issues)}",
                        "EXACTLY 4 managers (CP Strategy, TradingHub Gold, GoldenTrade, UNO14)",
                        f"Found managers: {managers_found}"
                    )
                    return False
            else:
                self.log_test(
                    "Money Managers Real Only",
                    False,
                    f"Money managers API returned HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Money Managers Real Only",
                False,
                f"Money managers API error: {str(e)}"
            )
            return False
    
    def test_mongodb_trade_data(self):
        """Test 6: MongoDB Atlas Trade Data Verification"""
        try:
            print("🗄️ TESTING MONGODB ATLAS TRADE DATA...")
            
            # Test MT5 accounts endpoint to verify trade data is syncing
            response = requests.get(
                f"{self.base_url}/mt5/admin/accounts",
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if we have accounts with trade data
                accounts_with_data = 0
                total_deals = 0
                
                if isinstance(data, list):
                    for account in data:
                        if account.get('profit') is not None or account.get('equity') is not None:
                            accounts_with_data += 1
                        
                        # Look for deal/trade count indicators
                        deals = account.get('deals_count', 0) or account.get('total_deals', 0)
                        total_deals += deals
                
                if accounts_with_data >= 5 and total_deals > 1000:
                    self.log_test(
                        "MongoDB Trade Data Sync",
                        True,
                        f"Trade data syncing correctly - {accounts_with_data} accounts with data, {total_deals} total deals",
                        "22,491+ deals in MongoDB Atlas without duplicate key errors",
                        f"{accounts_with_data} accounts with trade data, {total_deals} deals"
                    )
                    return True
                else:
                    self.log_test(
                        "MongoDB Trade Data Sync",
                        False,
                        f"Insufficient trade data - {accounts_with_data} accounts with data, {total_deals} total deals",
                        "22,491+ deals in MongoDB Atlas",
                        f"{accounts_with_data} accounts with data, {total_deals} deals"
                    )
                    return False
            else:
                self.log_test(
                    "MongoDB Trade Data Sync",
                    False,
                    f"MT5 accounts API returned HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "MongoDB Trade Data Sync",
                False,
                f"MongoDB trade data verification error: {str(e)}"
            )
            return False
    
    def test_response_times(self):
        """Test response times for all critical endpoints"""
        try:
            print("⏱️ TESTING API RESPONSE TIMES...")
            
            endpoints = [
                "/health",
                "/fund-portfolio/overview", 
                "/admin/cashflow/overview",
                "/admin/fund-performance/dashboard",
                "/admin/trading-analytics/managers"
            ]
            
            slow_endpoints = []
            
            for endpoint in endpoints:
                start_time = time.time()
                
                if endpoint == "/health":
                    response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                else:
                    response = requests.get(f"{self.base_url}{endpoint}", headers=self.get_headers(), timeout=10)
                
                response_time = time.time() - start_time
                
                if response_time > 5.0:
                    slow_endpoints.append(f"{endpoint} ({response_time:.2f}s)")
            
            if len(slow_endpoints) == 0:
                self.log_test(
                    "API Response Times",
                    True,
                    "All endpoints respond within 5 seconds",
                    "Backend responds within 5 seconds",
                    "All endpoints < 5s"
                )
                return True
            else:
                self.log_test(
                    "API Response Times",
                    False,
                    f"Slow endpoints detected: {', '.join(slow_endpoints)}",
                    "Backend responds within 5 seconds",
                    f"Slow endpoints: {slow_endpoints}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "API Response Times",
                False,
                f"Response time testing error: {str(e)}"
            )
            return False
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("🚀 STARTING RENDER DEPLOYMENT BACKEND TESTING")
        print("=" * 60)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print("=" * 60)
        print()
        
        # Step 1: Authenticate
        if not self.authenticate_admin():
            print("❌ CRITICAL: Authentication failed - cannot proceed with tests")
            return False
        
        # Step 2: Health Check (no auth required)
        self.test_health_endpoint()
        
        # Step 3: Run all priority tests
        self.test_fund_portfolio_rebates()
        self.test_cash_flow_obligations()
        self.test_trading_analytics_core_accounts()
        self.test_money_managers_real_only()
        self.test_mongodb_trade_data()
        self.test_response_times()
        
        # Generate summary
        self.generate_summary()
        
        return self.success_count == self.total_tests
    
    def generate_summary(self):
        """Generate comprehensive test summary"""
        print("=" * 60)
        print("🎯 RENDER DEPLOYMENT TEST SUMMARY")
        print("=" * 60)
        
        success_rate = (self.success_count / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"Overall Success Rate: {success_rate:.1f}% ({self.success_count}/{self.total_tests})")
        print()
        
        # Group results by status
        passed_tests = [r for r in self.test_results if r['success']]
        failed_tests = [r for r in self.test_results if not r['success']]
        
        if failed_tests:
            print("❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"   • {test['test']}: {test['details']}")
            print()
        
        if passed_tests:
            print("✅ PASSED TESTS:")
            for test in passed_tests:
                print(f"   • {test['test']}: {test['details']}")
            print()
        
        # Critical issues summary
        critical_issues = []
        for test in failed_tests:
            if "Rebates" in test['test']:
                critical_issues.append("FIDUS Monthly Profit showing $0 rebates")
            elif "Obligations" in test['test']:
                critical_issues.append("Fund obligations calculation broken")
            elif "CORE Accounts" in test['test']:
                critical_issues.append("CORE fund account count incorrect")
            elif "Money Managers" in test['test']:
                critical_issues.append("Money managers showing test/fake data")
            elif "Health" in test['test']:
                critical_issues.append("Backend deployment not responding")
            elif "MongoDB" in test['test']:
                critical_issues.append("Trade data sync issues")
        
        if critical_issues:
            print("🚨 CRITICAL ISSUES IDENTIFIED:")
            for issue in critical_issues:
                print(f"   • {issue}")
            print()
        
        # Success criteria check
        print("📋 SUCCESS CRITERIA CHECK:")
        criteria = [
            ("All endpoints return HTTP 200", any(t['test'] == 'Deployment Health Check' and t['success'] for t in self.test_results)),
            ("FIDUS Monthly Profit shows actual rebates", any(t['test'] == 'Fund Portfolio Rebates' and t['success'] for t in self.test_results)),
            ("CORE fund shows 2 accounts", any(t['test'] == 'Trading Analytics CORE Accounts' and t['success'] for t in self.test_results)),
            ("Money Managers shows exactly 4 managers", any(t['test'] == 'Money Managers Real Only' and t['success'] for t in self.test_results)),
            ("No duplicate key errors", any(t['test'] == 'MongoDB Trade Data Sync' and t['success'] for t in self.test_results)),
            ("Backend responds within 5 seconds", any(t['test'] == 'API Response Times' and t['success'] for t in self.test_results))
        ]
        
        for criterion, met in criteria:
            status = "✅" if met else "❌"
            print(f"   {status} {criterion}")
        
        print()
        print("=" * 60)
        
        if success_rate >= 85:
            print("🎉 DEPLOYMENT VERIFICATION: SUCCESS")
        elif success_rate >= 70:
            print("⚠️ DEPLOYMENT VERIFICATION: PARTIAL SUCCESS - ISSUES IDENTIFIED")
        else:
            print("🚨 DEPLOYMENT VERIFICATION: FAILED - CRITICAL ISSUES")
        
        print("=" * 60)

def main():
    """Main test execution"""
    tester = RenderDeploymentTester()
    
    try:
        success = tester.run_all_tests()
        
        # Exit with appropriate code
        if success:
            print("\n✅ All tests passed successfully!")
            sys.exit(0)
        else:
            print(f"\n❌ {tester.total_tests - tester.success_count} test(s) failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        sys.exit(2)
    except Exception as e:
        print(f"\n💥 Testing failed with error: {str(e)}")
        sys.exit(3)

if __name__ == "__main__":
    main()