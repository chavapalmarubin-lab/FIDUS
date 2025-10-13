#!/usr/bin/env python3
"""
Backend Testing for Cash Flow Broker Rebates Fix
Testing the fixed /api/admin/cashflow/overview endpoint after broker rebates integration.
Previously hardcoded to return broker_rebates: 0.0, now fetches actual rebates from RebateCalculator.

Test Objectives:
1. Test /api/admin/cashflow/overview - Should return broker_rebates = 291.44 (NOT 0.0)
2. Test /api/mt5/fund-performance/corrected - Should return consistent broker_rebates value
3. Verify rebates_summary object is present in response
4. Verify fund_revenue and net_profit calculations include broker rebates
5. Test response structure matches expected format

Expected Results:
- summary.broker_rebates should be 291.44 (NOT 0.0)
- rebates_summary.total_rebates should be 291.44
- rebates_summary.total_volume should show trading volume in lots
- summary.fund_revenue should include broker rebates in calculation
- summary.net_profit should include broker rebates
- Both endpoints should return consistent broker rebates values
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://cashflow-manager-35.preview.emergentagent.com"

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
                
                # Store for consistency check
                self.cashflow_broker_rebates = broker_rebates
                
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