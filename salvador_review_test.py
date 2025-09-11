#!/usr/bin/env python3
"""
SALVADOR PALMA PRODUCTION DATA RESTORATION TEST - REVIEW REQUEST
================================================================

This test validates the exact requirements from the urgent review request:

CONFIRMED PRODUCTION STATE:
✅ Salvador client profile exists (client_003, SALVADOR PALMA)
❌ 0 investments (missing BALANCE $1,263,485.40 and CORE $4,000)  
❌ 0 MT5 accounts (missing both DooTechnology and VT Markets)

IMMEDIATE CREATION NEEDED:
1. BALANCE fund investment ($1,263,485.40, ID: 5e4c7092-d5e7-46d7-8efd-ca29db8f33a4)
2. CORE fund investment ($4,000.00, ID: 68ce0609-dae8-48a5-bb86-a84d5e0d3184)
3. DooTechnology MT5 account (Login: 9928326)
4. VT Markets MT5 account (Login: 15759667)
"""

import requests
import sys
from datetime import datetime
import json

class SalvadorReviewTester:
    def __init__(self, base_url="https://fidus-invest.emergent.host"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.admin_token = None

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
            if details:
                print(f"   {details}")
        else:
            print(f"❌ {name}")
            if details:
                print(f"   {details}")
        return success

    def make_request(self, method, endpoint, data=None, headers=None, expected_status=200):
        """Make HTTP request with error handling"""
        url = f"{self.base_url}/{endpoint}"
        
        if headers is None:
            headers = {'Content-Type': 'application/json'}
        
        if self.admin_token and 'Authorization' not in headers:
            headers['Authorization'] = f"Bearer {self.admin_token}"
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=15)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=15)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=15)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=15)
            
            success = response.status_code == expected_status
            
            try:
                response_data = response.json()
            except:
                response_data = {"text": response.text}
            
            return success, response.status_code, response_data
            
        except Exception as e:
            return False, 0, {"error": str(e)}

    def test_admin_login(self):
        """Test admin authentication"""
        print("\n🔐 ADMIN AUTHENTICATION")
        
        success, status, response = self.make_request(
            'POST', 
            'api/auth/login',
            data={
                "username": "admin",
                "password": "password123", 
                "user_type": "admin"
            }
        )
        
        if success and response.get('token'):
            self.admin_token = response['token']
            return self.log_test(
                "Admin Login", 
                True, 
                f"Authenticated as {response.get('name', 'Admin')}"
            )
        else:
            return self.log_test(
                "Admin Login", 
                False, 
                f"Status: {status}, Response: {response}"
            )

    def test_salvador_client_profile(self):
        """Verify Salvador client profile exists"""
        print("\n👤 SALVADOR CLIENT PROFILE VERIFICATION")
        
        success, status, response = self.make_request(
            'GET',
            'api/clients/all'
        )
        
        if success:
            clients = response.get('clients', [])
            salvador_found = False
            
            for client in clients:
                if client.get('id') == 'client_003' and 'SALVADOR PALMA' in client.get('name', ''):
                    salvador_found = True
                    return self.log_test(
                        "Salvador Client Profile Exists",
                        True,
                        f"Found: {client.get('name')} ({client.get('email')})"
                    )
            
            if not salvador_found:
                return self.log_test(
                    "Salvador Client Profile Exists",
                    False,
                    f"Salvador not found in {len(clients)} clients"
                )
        else:
            return self.log_test(
                "Salvador Client Profile Exists",
                False,
                f"Failed to get clients: {status}"
            )

    def test_salvador_investments_current_state(self):
        """Check Salvador's current investment state"""
        print("\n💰 SALVADOR INVESTMENTS - CURRENT STATE")
        
        success, status, response = self.make_request(
            'GET',
            'api/investments/admin/overview'
        )
        
        if success:
            investments = response.get('investments', [])
            salvador_investments = [inv for inv in investments if inv.get('client_id') == 'client_003']
            
            print(f"   Total investments in system: {len(investments)}")
            print(f"   Salvador's investments: {len(salvador_investments)}")
            
            balance_found = False
            core_found = False
            
            for inv in salvador_investments:
                fund_code = inv.get('fund_code')
                amount = inv.get('principal_amount', 0)
                inv_id = inv.get('investment_id')
                print(f"   - {fund_code}: ${amount:,.2f} (ID: {inv_id})")
                
                if fund_code == 'BALANCE' and inv_id == '5e4c7092-d5e7-46d7-8efd-ca29db8f33a4':
                    balance_found = True
                elif fund_code == 'CORE' and inv_id == '68ce0609-dae8-48a5-bb86-a84d5e0d3184':
                    core_found = True
            
            return self.log_test(
                "Salvador Investment State",
                len(salvador_investments) >= 2 and balance_found and core_found,
                f"BALANCE ($1,263,485.40): {'✅ Found' if balance_found else '❌ Missing'}, CORE ($4,000): {'✅ Found' if core_found else '❌ Missing'}"
            )
            
        return False

    def test_salvador_mt5_accounts_current_state(self):
        """Check Salvador's current MT5 account state"""
        print("\n🏦 SALVADOR MT5 ACCOUNTS - CURRENT STATE")
        
        success, status, response = self.make_request(
            'GET',
            'api/mt5/admin/accounts'
        )
        
        if success:
            mt5_accounts = response.get('accounts', [])
            salvador_accounts = [acc for acc in mt5_accounts if acc.get('client_id') == 'client_003']
            
            print(f"   Total MT5 accounts in system: {len(mt5_accounts)}")
            print(f"   Salvador's MT5 accounts: {len(salvador_accounts)}")
            
            doo_found = False
            vt_found = False
            
            for acc in salvador_accounts:
                login = acc.get('login')
                broker = acc.get('broker')
                print(f"   - {broker}: Login {login}")
                
                if broker == 'DooTechnology' and login == '9928326':
                    doo_found = True
                elif broker == 'VT Markets' and login == '15759667':
                    vt_found = True
            
            return self.log_test(
                "Salvador MT5 Account State",
                len(salvador_accounts) >= 2 and doo_found and vt_found,
                f"DooTechnology (9928326): {'✅ Found' if doo_found else '❌ Missing'}, VT Markets (15759667): {'✅ Found' if vt_found else '❌ Missing'}"
            )
            
        return False

    def test_fund_performance_dashboard_integration(self):
        """Test if Salvador appears in Fund Performance dashboard"""
        print("\n📊 FUND PERFORMANCE DASHBOARD INTEGRATION")
        
        success, status, response = self.make_request(
            'GET',
            'api/admin/fund-performance/dashboard'
        )
        
        if success:
            performance_data = response.get('performance_data', [])
            salvador_records = [record for record in performance_data if record.get('client_id') == 'client_003']
            
            print(f"   Total performance records: {len(performance_data)}")
            print(f"   Salvador's performance records: {len(salvador_records)}")
            
            if salvador_records:
                for record in salvador_records:
                    fund = record.get('fund_code')
                    gap = record.get('performance_gap', 0)
                    print(f"   - {fund} fund: {gap:.2f}% performance gap")
                
                return self.log_test(
                    "Fund Performance Integration",
                    True,
                    f"Salvador found with {len(salvador_records)} performance records"
                )
            else:
                return self.log_test(
                    "Fund Performance Integration",
                    False,
                    "Salvador not found in Fund Performance dashboard"
                )
        else:
            return self.log_test(
                "Fund Performance Integration",
                False,
                f"Failed to get fund performance data: {status}"
            )

    def test_cash_flow_dashboard_integration(self):
        """Test if Salvador's data contributes to Cash Flow dashboard"""
        print("\n💹 CASH FLOW DASHBOARD INTEGRATION")
        
        success, status, response = self.make_request(
            'GET',
            'api/admin/cashflow/overview'
        )
        
        if success:
            mt5_profits = response.get('mt5_trading_profits', 0)
            client_obligations = response.get('client_interest_obligations', 0)
            total_aum = response.get('total_fund_assets', 0)
            
            print(f"   MT5 Trading Profits: ${mt5_profits:,.2f}")
            print(f"   Client Interest Obligations: ${client_obligations:,.2f}")
            print(f"   Total Fund Assets: ${total_aum:,.2f}")
            
            # If Salvador's data is integrated, we should see non-zero values
            data_integrated = mt5_profits > 0 and client_obligations > 0 and total_aum > 0
            
            return self.log_test(
                "Cash Flow Integration",
                data_integrated,
                "Salvador's data contributing to calculations" if data_integrated else "Cash Flow shows zero values - Salvador's data not integrated"
            )
        else:
            return self.log_test(
                "Cash Flow Integration",
                False,
                f"Failed to get cash flow data: {status}"
            )

    def test_system_health_check(self):
        """Test overall system health"""
        print("\n🏥 SYSTEM HEALTH CHECK")
        
        success, status, response = self.make_request(
            'GET',
            'api/health'
        )
        
        if success:
            system_status = response.get('status')
            return self.log_test(
                "System Health",
                system_status == 'healthy',
                f"System status: {system_status}"
            )
        else:
            return self.log_test(
                "System Health",
                False,
                f"Health check failed: {status}"
            )

    def test_critical_api_endpoints(self):
        """Test all critical API endpoints respond correctly"""
        print("\n🌐 CRITICAL API ENDPOINTS")
        
        critical_endpoints = [
            ('GET', 'api/health', 200),
            ('GET', 'api/clients/all', 200),
            ('GET', 'api/investments/admin/overview', 200),
            ('GET', 'api/mt5/admin/accounts', 200),
            ('GET', 'api/admin/fund-performance/dashboard', 200),
            ('GET', 'api/admin/cashflow/overview', 200)
        ]
        
        endpoint_results = []
        
        for method, endpoint, expected_status in critical_endpoints:
            success, status, response = self.make_request(method, endpoint, expected_status=expected_status)
            endpoint_results.append((endpoint, success, status))
            
            status_icon = "✅" if success else "❌"
            print(f"   {status_icon} {endpoint} - Status: {status}")
        
        passed_endpoints = sum(1 for _, passed, _ in endpoint_results if passed)
        total_endpoints = len(endpoint_results)
        
        return self.log_test(
            "Critical API Endpoints",
            passed_endpoints == total_endpoints,
            f"{passed_endpoints}/{total_endpoints} endpoints working correctly"
        )

    def run_comprehensive_test(self):
        """Run comprehensive Salvador production data test"""
        print("=" * 80)
        print("SALVADOR PALMA PRODUCTION DATA RESTORATION TEST")
        print("URGENT REVIEW REQUEST VALIDATION")
        print("=" * 80)
        print(f"Testing Environment: {self.base_url}")
        print(f"Target: Salvador Palma (client_003)")
        print("Required: BALANCE investment ($1,263,485.40) + CORE investment ($4,000)")
        print("Required: DooTechnology MT5 (9928326) + VT Markets MT5 (15759667)")
        print("=" * 80)
        
        # Test sequence
        test_sequence = [
            self.test_admin_login,
            self.test_salvador_client_profile,
            self.test_salvador_investments_current_state,
            self.test_salvador_mt5_accounts_current_state,
            self.test_fund_performance_dashboard_integration,
            self.test_cash_flow_dashboard_integration,
            self.test_system_health_check,
            self.test_critical_api_endpoints
        ]
        
        # Run all tests
        for test_func in test_sequence:
            try:
                test_func()
            except Exception as e:
                self.log_test(f"ERROR in {test_func.__name__}", False, str(e))
        
        # Final assessment
        print("\n" + "=" * 80)
        print("SALVADOR PALMA PRODUCTION TEST RESULTS")
        print("=" * 80)
        
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        print("\n📋 REVIEW REQUEST STATUS:")
        
        if success_rate >= 90:
            print("🎉 SALVADOR PALMA DATA RESTORATION: ✅ COMPLETE")
            print("✅ All required investments and MT5 accounts exist")
            print("✅ Dashboard integration working correctly")
            print("✅ System ready for production verification")
        elif success_rate >= 75:
            print("⚠️ SALVADOR PALMA DATA RESTORATION: 🔧 PARTIAL")
            print("🔧 Some components working, others need attention")
            print("📋 Review failed tests for missing data")
        else:
            print("🚨 SALVADOR PALMA DATA RESTORATION: ❌ INCOMPLETE")
            print("❌ Critical data missing - review request not fulfilled")
            print("🔧 Manual database operations may be required")
        
        print("=" * 80)
        
        return success_rate >= 75

if __name__ == "__main__":
    # Use production URL from review request
    base_url = "https://fidus-invest.emergent.host"
    
    tester = SalvadorReviewTester(base_url)
    success = tester.run_comprehensive_test()
    
    sys.exit(0 if success else 1)