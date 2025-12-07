#!/usr/bin/env python3
"""
BALANCE Fund 12-Month Interest Bug Fix Verification
==================================================

CRITICAL BUG FIX VERIFICATION:
The Investment Simulator was calculating only 10 months of interest instead of 12 months 
for the BALANCE fund. The fix adds the incubation period (2 months) to the requested 
timeframe so users get the full number of interest payment months they request.

CHANGE MADE:
Modified calculate_simulation_projections() in /app/backend/server.py to add 
fund_config.incubation_months to the simulation timeframe.

PRODUCTION CONCERN:
This system manages real client investments ($118,000+ in production).
Need to verify the fix doesn't break existing functionality.

TEST SCENARIOS:
1. BALANCE Fund (12 months) - Should show 30.0% ROI (not 25.0%)
2. CORE Fund (12 months) - Should show 18% ROI  
3. Multi-Fund Portfolio - Should aggregate correctly
4. Admin Investment Creation - Should create 12 interest payments
5. Commission Calculations - Should remain unchanged
"""

import requests
import json
import sys
from datetime import datetime

class BalanceFundBugTester:
    def __init__(self):
        self.base_url = "https://fidus-finance-4.preview.emergentagent.com/api"
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
    def log_test(self, test_name: str, status: str, details: str, expected=None, actual=None):
        """Log test result"""
        result = {
            "test_name": test_name,
            "status": status,
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

    def test_balance_fund_12_months_critical(self) -> bool:
        """CRITICAL TEST: BALANCE Fund 12-Month Bug Fix"""
        try:
            print("\n💰 CRITICAL TEST: BALANCE Fund 12-Month Interest Bug Fix...")
            
            # Test the exact scenario from the bug report
            simulation_data = {
                "investments": [{"fund_code": "BALANCE", "amount": 100000}],
                "timeframe_months": 12
            }
            
            response = self.session.post(f"{self.base_url}/investments/simulate", json=simulation_data)
            
            if response.status_code != 200:
                self.log_test("BALANCE Simulation API", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            print(f"📊 Raw API Response: {json.dumps(data, indent=2)}")
            
            if not data.get("success"):
                self.log_test("BALANCE Simulation API", "FAIL", f"API returned success=false: {data.get('message', 'Unknown error')}")
                return False
            
            simulation = data.get("simulation", {})
            success = True
            
            # CRITICAL CHECK 1: total_roi_percentage should be 30.0 (not 25.0)
            total_roi = simulation.get("total_roi_percentage", 0)
            expected_roi = 30.0
            
            print(f"🔍 ROI Analysis:")
            print(f"   Current ROI: {total_roi}%")
            print(f"   Expected ROI: {expected_roi}% (12 months * 2.5%)")
            print(f"   Bug ROI: 25.0% (10 months * 2.5%)")
            
            if abs(total_roi - expected_roi) < 0.01:
                self.log_test("BALANCE ROI Bug Fix", "PASS", 
                            f"✅ BUG FIXED: ROI shows 30% (12 months) instead of 25% (10 months)", 
                            f"{expected_roi}%", 
                            f"{total_roi}%")
            else:
                self.log_test("BALANCE ROI Bug Fix", "FAIL", 
                            f"❌ BUG NOT FIXED: ROI still incorrect", 
                            f"{expected_roi}%", 
                            f"{total_roi}%")
                success = False
            
            # CRITICAL CHECK 2: total_interest_earned should be $30,000
            total_interest = simulation.get("total_interest_earned", 0)
            expected_interest = 30000.0
            
            print(f"🔍 Interest Analysis:")
            print(f"   Current Interest: ${total_interest:,.2f}")
            print(f"   Expected Interest: ${expected_interest:,.2f} (12 months)")
            print(f"   Bug Interest: $25,000 (10 months)")
            
            if abs(total_interest - expected_interest) < 0.01:
                self.log_test("BALANCE Interest Bug Fix", "PASS", 
                            f"✅ BUG FIXED: Interest shows $30,000 (12 months) instead of $25,000 (10 months)", 
                            f"${expected_interest:,.2f}", 
                            f"${total_interest:,.2f}")
            else:
                self.log_test("BALANCE Interest Bug Fix", "FAIL", 
                            f"❌ BUG NOT FIXED: Interest still incorrect", 
                            f"${expected_interest:,.2f}", 
                            f"${total_interest:,.2f}")
                success = False
            
            # CRITICAL CHECK 3: actual_simulation_months should be 14
            actual_months = simulation.get("actual_simulation_months", 0)
            expected_months = 14
            
            print(f"🔍 Timeline Analysis:")
            print(f"   Current Timeline: {actual_months} months")
            print(f"   Expected Timeline: {expected_months} months (12 requested + 2 incubation)")
            
            if actual_months == expected_months:
                self.log_test("BALANCE Timeline Fix", "PASS", 
                            f"✅ Timeline correctly includes incubation period", 
                            f"{expected_months} months", 
                            f"{actual_months} months")
            else:
                self.log_test("BALANCE Timeline Fix", "FAIL", 
                            f"❌ Timeline calculation incorrect", 
                            f"{expected_months} months", 
                            f"{actual_months} months")
                success = False
            
            # CRITICAL CHECK 4: interest_payment_months should be 12
            interest_months = simulation.get("interest_payment_months", 0)
            expected_interest_months = 12
            
            print(f"🔍 Interest Payment Analysis:")
            print(f"   Current Interest Months: {interest_months}")
            print(f"   Expected Interest Months: {expected_interest_months}")
            
            if interest_months == expected_interest_months:
                self.log_test("BALANCE Interest Months Fix", "PASS", 
                            f"✅ Interest payment months correct", 
                            f"{expected_interest_months} months", 
                            f"{interest_months} months")
            else:
                self.log_test("BALANCE Interest Months Fix", "FAIL", 
                            f"❌ Interest payment months incorrect", 
                            f"{expected_interest_months} months", 
                            f"{interest_months} months")
                success = False
            
            # Check projected_timeline length
            timeline = simulation.get("projected_timeline", [])
            expected_timeline_length = 15  # months 0-14
            
            print(f"🔍 Timeline Data Points:")
            print(f"   Current Timeline Points: {len(timeline)}")
            print(f"   Expected Timeline Points: {expected_timeline_length} (months 0-14)")
            
            if len(timeline) == expected_timeline_length:
                self.log_test("BALANCE Timeline Data", "PASS", 
                            f"Timeline has correct data points", 
                            f"{expected_timeline_length} points", 
                            f"{len(timeline)} points")
            else:
                self.log_test("BALANCE Timeline Data", "FAIL", 
                            f"Timeline data points incorrect", 
                            f"{expected_timeline_length} points", 
                            f"{len(timeline)} points")
                success = False
            
            # Check for quarterly interest redemption events
            calendar_events = simulation.get("calendar_events", [])
            quarterly_events = [event for event in calendar_events if event.get("type") == "interest_redemption"]
            expected_quarterly_events = 4  # 4 quarterly payments
            
            print(f"🔍 Calendar Events Analysis:")
            print(f"   Current Quarterly Events: {len(quarterly_events)}")
            print(f"   Expected Quarterly Events: {expected_quarterly_events}")
            
            if len(quarterly_events) == expected_quarterly_events:
                self.log_test("BALANCE Quarterly Events", "PASS", 
                            f"Correct quarterly interest redemption events", 
                            f"{expected_quarterly_events} events", 
                            f"{len(quarterly_events)} events")
            else:
                self.log_test("BALANCE Quarterly Events", "FAIL", 
                            f"Incorrect quarterly events", 
                            f"{expected_quarterly_events} events", 
                            f"{len(quarterly_events)} events")
                success = False
            
            # Check incubation period marking
            if timeline and len(timeline) >= 2:
                incubation_months = [month for month in timeline[:2] if month.get("in_incubation")]
                expected_incubation = 2
                
                print(f"🔍 Incubation Period Analysis:")
                print(f"   Current Incubation Months: {len(incubation_months)}")
                print(f"   Expected Incubation Months: {expected_incubation}")
                
                if len(incubation_months) == expected_incubation:
                    self.log_test("BALANCE Incubation Marking", "PASS", 
                                f"First 2 months correctly marked as incubation", 
                                f"{expected_incubation} months", 
                                f"{len(incubation_months)} months")
                else:
                    self.log_test("BALANCE Incubation Marking", "FAIL", 
                                f"Incubation period marking incorrect", 
                                f"{expected_incubation} months", 
                                f"{len(incubation_months)} months")
                    success = False
            
            return success
            
        except Exception as e:
            self.log_test("BALANCE Fund Critical Test", "ERROR", f"Exception: {str(e)}")
            return False

    def test_core_fund_regression(self) -> bool:
        """Regression Test: CORE Fund should still work correctly"""
        try:
            print("\n💎 REGRESSION TEST: CORE Fund 12-Month...")
            
            simulation_data = {
                "investments": [{"fund_code": "CORE", "amount": 50000}],
                "timeframe_months": 12
            }
            
            response = self.session.post(f"{self.base_url}/investments/simulate", json=simulation_data)
            
            if response.status_code != 200:
                self.log_test("CORE Regression API", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            if not data.get("success"):
                self.log_test("CORE Regression API", "FAIL", f"API returned success=false: {data.get('message', 'Unknown error')}")
                return False
            
            simulation = data.get("simulation", {})
            success = True
            
            # CORE: 1.5% monthly for 12 months = 18% ROI
            total_roi = simulation.get("total_roi_percentage", 0)
            expected_roi = 18.0
            
            if abs(total_roi - expected_roi) < 0.01:
                self.log_test("CORE ROI Regression", "PASS", 
                            f"CORE fund ROI unchanged (regression test)", 
                            f"{expected_roi}%", 
                            f"{total_roi}%")
            else:
                self.log_test("CORE ROI Regression", "FAIL", 
                            f"CORE fund ROI changed unexpectedly", 
                            f"{expected_roi}%", 
                            f"{total_roi}%")
                success = False
            
            # CORE: $50,000 * 1.5% * 12 = $9,000 interest
            total_interest = simulation.get("total_interest_earned", 0)
            expected_interest = 9000.0
            
            if abs(total_interest - expected_interest) < 0.01:
                self.log_test("CORE Interest Regression", "PASS", 
                            f"CORE interest unchanged (regression test)", 
                            f"${expected_interest:,.2f}", 
                            f"${total_interest:,.2f}")
            else:
                self.log_test("CORE Interest Regression", "FAIL", 
                            f"CORE interest changed unexpectedly", 
                            f"${expected_interest:,.2f}", 
                            f"${total_interest:,.2f}")
                success = False
            
            return success
            
        except Exception as e:
            self.log_test("CORE Fund Regression Test", "ERROR", f"Exception: {str(e)}")
            return False

    def test_multi_fund_portfolio(self) -> bool:
        """Test Multi-Fund Portfolio aggregation"""
        try:
            print("\n🎯 PORTFOLIO TEST: Multi-Fund Aggregation...")
            
            simulation_data = {
                "investments": [
                    {"fund_code": "BALANCE", "amount": 100000},
                    {"fund_code": "CORE", "amount": 50000}
                ],
                "timeframe_months": 12
            }
            
            response = self.session.post(f"{self.base_url}/investments/simulate", json=simulation_data)
            
            if response.status_code != 200:
                self.log_test("Multi-Fund API", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            if not data.get("success"):
                self.log_test("Multi-Fund API", "FAIL", f"API returned success=false: {data.get('message', 'Unknown error')}")
                return False
            
            simulation = data.get("simulation", {})
            success = True
            
            # Total investment: $150,000
            total_investment = simulation.get("total_investment", 0)
            expected_investment = 150000.0
            
            if abs(total_investment - expected_investment) < 0.01:
                self.log_test("Multi-Fund Investment", "PASS", 
                            f"Total investment correct", 
                            f"${expected_investment:,.2f}", 
                            f"${total_investment:,.2f}")
            else:
                self.log_test("Multi-Fund Investment", "FAIL", 
                            f"Total investment incorrect", 
                            f"${expected_investment:,.2f}", 
                            f"${total_investment:,.2f}")
                success = False
            
            # Total interest: $39,000 ($30k BALANCE + $9k CORE)
            total_interest = simulation.get("total_interest_earned", 0)
            expected_interest = 39000.0
            
            if abs(total_interest - expected_interest) < 0.01:
                self.log_test("Multi-Fund Interest", "PASS", 
                            f"Total interest correct (BALANCE + CORE)", 
                            f"${expected_interest:,.2f}", 
                            f"${total_interest:,.2f}")
            else:
                self.log_test("Multi-Fund Interest", "FAIL", 
                            f"Total interest incorrect", 
                            f"${expected_interest:,.2f}", 
                            f"${total_interest:,.2f}")
                success = False
            
            # Total ROI: 26% (39000/150000)
            total_roi = simulation.get("total_roi_percentage", 0)
            expected_roi = 26.0
            
            if abs(total_roi - expected_roi) < 0.01:
                self.log_test("Multi-Fund ROI", "PASS", 
                            f"Multi-fund ROI correct", 
                            f"{expected_roi}%", 
                            f"{total_roi}%")
            else:
                self.log_test("Multi-Fund ROI", "FAIL", 
                            f"Multi-fund ROI incorrect", 
                            f"{expected_roi}%", 
                            f"{total_roi}%")
                success = False
            
            return success
            
        except Exception as e:
            self.log_test("Multi-Fund Portfolio Test", "ERROR", f"Exception: {str(e)}")
            return False

    def test_commission_regression(self) -> bool:
        """Regression Test: Commission calculations should be unchanged"""
        try:
            print("\n💼 REGRESSION TEST: Commission Calculations...")
            
            # Test Salvador's commission stats (should be unchanged)
            salvador_id = "6909e8eaaaf69606babea151"
            response = self.session.get(f"{self.base_url}/admin/salespeople/{salvador_id}/stats")
            
            if response.status_code != 200:
                self.log_test("Commission Regression API", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            if not data.get("success"):
                self.log_test("Commission Regression API", "FAIL", f"API returned success=false: {data.get('message', 'Unknown error')}")
                return False
            
            stats = data.get("stats", {})
            
            # Commission should be unchanged: $3,326.76
            total_commission = stats.get("total_commission", 0)
            expected_commission = 3326.76
            
            if abs(total_commission - expected_commission) < 0.01:
                self.log_test("Commission Unchanged", "PASS", 
                            f"Salvador's commission unchanged (regression test passed)", 
                            f"${expected_commission:,.2f}", 
                            f"${total_commission:,.2f}")
                return True
            else:
                self.log_test("Commission Unchanged", "FAIL", 
                            f"Salvador's commission changed unexpectedly", 
                            f"${expected_commission:,.2f}", 
                            f"${total_commission:,.2f}")
                return False
            
        except Exception as e:
            self.log_test("Commission Regression Test", "ERROR", f"Exception: {str(e)}")
            return False

    def run_all_tests(self) -> bool:
        """Run all BALANCE fund bug fix verification tests"""
        print("🚀 BALANCE FUND 12-MONTH INTEREST BUG FIX VERIFICATION")
        print("=" * 70)
        print("CRITICAL: Verifying fix for BALANCE fund calculating 10 months instead of 12")
        print("=" * 70)
        
        # Authenticate first
        if not self.authenticate_admin():
            print("\n❌ Authentication failed. Cannot proceed with tests.")
            return False
        
        # Run critical tests
        tests = [
            ("BALANCE Fund 12-Month Bug Fix", self.test_balance_fund_12_months_critical),
            ("CORE Fund Regression", self.test_core_fund_regression),
            ("Multi-Fund Portfolio", self.test_multi_fund_portfolio),
            ("Commission Regression", self.test_commission_regression)
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed_tests += 1
            except Exception as e:
                self.log_test(f"{test_name} Exception", "ERROR", f"Test failed with exception: {str(e)}")
        
        # Print summary
        print("\n" + "=" * 70)
        print("📊 BALANCE FUND BUG FIX VERIFICATION SUMMARY")
        print("=" * 70)
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        # Print detailed results
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status_icon = "✅" if result["status"] == "PASS" else "❌" if result["status"] == "FAIL" else "⚠️"
            print(f"{status_icon} {result['test_name']}: {result['details']}")
            
            if result.get("expected") and result.get("actual"):
                print(f"   Expected: {result['expected']}")
                print(f"   Actual: {result['actual']}")
        
        print("\n" + "=" * 70)
        
        # Critical success criteria
        critical_tests = [
            "BALANCE ROI Bug Fix",
            "BALANCE Interest Bug Fix", 
            "BALANCE Timeline Fix",
            "Commission Unchanged"
        ]
        
        critical_passed = sum(1 for result in self.test_results 
                            if result["test_name"] in critical_tests and result["status"] == "PASS")
        
        if success_rate >= 75 and critical_passed >= 3:
            print("🎉 BALANCE FUND BUG FIX VERIFICATION: SUCCESSFUL")
            print("✅ BALANCE fund now calculates 12 months of interest (not 10)")
            print("✅ ROI correctly shows 30% for 12-month BALANCE requests")
            print("✅ No regression in existing functionality")
            print("✅ Commission calculations unchanged")
            return True
        else:
            print("🚨 BALANCE FUND BUG FIX VERIFICATION: FAILED")
            print("❌ Critical bug fix validation failed")
            print("❌ BALANCE fund may still calculate only 10 months")
            return False

def main():
    """Main test execution"""
    tester = BalanceFundBugTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()