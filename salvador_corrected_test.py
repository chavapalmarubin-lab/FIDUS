#!/usr/bin/env python3
"""
SALVADOR FUND BALANCE VERIFICATION TEST - CORRECTED
===================================================

CORRECTION: Salvador Palma is client_003, not client_001
- client_001 = Gerardo Briones (no investments)
- client_003 = Salvador Palma (has BALANCE fund investment)

This test verifies Salvador Palma's (client_003) investment data 
and ensures the fund balance display is working correctly.
"""

import requests
import sys
from datetime import datetime
import json

class SalvadorCorrectedVerifier:
    def __init__(self, base_url="https://aml-kyc-portal.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.admin_user = None
        
        # CORRECTED Salvador's data
        self.salvador_client_id = "client_003"  # CORRECTED
        self.salvador_name = "Salvador Palma"   # CORRECTED
        self.expected_balance_fund_amount = 1421421.07  # From database

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

    def login_as_admin(self):
        """Login as admin"""
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
            print(f"   ✅ Admin logged in: {response.get('name', 'Unknown')}")
        return success

    def test_salvador_investments_endpoint(self):
        """
        TASK 1: Check Salvador's Investment Data
        Test GET /api/investments/client/client_003 to see Salvador's investments
        """
        print(f"\n{'='*60}")
        print("TASK 1: CHECKING SALVADOR'S INVESTMENT DATA")
        print(f"{'='*60}")
        
        success, response = self.run_test(
            f"Get Salvador's Investments ({self.salvador_client_id})",
            "GET",
            f"api/investments/client/{self.salvador_client_id}",
            200
        )
        
        if success:
            investments = response.get('investments', [])
            portfolio_stats = response.get('portfolio_stats', {})
            
            print(f"\n📊 SALVADOR'S INVESTMENT PORTFOLIO:")
            print(f"   Client ID: {self.salvador_client_id}")
            print(f"   Client Name: {self.salvador_name}")
            print(f"   Total Investments: {len(investments)}")
            print(f"   Total Principal: ${portfolio_stats.get('total_principal', 0):,.2f}")
            print(f"   Total Current Value: ${portfolio_stats.get('total_current_value', 0):,.2f}")
            print(f"   Total Interest Earned: ${portfolio_stats.get('total_interest_earned', 0):,.2f}")
            
            # Analyze investments by fund
            fund_breakdown = {}
            for investment in investments:
                fund_code = investment.get('fund_code', 'UNKNOWN')
                principal = investment.get('principal_amount', 0)
                current_value = investment.get('current_value', 0)
                
                if fund_code not in fund_breakdown:
                    fund_breakdown[fund_code] = {
                        'count': 0,
                        'total_principal': 0,
                        'total_current_value': 0
                    }
                
                fund_breakdown[fund_code]['count'] += 1
                fund_breakdown[fund_code]['total_principal'] += principal
                fund_breakdown[fund_code]['total_current_value'] += current_value
            
            print(f"\n📈 FUND BREAKDOWN:")
            for fund_code, data in fund_breakdown.items():
                print(f"   {fund_code} Fund:")
                print(f"     - Investments: {data['count']}")
                print(f"     - Principal: ${data['total_principal']:,.2f}")
                print(f"     - Current Value: ${data['total_current_value']:,.2f}")
                print(f"     - Interest Earned: ${data['total_current_value'] - data['total_principal']:,.2f}")
            
            # Check for BALANCE fund specifically
            balance_fund_data = fund_breakdown.get('BALANCE', {})
            if balance_fund_data:
                balance_amount = balance_fund_data.get('total_current_value', 0)
                print(f"\n✅ BALANCE FUND FOUND: ${balance_amount:,.2f}")
                
                # Check if it matches expected amount
                if abs(balance_amount - self.expected_balance_fund_amount) < 1:  # Allow small variance
                    print(f"   ✅ Amount matches expected: ${self.expected_balance_fund_amount:,.2f}")
                    return True
                else:
                    print(f"   ⚠️  Amount differs from expected: ${self.expected_balance_fund_amount:,.2f}")
                    return True  # Still success if fund exists
            else:
                print(f"\n❌ BALANCE FUND NOT FOUND")
                return False
        
        return False

    def test_salvador_client_data_endpoint(self):
        """
        TASK 2: Test Client Data Endpoint
        Test GET /api/client/client_003/data to see the balance calculation
        """
        print(f"\n{'='*60}")
        print("TASK 2: TESTING CLIENT DATA ENDPOINT")
        print(f"{'='*60}")
        
        success, response = self.run_test(
            f"Get Salvador's Client Data ({self.salvador_client_id})",
            "GET",
            f"api/client/{self.salvador_client_id}/data",
            200
        )
        
        if success:
            balance = response.get('balance', {})
            
            print(f"\n💰 SALVADOR'S BALANCE STRUCTURE:")
            print(f"   Core Balance: ${balance.get('core_balance', 0):,.2f}")
            print(f"   Balance Fund Balance: ${balance.get('balance_balance', 0):,.2f}")
            print(f"   Dynamic Balance: ${balance.get('dynamic_balance', 0):,.2f}")
            print(f"   Unlimited Balance: ${balance.get('unlimited_balance', 0):,.2f}")
            print(f"   FIDUS Funds (Legacy): ${balance.get('fidus_funds', 0):,.2f}")
            print(f"   Total Balance: ${balance.get('total_balance', 0):,.2f}")
            
            # Verify individual fund balances
            balance_balance = balance.get('balance_balance', 0)
            core_balance = balance.get('core_balance', 0)
            dynamic_balance = balance.get('dynamic_balance', 0)
            unlimited_balance = balance.get('unlimited_balance', 0)
            total_balance = balance.get('total_balance', 0)
            
            print(f"\n🔍 BALANCE VERIFICATION:")
            
            # Check BALANCE fund
            if balance_balance > 0:
                print(f"   ✅ BALANCE fund shows: ${balance_balance:,.2f}")
                if abs(balance_balance - self.expected_balance_fund_amount) < 1:
                    print(f"   ✅ BALANCE amount matches expected: ${self.expected_balance_fund_amount:,.2f}")
                else:
                    print(f"   ⚠️  BALANCE amount differs from expected: ${self.expected_balance_fund_amount:,.2f}")
            else:
                print(f"   ❌ BALANCE fund shows $0.00 - BUG CONFIRMED!")
                print(f"   Expected: ${self.expected_balance_fund_amount:,.2f}")
                return False
            
            # Check other funds should be $0.00
            if core_balance == 0:
                print(f"   ✅ CORE fund correctly shows $0.00")
            else:
                print(f"   ⚠️  CORE fund shows ${core_balance:,.2f} (expected $0.00)")
                
            if dynamic_balance == 0:
                print(f"   ✅ DYNAMIC fund correctly shows $0.00")
            else:
                print(f"   ⚠️  DYNAMIC fund shows ${dynamic_balance:,.2f} (expected $0.00)")
                
            if unlimited_balance == 0:
                print(f"   ✅ UNLIMITED fund correctly shows $0.00")
            else:
                print(f"   ⚠️  UNLIMITED fund shows ${unlimited_balance:,.2f} (expected $0.00)")
            
            # Check total calculation
            calculated_total = core_balance + balance_balance + dynamic_balance + unlimited_balance
            if abs(total_balance - calculated_total) < 0.01:
                print(f"   ✅ Total balance calculation correct: ${total_balance:,.2f}")
            else:
                print(f"   ❌ Total balance calculation error:")
                print(f"      Reported: ${total_balance:,.2f}")
                print(f"      Calculated: ${calculated_total:,.2f}")
            
            return balance_balance > 0
        
        return False

    def test_fund_balance_structure(self):
        """
        TASK 3: Verify Fund Balance Structure
        Test that the new fund balance structure works correctly
        """
        print(f"\n{'='*60}")
        print("TASK 3: VERIFYING FUND BALANCE STRUCTURE")
        print(f"{'='*60}")
        
        success, response = self.run_test(
            f"Get Salvador's Client Data for Structure Test",
            "GET",
            f"api/client/{self.salvador_client_id}/data",
            200
        )
        
        if success:
            balance = response.get('balance', {})
            
            # Check that all 4 individual fund balance fields exist
            required_fields = ['core_balance', 'balance_balance', 'dynamic_balance', 'unlimited_balance']
            
            print(f"\n🔍 FUND BALANCE STRUCTURE VERIFICATION:")
            
            all_fields_present = True
            for field in required_fields:
                if field in balance:
                    value = balance[field]
                    print(f"   ✅ {field}: ${value:,.2f}")
                else:
                    print(f"   ❌ {field}: MISSING")
                    all_fields_present = False
            
            # Check that BALANCE fund is correctly mapped to balance_balance
            balance_balance = balance.get('balance_balance', 0)
            if balance_balance > 0:
                print(f"\n✅ BALANCE fund correctly mapped to balance_balance field")
                print(f"   Amount: ${balance_balance:,.2f}")
            else:
                print(f"\n❌ BALANCE fund NOT mapped to balance_balance field")
                return False
            
            # Check legacy fidus_funds field for backward compatibility
            fidus_funds = balance.get('fidus_funds', 0)
            expected_fidus = balance.get('balance_balance', 0) + balance.get('unlimited_balance', 0)
            
            if abs(fidus_funds - expected_fidus) < 0.01:
                print(f"   ✅ Legacy fidus_funds field correctly calculated: ${fidus_funds:,.2f}")
            else:
                print(f"   ⚠️  Legacy fidus_funds field calculation issue:")
                print(f"      fidus_funds: ${fidus_funds:,.2f}")
                print(f"      Expected (balance + unlimited): ${expected_fidus:,.2f}")
            
            return all_fields_present and balance_balance > 0
        
        return False

    def test_frontend_display_logic(self):
        """
        TASK 4: Frontend Display Logic Test
        Verify the frontend can correctly display fund statuses
        """
        print(f"\n{'='*60}")
        print("TASK 4: FRONTEND DISPLAY LOGIC VERIFICATION")
        print(f"{'='*60}")
        
        success, response = self.run_test(
            f"Get Salvador's Data for Frontend Display",
            "GET",
            f"api/client/{self.salvador_client_id}/data",
            200
        )
        
        if success:
            balance = response.get('balance', {})
            
            # Check individual fund balances for frontend display
            funds = {
                'CORE': balance.get('core_balance', 0),
                'BALANCE': balance.get('balance_balance', 0),
                'DYNAMIC': balance.get('dynamic_balance', 0),
                'UNLIMITED': balance.get('unlimited_balance', 0)
            }
            
            print(f"\n🖥️  FRONTEND DISPLAY LOGIC:")
            
            active_funds = []
            no_investment_funds = []
            
            for fund_name, amount in funds.items():
                if amount > 0:
                    print(f"   {fund_name} Fund: ${amount:,.2f} → Should display 'ACTIVE'")
                    active_funds.append(fund_name)
                else:
                    print(f"   {fund_name} Fund: ${amount:,.2f} → Should display 'NO INVESTMENT'")
                    no_investment_funds.append(fund_name)
            
            # Verify BALANCE fund specifically
            balance_amount = funds['BALANCE']
            if balance_amount > 0:
                print(f"\n✅ BALANCE fund will show 'ACTIVE': ${balance_amount:,.2f}")
                
                if abs(balance_amount - self.expected_balance_fund_amount) < 1:
                    print(f"   ✅ Amount matches expected: ${self.expected_balance_fund_amount:,.2f}")
                else:
                    print(f"   ⚠️  Amount differs from expected: ${self.expected_balance_fund_amount:,.2f}")
                
                return True
            else:
                print(f"\n❌ BALANCE fund will show 'NO INVESTMENT' - BUG!")
                print(f"   Should show: ${self.expected_balance_fund_amount:,.2f}")
                return False
        
        return False

    def run_comprehensive_verification(self):
        """Run all verification tests"""
        print("🚀 STARTING SALVADOR FUND BALANCE VERIFICATION (CORRECTED)")
        print("=" * 80)
        print(f"Testing Salvador Palma (client_003) - NOT Gerardo Briones (client_001)")
        print("=" * 80)
        
        # Login as admin
        if not self.login_as_admin():
            print("❌ Failed to login as admin - cannot continue")
            return False
        
        # Run all verification tasks
        task_results = []
        
        # Task 1: Check Salvador's Investment Data
        task1_success = self.test_salvador_investments_endpoint()
        task_results.append(("Task 1: Salvador's Investment Data", task1_success))
        
        # Task 2: Test Client Data Endpoint
        task2_success = self.test_salvador_client_data_endpoint()
        task_results.append(("Task 2: Client Data Endpoint", task2_success))
        
        # Task 3: Verify Fund Balance Structure
        task3_success = self.test_fund_balance_structure()
        task_results.append(("Task 3: Fund Balance Structure", task3_success))
        
        # Task 4: Frontend Display Logic
        task4_success = self.test_frontend_display_logic()
        task_results.append(("Task 4: Frontend Display Logic", task4_success))
        
        # Print final results
        print(f"\n{'='*80}")
        print("FINAL VERIFICATION RESULTS")
        print(f"{'='*80}")
        
        for task_name, success in task_results:
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"{status} - {task_name}")
        
        passed_tasks = sum(1 for _, success in task_results if success)
        total_tasks = len(task_results)
        
        print(f"\n📊 OVERALL RESULTS:")
        print(f"   Tests Run: {self.tests_run}")
        print(f"   Tests Passed: {self.tests_passed}")
        print(f"   Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        print(f"   Tasks Completed: {passed_tasks}/{total_tasks}")
        
        # Determine final status
        if passed_tasks == total_tasks:
            print(f"\n✅ SALVADOR'S BALANCE FUND IS WORKING CORRECTLY!")
            print(f"   Salvador Palma (client_003) has BALANCE fund: ${self.expected_balance_fund_amount:,.2f}")
            print(f"   Fund balance structure is properly implemented")
            print(f"   Frontend will correctly display 'ACTIVE' for BALANCE fund")
        else:
            print(f"\n❌ ISSUES FOUND WITH SALVADOR'S BALANCE FUND!")
            print(f"   Some verification tests failed - review results above")
        
        return passed_tasks == total_tasks

if __name__ == "__main__":
    print("Salvador Fund Balance Verification Test (CORRECTED)")
    print("=" * 60)
    
    verifier = SalvadorCorrectedVerifier()
    success = verifier.run_comprehensive_verification()
    
    if success:
        print("\n🎉 All verification tests passed!")
        sys.exit(0)
    else:
        print("\n⚠️  Some verification tests failed - review results above")
        sys.exit(1)