#!/usr/bin/env python3
"""
SALVADOR PALMA MT5-INVESTMENT INTEGRATION CRITICAL TEST
=====================================================

This test specifically addresses the critical issue reported:
- Both MT5 accounts exist (DooTechnology: 9928326, VT Markets: 15759667) 
- But have broken integration (Investment ID: None)
- Salvador missing from fund performance dashboard (0 records)
- Cash flow showing $0 values despite having MT5 accounts
- Need to fix MT5-to-investment linking and business logic integration

EXPECTED RESULT: Salvador should appear in all business logic systems with both 
MT5 accounts contributing to performance/cash flow calculations.
"""

import requests
import sys
import json
from datetime import datetime
from typing import Dict, Any, List

class SalvadorMT5IntegrationTester:
    def __init__(self, base_url="https://equity-peak-tracker.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.admin_user = None
        self.salvador_client_id = "client_003"  # Salvador Palma's client ID
        self.salvador_email = "chava@alyarglobal.com"
        self.expected_mt5_accounts = [
            {"login": 9928326, "broker": "DooTechnology"},
            {"login": 15759667, "broker": "VT Markets"}
        ]
        self.critical_issues = []
        
    def run_test(self, name: str, method: str, endpoint: str, expected_status: int, 
                 data: Dict = None, headers: Dict = None, use_auth: bool = False) -> tuple[bool, Dict]:
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        if headers is None:
            headers = {'Content-Type': 'application/json'}
        
        # Add JWT token for authenticated endpoints
        if use_auth and self.admin_user and self.admin_user.get('token'):
            headers['Authorization'] = f"Bearer {self.admin_user['token']}"

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

    def setup_admin_authentication(self) -> bool:
        """Setup admin authentication"""
        print("\n" + "="*80)
        print("🔐 SETTING UP ADMIN AUTHENTICATION")
        print("="*80)
        
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
            print(f"   ✅ Admin logged in: {response.get('name', 'Unknown')} (ID: {response.get('id')})")
            return True
        else:
            print("   ❌ Admin login failed - cannot proceed with tests")
            return False

    def test_salvador_profile_verification(self) -> bool:
        """Verify Salvador Palma's profile exists and is accessible"""
        print("\n" + "="*80)
        print("👤 TESTING SALVADOR PALMA PROFILE VERIFICATION")
        print("="*80)
        
        # Test 1: Verify Salvador exists in client list
        print("\n📊 Test 1: Verify Salvador in Client List")
        success, response = self.run_test(
            "Get All Clients",
            "GET",
            "api/clients/all",
            200,
            use_auth=True
        )
        
        salvador_found = False
        if success:
            clients = response.get('clients', [])
            print(f"   Total clients found: {len(clients)}")
            
            for client in clients:
                if client.get('id') == self.salvador_client_id:
                    salvador_found = True
                    print(f"   ✅ Salvador Palma found: {client.get('name')} ({client.get('email')})")
                    print(f"   📊 Client Status: {client.get('status', 'Unknown')}")
                    print(f"   💰 Total Balance: ${client.get('total_balance', 0):,.2f}")
                    break
            
            if not salvador_found:
                self.critical_issues.append("Salvador Palma profile not found in client list")
                print(f"   ❌ Salvador Palma (ID: {self.salvador_client_id}) not found in client list")
                return False
        else:
            self.critical_issues.append("Failed to retrieve client list")
            return False

        # Test 2: Get Salvador's specific client data
        print("\n📊 Test 2: Get Salvador's Specific Client Data")
        success, response = self.run_test(
            "Get Salvador's Client Data",
            "GET",
            f"api/client/{self.salvador_client_id}/data",
            200
        )
        
        if success:
            balance = response.get('balance', {})
            total_balance = balance.get('total_balance', 0)
            print(f"   ✅ Salvador's total balance: ${total_balance:,.2f}")
            
            # Check individual fund balances
            core_balance = balance.get('core_balance', 0)
            balance_balance = balance.get('balance_balance', 0)
            dynamic_balance = balance.get('dynamic_balance', 0)
            unlimited_balance = balance.get('unlimited_balance', 0)
            
            print(f"   📊 CORE balance: ${core_balance:,.2f}")
            print(f"   📊 BALANCE balance: ${balance_balance:,.2f}")
            print(f"   📊 DYNAMIC balance: ${dynamic_balance:,.2f}")
            print(f"   📊 UNLIMITED balance: ${unlimited_balance:,.2f}")
            
            if total_balance > 0:
                print("   ✅ Salvador has positive balance indicating active investments")
            else:
                self.critical_issues.append("Salvador has zero balance despite expected investments")
                print("   ❌ Salvador has zero balance - this indicates missing investments")
        else:
            self.critical_issues.append("Failed to retrieve Salvador's client data")
            return False

        return salvador_found

    def test_salvador_investments(self) -> bool:
        """Test Salvador's investment portfolio"""
        print("\n" + "="*80)
        print("💰 TESTING SALVADOR'S INVESTMENT PORTFOLIO")
        print("="*80)
        
        # Test 1: Get Salvador's investments
        print("\n📊 Test 1: Get Salvador's Investment Portfolio")
        success, response = self.run_test(
            "Get Salvador's Investments",
            "GET",
            f"api/investments/client/{self.salvador_client_id}",
            200
        )
        
        investments_found = []
        if success:
            investments = response.get('investments', [])
            portfolio_stats = response.get('portfolio_stats', {})
            
            print(f"   📊 Total investments: {len(investments)}")
            print(f"   💰 Total principal: ${portfolio_stats.get('total_principal', 0):,.2f}")
            print(f"   📈 Total current value: ${portfolio_stats.get('total_current_value', 0):,.2f}")
            
            if len(investments) == 0:
                self.critical_issues.append("Salvador has ZERO investments - this is the root cause of MT5 integration failure")
                print("   ❌ CRITICAL: Salvador has ZERO investments!")
                print("   🚨 This explains why MT5 accounts show Investment ID: None")
                return False
            
            # Analyze each investment
            for investment in investments:
                investment_id = investment.get('investment_id')
                fund_code = investment.get('fund_code')
                principal = investment.get('principal_amount', 0)
                current_value = investment.get('current_value', 0)
                status = investment.get('status', 'Unknown')
                
                investments_found.append({
                    'id': investment_id,
                    'fund_code': fund_code,
                    'principal': principal,
                    'current_value': current_value,
                    'status': status
                })
                
                print(f"   💰 Investment {investment_id[:8]}...")
                print(f"      Fund: {fund_code}")
                print(f"      Principal: ${principal:,.2f}")
                print(f"      Current Value: ${current_value:,.2f}")
                print(f"      Status: {status}")
            
            # Check for expected BALANCE fund investment
            balance_investments = [inv for inv in investments if inv.get('fund_code') == 'BALANCE']
            if balance_investments:
                print("   ✅ Found BALANCE fund investment(s) - this should link to MT5 accounts")
            else:
                self.critical_issues.append("No BALANCE fund investment found for Salvador")
                print("   ❌ No BALANCE fund investment found - expected for MT5 linking")
                
        else:
            self.critical_issues.append("Failed to retrieve Salvador's investments")
            return False

        return len(investments_found) > 0

    def test_salvador_mt5_accounts(self) -> bool:
        """Test Salvador's MT5 accounts and their integration status"""
        print("\n" + "="*80)
        print("🏦 TESTING SALVADOR'S MT5 ACCOUNTS")
        print("="*80)
        
        # Test 1: Get Salvador's MT5 accounts
        print("\n📊 Test 1: Get Salvador's MT5 Accounts")
        success, response = self.run_test(
            "Get Salvador's MT5 Accounts",
            "GET",
            f"api/mt5/client/{self.salvador_client_id}/accounts",
            200
        )
        
        mt5_accounts_found = []
        if success:
            accounts = response.get('accounts', [])
            summary = response.get('summary', {})
            
            print(f"   📊 Total MT5 accounts: {len(accounts)}")
            print(f"   💰 Total allocated: ${summary.get('total_allocated', 0):,.2f}")
            print(f"   📈 Total equity: ${summary.get('total_equity', 0):,.2f}")
            
            if len(accounts) == 0:
                self.critical_issues.append("Salvador has ZERO MT5 accounts - contradicts user report")
                print("   ❌ CRITICAL: Salvador has ZERO MT5 accounts!")
                print("   🚨 This contradicts the user report that both accounts exist")
                return False
            
            # Check each MT5 account
            for account in accounts:
                account_id = account.get('account_id')
                mt5_login = account.get('mt5_login')
                broker = account.get('broker_name', account.get('mt5_server', 'Unknown'))
                investment_id = account.get('investment_id')
                fund_code = account.get('fund_code')
                total_allocated = account.get('total_allocated', 0)
                
                mt5_accounts_found.append({
                    'account_id': account_id,
                    'mt5_login': mt5_login,
                    'broker': broker,
                    'investment_id': investment_id,
                    'fund_code': fund_code,
                    'total_allocated': total_allocated
                })
                
                print(f"   🏦 MT5 Account: {account_id}")
                print(f"      Login: {mt5_login}")
                print(f"      Broker: {broker}")
                print(f"      Investment ID: {investment_id}")
                print(f"      Fund Code: {fund_code}")
                print(f"      Allocated: ${total_allocated:,.2f}")
                
                # Check for the critical issue: Investment ID is None
                if investment_id is None or investment_id == "None":
                    self.critical_issues.append(f"MT5 account {mt5_login} has Investment ID: None - broken integration")
                    print(f"      ❌ CRITICAL: Investment ID is None - broken integration!")
                else:
                    print(f"      ✅ Investment ID properly linked: {investment_id}")
            
            # Verify expected MT5 accounts exist
            found_logins = [acc.get('mt5_login') for acc in accounts]
            for expected_account in self.expected_mt5_accounts:
                expected_login = expected_account['login']
                expected_broker = expected_account['broker']
                
                if expected_login in found_logins:
                    print(f"   ✅ Expected MT5 account found: {expected_login} ({expected_broker})")
                else:
                    self.critical_issues.append(f"Expected MT5 account missing: {expected_login} ({expected_broker})")
                    print(f"   ❌ Expected MT5 account missing: {expected_login} ({expected_broker})")
                    
        else:
            self.critical_issues.append("Failed to retrieve Salvador's MT5 accounts")
            return False

        return len(mt5_accounts_found) > 0

    def test_fund_performance_dashboard_integration(self) -> bool:
        """Test Salvador's presence in fund performance dashboard"""
        print("\n" + "="*80)
        print("📈 TESTING FUND PERFORMANCE DASHBOARD INTEGRATION")
        print("="*80)
        
        # Test 1: Check fund performance dashboard
        print("\n📊 Test 1: Fund Performance Dashboard")
        success, response = self.run_test(
            "Get Fund Performance Dashboard",
            "GET",
            "api/admin/fund-performance/dashboard",
            200,
            use_auth=True
        )
        
        salvador_in_dashboard = False
        if success:
            performance_data = response.get('performance_data', [])
            summary = response.get('summary', {})
            
            print(f"   📊 Total performance records: {len(performance_data)}")
            print(f"   📊 Total clients tracked: {summary.get('total_clients', 0)}")
            print(f"   💰 Total AUM: ${summary.get('total_aum', 0):,.2f}")
            
            if len(performance_data) == 0:
                self.critical_issues.append("Fund performance dashboard shows 0 records - Salvador missing")
                print("   ❌ CRITICAL: Fund performance dashboard shows 0 records!")
                print("   🚨 Salvador is completely missing from performance calculations")
                return False
            
            # Look for Salvador in performance data
            for record in performance_data:
                client_id = record.get('client_id')
                client_name = record.get('client_name', '')
                
                if client_id == self.salvador_client_id or 'SALVADOR' in client_name.upper():
                    salvador_in_dashboard = True
                    print(f"   ✅ Salvador found in performance dashboard:")
                    print(f"      Client: {client_name} ({client_id})")
                    print(f"      Fund Performance: ${record.get('fund_performance', 0):,.2f}")
                    print(f"      MT5 Performance: ${record.get('mt5_performance', 0):,.2f}")
                    print(f"      Performance Gap: ${record.get('performance_gap', 0):,.2f}")
                    break
            
            if not salvador_in_dashboard:
                self.critical_issues.append("Salvador not found in fund performance dashboard")
                print("   ❌ CRITICAL: Salvador not found in fund performance dashboard!")
                print("   🚨 This confirms the broken MT5-investment integration")
                
                # Show who is in the dashboard for debugging
                print("   📋 Clients currently in dashboard:")
                for record in performance_data[:5]:  # Show first 5
                    print(f"      - {record.get('client_name', 'Unknown')} ({record.get('client_id', 'Unknown')})")
                    
        else:
            self.critical_issues.append("Failed to retrieve fund performance dashboard")
            return False

        return salvador_in_dashboard

    def test_cash_flow_management_integration(self) -> bool:
        """Test Salvador's presence in cash flow management"""
        print("\n" + "="*80)
        print("💸 TESTING CASH FLOW MANAGEMENT INTEGRATION")
        print("="*80)
        
        # Test 1: Check cash flow overview
        print("\n📊 Test 1: Cash Flow Overview")
        success, response = self.run_test(
            "Get Cash Flow Overview",
            "GET",
            "api/admin/cashflow/overview",
            200,
            use_auth=True
        )
        
        if success:
            overview = response.get('overview', {})
            mt5_trading_profits = overview.get('mt5_trading_profits', 0)
            client_obligations = overview.get('client_interest_obligations', 0)
            net_profitability = overview.get('net_fund_profitability', 0)
            
            print(f"   💰 MT5 Trading Profits: ${mt5_trading_profits:,.2f}")
            print(f"   💰 Client Obligations: ${client_obligations:,.2f}")
            print(f"   📊 Net Fund Profitability: ${net_profitability:,.2f}")
            
            if mt5_trading_profits == 0 and client_obligations == 0:
                self.critical_issues.append("Cash flow shows $0 values - Salvador's MT5 accounts not contributing")
                print("   ❌ CRITICAL: Cash flow shows $0 values!")
                print("   🚨 Salvador's MT5 accounts are not contributing to cash flow calculations")
                return False
            else:
                print("   ✅ Cash flow shows non-zero values - some integration working")
                
        else:
            self.critical_issues.append("Failed to retrieve cash flow overview")
            return False

        # Test 2: Check detailed cash flow breakdown
        print("\n📊 Test 2: Cash Flow Detailed Breakdown")
        success, response = self.run_test(
            "Get Cash Flow Breakdown",
            "GET",
            "api/admin/cashflow/breakdown",
            200,
            use_auth=True
        )
        
        salvador_in_cashflow = False
        if success:
            breakdown = response.get('breakdown', {})
            client_details = breakdown.get('client_details', [])
            
            print(f"   📊 Clients in cash flow breakdown: {len(client_details)}")
            
            # Look for Salvador in cash flow breakdown
            for client_detail in client_details:
                client_id = client_detail.get('client_id')
                client_name = client_detail.get('client_name', '')
                
                if client_id == self.salvador_client_id or 'SALVADOR' in client_name.upper():
                    salvador_in_cashflow = True
                    print(f"   ✅ Salvador found in cash flow breakdown:")
                    print(f"      Client: {client_name} ({client_id})")
                    print(f"      MT5 Profits: ${client_detail.get('mt5_profits', 0):,.2f}")
                    print(f"      Interest Obligations: ${client_detail.get('interest_obligations', 0):,.2f}")
                    break
            
            if not salvador_in_cashflow:
                self.critical_issues.append("Salvador not found in cash flow breakdown")
                print("   ❌ Salvador not found in cash flow breakdown!")
                print("   🚨 Confirms Salvador's MT5 accounts are not integrated into business logic")
                
        else:
            print("   ⚠️ Cash flow breakdown endpoint not available (may be expected)")

        return True  # Don't fail on cash flow breakdown as it may not be implemented

    def test_mt5_investment_linking_fix(self) -> bool:
        """Test if MT5-investment linking can be fixed"""
        print("\n" + "="*80)
        print("🔧 TESTING MT5-INVESTMENT LINKING FIX")
        print("="*80)
        
        # This test would attempt to fix the linking, but since we're testing only,
        # we'll just verify the current state and suggest fixes
        
        print("\n📊 Test 1: Analyze Current MT5-Investment Linking State")
        
        # Get Salvador's investments
        success1, inv_response = self.run_test(
            "Get Salvador's Investments for Linking Analysis",
            "GET",
            f"api/investments/client/{self.salvador_client_id}",
            200
        )
        
        # Get Salvador's MT5 accounts
        success2, mt5_response = self.run_test(
            "Get Salvador's MT5 Accounts for Linking Analysis",
            "GET",
            f"api/mt5/client/{self.salvador_client_id}/accounts",
            200
        )
        
        if success1 and success2:
            investments = inv_response.get('investments', [])
            mt5_accounts = mt5_response.get('accounts', [])
            
            print(f"   📊 Investments found: {len(investments)}")
            print(f"   📊 MT5 accounts found: {len(mt5_accounts)}")
            
            # Analyze linking potential
            balance_investments = [inv for inv in investments if inv.get('fund_code') == 'BALANCE']
            doo_tech_accounts = [acc for acc in mt5_accounts if acc.get('mt5_login') == 9928326]
            vt_markets_accounts = [acc for acc in mt5_accounts if acc.get('mt5_login') == 15759667]
            
            print(f"\n   🔍 Linking Analysis:")
            print(f"      BALANCE investments: {len(balance_investments)}")
            print(f"      DooTechnology MT5 accounts: {len(doo_tech_accounts)}")
            print(f"      VT Markets MT5 accounts: {len(vt_markets_accounts)}")
            
            if len(balance_investments) > 0 and len(doo_tech_accounts) > 0:
                balance_inv = balance_investments[0]
                doo_acc = doo_tech_accounts[0]
                
                print(f"\n   💡 LINKING OPPORTUNITY IDENTIFIED:")
                print(f"      BALANCE Investment ID: {balance_inv.get('investment_id')}")
                print(f"      DooTechnology Account ID: {doo_acc.get('account_id')}")
                print(f"      Current Investment ID in MT5: {doo_acc.get('investment_id')}")
                
                if doo_acc.get('investment_id') != balance_inv.get('investment_id'):
                    self.critical_issues.append("DooTechnology MT5 account not linked to BALANCE investment")
                    print(f"      ❌ BROKEN LINK: MT5 account should link to investment {balance_inv.get('investment_id')}")
                else:
                    print(f"      ✅ PROPER LINK: MT5 account correctly linked to investment")
            
            # Check for VT Markets linking opportunity
            if len(vt_markets_accounts) > 0:
                vt_acc = vt_markets_accounts[0]
                print(f"\n   💡 VT MARKETS ACCOUNT ANALYSIS:")
                print(f"      VT Markets Account ID: {vt_acc.get('account_id')}")
                print(f"      Current Investment ID: {vt_acc.get('investment_id')}")
                print(f"      Fund Code: {vt_acc.get('fund_code')}")
                
                if vt_acc.get('investment_id') is None:
                    self.critical_issues.append("VT Markets MT5 account has no investment link")
                    print(f"      ❌ BROKEN LINK: VT Markets account needs investment linking")
                    
                    # Suggest which investment it should link to
                    if len(investments) > 1:
                        print(f"      💡 SUGGESTION: Link to one of {len(investments)} available investments")
                    else:
                        print(f"      💡 SUGGESTION: Create new investment for VT Markets account")
            
        else:
            self.critical_issues.append("Failed to analyze MT5-investment linking state")
            return False

        return True

    def run_comprehensive_salvador_mt5_test(self) -> bool:
        """Run comprehensive Salvador MT5 integration test"""
        print("\n" + "="*100)
        print("🚀 STARTING SALVADOR PALMA MT5-INVESTMENT INTEGRATION CRITICAL TEST")
        print("="*100)
        print("🎯 OBJECTIVE: Fix broken MT5-to-investment integration for Salvador Palma")
        print("📋 EXPECTED: Both MT5 accounts should show proper Investment ID references")
        print("📈 EXPECTED: Salvador should appear in fund performance dashboard")
        print("💰 EXPECTED: Cash flow calculations should include Salvador's MT5 performance")
        
        # Setup authentication
        if not self.setup_admin_authentication():
            print("\n❌ Authentication setup failed - cannot proceed")
            return False
        
        # Run all test suites
        test_suites = [
            ("Salvador Profile Verification", self.test_salvador_profile_verification),
            ("Salvador Investment Portfolio", self.test_salvador_investments),
            ("Salvador MT5 Accounts", self.test_salvador_mt5_accounts),
            ("Fund Performance Dashboard Integration", self.test_fund_performance_dashboard_integration),
            ("Cash Flow Management Integration", self.test_cash_flow_management_integration),
            ("MT5-Investment Linking Analysis", self.test_mt5_investment_linking_fix)
        ]
        
        suite_results = []
        
        for suite_name, test_method in test_suites:
            print(f"\n🔄 Running {suite_name}...")
            try:
                result = test_method()
                suite_results.append((suite_name, result))
                
                if result:
                    print(f"✅ {suite_name} - PASSED")
                else:
                    print(f"❌ {suite_name} - FAILED")
            except Exception as e:
                print(f"❌ {suite_name} - ERROR: {str(e)}")
                suite_results.append((suite_name, False))
        
        # Print final results
        print("\n" + "="*100)
        print("📊 SALVADOR PALMA MT5 INTEGRATION TEST RESULTS")
        print("="*100)
        
        passed_suites = sum(1 for _, result in suite_results if result)
        total_suites = len(suite_results)
        
        for suite_name, result in suite_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"   {suite_name}: {status}")
        
        print(f"\n📈 Overall Results:")
        print(f"   Test Suites: {passed_suites}/{total_suites} passed ({passed_suites/total_suites*100:.1f}%)")
        print(f"   Individual Tests: {self.tests_passed}/{self.tests_run} passed ({self.tests_passed/self.tests_run*100:.1f}%)")
        
        # Print critical issues found
        if self.critical_issues:
            print(f"\n🚨 CRITICAL ISSUES IDENTIFIED ({len(self.critical_issues)}):")
            for i, issue in enumerate(self.critical_issues, 1):
                print(f"   {i}. {issue}")
        else:
            print(f"\n✅ NO CRITICAL ISSUES FOUND")
        
        # Determine overall success and provide recommendations
        critical_integration_working = (
            passed_suites >= 4 and  # At least 4 out of 6 suites should pass
            len(self.critical_issues) == 0
        )
        
        print(f"\n" + "="*100)
        if critical_integration_working:
            print(f"🎉 SALVADOR MT5 INTEGRATION IS WORKING CORRECTLY!")
            print("   ✅ Both MT5 accounts are properly linked to investments")
            print("   ✅ Salvador appears in fund performance dashboard")
            print("   ✅ Cash flow calculations include Salvador's MT5 performance")
            print("   ✅ All business logic systems are integrated")
        else:
            print(f"🚨 SALVADOR MT5 INTEGRATION HAS CRITICAL ISSUES!")
            print("   ❌ MT5-to-investment linking is broken")
            print("   ❌ Salvador missing from business logic calculations")
            print("   ❌ Immediate main agent action required")
            
            print(f"\n🔧 RECOMMENDED FIXES FOR MAIN AGENT:")
            print("   1. Fix MT5 account Investment ID linking (currently showing None)")
            print("   2. Ensure Salvador's investments are properly created and linked")
            print("   3. Update fund performance calculations to include Salvador")
            print("   4. Fix cash flow management to include Salvador's MT5 data")
            print("   5. Test complete integration after fixes")
        
        return critical_integration_working

def main():
    """Main test execution"""
    print("🔧 Salvador Palma MT5-Investment Integration Critical Test")
    print("Testing the specific integration issues reported by user")
    
    tester = SalvadorMT5IntegrationTester()
    
    try:
        success = tester.run_comprehensive_salvador_mt5_test()
        
        if success:
            print("\n✅ Salvador MT5 integration test completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Salvador MT5 integration test found critical issues!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Testing failed with error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()