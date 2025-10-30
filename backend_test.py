#!/usr/bin/env python3
"""
COMPREHENSIVE BACKEND TESTING - 4 PRIORITY ISSUES
Testing Date: December 18, 2025
Backend URL: https://mt5-bridge-system.preview.emergentagent.com/api
Auth: Admin token (username: admin, password: password123)

Test Cases:
1. Fund Portfolio - FIDUS Monthly Profit (total_rebates field)
2. Cash Flow - Fund Obligations (total_client_obligations and total_fund_outflows)
3. Trading Analytics - CORE Fund Account Count (should be 2 accounts)
4. Money Managers - Real Managers Only (should return exactly 4 managers)
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional

class BackendTester:
    def __init__(self):
        self.base_url = "https://mt5-bridge-system.preview.emergentagent.com/api"
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
    
    def test_fund_portfolio_rebates(self) -> bool:
        """Test 1: Fund Portfolio - FIDUS Monthly Profit (total_rebates field)"""
        try:
            print("\n📊 Testing Fund Portfolio - FIDUS Monthly Profit...")
            
            response = self.session.get(f"{self.base_url}/fund-portfolio/overview")
            
            if response.status_code != 200:
                self.log_test("Fund Portfolio API", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            self.log_test("Fund Portfolio API", "PASS", "Successfully retrieved fund portfolio data")
            
            # Check for total_rebates field in CORE and BALANCE funds
            funds_checked = 0
            rebates_found = 0
            non_zero_rebates = 0
            
            if isinstance(data, list):
                funds = data
            elif isinstance(data, dict) and 'funds' in data:
                funds = data['funds']
            else:
                funds = [data] if isinstance(data, dict) else []
            
            for fund in funds:
                if isinstance(fund, dict):
                    fund_code = fund.get('fund_code', fund.get('code', 'Unknown'))
                    if fund_code in ['CORE', 'BALANCE']:
                        funds_checked += 1
                        total_rebates = fund.get('total_rebates')
                        
                        if total_rebates is not None:
                            rebates_found += 1
                            if total_rebates != 0:
                                non_zero_rebates += 1
                                self.log_test(f"{fund_code} Fund Rebates", "PASS", 
                                            f"Found non-zero rebates: ${total_rebates}")
                            else:
                                self.log_test(f"{fund_code} Fund Rebates", "FAIL", 
                                            f"Rebates are $0 (should have actual values)", 
                                            "Non-zero rebates", "$0")
                        else:
                            self.log_test(f"{fund_code} Fund Rebates", "FAIL", 
                                        "total_rebates field missing from response")
            
            if funds_checked == 0:
                self.log_test("Fund Portfolio Structure", "FAIL", "No CORE or BALANCE funds found in response")
                return False
            
            success = rebates_found > 0 and non_zero_rebates > 0
            summary = f"Checked {funds_checked} funds, found {rebates_found} with rebates field, {non_zero_rebates} with non-zero values"
            self.log_test("Fund Portfolio Rebates Summary", "PASS" if success else "FAIL", summary)
            
            return success
            
        except Exception as e:
            self.log_test("Fund Portfolio Test", "ERROR", f"Exception: {str(e)}")
            return False
    
    def test_cashflow_obligations(self) -> bool:
        """Test 2: Cash Flow - Fund Obligations"""
        try:
            print("\n💰 Testing Cash Flow - Fund Obligations...")
            
            response = self.session.get(f"{self.base_url}/admin/cashflow/overview?timeframe=3months&fund=all")
            
            if response.status_code != 200:
                self.log_test("Cash Flow API", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            self.log_test("Cash Flow API", "PASS", "Successfully retrieved cash flow data")
            
            # Check for required fields
            total_client_obligations = data.get('total_client_obligations')
            total_fund_outflows = data.get('total_fund_outflows')
            
            success = True
            
            if total_client_obligations is not None:
                if total_client_obligations != 0:
                    self.log_test("Total Client Obligations", "PASS", 
                                f"Found non-zero obligations: ${total_client_obligations}")
                else:
                    self.log_test("Total Client Obligations", "FAIL", 
                                "Obligations are $0 (should calculate actual obligations)", 
                                "Non-zero obligations", "$0")
                    success = False
            else:
                self.log_test("Total Client Obligations", "FAIL", 
                            "total_client_obligations field missing from response")
                success = False
            
            if total_fund_outflows is not None:
                if total_fund_outflows != 0:
                    self.log_test("Total Fund Outflows", "PASS", 
                                f"Found non-zero outflows: ${total_fund_outflows}")
                else:
                    self.log_test("Total Fund Outflows", "FAIL", 
                                "Outflows are $0 (should calculate actual outflows)", 
                                "Non-zero outflows", "$0")
                    success = False
            else:
                self.log_test("Total Fund Outflows", "FAIL", 
                            "total_fund_outflows field missing from response")
                success = False
            
            return success
            
        except Exception as e:
            self.log_test("Cash Flow Test", "ERROR", f"Exception: {str(e)}")
            return False
    
    def test_trading_analytics_core_accounts(self) -> bool:
        """Test 3: Trading Analytics - CORE Fund Account Count (should be 2)"""
        try:
            print("\n📈 Testing Trading Analytics - CORE Fund Account Count...")
            
            response = self.session.get(f"{self.base_url}/admin/fund-performance/dashboard")
            
            if response.status_code != 200:
                self.log_test("Trading Analytics API", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            self.log_test("Trading Analytics API", "PASS", "Successfully retrieved trading analytics data")
            
            # Check for CORE fund account count
            by_fund = data.get('by_fund', {})
            core_fund = by_fund.get('CORE', {})
            account_count = core_fund.get('account_count')
            
            if account_count is not None:
                if account_count == 2:
                    self.log_test("CORE Fund Account Count", "PASS", 
                                f"Correct account count: {account_count} (accounts 891234 and 885822)")
                    return True
                else:
                    self.log_test("CORE Fund Account Count", "FAIL", 
                                f"Incorrect account count", 
                                "2 accounts (891234 and 885822)", f"{account_count} accounts")
                    return False
            else:
                self.log_test("CORE Fund Account Count", "FAIL", 
                            "account_count field missing from by_fund.CORE")
                return False
            
        except Exception as e:
            self.log_test("Trading Analytics Test", "ERROR", f"Exception: {str(e)}")
            return False
    
    def test_money_managers_real_only(self) -> bool:
        """Test 4: Money Managers - Real Managers Only (should return exactly 4)"""
        try:
            print("\n👥 Testing Money Managers - Real Managers Only...")
            
            response = self.session.get(f"{self.base_url}/admin/trading-analytics/managers")
            
            if response.status_code != 200:
                self.log_test("Money Managers API", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            self.log_test("Money Managers API", "PASS", "Successfully retrieved money managers data")
            
            # Extract managers list
            managers = []
            if isinstance(data, list):
                managers = data
            elif isinstance(data, dict) and 'managers' in data:
                managers = data['managers']
            elif isinstance(data, dict) and 'data' in data:
                managers = data['data']
            
            # Expected real managers
            expected_managers = ["CP Strategy", "TradingHub Gold", "GoldenTrade", "UNO14"]
            excluded_managers = ["Manual Trading", "Manager None"]
            
            # Check manager count
            manager_count = len(managers)
            if manager_count == 4:
                self.log_test("Manager Count", "PASS", f"Correct number of managers: {manager_count}")
            else:
                self.log_test("Manager Count", "FAIL", f"Incorrect number of managers", 
                            "4 real managers", f"{manager_count} managers")
            
            # Check manager names
            found_managers = []
            excluded_found = []
            
            for manager in managers:
                if isinstance(manager, dict):
                    name = manager.get('name', manager.get('manager_name', 'Unknown'))
                    found_managers.append(name)
                    
                    if name in excluded_managers:
                        excluded_found.append(name)
                elif isinstance(manager, str):
                    found_managers.append(manager)
                    if manager in excluded_managers:
                        excluded_found.append(manager)
            
            # Check for excluded managers
            if excluded_found:
                self.log_test("Excluded Managers Check", "FAIL", 
                            f"Found excluded managers: {excluded_found}", 
                            "No excluded managers", excluded_found)
                success = False
            else:
                self.log_test("Excluded Managers Check", "PASS", 
                            "No excluded managers (Manual Trading, Manager None) found")
                success = True
            
            # Check for expected managers
            expected_found = [m for m in expected_managers if m in found_managers]
            if len(expected_found) == 4:
                self.log_test("Expected Managers Check", "PASS", 
                            f"All expected managers found: {expected_found}")
            else:
                missing = [m for m in expected_managers if m not in found_managers]
                self.log_test("Expected Managers Check", "FAIL", 
                            f"Missing expected managers: {missing}", 
                            expected_managers, found_managers)
                success = False
            
            # Summary
            summary = f"Found {manager_count} managers: {found_managers}"
            self.log_test("Money Managers Summary", "PASS" if success and manager_count == 4 else "FAIL", summary)
            
            return success and manager_count == 4
            
        except Exception as e:
            self.log_test("Money Managers Test", "ERROR", f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all backend tests"""
        print("🚀 Starting Comprehensive Backend Testing - 4 Priority Issues")
        print("=" * 70)
        
        # Authenticate first
        if not self.authenticate_admin():
            return {"success": False, "error": "Authentication failed"}
        
        # Run all tests
        test_results = {
            "fund_portfolio_rebates": self.test_fund_portfolio_rebates(),
            "cashflow_obligations": self.test_cashflow_obligations(),
            "trading_analytics_core_accounts": self.test_trading_analytics_core_accounts(),
            "money_managers_real_only": self.test_money_managers_real_only()
        }
        
        # Calculate summary
        total_tests = len(test_results)
        passed_tests = sum(1 for result in test_results.values() if result)
        success_rate = (passed_tests / total_tests) * 100
        
        print("\n" + "=" * 70)
        print("📊 TEST SUMMARY")
        print("=" * 70)
        
        for test_name, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name.replace('_', ' ').title()}")
        
        print(f"\n🎯 Overall Success Rate: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        if success_rate == 100:
            print("🎉 ALL TESTS PASSED - Backend fixes verified successfully!")
        elif success_rate >= 75:
            print("⚠️  Most tests passed - Some issues remain")
        else:
            print("🚨 CRITICAL ISSUES - Multiple backend problems identified")
        
        return {
            "success": success_rate == 100,
            "success_rate": success_rate,
            "passed_tests": passed_tests,
            "total_tests": total_tests,
            "test_results": test_results,
            "detailed_results": self.test_results
        }

def main():
    """Main test execution"""
    tester = BackendTester()
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if results["success"] else 1)

if __name__ == "__main__":
    main()