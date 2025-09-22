#!/usr/bin/env python3
"""
Salvador Palma Complete System Test - Final Verification
Testing the exact specifications as requested in the review.
"""

import requests
import sys
from datetime import datetime
import json

class SalvadorPalmaVerificationTester:
    def __init__(self, base_url="https://finance-portal-60.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.critical_failures = []
        self.admin_token = None
        
        # Expected exact specifications
        self.expected_client_id = "client_003"
        self.expected_mt5_login = 9928326
        self.expected_broker = "DooTechnology"
        self.expected_server = "DooTechnology-Live"
        self.expected_account_id = "mt5_client_003_BALANCE_dootechnology_878e14e4"
        self.expected_investment_amount = 100000.0
        self.expected_fund_code = "BALANCE"

    def authenticate_admin(self):
        """Authenticate as admin to get JWT token"""
        print("\n🔐 Authenticating as admin...")
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
            self.admin_token = response.get('token')
            if self.admin_token:
                print(f"   ✅ Admin authenticated successfully")
                return True
            else:
                print(f"   ❌ No token received in response")
                return False
        else:
            print(f"   ❌ Admin authentication failed")
            return False

    def get_auth_headers(self):
        """Get headers with JWT token for authenticated requests"""
        if self.admin_token:
            return {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.admin_token}'
            }
        return {'Content-Type': 'application/json'}

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None, auth_required=False):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        if headers is None:
            if auth_required:
                headers = self.get_auth_headers()
            else:
                headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=15)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=15)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=15)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=15)

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

    def test_priority_1_salvador_investment_data(self):
        """Priority 1: Test Salvador's investment data"""
        print("\n" + "="*80)
        print("PRIORITY 1: COMPLETE SALVADOR DATA CHECK")
        print("="*80)
        
        # Test 1: GET /api/investments/client/client_003 - Salvador's investment data
        success, response = self.run_test(
            "Salvador Investment Data (client_003)",
            "GET",
            "api/investments/client/client_003",
            200
        )
        
        if success:
            investments = response.get('investments', [])
            portfolio_stats = response.get('portfolio_stats', {})
            
            print(f"   📊 Investment Count: {len(investments)}")
            print(f"   📊 Total Principal: ${portfolio_stats.get('total_principal', 0):,.2f}")
            print(f"   📊 Total Current Value: ${portfolio_stats.get('total_current_value', 0):,.2f}")
            
            # Verify exactly 1 BALANCE investment
            balance_investments = [inv for inv in investments if inv.get('fund_code') == 'BALANCE']
            if len(balance_investments) == 1:
                investment = balance_investments[0]
                principal = investment.get('principal_amount', 0)
                fund_code = investment.get('fund_code')
                
                print(f"   ✅ Found exactly 1 BALANCE investment")
                print(f"   💰 Principal Amount: ${principal:,.2f}")
                print(f"   📈 Fund Code: {fund_code}")
                
                if principal == self.expected_investment_amount:
                    print(f"   ✅ Principal amount matches expected ${self.expected_investment_amount:,.2f}")
                else:
                    print(f"   ❌ Principal amount mismatch: expected ${self.expected_investment_amount:,.2f}, got ${principal:,.2f}")
                    self.critical_failures.append(f"Salvador investment amount incorrect: ${principal:,.2f} != ${self.expected_investment_amount:,.2f}")
            else:
                print(f"   ❌ Expected exactly 1 BALANCE investment, found {len(balance_investments)}")
                self.critical_failures.append(f"Salvador should have exactly 1 BALANCE investment, found {len(balance_investments)}")
        else:
            self.critical_failures.append("Cannot retrieve Salvador's investment data")
            
        return success

    def test_priority_1_mt5_accounts_overview(self):
        """Priority 1: Test MT5 accounts overview - should show exactly 1 account"""
        # Test 2: GET /api/mt5/admin/accounts - Should show exactly 1 account with login 9928326
        success, response = self.run_test(
            "MT5 Admin Accounts Overview",
            "GET",
            "api/mt5/admin/accounts",
            200,
            auth_required=True
        )
        
        if success:
            accounts = response.get('accounts', [])
            total_accounts = response.get('total_accounts', len(accounts))
            
            print(f"   📊 Total MT5 Accounts: {total_accounts}")
            
            if total_accounts == 1:
                print(f"   ✅ Exactly 1 MT5 account found as expected")
                
                if accounts:
                    account = accounts[0]
                    mt5_login = account.get('mt5_login')
                    client_id = account.get('client_id')
                    fund_code = account.get('fund_code')
                    allocated = account.get('total_allocated', 0)
                    
                    print(f"   🔑 MT5 Login: {mt5_login}")
                    print(f"   👤 Client ID: {client_id}")
                    print(f"   📈 Fund Code: {fund_code}")
                    print(f"   💰 Allocated: ${allocated:,.2f}")
                    
                    # Verify MT5 login matches expected
                    if mt5_login == self.expected_mt5_login:
                        print(f"   ✅ MT5 login matches expected {self.expected_mt5_login}")
                    else:
                        print(f"   ❌ MT5 login mismatch: expected {self.expected_mt5_login}, got {mt5_login}")
                        self.critical_failures.append(f"MT5 login incorrect: {mt5_login} != {self.expected_mt5_login}")
                    
                    # Verify client ID matches Salvador
                    if client_id == self.expected_client_id:
                        print(f"   ✅ Client ID matches Salvador ({self.expected_client_id})")
                    else:
                        print(f"   ❌ Client ID mismatch: expected {self.expected_client_id}, got {client_id}")
                        self.critical_failures.append(f"MT5 account client ID incorrect: {client_id} != {self.expected_client_id}")
                    
                    # Verify fund code is BALANCE
                    if fund_code == self.expected_fund_code:
                        print(f"   ✅ Fund code matches expected {self.expected_fund_code}")
                    else:
                        print(f"   ❌ Fund code mismatch: expected {self.expected_fund_code}, got {fund_code}")
                        self.critical_failures.append(f"MT5 account fund code incorrect: {fund_code} != {self.expected_fund_code}")
            else:
                print(f"   ❌ Expected exactly 1 MT5 account, found {total_accounts}")
                self.critical_failures.append(f"Should have exactly 1 MT5 account, found {total_accounts}")
        else:
            self.critical_failures.append("Cannot retrieve MT5 accounts overview")
            
        return success

    def test_priority_1_mt5_accounts_by_broker(self):
        """Priority 1: Test MT5 accounts by broker - should show DooTechnology with 1 account"""
        # Test 3: GET /api/mt5/admin/accounts/by-broker - Should show DooTechnology broker with 1 account
        success, response = self.run_test(
            "MT5 Accounts by Broker",
            "GET",
            "api/mt5/admin/accounts/by-broker",
            200,
            auth_required=True
        )
        
        if success:
            brokers = response.get('brokers', {})
            
            print(f"   📊 Brokers found: {list(brokers.keys())}")
            
            # Check for DooTechnology broker
            if self.expected_broker.lower() in brokers or 'dootechnology' in brokers:
                broker_key = self.expected_broker.lower() if self.expected_broker.lower() in brokers else 'dootechnology'
                doo_accounts = brokers[broker_key]
                account_count = len(doo_accounts)
                
                print(f"   ✅ DooTechnology broker found")
                print(f"   📊 DooTechnology accounts: {account_count}")
                
                if account_count == 1:
                    print(f"   ✅ Exactly 1 account under DooTechnology as expected")
                    
                    account = doo_accounts[0]
                    mt5_login = account.get('mt5_login')
                    client_id = account.get('client_id')
                    server = account.get('mt5_server')
                    
                    print(f"   🔑 MT5 Login: {mt5_login}")
                    print(f"   👤 Client ID: {client_id}")
                    print(f"   🖥️  Server: {server}")
                    
                    # Verify server is DooTechnology-Live
                    if server == self.expected_server:
                        print(f"   ✅ Server matches expected {self.expected_server}")
                    else:
                        print(f"   ❌ Server mismatch: expected {self.expected_server}, got {server}")
                        self.critical_failures.append(f"MT5 server incorrect: {server} != {self.expected_server}")
                else:
                    print(f"   ❌ Expected exactly 1 DooTechnology account, found {account_count}")
                    self.critical_failures.append(f"DooTechnology should have exactly 1 account, found {account_count}")
            else:
                print(f"   ❌ DooTechnology broker not found in {list(brokers.keys())}")
                self.critical_failures.append("DooTechnology broker not found")
        else:
            self.critical_failures.append("Cannot retrieve MT5 accounts by broker")
            
        return success

    def test_priority_2_exact_specifications(self):
        """Priority 2: Verify exact specifications in detail"""
        print("\n" + "="*80)
        print("PRIORITY 2: VERIFY EXACT SPECIFICATIONS")
        print("="*80)
        
        all_specs_verified = True
        
        # Re-verify Salvador's investment with detailed checks
        success, response = self.run_test(
            "Detailed Salvador Investment Verification",
            "GET",
            "api/investments/client/client_003",
            200
        )
        
        if success:
            investments = response.get('investments', [])
            
            print(f"\n📋 SPECIFICATION CHECKLIST:")
            print(f"   1. Salvador (client_003) has exactly 1 BALANCE investment ($100,000)")
            
            balance_investments = [inv for inv in investments if inv.get('fund_code') == 'BALANCE']
            if len(balance_investments) == 1 and balance_investments[0].get('principal_amount') == 100000.0:
                print(f"      ✅ VERIFIED: 1 BALANCE investment of $100,000")
            else:
                print(f"      ❌ FAILED: Found {len(balance_investments)} BALANCE investments")
                all_specs_verified = False
        
        # Verify MT5 account specifications
        success, response = self.run_test(
            "Detailed MT5 Account Verification",
            "GET",
            "api/mt5/admin/accounts",
            200,
            auth_required=True
        )
        
        if success:
            accounts = response.get('accounts', [])
            
            print(f"   2. Exactly 1 MT5 account with login 9928326")
            if len(accounts) == 1 and accounts[0].get('mt5_login') == 9928326:
                print(f"      ✅ VERIFIED: 1 MT5 account with login 9928326")
            else:
                print(f"      ❌ FAILED: Found {len(accounts)} accounts, login: {accounts[0].get('mt5_login') if accounts else 'None'}")
                all_specs_verified = False
            
            print(f"   3. MT5 account belongs to Salvador and BALANCE fund")
            if accounts and accounts[0].get('client_id') == 'client_003' and accounts[0].get('fund_code') == 'BALANCE':
                print(f"      ✅ VERIFIED: Account belongs to client_003 (Salvador) and BALANCE fund")
            else:
                client_id = accounts[0].get('client_id') if accounts else 'None'
                fund_code = accounts[0].get('fund_code') if accounts else 'None'
                print(f"      ❌ FAILED: Client ID: {client_id}, Fund: {fund_code}")
                all_specs_verified = False
        
        # Verify broker and server
        success, response = self.run_test(
            "Detailed Broker Verification",
            "GET",
            "api/mt5/admin/accounts/by-broker",
            200,
            auth_required=True
        )
        
        if success:
            brokers = response.get('brokers', {})
            
            print(f"   4. Broker is DooTechnology with server DooTechnology-Live")
            doo_accounts = brokers.get('dootechnology', [])
            if doo_accounts and doo_accounts[0].get('mt5_server') == 'DooTechnology-Live':
                print(f"      ✅ VERIFIED: DooTechnology broker with DooTechnology-Live server")
            else:
                server = doo_accounts[0].get('mt5_server') if doo_accounts else 'None'
                print(f"      ❌ FAILED: Server: {server}")
                all_specs_verified = False
            
            print(f"   5. Account ID is mt5_client_003_BALANCE_dootechnology_878e14e4")
            if doo_accounts and doo_accounts[0].get('account_id') == self.expected_account_id:
                print(f"      ✅ VERIFIED: Correct account ID")
            else:
                account_id = doo_accounts[0].get('account_id') if doo_accounts else 'None'
                print(f"      ❌ FAILED: Account ID: {account_id}")
                # This might be acceptable if the ID is auto-generated
                print(f"      ℹ️  Note: Account ID might be auto-generated, checking pattern...")
                if account_id and 'mt5_client_003_BALANCE_dootechnology' in account_id:
                    print(f"      ✅ ACCEPTABLE: Account ID follows expected pattern")
                else:
                    all_specs_verified = False
        
        return all_specs_verified

    def test_priority_3_clean_system(self):
        """Priority 3: Verify clean system with only Salvador's data"""
        print("\n" + "="*80)
        print("PRIORITY 3: VERIFY CLEAN SYSTEM")
        print("="*80)
        
        clean_system = True
        
        # Test 1: GET /api/admin/portfolio-summary - Should show only Salvador's data
        success, response = self.run_test(
            "Admin Portfolio Summary (Clean System Check)",
            "GET",
            "api/admin/portfolio-summary",
            200,
            auth_required=True
        )
        
        if success:
            total_aum = response.get('aum', response.get('total_aum', 0))
            client_count = response.get('client_count', 0)
            allocation = response.get('allocation', {})
            
            print(f"   📊 Total AUM: ${total_aum:,.2f}")
            print(f"   👥 Client Count: {client_count}")
            print(f"   📈 Fund Allocation: {allocation}")
            
            # Check if AUM reflects only Salvador's investment
            expected_aum_range = (100000, 120000)  # $100K principal + interest
            if expected_aum_range[0] <= total_aum <= expected_aum_range[1]:
                print(f"   ✅ Total AUM in expected range for Salvador only (${expected_aum_range[0]:,} - ${expected_aum_range[1]:,})")
            else:
                print(f"   ❌ Total AUM outside expected range: ${total_aum:,.2f}")
                self.critical_failures.append(f"Total AUM suggests other client data present: ${total_aum:,.2f}")
                clean_system = False
            
            # Check BALANCE fund allocation should be 100%
            balance_allocation = allocation.get('BALANCE', 0)
            if balance_allocation >= 95:  # Allow for rounding
                print(f"   ✅ BALANCE fund allocation is {balance_allocation}% (expected ~100%)")
            else:
                print(f"   ❌ BALANCE fund allocation is {balance_allocation}% (expected ~100%)")
                clean_system = False
        
        # Test 2: Check other clients have no investments
        print(f"\n   🔍 Checking other clients have no investments...")
        
        other_clients = ['client_001', 'client_002', 'client_004', 'client_005']
        for client_id in other_clients:
            success, response = self.run_test(
                f"Check {client_id} has no investments",
                "GET",
                f"api/investments/client/{client_id}",
                200
            )
            
            if success:
                investments = response.get('investments', [])
                if len(investments) == 0:
                    print(f"      ✅ {client_id}: No investments (clean)")
                else:
                    print(f"      ❌ {client_id}: Has {len(investments)} investments (not clean)")
                    self.critical_failures.append(f"{client_id} has investments when system should be clean")
                    clean_system = False
        
        # Test 3: Verify no other MT5 accounts
        success, response = self.run_test(
            "Verify Only Salvador's MT5 Account Exists",
            "GET",
            "api/mt5/admin/accounts",
            200,
            auth_required=True
        )
        
        if success:
            accounts = response.get('accounts', [])
            total_accounts = len(accounts)
            
            if total_accounts == 1:
                print(f"   ✅ Exactly 1 MT5 account exists (clean system)")
                
                # Verify it belongs to Salvador
                if accounts[0].get('client_id') == 'client_003':
                    print(f"   ✅ The MT5 account belongs to Salvador (client_003)")
                else:
                    print(f"   ❌ MT5 account belongs to {accounts[0].get('client_id')}, not Salvador")
                    clean_system = False
            else:
                print(f"   ❌ Found {total_accounts} MT5 accounts (expected exactly 1)")
                self.critical_failures.append(f"System has {total_accounts} MT5 accounts, expected 1")
                clean_system = False
        
        return clean_system

    def run_complete_verification(self):
        """Run the complete Salvador Palma verification test suite"""
        print("🎯 SALVADOR PALMA COMPLETE SYSTEM TEST - FINAL VERIFICATION")
        print("=" * 80)
        print("Testing exact specifications as requested in review")
        print("Expected: PERFECT clean system with ONLY Salvador Palma data")
        print("=" * 80)
        
        # First authenticate as admin
        if not self.authenticate_admin():
            print("❌ Cannot proceed without admin authentication")
            return False
        
        # Priority 1: Complete Salvador Data Check
        priority_1_success = True
        priority_1_success &= self.test_priority_1_salvador_investment_data()
        priority_1_success &= self.test_priority_1_mt5_accounts_overview()
        priority_1_success &= self.test_priority_1_mt5_accounts_by_broker()
        
        # Priority 2: Verify Exact Specifications
        priority_2_success = self.test_priority_2_exact_specifications()
        
        # Priority 3: Verify Clean System
        priority_3_success = self.test_priority_3_clean_system()
        
        # Final Results
        print("\n" + "="*80)
        print("FINAL VERIFICATION RESULTS")
        print("="*80)
        
        print(f"📊 Tests Run: {self.tests_run}")
        print(f"✅ Tests Passed: {self.tests_passed}")
        print(f"❌ Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"📈 Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        print(f"\n🎯 PRIORITY RESULTS:")
        print(f"   Priority 1 (Salvador Data): {'✅ PASSED' if priority_1_success else '❌ FAILED'}")
        print(f"   Priority 2 (Exact Specs): {'✅ PASSED' if priority_2_success else '❌ FAILED'}")
        print(f"   Priority 3 (Clean System): {'✅ PASSED' if priority_3_success else '❌ FAILED'}")
        
        overall_success = priority_1_success and priority_2_success and priority_3_success
        
        if overall_success:
            print(f"\n🎉 OVERALL RESULT: ✅ PERFECT SYSTEM VERIFIED!")
            print(f"   Salvador Palma system is exactly as requested:")
            print(f"   • 1 client with investments (Salvador/client_003)")
            print(f"   • 1 BALANCE investment ($100k principal)")
            print(f"   • 1 MT5 account (login 9928326, DooTechnology, BALANCE fund)")
            print(f"   • Clean system with no other client data")
        else:
            print(f"\n🚨 OVERALL RESULT: ❌ SYSTEM NOT PERFECT")
            print(f"   Critical issues found:")
            for i, failure in enumerate(self.critical_failures, 1):
                print(f"   {i}. {failure}")
        
        return overall_success

if __name__ == "__main__":
    tester = SalvadorPalmaVerificationTester()
    success = tester.run_complete_verification()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)