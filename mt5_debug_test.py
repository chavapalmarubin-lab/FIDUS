#!/usr/bin/env python3
"""
MT5 API Endpoints Debug Test
Critical debugging for MT5 API endpoints not returning data
Focus: Salvador Palma's MT5 account should exist but frontend shows "No MT5 accounts found"
"""

import requests
import sys
import json
from datetime import datetime

class MT5DebugTester:
    def __init__(self, base_url="https://fidus-google-sync.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.critical_issues = []
        self.debug_findings = []
        
    def log_finding(self, finding):
        """Log debug finding"""
        self.debug_findings.append(finding)
        print(f"🔍 FINDING: {finding}")
        
    def log_critical_issue(self, issue):
        """Log critical issue"""
        self.critical_issues.append(issue)
        print(f"🚨 CRITICAL: {issue}")

    def run_test(self, name, method, endpoint, expected_status=None, data=None, headers=None):
        """Run a single API test with detailed debugging"""
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

    def test_priority_1_core_mt5_endpoints(self):
        """Priority 1: Debug Core MT5 API Endpoints"""
        print("\n" + "="*80)
        print("PRIORITY 1: DEBUGGING CORE MT5 API ENDPOINTS")
        print("="*80)
        
        # Test 1: GET /api/mt5/admin/accounts
        print("\n🎯 TEST 1: GET /api/mt5/admin/accounts")
        success1, response1 = self.run_test(
            "MT5 Admin Accounts",
            "GET", 
            "api/mt5/admin/accounts",
            200
        )
        
        if success1:
            if isinstance(response1, list):
                account_count = len(response1)
                print(f"   📊 Found {account_count} MT5 accounts")
                
                if account_count == 0:
                    self.log_critical_issue("MT5 Admin Accounts endpoint returns EMPTY ARRAY - No accounts found!")
                else:
                    print(f"   ✅ MT5 accounts exist: {account_count}")
                    # Check for Salvador's account
                    salvador_accounts = [acc for acc in response1 if 'client_003' in str(acc.get('account_id', '')) or 'SALVADOR' in str(acc.get('client_name', '')).upper()]
                    if salvador_accounts:
                        print(f"   ✅ Found Salvador's accounts: {len(salvador_accounts)}")
                        for acc in salvador_accounts:
                            print(f"      - Account ID: {acc.get('account_id')}")
                            print(f"      - MT5 Login: {acc.get('mt5_login')}")
                            print(f"      - Fund: {acc.get('fund_code')}")
                    else:
                        self.log_critical_issue("Salvador Palma's MT5 account NOT FOUND in accounts list!")
            else:
                self.log_critical_issue(f"MT5 Admin Accounts returns unexpected type: {type(response1)}")
        else:
            self.log_critical_issue("MT5 Admin Accounts endpoint FAILED to respond!")
            
        # Test 2: GET /api/mt5/admin/accounts/by-broker
        print("\n🎯 TEST 2: GET /api/mt5/admin/accounts/by-broker")
        success2, response2 = self.run_test(
            "MT5 Accounts By Broker",
            "GET",
            "api/mt5/admin/accounts/by-broker",
            200
        )
        
        if success2:
            if isinstance(response2, dict):
                brokers = list(response2.keys())
                print(f"   📊 Brokers found: {brokers}")
                
                total_accounts = sum(len(accounts) for accounts in response2.values())
                print(f"   📊 Total accounts across brokers: {total_accounts}")
                
                if total_accounts == 0:
                    self.log_critical_issue("MT5 Accounts By Broker shows NO ACCOUNTS across all brokers!")
                else:
                    # Check for DooTechnology broker (Salvador should be here)
                    doo_accounts = response2.get('dootechnology', [])
                    print(f"   📊 DooTechnology accounts: {len(doo_accounts)}")
                    
                    if len(doo_accounts) == 0:
                        self.log_critical_issue("NO ACCOUNTS found in DooTechnology broker - Salvador should be here!")
                    else:
                        # Look for Salvador specifically
                        salvador_in_doo = [acc for acc in doo_accounts if 'client_003' in str(acc.get('account_id', '')) or acc.get('mt5_login') == 9928326]
                        if salvador_in_doo:
                            print(f"   ✅ Found Salvador in DooTechnology: {len(salvador_in_doo)} accounts")
                        else:
                            self.log_critical_issue("Salvador NOT FOUND in DooTechnology accounts!")
            else:
                self.log_critical_issue(f"MT5 Accounts By Broker returns unexpected type: {type(response2)}")
        else:
            self.log_critical_issue("MT5 Accounts By Broker endpoint FAILED!")
            
        # Test 3: GET /api/mt5/admin/performance/overview
        print("\n🎯 TEST 3: GET /api/mt5/admin/performance/overview")
        success3, response3 = self.run_test(
            "MT5 Performance Overview",
            "GET",
            "api/mt5/admin/performance/overview",
            200
        )
        
        if success3:
            if isinstance(response3, dict):
                # Check for expected performance fields
                expected_fields = ['total_clients', 'total_balance', 'total_equity', 'total_positions']
                missing_fields = [field for field in expected_fields if field not in response3]
                
                if missing_fields:
                    self.log_finding(f"Performance overview missing fields: {missing_fields}")
                else:
                    print(f"   ✅ All expected performance fields present")
                    
                # Check values
                total_clients = response3.get('total_clients', 0)
                total_balance = response3.get('total_balance', 0)
                
                print(f"   📊 Performance Overview:")
                print(f"      - Total Clients: {total_clients}")
                print(f"      - Total Balance: ${total_balance:,.2f}")
                
                if total_clients == 0:
                    self.log_critical_issue("Performance overview shows 0 clients - should show Salvador!")
                if total_balance == 0:
                    self.log_critical_issue("Performance overview shows $0 balance - should show Salvador's $100K!")
            else:
                self.log_critical_issue(f"MT5 Performance Overview returns unexpected type: {type(response3)}")
        else:
            self.log_critical_issue("MT5 Performance Overview endpoint FAILED!")
            
        return success1 and success2 and success3

    def test_priority_2_database_verification(self):
        """Priority 2: Check Database Directly"""
        print("\n" + "="*80)
        print("PRIORITY 2: DATABASE VERIFICATION")
        print("="*80)
        
        # Test Salvador's investment data first
        print("\n🎯 TEST 4: Verify Salvador's Investment Data")
        success4, response4 = self.run_test(
            "Salvador Investment Data",
            "GET",
            "api/investments/client/client_003",
            200
        )
        
        if success4:
            if isinstance(response4, dict) and 'investments' in response4:
                investments = response4['investments']
                print(f"   📊 Salvador's investments: {len(investments)}")
                
                if len(investments) == 0:
                    self.log_critical_issue("Salvador has NO INVESTMENTS - this is the root problem!")
                    return False
                else:
                    balance_investments = [inv for inv in investments if inv.get('fund_code') == 'BALANCE']
                    print(f"   📊 BALANCE fund investments: {len(balance_investments)}")
                    
                    if len(balance_investments) == 0:
                        self.log_critical_issue("Salvador has no BALANCE investments - MT5 account should be linked to BALANCE!")
                    else:
                        balance_inv = balance_investments[0]
                        print(f"   ✅ Found BALANCE investment:")
                        print(f"      - Investment ID: {balance_inv.get('investment_id')}")
                        print(f"      - Principal: ${balance_inv.get('principal_amount', 0):,.2f}")
                        print(f"      - Current Value: ${balance_inv.get('current_value', 0):,.2f}")
                        print(f"      - Deposit Date: {balance_inv.get('deposit_date')}")
                        
                        # This investment should have triggered MT5 account creation
                        self.log_finding(f"Salvador has BALANCE investment - MT5 account should exist for this!")
            else:
                self.log_critical_issue("Salvador investment endpoint returns unexpected format!")
        else:
            self.log_critical_issue("Cannot retrieve Salvador's investment data!")
            
        # Test client data verification
        print("\n🎯 TEST 5: Verify Salvador Client Data")
        success5, response5 = self.run_test(
            "Salvador Client Data",
            "GET",
            "api/clients/all",
            200
        )
        
        if success5:
            if isinstance(response5, dict) and 'clients' in response5:
                clients = response5['clients']
                salvador_clients = [c for c in clients if 'SALVADOR' in c.get('name', '').upper() or c.get('id') == 'client_003']
                
                if len(salvador_clients) == 0:
                    self.log_critical_issue("Salvador Palma NOT FOUND in clients list!")
                else:
                    salvador = salvador_clients[0]
                    print(f"   ✅ Found Salvador Palma:")
                    print(f"      - Client ID: {salvador.get('id')}")
                    print(f"      - Name: {salvador.get('name')}")
                    print(f"      - Email: {salvador.get('email')}")
            else:
                self.log_critical_issue("Clients endpoint returns unexpected format!")
        else:
            self.log_critical_issue("Cannot retrieve clients data!")
            
        return success4 and success5

    def test_priority_3_api_response_structure(self):
        """Priority 3: Debug API Response Structure"""
        print("\n" + "="*80)
        print("PRIORITY 3: API RESPONSE STRUCTURE ANALYSIS")
        print("="*80)
        
        # Test MT5 brokers endpoint
        print("\n🎯 TEST 6: MT5 Brokers Configuration")
        success6, response6 = self.run_test(
            "MT5 Brokers",
            "GET",
            "api/mt5/brokers",
            200
        )
        
        if success6:
            if isinstance(response6, list):
                print(f"   📊 Available brokers: {len(response6)}")
                for broker in response6:
                    print(f"      - {broker.get('code', 'Unknown')}: {broker.get('name', 'Unknown')}")
                    
                # Check for DooTechnology
                doo_brokers = [b for b in response6 if b.get('code') == 'dootechnology']
                if doo_brokers:
                    print(f"   ✅ DooTechnology broker configured")
                else:
                    self.log_critical_issue("DooTechnology broker NOT CONFIGURED!")
            else:
                self.log_critical_issue(f"MT5 Brokers returns unexpected type: {type(response6)}")
        else:
            self.log_critical_issue("MT5 Brokers endpoint FAILED!")
            
        # Test DooTechnology servers
        print("\n🎯 TEST 7: DooTechnology Servers")
        success7, response7 = self.run_test(
            "DooTechnology Servers",
            "GET",
            "api/mt5/brokers/dootechnology/servers",
            200
        )
        
        if success7:
            if isinstance(response7, list):
                print(f"   📊 DooTechnology servers: {len(response7)}")
                for server in response7:
                    print(f"      - {server.get('name', 'Unknown')}")
                    
                # Check for DooTechnology-Live
                live_servers = [s for s in response7 if 'Live' in s.get('name', '')]
                if live_servers:
                    print(f"   ✅ DooTechnology-Live server available")
                else:
                    self.log_finding("DooTechnology-Live server not found in list")
            else:
                self.log_critical_issue(f"DooTechnology servers returns unexpected type: {type(response7)}")
        else:
            self.log_critical_issue("DooTechnology servers endpoint FAILED!")
            
        # Test authentication headers (if needed)
        print("\n🎯 TEST 8: Authentication Check")
        # Try with admin authentication if available
        auth_headers = {'Content-Type': 'application/json'}
        
        success8, response8 = self.run_test(
            "MT5 Admin Accounts (Auth Check)",
            "GET",
            "api/mt5/admin/accounts",
            None,  # Don't check status, just see what happens
            headers=auth_headers
        )
        
        if not success8:
            self.log_finding("MT5 endpoints may require authentication - checking auth flow")
            
        return success6 and success7

    def test_priority_4_alternative_endpoints(self):
        """Priority 4: Test Alternative Endpoints"""
        print("\n" + "="*80)
        print("PRIORITY 4: ALTERNATIVE ENDPOINTS TESTING")
        print("="*80)
        
        # Test manual account creation endpoint
        print("\n🎯 TEST 9: Manual MT5 Account Creation Endpoint")
        test_account_data = {
            "client_id": "client_003",
            "fund_code": "BALANCE", 
            "mt5_login": 9928326,
            "mt5_password": "TestPassword123",
            "mt5_server": "DooTechnology-Live",
            "broker_code": "dootechnology"
        }
        
        success9, response9 = self.run_test(
            "Manual MT5 Account Creation",
            "POST",
            "api/mt5/admin/add-manual-account",
            None,  # Don't expect specific status, just see what happens
            data=test_account_data
        )
        
        if success9:
            print(f"   ✅ Manual account creation endpoint working")
            if isinstance(response9, dict):
                account_id = response9.get('account_id')
                if account_id:
                    print(f"   📊 Created account ID: {account_id}")
                    self.log_finding("Manual account creation successful - this might fix the issue!")
        else:
            self.log_critical_issue("Manual MT5 account creation FAILED - this is needed to create Salvador's account!")
            
        # Test investment-MT5 linking
        print("\n🎯 TEST 10: Investment-MT5 Account Linking")
        success10, response10 = self.run_test(
            "Investment MT5 Accounts",
            "GET",
            "api/investments/client/client_003/mt5-accounts",
            None  # This endpoint might not exist, just testing
        )
        
        if not success10:
            self.log_finding("Investment-MT5 linking endpoint may not exist or may be broken")
            
        # Test MT5 account by client
        print("\n🎯 TEST 11: MT5 Accounts by Client")
        success11, response11 = self.run_test(
            "MT5 Accounts for Salvador",
            "GET",
            "api/mt5/client/client_003/accounts",
            None  # This endpoint might not exist
        )
        
        if success11:
            print(f"   ✅ Client-specific MT5 accounts endpoint working")
            if isinstance(response11, list):
                print(f"   📊 Salvador's MT5 accounts: {len(response11)}")
        else:
            self.log_finding("Client-specific MT5 accounts endpoint may not exist")
            
        return True  # Always return True for alternative tests

    def test_comprehensive_system_state(self):
        """Comprehensive system state check"""
        print("\n" + "="*80)
        print("COMPREHENSIVE SYSTEM STATE CHECK")
        print("="*80)
        
        # Check admin portfolio to see if Salvador's investment is reflected
        print("\n🎯 TEST 12: Admin Portfolio Summary")
        success12, response12 = self.run_test(
            "Admin Portfolio Summary",
            "GET",
            "api/admin/portfolio-summary",
            200
        )
        
        if success12:
            total_aum = response12.get('aum', 0)
            print(f"   📊 Total AUM: ${total_aum:,.2f}")
            
            if total_aum >= 100000:  # Salvador's $100K should be included
                print(f"   ✅ AUM includes Salvador's investment")
            else:
                self.log_critical_issue(f"AUM too low - Salvador's $100K may not be included!")
                
            allocation = response12.get('allocation', {})
            balance_allocation = allocation.get('BALANCE', 0)
            print(f"   📊 BALANCE fund allocation: {balance_allocation}%")
            
            if balance_allocation > 0:
                print(f"   ✅ BALANCE fund has allocation")
            else:
                self.log_critical_issue("BALANCE fund shows 0% allocation - Salvador's investment missing!")
        
        # Check funds overview
        print("\n🎯 TEST 13: Admin Funds Overview")
        success13, response13 = self.run_test(
            "Admin Funds Overview",
            "GET",
            "api/admin/funds-overview",
            200
        )
        
        if success13:
            if isinstance(response13, dict) and 'funds' in response13:
                funds = response13['funds']
                balance_funds = [f for f in funds if f.get('fund_code') == 'BALANCE']
                
                if balance_funds:
                    balance_fund = balance_funds[0]
                    balance_aum = balance_fund.get('aum', 0)
                    balance_investors = balance_fund.get('total_investors', 0)
                    
                    print(f"   📊 BALANCE Fund:")
                    print(f"      - AUM: ${balance_aum:,.2f}")
                    print(f"      - Investors: {balance_investors}")
                    
                    if balance_aum >= 100000:
                        print(f"   ✅ BALANCE fund AUM includes Salvador's investment")
                    else:
                        self.log_critical_issue("BALANCE fund AUM too low - Salvador's investment missing!")
                        
                    if balance_investors >= 1:
                        print(f"   ✅ BALANCE fund has investors")
                    else:
                        self.log_critical_issue("BALANCE fund shows 0 investors - Salvador missing!")
                else:
                    self.log_critical_issue("BALANCE fund not found in funds overview!")
        
        return success12 and success13

    def run_comprehensive_mt5_debug(self):
        """Run comprehensive MT5 debugging"""
        print("🚀 STARTING COMPREHENSIVE MT5 API DEBUG")
        print("="*80)
        print("GOAL: Find why MT5 API endpoints return empty results when Salvador's account should exist")
        print("Expected: Salvador Palma (client_003) should have MT5 account with login 9928326")
        print("="*80)
        
        # Run all priority tests
        priority1_success = self.test_priority_1_core_mt5_endpoints()
        priority2_success = self.test_priority_2_database_verification()
        priority3_success = self.test_priority_3_api_response_structure()
        priority4_success = self.test_priority_4_alternative_endpoints()
        system_check_success = self.test_comprehensive_system_state()
        
        # Generate comprehensive report
        print("\n" + "="*80)
        print("🎯 COMPREHENSIVE DEBUG REPORT")
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
            endpoint_failure_issues = [issue for issue in self.critical_issues if 'FAILED' in issue or 'endpoint' in issue]
            
            if empty_account_issues:
                print("   🔍 PATTERN: MT5 endpoints returning empty data")
                print("   💡 LIKELY CAUSE: MT5 accounts not being created or stored properly")
                
            if salvador_missing_issues:
                print("   🔍 PATTERN: Salvador's data missing from MT5 system")
                print("   💡 LIKELY CAUSE: Investment-to-MT5 account mapping broken")
                
            if endpoint_failure_issues:
                print("   🔍 PATTERN: MT5 endpoints failing")
                print("   💡 LIKELY CAUSE: Backend MT5 integration service issues")
                
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if 'MT5 Admin Accounts endpoint returns EMPTY ARRAY' in self.critical_issues:
            print("   1. Check MT5 account creation process during investment creation")
            print("   2. Verify MongoDB MT5 accounts collection has data")
            print("   3. Test manual MT5 account creation endpoint")
            
        if any('Salvador' in issue for issue in self.critical_issues):
            print("   4. Manually create Salvador's MT5 account using /api/mt5/admin/add-manual-account")
            print("   5. Verify Salvador's investment exists and is properly linked")
            
        if any('FAILED' in issue for issue in self.critical_issues):
            print("   6. Check backend MT5 integration service status")
            print("   7. Verify MT5 broker configurations")
            
        print(f"\n🎯 NEXT STEPS:")
        print("   1. Fix critical issues identified above")
        print("   2. Re-run this debug test to verify fixes")
        print("   3. Test frontend MT5 account display after backend fixes")
        
        return {
            'tests_run': self.tests_run,
            'tests_passed': self.tests_passed,
            'critical_issues': self.critical_issues,
            'debug_findings': self.debug_findings,
            'success_rate': (self.tests_passed/self.tests_run*100) if self.tests_run > 0 else 0
        }

def main():
    """Main function to run MT5 debug tests"""
    print("🔧 MT5 API ENDPOINTS DEBUG TEST")
    print("Debugging: Frontend shows 'No MT5 accounts found' despite Salvador's account creation")
    print("="*80)
    
    tester = MT5DebugTester()
    
    try:
        results = tester.run_comprehensive_mt5_debug()
        
        # Exit with appropriate code
        if len(tester.critical_issues) == 0:
            print("\n✅ MT5 DEBUG COMPLETED - No critical issues found")
            sys.exit(0)
        else:
            print(f"\n❌ MT5 DEBUG COMPLETED - {len(tester.critical_issues)} critical issues found")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  Debug test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Debug test failed with error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()