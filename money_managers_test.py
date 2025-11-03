#!/usr/bin/env python3
"""
MONEY MANAGERS COMPARE API ENDPOINT TESTING
Testing Date: December 18, 2025
Backend URL: https://fintech-monitor-2.preview.emergentagent.com/api
Auth: Admin user (username: admin, password: password123)

CRITICAL TEST OBJECTIVES:
1. POST /api/auth/login - Get admin token
2. GET /api/admin/trading-analytics/managers - Test Money Managers endpoint
   - Should return 4 managers: TradingHub Gold, GoldenTrade, UNO14 MAM, CP Strategy
   - Each should have: magic, manager_name, total_deals, total_profit, win_rate
   - Should NOT return "Manager None" or "Manual Trading"
   - Verify total_profit values are NOT all zero

EXPECTED RESULTS:
- 4 managers returned
- Each with non-zero performance metrics
- Proper account aggregation (GoldenTrade should combine accounts 886066 and 891234)

CONTEXT: Implemented workaround to use account_number mapping instead of broken VPS magic numbers.
Need to verify Money Managers Compare tab will now show data.
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional

class MoneyManagersTester:
    def __init__(self):
        self.base_url = "https://fintech-monitor-2.preview.emergentagent.com/api"
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
    
    def test_money_managers_endpoint(self) -> bool:
        """Test Money Managers Compare API endpoint"""
        try:
            print("\n👥 Testing Money Managers Compare API Endpoint...")
            
            response = self.session.get(f"{self.base_url}/admin/trading-analytics/managers")
            
            if response.status_code != 200:
                self.log_test("Money Managers API", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            self.log_test("Money Managers API", "PASS", "Successfully retrieved money managers data")
            
            # Print raw response for debugging
            print(f"\n📋 Raw API Response Structure:")
            print(f"Response keys: {list(data.keys())}")
            
            # Get managers list
            managers = data.get('managers', [])
            
            if not managers:
                self.log_test("Managers List", "FAIL", "No managers found in response")
                return False
            
            print(f"Found {len(managers)} managers in response")
            
            # Expected managers based on review request
            expected_managers = ["TradingHub Gold", "GoldenTrade", "UNO14 MAM", "CP Strategy"]
            excluded_managers = ["Manager None", "Manual Trading"]
            
            # Test 1: Check manager count
            manager_count = len(managers)
            if manager_count == 4:
                self.log_test("Manager Count", "PASS", f"Correct number of managers: {manager_count}")
            else:
                self.log_test("Manager Count", "FAIL", f"Expected 4 managers, got {manager_count}", 4, manager_count)
            
            # Test 2: Analyze each manager
            found_managers = []
            excluded_found = []
            managers_with_data = []
            managers_with_zero_profit = []
            
            for i, manager in enumerate(managers):
                if not isinstance(manager, dict):
                    self.log_test(f"Manager {i+1} Structure", "FAIL", f"Manager is not a dict: {type(manager)}")
                    continue
                
                # Get manager name
                manager_name = manager.get('manager_name', manager.get('name', 'Unknown'))
                found_managers.append(manager_name)
                
                print(f"\n📊 Manager {i+1}: {manager_name}")
                
                # Check required fields
                required_fields = ['magic', 'manager_name', 'total_deals', 'total_profit', 'win_rate']
                missing_fields = []
                
                for field in required_fields:
                    if field not in manager:
                        missing_fields.append(field)
                    else:
                        value = manager[field]
                        print(f"   {field}: {value}")
                
                if missing_fields:
                    self.log_test(f"{manager_name} Required Fields", "FAIL", 
                                f"Missing fields: {missing_fields}")
                else:
                    self.log_test(f"{manager_name} Required Fields", "PASS", 
                                "All required fields present")
                    managers_with_data.append(manager_name)
                
                # Check for excluded managers
                if any(exc in manager_name for exc in excluded_managers):
                    excluded_found.append(manager_name)
                
                # Check total_profit is not zero
                total_profit = manager.get('total_profit', 0)
                if total_profit == 0:
                    managers_with_zero_profit.append(manager_name)
                    self.log_test(f"{manager_name} Profit Check", "FAIL", 
                                f"Total profit is zero: ${total_profit}")
                else:
                    self.log_test(f"{manager_name} Profit Check", "PASS", 
                                f"Non-zero profit: ${total_profit}")
            
            # Test 3: Check for excluded managers
            if excluded_found:
                self.log_test("Excluded Managers Check", "FAIL", 
                            f"Found excluded managers: {excluded_found}", 
                            "No excluded managers", excluded_found)
            else:
                self.log_test("Excluded Managers Check", "PASS", 
                            "No excluded managers (Manual Trading, Manager None) found")
            
            # Test 4: Check for expected managers
            expected_found = []
            for expected in expected_managers:
                for found in found_managers:
                    if expected in found or found in expected:
                        expected_found.append(expected)
                        break
            
            missing_expected = [m for m in expected_managers if m not in expected_found]
            
            if len(expected_found) == 4:
                self.log_test("Expected Managers Check", "PASS", 
                            f"All expected managers found: {expected_found}")
            else:
                self.log_test("Expected Managers Check", "FAIL", 
                            f"Missing expected managers: {missing_expected}", 
                            expected_managers, found_managers)
            
            # Test 5: Check for non-zero profits
            if managers_with_zero_profit:
                self.log_test("Non-Zero Profits Check", "FAIL", 
                            f"Managers with zero profit: {managers_with_zero_profit}")
            else:
                self.log_test("Non-Zero Profits Check", "PASS", 
                            "All managers have non-zero profit values")
            
            # Test 6: Check for GoldenTrade account aggregation
            goldentrade_found = False
            goldentrade_accounts = []
            
            for manager in managers:
                manager_name = manager.get('manager_name', '')
                if 'GoldenTrade' in manager_name:
                    goldentrade_found = True
                    # Check if this manager aggregates multiple accounts
                    total_deals = manager.get('total_deals', 0)
                    accounts = manager.get('accounts', [])
                    
                    if isinstance(accounts, list) and len(accounts) > 1:
                        goldentrade_accounts = accounts
                        self.log_test("GoldenTrade Aggregation", "PASS", 
                                    f"GoldenTrade aggregates {len(accounts)} accounts: {accounts}")
                    else:
                        self.log_test("GoldenTrade Aggregation", "FAIL", 
                                    f"GoldenTrade should aggregate accounts 886066 and 891234")
                    break
            
            if not goldentrade_found:
                self.log_test("GoldenTrade Manager", "FAIL", "GoldenTrade manager not found")
            
            # Overall success calculation
            success_criteria = [
                manager_count == 4,
                len(excluded_found) == 0,
                len(expected_found) == 4,
                len(managers_with_zero_profit) == 0,
                len(managers_with_data) == manager_count
            ]
            
            success_rate = sum(success_criteria) / len(success_criteria) * 100
            overall_success = all(success_criteria)
            
            # Summary
            print(f"\n📋 MONEY MANAGERS TEST SUMMARY:")
            print(f"   Managers Found: {found_managers}")
            print(f"   Expected Managers: {expected_found}")
            print(f"   Excluded Managers: {excluded_found}")
            print(f"   Managers with Zero Profit: {managers_with_zero_profit}")
            print(f"   Success Rate: {success_rate:.1f}%")
            
            self.log_test("Money Managers Overall", "PASS" if overall_success else "FAIL", 
                        f"Overall test success rate: {success_rate:.1f}%")
            
            return overall_success
            
        except Exception as e:
            self.log_test("Money Managers Test", "ERROR", f"Exception: {str(e)}")
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")
            return False
    
    def run_test(self) -> Dict[str, Any]:
        """Run Money Managers test"""
        print("🚀 Starting Money Managers Compare API Endpoint Testing")
        print("=" * 70)
        print("Context: Testing account-based workaround implementation")
        print("Expected: 4 managers with non-zero performance metrics")
        print("=" * 70)
        
        # Authenticate first
        if not self.authenticate_admin():
            return {"success": False, "error": "Authentication failed"}
        
        # Run the test
        test_success = self.test_money_managers_endpoint()
        
        # Calculate summary
        passed_tests = 1 if test_success else 0
        total_tests = 1
        success_rate = (passed_tests / total_tests) * 100
        
        print("\n" + "=" * 70)
        print("📊 FINAL TEST RESULTS")
        print("=" * 70)
        
        status = "✅ PASS" if test_success else "❌ FAIL"
        print(f"{status} Money Managers Compare API Test")
        
        print(f"\n🎯 Overall Success Rate: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        if success_rate == 100:
            print("🎉 MONEY MANAGERS TEST PASSED - Account-based workaround working!")
            print("✅ Money Managers Compare tab should now show data correctly")
        else:
            print("🚨 MONEY MANAGERS TEST FAILED - Issues with account-based workaround")
            print("❌ Money Managers Compare tab may still have data issues")
        
        return {
            "success": test_success,
            "success_rate": success_rate,
            "passed_tests": passed_tests,
            "total_tests": total_tests,
            "detailed_results": self.test_results
        }

def main():
    """Main test execution"""
    tester = MoneyManagersTester()
    results = tester.run_test()
    
    # Exit with appropriate code
    sys.exit(0 if results["success"] else 1)

if __name__ == "__main__":
    main()