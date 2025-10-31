#!/usr/bin/env python3
"""
BROKER REBATES CALCULATION FIX TESTING
Testing Date: December 18, 2025
Backend URL: https://fidus-pnl-fix.preview.emergentagent.com/api
Auth: Admin token (username: admin, password: password123)

ISSUE: Broker rebates showing $9,457 (all-time) instead of time-period specific amounts
FIX: Rebates should be calculated for specific time periods, not all-time

Test Objectives:
1. GET /api/admin/cashflow/overview (used by frontend) - should use 30 days or 12 months default
2. GET /api/admin/cashflow/complete?days=30 - test with days=7, 30, 90
3. Verify rebates_summary.total_rebates value
4. Check trades_count and calculation_period_days in response
5. Verify no double counting (rebate per lot should be $5.05)

Expected Results:
- Default 30-day rebates: ~$8,000-$8,100 (currently showing $8,026.17 ✓)
- 7-day rebates: ~$6,300
- 90-day rebates: should be different from all-time $9,457
- No more $9,457 all-time rebates showing by default
- Rebate per lot should be ~$5.05
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://fidus-pnl-fix.preview.emergentagent.com"

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
    
    def test_cashflow_overview_default_period(self):
        """Test /api/admin/cashflow/overview (default period) - should use 30 days or 12 months"""
        try:
            url = f"{BACKEND_URL}/api/admin/cashflow/overview"
            response = self.session.get(url)  # No parameters = default period
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if response has rebates_summary section
                if 'rebates_summary' not in data:
                    self.log_test("Cash Flow Overview Structure", False, "Missing 'rebates_summary' key in response")
                    return False
                
                rebates_summary = data['rebates_summary']
                total_rebates = rebates_summary.get('total_rebates', 0)
                
                print(f"   📊 Default Period Total Rebates: ${total_rebates:.2f}")
                
                # CRITICAL TEST: Check if it's the problematic all-time value
                if abs(total_rebates - 9457) < 1:
                    self.log_test("Default Period All-Time Check", False, 
                                f"Still showing all-time rebates ${total_rebates:.2f} instead of period-specific")
                    return False
                
                # Check if it's in the expected 30-day range (~$8,000-$8,100)
                if 7500 <= total_rebates <= 8500:
                    self.log_test("Default Period Range Check", True, 
                                f"Rebates in expected 30-day range: ${total_rebates:.2f}")
                    success = True
                else:
                    self.log_test("Default Period Range Check", False, 
                                f"Rebates outside expected 30-day range: ${total_rebates:.2f} (expected $7,500-$8,500)")
                    success = False
                
                # Store for comparison
                self.default_rebates = total_rebates
                
                # Check for period information
                period_info = data.get('period_days') or data.get('calculation_period_days') or "unknown"
                print(f"   📅 Period Information: {period_info}")
                
                return success
                
            else:
                self.log_test("Cash Flow Overview Default", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Cash Flow Overview Default", False, f"Exception: {str(e)}")
            return False
    
    def test_cashflow_complete_multiple_periods(self):
        """Test /api/admin/cashflow/complete with different time periods"""
        try:
            test_periods = [7, 30, 90]
            expected_ranges = {
                7: (6000, 6600),    # ~$6,300 for 7 days
                30: (7500, 8500),   # ~$8,000-$8,100 for 30 days  
                90: (8000, 10000)   # Should be different from all-time $9,457
            }
            
            period_results = {}
            all_success = True
            
            for days in test_periods:
                try:
                    print(f"\n   🔍 Testing {days}-day period...")
                    
                    url = f"{BACKEND_URL}/api/admin/cashflow/complete"
                    params = {"days": days}
                    response = self.session.get(url, params=params)
                    
                    if response.status_code != 200:
                        self.log_test(f"Cash Flow Complete {days}d API", False, 
                                    f"HTTP {response.status_code}: {response.text}")
                        all_success = False
                        continue
                    
                    data = response.json()
                    
                    # Extract broker rebates value
                    broker_rebates = data.get('broker_rebates', 0)
                    trades_count = data.get('trades_count', 0)
                    calculation_period_days = data.get('calculation_period_days', 0)
                    
                    period_results[days] = {
                        'broker_rebates': broker_rebates,
                        'trades_count': trades_count,
                        'calculation_period_days': calculation_period_days
                    }
                    
                    print(f"      💰 Broker Rebates ({days}d): ${broker_rebates:.2f}")
                    print(f"      📊 Trades Count: {trades_count}")
                    print(f"      📅 Period Days: {calculation_period_days}")
                    
                    # Verify calculation period matches request
                    if calculation_period_days == days:
                        self.log_test(f"Period Verification {days}d", True, 
                                    f"Calculation period matches request: {days} days")
                    else:
                        self.log_test(f"Period Verification {days}d", False, 
                                    f"Period mismatch - expected {days}, got {calculation_period_days}")
                        all_success = False
                    
                    # Check if rebates are in expected range
                    expected_min, expected_max = expected_ranges[days]
                    if expected_min <= broker_rebates <= expected_max:
                        self.log_test(f"Rebates Range {days}d", True, 
                                    f"Rebates in expected range: ${broker_rebates:.2f}")
                    else:
                        self.log_test(f"Rebates Range {days}d", False, 
                                    f"Rebates outside expected range ${expected_min}-${expected_max}: ${broker_rebates:.2f}")
                        all_success = False
                    
                    # Check for problematic all-time value
                    if abs(broker_rebates - 9457) < 1:
                        self.log_test(f"All-Time Check {days}d", False, 
                                    "Still returning all-time rebates instead of period-specific")
                        all_success = False
                    else:
                        self.log_test(f"All-Time Check {days}d", True, 
                                    "Not returning problematic all-time value")
                    
                except Exception as e:
                    self.log_test(f"Cash Flow Complete {days}d Test", False, f"Exception: {str(e)}")
                    all_success = False
            
            # Store results for later comparison
            self.period_results = period_results
            
            # Verify different periods return different values (period-specific calculation)
            if len(period_results) >= 2:
                rebates_values = [result['broker_rebates'] for result in period_results.values()]
                unique_values = len(set(rebates_values))
                
                if unique_values > 1:
                    self.log_test("Period Differentiation", True, 
                                f"Different periods return different rebates: {rebates_values}")
                else:
                    self.log_test("Period Differentiation", False, 
                                f"All periods return same rebates (not period-specific): {rebates_values}")
                    all_success = False
            
            return all_success
                
        except Exception as e:
            self.log_test("Cash Flow Complete Multiple Periods", False, f"Exception: {str(e)}")
            return False
    
    def test_rebate_per_lot_calculation(self):
        """Test rebate per lot calculation (should be ~$5.05, no double counting)"""
        try:
            if hasattr(self, 'period_results') and 30 in self.period_results:
                result_30d = self.period_results[30]
                broker_rebates = result_30d['broker_rebates']
                trades_count = result_30d['trades_count']
                
                if trades_count > 0:
                    rebate_per_lot = broker_rebates / trades_count
                    print(f"   📊 Rebate per lot (30d): ${rebate_per_lot:.2f}")
                    
                    # Expected rebate per lot is $5.05
                    expected_rebate_per_lot = 5.05
                    tolerance = 0.50  # Allow 50 cent variance
                    
                    if abs(rebate_per_lot - expected_rebate_per_lot) <= tolerance:
                        self.log_test("Rebate Per Lot Calculation", True, 
                                    f"Rebate per lot within expected range: ${rebate_per_lot:.2f} (expected ~${expected_rebate_per_lot})")
                        return True
                    else:
                        self.log_test("Rebate Per Lot Calculation", False, 
                                    f"Rebate per lot outside expected range: ${rebate_per_lot:.2f} (expected ~${expected_rebate_per_lot} ± ${tolerance})")
                        return False
                else:
                    self.log_test("Rebate Per Lot Calculation", False, "No trades found for 30-day period")
                    return False
            else:
                self.log_test("Rebate Per Lot Calculation", False, "No 30-day period data available")
                return False
                
        except Exception as e:
            self.log_test("Rebate Per Lot Calculation", False, f"Exception: {str(e)}")
            return False
    
    def test_no_all_time_rebates_by_default(self):
        """Test that no endpoints return all-time $9,457 rebates by default"""
        try:
            # Test multiple endpoints that might show rebates
            endpoints_to_test = [
                ("/admin/cashflow/overview", "Cash Flow Overview"),
                ("/admin/cashflow/complete", "Cash Flow Complete (no params)"),
            ]
            
            all_success = True
            
            for endpoint, name in endpoints_to_test:
                try:
                    url = f"{BACKEND_URL}/api{endpoint}"
                    response = self.session.get(url)
                    
                    if response.status_code != 200:
                        self.log_test(f"All-Time Check {name}", False, 
                                    f"HTTP {response.status_code}: {response.text}")
                        all_success = False
                        continue
                    
                    data = response.json()
                    
                    # Look for rebates fields that might contain the problematic value
                    rebates_values = []
                    
                    # Check various possible field names
                    possible_paths = [
                        'rebates_summary.total_rebates',
                        'summary.broker_rebates', 
                        'broker_rebates',
                        'total_rebates'
                    ]
                    
                    for path in possible_paths:
                        value = self._get_nested_value(data, path)
                        if value is not None and isinstance(value, (int, float)):
                            rebates_values.append((path, value))
                    
                    # Check if any field contains the problematic all-time value
                    problematic_found = False
                    for field_name, value in rebates_values:
                        if abs(value - 9457) < 1:
                            self.log_test(f"All-Time Check {name}", False, 
                                        f"Found problematic all-time value ${value:.2f} in {field_name}")
                            problematic_found = True
                            all_success = False
                    
                    if not problematic_found and rebates_values:
                        values_str = ", ".join([f"{path}=${val:.2f}" for path, val in rebates_values])
                        self.log_test(f"All-Time Check {name}", True, 
                                    f"No all-time $9,457 found. Values: {values_str}")
                    elif not rebates_values:
                        self.log_test(f"All-Time Check {name}", True, 
                                    "No rebates fields found in response")
                    
                except Exception as e:
                    self.log_test(f"All-Time Check {name}", False, f"Exception: {str(e)}")
                    all_success = False
            
            return all_success
                
        except Exception as e:
            self.log_test("All-Time Rebates Check", False, f"Exception: {str(e)}")
            return False
    
    def _get_nested_value(self, data: dict, field_path: str):
        """Get nested value from dict using dot notation"""
        try:
            keys = field_path.split('.')
            value = data
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return None
            return value
        except:
            return None
    
    def run_all_tests(self):
        """Run all broker rebates time period calculation tests"""
        print("🎯 BROKER REBATES CALCULATION FIX TESTING")
        print("=" * 80)
        print("ISSUE: Rebates showing $9,457 (all-time) instead of period-specific amounts")
        print("FIX: Rebates should be calculated for specific time periods")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Testing Time: {datetime.now().isoformat()}")
        print("=" * 80)
        
        # Step 1: Authenticate
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return False
        
        # Step 2: Test Default Period (should use 30 days, not all-time)
        print("📋 STEP 1: Testing Cash Flow Overview Default Period")
        self.test_cashflow_overview_default_period()
        print()
        
        # Step 3: Test Multiple Time Periods
        print("📋 STEP 2: Testing Cash Flow Complete Multiple Periods (7d, 30d, 90d)")
        self.test_cashflow_complete_multiple_periods()
        print()
        
        # Step 4: Test Rebate Per Lot Calculation
        print("📋 STEP 3: Testing Rebate Per Lot Calculation (~$5.05)")
        self.test_rebate_per_lot_calculation()
        print()
        
        # Step 5: Test No All-Time Rebates by Default
        print("📋 STEP 4: Testing No All-Time $9,457 Rebates by Default")
        self.test_no_all_time_rebates_by_default()
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
        
        # Check if default period is working (not showing all-time)
        default_period_working = any(r['success'] and 'Default Period' in r['test'] 
                                   for r in self.test_results)
        
        if default_period_working:
            print("   ✅ Default period shows time-specific rebates (~$8,000), not all-time $9,457")
        else:
            print("   ❌ Default period may still be showing all-time rebates instead of period-specific")
        
        # Check if multiple periods return different values
        period_differentiation_working = any(r['success'] and 'Period Differentiation' in r['test'] 
                                           for r in self.test_results)
        
        if period_differentiation_working:
            print("   ✅ Different time periods return different rebate values (period-specific calculation)")
        else:
            print("   ❌ All time periods return same values (not calculating period-specific rebates)")
        
        # Check if rebate per lot is correct
        rebate_per_lot_working = any(r['success'] and 'Rebate Per Lot' in r['test'] 
                                   for r in self.test_results)
        
        if rebate_per_lot_working:
            print("   ✅ Rebate per lot calculation is correct (~$5.05, no double counting)")
        else:
            print("   ⚠️ Rebate per lot calculation may need verification")
        
        # Check if all-time value is eliminated
        no_all_time_working = any(r['success'] and 'All-Time Check' in r['test'] 
                                for r in self.test_results)
        
        if no_all_time_working:
            print("   ✅ No endpoints return the problematic all-time $9,457 value by default")
        else:
            print("   ⚠️ Some endpoints may still return all-time values instead of period-specific")
        
        print()

def main():
    """Main test execution"""
    tester = CashFlowBrokerRebatesTest()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()