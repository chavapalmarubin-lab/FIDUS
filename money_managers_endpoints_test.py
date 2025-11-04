#!/usr/bin/env python3
"""
MONEY MANAGERS ENDPOINTS TESTING - December 18, 2025
Testing Date: December 18, 2025
Backend URL: https://fidusrefs.preview.emergentagent.com/api
Auth: Admin token (username: admin, password: password123)

SPECIFIC TEST REQUEST:
Test BOTH Money Managers endpoints after fixes

**Test 1: Overview Tab (GET /api/admin/money-managers)**
- Should return 4 managers
- Initial Allocation ≠ Current Equity for each manager
- Verify TradingHub Gold, GoldenTrade, UNO14, CP Strategy
- Check that initial_allocation uses target_amount

**Test 2: Compare Tab (GET /api/admin/trading-analytics/managers)**
- Should return ALL 4 managers including UNO14 (even with 0 trades)
- TradingHub Gold, GoldenTrade, UNO14 MAM, CP Strategy
- UNO14 should show: 0 deals, $0 profit, 0% win rate

**Expected Results:**
- Overview: 4 managers with different Initial Allocation vs Current Equity
- Compare: 4 managers including UNO14 with zero stats
- No missing managers in either tab
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional

class MoneyManagersTester:
    def __init__(self):
        self.base_url = "https://fidusrefs.preview.emergentagent.com/api"
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
    
    def test_overview_tab_endpoint(self) -> bool:
        """Test 1: Overview Tab (GET /api/admin/money-managers)"""
        try:
            print("\n📊 Testing Overview Tab - Money Managers Endpoint...")
            
            response = self.session.get(f"{self.base_url}/admin/money-managers")
            
            if response.status_code != 200:
                self.log_test("Overview Tab API", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            self.log_test("Overview Tab API", "PASS", "Successfully retrieved money managers overview data")
            
            # Check for managers array
            managers = data.get('managers', [])
            
            if not managers:
                self.log_test("Overview Managers Array", "FAIL", "No managers found in response")
                return False
            
            # Test 1.1: Should return 4 managers
            manager_count = len(managers)
            if manager_count == 4:
                self.log_test("Overview Manager Count", "PASS", f"Correct number of managers: {manager_count}")
            else:
                self.log_test("Overview Manager Count", "FAIL", f"Expected 4 managers, got {manager_count}")
                return False
            
            # Test 1.2: Verify expected manager names
            expected_managers = ["TradingHub Gold", "GoldenTrade", "UNO14", "CP Strategy"]
            found_managers = []
            
            for manager in managers:
                if isinstance(manager, dict):
                    # Try different possible name fields
                    name = manager.get('manager_name') or manager.get('name') or manager.get('manager') or 'Unknown'
                    found_managers.append(name)
            
            # Check if all expected managers are found (allow partial matches)
            missing_managers = []
            found_expected = []
            
            for expected in expected_managers:
                found = False
                for actual in found_managers:
                    if expected.lower() in actual.lower() or actual.lower() in expected.lower():
                        found_expected.append(actual)
                        found = True
                        break
                if not found:
                    missing_managers.append(expected)
            
            if not missing_managers:
                self.log_test("Overview Manager Names", "PASS", f"All expected managers found: {found_expected}")
            else:
                self.log_test("Overview Manager Names", "FAIL", f"Missing managers: {missing_managers}")
                return False
            
            # Test 1.3: Check Initial Allocation ≠ Current Equity for each manager
            allocation_equity_different = 0
            allocation_equity_same = 0
            
            for i, manager in enumerate(managers):
                manager_name = manager.get('manager_name') or manager.get('name') or f"Manager {i+1}"
                
                # Try different field names for allocation and equity
                initial_allocation = (manager.get('initial_allocation') or 
                                    manager.get('target_amount') or 
                                    manager.get('allocated_amount') or 0)
                
                current_equity = (manager.get('current_equity') or 
                                manager.get('equity') or 
                                manager.get('current_balance') or 0)
                
                if initial_allocation != current_equity:
                    allocation_equity_different += 1
                    self.log_test(f"Overview {manager_name} Allocation≠Equity", "PASS", 
                                f"Initial: ${initial_allocation}, Current: ${current_equity}")
                else:
                    allocation_equity_same += 1
                    self.log_test(f"Overview {manager_name} Allocation≠Equity", "FAIL", 
                                f"Values are the same: ${initial_allocation}")
            
            # Test 1.4: Check that initial_allocation uses target_amount
            target_amount_used = 0
            for manager in managers:
                if 'target_amount' in manager and 'initial_allocation' in manager:
                    if manager['target_amount'] == manager['initial_allocation']:
                        target_amount_used += 1
            
            if target_amount_used > 0:
                self.log_test("Overview Target Amount Usage", "PASS", 
                            f"{target_amount_used} managers use target_amount for initial_allocation")
            else:
                self.log_test("Overview Target Amount Usage", "FAIL", 
                            "No managers found using target_amount for initial_allocation")
            
            # Summary for Overview Tab
            overview_success = (manager_count == 4 and 
                              not missing_managers and 
                              allocation_equity_different > 0)
            
            self.log_test("Overview Tab Summary", "PASS" if overview_success else "FAIL", 
                        f"4 managers: {manager_count==4}, All names found: {not missing_managers}, "
                        f"Different allocations: {allocation_equity_different}/4")
            
            return overview_success
            
        except Exception as e:
            self.log_test("Overview Tab Test", "ERROR", f"Exception: {str(e)}")
            return False
    
    def test_compare_tab_endpoint(self) -> bool:
        """Test 2: Compare Tab (GET /api/admin/trading-analytics/managers)"""
        try:
            print("\n📈 Testing Compare Tab - Trading Analytics Managers Endpoint...")
            
            response = self.session.get(f"{self.base_url}/admin/trading-analytics/managers")
            
            if response.status_code != 200:
                self.log_test("Compare Tab API", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            self.log_test("Compare Tab API", "PASS", "Successfully retrieved trading analytics managers data")
            
            # Check for managers array
            managers = data.get('managers', [])
            
            if not managers:
                self.log_test("Compare Managers Array", "FAIL", "No managers found in response")
                return False
            
            # Test 2.1: Should return ALL 4 managers including UNO14
            manager_count = len(managers)
            if manager_count == 4:
                self.log_test("Compare Manager Count", "PASS", f"Correct number of managers: {manager_count}")
            else:
                self.log_test("Compare Manager Count", "FAIL", f"Expected 4 managers, got {manager_count}")
                return False
            
            # Test 2.2: Verify expected manager names (including UNO14 MAM)
            expected_managers = ["TradingHub Gold", "GoldenTrade", "UNO14", "CP Strategy"]
            found_managers = []
            uno14_found = False
            
            for manager in managers:
                if isinstance(manager, dict):
                    # Try different possible name fields
                    name = manager.get('manager_name') or manager.get('name') or manager.get('manager') or 'Unknown'
                    found_managers.append(name)
                    
                    # Special check for UNO14
                    if 'uno14' in name.lower():
                        uno14_found = True
            
            # Check if UNO14 is specifically included
            if uno14_found:
                self.log_test("Compare UNO14 Inclusion", "PASS", "UNO14 manager found in compare tab")
            else:
                self.log_test("Compare UNO14 Inclusion", "FAIL", "UNO14 manager missing from compare tab")
                return False
            
            # Check if all expected managers are found
            missing_managers = []
            found_expected = []
            
            for expected in expected_managers:
                found = False
                for actual in found_managers:
                    if expected.lower() in actual.lower() or actual.lower() in expected.lower():
                        found_expected.append(actual)
                        found = True
                        break
                if not found:
                    missing_managers.append(expected)
            
            if not missing_managers:
                self.log_test("Compare Manager Names", "PASS", f"All expected managers found: {found_expected}")
            else:
                self.log_test("Compare Manager Names", "FAIL", f"Missing managers: {missing_managers}")
                return False
            
            # Test 2.3: UNO14 should show zero stats (0 deals, $0 profit, 0% win rate)
            uno14_manager = None
            for manager in managers:
                name = manager.get('manager_name') or manager.get('name') or manager.get('manager') or ''
                if 'uno14' in name.lower():
                    uno14_manager = manager
                    break
            
            if uno14_manager:
                # Check UNO14 stats
                deals = uno14_manager.get('total_deals') or uno14_manager.get('deals') or 0
                profit = uno14_manager.get('total_profit') or uno14_manager.get('profit') or 0
                win_rate = uno14_manager.get('win_rate') or 0
                
                uno14_zero_stats = (deals == 0 and profit == 0 and win_rate == 0)
                
                if uno14_zero_stats:
                    self.log_test("Compare UNO14 Zero Stats", "PASS", 
                                f"UNO14 shows zero stats: {deals} deals, ${profit} profit, {win_rate}% win rate")
                else:
                    self.log_test("Compare UNO14 Zero Stats", "FAIL", 
                                f"UNO14 should show zero stats but shows: {deals} deals, ${profit} profit, {win_rate}% win rate")
            else:
                self.log_test("Compare UNO14 Zero Stats", "FAIL", "UNO14 manager not found for stats verification")
                uno14_zero_stats = False
            
            # Test 2.4: Verify other managers have non-zero stats (to confirm UNO14 is special case)
            non_zero_managers = 0
            for manager in managers:
                name = manager.get('manager_name') or manager.get('name') or manager.get('manager') or ''
                if 'uno14' not in name.lower():
                    deals = manager.get('total_deals') or manager.get('deals') or 0
                    profit = manager.get('total_profit') or manager.get('profit') or 0
                    
                    if deals > 0 or profit != 0:
                        non_zero_managers += 1
            
            if non_zero_managers >= 2:
                self.log_test("Compare Non-UNO14 Stats", "PASS", 
                            f"{non_zero_managers} managers have non-zero stats (confirming UNO14 is special case)")
            else:
                self.log_test("Compare Non-UNO14 Stats", "FAIL", 
                            f"Only {non_zero_managers} managers have non-zero stats (expected at least 2)")
            
            # Summary for Compare Tab
            compare_success = (manager_count == 4 and 
                             uno14_found and 
                             not missing_managers and 
                             uno14_zero_stats if uno14_manager else False)
            
            self.log_test("Compare Tab Summary", "PASS" if compare_success else "FAIL", 
                        f"4 managers: {manager_count==4}, UNO14 found: {uno14_found}, "
                        f"All names found: {not missing_managers}, UNO14 zero stats: {uno14_zero_stats if uno14_manager else False}")
            
            return compare_success
            
        except Exception as e:
            self.log_test("Compare Tab Test", "ERROR", f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all Money Managers endpoint tests"""
        print("🚀 Starting Money Managers Endpoints Testing")
        print("=" * 70)
        print("Testing BOTH Money Managers endpoints after fixes")
        print("Backend URL:", self.base_url)
        print("=" * 70)
        
        # Authenticate first
        if not self.authenticate_admin():
            return {"success": False, "error": "Authentication failed"}
        
        # Run both endpoint tests
        test_results = {
            "overview_tab": self.test_overview_tab_endpoint(),
            "compare_tab": self.test_compare_tab_endpoint()
        }
        
        # Calculate summary
        total_tests = len(test_results)
        passed_tests = sum(1 for result in test_results.values() if result)
        success_rate = (passed_tests / total_tests) * 100
        
        print("\n" + "=" * 70)
        print("📊 MONEY MANAGERS ENDPOINTS TEST SUMMARY")
        print("=" * 70)
        
        for test_name, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            endpoint = "/api/admin/money-managers" if test_name == "overview_tab" else "/api/admin/trading-analytics/managers"
            print(f"{status} {test_name.replace('_', ' ').title()} ({endpoint})")
        
        print(f"\n🎯 Overall Success Rate: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        if success_rate == 100:
            print("🎉 ALL MONEY MANAGERS ENDPOINTS WORKING CORRECTLY!")
            print("✅ Overview: 4 managers with different Initial Allocation vs Current Equity")
            print("✅ Compare: 4 managers including UNO14 with zero stats")
            print("✅ No missing managers in either tab")
        elif success_rate >= 50:
            print("⚠️  Partial success - Some Money Managers endpoint issues remain")
        else:
            print("🚨 CRITICAL ISSUES - Money Managers endpoints have major problems")
        
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
    tester = MoneyManagersTester()
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if results["success"] else 1)

if __name__ == "__main__":
    main()