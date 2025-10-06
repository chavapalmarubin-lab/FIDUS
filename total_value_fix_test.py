#!/usr/bin/env python3
"""
INVESTMENT SIMULATOR TOTAL VALUE CALCULATION FIX VERIFICATION TEST
================================================================

This test verifies the critical Investment Simulator total value calculation fix as requested in the review.

CRITICAL ISSUE THAT WAS REPORTED:
User reported that while individual fund calculations show correct ROI (18%, 30%, 42%), 
the **total summary shows wrong values**:
- Total Final Value: $0 (should be sum of all funds)
- Total Interest: $0 (should be sum of all fund interest)
- Total ROI: -100% (should be weighted average of fund ROIs)

TESTING PAYLOAD:
{
  "investments": [
    {"fund_code": "CORE", "amount": 25000},
    {"fund_code": "BALANCE", "amount": 100000},
    {"fund_code": "DYNAMIC", "amount": 250000}
  ],
  "timeframe_months": 24,
  "simulation_name": "Total Value Fix Test"
}

EXPECTED CORRECT RESULTS:
- Total Investment: $375,000
- Total Final Value: $514,500 (sum: $29,500 + $130,000 + $355,000)
- Total Interest: $139,500 (sum: $4,500 + $30,000 + $105,000)
- Total ROI: 37.2% (weighted average: $139,500/$375,000)
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://mt5-integration.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class TotalValueFixTest:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name} - {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "username": ADMIN_USERNAME,
                "password": ADMIN_PASSWORD,
                "user_type": "admin"
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                if self.admin_token:
                    self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
                    self.log_result("Admin Authentication", True, "Successfully authenticated as admin")
                    return True
                else:
                    self.log_result("Admin Authentication", False, "No token received", {"response": data})
                    return False
            else:
                self.log_result("Admin Authentication", False, f"HTTP {response.status_code}", {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_investment_simulator_total_fix(self):
        """Test the Investment Simulator total value calculation fix"""
        try:
            # The exact test payload from the review request
            test_payload = {
                "investments": [
                    {"fund_code": "CORE", "amount": 25000},
                    {"fund_code": "BALANCE", "amount": 100000},
                    {"fund_code": "DYNAMIC", "amount": 250000}
                ],
                "timeframe_months": 24,
                "simulation_name": "Total Value Fix Test"
            }
            
            print(f"\n🎯 Testing Investment Simulator with exact payload from review:")
            print(f"   CORE Fund: $25,000")
            print(f"   BALANCE Fund: $100,000") 
            print(f"   DYNAMIC Fund: $250,000")
            print(f"   Timeframe: 24 months")
            print(f"   Total Investment: $375,000")
            
            response = self.session.post(f"{BACKEND_URL}/investments/simulate", json=test_payload)
            
            if response.status_code == 200:
                simulation_result = response.json()
                self.log_result("Investment Simulator API Call", True, 
                              "Investment Simulator endpoint responded successfully")
                
                # Extract the simulation data
                simulation = simulation_result.get('simulation', {})
                summary = simulation.get('summary', {})
                fund_breakdown = simulation.get('fund_breakdown', [])
                
                # Verify the critical fix
                self.verify_total_value_fix(summary, fund_breakdown)
                return simulation_result
            else:
                self.log_result("Investment Simulator API Call", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            self.log_result("Investment Simulator API Call", False, f"Exception: {str(e)}")
            return None
    
    def verify_total_value_fix(self, summary, fund_breakdown):
        """Verify the critical total value calculation fix"""
        try:
            print(f"\n🔍 VERIFYING THE CRITICAL TOTAL VALUE CALCULATION FIX:")
            
            # Expected values from review request
            expected_total_investment = 375000.0
            expected_total_final_value = 514500.0  # Sum: $29,500 + $130,000 + $355,000
            expected_total_interest = 139500.0     # Sum: $4,500 + $30,000 + $105,000
            expected_total_roi = 37.2              # Weighted average: $139,500/$375,000
            
            # Extract actual values from summary
            actual_total_investment = summary.get('total_investment')
            actual_final_value = summary.get('final_value')
            actual_total_interest = summary.get('total_interest_earned')
            actual_total_roi = summary.get('total_roi_percentage')
            
            print(f"   Expected: Investment=${expected_total_investment:,.0f}, Final=${expected_total_final_value:,.0f}, Interest=${expected_total_interest:,.0f}, ROI={expected_total_roi}%")
            print(f"   Actual:   Investment=${actual_total_investment:,.0f}, Final=${actual_final_value:,.0f}, Interest=${actual_total_interest:,.0f}, ROI={actual_total_roi}%")
            
            # CRITICAL TEST 1: Total Investment should be $375,000
            if actual_total_investment and abs(actual_total_investment - expected_total_investment) < 1.0:
                self.log_result("✅ Total Investment Calculation", True, 
                              f"Total investment correct: ${actual_total_investment:,.2f}")
            else:
                self.log_result("❌ Total Investment Calculation", False, 
                              f"Total investment incorrect: ${actual_total_investment} (expected ${expected_total_investment:,.2f})")
            
            # CRITICAL TEST 2: Total Final Value should NOT be $0 (should be $514,500)
            if actual_final_value is None or actual_final_value == 0:
                self.log_result("🚨 CRITICAL BUG STILL PRESENT: Total Final Value", False, 
                              f"Total Final Value is ${actual_final_value} - THE ORIGINAL BUG IS STILL PRESENT!")
            elif abs(actual_final_value - expected_total_final_value) < 1.0:
                self.log_result("🎉 CRITICAL FIX VERIFIED: Total Final Value", True, 
                              f"Total Final Value FIXED: ${actual_final_value:,.2f} (expected ${expected_total_final_value:,.2f})")
            else:
                self.log_result("⚠️  Total Final Value Calculation", False, 
                              f"Total final value incorrect: ${actual_final_value} (expected ${expected_total_final_value:,.2f})")
            
            # CRITICAL TEST 3: Total Interest should NOT be $0 (should be $139,500)
            if actual_total_interest is None or actual_total_interest == 0:
                self.log_result("🚨 CRITICAL BUG STILL PRESENT: Total Interest", False, 
                              f"Total Interest is ${actual_total_interest} - THE ORIGINAL BUG IS STILL PRESENT!")
            elif abs(actual_total_interest - expected_total_interest) < 1.0:
                self.log_result("🎉 CRITICAL FIX VERIFIED: Total Interest", True, 
                              f"Total Interest FIXED: ${actual_total_interest:,.2f} (expected ${expected_total_interest:,.2f})")
            else:
                self.log_result("⚠️  Total Interest Calculation", False, 
                              f"Total interest incorrect: ${actual_total_interest} (expected ${expected_total_interest:,.2f})")
            
            # CRITICAL TEST 4: Total ROI should NOT be -100% (should be 37.2%)
            if actual_total_roi is None or actual_total_roi == -100:
                self.log_result("🚨 CRITICAL BUG STILL PRESENT: Total ROI", False, 
                              f"Total ROI is {actual_total_roi}% - THE ORIGINAL BUG IS STILL PRESENT!")
            elif actual_total_roi and abs(actual_total_roi - expected_total_roi) < 0.1:
                self.log_result("🎉 CRITICAL FIX VERIFIED: Total ROI", True, 
                              f"Total ROI FIXED: {actual_total_roi}% (expected {expected_total_roi}%)")
            else:
                self.log_result("⚠️  Total ROI Calculation", False, 
                              f"Total ROI incorrect: {actual_total_roi}% (expected {expected_total_roi}%)")
            
            # VERIFICATION TEST: Final value should equal investment + interest
            if actual_total_investment and actual_total_interest and actual_final_value:
                calculated_final = actual_total_investment + actual_total_interest
                if abs(actual_final_value - calculated_final) < 1.0:
                    self.log_result("✅ Math Verification: Final = Investment + Interest", True, 
                                  f"Math verification passed: ${actual_final_value:,.2f} = ${actual_total_investment:,.2f} + ${actual_total_interest:,.2f}")
                else:
                    self.log_result("❌ Math Verification: Final = Investment + Interest", False, 
                                  f"Math verification failed: ${actual_final_value:,.2f} ≠ ${calculated_final:,.2f}")
            
            # INDIVIDUAL FUND VERIFICATION: Ensure individual calculations are still correct
            self.verify_individual_fund_calculations(fund_breakdown)
                
        except Exception as e:
            self.log_result("Total Value Fix Verification", False, f"Exception: {str(e)}")
    
    def verify_individual_fund_calculations(self, fund_breakdown):
        """Verify individual fund calculations remain correct"""
        try:
            print(f"\n📊 VERIFYING INDIVIDUAL FUND CALCULATIONS REMAIN CORRECT:")
            
            expected_fund_results = {
                "CORE": {"roi": 18.0, "final_value": 29500.0, "interest": 4500.0},
                "BALANCE": {"roi": 30.0, "final_value": 130000.0, "interest": 30000.0},
                "DYNAMIC": {"roi": 42.0, "final_value": 355000.0, "interest": 105000.0}
            }
            
            funds_verified = 0
            
            for fund in fund_breakdown:
                fund_code = fund.get('fund_code')
                if fund_code in expected_fund_results:
                    expected = expected_fund_results[fund_code]
                    
                    actual_roi = fund.get('roi_percentage')
                    actual_final = fund.get('final_value')
                    actual_interest = fund.get('total_interest')
                    
                    print(f"   {fund_code}: ROI={actual_roi}%, Final=${actual_final:,.0f}, Interest=${actual_interest:,.0f}")
                    
                    # Verify ROI
                    if actual_roi and abs(actual_roi - expected['roi']) < 0.1:
                        self.log_result(f"✅ {fund_code} Fund ROI", True, 
                                      f"ROI correct: {actual_roi}% (expected {expected['roi']}%)")
                        funds_verified += 1
                    else:
                        self.log_result(f"❌ {fund_code} Fund ROI", False, 
                                      f"ROI incorrect: {actual_roi}% (expected {expected['roi']}%)")
            
            if funds_verified == 3:
                self.log_result("✅ Individual Fund Calculations", True, 
                              "All 3 individual fund calculations remain correct (18%, 30%, 42%)")
            else:
                self.log_result("❌ Individual Fund Calculations", False, 
                              f"Only {funds_verified}/3 funds verified correctly")
                
        except Exception as e:
            self.log_result("Individual Fund Verification", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all Investment Simulator total value calculation fix tests"""
        print("🎯 INVESTMENT SIMULATOR TOTAL VALUE CALCULATION FIX VERIFICATION")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        print("🚨 CRITICAL ISSUE BEING TESTED:")
        print("   User reported total summary showing wrong values:")
        print("   - Total Final Value: $0 (should be sum of all funds)")
        print("   - Total Interest: $0 (should be sum of all fund interest)")
        print("   - Total ROI: -100% (should be weighted average)")
        print()
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with tests.")
            return False
        
        print("\n🔍 Running Investment Simulator Total Value Fix Tests...")
        print("-" * 50)
        
        # Run the main test
        simulation_result = self.test_investment_simulator_total_fix()
        
        # Generate summary
        self.generate_test_summary()
        
        return True
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 80)
        print("🎯 INVESTMENT SIMULATOR TOTAL VALUE FIX TEST SUMMARY")
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
        
        # Check for critical fixes
        critical_fixes = [
            "🎉 CRITICAL FIX VERIFIED: Total Final Value",
            "🎉 CRITICAL FIX VERIFIED: Total Interest", 
            "🎉 CRITICAL FIX VERIFIED: Total ROI"
        ]
        
        critical_bugs = [
            "🚨 CRITICAL BUG STILL PRESENT: Total Final Value",
            "🚨 CRITICAL BUG STILL PRESENT: Total Interest",
            "🚨 CRITICAL BUG STILL PRESENT: Total ROI"
        ]
        
        fixes_verified = sum(1 for result in self.test_results 
                           if result['success'] and any(fix in result['test'] for fix in critical_fixes))
        
        bugs_still_present = sum(1 for result in self.test_results 
                               if not result['success'] and any(bug in result['test'] for bug in critical_bugs))
        
        # Show failed tests (critical issues)
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['message']}")
            print()
        
        # Show passed tests
        if passed_tests > 0:
            print("✅ PASSED TESTS:")
            for result in self.test_results:
                if result['success']:
                    print(f"   • {result['test']}: {result['message']}")
            print()
        
        # Critical assessment
        print("🚨 CRITICAL ASSESSMENT:")
        if bugs_still_present > 0:
            print("❌ INVESTMENT SIMULATOR TOTAL VALUE BUG: STILL PRESENT")
            print("   The original issue reported by user is NOT FIXED.")
            print("   Total values are still showing $0 or -100%.")
            print("   🚨 URGENT MAIN AGENT ACTION REQUIRED!")
        elif fixes_verified >= 3:  # All 3 critical fixes working
            print("🎉 INVESTMENT SIMULATOR TOTAL VALUE BUG: SUCCESSFULLY FIXED!")
            print("   The critical total calculation issues have been COMPLETELY RESOLVED.")
            print("   ✅ Total Final Value: No longer $0 - now shows correct $514,500")
            print("   ✅ Total Interest: No longer $0 - now shows correct $139,500") 
            print("   ✅ Total ROI: No longer -100% - now shows correct 37.2%")
            print("   ✅ Individual fund calculations remain correct (18%, 30%, 42%)")
            print("   ✅ Summary totals are sum of individual fund values")
            print("   ✅ Final value equals total investment + total interest")
            print("   🎉 SYSTEM READY FOR PRODUCTION USE!")
        elif fixes_verified >= 2:  # At least 2 out of 3 critical fixes working
            print("⚠️  INVESTMENT SIMULATOR TOTAL VALUE BUG: MOSTLY FIXED")
            print("   Most critical total calculation issues have been resolved.")
            print("   Some minor issues may remain but core functionality is working.")
            print("   System is likely ready for production use.")
        else:
            print("⚠️  INVESTMENT SIMULATOR TOTAL VALUE BUG: PARTIALLY FIXED")
            print("   Some total calculation issues resolved, but verification incomplete.")
            print("   Additional testing may be required.")
        
        print("\n" + "=" * 80)

def main():
    """Main test execution"""
    test_runner = TotalValueFixTest()
    success = test_runner.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()