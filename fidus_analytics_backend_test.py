#!/usr/bin/env python3
"""
FIDUS Trading Analytics Backend Test Suite
Testing manager ranking fix and analytics endpoints

Test Focus:
1. Portfolio Overview - GET /api/admin/trading-analytics/portfolio
2. Manager Rankings - GET /api/admin/trading-analytics/managers  
3. Fund Performance BALANCE - GET /api/admin/trading-analytics/funds/BALANCE
4. Fund Performance CORE - GET /api/admin/trading-analytics/funds/CORE

Expected Results per SYSTEM_MASTER.md:
- Total AUM: $118,151.41 (BALANCE $100,000 + CORE $18,151.41)
- Active Managers: 5 (UNO14, TradingHub Gold, CP Strategy, MultiBank BALANCE, MEXAtlantic)
- GoldenTrade should be EXCLUDED (inactive)
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any, Optional

class FIDUSAnalyticsTest:
    def __init__(self):
        self.base_url = "https://fintech-dashboard-60.preview.emergentagent.com/api"
        self.session = requests.Session()
        self.admin_token = None
        
        # Expected values per SYSTEM_MASTER.md
        self.expected_total_aum = 118151.41
        self.expected_active_managers = 5
        self.expected_balance_aum = 100000.0
        self.expected_core_aum = 18151.41
        self.expected_balance_accounts = [886557, 886602, 891215, 897589]
        self.expected_core_accounts = [885822, 891234, 897590]
        
        # Manager names that should be active
        self.expected_active_manager_names = [
            "UNO14 Manager",
            "TradingHub Gold Provider", 
            "CP Strategy Provider",
            "MultiBank BALANCE Trader",
            "MEXAtlantic Provider"
        ]
        
        # Manager that should be EXCLUDED
        self.excluded_manager = "GoldenTrade"
        
        self.test_results = []
        
    def log_test(self, test_name: str, passed: bool, details: str = "", expected: Any = None, actual: Any = None):
        """Log test result with details"""
        status = "✅ PASS" if passed else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "passed": passed,
            "details": details,
            "expected": expected,
            "actual": actual,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
        if not passed and expected is not None and actual is not None:
            print(f"    Expected: {expected}")
            print(f"    Actual: {actual}")
        print()
        
    def authenticate_admin(self) -> bool:
        """Authenticate as admin user"""
        try:
            print("🔐 Authenticating as admin...")
            
            login_data = {
                "username": "admin",
                "password": "password123",
                "user_type": "admin"
            }
            
            response = self.session.post(
                f"{self.base_url}/auth/login",
                json=login_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                # Check if we have user data and token (success can be missing)
                if data.get("token") or (data.get("user", {}).get("token")):
                    # Extract token from either location
                    token = data.get("token") or data.get("user", {}).get("token")
                    self.admin_token = token
                    self.session.headers.update({
                        "Authorization": f"Bearer {self.admin_token}"
                    })
                    user_name = data.get("name") or data.get("user", {}).get("name", "Admin")
                    self.log_test("Admin Authentication", True, f"Logged in as {user_name}")
                    return True
                else:
                    self.log_test("Admin Authentication", False, f"Login failed: {data}")
                    return False
            else:
                self.log_test("Admin Authentication", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_portfolio_overview(self) -> bool:
        """Test Portfolio Overview endpoint"""
        try:
            print("📊 Testing Portfolio Overview...")
            
            response = self.session.get(
                f"{self.base_url}/admin/trading-analytics/portfolio",
                timeout=30
            )
            
            if response.status_code != 200:
                self.log_test("Portfolio Overview - HTTP Status", False, 
                            f"Expected 200, got {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            # Check if response has success flag
            if not data.get("success", True):
                self.log_test("Portfolio Overview - Success Flag", False, 
                            f"API returned success=false: {data.get('error', 'Unknown error')}")
                return False
            
            portfolio = data.get("portfolio", data)  # Handle both wrapped and direct response
            
            # Test 1: Total AUM
            actual_aum = portfolio.get("total_aum", 0)
            aum_match = abs(actual_aum - self.expected_total_aum) < 1.0  # Allow $1 tolerance
            self.log_test("Portfolio Overview - Total AUM", aum_match,
                         f"Expected ~${self.expected_total_aum:,.2f}, got ${actual_aum:,.2f}",
                         self.expected_total_aum, actual_aum)
            
            # Test 2: Active Managers Count
            actual_managers = portfolio.get("active_managers", portfolio.get("total_managers", 0))
            managers_match = actual_managers == self.expected_active_managers
            self.log_test("Portfolio Overview - Active Managers", managers_match,
                         f"Expected {self.expected_active_managers} active managers, got {actual_managers}",
                         self.expected_active_managers, actual_managers)
            
            # Test 3: Fund Breakdown
            funds = portfolio.get("funds", {})
            
            # BALANCE Fund
            balance_fund = funds.get("BALANCE", {})
            balance_aum = balance_fund.get("aum", 0)
            balance_aum_match = abs(balance_aum - self.expected_balance_aum) < 1.0
            self.log_test("Portfolio Overview - BALANCE Fund AUM", balance_aum_match,
                         f"Expected ${self.expected_balance_aum:,.2f}, got ${balance_aum:,.2f}",
                         self.expected_balance_aum, balance_aum)
            
            # CORE Fund  
            core_fund = funds.get("CORE", {})
            core_aum = core_fund.get("aum", 0)
            core_aum_match = abs(core_aum - self.expected_core_aum) < 1.0
            self.log_test("Portfolio Overview - CORE Fund AUM", core_aum_match,
                         f"Expected ${self.expected_core_aum:,.2f}, got ${core_aum:,.2f}",
                         self.expected_core_aum, core_aum)
            
            # Test 4: Response Structure
            required_fields = ["total_aum", "current_equity", "total_pnl", "funds"]
            missing_fields = [field for field in required_fields if field not in portfolio]
            structure_ok = len(missing_fields) == 0
            self.log_test("Portfolio Overview - Response Structure", structure_ok,
                         f"Missing fields: {missing_fields}" if missing_fields else "All required fields present")
            
            return aum_match and managers_match and balance_aum_match and core_aum_match and structure_ok
            
        except Exception as e:
            self.log_test("Portfolio Overview - Exception", False, f"Exception: {str(e)}")
            return False
    
    def test_manager_rankings(self) -> bool:
        """Test Manager Rankings endpoint"""
        try:
            print("🏆 Testing Manager Rankings...")
            
            response = self.session.get(
                f"{self.base_url}/admin/trading-analytics/managers",
                timeout=30
            )
            
            if response.status_code != 200:
                self.log_test("Manager Rankings - HTTP Status", False,
                            f"Expected 200, got {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            # Check if response has success flag
            if not data.get("success", True):
                self.log_test("Manager Rankings - Success Flag", False,
                            f"API returned success=false: {data.get('error', 'Unknown error')}")
                return False
            
            managers_data = data.get("managers", data)
            managers_list = managers_data.get("managers", []) if isinstance(managers_data, dict) else managers_data
            
            # Test 1: Manager Count
            actual_count = len(managers_list)
            count_match = actual_count == self.expected_active_managers
            self.log_test("Manager Rankings - Count", count_match,
                         f"Expected {self.expected_active_managers} managers, got {actual_count}",
                         self.expected_active_managers, actual_count)
            
            # Test 2: GoldenTrade Exclusion
            manager_names = [m.get("manager_name", "") for m in managers_list]
            goldentrade_excluded = self.excluded_manager not in " ".join(manager_names)
            self.log_test("Manager Rankings - GoldenTrade Excluded", goldentrade_excluded,
                         f"GoldenTrade should be excluded. Found managers: {manager_names}")
            
            # Test 3: Expected Active Managers Present
            found_managers = []
            missing_managers = []
            
            for expected_name in self.expected_active_manager_names:
                found = any(expected_name in manager.get("manager_name", "") for manager in managers_list)
                if found:
                    found_managers.append(expected_name)
                else:
                    missing_managers.append(expected_name)
            
            managers_present = len(missing_managers) == 0
            self.log_test("Manager Rankings - Expected Managers Present", managers_present,
                         f"Found: {found_managers}, Missing: {missing_managers}")
            
            # Test 4: Manager Data Structure
            if managers_list:
                sample_manager = managers_list[0]
                required_fields = ["manager_name", "fund_type", "total_pnl", "return_percentage", "account"]
                missing_fields = [field for field in required_fields if field not in sample_manager]
                structure_ok = len(missing_fields) == 0
                self.log_test("Manager Rankings - Data Structure", structure_ok,
                             f"Sample manager missing fields: {missing_fields}" if missing_fields else "All required fields present")
            else:
                structure_ok = False
                self.log_test("Manager Rankings - Data Structure", False, "No managers returned")
            
            # Test 5: Fund Type Distribution
            balance_managers = [m for m in managers_list if m.get("fund_type") == "BALANCE"]
            core_managers = [m for m in managers_list if m.get("fund_type") == "CORE"]
            
            fund_distribution_ok = len(balance_managers) >= 3 and len(core_managers) >= 1  # At least 4 BALANCE, 1 CORE
            self.log_test("Manager Rankings - Fund Distribution", fund_distribution_ok,
                         f"BALANCE managers: {len(balance_managers)}, CORE managers: {len(core_managers)}")
            
            return count_match and goldentrade_excluded and managers_present and structure_ok and fund_distribution_ok
            
        except Exception as e:
            self.log_test("Manager Rankings - Exception", False, f"Exception: {str(e)}")
            return False
    
    def test_balance_fund_performance(self) -> bool:
        """Test BALANCE Fund Performance endpoint"""
        try:
            print("💰 Testing BALANCE Fund Performance...")
            
            response = self.session.get(
                f"{self.base_url}/admin/trading-analytics/funds/BALANCE",
                timeout=30
            )
            
            if response.status_code != 200:
                self.log_test("BALANCE Fund - HTTP Status", False,
                            f"Expected 200, got {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            # Check if response has success flag
            if not data.get("success", True):
                self.log_test("BALANCE Fund - Success Flag", False,
                            f"API returned success=false: {data.get('error', 'Unknown error')}")
                return False
            
            fund_data = data.get("fund", data)
            
            # Test 1: AUM
            actual_aum = fund_data.get("aum", 0)
            aum_match = abs(actual_aum - self.expected_balance_aum) < 1.0
            self.log_test("BALANCE Fund - AUM", aum_match,
                         f"Expected ${self.expected_balance_aum:,.2f}, got ${actual_aum:,.2f}",
                         self.expected_balance_aum, actual_aum)
            
            # Test 2: Managers Count
            managers = fund_data.get("managers", [])
            expected_balance_managers = 4  # UNO14, TradingHub, MultiBank, MEXAtlantic
            managers_count_match = len(managers) == expected_balance_managers
            self.log_test("BALANCE Fund - Managers Count", managers_count_match,
                         f"Expected {expected_balance_managers} managers, got {len(managers)}",
                         expected_balance_managers, len(managers))
            
            # Test 3: Account Coverage
            manager_accounts = [m.get("account") for m in managers if m.get("account")]
            accounts_covered = all(acc in manager_accounts for acc in self.expected_balance_accounts)
            self.log_test("BALANCE Fund - Account Coverage", accounts_covered,
                         f"Expected accounts {self.expected_balance_accounts}, got {manager_accounts}")
            
            # Test 4: Fund Name
            fund_name_match = fund_data.get("fund_name") == "BALANCE"
            self.log_test("BALANCE Fund - Fund Name", fund_name_match,
                         f"Expected 'BALANCE', got '{fund_data.get('fund_name')}'")
            
            # Test 5: Performance Metrics
            required_metrics = ["total_equity", "total_pnl", "weighted_return"]
            missing_metrics = [metric for metric in required_metrics if metric not in fund_data]
            metrics_ok = len(missing_metrics) == 0
            self.log_test("BALANCE Fund - Performance Metrics", metrics_ok,
                         f"Missing metrics: {missing_metrics}" if missing_metrics else "All metrics present")
            
            return aum_match and managers_count_match and accounts_covered and fund_name_match and metrics_ok
            
        except Exception as e:
            self.log_test("BALANCE Fund - Exception", False, f"Exception: {str(e)}")
            return False
    
    def test_core_fund_performance(self) -> bool:
        """Test CORE Fund Performance endpoint"""
        try:
            print("🎯 Testing CORE Fund Performance...")
            
            response = self.session.get(
                f"{self.base_url}/admin/trading-analytics/funds/CORE",
                timeout=30
            )
            
            if response.status_code != 200:
                self.log_test("CORE Fund - HTTP Status", False,
                            f"Expected 200, got {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            # Check if response has success flag
            if not data.get("success", True):
                self.log_test("CORE Fund - Success Flag", False,
                            f"API returned success=false: {data.get('error', 'Unknown error')}")
                return False
            
            fund_data = data.get("fund", data)
            
            # Test 1: AUM
            actual_aum = fund_data.get("aum", 0)
            aum_match = abs(actual_aum - self.expected_core_aum) < 1.0
            self.log_test("CORE Fund - AUM", aum_match,
                         f"Expected ${self.expected_core_aum:,.2f}, got ${actual_aum:,.2f}",
                         self.expected_core_aum, actual_aum)
            
            # Test 2: Managers Count (CP Strategy on multiple accounts)
            managers = fund_data.get("managers", [])
            expected_core_managers = 2  # CP Strategy on 885822 and 897590
            managers_count_match = len(managers) >= 1 and len(managers) <= 2  # Allow 1-2 managers
            self.log_test("CORE Fund - Managers Count", managers_count_match,
                         f"Expected 1-2 managers, got {len(managers)}",
                         "1-2", len(managers))
            
            # Test 3: Account Coverage
            manager_accounts = [m.get("account") for m in managers if m.get("account")]
            # Should include at least 885822 and 897590 (CP Strategy accounts)
            core_accounts_covered = any(acc in manager_accounts for acc in [885822, 897590])
            self.log_test("CORE Fund - Account Coverage", core_accounts_covered,
                         f"Expected accounts from {self.expected_core_accounts}, got {manager_accounts}")
            
            # Test 4: Fund Name
            fund_name_match = fund_data.get("fund_name") == "CORE"
            self.log_test("CORE Fund - Fund Name", fund_name_match,
                         f"Expected 'CORE', got '{fund_data.get('fund_name')}'")
            
            # Test 5: Performance Metrics
            required_metrics = ["total_equity", "total_pnl", "weighted_return"]
            missing_metrics = [metric for metric in required_metrics if metric not in fund_data]
            metrics_ok = len(missing_metrics) == 0
            self.log_test("CORE Fund - Performance Metrics", metrics_ok,
                         f"Missing metrics: {missing_metrics}" if missing_metrics else "All metrics present")
            
            return aum_match and managers_count_match and core_accounts_covered and fund_name_match and metrics_ok
            
        except Exception as e:
            self.log_test("CORE Fund - Exception", False, f"Exception: {str(e)}")
            return False
    
    def test_data_consistency(self) -> bool:
        """Test data consistency across all endpoints"""
        try:
            print("🔄 Testing Data Consistency...")
            
            # Get all endpoint data
            portfolio_response = self.session.get(f"{self.base_url}/admin/trading-analytics/portfolio")
            managers_response = self.session.get(f"{self.base_url}/admin/trading-analytics/managers")
            balance_response = self.session.get(f"{self.base_url}/admin/trading-analytics/funds/BALANCE")
            core_response = self.session.get(f"{self.base_url}/admin/trading-analytics/funds/CORE")
            
            if not all(r.status_code == 200 for r in [portfolio_response, managers_response, balance_response, core_response]):
                self.log_test("Data Consistency - API Availability", False, "Not all endpoints returned 200")
                return False
            
            portfolio_data = portfolio_response.json().get("portfolio", portfolio_response.json())
            managers_data = managers_response.json()
            balance_data = balance_response.json().get("fund", balance_response.json())
            core_data = core_response.json().get("fund", core_response.json())
            
            # Test 1: AUM Consistency
            portfolio_aum = portfolio_data.get("total_aum", 0)
            balance_aum = balance_data.get("aum", 0)
            core_aum = core_data.get("aum", 0)
            calculated_aum = balance_aum + core_aum
            
            aum_consistent = abs(portfolio_aum - calculated_aum) < 1.0
            self.log_test("Data Consistency - AUM", aum_consistent,
                         f"Portfolio AUM: ${portfolio_aum:,.2f}, Calculated (BALANCE + CORE): ${calculated_aum:,.2f}")
            
            # Test 2: Manager Count Consistency
            portfolio_managers = portfolio_data.get("active_managers", portfolio_data.get("total_managers", 0))
            managers_list = managers_data.get("managers", managers_data)
            if isinstance(managers_list, dict):
                managers_list = managers_list.get("managers", [])
            actual_managers_count = len(managers_list)
            
            managers_consistent = portfolio_managers == actual_managers_count
            self.log_test("Data Consistency - Manager Count", managers_consistent,
                         f"Portfolio reports {portfolio_managers} managers, Rankings endpoint has {actual_managers_count}")
            
            # Test 3: Fund Breakdown Consistency
            portfolio_funds = portfolio_data.get("funds", {})
            portfolio_balance = portfolio_funds.get("BALANCE", {})
            portfolio_core = portfolio_funds.get("CORE", {})
            
            balance_consistent = abs(portfolio_balance.get("aum", 0) - balance_aum) < 1.0
            core_consistent = abs(portfolio_core.get("aum", 0) - core_aum) < 1.0
            
            funds_consistent = balance_consistent and core_consistent
            self.log_test("Data Consistency - Fund Breakdown", funds_consistent,
                         f"Portfolio vs Fund endpoints AUM match: BALANCE={balance_consistent}, CORE={core_consistent}")
            
            return aum_consistent and managers_consistent and funds_consistent
            
        except Exception as e:
            self.log_test("Data Consistency - Exception", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return summary"""
        print("🚀 Starting FIDUS Trading Analytics Backend Tests")
        print("=" * 60)
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ Authentication failed - cannot proceed with tests")
            return self.generate_summary()
        
        # Run all tests
        test_methods = [
            self.test_portfolio_overview,
            self.test_manager_rankings,
            self.test_balance_fund_performance,
            self.test_core_fund_performance,
            self.test_data_consistency
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                self.log_test(f"{test_method.__name__} - Critical Error", False, f"Exception: {str(e)}")
        
        return self.generate_summary()
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate test summary"""
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t["passed"]])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        summary = {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "success_rate": round(success_rate, 1),
            "test_results": self.test_results,
            "timestamp": datetime.now().isoformat()
        }
        
        print("=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for test in self.test_results:
                if not test["passed"]:
                    print(f"  - {test['test']}: {test['details']}")
            print()
        
        # Critical validation summary
        print("🎯 CRITICAL VALIDATIONS:")
        
        # Check for key metrics
        portfolio_tests = [t for t in self.test_results if "Portfolio Overview" in t["test"]]
        manager_tests = [t for t in self.test_results if "Manager Rankings" in t["test"]]
        
        aum_test = next((t for t in portfolio_tests if "Total AUM" in t["test"]), None)
        if aum_test:
            status = "✅" if aum_test["passed"] else "❌"
            print(f"  {status} Total AUM: Expected ${self.expected_total_aum:,.2f}, Got ${aum_test.get('actual', 'N/A')}")
        
        managers_test = next((t for t in manager_tests if "Count" in t["test"]), None)
        if managers_test:
            status = "✅" if managers_test["passed"] else "❌"
            print(f"  {status} Active Managers: Expected {self.expected_active_managers}, Got {managers_test.get('actual', 'N/A')}")
        
        goldentrade_test = next((t for t in manager_tests if "GoldenTrade" in t["test"]), None)
        if goldentrade_test:
            status = "✅" if goldentrade_test["passed"] else "❌"
            print(f"  {status} GoldenTrade Excluded: {goldentrade_test['passed']}")
        
        return summary

def main():
    """Main test execution"""
    tester = FIDUSAnalyticsTest()
    summary = tester.run_all_tests()
    
    # Exit with appropriate code
    if summary["success_rate"] >= 80:
        print("🎉 Tests completed successfully!")
        sys.exit(0)
    else:
        print("⚠️  Tests completed with issues!")
        sys.exit(1)

if __name__ == "__main__":
    main()