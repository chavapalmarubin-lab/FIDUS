#!/usr/bin/env python3
"""
SALVADOR PALMA MT5 ACCOUNTS DISPLAY TESTING
==========================================

This test specifically addresses the review request to fix MT5 accounts display issues:

REMAINING DISPLAY ISSUES TO FIX:
1. Make DooTechnology account (9928326) clearly visible in MT5 Accounts section
2. Make VT Markets account (15759667) clearly visible in MT5 Accounts section  
3. Show correct investment amounts and linking
4. Display Salvador Palma name explicitly in all dashboards

TESTING OBJECTIVES:
1. Test `/api/mt5/admin/accounts` endpoint - verify both accounts appear with correct data
2. Verify account details show:
   - DooTechnology Login: 9928326, linked to BALANCE investment ($1,263,485.40)
   - VT Markets Login: 15759667, linked to CORE investment ($4,000) ✅ corrected
3. Verify client names show as "Salvador Palma" not just client_003
4. Check that broker names display correctly (DooTechnology, VT Markets)
5. Confirm investment linking shows proper Investment IDs
"""

import requests
import sys
from datetime import datetime
import json
from typing import Dict, Any, List

class SalvadorMT5DisplayTester:
    def __init__(self, base_url="https://fidus-invest.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.admin_user = None
        self.admin_token = None
        self.salvador_client_id = "client_003"
        self.salvador_name = "Salvador Palma"
        
        # Expected MT5 accounts for Salvador
        self.expected_accounts = {
            "dootechnology": {
                "login": "9928326",
                "broker": "DooTechnology",
                "investment_type": "BALANCE",
                "expected_amount": 1263485.40
            },
            "vt_markets": {
                "login": "15759667", 
                "broker": "VT Markets",
                "investment_type": "CORE",
                "expected_amount": 4000.00  # Corrected from $5,000 to $4,000
            }
        }
        
    def run_test(self, name: str, method: str, endpoint: str, expected_status: int, 
                 data: Dict = None, headers: Dict = None, use_auth: bool = False) -> tuple[bool, Dict]:
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        if headers is None:
            headers = {'Content-Type': 'application/json'}
        
        # Add JWT token for authenticated requests
        if use_auth and self.admin_token:
            headers['Authorization'] = f'Bearer {self.admin_token}'

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
            # Extract JWT token for authenticated requests
            self.admin_token = response.get('token')
            if self.admin_token:
                print(f"   ✅ Admin logged in: {response.get('name', 'Unknown')} (ID: {response.get('id')})")
                print(f"   🔑 JWT token obtained for authenticated requests")
                return True
            else:
                print("   ❌ No JWT token received in login response")
                return False
        else:
            print("   ❌ Admin login failed - cannot proceed with MT5 admin tests")
            return False

    def test_salvador_client_profile(self) -> bool:
        """Test Salvador Palma client profile visibility"""
        print("\n" + "="*80)
        print("👤 TESTING SALVADOR PALMA CLIENT PROFILE")
        print("="*80)
        
        # Test 1: Get all clients and find Salvador
        print("\n📊 Test 1: Find Salvador Palma in Clients List")
        success, response = self.run_test(
            "Get All Clients",
            "GET",
            "api/admin/clients",
            200,
            use_auth=True
        )
        
        if success:
            clients = response.get('clients', [])
            salvador_found = False
            salvador_data = None
            
            for client in clients:
                if client.get('id') == self.salvador_client_id:
                    salvador_found = True
                    salvador_data = client
                    break
            
            if salvador_found:
                print(f"   ✅ Salvador Palma found in clients list")
                print(f"   📋 Client ID: {salvador_data.get('id')}")
                print(f"   📋 Name: {salvador_data.get('name')}")
                print(f"   📋 Email: {salvador_data.get('email')}")
                print(f"   📋 Total Balance: ${salvador_data.get('total_balance', 0):,.2f}")
                
                # Verify name display
                client_name = salvador_data.get('name', '')
                if 'Salvador' in client_name and 'Palma' in client_name:
                    print("   ✅ Salvador Palma name displayed correctly")
                else:
                    print(f"   ❌ Name display issue: '{client_name}' should show 'Salvador Palma'")
                    return False
            else:
                print(f"   ❌ Salvador Palma (client_003) not found in clients list")
                return False
        else:
            print("   ❌ Failed to get clients list")
            return False
            
        return True

    def test_salvador_investments(self) -> bool:
        """Test Salvador's investment data"""
        print("\n" + "="*80)
        print("💰 TESTING SALVADOR PALMA INVESTMENTS")
        print("="*80)
        
        # Test 1: Get Salvador's investments
        print("\n📊 Test 1: Get Salvador's Investment Portfolio")
        success, response = self.run_test(
            "Get Salvador's Investments",
            "GET",
            f"api/admin/clients/{self.salvador_client_id}/investments",
            200
        )
        
        if success:
            investments = response.get('investments', [])
            print(f"   ✅ Found {len(investments)} investments for Salvador")
            
            # Look for expected investments
            balance_investments = [inv for inv in investments if inv.get('fund_code') == 'BALANCE']
            core_investments = [inv for inv in investments if inv.get('fund_code') == 'CORE']
            
            print(f"   📊 BALANCE fund investments: {len(balance_investments)}")
            print(f"   📊 CORE fund investments: {len(core_investments)}")
            
            # Check BALANCE investment (should be linked to DooTechnology MT5)
            if balance_investments:
                balance_inv = balance_investments[0]  # Take first BALANCE investment
                balance_amount = balance_inv.get('principal_amount', 0)
                print(f"   💰 BALANCE investment amount: ${balance_amount:,.2f}")
                
                if abs(balance_amount - self.expected_accounts["dootechnology"]["expected_amount"]) < 1:
                    print("   ✅ BALANCE investment amount matches expected DooTechnology linking")
                else:
                    print(f"   ⚠️ BALANCE investment amount ${balance_amount:,.2f} differs from expected ${self.expected_accounts['dootechnology']['expected_amount']:,.2f}")
            
            # Check CORE investment (should be linked to VT Markets MT5)
            if core_investments:
                core_inv = core_investments[0]  # Take first CORE investment
                core_amount = core_inv.get('principal_amount', 0)
                print(f"   💰 CORE investment amount: ${core_amount:,.2f}")
                
                if abs(core_amount - self.expected_accounts["vt_markets"]["expected_amount"]) < 1:
                    print("   ✅ CORE investment amount matches expected VT Markets linking (corrected to $4,000)")
                else:
                    print(f"   ⚠️ CORE investment amount ${core_amount:,.2f} differs from expected ${self.expected_accounts['vt_markets']['expected_amount']:,.2f}")
            
            if not balance_investments and not core_investments:
                print("   ❌ No BALANCE or CORE investments found for Salvador")
                return False
                
        else:
            print("   ❌ Failed to get Salvador's investments")
            return False
            
        return True

    def test_mt5_admin_accounts_endpoint(self) -> bool:
        """Test the main MT5 admin accounts endpoint"""
        print("\n" + "="*80)
        print("🏦 TESTING MT5 ADMIN ACCOUNTS ENDPOINT")
        print("="*80)
        
        # Test 1: Get all MT5 accounts
        print("\n📊 Test 1: Get All MT5 Accounts via Admin Endpoint")
        success, response = self.run_test(
            "Get MT5 Admin Accounts",
            "GET",
            "api/mt5/admin/accounts",
            200
        )
        
        if success:
            accounts = response.get('accounts', [])
            summary = response.get('summary', {})
            
            print(f"   ✅ Total MT5 accounts found: {len(accounts)}")
            print(f"   📊 Summary - Total Accounts: {summary.get('total_accounts', 0)}")
            print(f"   📊 Summary - Total Allocated: ${summary.get('total_allocated', 0):,.2f}")
            print(f"   📊 Summary - Total Equity: ${summary.get('total_equity', 0):,.2f}")
            
            # Find Salvador's accounts
            salvador_accounts = [acc for acc in accounts if acc.get('client_id') == self.salvador_client_id]
            print(f"   🔍 Salvador's MT5 accounts found: {len(salvador_accounts)}")
            
            if not salvador_accounts:
                print("   ❌ No MT5 accounts found for Salvador Palma")
                return False
            
            # Check for expected accounts
            doo_account = None
            vt_account = None
            
            for account in salvador_accounts:
                mt5_login = str(account.get('mt5_login', ''))
                broker_name = account.get('broker_name', '')
                
                print(f"   🏦 Found account - Login: {mt5_login}, Broker: {broker_name}")
                
                # Check for DooTechnology account
                if mt5_login == self.expected_accounts["dootechnology"]["login"]:
                    doo_account = account
                    print(f"   ✅ DooTechnology account found: {mt5_login}")
                
                # Check for VT Markets account  
                if mt5_login == self.expected_accounts["vt_markets"]["login"]:
                    vt_account = account
                    print(f"   ✅ VT Markets account found: {mt5_login}")
            
            # Verify both expected accounts are present
            if not doo_account:
                print(f"   ❌ DooTechnology account (Login: {self.expected_accounts['dootechnology']['login']}) NOT FOUND")
                return False
                
            if not vt_account:
                print(f"   ❌ VT Markets account (Login: {self.expected_accounts['vt_markets']['login']}) NOT FOUND")
                return False
            
            print("   ✅ Both expected MT5 accounts found for Salvador")
            
            # Test account details
            self.verify_account_details(doo_account, "DooTechnology")
            self.verify_account_details(vt_account, "VT Markets")
            
        else:
            print("   ❌ Failed to get MT5 admin accounts")
            return False
            
        return True

    def verify_account_details(self, account: Dict, expected_broker: str) -> bool:
        """Verify specific account details"""
        print(f"\n📋 Verifying {expected_broker} Account Details:")
        
        # Check client name display
        client_name = account.get('client_name', '')
        if 'Salvador' in client_name and 'Palma' in client_name:
            print(f"   ✅ Client name displayed correctly: '{client_name}'")
        else:
            print(f"   ❌ Client name issue: '{client_name}' should show 'Salvador Palma'")
            return False
        
        # Check broker name
        broker_name = account.get('broker_name', '')
        if expected_broker.lower() in broker_name.lower():
            print(f"   ✅ Broker name displayed correctly: '{broker_name}'")
        else:
            print(f"   ⚠️ Broker name: '{broker_name}' (expected to contain '{expected_broker}')")
        
        # Check MT5 login
        mt5_login = account.get('mt5_login')
        print(f"   📱 MT5 Login: {mt5_login}")
        
        # Check investment linking
        investment_ids = account.get('investment_ids', [])
        if investment_ids and len(investment_ids) > 0:
            print(f"   ✅ Investment linking present: {len(investment_ids)} investment(s) linked")
            print(f"   🔗 Investment IDs: {investment_ids}")
        else:
            print(f"   ❌ No investment linking found (investment_ids: {investment_ids})")
            return False
        
        # Check allocation amounts
        total_allocated = account.get('total_allocated', 0)
        current_equity = account.get('current_equity', 0)
        print(f"   💰 Total Allocated: ${total_allocated:,.2f}")
        print(f"   💰 Current Equity: ${current_equity:,.2f}")
        
        return True

    def test_fund_performance_dashboard(self) -> bool:
        """Test Fund Performance dashboard includes Salvador"""
        print("\n" + "="*80)
        print("📈 TESTING FUND PERFORMANCE DASHBOARD")
        print("="*80)
        
        # Test 1: Get fund performance data
        print("\n📊 Test 1: Get Fund Performance vs MT5 Reality")
        success, response = self.run_test(
            "Get Fund Performance Dashboard",
            "GET",
            "api/admin/fund-performance",
            200
        )
        
        if success:
            performance_data = response.get('performance_gaps', [])
            print(f"   ✅ Found {len(performance_data)} performance records")
            
            # Look for Salvador's data
            salvador_records = []
            for record in performance_data:
                client_id = record.get('client_id', '')
                client_name = record.get('client_name', '')
                
                if client_id == self.salvador_client_id or 'Salvador' in client_name:
                    salvador_records.append(record)
            
            if salvador_records:
                print(f"   ✅ Salvador found in Fund Performance dashboard: {len(salvador_records)} records")
                
                for record in salvador_records:
                    client_name = record.get('client_name', '')
                    fund_code = record.get('fund_code', '')
                    performance_gap = record.get('performance_gap_percentage', 0)
                    
                    print(f"   📊 {client_name} - {fund_code}: {performance_gap:.2f}% performance gap")
                    
                    # Verify name display
                    if 'Salvador' in client_name and 'Palma' in client_name:
                        print(f"   ✅ Name displayed correctly in performance dashboard")
                    else:
                        print(f"   ❌ Name display issue in performance dashboard: '{client_name}'")
                        return False
            else:
                print("   ❌ Salvador NOT found in Fund Performance dashboard")
                return False
                
        else:
            print("   ❌ Failed to get fund performance data")
            return False
            
        return True

    def test_cash_flow_management(self) -> bool:
        """Test Cash Flow Management includes Salvador"""
        print("\n" + "="*80)
        print("💸 TESTING CASH FLOW MANAGEMENT")
        print("="*80)
        
        # Test 1: Get cash flow data
        print("\n📊 Test 1: Get Cash Flow Management Data")
        success, response = self.run_test(
            "Get Cash Flow Management",
            "GET",
            "api/admin/cash-flow",
            200
        )
        
        if success:
            cash_flow_data = response.get('cash_flow_summary', {})
            mt5_trading_profits = cash_flow_data.get('mt5_trading_profits', 0)
            client_obligations = cash_flow_data.get('client_interest_obligations', 0)
            net_profitability = cash_flow_data.get('net_fund_profitability', 0)
            
            print(f"   📊 MT5 Trading Profits: ${mt5_trading_profits:,.2f}")
            print(f"   📊 Client Interest Obligations: ${client_obligations:,.2f}")
            print(f"   📊 Net Fund Profitability: ${net_profitability:,.2f}")
            
            # Check if values are non-zero (indicating Salvador's data is included)
            if mt5_trading_profits != 0 or client_obligations != 0:
                print("   ✅ Cash Flow shows non-zero values (Salvador's data likely included)")
            else:
                print("   ❌ Cash Flow shows all zero values (Salvador's data missing)")
                return False
                
            # Check for detailed breakdown
            detailed_breakdown = response.get('detailed_breakdown', [])
            if detailed_breakdown:
                print(f"   ✅ Detailed breakdown available: {len(detailed_breakdown)} entries")
                
                # Look for Salvador in breakdown
                salvador_entries = []
                for entry in detailed_breakdown:
                    client_name = entry.get('client_name', '')
                    if 'Salvador' in client_name:
                        salvador_entries.append(entry)
                
                if salvador_entries:
                    print(f"   ✅ Salvador found in cash flow breakdown: {len(salvador_entries)} entries")
                else:
                    print("   ⚠️ Salvador not explicitly found in cash flow breakdown")
            else:
                print("   ⚠️ No detailed breakdown available")
                
        else:
            print("   ❌ Failed to get cash flow management data")
            return False
            
        return True

    def test_health_and_system_status(self) -> bool:
        """Test system health endpoints"""
        print("\n" + "="*80)
        print("🏥 TESTING SYSTEM HEALTH")
        print("="*80)
        
        # Test 1: Basic health check
        print("\n📊 Test 1: Basic Health Check")
        success, response = self.run_test(
            "Health Check",
            "GET",
            "api/health",
            200
        )
        
        if success:
            status = response.get('status', 'unknown')
            print(f"   ✅ System status: {status}")
        else:
            print("   ❌ Health check failed")
            return False
        
        # Test 2: Readiness check
        print("\n📊 Test 2: Readiness Check")
        success, response = self.run_test(
            "Readiness Check",
            "GET",
            "api/health/ready",
            200
        )
        
        if success:
            status = response.get('status', 'unknown')
            database = response.get('database', 'unknown')
            print(f"   ✅ Readiness status: {status}")
            print(f"   ✅ Database status: {database}")
        else:
            print("   ❌ Readiness check failed")
            return False
            
        return True

    def run_comprehensive_salvador_mt5_tests(self) -> bool:
        """Run all Salvador MT5 display tests"""
        print("\n" + "="*100)
        print("🎯 STARTING SALVADOR PALMA MT5 ACCOUNTS DISPLAY TESTING")
        print("="*100)
        print("Focus: Fix remaining display issues to show Salvador's MT5 accounts clearly")
        print("Expected Accounts:")
        print(f"  - DooTechnology (Login: {self.expected_accounts['dootechnology']['login']}) → BALANCE ${self.expected_accounts['dootechnology']['expected_amount']:,.2f}")
        print(f"  - VT Markets (Login: {self.expected_accounts['vt_markets']['login']}) → CORE ${self.expected_accounts['vt_markets']['expected_amount']:,.2f}")
        print("="*100)
        
        # Setup authentication
        if not self.setup_admin_authentication():
            print("\n❌ Admin authentication setup failed - cannot proceed")
            return False
        
        # Run all test suites
        test_suites = [
            ("Salvador Client Profile", self.test_salvador_client_profile),
            ("Salvador Investments", self.test_salvador_investments),
            ("MT5 Admin Accounts Endpoint", self.test_mt5_admin_accounts_endpoint),
            ("Fund Performance Dashboard", self.test_fund_performance_dashboard),
            ("Cash Flow Management", self.test_cash_flow_management),
            ("System Health", self.test_health_and_system_status)
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
        print("📊 SALVADOR MT5 DISPLAY TEST RESULTS SUMMARY")
        print("="*100)
        
        passed_suites = sum(1 for _, result in suite_results if result)
        total_suites = len(suite_results)
        
        for suite_name, result in suite_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"   {suite_name}: {status}")
        
        print(f"\n📈 Overall Results:")
        print(f"   Test Suites: {passed_suites}/{total_suites} passed ({passed_suites/total_suites*100:.1f}%)")
        print(f"   Individual Tests: {self.tests_passed}/{self.tests_run} passed ({self.tests_passed/self.tests_run*100:.1f}%)")
        
        # Determine overall success
        overall_success = passed_suites >= (total_suites * 0.8) and self.tests_passed >= (self.tests_run * 0.8)
        
        print("\n" + "="*100)
        print("🎯 SALVADOR MT5 DISPLAY ISSUES ASSESSMENT")
        print("="*100)
        
        if overall_success:
            print("✅ SALVADOR MT5 ACCOUNTS DISPLAY TESTING COMPLETED SUCCESSFULLY!")
            print("   Both DooTechnology and VT Markets accounts should be clearly visible")
            print("   Salvador Palma name should appear prominently in dashboards")
            print("   Investment amounts and linking should be correct")
        else:
            print("❌ SALVADOR MT5 ACCOUNTS DISPLAY ISSUES REMAIN")
            print("   Some display problems still need to be addressed")
            print("   Check failed test suites above for specific issues")
        
        return overall_success

def main():
    """Main test execution"""
    print("🎯 Salvador Palma MT5 Accounts Display Testing Suite")
    print("Testing MT5 account visibility and display issues for Salvador Palma")
    
    tester = SalvadorMT5DisplayTester()
    
    try:
        success = tester.run_comprehensive_salvador_mt5_tests()
        
        if success:
            print("\n✅ Salvador MT5 display tests completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Some Salvador MT5 display issues remain!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Testing failed with error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()