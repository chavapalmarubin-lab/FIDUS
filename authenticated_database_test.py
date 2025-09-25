#!/usr/bin/env python3
"""
AUTHENTICATED DATABASE CONNECTIVITY TEST
========================================

This test uses proper JWT authentication to investigate the database connectivity issue.
The previous test confirmed:
- Database contains 6 investments for client_003 (Salvador Palma)
- API endpoints return 401 Unauthorized without proper JWT tokens
- Need to test with proper authentication to see if API can access the data
"""

import requests
import sys
import json
from datetime import datetime
from typing import Dict, Any

class AuthenticatedDatabaseTester:
    def __init__(self, base_url="https://fidus-workspace-1.preview.emergentagent.com"):
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
        print(f"   Auth: {'Admin JWT' if use_admin_auth and self.admin_token else 'Client JWT' if self.client_token else 'None'}")
        
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
                print(f"   ✅ Admin JWT token obtained: {self.admin_token[:50]}...")
            else:
                print("   ❌ No JWT token in admin login response")
                return False
        else:
            print("   ❌ Admin login failed")
            return False

        # Get client JWT token (Salvador Palma)
        success, response = self.run_test(
            "Salvador Palma Login for JWT Token",
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
            if self.client_token:
                print(f"   ✅ Client JWT token obtained: {self.client_token[:50]}...")
            else:
                print("   ❌ No JWT token in client login response")
        else:
            print("   ❌ Salvador Palma login failed")
            
        return True

    def test_authenticated_api_endpoints(self) -> bool:
        """Test API endpoints with proper JWT authentication"""
        print("\n" + "="*80)
        print("🔍 TESTING AUTHENTICATED API ENDPOINTS")
        print("="*80)
        
        # Test 1: Get all clients with admin authentication
        print("\n📊 Test 1: Get All Clients (Admin Authenticated)")
        success, response = self.run_test(
            "Get All Clients (Admin Auth)",
            "GET",
            "api/admin/clients",
            200,
            use_admin_auth=True
        )
        
        if success:
            clients = response.get('clients', [])
            print(f"   📊 API returned {len(clients)} clients")
            
            # Look for Salvador Palma
            salvador_found = False
            for client in clients:
                if client.get('id') == 'client_003' or 'SALVADOR' in client.get('name', '').upper():
                    salvador_found = True
                    print(f"   ✅ Found Salvador Palma via API:")
                    print(f"     Name: {client.get('name', 'N/A')}")
                    print(f"     Email: {client.get('email', 'N/A')}")
                    print(f"     ID: {client.get('id', 'N/A')}")
                    print(f"     Total Balance: ${client.get('total_balance', 0):,.2f}")
                    break
            
            if not salvador_found:
                print("   ❌ Salvador Palma NOT FOUND via authenticated API")
            
            self.findings['api_clients_count'] = len(clients)
            self.findings['api_salvador_found'] = salvador_found
        else:
            print("   ❌ Failed to get clients via authenticated API")
            return False

        # Test 2: Get Salvador's investments directly
        print("\n📊 Test 2: Get Salvador's Investments (Admin Auth)")
        success, response = self.run_test(
            "Get Salvador's Investments (Admin Auth)",
            "GET",
            "api/admin/clients/client_003/investments",
            200,
            use_admin_auth=True
        )
        
        if success:
            investments = response.get('investments', [])
            print(f"   📊 API returned {len(investments)} investments for client_003")
            
            if len(investments) > 0:
                print("   💰 Salvador's Investments via Authenticated API:")
                total_api_value = 0
                balance_count = 0
                core_count = 0
                
                for inv in investments:
                    fund_code = inv.get('fund_code', 'Unknown')
                    principal = inv.get('principal_amount', 0)
                    current_value = inv.get('current_value', 0)
                    investment_id = inv.get('investment_id', 'N/A')
                    
                    print(f"     - {fund_code}: ${principal:,.2f} principal, ${current_value:,.2f} current (ID: {investment_id})")
                    total_api_value += current_value
                    
                    if fund_code == 'BALANCE':
                        balance_count += 1
                    elif fund_code == 'CORE':
                        core_count += 1
                
                print(f"   💰 Total API Investment Value: ${total_api_value:,.2f}")
                print(f"   📊 BALANCE investments: {balance_count}")
                print(f"   📊 CORE investments: {core_count}")
                
                # Check for expected amounts
                balance_1263485 = any(inv.get('principal_amount') == 1263485.40 for inv in investments if inv.get('fund_code') == 'BALANCE')
                core_4000 = any(inv.get('principal_amount') == 4000.00 for inv in investments if inv.get('fund_code') == 'CORE')
                
                if balance_1263485:
                    print("   ✅ Found expected BALANCE investment ($1,263,485.40)")
                else:
                    print("   ❌ Expected BALANCE investment ($1,263,485.40) NOT FOUND")
                    
                if core_4000:
                    print("   ✅ Found expected CORE investment ($4,000.00)")
                else:
                    print("   ❌ Expected CORE investment ($4,000.00) NOT FOUND")
                
                self.findings['api_investments_count'] = len(investments)
                self.findings['api_total_value'] = total_api_value
                self.findings['api_balance_count'] = balance_count
                self.findings['api_core_count'] = core_count
            else:
                print("   ❌ NO investments found for client_003 via authenticated API")
                self.findings['api_investments_count'] = 0
                self.findings['api_total_value'] = 0
        else:
            print("   ❌ Failed to get Salvador's investments via authenticated API")

        # Test 3: Get Salvador's MT5 accounts
        print("\n📊 Test 3: Get Salvador's MT5 Accounts (Admin Auth)")
        success, response = self.run_test(
            "Get Salvador's MT5 Accounts (Admin Auth)",
            "GET",
            "api/mt5/client/client_003/accounts",
            200,
            use_admin_auth=True
        )
        
        if success:
            accounts = response.get('accounts', [])
            print(f"   📊 API returned {len(accounts)} MT5 accounts for client_003")
            
            if len(accounts) > 0:
                print("   🏦 Salvador's MT5 Accounts via Authenticated API:")
                doo_tech_found = False
                vt_markets_found = False
                
                for acc in accounts:
                    login = acc.get('mt5_login', 'N/A')
                    broker = acc.get('broker_name', 'N/A')
                    fund_code = acc.get('fund_code', 'N/A')
                    allocated = acc.get('total_allocated', 0)
                    server = acc.get('mt5_server', 'N/A')
                    
                    print(f"     - Login: {login}, Broker: {broker}, Fund: {fund_code}")
                    print(f"       Server: {server}, Allocated: ${allocated:,.2f}")
                    
                    if login == 9928326:
                        doo_tech_found = True
                    elif login == 15759667:
                        vt_markets_found = True
                
                if doo_tech_found:
                    print("   ✅ Found expected DooTechnology MT5 account (Login: 9928326)")
                else:
                    print("   ❌ Expected DooTechnology MT5 account (Login: 9928326) NOT FOUND")
                    
                if vt_markets_found:
                    print("   ✅ Found expected VT Markets MT5 account (Login: 15759667)")
                else:
                    print("   ❌ Expected VT Markets MT5 account (Login: 15759667) NOT FOUND")
                
                self.findings['api_mt5_count'] = len(accounts)
                self.findings['doo_tech_found'] = doo_tech_found
                self.findings['vt_markets_found'] = vt_markets_found
            else:
                print("   ❌ NO MT5 accounts found for client_003 via authenticated API")
                self.findings['api_mt5_count'] = 0
        else:
            print("   ❌ Failed to get Salvador's MT5 accounts via authenticated API")

        # Test 4: Test Fund Performance Dashboard
        print("\n📊 Test 4: Test Fund Performance Dashboard (Admin Auth)")
        success, response = self.run_test(
            "Get Fund Performance Data (Admin Auth)",
            "GET",
            "api/admin/fund-performance",
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
                    fund_code = perf.get('fund_code', 'N/A')
                    performance_gap = perf.get('performance_gap', 0)
                    print(f"     - {fund_code}: Performance Gap: {performance_gap:.2f}%")
            
            self.findings['api_performance_count'] = len(performance_data)
            self.findings['api_salvador_performance_count'] = len(salvador_performance)
        else:
            print("   ❌ Failed to get fund performance data via authenticated API")

        # Test 5: Test Cash Flow Management
        print("\n📊 Test 5: Test Cash Flow Management (Admin Auth)")
        success, response = self.run_test(
            "Get Cash Flow Data (Admin Auth)",
            "GET",
            "api/admin/cash-flow",
            200,
            use_admin_auth=True
        )
        
        if success:
            mt5_trading_profits = response.get('mt5_trading_profits', 0)
            client_obligations = response.get('client_interest_obligations', 0)
            total_fund_assets = response.get('total_fund_assets', 0)
            
            print(f"   📊 Cash Flow Data:")
            print(f"     MT5 Trading Profits: ${mt5_trading_profits:,.2f}")
            print(f"     Client Obligations: ${client_obligations:,.2f}")
            print(f"     Total Fund Assets: ${total_fund_assets:,.2f}")
            
            self.findings['api_mt5_profits'] = mt5_trading_profits
            self.findings['api_client_obligations'] = client_obligations
            
            # Check if Salvador's data is contributing to cash flow
            if mt5_trading_profits > 0 or client_obligations > 0:
                print("   ✅ Cash flow shows non-zero values (Salvador's data may be contributing)")
            else:
                print("   ❌ Cash flow shows zero values (Salvador's data not contributing)")
        else:
            print("   ❌ Failed to get cash flow data via authenticated API")

        return True

    def test_health_endpoints(self) -> bool:
        """Test system health endpoints"""
        print("\n" + "="*80)
        print("🔍 TESTING SYSTEM HEALTH ENDPOINTS")
        print("="*80)
        
        # Test basic health
        print("\n📊 Test 1: Basic Health Check")
        success, response = self.run_test(
            "Basic Health Check",
            "GET",
            "api/health",
            200
        )
        
        if success:
            status = response.get('status', 'unknown')
            service = response.get('service', 'unknown')
            print(f"   ✅ Health Status: {status}")
            print(f"   ✅ Service: {service}")

        # Test readiness check
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
            print(f"   ✅ Readiness Status: {status}")
            print(f"   ✅ Database Status: {database}")
            
            if database == 'connected':
                print("   ✅ Database connection confirmed via health endpoint")
            else:
                print("   ❌ Database connection issue detected via health endpoint")

        return True

    def analyze_findings(self) -> bool:
        """Analyze all findings and determine the root cause"""
        print("\n" + "="*80)
        print("🔍 ANALYZING AUTHENTICATED API FINDINGS")
        print("="*80)
        
        api_investments = self.findings.get('api_investments_count', 0)
        api_mt5 = self.findings.get('api_mt5_count', 0)
        api_total_value = self.findings.get('api_total_value', 0)
        salvador_found = self.findings.get('api_salvador_found', False)
        
        print(f"📊 AUTHENTICATED API RESULTS:")
        print(f"   Salvador Palma found in clients: {salvador_found}")
        print(f"   Salvador's investments via API: {api_investments}")
        print(f"   Salvador's MT5 accounts via API: {api_mt5}")
        print(f"   Total investment value via API: ${api_total_value:,.2f}")
        
        # Compare with database findings from previous test
        print(f"\n📊 COMPARISON WITH DATABASE FINDINGS:")
        print(f"   Database had 6 investments for client_003")
        print(f"   Database had 6 MT5 accounts for client_003")
        print(f"   Database total value was $3,802,456.20")
        
        if api_investments > 0:
            print(f"\n✅ AUTHENTICATION RESOLVED THE ISSUE!")
            print(f"   ✅ With proper JWT authentication, API can access Salvador's data")
            print(f"   ✅ Found {api_investments} investments via authenticated API")
            
            if api_investments == 6:
                print(f"   ✅ Investment count matches database (6 investments)")
            else:
                print(f"   ⚠️ Investment count differs from database (API: {api_investments}, DB: 6)")
            
            # Check for expected investments
            balance_count = self.findings.get('api_balance_count', 0)
            core_count = self.findings.get('api_core_count', 0)
            
            if balance_count > 0 and core_count > 0:
                print(f"   ✅ Found both BALANCE ({balance_count}) and CORE ({core_count}) investments")
            else:
                print(f"   ⚠️ Missing expected investment types (BALANCE: {balance_count}, CORE: {core_count})")
            
            return True
        else:
            print(f"\n❌ AUTHENTICATION DID NOT RESOLVE THE ISSUE!")
            print(f"   ❌ Even with proper JWT authentication, API returns 0 investments")
            print(f"   ❌ This indicates a deeper database connectivity or API routing issue")
            return False

    def run_comprehensive_authenticated_test(self) -> bool:
        """Run comprehensive authenticated database connectivity test"""
        print("\n" + "="*100)
        print("🚀 STARTING COMPREHENSIVE AUTHENTICATED DATABASE CONNECTIVITY TEST")
        print("="*100)
        print("Testing with proper JWT authentication to determine if authentication was the issue")
        
        # Setup authentication
        if not self.setup_authentication():
            print("\n❌ Authentication setup failed - cannot proceed")
            return False
        
        # Run test suites
        test_suites = [
            ("Authenticated API Endpoints Test", self.test_authenticated_api_endpoints),
            ("System Health Endpoints Test", self.test_health_endpoints),
            ("Findings Analysis", self.analyze_findings)
        ]
        
        suite_results = []
        
        for suite_name, test_method in test_suites:
            print(f"\n🔄 Running {suite_name}...")
            try:
                result = test_method()
                suite_results.append((suite_name, result))
                
                if result:
                    print(f"✅ {suite_name} - COMPLETED")
                else:
                    print(f"❌ {suite_name} - ISSUES FOUND")
            except Exception as e:
                print(f"❌ {suite_name} - ERROR: {str(e)}")
                suite_results.append((suite_name, False))
        
        # Print final results
        print("\n" + "="*100)
        print("📊 AUTHENTICATED DATABASE CONNECTIVITY TEST RESULTS")
        print("="*100)
        
        completed_suites = sum(1 for _, result in suite_results if result)
        total_suites = len(suite_results)
        
        for suite_name, result in suite_results:
            status = "✅ COMPLETED" if result else "❌ ISSUES FOUND"
            print(f"   {suite_name}: {status}")
        
        print(f"\n📈 Test Results:")
        print(f"   Test Suites: {completed_suites}/{total_suites} completed")
        print(f"   Individual Tests: {self.tests_passed}/{self.tests_run} passed ({self.tests_passed/self.tests_run*100:.1f}%)")
        
        # Final determination
        api_investments = self.findings.get('api_investments_count', 0)
        
        if api_investments > 0:
            print(f"\n🎉 ISSUE RESOLVED WITH AUTHENTICATION!")
            print("   ✅ Salvador's data is accessible via API with proper JWT authentication")
            print("   ✅ The original issue was likely due to missing authentication in API calls")
            print("   ✅ Database connectivity is working correctly")
            
            # Check if we found the expected data
            balance_count = self.findings.get('api_balance_count', 0)
            core_count = self.findings.get('api_core_count', 0)
            
            if balance_count > 0 and core_count > 0:
                print("   ✅ Found expected BALANCE and CORE investments")
                print("   ✅ System is ready for production deployment")
                return True
            else:
                print("   ⚠️ Some expected investments may be missing")
                return False
        else:
            print(f"\n🚨 CRITICAL ISSUE PERSISTS!")
            print("   ❌ Even with proper authentication, Salvador's data is not accessible via API")
            print("   ❌ This indicates a serious database connectivity or API routing issue")
            print("   🔧 URGENT ACTION REQUIRED: Deep investigation of backend database connection")
            return False

def main():
    """Main test execution"""
    print("🔧 Authenticated Database Connectivity Test Suite")
    print("Testing database connectivity with proper JWT authentication")
    
    tester = AuthenticatedDatabaseTester()
    
    try:
        success = tester.run_comprehensive_authenticated_test()
        
        if success:
            print("\n✅ Database connectivity test completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Critical database connectivity issues persist!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed with error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()