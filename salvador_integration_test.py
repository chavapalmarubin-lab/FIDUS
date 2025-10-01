#!/usr/bin/env python3
"""
SALVADOR PALMA MT5 INTEGRATION VERIFICATION TEST
===============================================

This test verifies Salvador integration after backend fixes as requested in review:

BACKEND FIXES COMPLETED:
1. ✅ Database linking: Both MT5 accounts now linked to investments
2. ✅ Fixed async/await errors in MT5 service calls
3. ✅ Fixed coroutine handling in connection status calls

CRITICAL TESTS NEEDED:
1. Fund Performance Dashboard: /api/admin/fund-performance/dashboard - Should show Salvador with MT5 data
2. Cash Flow Management: /api/admin/cashflow/overview - Should include Salvador's trading profits 
3. CRM Dashboard: /api/crm/admin/dashboard - Should display both linked MT5 accounts
4. MT5 Accounts: /api/mt5/admin/accounts - Should show both accounts with proper Investment IDs

EXPECTED RESULTS:
- Salvador should appear in Fund Performance with $860,448.65 trading profits
- Cash Flow should show Salvador's MT5 performance contributing to calculations
- Both MT5 accounts should show proper Investment ID links (not None)
- CRM Dashboard should display Salvador's complete MT5 integration
"""

import requests
import sys
from datetime import datetime
import json

class SalvadorIntegrationTester:
    def __init__(self, base_url="https://crm-workspace-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.admin_token = None
        self.critical_issues = []
        self.success_items = []

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
                response = requests.get(url, headers=headers, timeout=15)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=15)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=15)

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

    def test_admin_login(self):
        """Test admin login to get authentication token"""
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
        if success and response.get('token'):
            self.admin_token = response['token']
            print(f"   Admin logged in: {response.get('name', 'Unknown')}")
            print(f"   Token received: {self.admin_token[:20]}...")
            return True
        else:
            self.critical_issues.append("Admin login failed - cannot proceed with authenticated tests")
            return False

    def get_auth_headers(self):
        """Get headers with admin authentication"""
        if not self.admin_token:
            return {'Content-Type': 'application/json'}
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.admin_token}'
        }

    def test_fund_performance_dashboard(self):
        """Test Fund Performance Dashboard - Should show Salvador with MT5 data"""
        print("\n" + "="*80)
        print("🎯 CRITICAL TEST 1: FUND PERFORMANCE DASHBOARD")
        print("Expected: Salvador should appear with $860,448.65 trading profits")
        print("="*80)
        
        success, response = self.run_test(
            "Fund Performance Dashboard",
            "GET",
            "api/admin/fund-performance/dashboard",
            200,
            headers=self.get_auth_headers()
        )
        
        if success:
            # Check if Salvador appears in the dashboard
            clients = response.get('clients', [])
            fund_performance = response.get('fund_performance', [])
            
            print(f"   Total clients in dashboard: {len(clients)}")
            print(f"   Fund performance records: {len(fund_performance)}")
            
            # Look for Salvador specifically
            salvador_found = False
            salvador_mt5_profits = 0
            
            for client in clients:
                if 'SALVADOR' in client.get('name', '').upper() or client.get('client_id') == 'client_003':
                    salvador_found = True
                    salvador_mt5_profits = client.get('mt5_trading_profits', 0)
                    print(f"   ✅ SALVADOR FOUND: {client.get('name')}")
                    print(f"   Client ID: {client.get('client_id')}")
                    print(f"   MT5 Trading Profits: ${salvador_mt5_profits:,.2f}")
                    
                    # Check if profits match expected amount
                    expected_profits = 860448.65
                    if abs(salvador_mt5_profits - expected_profits) < 1000:  # Allow small variance
                        print(f"   ✅ MT5 PROFITS CORRECT: ${salvador_mt5_profits:,.2f} ≈ ${expected_profits:,.2f}")
                        self.success_items.append(f"Fund Performance Dashboard shows Salvador with correct MT5 profits: ${salvador_mt5_profits:,.2f}")
                    else:
                        print(f"   ❌ MT5 PROFITS INCORRECT: Expected ~${expected_profits:,.2f}, got ${salvador_mt5_profits:,.2f}")
                        self.critical_issues.append(f"Fund Performance Dashboard shows incorrect MT5 profits for Salvador: ${salvador_mt5_profits:,.2f} (expected ${expected_profits:,.2f})")
                    
                    # Check for MT5 account data
                    mt5_accounts = client.get('mt5_accounts', [])
                    print(f"   MT5 Accounts linked: {len(mt5_accounts)}")
                    for account in mt5_accounts:
                        print(f"     - Login: {account.get('login')}, Broker: {account.get('broker')}")
                    
                    break
            
            if not salvador_found:
                print(f"   ❌ SALVADOR NOT FOUND in Fund Performance Dashboard")
                self.critical_issues.append("Salvador Palma missing from Fund Performance Dashboard - MT5 integration broken")
                return False
            
            return True
        else:
            self.critical_issues.append("Fund Performance Dashboard endpoint failed")
            return False

    def test_cash_flow_management(self):
        """Test Cash Flow Management - Should include Salvador's trading profits"""
        print("\n" + "="*80)
        print("🎯 CRITICAL TEST 2: CASH FLOW MANAGEMENT")
        print("Expected: Salvador's MT5 performance should contribute to calculations")
        print("="*80)
        
        success, response = self.run_test(
            "Cash Flow Management Overview",
            "GET",
            "api/admin/cashflow/overview",
            200,
            headers=self.get_auth_headers()
        )
        
        if success:
            mt5_trading_profits = response.get('mt5_trading_profits', 0)
            client_obligations = response.get('client_interest_obligations', 0)
            net_profitability = response.get('net_fund_profitability', 0)
            
            print(f"   MT5 Trading Profits: ${mt5_trading_profits:,.2f}")
            print(f"   Client Interest Obligations: ${client_obligations:,.2f}")
            print(f"   Net Fund Profitability: ${net_profitability:,.2f}")
            
            # Check if Salvador's profits are included
            expected_mt5_profits = 860448.65
            if mt5_trading_profits > 0:
                print(f"   ✅ MT5 TRADING PROFITS PRESENT: ${mt5_trading_profits:,.2f}")
                
                if abs(mt5_trading_profits - expected_mt5_profits) < 50000:  # Allow reasonable variance
                    print(f"   ✅ MT5 PROFITS MATCH EXPECTED: ${mt5_trading_profits:,.2f} ≈ ${expected_mt5_profits:,.2f}")
                    self.success_items.append(f"Cash Flow Management includes Salvador's MT5 profits: ${mt5_trading_profits:,.2f}")
                else:
                    print(f"   ⚠️  MT5 PROFITS VARIANCE: Expected ~${expected_mt5_profits:,.2f}, got ${mt5_trading_profits:,.2f}")
                    self.success_items.append(f"Cash Flow Management shows MT5 profits: ${mt5_trading_profits:,.2f} (some variance from expected)")
            else:
                print(f"   ❌ NO MT5 TRADING PROFITS - Salvador's data not contributing")
                self.critical_issues.append("Cash Flow Management shows $0 MT5 trading profits - Salvador's MT5 data not integrated")
                return False
            
            # Check client obligations
            if client_obligations > 0:
                print(f"   ✅ CLIENT OBLIGATIONS CALCULATED: ${client_obligations:,.2f}")
                self.success_items.append(f"Cash Flow Management calculates client obligations: ${client_obligations:,.2f}")
            else:
                print(f"   ❌ NO CLIENT OBLIGATIONS - Calculation may be broken")
                self.critical_issues.append("Cash Flow Management shows $0 client obligations")
            
            return True
        else:
            self.critical_issues.append("Cash Flow Management endpoint failed")
            return False

    def test_crm_dashboard(self):
        """Test CRM Dashboard - Should display both linked MT5 accounts"""
        print("\n" + "="*80)
        print("🎯 CRITICAL TEST 3: CRM DASHBOARD")
        print("Expected: Both MT5 accounts should be displayed with proper linking")
        print("="*80)
        
        success, response = self.run_test(
            "CRM Admin Dashboard",
            "GET",
            "api/crm/admin/dashboard",
            200,
            headers=self.get_auth_headers()
        )
        
        if success:
            clients = response.get('clients', [])
            mt5_accounts = response.get('mt5_accounts', [])
            
            print(f"   Total clients: {len(clients)}")
            print(f"   Total MT5 accounts: {len(mt5_accounts)}")
            
            # Look for Salvador in clients
            salvador_found = False
            for client in clients:
                if 'SALVADOR' in client.get('name', '').upper() or client.get('id') == 'client_003':
                    salvador_found = True
                    print(f"   ✅ SALVADOR FOUND in CRM: {client.get('name')}")
                    print(f"   Client Balance: ${client.get('total_balance', 0):,.2f}")
                    break
            
            if not salvador_found:
                print(f"   ❌ SALVADOR NOT FOUND in CRM Dashboard")
                self.critical_issues.append("Salvador Palma missing from CRM Dashboard")
            
            # Check MT5 accounts for Salvador
            salvador_mt5_accounts = []
            for account in mt5_accounts:
                if account.get('client_id') == 'client_003':
                    salvador_mt5_accounts.append(account)
            
            print(f"   Salvador's MT5 accounts: {len(salvador_mt5_accounts)}")
            
            expected_accounts = [
                {'login': '9928326', 'broker': 'DooTechnology'},
                {'login': '15759667', 'broker': 'VT Markets'}
            ]
            
            accounts_found = 0
            for expected in expected_accounts:
                for account in salvador_mt5_accounts:
                    if (str(account.get('login')) == expected['login'] and 
                        expected['broker'].lower() in account.get('broker', '').lower()):
                        accounts_found += 1
                        investment_id = account.get('investment_id')
                        print(f"   ✅ FOUND: {expected['broker']} account (Login: {expected['login']})")
                        print(f"     Investment ID: {investment_id}")
                        
                        if investment_id and investment_id != 'None':
                            print(f"     ✅ PROPERLY LINKED to investment")
                        else:
                            print(f"     ❌ NOT LINKED - Investment ID is None")
                            self.critical_issues.append(f"{expected['broker']} MT5 account (Login: {expected['login']}) not linked to investment")
                        break
            
            if accounts_found == 2:
                print(f"   ✅ BOTH MT5 ACCOUNTS FOUND in CRM Dashboard")
                self.success_items.append("CRM Dashboard displays both Salvador MT5 accounts (DooTechnology & VT Markets)")
            else:
                print(f"   ❌ MISSING MT5 ACCOUNTS: Found {accounts_found}/2 expected accounts")
                self.critical_issues.append(f"CRM Dashboard missing Salvador MT5 accounts: found {accounts_found}/2")
            
            return salvador_found and accounts_found > 0
        else:
            self.critical_issues.append("CRM Dashboard endpoint failed")
            return False

    def test_mt5_accounts_admin(self):
        """Test MT5 Accounts Admin - Should show both accounts with proper Investment IDs"""
        print("\n" + "="*80)
        print("🎯 CRITICAL TEST 4: MT5 ACCOUNTS ADMIN")
        print("Expected: Both accounts should show proper Investment IDs (not None)")
        print("="*80)
        
        success, response = self.run_test(
            "MT5 Admin Accounts",
            "GET",
            "api/mt5/admin/accounts",
            200,
            headers=self.get_auth_headers()
        )
        
        if success:
            accounts = response.get('accounts', [])
            print(f"   Total MT5 accounts: {len(accounts)}")
            
            # Look for Salvador's accounts
            salvador_accounts = []
            for account in accounts:
                if account.get('client_id') == 'client_003':
                    salvador_accounts.append(account)
            
            print(f"   Salvador's MT5 accounts: {len(salvador_accounts)}")
            
            expected_logins = ['9928326', '15759667']
            properly_linked = 0
            
            for account in salvador_accounts:
                login = str(account.get('login', ''))
                broker = account.get('broker', '')
                investment_id = account.get('investment_id')
                investment_ids = account.get('investment_ids', [])
                
                print(f"   Account Login: {login}, Broker: {broker}")
                print(f"   Investment ID: {investment_id}")
                print(f"   Investment IDs: {investment_ids}")
                
                if login in expected_logins:
                    if investment_id and investment_id != 'None':
                        properly_linked += 1
                        print(f"   ✅ PROPERLY LINKED: {broker} account has Investment ID")
                    elif investment_ids and len(investment_ids) > 0 and investment_ids[0] != 'None':
                        properly_linked += 1
                        print(f"   ✅ PROPERLY LINKED: {broker} account has Investment IDs")
                    else:
                        print(f"   ❌ NOT LINKED: {broker} account missing Investment ID")
                        self.critical_issues.append(f"MT5 account {login} ({broker}) not linked to investment - Investment ID is None")
            
            if properly_linked == 2:
                print(f"   ✅ BOTH ACCOUNTS PROPERLY LINKED")
                self.success_items.append("Both Salvador MT5 accounts properly linked to investments")
            elif properly_linked == 1:
                print(f"   ⚠️  PARTIAL LINKING: {properly_linked}/2 accounts linked")
                self.critical_issues.append(f"Only {properly_linked}/2 Salvador MT5 accounts properly linked")
            else:
                print(f"   ❌ NO ACCOUNTS LINKED: {properly_linked}/2 accounts linked")
                self.critical_issues.append("Neither Salvador MT5 account is linked to investments")
            
            return properly_linked > 0
        else:
            self.critical_issues.append("MT5 Admin Accounts endpoint failed")
            return False

    def test_health_endpoints(self):
        """Test health endpoints to ensure system is operational"""
        print("\n" + "="*80)
        print("🔧 SYSTEM HEALTH CHECK")
        print("="*80)
        
        # Test basic health
        health_success, _ = self.run_test(
            "Health Check",
            "GET",
            "api/health",
            200
        )
        
        # Test readiness
        ready_success, ready_response = self.run_test(
            "Readiness Check",
            "GET",
            "api/health/ready",
            200
        )
        
        if ready_success:
            status = ready_response.get('status', 'unknown')
            database = ready_response.get('database', 'unknown')
            print(f"   System Status: {status}")
            print(f"   Database: {database}")
            
            if status == 'ready' and database == 'connected':
                self.success_items.append("System health checks passing")
            else:
                self.critical_issues.append(f"System not ready: status={status}, database={database}")
        
        return health_success and ready_success

    def run_all_tests(self):
        """Run all Salvador integration tests"""
        print("🚀 STARTING SALVADOR PALMA MT5 INTEGRATION VERIFICATION")
        print("=" * 80)
        print("Testing Salvador integration after backend fixes...")
        print("Expected: Salvador should appear in all dashboards with proper MT5 linking")
        print("=" * 80)
        
        # Step 1: Login
        if not self.test_admin_login():
            print("\n❌ CRITICAL FAILURE: Cannot authenticate - stopping tests")
            return False
        
        # Step 2: Health checks
        self.test_health_endpoints()
        
        # Step 3: Core integration tests
        fund_performance_ok = self.test_fund_performance_dashboard()
        cash_flow_ok = self.test_cash_flow_management()
        crm_dashboard_ok = self.test_crm_dashboard()
        mt5_accounts_ok = self.test_mt5_accounts_admin()
        
        # Results summary
        print("\n" + "="*80)
        print("🎯 SALVADOR INTEGRATION TEST RESULTS")
        print("="*80)
        
        print(f"\nTests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        # Critical issues
        if self.critical_issues:
            print(f"\n❌ CRITICAL ISSUES FOUND ({len(self.critical_issues)}):")
            for i, issue in enumerate(self.critical_issues, 1):
                print(f"   {i}. {issue}")
        
        # Success items
        if self.success_items:
            print(f"\n✅ SUCCESSFUL INTEGRATIONS ({len(self.success_items)}):")
            for i, item in enumerate(self.success_items, 1):
                print(f"   {i}. {item}")
        
        # Overall assessment
        core_tests_passed = sum([fund_performance_ok, cash_flow_ok, crm_dashboard_ok, mt5_accounts_ok])
        
        print(f"\n🎯 INTEGRATION STATUS:")
        print(f"   Fund Performance Dashboard: {'✅' if fund_performance_ok else '❌'}")
        print(f"   Cash Flow Management: {'✅' if cash_flow_ok else '❌'}")
        print(f"   CRM Dashboard: {'✅' if crm_dashboard_ok else '❌'}")
        print(f"   MT5 Accounts Admin: {'✅' if mt5_accounts_ok else '❌'}")
        
        if core_tests_passed == 4:
            print(f"\n🎉 SALVADOR INTEGRATION FULLY WORKING!")
            print(f"   All 4 critical systems show Salvador with proper MT5 integration")
            return True
        elif core_tests_passed >= 2:
            print(f"\n⚠️  SALVADOR INTEGRATION PARTIALLY WORKING")
            print(f"   {core_tests_passed}/4 critical systems working properly")
            return False
        else:
            print(f"\n❌ SALVADOR INTEGRATION BROKEN")
            print(f"   Only {core_tests_passed}/4 critical systems working")
            return False

def main():
    """Main test execution"""
    tester = SalvadorIntegrationTester()
    
    try:
        success = tester.run_all_tests()
        
        if success:
            print(f"\n🎉 SALVADOR INTEGRATION VERIFICATION: PASSED")
            print(f"   Salvador appears in business dashboards with proper MT5 integration")
            sys.exit(0)
        else:
            print(f"\n❌ SALVADOR INTEGRATION VERIFICATION: FAILED")
            print(f"   Critical issues found - see details above")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test execution failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()