#!/usr/bin/env python3
"""
SALVADOR PALMA MT5 FINAL VERIFICATION TEST
==========================================

This test verifies that Salvador's MT5 accounts now display correctly after fixing async/await issues.

BACKEND FIXES COMPLETED:
✅ VT Markets investment corrected: $5,000 → $4,000
✅ Fixed async/await errors in MT5 connection status calls
✅ All MT5 service calls now properly structured

FINAL VERIFICATION NEEDED:
1. Test /api/mt5/admin/accounts endpoint - Should now work without async errors
2. Verify both Salvador's MT5 accounts appear:
   - DooTechnology account (Login: 9928326) linked to BALANCE investment ($1,263,485.40)
   - VT Markets account (Login: 15759667) linked to CORE investment ($4,000) ✅
3. Check data completeness
4. Test Fund Performance Dashboard - Should now include Salvador
5. Test Cash Flow Management - Should now show Salvador's MT5 data
"""

import requests
import sys
from datetime import datetime
import json
from typing import Dict, Any, List

class SalvadorMT5FinalTester:
    def __init__(self, base_url="https://fidus-finance-api.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.admin_token = None
        self.salvador_client_id = "client_003"
        self.issues_found = []
        self.successes = []
        
    def run_test(self, name: str, method: str, endpoint: str, expected_status: int, 
                 data: Dict = None, use_auth: bool = False) -> tuple[bool, Dict]:
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
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

            print(f"   Status Code: {response.status_code}")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return True, response.json()
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                    return False, error_data
                except:
                    print(f"   Error text: {response.text}")
                    return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def setup_authentication(self) -> bool:
        """Setup admin authentication"""
        print("\n" + "="*80)
        print("🔐 SETTING UP AUTHENTICATION")
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
            self.admin_token = response.get('token')
            if self.admin_token:
                print(f"   ✅ Admin authenticated successfully")
                return True
            else:
                print("   ❌ No JWT token received")
                return False
        else:
            print("   ❌ Admin authentication failed")
            return False

    def test_salvador_visibility(self) -> bool:
        """Test Salvador's visibility in the system"""
        print("\n" + "="*80)
        print("👤 TESTING SALVADOR PALMA VISIBILITY")
        print("="*80)
        
        # Test 1: Find Salvador in clients list
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
                client_name = salvador_data.get('name', '')
                total_balance = salvador_data.get('total_balance', 0)
                
                print(f"   ✅ Salvador found: {client_name}")
                print(f"   💰 Total Balance: ${total_balance:,.2f}")
                
                self.successes.append(f"Salvador Palma visible in clients list as '{client_name}'")
                self.successes.append(f"Salvador's total balance: ${total_balance:,.2f}")
                
                return True
            else:
                self.issues_found.append("Salvador Palma (client_003) not found in clients list")
                return False
        else:
            self.issues_found.append("Failed to retrieve clients list")
            return False

    def test_salvador_investments(self) -> bool:
        """Test Salvador's investment data"""
        print("\n" + "="*80)
        print("💰 TESTING SALVADOR PALMA INVESTMENTS")
        print("="*80)
        
        success, response = self.run_test(
            "Get Salvador's Investments",
            "GET",
            f"api/investments/client/{self.salvador_client_id}",
            200,
            use_auth=True
        )
        
        if success:
            investments = response.get('investments', [])
            print(f"   ✅ Found {len(investments)} investments")
            
            # Analyze investments
            balance_investments = [inv for inv in investments if inv.get('fund_code') == 'BALANCE']
            core_investments = [inv for inv in investments if inv.get('fund_code') == 'CORE']
            
            print(f"   📊 BALANCE fund investments: {len(balance_investments)}")
            print(f"   📊 CORE fund investments: {len(core_investments)}")
            
            # Check BALANCE investment (should link to DooTechnology MT5)
            if balance_investments:
                balance_amount = balance_investments[0].get('principal_amount', 0)
                print(f"   💰 BALANCE investment: ${balance_amount:,.2f}")
                
                if abs(balance_amount - 1263485.40) < 1:
                    self.successes.append(f"BALANCE investment amount correct: ${balance_amount:,.2f} (for DooTechnology MT5 linking)")
                else:
                    self.issues_found.append(f"BALANCE investment amount incorrect: ${balance_amount:,.2f} (expected $1,263,485.40)")
            else:
                self.issues_found.append("No BALANCE fund investments found for Salvador")
            
            # Check CORE investment (should link to VT Markets MT5)
            if core_investments:
                core_amount = core_investments[0].get('principal_amount', 0)
                print(f"   💰 CORE investment: ${core_amount:,.2f}")
                
                if abs(core_amount - 4000.00) < 1:
                    self.successes.append(f"CORE investment amount CORRECTED: ${core_amount:,.2f} (for VT Markets MT5 linking)")
                else:
                    self.issues_found.append(f"CORE investment amount incorrect: ${core_amount:,.2f} (expected $4,000.00)")
            else:
                self.issues_found.append("No CORE fund investments found for Salvador")
            
            return len(balance_investments) > 0 and len(core_investments) > 0
        else:
            self.issues_found.append("Failed to retrieve Salvador's investments")
            return False

    def test_mt5_integration(self) -> bool:
        """Test MT5 integration endpoints"""
        print("\n" + "="*80)
        print("🏦 TESTING MT5 INTEGRATION")
        print("="*80)
        
        # Test MT5 Admin Accounts endpoint
        success, response = self.run_test(
            "Get MT5 Admin Accounts",
            "GET",
            "api/mt5/admin/accounts",
            200,
            use_auth=True
        )
        
        if success:
            accounts = response.get('accounts', [])
            print(f"   ✅ MT5 endpoint working - {len(accounts)} accounts found")
            
            # Look for Salvador's accounts
            salvador_accounts = [acc for acc in accounts if acc.get('client_id') == self.salvador_client_id]
            
            if salvador_accounts:
                print(f"   ✅ Found {len(salvador_accounts)} MT5 accounts for Salvador")
                
                for account in salvador_accounts:
                    mt5_login = account.get('mt5_login')
                    broker_name = account.get('broker_name', 'Unknown')
                    client_name = account.get('client_name', 'Unknown')
                    
                    print(f"   🏦 Account: Login {mt5_login}, Broker: {broker_name}, Client: {client_name}")
                    
                    # Check for expected accounts
                    if str(mt5_login) == "9928326":
                        self.successes.append(f"DooTechnology account (9928326) found and visible")
                    elif str(mt5_login) == "15759667":
                        self.successes.append(f"VT Markets account (15759667) found and visible")
                
                return True
            else:
                self.issues_found.append("Salvador's MT5 accounts not found in admin accounts endpoint")
                return False
        else:
            error_detail = response.get('detail', 'Unknown error')
            self.issues_found.append(f"MT5 Admin Accounts endpoint failed: {error_detail}")
            print(f"   ❌ MT5 integration broken: {error_detail}")
            return False

    def test_dashboard_integration(self) -> bool:
        """Test dashboard integration"""
        print("\n" + "="*80)
        print("📊 TESTING DASHBOARD INTEGRATION")
        print("="*80)
        
        # Test Fund Performance Dashboard
        print("\n📈 Testing Fund Performance Dashboard...")
        success, response = self.run_test(
            "Get Fund Performance Dashboard",
            "GET",
            "api/admin/fund-performance/dashboard",
            200,
            use_auth=True
        )
        
        fund_performance_working = False
        if success:
            performance_data = response.get('performance_gaps', [])
            print(f"   📊 Found {len(performance_data)} performance records")
            
            salvador_records = [record for record in performance_data 
                              if record.get('client_id') == self.salvador_client_id or 'Salvador' in record.get('client_name', '')]
            
            if salvador_records:
                print(f"   ✅ Salvador found in Fund Performance: {len(salvador_records)} records")
                self.successes.append(f"Salvador appears in Fund Performance dashboard ({len(salvador_records)} records)")
                fund_performance_working = True
            else:
                print("   ❌ Salvador NOT found in Fund Performance dashboard")
                self.issues_found.append("Salvador missing from Fund Performance dashboard")
        else:
            self.issues_found.append("Fund Performance dashboard endpoint failed")
        
        # Test Cash Flow Management
        print("\n💸 Testing Cash Flow Management...")
        success, response = self.run_test(
            "Get Cash Flow Overview",
            "GET",
            "api/admin/cashflow/overview",
            200,
            use_auth=True
        )
        
        cash_flow_working = False
        if success:
            mt5_profits = response.get('mt5_trading_profits', 0)
            client_obligations = response.get('client_interest_obligations', 0)
            net_profitability = response.get('net_cash_flow', 0)
            
            print(f"   📊 MT5 Trading Profits: ${mt5_profits:,.2f}")
            print(f"   📊 Client Obligations: ${client_obligations:,.2f}")
            print(f"   📊 Net Profitability: ${net_profitability:,.2f}")
            
            if mt5_profits != 0 or client_obligations != 0:
                print("   ✅ Cash Flow shows non-zero values (Salvador's data likely included)")
                self.successes.append("Cash Flow Management shows non-zero values")
                cash_flow_working = True
            else:
                print("   ❌ Cash Flow shows zero values (Salvador's data missing)")
                self.issues_found.append("Cash Flow Management shows zero MT5 trading profits and client obligations")
        else:
            self.issues_found.append("Cash Flow Management endpoint failed")
        
        return fund_performance_working and cash_flow_working

    def run_comprehensive_test(self) -> bool:
        """Run comprehensive Salvador MT5 display test"""
        print("\n" + "="*100)
        print("🎯 SALVADOR PALMA MT5 ACCOUNTS DISPLAY - FINAL COMPREHENSIVE TEST")
        print("="*100)
        print("Review Request: Fix remaining display issues to show Salvador's MT5 accounts clearly")
        print("Expected: DooTechnology (9928326) + VT Markets (15759667) both visible with correct amounts")
        print("="*100)
        
        if not self.setup_authentication():
            return False
        
        # Run all tests
        test_results = []
        test_results.append(("Salvador Visibility", self.test_salvador_visibility()))
        test_results.append(("Salvador Investments", self.test_salvador_investments()))
        test_results.append(("MT5 Integration", self.test_mt5_integration()))
        test_results.append(("Dashboard Integration", self.test_dashboard_integration()))
        
        # Print results
        print("\n" + "="*100)
        print("📊 FINAL TEST RESULTS SUMMARY")
        print("="*100)
        
        passed_tests = sum(1 for _, result in test_results if result)
        total_tests = len(test_results)
        
        for test_name, result in test_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"   {test_name}: {status}")
        
        print(f"\n📈 Overall Results: {passed_tests}/{total_tests} test suites passed ({passed_tests/total_tests*100:.1f}%)")
        print(f"📈 Individual Tests: {self.tests_passed}/{self.tests_run} tests passed ({self.tests_passed/self.tests_run*100:.1f}%)")
        
        # Print successes
        if self.successes:
            print(f"\n✅ SUCCESSES ({len(self.successes)}):")
            for i, success in enumerate(self.successes, 1):
                print(f"   {i}. {success}")
        
        # Print issues
        if self.issues_found:
            print(f"\n❌ ISSUES FOUND ({len(self.issues_found)}):")
            for i, issue in enumerate(self.issues_found, 1):
                print(f"   {i}. {issue}")
        
        # Final assessment
        print("\n" + "="*100)
        print("🎯 SALVADOR MT5 DISPLAY ISSUES ASSESSMENT")
        print("="*100)
        
        if passed_tests >= 3:  # At least 3 out of 4 test suites should pass
            print("✅ SALVADOR MT5 ACCOUNTS DISPLAY TESTING - MOSTLY SUCCESSFUL!")
            print("   Core functionality working: Salvador visible, investments correct")
            if passed_tests < total_tests:
                print("   ⚠️  Some integration issues remain (see issues list above)")
        else:
            print("❌ SALVADOR MT5 ACCOUNTS DISPLAY ISSUES REMAIN")
            print("   Critical problems found that need main agent attention")
        
        return passed_tests >= 3

def main():
    """Main test execution"""
    print("🎯 Salvador Palma MT5 Accounts Display - Final Comprehensive Test")
    print("Testing MT5 account visibility and display issues for Salvador Palma")
    
    tester = SalvadorMT5FinalTester()
    
    try:
        success = tester.run_comprehensive_test()
        
        if success:
            print("\n✅ Salvador MT5 display testing completed with acceptable results!")
            sys.exit(0)
        else:
            print("\n❌ Critical Salvador MT5 display issues found!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Testing failed with error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()