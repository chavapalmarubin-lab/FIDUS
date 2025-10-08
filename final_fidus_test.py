#!/usr/bin/env python3
"""
FINAL FIDUS Fund Calculations and Timeline Compliance Test Suite
==============================================================

This final test suite provides a comprehensive assessment of the FIDUS fund 
calculations and timeline compliance as requested in the review.
"""

import requests
import sys
from datetime import datetime, timedelta, timezone
import json
from dateutil.relativedelta import relativedelta

class FinalFidusFundTester:
    def __init__(self, base_url="https://mt5-deploy-debug.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.admin_user = None
        
    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        if headers is None:
            headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)

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
        return success

    def test_fund_specifications_compliance(self):
        """Test 1: Verify all FIDUS fund specifications are correct"""
        print("\n" + "="*80)
        print("TEST 1: FIDUS FUND SPECIFICATIONS COMPLIANCE")
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
        
        # Verify all 4 funds are present
        fund_codes = [fund.get('fund_code') for fund in funds]
        expected_funds = ['CORE', 'BALANCE', 'DYNAMIC', 'UNLIMITED']
        
        print(f"\n   Fund Verification:")
        for expected_fund in expected_funds:
            if expected_fund in fund_codes:
                print(f"   ✅ {expected_fund} fund present")
            else:
                print(f"   ❌ {expected_fund} fund missing")
                return False
        
        # Verify specific fund rules
        fund_specs = {
            'CORE': {
                'interest_rate': 1.5,
                'minimum_investment': 10000.0,
                'redemption_frequency': 'monthly',
                'description': '1.5% monthly simple interest, monthly redemptions, $10K min'
            },
            'BALANCE': {
                'interest_rate': 2.5,
                'minimum_investment': 50000.0,
                'redemption_frequency': 'quarterly',
                'description': '2.5% monthly simple interest, quarterly redemptions, $50K min'
            },
            'DYNAMIC': {
                'interest_rate': 3.5,
                'minimum_investment': 250000.0,
                'redemption_frequency': 'semi_annually',
                'description': '3.5% monthly simple interest, semi-annual redemptions, $250K min'
            },
            'UNLIMITED': {
                'interest_rate': 0.0,
                'minimum_investment': 1000000.0,
                'redemption_frequency': 'flexible',
                'invitation_only': True,
                'description': '50-50 performance sharing, flexible redemptions, $1M min, invitation only'
            }
        }
        
        all_specs_correct = True
        
        for fund in funds:
            fund_code = fund.get('fund_code')
            if fund_code in fund_specs:
                expected = fund_specs[fund_code]
                print(f"\n   {fund_code} Fund Specifications:")
                print(f"   Expected: {expected['description']}")
                
                # Check each specification
                for spec_key, expected_value in expected.items():
                    if spec_key == 'description':
                        continue
                        
                    actual_value = fund.get(spec_key)
                    if actual_value == expected_value:
                        print(f"   ✅ {spec_key}: {actual_value}")
                    else:
                        print(f"   ❌ {spec_key}: {actual_value} (expected {expected_value})")
                        all_specs_correct = False
                        
                # Check incubation and hold periods
                incubation_months = fund.get('incubation_period_months')
                hold_months = fund.get('minimum_hold_period_months')
                
                if incubation_months == 2:
                    print(f"   ✅ Incubation Period: 2 months")
                else:
                    print(f"   ❌ Incubation Period: {incubation_months} months (expected 2)")
                    all_specs_correct = False
                    
                if hold_months == 12:
                    print(f"   ✅ Commitment Period: 12 months (14 months total)")
                else:
                    print(f"   ❌ Commitment Period: {hold_months} months (expected 12)")
                    all_specs_correct = False
        
        return all_specs_correct

    def test_timeline_calculations(self):
        """Test 2: Verify timeline calculations are correct"""
        print("\n" + "="*80)
        print("TEST 2: TIMELINE CALCULATIONS VERIFICATION")
        print("="*80)
        
        # Test with specific date for predictable results
        test_deposit_date = "2024-01-15"
        
        success, response = self.run_test(
            "Create Investment for Timeline Test",
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
            
        investment = response.get('investment', {})
        
        # Parse dates
        deposit_date = datetime.fromisoformat(test_deposit_date + "T00:00:00+00:00")
        incubation_end_str = investment.get('incubation_end_date', '')
        interest_start_str = investment.get('interest_start_date', '')
        minimum_hold_end_str = investment.get('minimum_hold_end_date', '')
        
        print(f"\n   Timeline Verification for {test_deposit_date} deposit:")
        
        timeline_correct = True
        
        # Verify incubation end (exactly 2 months after deposit)
        if incubation_end_str:
            incubation_end = datetime.fromisoformat(incubation_end_str.replace('Z', '+00:00'))
            expected_incubation_end = deposit_date + relativedelta(months=2)
            
            if incubation_end.date() == expected_incubation_end.date():
                print(f"   ✅ Incubation End: {incubation_end.strftime('%Y-%m-%d')} (exactly 2 months after deposit)")
            else:
                print(f"   ❌ Incubation End: {incubation_end.strftime('%Y-%m-%d')} (expected {expected_incubation_end.strftime('%Y-%m-%d')})")
                timeline_correct = False
        else:
            print(f"   ❌ Incubation End Date not provided")
            timeline_correct = False
            
        # Verify interest start (exactly 2 months after deposit, same as incubation end)
        if interest_start_str:
            interest_start = datetime.fromisoformat(interest_start_str.replace('Z', '+00:00'))
            expected_interest_start = deposit_date + relativedelta(months=2)
            
            if interest_start.date() == expected_interest_start.date():
                print(f"   ✅ Interest Start: {interest_start.strftime('%Y-%m-%d')} (exactly 2 months after deposit)")
            else:
                print(f"   ❌ Interest Start: {interest_start.strftime('%Y-%m-%d')} (expected {expected_interest_start.strftime('%Y-%m-%d')})")
                timeline_correct = False
                
            # Critical check: Interest starts exactly when incubation ends
            if incubation_end_str and interest_start_str:
                if incubation_end_str == interest_start_str:
                    print(f"   ✅ CRITICAL: Interest starts exactly when incubation ends")
                else:
                    print(f"   ❌ CRITICAL: Interest start differs from incubation end")
                    timeline_correct = False
        else:
            print(f"   ❌ Interest Start Date not provided")
            timeline_correct = False
            
        # Verify minimum hold end (exactly 14 months after deposit)
        if minimum_hold_end_str:
            minimum_hold_end = datetime.fromisoformat(minimum_hold_end_str.replace('Z', '+00:00'))
            expected_minimum_hold_end = deposit_date + relativedelta(months=14)
            
            if minimum_hold_end.date() == expected_minimum_hold_end.date():
                print(f"   ✅ Minimum Hold End: {minimum_hold_end.strftime('%Y-%m-%d')} (exactly 14 months after deposit)")
            else:
                print(f"   ❌ Minimum Hold End: {minimum_hold_end.strftime('%Y-%m-%d')} (expected {expected_minimum_hold_end.strftime('%Y-%m-%d')})")
                timeline_correct = False
        else:
            print(f"   ❌ Minimum Hold End Date not provided")
            timeline_correct = False
            
        return timeline_correct

    def test_incubation_period_compliance(self):
        """Test 3: Verify NO INTEREST during 2-month incubation period"""
        print("\n" + "="*80)
        print("TEST 3: INCUBATION PERIOD COMPLIANCE - NO INTEREST")
        print("="*80)
        
        # Test 1: Investment still in incubation period
        future_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        
        success, response = self.run_test(
            "Create Investment in Incubation Period",
            "POST",
            "api/investments/create",
            200,
            data={
                "client_id": "client_001",
                "fund_code": "CORE",
                "amount": 10000.0,
                "deposit_date": future_date
            }
        )
        
        if not success:
            return False
            
        investment = response.get('investment', {})
        current_value = investment.get('current_value', 0)
        principal_amount = investment.get('principal_amount', 0)
        
        print(f"\n   Incubation Period Test:")
        print(f"   Deposit Date: {future_date} (future date, still in incubation)")
        print(f"   Principal: ${principal_amount:,.2f}")
        print(f"   Current Value: ${current_value:,.2f}")
        
        incubation_compliance = True
        
        if current_value == principal_amount:
            print(f"   ✅ NO INTEREST during incubation period (current value = principal)")
        else:
            print(f"   ❌ Interest earned during incubation period (current value ≠ principal)")
            incubation_compliance = False
            
        # Test 2: Check redemption eligibility during incubation
        success, redemption_response = self.run_test(
            "Check Redemption During Incubation",
            "GET",
            "api/redemptions/client/client_001",
            200
        )
        
        if success:
            redemptions = redemption_response.get('available_redemptions', [])
            
            # Find the investment we just created
            for redemption in redemptions:
                if redemption.get('deposit_date', '').startswith(future_date):
                    can_redeem_interest = redemption.get('can_redeem_interest', False)
                    can_redeem_principal = redemption.get('can_redeem_principal', False)
                    interest_message = redemption.get('interest_message', '')
                    
                    print(f"\n   Redemption During Incubation:")
                    print(f"   Can Redeem Interest: {can_redeem_interest}")
                    print(f"   Can Redeem Principal: {can_redeem_principal}")
                    print(f"   Message: {interest_message}")
                    
                    if not can_redeem_interest and not can_redeem_principal:
                        print(f"   ✅ NO REDEMPTIONS allowed during incubation period")
                    else:
                        print(f"   ❌ Redemptions allowed during incubation period")
                        incubation_compliance = False
                    break
        
        return incubation_compliance

    def test_interest_calculation_accuracy(self):
        """Test 4: Verify interest calculation accuracy"""
        print("\n" + "="*80)
        print("TEST 4: INTEREST CALCULATION ACCURACY")
        print("="*80)
        
        # Get existing investments to verify calculations
        success, response = self.run_test(
            "Get Client Investments for Calculation Test",
            "GET",
            "api/investments/client/client_001",
            200
        )
        
        if not success:
            return False
            
        investments = response.get('investments', [])
        
        print(f"\n   Testing interest calculations on existing investments:")
        
        calculation_accuracy = True
        tested_count = 0
        
        for investment in investments[:3]:  # Test first 3 investments
            investment_id = investment.get('investment_id', '')
            fund_code = investment.get('fund_code', '')
            deposit_date_str = investment.get('deposit_date', '')
            principal_amount = investment.get('principal_amount', 0)
            current_value = investment.get('current_value', 0)
            
            if not deposit_date_str or fund_code not in ['CORE', 'BALANCE', 'DYNAMIC']:
                continue
                
            tested_count += 1
            
            print(f"\n   Investment {investment_id[:8]} ({fund_code}):")
            print(f"   Deposit Date: {deposit_date_str}")
            print(f"   Principal: ${principal_amount:,.2f}")
            print(f"   Current Value: ${current_value:,.2f}")
            
            # Parse deposit date
            try:
                if 'T' in deposit_date_str:
                    deposit_date = datetime.fromisoformat(deposit_date_str.replace('Z', '+00:00'))
                else:
                    deposit_date = datetime.fromisoformat(deposit_date_str + "T00:00:00+00:00")
            except:
                print(f"   ⚠️  Could not parse deposit date")
                continue
                
            # Calculate expected interest
            incubation_end = deposit_date + relativedelta(months=2)
            now = datetime.now(timezone.utc)
            
            if now <= incubation_end:
                # Still in incubation - should have no interest
                expected_current_value = principal_amount
                print(f"   Expected (in incubation): ${expected_current_value:,.2f}")
            else:
                # Calculate months since interest started
                months_since_interest = (now.year - incubation_end.year) * 12 + (now.month - incubation_end.month)
                days_diff = now.day - incubation_end.day
                if days_diff >= 0:
                    fractional_month = days_diff / 30.0
                else:
                    months_since_interest -= 1
                    fractional_month = (30 + days_diff) / 30.0
                
                total_interest_months = months_since_interest + fractional_month
                
                # Get interest rate for fund
                interest_rates = {'CORE': 0.015, 'BALANCE': 0.025, 'DYNAMIC': 0.035}
                monthly_rate = interest_rates.get(fund_code, 0)
                
                expected_interest = principal_amount * monthly_rate * total_interest_months
                expected_current_value = principal_amount + expected_interest
                
                print(f"   Months of Interest: {total_interest_months:.2f}")
                print(f"   Monthly Rate: {monthly_rate*100:.1f}%")
                print(f"   Expected Interest: ${expected_interest:,.2f}")
                print(f"   Expected Current Value: ${expected_current_value:,.2f}")
            
            # Check accuracy (allow for reasonable tolerance)
            value_difference = abs(current_value - expected_current_value)
            tolerance = max(100, principal_amount * 0.01)  # $100 or 1% of principal, whichever is larger
            
            if value_difference <= tolerance:
                print(f"   ✅ Calculation accurate (difference: ${value_difference:.2f})")
            else:
                print(f"   ❌ Calculation inaccurate (difference: ${value_difference:.2f})")
                calculation_accuracy = False
        
        if tested_count == 0:
            print(f"   ⚠️  No suitable investments found for calculation testing")
            return True
            
        return calculation_accuracy

    def test_redemption_compliance(self):
        """Test 5: Verify redemption eligibility compliance"""
        print("\n" + "="*80)
        print("TEST 5: REDEMPTION ELIGIBILITY COMPLIANCE")
        print("="*80)
        
        success, response = self.run_test(
            "Get Redemption Eligibility Data",
            "GET",
            "api/redemptions/client/client_001",
            200
        )
        
        if not success:
            return False
            
        redemptions = response.get('available_redemptions', [])
        
        print(f"\n   Testing redemption eligibility rules:")
        
        redemption_compliance = True
        tested_scenarios = {
            'incubation': 0,
            'post_incubation': 0,
            'post_hold': 0
        }
        
        for redemption in redemptions[:5]:  # Test first 5 investments
            investment_id = redemption.get('investment_id', '')[:8]
            fund_code = redemption.get('fund_code', '')
            deposit_date_str = redemption.get('deposit_date', '')
            can_redeem_interest = redemption.get('can_redeem_interest', False)
            can_redeem_principal = redemption.get('can_redeem_principal', False)
            interest_message = redemption.get('interest_message', '')
            
            if not deposit_date_str:
                continue
                
            print(f"\n   Investment {investment_id} ({fund_code}):")
            
            # Parse deposit date
            try:
                if 'T' in deposit_date_str:
                    deposit_date = datetime.fromisoformat(deposit_date_str.replace('Z', '+00:00'))
                else:
                    deposit_date = datetime.fromisoformat(deposit_date_str + "T00:00:00+00:00")
            except:
                continue
                
            incubation_end = deposit_date + relativedelta(months=2)
            minimum_hold_end = deposit_date + relativedelta(months=14)
            now = datetime.now(timezone.utc)
            
            print(f"   Deposit: {deposit_date.strftime('%Y-%m-%d')}")
            print(f"   Interest: {can_redeem_interest}, Principal: {can_redeem_principal}")
            print(f"   Message: {interest_message}")
            
            if now < incubation_end:
                # During incubation (0-2 months): No redemptions allowed
                tested_scenarios['incubation'] += 1
                if not can_redeem_interest and not can_redeem_principal:
                    print(f"   ✅ Correctly blocked during incubation")
                else:
                    print(f"   ❌ Should be blocked during incubation")
                    redemption_compliance = False
                    
            elif now < minimum_hold_end:
                # After incubation but before minimum hold: Interest redemptions based on frequency
                tested_scenarios['post_incubation'] += 1
                if can_redeem_interest:
                    print(f"   ✅ Interest redemption available after incubation")
                else:
                    print(f"   ❌ Interest redemption should be available after incubation")
                    redemption_compliance = False
                    
            else:
                # After 14 months: Full redemption (interest + principal)
                tested_scenarios['post_hold'] += 1
                if can_redeem_interest and can_redeem_principal:
                    print(f"   ✅ Full redemption available after hold period")
                else:
                    print(f"   ❌ Full redemption should be available after hold period")
                    redemption_compliance = False
        
        print(f"\n   Tested scenarios: {tested_scenarios}")
        return redemption_compliance

    def run_comprehensive_test(self):
        """Run comprehensive FIDUS fund test suite"""
        print("🎯 FINAL FIDUS FUND CALCULATIONS AND TIMELINE COMPLIANCE TEST SUITE")
        print("=" * 80)
        print("Comprehensive verification of corrected FIDUS fund calculations")
        print("Focus: 2-month incubation period with NO INTEREST, exact timeline compliance")
        print("=" * 80)
        
        if not self.admin_login():
            print("❌ Failed to login as admin")
            return False
            
        tests = [
            ("Fund Specifications Compliance", self.test_fund_specifications_compliance),
            ("Timeline Calculations Verification", self.test_timeline_calculations),
            ("Incubation Period Compliance", self.test_incubation_period_compliance),
            ("Interest Calculation Accuracy", self.test_interest_calculation_accuracy),
            ("Redemption Eligibility Compliance", self.test_redemption_compliance)
        ]
        
        test_results = []
        for test_name, test_func in tests:
            try:
                print(f"\n{'='*20} RUNNING: {test_name} {'='*20}")
                result = test_func()
                test_results.append((test_name, result))
                if result:
                    print(f"✅ {test_name}: PASSED")
                else:
                    print(f"❌ {test_name}: FAILED")
            except Exception as e:
                print(f"❌ {test_name}: FAILED with exception: {str(e)}")
                test_results.append((test_name, False))
        
        # Final summary
        print("\n" + "="*80)
        print("FINAL FIDUS FUND TEST RESULTS")
        print("="*80)
        
        passed_tests = sum(1 for _, result in test_results if result)
        total_tests = len(test_results)
        
        for i, (test_name, result) in enumerate(test_results, 1):
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{i}. {test_name}: {status}")
        
        print(f"\nOverall Results: {passed_tests}/{total_tests} tests passed")
        print(f"API Calls: {self.tests_passed}/{self.tests_run} successful")
        
        if passed_tests == total_tests:
            print("\n🎉 ALL FIDUS FUND TESTS PASSED!")
            print("✅ Fund calculations and timeline compliance VERIFIED")
            print("✅ 2-month incubation period with NO INTEREST CONFIRMED")
            print("✅ Interest starts exactly 2 months after deposit CONFIRMED")
            print("✅ 14-month total commitment (2 incubation + 12 commitment) CONFIRMED")
            print("✅ All fund-specific rules working correctly")
            print("✅ Redemption eligibility rules properly enforced")
            return True
        else:
            failed_tests = total_tests - passed_tests
            print(f"\n⚠️  {failed_tests}/{total_tests} FIDUS FUND TESTS FAILED")
            print("Some fund calculations or timeline compliance issues detected")
            return False

if __name__ == "__main__":
    tester = FinalFidusFundTester()
    success = tester.run_comprehensive_test()
    sys.exit(0 if success else 1)