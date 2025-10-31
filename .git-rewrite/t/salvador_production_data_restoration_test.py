#!/usr/bin/env python3
"""
CRITICAL SALVADOR PALMA PRODUCTION DATA RESTORATION TEST
=======================================================

This test executes the URGENT production database operations requested in the review:

IMMEDIATE DATABASE OPERATIONS REQUIRED:
1. CREATE SALVADOR CLIENT (if missing)
2. CREATE BALANCE INVESTMENT ($1,263,485.40)
3. CREATE CORE INVESTMENT ($4,000.00)
4. CREATE DOOTECHNOLOGY MT5 ACCOUNT (Login: 9928326)
5. CREATE VT MARKETS MT5 ACCOUNT (Login: 15759667)
6. IMMEDIATE VERIFICATION of production endpoints

Expected Results:
- /api/admin/clients should show 1 client (Salvador)
- /api/investments/client/client_003 should show 2 investments
- /api/mt5/admin/accounts should show 2 MT5 accounts
- Fund Portfolio should show non-zero AUM
"""

import requests
import sys
from datetime import datetime
import json
import pymongo
from pymongo import MongoClient
import os
from dotenv import load_dotenv

class SalvadorProductionDataRestoration:
    def __init__(self, base_url="https://fidus-invest.emergent.host"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.admin_token = None
        self.client_token = None
        
        # Load environment variables
        load_dotenv('/app/backend/.env')
        
        # MongoDB connection
        self.mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.db_name = os.environ.get('DB_NAME', 'test_database')
        
        print(f"🎯 CRITICAL SALVADOR PALMA PRODUCTION DATA RESTORATION")
        print(f"   Production URL: {self.base_url}")
        print(f"   MongoDB URL: {self.mongo_url}")
        print(f"   Database: {self.db_name}")

    def connect_to_mongodb(self):
        """Connect to MongoDB database"""
        try:
            self.mongo_client = MongoClient(self.mongo_url)
            self.db = self.mongo_client[self.db_name]
            
            # Test connection
            self.db.command('ping')
            print("✅ MongoDB connection successful")
            return True
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
            return False

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
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)

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

    def authenticate_admin(self):
        """Authenticate as admin user"""
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
        
        if success and response.get('token'):
            self.admin_token = response['token']
            print(f"   Admin authenticated: {response.get('name')}")
            return True
        return False

    def authenticate_client(self):
        """Authenticate as Salvador Palma (client3)"""
        success, response = self.run_test(
            "Salvador Palma Authentication",
            "POST",
            "api/auth/login",
            200,
            data={
                "username": "client3",
                "password": "password123",
                "user_type": "client"
            }
        )
        
        if success and response.get('token'):
            self.client_token = response['token']
            print(f"   Salvador authenticated: {response.get('name')}")
            return True
        return False

    def create_salvador_client_if_missing(self):
        """Create Salvador client profile if missing"""
        print("\n🎯 STEP 1: CREATE SALVADOR CLIENT (if missing)")
        
        try:
            # Check if Salvador already exists
            clients_collection = self.db.clients
            salvador = clients_collection.find_one({"id": "client_003"})
            
            if salvador:
                print("✅ Salvador Palma client already exists")
                print(f"   Name: {salvador.get('name')}")
                print(f"   Email: {salvador.get('email')}")
                return True
            
            # Create Salvador client
            salvador_data = {
                "id": "client_003",
                "name": "SALVADOR PALMA",
                "email": "chava@alyarglobal.com",
                "phone": "+52-663-123-4567",
                "status": "active",
                "registration_date": "2025-04-01T00:00:00.000Z",
                "total_balance": 1267485.40,
                "created_at": datetime.utcnow()
            }
            
            result = clients_collection.insert_one(salvador_data)
            print(f"✅ Salvador client created successfully")
            print(f"   MongoDB ID: {result.inserted_id}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create Salvador client: {e}")
            return False

    def create_balance_investment(self):
        """Create BALANCE fund investment for Salvador"""
        print("\n🎯 STEP 2: CREATE BALANCE INVESTMENT ($1,263,485.40)")
        
        try:
            investments_collection = self.db.investments
            
            # Check if BALANCE investment already exists
            existing = investments_collection.find_one({
                "investment_id": "5e4c7092-d5e7-46d7-8efd-ca29db8f33a4"
            })
            
            if existing:
                print("✅ BALANCE investment already exists")
                print(f"   Amount: ${existing.get('principal_amount')}")
                return True
            
            # Create BALANCE investment
            balance_investment = {
                "investment_id": "5e4c7092-d5e7-46d7-8efd-ca29db8f33a4",
                "client_id": "client_003",
                "fund_code": "BALANCE",
                "principal_amount": 1263485.40,
                "current_value": 1263485.40,
                "deposit_date": "2025-04-01T00:00:00.000Z",
                "status": "ACTIVE",
                "created_at": datetime.utcnow()
            }
            
            result = investments_collection.insert_one(balance_investment)
            print(f"✅ BALANCE investment created successfully")
            print(f"   Investment ID: 5e4c7092-d5e7-46d7-8efd-ca29db8f33a4")
            print(f"   Amount: $1,263,485.40")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create BALANCE investment: {e}")
            return False

    def create_core_investment(self):
        """Create CORE fund investment for Salvador"""
        print("\n🎯 STEP 3: CREATE CORE INVESTMENT ($4,000.00)")
        
        try:
            investments_collection = self.db.investments
            
            # Check if CORE investment already exists
            existing = investments_collection.find_one({
                "investment_id": "68ce0609-dae8-48a5-bb86-a84d5e0d3184"
            })
            
            if existing:
                print("✅ CORE investment already exists")
                print(f"   Amount: ${existing.get('principal_amount')}")
                return True
            
            # Create CORE investment
            core_investment = {
                "investment_id": "68ce0609-dae8-48a5-bb86-a84d5e0d3184",
                "client_id": "client_003",
                "fund_code": "CORE",
                "principal_amount": 4000.00,
                "current_value": 4000.00,
                "deposit_date": "2025-04-01T00:00:00.000Z",
                "status": "ACTIVE",
                "created_at": datetime.utcnow()
            }
            
            result = investments_collection.insert_one(core_investment)
            print(f"✅ CORE investment created successfully")
            print(f"   Investment ID: 68ce0609-dae8-48a5-bb86-a84d5e0d3184")
            print(f"   Amount: $4,000.00")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create CORE investment: {e}")
            return False

    def create_dootechnology_mt5_account(self):
        """Create DooTechnology MT5 account for Salvador"""
        print("\n🎯 STEP 4: CREATE DOOTECHNOLOGY MT5 ACCOUNT (Login: 9928326)")
        
        try:
            mt5_collection = self.db.mt5_accounts
            
            # Check if DooTechnology account already exists
            existing = mt5_collection.find_one({
                "account_id": "mt5_doo_9928326"
            })
            
            if existing:
                print("✅ DooTechnology MT5 account already exists")
                print(f"   Login: {existing.get('login')}")
                return True
            
            # Create DooTechnology MT5 account
            doo_account = {
                "account_id": "mt5_doo_9928326",
                "client_id": "client_003",
                "login": "9928326",
                "broker": "DooTechnology",
                "server": "DooTechnology-Live",
                "investment_id": "5e4c7092-d5e7-46d7-8efd-ca29db8f33a4",
                "total_allocated": 1263485.40,
                "current_equity": 1837934.05,
                "status": "active",
                "created_at": datetime.utcnow()
            }
            
            result = mt5_collection.insert_one(doo_account)
            print(f"✅ DooTechnology MT5 account created successfully")
            print(f"   Account ID: mt5_doo_9928326")
            print(f"   Login: 9928326")
            print(f"   Allocated: $1,263,485.40")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create DooTechnology MT5 account: {e}")
            return False

    def create_vt_markets_mt5_account(self):
        """Create VT Markets MT5 account for Salvador"""
        print("\n🎯 STEP 5: CREATE VT MARKETS MT5 ACCOUNT (Login: 15759667)")
        
        try:
            mt5_collection = self.db.mt5_accounts
            
            # Check if VT Markets account already exists
            existing = mt5_collection.find_one({
                "account_id": "mt5_vt_15759667"
            })
            
            if existing:
                print("✅ VT Markets MT5 account already exists")
                print(f"   Login: {existing.get('login')}")
                return True
            
            # Create VT Markets MT5 account
            vt_account = {
                "account_id": "mt5_vt_15759667",
                "client_id": "client_003",
                "login": "15759667",
                "broker": "VT Markets",
                "server": "VTMarkets-PAMM",
                "investment_id": "68ce0609-dae8-48a5-bb86-a84d5e0d3184",
                "total_allocated": 4000.00,
                "current_equity": 4000.00,
                "status": "active",
                "created_at": datetime.utcnow()
            }
            
            result = mt5_collection.insert_one(vt_account)
            print(f"✅ VT Markets MT5 account created successfully")
            print(f"   Account ID: mt5_vt_15759667")
            print(f"   Login: 15759667")
            print(f"   Allocated: $4,000.00")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create VT Markets MT5 account: {e}")
            return False

    def verify_production_endpoints(self):
        """Verify all production endpoints show Salvador's data"""
        print("\n🎯 STEP 6: IMMEDIATE VERIFICATION of production endpoints")
        
        if not self.admin_token:
            print("❌ No admin token available for verification")
            return False
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.admin_token}'
        }
        
        verification_results = []
        
        # Test 1: /api/admin/clients should show 1 client (Salvador)
        success, response = self.run_test(
            "Verify Clients Endpoint",
            "GET",
            "api/admin/clients",
            200,
            headers=headers
        )
        
        if success:
            clients = response.get('clients', [])
            salvador_found = any(c.get('name') == 'SALVADOR PALMA' for c in clients)
            if salvador_found:
                print("✅ Salvador found in clients endpoint")
                verification_results.append(True)
            else:
                print("❌ Salvador NOT found in clients endpoint")
                verification_results.append(False)
        else:
            verification_results.append(False)
        
        # Test 2: /api/investments/client/client_003 should show 2 investments
        success, response = self.run_test(
            "Verify Salvador Investments",
            "GET",
            "api/investments/client/client_003",
            200,
            headers=headers
        )
        
        if success:
            investments = response.get('investments', [])
            if len(investments) >= 2:
                balance_found = any(i.get('fund_code') == 'BALANCE' for i in investments)
                core_found = any(i.get('fund_code') == 'CORE' for i in investments)
                if balance_found and core_found:
                    print("✅ Both BALANCE and CORE investments found")
                    verification_results.append(True)
                else:
                    print(f"❌ Missing investments - BALANCE: {balance_found}, CORE: {core_found}")
                    verification_results.append(False)
            else:
                print(f"❌ Expected 2 investments, found {len(investments)}")
                verification_results.append(False)
        else:
            verification_results.append(False)
        
        # Test 3: /api/mt5/admin/accounts should show 2 MT5 accounts
        success, response = self.run_test(
            "Verify MT5 Accounts",
            "GET",
            "api/mt5/admin/accounts",
            200,
            headers=headers
        )
        
        if success:
            accounts = response.get('accounts', [])
            doo_found = any(a.get('login') == '9928326' for a in accounts)
            vt_found = any(a.get('login') == '15759667' for a in accounts)
            if doo_found and vt_found:
                print("✅ Both DooTechnology and VT Markets accounts found")
                verification_results.append(True)
            else:
                print(f"❌ Missing MT5 accounts - DooTechnology: {doo_found}, VT Markets: {vt_found}")
                verification_results.append(False)
        else:
            verification_results.append(False)
        
        # Test 4: Fund Portfolio should show non-zero AUM
        success, response = self.run_test(
            "Verify Fund Performance Dashboard",
            "GET",
            "api/admin/fund-performance/dashboard",
            200,
            headers=headers
        )
        
        if success:
            total_aum = response.get('total_aum', 0)
            if total_aum > 0:
                print(f"✅ Fund Portfolio shows AUM: ${total_aum:,.2f}")
                verification_results.append(True)
            else:
                print("❌ Fund Portfolio shows $0 AUM")
                verification_results.append(False)
        else:
            verification_results.append(False)
        
        # Summary
        passed_verifications = sum(verification_results)
        total_verifications = len(verification_results)
        
        print(f"\n📊 VERIFICATION SUMMARY: {passed_verifications}/{total_verifications} tests passed")
        
        if passed_verifications == total_verifications:
            print("🎉 ALL VERIFICATIONS PASSED - Salvador's data successfully restored!")
            return True
        else:
            print("❌ Some verifications failed - data restoration incomplete")
            return False

    def run_complete_restoration(self):
        """Run complete Salvador Palma data restoration"""
        print("🚀 STARTING SALVADOR PALMA PRODUCTION DATA RESTORATION")
        print("=" * 60)
        
        # Connect to MongoDB
        if not self.connect_to_mongodb():
            return False
        
        # Authenticate
        if not self.authenticate_admin():
            print("❌ Admin authentication failed")
            return False
        
        # Execute restoration steps
        steps = [
            self.create_salvador_client_if_missing,
            self.create_balance_investment,
            self.create_core_investment,
            self.create_dootechnology_mt5_account,
            self.create_vt_markets_mt5_account,
            self.verify_production_endpoints
        ]
        
        step_results = []
        for step in steps:
            result = step()
            step_results.append(result)
            if not result:
                print(f"❌ Step failed: {step.__name__}")
        
        # Final summary
        passed_steps = sum(step_results)
        total_steps = len(step_results)
        
        print("\n" + "=" * 60)
        print(f"🎯 FINAL RESTORATION SUMMARY: {passed_steps}/{total_steps} steps completed")
        print(f"📊 API Tests: {self.tests_passed}/{self.tests_run} passed")
        
        if passed_steps == total_steps:
            print("🎉 SALVADOR PALMA DATA RESTORATION COMPLETED SUCCESSFULLY!")
            print("✅ Production database now contains:")
            print("   - Salvador Palma client profile")
            print("   - BALANCE fund investment ($1,263,485.40)")
            print("   - CORE fund investment ($4,000.00)")
            print("   - DooTechnology MT5 account (Login: 9928326)")
            print("   - VT Markets MT5 account (Login: 15759667)")
            print("✅ All production endpoints verified working")
            return True
        else:
            print("❌ RESTORATION INCOMPLETE - Some steps failed")
            return False

def main():
    """Main execution function"""
    tester = SalvadorProductionDataRestoration()
    success = tester.run_complete_restoration()
    
    if success:
        print("\n🎉 SUCCESS: Salvador Palma's production data has been fully restored!")
        sys.exit(0)
    else:
        print("\n❌ FAILURE: Salvador Palma's data restoration incomplete!")
        sys.exit(1)

if __name__ == "__main__":
    main()