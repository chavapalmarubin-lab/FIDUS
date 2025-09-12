#!/usr/bin/env python3
"""
SALVADOR PALMA PRODUCTION DATABASE RESTORATION TEST
==================================================

EXECUTIVE SUMMARY:
This test executes the approved production database restoration for Salvador Palma's 
missing investments and MT5 accounts as requested in the review.

USER APPROVED: Option 1 - Direct database creation to immediately fix production system.

OPERATIONS TO EXECUTE:
1. Create BALANCE fund investment ($1,263,485.40)
2. Create CORE fund investment ($4,000.00) 
3. Create DooTechnology MT5 account (Login: 9928326)
4. Create VT Markets MT5 account (Login: 15759667)
5. Verify all endpoints are working correctly

PRODUCTION URL: https://fidus-invest.emergent.host/
"""

import requests
import sys
from datetime import datetime
import json
import pymongo
from pymongo import MongoClient
import os
from dotenv import load_dotenv

class SalvadorProductionRestorationTester:
    def __init__(self, base_url="https://fidus-invest.emergent.host"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.admin_user = None
        self.client_user = None
        
        # Load environment variables for MongoDB connection
        load_dotenv('/app/backend/.env')
        self.mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.db_name = os.environ.get('DB_NAME', 'test_database')
        
        print(f"🎯 SALVADOR PALMA PRODUCTION DATABASE RESTORATION")
        print(f"   Production URL: {self.base_url}")
        print(f"   MongoDB URL: {self.mongo_url}")
        print(f"   Database: {self.db_name}")
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

    def connect_to_mongodb(self):
        """Connect to MongoDB for direct database operations"""
        try:
            print(f"\n🔗 Connecting to MongoDB...")
            print(f"   URL: {self.mongo_url}")
            print(f"   Database: {self.db_name}")
            
            self.mongo_client = MongoClient(self.mongo_url)
            self.db = self.mongo_client[self.db_name]
            
            # Test connection
            self.db.command('ping')
            print(f"✅ MongoDB connection successful")
            return True
            
        except Exception as e:
            print(f"❌ MongoDB connection failed: {str(e)}")
            return False

    def execute_mongodb_operations(self):
        """Execute the approved MongoDB operations for Salvador's data restoration"""
        if not hasattr(self, 'db'):
            print("❌ No MongoDB connection available")
            return False
            
        print(f"\n💾 EXECUTING PRODUCTION DATABASE RESTORATION OPERATIONS...")
        print(f"   Target: Salvador Palma (client_003)")
        print(f"   Operations: 2 investments + 2 MT5 accounts")
        
        try:
            # 1. CREATE BALANCE FUND INVESTMENT
            print(f"\n1️⃣ Creating BALANCE fund investment...")
            balance_investment = {
                "investment_id": "5e4c7092-d5e7-46d7-8efd-ca29db8f33a4",
                "client_id": "client_003", 
                "fund_code": "BALANCE",
                "principal_amount": 1263485.40,
                "current_value": 1263485.40,
                "deposit_date": datetime.fromisoformat("2025-04-01T00:00:00.000Z".replace('Z', '+00:00')),
                "status": "ACTIVE",
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            result1 = self.db.investments.insert_one(balance_investment)
            print(f"   ✅ BALANCE investment created: {result1.inserted_id}")
            print(f"   Investment ID: {balance_investment['investment_id']}")
            print(f"   Amount: ${balance_investment['principal_amount']:,.2f}")
            
            # 2. CREATE CORE FUND INVESTMENT (corrected $4,000)
            print(f"\n2️⃣ Creating CORE fund investment...")
            core_investment = {
                "investment_id": "68ce0609-dae8-48a5-bb86-a84d5e0d3184",
                "client_id": "client_003",
                "fund_code": "CORE", 
                "principal_amount": 4000.00,
                "current_value": 4000.00,
                "deposit_date": datetime.fromisoformat("2025-04-01T00:00:00.000Z".replace('Z', '+00:00')),
                "status": "ACTIVE",
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            result2 = self.db.investments.insert_one(core_investment)
            print(f"   ✅ CORE investment created: {result2.inserted_id}")
            print(f"   Investment ID: {core_investment['investment_id']}")
            print(f"   Amount: ${core_investment['principal_amount']:,.2f}")
            
            # 3. CREATE DOOTECHNOLOGY MT5 ACCOUNT
            print(f"\n3️⃣ Creating DooTechnology MT5 account...")
            doo_mt5_account = {
                "account_id": "mt5_doo_9928326",
                "client_id": "client_003",
                "login": "9928326",
                "broker": "DooTechnology",
                "server": "DooTechnology-Live",
                "investment_id": "5e4c7092-d5e7-46d7-8efd-ca29db8f33a4",
                "total_allocated": 1263485.40,
                "current_equity": 1837934.05,
                "status": "active",
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            result3 = self.db.mt5_accounts.insert_one(doo_mt5_account)
            print(f"   ✅ DooTechnology MT5 account created: {result3.inserted_id}")
            print(f"   Login: {doo_mt5_account['login']}")
            print(f"   Broker: {doo_mt5_account['broker']}")
            print(f"   Current Equity: ${doo_mt5_account['current_equity']:,.2f}")
            
            # 4. CREATE VT MARKETS MT5 ACCOUNT
            print(f"\n4️⃣ Creating VT Markets MT5 account...")
            vt_mt5_account = {
                "account_id": "mt5_vt_15759667",
                "client_id": "client_003",
                "login": "15759667", 
                "broker": "VT Markets",
                "server": "VTMarkets-PAMM",
                "investment_id": "68ce0609-dae8-48a5-bb86-a84d5e0d3184",
                "total_allocated": 4000.00,
                "current_equity": 4000.00,
                "status": "active",
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            result4 = self.db.mt5_accounts.insert_one(vt_mt5_account)
            print(f"   ✅ VT Markets MT5 account created: {result4.inserted_id}")
            print(f"   Login: {vt_mt5_account['login']}")
            print(f"   Broker: {vt_mt5_account['broker']}")
            print(f"   Current Equity: ${vt_mt5_account['current_equity']:,.2f}")
            
            print(f"\n🎉 ALL DATABASE OPERATIONS COMPLETED SUCCESSFULLY!")
            print(f"   ✅ 2 investments created")
            print(f"   ✅ 2 MT5 accounts created")
            print(f"   ✅ Salvador Palma data fully restored")
            
            return True
            
        except Exception as e:
            print(f"❌ Database operations failed: {str(e)}")
            return False

    def test_admin_login(self):
        """Test admin login for verification"""
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

    def test_salvador_client_login(self):
        """Test Salvador's client login"""
        success, response = self.run_test(
            "Salvador Client Login",
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
            self.client_user = response
            print(f"   Salvador logged in: {response.get('name', 'Unknown')}")
            print(f"   Client ID: {response.get('id', 'Unknown')}")
        return success

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
        
        success, response = self.run_test(
            "Get All MT5 Accounts",
            "GET",
            "api/mt5/admin/accounts",
            200
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
        
        success, response = self.run_test(
            "Get Fund Performance Dashboard",
            "GET",
            "api/admin/fund-performance/dashboard",
            200
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
        
        success, response = self.run_test(
            "Get Cash Flow Overview",
            "GET",
            "api/admin/cashflow/overview",
            200
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

    def test_critical_endpoints(self):
        """Test all critical endpoints are responding"""
        print(f"\n🔍 TESTING CRITICAL ENDPOINTS...")
        
        endpoints = [
            ("Health Check", "GET", "api/health", 200),
            ("Get All Clients", "GET", "api/admin/clients", 200),
            ("Get All Investments", "GET", "api/admin/investments", 200),
            ("Get MT5 Accounts", "GET", "api/mt5/admin/accounts", 200),
            ("Fund Performance Dashboard", "GET", "api/admin/fund-performance/dashboard", 200),
            ("Cash Flow Overview", "GET", "api/admin/cashflow/overview", 200)
        ]
        
        passed = 0
        for name, method, endpoint, expected_status in endpoints:
            success, _ = self.run_test(name, method, endpoint, expected_status)
            if success:
                passed += 1
        
        print(f"\n   Critical endpoints: {passed}/{len(endpoints)} passed")
        return passed == len(endpoints)

    def run_comprehensive_test(self):
        """Run the complete Salvador production restoration test"""
        print(f"\n" + "="*80)
        print(f"🚀 STARTING SALVADOR PALMA PRODUCTION DATABASE RESTORATION")
        print(f"="*80)
        
        # Step 1: Connect to MongoDB
        if not self.connect_to_mongodb():
            print(f"\n❌ CRITICAL FAILURE: Cannot connect to MongoDB")
            return False
        
        # Step 2: Execute database operations
        if not self.execute_mongodb_operations():
            print(f"\n❌ CRITICAL FAILURE: Database operations failed")
            return False
        
        # Step 3: Test authentication
        print(f"\n" + "-"*60)
        print(f"🔐 TESTING AUTHENTICATION")
        print(f"-"*60)
        
        admin_login_success = self.test_admin_login()
        salvador_login_success = self.test_salvador_client_login()
        
        if not admin_login_success:
            print(f"⚠️  Admin login failed - continuing with verification")
        
        if not salvador_login_success:
            print(f"⚠️  Salvador login failed - continuing with verification")
        
        # Step 4: Verify data restoration
        print(f"\n" + "-"*60)
        print(f"✅ VERIFYING DATA RESTORATION")
        print(f"-"*60)
        
        investments_verified = self.verify_salvador_investments()
        mt5_accounts_verified = self.verify_salvador_mt5_accounts()
        fund_performance_verified = self.verify_fund_performance_dashboard()
        cash_flow_verified = self.verify_cash_flow_overview()
        
        # Step 5: Test critical endpoints
        print(f"\n" + "-"*60)
        print(f"🔧 TESTING CRITICAL ENDPOINTS")
        print(f"-"*60)
        
        endpoints_verified = self.test_critical_endpoints()
        
        # Final Results
        print(f"\n" + "="*80)
        print(f"📊 FINAL RESTORATION RESULTS")
        print(f"="*80)
        
        verification_results = {
            "Salvador's Investments": investments_verified,
            "Salvador's MT5 Accounts": mt5_accounts_verified,
            "Fund Performance Dashboard": fund_performance_verified,
            "Cash Flow Overview": cash_flow_verified,
            "Critical Endpoints": endpoints_verified
        }
        
        passed_verifications = sum(verification_results.values())
        total_verifications = len(verification_results)
        
        for test_name, result in verification_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"   {test_name}: {status}")
        
        success_rate = (passed_verifications / total_verifications) * 100
        print(f"\n🎯 OVERALL SUCCESS RATE: {passed_verifications}/{total_verifications} ({success_rate:.1f}%)")
        print(f"🔧 API TESTS: {self.tests_passed}/{self.tests_run} passed")
        
        if passed_verifications == total_verifications:
            print(f"\n🎉 SALVADOR PALMA PRODUCTION RESTORATION COMPLETED SUCCESSFULLY!")
            print(f"   ✅ All investments restored")
            print(f"   ✅ All MT5 accounts restored") 
            print(f"   ✅ All dashboards updated")
            print(f"   ✅ All endpoints responding")
            print(f"\n🚀 PRODUCTION SYSTEM IS NOW FULLY OPERATIONAL!")
            return True
        else:
            print(f"\n❌ SALVADOR PALMA PRODUCTION RESTORATION INCOMPLETE")
            print(f"   Some verification steps failed")
            print(f"   Manual intervention may be required")
            return False

if __name__ == "__main__":
    tester = SalvadorProductionRestorationTester()
    success = tester.run_comprehensive_test()
    
    if success:
        print(f"\n✅ TEST COMPLETED SUCCESSFULLY")
        sys.exit(0)
    else:
        print(f"\n❌ TEST COMPLETED WITH ISSUES")
        sys.exit(1)