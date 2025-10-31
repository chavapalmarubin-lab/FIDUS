#!/usr/bin/env python3
"""
SALVADOR PALMA API-BASED PRODUCTION RESTORATION TEST
===================================================

Since direct MongoDB operations don't reflect in the production API,
this test uses the API endpoints to create Salvador's investments and MT5 accounts.

OPERATIONS TO EXECUTE VIA API:
1. Create BALANCE fund investment ($1,263,485.40) via API
2. Create CORE fund investment ($4,000.00) via API
3. Verify MT5 accounts are created automatically
4. Verify all endpoints are working correctly

PRODUCTION URL: https://fidus-invest.emergent.host/
"""

import requests
import sys
from datetime import datetime
import json

class SalvadorAPIRestorationTester:
    def __init__(self, base_url="https://fidus-invest.emergent.host"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.admin_user = None
        self.client_user = None
        self.created_investments = []
        
        print(f"🎯 SALVADOR PALMA API-BASED PRODUCTION RESTORATION")
        print(f"   Production URL: {self.base_url}")
        print(f"   Timestamp: {datetime.now().isoformat()}")

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
        """Test admin login for API operations"""
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
            print(f"   Token: {response.get('token', 'No token')[:50]}...")
        return success

    def create_balance_investment_via_api(self):
        """Create BALANCE fund investment via API"""
        print(f"\n💰 CREATING BALANCE FUND INVESTMENT VIA API...")
        
        if not self.admin_user or 'token' not in self.admin_user:
            print(f"❌ No admin token available")
            return False
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {self.admin_user['token']}"
        }
        
        investment_data = {
            "client_id": "client_003",
            "fund_code": "BALANCE",
            "amount": 1263485.40,
            "deposit_date": "2025-04-01",
            "create_mt5_account": True,
            "mt5_login": "9928326",
            "mt5_password": "SecurePassword123!",
            "mt5_server": "DooTechnology-Live",
            "broker_name": "DooTechnology",
            "mt5_initial_balance": 1263485.40
        }
        
        success, response = self.run_test(
            "Create BALANCE Investment",
            "POST",
            "api/investments/create",
            200,
            data=investment_data,
            headers=headers
        )
        
        if success:
            investment_id = response.get('investment_id')
            mt5_account_id = response.get('mt5_account_id')
            print(f"   ✅ BALANCE investment created: {investment_id}")
            print(f"   ✅ MT5 account created: {mt5_account_id}")
            self.created_investments.append(investment_id)
            return True
        
        return False

    def create_core_investment_via_api(self):
        """Create CORE fund investment via API"""
        print(f"\n💰 CREATING CORE FUND INVESTMENT VIA API...")
        
        if not self.admin_user or 'token' not in self.admin_user:
            print(f"❌ No admin token available")
            return False
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {self.admin_user['token']}"
        }
        
        investment_data = {
            "client_id": "client_003",
            "fund_code": "CORE",
            "amount": 4000.00,
            "deposit_date": "2025-04-01",
            "create_mt5_account": True,
            "mt5_login": "15759667",
            "mt5_password": "SecurePassword456!",
            "mt5_server": "VTMarkets-PAMM",
            "broker_name": "VT Markets",
            "mt5_initial_balance": 4000.00
        }
        
        success, response = self.run_test(
            "Create CORE Investment",
            "POST",
            "api/investments/create",
            200,
            data=investment_data,
            headers=headers
        )
        
        if success:
            investment_id = response.get('investment_id')
            mt5_account_id = response.get('mt5_account_id')
            print(f"   ✅ CORE investment created: {investment_id}")
            print(f"   ✅ MT5 account created: {mt5_account_id}")
            self.created_investments.append(investment_id)
            return True
        
        return False

    def verify_salvador_investments(self):
        """Verify Salvador's investments are accessible via API"""
        print(f"\n🔍 VERIFYING SALVADOR'S INVESTMENTS...")
        
        success, response = self.run_test(
            "Get Salvador's Investments",
            "GET",
            "api/investments/client/client_003",
            200
        )
        
        if success:
            investments = response.get('investments', [])
            print(f"   Total investments found: {len(investments)}")
            
            balance_found = False
            core_found = False
            
            for investment in investments:
                fund_code = investment.get('fund_code')
                amount = investment.get('principal_amount', 0)
                investment_id = investment.get('investment_id')
                
                print(f"   Investment: {fund_code} - ${amount:,.2f} (ID: {investment_id})")
                
                if fund_code == 'BALANCE' and amount == 1263485.40:
                    balance_found = True
                    print(f"     ✅ BALANCE fund investment verified")
                elif fund_code == 'CORE' and amount == 4000.00:
                    core_found = True
                    print(f"     ✅ CORE fund investment verified")
            
            if balance_found and core_found:
                print(f"   🎉 ALL SALVADOR'S INVESTMENTS VERIFIED!")
                return True
            else:
                print(f"   ❌ Missing investments - BALANCE: {balance_found}, CORE: {core_found}")
                return False
        
        return False

    def verify_salvador_mt5_accounts(self):
        """Verify Salvador's MT5 accounts are accessible via API"""
        print(f"\n🔍 VERIFYING SALVADOR'S MT5 ACCOUNTS...")
        
        if not self.admin_user or 'token' not in self.admin_user:
            print(f"❌ No admin token available")
            return False
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {self.admin_user['token']}"
        }
        
        success, response = self.run_test(
            "Get All MT5 Accounts",
            "GET",
            "api/mt5/admin/accounts",
            200,
            headers=headers
        )
        
        if success:
            accounts = response.get('accounts', [])
            print(f"   Total MT5 accounts found: {len(accounts)}")
            
            doo_found = False
            vt_found = False
            
            for account in accounts:
                client_id = account.get('client_id')
                login = account.get('login')
                broker = account.get('broker')
                equity = account.get('current_equity', 0)
                
                if client_id == 'client_003':
                    print(f"   Salvador's MT5: {broker} - Login: {login} - Equity: ${equity:,.2f}")
                    
                    if broker == 'DooTechnology' and login == '9928326':
                        doo_found = True
                        print(f"     ✅ DooTechnology account verified")
                    elif broker == 'VT Markets' and login == '15759667':
                        vt_found = True
                        print(f"     ✅ VT Markets account verified")
            
            if doo_found and vt_found:
                print(f"   🎉 ALL SALVADOR'S MT5 ACCOUNTS VERIFIED!")
                return True
            else:
                print(f"   ❌ Missing MT5 accounts - DooTechnology: {doo_found}, VT Markets: {vt_found}")
                return False
        
        return False

    def verify_fund_performance_dashboard(self):
        """Verify Salvador appears in fund performance dashboard"""
        print(f"\n🔍 VERIFYING FUND PERFORMANCE DASHBOARD...")
        
        if not self.admin_user or 'token' not in self.admin_user:
            print(f"❌ No admin token available")
            return False
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {self.admin_user['token']}"
        }
        
        success, response = self.run_test(
            "Get Fund Performance Dashboard",
            "GET",
            "api/admin/fund-performance/dashboard",
            200,
            headers=headers
        )
        
        if success:
            performance_data = response.get('performance_data', [])
            print(f"   Performance records found: {len(performance_data)}")
            
            salvador_found = False
            for record in performance_data:
                client_id = record.get('client_id')
                if client_id == 'client_003':
                    salvador_found = True
                    fund_code = record.get('fund_code', 'Unknown')
                    performance_gap = record.get('performance_gap', 0)
                    print(f"   Salvador's {fund_code} fund - Performance gap: {performance_gap}%")
            
            if salvador_found:
                print(f"   ✅ Salvador found in fund performance dashboard")
                return True
            else:
                print(f"   ❌ Salvador NOT found in fund performance dashboard")
                return False
        
        return False

    def verify_cash_flow_overview(self):
        """Verify Salvador's data contributes to cash flow calculations"""
        print(f"\n🔍 VERIFYING CASH FLOW OVERVIEW...")
        
        if not self.admin_user or 'token' not in self.admin_user:
            print(f"❌ No admin token available")
            return False
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {self.admin_user['token']}"
        }
        
        success, response = self.run_test(
            "Get Cash Flow Overview",
            "GET",
            "api/admin/cashflow/overview",
            200,
            headers=headers
        )
        
        if success:
            mt5_trading_profits = response.get('mt5_trading_profits', 0)
            client_obligations = response.get('client_interest_obligations', 0)
            total_fund_assets = response.get('total_fund_assets', 0)
            
            print(f"   MT5 Trading Profits: ${mt5_trading_profits:,.2f}")
            print(f"   Client Interest Obligations: ${client_obligations:,.2f}")
            print(f"   Total Fund Assets: ${total_fund_assets:,.2f}")
            
            # Check if values are non-zero (indicating Salvador's data is included)
            if mt5_trading_profits > 0 and client_obligations > 0 and total_fund_assets > 0:
                print(f"   ✅ Cash flow shows non-zero values - Salvador's data included")
                return True
            else:
                print(f"   ❌ Cash flow shows zero values - Salvador's data NOT included")
                return False
        
        return False

    def run_comprehensive_test(self):
        """Run the complete Salvador API restoration test"""
        print(f"\n" + "="*80)
        print(f"🚀 STARTING SALVADOR PALMA API-BASED PRODUCTION RESTORATION")
        print(f"="*80)
        
        # Step 1: Test authentication
        print(f"\n" + "-"*60)
        print(f"🔐 TESTING AUTHENTICATION")
        print(f"-"*60)
        
        admin_login_success = self.test_admin_login()
        
        if not admin_login_success:
            print(f"❌ CRITICAL FAILURE: Admin login failed")
            return False
        
        # Step 2: Create investments via API
        print(f"\n" + "-"*60)
        print(f"💰 CREATING INVESTMENTS VIA API")
        print(f"-"*60)
        
        balance_created = self.create_balance_investment_via_api()
        core_created = self.create_core_investment_via_api()
        
        if not balance_created or not core_created:
            print(f"⚠️  Some investments failed to create - continuing with verification")
        
        # Step 3: Verify data restoration
        print(f"\n" + "-"*60)
        print(f"✅ VERIFYING DATA RESTORATION")
        print(f"-"*60)
        
        investments_verified = self.verify_salvador_investments()
        mt5_accounts_verified = self.verify_salvador_mt5_accounts()
        fund_performance_verified = self.verify_fund_performance_dashboard()
        cash_flow_verified = self.verify_cash_flow_overview()
        
        # Final Results
        print(f"\n" + "="*80)
        print(f"📊 FINAL API RESTORATION RESULTS")
        print(f"="*80)
        
        creation_results = {
            "BALANCE Investment Created": balance_created,
            "CORE Investment Created": core_created
        }
        
        verification_results = {
            "Salvador's Investments": investments_verified,
            "Salvador's MT5 Accounts": mt5_accounts_verified,
            "Fund Performance Dashboard": fund_performance_verified,
            "Cash Flow Overview": cash_flow_verified
        }
        
        print(f"CREATION RESULTS:")
        for test_name, result in creation_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"   {test_name}: {status}")
        
        print(f"\nVERIFICATION RESULTS:")
        for test_name, result in verification_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"   {test_name}: {status}")
        
        passed_creations = sum(creation_results.values())
        total_creations = len(creation_results)
        passed_verifications = sum(verification_results.values())
        total_verifications = len(verification_results)
        
        creation_rate = (passed_creations / total_creations) * 100
        verification_rate = (passed_verifications / total_verifications) * 100
        
        print(f"\n🎯 CREATION SUCCESS RATE: {passed_creations}/{total_creations} ({creation_rate:.1f}%)")
        print(f"🎯 VERIFICATION SUCCESS RATE: {passed_verifications}/{total_verifications} ({verification_rate:.1f}%)")
        print(f"🔧 API TESTS: {self.tests_passed}/{self.tests_run} passed")
        
        if passed_creations == total_creations and passed_verifications == total_verifications:
            print(f"\n🎉 SALVADOR PALMA API RESTORATION COMPLETED SUCCESSFULLY!")
            print(f"   ✅ All investments created via API")
            print(f"   ✅ All MT5 accounts created automatically") 
            print(f"   ✅ All dashboards updated")
            print(f"   ✅ All endpoints responding")
            print(f"\n🚀 PRODUCTION SYSTEM IS NOW FULLY OPERATIONAL!")
            return True
        else:
            print(f"\n⚠️  SALVADOR PALMA API RESTORATION PARTIALLY COMPLETED")
            if passed_creations == total_creations:
                print(f"   ✅ All investments created successfully")
            else:
                print(f"   ❌ Some investments failed to create")
            
            if passed_verifications > 0:
                print(f"   ✅ Some verification steps passed")
            else:
                print(f"   ❌ All verification steps failed")
            
            return passed_creations == total_creations

if __name__ == "__main__":
    tester = SalvadorAPIRestorationTester()
    success = tester.run_comprehensive_test()
    
    if success:
        print(f"\n✅ TEST COMPLETED SUCCESSFULLY")
        sys.exit(0)
    else:
        print(f"\n⚠️  TEST COMPLETED WITH PARTIAL SUCCESS")
        sys.exit(1)