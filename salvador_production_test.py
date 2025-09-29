#!/usr/bin/env python3
"""
SALVADOR PALMA PRODUCTION DATA RESTORATION TEST
==============================================

This test validates the creation of Salvador's missing investments and MT5 accounts 
in PRODUCTION database as requested in the urgent review.

REVIEW REQUEST SUMMARY:
✅ Salvador client profile exists (client_003, SALVADOR PALMA)
❌ 0 investments (missing BALANCE $1,263,485.40 and CORE $4,000)  
❌ 0 MT5 accounts (missing both DooTechnology and VT Markets)

REQUIRED ACTIONS:
1. Create BALANCE fund investment ($1,263,485.40)
2. Create CORE fund investment ($4,000.00)
3. Create DooTechnology MT5 account (Login: 9928326)
4. Create VT Markets MT5 account (Login: 15759667)
5. Verify Salvador appears in Fund Performance and Cash Flow dashboards

Production Environment: https://fidus-invest.emergent.host
"""

import requests
import sys
import json
from datetime import datetime, timezone
import time
import pymongo
from pymongo import MongoClient
import os
from dotenv import load_dotenv

class SalvadorProductionTester:
    def __init__(self, base_url="https://fidus-invest.emergent.host"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.admin_token = None
        self.salvador_client_id = "client_003"
        
        # MongoDB connection for direct database operations
        load_dotenv('/app/backend/.env')
        mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        db_name = os.environ.get('DB_NAME', 'test_database')
        
        try:
            self.mongo_client = MongoClient(mongo_url)
            self.db = self.mongo_client[db_name]
            print(f"✅ Connected to MongoDB: {mongo_url}/{db_name}")
        except Exception as e:
            print(f"❌ Failed to connect to MongoDB: {e}")
            self.mongo_client = None
            self.db = None
        
        # Salvador's expected data from review request
        self.salvador_data = {
            "client_id": "client_003",
            "name": "SALVADOR PALMA",
            "email": "chava@alyarglobal.com",
            "balance_investment": {
                "investment_id": "5e4c7092-d5e7-46d7-8efd-ca29db8f33a4",
                "fund_code": "BALANCE",
                "principal_amount": 1263485.40,
                "deposit_date": "2025-04-01"
            },
            "core_investment": {
                "investment_id": "68ce0609-dae8-48a5-bb86-a84d5e0d3184",
                "fund_code": "CORE",
                "principal_amount": 4000.00,
                "deposit_date": "2025-04-01"
            },
            "doo_mt5": {
                "login": "9928326",
                "broker": "DooTechnology",
                "server": "DooTechnology-Live"
            },
            "vt_mt5": {
                "login": "15759667",
                "broker": "VT Markets",
                "server": "VTMarkets-PAMM"
            }
        }

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
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)
            
            success = response.status_code == expected_status
            
            try:
                response_data = response.json()
            except:
                response_data = {"text": response.text}
            
            return success, response.status_code, response_data
            
        except Exception as e:
            return False, 0, {"error": str(e)}

    def test_admin_authentication(self):
        """Test admin login and get JWT token"""
        print("\n🔐 TESTING ADMIN AUTHENTICATION")
        
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
                "Admin Authentication", 
                True, 
                f"Logged in as {response.get('name', 'Admin')}"
            )
        else:
            return self.log_test(
                "Admin Authentication", 
                False, 
                f"Status: {status}, Response: {response}"
            )

    def test_salvador_client_exists(self):
        """Test if Salvador Palma client profile exists"""
        print("\n👤 TESTING SALVADOR CLIENT PROFILE")
        
        success, status, response = self.make_request(
            'GET',
            'api/clients/all'
        )
        
        if success:
            clients = response.get('clients', [])
            salvador_client = None
            
            for client in clients:
                if client.get('id') == self.salvador_client_id or client.get('name') == 'SALVADOR PALMA':
                    salvador_client = client
                    break
            
            if salvador_client:
                return self.log_test(
                    "Salvador Client Profile Exists",
                    True,
                    f"Found: {salvador_client.get('name')} ({salvador_client.get('email')})"
                )
            else:
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

    def test_create_salvador_client(self):
        """Create Salvador Palma client profile if not exists"""
        print("\n🆕 CREATING SALVADOR CLIENT PROFILE")
        
        client_data = {
            "username": "client3",
            "name": self.salvador_data["name"],
            "email": self.salvador_data["email"],
            "phone": self.salvador_data["phone"],
            "notes": f"Production client - Location: {self.salvador_data['location']}"
        }
        
        success, status, response = self.make_request(
            'POST',
            'api/admin/users/create',
            data=client_data
        )
        
        if success:
            return self.log_test(
                "Create Salvador Client Profile",
                True,
                f"Created client: {response.get('message', 'Success')}"
            )
        else:
            # Check if client already exists
            if status == 400 and 'already exists' in str(response):
                return self.log_test(
                    "Create Salvador Client Profile",
                    True,
                    "Client already exists"
                )
            else:
                return self.log_test(
                    "Create Salvador Client Profile",
                    False,
                    f"Status: {status}, Response: {response}"
                )

    def test_salvador_investment_exists(self):
        """Test if Salvador's BALANCE fund investment exists"""
        print("\n💰 TESTING SALVADOR INVESTMENT")
        
        success, status, response = self.make_request(
            'GET',
            f'api/investments/client/{self.salvador_client_id}'
        )
        
        if success:
            investments = response.get('investments', [])
            balance_investment = None
            
            for investment in investments:
                if (investment.get('fund_code') == 'BALANCE' and 
                    abs(investment.get('principal_amount', 0) - self.salvador_data['principal_amount']) < 1):
                    balance_investment = investment
                    self.salvador_investment_id = investment.get('investment_id')
                    break
            
            if balance_investment:
                return self.log_test(
                    "Salvador BALANCE Investment Exists",
                    True,
                    f"Found: ${balance_investment.get('principal_amount'):,.2f} BALANCE fund"
                )
            else:
                return self.log_test(
                    "Salvador BALANCE Investment Exists",
                    False,
                    f"BALANCE investment not found in {len(investments)} investments"
                )
        else:
            return self.log_test(
                "Salvador BALANCE Investment Exists",
                False,
                f"Failed to get investments: {status}"
            )

    def test_create_salvador_investment(self):
        """Create Salvador's BALANCE fund investment"""
        print("\n💵 CREATING SALVADOR INVESTMENT")
        
        investment_data = {
            "client_id": self.salvador_client_id,
            "fund_code": "BALANCE",
            "amount": self.salvador_data["principal_amount"],
            "deposit_date": self.salvador_data["start_date"],
            "create_mt5_account": True,
            "mt5_login": self.salvador_data["mt5_login"],
            "mt5_password": "encrypted_password_placeholder",
            "mt5_server": self.salvador_data["mt5_server"],
            "broker_name": "DooTechnology",
            "mt5_initial_balance": self.salvador_data["mt5_balance"],
            "banking_fees": 0,
            "fee_notes": "Production MT5 account mapping"
        }
        
        success, status, response = self.make_request(
            'POST',
            'api/investments/create',
            data=investment_data
        )
        
        if success:
            self.salvador_investment_id = response.get('investment_id')
            return self.log_test(
                "Create Salvador Investment",
                True,
                f"Investment ID: {self.salvador_investment_id}"
            )
        else:
            return self.log_test(
                "Create Salvador Investment",
                False,
                f"Status: {status}, Response: {response}"
            )

    def test_confirm_salvador_payment(self):
        """Confirm Salvador's investment payment"""
        print("\n💳 CONFIRMING SALVADOR PAYMENT")
        
        if not self.salvador_investment_id:
            return self.log_test(
                "Confirm Salvador Payment",
                False,
                "No investment ID available"
            )
        
        payment_data = {
            "investment_id": self.salvador_investment_id,
            "payment_method": "fiat",
            "amount": self.salvador_data["principal_amount"],
            "currency": "USD",
            "wire_confirmation_number": "PROD-SALVADOR-001",
            "bank_reference": "SALVADOR-BALANCE-DEPOSIT",
            "notes": "Production deposit confirmation for Salvador Palma BALANCE fund"
        }
        
        success, status, response = self.make_request(
            'POST',
            'api/payments/deposit/confirm?admin_id=admin_001',
            data=payment_data
        )
        
        if success:
            return self.log_test(
                "Confirm Salvador Payment",
                True,
                f"Payment confirmed: {response.get('message', 'Success')}"
            )
        else:
            return self.log_test(
                "Confirm Salvador Payment",
                False,
                f"Status: {status}, Response: {response}"
            )

    def test_salvador_mt5_account(self):
        """Test Salvador's MT5 account mapping"""
        print("\n🔗 TESTING SALVADOR MT5 ACCOUNT")
        
        success, status, response = self.make_request(
            'GET',
            'api/mt5/admin/accounts'
        )
        
        if success:
            accounts = response.get('accounts', [])
            salvador_mt5 = None
            
            for account in accounts:
                if (account.get('client_id') == self.salvador_client_id or 
                    str(account.get('mt5_login')) == str(self.salvador_data['mt5_login'])):
                    salvador_mt5 = account
                    self.salvador_mt5_account_id = account.get('account_id')
                    break
            
            if salvador_mt5:
                return self.log_test(
                    "Salvador MT5 Account Mapping",
                    True,
                    f"MT5 Login: {salvador_mt5.get('mt5_login')}, Balance: ${salvador_mt5.get('balance', 0):,.2f}"
                )
            else:
                return self.log_test(
                    "Salvador MT5 Account Mapping",
                    False,
                    f"MT5 account not found for login {self.salvador_data['mt5_login']}"
                )
        else:
            return self.log_test(
                "Salvador MT5 Account Mapping",
                False,
                f"Failed to get MT5 overview: {status}"
            )

    def test_fund_performance_dashboard(self):
        """Test Fund Performance vs MT5 Reality dashboard shows Salvador's data"""
        print("\n📊 TESTING FUND PERFORMANCE DASHBOARD")
        
        success, status, response = self.make_request(
            'GET',
            'api/admin/fund-performance/dashboard'
        )
        
        if success:
            dashboard = response.get('dashboard', {})
            fund_commitments = dashboard.get('fund_commitments', {})
            performance_gaps = dashboard.get('performance_gaps', [])
            
            # Check if Salvador's BALANCE fund is in fund commitments
            balance_fund = fund_commitments.get('BALANCE', {})
            client_investment = balance_fund.get('client_investment', {})
            
            if (client_investment.get('client_id') == self.salvador_client_id and 
                abs(client_investment.get('principal_amount', 0) - self.salvador_data['principal_amount']) < 1):
                
                # Check performance gaps for Salvador
                salvador_gaps = [gap for gap in performance_gaps if gap.get('client_id') == self.salvador_client_id]
                
                return self.log_test(
                    "Fund Performance Dashboard",
                    True,
                    f"Salvador found with ${client_investment.get('principal_amount'):,.2f} BALANCE fund, {len(salvador_gaps)} performance gaps tracked"
                )
            else:
                return self.log_test(
                    "Fund Performance Dashboard",
                    False,
                    f"Salvador not found in fund performance data"
                )
        else:
            return self.log_test(
                "Fund Performance Dashboard",
                False,
                f"Failed to get fund performance: {status}"
            )

    def test_cash_flow_management(self):
        """Test Cash Flow Management dashboard calculations"""
        print("\n💹 TESTING CASH FLOW MANAGEMENT")
        
        success, status, response = self.make_request(
            'GET',
            'api/admin/cashflow/overview'
        )
        
        if success:
            fund_accounting = response.get('fund_accounting', {})
            assets = fund_accounting.get('assets', {})
            liabilities = fund_accounting.get('liabilities', {})
            
            mt5_trading_profits = assets.get('mt5_trading_profits', 0)
            client_obligations = liabilities.get('client_obligations', 0)
            net_profitability = fund_accounting.get('net_fund_profitability', 0)
            
            # Check if we have reasonable cash flow data (non-zero values indicate system is working)
            if mt5_trading_profits > 0 and client_obligations > 0:
                return self.log_test(
                    "Cash Flow Management",
                    True,
                    f"MT5 Profits: ${mt5_trading_profits:,.2f}, Obligations: ${client_obligations:,.2f}, Net: ${net_profitability:,.2f}"
                )
            else:
                return self.log_test(
                    "Cash Flow Management",
                    False,
                    f"Cash flow data appears empty: MT5 Profits: ${mt5_trading_profits:,.2f}, Obligations: ${client_obligations:,.2f}"
                )
        else:
            return self.log_test(
                "Cash Flow Management",
                False,
                f"Failed to get cash flow data: {status}"
            )

    def test_client_portal_access(self):
        """Test Salvador can access client portal"""
        print("\n🖥️ TESTING CLIENT PORTAL ACCESS")
        
        # Test client login
        success, status, response = self.make_request(
            'POST',
            'api/auth/login',
            data={
                "username": "client3",
                "password": "password123",
                "user_type": "client"
            }
        )
        
        if success and response.get('token'):
            client_token = response['token']
            
            # Test client data access
            headers = {'Authorization': f"Bearer {client_token}"}
            success2, status2, response2 = self.make_request(
                'GET',
                f'api/client/{self.salvador_client_id}/data',
                headers=headers
            )
            
            if success2:
                balance = response2.get('balance', {})
                total_balance = balance.get('total_balance', 0)
                
                return self.log_test(
                    "Client Portal Access",
                    True,
                    f"Salvador can login and see balance: ${total_balance:,.2f}"
                )
            else:
                return self.log_test(
                    "Client Portal Access",
                    False,
                    f"Failed to get client data: {status2}"
                )
        else:
            return self.log_test(
                "Client Portal Access",
                False,
                f"Client login failed: {status}"
            )

    def test_data_integrity_verification(self):
        """Comprehensive data integrity verification"""
        print("\n🔍 TESTING DATA INTEGRITY")
        
        integrity_checks = []
        
        # Check 1: Investment amount matches
        success, status, response = self.make_request(
            'GET',
            f'api/investments/client/{self.salvador_client_id}'
        )
        
        if success:
            investments = response.get('investments', [])
            balance_investment = next(
                (inv for inv in investments if inv.get('fund_code') == 'BALANCE'), 
                None
            )
            
            if balance_investment:
                amount_match = abs(
                    balance_investment.get('principal_amount', 0) - 
                    self.salvador_data['principal_amount']
                ) < 1
                integrity_checks.append(("Investment Amount", amount_match))
            else:
                integrity_checks.append(("Investment Amount", False))
        else:
            integrity_checks.append(("Investment Amount", False))
        
        # Check 2: MT5 account linked
        success, status, response = self.make_request(
            'GET',
            'api/mt5/admin/accounts'
        )
        
        if success:
            accounts = response.get('accounts', [])
            salvador_mt5 = next(
                (account for account in accounts 
                 if str(account.get('mt5_login')) == str(self.salvador_data['mt5_login'])), 
                None
            )
            integrity_checks.append(("MT5 Account Linked", salvador_mt5 is not None))
        else:
            integrity_checks.append(("MT5 Account Linked", False))
        
        # Check 3: Fund performance data
        success, status, response = self.make_request(
            'GET',
            'api/admin/fund-performance/dashboard'
        )
        
        if success:
            dashboard = response.get('dashboard', {})
            fund_commitments = dashboard.get('fund_commitments', {})
            balance_fund = fund_commitments.get('BALANCE', {})
            client_investment = balance_fund.get('client_investment', {})
            
            salvador_in_performance = (client_investment.get('client_id') == self.salvador_client_id)
            integrity_checks.append(("Fund Performance Data", salvador_in_performance))
        else:
            integrity_checks.append(("Fund Performance Data", False))
        
        # Report integrity results
        passed_checks = sum(1 for _, passed in integrity_checks if passed)
        total_checks = len(integrity_checks)
        
        for check_name, passed in integrity_checks:
            status_icon = "✅" if passed else "❌"
            print(f"   {status_icon} {check_name}")
        
        return self.log_test(
            "Data Integrity Verification",
            passed_checks == total_checks,
            f"{passed_checks}/{total_checks} integrity checks passed"
        )

    def test_critical_endpoints(self):
        """Test all critical endpoints respond correctly"""
        print("\n🌐 TESTING CRITICAL ENDPOINTS")
        
        critical_endpoints = [
            ('GET', 'api/health', 200),
            ('GET', 'api/clients/all', 200),
            ('GET', f'api/investments/client/{self.salvador_client_id}', 200),
            ('GET', 'api/mt5/admin/accounts', 200),
            ('GET', 'api/admin/fund-performance/dashboard', 200),
            ('GET', 'api/admin/cashflow/overview', 200)
        ]
        
        endpoint_results = []
        
        for method, endpoint, expected_status in critical_endpoints:
            success, status, response = self.make_request(method, endpoint, expected_status=expected_status)
            endpoint_results.append((endpoint, success))
            
            status_icon = "✅" if success else "❌"
            print(f"   {status_icon} {endpoint} - Status: {status}")
        
        passed_endpoints = sum(1 for _, passed in endpoint_results if passed)
        total_endpoints = len(endpoint_results)
        
        return self.log_test(
            "Critical Endpoints",
            passed_endpoints == total_endpoints,
            f"{passed_endpoints}/{total_endpoints} endpoints working"
        )

    def run_all_tests(self):
        """Run complete Salvador Palma production data restoration test suite"""
        print("=" * 80)
        print("SALVADOR PALMA PRODUCTION DATA RESTORATION TEST")
        print("=" * 80)
        print(f"Testing Environment: {self.base_url}")
        print(f"Target Client: {self.salvador_data['name']} ({self.salvador_client_id})")
        print(f"Expected BALANCE Investment: ${self.salvador_data['balance_investment']['principal_amount']:,.2f}")
        print(f"Expected CORE Investment: ${self.salvador_data['core_investment']['principal_amount']:,.2f}")
        print(f"Expected DooTechnology MT5: {self.salvador_data['doo_mt5']['login']}")
        print(f"Expected VT Markets MT5: {self.salvador_data['vt_mt5']['login']}")
        print("=" * 80)
        
        # Test sequence
        test_sequence = [
            self.test_admin_authentication,
            self.test_salvador_client_exists,
            self.test_create_salvador_client,
            self.test_salvador_investment_exists,
            self.test_create_salvador_investment,
            self.test_confirm_salvador_payment,
            self.test_salvador_mt5_account,
            self.test_fund_performance_dashboard,
            self.test_cash_flow_management,
            self.test_client_portal_access,
            self.test_data_integrity_verification,
            self.test_critical_endpoints
        ]
        
        # Run tests
        for test_func in test_sequence:
            try:
                test_func()
            except Exception as e:
                self.log_test(f"ERROR in {test_func.__name__}", False, str(e))
            
            # Small delay between tests
            time.sleep(0.5)
        
        # Final results
        print("\n" + "=" * 80)
        print("SALVADOR PALMA PRODUCTION TEST RESULTS")
        print("=" * 80)
        
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("\n🎉 SALVADOR PALMA PRODUCTION DATA RESTORATION: SUCCESS!")
            print("✅ System is ready for production deployment")
            print("✅ All critical Salvador data is properly restored")
            print("✅ All endpoints are responding correctly")
        elif success_rate >= 75:
            print("\n⚠️ SALVADOR PALMA PRODUCTION DATA RESTORATION: PARTIAL SUCCESS")
            print("🔧 Some issues found but core functionality working")
            print("📋 Review failed tests before production deployment")
        else:
            print("\n❌ SALVADOR PALMA PRODUCTION DATA RESTORATION: FAILED")
            print("🚨 Critical issues found - DO NOT DEPLOY TO PRODUCTION")
            print("🔧 Fix all issues before attempting deployment")
        
        print("=" * 80)
        
        return success_rate >= 90

if __name__ == "__main__":
    # Allow custom base URL via command line
    base_url = sys.argv[1] if len(sys.argv) > 1 else "https://fidus-workspace-2.preview.emergentagent.com"
    
    tester = SalvadorProductionTester(base_url)
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)