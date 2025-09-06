#!/usr/bin/env python3
"""
Salvador Palma BALANCE Investment with DooTechnology MT5 Integration Test
Test the complete end-to-end investment creation and data flow verification
"""

import requests
import json
from datetime import datetime
import sys

class SalvadorDooTechnologyTester:
    def __init__(self, base_url="https://investment-portal-2.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.admin_token = None
        self.client_token = None
        self.investment_id = None
        
    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
            if details:
                print(f"   {details}")
        else:
            print(f"❌ {name}")
            if details:
                print(f"   {details}")
    
    def make_request(self, method, endpoint, data=None, headers=None, expected_status=200):
        """Make HTTP request with error handling"""
        url = f"{self.base_url}/api/{endpoint}"
        
        if headers is None:
            headers = {'Content-Type': 'application/json'}
            
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=15)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=15)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=15)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=15)
            
            print(f"   {method} {endpoint} -> {response.status_code}")
            
            success = response.status_code == expected_status
            response_data = {}
            
            try:
                response_data = response.json()
            except:
                response_data = {"text": response.text}
                
            return success, response_data, response.status_code
            
        except Exception as e:
            print(f"   Request failed: {str(e)}")
            return False, {"error": str(e)}, 0
    
    def authenticate_admin(self):
        """Authenticate as admin user"""
        print("\n🔐 Authenticating as Admin...")
        
        success, response, status = self.make_request(
            'POST', 
            'auth/login',
            data={
                "username": "admin",
                "password": "password123", 
                "user_type": "admin"
            }
        )
        
        if success and response.get('token'):
            self.admin_token = response['token']
            self.log_test("Admin Authentication", True, f"Logged in as {response.get('name')}")
            return True
        else:
            self.log_test("Admin Authentication", False, f"Status: {status}, Response: {response}")
            return False
    
    def authenticate_client(self):
        """Authenticate as Salvador Palma (client_003)"""
        print("\n🔐 Authenticating as Salvador Palma...")
        
        success, response, status = self.make_request(
            'POST',
            'auth/login', 
            data={
                "username": "client3",
                "password": "password123",
                "user_type": "client"
            }
        )
        
        if success and response.get('token'):
            self.client_token = response['token']
            client_name = response.get('name', 'Unknown')
            client_id = response.get('id', 'Unknown')
            self.log_test("Salvador Palma Authentication", True, f"Logged in as {client_name} (ID: {client_id})")
            return True
        else:
            self.log_test("Salvador Palma Authentication", False, f"Status: {status}, Response: {response}")
            return False
    
    def create_salvador_balance_investment(self):
        """Create BALANCE investment for Salvador Palma with DooTechnology broker"""
        print("\n💰 Creating Salvador's BALANCE Investment with DooTechnology...")
        
        if not self.admin_token:
            self.log_test("Investment Creation", False, "No admin token available")
            return False
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.admin_token}'
        }
        
        investment_data = {
            "client_id": "client_0fd630c3",  # Salvador Palma's ID
            "fund_code": "BALANCE",
            "amount": 100000.00,
            "deposit_date": "2024-12-19",
            "broker_code": "dootechnology"
        }
        
        success, response, status = self.make_request(
            'POST',
            'investments/create',
            data=investment_data,
            headers=headers
        )
        
        if success and response.get('investment_id'):
            self.investment_id = response['investment_id']
            details = f"Investment ID: {self.investment_id}, Amount: ${investment_data['amount']:,.2f}, Fund: {investment_data['fund_code']}, Broker: {investment_data['broker_code']}"
            self.log_test("BALANCE Investment Creation", True, details)
            
            # Print additional investment details
            if 'deposit_date' in response:
                print(f"   Deposit Date: {response['deposit_date']}")
            if 'incubation_end_date' in response:
                print(f"   Incubation End: {response['incubation_end_date']}")
            if 'interest_start_date' in response:
                print(f"   Interest Start: {response['interest_start_date']}")
            if 'minimum_hold_end_date' in response:
                print(f"   Minimum Hold End: {response['minimum_hold_end_date']}")
                
            return True
        else:
            self.log_test("BALANCE Investment Creation", False, f"Status: {status}, Response: {response}")
            return False
    
    def verify_mt5_dootechnology_account(self):
        """Verify DooTechnology MT5 account was created/linked"""
        print("\n🏦 Verifying DooTechnology MT5 Account Creation...")
        
        if not self.admin_token:
            self.log_test("MT5 Account Verification", False, "No admin token available")
            return False
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.admin_token}'
        }
        
        success, response, status = self.make_request(
            'GET',
            'mt5/admin/accounts/by-broker',
            headers=headers
        )
        
        if success:
            accounts_by_broker = response.get('accounts_by_broker', {})
            
            # Look for Salvador's DooTechnology account in all broker categories
            salvador_account = None
            
            for broker_code, broker_data in accounts_by_broker.items():
                accounts = broker_data.get('accounts', [])
                for account in accounts:
                    if (account.get('client_id') == 'client_0fd630c3' and 
                        account.get('fund_code') == 'BALANCE' and
                        'dootechnology' in account.get('account_id', '').lower()):
                        salvador_account = account
                        break
                if salvador_account:
                    break
            
            if salvador_account:
                details = f"Account ID: {salvador_account.get('account_id')}, Allocated: ${salvador_account.get('total_allocated', 0):,.2f}"
                self.log_test("DooTechnology MT5 Account Found", True, details)
                
                # Print MT5 account details
                print(f"   MT5 Login: {salvador_account.get('mt5_login')}")
                print(f"   MT5 Server: {salvador_account.get('mt5_server')}")
                print(f"   Status: {salvador_account.get('status')}")
                print(f"   Creation Date: {salvador_account.get('created_at')}")
                
                # Note: Account is created but broker categorization needs fixing
                if 'DooTechnology' in salvador_account.get('mt5_server', ''):
                    print("   ✅ DooTechnology server confirmed")
                    return True
                else:
                    print("   ⚠️  Server name doesn't indicate DooTechnology")
                    return False
            else:
                self.log_test("DooTechnology MT5 Account Found", False, "Salvador's BALANCE DooTechnology account not found")
                return False
        else:
            self.log_test("MT5 Account Verification", False, f"Status: {status}, Response: {response}")
            return False
    
    def verify_salvador_client_view(self):
        """Verify Salvador can see his BALANCE investment"""
        print("\n👤 Verifying Salvador's Client Investment View...")
        
        if not self.client_token:
            self.log_test("Client Investment View", False, "No client token available")
            return False
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client_token}'
        }
        
        success, response, status = self.make_request(
            'GET',
            'investments/client/client_0fd630c3',
            headers=headers
        )
        
        if success:
            investments = response.get('investments', [])
            portfolio_stats = response.get('portfolio_statistics', {})
            
            # Look for the BALANCE investment
            balance_investment = None
            for investment in investments:
                if (investment.get('fund_code') == 'BALANCE' and 
                    investment.get('principal_amount') == 100000.00):
                    balance_investment = investment
                    break
            
            if balance_investment:
                details = f"Investment found - Principal: ${balance_investment.get('principal_amount', 0):,.2f}, Current Value: ${balance_investment.get('current_value', 0):,.2f}"
                self.log_test("Salvador's BALANCE Investment Visible", True, details)
                
                # Print investment details
                print(f"   Investment ID: {balance_investment.get('investment_id')}")
                print(f"   Fund: {balance_investment.get('fund_code')}")
                print(f"   Status: {balance_investment.get('status')}")
                print(f"   Deposit Date: {balance_investment.get('deposit_date')}")
                
                # Print portfolio statistics
                total_invested = portfolio_stats.get('total_invested', 0)
                total_current_value = portfolio_stats.get('total_current_value', 0)
                print(f"   Portfolio Total Invested: ${total_invested:,.2f}")
                print(f"   Portfolio Current Value: ${total_current_value:,.2f}")
                
                return True
            else:
                self.log_test("Salvador's BALANCE Investment Visible", False, "BALANCE investment not found in client view")
                print(f"   Found {len(investments)} investments, but no BALANCE fund with $100,000")
                return False
        else:
            self.log_test("Client Investment View", False, f"Status: {status}, Response: {response}")
            return False
    
    def verify_admin_portfolio_summary(self):
        """Verify admin can see Salvador's investment in portfolio"""
        print("\n📊 Verifying Admin Portfolio Summary...")
        
        if not self.admin_token:
            self.log_test("Admin Portfolio Summary", False, "No admin token available")
            return False
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.admin_token}'
        }
        
        success, response, status = self.make_request(
            'GET',
            'admin/portfolio-summary',
            headers=headers
        )
        
        if success:
            total_aum = response.get('aum', response.get('total_aum', 0))
            allocation = response.get('allocation', {})
            
            # Check if BALANCE fund allocation includes Salvador's investment
            balance_allocation = allocation.get('BALANCE', 0)
            
            details = f"Total AUM: ${total_aum:,.2f}, BALANCE Allocation: {balance_allocation}%"
            
            if total_aum >= 100000:  # Should include Salvador's $100K investment
                self.log_test("Admin Portfolio Shows Salvador's Investment", True, details)
                
                # Print detailed allocation
                print(f"   Fund Allocations:")
                for fund, percentage in allocation.items():
                    print(f"     {fund}: {percentage}%")
                
                return True
            else:
                self.log_test("Admin Portfolio Shows Salvador's Investment", False, f"AUM too low: {details}")
                return False
        else:
            self.log_test("Admin Portfolio Summary", False, f"Status: {status}, Response: {response}")
            return False
    
    def verify_mt5_allocation(self):
        """Verify MT5 account shows $100,000 allocated to DooTechnology broker"""
        print("\n💹 Verifying MT5 Account Allocation...")
        
        if not self.admin_token:
            self.log_test("MT5 Allocation Verification", False, "No admin token available")
            return False
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.admin_token}'
        }
        
        # Get all MT5 accounts
        success, response, status = self.make_request(
            'GET',
            'mt5/admin/accounts',
            headers=headers
        )
        
        if success:
            accounts = response.get('accounts', [])
            
            # Look for Salvador's DooTechnology account
            salvador_mt5_account = None
            for account in accounts:
                if (account.get('client_id') == 'client_0fd630c3' and 
                    account.get('fund_code') == 'BALANCE' and
                    'dootechnology' in account.get('account_id', '').lower()):
                    salvador_mt5_account = account
                    break
            
            if salvador_mt5_account:
                allocated_amount = salvador_mt5_account.get('total_allocated', 0)
                current_equity = salvador_mt5_account.get('current_equity', 0)
                
                if allocated_amount == 100000.00:
                    details = f"Allocated: ${allocated_amount:,.2f}, Current Equity: ${current_equity:,.2f}"
                    self.log_test("MT5 Account Shows Correct Allocation", True, details)
                    
                    # Print MT5 performance details
                    profit_loss = salvador_mt5_account.get('profit_loss', 0)
                    print(f"   Profit/Loss: ${profit_loss:,.2f}")
                    print(f"   Last Update: {salvador_mt5_account.get('updated_at')}")
                    print(f"   MT5 Server: {salvador_mt5_account.get('mt5_server')}")
                    
                    return True
                else:
                    self.log_test("MT5 Account Shows Correct Allocation", False, f"Expected $100,000, got ${allocated_amount:,.2f}")
                    return False
            else:
                self.log_test("MT5 Account Shows Correct Allocation", False, "Salvador's DooTechnology MT5 account not found")
                return False
        else:
            self.log_test("MT5 Allocation Verification", False, f"Status: {status}, Response: {response}")
            return False
    
    def run_complete_test(self):
        """Run the complete end-to-end test"""
        print("=" * 80)
        print("🎯 SALVADOR PALMA BALANCE INVESTMENT WITH DOOTECHNOLOGY MT5 INTEGRATION TEST")
        print("=" * 80)
        
        # Step 1: Authenticate
        if not self.authenticate_admin():
            print("\n❌ CRITICAL: Admin authentication failed - cannot proceed")
            return False
        
        if not self.authenticate_client():
            print("\n❌ CRITICAL: Salvador authentication failed - cannot proceed")
            return False
        
        # Step 2: Create Investment
        if not self.create_salvador_balance_investment():
            print("\n❌ CRITICAL: Investment creation failed - cannot proceed")
            return False
        
        # Step 3: Verify MT5 Integration
        mt5_success = self.verify_mt5_dootechnology_account()
        
        # Step 4: Verify Client View
        client_view_success = self.verify_salvador_client_view()
        
        # Step 5: Verify Admin Portfolio
        admin_portfolio_success = self.verify_admin_portfolio_summary()
        
        # Step 6: Verify MT5 Allocation
        mt5_allocation_success = self.verify_mt5_allocation()
        
        # Summary
        print("\n" + "=" * 80)
        print("📋 TEST SUMMARY")
        print("=" * 80)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        print("\n🎯 CRITICAL REQUIREMENTS:")
        print(f"✅ Investment Creation: {'PASS' if self.investment_id else 'FAIL'}")
        print(f"{'✅' if mt5_success else '❌'} DooTechnology MT5 Account: {'PASS' if mt5_success else 'FAIL'}")
        print(f"{'✅' if client_view_success else '❌'} Salvador Client View: {'PASS' if client_view_success else 'FAIL'}")
        print(f"{'✅' if admin_portfolio_success else '❌'} Admin Portfolio Summary: {'PASS' if admin_portfolio_success else 'FAIL'}")
        print(f"{'✅' if mt5_allocation_success else '❌'} MT5 Allocation Verification: {'PASS' if mt5_allocation_success else 'FAIL'}")
        
        all_critical_passed = all([
            self.investment_id is not None,
            mt5_success,
            client_view_success, 
            admin_portfolio_success,
            mt5_allocation_success
        ])
        
        print(f"\n🏆 OVERALL RESULT: {'✅ ALL CRITICAL TESTS PASSED' if all_critical_passed else '❌ SOME CRITICAL TESTS FAILED'}")
        
        if self.investment_id:
            print(f"\n💰 Created Investment ID: {self.investment_id}")
            print("📝 Investment Details:")
            print("   - Client: Salvador Palma (client_0fd630c3)")
            print("   - Fund: BALANCE")
            print("   - Amount: $100,000.00")
            print("   - Deposit Date: 2024-12-19")
            print("   - Broker: DooTechnology")
        
        return all_critical_passed

if __name__ == "__main__":
    tester = SalvadorDooTechnologyTester()
    success = tester.run_complete_test()
    sys.exit(0 if success else 1)