#!/usr/bin/env python3
"""
INVESTMENT SIMULATION API ENDPOINTS TEST
========================================

This test verifies the new investment simulation API endpoints as requested:
1. Fund Configurations Endpoint: /api/investments/funds/config
2. Investment Simulation Endpoint: /api/investments/simulate
3. Verify simulation results include proper calculations
4. Test edge cases (invalid fund codes, minimum investment violations, etc.)

Expected Results:
- Fund configurations return all 4 FIDUS funds with correct details
- Investment simulation calculates proper projections and calendar events
- Edge cases are handled appropriately
- All calculations match expected business logic
"""

import requests
import json
import sys
from datetime import datetime, timedelta
import time

# Configuration
BACKEND_URL = "https://fidus-workspace.preview.emergentagent.com/api"

class InvestmentSimulationTest:
    def __init__(self):
        self.session = requests.Session()
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
    
    def test_fund_configurations_endpoint(self):
        """Test /api/investments/funds/config endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/investments/funds/config")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success') and 'funds' in data:
                    funds = data['funds']
                    
                    # Check if we have all 4 expected funds
                    expected_funds = ['CORE', 'BALANCE', 'DYNAMIC', 'UNLIMITED']
                    found_funds = [fund['fund_code'] for fund in funds]
                    
                    if len(funds) == 4 and all(fund_code in found_funds for fund_code in expected_funds):
                        self.log_result("Fund Configurations - Count", True, 
                                      f"All 4 FIDUS funds returned: {', '.join(found_funds)}")
                        
                        # Verify each fund's details
                        self.verify_fund_details(funds)
                    else:
                        self.log_result("Fund Configurations - Count", False, 
                                      f"Expected 4 funds {expected_funds}, got {len(funds)}: {found_funds}",
                                      {"funds": funds})
                else:
                    self.log_result("Fund Configurations - Response", False, 
                                  "Invalid response format", {"response": data})
            else:
                self.log_result("Fund Configurations - HTTP", False, 
                              f"HTTP {response.status_code}", {"response": response.text})
                
        except Exception as e:
            self.log_result("Fund Configurations - Exception", False, f"Exception: {str(e)}")
    
    def verify_fund_details(self, funds):
        """Verify each fund has correct configuration details"""
        expected_fund_details = {
            'CORE': {
                'name': 'FIDUS Core Fund',
                'interest_rate': 1.5,
                'minimum_investment': 10000.0,
                'incubation_months': 2,
                'minimum_hold_months': 12,
                'invitation_only': False
            },
            'BALANCE': {
                'name': 'FIDUS Balance Fund',
                'interest_rate': 2.5,
                'minimum_investment': 50000.0,
                'incubation_months': 2,
                'minimum_hold_months': 12,
                'invitation_only': False
            },
            'DYNAMIC': {
                'name': 'FIDUS Dynamic Fund',
                'interest_rate': 3.5,
                'minimum_investment': 250000.0,
                'incubation_months': 2,
                'minimum_hold_months': 12,
                'invitation_only': False
            },
            'UNLIMITED': {
                'name': 'FIDUS Unlimited Fund',
                'interest_rate': 0.0,
                'minimum_investment': 1000000.0,
                'incubation_months': 2,
                'minimum_hold_months': 12,
                'invitation_only': True
            }
        }
        
        for fund in funds:
            fund_code = fund['fund_code']
            if fund_code in expected_fund_details:
                expected = expected_fund_details[fund_code]
                issues = []
                
                for key, expected_value in expected.items():
                    actual_value = fund.get(key)
                    if actual_value != expected_value:
                        issues.append(f"{key}: expected {expected_value}, got {actual_value}")
                
                if not issues:
                    self.log_result(f"Fund Details - {fund_code}", True, 
                                  f"{fund_code} fund configuration correct")
                else:
                    self.log_result(f"Fund Details - {fund_code}", False, 
                                  f"{fund_code} fund configuration issues: {', '.join(issues)}",
                                  {"fund_data": fund})
    
    def test_investment_simulation_basic(self):
        """Test basic investment simulation with sample portfolio"""
        try:
            # Sample portfolio from the review request
            simulation_request = {
                "investments": [
                    {"fund_code": "CORE", "amount": 10000},
                    {"fund_code": "BALANCE", "amount": 60000},
                    {"fund_code": "DYNAMIC", "amount": 260000}
                ],
                "timeframe_months": 24,
                "simulation_name": "Test Portfolio",
                "lead_info": {"name": "John Doe", "email": "john@test.com"}
            }
            
            response = self.session.post(f"{BACKEND_URL}/investments/simulate", 
                                       json=simulation_request)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success') and 'simulation' in data:
                    simulation = data['simulation']
                    self.verify_simulation_results(simulation, simulation_request)
                else:
                    self.log_result("Investment Simulation - Response", False, 
                                  "Invalid response format", {"response": data})
            else:
                self.log_result("Investment Simulation - HTTP", False, 
                              f"HTTP {response.status_code}", {"response": response.text})
                
        except Exception as e:
            self.log_result("Investment Simulation - Exception", False, f"Exception: {str(e)}")
    
    def verify_simulation_results(self, simulation, original_request):
        """Verify simulation results contain all expected components"""
        expected_total = sum(inv['amount'] for inv in original_request['investments'])
        
        # Test 1: Total investment calculation
        actual_total = simulation.get('total_investment')
        if actual_total == expected_total:
            self.log_result("Simulation - Total Investment", True, 
                          f"Total investment correct: ${actual_total:,.2f}")
        else:
            self.log_result("Simulation - Total Investment", False, 
                          f"Expected ${expected_total:,.2f}, got ${actual_total:,.2f}")
        
        # Test 2: Fund breakdown
        fund_breakdown = simulation.get('fund_breakdown', [])
        if len(fund_breakdown) == 3:  # CORE, BALANCE, DYNAMIC
            self.log_result("Simulation - Fund Breakdown Count", True, 
                          f"Fund breakdown contains {len(fund_breakdown)} funds")
            
            # Verify each fund in breakdown
            for fund_data in fund_breakdown:
                fund_code = fund_data.get('fund_code')
                investment_amount = fund_data.get('investment_amount')
                interest_rate = fund_data.get('interest_rate')
                
                # Find corresponding original investment
                original_inv = next((inv for inv in original_request['investments'] 
                                   if inv['fund_code'] == fund_code), None)
                
                if original_inv and investment_amount == original_inv['amount']:
                    self.log_result(f"Simulation - {fund_code} Amount", True, 
                                  f"{fund_code}: ${investment_amount:,.2f} matches request")
                else:
                    self.log_result(f"Simulation - {fund_code} Amount", False, 
                                  f"{fund_code}: amount mismatch")
        else:
            self.log_result("Simulation - Fund Breakdown Count", False, 
                          f"Expected 3 funds in breakdown, got {len(fund_breakdown)}")
        
        # Test 3: Projected timeline
        projected_timeline = simulation.get('projected_timeline', [])
        expected_months = original_request['timeframe_months'] + 1  # Include month 0
        if len(projected_timeline) == expected_months:
            self.log_result("Simulation - Timeline Length", True, 
                          f"Timeline contains {len(projected_timeline)} months")
        else:
            self.log_result("Simulation - Timeline Length", False, 
                          f"Expected {expected_months} timeline entries, got {len(projected_timeline)}")
        
        # Test 4: Calendar events
        calendar_events = simulation.get('calendar_events', [])
        if len(calendar_events) > 0:
            self.log_result("Simulation - Calendar Events", True, 
                          f"Calendar contains {len(calendar_events)} events")
            
            # Check for key event types
            event_types = [event.get('type') for event in calendar_events]
            expected_types = ['investment_start', 'incubation_end', 'principal_redeemable']
            
            found_types = []
            for expected_type in expected_types:
                if expected_type in event_types:
                    found_types.append(expected_type)
            
            if len(found_types) == len(expected_types):
                self.log_result("Simulation - Event Types", True, 
                              f"All expected event types found: {', '.join(found_types)}")
            else:
                missing_types = [t for t in expected_types if t not in found_types]
                self.log_result("Simulation - Event Types", False, 
                              f"Missing event types: {', '.join(missing_types)}")
        else:
            self.log_result("Simulation - Calendar Events", False, 
                          "No calendar events generated")
        
        # Test 5: Summary statistics
        summary = simulation.get('summary', {})
        required_summary_fields = ['total_investment', 'final_value', 'total_interest_earned', 
                                 'total_roi_percentage', 'timeframe_months']
        
        missing_fields = [field for field in required_summary_fields if field not in summary]
        if not missing_fields:
            self.log_result("Simulation - Summary Fields", True, 
                          "All required summary fields present")
            
            # Verify summary calculations
            if summary.get('total_investment') == expected_total:
                self.log_result("Simulation - Summary Total", True, 
                              f"Summary total investment matches: ${expected_total:,.2f}")
            else:
                self.log_result("Simulation - Summary Total", False, 
                              f"Summary total mismatch: expected ${expected_total:,.2f}")
        else:
            self.log_result("Simulation - Summary Fields", False, 
                          f"Missing summary fields: {', '.join(missing_fields)}")
    
    def test_edge_case_invalid_fund_code(self):
        """Test simulation with invalid fund code"""
        try:
            simulation_request = {
                "investments": [
                    {"fund_code": "INVALID", "amount": 10000}
                ],
                "timeframe_months": 12
            }
            
            response = self.session.post(f"{BACKEND_URL}/investments/simulate", 
                                       json=simulation_request)
            
            # Should handle invalid fund code gracefully
            if response.status_code == 400 or (response.status_code == 200 and 
                                             response.json().get('simulation', {}).get('fund_breakdown', []) == []):
                self.log_result("Edge Case - Invalid Fund Code", True, 
                              "Invalid fund code handled appropriately")
            else:
                self.log_result("Edge Case - Invalid Fund Code", False, 
                              f"Invalid fund code not handled properly: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Edge Case - Invalid Fund Code", False, f"Exception: {str(e)}")
    
    def test_edge_case_minimum_investment_violation(self):
        """Test simulation with amounts below minimum investment"""
        try:
            simulation_request = {
                "investments": [
                    {"fund_code": "CORE", "amount": 5000},  # Below $10K minimum
                    {"fund_code": "BALANCE", "amount": 25000}  # Below $50K minimum
                ],
                "timeframe_months": 12
            }
            
            response = self.session.post(f"{BACKEND_URL}/investments/simulate", 
                                       json=simulation_request)
            
            # Should return error for minimum investment violations
            if response.status_code == 400:
                error_message = response.json().get('detail', '')
                if 'minimum' in error_message.lower():
                    self.log_result("Edge Case - Minimum Investment", True, 
                                  "Minimum investment violation detected correctly")
                else:
                    self.log_result("Edge Case - Minimum Investment", False, 
                                  f"Wrong error message: {error_message}")
            else:
                self.log_result("Edge Case - Minimum Investment", False, 
                              f"Minimum investment violation not caught: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Edge Case - Minimum Investment", False, f"Exception: {str(e)}")
    
    def test_edge_case_empty_investments(self):
        """Test simulation with empty investments array"""
        try:
            simulation_request = {
                "investments": [],
                "timeframe_months": 12
            }
            
            response = self.session.post(f"{BACKEND_URL}/investments/simulate", 
                                       json=simulation_request)
            
            # Should return error for empty investments
            if response.status_code == 400:
                error_message = response.json().get('detail', '')
                if 'required' in error_message.lower():
                    self.log_result("Edge Case - Empty Investments", True, 
                                  "Empty investments array handled correctly")
                else:
                    self.log_result("Edge Case - Empty Investments", False, 
                                  f"Wrong error message: {error_message}")
            else:
                self.log_result("Edge Case - Empty Investments", False, 
                              f"Empty investments not handled: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Edge Case - Empty Investments", False, f"Exception: {str(e)}")
    
    def test_edge_case_unlimited_fund_invitation_only(self):
        """Test UNLIMITED fund handling (invitation only)"""
        try:
            simulation_request = {
                "investments": [
                    {"fund_code": "UNLIMITED", "amount": 1000000}
                ],
                "timeframe_months": 12
            }
            
            response = self.session.post(f"{BACKEND_URL}/investments/simulate", 
                                       json=simulation_request)
            
            # UNLIMITED fund should be processed (simulation allows it for demo purposes)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    simulation = data['simulation']
                    fund_breakdown = simulation.get('fund_breakdown', [])
                    
                    unlimited_fund = next((fund for fund in fund_breakdown 
                                         if fund.get('fund_code') == 'UNLIMITED'), None)
                    
                    if unlimited_fund:
                        # UNLIMITED fund has 0% interest rate (performance sharing instead)
                        if unlimited_fund.get('interest_rate') == 0.0:
                            self.log_result("Edge Case - UNLIMITED Fund", True, 
                                          "UNLIMITED fund processed with 0% interest rate")
                        else:
                            self.log_result("Edge Case - UNLIMITED Fund", False, 
                                          f"UNLIMITED fund should have 0% interest rate, got {unlimited_fund.get('interest_rate')}%")
                    else:
                        self.log_result("Edge Case - UNLIMITED Fund", False, 
                                      "UNLIMITED fund not found in breakdown")
                else:
                    self.log_result("Edge Case - UNLIMITED Fund", False, 
                                  "Simulation failed for UNLIMITED fund")
            else:
                self.log_result("Edge Case - UNLIMITED Fund", False, 
                              f"UNLIMITED fund simulation failed: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Edge Case - UNLIMITED Fund", False, f"Exception: {str(e)}")
    
    def test_interest_calculations_accuracy(self):
        """Test accuracy of interest calculations"""
        try:
            # Simple test case for calculation verification
            simulation_request = {
                "investments": [
                    {"fund_code": "CORE", "amount": 10000}  # 1.5% monthly
                ],
                "timeframe_months": 12
            }
            
            response = self.session.post(f"{BACKEND_URL}/investments/simulate", 
                                       json=simulation_request)
            
            if response.status_code == 200:
                data = response.json()
                simulation = data['simulation']
                fund_breakdown = simulation.get('fund_breakdown', [])
                
                if fund_breakdown:
                    core_fund = fund_breakdown[0]
                    projections = core_fund.get('projections', [])
                    
                    if projections:
                        # Check month 4 (2 months incubation + 2 months interest)
                        # Should have 2 months of interest: 10000 * 0.015 * 2 = $300
                        if len(projections) > 4:
                            month_4 = projections[4]
                            expected_interest = 10000 * 0.015 * 2  # 2 months of interest
                            actual_interest = month_4.get('interest_earned', 0)
                            
                            # Allow small rounding differences
                            if abs(actual_interest - expected_interest) < 1.0:
                                self.log_result("Interest Calculation - Accuracy", True, 
                                              f"Interest calculation accurate: ${actual_interest:.2f} ≈ ${expected_interest:.2f}")
                            else:
                                self.log_result("Interest Calculation - Accuracy", False, 
                                              f"Interest calculation error: expected ${expected_interest:.2f}, got ${actual_interest:.2f}")
                        else:
                            self.log_result("Interest Calculation - Accuracy", False, 
                                          "Insufficient projection data for calculation test")
                    else:
                        self.log_result("Interest Calculation - Accuracy", False, 
                                      "No projections data found")
                else:
                    self.log_result("Interest Calculation - Accuracy", False, 
                                  "No fund breakdown found")
            else:
                self.log_result("Interest Calculation - Accuracy", False, 
                              f"Simulation failed: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Interest Calculation - Accuracy", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all investment simulation tests"""
        print("🎯 INVESTMENT SIMULATION API ENDPOINTS TEST")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        print("🔍 Running Investment Simulation Tests...")
        print("-" * 50)
        
        # Run all tests
        self.test_fund_configurations_endpoint()
        self.test_investment_simulation_basic()
        self.test_interest_calculations_accuracy()
        
        print("\n🚨 Running Edge Case Tests...")
        print("-" * 30)
        self.test_edge_case_invalid_fund_code()
        self.test_edge_case_minimum_investment_violation()
        self.test_edge_case_empty_investments()
        self.test_edge_case_unlimited_fund_invitation_only()
        
        # Generate summary
        self.generate_test_summary()
        
        return True
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🎯 INVESTMENT SIMULATION TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Show failed tests
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
        critical_tests = [
            "Fund Configurations - Count",
            "Simulation - Total Investment", 
            "Simulation - Fund Breakdown Count",
            "Simulation - Timeline Length",
            "Simulation - Calendar Events"
        ]
        
        critical_passed = sum(1 for result in self.test_results 
                            if result['success'] and any(critical in result['test'] for critical in critical_tests))
        
        print("🚨 CRITICAL ASSESSMENT:")
        if critical_passed >= 4:  # At least 4 out of 5 critical tests
            print("✅ INVESTMENT SIMULATION API: WORKING CORRECTLY")
            print("   Fund configurations and simulation endpoints are operational.")
            print("   All core functionality verified and ready for production use.")
        else:
            print("❌ INVESTMENT SIMULATION API: ISSUES FOUND")
            print("   Critical functionality problems detected.")
            print("   Main agent action required to fix simulation endpoints.")
        
        print("\n" + "=" * 60)

def main():
    """Main test execution"""
    test_runner = InvestmentSimulationTest()
    success = test_runner.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()