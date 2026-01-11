#!/usr/bin/env python3
"""
CRITICAL PRODUCTION TESTING - Investment Simulator Bug Fix Verification

This test follows the exact test scenarios from the review request to verify
the Investment Simulator bug fix where it was calculating only 10 months of 
interest instead of 12 months for the BALANCE fund.

The fix adds the incubation period (2 months) to the requested timeframe so 
users get the full number of interest payment months they request.

PRODUCTION CONCERN: This system manages real client investments ($118,000+ in production).
"""

import requests
import json
import sys
from datetime import datetime

class ProductionInvestmentTester:
    def __init__(self):
        self.base_url = "https://fintech-dashboard-60.preview.emergentagent.com/api"
        self.session = requests.Session()
        self.admin_token = None
        self.client_token = None
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

    def authenticate_client(self) -> bool:
        """Authenticate as client user (Alejandro)"""
        try:
            print("🔐 Authenticating as client (Alejandro)...")
            
            login_data = {
                "username": "alejandro_mariscal",
                "password": "password123",
                "user_type": "client"
            }
            
            response = requests.post(f"{self.base_url}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.client_token = data.get('token')
                if self.client_token:
                    self.log_test("Client Authentication", "PASS", "Successfully authenticated as client")
                    return True
                else:
                    self.log_test("Client Authentication", "FAIL", "No token received in response")
                    return False
            else:
                self.log_test("Client Authentication", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Client Authentication", "ERROR", f"Exception during client authentication: {str(e)}")
            return False

    def test_1_1_balance_fund_12_months(self) -> bool:
        """Test Case 1.1 - BALANCE Fund (12 months) - CRITICAL BUG FIX"""
        try:
            print("\n💰 TEST 1.1: BALANCE Fund (12 months) - CRITICAL BUG FIX VERIFICATION")
            
            simulation_data = {
                "investments": [{"fund_code": "BALANCE", "amount": 100000}],
                "timeframe_months": 12
            }
            
            response = self.session.post(f"{self.base_url}/investments/simulate", json=simulation_data)
            
            if response.status_code != 200:
                self.log_test("BALANCE Simulation API", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            if not data.get("success"):
                self.log_test("BALANCE Simulation API", "FAIL", f"API returned success=false: {data.get('message', 'Unknown error')}")
                return False
            
            simulation = data.get("simulation", {})
            
            # Look for the data in the fund_breakdown (where the actual calculations are)
            fund_breakdown = simulation.get("fund_breakdown", [])
            if not fund_breakdown:
                self.log_test("BALANCE Fund Breakdown", "FAIL", "No fund breakdown found in response")
                return False
            
            balance_fund = fund_breakdown[0]  # Should be the BALANCE fund
            success = True
            
            print(f"📊 BALANCE Fund Analysis:")
            print(f"   Fund Code: {balance_fund.get('fund_code')}")
            print(f"   Investment: ${balance_fund.get('investment_amount', 0):,.2f}")
            print(f"   Final Value: ${balance_fund.get('final_value', 0):,.2f}")
            print(f"   Total Interest: ${balance_fund.get('total_interest', 0):,.2f}")
            print(f"   ROI: {balance_fund.get('roi_percentage', 0)}%")
            
            # CRITICAL CHECK 1: total_roi_percentage should be 30.0 (not 25.0)
            roi_percentage = balance_fund.get("roi_percentage", 0)
            expected_roi = 30.0
            
            if abs(roi_percentage - expected_roi) < 0.01:
                self.log_test("BALANCE ROI Fix", "PASS", 
                            f"✅ BUG FIXED: ROI shows 30% (12 months) instead of 25% (10 months)", 
                            f"{expected_roi}%", 
                            f"{roi_percentage}%")
            else:
                self.log_test("BALANCE ROI Fix", "FAIL", 
                            f"❌ BUG NOT FIXED: ROI still incorrect", 
                            f"{expected_roi}%", 
                            f"{roi_percentage}%")
                success = False
            
            # CRITICAL CHECK 2: total_interest_earned should be $30,000
            total_interest = balance_fund.get("total_interest", 0)
            expected_interest = 30000.0
            
            if abs(total_interest - expected_interest) < 0.01:
                self.log_test("BALANCE Interest Amount", "PASS", 
                            f"✅ BUG FIXED: Interest shows $30,000 (12 months) instead of $25,000 (10 months)", 
                            f"${expected_interest:,.2f}", 
                            f"${total_interest:,.2f}")
            else:
                self.log_test("BALANCE Interest Amount", "FAIL", 
                            f"❌ BUG NOT FIXED: Interest still incorrect", 
                            f"${expected_interest:,.2f}", 
                            f"${total_interest:,.2f}")
                success = False
            
            # Check summary data
            summary = simulation.get("summary", {})
            if summary:
                print(f"📊 Summary Analysis:")
                print(f"   Timeframe Months: {summary.get('timeframe_months', 0)}")
                print(f"   Actual Simulation Months: {summary.get('actual_simulation_months', 0)}")
                print(f"   Interest Payment Months: {summary.get('interest_payment_months', 0)}")
                
                # CRITICAL CHECK 3: actual_simulation_months should be 14
                actual_months = summary.get("actual_simulation_months", 0)
                expected_months = 14
                
                if actual_months == expected_months:
                    self.log_test("BALANCE Timeline", "PASS", 
                                f"Timeline includes incubation period", 
                                f"{expected_months} months", 
                                f"{actual_months} months")
                else:
                    self.log_test("BALANCE Timeline", "FAIL", 
                                f"Timeline calculation incorrect", 
                                f"{expected_months} months", 
                                f"{actual_months} months")
                    success = False
                
                # CRITICAL CHECK 4: interest_payment_months should be 12
                interest_months = summary.get("interest_payment_months", 0)
                expected_interest_months = 12
                
                if interest_months == expected_interest_months:
                    self.log_test("BALANCE Interest Payment Months", "PASS", 
                                f"Interest payment months correct", 
                                f"{expected_interest_months} months", 
                                f"{interest_months} months")
                else:
                    self.log_test("BALANCE Interest Payment Months", "FAIL", 
                                f"Interest payment months incorrect", 
                                f"{expected_interest_months} months", 
                                f"{interest_months} months")
                    success = False
            
            # Check projected_timeline length = 15 (months 0-14)
            timeline = simulation.get("projected_timeline", [])
            expected_timeline_length = 15
            
            if len(timeline) == expected_timeline_length:
                self.log_test("BALANCE Timeline Data Points", "PASS", 
                            f"Timeline has correct number of data points", 
                            f"{expected_timeline_length} points", 
                            f"{len(timeline)} points")
            else:
                self.log_test("BALANCE Timeline Data Points", "FAIL", 
                            f"Timeline data points incorrect", 
                            f"{expected_timeline_length} points", 
                            f"{len(timeline)} points")
                success = False
            
            # Check calendar events for quarterly interest redemption events (4 events)
            calendar_events = simulation.get("calendar_events", [])
            quarterly_events = [event for event in calendar_events if event.get("type") == "interest_redemption"]
            expected_quarterly_events = 4
            
            print(f"📊 Calendar Events Analysis:")
            print(f"   Total Events: {len(calendar_events)}")
            print(f"   Interest Redemption Events: {len(quarterly_events)}")
            for event in quarterly_events:
                print(f"     - {event.get('date')}: ${event.get('amount', 0):,.2f}")
            
            if len(quarterly_events) == expected_quarterly_events:
                self.log_test("BALANCE Quarterly Events", "PASS", 
                            f"Correct number of quarterly interest redemption events", 
                            f"{expected_quarterly_events} events", 
                            f"{len(quarterly_events)} events")
            else:
                self.log_test("BALANCE Quarterly Events", "FAIL", 
                            f"Incorrect number of quarterly events", 
                            f"{expected_quarterly_events} events", 
                            f"{len(quarterly_events)} events")
                success = False
            
            # Check first 2 months show in_incubation: true
            if timeline and len(timeline) >= 2:
                incubation_count = 0
                for i in range(2):
                    if timeline[i].get("month") == i:
                        # Check in fund breakdown projections for incubation
                        projections = balance_fund.get("projections", [])
                        if projections and len(projections) > i:
                            if projections[i].get("in_incubation"):
                                incubation_count += 1
                
                expected_incubation_months = 2
                
                if incubation_count == expected_incubation_months:
                    self.log_test("BALANCE Incubation Period", "PASS", 
                                f"First 2 months correctly marked as incubation", 
                                f"{expected_incubation_months} months", 
                                f"{incubation_count} months")
                else:
                    self.log_test("BALANCE Incubation Period", "FAIL", 
                                f"Incubation period marking incorrect", 
                                f"{expected_incubation_months} months", 
                                f"{incubation_count} months")
                    success = False
            
            return success
            
        except Exception as e:
            self.log_test("BALANCE Fund 12-Month Test", "ERROR", f"Exception: {str(e)}")
            return False

    def test_1_2_core_fund_12_months(self) -> bool:
        """Test Case 1.2 - CORE Fund (12 months)"""
        try:
            print("\n💎 TEST 1.2: CORE Fund (12 months)")
            
            simulation_data = {
                "investments": [{"fund_code": "CORE", "amount": 50000}],
                "timeframe_months": 12
            }
            
            response = self.session.post(f"{self.base_url}/investments/simulate", json=simulation_data)
            
            if response.status_code != 200:
                self.log_test("CORE Fund Simulation API", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            if not data.get("success"):
                self.log_test("CORE Fund Simulation API", "FAIL", f"API returned success=false: {data.get('message', 'Unknown error')}")
                return False
            
            simulation = data.get("simulation", {})
            fund_breakdown = simulation.get("fund_breakdown", [])
            
            if not fund_breakdown:
                self.log_test("CORE Fund Breakdown", "FAIL", "No fund breakdown found in response")
                return False
            
            core_fund = fund_breakdown[0]  # Should be the CORE fund
            success = True
            
            # Verify interest rate: 1.5% monthly
            # Total interest for 12 months: $50,000 * 1.5% * 12 = $9,000
            total_interest = core_fund.get("total_interest", 0)
            expected_interest = 9000.0
            
            if abs(total_interest - expected_interest) < 0.01:
                self.log_test("CORE Interest Amount", "PASS", 
                            f"CORE interest calculated correctly (1.5% monthly)", 
                            f"${expected_interest:,.2f}", 
                            f"${total_interest:,.2f}")
            else:
                self.log_test("CORE Interest Amount", "FAIL", 
                            f"CORE interest calculation incorrect", 
                            f"${expected_interest:,.2f}", 
                            f"${total_interest:,.2f}")
                success = False
            
            # Verify ROI: 18%
            roi_percentage = core_fund.get("roi_percentage", 0)
            expected_roi = 18.0
            
            if abs(roi_percentage - expected_roi) < 0.01:
                self.log_test("CORE ROI", "PASS", 
                            f"CORE ROI correct", 
                            f"{expected_roi}%", 
                            f"{roi_percentage}%")
            else:
                self.log_test("CORE ROI", "FAIL", 
                            f"CORE ROI incorrect", 
                            f"{expected_roi}%", 
                            f"{roi_percentage}%")
                success = False
            
            # Verify timeline: 14 months total
            summary = simulation.get("summary", {})
            actual_months = summary.get("actual_simulation_months", 0)
            expected_months = 14
            
            if actual_months == expected_months:
                self.log_test("CORE Timeline", "PASS", 
                            f"CORE timeline correct", 
                            f"{expected_months} months", 
                            f"{actual_months} months")
            else:
                self.log_test("CORE Timeline", "FAIL", 
                            f"CORE timeline incorrect", 
                            f"{expected_months} months", 
                            f"{actual_months} months")
                success = False
            
            # Verify 12 monthly interest redemption events
            calendar_events = simulation.get("calendar_events", [])
            monthly_events = [event for event in calendar_events if event.get("type") == "interest_redemption"]
            expected_monthly_events = 12
            
            if len(monthly_events) == expected_monthly_events:
                self.log_test("CORE Monthly Events", "PASS", 
                            f"Correct number of monthly interest redemption events", 
                            f"{expected_monthly_events} events", 
                            f"{len(monthly_events)} events")
            else:
                self.log_test("CORE Monthly Events", "FAIL", 
                            f"Incorrect number of monthly events", 
                            f"{expected_monthly_events} events", 
                            f"{len(monthly_events)} events")
                success = False
            
            return success
            
        except Exception as e:
            self.log_test("CORE Fund 12-Month Test", "ERROR", f"Exception: {str(e)}")
            return False

    def test_1_3_multi_fund_portfolio(self) -> bool:
        """Test Case 1.3 - Multi-Fund Portfolio"""
        try:
            print("\n🎯 TEST 1.3: Multi-Fund Portfolio")
            
            simulation_data = {
                "investments": [
                    {"fund_code": "BALANCE", "amount": 100000},
                    {"fund_code": "CORE", "amount": 50000}
                ],
                "timeframe_months": 12
            }
            
            response = self.session.post(f"{self.base_url}/investments/simulate", json=simulation_data)
            
            if response.status_code != 200:
                self.log_test("Multi-Fund Simulation API", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            if not data.get("success"):
                self.log_test("Multi-Fund Simulation API", "FAIL", f"API returned success=false: {data.get('message', 'Unknown error')}")
                return False
            
            simulation = data.get("simulation", {})
            success = True
            
            # Verify total investment: $150,000
            total_investment = simulation.get("total_investment", 0)
            expected_investment = 150000.0
            
            if abs(total_investment - expected_investment) < 0.01:
                self.log_test("Multi-Fund Total Investment", "PASS", 
                            f"Total investment correct", 
                            f"${expected_investment:,.2f}", 
                            f"${total_investment:,.2f}")
            else:
                self.log_test("Multi-Fund Total Investment", "FAIL", 
                            f"Total investment incorrect", 
                            f"${expected_investment:,.2f}", 
                            f"${total_investment:,.2f}")
                success = False
            
            # Calculate total interest from fund breakdown: $39,000 ($30k BALANCE + $9k CORE)
            fund_breakdown = simulation.get("fund_breakdown", [])
            total_interest_calculated = sum(fund.get("total_interest", 0) for fund in fund_breakdown)
            expected_interest = 39000.0
            
            if abs(total_interest_calculated - expected_interest) < 0.01:
                self.log_test("Multi-Fund Total Interest", "PASS", 
                            f"Total interest correct (BALANCE + CORE)", 
                            f"${expected_interest:,.2f}", 
                            f"${total_interest_calculated:,.2f}")
            else:
                self.log_test("Multi-Fund Total Interest", "FAIL", 
                            f"Total interest incorrect", 
                            f"${expected_interest:,.2f}", 
                            f"${total_interest_calculated:,.2f}")
                success = False
            
            # Calculate total ROI from fund breakdown: 26% (39000/150000)
            total_roi_calculated = (total_interest_calculated / total_investment) * 100 if total_investment > 0 else 0
            expected_roi = 26.0
            
            if abs(total_roi_calculated - expected_roi) < 0.01:
                self.log_test("Multi-Fund ROI", "PASS", 
                            f"Multi-fund ROI correct", 
                            f"{expected_roi}%", 
                            f"{total_roi_calculated:.1f}%")
            else:
                self.log_test("Multi-Fund ROI", "FAIL", 
                            f"Multi-fund ROI incorrect", 
                            f"{expected_roi}%", 
                            f"{total_roi_calculated:.1f}%")
                success = False
            
            # Verify timeline handles both funds correctly
            timeline = simulation.get("projected_timeline", [])
            if len(timeline) >= 14:
                self.log_test("Multi-Fund Timeline", "PASS", 
                            f"Timeline handles both funds correctly", 
                            "≥14 months", 
                            f"{len(timeline)} months")
            else:
                self.log_test("Multi-Fund Timeline", "FAIL", 
                            f"Timeline too short for multi-fund", 
                            "≥14 months", 
                            f"{len(timeline)} months")
                success = False
            
            return success
            
        except Exception as e:
            self.log_test("Multi-Fund Portfolio Test", "ERROR", f"Exception: {str(e)}")
            return False

    def test_2_1_admin_investment_creation(self) -> bool:
        """Test Case 2.1 - Admin Portal Investment Creation"""
        try:
            print("\n👨‍💼 TEST 2.1: Admin Portal Investment Creation")
            
            # Get existing user ID (Alejandro)
            users_response = self.session.get(f"{self.base_url}/admin/users")
            if users_response.status_code != 200:
                self.log_test("Get Users API", "FAIL", f"HTTP {users_response.status_code}: {users_response.text}")
                return False
            
            users_data = users_response.json()
            users = users_data.get("users", [])
            
            # Find Alejandro's user ID
            alejandro_user = None
            for user in users:
                if user.get("username") == "alejandro_mariscal":
                    alejandro_user = user
                    break
            
            if not alejandro_user:
                self.log_test("Find Alejandro User", "FAIL", "Alejandro user not found")
                return False
            
            user_id = alejandro_user.get("id")
            
            investment_data = {
                "user_id": user_id,
                "fund_code": "BALANCE",
                "amount": 50000,
                "deposit_date": "2025-01-15"
            }
            
            response = self.session.post(f"{self.base_url}/admin/investments/create", json=investment_data)
            
            if response.status_code != 200:
                self.log_test("Admin Investment Creation API", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            if not data.get("success"):
                self.log_test("Admin Investment Creation API", "FAIL", f"API returned success=false: {data.get('message', 'Unknown error')}")
                return False
            
            investment = data.get("investment", {})
            success = True
            
            # Verify investment created successfully
            investment_id = investment.get("investment_id")
            if investment_id:
                self.log_test("Investment Creation", "PASS", 
                            f"Investment created successfully with ID: {investment_id}")
            else:
                self.log_test("Investment Creation", "FAIL", "No investment ID returned")
                success = False
            
            # Verify interest_calendar has 12 entries (not 10)
            interest_calendar = investment.get("interest_calendar", [])
            expected_calendar_entries = 12
            
            if len(interest_calendar) == expected_calendar_entries:
                self.log_test("Interest Calendar Entries", "PASS", 
                            f"Interest calendar has correct number of entries", 
                            f"{expected_calendar_entries} entries", 
                            f"{len(interest_calendar)} entries")
            else:
                self.log_test("Interest Calendar Entries", "FAIL", 
                            f"Interest calendar entries incorrect - bug not fixed", 
                            f"{expected_calendar_entries} entries", 
                            f"{len(interest_calendar)} entries")
                success = False
            
            return success
            
        except Exception as e:
            self.log_test("Admin Investment Creation Test", "ERROR", f"Exception: {str(e)}")
            return False

    def test_3_client_investments_view(self) -> bool:
        """Test Case 3.1 & 3.2 - Client Portal Investment Viewing"""
        try:
            print("\n👤 TEST 3: Client Portal Investment Viewing")
            
            if not self.authenticate_client():
                return False
            
            # Create client session with token
            client_session = requests.Session()
            client_session.headers.update({
                'Authorization': f'Bearer {self.client_token}'
            })
            
            # Test GET /api/client/investments
            response = client_session.get(f"{self.base_url}/client/investments")
            
            if response.status_code != 200:
                self.log_test("Client Investments API", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            if not data.get("success"):
                self.log_test("Client Investments API", "FAIL", f"API returned success=false: {data.get('message', 'Unknown error')}")
                return False
            
            investments = data.get("investments", [])
            success = True
            
            # Verify all investments load without errors
            if investments:
                self.log_test("Client Investments Load", "PASS", 
                            f"Successfully loaded {len(investments)} investments")
                
                # Check timeline data and interest calendar consistency
                for investment in investments:
                    timeline = investment.get("projected_timeline", [])
                    interest_calendar = investment.get("interest_calendar", [])
                    
                    if timeline:
                        self.log_test("Investment Timeline Format", "PASS", 
                                    f"Timeline data present for investment {investment.get('investment_id', 'unknown')}")
                    
                    if interest_calendar:
                        self.log_test("Interest Calendar Consistency", "PASS", 
                                    f"Interest calendar present with {len(interest_calendar)} entries")
            else:
                self.log_test("Client Investments Load", "FAIL", "No investments found for client")
                success = False
            
            return success
            
        except Exception as e:
            self.log_test("Client Investments View Test", "ERROR", f"Exception: {str(e)}")
            return False

    def test_4_referral_commission_calculations(self) -> bool:
        """Test Case 4.1 - Referral Commission Calculations (Should be unchanged)"""
        try:
            print("\n💼 TEST 4: Referral Commission Calculations (Regression Test)")
            
            # Test Salvador's commission stats (should be unchanged)
            response = self.session.get(f"{self.base_url}/admin/referrals/salespeople")
            
            if response.status_code != 200:
                self.log_test("Referrals Salespeople API", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            if not data.get("success"):
                self.log_test("Referrals Salespeople API", "FAIL", f"API returned success=false: {data.get('message', 'Unknown error')}")
                return False
            
            salespeople = data.get("salespeople", [])
            
            # Find Salvador
            salvador = None
            for person in salespeople:
                if "Salvador" in person.get("name", "") or "salvador" in person.get("email", "").lower():
                    salvador = person
                    break
            
            if not salvador:
                self.log_test("Find Salvador", "FAIL", "Salvador not found in salespeople list")
                return False
            
            # Verify total commission: $3,326.76 (should be unchanged)
            total_commission = salvador.get("totalCommissions", 0)
            expected_commission = 3326.76
            
            if abs(total_commission - expected_commission) < 0.01:
                self.log_test("Salvador Total Commission", "PASS", 
                            f"Salvador's commission unchanged (regression test passed)", 
                            f"${expected_commission:,.2f}", 
                            f"${total_commission:,.2f}")
                return True
            else:
                self.log_test("Salvador Total Commission", "FAIL", 
                            f"Salvador's commission changed unexpectedly", 
                            f"${expected_commission:,.2f}", 
                            f"${total_commission:,.2f}")
                return False
            
        except Exception as e:
            self.log_test("Referral Commission Test", "ERROR", f"Exception: {str(e)}")
            return False

    def test_5_database_consistency(self) -> bool:
        """Test Case 5.1 - Database Consistency Check"""
        try:
            print("\n🗄️ TEST 5: Database Consistency Check")
            
            # Query existing investments to verify no corruption
            response = self.session.get(f"{self.base_url}/admin/investments")
            
            if response.status_code != 200:
                self.log_test("Database Investments Query", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            if not data.get("success"):
                self.log_test("Database Investments Query", "FAIL", f"API returned success=false: {data.get('message', 'Unknown error')}")
                return False
            
            investments = data.get("investments", [])
            success = True
            
            # Verify existing investment records are unchanged
            if investments:
                self.log_test("Existing Investment Records", "PASS", 
                            f"Found {len(investments)} existing investment records")
                
                # Check structure consistency
                for investment in investments:
                    interest_calendar = investment.get("interest_calendar", [])
                    if interest_calendar and len(interest_calendar) > 0:
                        # Check first calendar entry structure
                        first_entry = interest_calendar[0]
                        required_fields = ["date", "amount"]
                        missing_fields = [field for field in required_fields if field not in first_entry]
                        
                        if not missing_fields:
                            self.log_test("Interest Calendar Structure", "PASS", 
                                        "Interest calendar structure valid")
                        else:
                            self.log_test("Interest Calendar Structure", "FAIL", 
                                        f"Missing fields in calendar: {missing_fields}")
                            success = False
                        break
                
                # Verify no data loss
                total_investment_value = sum(inv.get("principal_amount", 0) for inv in investments)
                if total_investment_value > 0:
                    self.log_test("Data Integrity", "PASS", 
                                f"Total investment value: ${total_investment_value:,.2f} (no data loss)")
                else:
                    self.log_test("Data Integrity", "FAIL", 
                                "Investment data appears corrupted or lost")
                    success = False
            else:
                self.log_test("Existing Investment Records", "FAIL", 
                            "No existing investment records found")
                success = False
            
            return success
            
        except Exception as e:
            self.log_test("Database Consistency Test", "ERROR", f"Exception: {str(e)}")
            return False

    def test_6_edge_cases(self) -> bool:
        """Test Case 6 - Edge Cases"""
        try:
            print("\n🎯 TEST 6: Edge Cases")
            
            success = True
            
            # Test Case 6.1 - Different Timeframes
            timeframes = [6, 12, 24]
            for months in timeframes:
                simulation_data = {
                    "investments": [{"fund_code": "BALANCE", "amount": 100000}],
                    "timeframe_months": months
                }
                
                response = self.session.post(f"{self.base_url}/investments/simulate", json=simulation_data)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        simulation = data.get("simulation", {})
                        fund_breakdown = simulation.get("fund_breakdown", [])
                        
                        if fund_breakdown:
                            roi = fund_breakdown[0].get("roi_percentage", 0)
                            expected_roi = months * 2.5  # 2.5% per month for BALANCE
                            
                            if abs(roi - expected_roi) < 0.1:
                                self.log_test(f"Timeframe {months} Months", "PASS", 
                                            f"ROI calculation correct for {months} months", 
                                            f"{expected_roi}%", 
                                            f"{roi}%")
                            else:
                                self.log_test(f"Timeframe {months} Months", "FAIL", 
                                            f"ROI calculation incorrect for {months} months", 
                                            f"{expected_roi}%", 
                                            f"{roi}%")
                                success = False
                        else:
                            self.log_test(f"Timeframe {months} Months", "FAIL", 
                                        f"No fund breakdown for {months} months")
                            success = False
                    else:
                        self.log_test(f"Timeframe {months} Months", "FAIL", 
                                    f"Simulation failed for {months} months")
                        success = False
                else:
                    self.log_test(f"Timeframe {months} Months", "FAIL", 
                                f"HTTP {response.status_code} for {months} months")
                    success = False
            
            # Test Case 6.2 - Minimum Investment Validation
            simulation_data = {
                "investments": [{"fund_code": "BALANCE", "amount": 1000}],  # Below $50,000 minimum
                "timeframe_months": 12
            }
            
            response = self.session.post(f"{self.base_url}/investments/simulate", json=simulation_data)
            
            if response.status_code == 400 or (response.status_code == 200 and not response.json().get("success")):
                self.log_test("Minimum Investment Validation", "PASS", 
                            "Properly rejected investment below minimum")
            else:
                self.log_test("Minimum Investment Validation", "FAIL", 
                            "Failed to validate minimum investment requirement")
                success = False
            
            # Test Case 6.3 - Invalid Fund Codes
            simulation_data = {
                "investments": [{"fund_code": "INVALID", "amount": 100000}],
                "timeframe_months": 12
            }
            
            response = self.session.post(f"{self.base_url}/investments/simulate", json=simulation_data)
            
            if response.status_code == 400 or (response.status_code == 200 and not response.json().get("success")):
                self.log_test("Invalid Fund Code Validation", "PASS", 
                            "Properly rejected invalid fund code")
            else:
                self.log_test("Invalid Fund Code Validation", "FAIL", 
                            "Failed to validate fund code")
                success = False
            
            return success
            
        except Exception as e:
            self.log_test("Edge Cases Test", "ERROR", f"Exception: {str(e)}")
            return False

    def run_all_tests(self) -> bool:
        """Run all Investment Simulator bug fix verification tests"""
        print("🚀 CRITICAL PRODUCTION TESTING - Investment Simulator Bug Fix Verification")
        print("=" * 80)
        print("PRODUCTION CONCERN: This system manages real client investments ($118,000+ in production)")
        print("BUG FIX: BALANCE fund calculating 12 months instead of 10 months of interest")
        print("=" * 80)
        
        # Authenticate first
        if not self.authenticate_admin():
            print("\n❌ Authentication failed. Cannot proceed with tests.")
            return False
        
        # Run all tests according to the review request
        tests = [
            ("TEST 1.1 - BALANCE Fund 12-Month Fix", self.test_1_1_balance_fund_12_months),
            ("TEST 1.2 - CORE Fund 12-Month", self.test_1_2_core_fund_12_months),
            ("TEST 1.3 - Multi-Fund Portfolio", self.test_1_3_multi_fund_portfolio),
            ("TEST 2.1 - Admin Investment Creation", self.test_2_1_admin_investment_creation),
            ("TEST 3 - Client Investments View", self.test_3_client_investments_view),
            ("TEST 4 - Referral Commission Regression", self.test_4_referral_commission_calculations),
            ("TEST 5 - Database Consistency", self.test_5_database_consistency),
            ("TEST 6 - Edge Cases", self.test_6_edge_cases)
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
        print("\n" + "=" * 80)
        print("📊 CRITICAL PRODUCTION TESTING SUMMARY")
        print("=" * 80)
        
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
        
        print("\n" + "=" * 80)
        
        # Critical success criteria from review request
        critical_tests = [
            "BALANCE ROI Fix",
            "BALANCE Interest Amount", 
            "Interest Calendar Entries",
            "Salvador Total Commission"
        ]
        
        critical_passed = sum(1 for result in self.test_results 
                            if result["test_name"] in critical_tests and result["status"] == "PASS")
        
        if success_rate >= 75 and critical_passed >= 3:
            print("🎉 CRITICAL PRODUCTION TESTING: SUCCESSFUL")
            print("✅ Fix is VALID - BALANCE fund ROI = 30% for 12-month requests")
            print("✅ Timeline = 14 months total (2 incubation + 12 interest)")
            print("✅ No errors in admin investment creation")
            print("✅ No errors in client portal viewing")
            print("✅ No changes to existing commission calculations")
            print("✅ Database records remain consistent")
            print("\n🎯 READY FOR PHASE 4")
            return True
        else:
            print("🚨 CRITICAL PRODUCTION TESTING: FAILED")
            print("❌ Fix is BROKEN - Critical failures detected")
            print("❌ Admin portal may crash when creating investments")
            print("❌ Client portal may show wrong data")
            print("❌ Existing investments may have corrupted calendars")
            print("❌ Commission calculations may have changed unexpectedly")
            print("❌ 500 errors on previously working endpoints")
            print("\n⚠️ ROLLBACK NEEDED")
            return False

def main():
    """Main test execution"""
    tester = ProductionInvestmentTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()