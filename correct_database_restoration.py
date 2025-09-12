#!/usr/bin/env python3
"""
CORRECT DATABASE RESTORATION FOR SALVADOR PALMA
===============================================

This test creates Salvador's data in the CORRECT database that the production
system is actually using (fidus_investment_db) instead of test_database.
"""

import requests
import sys
from datetime import datetime
import json
import pymongo
from pymongo import MongoClient
import os
from dotenv import load_dotenv

class CorrectDatabaseRestoration:
    def __init__(self, base_url="https://fidus-invest.emergent.host"):
        self.base_url = base_url
        self.admin_token = None
        
        # Load environment variables
        load_dotenv('/app/backend/.env')
        
        # Use the CORRECT database name that the production system uses
        self.mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.correct_db_name = "fidus_investment_db"  # This is what the production system uses
        
        print(f"🎯 CORRECT DATABASE RESTORATION FOR SALVADOR PALMA")
        print(f"   Production URL: {self.base_url}")
        print(f"   MongoDB URL: {self.mongo_url}")
        print(f"   CORRECT Database: {self.correct_db_name}")

    def connect_to_correct_database(self):
        """Connect to the CORRECT MongoDB database"""
        try:
            self.mongo_client = MongoClient(self.mongo_url)
            self.db = self.mongo_client[self.correct_db_name]
            
            # Test connection
            self.db.command('ping')
            print(f"✅ MongoDB connection successful to CORRECT database: {self.correct_db_name}")
            return True
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
            return False

    def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                json={
                    "username": "admin",
                    "password": "password123",
                    "user_type": "admin"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token')
                print(f"✅ Admin authenticated: {data.get('name')}")
                return True
            else:
                print(f"❌ Admin authentication failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Admin authentication error: {e}")
            return False

    def investigate_current_database_state(self):
        """Investigate both databases to understand the current state"""
        print("\n🔍 INVESTIGATING CURRENT DATABASE STATE")
        print("-" * 50)
        
        try:
            # Check the CORRECT database (fidus_investment_db)
            print(f"📊 CORRECT Database ({self.correct_db_name}):")
            
            # Check clients
            clients = list(self.db.clients.find())
            print(f"   Clients: {len(clients)}")
            for client in clients:
                print(f"     - {client.get('name', 'Unknown')} (ID: {client.get('id', 'Unknown')})")
            
            # Check investments
            investments = list(self.db.investments.find())
            print(f"   Investments: {len(investments)}")
            salvador_investments = [i for i in investments if i.get('client_id') == 'client_003']
            print(f"   Salvador's investments: {len(salvador_investments)}")
            
            # Check MT5 accounts
            mt5_accounts = list(self.db.mt5_accounts.find())
            print(f"   MT5 accounts: {len(mt5_accounts)}")
            salvador_mt5 = [m for m in mt5_accounts if m.get('client_id') == 'client_003']
            print(f"   Salvador's MT5 accounts: {len(salvador_mt5)}")
            
            # Also check the wrong database (test_database) for comparison
            print(f"\n📊 WRONG Database (test_database):")
            wrong_db = self.mongo_client["test_database"]
            
            wrong_clients = list(wrong_db.clients.find())
            print(f"   Clients: {len(wrong_clients)}")
            
            wrong_investments = list(wrong_db.investments.find())
            print(f"   Investments: {len(wrong_investments)}")
            
            wrong_mt5 = list(wrong_db.mt5_accounts.find())
            print(f"   MT5 accounts: {len(wrong_mt5)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Database investigation failed: {e}")
            return False

    def create_salvador_data_in_correct_database(self):
        """Create Salvador's complete data in the CORRECT database"""
        print("\n🎯 CREATING SALVADOR'S DATA IN CORRECT DATABASE")
        print("-" * 50)
        
        try:
            # 1. Create Salvador client
            print("1. Creating Salvador client...")
            salvador_client = {
                "id": "client_003",
                "name": "SALVADOR PALMA",
                "email": "chava@alyarglobal.com",
                "phone": "+52-663-123-4567",
                "status": "active",
                "registration_date": "2025-04-01T00:00:00.000Z",
                "total_balance": 1267485.40,
                "created_at": datetime.utcnow()
            }
            
            # Use upsert to avoid duplicates
            result = self.db.clients.update_one(
                {"id": "client_003"},
                {"$set": salvador_client},
                upsert=True
            )
            print(f"   ✅ Salvador client: {'created' if result.upserted_id else 'updated'}")
            
            # 2. Create BALANCE investment
            print("2. Creating BALANCE investment...")
            balance_investment = {
                "investment_id": "5e4c7092-d5e7-46d7-8efd-ca29db8f33a4",
                "client_id": "client_003",
                "fund_code": "BALANCE",
                "principal_amount": 1263485.40,
                "current_value": 1263485.40,
                "deposit_date": datetime.fromisoformat("2025-04-01T00:00:00+00:00"),
                "status": "active",
                "created_at": datetime.utcnow()
            }
            
            result = self.db.investments.update_one(
                {"investment_id": "5e4c7092-d5e7-46d7-8efd-ca29db8f33a4"},
                {"$set": balance_investment},
                upsert=True
            )
            print(f"   ✅ BALANCE investment: {'created' if result.upserted_id else 'updated'}")
            
            # 3. Create CORE investment
            print("3. Creating CORE investment...")
            core_investment = {
                "investment_id": "68ce0609-dae8-48a5-bb86-a84d5e0d3184",
                "client_id": "client_003",
                "fund_code": "CORE",
                "principal_amount": 4000.00,
                "current_value": 4000.00,
                "deposit_date": datetime.fromisoformat("2025-04-01T00:00:00+00:00"),
                "status": "ACTIVE",
                "created_at": datetime.utcnow()
            }
            
            result = self.db.investments.update_one(
                {"investment_id": "68ce0609-dae8-48a5-bb86-a84d5e0d3184"},
                {"$set": core_investment},
                upsert=True
            )
            print(f"   ✅ CORE investment: {'created' if result.upserted_id else 'updated'}")
            
            # 4. Create DooTechnology MT5 account
            print("4. Creating DooTechnology MT5 account...")
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
            
            result = self.db.mt5_accounts.update_one(
                {"account_id": "mt5_doo_9928326"},
                {"$set": doo_account},
                upsert=True
            )
            print(f"   ✅ DooTechnology MT5 account: {'created' if result.upserted_id else 'updated'}")
            
            # 5. Create VT Markets MT5 account
            print("5. Creating VT Markets MT5 account...")
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
            
            result = self.db.mt5_accounts.update_one(
                {"account_id": "mt5_vt_15759667"},
                {"$set": vt_account},
                upsert=True
            )
            print(f"   ✅ VT Markets MT5 account: {'created' if result.upserted_id else 'updated'}")
            
            print("\n🎉 ALL SALVADOR DATA CREATED IN CORRECT DATABASE!")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create Salvador's data: {e}")
            return False

    def verify_api_endpoints_after_correction(self):
        """Verify API endpoints after creating data in correct database"""
        print("\n🔍 VERIFYING API ENDPOINTS AFTER CORRECTION")
        print("-" * 50)
        
        if not self.admin_token:
            print("❌ No admin token available")
            return False
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.admin_token}'
        }
        
        verification_results = []
        
        # Test 1: Check clients
        try:
            response = requests.get(f"{self.base_url}/api/admin/clients", headers=headers, timeout=10)
            print(f"1. Admin Clients: Status {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                clients = data.get('clients', [])
                salvador_found = any(c.get('name') == 'SALVADOR PALMA' for c in clients)
                print(f"   Salvador found: {'✅' if salvador_found else '❌'}")
                verification_results.append(salvador_found)
            else:
                verification_results.append(False)
        except Exception as e:
            print(f"   Error: {e}")
            verification_results.append(False)
        
        # Test 2: Check Salvador's investments
        try:
            response = requests.get(f"{self.base_url}/api/investments/client/client_003", headers=headers, timeout=10)
            print(f"2. Salvador Investments: Status {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                investments = data.get('investments', [])
                print(f"   Investments found: {len(investments)}")
                
                balance_found = any(i.get('fund_code') == 'BALANCE' for i in investments)
                core_found = any(i.get('fund_code') == 'CORE' for i in investments)
                print(f"   BALANCE fund: {'✅' if balance_found else '❌'}")
                print(f"   CORE fund: {'✅' if core_found else '❌'}")
                
                verification_results.append(balance_found and core_found)
            else:
                verification_results.append(False)
        except Exception as e:
            print(f"   Error: {e}")
            verification_results.append(False)
        
        # Test 3: Check MT5 accounts
        try:
            response = requests.get(f"{self.base_url}/api/mt5/admin/accounts", headers=headers, timeout=10)
            print(f"3. MT5 Admin Accounts: Status {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                accounts = data.get('accounts', [])
                print(f"   MT5 accounts found: {len(accounts)}")
                
                doo_found = any(a.get('login') == '9928326' for a in accounts)
                vt_found = any(a.get('login') == '15759667' for a in accounts)
                print(f"   DooTechnology (9928326): {'✅' if doo_found else '❌'}")
                print(f"   VT Markets (15759667): {'✅' if vt_found else '❌'}")
                
                verification_results.append(doo_found and vt_found)
            else:
                verification_results.append(False)
        except Exception as e:
            print(f"   Error: {e}")
            verification_results.append(False)
        
        # Test 4: Check fund performance
        try:
            response = requests.get(f"{self.base_url}/api/admin/fund-performance/dashboard", headers=headers, timeout=10)
            print(f"4. Fund Performance: Status {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                total_aum = data.get('total_aum', 0)
                print(f"   Total AUM: ${total_aum}")
                verification_results.append(total_aum > 0)
            else:
                verification_results.append(False)
        except Exception as e:
            print(f"   Error: {e}")
            verification_results.append(False)
        
        # Summary
        passed = sum(verification_results)
        total = len(verification_results)
        
        print(f"\n📊 VERIFICATION SUMMARY: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ALL VERIFICATIONS PASSED!")
            return True
        else:
            print("❌ Some verifications failed")
            return False

    def run_complete_correction(self):
        """Run complete database correction"""
        print("🚀 STARTING CORRECT DATABASE RESTORATION")
        print("=" * 60)
        
        # Connect to correct database
        if not self.connect_to_correct_database():
            return False
        
        # Authenticate
        if not self.authenticate_admin():
            return False
        
        # Investigate current state
        if not self.investigate_current_database_state():
            return False
        
        # Create Salvador's data in correct database
        if not self.create_salvador_data_in_correct_database():
            return False
        
        # Verify API endpoints
        success = self.verify_api_endpoints_after_correction()
        
        print("\n" + "=" * 60)
        if success:
            print("🎉 SALVADOR PALMA DATA RESTORATION COMPLETED SUCCESSFULLY!")
            print("✅ Data created in CORRECT database (fidus_investment_db)")
            print("✅ All API endpoints verified working")
        else:
            print("❌ RESTORATION INCOMPLETE - Some verifications failed")
        
        return success

def main():
    """Main execution function"""
    corrector = CorrectDatabaseRestoration()
    success = corrector.run_complete_correction()
    
    if success:
        print("\n🎉 SUCCESS: Salvador Palma's data restored in correct database!")
        sys.exit(0)
    else:
        print("\n❌ FAILURE: Data restoration incomplete!")
        sys.exit(1)

if __name__ == "__main__":
    main()