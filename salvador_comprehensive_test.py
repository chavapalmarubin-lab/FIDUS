#!/usr/bin/env python3
"""
COMPREHENSIVE BACKEND TESTING FOR SALVADOR PALMA VT MARKETS MT5 INVESTIGATION
============================================================================

This test investigates and validates Salvador Palma's MT5 account structure
based on the critical user report:

USER REPORT:
- ✅ DooTechnology account (Login: 9928326) - RESTORED  
- ❌ VT Markets account - MISSING

INVESTIGATION OBJECTIVES:
1. Check Salvador's complete MT5 account history
2. Investigate the original investment structure  
3. Restore the missing VT Markets MT5 account
4. Test MT5 accounts display
5. Validate fund performance calculations include both accounts
"""

import requests
import sys
from datetime import datetime
import json

class ComprehensiveBackendTester:
    def __init__(self, base_url="https://mockdb-cleanup.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.admin_user = None
        self.client_user = None
        
        # Salvador Palma specific data
        self.salvador_client_id = "client_003"
        self.salvador_email = "salvador.palma@fidus.com"
        self.salvador_name = "Salvador Palma"
        
        # Investigation results
        self.salvador_data = {}
        self.mt5_investigation_results = {}
        self.critical_issues = []
        self.test_results = {}

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None, use_auth=True):
        """Run a single API test with proper authentication"""
        url = f"{self.base_url}/{endpoint}"
        if headers is None:
            headers = {'Content-Type': 'application/json'}
            
        # Add JWT token for authenticated requests
        if use_auth and self.admin_user and 'token' in self.admin_user:
            headers['Authorization'] = f"Bearer {self.admin_user['token']}"

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

    def test_authentication(self):
        """Test admin and client authentication"""
        print(f"\n" + "="*60)
        print(f"🔐 AUTHENTICATION TESTING")
        print(f"="*60)
        
        # Test admin login
        success, response = self.run_test(
            "Admin Login",
            "POST",
            "api/auth/login",
            200,
            data={
                "username": "admin", 
                "password": "password123",
                "user_type": "admin"
            },
            use_auth=False
        )
        
        if success:
            self.admin_user = response
            print(f"   ✅ Admin logged in: {response.get('name', 'Unknown')}")
            print(f"   Admin ID: {response.get('id', 'Unknown')}")
            print(f"   Token: {response.get('token', 'No token')[:20]}...")
        else:
            self.critical_issues.append("Admin authentication failed")
            return False
            
        # Test client login (Salvador)
        success, response = self.run_test(
            "Salvador Client Login",
            "POST", 
            "api/auth/login",
            200,
            data={
                "username": "client3",
                "password": "password123", 
                "user_type": "client"
            },
            use_auth=False
        )
        
        if success:
            self.client_user = response
            print(f"   ✅ Salvador logged in: {response.get('name', 'Unknown')}")
            print(f"   Client ID: {response.get('id', 'Unknown')}")
        else:
            print(f"   ⚠️  Salvador client login failed - may not be critical")
            
        return True

    def test_salvador_client_profile(self):
        """Test Salvador's client profile and data integrity"""
        print(f"\n" + "="*60)
        print(f"👤 SALVADOR PALMA CLIENT PROFILE TESTING")
        print(f"="*60)
        
        # Get all clients to find Salvador
        success, response = self.run_test(
            "Get All Clients (Find Salvador)",
            "GET",
            "api/clients/all",
            200
        )
        
        if success:
            clients = response.get('clients', [])
            salvador_found = False
            
            for client in clients:
                if client.get('id') == self.salvador_client_id:
                    salvador_found = True
                    self.salvador_data['profile'] = client
                    print(f"   ✅ SALVADOR FOUND:")
                    print(f"      Client ID: {client.get('id')}")
                    print(f"      Name: {client.get('name')}")
                    print(f"      Email: {client.get('email')}")
                    print(f"      Status: {client.get('status', 'Unknown')}")
                    break
                    
            if not salvador_found:
                self.critical_issues.append("Salvador Palma not found in client list")
                return False
        else:
            self.critical_issues.append("Cannot retrieve client list")
            return False
            
        # Get Salvador's detailed client data
        success, response = self.run_test(
            "Get Salvador's Client Data",
            "GET",
            f"api/client/{self.salvador_client_id}/data",
            200
        )
        
        if success:
            self.salvador_data['client_data'] = response
            balance = response.get('balance', {})
            print(f"   💰 SALVADOR'S BALANCE SUMMARY:")
            print(f"      Total Balance: ${balance.get('total_balance', 0):,.2f}")
            print(f"      Core Balance: ${balance.get('core_balance', 0):,.2f}")
            print(f"      Balance Fund: ${balance.get('balance_balance', 0):,.2f}")
            print(f"      Dynamic Balance: ${balance.get('dynamic_balance', 0):,.2f}")
            print(f"      FIDUS Funds: ${balance.get('fidus_funds', 0):,.2f}")
            
        return True

    def test_salvador_investments(self):
        """Test Salvador's investment portfolio"""
        print(f"\n" + "="*60)
        print(f"💰 SALVADOR'S INVESTMENT PORTFOLIO TESTING")
        print(f"="*60)
        
        # Get Salvador's investment portfolio
        success, response = self.run_test(
            "Get Salvador's Investment Portfolio",
            "GET",
            f"api/investments/client/{self.salvador_client_id}",
            200
        )
        
        if success:
            investments = response.get('investments', [])
            portfolio_stats = response.get('portfolio_stats', {})
            
            self.salvador_data['investments'] = investments
            self.salvador_data['portfolio_stats'] = portfolio_stats
            
            print(f"   📊 INVESTMENT PORTFOLIO SUMMARY:")
            print(f"      Total Investments: {len(investments)}")
            print(f"      Total Principal: ${portfolio_stats.get('total_principal', 0):,.2f}")
            print(f"      Total Current Value: ${portfolio_stats.get('total_current_value', 0):,.2f}")
            print(f"      Total Interest Earned: ${portfolio_stats.get('total_interest_earned', 0):,.2f}")
            
            # Analyze investment structure
            fund_breakdown = {}
            for investment in investments:
                fund_code = investment.get('fund_code')
                principal = investment.get('principal_amount', 0)
                
                if fund_code not in fund_breakdown:
                    fund_breakdown[fund_code] = {'count': 0, 'total_principal': 0}
                    
                fund_breakdown[fund_code]['count'] += 1
                fund_breakdown[fund_code]['total_principal'] += principal
                
            print(f"\n   📋 FUND BREAKDOWN:")
            for fund_code, data in fund_breakdown.items():
                print(f"      {fund_code}: {data['count']} investments, ${data['total_principal']:,.2f}")
                
            # Check for the main BALANCE fund investment (should be $1,263,485.40)
            main_balance_found = False
            for investment in investments:
                if (investment.get('fund_code') == 'BALANCE' and 
                    investment.get('principal_amount') == 1263485.40):
                    main_balance_found = True
                    print(f"   ✅ MAIN BALANCE INVESTMENT FOUND:")
                    print(f"      Investment ID: {investment.get('investment_id')}")
                    print(f"      Principal: ${investment.get('principal_amount'):,.2f}")
                    print(f"      Status: {investment.get('status')}")
                    break
                    
            if not main_balance_found:
                self.critical_issues.append("Main BALANCE fund investment ($1,263,485.40) not found")
                
        else:
            self.critical_issues.append("Cannot retrieve Salvador's investment portfolio")
            return False
            
        return True

    def test_mt5_account_structure(self):
        """Test Salvador's MT5 account structure - CRITICAL FOR VT MARKETS INVESTIGATION"""
        print(f"\n" + "="*60)
        print(f"🏦 MT5 ACCOUNT STRUCTURE INVESTIGATION")
        print(f"="*60)
        
        # Get all MT5 accounts (admin view)
        success, response = self.run_test(
            "Get All MT5 Accounts (Admin View)",
            "GET",
            "api/mt5/admin/accounts",
            200
        )
        
        if success:
            all_mt5_accounts = response.get('accounts', [])
            
            # Filter Salvador's MT5 accounts
            salvador_mt5_accounts = [
                acc for acc in all_mt5_accounts 
                if acc.get('client_id') == self.salvador_client_id
            ]
            
            self.salvador_data['mt5_accounts'] = salvador_mt5_accounts
            
            print(f"   📊 MT5 ACCOUNTS OVERVIEW:")
            print(f"      Total System MT5 Accounts: {len(all_mt5_accounts)}")
            print(f"      Salvador's MT5 Accounts: {len(salvador_mt5_accounts)}")
            
            if salvador_mt5_accounts:
                print(f"\n   📋 SALVADOR'S MT5 ACCOUNT DETAILS:")
                
                doo_technology_accounts = []
                vt_markets_accounts = []
                other_accounts = []
                
                for i, account in enumerate(salvador_mt5_accounts, 1):
                    broker_name = account.get('broker_name', '').lower()
                    mt5_login = account.get('mt5_login', '')
                    
                    print(f"      MT5 Account {i}:")
                    print(f"         Account ID: {account.get('account_id')}")
                    print(f"         MT5 Login: {mt5_login}")
                    print(f"         Broker: {account.get('broker_name')}")
                    print(f"         Server: {account.get('mt5_server')}")
                    print(f"         Investment ID: {account.get('investment_id', 'None')}")
                    print(f"         Balance: ${account.get('balance', 0):,.2f}")
                    print(f"         Equity: ${account.get('equity', 0):,.2f}")
                    print(f"         Created: {account.get('created_at')}")
                    
                    # Categorize accounts
                    if 'doo' in broker_name or 'technology' in broker_name or mt5_login == "9928326":
                        doo_technology_accounts.append(account)
                    elif 'vt' in broker_name or 'markets' in broker_name or mt5_login == "15759667":
                        vt_markets_accounts.append(account)
                    else:
                        other_accounts.append(account)
                        
                # Analysis results
                print(f"\n   🔍 MT5 ACCOUNT ANALYSIS:")
                print(f"      DooTechnology Accounts: {len(doo_technology_accounts)}")
                print(f"      VT Markets Accounts: {len(vt_markets_accounts)}")
                print(f"      Other Accounts: {len(other_accounts)}")
                
                # Store investigation results
                self.mt5_investigation_results = {
                    'total_accounts': len(salvador_mt5_accounts),
                    'doo_technology_count': len(doo_technology_accounts),
                    'vt_markets_count': len(vt_markets_accounts),
                    'other_count': len(other_accounts),
                    'doo_technology_found': len(doo_technology_accounts) > 0,
                    'vt_markets_found': len(vt_markets_accounts) > 0,
                    'doo_technology_accounts': doo_technology_accounts,
                    'vt_markets_accounts': vt_markets_accounts
                }
                
                # Validate expected accounts
                print(f"\n   ✅ VALIDATION AGAINST USER REPORT:")
                if self.mt5_investigation_results['doo_technology_found']:
                    print(f"      ✅ DooTechnology account (9928326): FOUND")
                    for acc in doo_technology_accounts:
                        if acc.get('mt5_login') == "9928326":
                            print(f"         Login 9928326 confirmed: {acc.get('broker_name')}")
                else:
                    print(f"      ❌ DooTechnology account (9928326): MISSING")
                    self.critical_issues.append("DooTechnology account (9928326) missing")
                    
                if self.mt5_investigation_results['vt_markets_found']:
                    print(f"      ✅ VT Markets account: FOUND")
                    for acc in vt_markets_accounts:
                        print(f"         VT Markets Login: {acc.get('mt5_login')} ({acc.get('broker_name')})")
                else:
                    print(f"      ❌ VT Markets account: MISSING")
                    self.critical_issues.append("VT Markets account missing - MATCHES USER REPORT")
                    
            else:
                print(f"   ❌ CRITICAL: No MT5 accounts found for Salvador!")
                self.critical_issues.append("No MT5 accounts found for Salvador")
                
        else:
            self.critical_issues.append("Cannot retrieve MT5 accounts")
            return False
            
        return True

    def test_fund_performance_integration(self):
        """Test fund performance dashboard integration"""
        print(f"\n" + "="*60)
        print(f"📈 FUND PERFORMANCE DASHBOARD TESTING")
        print(f"="*60)
        
        # Test fund performance dashboard
        success, response = self.run_test(
            "Fund Performance Dashboard",
            "GET",
            "api/admin/fund-performance/dashboard",
            200
        )
        
        if success:
            dashboard_data = response.get('dashboard_data', {})
            performance_gaps = response.get('performance_gaps', [])
            
            print(f"   📊 FUND PERFORMANCE DASHBOARD:")
            print(f"      Performance Records: {len(performance_gaps)}")
            
            # Find Salvador's performance records
            salvador_performance = []
            for record in performance_gaps:
                client_name = record.get('client_name', '').upper()
                if 'SALVADOR' in client_name or 'PALMA' in client_name:
                    salvador_performance.append(record)
                    
            print(f"      Salvador's Performance Records: {len(salvador_performance)}")
            
            if salvador_performance:
                print(f"\n   📋 SALVADOR'S PERFORMANCE RECORDS:")
                for i, record in enumerate(salvador_performance, 1):
                    print(f"      Record {i}:")
                    print(f"         Client: {record.get('client_name')}")
                    print(f"         MT5 Login: {record.get('mt5_login')}")
                    print(f"         Broker: {record.get('broker_name', 'Unknown')}")
                    print(f"         MT5 Balance: ${record.get('mt5_balance', 0):,.2f}")
                    print(f"         FIDUS Commitment: ${record.get('fidus_commitment', 0):,.2f}")
                    print(f"         Performance Gap: ${record.get('performance_gap', 0):,.2f}")
                    
                # Check if both accounts are represented
                mt5_logins_in_performance = [str(r.get('mt5_login', '')) for r in salvador_performance]
                
                if "9928326" in mt5_logins_in_performance:
                    print(f"      ✅ DooTechnology (9928326) in performance data")
                else:
                    print(f"      ❌ DooTechnology (9928326) missing from performance data")
                    
                if "15759667" in mt5_logins_in_performance:
                    print(f"      ✅ VT Markets (15759667) in performance data")
                else:
                    print(f"      ❌ VT Markets (15759667) missing from performance data")
                    
            else:
                print(f"   ❌ No performance records found for Salvador")
                self.critical_issues.append("Salvador missing from fund performance dashboard")
                
        else:
            print(f"   ⚠️  Fund performance dashboard not accessible")
            
        return True

    def test_cash_flow_management(self):
        """Test cash flow management calculations"""
        print(f"\n" + "="*60)
        print(f"💰 CASH FLOW MANAGEMENT TESTING")
        print(f"="*60)
        
        # Test cash flow overview
        success, response = self.run_test(
            "Cash Flow Management Overview",
            "GET",
            "api/admin/cashflow/overview",
            200
        )
        
        if success:
            cash_flow_data = response.get('cash_flow_data', {})
            
            print(f"   📊 CASH FLOW OVERVIEW:")
            print(f"      MT5 Trading Profits: ${cash_flow_data.get('mt5_trading_profits', 0):,.2f}")
            print(f"      Client Interest Obligations: ${cash_flow_data.get('client_interest_obligations', 0):,.2f}")
            print(f"      Net Fund Profitability: ${cash_flow_data.get('net_fund_profitability', 0):,.2f}")
            
            # Check if Salvador's data is included
            client_breakdown = cash_flow_data.get('client_breakdown', [])
            salvador_cash_flow = None
            
            for client_data in client_breakdown:
                if client_data.get('client_id') == self.salvador_client_id:
                    salvador_cash_flow = client_data
                    break
                    
            if salvador_cash_flow:
                print(f"\n   👤 SALVADOR'S CASH FLOW DATA:")
                print(f"      Client: {salvador_cash_flow.get('client_name')}")
                print(f"      MT5 Profits: ${salvador_cash_flow.get('mt5_profits', 0):,.2f}")
                print(f"      Interest Obligations: ${salvador_cash_flow.get('interest_obligations', 0):,.2f}")
                print(f"      Net Position: ${salvador_cash_flow.get('net_position', 0):,.2f}")
            else:
                print(f"   ❌ Salvador not found in cash flow breakdown")
                self.critical_issues.append("Salvador missing from cash flow calculations")
                
        return True

    def test_critical_endpoints(self):
        """Test critical system endpoints"""
        print(f"\n" + "="*60)
        print(f"🔧 CRITICAL SYSTEM ENDPOINTS TESTING")
        print(f"="*60)
        
        critical_endpoints = [
            ("Health Check", "GET", "api/health", 200),
            ("Health Ready", "GET", "api/health/ready", 200),
            ("Health Metrics", "GET", "api/health/metrics", 200),
        ]
        
        for name, method, endpoint, expected_status in critical_endpoints:
            success, response = self.run_test(name, method, endpoint, expected_status, use_auth=False)
            
            if not success:
                self.critical_issues.append(f"Critical endpoint failed: {endpoint}")
                
        return True

    def generate_comprehensive_report(self):
        """Generate comprehensive investigation and testing report"""
        print(f"\n" + "="*80)
        print(f"🚨 COMPREHENSIVE BACKEND TESTING REPORT")
        print(f"SALVADOR PALMA VT MARKETS MT5 ACCOUNT INVESTIGATION")
        print(f"="*80)
        
        print(f"\n📋 EXECUTIVE SUMMARY:")
        print(f"   Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print(f"   Client: {self.salvador_name}")
        print(f"   Client ID: {self.salvador_client_id}")
        print(f"   Email: {self.salvador_email}")
        
        print(f"\n📊 TEST EXECUTION SUMMARY:")
        print(f"   Total Tests Run: {self.tests_run}")
        print(f"   Tests Passed: {self.tests_passed}")
        print(f"   Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"   Success Rate: {(self.tests_passed/self.tests_run*100) if self.tests_run > 0 else 0:.1f}%")
        
        # Salvador's Data Summary
        if self.salvador_data:
            print(f"\n👤 SALVADOR PALMA DATA SUMMARY:")
            
            # Profile
            profile = self.salvador_data.get('profile', {})
            print(f"   Profile Status: {'✅ Found' if profile else '❌ Missing'}")
            if profile:
                print(f"      Name: {profile.get('name')}")
                print(f"      Email: {profile.get('email')}")
                print(f"      Status: {profile.get('status')}")
                
            # Investments
            investments = self.salvador_data.get('investments', [])
            portfolio_stats = self.salvador_data.get('portfolio_stats', {})
            print(f"\n   💰 INVESTMENT SUMMARY:")
            print(f"      Total Investments: {len(investments)}")
            print(f"      Total Principal: ${portfolio_stats.get('total_principal', 0):,.2f}")
            print(f"      Total Current Value: ${portfolio_stats.get('total_current_value', 0):,.2f}")
            
            # MT5 Accounts
            mt5_accounts = self.salvador_data.get('mt5_accounts', [])
            print(f"\n   🏦 MT5 ACCOUNT SUMMARY:")
            print(f"      Total MT5 Accounts: {len(mt5_accounts)}")
            
        # MT5 Investigation Results
        if self.mt5_investigation_results:
            print(f"\n🔍 MT5 INVESTIGATION RESULTS:")
            results = self.mt5_investigation_results
            
            print(f"   Account Distribution:")
            print(f"      DooTechnology Accounts: {results.get('doo_technology_count', 0)}")
            print(f"      VT Markets Accounts: {results.get('vt_markets_count', 0)}")
            print(f"      Other Accounts: {results.get('other_count', 0)}")
            
            print(f"\n   ✅ USER REPORT VALIDATION:")
            print(f"      DooTechnology (9928326): {'✅ FOUND' if results.get('doo_technology_found') else '❌ MISSING'}")
            print(f"      VT Markets Account: {'✅ FOUND' if results.get('vt_markets_found') else '❌ MISSING'}")
            
            # Detailed account info
            if results.get('doo_technology_accounts'):
                print(f"\n   📋 DooTechnology Account Details:")
                for acc in results['doo_technology_accounts']:
                    print(f"      Login: {acc.get('mt5_login')} | Balance: ${acc.get('balance', 0):,.2f}")
                    
            if results.get('vt_markets_accounts'):
                print(f"\n   📋 VT Markets Account Details:")
                for acc in results['vt_markets_accounts']:
                    print(f"      Login: {acc.get('mt5_login')} | Balance: ${acc.get('balance', 0):,.2f}")
                    
        # Critical Issues
        if self.critical_issues:
            print(f"\n🚨 CRITICAL ISSUES IDENTIFIED:")
            for i, issue in enumerate(self.critical_issues, 1):
                print(f"   {i}. ❌ {issue}")
        else:
            print(f"\n✅ NO CRITICAL ISSUES IDENTIFIED")
            
        # Recommendations
        print(f"\n🎯 RECOMMENDATIONS:")
        
        if not self.mt5_investigation_results.get('vt_markets_found', False):
            print(f"   1. 🚨 URGENT: VT Markets Account Missing")
            print(f"      - This confirms the user report")
            print(f"      - Need to restore VT Markets MT5 account")
            print(f"      - Investigate why it was removed/lost")
            
        if not self.mt5_investigation_results.get('doo_technology_found', False):
            print(f"   2. 🚨 URGENT: DooTechnology Account Missing")
            print(f"      - User reported this as RESTORED, but not found")
            print(f"      - Need to verify DooTechnology account status")
            
        if len(self.salvador_data.get('investments', [])) != len(self.salvador_data.get('mt5_accounts', [])):
            print(f"   3. ⚠️  Investment-MT5 Account Mismatch")
            print(f"      - {len(self.salvador_data.get('investments', []))} investments vs {len(self.salvador_data.get('mt5_accounts', []))} MT5 accounts")
            print(f"      - Need to verify proper mapping")
            
        print(f"\n   4. 🔍 Further Investigation Needed:")
        print(f"      - Check database backups for missing VT Markets data")
        print(f"      - Review MT5 integration logs")
        print(f"      - Validate total investment amounts")
        print(f"      - Ensure fund performance calculations include all accounts")
        
        # Final Status
        if self.critical_issues:
            print(f"\n🚨 FINAL STATUS: CRITICAL ISSUES FOUND")
            print(f"   System requires immediate attention before production deployment")
            print(f"   Salvador's complete MT5 integration is incomplete")
        else:
            print(f"\n✅ FINAL STATUS: ALL SYSTEMS OPERATIONAL")
            print(f"   Salvador's MT5 integration appears complete")
            
        return len(self.critical_issues) == 0

    def run_comprehensive_testing(self):
        """Run comprehensive backend testing"""
        print(f"🚨 COMPREHENSIVE BACKEND TESTING - SALVADOR PALMA MT5 INVESTIGATION")
        print(f"="*80)
        print(f"CRITICAL USER REPORT:")
        print(f"✅ DooTechnology account (Login: 9928326) - RESTORED")
        print(f"❌ VT Markets account - MISSING")
        print(f"="*80)
        
        try:
            # Step 1: Authentication
            if not self.test_authentication():
                print(f"❌ CRITICAL: Authentication failed - cannot proceed")
                return False
                
            # Step 2: Salvador's profile
            if not self.test_salvador_client_profile():
                print(f"❌ CRITICAL: Salvador profile issues")
                return False
                
            # Step 3: Investment portfolio
            self.test_salvador_investments()
            
            # Step 4: MT5 account structure (CRITICAL)
            self.test_mt5_account_structure()
            
            # Step 5: Fund performance integration
            self.test_fund_performance_integration()
            
            # Step 6: Cash flow management
            self.test_cash_flow_management()
            
            # Step 7: Critical endpoints
            self.test_critical_endpoints()
            
            # Step 8: Generate comprehensive report
            success = self.generate_comprehensive_report()
            
            return success
            
        except Exception as e:
            print(f"\n❌ TESTING FAILED WITH ERROR: {str(e)}")
            return False

def main():
    """Main execution function"""
    print("🚨 COMPREHENSIVE BACKEND TESTING")
    print("SALVADOR PALMA VT MARKETS MT5 ACCOUNT INVESTIGATION")
    print("="*60)
    
    tester = ComprehensiveBackendTester()
    
    try:
        success = tester.run_comprehensive_testing()
        
        if success:
            print(f"\n✅ All tests completed successfully")
            return True
        else:
            print(f"\n❌ Critical issues found - system needs attention")
            return False
            
    except KeyboardInterrupt:
        print(f"\n⚠️ Testing interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Testing failed with error: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)