#!/usr/bin/env python3
"""
Fund Performance Management System Backend Testing
Testing the corrected Fund Performance Management System that uses MT5 data as primary source
"""

import requests
import sys
from datetime import datetime
import json

class FundPerformanceTester:
    def __init__(self, base_url="https://mt5-integration.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.admin_token = None
        self.admin_user = None
        
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
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=15)

            print(f"   Status Code: {response.status_code}")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response keys: {list(response_data.keys()) if isinstance(response_data, dict) else 'Non-dict response'}")
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
        print("\n🔐 AUTHENTICATION TESTING")
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
            self.admin_token = response.get('token')
            print(f"   Admin logged in: {response.get('name', 'Unknown')}")
            if self.admin_token:
                print(f"   JWT Token received: {self.admin_token[:20]}...")
        return success

    def get_auth_headers(self):
        """Get headers with authentication token"""
        headers = {'Content-Type': 'application/json'}
        if self.admin_token:
            headers['Authorization'] = f'Bearer {self.admin_token}'
        return headers

    def test_fund_performance_dashboard(self):
        """Test GET /api/admin/fund-performance/dashboard"""
        print("\n📊 FUND PERFORMANCE DASHBOARD TESTING")
        
        success, response = self.run_test(
            "Fund Performance Dashboard",
            "GET",
            "api/admin/fund-performance/dashboard",
            200,
            headers=self.get_auth_headers()
        )
        
        if success:
            # Verify dashboard structure
            expected_keys = ['success', 'dashboard', 'generated_at']
            missing_keys = [key for key in expected_keys if key not in response]
            if missing_keys:
                print(f"   ⚠️  Missing keys in response: {missing_keys}")
            else:
                print(f"   ✅ All required keys present")
            
            # Check dashboard content
            dashboard = response.get('dashboard', {})
            if dashboard:
                print(f"   Dashboard keys: {list(dashboard.keys())}")
                
                # Look for performance gaps
                if 'performance_gaps' in dashboard:
                    gaps = dashboard['performance_gaps']
                    print(f"   Performance gaps found: {len(gaps)}")
                    
                # Look for risk summary
                if 'risk_summary' in dashboard:
                    risk = dashboard['risk_summary']
                    print(f"   Risk summary: {risk}")
                    
                # Look for action items
                if 'action_items' in dashboard:
                    actions = dashboard['action_items']
                    print(f"   Action items: {len(actions)}")
            else:
                print(f"   ⚠️  Empty dashboard data")
                
        return success

    def test_fund_performance_gaps(self):
        """Test GET /api/admin/fund-performance/gaps"""
        print("\n📈 FUND PERFORMANCE GAPS TESTING")
        
        success, response = self.run_test(
            "Fund Performance Gaps",
            "GET",
            "api/admin/fund-performance/gaps",
            200,
            headers=self.get_auth_headers()
        )
        
        if success:
            # Verify gaps structure
            expected_keys = ['success', 'performance_gaps', 'total_gaps', 'generated_at']
            missing_keys = [key for key in expected_keys if key not in response]
            if missing_keys:
                print(f"   ⚠️  Missing keys in response: {missing_keys}")
            else:
                print(f"   ✅ All required keys present")
            
            # Check performance gaps
            gaps = response.get('performance_gaps', [])
            total_gaps = response.get('total_gaps', 0)
            print(f"   Total gaps reported: {total_gaps}")
            print(f"   Gaps array length: {len(gaps)}")
            
            # Look for Salvador Palma's BALANCE fund gap
            salvador_gap = None
            for gap in gaps:
                if gap.get('client_id') == 'client_003' and gap.get('fund_code') == 'BALANCE':
                    salvador_gap = gap
                    break
            
            if salvador_gap:
                print(f"   ✅ Found Salvador Palma BALANCE fund gap:")
                print(f"      Expected performance: {salvador_gap.get('expected_performance')}")
                print(f"      Actual MT5 performance: {salvador_gap.get('actual_mt5_performance')}")
                print(f"      Gap amount: {salvador_gap.get('gap_amount')}")
                print(f"      Gap percentage: {salvador_gap.get('gap_percentage')}%")
                print(f"      Risk level: {salvador_gap.get('risk_level')}")
                print(f"      Action required: {salvador_gap.get('action_required')}")
                
                # Verify the expected 425.7% gap
                gap_percentage = salvador_gap.get('gap_percentage', 0)
                if abs(gap_percentage - 425.7) < 50:  # Allow some tolerance
                    print(f"   ✅ Gap percentage matches expected range (~425.7%)")
                else:
                    print(f"   ⚠️  Gap percentage {gap_percentage}% differs from expected 425.7%")
            else:
                print(f"   ⚠️  Salvador Palma BALANCE fund gap not found")
                print(f"   Available gaps: {[(g.get('client_id'), g.get('fund_code')) for g in gaps]}")
                
        return success

    def test_fund_commitments(self):
        """Test GET /api/admin/fund-commitments"""
        print("\n📋 FUND COMMITMENTS TESTING")
        
        success, response = self.run_test(
            "Fund Commitments",
            "GET",
            "api/admin/fund-commitments",
            200,
            headers=self.get_auth_headers()
        )
        
        if success:
            # Verify commitments structure
            expected_keys = ['success', 'fund_commitments', 'generated_at']
            missing_keys = [key for key in expected_keys if key not in response]
            if missing_keys:
                print(f"   ⚠️  Missing keys in response: {missing_keys}")
            else:
                print(f"   ✅ All required keys present")
            
            # Check fund commitments
            commitments = response.get('fund_commitments', {})
            expected_funds = ['CORE', 'BALANCE', 'DYNAMIC', 'UNLIMITED']
            
            print(f"   Available funds: {list(commitments.keys())}")
            
            for fund in expected_funds:
                if fund in commitments:
                    fund_data = commitments[fund]
                    print(f"   ✅ {fund} fund found:")
                    print(f"      Monthly return: {fund_data.get('monthly_return')}%")
                    print(f"      Redemption frequency: {fund_data.get('redemption_frequency')}")
                    print(f"      Risk level: {fund_data.get('risk_level')}")
                    print(f"      Guaranteed: {fund_data.get('guaranteed')}")
                    
                    # Verify BALANCE fund specifically (2.5% monthly)
                    if fund == 'BALANCE':
                        monthly_return = fund_data.get('monthly_return')
                        if monthly_return == 2.5:
                            print(f"      ✅ BALANCE fund monthly return matches expected 2.5%")
                        else:
                            print(f"      ⚠️  BALANCE fund monthly return {monthly_return}% differs from expected 2.5%")
                else:
                    print(f"   ❌ {fund} fund missing from commitments")
                    
        return success

    def test_client_fund_performance(self):
        """Test GET /api/admin/fund-performance/client/client_003 (Salvador Palma)"""
        print("\n👤 CLIENT FUND PERFORMANCE TESTING")
        
        client_id = "client_003"  # Salvador Palma
        success, response = self.run_test(
            f"Client Fund Performance - {client_id}",
            "GET",
            f"api/admin/fund-performance/client/{client_id}",
            200,
            headers=self.get_auth_headers()
        )
        
        if success:
            # Verify client comparison structure
            expected_keys = ['success', 'client_comparison', 'generated_at']
            missing_keys = [key for key in expected_keys if key not in response]
            if missing_keys:
                print(f"   ⚠️  Missing keys in response: {missing_keys}")
            else:
                print(f"   ✅ All required keys present")
            
            # Check client comparison data
            comparison = response.get('client_comparison', {})
            if comparison:
                print(f"   Client comparison keys: {list(comparison.keys())}")
                
                # Look for Salvador's investment details
                if 'client_info' in comparison:
                    client_info = comparison['client_info']
                    print(f"   Client name: {client_info.get('name')}")
                    print(f"   Client ID: {client_info.get('client_id')}")
                
                # Look for BALANCE fund investment
                if 'investments' in comparison:
                    investments = comparison['investments']
                    balance_investment = None
                    
                    for inv in investments:
                        if inv.get('fund_code') == 'BALANCE':
                            balance_investment = inv
                            break
                    
                    if balance_investment:
                        print(f"   ✅ Found BALANCE fund investment:")
                        print(f"      Principal: ${balance_investment.get('principal_amount'):,.2f}")
                        print(f"      Current value: ${balance_investment.get('current_value'):,.2f}")
                        print(f"      Deposit date: {balance_investment.get('deposit_date')}")
                        
                        # Verify expected values
                        principal = balance_investment.get('principal_amount', 0)
                        current_value = balance_investment.get('current_value', 0)
                        
                        if abs(principal - 100000) < 1000:  # $100K principal
                            print(f"      ✅ Principal matches expected $100K")
                        else:
                            print(f"      ⚠️  Principal ${principal:,.2f} differs from expected $100K")
                            
                        if abs(current_value - 117500) < 5000:  # $117.5K current value
                            print(f"      ✅ Current value matches expected $117.5K")
                        else:
                            print(f"      ⚠️  Current value ${current_value:,.2f} differs from expected $117.5K")
                    else:
                        print(f"   ⚠️  BALANCE fund investment not found")
                
                # Look for MT5 account details
                if 'mt5_accounts' in comparison:
                    mt5_accounts = comparison['mt5_accounts']
                    doo_account = None
                    
                    for account in mt5_accounts:
                        if account.get('broker_code') == 'dootechnology':
                            doo_account = account
                            break
                    
                    if doo_account:
                        print(f"   ✅ Found DooTechnology MT5 account:")
                        print(f"      MT5 Login: {doo_account.get('mt5_login')}")
                        print(f"      Server: {doo_account.get('mt5_server')}")
                        print(f"      Allocated: ${doo_account.get('total_allocated'):,.2f}")
                        
                        # Verify expected MT5 login 9928326
                        mt5_login = doo_account.get('mt5_login')
                        if mt5_login == 9928326:
                            print(f"      ✅ MT5 login matches expected 9928326")
                        else:
                            print(f"      ⚠️  MT5 login {mt5_login} differs from expected 9928326")
                    else:
                        print(f"   ⚠️  DooTechnology MT5 account not found")
                        
                # Look for performance comparison
                if 'performance_comparison' in comparison:
                    perf = comparison['performance_comparison']
                    print(f"   Performance comparison:")
                    print(f"      FIDUS commitment: {perf.get('fidus_expected')}%")
                    print(f"      MT5 actual: {perf.get('mt5_actual')}%")
                    print(f"      Gap: {perf.get('gap_percentage')}%")
            else:
                print(f"   ⚠️  Empty client comparison data")
                
        return success

    def test_salvador_palma_data_verification(self):
        """Verify Salvador Palma's specific data matches expectations"""
        print("\n🎯 SALVADOR PALMA DATA VERIFICATION")
        
        # Test client investment data
        success1, response1 = self.run_test(
            "Salvador Palma Investment Data",
            "GET",
            "api/investments/client/client_003",
            200,
            headers=self.get_auth_headers()
        )
        
        if success1:
            investments = response1.get('investments', [])
            balance_investment = None
            
            for inv in investments:
                if inv.get('fund_code') == 'BALANCE':
                    balance_investment = inv
                    break
            
            if balance_investment:
                print(f"   ✅ Salvador's BALANCE investment verified:")
                print(f"      Investment ID: {balance_investment.get('investment_id')}")
                print(f"      Principal: ${balance_investment.get('principal_amount'):,.2f}")
                print(f"      Current value: ${balance_investment.get('current_value'):,.2f}")
                print(f"      Deposit date: {balance_investment.get('deposit_date')}")
                print(f"      Interest start: {balance_investment.get('interest_start_date')}")
                
                # Verify deposit date is 2024-12-19
                deposit_date = balance_investment.get('deposit_date', '')
                if '2024-12-19' in deposit_date:
                    print(f"      ✅ Deposit date matches expected 2024-12-19")
                else:
                    print(f"      ⚠️  Deposit date {deposit_date} differs from expected 2024-12-19")
                    
                # Verify interest start is 2025-02-19 (2 months after deposit)
                interest_start = balance_investment.get('interest_start_date', '')
                if '2025-02-19' in interest_start:
                    print(f"      ✅ Interest start matches expected 2025-02-19")
                else:
                    print(f"      ⚠️  Interest start {interest_start} differs from expected 2025-02-19")
            else:
                print(f"   ❌ Salvador's BALANCE investment not found")
                return False
        
        # Test MT5 account data
        success2, response2 = self.run_test(
            "Salvador Palma MT5 Accounts",
            "GET",
            "api/mt5/client/client_003/accounts",
            200,
            headers=self.get_auth_headers()
        )
        
        if success2:
            mt5_accounts = response2.get('accounts', [])
            doo_account = None
            
            for account in mt5_accounts:
                if account.get('broker_code') == 'dootechnology' and account.get('fund_code') == 'BALANCE':
                    doo_account = account
                    break
            
            if doo_account:
                print(f"   ✅ Salvador's DooTechnology MT5 account verified:")
                print(f"      Account ID: {doo_account.get('account_id')}")
                print(f"      MT5 Login: {doo_account.get('mt5_login')}")
                print(f"      Server: {doo_account.get('mt5_server')}")
                print(f"      Broker: {doo_account.get('broker_name')}")
                
                # Verify MT5 login is 9928326
                mt5_login = doo_account.get('mt5_login')
                if mt5_login == 9928326:
                    print(f"      ✅ MT5 login matches expected 9928326")
                else:
                    print(f"      ⚠️  MT5 login {mt5_login} differs from expected 9928326")
                    
                # Verify server is DooTechnology-Live
                server = doo_account.get('mt5_server', '')
                if 'DooTechnology-Live' in server:
                    print(f"      ✅ Server matches expected DooTechnology-Live")
                else:
                    print(f"      ⚠️  Server {server} differs from expected DooTechnology-Live")
            else:
                print(f"   ❌ Salvador's DooTechnology MT5 account not found")
                return False
        
        return success1 and success2

    def run_comprehensive_fund_performance_tests(self):
        """Run all fund performance management tests"""
        print("🚀 STARTING FUND PERFORMANCE MANAGEMENT SYSTEM TESTING")
        print("=" * 80)
        
        # Authentication
        if not self.test_admin_login():
            print("\n❌ CRITICAL: Admin authentication failed - cannot proceed with tests")
            return False
        
        # Core fund performance endpoints
        tests = [
            self.test_fund_performance_dashboard,
            self.test_fund_performance_gaps,
            self.test_fund_commitments,
            self.test_client_fund_performance,
            self.test_salvador_palma_data_verification
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                print(f"\n❌ Test {test.__name__} failed with exception: {str(e)}")
        
        # Final summary
        print("\n" + "=" * 80)
        print("📊 FUND PERFORMANCE TESTING SUMMARY")
        print("=" * 80)
        print(f"Total tests run: {self.tests_run}")
        print(f"Tests passed: {self.tests_passed}")
        print(f"Tests failed: {self.tests_run - self.tests_passed}")
        print(f"Success rate: {(self.tests_passed / self.tests_run * 100):.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("\n🎉 ALL FUND PERFORMANCE TESTS PASSED!")
            return True
        else:
            print(f"\n⚠️  {self.tests_run - self.tests_passed} TESTS FAILED - Review issues above")
            return False

if __name__ == "__main__":
    tester = FundPerformanceTester()
    success = tester.run_comprehensive_fund_performance_tests()
    sys.exit(0 if success else 1)