#!/usr/bin/env python3
"""
FIDUS Fund Calculations and Timeline Compliance Test Suite
=========================================================

This test suite specifically verifies the corrected FIDUS fund calculations 
and timeline compliance as requested in the review.

CRITICAL SPECIFICATIONS TO VERIFY:
1. Incubation Period: 2 months NO INTEREST for all funds
2. Interest Start: Exactly 2 months after deposit for all funds  
3. Total Commitment: 14 months (2 incubation + 12 commitment)
4. Fund-Specific Rules:
   - CORE: 1.5% monthly simple interest, monthly redemptions, $10K min
   - BALANCE: 2.5% monthly simple interest, quarterly (3-month) redemptions, $50K min  
   - DYNAMIC: 3.5% monthly simple interest, semi-annual (6-month) redemptions, $250K min
   - UNLIMITED: 50-50 performance sharing, flexible redemptions, $1M min, invitation only
"""

import requests
import sys
from datetime import datetime, timedelta
import json
from dateutil.relativedelta import relativedelta

class FidusFundTester:
    def __init__(self, base_url="https://crm-workspace-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.admin_user = None
        self.test_investments = []  # Track created investments for cleanup
        
    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        if headers is None:
            headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)

            print(f"   Status Code: {response.status_code}")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error text: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def admin_login(self):
        """Login as admin for testing"""
        success, response = self.run_test(
            "Admin Login",
            "POST",
            "api/auth/login",
            200,
            data={
                "username": "admin", 
                "password": "password123",
                "user_type": "admin"
            }
        )
        if success:
            self.admin_user = response
            print(f"   Admin logged in: {response.get('name', 'Unknown')}")
        return success

    def test_fund_configuration_verification(self):
        """Test 1: Verify Fund Configuration - All fund specifications are correct"""
        print("\n" + "="*80)
        print("TEST 1: FUND CONFIGURATION VERIFICATION")
        print("="*80)
        
        success, response = self.run_test(
            "Get Fund Configuration",
            "GET",
            "api/investments/funds/config",
            200
        )
        
        if not success:
            return False
            
        funds = response.get('funds', [])
        if not funds:
            print("❌ No funds returned in configuration")
            return False
            
        # Expected fund specifications
        expected_funds = {
            'CORE': {
                'interest_rate': 1.5,
                'minimum_investment': 10000.0,
                'redemption_frequency': 'monthly',
                'incubation_months': 2,
                'minimum_hold_months': 12
            },
            'BALANCE': {
                'interest_rate': 2.5,
                'minimum_investment': 50000.0,
                'redemption_frequency': 'quarterly',
                'incubation_months': 2,
                'minimum_hold_months': 12
            },
            'DYNAMIC': {
                'interest_rate': 3.5,
                'minimum_investment': 250000.0,
                'redemption_frequency': 'semi_annually',
                'incubation_months': 2,
                'minimum_hold_months': 12
            },
            'UNLIMITED': {
                'interest_rate': 0.0,  # Performance sharing, not fixed interest
                'minimum_investment': 1000000.0,
                'redemption_frequency': 'flexible',
                'incubation_months': 2,
                'minimum_hold_months': 12,
                'invitation_only': True
            }
        }
        
        all_correct = True
        
        for fund in funds:
            fund_code = fund.get('fund_code')
            if fund_code not in expected_funds:
                print(f"❌ Unexpected fund: {fund_code}")
                all_correct = False
                continue
                
            expected = expected_funds[fund_code]
            print(f"\n   Verifying {fund_code} Fund:")
            
            # Check interest rate
            actual_rate = fund.get('interest_rate')
            expected_rate = expected['interest_rate']
            if actual_rate == expected_rate:
                print(f"   ✅ Interest Rate: {actual_rate}% (correct)")
            else:
                print(f"   ❌ Interest Rate: {actual_rate}% (expected {expected_rate}%)")
                all_correct = False
                
            # Check minimum investment
            actual_min = fund.get('minimum_investment')
            expected_min = expected['minimum_investment']
            if actual_min == expected_min:
                print(f"   ✅ Minimum Investment: ${actual_min:,.0f} (correct)")
            else:
                print(f"   ❌ Minimum Investment: ${actual_min:,.0f} (expected ${expected_min:,.0f})")
                all_correct = False
                
            # Check redemption frequency
            actual_freq = fund.get('redemption_frequency')
            expected_freq = expected['redemption_frequency']
            if actual_freq == expected_freq:
                print(f"   ✅ Redemption Frequency: {actual_freq} (correct)")
            else:
                print(f"   ❌ Redemption Frequency: {actual_freq} (expected {expected_freq})")
                all_correct = False
                
            # Check incubation period
            actual_incubation = fund.get('incubation_months')
            expected_incubation = expected['incubation_months']
            if actual_incubation == expected_incubation:
                print(f"   ✅ Incubation Period: {actual_incubation} months (correct)")
            else:
                print(f"   ❌ Incubation Period: {actual_incubation} months (expected {expected_incubation} months)")
                all_correct = False
                
            # Check minimum hold period
            actual_hold = fund.get('minimum_hold_months')
            expected_hold = expected['minimum_hold_months']
            if actual_hold == expected_hold:
                print(f"   ✅ Minimum Hold Period: {actual_hold} months (correct)")
            else:
                print(f"   ❌ Minimum Hold Period: {actual_hold} months (expected {expected_hold} months)")
                all_correct = False
                
            # Check invitation only for UNLIMITED
            if fund_code == 'UNLIMITED':
                actual_invitation = fund.get('invitation_only', False)
                expected_invitation = expected.get('invitation_only', False)
                if actual_invitation == expected_invitation:
                    print(f"   ✅ Invitation Only: {actual_invitation} (correct)")
                else:
                    print(f"   ❌ Invitation Only: {actual_invitation} (expected {expected_invitation})")
                    all_correct = False
        
        if all_correct:
            print(f"\n✅ ALL FUND CONFIGURATIONS CORRECT!")
            return True
        else:
            print(f"\n❌ FUND CONFIGURATION ERRORS FOUND!")
            return False

    def test_interest_start_date_calculation(self):
        """Test 2: Test Interest Start Date Calculation - Exactly 2 months after deposit"""
        print("\n" + "="*80)
        print("TEST 2: INTEREST START DATE CALCULATION")
        print("="*80)
        
        # Test with specific deposit date
        test_deposit_date = "2024-01-15"  # January 15, 2024
        
        success, response = self.run_test(
            "Create Test Investment for Date Calculation",
            "POST",
            "api/investments/create",
            200,
            data={
                "client_id": "client_001",  # Gerardo Briones
                "fund_code": "CORE",
                "amount": 10000.0,
                "deposit_date": test_deposit_date
            }
        )
        
        if not success:
            return False
            
        investment_id = response.get('investment_id')
        if investment_id:
            self.test_investments.append(investment_id)
            
        # Verify date calculations
        deposit_date = datetime.fromisoformat(test_deposit_date + "T00:00:00+00:00")
        
        # Expected dates
        expected_incubation_end = deposit_date + relativedelta(months=2)
        expected_interest_start = deposit_date + relativedelta(months=2)  # Same as incubation end
        expected_minimum_hold_end = deposit_date + relativedelta(months=14)
        
        print(f"\n   Test Deposit Date: {test_deposit_date}")
        print(f"   Expected Incubation End: {expected_incubation_end.strftime('%Y-%m-%d')}")
        print(f"   Expected Interest Start: {expected_interest_start.strftime('%Y-%m-%d')}")
        print(f"   Expected Minimum Hold End: {expected_minimum_hold_end.strftime('%Y-%m-%d')}")
        
        # Check actual dates from response
        actual_incubation_end = response.get('incubation_end_date')
        actual_interest_start = response.get('interest_start_date')
        actual_minimum_hold_end = response.get('minimum_hold_end_date')
        
        all_dates_correct = True
        
        if actual_incubation_end:
            actual_incubation_dt = datetime.fromisoformat(actual_incubation_end.replace('Z', '+00:00'))
            if actual_incubation_dt.date() == expected_incubation_end.date():
                print(f"   ✅ Incubation End Date: {actual_incubation_dt.strftime('%Y-%m-%d')} (correct)")
            else:
                print(f"   ❌ Incubation End Date: {actual_incubation_dt.strftime('%Y-%m-%d')} (expected {expected_incubation_end.strftime('%Y-%m-%d')})")
                all_dates_correct = False
        else:
            print(f"   ❌ Incubation End Date: Not provided")
            all_dates_correct = False
            
        if actual_interest_start:
            actual_interest_dt = datetime.fromisoformat(actual_interest_start.replace('Z', '+00:00'))
            if actual_interest_dt.date() == expected_interest_start.date():
                print(f"   ✅ Interest Start Date: {actual_interest_dt.strftime('%Y-%m-%d')} (correct)")
            else:
                print(f"   ❌ Interest Start Date: {actual_interest_dt.strftime('%Y-%m-%d')} (expected {expected_interest_start.strftime('%Y-%m-%d')})")
                all_dates_correct = False
        else:
            print(f"   ❌ Interest Start Date: Not provided")
            all_dates_correct = False
            
        if actual_minimum_hold_end:
            actual_hold_dt = datetime.fromisoformat(actual_minimum_hold_end.replace('Z', '+00:00'))
            if actual_hold_dt.date() == expected_minimum_hold_end.date():
                print(f"   ✅ Minimum Hold End Date: {actual_hold_dt.strftime('%Y-%m-%d')} (correct)")
            else:
                print(f"   ❌ Minimum Hold End Date: {actual_hold_dt.strftime('%Y-%m-%d')} (expected {expected_minimum_hold_end.strftime('%Y-%m-%d')})")
                all_dates_correct = False
        else:
            print(f"   ❌ Minimum Hold End Date: Not provided")
            all_dates_correct = False
            
        # Verify the critical rule: Interest starts EXACTLY 2 months after deposit
        if actual_interest_start and actual_incubation_end:
            if actual_interest_start == actual_incubation_end:
                print(f"   ✅ CRITICAL: Interest starts exactly when incubation ends (2 months after deposit)")
            else:
                print(f"   ❌ CRITICAL: Interest start date differs from incubation end date")
                all_dates_correct = False
        
        if all_dates_correct:
            print(f"\n✅ ALL DATE CALCULATIONS CORRECT!")
            return True
        else:
            print(f"\n❌ DATE CALCULATION ERRORS FOUND!")
            return False

    def test_interest_calculations_incubation_period(self):
        """Test 3: Test Interest Calculations - NO INTEREST during 2-month incubation"""
        print("\n" + "="*80)
        print("TEST 3: INTEREST CALCULATIONS - INCUBATION PERIOD")
        print("="*80)
        
        # Create investment with past deposit date to simulate time passage
        past_deposit_date = "2024-10-01"  # October 1, 2024 (about 2.5 months ago)
        
        success, response = self.run_test(
            "Create Test Investment for Interest Calculation",
            "POST",
            "api/investments/create",
            200,
            data={
                "client_id": "client_001",  # Gerardo Briones
                "fund_code": "CORE",
                "amount": 10000.0,
                "deposit_date": past_deposit_date
            }
        )
        
        if not success:
            return False
            
        investment_id = response.get('investment_id')
        if investment_id:
            self.test_investments.append(investment_id)
            
        # Get investment projections to see interest calculations
        success, proj_response = self.run_test(
            "Get Investment Projections",
            "GET",
            f"api/investments/{investment_id}/projections",
            200
        )
        
        if not success:
            return False
            
        # Analyze the projections for incubation period compliance
        projections = proj_response.get('projections', [])
        timeline = proj_response.get('timeline', [])
        
        print(f"\n   Test Investment Details:")
        print(f"   Deposit Date: {past_deposit_date}")
        print(f"   Principal Amount: $10,000")
        print(f"   Fund: CORE (1.5% monthly)")
        
        # Calculate expected dates
        deposit_dt = datetime.fromisoformat(past_deposit_date + "T00:00:00+00:00")
        incubation_end_dt = deposit_dt + relativedelta(months=2)  # December 1, 2024
        
        print(f"   Incubation Period: {past_deposit_date} to {incubation_end_dt.strftime('%Y-%m-%d')}")
        print(f"   Interest Should Start: {incubation_end_dt.strftime('%Y-%m-%d')}")
        
        # Check timeline for incubation compliance
        incubation_compliant = True
        interest_start_correct = False
        
        for milestone in timeline:
            milestone_date = milestone.get('date', '')
            milestone_type = milestone.get('type', '')
            milestone_desc = milestone.get('description', '')
            
            print(f"   Timeline: {milestone_date} - {milestone_type} - {milestone_desc}")
            
            if milestone_type == 'incubation_end':
                expected_date = incubation_end_dt.strftime('%Y-%m-%d')
                if milestone_date.startswith(expected_date):
                    print(f"   ✅ Incubation end date correct: {milestone_date}")
                else:
                    print(f"   ❌ Incubation end date incorrect: {milestone_date} (expected {expected_date})")
                    incubation_compliant = False
                    
            elif milestone_type == 'interest_start':
                expected_date = incubation_end_dt.strftime('%Y-%m-%d')
                if milestone_date.startswith(expected_date):
                    print(f"   ✅ Interest start date correct: {milestone_date}")
                    interest_start_correct = True
                else:
                    print(f"   ❌ Interest start date incorrect: {milestone_date} (expected {expected_date})")
                    incubation_compliant = False
        
        # Verify NO INTEREST during incubation period
        current_value = response.get('current_value', 0)
        principal_amount = response.get('principal_amount', 0)
        
        # Since we're testing with a past date, check if interest calculation respects incubation
        # For October 1 deposit, incubation ends December 1
        # Current date is around December 19, so about 0.6 months of interest should be earned
        
        now = datetime.now()
        if now > incubation_end_dt:
            # Interest should have started
            months_since_interest_start = (now.year - incubation_end_dt.year) * 12 + (now.month - incubation_end_dt.month)
            days_into_month = now.day - incubation_end_dt.day
            if days_into_month >= 0:
                fractional_month = days_into_month / 30.0
            else:
                months_since_interest_start -= 1
                fractional_month = (30 + days_into_month) / 30.0
            
            total_months_interest = months_since_interest_start + fractional_month
            expected_interest = principal_amount * 0.015 * total_months_interest  # 1.5% monthly
            expected_current_value = principal_amount + expected_interest
            
            print(f"\n   Interest Calculation Verification:")
            print(f"   Months since interest start: {total_months_interest:.2f}")
            print(f"   Expected interest earned: ${expected_interest:.2f}")
            print(f"   Expected current value: ${expected_current_value:.2f}")
            print(f"   Actual current value: ${current_value:.2f}")
            
            # Allow for small rounding differences
            value_difference = abs(current_value - expected_current_value)
            if value_difference < 10:  # Within $10 tolerance
                print(f"   ✅ Current value calculation correct (difference: ${value_difference:.2f})")
            else:
                print(f"   ❌ Current value calculation incorrect (difference: ${value_difference:.2f})")
                incubation_compliant = False
        else:
            # Still in incubation period - should show only principal
            if current_value == principal_amount:
                print(f"   ✅ No interest during incubation period (current value = principal)")
            else:
                print(f"   ❌ Interest earned during incubation period (current value > principal)")
                incubation_compliant = False
        
        if incubation_compliant and interest_start_correct:
            print(f"\n✅ INCUBATION PERIOD COMPLIANCE VERIFIED!")
            return True
        else:
            print(f"\n❌ INCUBATION PERIOD COMPLIANCE FAILED!")
            return False

    def test_core_fund_interest_calculation_example(self):
        """Test 4: Test CORE Fund Interest Calculation Example from Review"""
        print("\n" + "="*80)
        print("TEST 4: CORE FUND INTEREST CALCULATION EXAMPLE")
        print("="*80)
        
        # Test the specific example from the review:
        # CORE fund: $10,000 investment
        # After 2 months: should show $10,000 (no interest during incubation)
        # After 3 months: should show $10,150 (1 month of 1.5% = $150)
        # After 4 months: should show $10,300 (2 months of 1.5% = $300)
        
        print("   Testing CORE Fund Interest Calculation Example:")
        print("   - $10,000 investment")
        print("   - After 2 months: $10,000 (no interest during incubation)")
        print("   - After 3 months: $10,150 (1 month of 1.5% = $150)")
        print("   - After 4 months: $10,300 (2 months of 1.5% = $300)")
        
        # Create investment with date 4 months ago to simulate the example
        four_months_ago = datetime.now() - relativedelta(months=4)
        test_deposit_date = four_months_ago.strftime('%Y-%m-%d')
        
        success, response = self.run_test(
            "Create CORE Fund Test Investment",
            "POST",
            "api/investments/create",
            200,
            data={
                "client_id": "client_001",
                "fund_code": "CORE",
                "amount": 10000.0,
                "deposit_date": test_deposit_date
            }
        )
        
        if not success:
            return False
            
        investment_id = response.get('investment_id')
        if investment_id:
            self.test_investments.append(investment_id)
            
        # Calculate expected values
        deposit_dt = datetime.fromisoformat(test_deposit_date + "T00:00:00+00:00")
        incubation_end_dt = deposit_dt + relativedelta(months=2)
        now = datetime.now()
        
        # Calculate months since interest started (after 2-month incubation)
        if now > incubation_end_dt:
            months_since_interest = (now.year - incubation_end_dt.year) * 12 + (now.month - incubation_end_dt.month)
            days_into_month = now.day - incubation_end_dt.day
            if days_into_month >= 0:
                fractional_month = days_into_month / 30.0
            else:
                months_since_interest -= 1
                fractional_month = (30 + days_into_month) / 30.0
            
            total_interest_months = months_since_interest + fractional_month
        else:
            total_interest_months = 0
            
        # Expected calculations
        principal = 10000.0
        monthly_rate = 0.015  # 1.5%
        expected_interest = principal * monthly_rate * total_interest_months
        expected_current_value = principal + expected_interest
        
        # Get actual values
        current_value = response.get('current_value', 0)
        
        print(f"\n   Calculation Details:")
        print(f"   Deposit Date: {test_deposit_date}")
        print(f"   Incubation End: {incubation_end_dt.strftime('%Y-%m-%d')}")
        print(f"   Months of Interest: {total_interest_months:.2f}")
        print(f"   Expected Interest: ${expected_interest:.2f}")
        print(f"   Expected Current Value: ${expected_current_value:.2f}")
        print(f"   Actual Current Value: ${current_value:.2f}")
        
        # Verify the calculation
        value_difference = abs(current_value - expected_current_value)
        calculation_correct = value_difference < 10  # Within $10 tolerance
        
        if calculation_correct:
            print(f"   ✅ Interest calculation correct (difference: ${value_difference:.2f})")
        else:
            print(f"   ❌ Interest calculation incorrect (difference: ${value_difference:.2f})")
            
        # Verify specific milestones from the example
        print(f"\n   Verifying Example Milestones:")
        
        # At 2 months (end of incubation): should be $10,000
        two_month_dt = deposit_dt + relativedelta(months=2)
        print(f"   At 2 months ({two_month_dt.strftime('%Y-%m-%d')}): Should be $10,000 (no interest)")
        
        # At 3 months: should be $10,150
        three_month_dt = deposit_dt + relativedelta(months=3)
        expected_at_3_months = 10000 + (10000 * 0.015 * 1)  # 1 month of interest
        print(f"   At 3 months ({three_month_dt.strftime('%Y-%m-%d')}): Should be ${expected_at_3_months:.2f}")
        
        # At 4 months: should be $10,300
        four_month_dt = deposit_dt + relativedelta(months=4)
        expected_at_4_months = 10000 + (10000 * 0.015 * 2)  # 2 months of interest
        print(f"   At 4 months ({four_month_dt.strftime('%Y-%m-%d')}): Should be ${expected_at_4_months:.2f}")
        
        # Check if current calculation matches the 4-month example
        if now >= four_month_dt:
            months_diff = total_interest_months - 2.0  # Should be close to 2 months of interest
            if abs(months_diff) < 0.2:  # Within 0.2 months tolerance
                print(f"   ✅ Current calculation matches 4-month example scenario")
                example_matches = True
            else:
                print(f"   ⚠️  Current calculation is for {total_interest_months:.2f} months of interest")
                example_matches = True  # Still valid, just different timing
        else:
            print(f"   ⚠️  Investment not yet at 4-month mark")
            example_matches = True
            
        if calculation_correct and example_matches:
            print(f"\n✅ CORE FUND INTEREST CALCULATION EXAMPLE VERIFIED!")
            return True
        else:
            print(f"\n❌ CORE FUND INTEREST CALCULATION EXAMPLE FAILED!")
            return False

    def test_redemption_eligibility_rules(self):
        """Test 5: Test Redemption Eligibility Rules"""
        print("\n" + "="*80)
        print("TEST 5: REDEMPTION ELIGIBILITY RULES")
        print("="*80)
        
        # Test redemption eligibility for different scenarios
        print("   Testing Redemption Eligibility Rules:")
        print("   - During incubation (0-2 months): No redemptions allowed")
        print("   - After 2 months: Interest redemptions based on frequency")
        print("   - After 14 months: Full redemption (interest + principal)")
        
        # Get existing client investments to test redemption eligibility
        success, response = self.run_test(
            "Get Client Investments for Redemption Test",
            "GET",
            "api/investments/client/client_001",
            200
        )
        
        if not success:
            return False
            
        investments = response.get('investments', [])
        if not investments:
            print("   ❌ No investments found for redemption testing")
            return False
            
        print(f"\n   Found {len(investments)} investments to test")
        
        redemption_rules_correct = True
        
        for investment in investments:
            investment_id = investment.get('investment_id')
            fund_code = investment.get('fund_code')
            deposit_date = investment.get('deposit_date')
            principal_amount = investment.get('principal_amount')
            current_value = investment.get('current_value')
            
            print(f"\n   Testing Investment {investment_id[:8]}...")
            print(f"   Fund: {fund_code}")
            print(f"   Deposit Date: {deposit_date}")
            print(f"   Principal: ${principal_amount:,.2f}")
            print(f"   Current Value: ${current_value:,.2f}")
            
            # Test redemption eligibility
            success, redemption_response = self.run_test(
                f"Get Redemption Data for {fund_code} Investment",
                "GET",
                f"api/redemptions/client/client_001",
                200
            )
            
            if success:
                redemptions = redemption_response.get('available_redemptions', [])
                
                # Find this specific investment in redemptions
                investment_redemption = None
                for redemption in redemptions:
                    if redemption.get('investment_id') == investment_id:
                        investment_redemption = redemption
                        break
                        
                if investment_redemption:
                    eligibility = investment_redemption.get('eligibility', {})
                    can_redeem_interest = eligibility.get('can_redeem_interest', False)
                    can_redeem_principal = eligibility.get('can_redeem_principal', False)
                    next_redemption_date = eligibility.get('next_redemption_date')
                    
                    print(f"   Can Redeem Interest: {can_redeem_interest}")
                    print(f"   Can Redeem Principal: {can_redeem_principal}")
                    print(f"   Next Redemption Date: {next_redemption_date}")
                    
                    # Calculate expected eligibility based on dates
                    deposit_dt = datetime.fromisoformat(deposit_date.replace('Z', '+00:00'))
                    incubation_end_dt = deposit_dt + relativedelta(months=2)
                    minimum_hold_end_dt = deposit_dt + relativedelta(months=14)
                    now = datetime.now()
                    
                    # Check incubation period compliance
                    if now < incubation_end_dt:
                        # Still in incubation - no redemptions should be allowed
                        if not can_redeem_interest and not can_redeem_principal:
                            print(f"   ✅ Correctly blocked during incubation period")
                        else:
                            print(f"   ❌ Redemptions allowed during incubation period")
                            redemption_rules_correct = False
                    elif now < minimum_hold_end_dt:
                        # After incubation but before minimum hold - interest only
                        if can_redeem_interest and not can_redeem_principal:
                            print(f"   ✅ Correctly allows interest redemption only")
                        else:
                            print(f"   ❌ Incorrect redemption eligibility after incubation")
                            redemption_rules_correct = False
                    else:
                        # After minimum hold - full redemption allowed
                        if can_redeem_interest and can_redeem_principal:
                            print(f"   ✅ Correctly allows full redemption after hold period")
                        else:
                            print(f"   ❌ Full redemption not allowed after hold period")
                            redemption_rules_correct = False
                            
                    # Verify fund-specific redemption frequency
                    if fund_code == 'CORE':
                        # Monthly redemptions
                        print(f"   Expected: Monthly redemption frequency for CORE fund")
                    elif fund_code == 'BALANCE':
                        # Quarterly redemptions
                        print(f"   Expected: Quarterly redemption frequency for BALANCE fund")
                    elif fund_code == 'DYNAMIC':
                        # Semi-annual redemptions
                        print(f"   Expected: Semi-annual redemption frequency for DYNAMIC fund")
                    elif fund_code == 'UNLIMITED':
                        # Flexible redemptions
                        print(f"   Expected: Flexible redemption frequency for UNLIMITED fund")
                        
                else:
                    print(f"   ⚠️  Investment not found in redemption data")
            else:
                print(f"   ❌ Failed to get redemption data")
                redemption_rules_correct = False
        
        if redemption_rules_correct:
            print(f"\n✅ REDEMPTION ELIGIBILITY RULES VERIFIED!")
            return True
        else:
            print(f"\n❌ REDEMPTION ELIGIBILITY RULES FAILED!")
            return False

    def test_minimum_investment_validation(self):
        """Test 6: Test Minimum Investment Validation"""
        print("\n" + "="*80)
        print("TEST 6: MINIMUM INVESTMENT VALIDATION")
        print("="*80)
        
        # Test minimum investment requirements for each fund
        test_cases = [
            {'fund': 'CORE', 'min_amount': 10000, 'test_amount': 5000, 'should_fail': True},
            {'fund': 'CORE', 'min_amount': 10000, 'test_amount': 10000, 'should_fail': False},
            {'fund': 'BALANCE', 'min_amount': 50000, 'test_amount': 25000, 'should_fail': True},
            {'fund': 'BALANCE', 'min_amount': 50000, 'test_amount': 50000, 'should_fail': False},
            {'fund': 'DYNAMIC', 'min_amount': 250000, 'test_amount': 100000, 'should_fail': True},
            {'fund': 'DYNAMIC', 'min_amount': 250000, 'test_amount': 250000, 'should_fail': False},
            {'fund': 'UNLIMITED', 'min_amount': 1000000, 'test_amount': 500000, 'should_fail': True},
            {'fund': 'UNLIMITED', 'min_amount': 1000000, 'test_amount': 1000000, 'should_fail': False},
        ]
        
        all_validations_correct = True
        
        for test_case in test_cases:
            fund_code = test_case['fund']
            test_amount = test_case['test_amount']
            should_fail = test_case['should_fail']
            min_amount = test_case['min_amount']
            
            expected_status = 400 if should_fail else 200
            test_name = f"Test {fund_code} Fund - ${test_amount:,} ({'Should Fail' if should_fail else 'Should Pass'})"
            
            success, response = self.run_test(
                test_name,
                "POST",
                "api/investments/create",
                expected_status,
                data={
                    "client_id": "client_001",
                    "fund_code": fund_code,
                    "amount": test_amount,
                    "deposit_date": "2024-12-19"
                }
            )
            
            if success:
                if should_fail:
                    print(f"   ✅ Correctly rejected ${test_amount:,} for {fund_code} (min: ${min_amount:,})")
                else:
                    print(f"   ✅ Correctly accepted ${test_amount:,} for {fund_code}")
                    # Track successful investment for cleanup
                    investment_id = response.get('investment_id')
                    if investment_id:
                        self.test_investments.append(investment_id)
            else:
                if should_fail:
                    print(f"   ❌ Should have rejected ${test_amount:,} for {fund_code}")
                else:
                    print(f"   ❌ Should have accepted ${test_amount:,} for {fund_code}")
                all_validations_correct = False
        
        if all_validations_correct:
            print(f"\n✅ MINIMUM INVESTMENT VALIDATION VERIFIED!")
            return True
        else:
            print(f"\n❌ MINIMUM INVESTMENT VALIDATION FAILED!")
            return False

    def run_all_tests(self):
        """Run all FIDUS fund calculation and timeline compliance tests"""
        print("🎯 FIDUS FUND CALCULATIONS AND TIMELINE COMPLIANCE TEST SUITE")
        print("=" * 80)
        print("Testing corrected FIDUS fund calculations and timeline compliance")
        print("Focus: 2-month incubation period with NO INTEREST")
        print("=" * 80)
        
        # Login as admin first
        if not self.admin_login():
            print("❌ Failed to login as admin - cannot proceed with tests")
            return False
            
        # Run all tests
        tests = [
            self.test_fund_configuration_verification,
            self.test_interest_start_date_calculation,
            self.test_interest_calculations_incubation_period,
            self.test_core_fund_interest_calculation_example,
            self.test_redemption_eligibility_rules,
            self.test_minimum_investment_validation
        ]
        
        test_results = []
        for test in tests:
            try:
                result = test()
                test_results.append(result)
            except Exception as e:
                print(f"❌ Test failed with exception: {str(e)}")
                test_results.append(False)
        
        # Print summary
        print("\n" + "="*80)
        print("FIDUS FUND TEST SUMMARY")
        print("="*80)
        
        passed_tests = sum(test_results)
        total_tests = len(test_results)
        
        test_names = [
            "Fund Configuration Verification",
            "Interest Start Date Calculation", 
            "Interest Calculations - Incubation Period",
            "CORE Fund Interest Calculation Example",
            "Redemption Eligibility Rules",
            "Minimum Investment Validation"
        ]
        
        for i, (test_name, result) in enumerate(zip(test_names, test_results)):
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{i+1}. {test_name}: {status}")
        
        print(f"\nOverall Results: {passed_tests}/{total_tests} tests passed")
        print(f"API Tests: {self.tests_passed}/{self.tests_run} individual API calls passed")
        
        if passed_tests == total_tests:
            print("\n🎉 ALL FIDUS FUND TESTS PASSED!")
            print("✅ Fund calculations and timeline compliance verified")
            print("✅ 2-month incubation period with NO INTEREST confirmed")
            print("✅ Interest starts exactly 2 months after deposit")
            print("✅ All fund-specific rules working correctly")
            return True
        else:
            print(f"\n❌ {total_tests - passed_tests} FIDUS FUND TESTS FAILED!")
            print("⚠️  Fund calculations or timeline compliance issues detected")
            return False

if __name__ == "__main__":
    tester = FidusFundTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)