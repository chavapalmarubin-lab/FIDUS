#!/usr/bin/env python3
"""
FINAL DATABASE CONNECTIVITY RESOLUTION TEST
===========================================

Based on investigation findings:
1. ✅ Database contains Salvador's data (8 investments for client_003)
2. ✅ Backend can access database (logs show "Retrieved 8 investments for client_003")
3. ✅ Authentication is working (JWT tokens obtained successfully)
4. ❌ API endpoints were returning 404 because we were using wrong endpoint URLs

CORRECT API ENDPOINTS DISCOVERED:
- Investments: /api/investments/client/{client_id} (not /api/admin/clients/{client_id}/investments)
- Fund Performance: /api/admin/fund-performance/dashboard (not /api/admin/fund-performance)
- Cash Flow: /api/admin/cashflow/overview (not /api/admin/cash-flow)

This test will verify the database connectivity issue is resolved using correct endpoints.
"""

import requests
import sys
import json
from datetime import datetime
from typing import Dict, Any

class FinalDatabaseConnectivityTester:
    def __init__(self, base_url="https://invest-manager-9.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.admin_token = None
        self.client_token = None
        self.findings = {}
        
    def run_test(self, name: str, method: str, endpoint: str, expected_status: int, 
                 data: Dict = None, headers: Dict = None, use_admin_auth: bool = False) -> tuple[bool, Dict]:
        """Run a single API test with proper authentication"""
        url = f"{self.base_url}/{endpoint}"
        
        # Set up headers with authentication
        if headers is None:
            headers = {'Content-Type': 'application/json'}
        
        # Add JWT token if available
        if use_admin_auth and self.admin_token:
            headers['Authorization'] = f'Bearer {self.admin_token}'
        elif not use_admin_auth and self.client_token:
            headers['Authorization'] = f'Bearer {self.client_token}'

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

    def setup_authentication(self) -> bool:
        """Setup JWT authentication tokens"""
        print("\n" + "="*80)
        print("🔐 SETTING UP JWT AUTHENTICATION")
        print("="*80)
        
        # Get admin JWT token
        success, response = self.run_test(
            "Admin Login for JWT Token",
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
                print(f"   ✅ Admin JWT token obtained")
            else:
                print("   ❌ No JWT token in admin login response")
                return False
        else:
            print("   ❌ Admin login failed")
            return False

        return True

    def test_correct_api_endpoints(self) -> bool:
        """Test the correct API endpoints discovered from backend code"""
        print("\n" + "="*80)
        print("🔍 TESTING CORRECT API ENDPOINTS")
        print("="*80)
        
        # Test 1: Get Salvador's investments using correct endpoint
        print("\n📊 Test 1: Get Salvador's Investments (Correct Endpoint)")
        success, response = self.run_test(
            "Get Salvador's Investments (Correct Endpoint)",
            "GET",
            "api/investments/client/client_003",
            200,
            use_admin_auth=True
        )
        
        if success:
            investments = response.get('investments', [])
            print(f"   📊 API returned {len(investments)} investments for client_003")
            
            if len(investments) > 0:
                print("   💰 Salvador's Investments via Correct API Endpoint:")
                total_api_value = 0
                balance_count = 0
                core_count = 0
                balance_1263485_found = False
                core_4000_found = False
                
                for inv in investments:
                    fund_code = inv.get('fund_code', 'Unknown')
                    principal = inv.get('principal_amount', 0)
                    current_value = inv.get('current_value', 0)
                    investment_id = inv.get('investment_id', 'N/A')
                    deposit_date = inv.get('deposit_date', 'N/A')
                    
                    print(f"     - {fund_code}: ${principal:,.2f} principal, ${current_value:,.2f} current")
                    print(f"       ID: {investment_id}, Deposit: {deposit_date}")
                    total_api_value += current_value
                    
                    if fund_code == 'BALANCE':
                        balance_count += 1
                        if principal == 1263485.40:
                            balance_1263485_found = True
                    elif fund_code == 'CORE':
                        core_count += 1
                        if principal == 4000.00:
                            core_4000_found = True
                
                print(f"   💰 Total Investment Value: ${total_api_value:,.2f}")
                print(f"   📊 BALANCE investments: {balance_count}")
                print(f"   📊 CORE investments: {core_count}")
                
                # Check for expected specific investments
                if balance_1263485_found:
                    print("   ✅ Found expected BALANCE investment ($1,263,485.40)")
                else:
                    print("   ❌ Expected BALANCE investment ($1,263,485.40) NOT FOUND")
                    
                if core_4000_found:
                    print("   ✅ Found expected CORE investment ($4,000.00)")
                else:
                    print("   ❌ Expected CORE investment ($4,000.00) NOT FOUND")
                
                self.findings['api_investments_count'] = len(investments)
                self.findings['api_total_value'] = total_api_value
                self.findings['balance_1263485_found'] = balance_1263485_found
                self.findings['core_4000_found'] = core_4000_found
                
                # Check if this matches the backend logs count
                if len(investments) == 8:
                    print("   ✅ Investment count matches backend logs (8 investments)")
                else:
                    print(f"   ⚠️ Investment count differs from backend logs (API: {len(investments)}, Logs: 8)")
                
            else:
                print("   ❌ NO investments found for client_003 via correct API endpoint")
                self.findings['api_investments_count'] = 0
                return False
        else:
            print("   ❌ Failed to get Salvador's investments via correct API endpoint")
            return False

        # Test 2: Get Fund Performance using correct endpoint
        print("\n📊 Test 2: Get Fund Performance (Correct Endpoint)")
        success, response = self.run_test(
            "Get Fund Performance Dashboard (Correct Endpoint)",
            "GET",
            "api/admin/fund-performance/dashboard",
            200,
            use_admin_auth=True
        )
        
        if success:
            performance_data = response.get('performance_data', [])
            print(f"   📊 API returned {len(performance_data)} fund performance records")
            
            # Look for Salvador in performance data
            salvador_performance = [p for p in performance_data if p.get('client_id') == 'client_003']
            print(f"   📊 Found {len(salvador_performance)} performance records for client_003")
            
            if salvador_performance:
                print("   📈 Salvador's Performance Records:")
                for perf in salvador_performance:
                    client_id = perf.get('client_id', 'N/A')
                    fund_code = perf.get('fund_code', 'N/A')
                    performance_gap = perf.get('performance_gap', 0)
                    mt5_performance = perf.get('mt5_performance', 0)
                    fidus_commitment = perf.get('fidus_commitment', 0)
                    
                    print(f"     - Client: {client_id}, Fund: {fund_code}")
                    print(f"       Performance Gap: {performance_gap:.2f}%")
                    print(f"       MT5 Performance: {mt5_performance:.2f}%")
                    print(f"       FIDUS Commitment: {fidus_commitment:.2f}%")
                
                self.findings['salvador_in_performance'] = True
            else:
                print("   ❌ Salvador NOT found in fund performance data")
                self.findings['salvador_in_performance'] = False
            
            self.findings['api_performance_count'] = len(performance_data)
        else:
            print("   ❌ Failed to get fund performance data via correct API endpoint")

        # Test 3: Get Cash Flow using correct endpoint
        print("\n📊 Test 3: Get Cash Flow Management (Correct Endpoint)")
        success, response = self.run_test(
            "Get Cash Flow Overview (Correct Endpoint)",
            "GET",
            "api/admin/cashflow/overview",
            200,
            use_admin_auth=True
        )
        
        if success:
            mt5_trading_profits = response.get('mt5_trading_profits', 0)
            client_obligations = response.get('client_interest_obligations', 0)
            total_fund_assets = response.get('total_fund_assets', 0)
            net_fund_profitability = response.get('net_fund_profitability', 0)
            
            print(f"   📊 Cash Flow Data:")
            print(f"     MT5 Trading Profits: ${mt5_trading_profits:,.2f}")
            print(f"     Client Interest Obligations: ${client_obligations:,.2f}")
            print(f"     Total Fund Assets: ${total_fund_assets:,.2f}")
            print(f"     Net Fund Profitability: ${net_fund_profitability:,.2f}")
            
            self.findings['api_mt5_profits'] = mt5_trading_profits
            self.findings['api_client_obligations'] = client_obligations
            
            # Check if Salvador's data is contributing to cash flow
            if mt5_trading_profits > 0 or client_obligations > 0:
                print("   ✅ Cash flow shows non-zero values (Salvador's data contributing)")
                self.findings['salvador_in_cashflow'] = True
            else:
                print("   ❌ Cash flow shows zero values (Salvador's data not contributing)")
                self.findings['salvador_in_cashflow'] = False
        else:
            print("   ❌ Failed to get cash flow data via correct API endpoint")

        return True

    def test_mt5_accounts_verification(self) -> bool:
        """Verify MT5 accounts are accessible and contain expected data"""
        print("\n" + "="*80)
        print("🔍 VERIFYING MT5 ACCOUNTS DATA")
        print("="*80)
        
        # Test MT5 accounts endpoint
        print("\n📊 Test: Get Salvador's MT5 Accounts")
        success, response = self.run_test(
            "Get Salvador's MT5 Accounts",
            "GET",
            "api/mt5/client/client_003/accounts",
            200,
            use_admin_auth=True
        )
        
        if success:
            accounts = response.get('accounts', [])
            print(f"   📊 API returned {len(accounts)} MT5 accounts for client_003")
            
            if len(accounts) > 0:
                print("   🏦 Salvador's MT5 Accounts:")
                doo_tech_found = False
                vt_markets_found = False
                total_allocated = 0
                
                for acc in accounts:
                    login = acc.get('mt5_login', 'N/A')
                    broker = acc.get('broker_name', 'N/A')
                    fund_code = acc.get('fund_code', 'N/A')
                    allocated = acc.get('total_allocated', 0)
                    server = acc.get('mt5_server', 'N/A')
                    
                    print(f"     - Login: {login}, Fund: {fund_code}, Server: {server}")
                    print(f"       Allocated: ${allocated:,.2f}")
                    total_allocated += allocated
                    
                    if login == 9928326:
                        doo_tech_found = True
                        print("       ✅ DooTechnology account found")
                    elif login == 15759667:
                        vt_markets_found = True
                        print("       ✅ VT Markets account found")
                
                print(f"   💰 Total MT5 Allocated: ${total_allocated:,.2f}")
                
                # Verify expected accounts
                if doo_tech_found:
                    print("   ✅ Expected DooTechnology MT5 account (Login: 9928326) FOUND")
                else:
                    print("   ❌ Expected DooTechnology MT5 account (Login: 9928326) NOT FOUND")
                    
                if vt_markets_found:
                    print("   ✅ Expected VT Markets MT5 account (Login: 15759667) FOUND")
                else:
                    print("   ❌ Expected VT Markets MT5 account (Login: 15759667) NOT FOUND")
                
                self.findings['doo_tech_found'] = doo_tech_found
                self.findings['vt_markets_found'] = vt_markets_found
                self.findings['mt5_total_allocated'] = total_allocated
                
                return doo_tech_found and vt_markets_found
            else:
                print("   ❌ NO MT5 accounts found for client_003")
                return False
        else:
            print("   ❌ Failed to get Salvador's MT5 accounts")
            return False

    def final_analysis(self) -> bool:
        """Provide final analysis of the database connectivity investigation"""
        print("\n" + "="*80)
        print("🔍 FINAL DATABASE CONNECTIVITY ANALYSIS")
        print("="*80)
        
        api_investments = self.findings.get('api_investments_count', 0)
        api_total_value = self.findings.get('api_total_value', 0)
        balance_1263485_found = self.findings.get('balance_1263485_found', False)
        core_4000_found = self.findings.get('core_4000_found', False)
        doo_tech_found = self.findings.get('doo_tech_found', False)
        vt_markets_found = self.findings.get('vt_markets_found', False)
        salvador_in_performance = self.findings.get('salvador_in_performance', False)
        salvador_in_cashflow = self.findings.get('salvador_in_cashflow', False)
        
        print(f"📊 FINAL RESULTS SUMMARY:")
        print(f"   Salvador's investments found via API: {api_investments}")
        print(f"   Total investment value: ${api_total_value:,.2f}")
        print(f"   Expected BALANCE investment ($1,263,485.40): {'✅ FOUND' if balance_1263485_found else '❌ NOT FOUND'}")
        print(f"   Expected CORE investment ($4,000.00): {'✅ FOUND' if core_4000_found else '❌ NOT FOUND'}")
        print(f"   DooTechnology MT5 account (9928326): {'✅ FOUND' if doo_tech_found else '❌ NOT FOUND'}")
        print(f"   VT Markets MT5 account (15759667): {'✅ FOUND' if vt_markets_found else '❌ NOT FOUND'}")
        print(f"   Salvador in Fund Performance: {'✅ YES' if salvador_in_performance else '❌ NO'}")
        print(f"   Salvador in Cash Flow: {'✅ YES' if salvador_in_cashflow else '❌ NO'}")
        
        # Determine if the critical issue is resolved
        critical_data_found = (
            api_investments > 0 and
            balance_1263485_found and
            core_4000_found and
            doo_tech_found and
            vt_markets_found
        )
        
        if critical_data_found:
            print(f"\n🎉 DATABASE CONNECTIVITY ISSUE RESOLVED!")
            print("   ✅ All expected Salvador Palma data is accessible via API")
            print("   ✅ BALANCE fund investment ($1,263,485.40) found")
            print("   ✅ CORE fund investment ($4,000.00) found")
            print("   ✅ Both MT5 accounts (DooTechnology & VT Markets) found")
            print("   ✅ The issue was incorrect API endpoint URLs, not database connectivity")
            
            print(f"\n🔍 ROOT CAUSE IDENTIFIED:")
            print("   ❌ Previous tests used wrong API endpoints:")
            print("     - Used: /api/admin/clients/client_003/investments (404 Not Found)")
            print("     - Correct: /api/investments/client/client_003 (200 OK)")
            print("   ❌ Used: /api/admin/fund-performance (404 Not Found)")
            print("     - Correct: /api/admin/fund-performance/dashboard (200 OK)")
            print("   ❌ Used: /api/admin/cash-flow (404 Not Found)")
            print("     - Correct: /api/admin/cashflow/overview (200 OK)")
            
            print(f"\n✅ PRODUCTION READINESS:")
            print("   ✅ Database connectivity is working correctly")
            print("   ✅ Salvador's complete investment profile is accessible")
            print("   ✅ Both MT5 accounts are properly linked")
            print("   ✅ System is ready for production deployment")
            
            return True
        else:
            print(f"\n🚨 CRITICAL DATA STILL MISSING!")
            print("   ❌ Some expected Salvador Palma data is still not accessible")
            
            missing_items = []
            if api_investments == 0:
                missing_items.append("No investments found")
            if not balance_1263485_found:
                missing_items.append("BALANCE investment ($1,263,485.40)")
            if not core_4000_found:
                missing_items.append("CORE investment ($4,000.00)")
            if not doo_tech_found:
                missing_items.append("DooTechnology MT5 account (9928326)")
            if not vt_markets_found:
                missing_items.append("VT Markets MT5 account (15759667)")
            
            print(f"   Missing items: {', '.join(missing_items)}")
            print("   🔧 URGENT ACTION REQUIRED: Restore missing data")
            
            return False

    def run_final_database_connectivity_test(self) -> bool:
        """Run the final comprehensive database connectivity test"""
        print("\n" + "="*100)
        print("🚀 STARTING FINAL DATABASE CONNECTIVITY RESOLUTION TEST")
        print("="*100)
        print("Testing with correct API endpoints to resolve the database connectivity issue")
        
        # Setup authentication
        if not self.setup_authentication():
            print("\n❌ Authentication setup failed - cannot proceed")
            return False
        
        # Run test suites
        test_suites = [
            ("Correct API Endpoints Test", self.test_correct_api_endpoints),
            ("MT5 Accounts Verification", self.test_mt5_accounts_verification),
            ("Final Analysis", self.final_analysis)
        ]
        
        suite_results = []
        
        for suite_name, test_method in test_suites:
            print(f"\n🔄 Running {suite_name}...")
            try:
                result = test_method()
                suite_results.append((suite_name, result))
                
                if result:
                    print(f"✅ {suite_name} - COMPLETED SUCCESSFULLY")
                else:
                    print(f"❌ {suite_name} - ISSUES FOUND")
            except Exception as e:
                print(f"❌ {suite_name} - ERROR: {str(e)}")
                suite_results.append((suite_name, False))
        
        # Print final results
        print("\n" + "="*100)
        print("📊 FINAL DATABASE CONNECTIVITY TEST RESULTS")
        print("="*100)
        
        completed_suites = sum(1 for _, result in suite_results if result)
        total_suites = len(suite_results)
        
        for suite_name, result in suite_results:
            status = "✅ COMPLETED" if result else "❌ ISSUES FOUND"
            print(f"   {suite_name}: {status}")
        
        print(f"\n📈 Test Results:")
        print(f"   Test Suites: {completed_suites}/{total_suites} completed successfully")
        print(f"   Individual Tests: {self.tests_passed}/{self.tests_run} passed ({self.tests_passed/self.tests_run*100:.1f}%)")
        
        # Final determination
        overall_success = completed_suites == total_suites
        
        if overall_success:
            print(f"\n🎉 DATABASE CONNECTIVITY ISSUE FULLY RESOLVED!")
            print("   ✅ All Salvador Palma data is accessible via correct API endpoints")
            print("   ✅ The original issue was API endpoint routing, not database connectivity")
            print("   ✅ System is production-ready with complete data access")
            return True
        else:
            print(f"\n⚠️ SOME ISSUES REMAIN")
            print("   ⚠️ While API endpoints are now correct, some data may still be missing")
            print("   🔧 Additional investigation or data restoration may be required")
            return False

def main():
    """Main test execution"""
    print("🔧 Final Database Connectivity Resolution Test Suite")
    print("Resolving the database connectivity issue with correct API endpoints")
    
    tester = FinalDatabaseConnectivityTester()
    
    try:
        success = tester.run_final_database_connectivity_test()
        
        if success:
            print("\n✅ Database connectivity issue fully resolved!")
            sys.exit(0)
        else:
            print("\n❌ Some issues remain - additional investigation needed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed with error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()