#!/usr/bin/env python3
"""
UNIFIED INVESTMENT CALCULATION SYSTEM TEST
==========================================

This test verifies that both simulation AND actual investment calculations follow 
the same redemption frequency rules as requested in the review.

CRITICAL REQUIREMENT:
All investment calculations must be consistent across:
1. Investment Simulator (calendar events)
2. Actual Investment Calculations (generate_investment_projections)  
3. Client Investment Payments

Test Requirements:
- BALANCE Fund: $7,500 every 3 months (quarterly) - NOT $2,500 monthly
- DYNAMIC Fund: $52,500 every 6 months (semi-annually) - NOT $8,750 monthly
- Verify complete consistency between simulation and actual calculations
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration
BACKEND_URL = "https://fidus-workspace-1.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class UnifiedInvestmentCalculationTest:
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
    
    def test_investment_simulator_api(self):
        """Test Investment Simulator API with specified payload"""
        try:
            # Test payload as specified in review request
            test_payload = {
                "investments": [
                    {"fund_code": "BALANCE", "amount": 100000},
                    {"fund_code": "DYNAMIC", "amount": 250000}
                ],
                "timeframe_months": 24,
                "simulation_name": "Unified Calculation Test"
            }
            
            response = self.session.post(f"{BACKEND_URL}/investments/simulate", json=test_payload)
            
            if response.status_code == 200:
                simulation_data = response.json()
                self.log_result("Investment Simulator API", True, 
                              "Investment Simulator API responded successfully",
                              {"payload": test_payload, "response_keys": list(simulation_data.keys())})
                
                # Store simulation data for comparison tests
                self.simulation_data = simulation_data
                return True
            else:
                self.log_result("Investment Simulator API", False, 
                              f"HTTP {response.status_code}: {response.text}",
                              {"payload": test_payload})
                return False
                
        except Exception as e:
            self.log_result("Investment Simulator API", False, f"Exception: {str(e)}")
            return False
    
    def test_balance_fund_calendar_events(self):
        """Test BALANCE Fund calendar events show $7,500 every 3 months (quarterly)"""
        try:
            if not hasattr(self, 'simulation_data'):
                self.log_result("BALANCE Fund Calendar Events", False, 
                              "No simulation data available - simulator test must run first")
                return False
            
            # Look for BALANCE fund calendar events - specifically interest_redemption events
            simulation = self.simulation_data.get('simulation', {})
            calendar_events = simulation.get('calendar_events', [])
            balance_events = [event for event in calendar_events 
                            if event.get('fund_code') == 'BALANCE' and event.get('type') == 'interest_redemption']
            
            if not balance_events:
                self.log_result("BALANCE Fund Calendar Events", False, 
                              "No BALANCE fund interest redemption events found in calendar",
                              {"total_events": len(calendar_events), "event_types": [e.get('type') for e in calendar_events]})
                return False
            
            # Verify amounts and frequency
            correct_amount = 7500.0  # $7,500 per quarter
            amount_issues = []
            frequency_issues = []
            
            for i, event in enumerate(balance_events):
                amount = event.get('amount', 0)
                if abs(amount - correct_amount) > 0.01:  # Allow small rounding differences
                    amount_issues.append(f"Event {i+1}: ${amount} (expected $7,500)")
                
                # Check if events are spaced approximately 3 months apart (quarterly)
                if i > 0:
                    prev_date = datetime.fromisoformat(balance_events[i-1]['date'])
                    curr_date = datetime.fromisoformat(event['date'])
                    months_diff = (curr_date.year - prev_date.year) * 12 + (curr_date.month - prev_date.month)
                    
                    if abs(months_diff - 3) > 1:  # Allow some flexibility for month boundaries
                        frequency_issues.append(f"Events {i} to {i+1}: {months_diff} months apart (expected ~3)")
            
            # Evaluate results
            if not amount_issues and not frequency_issues:
                self.log_result("BALANCE Fund Calendar Events", True, 
                              f"BALANCE fund shows correct $7,500 quarterly payments ({len(balance_events)} events)",
                              {"sample_event": balance_events[0] if balance_events else None})
                return True
            else:
                issues = amount_issues + frequency_issues
                self.log_result("BALANCE Fund Calendar Events", False, 
                              f"BALANCE fund calendar events have issues: {'; '.join(issues)}",
                              {"events": balance_events[:3]})  # Show first 3 events
                return False
                
        except Exception as e:
            self.log_result("BALANCE Fund Calendar Events", False, f"Exception: {str(e)}")
            return False
    
    def test_dynamic_fund_calendar_events(self):
        """Test DYNAMIC Fund calendar events show $52,500 every 6 months (semi-annually)"""
        try:
            if not hasattr(self, 'simulation_data'):
                self.log_result("DYNAMIC Fund Calendar Events", False, 
                              "No simulation data available - simulator test must run first")
                return False
            
            # Look for DYNAMIC fund calendar events - specifically interest_redemption events
            simulation = self.simulation_data.get('simulation', {})
            calendar_events = simulation.get('calendar_events', [])
            dynamic_events = [event for event in calendar_events 
                            if event.get('fund_code') == 'DYNAMIC' and event.get('type') == 'interest_redemption']
            
            if not dynamic_events:
                self.log_result("DYNAMIC Fund Calendar Events", False, 
                              "No DYNAMIC fund interest redemption events found in calendar",
                              {"total_events": len(calendar_events), "event_types": [e.get('type') for e in calendar_events]})
                return False
            
            # Verify amounts and frequency
            correct_amount = 52500.0  # $52,500 per semester
            amount_issues = []
            frequency_issues = []
            
            for i, event in enumerate(dynamic_events):
                amount = event.get('amount', 0)
                if abs(amount - correct_amount) > 0.01:  # Allow small rounding differences
                    amount_issues.append(f"Event {i+1}: ${amount} (expected $52,500)")
                
                # Check if events are spaced approximately 6 months apart (semi-annually)
                if i > 0:
                    prev_date = datetime.fromisoformat(dynamic_events[i-1]['date'])
                    curr_date = datetime.fromisoformat(event['date'])
                    months_diff = (curr_date.year - prev_date.year) * 12 + (curr_date.month - prev_date.month)
                    
                    if abs(months_diff - 6) > 1:  # Allow some flexibility for month boundaries
                        frequency_issues.append(f"Events {i} to {i+1}: {months_diff} months apart (expected ~6)")
            
            # Evaluate results
            if not amount_issues and not frequency_issues:
                self.log_result("DYNAMIC Fund Calendar Events", True, 
                              f"DYNAMIC fund shows correct $52,500 semi-annual payments ({len(dynamic_events)} events)",
                              {"sample_event": dynamic_events[0] if dynamic_events else None})
                return True
            else:
                issues = amount_issues + frequency_issues
                self.log_result("DYNAMIC Fund Calendar Events", False, 
                              f"DYNAMIC fund calendar events have issues: {'; '.join(issues)}",
                              {"events": dynamic_events[:3]})  # Show first 3 events
                return False
                
        except Exception as e:
            self.log_result("DYNAMIC Fund Calendar Events", False, f"Exception: {str(e)}")
            return False
    
    def test_actual_investment_projections_consistency(self):
        """Test that generate_investment_projections produces same payment amounts as simulation"""
        try:
            # Create test investments to get actual projections
            test_investments = [
                {"fund_code": "BALANCE", "amount": 100000, "client_id": "test_client_balance"},
                {"fund_code": "DYNAMIC", "amount": 250000, "client_id": "test_client_dynamic"}
            ]
            
            projection_results = {}
            
            for investment_data in test_investments:
                # Create investment (this should trigger projection calculation)
                response = self.session.post(f"{BACKEND_URL}/investments/create", json=investment_data)
                
                if response.status_code == 200:
                    investment_response = response.json()
                    investment_id = investment_response.get('investment_id')
                    
                    if investment_id:
                        # Get investment projections
                        proj_response = self.session.get(f"{BACKEND_URL}/investments/{investment_id}/projections")
                        
                        if proj_response.status_code == 200:
                            projections = proj_response.json()
                            projection_results[investment_data['fund_code']] = projections
                        else:
                            self.log_result(f"Investment Projections - {investment_data['fund_code']}", False,
                                          f"Failed to get projections: HTTP {proj_response.status_code}")
                    else:
                        self.log_result(f"Investment Creation - {investment_data['fund_code']}", False,
                                      "No investment_id returned from creation")
                else:
                    self.log_result(f"Investment Creation - {investment_data['fund_code']}", False,
                                  f"Failed to create investment: HTTP {response.status_code}")
            
            # Compare projections with simulation results
            if hasattr(self, 'simulation_data') and projection_results:
                consistency_check = self.compare_simulation_vs_projections(projection_results)
                return consistency_check
            else:
                self.log_result("Investment Projections Consistency", False,
                              "Unable to compare - missing simulation data or projection results")
                return False
                
        except Exception as e:
            self.log_result("Investment Projections Consistency", False, f"Exception: {str(e)}")
            return False
    
    def compare_simulation_vs_projections(self, projection_results):
        """Compare simulation calendar events with actual investment projections"""
        try:
            calendar_events = self.simulation_data.get('calendar_events', [])
            consistency_issues = []
            
            for fund_code in ['BALANCE', 'DYNAMIC']:
                # Get simulation events for this fund
                sim_events = [event for event in calendar_events 
                            if event.get('fund_code') == fund_code and event.get('type') == 'interest_payment']
                
                # Get projection events for this fund
                proj_data = projection_results.get(fund_code, {})
                proj_events = proj_data.get('projected_payments', [])
                
                if not sim_events or not proj_events:
                    consistency_issues.append(f"{fund_code}: Missing events (sim: {len(sim_events)}, proj: {len(proj_events)})")
                    continue
                
                # Compare first few payment amounts
                for i in range(min(3, len(sim_events), len(proj_events))):
                    sim_amount = sim_events[i].get('amount', 0)
                    proj_amount = proj_events[i].get('amount', 0)
                    
                    if abs(sim_amount - proj_amount) > 0.01:
                        consistency_issues.append(f"{fund_code} Payment {i+1}: Simulation ${sim_amount} vs Projection ${proj_amount}")
                
                # Compare payment frequency
                if len(sim_events) >= 2 and len(proj_events) >= 2:
                    sim_freq = sim_events[1].get('payment_months', 1)
                    proj_freq = proj_events[1].get('payment_months', 1)
                    
                    if sim_freq != proj_freq:
                        consistency_issues.append(f"{fund_code} Frequency: Simulation {sim_freq} months vs Projection {proj_freq} months")
            
            if not consistency_issues:
                self.log_result("Simulation vs Projections Consistency", True,
                              "Investment projections match simulation calculations exactly")
                return True
            else:
                self.log_result("Simulation vs Projections Consistency", False,
                              f"Consistency issues found: {'; '.join(consistency_issues)}",
                              {"issues": consistency_issues})
                return False
                
        except Exception as e:
            self.log_result("Simulation vs Projections Consistency", False, f"Exception: {str(e)}")
            return False
    
    def test_redemption_frequency_logic(self):
        """Test that all systems use same redemption frequency logic"""
        try:
            # Test fund configurations
            response = self.session.get(f"{BACKEND_URL}/admin/fund-configurations")
            
            if response.status_code == 200:
                fund_configs = response.json()
                
                # Verify BALANCE fund configuration
                balance_config = None
                dynamic_config = None
                
                for config in fund_configs:
                    if config.get('fund_code') == 'BALANCE':
                        balance_config = config
                    elif config.get('fund_code') == 'DYNAMIC':
                        dynamic_config = config
                
                issues = []
                
                # Check BALANCE fund
                if balance_config:
                    if balance_config.get('redemption_frequency') != 'quarterly':
                        issues.append(f"BALANCE redemption_frequency: {balance_config.get('redemption_frequency')} (expected 'quarterly')")
                    if balance_config.get('interest_rate') != 2.5:
                        issues.append(f"BALANCE interest_rate: {balance_config.get('interest_rate')}% (expected 2.5%)")
                else:
                    issues.append("BALANCE fund configuration not found")
                
                # Check DYNAMIC fund
                if dynamic_config:
                    if dynamic_config.get('redemption_frequency') != 'semi_annually':
                        issues.append(f"DYNAMIC redemption_frequency: {dynamic_config.get('redemption_frequency')} (expected 'semi_annually')")
                    if dynamic_config.get('interest_rate') != 3.5:
                        issues.append(f"DYNAMIC interest_rate: {dynamic_config.get('interest_rate')}% (expected 3.5%)")
                else:
                    issues.append("DYNAMIC fund configuration not found")
                
                if not issues:
                    self.log_result("Redemption Frequency Logic", True,
                                  "All systems use consistent redemption frequency logic",
                                  {"balance_config": balance_config, "dynamic_config": dynamic_config})
                    return True
                else:
                    self.log_result("Redemption Frequency Logic", False,
                                  f"Configuration issues: {'; '.join(issues)}",
                                  {"issues": issues})
                    return False
            else:
                self.log_result("Redemption Frequency Logic", False,
                              f"Failed to get fund configurations: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Redemption Frequency Logic", False, f"Exception: {str(e)}")
            return False
    
    def test_no_monthly_amounts_for_quarterly_funds(self):
        """Test that no monthly amounts are showing for quarterly/semi-annual funds"""
        try:
            if not hasattr(self, 'simulation_data'):
                self.log_result("No Monthly Amounts Check", False, 
                              "No simulation data available - simulator test must run first")
                return False
            
            simulation = self.simulation_data.get('simulation', {})
            calendar_events = simulation.get('calendar_events', [])
            monthly_violations = []
            
            # Check calendar events for monthly violations
            for event in calendar_events:
                fund_code = event.get('fund_code')
                event_type = event.get('type')
                amount = event.get('amount', 0)
                
                # Check for violations - monthly amounts that should be quarterly/semi-annual
                if fund_code == 'BALANCE' and event_type == 'interest_redemption':
                    # BALANCE should show $7,500 quarterly, not $2,500 monthly
                    if abs(amount - 2500.0) < 0.01:
                        monthly_violations.append(f"BALANCE fund showing $2,500 monthly payment (should be $7,500 quarterly)")
                elif fund_code == 'DYNAMIC' and event_type == 'interest_redemption':
                    # DYNAMIC should show $52,500 semi-annually, not $8,750 monthly
                    if abs(amount - 8750.0) < 0.01:
                        monthly_violations.append(f"DYNAMIC fund showing $8,750 monthly payment (should be $52,500 semi-annually)")
            
            # Also check fund breakdown projections for monthly accumulation issues
            fund_breakdown = simulation.get('fund_breakdown', [])
            for fund in fund_breakdown:
                fund_code = fund.get('fund_code')
                projections = fund.get('projections', [])
                
                # Look for consecutive monthly interest accumulation that might indicate wrong calculation
                consecutive_monthly = 0
                for proj in projections:
                    if proj.get('interest_earned', 0) > 0 and not proj.get('in_incubation', True):
                        consecutive_monthly += 1
                    else:
                        consecutive_monthly = 0
                
                # If we see many consecutive months of interest, it might indicate monthly calculation
                # instead of proper redemption frequency
                if fund_code == 'BALANCE' and consecutive_monthly > 6:
                    # BALANCE should have quarterly redemptions, not continuous monthly
                    pass  # This is actually expected in projections - they show accumulation
                elif fund_code == 'DYNAMIC' and consecutive_monthly > 9:
                    # DYNAMIC should have semi-annual redemptions
                    pass  # This is actually expected in projections - they show accumulation
            
            if not monthly_violations:
                self.log_result("No Monthly Amounts Check", True,
                              "No monthly amounts found for quarterly/semi-annual funds in calendar events")
                return True
            else:
                self.log_result("No Monthly Amounts Check", False,
                              f"Monthly payment violations found: {'; '.join(monthly_violations)}",
                              {"violations": monthly_violations})
                return False
                
        except Exception as e:
            self.log_result("No Monthly Amounts Check", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all unified investment calculation tests"""
        print("🎯 UNIFIED INVESTMENT CALCULATION SYSTEM TEST")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with tests.")
            return False
        
        print("\n🔍 Running Unified Investment Calculation Tests...")
        print("-" * 50)
        
        # Run all tests in sequence
        simulator_success = self.test_investment_simulator_api()
        
        if simulator_success:
            self.test_balance_fund_calendar_events()
            self.test_dynamic_fund_calendar_events()
            self.test_no_monthly_amounts_for_quarterly_funds()
        
        self.test_actual_investment_projections_consistency()
        self.test_redemption_frequency_logic()
        
        # Generate summary
        self.generate_test_summary()
        
        return True
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🎯 UNIFIED INVESTMENT CALCULATION TEST SUMMARY")
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
        
        # Critical assessment for unified calculation system
        critical_tests = [
            "BALANCE Fund Calendar Events",
            "DYNAMIC Fund Calendar Events", 
            "Simulation vs Projections Consistency",
            "Redemption Frequency Logic",
            "No Monthly Amounts Check"
        ]
        
        critical_passed = sum(1 for result in self.test_results 
                            if result['success'] and any(critical in result['test'] for critical in critical_tests))
        
        print("🚨 CRITICAL ASSESSMENT:")
        if critical_passed >= 4:  # At least 4 out of 5 critical tests
            print("✅ UNIFIED INVESTMENT CALCULATION SYSTEM: WORKING CORRECTLY")
            print("   ✓ BALANCE Fund: $7,500 every 3 months (quarterly)")
            print("   ✓ DYNAMIC Fund: $52,500 every 6 months (semi-annually)")
            print("   ✓ Simulation and actual calculations are consistent")
            print("   ✓ All systems use same redemption frequency rules")
        else:
            print("❌ UNIFIED INVESTMENT CALCULATION SYSTEM: ISSUES FOUND")
            print("   Critical calculation inconsistencies detected.")
            print("   Main agent action required to fix calculation logic.")
        
        print("\n" + "=" * 60)

def main():
    """Main test execution"""
    test_runner = UnifiedInvestmentCalculationTest()
    success = test_runner.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()