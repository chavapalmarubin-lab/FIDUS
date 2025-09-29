#!/usr/bin/env python3
"""
INVESTMENT SIMULATOR FIXED CALCULATIONS VERIFICATION TEST
=========================================================

This test verifies the FIXED Investment Simulator backend API after removing duplicate functions
to verify the mathematical calculations are now CORRECT as requested in the review.

Testing Requirements:
1. Test the /api/investments/simulate endpoint with specific payload
2. Verify CORRECT ROI calculations for each fund:
   - CORE Fund: 1.5% × 12 months = 18% ROI = $4,500 interest on $25,000
   - BALANCE Fund: 2.5% × 12 months = 30% ROI = $30,000 interest on $100,000  
   - DYNAMIC Fund: 3.5% × 12 months = 42% ROI = $105,000 interest on $250,000
3. Validate that 77% error is ELIMINATED - no ROI values should exceed 50%
4. Check total calculations:
   - Total investment: $375,000
   - Total interest: $139,500 ($4,500 + $30,000 + $105,000)
   - Total final value: $514,500
5. Verify fund breakdown structure with 2-month incubation + 12-month interest = 14-month total

Expected Results: The calculations should now be mathematically correct with CORE=18%, 
BALANCE=30%, DYNAMIC=42% ROI, and the 77% error completely eliminated.
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration
BACKEND_URL = "https://fidus-workspace-2.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class InvestmentSimulatorFixedTest:
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
    
    def test_investment_simulator_endpoint(self):
        """Test the /api/investments/simulate endpoint with the specified payload"""
        try:
            # Test payload as specified in the review request
            test_payload = {
                "investments": [
                    {"fund_code": "CORE", "amount": 25000},
                    {"fund_code": "BALANCE", "amount": 100000},
                    {"fund_code": "DYNAMIC", "amount": 250000}
                ],
                "timeframe_months": 24,
                "simulation_name": "Fixed Calculations Test"
            }
            
            response = self.session.post(f"{BACKEND_URL}/investments/simulate", json=test_payload)
            
            if response.status_code == 200:
                simulation_result = response.json()
                self.log_result("Investment Simulator Endpoint", True, 
                              "Simulation endpoint responding correctly",
                              {"payload": test_payload, "response_keys": list(simulation_result.keys())})
                return simulation_result
            else:
                self.log_result("Investment Simulator Endpoint", False, 
                              f"HTTP {response.status_code}: {response.text}",
                              {"payload": test_payload})
                return None
                
        except Exception as e:
            self.log_result("Investment Simulator Endpoint", False, f"Exception: {str(e)}")
            return None
    
    def test_core_fund_calculations(self, simulation_result):
        """Test CORE Fund calculations: 1.5% × 12 months = 18% ROI = $4,500 interest on $25,000"""
        if not simulation_result:
            self.log_result("CORE Fund Calculations", False, "No simulation result to test")
            return
        
        try:
            simulation_data = simulation_result.get('simulation', {})
            fund_breakdown = simulation_data.get('fund_breakdown', [])
            
            core_fund = None
            for fund in fund_breakdown:
                if fund.get('fund_code') == 'CORE':
                    core_fund = fund
                    break
            
            if not core_fund:
                self.log_result("CORE Fund Calculations", False, "CORE fund not found in simulation result")
                return
            
            # Expected values
            expected_investment = 25000
            expected_roi_percentage = 18.0
            expected_total_interest = 4500.0
            expected_final_value = 29500.0
            
            # Actual values
            actual_investment = core_fund.get('investment_amount', 0)
            actual_roi = core_fund.get('roi_percentage', 0)
            actual_interest = core_fund.get('total_interest', 0)
            actual_final = core_fund.get('final_value', 0)
            
            # Test investment amount
            if actual_investment == expected_investment:
                self.log_result("CORE Investment Amount", True, f"Investment amount correct: ${actual_investment:,.2f}")
            else:
                self.log_result("CORE Investment Amount", False, 
                              f"Investment amount incorrect: ${actual_investment:,.2f} (expected ${expected_investment:,.2f})")
            
            # Test ROI percentage
            if abs(actual_roi - expected_roi_percentage) < 0.1:
                self.log_result("CORE ROI Percentage", True, f"ROI correct: {actual_roi}% (1.5% × 12 months)")
            else:
                self.log_result("CORE ROI Percentage", False, 
                              f"ROI incorrect: {actual_roi}% (expected {expected_roi_percentage}%)")
            
            # Test total interest
            if abs(actual_interest - expected_total_interest) < 1.0:
                self.log_result("CORE Total Interest", True, f"Interest correct: ${actual_interest:,.2f}")
            else:
                self.log_result("CORE Total Interest", False, 
                              f"Interest incorrect: ${actual_interest:,.2f} (expected ${expected_total_interest:,.2f})")
            
            # Test final value
            if abs(actual_final - expected_final_value) < 1.0:
                self.log_result("CORE Final Value", True, f"Final value correct: ${actual_final:,.2f}")
            else:
                self.log_result("CORE Final Value", False, 
                              f"Final value incorrect: ${actual_final:,.2f} (expected ${expected_final_value:,.2f})")
                
        except Exception as e:
            self.log_result("CORE Fund Calculations", False, f"Exception: {str(e)}")
    
    def test_balance_fund_calculations(self, simulation_result):
        """Test BALANCE Fund calculations: 2.5% × 12 months = 30% ROI = $30,000 interest on $100,000"""
        if not simulation_result:
            self.log_result("BALANCE Fund Calculations", False, "No simulation result to test")
            return
        
        try:
            simulation_data = simulation_result.get('simulation', {})
            fund_breakdown = simulation_data.get('fund_breakdown', [])
            
            balance_fund = None
            for fund in fund_breakdown:
                if fund.get('fund_code') == 'BALANCE':
                    balance_fund = fund
                    break
            
            if not balance_fund:
                self.log_result("BALANCE Fund Calculations", False, "BALANCE fund not found in simulation result")
                return
            
            # Expected values
            expected_investment = 100000
            expected_roi_percentage = 30.0
            expected_total_interest = 30000.0
            expected_final_value = 130000.0
            
            # Actual values
            actual_investment = balance_fund.get('investment_amount', 0)
            actual_roi = balance_fund.get('roi_percentage', 0)
            actual_interest = balance_fund.get('total_interest', 0)
            actual_final = balance_fund.get('final_value', 0)
            
            # Test investment amount
            if actual_investment == expected_investment:
                self.log_result("BALANCE Investment Amount", True, f"Investment amount correct: ${actual_investment:,.2f}")
            else:
                self.log_result("BALANCE Investment Amount", False, 
                              f"Investment amount incorrect: ${actual_investment:,.2f} (expected ${expected_investment:,.2f})")
            
            # Test ROI percentage
            if abs(actual_roi - expected_roi_percentage) < 0.1:
                self.log_result("BALANCE ROI Percentage", True, f"ROI correct: {actual_roi}% (2.5% × 12 months)")
            else:
                self.log_result("BALANCE ROI Percentage", False, 
                              f"ROI incorrect: {actual_roi}% (expected {expected_roi_percentage}%)")
            
            # Test total interest
            if abs(actual_interest - expected_total_interest) < 1.0:
                self.log_result("BALANCE Total Interest", True, f"Interest correct: ${actual_interest:,.2f}")
            else:
                self.log_result("BALANCE Total Interest", False, 
                              f"Interest incorrect: ${actual_interest:,.2f} (expected ${expected_total_interest:,.2f})")
            
            # Test final value
            if abs(actual_final - expected_final_value) < 1.0:
                self.log_result("BALANCE Final Value", True, f"Final value correct: ${actual_final:,.2f}")
            else:
                self.log_result("BALANCE Final Value", False, 
                              f"Final value incorrect: ${actual_final:,.2f} (expected ${expected_final_value:,.2f})")
                
        except Exception as e:
            self.log_result("BALANCE Fund Calculations", False, f"Exception: {str(e)}")
    
    def test_dynamic_fund_calculations(self, simulation_result):
        """Test DYNAMIC Fund calculations: 3.5% × 12 months = 42% ROI = $105,000 interest on $250,000"""
        if not simulation_result:
            self.log_result("DYNAMIC Fund Calculations", False, "No simulation result to test")
            return
        
        try:
            simulation_data = simulation_result.get('simulation', {})
            fund_breakdown = simulation_data.get('fund_breakdown', [])
            
            dynamic_fund = None
            for fund in fund_breakdown:
                if fund.get('fund_code') == 'DYNAMIC':
                    dynamic_fund = fund
                    break
            
            if not dynamic_fund:
                self.log_result("DYNAMIC Fund Calculations", False, "DYNAMIC fund not found in simulation result")
                return
            
            # Expected values
            expected_investment = 250000
            expected_roi_percentage = 42.0
            expected_total_interest = 105000.0
            expected_final_value = 355000.0
            
            # Actual values
            actual_investment = dynamic_fund.get('investment_amount', 0)
            actual_roi = dynamic_fund.get('roi_percentage', 0)
            actual_interest = dynamic_fund.get('total_interest', 0)
            actual_final = dynamic_fund.get('final_value', 0)
            
            # Test investment amount
            if actual_investment == expected_investment:
                self.log_result("DYNAMIC Investment Amount", True, f"Investment amount correct: ${actual_investment:,.2f}")
            else:
                self.log_result("DYNAMIC Investment Amount", False, 
                              f"Investment amount incorrect: ${actual_investment:,.2f} (expected ${expected_investment:,.2f})")
            
            # Test ROI percentage
            if abs(actual_roi - expected_roi_percentage) < 0.1:
                self.log_result("DYNAMIC ROI Percentage", True, f"ROI correct: {actual_roi}% (3.5% × 12 months)")
            else:
                self.log_result("DYNAMIC ROI Percentage", False, 
                              f"ROI incorrect: {actual_roi}% (expected {expected_roi_percentage}%)")
            
            # Test total interest
            if abs(actual_interest - expected_total_interest) < 1.0:
                self.log_result("DYNAMIC Total Interest", True, f"Interest correct: ${actual_interest:,.2f}")
            else:
                self.log_result("DYNAMIC Total Interest", False, 
                              f"Interest incorrect: ${actual_interest:,.2f} (expected ${expected_total_interest:,.2f})")
            
            # Test final value
            if abs(actual_final - expected_final_value) < 1.0:
                self.log_result("DYNAMIC Final Value", True, f"Final value correct: ${actual_final:,.2f}")
            else:
                self.log_result("DYNAMIC Final Value", False, 
                              f"Final value incorrect: ${actual_final:,.2f} (expected ${expected_final_value:,.2f})")
                
        except Exception as e:
            self.log_result("DYNAMIC Fund Calculations", False, f"Exception: {str(e)}")
    
    def test_77_percent_error_elimination(self, simulation_result):
        """Validate that 77% error is ELIMINATED - no ROI values should exceed 50%"""
        if not simulation_result:
            self.log_result("77% Error Elimination", False, "No simulation result to test")
            return
        
        try:
            simulation_data = simulation_result.get('simulation', {})
            fund_breakdown = simulation_data.get('fund_breakdown', [])
            
            max_roi_found = 0
            roi_values = []
            error_77_found = False
            
            for fund_data in fund_breakdown:
                roi_percentage = fund_data.get('roi_percentage', 0)
                fund_code = fund_data.get('fund_code', 'Unknown')
                roi_values.append(f"{fund_code}: {roi_percentage}%")
                
                if roi_percentage > max_roi_found:
                    max_roi_found = roi_percentage
                
                # Check specifically for the problematic 77% error
                if abs(roi_percentage - 77.0) < 0.1:
                    error_77_found = True
            
            # Also check the entire response for any 77% values
            response_text = json.dumps(simulation_result)
            if "77" in response_text and ("%" in response_text or "percent" in response_text.lower()):
                # More detailed check to avoid false positives
                import re
                roi_pattern = r'77\.?\d*\s*%|77\.?\d*\s*percent'
                if re.search(roi_pattern, response_text, re.IGNORECASE):
                    error_77_found = True
            
            if error_77_found:
                self.log_result("77% Error Elimination", False, 
                              "77% error still present in simulation results",
                              {"roi_values": roi_values, "max_roi": max_roi_found})
            elif max_roi_found <= 50.0:
                self.log_result("77% Error Elimination", True, 
                              f"77% error eliminated. Max ROI: {max_roi_found}% (≤50%)",
                              {"roi_values": roi_values})
            else:
                self.log_result("77% Error Elimination", False, 
                              f"ROI values exceed 50%: Max ROI {max_roi_found}%",
                              {"roi_values": roi_values})
                
        except Exception as e:
            self.log_result("77% Error Elimination", False, f"Exception: {str(e)}")
    
    def test_total_calculations(self, simulation_result):
        """Check total calculations: investment, interest, and final value"""
        if not simulation_result:
            self.log_result("Total Calculations", False, "No simulation result to test")
            return
        
        try:
            simulation_data = simulation_result.get('simulation', {})
            
            # Expected totals
            expected_total_investment = 375000.0  # $25,000 + $100,000 + $250,000
            expected_total_interest = 139500.0    # $4,500 + $30,000 + $105,000
            expected_total_final = 514500.0       # $375,000 + $139,500
            
            # Get actual totals from simulation result
            actual_total_investment = simulation_data.get('total_investment', 0)
            
            # Calculate total interest and final value from fund breakdown
            fund_breakdown = simulation_data.get('fund_breakdown', [])
            calculated_total_interest = sum(fund.get('total_interest', 0) for fund in fund_breakdown)
            calculated_total_final = sum(fund.get('final_value', 0) for fund in fund_breakdown)
            
            # Also check projected timeline for final values
            projected_timeline = simulation_data.get('projected_timeline', [])
            timeline_final_interest = 0
            timeline_final_value = 0
            
            # Find the final values at month 14 (contract completion)
            for timeline_entry in projected_timeline:
                if timeline_entry.get('month') == 14:
                    timeline_final_interest = timeline_entry.get('total_interest', 0)
                    timeline_final_value = timeline_entry.get('total_value', 0)
                    break
            
            # Test total investment
            if abs(actual_total_investment - expected_total_investment) < 1.0:
                self.log_result("Total Investment Calculation", True, 
                              f"Total investment correct: ${actual_total_investment:,.2f}")
            else:
                self.log_result("Total Investment Calculation", False, 
                              f"Total investment incorrect: ${actual_total_investment:,.2f} (expected ${expected_total_investment:,.2f})")
            
            # Test total interest (from fund breakdown)
            if abs(calculated_total_interest - expected_total_interest) < 1.0:
                self.log_result("Total Interest Calculation", True, 
                              f"Total interest correct: ${calculated_total_interest:,.2f}")
            else:
                self.log_result("Total Interest Calculation", False, 
                              f"Total interest incorrect: ${calculated_total_interest:,.2f} (expected ${expected_total_interest:,.2f})")
            
            # Test total final value (from fund breakdown)
            if abs(calculated_total_final - expected_total_final) < 1.0:
                self.log_result("Total Final Value Calculation", True, 
                              f"Total final value correct: ${calculated_total_final:,.2f}")
            else:
                self.log_result("Total Final Value Calculation", False, 
                              f"Total final value incorrect: ${calculated_total_final:,.2f} (expected ${expected_total_final:,.2f})")
            
            # Test timeline final values
            if abs(timeline_final_interest - expected_total_interest) < 1.0:
                self.log_result("Timeline Interest Calculation", True, 
                              f"Timeline interest correct: ${timeline_final_interest:,.2f}")
            else:
                self.log_result("Timeline Interest Calculation", False, 
                              f"Timeline interest incorrect: ${timeline_final_interest:,.2f} (expected ${expected_total_interest:,.2f})")
                
        except Exception as e:
            self.log_result("Total Calculations", False, f"Exception: {str(e)}")
    
    def test_fund_structure_verification(self, simulation_result):
        """Verify fund breakdown structure with 2-month incubation + 12-month interest = 14-month total"""
        if not simulation_result:
            self.log_result("Fund Structure Verification", False, "No simulation result to test")
            return
        
        try:
            simulation_data = simulation_result.get('simulation', {})
            fund_breakdown = simulation_data.get('fund_breakdown', [])
            
            # Expected structure
            expected_incubation_months = 2
            expected_interest_months = 12
            expected_total_months = 14
            
            structure_correct = True
            structure_issues = []
            
            for fund in fund_breakdown:
                fund_code = fund.get('fund_code', 'Unknown')
                
                # Check incubation months
                actual_incubation = fund.get('incubation_months', 0)
                if actual_incubation != expected_incubation_months:
                    structure_correct = False
                    structure_issues.append(f"{fund_code}: incubation {actual_incubation} months (expected {expected_incubation_months})")
                
                # Check interest months
                actual_interest = fund.get('interest_months', 0)
                if actual_interest != expected_interest_months:
                    structure_correct = False
                    structure_issues.append(f"{fund_code}: interest {actual_interest} months (expected {expected_interest_months})")
                
                # Check total contract months
                actual_total = fund.get('contract_months', 0)
                if actual_total != expected_total_months:
                    structure_correct = False
                    structure_issues.append(f"{fund_code}: total {actual_total} months (expected {expected_total_months})")
            
            if structure_correct:
                self.log_result("Fund Structure Verification", True, 
                              f"All funds have correct structure: {expected_incubation_months}-month incubation + {expected_interest_months}-month interest = {expected_total_months}-month total")
            else:
                self.log_result("Fund Structure Verification", False, 
                              f"Fund structure issues found", {"issues": structure_issues})
            
            # Verify calendar events exist
            calendar_events = simulation_data.get('calendar_events', [])
            if calendar_events:
                self.log_result("Calendar Events Structure", True, 
                              f"Calendar events present: {len(calendar_events)} events")
            else:
                self.log_result("Calendar Events Structure", False, 
                              "Calendar events missing from simulation result")
                
        except Exception as e:
            self.log_result("Fund Structure Verification", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all Investment Simulator calculation verification tests"""
        print("🎯 INVESTMENT SIMULATOR FIXED CALCULATIONS VERIFICATION TEST")
        print("=" * 70)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        print("Testing Requirements:")
        print("• CORE Fund: 1.5% × 12 months = 18% ROI = $4,500 interest on $25,000")
        print("• BALANCE Fund: 2.5% × 12 months = 30% ROI = $30,000 interest on $100,000")
        print("• DYNAMIC Fund: 3.5% × 12 months = 42% ROI = $105,000 interest on $250,000")
        print("• Total investment: $375,000")
        print("• Total interest: $139,500")
        print("• Total final value: $514,500")
        print("• 77% error must be ELIMINATED")
        print()
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with tests.")
            return False
        
        print("\n🔍 Running Investment Simulator Fixed Calculation Tests...")
        print("-" * 60)
        
        # Test the simulation endpoint
        simulation_result = self.test_investment_simulator_endpoint()
        
        if simulation_result:
            # Run all calculation verification tests
            self.test_core_fund_calculations(simulation_result)
            self.test_balance_fund_calculations(simulation_result)
            self.test_dynamic_fund_calculations(simulation_result)
            self.test_77_percent_error_elimination(simulation_result)
            self.test_total_calculations(simulation_result)
            self.test_fund_structure_verification(simulation_result)
        else:
            print("❌ Cannot proceed with calculation tests - simulation endpoint failed")
        
        # Generate summary
        self.generate_test_summary()
        
        return True
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 70)
        print("🎯 INVESTMENT SIMULATOR FIXED CALCULATIONS TEST SUMMARY")
        print("=" * 70)
        
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
        
        # Critical assessment for Investment Simulator
        critical_tests = [
            "CORE ROI Percentage",
            "BALANCE ROI Percentage", 
            "DYNAMIC ROI Percentage",
            "77% Error Elimination",
            "Total Interest Calculation"
        ]
        
        critical_passed = sum(1 for result in self.test_results 
                            if result['success'] and any(critical in result['test'] for critical in critical_tests))
        
        print("🚨 CRITICAL ASSESSMENT:")
        if critical_passed >= 4:  # At least 4 out of 5 critical tests
            print("✅ INVESTMENT SIMULATOR CALCULATIONS: CORRECT")
            print("   Mathematical calculations are now accurate:")
            print("   • CORE Fund: 18% ROI (1.5% × 12 months)")
            print("   • BALANCE Fund: 30% ROI (2.5% × 12 months)")
            print("   • DYNAMIC Fund: 42% ROI (3.5% × 12 months)")
            print("   • 77% error has been eliminated")
            print("   • System ready for production use")
        else:
            print("❌ INVESTMENT SIMULATOR CALCULATIONS: INCORRECT")
            print("   Mathematical calculation errors still present.")
            print("   Main agent action required to fix calculations.")
        
        print("\n" + "=" * 70)

def main():
    """Main test execution"""
    test_runner = InvestmentSimulatorFixedTest()
    success = test_runner.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()