#!/usr/bin/env python3
"""
MT5 API Endpoints Authenticated Debug Test
Critical debugging for MT5 API endpoints with proper authentication
Focus: Salvador Palma's MT5 account should exist but frontend shows "No MT5 accounts found"
"""

import requests
import sys
import json
from datetime import datetime

class MT5AuthenticatedDebugTester:
    def __init__(self, base_url="https://mt5-portal.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.critical_issues = []
        self.debug_findings = []
        self.admin_token = None
        self.client_token = None
        
    def log_finding(self, finding):
        """Log debug finding"""
        self.debug_findings.append(finding)
        print(f"🔍 FINDING: {finding}")
        
    def log_critical_issue(self, issue):
        """Log critical issue"""
        self.critical_issues.append(issue)
        print(f"🚨 CRITICAL: {issue}")

    def authenticate_admin(self):
        """Authenticate as admin to get JWT token"""
        print("\n🔐 Authenticating as Admin...")
        
        login_data = {
            "username": "admin",
            "password": "password123", 
            "user_type": "admin"
        }
        
        try:
            url = f"{self.base_url}/api/auth/login"
            response = requests.post(url, json=login_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token')
                if self.admin_token:
                    print(f"✅ Admin authenticated successfully")
                    return True
                else:
                    print(f"❌ No token received in admin login response")
                    return False
            else:
                print(f"❌ Admin login failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Admin authentication error: {str(e)}")
            return False

    def authenticate_client(self):
        """Authenticate as Salvador (client3) to get JWT token"""
        print("\n🔐 Authenticating as Salvador (client3)...")
        
        login_data = {
            "username": "client3",
            "password": "password123",
            "user_type": "client"
        }
        
        try:
            url = f"{self.base_url}/api/auth/login"
            response = requests.post(url, json=login_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.client_token = data.get('token')
                if self.client_token:
                    print(f"✅ Salvador authenticated successfully")
                    print(f"   Client ID: {data.get('id')}")
                    print(f"   Name: {data.get('name')}")
                    return True
                else:
                    print(f"❌ No token received in client login response")
                    return False
            else:
                print(f"❌ Salvador login failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Salvador authentication error: {str(e)}")
            return False

    def run_authenticated_test(self, name, method, endpoint, expected_status=None, data=None, use_admin_auth=True):
        """Run a single API test with authentication"""
        url = f"{self.base_url}/{endpoint}"
        
        # Set up headers with authentication
        headers = {'Content-Type': 'application/json'}
        if use_admin_auth and self.admin_token:
            headers['Authorization'] = f'Bearer {self.admin_token}'
        elif not use_admin_auth and self.client_token:
            headers['Authorization'] = f'Bearer {self.client_token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        print(f"   Auth: {'Admin' if use_admin_auth else 'Client'} {'✅' if (use_admin_auth and self.admin_token) or (not use_admin_auth and self.client_token) else '❌'}")
        
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
            
            # Always try to parse response for debugging
            try:
                response_data = response.json()
                print(f"   Response Type: {type(response_data)}")
                if isinstance(response_data, dict):
                    print(f"   Response Keys: {list(response_data.keys())}")
                elif isinstance(response_data, list):
                    print(f"   Response Length: {len(response_data)}")
                    if response_data:
                        print(f"   First Item Keys: {list(response_data[0].keys()) if isinstance(response_data[0], dict) else 'Not dict'}")
                else:
                    print(f"   Response Value: {response_data}")
                    
                # Check for expected status if provided
                if expected_status is not None:
                    success = response.status_code == expected_status
                    if success:
                        self.tests_passed += 1
                        print(f"✅ Status Check Passed")
                    else:
                        print(f"❌ Status Check Failed - Expected {expected_status}, got {response.status_code}")
                else:
                    # If no expected status, consider 2xx as success
                    success = 200 <= response.status_code < 300
                    if success:
                        self.tests_passed += 1
                        print(f"✅ Request Successful")
                    else:
                        print(f"❌ Request Failed")
                        
                return success, response_data
                
            except json.JSONDecodeError:
                print(f"   Response Text: {response.text[:200]}...")
                return False, {}

        except Exception as e:
            print(f"❌ Request Failed - Error: {str(e)}")
            return False, {}

    def test_authenticated_mt5_endpoints(self):
        """Test MT5 endpoints with proper authentication"""
        print("\n" + "="*80)
        print("AUTHENTICATED MT5 API ENDPOINTS TESTING")
        print("="*80)
        
        # Test 1: GET /api/mt5/admin/accounts (with admin auth)
        print("\n🎯 TEST 1: GET /api/mt5/admin/accounts (Authenticated)")
        success1, response1 = self.run_authenticated_test(
            "MT5 Admin Accounts (Auth)",
            "GET", 
            "api/mt5/admin/accounts",
            200,
            use_admin_auth=True
        )
        
        if success1:
            # Check if response has the expected structure
            if isinstance(response1, dict):
                if 'accounts' in response1:
                    accounts = response1['accounts']
                    print(f"   📊 Found {len(accounts)} MT5 accounts")
                    
                    if len(accounts) == 0:
                        self.log_critical_issue("MT5 Admin Accounts returns EMPTY ACCOUNTS ARRAY!")
                    else:
                        print(f"   ✅ MT5 accounts exist: {len(accounts)}")
                        # Check for Salvador's account
                        salvador_accounts = []
                        for acc in accounts:
                            account_id = str(acc.get('account_id', ''))
                            client_id = str(acc.get('client_id', ''))
                            mt5_login = acc.get('mt5_login', 0)
                            
                            if ('client_003' in account_id or 'client_003' in client_id or 
                                mt5_login == 9928326 or 'SALVADOR' in str(acc.get('client_name', '')).upper()):
                                salvador_accounts.append(acc)
                                
                        if salvador_accounts:
                            print(f"   ✅ Found Salvador's accounts: {len(salvador_accounts)}")
                            for acc in salvador_accounts:
                                print(f"      - Account ID: {acc.get('account_id')}")
                                print(f"      - Client ID: {acc.get('client_id')}")
                                print(f"      - MT5 Login: {acc.get('mt5_login')}")
                                print(f"      - Fund: {acc.get('fund_code')}")
                                print(f"      - Broker: {acc.get('broker_code', 'Unknown')}")
                                print(f"      - Status: {acc.get('status', 'Unknown')}")
                        else:
                            self.log_critical_issue("Salvador Palma's MT5 account NOT FOUND in accounts list!")
                            
                            # Show what accounts do exist for debugging
                            print(f"   🔍 Existing accounts for debugging:")
                            for i, acc in enumerate(accounts[:3]):  # Show first 3 accounts
                                print(f"      Account {i+1}:")
                                print(f"        - Account ID: {acc.get('account_id')}")
                                print(f"        - Client ID: {acc.get('client_id')}")
                                print(f"        - MT5 Login: {acc.get('mt5_login')}")
                                print(f"        - Fund: {acc.get('fund_code')}")
                elif isinstance(response1, list):
                    # Direct list of accounts
                    accounts = response1
                    print(f"   📊 Found {len(accounts)} MT5 accounts (direct list)")
                    
                    if len(accounts) == 0:
                        self.log_critical_issue("MT5 Admin Accounts returns EMPTY LIST!")
                    else:
                        # Same Salvador check logic
                        salvador_accounts = []
                        for acc in accounts:
                            account_id = str(acc.get('account_id', ''))
                            client_id = str(acc.get('client_id', ''))
                            mt5_login = acc.get('mt5_login', 0)
                            
                            if ('client_003' in account_id or 'client_003' in client_id or 
                                mt5_login == 9928326):
                                salvador_accounts.append(acc)
                                
                        if salvador_accounts:
                            print(f"   ✅ Found Salvador's accounts: {len(salvador_accounts)}")
                        else:
                            self.log_critical_issue("Salvador Palma's MT5 account NOT FOUND!")
                else:
                    self.log_critical_issue(f"MT5 Admin Accounts returns unexpected structure: {response1}")
            else:
                self.log_critical_issue(f"MT5 Admin Accounts returns unexpected type: {type(response1)}")
        else:
            self.log_critical_issue("MT5 Admin Accounts endpoint FAILED even with authentication!")
            
        # Test 2: GET /api/mt5/admin/accounts/by-broker (with admin auth)
        print("\n🎯 TEST 2: GET /api/mt5/admin/accounts/by-broker (Authenticated)")
        success2, response2 = self.run_authenticated_test(
            "MT5 Accounts By Broker (Auth)",
            "GET",
            "api/mt5/admin/accounts/by-broker",
            200,
            use_admin_auth=True
        )
        
        if success2:
            if isinstance(response2, dict):
                # Check if it has broker groupings
                if 'brokers' in response2:
                    brokers_data = response2['brokers']
                elif 'accounts_by_broker' in response2:
                    brokers_data = response2['accounts_by_broker']
                else:
                    # Assume the dict itself contains broker keys
                    brokers_data = response2
                    
                brokers = list(brokers_data.keys())
                print(f"   📊 Brokers found: {brokers}")
                
                total_accounts = 0
                for broker, accounts in brokers_data.items():
                    if isinstance(accounts, list):
                        total_accounts += len(accounts)
                        print(f"   📊 {broker}: {len(accounts)} accounts")
                
                print(f"   📊 Total accounts across brokers: {total_accounts}")
                
                if total_accounts == 0:
                    self.log_critical_issue("MT5 Accounts By Broker shows NO ACCOUNTS across all brokers!")
                else:
                    # Check for DooTechnology broker (Salvador should be here)
                    doo_accounts = brokers_data.get('dootechnology', [])
                    if not doo_accounts:
                        # Try alternative keys
                        doo_accounts = brokers_data.get('DooTechnology', [])
                    if not doo_accounts:
                        doo_accounts = brokers_data.get('doo_technology', [])
                        
                    print(f"   📊 DooTechnology accounts: {len(doo_accounts)}")
                    
                    if len(doo_accounts) == 0:
                        self.log_critical_issue("NO ACCOUNTS found in DooTechnology broker - Salvador should be here!")
                        
                        # Show what brokers do have accounts
                        for broker, accounts in brokers_data.items():
                            if isinstance(accounts, list) and len(accounts) > 0:
                                print(f"   🔍 {broker} has {len(accounts)} accounts")
                    else:
                        # Look for Salvador specifically in DooTechnology
                        salvador_in_doo = []
                        for acc in doo_accounts:
                            account_id = str(acc.get('account_id', ''))
                            client_id = str(acc.get('client_id', ''))
                            mt5_login = acc.get('mt5_login', 0)
                            
                            if ('client_003' in account_id or 'client_003' in client_id or 
                                mt5_login == 9928326):
                                salvador_in_doo.append(acc)
                                
                        if salvador_in_doo:
                            print(f"   ✅ Found Salvador in DooTechnology: {len(salvador_in_doo)} accounts")
                            for acc in salvador_in_doo:
                                print(f"      - Account ID: {acc.get('account_id')}")
                                print(f"      - MT5 Login: {acc.get('mt5_login')}")
                        else:
                            self.log_critical_issue("Salvador NOT FOUND in DooTechnology accounts!")
            else:
                self.log_critical_issue(f"MT5 Accounts By Broker returns unexpected type: {type(response2)}")
        else:
            self.log_critical_issue("MT5 Accounts By Broker endpoint FAILED even with authentication!")
            
        # Test 3: GET /api/mt5/admin/performance/overview (with admin auth)
        print("\n🎯 TEST 3: GET /api/mt5/admin/performance/overview (Authenticated)")
        success3, response3 = self.run_authenticated_test(
            "MT5 Performance Overview (Auth)",
            "GET",
            "api/mt5/admin/performance/overview",
            200,
            use_admin_auth=True
        )
        
        if success3:
            if isinstance(response3, dict):
                # Check for expected performance fields
                expected_fields = ['total_clients', 'total_balance', 'total_equity']
                found_fields = []
                
                # Check both direct keys and nested structure
                for field in expected_fields:
                    if field in response3:
                        found_fields.append(field)
                    elif 'overview' in response3 and field in response3['overview']:
                        found_fields.append(field)
                        
                print(f"   📊 Performance fields found: {found_fields}")
                
                # Get values (check both direct and nested)
                if 'overview' in response3:
                    perf_data = response3['overview']
                else:
                    perf_data = response3
                    
                total_clients = perf_data.get('total_clients', 0)
                total_balance = perf_data.get('total_balance', 0)
                total_equity = perf_data.get('total_equity', 0)
                
                print(f"   📊 Performance Overview:")
                print(f"      - Total Clients: {total_clients}")
                print(f"      - Total Balance: ${total_balance:,.2f}")
                print(f"      - Total Equity: ${total_equity:,.2f}")
                
                if total_clients == 0:
                    self.log_critical_issue("Performance overview shows 0 clients - should show Salvador!")
                if total_balance == 0:
                    self.log_critical_issue("Performance overview shows $0 balance - should show Salvador's $100K!")
                    
                if total_clients > 0 and total_balance > 0:
                    print(f"   ✅ Performance overview shows active MT5 data")
            else:
                self.log_critical_issue(f"MT5 Performance Overview returns unexpected type: {type(response3)}")
        else:
            self.log_critical_issue("MT5 Performance Overview endpoint FAILED even with authentication!")
            
        return success1 or success2 or success3

    def test_salvador_specific_mt5_data(self):
        """Test Salvador-specific MT5 data"""
        print("\n" + "="*80)
        print("SALVADOR-SPECIFIC MT5 DATA VERIFICATION")
        print("="*80)
        
        # Test Salvador's client-specific MT5 accounts
        print("\n🎯 TEST 4: Salvador's Client MT5 Accounts")
        success4, response4 = self.run_authenticated_test(
            "Salvador MT5 Accounts",
            "GET",
            "api/mt5/client/client_003/accounts",
            200,
            use_admin_auth=False  # Use client auth for client endpoint
        )
        
        if success4:
            if isinstance(response4, dict):
                accounts = response4.get('accounts', [])
                total_accounts = response4.get('total_accounts', len(accounts))
                
                print(f"   📊 Salvador's MT5 accounts: {total_accounts}")
                
                if total_accounts == 0:
                    self.log_critical_issue("Salvador has NO MT5 accounts from client endpoint!")
                else:
                    print(f"   ✅ Salvador has {total_accounts} MT5 accounts")
                    for acc in accounts:
                        print(f"      - Account ID: {acc.get('account_id')}")
                        print(f"      - MT5 Login: {acc.get('mt5_login')}")
                        print(f"      - Fund: {acc.get('fund_code')}")
                        print(f"      - Allocated: ${acc.get('total_allocated', 0):,.2f}")
                        print(f"      - Status: {acc.get('status')}")
                        
                        # Check if this matches expected Salvador account
                        if acc.get('mt5_login') == 9928326:
                            print(f"      ✅ FOUND EXPECTED ACCOUNT with login 9928326!")
                        elif acc.get('fund_code') == 'BALANCE':
                            print(f"      ✅ FOUND BALANCE fund account!")
            else:
                self.log_critical_issue(f"Salvador MT5 accounts returns unexpected type: {type(response4)}")
        else:
            self.log_critical_issue("Salvador's client MT5 accounts endpoint FAILED!")
            
        # Test Salvador's investment data to verify it exists
        print("\n🎯 TEST 5: Salvador's Investment Data Verification")
        success5, response5 = self.run_authenticated_test(
            "Salvador Investment Data",
            "GET",
            "api/investments/client/client_003",
            200,
            use_admin_auth=False  # Use client auth
        )
        
        if success5:
            if isinstance(response5, dict) and 'investments' in response5:
                investments = response5['investments']
                print(f"   📊 Salvador's investments: {len(investments)}")
                
                balance_investments = [inv for inv in investments if inv.get('fund_code') == 'BALANCE']
                print(f"   📊 BALANCE fund investments: {len(balance_investments)}")
                
                if len(balance_investments) > 0:
                    balance_inv = balance_investments[0]
                    print(f"   ✅ Found BALANCE investment:")
                    print(f"      - Investment ID: {balance_inv.get('investment_id')}")
                    print(f"      - Principal: ${balance_inv.get('principal_amount', 0):,.2f}")
                    print(f"      - Current Value: ${balance_inv.get('current_value', 0):,.2f}")
                    print(f"      - Deposit Date: {balance_inv.get('deposit_date')}")
                    
                    # This investment should have triggered MT5 account creation
                    self.log_finding("Salvador has BALANCE investment - MT5 account should exist for this!")
                    
                    # Check if investment has MT5 account reference
                    if 'mt5_account_id' in balance_inv:
                        mt5_account_id = balance_inv.get('mt5_account_id')
                        print(f"      - MT5 Account ID: {mt5_account_id}")
                        if mt5_account_id:
                            print(f"      ✅ Investment has MT5 account reference!")
                        else:
                            self.log_critical_issue("Investment has empty MT5 account reference!")
                    else:
                        self.log_finding("Investment does not have MT5 account reference field")
                else:
                    self.log_critical_issue("Salvador has no BALANCE investments - this is the root problem!")
            else:
                self.log_critical_issue("Salvador investment endpoint returns unexpected format!")
        else:
            self.log_critical_issue("Cannot retrieve Salvador's investment data!")
            
        return success4 and success5

    def test_manual_mt5_account_creation(self):
        """Test manual MT5 account creation for Salvador"""
        print("\n" + "="*80)
        print("MANUAL MT5 ACCOUNT CREATION TEST")
        print("="*80)
        
        # Test manual account creation endpoint
        print("\n🎯 TEST 6: Manual MT5 Account Creation for Salvador")
        
        # Create the exact account that should exist for Salvador
        test_account_data = {
            "client_id": "client_003",
            "fund_code": "BALANCE", 
            "mt5_login": 9928326,
            "mt5_password": "TestPassword123",
            "mt5_server": "DooTechnology-Live",
            "broker_code": "dootechnology"
        }
        
        success6, response6 = self.run_authenticated_test(
            "Manual MT5 Account Creation",
            "POST",
            "api/mt5/admin/add-manual-account",
            None,  # Don't expect specific status, just see what happens
            data=test_account_data,
            use_admin_auth=True
        )
        
        if success6:
            print(f"   ✅ Manual account creation endpoint working")
            if isinstance(response6, dict):
                account_id = response6.get('account_id')
                success_flag = response6.get('success', False)
                message = response6.get('message', '')
                
                print(f"   📊 Creation result:")
                print(f"      - Success: {success_flag}")
                print(f"      - Account ID: {account_id}")
                print(f"      - Message: {message}")
                
                if success_flag and account_id:
                    self.log_finding("Manual account creation successful - Salvador's MT5 account created!")
                    
                    # Now test if the account appears in the admin accounts list
                    print(f"\n   🔍 Verifying account appears in admin list...")
                    verify_success, verify_response = self.run_authenticated_test(
                        "Verify Created Account",
                        "GET",
                        "api/mt5/admin/accounts",
                        200,
                        use_admin_auth=True
                    )
                    
                    if verify_success:
                        # Look for the newly created account
                        accounts = []
                        if isinstance(verify_response, dict) and 'accounts' in verify_response:
                            accounts = verify_response['accounts']
                        elif isinstance(verify_response, list):
                            accounts = verify_response
                            
                        found_new_account = False
                        for acc in accounts:
                            if (acc.get('account_id') == account_id or 
                                acc.get('mt5_login') == 9928326):
                                found_new_account = True
                                print(f"      ✅ Created account found in admin list!")
                                print(f"         - Account ID: {acc.get('account_id')}")
                                print(f"         - MT5 Login: {acc.get('mt5_login')}")
                                break
                                
                        if not found_new_account:
                            self.log_critical_issue("Created account NOT FOUND in admin accounts list!")
                    else:
                        self.log_finding("Could not verify created account in admin list")
                else:
                    self.log_critical_issue(f"Manual account creation failed: {message}")
        else:
            self.log_critical_issue("Manual MT5 account creation FAILED even with authentication!")
            
        return success6

    def run_comprehensive_authenticated_debug(self):
        """Run comprehensive MT5 debugging with authentication"""
        print("🚀 STARTING COMPREHENSIVE AUTHENTICATED MT5 API DEBUG")
        print("="*80)
        print("GOAL: Find why MT5 API endpoints return empty results when Salvador's account should exist")
        print("Expected: Salvador Palma (client_003) should have MT5 account with login 9928326")
        print("="*80)
        
        # First authenticate
        admin_auth_success = self.authenticate_admin()
        client_auth_success = self.authenticate_client()
        
        if not admin_auth_success:
            print("❌ Cannot proceed without admin authentication")
            return False
            
        if not client_auth_success:
            print("⚠️  Client authentication failed, some tests may not work")
        
        # Run authenticated tests
        mt5_endpoints_success = self.test_authenticated_mt5_endpoints()
        salvador_data_success = self.test_salvador_specific_mt5_data()
        manual_creation_success = self.test_manual_mt5_account_creation()
        
        # Generate comprehensive report
        print("\n" + "="*80)
        print("🎯 COMPREHENSIVE AUTHENTICATED DEBUG REPORT")
        print("="*80)
        
        print(f"\n📊 TEST STATISTICS:")
        print(f"   Total Tests Run: {self.tests_run}")
        print(f"   Tests Passed: {self.tests_passed}")
        print(f"   Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        print(f"\n🚨 CRITICAL ISSUES FOUND ({len(self.critical_issues)}):")
        for i, issue in enumerate(self.critical_issues, 1):
            print(f"   {i}. {issue}")
            
        print(f"\n🔍 DEBUG FINDINGS ({len(self.debug_findings)}):")
        for i, finding in enumerate(self.debug_findings, 1):
            print(f"   {i}. {finding}")
            
        # Root cause analysis
        print(f"\n🎯 ROOT CAUSE ANALYSIS:")
        if len(self.critical_issues) == 0:
            print("   ✅ No critical issues found - MT5 system appears to be working correctly")
        else:
            print("   ❌ Critical issues detected in MT5 system:")
            
            # Analyze patterns in critical issues
            empty_account_issues = [issue for issue in self.critical_issues if 'EMPTY' in issue or 'NO ACCOUNTS' in issue or '0 clients' in issue]
            salvador_missing_issues = [issue for issue in self.critical_issues if 'Salvador' in issue or 'SALVADOR' in issue]
            endpoint_failure_issues = [issue for issue in self.critical_issues if 'FAILED' in issue]
            
            if empty_account_issues:
                print("   🔍 PATTERN: MT5 endpoints returning empty data")
                print("   💡 LIKELY CAUSE: MT5 accounts not being created during investment process")
                
            if salvador_missing_issues:
                print("   🔍 PATTERN: Salvador's MT5 account missing")
                print("   💡 LIKELY CAUSE: Investment-to-MT5 account creation process broken")
                
            if endpoint_failure_issues:
                print("   🔍 PATTERN: MT5 endpoints failing")
                print("   💡 LIKELY CAUSE: Authentication or backend service issues")
                
        # Specific recommendations based on findings
        print(f"\n💡 SPECIFIC RECOMMENDATIONS:")
        
        if any('EMPTY' in issue for issue in self.critical_issues):
            print("   1. MT5 account creation process is not working during investment creation")
            print("   2. Check if investment creation triggers MT5 account creation properly")
            
        if any('Salvador' in issue for issue in self.critical_issues):
            print("   3. Salvador's BALANCE investment exists but no MT5 account was created")
            print("   4. Use manual MT5 account creation to fix Salvador's missing account")
            
        if manual_creation_success:
            print("   5. ✅ Manual account creation works - use this to create missing accounts")
        else:
            print("   5. ❌ Manual account creation failed - fix this endpoint first")
            
        print(f"\n🎯 IMMEDIATE ACTION ITEMS:")
        print("   1. Fix MT5 account creation during investment process")
        print("   2. Create Salvador's missing MT5 account manually")
        print("   3. Verify frontend can display MT5 accounts after backend fixes")
        print("   4. Test complete investment → MT5 account creation flow")
        
        return {
            'tests_run': self.tests_run,
            'tests_passed': self.tests_passed,
            'critical_issues': self.critical_issues,
            'debug_findings': self.debug_findings,
            'success_rate': (self.tests_passed/self.tests_run*100) if self.tests_run > 0 else 0,
            'authentication_success': admin_auth_success and client_auth_success
        }

def main():
    """Main function to run authenticated MT5 debug tests"""
    print("🔧 MT5 API ENDPOINTS AUTHENTICATED DEBUG TEST")
    print("Debugging: Frontend shows 'No MT5 accounts found' despite Salvador's account creation")
    print("="*80)
    
    tester = MT5AuthenticatedDebugTester()
    
    try:
        results = tester.run_comprehensive_authenticated_debug()
        
        # Exit with appropriate code
        if len(tester.critical_issues) == 0:
            print("\n✅ MT5 AUTHENTICATED DEBUG COMPLETED - No critical issues found")
            sys.exit(0)
        else:
            print(f"\n❌ MT5 AUTHENTICATED DEBUG COMPLETED - {len(tester.critical_issues)} critical issues found")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  Debug test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Debug test failed with error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()