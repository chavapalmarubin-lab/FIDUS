#!/usr/bin/env python3
"""
SALVADOR PALMA VT MARKETS DATA CORRECTION TEST
==============================================

CRITICAL DATA CORRECTION: Fix Salvador Palma's VT Markets investment amount from incorrect value to $4,000 USD.

USER REPORT: VT Markets investment should be $4,000 USD, not $860,448.65

URGENT CORRECTIONS NEEDED:
1. Correct Salvador's Investment Data - VT Markets should be $4,000 USD
2. Update Database Records - Find and correct the principal amount
3. Fix Related Calculations - MT5 performance calculations
4. Verify Data Accuracy - Test that VT Markets shows $4,000 in all areas
5. Fix MT5 Account Display Issues - Make accounts visible with correct values

This test specifically validates the data correction and ensures Salvador's
VT Markets investment shows the correct $4,000 amount across all systems.
"""

import requests
import sys
import json
from datetime import datetime
from typing import Dict, Any, List

class SalvadorVTMarketsDataTester:
    def __init__(self, base_url="https://fidus-workspace-2.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.admin_user = None
        self.salvador_client_id = "client_003"  # Salvador Palma's client ID
        self.salvador_data = {}
        self.mt5_accounts = []
        self.investments = []
        
    def run_test(self, name: str, method: str, endpoint: str, expected_status: int, 
                 data: Dict = None, headers: Dict = None, use_auth: bool = True) -> tuple[bool, Dict]:
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        if headers is None:
            headers = {'Content-Type': 'application/json'}
        
        # Add JWT token for authenticated endpoints
        if use_auth and self.admin_user and 'token' in self.admin_user:
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
            },
            use_auth=False  # Don't use auth for login endpoint
        )
        if success:
            self.admin_user = response
            print(f"   ✅ Admin logged in: {response.get('name', 'Unknown')} (ID: {response.get('id')})")
            return True
        else:
            print("   ❌ Admin login failed - cannot proceed with testing")
            return False

    def test_salvador_profile_verification(self) -> bool:
        """Test 1: Verify Salvador Palma's profile exists and is accessible"""
        print("\n" + "="*80)
        print("👤 TEST 1: SALVADOR PALMA PROFILE VERIFICATION")
        print("="*80)
        
        # Get all clients to find Salvador
        success, response = self.run_test(
            "Get All Clients",
            "GET",
            "api/clients/all",
            200
        )
        
        if not success:
            print("   ❌ Failed to get clients list")
            return False
            
        clients = response.get('clients', [])
        salvador = None
        
        for client in clients:
            if client.get('id') == self.salvador_client_id or 'SALVADOR' in client.get('name', '').upper():
                salvador = client
                break
        
        if not salvador:
            print(f"   ❌ Salvador Palma not found in clients list")
            return False
            
        self.salvador_data = salvador
        print(f"   ✅ Salvador Palma found: {salvador.get('name')} (ID: {salvador.get('id')})")
        print(f"   📧 Email: {salvador.get('email')}")
        print(f"   💰 Total Balance: ${salvador.get('total_balance', 0):,.2f}")
        
        return True

    def test_salvador_investments_analysis(self) -> bool:
        """Test 2: Analyze Salvador's current investments"""
        print("\n" + "="*80)
        print("💰 TEST 2: SALVADOR'S INVESTMENTS ANALYSIS")
        print("="*80)
        
        # Get Salvador's investments
        success, response = self.run_test(
            "Get Salvador's Investments",
            "GET",
            f"api/investments/client/{self.salvador_client_id}",
            200
        )
        
        if not success:
            print("   ❌ Failed to get Salvador's investments")
            return False
            
        investments = response.get('investments', [])
        self.investments = investments
        
        print(f"   📊 Total investments found: {len(investments)}")
        
        if not investments:
            print("   ❌ No investments found for Salvador")
            return False
        
        # Analyze each investment
        total_value = 0
        vt_markets_investment = None
        doo_technology_investment = None
        
        for investment in investments:
            fund_code = investment.get('fund_code', 'Unknown')
            principal = investment.get('principal_amount', 0)
            current_value = investment.get('current_value', 0)
            investment_id = investment.get('investment_id', 'Unknown')
            
            print(f"   💼 {fund_code} Fund:")
            print(f"      - Investment ID: {investment_id}")
            print(f"      - Principal: ${principal:,.2f}")
            print(f"      - Current Value: ${current_value:,.2f}")
            
            total_value += current_value
            
            # Look for specific investments based on amounts
            if principal == 1263485.40:  # DooTechnology BALANCE fund
                doo_technology_investment = investment
                print(f"      ✅ IDENTIFIED: DooTechnology BALANCE fund investment")
            elif principal == 4000.00:  # Expected VT Markets amount
                vt_markets_investment = investment
                print(f"      ✅ IDENTIFIED: VT Markets investment (CORRECT AMOUNT)")
            elif principal == 860448.65:  # Incorrect VT Markets amount
                vt_markets_investment = investment
                print(f"      ❌ IDENTIFIED: VT Markets investment (INCORRECT AMOUNT - NEEDS CORRECTION)")
        
        print(f"   💰 Total Portfolio Value: ${total_value:,.2f}")
        
        # Store findings for later tests
        self.doo_technology_investment = doo_technology_investment
        self.vt_markets_investment = vt_markets_investment
        
        return True

    def test_mt5_accounts_investigation(self) -> bool:
        """Test 3: Investigate Salvador's MT5 accounts"""
        print("\n" + "="*80)
        print("🏦 TEST 3: SALVADOR'S MT5 ACCOUNTS INVESTIGATION")
        print("="*80)
        
        # Get Salvador's MT5 accounts
        success, response = self.run_test(
            "Get Salvador's MT5 Accounts",
            "GET",
            f"api/mt5/client/{self.salvador_client_id}/accounts",
            200
        )
        
        if not success:
            print("   ❌ Failed to get Salvador's MT5 accounts")
            return False
            
        accounts = response.get('accounts', [])
        self.mt5_accounts = accounts
        
        print(f"   🏦 Total MT5 accounts found: {len(accounts)}")
        
        if not accounts:
            print("   ❌ No MT5 accounts found for Salvador")
            return False
        
        # Analyze each MT5 account
        doo_technology_account = None
        vt_markets_account = None
        
        for account in accounts:
            mt5_login = account.get('mt5_login', 'Unknown')
            broker = account.get('broker', 'Unknown')
            server = account.get('mt5_server', 'Unknown')
            fund_code = account.get('fund_code', 'Unknown')
            total_allocated = account.get('total_allocated', 0)
            current_equity = account.get('current_equity', 0)
            investment_ids = account.get('investment_ids', [])
            
            print(f"   🏦 MT5 Account:")
            print(f"      - Login: {mt5_login}")
            print(f"      - Broker: {broker}")
            print(f"      - Server: {server}")
            print(f"      - Fund: {fund_code}")
            print(f"      - Allocated: ${total_allocated:,.2f}")
            print(f"      - Equity: ${current_equity:,.2f}")
            print(f"      - Investment IDs: {investment_ids}")
            
            # Identify accounts based on login numbers
            if mt5_login == 9928326:  # DooTechnology account
                doo_technology_account = account
                print(f"      ✅ IDENTIFIED: DooTechnology account (Login: 9928326)")
            elif mt5_login == 15759667:  # VT Markets account
                vt_markets_account = account
                print(f"      ✅ IDENTIFIED: VT Markets account (Login: 15759667)")
        
        # Store findings
        self.doo_technology_account = doo_technology_account
        self.vt_markets_account = vt_markets_account
        
        # Verify expected accounts exist
        if not doo_technology_account:
            print("   ❌ DooTechnology account (Login: 9928326) NOT FOUND")
            return False
            
        if not vt_markets_account:
            print("   ❌ VT Markets account (Login: 15759667) NOT FOUND")
            return False
            
        print("   ✅ Both expected MT5 accounts found")
        return True

    def test_investment_mt5_linking(self) -> bool:
        """Test 4: Verify investment-to-MT5 account linking"""
        print("\n" + "="*80)
        print("🔗 TEST 4: INVESTMENT-TO-MT5 ACCOUNT LINKING VERIFICATION")
        print("="*80)
        
        if not hasattr(self, 'doo_technology_account') or not hasattr(self, 'vt_markets_account'):
            print("   ❌ MT5 accounts not available from previous test")
            return False
            
        # Check DooTechnology account linking
        doo_account = self.doo_technology_account
        doo_investment_ids = doo_account.get('investment_ids', [])
        
        print(f"   🏦 DooTechnology Account (Login: 9928326):")
        print(f"      - Investment IDs: {doo_investment_ids}")
        
        if doo_investment_ids and len(doo_investment_ids) > 0:
            print(f"      ✅ Linked to {len(doo_investment_ids)} investment(s)")
            
            # Verify BALANCE fund investment is linked
            if hasattr(self, 'doo_technology_investment') and self.doo_technology_investment:
                balance_investment_id = self.doo_technology_investment.get('investment_id')
                if balance_investment_id in doo_investment_ids:
                    print(f"      ✅ BALANCE fund investment properly linked")
                else:
                    print(f"      ❌ BALANCE fund investment NOT linked")
                    return False
        else:
            print(f"      ❌ No investments linked (Investment ID: None)")
            return False
        
        # Check VT Markets account linking
        vt_account = self.vt_markets_account
        vt_investment_ids = vt_account.get('investment_ids', [])
        
        print(f"   🏦 VT Markets Account (Login: 15759667):")
        print(f"      - Investment IDs: {vt_investment_ids}")
        
        if vt_investment_ids and len(vt_investment_ids) > 0:
            print(f"      ✅ Linked to {len(vt_investment_ids)} investment(s)")
            
            # Check if VT Markets investment is properly linked
            if hasattr(self, 'vt_markets_investment') and self.vt_markets_investment:
                vt_investment_id = self.vt_markets_investment.get('investment_id')
                if vt_investment_id in vt_investment_ids:
                    print(f"      ✅ VT Markets investment properly linked")
                else:
                    print(f"      ❌ VT Markets investment NOT linked")
                    return False
        else:
            print(f"      ❌ No investments linked (Investment ID: None)")
            return False
        
        return True

    def test_fund_performance_dashboard(self) -> bool:
        """Test 5: Check Fund Performance Dashboard for Salvador's data"""
        print("\n" + "="*80)
        print("📈 TEST 5: FUND PERFORMANCE DASHBOARD VERIFICATION")
        print("="*80)
        
        # Get fund performance data
        success, response = self.run_test(
            "Get Fund Performance Dashboard",
            "GET",
            "api/admin/fund-performance/dashboard",
            200
        )
        
        if not success:
            print("   ❌ Failed to get fund performance data")
            return False
            
        performance_data = response.get('performance_data', [])
        
        print(f"   📊 Total performance records: {len(performance_data)}")
        
        # Look for Salvador's data
        salvador_records = []
        for record in performance_data:
            client_id = record.get('client_id', '')
            client_name = record.get('client_name', '')
            
            if client_id == self.salvador_client_id or 'SALVADOR' in client_name.upper():
                salvador_records.append(record)
        
        print(f"   👤 Salvador's performance records: {len(salvador_records)}")
        
        if not salvador_records:
            print("   ❌ Salvador NOT found in Fund Performance Dashboard")
            return False
        
        # Analyze Salvador's performance records
        for record in salvador_records:
            fund_code = record.get('fund_code', 'Unknown')
            fidus_commitment = record.get('fidus_commitment', 0)
            mt5_performance = record.get('mt5_performance', 0)
            performance_gap = record.get('performance_gap', 0)
            
            print(f"   📈 {fund_code} Fund Performance:")
            print(f"      - FIDUS Commitment: ${fidus_commitment:,.2f}")
            print(f"      - MT5 Performance: ${mt5_performance:,.2f}")
            print(f"      - Performance Gap: ${performance_gap:,.2f}")
            
            # Check for VT Markets specific data
            if fund_code == 'CORE' and fidus_commitment == 4000.00:
                print(f"      ✅ VT Markets CORE fund shows CORRECT $4,000 commitment")
            elif fund_code == 'BALANCE' and fidus_commitment == 1263485.40:
                print(f"      ✅ DooTechnology BALANCE fund shows correct commitment")
        
        print("   ✅ Salvador found in Fund Performance Dashboard")
        return True

    def test_cash_flow_management(self) -> bool:
        """Test 6: Check Cash Flow Management calculations"""
        print("\n" + "="*80)
        print("💰 TEST 6: CASH FLOW MANAGEMENT VERIFICATION")
        print("="*80)
        
        # Get cash flow data
        success, response = self.run_test(
            "Get Cash Flow Management Data",
            "GET",
            "api/admin/cashflow/overview",
            200
        )
        
        if not success:
            print("   ❌ Failed to get cash flow data")
            return False
            
        cash_flow = response.get('cash_flow', {})
        
        # Check key cash flow metrics
        mt5_trading_profits = cash_flow.get('mt5_trading_profits', 0)
        client_obligations = cash_flow.get('client_interest_obligations', 0)
        net_profitability = cash_flow.get('net_fund_profitability', 0)
        
        print(f"   💰 Cash Flow Metrics:")
        print(f"      - MT5 Trading Profits: ${mt5_trading_profits:,.2f}")
        print(f"      - Client Obligations: ${client_obligations:,.2f}")
        print(f"      - Net Fund Profitability: ${net_profitability:,.2f}")
        
        # Verify non-zero values (indicating Salvador's data is included)
        if mt5_trading_profits > 0:
            print("   ✅ MT5 Trading Profits show positive values")
        else:
            print("   ❌ MT5 Trading Profits are zero (Salvador's data may not be included)")
            return False
            
        if client_obligations > 0:
            print("   ✅ Client Obligations show positive values")
        else:
            print("   ❌ Client Obligations are zero (Salvador's data may not be included)")
            return False
        
        return True

    def test_vt_markets_amount_verification(self) -> bool:
        """Test 7: Specific VT Markets $4,000 amount verification"""
        print("\n" + "="*80)
        print("🎯 TEST 7: VT MARKETS $4,000 AMOUNT VERIFICATION")
        print("="*80)
        
        # Check if we found VT Markets investment in earlier test
        if not hasattr(self, 'vt_markets_investment') or not self.vt_markets_investment:
            print("   ❌ VT Markets investment not identified in previous tests")
            return False
        
        vt_investment = self.vt_markets_investment
        principal = vt_investment.get('principal_amount', 0)
        current_value = vt_investment.get('current_value', 0)
        fund_code = vt_investment.get('fund_code', 'Unknown')
        
        print(f"   🎯 VT Markets Investment Details:")
        print(f"      - Fund Code: {fund_code}")
        print(f"      - Principal Amount: ${principal:,.2f}")
        print(f"      - Current Value: ${current_value:,.2f}")
        
        # Check if amount is correct
        if principal == 4000.00:
            print("   ✅ VT Markets investment shows CORRECT $4,000 principal amount")
            
            # Also check MT5 account allocation
            if hasattr(self, 'vt_markets_account') and self.vt_markets_account:
                vt_account = self.vt_markets_account
                allocated = vt_account.get('total_allocated', 0)
                
                print(f"   🏦 VT Markets MT5 Account Allocation: ${allocated:,.2f}")
                
                if allocated == 4000.00 or abs(allocated - 4000.00) < 100:  # Allow small variance
                    print("   ✅ VT Markets MT5 account shows correct allocation")
                else:
                    print(f"   ❌ VT Markets MT5 account allocation incorrect: Expected ~$4,000, got ${allocated:,.2f}")
                    return False
            
            return True
        elif principal == 860448.65:
            print("   ❌ VT Markets investment shows INCORRECT $860,448.65 amount - NEEDS CORRECTION")
            print("   🚨 CRITICAL: This is the exact issue reported by the user!")
            return False
        else:
            print(f"   ❌ VT Markets investment shows unexpected amount: ${principal:,.2f}")
            return False

    def test_system_health_endpoints(self) -> bool:
        """Test 8: Verify system health endpoints are working"""
        print("\n" + "="*80)
        print("🏥 TEST 8: SYSTEM HEALTH VERIFICATION")
        print("="*80)
        
        # Test basic health endpoint
        success, response = self.run_test(
            "Basic Health Check",
            "GET",
            "api/health",
            200,
            use_auth=False  # Health endpoints don't require auth
        )
        
        if not success:
            print("   ❌ Basic health check failed")
            return False
        
        print("   ✅ Basic health check passed")
        
        # Test readiness endpoint
        success, response = self.run_test(
            "Readiness Check",
            "GET",
            "api/health/ready",
            200,
            use_auth=False  # Health endpoints don't require auth
        )
        
        if success:
            print("   ✅ Readiness check passed")
            database_status = response.get('database', 'unknown')
            print(f"      - Database: {database_status}")
        else:
            print("   ❌ Readiness check failed")
            return False
        
        return True

    def run_salvador_vt_markets_tests(self) -> bool:
        """Run all Salvador VT Markets data correction tests"""
        print("\n" + "="*100)
        print("🎯 STARTING SALVADOR PALMA VT MARKETS DATA CORRECTION TESTING")
        print("="*100)
        print("OBJECTIVE: Verify VT Markets investment shows $4,000 USD (not $860,448.65)")
        print("="*100)
        
        # Setup authentication
        if not self.setup_admin_authentication():
            print("\n❌ Authentication setup failed - cannot proceed")
            return False
        
        # Run all test suites
        test_suites = [
            ("Salvador Profile Verification", self.test_salvador_profile_verification),
            ("Salvador Investments Analysis", self.test_salvador_investments_analysis),
            ("MT5 Accounts Investigation", self.test_mt5_accounts_investigation),
            ("Investment-MT5 Linking Verification", self.test_investment_mt5_linking),
            ("Fund Performance Dashboard", self.test_fund_performance_dashboard),
            ("Cash Flow Management", self.test_cash_flow_management),
            ("VT Markets $4,000 Amount Verification", self.test_vt_markets_amount_verification),
            ("System Health Verification", self.test_system_health_endpoints)
        ]
        
        suite_results = []
        critical_issues = []
        
        for suite_name, test_method in test_suites:
            print(f"\n🔄 Running {suite_name}...")
            try:
                result = test_method()
                suite_results.append((suite_name, result))
                
                if result:
                    print(f"✅ {suite_name} - PASSED")
                else:
                    print(f"❌ {suite_name} - FAILED")
                    if "VT Markets" in suite_name or "Amount Verification" in suite_name:
                        critical_issues.append(suite_name)
            except Exception as e:
                print(f"❌ {suite_name} - ERROR: {str(e)}")
                suite_results.append((suite_name, False))
                if "VT Markets" in suite_name or "Amount Verification" in suite_name:
                    critical_issues.append(suite_name)
        
        # Print final results
        print("\n" + "="*100)
        print("📊 SALVADOR VT MARKETS DATA CORRECTION TEST RESULTS")
        print("="*100)
        
        passed_suites = sum(1 for _, result in suite_results if result)
        total_suites = len(suite_results)
        
        for suite_name, result in suite_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"   {suite_name}: {status}")
        
        print(f"\n📈 Overall Results:")
        print(f"   Test Suites: {passed_suites}/{total_suites} passed ({passed_suites/total_suites*100:.1f}%)")
        print(f"   Individual Tests: {self.tests_passed}/{self.tests_run} passed ({self.tests_passed/self.tests_run*100:.1f}%)")
        
        # Critical issue analysis
        if critical_issues:
            print(f"\n🚨 CRITICAL ISSUES FOUND:")
            for issue in critical_issues:
                print(f"   ❌ {issue}")
            print(f"\n💡 RECOMMENDED ACTIONS:")
            print(f"   1. Check Salvador's VT Markets investment principal amount in database")
            print(f"   2. Correct amount from $860,448.65 to $4,000.00 if needed")
            print(f"   3. Update MT5 account allocation to match corrected amount")
            print(f"   4. Verify Fund Performance and Cash Flow calculations reflect correction")
        
        # Determine overall success
        overall_success = passed_suites >= (total_suites * 0.75) and len(critical_issues) == 0
        
        if overall_success:
            print(f"\n🎉 SALVADOR VT MARKETS DATA CORRECTION TESTING COMPLETED SUCCESSFULLY!")
            print("   VT Markets investment data appears to be correct.")
        else:
            print(f"\n⚠️ SALVADOR VT MARKETS DATA CORRECTION TESTING COMPLETED WITH ISSUES")
            print("   VT Markets investment data may need correction.")
        
        return overall_success

def main():
    """Main test execution"""
    print("🎯 Salvador Palma VT Markets Data Correction Testing Suite")
    print("Testing specific data correction: VT Markets investment should be $4,000 USD")
    
    tester = SalvadorVTMarketsDataTester()
    
    try:
        success = tester.run_salvador_vt_markets_tests()
        
        if success:
            print("\n✅ Salvador VT Markets data correction tests completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Salvador VT Markets data correction tests found issues!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Testing failed with error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()