#!/usr/bin/env python3
"""
SALVADOR FUND BALANCE BUG VERIFICATION TEST
===========================================

This test specifically verifies Salvador's (client1/client_001) investment data 
and ensures the fund balance display is working correctly.

SPECIFIC TASKS:
1. Check Salvador's Investment Data - Test GET /api/investments/client/client_001
2. Test Client Data Endpoint - Test GET /api/client/client_001/data  
3. Verify Balance Calculation Logic - Test calculate_balances function
4. Frontend Integration Test - Verify individual fund balances display

EXPECTED RESULTS:
- Salvador should show his actual BALANCE fund investment (not $0.00)
- Other funds (CORE, DYNAMIC, UNLIMITED) should show $0.00
- Total balance should equal the sum of all fund balances
- Frontend should display individual fund names correctly
"""

import requests
import sys
from datetime import datetime
import json

class SalvadorFundBalanceVerifier:
    def __init__(self, base_url="https://fund-performance.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.client_user = None
        self.admin_user = None
        self.salvador_investments = []
        
        # Salvador's expected data
        self.salvador_client_id = "client_001"
        self.salvador_username = "client1"
        self.salvador_name = "Gerardo Briones"
        self.expected_balance_fund_amount = 1421421.08  # Expected BALANCE fund investment

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

    def login_as_salvador(self):
        """Login as Salvador (client1)"""
        success, response = self.run_test(
            "Salvador Login (client1)",
            "POST",
            "api/auth/login",
            200,
            data={
                "username": self.salvador_username, 
                "password": "password123",
                "user_type": "client"
            }
        )
        if success:
            self.client_user = response
            print(f"   ✅ Salvador logged in: {response.get('name', 'Unknown')}")
            print(f"   Client ID: {response.get('id', 'Unknown')}")
        return success

    def login_as_admin(self):
        """Login as admin for admin-only endpoints"""
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
        Test GET /api/investments/client/client_001 to see Salvador's investments
        """
        print(f"\n{'='*60}")
        print("TASK 1: CHECKING SALVADOR'S INVESTMENT DATA")
        print(f"{'='*60}")
        
        success, response = self.run_test(
            "Get Salvador's Investments",
            "GET",
            f"api/investments/client/{self.salvador_client_id}",
            200
        )
        
        if success:
            self.salvador_investments = response.get('investments', [])
            portfolio_stats = response.get('portfolio_stats', {})
            
            print(f"\n📊 SALVADOR'S INVESTMENT PORTFOLIO:")
            print(f"   Total Investments: {len(self.salvador_investments)}")
            print(f"   Total Principal: ${portfolio_stats.get('total_principal', 0):,.2f}")
            print(f"   Total Current Value: ${portfolio_stats.get('total_current_value', 0):,.2f}")
            print(f"   Total Interest Earned: ${portfolio_stats.get('total_interest_earned', 0):,.2f}")
            
            # Analyze investments by fund
            fund_breakdown = {}
            for investment in self.salvador_investments:
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
                if abs(balance_amount - self.expected_balance_fund_amount) < 1000:  # Allow small variance
                    print(f"   ✅ Amount matches expected: ${self.expected_balance_fund_amount:,.2f}")
                else:
                    print(f"   ⚠️  Amount differs from expected: ${self.expected_balance_fund_amount:,.2f}")
            else:
                print(f"\n❌ BALANCE FUND NOT FOUND - This is the bug!")
                print(f"   Expected BALANCE fund investment: ${self.expected_balance_fund_amount:,.2f}")
            
            return success
        
        return False

    def test_salvador_client_data_endpoint(self):
        """
        TASK 2: Test Client Data Endpoint
        Test GET /api/client/client_001/data to see the balance calculation
        """
        print(f"\n{'='*60}")
        print("TASK 2: TESTING CLIENT DATA ENDPOINT")
        print(f"{'='*60}")
        
        success, response = self.run_test(
            "Get Salvador's Client Data",
            "GET",
            f"api/client/{self.salvador_client_id}/data",
            200
        )
        
        if success:
            balance = response.get('balance', {})
            transactions = response.get('transactions', [])
            monthly_statement = response.get('monthly_statement', {})
            
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
                if abs(balance_balance - self.expected_balance_fund_amount) < 1000:
                    print(f"   ✅ BALANCE amount matches expected: ${self.expected_balance_fund_amount:,.2f}")
                else:
                    print(f"   ⚠️  BALANCE amount differs from expected: ${self.expected_balance_fund_amount:,.2f}")
            else:
                print(f"   ❌ BALANCE fund shows $0.00 - BUG CONFIRMED!")
                print(f"   Expected: ${self.expected_balance_fund_amount:,.2f}")
            
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
            
            # Check monthly statement
            print(f"\n📊 MONTHLY STATEMENT:")
            print(f"   Month: {monthly_statement.get('month', 'N/A')}")
            print(f"   Initial Balance: ${monthly_statement.get('initial_balance', 0):,.2f}")
            print(f"   Profit: ${monthly_statement.get('profit', 0):,.2f}")
            print(f"   Profit %: {monthly_statement.get('profit_percentage', 0):.2f}%")
            print(f"   Final Balance: ${monthly_statement.get('final_balance', 0):,.2f}")
            
            return success
        
        return False

    def test_balance_calculation_logic(self):
        """
        TASK 3: Verify Balance Calculation Logic
        Test the calculate_balances function with Salvador's data
        """
        print(f"\n{'='*60}")
        print("TASK 3: VERIFYING BALANCE CALCULATION LOGIC")
        print(f"{'='*60}")
        
        # First, let's check if Salvador has investments in the database
        if not self.salvador_investments:
            print("❌ No investment data available from previous test")
            return False
        
        print(f"\n🔍 ANALYZING BALANCE CALCULATION LOGIC:")
        print(f"   Salvador has {len(self.salvador_investments)} investments")
        
        # Manual calculation based on investment data
        manual_balances = {
            'core_balance': 0,
            'balance_balance': 0,
            'dynamic_balance': 0,
            'unlimited_balance': 0
        }
        
        for investment in self.salvador_investments:
            fund_code = investment.get('fund_code', '')
            current_value = investment.get('current_value', 0)
            
            if fund_code == 'CORE':
                manual_balances['core_balance'] += current_value
            elif fund_code == 'BALANCE':
                manual_balances['balance_balance'] += current_value
            elif fund_code == 'DYNAMIC':
                manual_balances['dynamic_balance'] += current_value
            elif fund_code == 'UNLIMITED':
                manual_balances['unlimited_balance'] += current_value
        
        manual_total = sum(manual_balances.values())
        
        print(f"\n📊 MANUAL CALCULATION FROM INVESTMENT DATA:")
        print(f"   Core Balance: ${manual_balances['core_balance']:,.2f}")
        print(f"   Balance Fund Balance: ${manual_balances['balance_balance']:,.2f}")
        print(f"   Dynamic Balance: ${manual_balances['dynamic_balance']:,.2f}")
        print(f"   Unlimited Balance: ${manual_balances['unlimited_balance']:,.2f}")
        print(f"   Manual Total: ${manual_total:,.2f}")
        
        # Now get the API calculation
        success, response = self.run_test(
            "Get Salvador's Client Data (for comparison)",
            "GET",
            f"api/client/{self.salvador_client_id}/data",
            200
        )
        
        if success:
            api_balance = response.get('balance', {})
            
            print(f"\n📊 API CALCULATION:")
            print(f"   Core Balance: ${api_balance.get('core_balance', 0):,.2f}")
            print(f"   Balance Fund Balance: ${api_balance.get('balance_balance', 0):,.2f}")
            print(f"   Dynamic Balance: ${api_balance.get('dynamic_balance', 0):,.2f}")
            print(f"   Unlimited Balance: ${api_balance.get('unlimited_balance', 0):,.2f}")
            print(f"   API Total: ${api_balance.get('total_balance', 0):,.2f}")
            
            # Compare manual vs API calculations
            print(f"\n🔍 CALCULATION COMPARISON:")
            
            discrepancies = []
            for fund in ['core_balance', 'balance_balance', 'dynamic_balance', 'unlimited_balance']:
                manual_val = manual_balances[fund.replace('_balance', '_balance')]
                api_val = api_balance.get(fund, 0)
                
                if abs(manual_val - api_val) > 0.01:
                    discrepancies.append(f"{fund}: Manual=${manual_val:,.2f}, API=${api_val:,.2f}")
                    print(f"   ❌ {fund}: Manual=${manual_val:,.2f} vs API=${api_val:,.2f}")
                else:
                    print(f"   ✅ {fund}: Match (${api_val:,.2f})")
            
            if not discrepancies:
                print(f"\n✅ ALL BALANCE CALCULATIONS MATCH!")
            else:
                print(f"\n❌ BALANCE CALCULATION DISCREPANCIES FOUND:")
                for discrepancy in discrepancies:
                    print(f"   - {discrepancy}")
            
            # Check if BALANCE fund is properly mapped
            if manual_balances['balance_balance'] > 0:
                print(f"\n✅ BALANCE fund investments correctly mapped to balance_balance field")
            else:
                print(f"\n❌ BALANCE fund investments NOT found in calculation")
                
            return len(discrepancies) == 0
        
        return False

    def test_frontend_integration_verification(self):
        """
        TASK 4: Frontend Integration Test
        Verify the frontend can correctly display the 4 individual fund balances
        """
        print(f"\n{'='*60}")
        print("TASK 4: FRONTEND INTEGRATION VERIFICATION")
        print(f"{'='*60}")
        
        # Get Salvador's data in the format the frontend expects
        success, response = self.run_test(
            "Get Salvador's Data (Frontend Format)",
            "GET",
            f"api/client/{self.salvador_client_id}/data",
            200
        )
        
        if success:
            balance = response.get('balance', {})
            
            print(f"\n🖥️  FRONTEND DISPLAY VERIFICATION:")
            
            # Check individual fund balances for frontend display
            funds = {
                'CORE': balance.get('core_balance', 0),
                'BALANCE': balance.get('balance_balance', 0),
                'DYNAMIC': balance.get('dynamic_balance', 0),
                'UNLIMITED': balance.get('unlimited_balance', 0)
            }
            
            print(f"\n📊 INDIVIDUAL FUND BALANCES FOR FRONTEND:")
            for fund_name, amount in funds.items():
                if amount > 0:
                    print(f"   {fund_name} Fund: ${amount:,.2f} - Should show 'ACTIVE'")
                else:
                    print(f"   {fund_name} Fund: ${amount:,.2f} - Should show 'NO INVESTMENT'")
            
            # Verify BALANCE fund specifically
            balance_amount = funds['BALANCE']
            if balance_amount > 0:
                print(f"\n✅ BALANCE fund has investment: ${balance_amount:,.2f}")
                print(f"   Frontend should display: 'ACTIVE' with amount")
                
                if abs(balance_amount - self.expected_balance_fund_amount) < 1000:
                    print(f"   ✅ Amount matches expected: ${self.expected_balance_fund_amount:,.2f}")
                else:
                    print(f"   ⚠️  Amount differs from expected: ${self.expected_balance_fund_amount:,.2f}")
            else:
                print(f"\n❌ BALANCE fund shows $0.00 - FRONTEND WILL SHOW 'NO INVESTMENT'")
                print(f"   This is the bug! Should show: ${self.expected_balance_fund_amount:,.2f}")
            
            # Check other funds should show "NO INVESTMENT"
            zero_funds = [name for name, amount in funds.items() if amount == 0]
            if zero_funds:
                print(f"\n✅ Funds showing 'NO INVESTMENT': {', '.join(zero_funds)}")
            
            # Check total balance
            total_balance = balance.get('total_balance', 0)
            calculated_total = sum(funds.values())
            
            print(f"\n💰 TOTAL BALANCE VERIFICATION:")
            print(f"   Reported Total: ${total_balance:,.2f}")
            print(f"   Sum of Individual Funds: ${calculated_total:,.2f}")
            
            if abs(total_balance - calculated_total) < 0.01:
                print(f"   ✅ Total balance calculation correct")
            else:
                print(f"   ❌ Total balance calculation error")
            
            return balance_amount > 0  # Success if BALANCE fund has investment
        
        return False

    def run_comprehensive_verification(self):
        """Run all verification tests"""
        print("🚀 STARTING SALVADOR FUND BALANCE BUG VERIFICATION")
        print("=" * 80)
        
        # Login as Salvador
        if not self.login_as_salvador():
            print("❌ Failed to login as Salvador - cannot continue")
            return False
        
        # Login as admin (for admin endpoints if needed)
        if not self.login_as_admin():
            print("⚠️  Failed to login as admin - some tests may be limited")
        
        # Run all verification tasks
        task_results = []
        
        # Task 1: Check Salvador's Investment Data
        task1_success = self.test_salvador_investments_endpoint()
        task_results.append(("Task 1: Salvador's Investment Data", task1_success))
        
        # Task 2: Test Client Data Endpoint
        task2_success = self.test_salvador_client_data_endpoint()
        task_results.append(("Task 2: Client Data Endpoint", task2_success))
        
        # Task 3: Verify Balance Calculation Logic
        task3_success = self.test_balance_calculation_logic()
        task_results.append(("Task 3: Balance Calculation Logic", task3_success))
        
        # Task 4: Frontend Integration Test
        task4_success = self.test_frontend_integration_verification()
        task_results.append(("Task 4: Frontend Integration", task4_success))
        
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
        
        # Determine if bug is confirmed
        if task2_success and task4_success:
            print(f"\n✅ SALVADOR'S BALANCE FUND IS WORKING CORRECTLY!")
        else:
            print(f"\n❌ SALVADOR'S BALANCE FUND BUG CONFIRMED!")
            print(f"   Expected: BALANCE fund showing ${self.expected_balance_fund_amount:,.2f}")
            print(f"   Issue: Fund balance not displaying correctly")
        
        return passed_tasks == total_tasks

if __name__ == "__main__":
    print("Salvador Fund Balance Bug Verification Test")
    print("=" * 50)
    
    verifier = SalvadorFundBalanceVerifier()
    success = verifier.run_comprehensive_verification()
    
    if success:
        print("\n🎉 All verification tests passed!")
        sys.exit(0)
    else:
        print("\n⚠️  Some verification tests failed - review results above")
        sys.exit(1)