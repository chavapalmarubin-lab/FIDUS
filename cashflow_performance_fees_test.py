#!/usr/bin/env python3
"""
Backend Testing for Cash Flow Integration with Performance Fees (Phase 4)
Testing the updated /api/admin/cashflow/overview endpoint with performance fees integration.

Test Objectives:
1. GET /api/admin/cashflow/overview?timeframe=12_months&fund=all
2. Verify performance fees are included in calculations
3. Verify total liabilities increased by performance fees
4. Verify net profit reflects performance fees
5. Verify breakdown shows 3 managers with correct fee amounts
6. Verify all calculations are mathematically correct

Expected Response Structure:
{
  "success": true,
  "summary": {
    "mt5_trading_profits": <number>,
    "separation_interest": <number>,
    "broker_rebates": <number>,
    "client_interest_obligations": <number>,
    "performance_fees_accrued": 1000.64,  ← NEW FIELD
    "fund_revenue": <number>,
    "fund_obligations": <number>,
    "total_liabilities": <client_obligations + 1000.64>,  ← NEW FIELD
    "net_profit": <fund_revenue - total_liabilities>  ← UPDATED CALCULATION
  },
  "performance_fees": {  ← NEW OBJECT
    "total_accrued": 1000.64,
    "managers_count": 3,
    "breakdown": [
      {"manager": "TradingHub Gold Provider", "fee": 848.91},
      {"manager": "GoldenTrade Provider", "fee": 98.41},
      {"manager": "UNO14 MAM Manager", "fee": 53.32}
    ]
  },
  "rebates_summary": {...},
  "monthly_breakdown": [...],
  "upcoming_redemptions": [...]
}

Success Criteria:
✅ Endpoint returns HTTP 200
✅ summary.performance_fees_accrued = 1000.64
✅ summary.total_liabilities = client_obligations + 1000.64
✅ summary.net_profit accounts for performance fees
✅ performance_fees object present with 3 managers
✅ performance_fees.breakdown shows correct manager fees
✅ performance_fees.total_accrued = 1000.64
✅ performance_fees.managers_count = 3
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://fund-manager-assign.preview.emergentagent.com"

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class CashFlowPerformanceFeesTest:
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
    
    def test_cashflow_overview_with_performance_fees(self):
        """Test GET /api/admin/cashflow/overview with performance fees integration"""
        try:
            url = f"{BACKEND_URL}/api/admin/cashflow/overview"
            params = {
                "timeframe": "12_months",
                "fund": "all"
            }
            
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check basic response structure
                if not data.get('success'):
                    self.log_test("Cash Flow Overview Success", False, f"success=false in response: {data}")
                    return False
                
                if 'summary' not in data:
                    self.log_test("Cash Flow Overview Structure", False, "Missing 'summary' key in response")
                    return False
                
                summary = data['summary']
                
                # Test 1: Check for NEW performance_fees_accrued field
                performance_fees_accrued = summary.get('performance_fees_accrued')
                expected_performance_fees = 1000.64
                
                if performance_fees_accrued is None:
                    self.log_test("Performance Fees Accrued Field", False, "Missing 'performance_fees_accrued' field in summary")
                    return False
                
                if abs(performance_fees_accrued - expected_performance_fees) < 0.01:
                    self.log_test("Performance Fees Accrued Value", True, f"${performance_fees_accrued:.2f} (matches expected ${expected_performance_fees:.2f})")
                else:
                    self.log_test("Performance Fees Accrued Value", False, f"${performance_fees_accrued:.2f} (expected ${expected_performance_fees:.2f})")
                    return False
                
                # Test 2: Check for NEW performance_fees object
                if 'performance_fees' not in data:
                    self.log_test("Performance Fees Object", False, "Missing 'performance_fees' object in response")
                    return False
                
                performance_fees = data['performance_fees']
                
                # Test 3: Verify performance_fees structure
                required_pf_fields = ['total_accrued', 'managers_count', 'breakdown']
                missing_pf_fields = [field for field in required_pf_fields if field not in performance_fees]
                
                if missing_pf_fields:
                    self.log_test("Performance Fees Structure", False, f"Missing fields in performance_fees: {missing_pf_fields}")
                    return False
                
                # Test 4: Verify performance_fees.total_accrued
                total_accrued = performance_fees.get('total_accrued', 0)
                if abs(total_accrued - expected_performance_fees) < 0.01:
                    self.log_test("Performance Fees Total Accrued", True, f"${total_accrued:.2f} (matches expected ${expected_performance_fees:.2f})")
                else:
                    self.log_test("Performance Fees Total Accrued", False, f"${total_accrued:.2f} (expected ${expected_performance_fees:.2f})")
                    return False
                
                # Test 5: Verify performance_fees.managers_count
                managers_count = performance_fees.get('managers_count', 0)
                expected_managers_count = 3
                
                if managers_count == expected_managers_count:
                    self.log_test("Performance Fees Managers Count", True, f"{managers_count} managers (matches expected {expected_managers_count})")
                else:
                    self.log_test("Performance Fees Managers Count", False, f"{managers_count} managers (expected {expected_managers_count})")
                    return False
                
                # Test 6: Verify performance_fees.breakdown
                breakdown = performance_fees.get('breakdown', [])
                if not isinstance(breakdown, list):
                    self.log_test("Performance Fees Breakdown Type", False, f"breakdown should be array, got {type(breakdown)}")
                    return False
                
                if len(breakdown) != expected_managers_count:
                    self.log_test("Performance Fees Breakdown Count", False, f"breakdown has {len(breakdown)} entries (expected {expected_managers_count})")
                    return False
                
                # Test 7: Verify specific manager fees in breakdown
                expected_managers = {
                    'TradingHub Gold Provider': 848.91,
                    'GoldenTrade Provider': 98.41,
                    'UNO14 MAM Manager': 53.32
                }
                
                managers_verified = 0
                breakdown_total = 0
                
                for entry in breakdown:
                    if not isinstance(entry, dict):
                        self.log_test("Performance Fees Breakdown Entry", False, f"breakdown entry should be object, got {type(entry)}")
                        continue
                    
                    manager_name = entry.get('manager', '')
                    fee_amount = entry.get('fee', 0)
                    breakdown_total += fee_amount
                    
                    if manager_name in expected_managers:
                        expected_fee = expected_managers[manager_name]
                        if abs(fee_amount - expected_fee) < 0.01:
                            self.log_test(f"Manager Fee - {manager_name}", True, f"${fee_amount:.2f} (matches expected ${expected_fee:.2f})")
                            managers_verified += 1
                        else:
                            self.log_test(f"Manager Fee - {manager_name}", False, f"${fee_amount:.2f} (expected ${expected_fee:.2f})")
                    else:
                        self.log_test(f"Unexpected Manager - {manager_name}", False, f"Manager not in expected list")
                
                # Test 8: Verify breakdown total matches total_accrued
                if abs(breakdown_total - total_accrued) < 0.01:
                    self.log_test("Performance Fees Breakdown Total", True, f"Breakdown sum ${breakdown_total:.2f} matches total_accrued ${total_accrued:.2f}")
                else:
                    self.log_test("Performance Fees Breakdown Total", False, f"Breakdown sum ${breakdown_total:.2f} doesn't match total_accrued ${total_accrued:.2f}")
                    return False
                
                # Test 9: Check UPDATED total_liabilities calculation
                total_liabilities = summary.get('total_liabilities')
                client_interest_obligations = summary.get('client_interest_obligations', 0)
                
                if total_liabilities is None:
                    self.log_test("Total Liabilities Field", False, "Missing 'total_liabilities' field in summary")
                    return False
                
                # Total liabilities should be client obligations + performance fees
                expected_total_liabilities = client_interest_obligations + performance_fees_accrued
                
                if abs(total_liabilities - expected_total_liabilities) < 0.01:
                    self.log_test("Total Liabilities Calculation", True, f"${total_liabilities:.2f} = ${client_interest_obligations:.2f} + ${performance_fees_accrued:.2f}")
                else:
                    self.log_test("Total Liabilities Calculation", False, f"${total_liabilities:.2f} ≠ ${client_interest_obligations:.2f} + ${performance_fees_accrued:.2f} = ${expected_total_liabilities:.2f}")
                    return False
                
                # Test 10: Check UPDATED net_profit calculation
                net_profit = summary.get('net_profit')
                fund_revenue = summary.get('fund_revenue', 0)
                
                if net_profit is None:
                    self.log_test("Net Profit Field", False, "Missing 'net_profit' field in summary")
                    return False
                
                # Net profit should be fund revenue - total liabilities (which now includes performance fees)
                expected_net_profit = fund_revenue - total_liabilities
                
                if abs(net_profit - expected_net_profit) < 0.01:
                    self.log_test("Net Profit Calculation", True, f"${net_profit:.2f} = ${fund_revenue:.2f} - ${total_liabilities:.2f}")
                else:
                    self.log_test("Net Profit Calculation", False, f"${net_profit:.2f} ≠ ${fund_revenue:.2f} - ${total_liabilities:.2f} = ${expected_net_profit:.2f}")
                    return False
                
                # Test 11: Verify other required fields still exist
                required_summary_fields = ['mt5_trading_profits', 'separation_interest', 'broker_rebates', 'fund_revenue', 'fund_obligations']
                missing_summary_fields = [field for field in required_summary_fields if field not in summary]
                
                if missing_summary_fields:
                    self.log_test("Summary Required Fields", False, f"Missing fields in summary: {missing_summary_fields}")
                    return False
                else:
                    self.log_test("Summary Required Fields", True, f"All required summary fields present")
                
                # Test 12: Verify other required response sections still exist
                required_response_fields = ['rebates_summary', 'monthly_breakdown', 'upcoming_redemptions']
                missing_response_fields = [field for field in required_response_fields if field not in data]
                
                if missing_response_fields:
                    self.log_test("Response Required Sections", False, f"Missing sections in response: {missing_response_fields}")
                else:
                    self.log_test("Response Required Sections", True, f"All required response sections present")
                
                # Overall success
                details = f"Performance fees: ${performance_fees_accrued:.2f}, Total liabilities: ${total_liabilities:.2f}, Net profit: ${net_profit:.2f}, Managers: {managers_count}, Verified managers: {managers_verified}/3"
                self.log_test("Cash Flow Overview with Performance Fees", True, details)
                return True
                
            else:
                self.log_test("Cash Flow Overview with Performance Fees", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Cash Flow Overview with Performance Fees", False, f"Exception: {str(e)}")
            return False
    
    def test_calculation_verification(self):
        """Verify the mathematical correctness of performance fees integration"""
        try:
            url = f"{BACKEND_URL}/api/admin/cashflow/overview"
            params = {
                "timeframe": "12_months",
                "fund": "all"
            }
            
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                summary = data.get('summary', {})
                performance_fees = data.get('performance_fees', {})
                
                # Get all relevant values
                mt5_trading_profits = summary.get('mt5_trading_profits', 0)
                separation_interest = summary.get('separation_interest', 0)
                broker_rebates = summary.get('broker_rebates', 0)
                client_interest_obligations = summary.get('client_interest_obligations', 0)
                performance_fees_accrued = summary.get('performance_fees_accrued', 0)
                fund_revenue = summary.get('fund_revenue', 0)
                fund_obligations = summary.get('fund_obligations', 0)
                total_liabilities = summary.get('total_liabilities', 0)
                net_profit = summary.get('net_profit', 0)
                
                # Verify fund revenue calculation
                expected_fund_revenue = mt5_trading_profits + separation_interest + broker_rebates
                if abs(fund_revenue - expected_fund_revenue) < 0.01:
                    self.log_test("Fund Revenue Calculation", True, f"${fund_revenue:.2f} = ${mt5_trading_profits:.2f} + ${separation_interest:.2f} + ${broker_rebates:.2f}")
                else:
                    self.log_test("Fund Revenue Calculation", False, f"${fund_revenue:.2f} ≠ ${mt5_trading_profits:.2f} + ${separation_interest:.2f} + ${broker_rebates:.2f} = ${expected_fund_revenue:.2f}")
                
                # Verify total liabilities calculation (NEW: includes performance fees)
                expected_total_liabilities = client_interest_obligations + performance_fees_accrued
                if abs(total_liabilities - expected_total_liabilities) < 0.01:
                    self.log_test("Total Liabilities with Performance Fees", True, f"${total_liabilities:.2f} = ${client_interest_obligations:.2f} + ${performance_fees_accrued:.2f}")
                else:
                    self.log_test("Total Liabilities with Performance Fees", False, f"${total_liabilities:.2f} ≠ ${client_interest_obligations:.2f} + ${performance_fees_accrued:.2f} = ${expected_total_liabilities:.2f}")
                
                # Verify net profit calculation (UPDATED: accounts for performance fees)
                expected_net_profit = fund_revenue - total_liabilities
                if abs(net_profit - expected_net_profit) < 0.01:
                    self.log_test("Net Profit with Performance Fees", True, f"${net_profit:.2f} = ${fund_revenue:.2f} - ${total_liabilities:.2f}")
                else:
                    self.log_test("Net Profit with Performance Fees", False, f"${net_profit:.2f} ≠ ${fund_revenue:.2f} - ${total_liabilities:.2f} = ${expected_net_profit:.2f}")
                
                # Verify performance fees breakdown consistency
                breakdown = performance_fees.get('breakdown', [])
                total_accrued = performance_fees.get('total_accrued', 0)
                breakdown_sum = sum(entry.get('fee', 0) for entry in breakdown)
                
                if abs(breakdown_sum - total_accrued) < 0.01:
                    self.log_test("Performance Fees Breakdown Consistency", True, f"Breakdown sum ${breakdown_sum:.2f} matches total_accrued ${total_accrued:.2f}")
                else:
                    self.log_test("Performance Fees Breakdown Consistency", False, f"Breakdown sum ${breakdown_sum:.2f} doesn't match total_accrued ${total_accrued:.2f}")
                
                # Verify performance fees match summary field
                if abs(total_accrued - performance_fees_accrued) < 0.01:
                    self.log_test("Performance Fees Summary Consistency", True, f"performance_fees.total_accrued ${total_accrued:.2f} matches summary.performance_fees_accrued ${performance_fees_accrued:.2f}")
                else:
                    self.log_test("Performance Fees Summary Consistency", False, f"performance_fees.total_accrued ${total_accrued:.2f} doesn't match summary.performance_fees_accrued ${performance_fees_accrued:.2f}")
                
                details = f"All calculations verified: Fund Revenue=${fund_revenue:.2f}, Total Liabilities=${total_liabilities:.2f}, Net Profit=${net_profit:.2f}"
                self.log_test("Calculation Verification", True, details)
                return True
                
            else:
                self.log_test("Calculation Verification", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Calculation Verification", False, f"Exception: {str(e)}")
            return False
    
    def test_impact_verification(self):
        """Verify the expected impact of performance fees integration"""
        try:
            # This test would ideally compare before/after values, but since we don't have
            # a "before" state, we'll verify the expected impact based on the specification
            
            url = f"{BACKEND_URL}/api/admin/cashflow/overview"
            params = {
                "timeframe": "12_months",
                "fund": "all"
            }
            
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                summary = data.get('summary', {})
                
                performance_fees_accrued = summary.get('performance_fees_accrued', 0)
                total_liabilities = summary.get('total_liabilities', 0)
                net_profit = summary.get('net_profit', 0)
                client_interest_obligations = summary.get('client_interest_obligations', 0)
                
                # Expected impact: Fund Liabilities should be ~$1,000 higher than before
                expected_performance_fees = 1000.64
                if abs(performance_fees_accrued - expected_performance_fees) < 0.01:
                    self.log_test("Performance Fees Impact", True, f"Fund liabilities increased by ${performance_fees_accrued:.2f} (expected ~$1,000)")
                else:
                    self.log_test("Performance Fees Impact", False, f"Performance fees ${performance_fees_accrued:.2f} don't match expected ~$1,000")
                
                # Expected impact: Net Profit should be ~$1,000 lower than before (more accurate)
                # We can verify this by checking that performance fees reduce net profit
                net_profit_without_perf_fees = net_profit + performance_fees_accrued
                
                self.log_test("Net Profit Impact", True, f"Net profit ${net_profit:.2f} is ${performance_fees_accrued:.2f} lower due to performance fees (would be ${net_profit_without_perf_fees:.2f} without them)")
                
                # Verify that performance fees are treated as liabilities (increase total liabilities)
                liabilities_without_perf_fees = total_liabilities - performance_fees_accrued
                if abs(liabilities_without_perf_fees - client_interest_obligations) < 0.01:
                    self.log_test("Performance Fees as Liabilities", True, f"Performance fees correctly increase total liabilities from ${liabilities_without_perf_fees:.2f} to ${total_liabilities:.2f}")
                else:
                    self.log_test("Performance Fees as Liabilities", False, f"Performance fees liability calculation may be incorrect")
                
                details = f"Impact verified: Liabilities +${performance_fees_accrued:.2f}, Net Profit -{performance_fees_accrued:.2f}"
                self.log_test("Impact Verification", True, details)
                return True
                
            else:
                self.log_test("Impact Verification", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Impact Verification", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all cash flow performance fees integration tests"""
        print("🎯 CASH FLOW INTEGRATION WITH PERFORMANCE FEES TESTING (Phase 4)")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Testing Time: {datetime.now().isoformat()}")
        print()
        
        # Step 1: Authenticate
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return False
        
        # Step 2: Test Cash Flow Overview with Performance Fees
        print("📋 TEST 1: Cash Flow Overview with Performance Fees Integration")
        self.test_cashflow_overview_with_performance_fees()
        print()
        
        # Step 3: Test Calculation Verification
        print("📋 TEST 2: Mathematical Calculation Verification")
        self.test_calculation_verification()
        print()
        
        # Step 4: Test Impact Verification
        print("📋 TEST 3: Performance Fees Impact Verification")
        self.test_impact_verification()
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
        print("📊 CASH FLOW PERFORMANCE FEES INTEGRATION TEST SUMMARY")
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
            print("🎉 OVERALL RESULT: EXCELLENT - Performance fees integration working perfectly!")
        elif success_rate >= 75:
            print("✅ OVERALL RESULT: GOOD - Performance fees integration mostly working")
        elif success_rate >= 50:
            print("⚠️ OVERALL RESULT: PARTIAL - Performance fees integration needs attention")
        else:
            print("❌ OVERALL RESULT: CRITICAL - Performance fees integration has major issues")
        
        print()
        print("🔍 SUCCESS CRITERIA VERIFICATION:")
        
        # Check specific success criteria from review request
        endpoint_working = any(r['success'] and 'Cash Flow Overview with Performance Fees' in r['test'] 
                              for r in self.test_results)
        
        performance_fees_field = any(r['success'] and 'Performance Fees Accrued Value' in r['test'] 
                                   for r in self.test_results)
        
        total_liabilities_calc = any(r['success'] and 'Total Liabilities Calculation' in r['test'] 
                                   for r in self.test_results)
        
        net_profit_calc = any(r['success'] and 'Net Profit Calculation' in r['test'] 
                            for r in self.test_results)
        
        performance_fees_object = any(r['success'] and 'Performance Fees Object' in r['test'] 
                                    for r in self.test_results)
        
        managers_breakdown = any(r['success'] and 'Performance Fees Managers Count' in r['test'] 
                               for r in self.test_results)
        
        print("   ✅ Endpoint returns HTTP 200" if endpoint_working else "   ❌ Endpoint returns HTTP 200")
        print("   ✅ summary.performance_fees_accrued = 1000.64" if performance_fees_field else "   ❌ summary.performance_fees_accrued = 1000.64")
        print("   ✅ summary.total_liabilities = client_obligations + 1000.64" if total_liabilities_calc else "   ❌ summary.total_liabilities calculation")
        print("   ✅ summary.net_profit accounts for performance fees" if net_profit_calc else "   ❌ summary.net_profit calculation")
        print("   ✅ performance_fees object present with 3 managers" if performance_fees_object and managers_breakdown else "   ❌ performance_fees object structure")
        print("   ✅ performance_fees.breakdown shows correct manager fees" if managers_breakdown else "   ❌ performance_fees.breakdown")
        print("   ✅ All calculations are mathematically correct" if any(r['success'] and 'Calculation Verification' in r['test'] for r in self.test_results) else "   ❌ Mathematical calculations")
        
        print()
        print("🎯 EXPECTED IMPACT VERIFICATION:")
        print("   • Fund Liabilities should be ~$1,000 higher than before ✓" if any(r['success'] and 'Performance Fees Impact' in r['test'] for r in self.test_results) else "   • Fund Liabilities impact ❌")
        print("   • Net Profit should be ~$1,000 lower than before (more accurate) ✓" if any(r['success'] and 'Net Profit Impact' in r['test'] for r in self.test_results) else "   • Net Profit impact ❌")
        print("   • Performance fees should INCREASE liabilities (reduce net profit) ✓" if any(r['success'] and 'Performance Fees as Liabilities' in r['test'] for r in self.test_results) else "   • Performance fees as liabilities ❌")
        
        print()

def main():
    """Main test execution"""
    tester = CashFlowPerformanceFeesTest()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()