#!/usr/bin/env python3
"""
PRODUCTION SALVADOR PALMA DATA VERIFICATION TEST
===============================================

This test verifies Salvador's data accessibility in production after fixing frontend URL configuration.

FRONTEND CONFIG FIXED:
✅ Changed REACT_APP_BACKEND_URL from preview URL to production URL
✅ Frontend will now connect to correct production backend at https://fidus-invest.emergent.host

VERIFICATION NEEDED:
1. Test Salvador's client data: GET /api/client/client_003/data
2. Test Salvador's investments: GET /api/investments/client/client_003  
3. Test MT5 accounts: GET /api/mt5/admin/accounts
4. Test fund performance: GET /api/admin/fund-performance/dashboard
5. Test cash flow: GET /api/admin/cashflow/overview

EXPECTED RESULTS AFTER FRONTEND FIX:
- Client dashboard should show Salvador's correct balances
- Total AUM: $1,267,485.40 (BALANCE: $1,263,485.40 + CORE: $4,000)
- MT5 accounts should be visible (DooTechnology + VT Markets)
- Fund performance dashboard should include Salvador
- No more $0 values in frontend
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration - PRODUCTION BACKEND URL
BACKEND_URL = "https://fidus-invest.emergent.host/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class ProductionSalvadorVerificationTest:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []

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

    def test_admin_login(self):
        """Test admin login"""
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
            print(f"   Admin logged in: {response.get('name', 'Unknown')}")
        return success

    def get_auth_headers(self):
        """Get authorization headers"""
        if not self.admin_user or not self.admin_user.get('token'):
            return {'Content-Type': 'application/json'}
        return {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {self.admin_user['token']}"
        }

    def test_salvador_client_exists(self):
        """Test if Salvador Palma client exists"""
        headers = self.get_auth_headers()
        success, response = self.run_test(
            "Salvador Client Profile Check",
            "GET",
            "api/admin/clients",
            200,
            headers=headers
        )
        
        if success:
            clients = response.get('clients', [])
            print(f"   Total clients in production: {len(clients)}")
            
            salvador_found = False
            for client in clients:
                if client.get('id') == self.salvador_client_id:
                    salvador_found = True
                    print(f"   ✅ Salvador Palma found!")
                    print(f"   - Name: {client.get('name')}")
                    print(f"   - Email: {client.get('email')}")
                    print(f"   - Status: {client.get('status', 'N/A')}")
                    break
            
            if not salvador_found:
                print(f"   ❌ Salvador Palma (client_003) NOT FOUND in production!")
                print(f"   Available clients:")
                for client in clients[:5]:  # Show first 5 clients
                    print(f"   - {client.get('id')}: {client.get('name')}")
                return False
                
            return True
        
        return False

    def test_salvador_investments(self):
        """Test Salvador's investments"""
        headers = self.get_auth_headers()
        success, response = self.run_test(
            "Salvador Investments Check",
            "GET",
            f"api/investments/client/{self.salvador_client_id}",
            200,
            headers=headers
        )
        
        if success:
            investments = response.get('investments', [])
            print(f"   Salvador's investments: {len(investments)}")
            
            balance_found = False
            core_found = False
            
            for investment in investments:
                fund_code = investment.get('fund_code')
                principal = investment.get('principal_amount', 0)
                investment_id = investment.get('investment_id')
                
                print(f"   - {fund_code}: ${principal:,.2f} (ID: {investment_id})")
                
                if fund_code == "BALANCE" and abs(principal - 1263485.40) < 1:
                    balance_found = True
                    print(f"     ✅ BALANCE fund investment verified!")
                
                if fund_code == "CORE" and abs(principal - 4000.00) < 1:
                    core_found = True
                    print(f"     ✅ CORE fund investment verified!")
            
            if not balance_found:
                print(f"   ❌ BALANCE fund investment ($1,263,485.40) NOT FOUND!")
            
            if not core_found:
                print(f"   ❌ CORE fund investment ($4,000.00) NOT FOUND!")
            
            return balance_found and core_found
        
        return False

    def test_mt5_accounts(self):
        """Test MT5 accounts"""
        headers = self.get_auth_headers()
        success, response = self.run_test(
            "MT5 Accounts Check",
            "GET",
            "api/mt5/admin/accounts",
            200,
            headers=headers
        )
        
        if success:
            accounts = response.get('accounts', [])
            print(f"   Total MT5 accounts: {len(accounts)}")
            
            salvador_accounts = [acc for acc in accounts if acc.get('client_id') == self.salvador_client_id]
            print(f"   Salvador's MT5 accounts: {len(salvador_accounts)}")
            
            doo_found = False
            vt_found = False
            
            for account in salvador_accounts:
                login = account.get('login')
                broker = account.get('broker', 'Unknown')
                print(f"   - Login: {login}, Broker: {broker}")
                
                if login == "9928326":
                    doo_found = True
                    print(f"     ✅ DooTechnology account found!")
                
                if login == "15759667":
                    vt_found = True
                    print(f"     ✅ VT Markets account found!")
            
            if not doo_found:
                print(f"   ❌ DooTechnology MT5 account (9928326) NOT FOUND!")
            
            if not vt_found:
                print(f"   ❌ VT Markets MT5 account (15759667) NOT FOUND!")
            
            return doo_found and vt_found
        
        return False

    def test_fund_performance(self):
        """Test Fund Performance dashboard"""
        headers = self.get_auth_headers()
        success, response = self.run_test(
            "Fund Performance Dashboard",
            "GET",
            "api/admin/fund-performance/dashboard",
            200,
            headers=headers
        )
        
        if success:
            performance_data = response.get('performance_gaps', [])
            print(f"   Performance records: {len(performance_data)}")
            
            salvador_records = [rec for rec in performance_data if rec.get('client_id') == self.salvador_client_id]
            print(f"   Salvador's performance records: {len(salvador_records)}")
            
            if salvador_records:
                print(f"   ✅ Salvador found in Fund Performance dashboard!")
                for record in salvador_records[:3]:  # Show first 3 records
                    print(f"   - Fund: {record.get('fund_code')}, Gap: {record.get('performance_gap', 'N/A')}")
                return True
            else:
                print(f"   ❌ Salvador NOT found in Fund Performance dashboard!")
                return False
        
        return False

    def test_cash_flow(self):
        """Test Cash Flow Management"""
        headers = self.get_auth_headers()
        success, response = self.run_test(
            "Cash Flow Management",
            "GET",
            "api/admin/cashflow/overview",
            200,
            headers=headers
        )
        
        if success:
            mt5_profits = response.get('mt5_trading_profits', 0)
            client_obligations = response.get('client_interest_obligations', 0)
            
            print(f"   MT5 Trading Profits: ${mt5_profits:,.2f}")
            print(f"   Client Obligations: ${client_obligations:,.2f}")
            
            if mt5_profits > 0 and client_obligations > 0:
                print(f"   ✅ Cash Flow shows non-zero values!")
                return True
            else:
                print(f"   ❌ Cash Flow shows zero values!")
                return False
        
        return False

    def test_health_check(self):
        """Test basic health check"""
        success, response = self.run_test(
            "Health Check",
            "GET",
            "api/health",
            200
        )
        
        if success:
            status = response.get('status', 'unknown')
            print(f"   System Status: {status}")
        
        return success

    def run_all_tests(self):
        """Run all production verification tests"""
        print("=" * 80)
        print("🚀 PRODUCTION ENVIRONMENT VERIFICATION")
        print("=" * 80)
        print(f"Production URL: {self.base_url}")
        print(f"Target: Salvador Palma (client_003) complete data restoration")
        print()
        
        # Test sequence
        tests = [
            ("Health Check", self.test_health_check),
            ("Admin Authentication", self.test_admin_login),
            ("Salvador Client Profile", self.test_salvador_client_exists),
            ("Salvador Investments", self.test_salvador_investments),
            ("MT5 Accounts", self.test_mt5_accounts),
            ("Fund Performance Dashboard", self.test_fund_performance),
            ("Cash Flow Management", self.test_cash_flow),
        ]
        
        results = []
        for test_name, test_method in tests:
            print(f"\n{'='*60}")
            print(f"🧪 {test_name}")
            print(f"{'='*60}")
            
            try:
                result = test_method()
                results.append((test_name, result))
                if result:
                    print(f"✅ {test_name}: PASSED")
                else:
                    print(f"❌ {test_name}: FAILED")
            except Exception as e:
                print(f"💥 {test_name}: ERROR - {str(e)}")
                results.append((test_name, False))
        
        # Final summary
        print("\n" + "=" * 80)
        print("📊 PRODUCTION VERIFICATION RESULTS")
        print("=" * 80)
        
        passed_tests = sum(1 for _, result in results if result)
        total_tests = len(results)
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"API Tests Run: {self.tests_run}")
        print(f"API Tests Passed: {self.tests_passed}")
        print(f"API Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        print()
        print(f"Test Suites Passed: {passed_tests}/{total_tests}")
        print(f"Test Suite Success Rate: {success_rate:.1f}%")
        print()
        
        print("DETAILED RESULTS:")
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {status} - {test_name}")
        
        print("\n" + "=" * 80)
        
        # Critical assessment
        critical_tests = [
            "Salvador Client Profile",
            "Salvador Investments", 
            "MT5 Accounts"
        ]
        
        critical_passed = sum(1 for test_name, result in results 
                            if test_name in critical_tests and result)
        
        if critical_passed == len(critical_tests):
            print("🎉 PRODUCTION DATA RESTORATION: ✅ SUCCESS")
            print("Salvador Palma's complete data successfully verified in production!")
        else:
            print("🚨 PRODUCTION DATA RESTORATION: ❌ INCOMPLETE")
            print("Salvador Palma's data restoration needs attention!")
            print(f"Critical tests passed: {critical_passed}/{len(critical_tests)}")
        
        print("=" * 80)
        
        return success_rate >= 70.0

if __name__ == "__main__":
    tester = ProductionVerificationTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)