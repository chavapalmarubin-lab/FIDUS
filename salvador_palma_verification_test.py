#!/usr/bin/env python3
"""
SALVADOR PALMA CLEAN SETUP VERIFICATION TEST
============================================

This test verifies that the database has been reset to contain ONLY Salvador Palma's data:
- Exactly 1 BALANCE investment for $100,000
- Exactly 1 MT5 account with login 9928326
- MT5 account belongs to Salvador (client_003) and BALANCE fund
- Broker is DooTechnology
- No other client data exists

Expected Results After Database Reset:
- Total investments: 1 (Salvador BALANCE $100k)
- Total MT5 accounts: 1 (client_003 with login 9928326)
- MT5 broker: DooTechnology
- MT5 server: DooTechnology-Live
- No other client data exists
"""

import requests
import sys
from datetime import datetime
import json

class SalvadorPalmaVerificationTester:
    def __init__(self, base_url="https://invest-platform-19.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.critical_failures = []
        self.admin_token = None
        self.client_token = None
        
        # Expected Salvador Palma data
        self.expected_client_id = "client_003"
        self.expected_client_name = "SALVADOR PALMA"
        self.expected_investment_amount = 100000.0
        self.expected_fund_code = "BALANCE"
        self.expected_mt5_login = 9928326
        self.expected_broker = "DooTechnology"
        self.expected_server = "DooTechnology-Live"

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
                print(f"✅ Admin authentication successful")
                return True
            else:
                print(f"❌ No token received in admin login response")
                return False
        else:
            print(f"❌ Admin authentication failed")
            return False

    def authenticate_client(self):
        """Authenticate as Salvador Palma (client3) to get JWT token"""
        print("\n🔐 Authenticating as Salvador Palma...")
        success, response = self.run_test(
            "Salvador Login",
            "POST",
            "api/auth/login",
            200,
            data={
                "username": "client3",
                "password": "password123",
                "user_type": "client"
            }
        )
        
        if success:
            self.client_token = response.get('token')
            client_name = response.get('name')
            client_id = response.get('id')
            if self.client_token:
                print(f"✅ Salvador authentication successful: {client_name} ({client_id})")
                return True
            else:
                print(f"❌ No token received in Salvador login response")
                return False
        else:
            print(f"❌ Salvador authentication failed")
            return False

    def get_auth_headers(self, use_admin=True):
        """Get authorization headers with JWT token"""
        token = self.admin_token if use_admin else self.client_token
        if token:
            return {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}'
            }
        else:
            return {'Content-Type': 'application/json'}

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        if headers is None:
            headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 {name}")
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

            print(f"   Status: {response.status_code}")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                try:
                    response_data = response.json()
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ FAILED - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error text: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ FAILED - Error: {str(e)}")
            return False, {}

    def verify_salvador_investment_data(self):
        """Priority 1: Verify Salvador has exactly 1 BALANCE investment"""
        print("\n" + "="*80)
        print("PRIORITY 1: SALVADOR PALMA INVESTMENT VERIFICATION")
        print("="*80)
        
        success, response = self.run_test(
            "GET Salvador's Investment Data",
            "GET",
            f"api/investments/client/{self.expected_client_id}",
            200,
            headers=self.get_auth_headers(use_admin=True)
        )
        
        if not success:
            self.critical_failures.append("Cannot retrieve Salvador's investment data")
            return False
            
        # Verify investment structure
        investments = response.get('investments', [])
        portfolio_stats = response.get('portfolio_stats', {})
        
        print(f"\n📊 SALVADOR'S INVESTMENT ANALYSIS:")
        print(f"   Total Investments Found: {len(investments)}")
        print(f"   Portfolio Total Value: ${portfolio_stats.get('total_value', 0):,.2f}")
        print(f"   Portfolio Principal: ${portfolio_stats.get('total_principal', 0):,.2f}")
        
        # CRITICAL CHECK 1: Exactly 1 investment
        if len(investments) != 1:
            self.critical_failures.append(f"Expected exactly 1 investment, found {len(investments)}")
            print(f"❌ CRITICAL FAILURE: Expected 1 investment, found {len(investments)}")
            return False
        else:
            print(f"✅ CORRECT: Exactly 1 investment found")
        
        investment = investments[0]
        
        # CRITICAL CHECK 2: Investment is BALANCE fund
        fund_code = investment.get('fund_code')
        if fund_code != self.expected_fund_code:
            self.critical_failures.append(f"Expected BALANCE fund, found {fund_code}")
            print(f"❌ CRITICAL FAILURE: Expected {self.expected_fund_code} fund, found {fund_code}")
            return False
        else:
            print(f"✅ CORRECT: Investment is {self.expected_fund_code} fund")
        
        # CRITICAL CHECK 3: Investment amount is $100,000
        principal_amount = investment.get('principal_amount', 0)
        if principal_amount != self.expected_investment_amount:
            self.critical_failures.append(f"Expected $100,000 investment, found ${principal_amount:,.2f}")
            print(f"❌ CRITICAL FAILURE: Expected ${self.expected_investment_amount:,.2f}, found ${principal_amount:,.2f}")
            return False
        else:
            print(f"✅ CORRECT: Investment amount is ${principal_amount:,.2f}")
        
        # CRITICAL CHECK 4: Client ID matches
        client_id = investment.get('client_id')
        if client_id != self.expected_client_id:
            self.critical_failures.append(f"Expected client_003, found {client_id}")
            print(f"❌ CRITICAL FAILURE: Expected {self.expected_client_id}, found {client_id}")
            return False
        else:
            print(f"✅ CORRECT: Client ID is {client_id}")
        
        print(f"\n📋 INVESTMENT DETAILS:")
        print(f"   Investment ID: {investment.get('investment_id')}")
        print(f"   Fund Code: {investment.get('fund_code')}")
        print(f"   Principal Amount: ${investment.get('principal_amount', 0):,.2f}")
        print(f"   Current Value: ${investment.get('current_value', 0):,.2f}")
        print(f"   Status: {investment.get('status')}")
        print(f"   Deposit Date: {investment.get('deposit_date')}")
        
        return True

    def verify_mt5_account_data(self):
        """Priority 2: Verify exactly 1 MT5 account exists with correct details"""
        print("\n" + "="*80)
        print("PRIORITY 2: MT5 ACCOUNT VERIFICATION")
        print("="*80)
        
        # Check all MT5 accounts
        success, response = self.run_test(
            "GET All MT5 Accounts",
            "GET",
            "api/mt5/admin/accounts",
            200,
            headers=self.get_auth_headers(use_admin=True)
        )
        
        if not success:
            self.critical_failures.append("Cannot retrieve MT5 accounts data")
            return False
            
        accounts = response.get('accounts', [])
        
        print(f"\n📊 MT5 ACCOUNTS ANALYSIS:")
        print(f"   Total MT5 Accounts Found: {len(accounts)}")
        
        # CRITICAL CHECK 1: Exactly 1 MT5 account
        if len(accounts) != 1:
            self.critical_failures.append(f"Expected exactly 1 MT5 account, found {len(accounts)}")
            print(f"❌ CRITICAL FAILURE: Expected 1 MT5 account, found {len(accounts)}")
            if len(accounts) > 1:
                print("   Found accounts:")
                for i, acc in enumerate(accounts):
                    print(f"   {i+1}. Client: {acc.get('client_id')}, Login: {acc.get('mt5_login')}, Fund: {acc.get('fund_code')}")
            return False
        else:
            print(f"✅ CORRECT: Exactly 1 MT5 account found")
        
        account = accounts[0]
        
        # CRITICAL CHECK 2: MT5 login is 9928326
        mt5_login = account.get('mt5_login')
        if mt5_login != self.expected_mt5_login:
            self.critical_failures.append(f"Expected MT5 login {self.expected_mt5_login}, found {mt5_login}")
            print(f"❌ CRITICAL FAILURE: Expected MT5 login {self.expected_mt5_login}, found {mt5_login}")
            return False
        else:
            print(f"✅ CORRECT: MT5 login is {mt5_login}")
        
        # CRITICAL CHECK 3: Account belongs to Salvador (client_003)
        client_id = account.get('client_id')
        if client_id != self.expected_client_id:
            self.critical_failures.append(f"Expected client_003, found {client_id}")
            print(f"❌ CRITICAL FAILURE: Expected {self.expected_client_id}, found {client_id}")
            return False
        else:
            print(f"✅ CORRECT: Account belongs to {client_id}")
        
        # CRITICAL CHECK 4: Account is for BALANCE fund
        fund_code = account.get('fund_code')
        if fund_code != self.expected_fund_code:
            self.critical_failures.append(f"Expected BALANCE fund, found {fund_code}")
            print(f"❌ CRITICAL FAILURE: Expected {self.expected_fund_code} fund, found {fund_code}")
            return False
        else:
            print(f"✅ CORRECT: Account is for {fund_code} fund")
        
        # CRITICAL CHECK 5: Broker is DooTechnology
        broker_name = account.get('broker_name')
        if broker_name != self.expected_broker:
            self.critical_failures.append(f"Expected DooTechnology broker, found {broker_name}")
            print(f"❌ CRITICAL FAILURE: Expected {self.expected_broker} broker, found {broker_name}")
            return False
        else:
            print(f"✅ CORRECT: Broker is {broker_name}")
        
        # CRITICAL CHECK 6: Server is DooTechnology-Live
        mt5_server = account.get('mt5_server')
        if mt5_server != self.expected_server:
            self.critical_failures.append(f"Expected DooTechnology-Live server, found {mt5_server}")
            print(f"❌ CRITICAL FAILURE: Expected {self.expected_server} server, found {mt5_server}")
            return False
        else:
            print(f"✅ CORRECT: Server is {mt5_server}")
        
        # CRITICAL CHECK 7: Allocated amount is $100,000
        allocated_amount = account.get('allocated_amount', 0)
        if allocated_amount != self.expected_investment_amount:
            self.critical_failures.append(f"Expected $100,000 allocation, found ${allocated_amount:,.2f}")
            print(f"❌ CRITICAL FAILURE: Expected ${self.expected_investment_amount:,.2f} allocation, found ${allocated_amount:,.2f}")
            return False
        else:
            print(f"✅ CORRECT: Allocated amount is ${allocated_amount:,.2f}")
        
        print(f"\n📋 MT5 ACCOUNT DETAILS:")
        print(f"   Account ID: {account.get('account_id')}")
        print(f"   Client ID: {account.get('client_id')}")
        print(f"   Fund Code: {account.get('fund_code')}")
        print(f"   MT5 Login: {account.get('mt5_login')}")
        print(f"   MT5 Server: {account.get('mt5_server')}")
        print(f"   Broker Name: {account.get('broker_name')}")
        print(f"   Broker Code: {account.get('broker_code')}")
        print(f"   Allocated Amount: ${account.get('allocated_amount', 0):,.2f}")
        print(f"   Status: {account.get('status')}")
        
        return True

    def verify_mt5_accounts_by_broker(self):
        """Priority 3: Verify MT5 accounts grouped by broker shows only DooTechnology"""
        print("\n" + "="*80)
        print("PRIORITY 3: MT5 ACCOUNTS BY BROKER VERIFICATION")
        print("="*80)
        
        success, response = self.run_test(
            "GET MT5 Accounts by Broker",
            "GET",
            "api/mt5/admin/accounts/by-broker",
            200,
            headers=self.get_auth_headers(use_admin=True)
        )
        
        if not success:
            self.critical_failures.append("Cannot retrieve MT5 accounts by broker")
            return False
            
        accounts_by_broker = response.get('accounts_by_broker', {})
        
        print(f"\n📊 MT5 ACCOUNTS BY BROKER ANALYSIS:")
        print(f"   Total Brokers Found: {len(accounts_by_broker)}")
        
        for broker, accounts in accounts_by_broker.items():
            print(f"   {broker}: {len(accounts)} accounts")
            for account in accounts:
                print(f"     - Client: {account.get('client_id')}, Login: {account.get('mt5_login')}, Fund: {account.get('fund_code')}")
        
        # CRITICAL CHECK 1: Only DooTechnology broker should exist
        if len(accounts_by_broker) != 1:
            self.critical_failures.append(f"Expected only 1 broker (DooTechnology), found {len(accounts_by_broker)}")
            print(f"❌ CRITICAL FAILURE: Expected only 1 broker, found {len(accounts_by_broker)}")
            return False
        
        # CRITICAL CHECK 2: The broker should be DooTechnology
        if self.expected_broker not in accounts_by_broker:
            brokers_found = list(accounts_by_broker.keys())
            self.critical_failures.append(f"Expected DooTechnology broker, found {brokers_found}")
            print(f"❌ CRITICAL FAILURE: Expected {self.expected_broker} broker, found {brokers_found}")
            return False
        else:
            print(f"✅ CORRECT: Only {self.expected_broker} broker found")
        
        # CRITICAL CHECK 3: DooTechnology should have exactly 1 account
        doo_accounts = accounts_by_broker[self.expected_broker]
        if len(doo_accounts) != 1:
            self.critical_failures.append(f"Expected 1 DooTechnology account, found {len(doo_accounts)}")
            print(f"❌ CRITICAL FAILURE: Expected 1 {self.expected_broker} account, found {len(doo_accounts)}")
            return False
        else:
            print(f"✅ CORRECT: Exactly 1 {self.expected_broker} account found")
        
        return True

    def verify_admin_portfolio_summary(self):
        """Priority 4: Verify admin sees Salvador's investment in portfolio summary"""
        print("\n" + "="*80)
        print("PRIORITY 4: ADMIN PORTFOLIO SUMMARY VERIFICATION")
        print("="*80)
        
        success, response = self.run_test(
            "GET Admin Portfolio Summary",
            "GET",
            "api/admin/portfolio-summary",
            200
        )
        
        if not success:
            self.critical_failures.append("Cannot retrieve admin portfolio summary")
            return False
            
        total_aum = response.get('aum', 0)
        allocation = response.get('allocation', {})
        client_count = response.get('client_count', 0)
        
        print(f"\n📊 ADMIN PORTFOLIO SUMMARY ANALYSIS:")
        print(f"   Total AUM: ${total_aum:,.2f}")
        print(f"   Client Count: {client_count}")
        print(f"   Fund Allocation:")
        for fund, percentage in allocation.items():
            print(f"     {fund}: {percentage:.2f}%")
        
        # CRITICAL CHECK 1: Total AUM should be $100,000 (Salvador's investment)
        if total_aum != self.expected_investment_amount:
            self.critical_failures.append(f"Expected AUM $100,000, found ${total_aum:,.2f}")
            print(f"❌ CRITICAL FAILURE: Expected AUM ${self.expected_investment_amount:,.2f}, found ${total_aum:,.2f}")
            return False
        else:
            print(f"✅ CORRECT: Total AUM is ${total_aum:,.2f}")
        
        # CRITICAL CHECK 2: Client count should be 1 (only Salvador)
        if client_count != 1:
            self.critical_failures.append(f"Expected 1 client, found {client_count}")
            print(f"❌ CRITICAL FAILURE: Expected 1 client, found {client_count}")
            return False
        else:
            print(f"✅ CORRECT: Client count is {client_count}")
        
        # CRITICAL CHECK 3: BALANCE fund should have 100% allocation
        balance_allocation = allocation.get('BALANCE', 0)
        if balance_allocation != 100.0:
            self.critical_failures.append(f"Expected BALANCE 100% allocation, found {balance_allocation}%")
            print(f"❌ CRITICAL FAILURE: Expected BALANCE 100% allocation, found {balance_allocation}%")
            return False
        else:
            print(f"✅ CORRECT: BALANCE fund has {balance_allocation}% allocation")
        
        # CRITICAL CHECK 4: Other funds should have 0% allocation
        other_funds = ['CORE', 'DYNAMIC', 'UNLIMITED']
        for fund in other_funds:
            fund_allocation = allocation.get(fund, 0)
            if fund_allocation != 0:
                self.critical_failures.append(f"Expected {fund} 0% allocation, found {fund_allocation}%")
                print(f"❌ CRITICAL FAILURE: Expected {fund} 0% allocation, found {fund_allocation}%")
                return False
            else:
                print(f"✅ CORRECT: {fund} fund has {fund_allocation}% allocation")
        
        return True

    def verify_no_other_client_data(self):
        """Priority 5: Verify no other clients have investments or MT5 accounts"""
        print("\n" + "="*80)
        print("PRIORITY 5: NO OTHER CLIENT DATA VERIFICATION")
        print("="*80)
        
        # Check all clients
        success, response = self.run_test(
            "GET All Clients",
            "GET",
            "api/clients/all",
            200
        )
        
        if not success:
            self.critical_failures.append("Cannot retrieve all clients data")
            return False
            
        clients = response.get('clients', [])
        
        print(f"\n📊 ALL CLIENTS ANALYSIS:")
        print(f"   Total Clients Found: {len(clients)}")
        
        # Find Salvador and other clients
        salvador_found = False
        other_clients_with_investments = []
        
        for client in clients:
            client_id = client.get('id')
            client_name = client.get('name')
            total_investments = client.get('total_investments', 0)
            
            print(f"   Client: {client_name} ({client_id}) - Investments: {total_investments}")
            
            if client_id == self.expected_client_id:
                salvador_found = True
                if total_investments != 1:
                    self.critical_failures.append(f"Salvador should have 1 investment, found {total_investments}")
                    print(f"❌ CRITICAL FAILURE: Salvador should have 1 investment, found {total_investments}")
                    return False
                else:
                    print(f"✅ CORRECT: Salvador has {total_investments} investment")
            else:
                if total_investments > 0:
                    other_clients_with_investments.append(f"{client_name} ({client_id}): {total_investments}")
        
        # CRITICAL CHECK 1: Salvador should be found
        if not salvador_found:
            self.critical_failures.append("Salvador Palma (client_003) not found in clients list")
            print(f"❌ CRITICAL FAILURE: Salvador Palma ({self.expected_client_id}) not found")
            return False
        else:
            print(f"✅ CORRECT: Salvador Palma found in clients list")
        
        # CRITICAL CHECK 2: No other clients should have investments
        if other_clients_with_investments:
            self.critical_failures.append(f"Other clients have investments: {other_clients_with_investments}")
            print(f"❌ CRITICAL FAILURE: Other clients have investments:")
            for client_info in other_clients_with_investments:
                print(f"   - {client_info}")
            return False
        else:
            print(f"✅ CORRECT: No other clients have investments")
        
        return True

    def run_comprehensive_verification(self):
        """Run all verification tests"""
        print("\n" + "="*100)
        print("SALVADOR PALMA CLEAN SETUP VERIFICATION")
        print("="*100)
        print("Verifying database contains ONLY Salvador Palma's data:")
        print("- Exactly 1 BALANCE investment for $100,000")
        print("- Exactly 1 MT5 account with login 9928326")
        print("- MT5 account belongs to Salvador (client_003) and BALANCE fund")
        print("- Broker is DooTechnology")
        print("- No other client data exists")
        print("="*100)
        
        # Run all verification tests
        test_results = []
        
        test_results.append(("Salvador Investment Data", self.verify_salvador_investment_data()))
        test_results.append(("MT5 Account Data", self.verify_mt5_account_data()))
        test_results.append(("MT5 Accounts by Broker", self.verify_mt5_accounts_by_broker()))
        test_results.append(("Admin Portfolio Summary", self.verify_admin_portfolio_summary()))
        test_results.append(("No Other Client Data", self.verify_no_other_client_data()))
        
        # Print final results
        print("\n" + "="*100)
        print("VERIFICATION RESULTS SUMMARY")
        print("="*100)
        
        all_passed = True
        for test_name, result in test_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{status} - {test_name}")
            if not result:
                all_passed = False
        
        print(f"\nTests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.critical_failures:
            print(f"\n🚨 CRITICAL FAILURES FOUND ({len(self.critical_failures)}):")
            for i, failure in enumerate(self.critical_failures, 1):
                print(f"   {i}. {failure}")
        
        if all_passed:
            print(f"\n🎉 SUCCESS: Salvador Palma clean setup verification PASSED!")
            print(f"✅ Database contains exactly the expected data:")
            print(f"   - 1 BALANCE investment for $100,000")
            print(f"   - 1 MT5 account (login: 9928326)")
            print(f"   - DooTechnology broker")
            print(f"   - No other client data")
            return True
        else:
            print(f"\n🚨 FAILURE: Salvador Palma clean setup verification FAILED!")
            print(f"❌ Database does not match expected clean state")
            return False

def main():
    """Main test execution"""
    tester = SalvadorPalmaVerificationTester()
    
    try:
        success = tester.run_comprehensive_verification()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()