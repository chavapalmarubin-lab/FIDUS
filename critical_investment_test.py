#!/usr/bin/env python3
"""
Critical Investment API Testing - Database Cleanup Verification
Testing specific endpoints after database cleanup to ensure correct data display.
"""

import requests
import sys
from datetime import datetime
import json

class CriticalInvestmentTester:
    def __init__(self, base_url="https://mt5-portal.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []
        self.critical_issues = []
        self.admin_token = None
        self.client_token = None

    def authenticate_admin(self):
        """Authenticate as admin to get JWT token"""
        print("\n🔐 Authenticating as admin...")
        
        success, response = self.run_test(
            "Admin Authentication",
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
                print(f"   ❌ No token received in response")
        
        return False

    def get_auth_headers(self):
        """Get authorization headers with JWT token"""
        if self.admin_token:
            return {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.admin_token}'
            }
        return {'Content-Type': 'application/json'}

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None, use_auth=False):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        if headers is None:
            headers = self.get_auth_headers() if use_auth else {'Content-Type': 'application/json'}

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
                self.failed_tests.append(f"{name}: Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                    return False, error_data
                except:
                    print(f"   Error text: {response.text}")
                    return False, {"error": response.text}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.failed_tests.append(f"{name}: {str(e)}")
            return False, {"error": str(e)}

    def test_salvador_investments(self):
        """Test Salvador's investments - Should show 2 BALANCE investments"""
        print("\n" + "="*80)
        print("🎯 TESTING SALVADOR PALMA INVESTMENTS (client_003)")
        print("Expected: 2 BALANCE investments totaling $1,763,485.40")
        print("="*80)
        
        success, response = self.run_test(
            "Salvador Palma Investments (client_003)",
            "GET",
            "api/investments/client/client_003",
            200
        )
        
        if success:
            investments = response.get('investments', [])
            portfolio_stats = response.get('portfolio_stats', {})
            
            print(f"\n📊 SALVADOR'S INVESTMENT ANALYSIS:")
            print(f"   Total Investments Found: {len(investments)}")
            
            if len(investments) == 0:
                self.critical_issues.append("❌ CRITICAL: Salvador has NO investments - Expected 2 BALANCE investments")
                print("   ❌ CRITICAL ISSUE: No investments found for Salvador!")
                return False
            
            # Analyze each investment
            balance_investments = 0
            total_value = 0
            
            for i, investment in enumerate(investments, 1):
                fund_code = investment.get('fund_code', 'Unknown')
                principal = investment.get('principal_amount', 0)
                current_value = investment.get('current_value', 0)
                status = investment.get('status', 'Unknown')
                
                print(f"   Investment {i}:")
                print(f"     Fund: {fund_code}")
                print(f"     Principal: ${principal:,.2f}")
                print(f"     Current Value: ${current_value:,.2f}")
                print(f"     Status: {status}")
                
                if fund_code == 'BALANCE':
                    balance_investments += 1
                
                total_value += current_value
            
            print(f"\n📈 PORTFOLIO SUMMARY:")
            print(f"   BALANCE Fund Investments: {balance_investments}")
            print(f"   Total Portfolio Value: ${total_value:,.2f}")
            print(f"   Expected Total Value: $1,763,485.40")
            
            # Validation checks
            if balance_investments != 2:
                self.critical_issues.append(f"❌ CRITICAL: Salvador has {balance_investments} BALANCE investments, expected 2")
                print(f"   ❌ CRITICAL: Expected 2 BALANCE investments, found {balance_investments}")
            else:
                print(f"   ✅ Correct number of BALANCE investments: {balance_investments}")
            
            # Check if total value is close to expected (allowing for interest accrual)
            expected_value = 1763485.40
            if abs(total_value - expected_value) > 100000:  # Allow $100k variance for interest
                self.critical_issues.append(f"❌ CRITICAL: Salvador's total value ${total_value:,.2f} differs significantly from expected ${expected_value:,.2f}")
                print(f"   ⚠️  Total value variance: ${abs(total_value - expected_value):,.2f}")
            else:
                print(f"   ✅ Total value within expected range")
            
            return len(investments) > 0 and balance_investments == 2
        
        return False

    def test_gerardo_investments(self):
        """Test Gerardo's investments - Should show NO investments"""
        print("\n" + "="*80)
        print("🎯 TESTING GERARDO BRIONES INVESTMENTS (client_001)")
        print("Expected: NO investments (should be empty)")
        print("="*80)
        
        success, response = self.run_test(
            "Gerardo Briones Investments (client_001)",
            "GET",
            "api/investments/client/client_001",
            200
        )
        
        if success:
            investments = response.get('investments', [])
            portfolio_stats = response.get('portfolio_stats', {})
            
            print(f"\n📊 GERARDO'S INVESTMENT ANALYSIS:")
            print(f"   Total Investments Found: {len(investments)}")
            
            if len(investments) > 0:
                self.critical_issues.append(f"❌ CRITICAL: Gerardo has {len(investments)} investments - Expected ZERO")
                print("   ❌ CRITICAL ISSUE: Gerardo should have NO investments after cleanup!")
                
                # Show what investments were found
                for i, investment in enumerate(investments, 1):
                    fund_code = investment.get('fund_code', 'Unknown')
                    principal = investment.get('principal_amount', 0)
                    current_value = investment.get('current_value', 0)
                    
                    print(f"   Unexpected Investment {i}:")
                    print(f"     Fund: {fund_code}")
                    print(f"     Principal: ${principal:,.2f}")
                    print(f"     Current Value: ${current_value:,.2f}")
                
                return False
            else:
                print("   ✅ CORRECT: Gerardo has NO investments as expected")
                return True
        
        return False

    def test_maria_investments(self):
        """Test Maria's investments - Should show NO investments"""
        print("\n" + "="*80)
        print("🎯 TESTING MARIA RODRIGUEZ INVESTMENTS (client_002)")
        print("Expected: NO investments (should be empty)")
        print("="*80)
        
        success, response = self.run_test(
            "Maria Rodriguez Investments (client_002)",
            "GET",
            "api/investments/client/client_002",
            200
        )
        
        if success:
            investments = response.get('investments', [])
            portfolio_stats = response.get('portfolio_stats', {})
            
            print(f"\n📊 MARIA'S INVESTMENT ANALYSIS:")
            print(f"   Total Investments Found: {len(investments)}")
            
            if len(investments) > 0:
                self.critical_issues.append(f"❌ CRITICAL: Maria has {len(investments)} investments - Expected ZERO")
                print("   ❌ CRITICAL ISSUE: Maria should have NO investments after cleanup!")
                
                # Show what investments were found
                for i, investment in enumerate(investments, 1):
                    fund_code = investment.get('fund_code', 'Unknown')
                    principal = investment.get('principal_amount', 0)
                    current_value = investment.get('current_value', 0)
                    
                    print(f"   Unexpected Investment {i}:")
                    print(f"     Fund: {fund_code}")
                    print(f"     Principal: ${principal:,.2f}")
                    print(f"     Current Value: ${current_value:,.2f}")
                
                return False
            else:
                print("   ✅ CORRECT: Maria has NO investments as expected")
                return True
        
        return False

    def test_admin_portfolio_summary(self):
        """Test admin portfolio summary - Should show correct total AUM from Salvador's investments only"""
        print("\n" + "="*80)
        print("🎯 TESTING ADMIN PORTFOLIO SUMMARY")
        print("Expected: Total AUM from Salvador's investments only")
        print("="*80)
        
        success, response = self.run_test(
            "Admin Portfolio Summary",
            "GET",
            "api/admin/portfolio-summary",
            200,
            use_auth=True
        )
        
        if success:
            aum = response.get('aum', 0)
            total_aum = response.get('total_aum', 0)  # Check both field names
            client_count = response.get('client_count', 0)
            allocation = response.get('allocation', {})
            
            # Use whichever AUM field is present
            actual_aum = aum if aum > 0 else total_aum
            
            print(f"\n📊 PORTFOLIO SUMMARY ANALYSIS:")
            print(f"   Total AUM: ${actual_aum:,.2f}")
            print(f"   Client Count: {client_count}")
            print(f"   Fund Allocation: {allocation}")
            
            # Expected values based on Salvador's investments
            expected_aum_min = 1500000  # Minimum expected (allowing for variations)
            expected_aum_max = 2000000  # Maximum expected (allowing for interest)
            
            if actual_aum == 0:
                self.critical_issues.append("❌ CRITICAL: Total AUM is $0 - Should show Salvador's investment value")
                print("   ❌ CRITICAL ISSUE: AUM is zero!")
                return False
            
            if actual_aum < expected_aum_min:
                self.critical_issues.append(f"❌ CRITICAL: AUM ${actual_aum:,.2f} is too low - Expected around $1.7M from Salvador")
                print(f"   ❌ AUM too low: ${actual_aum:,.2f}")
            elif actual_aum > expected_aum_max:
                self.critical_issues.append(f"❌ CRITICAL: AUM ${actual_aum:,.2f} is too high - Should only include Salvador")
                print(f"   ⚠️  AUM higher than expected: ${actual_aum:,.2f}")
            else:
                print(f"   ✅ AUM within expected range: ${actual_aum:,.2f}")
            
            # Check if BALANCE fund is properly represented in allocation
            balance_allocation = allocation.get('BALANCE', 0)
            if balance_allocation == 0:
                self.critical_issues.append("❌ CRITICAL: No BALANCE fund allocation - Salvador has BALANCE investments")
                print("   ❌ Missing BALANCE fund allocation")
            else:
                print(f"   ✅ BALANCE fund allocation: {balance_allocation}%")
            
            return actual_aum > 0 and expected_aum_min <= actual_aum <= expected_aum_max
        
        return False

    def test_mt5_salvador_status(self):
        """Test Salvador's MT5 status - Should show 2 MT5 accounts with real-time data"""
        print("\n" + "="*80)
        print("🎯 TESTING SALVADOR MT5 STATUS")
        print("Expected: 2 MT5 accounts with real-time data feeds")
        print("="*80)
        
        success, response = self.run_test(
            "Salvador MT5 Status Monitor",
            "GET",
            "api/mt5/monitor/salvador-status",
            200
        )
        
        if success:
            accounts = response.get('accounts', [])
            total_equity = response.get('total_equity', 0)
            total_allocated = response.get('total_allocated', 0)
            status = response.get('status', 'Unknown')
            
            print(f"\n📊 SALVADOR MT5 ANALYSIS:")
            print(f"   MT5 Accounts Found: {len(accounts)}")
            print(f"   Total Equity: ${total_equity:,.2f}")
            print(f"   Total Allocated: ${total_allocated:,.2f}")
            print(f"   Overall Status: {status}")
            
            if len(accounts) == 0:
                self.critical_issues.append("❌ CRITICAL: Salvador has NO MT5 accounts - Expected 2 accounts")
                print("   ❌ CRITICAL ISSUE: No MT5 accounts found!")
                return False
            
            # Analyze each MT5 account
            balance_accounts = 0
            
            for i, account in enumerate(accounts, 1):
                account_id = account.get('account_id', 'Unknown')
                fund_code = account.get('fund_code', 'Unknown')
                mt5_login = account.get('mt5_login', 'Unknown')
                mt5_server = account.get('mt5_server', 'Unknown')
                allocated = account.get('total_allocated', 0)
                equity = account.get('current_equity', 0)
                profit_loss = account.get('profit_loss', 0)
                account_status = account.get('status', 'Unknown')
                
                print(f"\n   MT5 Account {i}:")
                print(f"     Account ID: {account_id}")
                print(f"     Fund: {fund_code}")
                print(f"     MT5 Login: {mt5_login}")
                print(f"     MT5 Server: {mt5_server}")
                print(f"     Allocated: ${allocated:,.2f}")
                print(f"     Current Equity: ${equity:,.2f}")
                print(f"     P&L: ${profit_loss:,.2f}")
                print(f"     Status: {account_status}")
                
                if fund_code == 'BALANCE':
                    balance_accounts += 1
                
                # Check for real-time data indicators
                if equity > 0 and equity != allocated:
                    print(f"     ✅ Real-time data detected (equity ≠ allocated)")
                else:
                    print(f"     ⚠️  Static data (equity = allocated)")
            
            print(f"\n📈 MT5 SUMMARY:")
            print(f"   BALANCE Fund Accounts: {balance_accounts}")
            
            # Validation checks
            if len(accounts) != 2:
                self.critical_issues.append(f"❌ CRITICAL: Salvador has {len(accounts)} MT5 accounts, expected 2")
                print(f"   ❌ Expected 2 MT5 accounts, found {len(accounts)}")
            else:
                print(f"   ✅ Correct number of MT5 accounts: {len(accounts)}")
            
            if balance_accounts == 0:
                self.critical_issues.append("❌ CRITICAL: No BALANCE fund MT5 accounts found")
                print("   ❌ No BALANCE fund MT5 accounts")
            else:
                print(f"   ✅ BALANCE fund MT5 accounts: {balance_accounts}")
            
            return len(accounts) == 2 and balance_accounts > 0
        
        return False

    def test_api_response_formats(self):
        """Test that all API responses are properly formatted JSON"""
        print("\n" + "="*80)
        print("🎯 TESTING API RESPONSE FORMATS")
        print("Expected: All responses should be properly formatted JSON")
        print("="*80)
        
        endpoints_to_test = [
            ("Salvador Investments JSON", "api/investments/client/client_003"),
            ("Gerardo Investments JSON", "api/investments/client/client_001"),
            ("Maria Investments JSON", "api/investments/client/client_002"),
            ("Portfolio Summary JSON", "api/admin/portfolio-summary"),
            ("MT5 Salvador Status JSON", "api/mt5/monitor/salvador-status")
        ]
        
        all_valid = True
        
        for name, endpoint in endpoints_to_test:
            try:
                url = f"{self.base_url}/{endpoint}"
                response = requests.get(url, timeout=10)
                
                print(f"\n   Testing {name}:")
                print(f"     Status: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        json_data = response.json()
                        print(f"     ✅ Valid JSON response")
                        print(f"     Keys: {list(json_data.keys()) if isinstance(json_data, dict) else 'Non-dict response'}")
                    except json.JSONDecodeError as e:
                        print(f"     ❌ Invalid JSON: {str(e)}")
                        self.critical_issues.append(f"❌ CRITICAL: {name} returns invalid JSON")
                        all_valid = False
                else:
                    print(f"     ⚠️  Non-200 status: {response.status_code}")
                    
            except Exception as e:
                print(f"     ❌ Request failed: {str(e)}")
                self.critical_issues.append(f"❌ CRITICAL: {name} request failed: {str(e)}")
                all_valid = False
        
        return all_valid

    def run_all_tests(self):
        """Run all critical investment tests"""
        print("🚀 STARTING CRITICAL INVESTMENT API TESTING")
        print("Testing endpoints after database cleanup to verify correct data display")
        print("="*80)
        
        # Run all tests
        test_results = {
            "Salvador Investments": self.test_salvador_investments(),
            "Gerardo Investments": self.test_gerardo_investments(),
            "Maria Investments": self.test_maria_investments(),
            "Admin Portfolio Summary": self.test_admin_portfolio_summary(),
            "MT5 Salvador Status": self.test_mt5_salvador_status(),
            "API Response Formats": self.test_api_response_formats()
        }
        
        # Print final summary
        print("\n" + "="*80)
        print("📋 CRITICAL INVESTMENT TESTING SUMMARY")
        print("="*80)
        
        print(f"\nTests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        print(f"\n🎯 CRITICAL TEST RESULTS:")
        for test_name, result in test_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"   {test_name}: {status}")
        
        if self.critical_issues:
            print(f"\n🚨 CRITICAL ISSUES FOUND ({len(self.critical_issues)}):")
            for issue in self.critical_issues:
                print(f"   {issue}")
        else:
            print(f"\n🎉 NO CRITICAL ISSUES FOUND!")
        
        if self.failed_tests:
            print(f"\n❌ FAILED TESTS ({len(self.failed_tests)}):")
            for failed_test in self.failed_tests:
                print(f"   {failed_test}")
        
        # Overall assessment
        critical_tests_passed = sum(test_results.values())
        total_critical_tests = len(test_results)
        
        print(f"\n🏆 OVERALL ASSESSMENT:")
        print(f"   Critical Tests Passed: {critical_tests_passed}/{total_critical_tests}")
        
        if critical_tests_passed == total_critical_tests and not self.critical_issues:
            print("   🎉 ALL CRITICAL TESTS PASSED - Database cleanup successful!")
            print("   ✅ Salvador's investments are correctly displayed")
            print("   ✅ Other clients show no investments as expected")
            print("   ✅ Admin portfolio shows correct AUM")
            print("   ✅ MT5 accounts are properly configured")
            return True
        else:
            print("   ⚠️  SOME CRITICAL ISSUES NEED ATTENTION")
            print("   🔧 Database cleanup may need additional work")
            return False

if __name__ == "__main__":
    tester = CriticalInvestmentTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)