#!/usr/bin/env python3
"""
Salvador Palma Investment Creation Test
=====================================

This test specifically addresses the review request:
1. Check Current Clients - GET /api/clients/all to find Salvador Palma
2. Create Investment for Salvador Palma - BALANCE fund, $100,000 to link with DooTechnology MT5
3. Verify Data Flow - Investment → MT5 Account Link → Client Dashboard → Fund Portfolio

Expected Data Flow: Investment Creation → MT5 Account Link → Client Dashboard → Fund Portfolio
"""

import requests
import sys
import json
from datetime import datetime

class SalvadorPalmaInvestmentTester:
    def __init__(self, base_url="https://mockdb-cleanup.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.salvador_client = None
        self.created_investment = None
        self.mt5_account = None
        self.admin_token = None
        self.client_token = None
        
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

    def authenticate_admin(self):
        """Authenticate as admin to get JWT token"""
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
            print(f"   ✅ Admin authenticated successfully")
            return True
        else:
            print(f"   ❌ Admin authentication failed")
            return False

    def authenticate_client(self, username="client3"):
        """Authenticate as client to get JWT token (client3 is Salvador Palma)"""
        success, response = self.run_test(
            "Client Login",
            "POST", 
            "api/auth/login",
            200,
            data={
                "username": username,
                "password": "password123",
                "user_type": "client"
            }
        )
        
        if success:
            self.client_token = response.get('token')
            print(f"   ✅ Client authenticated successfully")
            return True
        else:
            print(f"   ❌ Client authentication failed")
            return False

    def get_auth_headers(self, use_admin=True):
        """Get authorization headers with JWT token"""
        token = self.admin_token if use_admin else self.client_token
        if token:
            return {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}'
            }
        return {'Content-Type': 'application/json'}

    def step_1_check_available_clients(self):
        """Step 1: Check Available Clients - Look for Salvador Palma"""
        print("\n" + "="*80)
        print("STEP 1: CHECK AVAILABLE CLIENTS")
        print("="*80)
        
        success, response = self.run_test(
            "Get All Clients",
            "GET", 
            "api/clients/all",
            200,
            headers=self.get_auth_headers(use_admin=True)
        )
        
        if not success:
            print("❌ CRITICAL: Cannot retrieve client list")
            return False
            
        clients = response.get('clients', [])
        print(f"\n📊 FOUND {len(clients)} CLIENTS IN SYSTEM:")
        
        salvador_found = False
        for client in clients:
            client_name = client.get('name', 'Unknown')
            client_id = client.get('id', 'Unknown')
            client_email = client.get('email', 'Unknown')
            
            print(f"   • {client_name} (ID: {client_id}, Email: {client_email})")
            
            # Look for Salvador Palma (case insensitive)
            if 'salvador' in client_name.lower() and 'palma' in client_name.lower():
                self.salvador_client = client
                salvador_found = True
                print(f"   🎯 FOUND SALVADOR PALMA: {client}")
        
        if salvador_found:
            print(f"\n✅ SUCCESS: Salvador Palma found in system")
            print(f"   Client ID: {self.salvador_client['id']}")
            print(f"   Full Name: {self.salvador_client['name']}")
            print(f"   Email: {self.salvador_client['email']}")
            return True
        else:
            print(f"\n❌ ISSUE: Salvador Palma NOT found in client list")
            print(f"   Available clients: {[c.get('name') for c in clients]}")
            return False

    def step_2_create_salvador_investment(self):
        """Step 2: Create Investment for Salvador Palma - BALANCE fund $100,000"""
        print("\n" + "="*80)
        print("STEP 2: CREATE SALVADOR PALMA INVESTMENT")
        print("="*80)
        
        if not self.salvador_client:
            print("❌ CRITICAL: No Salvador Palma client available")
            return False
            
        # First check if Salvador is investment ready
        client_id = self.salvador_client['id']
        success, readiness_response = self.run_test(
            "Check Salvador Investment Readiness",
            "GET",
            f"api/clients/{client_id}/readiness",
            200,
            headers=self.get_auth_headers(use_admin=True)
        )
        
        if success:
            investment_ready = readiness_response.get('investment_ready', False)
            print(f"   Salvador Investment Ready: {investment_ready}")
            
            if not investment_ready:
                print("   ⚠️  Salvador not investment ready - making him ready for test")
                # Make Salvador investment ready
                readiness_update = {
                    "aml_kyc_completed": True,
                    "agreement_signed": True,
                    "account_creation_date": datetime.now().isoformat(),
                    "notes": "Made ready for Salvador Palma BALANCE investment test",
                    "updated_by": "testing_agent"
                }
                
                success, _ = self.run_test(
                    "Make Salvador Investment Ready",
                    "PUT",
                    f"api/clients/{client_id}/readiness",
                    200,
                    data=readiness_update,
                    headers=self.get_auth_headers(use_admin=True)
                )
                
                if not success:
                    print("❌ CRITICAL: Cannot make Salvador investment ready")
                    return False
        
        # Create BALANCE fund investment for $100,000
        investment_data = {
            "client_id": client_id,
            "fund_code": "BALANCE",
            "amount": 100000.00,
            "deposit_date": "2024-12-19"  # Today's date
        }
        
        print(f"\n💰 CREATING BALANCE FUND INVESTMENT:")
        print(f"   Client: {self.salvador_client['name']}")
        print(f"   Fund: BALANCE")
        print(f"   Amount: $100,000.00")
        print(f"   Target: Link to DooTechnology MT5 account")
        
        success, response = self.run_test(
            "Create Salvador BALANCE Investment",
            "POST",
            "api/investments/create",
            200,
            data=investment_data,
            headers=self.get_auth_headers(use_admin=True)
        )
        
        if success:
            self.created_investment = response
            investment_id = response.get('investment_id')
            fund_code = response.get('fund_code')
            principal_amount = response.get('principal_amount')
            
            print(f"\n✅ INVESTMENT CREATED SUCCESSFULLY!")
            print(f"   Investment ID: {investment_id}")
            print(f"   Fund Code: {fund_code}")
            print(f"   Principal Amount: ${principal_amount:,.2f}" if principal_amount else f"   Principal Amount: {principal_amount}")
            print(f"   Deposit Date: {response.get('deposit_date')}")
            print(f"   Interest Start Date: {response.get('interest_start_date')}")
            
            return True
        else:
            print(f"\n❌ CRITICAL: Failed to create Salvador investment")
            return False

    def step_3_verify_mt5_account_link(self):
        """Step 3: Verify MT5 Account Link - Check DooTechnology connection"""
        print("\n" + "="*80)
        print("STEP 3: VERIFY MT5 ACCOUNT LINK")
        print("="*80)
        
        if not self.created_investment:
            print("❌ CRITICAL: No investment created to verify MT5 link")
            return False
            
        # Check MT5 accounts by broker to find DooTechnology accounts
        success, response = self.run_test(
            "Get MT5 Accounts by Broker",
            "GET",
            "api/mt5/admin/accounts/by-broker",
            200,
            headers=self.get_auth_headers(use_admin=True)
        )
        
        if success:
            brokers = response.get('brokers', {})
            print(f"\n🏦 MT5 BROKERS FOUND: {list(brokers.keys())}")
            
            # Look for DooTechnology broker
            doo_accounts = brokers.get('dootechnology', [])
            multibank_accounts = brokers.get('multibank', [])
            
            print(f"   DooTechnology Accounts: {len(doo_accounts)}")
            print(f"   Multibank Accounts: {len(multibank_accounts)}")
            
            # Check if Salvador's investment is linked to DooTechnology
            salvador_client_id = self.salvador_client['id']
            salvador_mt5_found = False
            
            for account in doo_accounts:
                if account.get('client_id') == salvador_client_id:
                    self.mt5_account = account
                    salvador_mt5_found = True
                    print(f"\n🎯 SALVADOR'S DOOTECHNOLOGY MT5 ACCOUNT FOUND:")
                    print(f"   Account ID: {account.get('account_id')}")
                    print(f"   MT5 Login: {account.get('mt5_login')}")
                    print(f"   Total Allocated: ${account.get('total_allocated', 0):,.2f}")
                    print(f"   Fund Code: {account.get('fund_code')}")
                    break
            
            if salvador_mt5_found:
                print(f"\n✅ SUCCESS: Salvador's investment linked to DooTechnology MT5")
                return True
            else:
                print(f"\n❌ ISSUE: Salvador's investment NOT linked to DooTechnology MT5")
                print(f"   Expected: BALANCE fund investment should create/link to DooTechnology account")
                return False
        else:
            print(f"\n❌ CRITICAL: Cannot retrieve MT5 accounts by broker")
            return False

    def step_4_verify_client_dashboard_access(self):
        """Step 4: Verify Client Dashboard Access - Check Salvador can see investment"""
        print("\n" + "="*80)
        print("STEP 4: VERIFY CLIENT DASHBOARD ACCESS")
        print("="*80)
        
        if not self.salvador_client:
            print("❌ CRITICAL: No Salvador client to test dashboard access")
            return False
            
        client_id = self.salvador_client['id']
        
        # Get Salvador's investment portfolio
        success, response = self.run_test(
            "Get Salvador Investment Portfolio",
            "GET",
            f"api/investments/client/{client_id}",
            200,
            headers=self.get_auth_headers(use_admin=True)
        )
        
        if success:
            investments = response.get('investments', [])
            portfolio_stats = response.get('portfolio_statistics', {})
            
            print(f"\n📊 SALVADOR'S INVESTMENT PORTFOLIO:")
            print(f"   Total Investments: {len(investments)}")
            print(f"   Total Principal: ${portfolio_stats.get('total_principal', 0):,.2f}")
            print(f"   Total Current Value: ${portfolio_stats.get('total_current_value', 0):,.2f}")
            
            # Look for the BALANCE fund investment we just created
            balance_investment_found = False
            for investment in investments:
                fund_code = investment.get('fund_code')
                principal = investment.get('principal_amount', 0)
                current_value = investment.get('current_value', 0)
                
                print(f"   • {fund_code} Fund: ${principal:,.2f} → ${current_value:,.2f}")
                
                if fund_code == 'BALANCE' and principal == 100000.00:
                    balance_investment_found = True
                    print(f"     🎯 FOUND TARGET BALANCE INVESTMENT: ${principal:,.2f}")
            
            if balance_investment_found:
                print(f"\n✅ SUCCESS: Salvador can see BALANCE investment in dashboard")
                return True
            else:
                print(f"\n❌ ISSUE: Salvador's BALANCE investment not visible in dashboard")
                return False
        else:
            print(f"\n❌ CRITICAL: Cannot retrieve Salvador's investment portfolio")
            return False

    def step_5_verify_fund_portfolio_integration(self):
        """Step 5: Verify Fund Portfolio Integration - Check admin view shows Salvador"""
        print("\n" + "="*80)
        print("STEP 5: VERIFY FUND PORTFOLIO INTEGRATION")
        print("="*80)
        
        # Check admin investment overview
        success, response = self.run_test(
            "Get Admin Investment Overview",
            "GET",
            "api/investments/admin/overview",
            200,
            headers=self.get_auth_headers(use_admin=True)
        )
        
        if success:
            total_aum = response.get('total_aum', 0)
            fund_summaries = response.get('fund_summaries', {})
            clients = response.get('clients', [])
            
            print(f"\n📈 ADMIN INVESTMENT OVERVIEW:")
            print(f"   Total AUM: ${total_aum:,.2f}")
            print(f"   Fund Summaries: {list(fund_summaries.keys()) if isinstance(fund_summaries, dict) else 'Not dict format'}")
            print(f"   Client Count: {len(clients)}")
            
            # Check BALANCE fund specifically
            balance_fund = fund_summaries.get('BALANCE', {}) if isinstance(fund_summaries, dict) else {}
            if balance_fund:
                balance_aum = balance_fund.get('total_aum', 0)
                balance_investors = balance_fund.get('total_investors', 0)
                
                print(f"\n💰 BALANCE FUND DETAILS:")
                print(f"   AUM: ${balance_aum:,.2f}")
                print(f"   Investors: {balance_investors}")
                
                # Check if Salvador's $100K is included
                if balance_aum >= 100000:
                    print(f"   ✅ Salvador's $100K investment appears to be included")
                else:
                    print(f"   ❌ Salvador's $100K investment may not be included")
            
            # Look for Salvador in client list
            salvador_in_admin = False
            salvador_client_id = self.salvador_client['id']
            
            for client in clients:
                if client.get('client_id') == salvador_client_id:
                    salvador_in_admin = True
                    total_investment = client.get('total_investment', 0)
                    print(f"\n🎯 SALVADOR IN ADMIN VIEW:")
                    print(f"   Client ID: {client.get('client_id')}")
                    print(f"   Total Investment: ${total_investment:,.2f}")
                    break
            
            if salvador_in_admin:
                print(f"\n✅ SUCCESS: Salvador appears in admin fund portfolio view")
                return True
            else:
                print(f"\n❌ ISSUE: Salvador not visible in admin fund portfolio")
                return False
        else:
            print(f"\n❌ CRITICAL: Cannot retrieve admin investment overview")
            return False

    def run_complete_test_suite(self):
        """Run the complete Salvador Palma investment test suite"""
        print("🚀 STARTING SALVADOR PALMA INVESTMENT CREATION TEST")
        print("="*80)
        print("GOAL: Create Salvador Palma BALANCE fund investment that connects to DooTechnology MT5")
        print("="*80)
        
        # Authentication first
        print("\n🔐 AUTHENTICATING...")
        if not self.authenticate_admin():
            print("❌ CRITICAL: Cannot authenticate as admin")
            return False
        
        # Step 1: Check Available Clients
        step1_success = self.step_1_check_available_clients()
        
        # Step 2: Create Investment (only if Salvador found)
        step2_success = False
        if step1_success:
            step2_success = self.step_2_create_salvador_investment()
        
        # Step 3: Verify MT5 Account Link (only if investment created)
        step3_success = False
        if step2_success:
            step3_success = self.step_3_verify_mt5_account_link()
        
        # Step 4: Verify Client Dashboard Access
        step4_success = False
        if step2_success:
            step4_success = self.step_4_verify_client_dashboard_access()
        
        # Step 5: Verify Fund Portfolio Integration
        step5_success = False
        if step2_success:
            step5_success = self.step_5_verify_fund_portfolio_integration()
        
        # Final Results
        print("\n" + "="*80)
        print("SALVADOR PALMA INVESTMENT TEST RESULTS")
        print("="*80)
        
        print(f"Step 1 - Check Clients: {'✅ PASS' if step1_success else '❌ FAIL'}")
        print(f"Step 2 - Create Investment: {'✅ PASS' if step2_success else '❌ FAIL'}")
        print(f"Step 3 - MT5 Account Link: {'✅ PASS' if step3_success else '❌ FAIL'}")
        print(f"Step 4 - Client Dashboard: {'✅ PASS' if step4_success else '❌ FAIL'}")
        print(f"Step 5 - Fund Portfolio: {'✅ PASS' if step5_success else '❌ FAIL'}")
        
        total_steps = 5
        passed_steps = sum([step1_success, step2_success, step3_success, step4_success, step5_success])
        
        print(f"\nOVERALL RESULT: {passed_steps}/{total_steps} steps passed")
        print(f"Success Rate: {(passed_steps/total_steps)*100:.1f}%")
        
        if passed_steps == total_steps:
            print("\n🎉 COMPLETE SUCCESS: Salvador Palma BALANCE investment flow working perfectly!")
            print("   ✅ Investment Creation → MT5 Account Link → Client Dashboard → Fund Portfolio")
        elif passed_steps >= 3:
            print("\n⚠️  PARTIAL SUCCESS: Core functionality working, minor issues detected")
        else:
            print("\n❌ CRITICAL ISSUES: Major problems with Salvador Palma investment flow")
        
        print(f"\nTotal API Tests: {self.tests_run}")
        print(f"Passed Tests: {self.tests_passed}")
        print(f"Test Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        return passed_steps == total_steps

if __name__ == "__main__":
    print("Salvador Palma Investment Creation Test")
    print("=====================================")
    
    tester = SalvadorPalmaInvestmentTester()
    success = tester.run_complete_test_suite()
    
    sys.exit(0 if success else 1)