#!/usr/bin/env python3
"""
CRITICAL DATABASE CONNECTIVITY INVESTIGATION
===========================================

This test investigates the critical production database connectivity issue:
- Backend logs show "8 investments for client_003" exist in database
- API endpoints return 0 investments/MT5 accounts  
- This indicates API is connected to wrong database or database configuration mismatch

INVESTIGATION OBJECTIVES:
1. Check current database connection - what database is the API actually connecting to?
2. Check environment variables - MONGO_URL setting
3. Database verification - connect to production database directly and verify Salvador's data
4. Check which database contains the "8 investments" mentioned in logs
5. Test API endpoints after fixing connection

Expected Result: Salvador's BALANCE ($1,263,485.40) and CORE ($4,000) investments 
should be visible via API, along with both MT5 accounts (DooTechnology 9928326, VT Markets 15759667).
"""

import requests
import sys
import json
import os
from datetime import datetime
from typing import Dict, Any, List
import pymongo
from pymongo import MongoClient

class DatabaseConnectivityTester:
    def __init__(self, base_url="https://auth-troubleshoot-14.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.admin_user = None
        self.client_user = None
        self.database_findings = {}
        
    def run_test(self, name: str, method: str, endpoint: str, expected_status: int, 
                 data: Dict = None, headers: Dict = None) -> tuple[bool, Dict]:
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

    def setup_authentication(self) -> bool:
        """Setup admin authentication for database investigation"""
        print("\n" + "="*80)
        print("🔐 SETTING UP AUTHENTICATION FOR DATABASE INVESTIGATION")
        print("="*80)
        
        # Test admin login
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
            print(f"   ✅ Admin logged in: {response.get('name', 'Unknown')} (ID: {response.get('id')})")
        else:
            print("   ❌ Admin login failed - cannot proceed with database investigation")
            return False

        # Test client login (Salvador Palma - client3)
        success, response = self.run_test(
            "Salvador Palma Client Login",
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
            print(f"   ✅ Salvador Palma logged in: {response.get('name', 'Unknown')} (ID: {response.get('id')})")
        else:
            print("   ❌ Salvador Palma login failed - will proceed with admin investigation only")
            
        return True

    def investigate_current_database_connection(self) -> bool:
        """Investigate what database the API is currently connected to"""
        print("\n" + "="*80)
        print("🔍 INVESTIGATING CURRENT DATABASE CONNECTION")
        print("="*80)
        
        # Check environment variables from backend
        print("\n📊 Environment Variables Investigation:")
        try:
            # Read backend .env file
            backend_env_path = "/app/backend/.env"
            if os.path.exists(backend_env_path):
                with open(backend_env_path, 'r') as f:
                    env_content = f.read()
                    print(f"   Backend .env content:")
                    for line in env_content.strip().split('\n'):
                        if line.strip():
                            print(f"     {line}")
                            
                    # Extract MONGO_URL and DB_NAME
                    for line in env_content.strip().split('\n'):
                        if line.startswith('MONGO_URL='):
                            mongo_url = line.split('=', 1)[1].strip('"')
                            self.database_findings['backend_mongo_url'] = mongo_url
                            print(f"   🔍 Backend MONGO_URL: {mongo_url}")
                        elif line.startswith('DB_NAME='):
                            db_name = line.split('=', 1)[1].strip('"')
                            self.database_findings['backend_db_name'] = db_name
                            print(f"   🔍 Backend DB_NAME: {db_name}")
            else:
                print("   ❌ Backend .env file not found")
                return False
                
        except Exception as e:
            print(f"   ❌ Error reading backend .env: {str(e)}")
            return False

        # Check frontend environment
        print("\n📊 Frontend Environment Investigation:")
        try:
            frontend_env_path = "/app/frontend/.env"
            if os.path.exists(frontend_env_path):
                with open(frontend_env_path, 'r') as f:
                    env_content = f.read()
                    print(f"   Frontend .env content:")
                    for line in env_content.strip().split('\n'):
                        if line.strip():
                            print(f"     {line}")
                            
                    # Extract REACT_APP_BACKEND_URL
                    for line in env_content.strip().split('\n'):
                        if line.startswith('REACT_APP_BACKEND_URL='):
                            backend_url = line.split('=', 1)[1].strip()
                            self.database_findings['frontend_backend_url'] = backend_url
                            print(f"   🔍 Frontend Backend URL: {backend_url}")
            else:
                print("   ❌ Frontend .env file not found")
                
        except Exception as e:
            print(f"   ❌ Error reading frontend .env: {str(e)}")

        return True

    def test_direct_database_connection(self) -> bool:
        """Test direct connection to MongoDB database"""
        print("\n" + "="*80)
        print("🔍 TESTING DIRECT DATABASE CONNECTION")
        print("="*80)
        
        mongo_url = self.database_findings.get('backend_mongo_url', 'mongodb://localhost:27017')
        db_name = self.database_findings.get('backend_db_name', 'test_database')
        
        print(f"   Connecting to: {mongo_url}")
        print(f"   Database: {db_name}")
        
        try:
            # Connect to MongoDB
            client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
            db = client[db_name]
            
            # Test connection
            client.admin.command('ping')
            print("   ✅ Successfully connected to MongoDB")
            
            # List all collections
            collections = db.list_collection_names()
            print(f"   📊 Found {len(collections)} collections: {collections}")
            self.database_findings['collections'] = collections
            
            # Check for Salvador Palma (client_003) data
            print("\n📊 Investigating Salvador Palma (client_003) Data:")
            
            # Check clients collection
            if 'clients' in collections:
                clients_collection = db['clients']
                salvador_client = clients_collection.find_one({"id": "client_003"})
                if salvador_client:
                    print(f"   ✅ Found Salvador Palma client record:")
                    print(f"     Name: {salvador_client.get('name', 'N/A')}")
                    print(f"     Email: {salvador_client.get('email', 'N/A')}")
                    print(f"     ID: {salvador_client.get('id', 'N/A')}")
                    self.database_findings['salvador_client_found'] = True
                else:
                    print("   ❌ Salvador Palma client record NOT FOUND")
                    self.database_findings['salvador_client_found'] = False
            else:
                print("   ❌ No 'clients' collection found")
                self.database_findings['salvador_client_found'] = False
            
            # Check investments collection
            if 'investments' in collections:
                investments_collection = db['investments']
                salvador_investments = list(investments_collection.find({"client_id": "client_003"}))
                investment_count = len(salvador_investments)
                print(f"   📊 Found {investment_count} investments for client_003")
                
                if investment_count > 0:
                    print("   💰 Salvador's Investments:")
                    total_value = 0
                    for inv in salvador_investments:
                        fund_code = inv.get('fund_code', 'Unknown')
                        principal = inv.get('principal_amount', 0)
                        current_value = inv.get('current_value', 0)
                        investment_id = inv.get('investment_id', 'N/A')
                        deposit_date = inv.get('deposit_date', 'N/A')
                        
                        print(f"     - {fund_code}: ${principal:,.2f} principal, ${current_value:,.2f} current (ID: {investment_id})")
                        print(f"       Deposit Date: {deposit_date}")
                        total_value += current_value
                    
                    print(f"   💰 Total Investment Value: ${total_value:,.2f}")
                    self.database_findings['salvador_investments_count'] = investment_count
                    self.database_findings['salvador_total_value'] = total_value
                    self.database_findings['salvador_investments_found'] = True
                    
                    # Check for specific expected investments
                    balance_investments = [inv for inv in salvador_investments if inv.get('fund_code') == 'BALANCE']
                    core_investments = [inv for inv in salvador_investments if inv.get('fund_code') == 'CORE']
                    
                    print(f"   📊 BALANCE fund investments: {len(balance_investments)}")
                    print(f"   📊 CORE fund investments: {len(core_investments)}")
                    
                    # Look for the specific amounts mentioned in review
                    balance_1263485 = any(inv.get('principal_amount') == 1263485.40 for inv in balance_investments)
                    core_4000 = any(inv.get('principal_amount') == 4000.00 for inv in core_investments)
                    
                    if balance_1263485:
                        print("   ✅ Found BALANCE investment with $1,263,485.40")
                    else:
                        print("   ❌ BALANCE investment with $1,263,485.40 NOT FOUND")
                        
                    if core_4000:
                        print("   ✅ Found CORE investment with $4,000.00")
                    else:
                        print("   ❌ CORE investment with $4,000.00 NOT FOUND")
                        
                else:
                    print("   ❌ NO investments found for client_003")
                    self.database_findings['salvador_investments_found'] = False
                    self.database_findings['salvador_investments_count'] = 0
            else:
                print("   ❌ No 'investments' collection found")
                self.database_findings['salvador_investments_found'] = False
            
            # Check MT5 accounts collection
            if 'mt5_accounts' in collections:
                mt5_collection = db['mt5_accounts']
                salvador_mt5 = list(mt5_collection.find({"client_id": "client_003"}))
                mt5_count = len(salvador_mt5)
                print(f"   📊 Found {mt5_count} MT5 accounts for client_003")
                
                if mt5_count > 0:
                    print("   🏦 Salvador's MT5 Accounts:")
                    for mt5 in salvador_mt5:
                        login = mt5.get('mt5_login', 'N/A')
                        broker = mt5.get('broker_name', 'N/A')
                        server = mt5.get('mt5_server', 'N/A')
                        fund_code = mt5.get('fund_code', 'N/A')
                        investment_ids = mt5.get('investment_ids', [])
                        
                        print(f"     - Login: {login}, Broker: {broker}, Server: {server}")
                        print(f"       Fund: {fund_code}, Investment IDs: {investment_ids}")
                    
                    # Check for specific expected MT5 accounts
                    doo_tech_account = any(mt5.get('mt5_login') == 9928326 for mt5 in salvador_mt5)
                    vt_markets_account = any(mt5.get('mt5_login') == 15759667 for mt5 in salvador_mt5)
                    
                    if doo_tech_account:
                        print("   ✅ Found DooTechnology MT5 account (Login: 9928326)")
                    else:
                        print("   ❌ DooTechnology MT5 account (Login: 9928326) NOT FOUND")
                        
                    if vt_markets_account:
                        print("   ✅ Found VT Markets MT5 account (Login: 15759667)")
                    else:
                        print("   ❌ VT Markets MT5 account (Login: 15759667) NOT FOUND")
                    
                    self.database_findings['salvador_mt5_count'] = mt5_count
                    self.database_findings['salvador_mt5_found'] = True
                else:
                    print("   ❌ NO MT5 accounts found for client_003")
                    self.database_findings['salvador_mt5_found'] = False
                    self.database_findings['salvador_mt5_count'] = 0
            else:
                print("   ❌ No 'mt5_accounts' collection found")
                self.database_findings['salvador_mt5_found'] = False
            
            client.close()
            return True
            
        except Exception as e:
            print(f"   ❌ Failed to connect to MongoDB: {str(e)}")
            return False

    def test_api_endpoints_data_retrieval(self) -> bool:
        """Test API endpoints to see what data they return"""
        print("\n" + "="*80)
        print("🔍 TESTING API ENDPOINTS DATA RETRIEVAL")
        print("="*80)
        
        # Test 1: Get all clients via API
        print("\n📊 Test 1: Get All Clients via API")
        success, response = self.run_test(
            "Get All Clients",
            "GET",
            "api/admin/clients",
            200
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
                print("   ❌ Salvador Palma NOT FOUND via API")
            
            self.database_findings['api_clients_count'] = len(clients)
            self.database_findings['api_salvador_found'] = salvador_found
        else:
            print("   ❌ Failed to get clients via API")
            return False

        # Test 2: Get Salvador's investments via API
        print("\n📊 Test 2: Get Salvador's Investments via API")
        success, response = self.run_test(
            "Get Salvador's Investments",
            "GET",
            "api/admin/clients/client_003/investments",
            200
        )
        
        if success:
            investments = response.get('investments', [])
            print(f"   📊 API returned {len(investments)} investments for client_003")
            
            if len(investments) > 0:
                print("   💰 Salvador's Investments via API:")
                total_api_value = 0
                for inv in investments:
                    fund_code = inv.get('fund_code', 'Unknown')
                    principal = inv.get('principal_amount', 0)
                    current_value = inv.get('current_value', 0)
                    investment_id = inv.get('investment_id', 'N/A')
                    
                    print(f"     - {fund_code}: ${principal:,.2f} principal, ${current_value:,.2f} current (ID: {investment_id})")
                    total_api_value += current_value
                
                print(f"   💰 Total API Investment Value: ${total_api_value:,.2f}")
                self.database_findings['api_investments_count'] = len(investments)
                self.database_findings['api_total_value'] = total_api_value
            else:
                print("   ❌ NO investments found for client_003 via API")
                self.database_findings['api_investments_count'] = 0
                self.database_findings['api_total_value'] = 0
        else:
            print("   ❌ Failed to get Salvador's investments via API")

        # Test 3: Get Salvador's MT5 accounts via API
        print("\n📊 Test 3: Get Salvador's MT5 Accounts via API")
        success, response = self.run_test(
            "Get Salvador's MT5 Accounts",
            "GET",
            "api/mt5/client/client_003/accounts",
            200
        )
        
        if success:
            accounts = response.get('accounts', [])
            print(f"   📊 API returned {len(accounts)} MT5 accounts for client_003")
            
            if len(accounts) > 0:
                print("   🏦 Salvador's MT5 Accounts via API:")
                for acc in accounts:
                    login = acc.get('mt5_login', 'N/A')
                    broker = acc.get('broker_name', 'N/A')
                    fund_code = acc.get('fund_code', 'N/A')
                    allocated = acc.get('total_allocated', 0)
                    
                    print(f"     - Login: {login}, Broker: {broker}, Fund: {fund_code}, Allocated: ${allocated:,.2f}")
                
                self.database_findings['api_mt5_count'] = len(accounts)
            else:
                print("   ❌ NO MT5 accounts found for client_003 via API")
                self.database_findings['api_mt5_count'] = 0
        else:
            print("   ❌ Failed to get Salvador's MT5 accounts via API")

        # Test 4: Test Fund Performance Dashboard
        print("\n📊 Test 4: Test Fund Performance Dashboard")
        success, response = self.run_test(
            "Get Fund Performance Data",
            "GET",
            "api/admin/fund-performance",
            200
        )
        
        if success:
            performance_data = response.get('performance_data', [])
            print(f"   📊 API returned {len(performance_data)} fund performance records")
            
            # Look for Salvador in performance data
            salvador_performance = [p for p in performance_data if p.get('client_id') == 'client_003']
            print(f"   📊 Found {len(salvador_performance)} performance records for client_003")
            
            self.database_findings['api_performance_count'] = len(performance_data)
            self.database_findings['api_salvador_performance_count'] = len(salvador_performance)
        else:
            print("   ❌ Failed to get fund performance data via API")

        # Test 5: Test Cash Flow Management
        print("\n📊 Test 5: Test Cash Flow Management")
        success, response = self.run_test(
            "Get Cash Flow Data",
            "GET",
            "api/admin/cash-flow",
            200
        )
        
        if success:
            mt5_trading_profits = response.get('mt5_trading_profits', 0)
            client_obligations = response.get('client_interest_obligations', 0)
            total_fund_assets = response.get('total_fund_assets', 0)
            
            print(f"   📊 Cash Flow Data:")
            print(f"     MT5 Trading Profits: ${mt5_trading_profits:,.2f}")
            print(f"     Client Obligations: ${client_obligations:,.2f}")
            print(f"     Total Fund Assets: ${total_fund_assets:,.2f}")
            
            self.database_findings['api_mt5_profits'] = mt5_trading_profits
            self.database_findings['api_client_obligations'] = client_obligations
        else:
            print("   ❌ Failed to get cash flow data via API")

        return True

    def analyze_database_api_disconnect(self) -> bool:
        """Analyze the disconnect between database and API data"""
        print("\n" + "="*80)
        print("🔍 ANALYZING DATABASE vs API DISCONNECT")
        print("="*80)
        
        # Compare database vs API findings
        db_investments = self.database_findings.get('salvador_investments_count', 0)
        api_investments = self.database_findings.get('api_investments_count', 0)
        
        db_mt5 = self.database_findings.get('salvador_mt5_count', 0)
        api_mt5 = self.database_findings.get('api_mt5_count', 0)
        
        db_total_value = self.database_findings.get('salvador_total_value', 0)
        api_total_value = self.database_findings.get('api_total_value', 0)
        
        print(f"📊 COMPARISON RESULTS:")
        print(f"   Salvador's Investments:")
        print(f"     Database: {db_investments} investments, ${db_total_value:,.2f} total value")
        print(f"     API:      {api_investments} investments, ${api_total_value:,.2f} total value")
        
        print(f"   Salvador's MT5 Accounts:")
        print(f"     Database: {db_mt5} accounts")
        print(f"     API:      {api_mt5} accounts")
        
        # Determine the issue
        if db_investments > 0 and api_investments == 0:
            print("\n🚨 CRITICAL ISSUE IDENTIFIED:")
            print("   ❌ Database contains Salvador's investment data but API returns ZERO investments")
            print("   ❌ This confirms the database connectivity issue described in the review")
            print("   🔍 ROOT CAUSE: API is not properly connected to the database containing Salvador's data")
            
            # Check if this matches the "8 investments" mentioned in logs
            if db_investments == 8:
                print(f"   ✅ Database count ({db_investments}) matches backend logs ('8 investments for client_003')")
            else:
                print(f"   ⚠️ Database count ({db_investments}) differs from backend logs ('8 investments for client_003')")
            
            return False
            
        elif db_investments == 0 and api_investments == 0:
            print("\n🚨 CRITICAL ISSUE IDENTIFIED:")
            print("   ❌ Both database AND API show ZERO investments for Salvador")
            print("   ❌ This means Salvador's data is completely missing from the current database")
            print("   🔍 ROOT CAUSE: Database does not contain Salvador's investment data")
            return False
            
        elif db_investments > 0 and api_investments > 0:
            if db_investments == api_investments and abs(db_total_value - api_total_value) < 1.0:
                print("\n✅ DATABASE-API CONNECTION WORKING:")
                print("   ✅ Database and API show consistent data for Salvador")
                print("   ✅ Investment counts match and values are consistent")
                return True
            else:
                print("\n⚠️ PARTIAL DATABASE-API DISCONNECT:")
                print("   ⚠️ Database and API both have data but with inconsistencies")
                print("   🔍 ROOT CAUSE: Data synchronization issue between database and API")
                return False
        else:
            print("\n⚠️ UNUSUAL DATABASE-API STATE:")
            print("   ⚠️ API shows data but database doesn't (unusual scenario)")
            print("   🔍 ROOT CAUSE: API may be using cached data or different database")
            return False

    def provide_fix_recommendations(self) -> None:
        """Provide specific recommendations to fix the database connectivity issue"""
        print("\n" + "="*80)
        print("🔧 FIX RECOMMENDATIONS")
        print("="*80)
        
        db_investments = self.database_findings.get('salvador_investments_count', 0)
        api_investments = self.database_findings.get('api_investments_count', 0)
        
        if db_investments > 0 and api_investments == 0:
            print("🎯 RECOMMENDED ACTIONS TO FIX DATABASE CONNECTIVITY:")
            print("1. ✅ VERIFY DATABASE CONNECTION:")
            print("   - Check if backend is connecting to correct MongoDB instance")
            print("   - Verify MONGO_URL in production environment matches database with Salvador's data")
            print("   - Ensure DB_NAME is correct")
            
            print("\n2. ✅ CHECK ENVIRONMENT CONFIGURATION:")
            print("   - Production environment may be using different .env file")
            print("   - Verify production MONGO_URL points to database with Salvador's data")
            print("   - Check if there are multiple database instances")
            
            print("\n3. ✅ RESTART BACKEND SERVICE:")
            print("   - After fixing MONGO_URL, restart backend to pick up new connection")
            print("   - Clear any connection pools or cached connections")
            
            print("\n4. ✅ VERIFY DATA MIGRATION:")
            print("   - If using different database in production, migrate Salvador's data")
            print("   - Ensure all collections (clients, investments, mt5_accounts) are migrated")
            
        elif db_investments == 0 and api_investments == 0:
            print("🎯 RECOMMENDED ACTIONS TO RESTORE SALVADOR'S DATA:")
            print("1. ✅ RESTORE SALVADOR'S CLIENT PROFILE:")
            print("   - Create client record for client_003 (Salvador Palma)")
            print("   - Email: chava@alyarglobal.com")
            
            print("\n2. ✅ RESTORE SALVADOR'S INVESTMENTS:")
            print("   - BALANCE fund: $1,263,485.40 (April 1, 2025)")
            print("   - CORE fund: $4,000.00 (September 4, 2025)")
            
            print("\n3. ✅ RESTORE SALVADOR'S MT5 ACCOUNTS:")
            print("   - DooTechnology account: Login 9928326")
            print("   - VT Markets account: Login 15759667")
            
            print("\n4. ✅ LINK MT5 ACCOUNTS TO INVESTMENTS:")
            print("   - Link DooTechnology to BALANCE investment")
            print("   - Link VT Markets to CORE investment")
            
        print(f"\n🔍 CURRENT DATABASE FINDINGS SUMMARY:")
        print(f"   Backend MONGO_URL: {self.database_findings.get('backend_mongo_url', 'Not found')}")
        print(f"   Backend DB_NAME: {self.database_findings.get('backend_db_name', 'Not found')}")
        print(f"   Collections found: {self.database_findings.get('collections', [])}")
        print(f"   Salvador client found in DB: {self.database_findings.get('salvador_client_found', False)}")
        print(f"   Salvador investments in DB: {self.database_findings.get('salvador_investments_count', 0)}")
        print(f"   Salvador MT5 accounts in DB: {self.database_findings.get('salvador_mt5_count', 0)}")
        print(f"   Salvador investments via API: {self.database_findings.get('api_investments_count', 0)}")
        print(f"   Salvador MT5 accounts via API: {self.database_findings.get('api_mt5_count', 0)}")

    def run_comprehensive_database_investigation(self) -> bool:
        """Run comprehensive database connectivity investigation"""
        print("\n" + "="*100)
        print("🚀 STARTING COMPREHENSIVE DATABASE CONNECTIVITY INVESTIGATION")
        print("="*100)
        print("Investigating critical issue: Backend logs show '8 investments for client_003'")
        print("but API endpoints return 0 investments/MT5 accounts")
        
        # Setup authentication
        if not self.setup_authentication():
            print("\n❌ Authentication setup failed - cannot proceed")
            return False
        
        # Run investigation steps
        investigation_steps = [
            ("Current Database Connection Investigation", self.investigate_current_database_connection),
            ("Direct Database Connection Test", self.test_direct_database_connection),
            ("API Endpoints Data Retrieval Test", self.test_api_endpoints_data_retrieval),
            ("Database vs API Disconnect Analysis", self.analyze_database_api_disconnect)
        ]
        
        step_results = []
        
        for step_name, test_method in investigation_steps:
            print(f"\n🔄 Running {step_name}...")
            try:
                result = test_method()
                step_results.append((step_name, result))
                
                if result:
                    print(f"✅ {step_name} - COMPLETED")
                else:
                    print(f"❌ {step_name} - ISSUES FOUND")
            except Exception as e:
                print(f"❌ {step_name} - ERROR: {str(e)}")
                step_results.append((step_name, False))
        
        # Provide fix recommendations
        self.provide_fix_recommendations()
        
        # Print final results
        print("\n" + "="*100)
        print("📊 DATABASE CONNECTIVITY INVESTIGATION RESULTS")
        print("="*100)
        
        completed_steps = sum(1 for _, result in step_results if result)
        total_steps = len(step_results)
        
        for step_name, result in step_results:
            status = "✅ COMPLETED" if result else "❌ ISSUES FOUND"
            print(f"   {step_name}: {status}")
        
        print(f"\n📈 Investigation Results:")
        print(f"   Steps Completed: {completed_steps}/{total_steps}")
        print(f"   Individual Tests: {self.tests_passed}/{self.tests_run} passed ({self.tests_passed/self.tests_run*100:.1f}%)")
        
        # Determine if the critical issue is confirmed
        db_investments = self.database_findings.get('salvador_investments_count', 0)
        api_investments = self.database_findings.get('api_investments_count', 0)
        
        if db_investments > 0 and api_investments == 0:
            print(f"\n🚨 CRITICAL DATABASE CONNECTIVITY ISSUE CONFIRMED!")
            print("   ❌ Database contains Salvador's data but API returns zero results")
            print("   ❌ This confirms the exact issue described in the review request")
            print("   🔧 URGENT ACTION REQUIRED: Fix database connection configuration")
            return False
        elif db_investments == 0 and api_investments == 0:
            print(f"\n🚨 CRITICAL DATA MISSING ISSUE CONFIRMED!")
            print("   ❌ Salvador's data is completely missing from current database")
            print("   ❌ Need to restore Salvador's complete profile and investment data")
            print("   🔧 URGENT ACTION REQUIRED: Restore Salvador's data to database")
            return False
        elif db_investments > 0 and api_investments > 0:
            print(f"\n✅ DATABASE CONNECTIVITY WORKING CORRECTLY!")
            print("   ✅ Database and API show consistent data for Salvador")
            print("   ✅ The reported issue may have been resolved")
            return True
        else:
            print(f"\n⚠️ UNUSUAL DATABASE STATE DETECTED!")
            print("   ⚠️ Inconsistent data between database and API")
            print("   🔧 ACTION REQUIRED: Investigate data synchronization")
            return False

def main():
    """Main test execution"""
    print("🔧 Database Connectivity Investigation Suite")
    print("Investigating critical production database connectivity issue")
    
    tester = DatabaseConnectivityTester()
    
    try:
        success = tester.run_comprehensive_database_investigation()
        
        if success:
            print("\n✅ Database connectivity investigation completed - no critical issues found!")
            sys.exit(0)
        else:
            print("\n❌ Critical database connectivity issues confirmed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Investigation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Investigation failed with error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()